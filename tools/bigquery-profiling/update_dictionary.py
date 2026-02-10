#!/usr/bin/env python3
"""
Update a markdown data dictionary with profiling statistics.

Usage:
  python update_dictionary.py <markdown_file> <profiling_results.json> [--total-rows N]

Profiling results format (NDJSON, one object per line):
  {"col_name": "column1", "data_type": "STRING", "null_count": 1000, "distinct_count": 50, "top_values": [{"value": "X", "count": 500}, ...]}
  ...

The script finds column sections in the markdown (### column_name) and injects/updates:
  - Type: `DTYPE`
  - Nulls: N (X.XX%)
  - Distinct: N
  - Top values: Value (Count X.XX%), ...
"""

import argparse
import json
import re
import sys

def format_count_pct(count_val, total):
    """Format a count and its percentage of total."""
    try:
        c = int(str(count_val).replace(',', ''))
        c_str = f"{c:,}"
        if total and isinstance(total, int) and total > 0:
            pct = (c / total) * 100
            if pct == 0 and c > 0:
                    pct_str = "(<0.01%)"
            elif pct == 0:
                    pct_str = "(0%)"
            elif pct < 0.01:
                pct_str = "(<0.01%)"
            else:
                pct_str = f"({pct:.2f}%)"
            return f"{c_str} {pct_str}"
        return c_str
    except (ValueError, TypeError):
        return str(count_val)

def load_profiling_results(json_path: str) -> list[dict]:
    """Load profiling results from NDJSON file."""
    results = []
    with open(json_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line: {e}", file=sys.stderr)
    return results


def format_top_values(top_vals: list[dict], total_rows: int) -> str:
    """Format top values as a markdown list with percentages."""
    if not top_vals:
        return ""
    
    lines = []
    for item in top_vals:
        val = item.get('value')
        if val is None:
            val = "NULL"
        
        # Ensure value is string
        val_str = str(val)
        
        cnt = item.get('count', 0)
        cnt_display = format_count_pct(cnt, total_rows)
        
        lines.append(f"  - `{val_str}`: {cnt_display}")
    
    return "\n".join(lines)


def update_markdown(content: str, metadata_list: list[dict], total_rows: int) -> str:
    """
    Update markdown content with profiling metadata.
    
    Finds sections matching "### column_name" followed by "- Description: ..."
    and injects Type, Nulls, Distinct, Top values lines.
    """
    for meta in metadata_list:
        col = meta.get('col_name', '')
        if not col:
            continue
            
        dtype = meta.get('data_type', 'UNKNOWN')
        nulls = meta.get('null_count', 0)
        distinct = meta.get('distinct_count', 0)
        top_vals_raw = meta.get('top_values', [])
        
        # Format counts
        null_display = format_count_pct(nulls, total_rows)
        try:
             distinct_display = f"{int(str(distinct).replace(',', '')):,}"
        except:
             distinct_display = str(distinct)
        
        # Format top values string
        top_str = format_top_values(top_vals_raw, total_rows)
        
        # Build metadata lines
        # Uses Standard Format
        extra_meta = f"- **Distinct Values**: {distinct_display}\n"
        extra_meta += f"- **Nulls**: {null_display}\n"
        
        if top_str:
            extra_meta += f"- **Top Values**:\n{top_str}\n"
        
        # Regex to find column section and inject metadata
        # Supports old "- Description:" and new "- **Description**:"
        # Also handles cases where Type might already exist or not.
        # Strategy: Match Header, then look for Description line.
        
        regex = r"(### " + re.escape(col) + r"\s*\n)(?:[\s\S]*?)(\- \*\*?Description\*\*?: .*)"
        
        replacement = (
            f"### {col}\n"
            f"- **Type**: `{dtype}`\n"
            f"\\2\n"
            f"{extra_meta}"
        )
        
        # Apply replacement (only first match per column)
        content = re.sub(regex, replacement, content, count=1)
    
    return content


def main():
    parser = argparse.ArgumentParser(
        description="Update markdown data dictionary with profiling stats"
    )
    parser.add_argument("markdown_file", help="Path to markdown dictionary file")
    parser.add_argument("profiling_json", help="Path to profiling results (NDJSON)")
    parser.add_argument("--total-rows", type=int, default=0,
                        help="Total row count for null percentage calculation")
    
    args = parser.parse_args()
    
    # Load profiling results
    metadata = load_profiling_results(args.profiling_json)
    if not metadata:
        print("Error: No profiling data found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded profiling data for {len(metadata)} columns", file=sys.stderr)
    
    # Infer total rows from the first column's null + non-null if not provided
    total_rows = args.total_rows
    if total_rows == 0 and metadata:
        # Heuristic: sum of all top_values counts approximates total rows
        # But this is unreliable. Better to require --total-rows or read from file.
        # For now, use a safe fallback or warn.
        print("Warning: --total-rows not specified. Null percentages may be inaccurate.", 
              file=sys.stderr)
    
    # Read markdown file
    with open(args.markdown_file, 'r') as f:
        content = f.read()
    
    # Update content
    updated = update_markdown(content, metadata, total_rows)
    
    # Write back
    with open(args.markdown_file, 'w') as f:
        f.write(updated)
    
    print(f"Updated {args.markdown_file}", file=sys.stderr)

if __name__ == "__main__":
    main()
