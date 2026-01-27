# Skill: BigQuery Data Dictionaries

**Purpose:** Profile BigQuery tables and generate/update markdown data dictionaries with schema metadata and column statistics.

## When to use this skill
- Creating a new data dictionary for a BigQuery table
- Enriching an existing partial dictionary with profiling stats (nulls, distinct counts, top values)
- Understanding an unfamiliar table's structure and data distribution

## Workflow Phases

### Phase 1: Schema Extraction
1. Use `mcp_bigquery_get_table_info` to retrieve the full schema (column names + types).
2. If the table has many columns (50+), note that profiling queries will need batching.

### Phase 2: Generate Profiling SQL
Use `tools/bigquery-profiling/gen_profiling_sql.py`:
```bash
python tools/bigquery-profiling/gen_profiling_sql.py \
  --project <project_id> \
  --dataset <dataset_id> \
  --table <table_id> \
  --schema-json <path_to_schema.json> \
  --output <output.sql>
```

**Key patterns in the generated SQL:**
- `COUNTIF(col IS NULL)` for null counts
- `APPROX_COUNT_DISTINCT(col)` for distinct counts
- `APPROX_TOP_COUNT(CAST(col AS STRING), 5)` for top values

**Critical:** All `APPROX_TOP_COUNT` inputs are CAST to STRING to avoid `UNION ALL` type mismatches.

### Phase 3: Execute Queries
1. Run the SQL via `mcp_bigquery_execute_sql`.
2. If the query is too large (>50 columns), split into batches of ~40 columns each.
3. Combine results into a single NDJSON file (one JSON object per line).

### Phase 4: Update Markdown Dictionary
Use `tools/bigquery-profiling/update_dictionary.py`:
```bash
python tools/bigquery-profiling/update_dictionary.py \
  <path_to_dictionary.md> \
  <profiling_results.json> \
  [--total-rows N]
```

The script injects/updates:
- `- Type: \`DTYPE\``
- `- Nulls: N (X.XX%)`
- `- Distinct: N`
- `- Top values: val1 (count), val2 (count), ...`

## Recovery Rules

### Type mismatch in UNION ALL
- **Symptom:** `Column 4 in UNION ALL has incompatible types`
- **Cause:** `APPROX_TOP_COUNT` returns `ARRAY<STRUCT<value T, count INT64>>` where T varies by column type
- **Fix:** Ensure ALL columns use `APPROX_TOP_COUNT(CAST(col AS STRING), 5)`

### Query too large / timeout
- **Symptom:** Query exceeds size limits or times out
- **Fix:** Reduce batch size (try 30 or 20 columns per batch)

### Column not found in markdown
- **Symptom:** Script doesn't update a column
- **Cause:** Column header format mismatch (e.g., grouped columns like `### col1 / col2 / col3`)
- **Fix:** Grouped columns need manual splitting OR the script only handles exact `### column_name` matches

### Missing descriptions
- **Symptom:** Profiling stats added but no description
- **Cause:** The source markdown lacked a `- Description:` line for that column
- **Fix:** Add placeholder descriptions before running the update script

## Data Dictionary Template
See `docs/data_dictionaries/_TEMPLATE.md` for the standard structure.

## Tool Reference
| Tool | Location | Purpose |
|------|----------|---------|
| `gen_profiling_sql.py` | `tools/bigquery-profiling/` | Generate profiling SQL from schema |
| `update_dictionary.py` | `tools/bigquery-profiling/` | Inject profiling stats into markdown |

## Privacy / Safety
- Do not include actual data values that could be PII in the dictionary (top values are aggregated counts, generally safe)
- If a column contains sensitive data (SSN, email, etc.), note it in the description and consider omitting top values
- Store profiling results as run-local artifacts unless the dictionary itself is being committed

## Example End-to-End

```bash
# 1. Extract schema (via MCP tool or manual query)
# 2. Generate SQL
python tools/bigquery-profiling/gen_profiling_sql.py \
  --project abi-inbound-prod \
  --dataset abi_inbound_bq_stg_purchasing_rx_wholesaler_sales \
  --table report_builder \
  --schema-json schema.json \
  --output profiling.sql

# 3. Execute via BigQuery MCP (or bq CLI)
# 4. Update dictionary
python tools/bigquery-profiling/update_dictionary.py \
  docs/data_dictionaries/my_table.md \
  profiling_results.json \
  --total-rows 690000000
```
