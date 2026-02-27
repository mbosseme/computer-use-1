#!/usr/bin/env python3
"""Generic Excel workbook profiler.

Reads an .xlsx file, profiles every sheet, and outputs a human-readable
Markdown summary plus a structured JSON report.

For each sheet, the profiler reports:
  - Row / column counts
  - Column names + non-null counts
  - Data-type distribution (numeric / datetime / text / mixed / empty)
  - Cardinality (unique values) per column
  - Min / max / mean for numeric columns
  - Date range for datetime columns
  - Heuristic "key columns" detection (facility, product, spend, etc.)
  - Sample rows (first N rows of highlighted columns)

Usage::

    python tools/profile_workbook.py path/to/workbook.xlsx [--out-dir tmp/profiles]

If ``--out-dir`` is omitted, output files are written next to the input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Heuristic keyword list for "key column" detection
# ---------------------------------------------------------------------------

_KEY_COLUMN_KEYWORDS = [
    "facility",
    "entity",
    "contract",
    "product",
    "group",
    "vendor",
    "manufacturer",
    "description",
    "date",
    "spend",
    "quantity",
    "reference",
    "price",
    "category",
    "code",
    "id",
    "name",
    "type",
    "status",
    "amount",
    "total",
    "unit",
    "ndc",
    "invoice",
]


def _detect_key_columns(columns: List[str]) -> List[str]:
    """Return columns whose names match any heuristic keyword."""
    return [
        c
        for c in columns
        if any(k in c.lower() for k in _KEY_COLUMN_KEYWORDS)
    ]


def _col_dtype_label(series: pd.Series) -> str:
    """Classify a column as numeric / datetime / text / mixed / empty."""
    non_null = series.dropna()
    if len(non_null) == 0:
        return "empty"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # Try coercion for object columns.
    num_coerced = pd.to_numeric(non_null, errors="coerce")
    num_frac = num_coerced.notna().sum() / len(non_null)
    if num_frac > 0.8:
        return "numeric"

    try:
        dt_coerced = pd.to_datetime(non_null, errors="coerce")
        dt_frac = dt_coerced.notna().sum() / len(non_null)
        if dt_frac > 0.8:
            return "datetime"
    except Exception:
        pass

    return "text"


def _safe_stat(value: Any) -> Any:
    """Convert numpy/pandas scalars to JSON-safe Python types."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def profile_sheet(df: pd.DataFrame, name: str) -> Dict[str, Any]:
    """Profile a single DataFrame (sheet)."""
    cols = [str(c) for c in df.columns]

    col_profiles: List[Dict[str, Any]] = []
    for c in df.columns:
        cstr = str(c)
        series = df[c]
        non_null = int(series.notna().sum())
        dtype_label = _col_dtype_label(series)
        cardinality = int(series.nunique(dropna=True))

        profile: Dict[str, Any] = {
            "column": cstr,
            "dtype": dtype_label,
            "non_null": non_null,
            "null": int(series.isna().sum()),
            "cardinality": cardinality,
        }

        if dtype_label == "numeric":
            num = pd.to_numeric(series, errors="coerce").dropna()
            if len(num) > 0:
                profile["min"] = _safe_stat(num.min())
                profile["max"] = _safe_stat(num.max())
                profile["mean"] = _safe_stat(round(num.mean(), 4))

        if dtype_label == "datetime":
            try:
                dt = pd.to_datetime(series, errors="coerce").dropna()
                if len(dt) > 0:
                    profile["min_date"] = str(dt.min())
                    profile["max_date"] = str(dt.max())
            except Exception:
                pass

        col_profiles.append(profile)

    key_cols = _detect_key_columns(cols)

    # Sample rows.
    show_cols = key_cols[:12] if key_cols else cols[:12]
    sample_rows: List[Dict[str, Any]] = []
    if len(df) > 0:
        preview = df[show_cols].head(8).copy()
        preview = preview.fillna("")
        sample_rows = preview.to_dict(orient="records")
        # Ensure JSON-safe values.
        for row in sample_rows:
            for k, v in row.items():
                row[k] = _safe_stat(v) if not isinstance(v, str) else v

    return {
        "sheet": name,
        "rows": int(len(df)),
        "cols": int(len(cols)),
        "columns": cols,
        "column_profiles": col_profiles,
        "key_columns": key_cols,
        "sample_rows": sample_rows,
    }


def profile_workbook(xlsx_path: Path) -> Dict[str, Any]:
    """Profile all sheets in an Excel workbook.

    Returns a structured report dict.
    """
    xlsx_path = Path(xlsx_path).expanduser().resolve()
    if not xlsx_path.exists():
        raise FileNotFoundError(str(xlsx_path))

    xls = pd.ExcelFile(xlsx_path)
    sheets: List[Dict[str, Any]] = []

    for name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=name)
        sheets.append(profile_sheet(df, name))

    return {
        "file": str(xlsx_path),
        "file_name": xlsx_path.name,
        "sheet_count": len(xls.sheet_names),
        "sheets": sheets,
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(report: Dict[str, Any]) -> str:
    """Render a profile report dict as a Markdown string."""
    lines: List[str] = []
    lines.append(f"# Workbook Profile: {report['file_name']}")
    lines.append("")
    lines.append(f"- **File**: {report['file_name']}")
    lines.append(f"- **Sheets**: {report['sheet_count']}")
    lines.append("")

    for sheet in report["sheets"]:
        lines.append(f"## {sheet['sheet']}")
        lines.append("")
        lines.append(f"- **Rows**: {sheet['rows']:,}")
        lines.append(f"- **Columns**: {sheet['cols']}")

        key_cols = sheet.get("key_columns", [])
        if key_cols:
            lines.append(f"- **Key columns**: {', '.join(key_cols[:20])}")
        lines.append("")

        # Column profile table.
        col_profiles = sheet.get("column_profiles", [])
        if col_profiles:
            lines.append("### Column profiles")
            lines.append("")
            lines.append("| Column | Type | Non-null | Null | Cardinality | Stats |")
            lines.append("|--------|------|----------|------|-------------|-------|")
            for cp in col_profiles:
                stats_parts: List[str] = []
                if "min" in cp and "max" in cp:
                    stats_parts.append(f"min={cp['min']}, max={cp['max']}, mean={cp.get('mean', '')}")
                if "min_date" in cp and "max_date" in cp:
                    stats_parts.append(f"{cp['min_date']} → {cp['max_date']}")
                stats = "; ".join(stats_parts) or "—"
                lines.append(
                    f"| {cp['column']} | {cp['dtype']} | {cp['non_null']:,} | {cp['null']:,} | {cp['cardinality']:,} | {stats} |"
                )
            lines.append("")

        # Sample rows.
        sample_rows = sheet.get("sample_rows", [])
        if sample_rows:
            lines.append("### Sample rows (first 8)")
            lines.append("")
            for i, row in enumerate(sample_rows, 1):
                compact = "; ".join(f"{k}={v}" for k, v in row.items())
                lines.append(f"- {i}. {compact}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Profile an Excel workbook and output Markdown + JSON reports."
    )
    parser.add_argument("workbook", help="Path to .xlsx file")
    parser.add_argument(
        "--out-dir",
        default="",
        help="Output directory for reports. Defaults to same directory as the workbook.",
    )
    args = parser.parse_args(argv)

    xlsx_path = Path(args.workbook).expanduser().resolve()
    if args.out_dir:
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_dir = xlsx_path.parent

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = xlsx_path.stem

    report = profile_workbook(xlsx_path)

    json_path = out_dir / f"{stem}_profile.json"
    md_path = out_dir / f"{stem}_profile.md"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    md_path.write_text(render_markdown(report), encoding="utf-8")

    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
