#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.llm.azure_openai_responses import (
    AzureOpenAIResponsesClient,
    AzureResponsesClientConfig,
)
from agent_tools.llm.document_extraction import call_with_retry, extract_eml_text, sanitize_text
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config
from agent_tools.llm.summarize_file import synthesize_pdf, synthesize_text


INCLUDE_EXTS = {".pdf", ".docx", ".eml", ".txt", ".md"}


@dataclass(frozen=True)
class FileFingerprint:
    path: str
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class DocIndexEntry:
    source: FileFingerprint
    source_name: str
    kind: str
    staged_path: str
    per_doc_md: str
    per_doc_manifest: str
    chunk_dir: str
    last_synthesized_on: Optional[str] = None


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\.[a-z0-9]{1,6}$", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "document"


def _stable_id_for_path(path: Path, *, length: int = 10) -> str:
    # Use absolute path as stable ID source (run-local; not committed).
    h = hashlib.sha1(str(path).encode("utf-8"))
    return h.hexdigest()[:length]


def _fingerprint(path: Path) -> FileFingerprint:
    st = path.stat()
    return FileFingerprint(path=str(path), size=int(st.st_size), mtime_ns=int(st.st_mtime_ns))


def _load_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "generated_on": None,
            "source_dir": None,
            "entries": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _write_index(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _resolve_azure_config(*, model_name: str = "azure-gpt-5.2") -> AzureResponsesClientConfig:
    load_repo_dotenv(REPO_ROOT)

    env = read_azure_openai_env()
    if not env.api_key:
        raise RuntimeError("Missing AZURE_OPENAI_KEY in environment (.env)")

    models = load_models_config(REPO_ROOT)
    model = models.get(model_name)

    deployment_name = (model.deployment_name if model else None) or env.deployment_name
    candidate_url = (model.api_url if model else None) or env.responses_api_url or env.api_url

    if not deployment_name:
        raise RuntimeError("Missing deployment name (AZURE_OPENAI_DEPLOYMENT or config/models.json)")
    if not candidate_url:
        raise RuntimeError("Missing Responses API URL (AZURE_OPENAI_RESPONSES_URL or config/models.json)")

    max_output_tokens = (model.max_output_tokens if model else None) or 8192
    reasoning_effort = (model.reasoning_effort if model else None) or "medium"

    return AzureResponsesClientConfig(
        api_key=env.api_key,
        responses_api_url=candidate_url,
        deployment_name=deployment_name,
        max_output_tokens=int(max_output_tokens),
        reasoning_effort=reasoning_effort,  # type: ignore[arg-type]
    )


def _textutil_docx_to_text(docx_path: Path) -> str:
    result = subprocess.run(
        ["/usr/bin/textutil", "-convert", "txt", "-stdout", str(docx_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "textutil failed (exit={code}): {stderr}".format(
                code=result.returncode,
                stderr=(result.stderr.decode("utf-8", errors="replace")[:2000]),
            )
        )
    return result.stdout.decode("utf-8", errors="replace")


def _ensure_symlink(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Safety: if src and dst refer to the same on-disk path, do nothing.
    try:
        if src.exists() and dst.exists() and src.samefile(dst):
            return
    except OSError:
        pass

    if src.resolve() == dst.resolve():
        return

    if dst.exists() or dst.is_symlink():
        dst.unlink()
    os.symlink(src, dst)


def _extract_body(md: str) -> str:
    # summarize_file writes header + warnings, then a separator.
    if "\n---\n" in md:
        return md.split("\n---\n", 1)[1].strip()
    if "\n---\r\n" in md:
        return md.split("\n---\r\n", 1)[1].strip()
    return md.strip()


def _build_combined_synthesis(
    *,
    docs_included: list[DocIndexEntry],
    out_md_path: Path,
    manifest_path: Path,
    model_name: str,
) -> None:
    combined_inputs: list[str] = []
    for e in docs_included:
        md = Path(e.per_doc_md).read_text(encoding="utf-8")
        body = _extract_body(md)
        combined_inputs.append(f"### {e.source_name}\n\n{body}")

    combined = "\n\n".join(combined_inputs)

    final_prompt = (
        "I have the following per-document syntheses from a folder of documents.\n"
        "Please provide a high-level executive summary and thematic synthesis across all these findings.\n"
        "Identify key themes, recurring topics, and strategic takeaways.\n\n"
        "Output Markdown with:\n"
        "- Executive Summary (8-12 bullets)\n"
        "- Themes (with evidence references to specific documents)\n"
        "- Notable Decisions / Confirmations\n"
        "- Open Questions / Follow-ups\n"
        "- Recommended Next Actions\n\n"
        "Be faithful to the sources; do not invent details.\n\n"
        f"SOURCES:\n{combined}"
    )

    cfg = _resolve_azure_config(model_name=model_name)
    client = AzureOpenAIResponsesClient(cfg)

    messages = [
        {"role": "system", "content": "You are a strategic analyst synthesizing business intelligence documents."},
        {"role": "user", "content": final_prompt},
    ]

    instructions, input_text = client.conversation_to_responses_input(messages)
    result = call_with_retry(client, input_text, instructions, max_retries=6, initial_delay=2.0, timeout_s=300.0)
    synthesis = client.extract_output_text(result).strip()

    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_md_path.write_text(
        "\n".join(
            [
                "# Folder Synthesis",
                "",
                f"Generated on: {date.today().isoformat()}",
                f"Rebuilt on: {datetime.now().isoformat(timespec='seconds')}",
                f"Documents included: {len(docs_included)}",
                "",
                synthesis,
                "",
                "## Individual Document Syntheses",
                "",
                "\n\n".join([f"- {Path(e.per_doc_md).name}" for e in docs_included]),
                "",
            ]
        ),
        encoding="utf-8",
    )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_on": date.today().isoformat(),
        "rebuilt_on": datetime.now().isoformat(timespec="seconds"),
        "model": model_name,
        "documents_included": len(docs_included),
        "documents": [asdict(e) for e in docs_included],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def sync(
    *,
    source_dir: Path,
    staging_dir: Path,
    per_doc_dir: Path,
    tmp_dir: Path,
    index_path: Path,
    out_md_path: Path,
    out_manifest_path: Path,
    model_name: str,
    rebuild_if_no_changes: bool,
) -> None:
    if not source_dir.exists() or not source_dir.is_dir():
        raise RuntimeError(f"Not a directory: {source_dir}")

    staging_dir.mkdir(parents=True, exist_ok=True)
    per_doc_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    index = _load_index(index_path)
    prior_entries: dict[str, Any] = index.get("entries", {}) if isinstance(index.get("entries"), dict) else {}

    # Scan current files.
    current_files: list[Path] = []
    for p in sorted(source_dir.iterdir()):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() not in INCLUDE_EXTS:
            continue
        current_files.append(p)

    entries: dict[str, Any] = {}
    changed = 0
    synthesized = 0

    for p in current_files:
        fp = _fingerprint(p)
        key = fp.path  # absolute path key (run-local)

        prev = prior_entries.get(key)
        prev_fp = (prev or {}).get("source") if isinstance(prev, dict) else None
        prev_size = (prev_fp or {}).get("size") if isinstance(prev_fp, dict) else None
        prev_mtime_ns = (prev_fp or {}).get("mtime_ns") if isinstance(prev_fp, dict) else None

        has_changed = (prev is None) or (int(prev_size or -1) != fp.size) or (int(prev_mtime_ns or -1) != fp.mtime_ns)

        kind = p.suffix.lower().lstrip(".")
        stable_id = _stable_id_for_path(p)
        slug = _slugify(p.name)
        out_prefix = f"{slug}__{stable_id}"

        out_md = per_doc_dir / f"{out_prefix}__synthesis.md"
        out_manifest = per_doc_dir / f"{out_prefix}__synthesis.manifest.json"
        chunk_dir = tmp_dir / f"{out_prefix}__chunks"

        # Stage
        staged_path: Path
        if p.suffix.lower() == ".docx":
            staged_path = staging_dir / f"{p.stem}.txt"
            if has_changed or not staged_path.exists():
                text = _textutil_docx_to_text(p)
                text = sanitize_text(text)
                staged_path.write_text(
                    "\n".join(
                        [
                            f"# Extracted from DOCX: {p.name}",
                            f"# Generated: {datetime.now().isoformat(timespec='seconds')}",
                            "",
                            text.strip(),
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
        else:
            staged_path = staging_dir / p.name
            if has_changed or not staged_path.exists() or not staged_path.is_symlink():
                _ensure_symlink(p, staged_path)

        # Synthesize if changed or missing outputs.
        needs_synthesis = has_changed or (not out_md.exists()) or (not out_manifest.exists())
        if needs_synthesis:
            changed += 1
            print(f"[changed] {p.name}")
            if p.suffix.lower() == ".pdf":
                synthesize_pdf(
                    pdf_path=staged_path,
                    out_md_path=out_md,
                    manifest_path=out_manifest,
                    model_name=model_name,
                    save_chunk_summaries_dir=chunk_dir,
                )
            elif p.suffix.lower() == ".eml":
                raw = extract_eml_text(p)
                synthesize_text(
                    title=p.name,
                    text=raw,
                    out_md_path=out_md,
                    manifest_path=out_manifest,
                    model_name=model_name,
                )
            else:
                raw = staged_path.read_text(encoding="utf-8", errors="replace")
                synthesize_text(
                    title=p.name,
                    text=raw,
                    out_md_path=out_md,
                    manifest_path=out_manifest,
                    model_name=model_name,
                )
            synthesized += 1
            time.sleep(0.25)
        else:
            print(f"[unchanged] {p.name}")

        entry = DocIndexEntry(
            source=fp,
            source_name=p.name,
            kind=kind,
            staged_path=str(staged_path),
            per_doc_md=str(out_md),
            per_doc_manifest=str(out_manifest),
            chunk_dir=str(chunk_dir),
            last_synthesized_on=datetime.now().isoformat(timespec="seconds") if needs_synthesis else (prev or {}).get("last_synthesized_on"),
        )
        entries[key] = asdict(entry)

    # Detect removed.
    removed = [k for k in prior_entries.keys() if k not in entries]

    # Write index
    index_out = {
        "generated_on": datetime.now().isoformat(timespec="seconds"),
        "source_dir": str(source_dir),
        "staging_dir": str(staging_dir),
        "per_doc_dir": str(per_doc_dir),
        "tmp_dir": str(tmp_dir),
        "model": model_name,
        "stats": {
            "files_seen": len(current_files),
            "changed": changed,
            "synthesized": synthesized,
            "removed": len(removed),
        },
        "removed": removed,
        "entries": entries,
    }
    _write_index(index_path, index_out)

    # Rebuild combined only if necessary (unless forced)
    if changed == 0 and not rebuild_if_no_changes and out_md_path.exists() and out_manifest_path.exists():
        print("No changes detected; skipping combined rebuild.")
        return

    docs_for_combined: list[DocIndexEntry] = []
    for v in entries.values():
        e = DocIndexEntry(
            source=FileFingerprint(**v["source"]),
            source_name=v["source_name"],
            kind=v["kind"],
            staged_path=v["staged_path"],
            per_doc_md=v["per_doc_md"],
            per_doc_manifest=v["per_doc_manifest"],
            chunk_dir=v["chunk_dir"],
            last_synthesized_on=v.get("last_synthesized_on"),
        )
        # Only include docs whose per-doc output exists.
        if Path(e.per_doc_md).exists():
            docs_for_combined.append(e)

    _build_combined_synthesis(
        docs_included=docs_for_combined,
        out_md_path=out_md_path,
        manifest_path=out_manifest_path,
        model_name=model_name,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Incremental synthesis sync (only reprocess changed docs)")
    parser.add_argument("--source-dir", required=True, help="Source folder containing GE docs")
    parser.add_argument("--staging-dir", required=True, help="Run-local staging folder")
    parser.add_argument("--per-doc-dir", required=True, help="Directory for per-doc syntheses")
    parser.add_argument("--tmp-dir", required=True, help="Directory for chunk artifacts")
    parser.add_argument("--index", required=True, help="Path to incremental index JSON")
    parser.add_argument("--out", required=True, help="Combined synthesis markdown path")
    parser.add_argument("--manifest", required=True, help="Combined synthesis manifest JSON path")
    parser.add_argument("--model", default="azure-gpt-5.2")
    parser.add_argument(
        "--rebuild-if-no-changes",
        action="store_true",
        help="Rebuild the combined synthesis even if no source files changed",
    )

    args = parser.parse_args()

    sync(
        source_dir=Path(args.source_dir),
        staging_dir=Path(args.staging_dir),
        per_doc_dir=Path(args.per_doc_dir),
        tmp_dir=Path(args.tmp_dir),
        index_path=Path(args.index),
        out_md_path=Path(args.out),
        out_manifest_path=Path(args.manifest),
        model_name=args.model,
        rebuild_if_no_changes=bool(args.rebuild_if_no_changes),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
