# 🔧 Unified Agent Instructions (repo-wide)

**North Star.** Produce PRD-aligned analytics.

## Sources of truth (read in this order)

1. `README.md` — how to run locally; CLI commands; snapshots. 
2. `docs/ARCHITECTURE.md` — pipeline flow & repo layout. 
3. `docs/PRODUCT_REQUIREMENTS.md` — business rules & acceptance (follow as law). *(Referenced throughout repo docs.)* 

**Auth:** BigQuery uses **Application Default Credentials (ADC)** only. Never embed secrets or commit keys. Run `gcloud auth application-default login` if needed. 

**Outputs:** Write under `snapshots/<RUN_ID>/` (e.g., `prd_answers.csv`, charts, manifest). Keep filenames and schema stable.

## Non-negotiable guardrails

* Enforce PRD rules. 
* Prefer small, typed changes; fail fast on QA errors; use `pytest -q` for smoke.

## Required logging (for **all** agents)

Append major changes, findings, and "blocked" notes to **`SUMMARY_OF_RECENT_ITERATION.md`** at repo root (newest at the top). Each entry should include:

* **Timestamp** and **intent/step**
* **Files touched / commands run**
* **Outcome** (tests/lint), **Next action**, and **Commit SHA** (if any)

Use a **BLOCKED** entry and stop when human input is required. *(This file serves as the handoff log between sessions.)* 

## MCP Server (optional but available)

**Server:** `bigquery_ge_sample` (workspace-specific instance)  
**Purpose:** Interactive BigQuery exploration — list datasets/tables, inspect schemas, execute queries, validate transformations.  
**Auth:** Uses ADC (same as pipeline); no additional setup required.  
**Reference:** See `docs/MCP_TOOLBOX_GUIDE.md` for complete tool list and usage examples.

Use MCP tools when helpful for exploration; do not depend on them for core pipeline runs.