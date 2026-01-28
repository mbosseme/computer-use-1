# AGENTS — src

Key files
- `src/runner/bq.py`: initializes the ADC-first BigQuery client and query helpers
- `src/runner/context.py`: builds the run context from YAML config and filesystem layout
- `src/test_bigquery_connectivity.py`: quick auth sanity check

Guidance
- No secrets in code; reference `.env` and local credentials path only
- When changing auth/client behavior, write a small `Decision` or `Config` entry to `.mcp/memory.jsonl`
