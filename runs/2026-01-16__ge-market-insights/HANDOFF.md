# Run Handoff — 2026-01-16__ge-market-insights

## Summary
- Bootstrapped per-run Playwright MCP isolation by updating `.vscode/mcp.json` to pass `--user-data-dir` and `--output-dir` under this RUN_ID.
- Identified 6 PDFs + 1 DOCX in the GE source folder and staged them for synthesis under `runs/2026-01-16__ge-market-insights/inputs/ge_synthesis_staging` (PDFs symlinked; DOCX converted to TXT).
- Ran per-document and combined synthesis for the staged GE documents.

## Verification
- Navigated to `https://example.com` via Playwright MCP; title: "Example Domain".
- Screenshot written to `runs/2026-01-16__ge-market-insights/playwright-output/mcp-validation.png`.
- Profile dir became non-empty: `runs/2026-01-16__ge-market-insights/playwright-profile/`.
- Verified a running Chrome process includes `--user-data-dir=.../runs/2026-01-16__ge-market-insights/playwright-profile`.
- Staging script produced 7 staged files and wrote manifest: `runs/2026-01-16__ge-market-insights/exports/ge_synthesis_staging.manifest.json`.
- Per-doc syntheses written under `runs/2026-01-16__ge-market-insights/exports/ge_docs/`.
- Folder synthesis written to `runs/2026-01-16__ge-market-insights/exports/ge_folder_synthesis.md` with manifest `runs/2026-01-16__ge-market-insights/exports/ge_folder_synthesis.manifest.json`.

## Next steps
- Proceed with the run task using the isolated Playwright MCP server in this worktree window.
- Use the folder synthesis as context for drafting the GE statement of work (scope, deliverables, governance, and pricing/pilot structure).

## Incremental synthesis (added)
- Added an incremental sync script that fingerprints source docs (size + mtime) and only re-synthesizes the ones that changed, then rebuilds the combined synthesis.
- Script: `runs/2026-01-16__ge-market-insights/scripts/sync_ge_incremental_synthesis.py`
- Outputs:
	- Index: `runs/2026-01-16__ge-market-insights/exports/ge_incremental_index.json`
	- Per-doc (incremental): `runs/2026-01-16__ge-market-insights/exports/ge_docs_incremental/`
	- Combined (incremental): `runs/2026-01-16__ge-market-insights/exports/ge_folder_synthesis_incremental.md`
	- Combined manifest: `runs/2026-01-16__ge-market-insights/exports/ge_folder_synthesis_incremental.manifest.json`
- Notes: per-doc outputs are keyed by `slug__stableId` (stableId = hash of absolute source path) to avoid collisions (e.g., "RE ..." vs "RE: ...").

## SOW Drafting & Generation (2026-01-23)
- **Drafted SOW v8:** Finalized content for "GE Healthcare Market Insights Pilot" including:
    - Core MVP ($150k + $85k/yr renewal).
    - Add-ons for Non-Acute ($60k) and PO/Invoice Deep Dive ($150k).
    - Timeline estimates tailored to add-on complexity.
- **Generated Word Doc:** Created `runs/2026-01-16__ge-market-insights/exports/GE_Market_Insights_Pilot_SOW_v8.docx` using Premier Standard formatting.
- **Tooling:** Implemented `tools/generate_docx.py` to handle `.dotx` conversion and style mapping natively in Python.
- **Core Promotions:**
    - Promoted `generate_docx.py` to `tools/`.
    - Promoted `26-Legal-WordTemp.dotx` to `templates/Premier_Standard_Legal.dotx`.
    - Added `document-generation-sow` skill.

## GE Pipeline Migration (2026-01-28)
Migrated the full analytics pipeline from `https://github.com/mbosseme/ge-sample` (commit `87e8248`) into this run-local folder.

**Location:** `runs/2026-01-16__ge-market-insights/ge-pipeline/`

**What was migrated:**
- `dataform/` — BigQuery SQL transformations (14 actions: 11 datasets, 3 assertions)
- `src/` — Python pipeline modules (runner, steps, pptx_builder, utilities)
- `scripts/` — Orchestration scripts (`run_full_pipeline.py`, `generate_capital_visuals.py`, etc.)
- `config/` — YAML configs (deck settings, themes)
- `brand/` — PowerPoint template (.potx)
- `tests/` — Pytest test suite with fixtures
- `sql/` — Ad-hoc SQL queries
- `docs/` — Key documentation (PRD, Architecture, Data Models, Parity Audit)

**Configuration:**
- GCP Project: `matthew-bossemeyer`
- Datasets: `ge_sample_staging`, `ge_sample_marts`, `ge_sample_assertions`
- Authentication: ADC only (`gcloud auth application-default login`)

**Validation:**
- Dataform compiles successfully (14 actions)
- Python dependencies installed and imports verified
- Created `ge-pipeline/PIPELINE_README.md` with usage instructions

**Workspace updates:**
- Merged `requirements.txt` to include BigQuery, pandas, matplotlib, typer, etc.
- Dataform npm dependencies installed under `ge-pipeline/dataform/node_modules/`

## Next Steps
- Run `npx dataform run` to materialize BigQuery tables (requires ADC auth) ✅ **DONE**
- Run `PYTHONPATH=. python scripts/run_full_pipeline.py` for end-to-end pipeline ✅ **DONE**
- Use migrated pipeline for future presentation/analysis updates
- Consider promoting reusable capabilities to core (`tools/`, `docs/`) over time

## Pipeline Run (2026-01-28)
Successfully executed the full pipeline:

**Dataform (BigQuery):**
- 9 tables/views materialized in `matthew-bossemeyer` project
- 2 assertions passed (data quality checks)
- Schemas: `ge_sample_staging`, `ge_sample_marts`, `ge_sample_assertions`

**Python Pipeline:**
- Run ID: `20260128T152828Z`
- Location: `ge-pipeline/snapshots/20260128T152828Z/`

**Outputs:**
| File | Rows/Size | Description |
|------|-----------|-------------|
| `GE_PILOT_Validation.pptx` | 4.3 MB | Branded presentation |
| `GE_PILOT_Validation.pdf` | 970 KB | PDF export |
| `mart_validation_mapping_*.csv` | 3,306 rows | Product validation data |
| `mart_observed_trends_*.csv` | 149 rows | Quarterly trends |
| `slide_data_ct_breakout.csv` | 1,275 rows | CT product breakout |
| `visuals/` | 12 charts | Executive + QA visualizations |

**Notes:**
- Created `.df-credentials.json` to enable Dataform ADC auth

## Charity CT Permissions Fix (2026-01-28)
**Problem:** The `ct_charity_outputs.py` script failed with 403 "Access Denied" when querying `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`.

**Root Cause:** The workspace-level `.env` file (at repo root) sets `GOOGLE_APPLICATION_CREDENTIALS` pointing to a service account (`insight-flash@matthew-bossemeyer.iam.gserviceaccount.com`) that lacks read access to the `abi-inbound-prod` project. The Python `load_dotenv()` calls in `src/config.py` and `src/bigquery_client.py` would search up the directory tree and load this file, overriding user ADC credentials.

**Solution:** Created a local `ge-pipeline/.env` file (empty except for comments) so that `load_dotenv()` finds it first and doesn't inherit the parent workspace's settings. This allows the pipeline to use user ADC credentials which have cross-project read access.

**Successful Run:**
- Run ID: `20260128T154849Z`
- Location: `ge-pipeline/snapshots/20260128T154849Z/`

**Full Outputs (including Charity CT):**
| File | Rows | Description |
|------|------|-------------|
| `ct_charity_presence_summary.csv` | 18 | Charity CT term presence summary |
| `ct_charity_hierarchy_extract.csv` | 450 | Hierarchy mapping for CT products |
| `ct_charity_zero_match_discovery.csv` | 76 | Zero-match discovery analysis |
| `ct_ct_text_discovery.csv` | 200 | CT text discovery patterns |
| `ct_charity_term_debug_samples.csv` | 182 | Debug samples for term matching |
| `ct_frontier_subtype_breakdown.csv` | 1 | Frontier subtype summary |
| `GE_PILOT_Validation.pptx` | 4.5 MB | Branded presentation (complete) |
| `GE_PILOT_Validation.pdf` | 1.0 MB | PDF export |
| `mart_validation_mapping_*.csv` | 3,306 | Product validation data |
| `mart_observed_trends_*.csv` | 149 | Quarterly trends |
| `visuals/` | 14 files | Executive + QA visualizations |

## Core Promotions (2026-01-28)

Analyzed ge-pipeline for reusable patterns and promoted to core:

**New Skills Created:**
- `.github/skills/bigquery-data-exploration/SKILL.md` — Cross-project access, schema discovery, product matching, Dataform patterns
- `.github/skills/pptx-deck-generation/SKILL.md` — python-pptx patterns, template handling, chart insertion, PDF export

**New Documentation:**
- `docs/BIGQUERY_CROSS_PROJECT_ACCESS.md` — ADC authentication, troubleshooting cross-project 403 errors

**Updated:**
- `.github/skills/README.md` — Reorganized index with categories, added new skills

**Environment Fix:**
- Removed `GOOGLE_APPLICATION_CREDENTIALS` and `VERTEX_AI_PROJECT` from workspace `.env` (unused, caused cross-project query failures)
- Added comment documenting the "no service account" requirement

## Blockers
- None.

## 4th Category Addition (2026-01-28)
Added "ULTRASOUND RADIOLOGY CARDIOLOGY HAND CARRIED" category to expand analysis from 3 to 4 categories.

**Files Modified:**
- `dataform/definitions/staging/stg_supplier_spend_parity.sqlx` — Added to IN clause
- `dataform/definitions/staging/stg_transaction_parity_basis.sqlx` — Added to IN clause
- `dataform/includes/capital_config.js` — Added to primaryCategoryTerms + positiveKeywords
- `dataform/includes/ge_capital_shared.js` — Added "Ultrasound HC" to reportCategoryCase
- `dataform/definitions/marts/mart_parity_analysis.sqlx` — Added category mapping
- `src/pptx_builder/build_ge_deck.py` — Updated title, exec summary, market trends

**New Data Generated (Run ID: `20260128T181416Z`):**
| Category | Transaction Spend | Supplier Spend | Coverage |
|----------|------------------|----------------|----------|
| CT | $426M | $324M | 131% |
| MRI | $289M | $288M | 100% |
| Monitoring | $634M | $619M | 102% |
| Ultrasound HC | $684M | $475M | 144% |

**Dataform Performance Fix:**
- Root cause: `npx @dataform/cli` downloads packages each time (~30+ min)
- Solution: Use `./node_modules/.bin/dataform` directly (0.65s)
- Updated documentation in 3 files to prevent future issues

## PowerPoint Layout Fix (2026-01-28)
Fixed Executive Summary slide layout issue where bullets appeared at the bottom of the slide.

**Root Cause:**
- The `add_bullet_slide()` function was using "Premier Two Content Subtitle 1a" layout (2-column with multiple placeholders)
- python-pptx wasn't correctly inheriting placeholder positions from the layout template

**Solution:**
1. Added `"MAIN_CONTENT"` layout key mapping to "Premier Main Content 1a" (single full-width body)
2. Updated `add_bullet_slide()` to:
   - Use MAIN_CONTENT layout for simpler single-body structure
   - Explicitly copy layout placeholder position/size to slide placeholders
3. Updated `layouts.py` to add MAIN_CONTENT to `_NON_BLANK_KEYS`

**Verification:**
- Before: Body placeholder at top=0.43" (overlapping title)
- After: Body placeholder at top=1.31" height=5.31" (correct position)

**Deck Output:** `snapshots/20260128T183424Z/GE_PILOT_Validation.pptx` (v3)
