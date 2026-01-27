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
  - Top values: val1 (count), val2 (count), ...
"""

import argparse
import json
import re
import sys


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


def format_top_values(top_vals: list[dict]) -> str:
    """Format top values as 'val1 (count), val2 (count), ...'"""
    if not top_vals:
        return ""
    items = []
    for item in top_vals:
        val = item.get('value')
        if val is None:
            val = "None"
        cnt = item.get('count', 0)
        items.append(f"{val} ({cnt:,})")
    return ", ".join(items)


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
        
        # Calculate null percentage
        pct = (nulls / total_rows) * 100 if total_rows > 0 else 0
        
        # Format top values string
        top_str = format_top_values(top_vals_raw)
        
        # Build metadata lines
        extra_meta = f"- Nulls: {nulls:,} ({pct:.2f}%)\n- Distinct: {distinct:,}\n"
        if top_str:
            extra_meta += f"- Top values: {top_str}\n"
        
        # Regex to find column section and inject metadata
        # Matches: ### column_name\n(optional existing Type/Nulls lines)\n- Description: ...
        # We replace to: ### column_name\n- Type: ...\n- Description: ...\n- Nulls: ...\n...
        
        # Pattern: capture the header and description line
        regex = r"(### " + re.escape(col) + r"\s+)(- Description: .*)"
        
        replacement = (
            f"### {col}\n"
            f"- Type: `{dtype}`\n"
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
        # Try to estimate from the data (sum of first column's top values)
        first_col = metadata[0]
        top_vals = first_col.get('top_values', [])
        if top_vals:
            # This is a rough estimate - assumes top 5 values cover most data
            # Not reliable, but better than 0
            total_rows = sum(v.get('count', 0) for v in top_vals) * 10
            print(f"Estimated total rows: ~{total_rows:,} (rough estimate)", file=sys.stderr)
    
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
