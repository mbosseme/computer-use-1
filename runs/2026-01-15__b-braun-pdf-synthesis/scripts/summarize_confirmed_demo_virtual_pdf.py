from __future__ import annotations

from pathlib import Path
import sys

# Allow running this script directly without installing the repo as a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from agent_tools.llm.summarize_file import synthesize_pdf


RUN_ID = "2026-01-15__b-braun-pdf-synthesis"
PDF_PATH = Path(
    "/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/B Braun/Re: Confirmed-BBraun MI Demo - virtual .pdf"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> None:
    repo_root = _repo_root()
    exports_dir = repo_root / "runs" / RUN_ID / "exports"
    tmp_dir = repo_root / "runs" / RUN_ID / "tmp"

    exports_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    out_path = exports_dir / "confirmed_demo_virtual__synthesis.md"
    manifest_path = exports_dir / "confirmed_demo_virtual__synthesis.manifest.json"
    chunk_dir = tmp_dir / "confirmed_demo_virtual__synthesis_chunks"

    synthesize_pdf(
        pdf_path=PDF_PATH,
        out_md_path=out_path,
        manifest_path=manifest_path,
        target_chunk_chars=30_000,
        max_chunk_chars=45_000,
        overlap_pages=1,
        page_timeout_s=15,
        max_reduction_passes=3,
        save_chunk_summaries_dir=chunk_dir,
    )

    print(f"Wrote synthesis: {out_path}")
    print(f"Wrote manifest: {manifest_path}")
    print(f"Wrote chunk summaries: {chunk_dir}")


if __name__ == "__main__":
    main()
