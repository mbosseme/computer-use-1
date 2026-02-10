# Continuation Prompt for Next Agent

Copy-paste everything below the `---` line into a new conversation.

---

## Context: Portfolio Expansion — Workflow History vs TSA Comparison

You are continuing work on RUN_ID `2026-02-10__portfolio-expansion` (branch: `run/2026-02-10__portfolio-expansion`). A previous session completed significant analysis. Before doing anything, read these files to orient yourself:

1. **`runs/2026-02-10__portfolio-expansion/HANDOFF.md`** — Full session narrative, data source reference, known issues/gotchas, and suggested next steps.
2. **`runs/2026-02-10__portfolio-expansion/exports/osf_deep_dive_analysis.md`** — Detailed working paper with all OSF query results, tables, and root cause analysis.
3. **`docs/validated_health_system_mapping.md`** — The 9 validated health system name mappings between the two data models.
4. **`scripts/gen_mapped_spend_comparison.sql`** — The SQL with hardcoded CASE logic used for the 9-system spend comparison.

### What Was Done (Session 1)

**Mission**: Determine whether Premier's `provider_invoice_workflow_history` table (89M rows, AP-level) can replace or supplement the legacy `transaction_analysis_expanded` table (819M rows, med/surg supply chain) for health-system-level spend analytics.

**Key Findings**:
- Entity code fields in Workflow History are broken (~50-100% NULL). Must use name-based mapping.
- 9 health systems were successfully mapped by name (user-validated). See `docs/validated_health_system_mapping.md`.
- Most mapped systems show Workflow capturing 1.4x–2.7x more spend than TSA. One system (Advocate) shows 54% under-capture.
- **Root cause** (confirmed via deep dive on OSF, the most extreme case at 272%): **Workflow History is an Accounts Payable model** (all invoices — pharma, insurance, payroll, IT, intercompany, etc.). **TSA is a Med/Surg Supply Chain purchasing feed** (narrow product-level scope). 55% of OSF's Workflow spend is non-supply-chain. After removing it, the gap shrinks to ~22%, explainable by vendor hierarchy fragmentation and TSA overhead allocations.

### What's Left To Do (Prioritized)

1. **Confirm the scope-difference hypothesis generalizes**: Run the same vendor categorization waterfall for **AdventHealth** (226% capture ratio) to see if the same ~55% non-supply-chain pattern holds.
2. **Investigate Advocate under-capture**: Why does Workflow show only 54% of TSA for Advocate Health? Is it a post-merger entity split (Advocate + Aurora)?
3. **Build a reusable "TSA-scope filter"**: Create a SQL filter/view that removes non-supply-chain vendors from Workflow History, making it comparable to TSA. Base it on the category rules from the OSF deep dive (pharma, insurance, intercompany, staffing, IT, capital, food, legal, one-time — all described in `exports/osf_deep_dive_analysis.md`).
4. **Expand the mapping table**: Map additional health systems beyond the current 9 (candidates: Dignity Health, Catholic Health Initiatives, Northwell Health, Tenet Healthcare, EM_UCSD).
5. **Vendor entity code roll-up strategy**: Build a vendor parent-to-child crosswalk to normalize vendor codes across the two models.

### Critical Gotchas (from Session 1)

- **NULL representation**: Workflow uses both string `'NULL'` and actual SQL NULL. Always filter with `AND col IS NOT NULL AND col != 'NULL'`.
- **Header vs line-item**: Workflow `invoice_total_amount` is per-invoice header. TSA `Base_Spend` is per-product line item. Compare at aggregated totals only.
- **Vendor hierarchy fragmentation**: Same parent vendor has different child entity codes in each system (e.g., Medtronic = `MN2140` in WF, `643965` in TSA).
- **`facility_entity_name` is 100% NULL** in Workflow. Use `org_description` + `facility_entity_code` instead.

### BigQuery Tables

- **Workflow**: `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
- **TSA**: `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
- **Data dictionaries**: see `docs/data_dictionaries/` for both tables.
