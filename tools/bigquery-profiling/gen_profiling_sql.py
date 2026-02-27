#!/usr/bin/env python3
"""
Generate BigQuery profiling SQL from a schema JSON file.

Usage:
  python gen_profiling_sql.py \
    --project <project_id> \
    --dataset <dataset_id> \
    --table <table_id> \
    --schema-json <schema.json> \
    [--output <output.sql>]

Schema JSON format:
  {
    "Schema": [
      {"Name": "col1", "Type": "STRING"},
      ...
    ]
  }
  OR list of dicts: [{"Name": "col1", ...}, ...]

Output: SQL query to profile all columns (distinct, nulls, top 5).
"""

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description='Generate BigQuery profiling SQL.')
    parser.add_argument('--project', required=True, help='GCP Project ID')
    parser.add_argument('--dataset', required=True, help='BigQuery Dataset ID')
    parser.add_argument('--table', required=True, help='BigQuery Table ID')
    parser.add_argument('--schema-json', required=True, help='Path to schema JSON file')
    parser.add_argument('--output', help='Path to output SQL file')

    args = parser.parse_args()

    # Load Schema
    try:
        with open(args.schema_json, 'r') as f:
            schema_data = json.load(f)
    except Exception as e:
        print(f"Error loading schema file: {e}")
        sys.exit(1)

    # Handle different schema formats
    if isinstance(schema_data, list):
        fields = schema_data
    else:
        fields = schema_data.get('Schema', [])
        # Fallback if Schema key missing but maybe it's the direct dict (unlikely for BQ schema downloads but possible)
        if not fields and isinstance(schema_data, dict):
            # If it's the specific output from mcp_bigquery_get_table_info often it has "Schema" key.
            pass

    if not fields:
        print("No fields found in schema.")
        sys.exit(1)

    select_clauses = []
    
    for field in fields:
        # Support both "Name" (from API) and "name" (common convention)
        name = field.get('Name') or field.get('name')
        if not name:
            continue
            
        # 1. Distinct count
        select_clauses.append(f"APPROX_COUNT_DISTINCT({name}) as {name}_distinct")
        
        # 2. Null count
        select_clauses.append(f"COUNTIF({name} IS NULL) as {name}_nulls")
        
        # 3. Top Values (Approx)
        select_clauses.append(f"APPROX_TOP_COUNT({name}, 5) as {name}_top")

    full_table_id = f"`{args.project}.{args.dataset}.{args.table}`"
    
    sql = "SELECT \n"
    sql += ",\n".join(select_clauses)
    sql += f"\nFROM {full_table_id}"

    if args.output:
        with open(args.output, 'w') as f:
            f.write(sql)
        print(f"SQL generated at {args.output}")
    else:
        print(sql)

if __name__ == "__main__":
    main()
