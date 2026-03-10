import json
import re
import sys
import os

def update_markdown(markdown_path, metadata_list):
    """
    Updates the markdown file with metadata (Type, Nulls, Distinct, Top Values).
    metadata_list: list of dicts with keys: col_name, data_type, null_count, distinct_count, top_values
    """
    with open(markdown_path, 'r') as f:
        content = f.read()

    # Total rows estimate (hardcoded or passed? We'll use a fixed value for % calc)
    TOTAL_ROWS = 689960560

    for meta in metadata_list:
        col = meta['col_name']
        dtype = meta.get('data_type', 'UNKNOWN')
        nulls = meta.get('null_count', 0)
        distinct = meta.get('distinct_count', 0)
        top_vals_raw = meta.get('top_values', [])
        
        # Format Top Values
        # top_vals_raw is usually [{'value': 'X', 'count': 123}, ...]
        top_str = ""
        if top_vals_raw:
            items = []
            for item in top_vals_raw:
                val = item.get('value', 'NULL')
                cnt = item.get('count', 0)
                items.append(f"{val} ({cnt:,})")
            top_str = ", ".join(items)

        # Regex to find the column section
        # Finds "### colname" followed by "- Description:"
        # We want to insert the metadata after "### colname" and before "- Description"
        # OR insert it after "- Description: ..." line?
        # The exemplar has:
        # ### Column
        # - Type: ...
        # - Description: ...
        # - Nulls: ...
        
        # My current file has:
        # ### column
        # - Description: ...
        
        # I want to inject/replace to get:
        # ### column
        # - Type: DTYPE
        # - Description: ...
        # - Nulls: N (X%)
        # - Distinct: N
        # - Top Values: ...
        
        pattern = re.compile(f"(### {col}\\n)(.*?)(- Description: .*?\\n)", re.DOTALL)
        
        # percentages
        pct = (nulls / TOTAL_ROWS) * 100
        
        new_block = f"- Type: `{dtype}`\n"
        extra_meta = f"- Nulls: {nulls:,} ({pct:.2f}%)\n- Distinct: {distinct:,}\n"
        if top_str and dtype == 'STRING':
             extra_meta += f"- Top values: {top_str}\n"

        # Check if already updated (avoid duplication if run multiple times)
        # simplistic check: if "- Type:" is already there?
        # Actually, let's just replace the whole block structure if we can matches reliably.
        
        # If the file currently is:
        # ### col
        # - Description: foo
        
        # We replace "### col\n" with "### col\n- Type: ...\n" and append the rest after description.
        
        # Let's try to match the WHOLE block relative to the header.
        # But description length varies.
        
        # Strategy: Find "### col\n" and replacing it is risky if I lose the description.
        # Better: Find "### col" and look for "- Description: (.*)"
        
        # Let's use string replacement for the header line + description line?
        # No, let's use a regex that captures the description line.
        
        # Regex:
        # (### col\s+)(- Description: .*)
        # Replace with:
        # \1- Type: `TYPE`\n\2\n- Nulls: ...
        
        regex = r"(### " + re.escape(col) + r"\s+)(- Description: .*)"
        replacement = (
            f"### {col}\n"
            f"- Type: `{dtype}`\n"
            f"\\2\n"
            f"{extra_meta}"
        )
        
        # Ensure we don't double-add if run twice (check if Type is already there?)
        # For now, assume clean slate or just overwrite.
        # But if I overwrite, I need to match the EXISTING "Type/Nulls" lines to remove them first?
        # The current file does NOT have them.
        
        content = re.sub(regex, replacement, content, count=1)

    with open(markdown_path, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_dictionary.py <md_file> <json_file>")
        sys.exit(1)
        
    md_file = sys.argv[1]
    json_file = sys.argv[2]
    
    with open(json_file, 'r') as f:
        # JSON file might be line-delimited JSON objects from the tool output?
        # The tool likely returns lines of JSON.
        data = []
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    update_markdown(md_file, data)
