from __future__ import annotations

import json
import re
from pathlib import Path

from agent_tools.llm.document_extraction import extract_pdf_text


def _digits_only(value: str) -> str:
    return re.sub(r"\D+", "", value)


def extract_ndcs_from_pdf(pdf_path: Path) -> list[str]:
    text = extract_pdf_text(pdf_path)

    # Capture separated NDC formats like 5-3-2 or 4-4-2.
    # Important: the PDF text often uses non-ASCII hyphens (en-dash, unicode hyphen),
    # so we match *any* non-digit separator between the segments.
    # Note: avoid word-boundary anchors because PDF extraction can concatenate the
    # trailing NDC segment with the next numeric field (e.g., NDC + volume).
    separated = re.findall(r"(\d{4,5}[^0-9]\d{3,4}[^0-9]\d{1,2})", text)

    ndc_candidates: list[str] = []
    ndc_candidates += [_digits_only(x) for x in separated]

    # Also capture plain 10/11 digit runs.
    ndc_candidates += re.findall(r"\b\d{10,11}\b", text)

    ndcs: list[str] = []
    for n in ndc_candidates:
        if len(n) not in (10, 11):
            continue
        if set(n) == {"0"}:
            continue
        ndcs.append(n)

    return sorted(set(ndcs))


def main() -> None:
    run_dir = Path("runs/2026-01-27__fy27-email-handoff")
    pdf_path = run_dir / "inputs/b_braun_docs__staging/re_confirmed_bbraun_mi_demo_virtual__39e24a0260.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(str(pdf_path))

    ndcs = extract_ndcs_from_pdf(pdf_path)

    out_dir = run_dir / "tmp"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "re_confirmed_bbraun_mi_demo_virtual__39e24a0260__ndcs.json").write_text(
        json.dumps({"pdf": str(pdf_path), "ndc_count": len(ndcs), "ndcs": ndcs}, indent=2)
    )
    (out_dir / "re_confirmed_bbraun_mi_demo_virtual__39e24a0260__ndcs.txt").write_text(
        "\n".join(ndcs) + ("\n" if ndcs else "")
    )

    print(f"Extracted {len(ndcs)} candidate NDCs")
    for n in ndcs[:40]:
        print(n)
    if len(ndcs) > 40:
        print("...")


if __name__ == "__main__":
    main()
