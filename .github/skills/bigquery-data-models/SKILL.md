# Skill: BigQuery Data Models

> **When to load:** Any task involving BigQuery queries, data extraction, or analysis against the documented data models.

---

## Overview

This skill covers:
- Authenticating with BigQuery (Application Default Credentials)
- Configuring and using the BigQuery MCP toolbox
- Finding and using data dictionaries for documented tables
- Common query patterns and best practices

---

## 1. Authentication (Non-Negotiable)

**Application Default Credentials (ADC) only.** Never embed secrets or commit service account keys.

```bash
# User must run this before BigQuery access works
gcloud auth application-default login

# Set default project (if needed)
export BIGQUERY_PROJECT_ID=matthew-bossemeyer
```

If auth fails, prompt the user to run the `gcloud` command above.

---

## 2. MCP Toolbox Configuration

### VS Code MCP Server Setup

The BigQuery MCP server should be configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "bigquery": {
      "command": "toolbox",
      "args": ["--prebuilt", "bigquery", "--stdio"]
    }
  }
}
```

**Naming convention:** Use `bigquery` as the server name (or `bigquery_<workspace>` if disambiguation is needed).

### Available MCP Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `list_dataset_ids` | List datasets in a project | `project` |
| `list_table_ids` | List tables in a dataset | `project`, `dataset` |
| `get_table_info` | Get schema + metadata | `project`, `dataset`, `table` |
| `execute_sql` | Run SQL queries | `sql`, `dry_run` (optional) |
| `ask_data_insights` | Natural language exploration | `question` |

### Recommended Workflow

1. **Orient to schema first:**
   ```
   Use get_table_info to understand columns before querying.
   ```

2. **Start with bounded queries:**
   ```sql
   -- Always include LIMIT when exploring
   SELECT * FROM `table` WHERE ... LIMIT 100
   ```

3. **Use dry_run for cost estimation:**
   ```
   execute_sql with dry_run=true to check bytes scanned before running large queries.
   ```

4. **Profile before aggregating:**
   ```sql
   -- Check distinct values and nulls
   SELECT column, COUNT(*) FROM table GROUP BY 1 ORDER BY 2 DESC LIMIT 20
   ```

---

## 3. Data Dictionaries

Before writing SQL, check for a data dictionary in `docs/data_dictionaries/`.

### Finding the Right Dictionary

Dictionaries are named by full table path:
```
docs/data_dictionaries/<project>.<dataset>.<table>.md
```

### What Dictionaries Contain

- Column names, types, and business meanings
- Null rates and distinct counts
- Common filter patterns (e.g., exclude test entities)
- Example queries
- Join relationships to other tables

### Current Data Models

| Model | Full Table Path | Use Case |
|-------|-----------------|----------|
| Transaction Analysis | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` | Provider-side purchasing visibility |
| Supplier Spend | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_supplier_sales.supplier_spend` | Manufacturer-reported contract sales |
| SASF DHC Join | `matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join` | Facility/IDN enrichment, hospital metadata |

For detailed model documentation, see [Premier Data Models Handoff](../../../docs/PREMIER_DATA_MODELS_HANDOFF.md).

---

## 4. Common Query Patterns

### Standard Exclusion Filter (Apply Always)

```sql
-- Exclude test/demo entities from health system tables
WHERE Health_System_Name NOT LIKE '%TEST%'
  AND Health_System_Name NOT LIKE '%PREMIER%'
  AND Health_System_Name NOT LIKE '%DEMO%'
```

### Capital Equipment Identification (Transaction Analysis)

No explicit "Capital" flag exists; use this heuristic:

```sql
-- Tier 1: Price threshold (strongest signal)
WHERE Base_Each_Price > 25000

-- Tier 2: Unmatched proxy (capital often non-contract)
AND Spend_Type IN ('NON CONTRACT', 'CATEGORIZED ONLY')

-- Tier 3: Exclude services/software
AND Product_Description NOT REGEXP_CONTAINS(
  r'(?i)SERVICE|MAINTENANCE|WARRANTY|AGREEMENT|REPAIR|SOFTWARE|LICENSE|RENEWAL'
)
```

### Timing Field Decoding (Supplier Spend)

The `Spend_Period_YYYYQMM` field encodes year, quarter, and month:
```
2024410 = 2024, Q4, October (month 10)
```

Extract components:
```sql
CAST(FLOOR(Spend_Period_YYYYQMM / 1000) AS INT64) as year,
MOD(CAST(FLOOR(Spend_Period_YYYYQMM / 100) AS INT64), 10) as quarter,
MOD(Spend_Period_YYYYQMM, 100) as month_num
```

---

## 5. Privacy & Compliance Guardrails

**Aggregated data only.** Never export or display at the individual facility level:
- `Facility_Name`
- `Health_System_Name`
- `Facility_Hin` (Hospital Identification Number)

When building reports, always aggregate to:
- Category level
- Manufacturer level
- Time period level
- Geographic region (state) level

---

## 6. Troubleshooting

### Auth Errors
- Run `gcloud auth application-default login`
- Verify `BIGQUERY_PROJECT_ID` is set if project not specified in queries

### MCP Server Not Found
- Check `.vscode/mcp.json` includes the `bigquery` server config
- Ensure `toolbox` CLI is installed and on PATH

### Query Timeouts / Cost
- Use `dry_run=true` first to estimate bytes scanned
- Add tighter date filters or LIMIT clauses
- Consider materializing intermediate results

---

## 7. Related Resources

- [Data Dictionaries Index](../../../docs/data_dictionaries/README.md)
- [MCP Toolbox Guide](../../../docs/MCP_TOOLBOX_GUIDE.md) — Detailed how-to for BigQuery MCP server configuration, tool usage, and troubleshooting
- [Premier Data Models Handoff](../../../docs/PREMIER_DATA_MODELS_HANDOFF.md) — Domain-specific patterns for healthcare purchasing data

---

*Load this skill when working with BigQuery data models.*
