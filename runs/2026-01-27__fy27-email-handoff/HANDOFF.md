# Run Handoff Journal — 2026-01-27__fy27-email-handoff

## Purpose
- Run-local continuity journal for FY27 email handoff + keeping B. Braun context up to date.
- No sensitive URLs/tokens; use placeholders like `<PORTAL_URL>`.

## 2026-01-27 — Initialize run + sync plan

### Goals
- Sync the latest local B. Braun document repository into a stable run-local “source mirror” (symlink-based).
- Run incremental synthesis so only changed/new docs are reprocessed going forward.

### Source folder (local)
- `/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/Digital Supply Chain/Market Insights/B Braun`

### Planned outputs (this run)
- `runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat/` (symlink mirror of docs)
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__incremental_index.json`
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.md`
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.manifest.json`
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs/per_doc/*__synthesis.md`

### Completed (sync + incremental synthesis)
- Mirrored files (recursive): 17
- Incremental synthesis stats: `files_seen=17`, `changed=17`, `synthesized=17`, `removed=0`

### Artifacts
- Source mirror map (rel paths → mirrored names): `runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_map.json`
- Flat symlink mirror (inputs): `runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat/`
- Per-doc syntheses + manifests: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs/per_doc/`
- Incremental index: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__incremental_index.json`
- Folder synthesis: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.md`
- Folder synthesis manifest: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.manifest.json`

### Repro (incremental re-run)
1) Re-sync mirror (updates symlinks / captures new files):
	- `/.venv/bin/python runs/2026-01-27__fy27-email-handoff/scripts/sync_b_braun_docs.py --source-root "<LOCAL_ONE_DRIVE_B_BRAUN_FOLDER>" --out-dir runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat --map-json runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_map.json --clean`
2) Re-run incremental synthesis (only new/changed docs get reprocessed):
	- `/.venv/bin/python -m agent_tools.llm.summarize_incremental --source-dir runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat --staging-dir runs/2026-01-27__fy27-email-handoff/inputs/b_braun_docs__staging --per-doc-dir runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs/per_doc --tmp-dir runs/2026-01-27__fy27-email-handoff/tmp/b_braun_docs__chunks --index runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__incremental_index.json --out runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.md --manifest runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.manifest.json`

## 2026-01-28 — IV Solutions Data Cut

### Objective
- Generate a facility-level sample data cut for B. Braun IV NDCs to support the email handoff analysis.
- Validate internal consistency where possible.

### Execution
1. **Scope Definition**:
   - Validated mapping file: `runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping__verified.csv`
   - Expanded NDC scope using `expand_ndc_scope.py` to capture related packaging NDCs.
   - Output: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__expanded_ndc_scope.csv`

2. **Data Extraction**:
   - Script: `runs/2026-01-27__fy27-email-handoff/scripts/pull_iv_solutions_data.py`
   - **Provider Data (TAE)**: Extracted 27k+ rows. 
     - *Observation*: Vendors are primarily distributors (Medline, Fresenius, etc.), which explains why direct Reference Number validation against B. Braun's manufacturer account failed.
   - **Wholesaler Data (RB)**: Extracted 17.6k+ rows.
   - **Validation (CAMS)**: Step skipped/commented out in script. 
     - Reason: The Reference Numbers in TAE map to distributor accounts, while CAMS requires B. Braun's manufacturer account identifiers. Automated validation via Reference Number is not possible with current keys.

### Outputs
- **Provider Data**: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__tae_raw.csv`
- **Wholesaler Data**: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__rb_raw.csv`

### Next Steps
- ~~Analyze the raw extracts (`tae_raw.csv` and `rb_raw.csv`) to generate the final facility-level sample.~~
- ~~Since CAMS validation was skipped, rely on the consistency between TAE and RB datasets for confidence.~~

## 2026-01-28 — Facility Sample Generation (Completed)

### Execution
- Script: `runs/2026-01-27__fy27-email-handoff/scripts/generate_facility_sample.py`
- Loaded TAE (27,679 rows) and RB (17,322 rows) raw extracts.
- Aggregated by facility, merged with outer join, computed cross-source coverage.
- De-identified facility IDs (sorted by combined spend, blinded as `FAC_0001`, etc.).

### Key Findings
| Metric | Value |
|--------|-------|
| Total unique facilities | 2,771 |
| Facilities in BOTH sources | 689 (24.9%) |
| TAE-only facilities | 637 (23.0%) |
| RB-only facilities | 1,445 (52.1%) |
| **Total combined spend** | **$41,557,665.18** |
| TAE spend | $39,524,864.52 (95.1%) |
| RB spend | $2,032,800.66 (4.9%) |
| Total units | 3,500,433 |

### Observations
1. **TAE dominates spend**: 95% of combined spend comes from TAE (Provider direct), which reflects distributor-intermediated purchasing rather than direct manufacturer sales.
2. **Cross-source overlap is limited**: Only 689 facilities (24.9%) appear in both TAE and RB, suggesting different visibility windows between the two data sources.
3. **Top facilities are TAE-only**: The top 2 facilities by spend (~$2.5M and ~$1.3M) have no RB coverage, reinforcing that TAE captures the larger institutional buyers.

### Outputs
- **Blinded facility sample**: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__facility_sample.csv`
- **Summary JSON**: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__facility_sample_summary.json`

### Next Steps
- Review the sample for email handoff content (top facilities, spend distribution, source coverage).
- If additional validation is needed, consider manual spot-checks against known facility names.

## 2026-01-30 — Corrected Enriched External Sample (QA’d)

### Context / correction
- The earlier facility-sample totals in this journal (e.g., ~$41.6M) included two reference numbers that were later proven to be incorrect matches (non-IV items) and were removed from the verified mapping.
- Current sample outputs are based on the corrected mapping file and the enriched-sample pipeline.

### Current deliverables (source of truth)
- Enriched sample CSV: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched.csv`
- Summary JSON (metrics): `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched_summary.json`
- Data dictionary: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched_dictionary.md`
- QA report: `runs/2026-01-27__fy27-email-handoff/QA_REPORT.md`

### Key metrics (2024-01 to 2025-12)
- Rows: 26,379 (ERP: 2,988; Wholesaler: 23,391)
- Spend: $10,286,068.29 (ERP: $7,084,543.94; Wholesaler: $3,201,524.35)
- Facilities (blinded IDs): 3,103
- NDCs: 65

### Why spend dropped vs older numbers
- Two reference numbers were removed after provenance review:
  - `reference_number=40992`
  - `reference_number=34813`
- These two items contributed ~$32.46M in ERP spend in 2024–2025, explaining most of the drop from ~$42.7M → ~$10.3M.

### Repro
1) Extract inputs: `/.venv/bin/python runs/2026-01-27__fy27-email-handoff/scripts/extract_enriched_sample.py`
2) Build final outputs: `/.venv/bin/python runs/2026-01-27__fy27-email-handoff/scripts/generate_enriched_sample.py`

## 2026-02-02 — Gap Analysis & Workbook Finalization (Completed)

### Objective
- Identify and quantify Fresenius IV products ("Gap Products") present in the broader Premier transaction data but missing from the initial "Jen's List" scope.
- Produce a single, cohesive Excel workbook containing the original requested sample, the new gap analysis, and a unified data dictionary.
- Ensure consistent blinding across both datasets (extract 1 and extract 2).

### Execution
1. **Gap Analysis Extraction**:
   - Script: `runs/2026-01-27__fy27-email-handoff/scripts/extract_gap_products.py`
   - **Logic**: 
     - Queries `transaction_analysis_expanded` (ERP) and `report_builder` (Wholesaler).
     - Filters for `Manufacturer_Top_Parent_Name = 'FRESENIUS GROUP'` and `Contract_Category = 'IV THERAPY PRODUCTS...'`.
     - **Exclusion**: Explicitly excludes `reference_number`s already captured in the initial verified mapping (`jen_ndc_reference_mapping__verified.csv`).
     - **Schema**: Aligned exactly with the "Enriched Sample" schema (21 columns).
     - **Wholesaler Naming**: For Report Builder rows, `vendor_name` is dynamically pulled from the `wholesaler` column (e.g., "Cardinal", "McKesson") rather than a hardcoded "Wholesaler".
   - **Blinding**:
     - Uses `iv_solutions__blinding_map__INTERNAL_ONLY.json`.
     - Script *dynamically extends* the map: if new facilities are found in the gap analysis (not in extract 1), they affect sequential IDs (`FAC_XXXXX`) and are saved back to the JSON map.
     - Gap analysis identified **1,361 new facilities** unique to this dataset.

2. **Workbook Assembly**:
   - Script: `runs/2026-01-27__fy27-email-handoff/scripts/create_final_workbook.py`
   - Combines:
     - Tab 1: **Data Dictionary** (Markdown parsed to Excel).
     - Tab 2: **Requested Products (Extract 1)** (`iv_solutions__external_sample_enriched.csv`).
     - Tab 3: **Gap Products (Extract 2)** (`iv_solutions__gap_products.csv`).

### Outputs
- **Final Workbook**: `runs/2026-01-27__fy27-email-handoff/exports/Fresenius_IV_Solutions_Data_Pack_FY27.xlsx`
- **Gap Data CSV**: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__gap_products.csv`
- **Updated Blinding Map**: `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__blinding_map__INTERNAL_ONLY.json`

### Key Findings (Gap Analysis)
- **Total Spend**: ~$124.8M (vs ~$10.3M in the requested sample).
- **Volume**: 55,055 rows.
- **Why the mismatch?**: The original request focused on a specific list of items. The gap analysis shows the broader "Fresenius IV Therapy" category is significantly larger, likely due to different product families or contract categories not in the initial list.



