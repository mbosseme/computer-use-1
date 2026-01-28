#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient
from agent_tools.llm.document_extraction import call_with_retry
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_azure_config(*, model_name: str = "azure-gpt-5.2"):
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

    from agent_tools.llm.azure_openai_responses import AzureResponsesClientConfig

    return AzureResponsesClientConfig(
        api_key=env.api_key,
        responses_api_url=candidate_url,
        deployment_name=deployment_name,
        max_output_tokens=int(max_output_tokens),
        reasoning_effort=reasoning_effort,  # type: ignore[arg-type]
    )


def _extract_body(md: str) -> str:
    if "\n---\n" in md:
        return md.split("\n---\n", 1)[1].strip()
    if "\n---\r\n" in md:
        return md.split("\n---\r\n", 1)[1].strip()
    return md.strip()


def _infer_source_filename(md: str, fallback: str) -> str:
    # synthesize_* writes a header including: "Source: <path>" or similar; keep it best-effort.
    m = re.search(r"^Source:\s*(.+)$", md, flags=re.MULTILINE)
    if not m:
        return fallback
    p = m.group(1).strip()
    try:
        return Path(p).name
    except Exception:
        return fallback


def rebuild(
    *,
    per_doc_dir: Path,
    out_md_path: Path,
    manifest_path: Path,
    model_name: str,
) -> None:
    if not per_doc_dir.exists() or not per_doc_dir.is_dir():
        raise RuntimeError(f"Not a directory: {per_doc_dir}")

    docs = sorted(per_doc_dir.glob("*__synthesis.md"))
    if not docs:
        raise RuntimeError(f"No per-doc syntheses found under {per_doc_dir}")

    combined_inputs: list[str] = []
    source_entries: list[dict] = []

    for doc_md in docs:
        md = doc_md.read_text(encoding="utf-8")
        body = _extract_body(md)
        src_name = _infer_source_filename(md, fallback=doc_md.name)
        combined_inputs.append(f"### {src_name}\n\n{body}")

        source_entries.append(
            {
                "per_doc_md": str(doc_md),
                "per_doc_manifest": str(doc_md.with_suffix(".manifest.json")),
                "source_filename": src_name,
            }
        )

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
                f"Per-doc dir: {per_doc_dir}",
                f"Documents included: {len(docs)}",
                "",
                synthesis,
                "",
                "## Individual Document Syntheses",
                "",
                "\n\n".join([f"- {p.name}" for p in docs]),
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
        "per_doc_dir": str(per_doc_dir),
        "documents_included": len(docs),
        "documents": source_entries,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild combined synthesis from existing per-doc syntheses")
    parser.add_argument("--per-doc-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--model", default="azure-gpt-5.2")

    args = parser.parse_args()
    rebuild(
        per_doc_dir=Path(args.per_doc_dir),
        out_md_path=Path(args.out),
        manifest_path=Path(args.manifest),
        model_name=args.model,
    )
    print(f"Wrote: {args.out}")
    print(f"Wrote: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
