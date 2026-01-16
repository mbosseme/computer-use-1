from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

from agent_tools.llm.azure_openai_responses import (
    AzureOpenAIResponsesClient,
    AzureResponsesClientConfig,
)
from agent_tools.llm.document_extraction import PdfPageExtraction, extract_pdf_pages, sanitize_text
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config


@dataclass(frozen=True)
class Chunk:
    chunk_index: int
    start_page: int  # 1-based
    end_page: int  # 1-based
    text: str
    chars: int


@dataclass(frozen=True)
class CoverageWarning:
    code: str
    message: str


@dataclass(frozen=True)
class SynthesisManifest:
    source_path: str
    generated_on: str
    extraction: dict[str, Any]
    chunking: dict[str, Any]
    warnings: list[CoverageWarning]


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


def _hash_page_fingerprint(text: str, *, head_chars: int = 2500, tail_chars: int = 2500) -> str:
    """Create a conservative page fingerprint.

    Uses both the beginning and end of extracted text to avoid false de-duplication
    on documents that share headers/footers but differ in body content.
    """

    t = text or ""
    head = t[:head_chars]
    tail = t[-tail_chars:] if len(t) > tail_chars else t
    return str(hash(head + "\n---\n" + tail))


def _dedupe_redundant_pages(
    pages: list[PdfPageExtraction],
    *,
    min_dup_pages: int = 8,
) -> tuple[list[PdfPageExtraction], Optional[CoverageWarning]]:
    """Best-effort dedupe for pathological PDFs where a large block repeats on many pages.

    We do NOT do semantic dedupe; just a conservative snippet-hash heuristic.
    """

    hashes = [_hash_page_fingerprint(p.text) for p in pages]
    counts: dict[str, int] = {}
    for h in hashes:
        counts[h] = counts.get(h, 0) + 1

    # If we see a snippet repeated on many pages, keep only first occurrence of each snippet.
    most_common = max(counts.values()) if counts else 0
    unique_ratio = (len(counts) / len(pages)) if pages else 1.0

    # Only dedupe when duplication is overwhelming (pathological extraction).
    # Example: a transcript block repeated on every page.
    if most_common < min_dup_pages or unique_ratio > 0.35:
        return pages, None

    kept: list[PdfPageExtraction] = []
    seen: set[str] = set()
    dropped_pages: list[int] = []

    for p, h in zip(pages, hashes):
        if h in seen:
            dropped_pages.append(p.page_number)
            continue
        seen.add(h)
        kept.append(p)

    warn = CoverageWarning(
        code="PDF_REDUNDANCY_DEDUPED",
        message=(
            f"Detected repeated page extraction; de-duplicated {len(dropped_pages)} pages using a conservative fingerprint "
            "(head+tail). This typically indicates the PDF text layer is duplicated across pages by the extractor. "
            f"Dropped pages: {dropped_pages[:20]}{'…' if len(dropped_pages) > 20 else ''}."
        ),
    )
    return kept, warn


def _pack_pages_into_chunks(
    pages: list[PdfPageExtraction],
    *,
    target_chunk_chars: int,
    max_chunk_chars: int,
    overlap_pages: int,
    max_chunks: Optional[int],
) -> tuple[list[Chunk], list[CoverageWarning]]:
    warnings: list[CoverageWarning] = []

    chunks: list[Chunk] = []
    chunk_text_parts: list[str] = []
    chunk_chars = 0
    chunk_start_page: Optional[int] = None
    last_page_number: Optional[int] = None

    def flush(chunk_end_page: int) -> None:
        nonlocal chunk_text_parts, chunk_chars, chunk_start_page
        if chunk_start_page is None:
            return

        text = "\n".join(chunk_text_parts).strip()
        if len(text) > max_chunk_chars:
            warnings.append(
                CoverageWarning(
                    code="CHUNK_TRUNCATED",
                    message=(
                        f"Chunk {len(chunks)+1} exceeded max_chunk_chars ({max_chunk_chars}); "
                        "truncated chunk text before sending to the model."
                    ),
                )
            )
            text = text[:max_chunk_chars]

        chunks.append(
            Chunk(
                chunk_index=len(chunks) + 1,
                start_page=chunk_start_page,
                end_page=chunk_end_page,
                text=text,
                chars=len(text),
            )
        )

        # Overlap: keep the last N pages' worth of text markers (coarse, but deterministic).
        if overlap_pages <= 0:
            chunk_text_parts = []
            chunk_chars = 0
            chunk_start_page = None
            return

        # Keep overlap by retaining markers/text from the last overlap_pages pages.
        kept_parts: list[str] = []
        pages_seen = 0
        for part in reversed(chunk_text_parts):
            kept_parts.append(part)
            if part.startswith("--- Page "):
                pages_seen += 1
                if pages_seen >= overlap_pages:
                    break

        chunk_text_parts = list(reversed(kept_parts))
        chunk_chars = sum(len(p) for p in chunk_text_parts)
        # chunk_start_page becomes unknown; we'll re-set when we add next page marker.
        chunk_start_page = None

    for page in pages:
        if max_chunks is not None and len(chunks) >= max_chunks:
            warnings.append(
                CoverageWarning(
                    code="MAX_CHUNKS_REACHED",
                    message=(
                        f"Reached max_chunks={max_chunks}; remaining pages were not synthesized. "
                        "Increase max_chunks to ensure full coverage."
                    ),
                )
            )
            break

        marker = f"--- Page {page.page_number} ---"
        page_text = page.text or ""

        if page.error:
            warnings.append(
                CoverageWarning(
                    code="PAGE_EXTRACTION_ERROR",
                    message=f"Page {page.page_number} extraction error: {page.error}",
                )
            )

        # If a single page is enormous, split it deterministically.
        if len(page_text) > max_chunk_chars:
            # Flush current chunk first.
            if chunk_text_parts and last_page_number is not None:
                flush(last_page_number)

            parts = _split_text(page_text, max_chunk_chars)
            for i, part in enumerate(parts, start=1):
                if max_chunks is not None and len(chunks) >= max_chunks:
                    warnings.append(
                        CoverageWarning(
                            code="MAX_CHUNKS_REACHED",
                            message=(
                                f"Reached max_chunks={max_chunks}; remaining pages were not synthesized. "
                                "Increase max_chunks to ensure full coverage."
                            ),
                        )
                    )
                    break

                sub_marker = f"--- Page {page.page_number} (part {i}/{len(parts)}) ---"
                chunks.append(
                    Chunk(
                        chunk_index=len(chunks) + 1,
                        start_page=page.page_number,
                        end_page=page.page_number,
                        text=f"{sub_marker}\n{part}".strip(),
                        chars=len(part),
                    )
                )

            last_page_number = page.page_number
            continue

        # Start a new chunk if empty.
        if chunk_start_page is None:
            chunk_start_page = page.page_number

        candidate_parts = chunk_text_parts + [marker, page_text]
        candidate_chars = chunk_chars + len(marker) + len(page_text)

        # If adding this page exceeds target, flush current chunk before adding.
        if chunk_text_parts and candidate_chars > target_chunk_chars and last_page_number is not None:
            flush(last_page_number)
            if chunk_start_page is None:
                chunk_start_page = page.page_number
            chunk_text_parts.extend([marker, page_text])
            chunk_chars = sum(len(p) for p in chunk_text_parts)
        else:
            chunk_text_parts.extend([marker, page_text])
            chunk_chars = candidate_chars

        last_page_number = page.page_number

    if chunk_text_parts and last_page_number is not None and (max_chunks is None or len(chunks) < max_chunks):
        flush(last_page_number)

    return chunks, warnings


def _split_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        # try to split on a paragraph boundary near the end
        window = text[start:end]
        split_at = window.rfind("\n\n")
        if split_at < int(max_chars * 0.6):
            split_at = -1
        if split_at != -1:
            end = start + split_at
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]


def synthesize_text(
    *,
    title: str,
    text: str,
    out_md_path: Path,
    manifest_path: Optional[Path] = None,
    model_name: str = "azure-gpt-5.2",
    target_chunk_chars: int = 30_000,
    max_chunk_chars: int = 45_000,
    max_reduction_passes: int = 3,
) -> None:
    """Chunked map-reduce synthesis for non-PDF text (EML, TXT, MD, etc.)."""

    safe = sanitize_text(text or "")

    # First split into hard-bounded pieces, then pack into target-ish chunks.
    parts = _split_text(safe, max_chunk_chars)

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

    warnings: list[CoverageWarning] = []
    if len(packed) > 1:
        warnings.append(
            CoverageWarning(
                code="TEXT_CHUNKED",
                message=f"Input text was chunked into {len(packed)} chunks for synthesis.",
            )
        )

    cfg = _resolve_azure_config(model_name=model_name)
    client = AzureOpenAIResponsesClient(cfg)

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
            f"CHUNK {i}/{len(packed)}:\n{sanitize_text(chunk)}"
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
                    CoverageWarning(
                        code="MAX_REDUCTION_PASSES_REACHED",
                        message=(
                            f"Reduce output still large after {max_reduction_passes} passes; output may be overly compressed."
                        ),
                    )
                )
            break

        combined = final

    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    warnings_md = "\n".join([f"- [{w.code}] {w.message}" for w in warnings]) or "- None"

    header = "\n".join(
        [
            f"# Synthesis: {title}",
            "",
            f"Generated on: {date.today().isoformat()}",
            "",
            "## Coverage / Limit Warnings",
            warnings_md,
            "",
            "## Extraction/Chunking Stats",
            f"- chars_input: {len(safe)}",
            f"- chunks: {len(packed)}",
            f"- target_chunk_chars: {target_chunk_chars}",
            f"- max_chunk_chars: {max_chunk_chars}",
            "",
            "---",
            "",
        ]
    )

    out_md_path.write_text(header + final + "\n", encoding="utf-8")

    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "title": title,
                    "generated_on": date.today().isoformat(),
                    "chars_input": len(safe),
                    "chunks": len(packed),
                    "target_chunk_chars": target_chunk_chars,
                    "max_chunk_chars": max_chunk_chars,
                    "warnings": [asdict(w) for w in warnings],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def _call_llm(
    client: AzureOpenAIResponsesClient,
    *,
    user_prompt: str,
    system_prompt: str,
    timeout_s: float,
    max_retries: int,
) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    instructions, input_text = client.conversation_to_responses_input(messages)

    # Inline retry/backoff (avoid importing older run-local helpers)
    delay = 2.0
    for attempt in range(max_retries):
        try:
            result = client.create_response(
                input_text=input_text,
                instructions=instructions,
                timeout_s=timeout_s,
            )
            return client.extract_output_text(result)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "Too Many Requests" in msg:
                time.sleep(delay)
                delay *= 2
                continue
            if "timed out" in msg.lower():
                timeout_s += 60
                continue
            raise

    raise RuntimeError(f"Max retries exceeded ({max_retries})")


def synthesize_pdf(
    *,
    pdf_path: Path,
    out_md_path: Path,
    manifest_path: Optional[Path] = None,
    model_name: str = "azure-gpt-5.2",
    target_chunk_chars: int = 30_000,
    max_chunk_chars: int = 45_000,
    overlap_pages: int = 1,
    max_chunks: Optional[int] = None,
    page_timeout_s: Optional[int] = 15,
    max_reduction_passes: int = 3,
    save_chunk_summaries_dir: Optional[Path] = None,
) -> None:
    pages_raw = extract_pdf_pages(pdf_path, page_timeout_s=page_timeout_s)

    extraction_stats = {
        "pages_total": len(pages_raw),
        "pages_with_text": sum(1 for p in pages_raw if (p.text or "").strip()),
        "pages_with_error": sum(1 for p in pages_raw if p.error),
        "total_extracted_chars": sum(len(p.text or "") for p in pages_raw),
    }

    pages, dedupe_warn = _dedupe_redundant_pages(pages_raw)

    deduped_page_numbers = sorted(
        set(p.page_number for p in pages_raw) - set(p.page_number for p in pages)
    )

    warnings: list[CoverageWarning] = []
    if dedupe_warn:
        warnings.append(dedupe_warn)

    chunks, chunk_warnings = _pack_pages_into_chunks(
        pages,
        target_chunk_chars=target_chunk_chars,
        max_chunk_chars=max_chunk_chars,
        overlap_pages=overlap_pages,
        max_chunks=max_chunks,
    )
    warnings.extend(chunk_warnings)

    # If max_chunks truncated, compute omitted pages (excluding pages dropped due to dedupe).
    processed_pages = set()
    for c in chunks:
        processed_pages.update(range(c.start_page, c.end_page + 1))

    omitted_pages = [
        p.page_number
        for p in pages_raw
        if p.page_number not in processed_pages and p.page_number not in set(deduped_page_numbers)
    ]
    if omitted_pages:
        warnings.append(
            CoverageWarning(
                code="PAGES_OMITTED",
                message=(
                    f"Some pages were not included in any chunk and were not synthesized. "
                    f"Omitted pages (count={len(omitted_pages)}): {omitted_pages[:30]}{'…' if len(omitted_pages) > 30 else ''}."
                ),
            )
        )

    cfg = _resolve_azure_config(model_name=model_name)
    client = AzureOpenAIResponsesClient(cfg)

    if save_chunk_summaries_dir:
        save_chunk_summaries_dir.mkdir(parents=True, exist_ok=True)

    system_map = "You extract accurate notes from provided document text."
    system_reduce = "You synthesize multiple chunk summaries into a single accurate memo."

    chunk_summaries: list[str] = []
    for c in chunks:
        user_prompt = (
            "Summarize this chunk of a PDF.\n\n"
            "Return Markdown with:\n"
            "- Key points (bullets)\n"
            "- Decisions / confirmations\n"
            "- Open questions\n"
            "- Action items (with owners if present)\n"
            "- Notable metrics/claims (quote exact phrases when possible)\n\n"
            "Do not invent details. If uncertain, say 'unknown'.\n\n"
            f"Chunk pages: {c.start_page}-{c.end_page}\n\n"
            f"TEXT:\n{sanitize_text(c.text)}"
        )

        summary = _call_llm(
            client,
            user_prompt=user_prompt,
            system_prompt=system_map,
            timeout_s=300.0,
            max_retries=6,
        ).strip()

        labeled = f"## Chunk {c.chunk_index} (pages {c.start_page}-{c.end_page})\n\n{summary}"
        chunk_summaries.append(labeled)

        if save_chunk_summaries_dir:
            (save_chunk_summaries_dir / f"chunk_{c.chunk_index:03d}__p{c.start_page}-{c.end_page}.md").write_text(
                labeled + "\n", encoding="utf-8"
            )

        time.sleep(0.5)

    combined = "\n\n".join(chunk_summaries)

    # Reduce pass(es)
    reduction_pass = 0
    while True:
        reduction_pass += 1
        user_prompt = (
            "Given the following chunk summaries from a single document, produce a consolidated, client-ready synthesis.\n\n"
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

        # If the reduce output is still huge, do another pass (summary-of-summary).
        if len(final) <= max_chunk_chars or reduction_pass >= max_reduction_passes:
            if reduction_pass >= max_reduction_passes and len(final) > max_chunk_chars:
                warnings.append(
                    CoverageWarning(
                        code="MAX_REDUCTION_PASSES_REACHED",
                        message=(
                            f"Reduce output still large after {max_reduction_passes} passes; output may be overly compressed."
                        ),
                    )
                )
            break

        combined = final

    out_md_path.parent.mkdir(parents=True, exist_ok=True)

    warnings_md = "\n".join([f"- [{w.code}] {w.message}" for w in warnings]) or "- None"

    header = "\n".join(
        [
            f"# Synthesis: {pdf_path.name}",
            "",
            f"Generated on: {date.today().isoformat()}",
            "",
            "## Coverage / Limit Warnings",
            warnings_md,
            "",
            "## Extraction Stats",
            f"- Pages total: {extraction_stats['pages_total']}",
            f"- Pages de-duplicated (identical extraction): {len(deduped_page_numbers)}",
            f"- Pages with text: {extraction_stats['pages_with_text']}",
            f"- Pages with extraction errors: {extraction_stats['pages_with_error']}",
            f"- Total extracted chars: {extraction_stats['total_extracted_chars']}",
            "",
            "## Chunking Stats",
            f"- Chunks: {len(chunks)}",
            f"- target_chunk_chars: {target_chunk_chars}",
            f"- max_chunk_chars: {max_chunk_chars}",
            f"- overlap_pages: {overlap_pages}",
            f"- max_chunks: {max_chunks}",
            f"- page_timeout_s: {page_timeout_s}",
            "",
            "---",
            "",
        ]
    )

    out_md_path.write_text(header + final + "\n", encoding="utf-8")

    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = SynthesisManifest(
            source_path=str(pdf_path),
            generated_on=date.today().isoformat(),
            extraction=extraction_stats,
            chunking={
                "chunks": len(chunks),
                "target_chunk_chars": target_chunk_chars,
                "max_chunk_chars": max_chunk_chars,
                "overlap_pages": overlap_pages,
                "max_chunks": max_chunks,
                "page_timeout_s": page_timeout_s,
            },
            warnings=warnings,
        )
        manifest_path.write_text(
            json.dumps(
                {
                    **asdict(manifest),
                    "warnings": [asdict(w) for w in warnings],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Chunked PDF synthesizer (local-first)")
    parser.add_argument("--pdf", required=True, help="Path to a PDF to synthesize")
    parser.add_argument("--out", required=True, help="Output markdown path")
    parser.add_argument("--manifest", required=False, help="Optional JSON manifest output path")
    parser.add_argument("--model", default="azure-gpt-5.2", help="Model name from config/models.json")
    parser.add_argument("--target-chunk-chars", type=int, default=30000)
    parser.add_argument("--max-chunk-chars", type=int, default=45000)
    parser.add_argument("--overlap-pages", type=int, default=1)
    parser.add_argument("--max-chunks", type=int, default=0)
    parser.add_argument("--page-timeout-s", type=int, default=15)
    parser.add_argument("--max-reduction-passes", type=int, default=3)
    parser.add_argument("--chunk-summaries-dir", default="", help="Optional directory to write per-chunk summaries")

    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf)
    out_path = Path(args.out)
    manifest_path = Path(args.manifest) if args.manifest else None
    max_chunks = None if args.max_chunks <= 0 else int(args.max_chunks)
    page_timeout_s = None if args.page_timeout_s <= 0 else int(args.page_timeout_s)
    chunk_dir = Path(args.chunk_summaries_dir) if args.chunk_summaries_dir else None

    synthesize_pdf(
        pdf_path=pdf_path,
        out_md_path=out_path,
        manifest_path=manifest_path,
        model_name=args.model,
        target_chunk_chars=int(args.target_chunk_chars),
        max_chunk_chars=int(args.max_chunk_chars),
        overlap_pages=int(args.overlap_pages),
        max_chunks=max_chunks,
        page_timeout_s=page_timeout_s,
        max_reduction_passes=int(args.max_reduction_passes),
        save_chunk_summaries_dir=chunk_dir,
    )

    print(f"Wrote: {out_path}")
    if manifest_path:
        print(f"Wrote: {manifest_path}")
    if chunk_dir:
        print(f"Wrote chunk summaries under: {chunk_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
