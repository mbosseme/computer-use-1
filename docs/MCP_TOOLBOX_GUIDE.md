# MCP Toolbox for BigQuery Guide

Authoritative HOW-TO for using BigQuery through MCP in this repo. We now standardize on the **prebuilt BigQuery server + user Application Default Credentials (ADC)**. The earlier custom `tools.yaml` approach remains optional for curated static queries.

> **Server Name:** `bigquery` (simple default for single-repo usage)
> **Alternative:** `bigquery_<workspace_root_folder_name>` if running multiple repos simultaneously
> **Scope:** Prebuilt BigQuery toolset (discovery, insights) + optional custom static tools

## 1. Overview
The MCP Toolbox integration enables Copilot (or any MCP-compliant client) to run predefined BigQuery queries safely:
- **Fast schema inspection** (flat + nested fields)
- **Sample data retrieval**
- **Ad-hoc, bounded exploration**

Two launch modes:
| Mode | Command | Purpose |
|------|---------|---------|
| UI (HTTP) | `toolbox --tools-file tools.yaml --ui` | Local web UI & API for manual exploration/debug |
| STDIO (MCP) | `toolbox --tools-file tools.yaml --stdio` | Headless integration consumed by Copilot Chat |

## 2. Architecture Summary
Two layers (choose what you need):
1. **Prebuilt server (recommended)** — launched with `toolbox --prebuilt bigquery --stdio`. Provides rich, maintained toolset (listing, metadata, execute_sql, ask_data_insights, forecast, etc.).
2. **Custom YAML (optional)** — `toolbox --tools-file tools.yaml` for hand-curated static SQL tools (no advanced semantic features).

### Server Naming
VS Code config (prebuilt) lives in `.vscode/mcp.json` under server id `bigquery`.

**Required configuration:** The BigQuery prebuilt server requires the `BIGQUERY_PROJECT` environment variable. Example `.vscode/mcp.json`:

```json
{
  "servers": {
    "bigquery": {
      "command": "/opt/homebrew/bin/toolbox",
      "args": ["--prebuilt", "bigquery", "--stdio"],
      "env": {
        "BIGQUERY_PROJECT": "matthew-bossemeyer",
        "BIGQUERY_PROJECT_ID": "matthew-bossemeyer"
      }
    }
  }
}
```

**Multi-repo usage:** When working with multiple repositories simultaneously, use workspace-specific naming to prevent collisions:
```
bigquery_<workspace_root_folder_name>
```

For example, `bigquery_computer_use_1` or `bigquery_my_project`. Update the server name in `.vscode/mcp.json` accordingly.

Authentication: User ADC (gcloud) only. Service account JSON and `GOOGLE_APPLICATION_CREDENTIALS` are not supported.
Memory: Operational notes & incidents go to `SUMMARY_OF_RECENT_ITERATION.md`.

## 3. Environment & Auth Setup (ADC Only)
```bash
gcloud auth application-default login
export BIGQUERY_PROJECT_ID=matthew-bossemeyer
```
If ADC is not present, requests will fail; guide users to run the gcloud command.

## 4. Launch Modes
### Launch Modes
| Mode | Recommended Use | Command |
|------|-----------------|---------|
| Prebuilt STDIO (MCP) | Daily interactive work (preferred) | `toolbox --prebuilt bigquery --stdio` |
| Custom YAML STDIO | Curated static tools | `toolbox --tools-file tools.yaml --stdio` |
| Custom YAML UI | Visual inspection / debugging | `toolbox --tools-file tools.yaml --ui` |

UI mode is optional; prebuilt mode currently focuses on stdio.

## 5. Prebuilt Tool Examples (subject to version)
Common names you should see via `listTools`:
- `execute_sql` — Execute SQL queries with optional dry-run mode
- `list_dataset_ids` — List all datasets in a project
- `list_table_ids` — List all tables in a dataset
- `get_dataset_info` — Get metadata for a specific dataset
- `get_table_info` — Get schema and metadata for a specific table
- `ask_data_insights` — Ask natural language questions about table data
- `forecast` — Forecast time series data

Exact set may evolve; always rely on `/mcp bigquery listTools`.

**Verified Working** (as of 2025-11-12): All core tools tested successfully with project `matthew-bossemeyer`.

## 6. Usage via Copilot Chat (Prebuilt)
**Note:** All examples use `bigquery` as the server name. If you've configured a workspace-specific name, replace accordingly.

List tools:
```
/mcp bigquery listTools
```
Dataset IDs:
```
/mcp bigquery callTool list_dataset_ids project="matthew-bossemeyer"
```
Tables in a dataset:
```
/mcp bigquery callTool list_table_ids project="matthew-bossemeyer" dataset="cdx_sample_size"
```
Dataset info:
```
/mcp bigquery callTool get_dataset_info project="matthew-bossemeyer" dataset="cdx_sample_size"
```
Table info:
```
/mcp bigquery callTool get_table_info project="matthew-bossemeyer" dataset="cdx_sample_size" table="sa_sf_dhc_join"
```
Execute bounded SQL:
```
/mcp bigquery callTool execute_sql sql="SELECT COUNT(*) FROM `matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join` LIMIT 1"
```
Execute SQL with dry run:
```
/mcp bigquery callTool execute_sql sql="SELECT * FROM `matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join` LIMIT 10" dry_run=true
```
Insight question:
```
/mcp bigquery callTool ask_data_insights user_query_with_context="What are the top hospital types by count?" table_references='[{"projectId":"matthew-bossemeyer","datasetId":"cdx_sample_size","tableId":"sa_sf_dhc_join"}]'
```

## 7. Optional: Custom YAML Tools
If you still need deterministic static queries, keep `tools.yaml` and run a second process. Add entries (kind `bigquery-sql` / `bigquery-execute-sql`) as before. Do **not** mix `--prebuilt` with `--tools-file` in one process. Service account JSON is not supported.

### Parameterized Execution
For more dynamic queries, create a `bigquery-execute-sql` tool and supply parameters at call time. Keep the tool generic:
```yaml
mini_adhoc:
  kind: bigquery-execute-sql
  source: bq
  description: Run a bounded ad-hoc query (must include LIMIT).
```
Invocation:
```
/mcp toolbox callTool mini_adhoc sql="SELECT * FROM `project.dataset.table` LIMIT 5"
```

## 8. Conventions & Best Practices
- **Naming**: prefix with dataset/topic (`provider_`, `agg_`, `schema_`).
- **Safety**: Always project columns explicitly for large tables; avoid `SELECT *` outside small LIMIT sampling.
- **Performance**: Include LIMIT early while exploring; remove only when necessary.
- **Clarity**: Add a description block for every tool, especially those used in automation.

## 9. Troubleshooting (Prebuilt Focus)
| Symptom | Cause | Fix |
|---------|-------|-----|
| `non-map value is specified` parse error | SQL lines not indented after `statement: |` | Indent each SQL line (2+ spaces) and restart |
| Empty tool list | Env vars missing or server not started | Export env vars; restart VS Code / process |
| Auth error / permission denied | Missing ADC or invalid service account | Re-auth (`gcloud auth application-default login`) or correct JSON path |
| Changes not detected | Hot reload missed whitespace-only diff | Full restart of Toolbox process |
| Slow query | Large scan or missing LIMIT | Narrow columns, add LIMIT / predicates |

## 10. Memory Entries (Operational Logging)
When you make a structural change or fix an incident:
1. Append a JSON line to `.mcp/memory.jsonl` with `type` (`Incident`, `Decision`, etc.).
2. Reference file and approximate line (`tools.yaml:NN`).
3. Keep body <= 3 sentences.

Example Incident:
```json
{"type":"Incident","title":"Toolbox YAML parse failure","tags":["toolbox","yaml"],"refs":["tools.yaml:54"],"body":"Parse error due to unindented SQL after statement pipe. Fixed by indenting lines and restarting."}
```

## 11. Security & Hygiene
- Never commit credentials. `.gitignore` protects common filenames.
- Do not add tools that expose unrestricted `SELECT *` over sensitive datasets without filters.
- Avoid writing query results to disk in shared branches unless necessary.

## 12. Extension Ideas
| Idea | Description | Effort |
|------|-------------|--------|
| Row count estimator | Use INFORMATION_SCHEMA.TABLE_STORAGE | Low |
| Partition summary tool | Query `__PARTITIONS_SUMMARY__` pseudo table | Medium |
| Column stats tool | Leverage `APPROX_TOP_COUNT` for categorical fields | Medium |
| Cost guardrail | Prepend `EXPLAIN` tool for big queries | Medium |

## 13. Appendix: Minimal Custom Tool Skeletons
Flat schema template:
```yaml
flat_schema_template:
  kind: bigquery-sql
  source: bq
  description: |
    List columns (name + type) for a table.
  statement: |
    SELECT column_name, data_type
    FROM `PROJECT.DATASET`.INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = 'TABLE_NAME'
    ORDER BY ordinal_position
```

Nested path template:
```yaml
nested_schema_template:
  kind: bigquery-sql
  source: bq
  description: |
    List nested field paths for a table (if any).
  statement: |
    SELECT column_name, field_path, data_type
    FROM `PROJECT.DATASET`.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS
    WHERE table_name = 'TABLE_NAME'
    ORDER BY field_path
```

Ad-hoc executor template:
```yaml
adhoc_template:
  kind: bigquery-execute-sql
  source: bq
  description: Run a bounded ad-hoc query (must include LIMIT).
```

---
**Change Log**
- 2025-11-12: Verified all prebuilt tools working; updated examples with correct parameter syntax.
- 2025-09-07: Initial guide created; documented indentation parse fix and four baseline tools.

*End of guide.*
