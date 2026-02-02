# QA Report — IV Solutions Enriched External Sample

**Run ID:** 2026-01-27__fy27-email-handoff  
**Latest sample build:** See `iv_solutions__external_sample_enriched_summary.json` (`generated_at`)  
**Sample window:** 2024-01 to 2025-12 (24 months)

## What this sample is (and is not)
- This sample is driven by **Jen’s provided NDC list**, mapped into Premier item master identifiers and expanded to related NDC packaging.
- Product attributes come from **Premier Primary Item Master** (via `ndc11`, with an ERP-only fallback via `reference_number`).
- The sample **does not assume** the products are B. Braun-manufactured; manufacturer is taken from product master.

## Inputs (canonical artifacts)
- Cohort mapping (drives scope):
  - `runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping__verified.csv`
- Extracted inputs (BigQuery → CSV):
  - `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__tae_enriched.csv`
  - `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__rb_enriched.csv`
  - `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__facility_attributes.csv`
  - `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__product_master_attributes.csv`

## Outputs (external deliverables)
- Enriched sample CSV:
  - `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched.csv`
- Summary JSON (metrics source-of-truth for the draft email):
  - `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched_summary.json`
- Data dictionary:
  - `runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched_dictionary.md`

## QA checks performed

### 1) Cohort integrity (mapping file)
- Mapping file has 71 rows:
  - `MATCHED`: 66
  - `MANUAL_CATALOG_MATCH_*`: 3
  - `NO_MATCH`: 2
- The two `NO_MATCH` NDCs are:
  - `6521949510`
  - `6521949720`

Interpretation:
- These two items are **explicitly excluded** from the cohort until a defensible reference-number mapping is established.

### 2) Reference numbers are present and consistent
- `reference_number` in the final sample is the Premier Primary Item Master `reference_number` inferred via the product master join on `ndc11`.
- This keeps `reference_number` populated for both ERP and wholesaler rows, and the distinct `reference_number` count should match the distinct `ndc11` count (because PM enrichment is NDC-keyed for this extract).

### 3) Product scope sanity (gross out-of-scope scan)
- Top spend categories are consistent with IV solutions and irrigation.
- Keyword scan for obvious non-IV supplies found 0 hits for:
  - wristband, drape, id band, label, glove, syringe, catheter, tape, gauze

### 4) De-identification / PHI check
- `facility_id`, city, and IDN affiliation columns are not present in the exported sample.
- The only facility identifier in the output is `blinded_facility_id` (FAC_00001 style).

### 5) Coverage checks
From the summary JSON (see `generated_at` in-file):
- Rows: 26,379
  - ERP: 2,988
  - Wholesaler: 23,391
- Spend: $10,286,068.29
  - ERP: $7,084,543.94 (68.9%)
  - Wholesaler: $3,201,524.35
- Facilities: 3,103
- NDCs: 65
- Geography coverage:
  - 99.3% rows have `state`
  - 99.3% rows have `zip3`
- Product description coverage: 100.0% rows have `description`

Additional note:
- `product_group_category` is missing for ~20.6% of rows (~$1.08M spend). This appears to be a **product master data sparsity** issue (description/manufacturer are still present).

## Spend reconciliation (why totals changed vs earlier draft)
- Two previously-included reference numbers were removed after provenance review showed they were **incorrect matches** (non-IV items):
  - `reference_number=40992`
  - `reference_number=34813`
- Those two reference numbers contributed approximately **$32.46M** in ERP spend during 2024–2025, which explains most of the drop from ~$42.7M to ~$10.3M.

## Repro steps
1) Regenerate extracted CSVs (BigQuery → exports):
   - `/.venv/bin/python runs/2026-01-27__fy27-email-handoff/scripts/extract_enriched_sample.py`
2) Regenerate final enriched sample + summary + dictionary:
   - `/.venv/bin/python runs/2026-01-27__fy27-email-handoff/scripts/generate_enriched_sample.py`

## Known gaps / follow-ups
- The two excluded NDCs (`6521949510`, `6521949720`) are currently `NO_MATCH`. To include them, we need a **non-guessy** mapping path (e.g., validated item master reference number or other deterministic key).
- `product_group_category` is null for a meaningful slice of rows; if this field is critical for analysis, we may need to source/derive a category mapping separately.
