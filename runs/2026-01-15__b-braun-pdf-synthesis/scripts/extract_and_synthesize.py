from __future__ import annotations

import re
import json
import time
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Optional

# Allow running this script directly without installing the repo as a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from agent_tools.llm.azure_openai_responses import (
    AzureOpenAIResponsesClient,
    AzureResponsesClientConfig,
)
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config
from agent_tools.llm.document_extraction import sanitize_text
from agent_tools.llm.summarize_file import synthesize_pdf

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]

def _resolve_azure_config(*, model_name: str = "azure-gpt-5.2") -> AzureResponsesClientConfig:
    repo_root = _repo_root()
    load_repo_dotenv(repo_root)

    env = read_azure_openai_env()
    models = load_models_config(repo_root)
    model = models.get(model_name)

    api_key = env.api_key
    deployment_name = (model.deployment_name if model else None) or env.deployment_name
    candidate_url = (model.api_url if model else None) or env.responses_api_url or env.api_url
    
    max_output_tokens = (model.max_output_tokens if model else None) or 16384
    reasoning_effort = (model.reasoning_effort if model else None) or "medium"

    return AzureResponsesClientConfig(
        api_key=api_key,
        responses_api_url=candidate_url,
        deployment_name=deployment_name,
        max_output_tokens=int(max_output_tokens),
        reasoning_effort=reasoning_effort,  # type: ignore[arg-type]
    )

def extract_eml_text(file_path: Path) -> str:
    try:
        with open(file_path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)
        
        text = (
            f"Subject: {msg['subject']}\n"
            f"From: {msg['from']}\n"
            f"To: {msg['to']}\n"
            f"Date: {msg['date']}\n\n"
        )
        body = msg.get_body(preferencelist=('plain', 'html'))
        if body:
            text += body.get_content()
        return text
    except Exception as e:
        print(f"Error extracting EML {file_path}: {e}")
        return ""

def sanitize(text: str) -> str:
    # Keep older behavior, then apply shared sanitization helper.
    text = re.sub(
        r"(?i)(api[-_]?key|secret|token|password|credential|pwd)\s*[:=]\s*[a-zA-Z0-9_\-\.\~]+",
        r"\1: [REDACTED]",
        text,
    )
    text = re.sub(r"Bearer\s+[a-zA-Z0-9\-\.\_]+", "Bearer [REDACTED]", text)
    return sanitize_text(text)


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\.[a-z0-9]{1,6}$", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "document"


def _split_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        window = text[start:end]
        split_at = window.rfind("\n\n")
        if split_at < int(max_chars * 0.6):
            split_at = -1
        if split_at != -1:
            end = start + split_at
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]


def _summarize_text_map_reduce(
    *,
    client: AzureOpenAIResponsesClient,
    title: str,
    text: str,
    target_chunk_chars: int = 30_000,
    max_chunk_chars: int = 45_000,
    max_reduction_passes: int = 3,
) -> tuple[str, dict[str, Any]]:
    safe = sanitize(text)
    parts = _split_text(safe, max_chunk_chars)

    warnings: list[dict[str, str]] = []
    if len(safe) > max_chunk_chars and len(parts) > 1:
        warnings.append(
            {
                "code": "TEXT_CHUNKED",
                "message": f"Input text was chunked into {len(parts)} parts for synthesis.",
            }
        )

    # Pack parts into target-sized chunks deterministically.
    packed: list[str] = []
    buf: list[str] = []
    buf_chars = 0
    for p in parts:
        if buf and buf_chars + len(p) > target_chunk_chars:
            packed.append("\n\n".join(buf).strip())
            buf = [p]
            buf_chars = len(p)
        else:
            buf.append(p)
            buf_chars += len(p)
    if buf:
        packed.append("\n\n".join(buf).strip())

    system_map = "You extract accurate notes from provided document text."
    system_reduce = "You synthesize multiple chunk summaries into a single accurate memo."

    chunk_summaries: list[str] = []
    for i, chunk in enumerate(packed, start=1):
        user_prompt = (
            f"Summarize this chunk of a document titled: {title}.\n\n"
            "Return Markdown with:\n"
            "- Key points (bullets)\n"
            "- Decisions / confirmations\n"
            "- Open questions\n"
            "- Action items (with owners if present)\n"
            "- Notable metrics/claims (quote exact phrases when possible)\n\n"
            "Do not invent details. If uncertain, say 'unknown'.\n\n"
            f"CHUNK {i}/{len(packed)}:\n{chunk}"
        )
        summary = _call_llm(
            client,
            user_prompt=user_prompt,
            system_prompt=system_map,
            timeout_s=300.0,
            max_retries=6,
        ).strip()
        chunk_summaries.append(f"## Chunk {i}\n\n{summary}")
        time.sleep(0.5)

    combined = "\n\n".join(chunk_summaries)

    reduction_pass = 0
    while True:
        reduction_pass += 1
        user_prompt = (
            f"Given the following chunk summaries from a single document titled: {title}, produce a consolidated, client-ready synthesis.\n\n"
            "Output Markdown with:\n"
            "1) Executive Summary (6-10 bullets)\n"
            "2) Meeting Context\n"
            "3) Key Decisions / Confirmations\n"
            "4) Open Questions / Follow-ups\n"
            "5) Risks / Dependencies\n"
            "6) Suggested Next-Step Email (short draft)\n\n"
            "Be faithful to the chunk summaries; do not invent. If something is unclear, mark as unknown.\n\n"
            f"CHUNK SUMMARIES:\n{combined}"
        )
        final = _call_llm(
            client,
            user_prompt=user_prompt,
            system_prompt=system_reduce,
            timeout_s=300.0,
            max_retries=6,
        ).strip()

        if len(final) <= max_chunk_chars or reduction_pass >= max_reduction_passes:
            if reduction_pass >= max_reduction_passes and len(final) > max_chunk_chars:
                warnings.append(
                    {
                        "code": "MAX_REDUCTION_PASSES_REACHED",
                        "message": (
                            f"Reduce output still large after {max_reduction_passes} passes; output may be overly compressed."
                        ),
                    }
                )
            return final, {
                "chars_input": len(safe),
                "chunks": len(packed),
                "target_chunk_chars": target_chunk_chars,
                "max_chunk_chars": max_chunk_chars,
                "warnings": warnings,
            }

        combined = final

def call_with_retry(client, input_text, instructions=None, max_retries=5, initial_delay=2, timeout_s=300):
    for i in range(max_retries):
        try:
            result = client.create_response(input_text=input_text, instructions=instructions, timeout_s=timeout_s)
            return result
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                delay = initial_delay * (2 ** i)
                print(f"Rate limited. Retrying in {delay}s...")
                time.sleep(delay)
            elif "Read timed out" in str(e):
                print(f"Read timed out. Retrying with longer timeout...")
                timeout_s += 120
            else:
                raise e
    raise RuntimeError("Max retries exceeded for API call")

def main():
    doc_dir = Path("/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/B Braun")
    run_id = "2026-01-15__b-braun-pdf-synthesis"
    repo_root = _repo_root()
    export_path = repo_root / "runs" / run_id / "exports" / "b-braun_synthesis.md"
    per_doc_dir = repo_root / "runs" / run_id / "exports" / "docs"
    per_doc_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = repo_root / "runs" / run_id / "tmp" / "docs"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_docs: list[dict[str, Any]] = []
    skipped: list[str] = []
    
    print(f"Inventorying files in {doc_dir}...")
    for file_path in sorted(doc_dir.iterdir()):
        if file_path.is_dir():
            continue

        ext = file_path.suffix.lower()
        if ext == ".pdf":
            # PDF is synthesized directly via chunked map-reduce (no naive truncation).
            extracted_docs.append({"filename": file_path.name, "path": str(file_path), "type": "pdf"})
        elif ext == ".eml":
            extracted_docs.append({"filename": file_path.name, "path": str(file_path), "type": "eml"})
        elif ext in {".txt", ".md"}:
            extracted_docs.append({"filename": file_path.name, "path": str(file_path), "type": "text"})
        else:
            skipped.append(file_path.name)
    
    if not extracted_docs:
        print("No documents found to process.")
        return

    if skipped:
        print(f"Skipping unsupported files (count={len(skipped)}): {skipped}")

    print(f"Processing {len(extracted_docs)} documents individually to generate summaries...")
    
    cfg = _resolve_azure_config()
    client = AzureOpenAIResponsesClient(cfg)
    
    summaries: list[str] = []
    for doc in extracted_docs:
        filename = doc["filename"]
        doc_type = doc["type"]
        path = Path(doc["path"])
        slug = _slugify(filename)

        out_md = per_doc_dir / f"{slug}__synthesis.md"
        out_manifest = per_doc_dir / f"{slug}__synthesis.manifest.json"

        print(f"Synthesizing ({doc_type}): {filename}...")

        try:
            if doc_type == "pdf":
                synthesize_pdf(
                    pdf_path=path,
                    out_md_path=out_md,
                    manifest_path=out_manifest,
                    target_chunk_chars=30_000,
                    max_chunk_chars=45_000,
                    overlap_pages=1,
                    page_timeout_s=15,
                    max_reduction_passes=3,
                    save_chunk_summaries_dir=(tmp_dir / f"{slug}__chunks"),
                )
                doc_summary_text = out_md.read_text(encoding="utf-8")
                summaries.append(f"### {filename}\n\n{doc_summary_text.strip()}")
            else:
                if doc_type == "eml":
                    raw = extract_eml_text(path)
                else:
                    raw = path.read_text(encoding="utf-8", errors="replace")

                final, stats = _summarize_text_map_reduce(
                    client=client,
                    title=filename,
                    text=raw,
                    target_chunk_chars=30_000,
                    max_chunk_chars=45_000,
                    max_reduction_passes=3,
                )

                out_md.write_text(
                    "\n".join(
                        [
                            f"# Synthesis: {filename}",
                            "",
                            "## Coverage / Limit Warnings",
                            "\n".join(
                                [
                                    f"- [{w['code']}] {w['message']}" for w in stats.get("warnings", [])
                                ]
                            )
                            or "- None",
                            "",
                            "## Extraction/Chunking Stats",
                            f"- chars_input: {stats.get('chars_input')}",
                            f"- chunks: {stats.get('chunks')}",
                            f"- target_chunk_chars: {stats.get('target_chunk_chars')}",
                            f"- max_chunk_chars: {stats.get('max_chunk_chars')}",
                            "",
                            "---",
                            "",
                            final.strip(),
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
                out_manifest.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
                summaries.append(f"### {filename}\n\n{out_md.read_text(encoding='utf-8').strip()}")

            time.sleep(0.5)
        except Exception as e:
            print(f"Error synthesizing {filename}: {e}")
            summaries.append(f"### {filename}\n[Summary failed]")

    print("Aggregating summaries for final synthesis...")
    
    combined_summaries = "\n\n".join(summaries)
    
    final_prompt = (
        "I have the following per-document syntheses related to B Braun and Market Insights.\n"
        "Please provide a high-level executive summary and thematic synthesis across all these findings.\n"
        "Identify key themes, recurring topics, and strategic takeaways.\n\n"
        "Output Markdown with:\n"
        "- Executive Summary (8-12 bullets)\n"
        "- Themes (with evidence references to specific documents)\n"
        "- Notable Decisions / Confirmations\n"
        "- Open Questions / Follow-ups\n"
        "- Recommended Next Actions\n\n"
        "Be faithful to the sources; do not invent details.\n\n"
        f"SOURCES:\n{combined_summaries}"
    )

    print("Sending for final synthesis...")
    try:
        messages = [
            {"role": "system", "content": "You are a strategic analyst synthesizing business intelligence documents."},
            {"role": "user", "content": final_prompt}
        ]
        
        instructions, input_text = client.conversation_to_responses_input(messages)
        result = call_with_retry(client, input_text, instructions)
        synthesis = client.extract_output_text(result)
        
        print(f"Writing synthesis to {export_path}")
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(
                "\n".join(
                    [
                        "# Global Synthesis: B Braun Documents",
                        "",
                        "Generated on: 2026-01-16",
                        f"Source folder: {doc_dir}",
                        "",
                        synthesis.strip(),
                        "",
                        "## Individual Document Syntheses",
                        "",
                        combined_summaries,
                        "",
                    ]
                )
            )
            
        print("Success!")
        
    except Exception as e:
        print(f"Error during final synthesis: {e}")

if __name__ == "__main__":
    main()
