#!/usr/bin/env python3
"""
Generate BigQuery profiling SQL from a schema JSON file.

Usage:
  python gen_profiling_sql.py \
    --project <project_id> \
    --dataset <dataset_id> \
    --table <table_id> \
    --schema-json <schema.json> \
    [--output <output.sql>] \
    [--batch-size 40]

Schema JSON format (NDJSON, one object per line):
  {"column_name": "col1", "data_type": "STRING"}
  {"column_name": "col2", "data_type": "INT64"}
  ...

Or standard JSON array:
  [{"column_name": "col1", "data_type": "STRING"}, ...]

Output: SQL with UNION ALL batches for profiling (nulls, distinct, top values).
"""

import argparse
import json
import sys


def load_schema(schema_path: str) -> list[dict]:
    """Load schema from JSON file (supports NDJSON or array format)."""
    with open(schema_path, 'r') as f:
        content = f.read().strip()
    
    # Try parsing as JSON array first
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    
    # Fall back to NDJSON (one object per line)
    columns = []
    for line in content.split('\n'):
        line = line.strip()
        if line:
            try:
                columns.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON line: {line}", file=sys.stderr)
    return columns


def make_profiling_sql(columns: list[dict], table_fqn: str) -> str:
    """
    Generate a single UNION ALL query for profiling all columns.
    
    Each column gets:
      - col_name (literal)
      - data_type (literal)
      - null_count (COUNTIF)
      - distinct_count (APPROX_COUNT_DISTINCT)
      - top_values (APPROX_TOP_COUNT with CAST to STRING for type safety)
    """
    parts = []
    for col in columns:
        name = col['column_name']
        dtype = col.get('data_type', 'UNKNOWN')
        
        # CRITICAL: Cast to STRING for APPROX_TOP_COUNT to avoid UNION ALL type mismatches
        top_val_expr = f"APPROX_TOP_COUNT(CAST(`{name}` AS STRING), 5)"
        
        sql = f"""SELECT
  '{name}' AS col_name,
  '{dtype}' AS data_type,
  COUNTIF(`{name}` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`{name}`) AS distinct_count,
  {top_val_expr} AS top_values
FROM `{table_fqn}`"""
        parts.append(sql)
    
    return "\nUNION ALL\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Generate BigQuery profiling SQL")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--dataset", required=True, help="BigQuery dataset ID")
    parser.add_argument("--table", required=True, help="BigQuery table ID")
    parser.add_argument("--schema-json", required=True, help="Path to schema JSON file")
    parser.add_argument("--output", help="Output SQL file (default: stdout)")
    parser.add_argument("--batch-size", type=int, default=40, 
                        help="Max columns per batch (default: 40)")
    
    args = parser.parse_args()
    
    # Build fully qualified table name
    table_fqn = f"{args.project}.{args.dataset}.{args.table}"
    
    # Load schema
    columns = load_schema(args.schema_json)
    if not columns:
        print("Error: No columns found in schema file", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded {len(columns)} columns from schema", file=sys.stderr)
    
    # Generate SQL in batches
    output_lines = []
    batch_size = args.batch_size
    
    for i in range(0, len(columns), batch_size):
        batch = columns[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        output_lines.append(f"-- Batch {batch_num}: columns {i+1} to {i+len(batch)}")
        output_lines.append(make_profiling_sql(batch, table_fqn))
        output_lines.append("\n-- END BATCH --\n")
    
    result = "\n".join(output_lines)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"Wrote SQL to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
