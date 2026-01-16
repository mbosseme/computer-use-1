from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any, Optional

from agent_tools.llm.azure_openai_responses import (
    AzureOpenAIResponsesClient,
    AzureResponsesClientConfig,
)
from agent_tools.llm.document_extraction import call_with_retry, extract_eml_text
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config
from agent_tools.llm.summarize_file import synthesize_pdf, synthesize_text


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_azure_config(*, model_name: str = "azure-gpt-5.2") -> AzureResponsesClientConfig:
    repo_root = _repo_root()
    load_repo_dotenv(repo_root)

    env = read_azure_openai_env()
    if not env.api_key:
        raise RuntimeError("Missing AZURE_OPENAI_KEY in environment (.env)")

    models = load_models_config(repo_root)
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


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\.[a-z0-9]{1,6}$", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "document"


def _extract_body(md: str) -> str:
    """Return markdown content after the first '---' separator, if present."""
    if "\n---\n" in md:
        return md.split("\n---\n", 1)[1].strip()
    if "\n---\r\n" in md:
        return md.split("\n---\r\n", 1)[1].strip()
    return md.strip()


def synthesize_folder(
    *,
    dir_path: Path,
    out_md_path: Path,
    per_doc_dir: Path,
    tmp_dir: Path,
    model_name: str = "azure-gpt-5.2",
    include_exts: tuple[str, ...] = (".pdf", ".eml", ".txt", ".md"),
    max_files: int = 0,
    target_chunk_chars: int = 30_000,
    max_chunk_chars: int = 45_000,
    overlap_pages: int = 1,
    max_chunks: Optional[int] = None,
    page_timeout_s: Optional[int] = 15,
    max_reduction_passes: int = 3,
) -> dict[str, Any]:
    if not dir_path.exists() or not dir_path.is_dir():
        raise RuntimeError(f"Not a directory: {dir_path}")

    per_doc_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_md_path.parent.mkdir(parents=True, exist_ok=True)

    files = [p for p in sorted(dir_path.iterdir()) if p.is_file()]
    candidates = [p for p in files if p.suffix.lower() in set(include_exts)]

    if max_files and max_files > 0:
        candidates = candidates[: int(max_files)]

    # Per-doc syntheses
    source_entries: list[dict[str, Any]] = []
    combined_inputs: list[str] = []

    for idx, path in enumerate(candidates, start=1):
        slug = _slugify(path.name)
        out_doc_md = per_doc_dir / f"{slug}__synthesis.md"
        out_doc_manifest = per_doc_dir / f"{slug}__synthesis.manifest.json"

        print(f"[{idx}/{len(candidates)}] Synthesizing: {path.name}")

        if path.suffix.lower() == ".pdf":
            synthesize_pdf(
                pdf_path=path,
                out_md_path=out_doc_md,
                manifest_path=out_doc_manifest,
                model_name=model_name,
                target_chunk_chars=target_chunk_chars,
                max_chunk_chars=max_chunk_chars,
                overlap_pages=overlap_pages,
                max_chunks=max_chunks,
                page_timeout_s=page_timeout_s,
                max_reduction_passes=max_reduction_passes,
                save_chunk_summaries_dir=(tmp_dir / f"{slug}__chunks"),
            )
        elif path.suffix.lower() == ".eml":
            raw = extract_eml_text(path)
            synthesize_text(
                title=path.name,
                text=raw,
                out_md_path=out_doc_md,
                manifest_path=out_doc_manifest,
                model_name=model_name,
                target_chunk_chars=target_chunk_chars,
                max_chunk_chars=max_chunk_chars,
                max_reduction_passes=max_reduction_passes,
            )
        else:
            raw = path.read_text(encoding="utf-8", errors="replace")
            synthesize_text(
                title=path.name,
                text=raw,
                out_md_path=out_doc_md,
                manifest_path=out_doc_manifest,
                model_name=model_name,
                target_chunk_chars=target_chunk_chars,
                max_chunk_chars=max_chunk_chars,
                max_reduction_passes=max_reduction_passes,
            )

        md = out_doc_md.read_text(encoding="utf-8")
        body = _extract_body(md)
        combined_inputs.append(f"### {path.name}\n\n{body}")

        source_entries.append(
            {
                "filename": path.name,
                "path": str(path),
                "type": path.suffix.lower().lstrip("."),
                "out_md": str(out_doc_md),
                "out_manifest": str(out_doc_manifest),
            }
        )

        time.sleep(0.25)

    # Folder-level synthesis
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

    out_md_path.write_text(
        "\n".join(
            [
                "# Folder Synthesis",
                "",
                f"Generated on: {date.today().isoformat()}",
                f"Source folder: {dir_path}",
                f"Documents included: {len(candidates)}",
                "",
                synthesis,
                "",
                "## Individual Document Syntheses",
                "",
                "\n\n".join([f"- {p.name}" for p in candidates]) if candidates else "- None",
                "",
            ]
        ),
        encoding="utf-8",
    )

    manifest = {
        "source_folder": str(dir_path),
        "generated_on": date.today().isoformat(),
        "model": model_name,
        "include_exts": list(include_exts),
        "documents_included": len(candidates),
        "documents": source_entries,
        "chunking": {
            "target_chunk_chars": target_chunk_chars,
            "max_chunk_chars": max_chunk_chars,
            "overlap_pages": overlap_pages,
            "max_chunks": max_chunks,
            "page_timeout_s": page_timeout_s,
            "max_reduction_passes": max_reduction_passes,
        },
    }

    return manifest


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Chunked folder synthesizer (PDF/EML/text)")
    parser.add_argument("--dir", required=True, help="Folder containing documents")
    parser.add_argument("--out", required=True, help="Output markdown path for folder synthesis")
    parser.add_argument("--per-doc-dir", required=True, help="Directory to write per-document syntheses")
    parser.add_argument("--tmp-dir", required=True, help="Directory to write per-document chunk artifacts")
    parser.add_argument("--manifest", default="", help="Optional JSON manifest output path")
    parser.add_argument("--model", default="azure-gpt-5.2", help="Model name from config/models.json")
    parser.add_argument("--include-exts", default=".pdf,.eml,.txt,.md", help="Comma-separated extensions")
    parser.add_argument("--max-files", type=int, default=0, help="Optional limit for number of files (0 = all)")

    parser.add_argument("--target-chunk-chars", type=int, default=30000)
    parser.add_argument("--max-chunk-chars", type=int, default=45000)
    parser.add_argument("--overlap-pages", type=int, default=1)
    parser.add_argument("--max-chunks", type=int, default=0)
    parser.add_argument("--page-timeout-s", type=int, default=15)
    parser.add_argument("--max-reduction-passes", type=int, default=3)

    args = parser.parse_args(argv)

    dir_path = Path(args.dir)
    out_md = Path(args.out)
    per_doc_dir = Path(args.per_doc_dir)
    tmp_dir = Path(args.tmp_dir)
    manifest_path = Path(args.manifest) if args.manifest else None

    include_exts = tuple(e.strip().lower() for e in args.include_exts.split(",") if e.strip())
    max_chunks = None if args.max_chunks <= 0 else int(args.max_chunks)
    page_timeout_s = None if args.page_timeout_s <= 0 else int(args.page_timeout_s)

    manifest = synthesize_folder(
        dir_path=dir_path,
        out_md_path=out_md,
        per_doc_dir=per_doc_dir,
        tmp_dir=tmp_dir,
        model_name=args.model,
        include_exts=include_exts,
        max_files=int(args.max_files),
        target_chunk_chars=int(args.target_chunk_chars),
        max_chunk_chars=int(args.max_chunk_chars),
        overlap_pages=int(args.overlap_pages),
        max_chunks=max_chunks,
        page_timeout_s=page_timeout_s,
        max_reduction_passes=int(args.max_reduction_passes),
    )

    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote: {manifest_path}")

    print(f"Wrote: {out_md}")
    print(f"Wrote per-doc syntheses under: {per_doc_dir}")
    print(f"Wrote tmp artifacts under: {tmp_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
