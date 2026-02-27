#!/usr/bin/env python3
"""
Create a new markdown data dictionary from BigQuery schema and profiling statistics.

Usage:
  python create_dictionary.py --schema <schema.json> --stats <stats.json> --output <output.md>

Schema JSON format:
  {
    "FullID": "project.dataset.table",
    "Description": "Table description",
    "Schema": [
      {"Name": "col1", "Type": "STRING", "Description": "desc"},
      ...
    ]
  }

Stats JSON format:
  {
    "total_rows": 1000,
    "col1_distinct": 10,
    "col1_nulls": 5,
    "col1_top": [{"value": "A", "count": 5}, ...]
  }
"""

import argparse
import json
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

def main():
    parser = argparse.ArgumentParser(description='Create a markdown data dictionary.')
    parser.add_argument('--schema', required=True, help='Path to schema JSON file')
    parser.add_argument('--stats', required=True, help='Path to stats JSON file')
    parser.add_argument('--output', required=True, help='Path to output Markdown file')
    args = parser.parse_args()

    # Load Schema
    try:
        with open(args.schema, 'r') as f:
            schema_data = json.load(f)
    except Exception as e:
        print(f"Error loading schema file: {e}")
        sys.exit(1)

    # Load Stats
    try:
        with open(args.stats, 'r') as f:
            stats_data = json.load(f)
    except Exception as e:
        print(f"Error loading stats file: {e}")
        sys.exit(1)

    table_id = schema_data.get('FullID', 'Unknown Table ID')
    table_desc = schema_data.get('Description', 'No description provided.')
    
    # Handle both schema structures (direct list or nested under "Schema")
    if isinstance(schema_data, list):
        fields = schema_data
    else:
        fields = schema_data.get('Schema', [])

    total_records = stats_data.get('total_rows', 'Unknown')
    if isinstance(total_records, int):
        total_records_display = f"{total_records:,}"
    else:
        # try to cast if it's a string number
        try:
           total_records = int(str(total_records).replace(',', ''))
           total_records_display = f"{total_records:,}"
        except:
           total_records_display = str(total_records)
           total_records = None # Cannot calc percentages if not int

    # Extract short name for title
    short_name = table_id.split('.')[-1]

    markdown_lines = []
    markdown_lines.append(f"# Data Dictionary: {short_name}")
    markdown_lines.append(f"**Table**: `{table_id}`")
    markdown_lines.append(f"**Description**: {table_desc}")
    markdown_lines.append(f"**Total Records**: {total_records_display}")
    markdown_lines.append("")
    markdown_lines.append("## Columns")

    for i, field in enumerate(fields):
        field_name = field.get('Name')
        field_type = field.get('Type')
        field_desc = field.get('Description', '')

        if not field_name:
            continue

        if i > 0:
            markdown_lines.append("")
            markdown_lines.append("---")

        # Get stats
        distinct_key = f"{field_name}_distinct"
        nulls_key = f"{field_name}_nulls"
        top_key = f"{field_name}_top"

        distinct_count = stats_data.get(distinct_key, 'N/A')
        null_count = stats_data.get(nulls_key, 'N/A')
        top_values = stats_data.get(top_key, [])
        
        # Format counts with percentages
        null_display = format_count_pct(null_count, total_records)
        
        # Distinct count does NOT get percentage
        try:
             distinct_display = f"{int(str(distinct_count).replace(',', '')):,}"
        except:
             distinct_display = str(distinct_count)

        markdown_lines.append(f"### {field_name}")
        markdown_lines.append(f"- **Type**: `{field_type}`")
        markdown_lines.append(f"- **Description**: {field_desc}")
        markdown_lines.append(f"- **Distinct Values**: {distinct_display}")
        markdown_lines.append(f"- **Nulls**: {null_display}")

        if top_values:
            markdown_lines.append(f"- **Top Values**:")
            for val_obj in top_values:
                val = val_obj.get('value')
                # Explicit check for None/Null
                if val is None:
                    val_display = "NULL"
                else:
                    val_display = str(val)
                
                count = val_obj.get('count', 0)
                count_display = format_count_pct(count, total_records)

                markdown_lines.append(f"  - `{val_display}`: {count_display}")

    with open(args.output, 'w') as f:
        f.write('\n'.join(markdown_lines))

    print(f"Successfully created data dictionary at {args.output}")

if __name__ == "__main__":
    main()
