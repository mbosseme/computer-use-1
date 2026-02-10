# Run Handoff: 2026-02-10__portfolio-expansion

## RUN_ID
`2026-02-10__portfolio-expansion`

## Branch
`run/2026-02-10__portfolio-expansion`

---

## Mission
Investigate the feasibility of expanding Premier's portfolio analytics from the legacy **Transaction Analysis (TSA)** data model to the newer **Provider Invoice Workflow History** data model. The core question: Can Workflow History serve as a viable replacement/complement to TSA for health-system-level spend analysis?

---

## Session 1 Summary (2026-02-10)

### Phase 1: Entity Code Mapping Attempt (FAILED)
- **Tried**: Join the two data models on `health_system_entity_code` (Workflow) ↔ entity codes in TSA.
- **Outcome**: FAILED — `health_system_entity_code` in Workflow History is ~50% NULL (42.6M of 89M rows). Only 33 distinct non-null codes exist.
- **`direct_parent_entity_code`** is 100% null (single distinct value = literal `null` string for all 89M rows).
- **Learning**: Entity code fields in the Workflow History table are unusable for cross-referencing to TSA at scale.

### Phase 2: Name-Based Mapping (SUCCEEDED)
- **Strategy pivot**: Map health systems by **name** instead of entity code.
- **Process**:
  1. Extracted Top 20 health systems by volume from each table.
  2. Ran Python fuzzy matching (`scripts/map_health_systems.py` using `difflib.SequenceMatcher`) to generate candidate pairs.
  3. **User manually reviewed and corrected** the mappings (removed bad matches like Northwell→Acurity; corrected EM_Fletcher→University of Vermont parent mapping; removed EM_CCH).
  4. Locked in 9 high-confidence mappings.
- **Key schema insight**: Workflow uses `health_system_name`; TSA uses `Health_System_Name` OR `Direct_Parent_Name` (some Workflow systems map to TSA parents, not direct system names).

### Phase 3: Spend Comparison (9 Systems, 2025)
- **Script**: `scripts/gen_mapped_spend_comparison.sql` — uses hardcoded `CASE` statements for precise 1-to-1 join.
- **Results** (2025, all months):

| Mapping Key | Workflow Name | WF Spend ($B) | TSA Spend ($B) | Capture Ratio | Pattern |
|---|---|---|---|---|---|
| ADVENTHEALTH | AdventHealth (AHS Florida) | 8.4 | 3.7 | 226% | Over-capture |
| OSF | EM_OSF | 2.7 | 1.0 | 272% | Over-capture |
| UVM | EM_Fletcher | 2.1 | 0.9 | 221% | Over-capture |
| ADVOCATE | Advocate Health | 1.6 | 3.0 | 54% | Under-capture |
| ADVENTIST | Adventist Health (California HQ) | 1.5 | 0.9 | 167% | Over-capture |
| UHS | EM_UHS | 1.4 | 1.4 | ~100% | Matched |
| HONORHEALTH | EM_HonorHealth | 1.0 | 0.7 | 155% | Over-capture |
| RENOWN | EM_Renown | 0.6 | 0.4 | 142% | Over-capture |
| UCI | EM_UCI | 0.4 | 0.4 | ~100% | Matched |

- **Advocate under-capture**: Likely because TSA has the combined Advocate + Aurora entity under the legacy alliance name. Workflow may only capture from one side post-merger.

### Phase 4: OSF Deep Dive — Root Cause Analysis (COMPLETED)
Drilled into OSF HealthCare to explain why Workflow ($2,717M) is 272% of TSA ($1,000M). **Root cause: Scope difference, not duplication.**

#### Monthly Coverage
- Both sources cover all 12 months of 2025. No partial-year issue.
- Workflow: ~$195–276M/month (545K total rows). TSA: ~$74–104M/month (1.67M total rows).
- TSA has more rows because it's line-item-level (per product); Workflow is header-level (per invoice).

#### Data Source Split (Workflow)
- **ERP only**: $1,739M across 261K rows (247K distinct invoices)
- **ERP/Remitra**: $978M across 304K rows (300K distinct invoices)
- **Remitra only**: $0 (no Remitra-only rows for OSF)
- **No double-counting**: ERP vs ERP/Remitra invoice numbers are 99.7% non-overlapping.

#### Facility Coverage
- Workflow: 38 org descriptions, 24 facility entity codes (all under `direct_parent_name = 'OSF HealthCare'`).
- TSA: 42 facility names, including associated entities like Blessing Hospital, McDonough District Hospital, Kirby Medical Center.
- Core OSF hospitals appear in both with comparable facility-level distributions.

#### Vendor-Level Categorization (THE KEY FINDING)
Classified all $2,717M of OSF Workflow spend into vendor categories:

| Category | $ Millions | % of WF Total | In TSA? |
|---|---|---|---|
| **Pharma / Drug Distributors** (AmerisourceBergen $326M) | $334M | 12.3% | Barely ($4M) |
| **Insurance / Benefits / Payroll** (BCBS $213M, life ins, payroll deductions) | $267M | 9.8% | No |
| **Intercompany / Internal** (Healthcare Solutions LLC $236M, Pointcore, Touchette, foundation) | $333M | 12.2% | No |
| **Staffing / Professional / Academic** (Medical Solutions $56M, anesthesia, university contracts) | $284M | 10.4% | No |
| **IT / Software** (SYNNEX $29M, Epic $18M, Microsoft $18M, HP, Dell) | $98M | 3.6% | Minimal |
| **Capital / Utilities / Real Estate** (Construction $69M, Illinois Tool Works $31M, energy) | $128M | 4.7% | Partially |
| **Food / Nutrition** | $21M | 0.8% | Minimal |
| **Legal / Consulting / Other Services** | $23M | 0.8% | No |
| **OneTime Vendors** | $13M | 0.5% | No |
| **Med/Surg Supply Chain (TSA-comparable)** | **$1,217M** | **44.8%** | **Yes** |
| **TOTAL** | **$2,717M** | 100% | |

#### The $217M Residual Gap (Med/Surg $1,217M vs TSA $1,000M)
After removing non-supply-chain categories, the remaining ~22% gap is explained by:
1. **TSA overhead allocations**: $149M in TSA under "HOSPITALS SERVICES EXPENSES" ($85M) + "UNKNOWN" ($64M) — allocated overhead categories that inflate TSA but don't match specific vendor invoices.
2. **Vendor entity code fragmentation**: Same vendor mapped to different subsidiary codes (e.g., Medtronic appears as `MN2140` in Workflow, `643965` in TSA — both are Medtronic subsidiaries).
3. **Long-tail vendors**: ~$70–80M in smaller vendors with slightly different scope boundaries.

#### Root Cause Conclusion
> **Workflow History is an Accounts Payable data model** — it captures every invoice processed through the ERP and/or Remitra, including pharma wholesale, insurance premiums, payroll deductions, IT contracts, professional services, and intercompany transfers.
>
> **TSA is a Med/Surg Supply Chain purchasing feed** — narrowly scoped to product-level transactions with vendor/manufacturer normalization.
>
> Once you subtract non-supply-chain categories (55% of Workflow spend for OSF), the two sources align within ~20%, which is explainable by vendor hierarchy differences and TSA overhead allocations.

---

## Artifacts Created

| File | Purpose | Status |
|---|---|---|
| `docs/validated_health_system_mapping.md` | Explicit mapping table for 9 health systems across both data models | Committed |
| `scripts/gen_mapped_spend_comparison.sql` | SQL with hardcoded CASE logic to compare 9 mapped systems (2025) | Committed |
| `scripts/map_health_systems.py` | Python fuzzy matcher for initial candidate discovery | Committed |
| `scripts/gen_spend_comparison_2025.sql` | Earlier iteration of comparison SQL | Committed |
| `scripts/gen_stable_systems_spend_comparison.sql` | Earlier iteration for "stable" systems | Committed |

---

## Data Sources Reference

### Workflow History (New)
- **Table**: `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
- **Rows**: 89M | **Scope**: All ERP + Remitra invoices (AP-level)
- **Health system field**: `health_system_name` (796 distinct)
- **Vendor fields**: `vendor_name` (raw, 360K distinct), `premier_vendor_name` (cleansed, 18.7K distinct), `vendor_entity_code` (21.7K distinct, 15% null)
- **Amount field**: `invoice_total_amount` (header-level total)
- **Date field**: `vendor_invoice_date`
- **Data source indicator**: `data_source` (ERP / Remitra / ERP/Remitra)
- **Data dictionary**: `docs/data_dictionaries/abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history.md`

### TSA (Legacy)
- **Table**: `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
- **Rows**: 819M | **Scope**: Med/surg supply chain purchasing (line-item-level)
- **Health system field**: `Health_System_Name`, also `Direct_Parent_Name` for parent-level rollups
- **Vendor fields**: `Vendor_Name` (cleansed, 25K distinct), `Vendor_Entity_Code` (25K distinct)
- **Amount fields**: `Base_Spend` (no markup), `Landed_Spend` (with markup)
- **Date field**: `Transaction_Date` (TIMESTAMP)
- **Facility field**: `Facility_Name` (13K distinct)
- **Data dictionary**: `docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md`

### Key Cross-Reference Fields
- **Health system**: `health_system_name` (WF) ↔ `Health_System_Name` or `Direct_Parent_Name` (TSA) — requires hardcoded mapping
- **Vendor**: `vendor_entity_code` (WF) ↔ `Vendor_Entity_Code` (TSA) — joinable but vendor hierarchy fragmentation exists
- **Facility**: `facility_entity_code` + `org_description` (WF) ↔ `Facility_Name` (TSA) — `facility_entity_name` in WF is 100% null

---

## Known Issues / Gotchas

1. **Entity code fields are broken** in Workflow History:
   - `health_system_entity_code`: 50% NULL, only 33 distinct values
   - `direct_parent_entity_code`: 100% NULL (all rows = literal `null`)
   - `facility_entity_name`: 100% NULL
   - Must use name-based approaches for health system mapping

2. **NULL representation inconsistency**: Workflow uses both string `'NULL'` and actual SQL NULL for missing values. Always filter with `AND col IS NOT NULL AND col != 'NULL'`.

3. **Vendor hierarchy fragmentation**: The same parent company (e.g., Medtronic) can appear under different child entity codes in each system (e.g., `MN2140` = Medtronic Inc in WF, `643965` = Medtronic USA Inc in TSA). Need `vendor_top_parent_entity_code` for proper roll-up, but it's 21% null in WF.

4. **Header vs line-item granularity**: WF `invoice_total_amount` is header-level. TSA `Base_Spend` is line-item-level. Comparing totals works; comparing per-invoice amounts requires aggregation awareness.

5. **Advocate anomaly**: Advocate Health shows 54% capture ratio (WF < TSA). Likely because TSA still has the combined Advocate + Aurora alliance entity, while Workflow may only capture from one post-merger entity.

6. **No Remitra-only rows for ERP systems**: OSF, for example, has only data_source = 'ERP' or 'ERP/Remitra', not standalone 'Remitra'. The 45.8M 'Remitra' rows globally are likely from health systems that use Remitra but haven't connected their ERP.

---

## Session 2 Summary (continuation)

### Mission Reframing
User reframed the core objective: the REAL goal is **not** just comparing two data models. It is:
> "Identify a set of health systems present in the TSA that is substantial enough to extrapolate from to make estimations for at least the whole of Premier's GPO membership (~25% of US healthcare)."

Target: ≥20 health systems with comprehensive non-labor purchasing data across 4 service lines (Clinical, Non-Clinical, Pharma, Food). The WF comparison is a **calibration tool** — use it to understand what "comprehensive" looks like, then expand in TSA.

### Key Analysis Steps Completed
1. **Universe establishment**: Identified 80+ TSA health systems with 12-month coverage and >$100M spend in CY2025.
2. **Expanded WF-TSA mapping**: Grew from 9 to 15 cross-referenced systems. Computed WF supply-chain-only spend by applying comprehensive vendor categorization (pharma, insurance, staffing, IT, overhead, government, food, intercompany removal).
3. **Capture ratio calibration**: 6 systems have TSA/WF_SC_only ≥0.85 (ADVOCATE 3.0x, HONORHEALTH 1.86x, UCI 1.89x, METHODIST_LB 2.03x, CFNI 1.16x, ADVENTIST 0.90x). These confirm TSA can capture comprehensive supply chain data.
4. **Service line classification**: Mapped ~870 TSA Contract_Category values into 4 buckets (Clinical, Non-Clinical, Pharma, Food). Applied filter: each ≥2% of system spend AND ≥$5M.
5. **Structural finding — FOOD GAP**: Food is <1% of total TSA platform spend (~$1B out of $115B+). Only 3 systems have food ≥2%. This is structural, not a per-system data quality issue.
6. **Cohort identified**: 29 unique health systems with 3+ service line coverage, spanning 25+ states, ~80,000 beds, ~$57B annual TSA volume. (Originally 27; post-audit added AdventHealth and St Luke's University, removed Midland duplicate.)

### Deliverable
- **[comprehensive_cohort_analysis.md](exports/comprehensive_cohort_analysis.md)** — Full analysis with tiered cohort, capture ratio calibration, service line distributions, geographic coverage, risk assessment, and recommendations.

---

## What's Left To Do

### Immediate Next Steps
1. ~~**Validate 3-5 TSA-only cohort systems**~~: ✅ Done — spot-checked PRISMA (Tier 1) and ECU (Tier 3) top vendors/categories; both confirmed comprehensive. Also validated service line classification sensitivity (debatable NC categories don't affect any system's qualification).
2. **Build per-bed spend benchmarks**: For each service line, compute $/bed ratios across the cohort to establish baseline for extrapolation.
3. **Map cohort to Premier GPO membership universe**: Use `sa_sf_dhc_join` demographics to determine how representative the cohort is (bed mix, geography, hospital type).

### Medium-Term
4. **Develop extrapolation model**: Cohort spend × membership scale factor, accounting for size/type/geography.
5. **Food supplementary analysis**: If food is critical, investigate Supplier Sales data or industry benchmarks (~3-5% of operating expenses).
6. **Contract coverage analysis**: Assess which products/categories have Premier contracts vs off-contract purchasing (future scope per user).

### Strategic Decisions Needed
7. **Accept 3-service-line standard?** Given TSA's structural food gap, is Clinical + Non-Clinical + Pharma sufficient for extrapolation?
8. **Include GPO alliances?** ACURITY ($29.9B), ALLSPIRE ($7.8B), ADVOCATE ALLIANCE ($17.6B) were excluded as multi-system alliances. Should they be included as "super-systems" for volume coverage?
9. **Cohort size vs quality tradeoff**: 29 systems identified. Prioritize Tiers 1-2 (16 systems with food data) or use all 29?

---

## Blockers
- None currently. All data access is working.
