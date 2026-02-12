# Continuation Prompt for Next Agent

Copy-paste everything below the `---` line into a new conversation.

---

## Context: Portfolio Expansion — TSA Cohort for Non-Labor Spend Extrapolation

You are continuing work on RUN_ID `2026-02-10__portfolio-expansion` (branch: `run/2026-02-10__portfolio-expansion`).

### Bootstrap (read these first)

1. **`runs/2026-02-10__portfolio-expansion/HANDOFF.md`** — Full narrative across 2 sessions, data source reference, known issues/gotchas, all artifacts, and prioritized next steps.
2. **`runs/2026-02-10__portfolio-expansion/exports/comprehensive_cohort_analysis.md`** — **PRIMARY DELIVERABLE**: 29-system tiered cohort with methodology, service line classification, capture ratios, demographic enrichment, risk assessment, and validation notes.
3. **`runs/2026-02-10__portfolio-expansion/ANALYSIS_PLAN.md`** — 6-phase analysis plan (all phases executed and audited).

Optional deeper context:
- `runs/.../exports/analyst_briefing.md` — Concise narrative sent to analyst team
- `runs/.../exports/osf_deep_dive_analysis.md` — OSF vendor categorization deep dive (Session 1)
- `docs/validated_health_system_mapping.md` — Original 9-system name mapping (Session 1)
- `notes/agent-runs/2026-02-10__portfolio-expansion-session-2.md` — Session 2 run log

### What Was Done (Sessions 1 + 2)

**Mission**: Identify ≥20 health systems in Premier's Transaction Analysis (TSA) data with comprehensive non-labor purchasing across Clinical, Non-Clinical, and Pharma service lines, suitable for extrapolation to Premier's GPO membership (~25% of US healthcare).

**Result**: **29 health systems** identified across 3 tiers:
- **Tier 1** (3 systems): All 4 service lines including Food (Prisma, Health First, VCU)
- **Tier 2** (13 systems): 3 service lines + some food data (UPMC through Midland)
- **Tier 3** (13 systems): 3 service lines, no food (AdventHealth through Greater Baltimore)
- **Cohort total**: ~80,000 beds, ~$57B annual TSA volume, 25+ states

**Key structural finding**: Food is <1% of TSA platform-wide ($1B of $115B+). "Comprehensive" = Clinical + Non-Clinical + Pharma.

**Validated**: Post-hoc audit caught and corrected 2 inclusion errors + 1 duplicate. Spot-checked PRISMA and ECU. Sensitivity-tested service line classification.

### What's Left To Do (Prioritized)

1. **Per-bed spend benchmarks** (highest priority): Compute $/bed ratios for each service line across the 29-system cohort using bed counts from `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join`. This is the bridge from cohort-level findings to extrapolation.

2. **GPO membership mapping**: Compare cohort demographics (size, type, geography) against the full Premier GPO membership universe (~4,000+ hospitals) to quantify representativeness and coverage gaps.

3. **Extrapolation model**: Cohort spend × membership scale factor, segmented by system size, hospital type, and region.

4. **Food supplementary analysis**: If food is in scope, pull from Supplier Sales data or apply industry benchmarks (~3-5% of operating expenses).

### BigQuery Tables

| Table | FQN | Purpose |
|-------|-----|---------|
| TSA | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` | Primary — 819M rows, med/surg purchasing with `Contract_Category` taxonomy |
| WF | `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history` | Calibration — 89M rows, full AP invoices |
| Demographics | `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join` | Facility enrichment — beds, types, geography (filter `dhc_firm_type='Hospital'`) |

Data dictionaries: `docs/data_dictionaries/`

### Critical Gotchas

- **TSA is med/surg only; WF is full AP.** Capture ratios require filtering WF to supply-chain-only spend first.
- **Food is structurally absent from TSA** (<1% platform-wide). Don't filter on 4 service lines.
- **NULL representation in WF**: Both string `'NULL'` and actual SQL NULL exist. Filter with `AND col IS NOT NULL AND col != 'NULL'`.
- **Entity codes are broken in WF**: `health_system_entity_code` is 50% NULL, `direct_parent_entity_code` is 100% NULL. Use name-based mapping only.
- **Service line classification**: ~870 `Contract_Category` values mapped to 4 buckets. Full mapping in the comprehensive analysis appendix. 6 "debatable" categories (clinically-adjacent purchased services) are classified as Non-Clinical — sensitivity-tested and confirmed robust.
