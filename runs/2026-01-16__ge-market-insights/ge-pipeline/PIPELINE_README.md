# GE Market Insights Pipeline (Migrated)

> **Migrated from:** `https://github.com/mbosseme/ge-sample` (commit: `87e8248`)  
> **Migration date:** 2026-01-28  
> **Location:** `runs/2026-01-16__ge-market-insights/ge-pipeline/`

This directory contains the full analytics pipeline for GE Market Insights, including:

- **Dataform SQL transformations** for BigQuery
- **Python pipeline** for data export, visualization, and PowerPoint generation
- **Business logic documentation** (PRD rules, parity methodology)

---

## Quick Start

### Prerequisites

1. **GCP Authentication** (ADC only — no embedded secrets):
   ```bash
   gcloud auth application-default login
   ```

2. **Python environment** (use workspace venv):
   ```bash
   source ../../.venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Dataform CLI**:
   ```bash
   cd dataform && npm install
   ```

---

## Directory Structure

```
ge-pipeline/
├── dataform/                # BigQuery SQL transformations
│   ├── dataform.json        # Config (project: matthew-bossemeyer)
│   ├── definitions/
│   │   ├── sources/         # External table declarations
│   │   ├── staging/         # Cleaning/filtering transforms
│   │   ├── marts/           # Business-logic aggregations
│   │   └── assertions/      # Data quality tests
│   └── includes/            # Shared JS helpers (config, manufacturer map)
├── src/                     # Python pipeline modules
│   ├── runner/              # CLI + orchestration
│   ├── steps/               # Pipeline stages
│   ├── pptx_builder/        # PowerPoint generation
│   └── *.py                 # Core utilities (BigQuery client, config, etc.)
├── scripts/                 # Orchestration scripts
│   ├── run_full_pipeline.py # Main entry point
│   ├── generate_capital_visuals.py
│   └── ct_charity_outputs.py
├── config/                  # YAML configuration (deck settings, themes)
├── brand/                   # PowerPoint template (.potx)
├── tests/                   # Pytest test suite
├── sql/                     # Ad-hoc SQL queries
└── docs/                    # Business rules, architecture, data models
```

---

## Running the Pipeline

### 1. Dataform (SQL Transformations)

> **⚠️ CRITICAL: Always use the local binary, NOT `npx`**
> 
> `npx @dataform/cli` can hang for 30+ minutes due to npm package resolution.
> Use `./node_modules/.bin/dataform` instead — compile should take < 1 second.

```bash
cd dataform

# Install dependencies (one-time after clone/migration)
npm install

# Compile (validate SQL, check dependencies) — should take < 1 second
./node_modules/.bin/dataform compile

# Dry run (show what would be created)
./node_modules/.bin/dataform run --dry-run

# Full run (materialize all views/tables)
./node_modules/.bin/dataform run

# Run specific tags
./node_modules/.bin/dataform run --tags staging
./node_modules/.bin/dataform run --tags marts
./node_modules/.bin/dataform run --tags parity
```

### 2. Full Pipeline (Dataform → Export → Visuals → Deck)

```bash
# From ge-pipeline directory
PYTHONPATH=. python scripts/run_full_pipeline.py

# Skip Dataform (if tables already materialized)
PYTHONPATH=. python scripts/run_full_pipeline.py --skip-dataform
```

**Output:** Timestamped folder in `snapshots/<RUN_ID>/` containing:
- `GE_PILOT_Validation.pptx` — Branded presentation
- `GE_PILOT_Validation.pdf` — PDF export
- CSV exports from BigQuery marts
- Generated visualizations

### 3. Tests

```bash
PYTHONPATH=. pytest -q
```

---

## Configuration

### Dataform (`dataform/dataform.json`)

| Setting | Current Value | Notes |
|---------|---------------|-------|
| `defaultDatabase` | `matthew-bossemeyer` | GCP Project ID |
| `defaultSchema` | `ge_sample_staging` | Default output dataset |
| `assertionSchema` | `ge_sample_assertions` | Dataset for test views |
| `capital_price_threshold` | `25000` | Filter for capital equipment |

### Python (`config/default.yaml`)

Main pipeline configuration for time windows, guard thresholds, and deck settings.

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/PRODUCT_REQUIREMENTS.md` | **Business rules — treat as law** |
| `docs/ARCHITECTURE.md` | Pipeline flow and table roles |
| `docs/PREMIER_DATA_MODELS_HANDOFF.md` | Data model reference + MCP interaction |
| `docs/PARITY_AUDIT_FINDINGS.md` | Philips audit proving defensibility |
| `PARITY_ALIGNMENT_APPROACH.md` | Methodology for TA vs Supplier Spend alignment |

---

## BigQuery Tables

### Source Tables (Premier feeds)

| Table | Schema | Description |
|-------|--------|-------------|
| `transaction_analysis_expanded` | `premier-analysis-2024.premier_feeds` | Provider-reported PO/Invoice data (~820M rows) |
| `supplier_spend` | `premier-analysis-2024.premier_feeds` | Manufacturer-reported sales tracings (~87M rows) |
| `sasf_dhc_join` | `premier-analysis-2024.premier_feeds` | Facility/entity metadata |

### Output Tables (Dataform-managed)

| Table | Schema | Description |
|-------|--------|-------------|
| `mart_parity_analysis` | `ge_sample_marts` | Parity comparison (TA vs SS) |
| `mart_validation_mapping` | `ge_sample_marts` | Product validation by category |
| `mart_observed_trends` | `ge_sample_marts` | Quarterly spend/share trends |

---

## Non-Negotiable Rules

1. **Authentication:** ADC only. Never embed secrets or commit keys.
2. **Business Logic:** Follow PRD rules in `docs/PRODUCT_REQUIREMENTS.md` exactly.
3. **Outputs:** Write to `snapshots/<RUN_ID>/` with manifest tracking.
4. **Data Quality:** Dataform assertions must pass before exports.

---

## Migration Notes

- Original source: `https://github.com/mbosseme/ge-sample`
- This is a **run-local** copy under the GE Market Insights worktree
- Future updates to the presentation/analysis should be made here
- Reusable capabilities may be promoted to core (`tools/`, `docs/`) over time
