from __future__ import annotations

from pathlib import Path

import PyPDF2
from email import policy
from email.parser import BytesParser

DOC_DIR = Path(
    "/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/B Braun"
)
TARGET = DOC_DIR / "Confirmed-BBraun MI Demo - virtual.pdf"
TRUNCATION_THRESHOLD_CHARS = 20_000


def extract_pdf_chars(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        pages = len(reader.pages)
        char_count = 0
        for page in reader.pages:
            char_count += len(page.extract_text() or "")
    return pages, char_count


def extract_eml_chars(path: Path) -> int:
    with path.open("rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    headers = (
        f"Subject: {msg['subject']}\n"
        f"From: {msg['from']}\n"
        f"To: {msg['to']}\n"
        f"Date: {msg['date']}\n\n"
    )
    body = msg.get_body(preferencelist=("plain", "html"))
    body_text = body.get_content() if body else ""
    return len(headers) + len(body_text)


def main() -> None:
    if not DOC_DIR.exists():
        raise SystemExit(f"Missing doc dir: {DOC_DIR}")

    rows: list[dict[str, object]] = []

    for p in sorted(DOC_DIR.iterdir()):
        if p.suffix.lower() not in {".pdf", ".eml"}:
            continue

        size_bytes = p.stat().st_size

        if p.suffix.lower() == ".pdf":
            try:
                pages, chars = extract_pdf_chars(p)
                rows.append(
                    {
                        "name": p.name,
                        "type": "pdf",
                        "bytes": size_bytes,
                        "pages": pages,
                        "extracted_chars": chars,
                        "error": None,
                    }
                )
            except Exception as e:
                rows.append(
                    {
                        "name": p.name,
                        "type": "pdf",
                        "bytes": size_bytes,
                        "pages": None,
                        "extracted_chars": None,
                        "error": str(e),
                    }
                )

        if p.suffix.lower() == ".eml":
            try:
                chars = extract_eml_chars(p)
                rows.append(
                    {
                        "name": p.name,
                        "type": "eml",
                        "bytes": size_bytes,
                        "pages": None,
                        "extracted_chars": chars,
                        "error": None,
                    }
                )
            except Exception as e:
                rows.append(
                    {
                        "name": p.name,
                        "type": "eml",
                        "bytes": size_bytes,
                        "pages": None,
                        "extracted_chars": None,
                        "error": str(e),
                    }
                )

    if not rows:
        raise SystemExit(f"No .pdf/.eml files found under: {DOC_DIR}")

    def sort_key(r: dict[str, object]) -> tuple[bool, int]:
        extracted = r.get("extracted_chars")
        if extracted is None:
            return (True, 0)
        return (False, -int(extracted))

    rows_sorted = sorted(rows, key=sort_key)

    print(f"Doc dir: {DOC_DIR}")
    print(f"Material count (.pdf/.eml): {len(rows_sorted)}")
    print("\nTop 10 by extracted_chars:")
    for r in rows_sorted[:10]:
        print(
            f"- {r['name']} ({r['type']}) | pages={r['pages']} | chars={r['extracted_chars']} | bytes={r['bytes']}"
        )
        if r.get("error"):
            print(f"  error: {r['error']}")

    largest = rows_sorted[0]
    print("\nLargest-by-extracted_chars:")
    print(
        f"- {largest['name']} ({largest['type']}) | pages={largest['pages']} | chars={largest['extracted_chars']} | bytes={largest['bytes']}"
    )

    print("\nTarget:")
    if not TARGET.exists():
        print(f"- MISSING: {TARGET}")
        return

    target_row = next((r for r in rows if r["name"] == TARGET.name), None)
    if target_row is None:
        print(f"- Not found in scan results: {TARGET.name}")
        return

    print(
        f"- {target_row['name']} ({target_row['type']}) | pages={target_row['pages']} | chars={target_row['extracted_chars']} | bytes={target_row['bytes']}"
    )

    is_largest = largest["name"] == TARGET.name
    print(f"\nIs target the largest (by extracted_chars)? {is_largest}")

    extracted_chars = target_row.get("extracted_chars")
    if isinstance(extracted_chars, int):
        would_truncate = extracted_chars > TRUNCATION_THRESHOLD_CHARS
        print(
            f"Would be truncated by current 20k-char approach? {would_truncate} (threshold={TRUNCATION_THRESHOLD_CHARS})"
        )
    else:
        print("Would be truncated by current 20k-char approach? unknown (extraction failed)")


if __name__ == "__main__":
    main()
