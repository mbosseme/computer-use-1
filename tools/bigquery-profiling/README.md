# BigQuery Profiling Tools

Tools for profiling BigQuery tables and generating/updating data dictionaries.

## Tools

### gen_profiling_sql.py

Generates profiling SQL from a schema JSON file.

**Usage:**
```bash
python gen_profiling_sql.py \
  --project <project_id> \
  --dataset <dataset_id> \
  --table <table_id> \
  --schema-json <schema.json> \
  [--output <output.sql>] \
  [--batch-size 40]
```

**Schema JSON format (NDJSON):**
```json
{"column_name": "col1", "data_type": "STRING"}
{"column_name": "col2", "data_type": "INT64"}
```

**Output:** SQL queries with `UNION ALL` that return:
- `col_name`: Column name
- `data_type`: Column type
- `null_count`: Count of NULL values
- `distinct_count`: Approximate distinct count
- `top_values`: Top 5 most frequent values (as STRING)

### update_dictionary.py

Updates a markdown data dictionary with profiling statistics.

**Usage:**
```bash
python update_dictionary.py <markdown_file> <profiling_results.json> [--total-rows N]
```

**Profiling results format (NDJSON):**
```json
{"col_name": "column1", "data_type": "STRING", "null_count": 1000, "distinct_count": 50, "top_values": [{"value": "X", "count": 500}]}
```

**What it updates:**
- `- Type: \`DTYPE\``
- `- Nulls: N (X.XX%)`
- `- Distinct: N`
- `- Top values: val1 (count), val2 (count), ...`

## Workflow

1. **Extract schema** from BigQuery (via MCP `get_table_info` or `bq show --schema`)
2. **Generate SQL** with `gen_profiling_sql.py`
3. **Execute queries** via BigQuery MCP or `bq query`
4. **Save results** as NDJSON
5. **Update dictionary** with `update_dictionary.py`

## Key Technical Notes

- **APPROX_TOP_COUNT type safety:** All values are CAST to STRING to avoid `UNION ALL` type mismatches across columns of different types.
- **Batching:** For tables with 50+ columns, the SQL is split into batches (default: 40 columns per batch) to avoid query size limits.
- **Idempotent updates:** The update script can be run multiple times; it will overwrite existing stats.

## Related

- **Skill file:** `.github/skills/bigquery-data-dictionaries/SKILL.md`
- **Template:** `docs/data_dictionaries/_TEMPLATE.md`
