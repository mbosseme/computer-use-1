# Migration Guide: GE Market Insights Pilot → New Repository

> **For:** Agent working in a destination repository  
> **Source repo:** `https://github.com/mbosseme/ge-sample` (branch: `main`, commit: `87e8248`)  
> **Purpose:** Replicate the full analytics pipeline, including Dataform transformations, Python orchestration, and branded output generation.

---

## 1. Access the Source Repository

You have direct GitHub access. Clone or fetch from:

```bash
git clone https://github.com/mbosseme/ge-sample.git ge-sample-source
cd ge-sample-source
```

Or add as a remote to your existing repo for selective cherry-picking:

```bash
git remote add ge-source https://github.com/mbosseme/ge-sample.git
git fetch ge-source main
```

---

## 2. What to Migrate (Priority Order)

### Critical (Must Have)

| Directory/File | Purpose | Migration Notes |
|----------------|---------|-----------------|
| `dataform/` | BigQuery SQL transformations | Copy entire folder; update `dataform.json` for your GCP project |
| `src/` | Python pipeline modules | Copy entire folder |
| `scripts/run_full_pipeline.py` | Main CLI entry point | Copy + dependencies |
| `requirements.txt` | Python dependencies | Merge with your existing requirements |
| `config/` | YAML configs (themes, deck settings) | Copy entire folder |
| `brand/` | PowerPoint template (.potx) | Copy if you need branded output |

### Important (Context & Business Logic)

| File | Purpose |
|------|---------|
| `docs/PRODUCT_REQUIREMENTS.md` | Business rules — **treat as law** |
| `docs/ARCHITECTURE.md` | Pipeline flow and table roles |
| `PARITY_ALIGNMENT_APPROACH.md` | Methodology for aligning Transaction Analysis vs Supplier Spend |
| `docs/PREMIER_DATA_MODELS_HANDOFF.md` | Data model reference + MCP interaction patterns |
| `docs/PARITY_AUDIT_FINDINGS.md` | Philips audit proving defensibility |

### Reference (Optional)

| File | Purpose |
|------|---------|
| `sql/` | Ad-hoc SQL queries (discovery, debugging) |
| `tests/` | Pytest suite for pipeline validation |
| `snapshots/20260122T122915Z/` | Final deliverables (PPTX, PDF, CSVs) as reference |

---

## 3. Dataform Setup (Critical Path)

### 3.1 Directory Structure

```
dataform/
├── dataform.json          # Project config (update for your GCP project!)
├── package.json           # Node dependencies (@dataform/core, @dataform/cli)
├── definitions/
│   ├── sources/           # External table declarations
│   ├── staging/           # Cleaning/filtering transformations
│   │   ├── stg_transaction_parity_basis.sqlx   # Provider data filter
│   │   ├── stg_supplier_spend_parity.sqlx      # Manufacturer data filter
│   │   ├── int_supplier_parent_lookup.sqlx     # Name normalization lookup
│   │   ├── int_facility_exclusion_list.sqlx    # Facilities to exclude
│   │   ├── int_parity_exclusion_list.sqlx      # Combined exclusion logic
│   │   └── stg_ge_capital_systems.sqlx         # GE capital staging
│   ├── marts/             # Business-logic aggregations
│   │   ├── mart_parity_analysis.sqlx           # Parity comparison
│   │   ├── mart_validation_mapping.sqlx        # Product validation
│   │   └── mart_observed_trends.sqlx           # Quarterly trends
│   └── assertions/        # Data quality tests
└── includes/              # Shared JavaScript helpers
    ├── capital_config.js          # Threshold/keyword config
    ├── constants.js               # Shared constants
    ├── ge_capital_shared.js       # GE-specific helpers
    └── manufacturer_map.js        # Manufacturer name normalization
```

### 3.2 Configuration Updates Required

**`dataform/dataform.json`** — Update these values for your environment:

```json
{
  "warehouse": "bigquery",
  "defaultDatabase": "YOUR-GCP-PROJECT-ID",    // ← CHANGE THIS
  "defaultSchema": "ge_sample_staging",        // ← Or your schema name
  "defaultLocation": "US",
  "assertionSchema": "ge_sample_assertions",
  "vars": {
    "capital_price_threshold": "25000",
    "capital_primary_categories": "MAGNETIC RESONANCE|COMPUTED TOMOGRAPHY|PHYSIOLOGICAL MONITORING",
    "capital_positive_keywords": "MRI|CT|TOMOGRAPHY|RESONANCE|MONITORING",
    "capital_negative_keywords": "SERVICE|MAINTENANCE|WARRANTY|AGREEMENT|REPAIR|SOFTWARE|LICENSE|RENEWAL"
  }
}
```

### 3.3 Install Dataform CLI

```bash
cd dataform
npm install
```

This installs:
- `@dataform/core` ^3.0.35
- `@dataform/cli` ^3.0.35
- `google-auth-library` ^9.14.1

### 3.4 Running Dataform Transformations

```bash
# Compile (validate SQL, check dependencies)
npx dataform compile

# Dry run (show what would be created)
npx dataform run --dry-run

# Full run (materialize all views/tables)
npx dataform run

# Run specific layer
npx dataform run --tags staging
npx dataform run --tags marts

# Run single definition with dependencies
npx dataform run --include-deps definitions/marts/mart_parity_analysis
```

### 3.5 Key Dataform Patterns Used

**Referencing other definitions:**
```sql
SELECT * FROM ${ref("stg_transaction_parity_basis")}
```

**Using config variables:**
```javascript
// In includes/capital_config.js
const priceThreshold = dataform.projectConfig.vars.capital_price_threshold;
```

**Manufacturer normalization (includes/manufacturer_map.js):**
```javascript
const manufacturerMap = require("./manufacturer_map");
// In SQL:
${manufacturerMap.buildCaseExpression("raw_manufacturer_column")}
```

---

## 4. Python Pipeline Setup

### 4.1 Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Key dependencies:**
- `google-cloud-bigquery` — BigQuery client
- `python-pptx` — PowerPoint generation
- `pandas`, `matplotlib` — Data processing and visualization
- `typer` — CLI framework
- `Jinja2` — Template rendering
- `PyYAML` — Config parsing

### 4.2 Authentication (Non-Negotiable)

**ADC only. No embedded secrets. No committed keys.**

```bash
gcloud auth application-default login
```

This authenticates both:
- Python BigQuery client (`google-cloud-bigquery`)
- Dataform CLI (`npx dataform run`)

### 4.3 Running the Pipeline

```bash
# Full end-to-end run
python scripts/run_full_pipeline.py

# With specific options (if implemented)
python scripts/run_full_pipeline.py --skip-dataform
```

**Output:** Timestamped folder in `snapshots/<RUN_ID>/` containing:
- `GE_PILOT_Validation.pptx` — Branded presentation
- `GE_PILOT_Validation.pdf` — PDF export
- `ct_charity_presence_summary.csv` — Product validation
- `manifest.json` — Run metadata

### 4.4 Key Python Modules

| Module | Purpose |
|--------|---------|
| `src/bigquery_client.py` | BigQuery connection wrapper |
| `src/config.py` | Configuration loading |
| `src/kpis.py` | KPI calculation logic |
| `src/qa.py` | Quality assurance checks |
| `src/sql.py` | SQL query templates |
| `src/windowing.py` | Time window utilities |
| `src/pptx_builder/` | PowerPoint generation |
| `src/runner/` | Pipeline step orchestration |
| `src/steps/` | Individual pipeline steps |
| `src/validation/` | Data validation logic |

---

## 5. BigQuery Tables (Data Dependencies)

The pipeline reads from these Premier source tables:

| Table | Schema | Description |
|-------|--------|-------------|
| `transaction_analysis_expanded` | `premier-analysis-2024.premier_feeds` | Provider-reported PO/Invoice data (~820M rows) |
| `supplier_spend` | `premier-analysis-2024.premier_feeds` | Manufacturer-reported sales tracings (~87M rows) |
| `sasf_dhc_join` | `premier-analysis-2024.premier_feeds` | Facility/entity metadata |

**Schema details:** See `docs/PREMIER_DATA_MODELS_HANDOFF.md` for column descriptions.

---

## 6. MCP Server Setup (Optional but Useful)

For interactive BigQuery exploration in VS Code Copilot Chat:

### 6.1 VS Code Configuration

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "bigquery_ge_sample": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-bigquery", "--project-id", "YOUR-GCP-PROJECT-ID"],
      "env": {}
    }
  }
}
```

### 6.2 Usage

```
# In Copilot Chat
/mcp bigquery_ge_sample callTool list_dataset_ids
/mcp bigquery_ge_sample callTool list_table_ids dataset="ge_sample_staging"
/mcp bigquery_ge_sample callTool execute_sql sql="SELECT COUNT(*) FROM ..."
```

See `docs/MCP_TOOLBOX_GUIDE.md` for complete tool reference.

---

## 7. Test Suite

```bash
# Run all tests
PYTHONPATH=. pytest -q

# Run specific test
PYTHONPATH=. pytest tests/test_kpis.py -v
```

Key test files:
- `tests/test_kpis.py` — KPI calculation validation
- `tests/test_qa_invariants.py` — Data quality rules
- `tests/test_parity_compare.py` — Parity logic tests

---

## 8. Migration Checklist

```markdown
## Pre-Migration
- [ ] Clone/fetch source repo: `git clone https://github.com/mbosseme/ge-sample.git`
- [ ] Verify GCP project access and BigQuery permissions
- [ ] Run `gcloud auth application-default login`

## Dataform Migration
- [ ] Copy `dataform/` directory to destination repo
- [ ] Update `dataform.json` with your GCP project ID
- [ ] Run `cd dataform && npm install`
- [ ] Run `npx dataform compile` (should show 0 errors)
- [ ] Run `npx dataform run --dry-run` (verify tables/schemas)
- [ ] Run `npx dataform run` (materialize views)

## Python Migration
- [ ] Copy `src/`, `scripts/`, `config/`, `brand/` directories
- [ ] Merge `requirements.txt` with destination repo
- [ ] Create/activate venv and install dependencies
- [ ] Run `PYTHONPATH=. pytest -q` (tests should pass)
- [ ] Run `python scripts/run_full_pipeline.py` (end-to-end test)

## Documentation Migration
- [ ] Copy `docs/PRODUCT_REQUIREMENTS.md` (business rules)
- [ ] Copy `docs/ARCHITECTURE.md` (technical reference)
- [ ] Copy `PARITY_ALIGNMENT_APPROACH.md` (methodology)
- [ ] Copy `docs/PREMIER_DATA_MODELS_HANDOFF.md` (data models)
- [ ] Copy `AGENTS.md` (agent instructions)

## Validation
- [ ] Compare output to reference: `snapshots/20260122T122915Z/`
- [ ] Verify PPTX/PDF generation works
- [ ] Verify BigQuery queries return expected row counts
```

---

## 9. Key Business Logic (Do Not Change Without Review)

These rules are defined in `docs/PRODUCT_REQUIREMENTS.md` and enforced throughout:

1. **Capital threshold:** $25,000 minimum per transaction
2. **Date window:** Oct 2023 – Sep 2025 (24 months)
3. **Member type filter:** ACUTE only (provider side)
4. **Facility type filter:** ACUTE only (manufacturer side)
5. **Dark facility exclusion:** Exclude facilities not in both datasets
6. **Manufacturer normalization:** Use `manufacturer_map.js` CASE expressions
7. **Outlier cap:** $10M per transaction

---

## 10. Questions? Check These First

| Question | Where to Look |
|----------|---------------|
| What are the business rules? | `docs/PRODUCT_REQUIREMENTS.md` |
| How does the pipeline work? | `docs/ARCHITECTURE.md` |
| How were datasets aligned? | `PARITY_ALIGNMENT_APPROACH.md` |
| What are the BigQuery tables? | `docs/PREMIER_DATA_MODELS_HANDOFF.md` |
| Is the Philips analysis defensible? | `docs/PARITY_AUDIT_FINDINGS.md` |
| How do I use MCP tools? | `docs/MCP_TOOLBOX_GUIDE.md` |

---

## 11. Contact / Escalation

If you encounter issues the source repo documentation doesn't address:

1. **Check `SUMMARY_OF_RECENT_ITERATION.md`** — chronological log of decisions and changes
2. **Check git history** — `git log --oneline` for context on recent commits
3. **Flag as BLOCKED** — Add entry to your own `SUMMARY_OF_RECENT_ITERATION.md` with details

---

*Generated: 2026-01-28 | Source commit: `87e8248`*
