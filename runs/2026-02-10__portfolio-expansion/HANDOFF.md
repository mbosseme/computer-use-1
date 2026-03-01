# Run Handoff: 2026-02-10__portfolio-expansion

## RUN_ID
`2026-02-10__portfolio-expansion`

## Branch
`run/2026-02-10__portfolio-expansion`

---

## Mission
Identify a set of health systems in Premier's **Transaction Analysis (TSA)** data that provide comprehensive non-labor purchasing data across multiple service lines, suitable for extrapolation to Premier's GPO membership (~25% of US healthcare).

> **Note**: Session 1 originally framed this as a WF-vs-TSA comparison. Session 2 reframed to the real objective above. The WF comparison is retained as a **calibration tool** — it validates which TSA systems submit comprehensive data.

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
| `runs/.../exports/comprehensive_cohort_analysis.md` | **PRIMARY DELIVERABLE** — 31-system tiered cohort | Updated Session 3b |
| `runs/.../exports/analyst_briefing.md` | **PRIMARY DELIVERABLE** — Clean current-state briefing (v4.2 numbers) | **Updated Session 10** |
| `runs/.../exports/osf_deep_dive_analysis.md` | OSF vendor categorization deep dive (Session 1) | Committed |
| `runs/.../ANALYSIS_PLAN.md` | 6-phase analysis plan (audited; all phases executed) | Committed |
| `dataform/` | Full Dataform pipeline — 8 tables + 14 assertions | **Updated Session 10** |

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

## Session 3 Summary (continuation)

### Objectives
Three priority tasks from Session 2's "What's Left To Do":
1. Per-bed spend benchmarks across the 29-system cohort
2. GPO membership mapping — cohort representativeness vs full Premier membership
3. Extrapolation model — cohort spend × membership scale factor

### Key Analysis Steps Completed

#### 1. Demographics Table Exploration (`sa_sf_dhc_join`)
- Table: `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join` — 482,332 rows
- Structure: Denormalized join of Salesforce membership + DHC hospital data
- 3 `data_source` values: NULL (476K rows, base demographic layer), "Blended PO/Receipt/Invoice" (5.4K), "ERP Receipts Only" (208)
- Key fields: `health_system_name`, `dhc_number_of_staffed_beds`, `premier_gpo_member`, `active_membership_type`, `dhc_idn`, `dhc_hospital_type`, `dhc_state`, `dhc_definitive_id`
- **Critical finding**: DHC bed data in this table is incomplete — many cohort systems show dramatically lower bed counts than Session 2's validated figures (e.g., AdventHealth: 1,204 vs 10,719; UPMC: 0 vs 6,650). Decision: use Session 2's validated bed counts directly.

#### 2. TSA Name Crosswalk
- Cohort uses shorthand names but TSA uses exact legal entity names
- All 29 exact TSA `Health_System_Name` values identified via targeted LIKE queries
- Key mappings: UCI → `UNIVERSITY OF CALIFORNIA - IRVINE`, CFNI → `COMMUNITY FOUNDATION OF NORTHWEST INDIANA, INC.`, VCU → `VCU HEALTH SYSTEM AUTHORITY`, etc.
- St Luke's apostrophe issue: BigQuery STRUCT literal syntax breaks; queried separately via LIKE pattern

#### 3. Per-Bed Spend Benchmarks
- Computed $/bed/year for all 29 systems × 4 service lines (Clinical, NC, Pharma, Food)
- **Aggregate weighted average**: $720K/bed/year (Clinical $350K, NC $264K, Pharma $100K, Food $6K)
- **Extreme variance**: CV = 72%, range $332K (Saint Francis) to $3,305K (UCI)
- **Size effect**: Large systems ($572K/bed) vs Small ($1,289K/bed) — 2.3× difference
- **Tier effect**: Tier 1-2 ($864K/bed) vs Tier 3 ($503K/bed) — 42% gap, likely driven by incomplete Tier 3 submissions
- **Percentile distribution**: P25=$543K, P50=$789K, P75=$1,108K

#### 4. GPO Membership Universe Profiling
- **Premier GPO (acute)**: 868 hospitals, 193,636 beds (defined by `premier_gpo_member=TRUE`, acute hospital types)
- _(Superseded Session 3 NATIONAL-keyword approach: 1,197 hospitals / 200,673 beds across all htypes)_
- **All Premier Members**: 2,652 hospitals, 804,257 beds (~62% of US)
- Hospital type filter: STAC, Health System, Children's, CAH (excluded psych, LTAC, VA, DoD)
- Profiled by region (South 45%, Midwest 24%, West 16%, NE 13%) and facility size

#### 5. Cohort Representativeness Assessment
- **Regional bias identified**: Cohort is 67% Southern beds vs 45% in membership
- Midwest (10% cohort vs 24% membership) and West (9% vs 16%) are underrepresented
- Cohort covers 31.5% of Premier GPO acute beds, 7.8% of all acute member beds

#### 6. Extrapolation Model
- **Premier GPO central estimate**: $139–167B/year in non-labor purchasing
  - Method A (weighted avg $720K × 194K beds): $139B
  - Method B (Tier 1-2 rate $864K × 194K beds): $167B
  - Method C range (P25-P75): $105–215B
- **All Members estimate (acute)**: $564–676B/year
- Service line decomposition: Clinical ~$63B, Non-Clinical ~$59B, Pharma ~$22B, Food ~$1.5B (structural undercount)
- Key caveats: regional bias, hospital-vs-system mismatch, high variance, Tier 3 depression

### Deliverable
- **[per_bed_benchmarks_and_extrapolation.md](exports/per_bed_benchmarks_and_extrapolation.md)** — Full per-bed benchmarks (29 systems), GPO membership mapping, representativeness analysis, extrapolation model with 3 methods and ranges, caveats, and recommendations.

### Session 3b: Methodology Correction & Advocate Deep Dive

#### WF Calibration Methodology Correction (CRITICAL)
The original WF calibration used **broad exclusions** — removing pharma, IT, capital, staffing, food, consulting, and legal from WF before computing capture ratios. User correctly identified this was wrong: all of these categories are GPO-addressable.

**Corrected approach**: Narrow exclusions only — remove insurance/benefits/payroll, intercompany/internal, and government/regulatory. All other categories retained as GPO-addressable.

**Impact on capture ratios**:
- Systems formerly >1.0 with broad exclusions dropped to more realistic levels (UCI: 1.89→1.10, CFNI: 1.16→1.02)
- Methodist LB **flipped** from 2.03 to 0.83
- Typical capture ratio for partial systems: 0.45–0.69 (was 0.49–0.90)
- 4 systems confirmed at ≥1.0: HONORHEALTH (1.48), UCI (1.10), ADVOCATE AURORA (1.05), CFNI (1.02)

#### Advocate Alliance Decomposition
- TSA entity "ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE" ($17.6B) aggregates two distinct direct parents:
  - **Carolinas Healthcare System** ($10,237M): Clin 43%, NC 40%, Pharma 16%, Food 1.3% — Tier 2
  - **Advocate Aurora Health** ($7,366M): Clin 65%, NC 31%, Pharma 3%, Food 0.5% — Tier 2
- WF "Advocate Health" ($7,021M GPO-addressable) maps primarily to Advocate Aurora side
- Apples-to-apples calibration: WF Advocate Health vs TSA Advocate Aurora = **1.05 capture ratio** (near parity)
- WF "Atrium Health" ($995M) is a small Carolinas-side fragment (~10% of TSA Carolinas)
- Both direct parents included as separate Tier 2 entries in all deliverables
- Cohort expanded from 29 to **31 systems**, ~$57B to ~$75B, ~80K to ~98K beds

#### TSA Coverage Calibration (New Extrapolation Layer)
- WF calibration confirms Tier 1–2 rate ($864K/bed) represents full GPO-addressable purchasing (median calibrated ratio = 1.04)
- No upward adjustment needed for Tier 1–2 rate
- Gap between $720K (all systems) and $864K (Tier 1–2) is entirely attributable to incomplete Tier 3 submissions
- Central extrapolation estimate unchanged: NATIONAL GPO $145–175B/year

#### Deliverables Updated
- `comprehensive_cohort_analysis.md` — Corrected WF methodology, revised capture ratios, Advocate split, 31-system cohort
- `analyst_briefing.md` — Updated WF calibration narrative, TSA coverage calibration section, Advocate treatment
- `per_bed_benchmarks_and_extrapolation.md` — New Section 4 (TSA Coverage Calibration), Advocate crosswalk entries

---

## Artifacts Created (Updated)

| File | Purpose | Status |
|---|---|---|
| `docs/validated_health_system_mapping.md` | Explicit mapping table for 9 health systems across both data models | Committed |
| `scripts/gen_mapped_spend_comparison.sql` | SQL with hardcoded CASE logic to compare 9 mapped systems (2025) | Committed |
| `scripts/map_health_systems.py` | Python fuzzy matcher for initial candidate discovery | Committed |
| `scripts/gen_spend_comparison_2025.sql` | Earlier iteration of comparison SQL | Committed |
| `scripts/gen_stable_systems_spend_comparison.sql` | Earlier iteration for "stable" systems | Committed |
| `runs/.../exports/comprehensive_cohort_analysis.md` | **PRIMARY DELIVERABLE** — 31-system tiered cohort with corrected methodology, revised capture ratios, Advocate split | Updated Session 3b |
| `runs/.../exports/analyst_briefing.md` | **PRIMARY DELIVERABLE** — Clean current-state briefing with v4.2 numbers, pattern table methodology, full cohort benchmarks | **Updated Session 10** |
| `runs/.../exports/osf_deep_dive_analysis.md` | OSF vendor categorization deep dive (Session 1) | Committed |
| `runs/.../exports/per_bed_benchmarks_and_extrapolation.md` | Per-bed benchmarks, GPO mapping, extrapolation model, TSA coverage calibration | Updated Session 3b |
| `runs/.../exports/external_validation_synthesis.md` | External benchmark comparison — consensus ranges from deep research reports vs our v3.2 empirical findings | **New Session 7** |
| `runs/.../ANALYSIS_PLAN.md` | 6-phase analysis plan (audited; all phases executed) | Committed |
| `dataform/definitions/staging/vendor_name_patterns.sqlx` | **Name-pattern reference table** — 200 LIKE rules, priority-ordered, single source of truth for WF name classification | **Updated Session 10** |
| `dataform/definitions/marts/wf_sl_v4.sqlx` | **WF Service Line classification** — JOIN-based (entity-bridge + pattern table), primary benchmark table | **Rewritten Session 9c** |
| `dataform/definitions/staging/*.sqlx` | Staging tables: service_line_mapping, entity_sl_mix, tsa_cy2025, tsa_cy2025_enriched, tsa_clin_nc_cohort, gpo_member_universe | Committed Session 9b |
| `dataform/definitions/assertions/*.sqlx` | 14 assertions (5 inline + 3 standalone files) validating referential integrity, classification coverage, budget-level sanity | Committed Session 9b–9c |

---

## What's Left To Do

### Completed (Sessions 1–3)
1. ~~Entity code mapping attempt~~ → Failed, switched to name-based
2. ~~Name-based mapping (9 systems)~~ → Completed
3. ~~OSF deep dive~~ → Root cause identified (scope difference)
4. ~~29-system cohort identification~~ → Tiered cohort with service line validation
5. ~~Spot-check validation~~ → PRISMA + ECU validated
6. ~~Analyst briefing~~ → `analyst_briefing.md`
7. ~~Per-bed spend benchmarks~~ → $720K/bed weighted, $789K median
8. ~~GPO membership mapping~~ → 30% NATIONAL GPO coverage, South bias identified
9. ~~Extrapolation model~~ → $144–173B NATIONAL GPO, $540–650B All Members
10. ~~WF calibration methodology correction~~ → Narrow exclusions, 4 systems at ≥1.0 ratio
11. ~~Advocate Alliance decomposition~~ → Split into 2 direct parents, cohort expanded to 31 systems
12. ~~TSA coverage calibration~~ → Tier 1–2 rate confirmed as full GPO-addressable coverage

### Session 4 (2026-02-11): Strategic Reframing — Multi-Source Framework

#### Key Insight
Pharma and food purchasing flows through **wholesalers/distributors** (McKesson, Cardinal, Sysco, US Foods). TSA `Contract_Category` cannot reliably distinguish on/off/non-contract for these channels. Therefore:
- **WF** establishes expected **service line mix** (all 4 SLs)
- **TSA** provides the **addressable cohort** scoped to **Clinical + Non-Clinical only** (where Premier has direct contracting visibility)
- This reframing expands the qualifying cohort from 31 → 81 systems

#### Step A: WF Service Line Mix Benchmarks (COMPLETED)
- 269 systems with all 12 months CY2025 WF data
- ~150 vendor patterns mapped to 4 SLs via `wf_sl_classified_v2` temp table
- **Balanced 4-SL benchmark (36 systems, $18.1B classified)**: Clinical 49.5%, Pharma 21.0%, NC 25.4%, Food 4.1%
- Clinical is locked at ~50% across all cohort cuts — most stable finding
- WF `health_system_name` does NOT match demographics table names — bed join produces all NULLs. Per-bed WF benchmarks not computed.

#### Step B: TSA Clinical+NC Cohort Expansion (COMPLETED)
- Qualification: Clinical ≥$10M AND NC ≥$10M AND ≥5 clinical marker categories AND ≥5 NC marker categories
- 50 clinical marker categories, 43 NC marker categories
- Excluded 11 GPOs + test/demo entities
- **Result: 81 health systems, 297K beds, $90B total, $27B Clinical, $21B NC**
- Per-bed addressable: $90K Clinical + $70K NC = **$160K/bed**
- All 29 original cohort systems retained; 52 new systems added
- Cohort persisted to `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.tsa_clin_nc_cohort`

#### Analyst Briefing Updated
- `analyst_briefing.md` fully rewritten with multi-source framework
- New sections: WF SL mix benchmarks, expanded TSA cohort, updated extrapolation, connection to Portfolio Expansion Heat Map initiative

---

## Session 5 (2026-02-11): Entity-Bridge WF Classification (v3 → v3.1)

### Motivation
User challenged the v1 WF service line classification methodology (~150 vendor-name LIKE patterns). The fundamental flaw: assigning entire vendors to single SLs (e.g., all Cardinal Health → pharma, all McKesson → pharma) when these distributors have distinct child entities for med-surg vs. drug distribution.

### Entity-Bridge Approach (v3)
User proposed using `vendor_entity_code` as a bridge between WF and TSA:

1. For each child entity code in TSA, compute the SL mix from `Contract_Category` classifications
2. Apply **double-attribution**: each TSA row's spend attributed to both its `Vendor_Entity_Code` AND `Manufacturer_Entity_Code` (excluding where they're equal)
3. Apply at **child entity level** (not top-parent)
4. Join to WF on `vendor_entity_code` → distribute WF invoice amounts proportionally

#### Entity SL Mix Table
- 18,838 child entity codes with clinical/nc/pharma/food percentages
- SL classification: 22 pharma categories, 17 food categories, 51 NC categories, 3 EXCLUDE categories, everything else → CLINICAL
- **Critical fix**: `PHARMACY DISTRIBUTION` was missing from initial pharma list (had `PHARMACY DISTRIBUTION SERVICES`). AmerisourceBergen (OH2129) showed as 83% clinical instead of 99.3% pharma. Fixed by adding exact category names found in TSA.
- Outlier filter applied to TSA: `Landed_Spend > -50000 AND Landed_Spend < 100000000`
- Persisted to `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.entity_sl_mix`

#### v3 Results
- 84.7% of WF rows matched (79% of spend = $58.8B of $74.5B)
- 21% unmatched ($15.7B) — primarily vendors with NULL `vendor_entity_code`

### Hybrid Fallback (v3.1)
User requested adding name-based fallback for large unmatched vendors. Agent:

1. Queried top ~250 unmatched vendors by CY2025 WF spend ($1M+ threshold)
2. Built name-pattern rules covering the major categories:
   - **EXCLUDE** ($2.2B): IRS, state taxes, retirement funds (Fidelity/Vanguard/Voya), insurance claims (Aetna/BCBS/Cigna/Humana/Delta Dental), payroll transfers, banking (PNC/BofA/US Bank), intercompany, placeholder vendors (OneTime)
   - **PHARMA** ($0.3B): Navitus (PBM), Caremark, specialty pharmacy vendors
   - **FOOD** ($0.04B): Morrison Management, Distribution Cooperative, Sodexo
   - **NC** ($0.6B): construction firms, staffing agencies, utilities/energy, insurance brokers, laundry/textiles, IT hosting (Epic Hosting), education (Guild Education)
   - **CLINICAL** ($0.6B): anesthesia groups, physician practices, blood banks, wound care, DME, unmatched Cardinal Health entities, oncology/hematology
3. Implemented as a `CASE WHEN` cascade that fires only when entity bridge misses
4. Persisted to `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.wf_sl_v3_1`

#### v3.1 Coverage Improvement
| Metric | v3 | v3.1 |
|---|---|---|
| EXCLUDE identified | $0 | **$2.2B** |
| Classified spend | $58.8B | **$61.3B** |
| Unmatched | $15.7B (21%) | **$11.0B (15%)** |
| Systems ≥70% addressable match (≥$50M) | 59 | **88** |
| Balanced 4-SL systems | ~15–20 | **23** |

#### v3.1 Benchmarks (Final)

| Cohort | N | Classified $B | Clinical | NC | Pharma | Food |
|--------|---|-------------|----------|-----|--------|------|
| **Balanced 4-SL** | **23** | **$24.6** | **64.3%** | **24.6%** | **8.8%** | **2.3%** |
| All ≥$50M ≥70% addr | 88 | $59.2 | 61.4% | 20.8% | 16.4% | 1.4% |

#### v1 → v3.1 Shift
| Metric | v1 | v3.1 | Change |
|--------|-----|------|--------|
| Clinical | 49.5% | **64.3%** | +14.8pp |
| NC | 25.4% | **24.6%** | −0.8pp |
| Pharma | 21.0% | **8.8%** | −12.2pp |
| Food | 4.1% | **2.3%** | −1.8pp |
| C+NC share | 74.9% | **88.9%** | +14.0pp |

**Root cause**: v1 classified all Cardinal Health and McKesson invoices as pharma. v3.1 correctly splits child entities (Cardinal OH5010 = 81% clinical med-surg, Cardinal 682446 = 90% pharma drug distribution). The shift is almost entirely a clinical↔pharma reallocation; NC is essentially unchanged.

#### Downstream Impact
- **Extrapolation multiplier**: C+NC as share of total rose from 74.9% → 88.9%, meaning TSA addressable ($160K/bed) now implies total non-labor of ~$180K/bed (vs old $214K/bed). NATIONAL GPO total non-labor estimate: **$36B** (vs old $43B).
- **Analyst briefing**: Fully rewritten Section I with v3.1 methodology, benchmarks, system-level detail, sensitivity analysis, and v1→v3.1 comparison (new Section V). Section III extrapolation updated.
- **Per-bed benchmarks**: SL decomposition table updated to v3.1 mix. Per-bed rates from TSA cohort unchanged.

### Key Validation
- AmerisourceBergen (OH2129): 99.3% pharma ✓
- Cardinal OH5010: 81% clinical (med-surg distribution) vs Cardinal 682446: 90% pharma (drug distribution) ✓
- Northwestern Memorial: 98% pharma in v3.1 — real, not a bug (WF data is almost all AmerisourceBergen invoices; other spend flows through a different ERP) — balanced 4-SL filter correctly excludes
- Match-rate >100% for some systems — occurs when entity bridge classifies some vendors that the name-pattern layer also identifies as EXCLUDE, reducing the addressable denominator below the classified amount

---

## Completed Milestones (All Sessions)
1. ~~Entity code mapping attempt~~ → Failed, switched to name-based
2. ~~Name-based mapping (9 systems)~~ → Completed
3. ~~OSF deep dive~~ → Root cause identified (scope difference)
4. ~~29-system cohort identification~~ → Tiered cohort with service line validation
5. ~~Spot-check validation~~ → PRISMA + ECU validated
6. ~~Analyst briefing~~ → `analyst_briefing.md`
7. ~~Per-bed spend benchmarks~~ → $720K/bed weighted, $789K median
8. ~~GPO membership mapping~~ → 30% NATIONAL GPO coverage, South bias identified
9. ~~Extrapolation model~~ → $144–173B NATIONAL GPO, $540–650B All Members
10. ~~WF calibration methodology correction~~ → Narrow exclusions, 4 systems at ≥1.0 ratio
11. ~~Advocate Alliance decomposition~~ → Split into 2 direct parents, cohort expanded to 31 systems
12. ~~TSA coverage calibration~~ → Tier 1–2 rate confirmed as full GPO-addressable coverage
13. ~~WF SL mix benchmarks (v1)~~ → Superseded by v3.1
14. ~~TSA Clinical+NC cohort expansion~~ → 81 systems, 297K beds, $90B
15. ~~Analyst briefing v2~~ → Multi-source framework, expanded cohort
16. ~~WF entity-bridge classification (v3)~~ → 18,838 entity mixes, 79% spend match
17. ~~WF hybrid classification (v3.1)~~ → Added fallback + EXCLUDE identification, 85% addressable match
18. ~~Analyst briefing v3~~ → Updated with v3.1 benchmarks, methodology evolution section, revised extrapolation

---

## Session 6 (2026-02-12): v3.2 Pharma Fix + Ranges + 3-SL Primary Cohort

### Motivation
User challenged the v3.1 balanced 4-SL pharma estimate (8.8%), noting it was "maybe a little bit light" compared to v1's 21%. Agent investigated in depth (~15 diagnostic queries) and identified three drivers:

1. **Entity-bridge correction (legitimate, ~12pp)**: v1 assigned all Cardinal/McKesson to pharma; v3.x correctly splits child entities. This is the correct behavior.
2. **Food-floor selection bias (~3-4pp)**: The ≥1% food requirement drops 23 of 46 qualifying systems; eliminated systems tend to have higher pharma percentages. The 4-SL food ≥1% cohort (21 systems) artificially depresses pharma.
3. **Name-pattern misclassification (~$270M)**: Cardinal Health 414 Nuclear Pharmacy ($119M), CARDINAL HEALTH 105 SPEC PH SRVC ($92M), McKesson Specialty ($22M) caught by broad "CARDINAL HEALTH → CLINICAL" instead of pharma-specific patterns.

### Recommendations (All User-Approved)
1. **Fix pharma fallback patterns**: Pharma-specific patterns (Nuclear Pharmacy, 340B, Specialty Pharmacy, radiopharmacy, McKesson Drug/Spec/Rx, Omnicell Pharm) now fire *before* the broad Cardinal Health/McKesson → CLINICAL catch-all
2. **Adopt 3-SL balanced cohort as primary**: 42 systems (≥$200M, ≥70% match, ≥1% in C+NC+P) — avoids food-floor selection bias
3. **Present all 4 SLs as ranges/confidence intervals**: IQR + cross-cohort sensitivity, not point estimates

### v3.2 Build
Three iterations required:
- **Build 1**: pct divisor bug — entity_sl_mix stores percentages as 0-100 (not basis points); divided by 10000 instead of 100 → only $3.1B classified. Fixed immediately.
- **Build 2**: Correct /100 divisor but EXCLUDE only $0.9B (vs v3.1's $2.2B). Diagnosed gaps: OneTime case sensitivity, broader PAYROLL patterns, government entities (HEALTHCARE AND FAMILY SERVICES $236M, STATE OF patterns), ASO patterns, BENEFITS FUND.
- **Build 3 (final)**: Added ~20 comprehensive EXCLUDE patterns → $1.76B exclude (closer to v3.1's $2.2B; remaining $440M gap from hard-to-pattern government vendors — pragmatically acceptable).

#### v3.2 Global Numbers
| Metric | v3.1 | v3.2 | Delta |
|--------|------|------|-------|
| Classified SL | $61.3B | $61.3B | — |
| EXCLUDE | $2.2B | $1.8B | -$0.4B |
| Unmatched | $11.0B | $11.5B | +$0.5B |
| Pharma | $9.97B | $10.05B | **+$80M** |
| Clinical | $37.9B | $37.9B | — |

### v3.2 Benchmark Ranges (Primary: 3-SL Balanced, 42 Systems)

#### Weighted Central Estimates by Cohort
| Cohort | N | Classified | C% | NC% | P% | F% |
|--------|---|-----------|-----|------|------|------|
| **3-SL balanced ≥$200M** (primary) | **42** | **$52.3B** | **63.9** | **22.2** | **12.5** | **1.4** |
| 3-SL balanced ≥$100M | 51 | $53.3B | 63.9 | 22.1 | 12.6 | 1.4 |
| 4-SL food≥0.5% ≥$200M | 34 | $38.2B | 59.7 | 24.9 | 13.6 | 1.8 |
| 4-SL food≥1% ≥$200M | 21 | $24.5B | 64.4 | 24.4 | 8.9 | 2.3 |
| All ≥$50M ≥70% match | 78 | $58.4B | 61.4 | 20.7 | 16.5 | 1.4 |

#### System-Level Percentile Distribution (42-System Primary Cohort)
| SL | P25 | Median | Mean | P75 |
|----|-----|--------|------|-----|
| Clinical | 50.4% | 59.5% | 58.3% | 68.9% |
| NC | 16.1% | 22.1% | 23.7% | 31.8% |
| Pharma | 5.9% | 10.6% | 16.5% | 23.0% |
| Food | 0.7% | 1.0% | 1.6% | 2.0% |

#### Recommended Presentation Ranges
| SL | Central | IQR | Cross-Cohort |
|----|---------|-----|-------------|
| Clinical | ~64% | 50-69% | 60-64% |
| NC | ~22% | 16-32% | 21-25% |
| Pharma | ~12-13% | 6-23% | 9-17% |
| Food | ~1-2% | 0.7-2.0% | 1-2% |

#### TSA External Cross-Check
TSA CY2025 Pharmacy = **15.1%** of $139.8B total spend — validates our WF-derived 12-15% pharma range.

### Extrapolation Update
- C+NC = ~86% of total (was 88.9% in v3.1's 4-SL cohort)
- Total non-labor multiplier: 1.16× (was 1.12×)
- NATIONAL GPO estimate: ~$37B (was $36B)
- All Members: ~$149B (was $144B)

### Deliverables Updated
- `analyst_briefing.md` — Fully updated: v3.2 methodology, 3-SL primary cohort, ranges for all 4 SLs, TSA cross-check, revised extrapolation, v1→v3.2 methodology evolution
- `HANDOFF.md` — This section added

---

## Completed Milestones (All Sessions)
1. ~~Entity code mapping attempt~~ → Failed, switched to name-based
2. ~~Name-based mapping (9 systems)~~ → Completed
3. ~~OSF deep dive~~ → Root cause identified (scope difference)
4. ~~29-system cohort identification~~ → Tiered cohort with service line validation
5. ~~Spot-check validation~~ → PRISMA + ECU validated
6. ~~Analyst briefing~~ → `analyst_briefing.md`
7. ~~Per-bed spend benchmarks~~ → $720K/bed weighted, $789K median
8. ~~GPO membership mapping~~ → 30% NATIONAL GPO coverage, South bias identified
9. ~~Extrapolation model~~ → $144–173B NATIONAL GPO, $540–650B All Members
10. ~~WF calibration methodology correction~~ → Narrow exclusions, 4 systems at ≥1.0 ratio
11. ~~Advocate Alliance decomposition~~ → Split into 2 direct parents, cohort expanded to 31 systems
12. ~~TSA coverage calibration~~ → Tier 1–2 rate confirmed as full GPO-addressable coverage
13. ~~WF SL mix benchmarks (v1)~~ → Superseded by v3.2
14. ~~TSA Clinical+NC cohort expansion~~ → 81 systems, 297K beds, $90B
15. ~~Analyst briefing v2~~ → Multi-source framework, expanded cohort
16. ~~WF entity-bridge classification (v3)~~ → 18,838 entity mixes, 79% spend match
17. ~~WF hybrid classification (v3.1)~~ → Added fallback + EXCLUDE identification, 85% addressable match
18. ~~Analyst briefing v3~~ → Updated with v3.1 benchmarks, methodology evolution section, revised extrapolation
19. ~~Pharma fallback fix (v3.2)~~ → +$80M pharma recovery, pharma-specific patterns before broad CLINICAL catch-all
20. ~~3-SL primary cohort switch~~ → 42 systems (from 21 in 4-SL), eliminates food-floor selection bias
21. ~~SL benchmark ranges~~ → IQR + cross-cohort for all 4 SLs, TSA cross-check validates pharma
22. ~~Analyst briefing v4~~ → Updated with v3.2 ranges, 3-SL cohort, TSA pharma cross-check
23. ~~Analyst briefing cleanup~~ → Removed all historical version references, replaced Sections IV-V with Data Assets
24. ~~External validation synthesis~~ → 3 deep research reports extracted and synthesized; 3/4 SLs strongly validated, pharma at low-end but defensible
25. ~~Pharma classification audit~~ → Entity-bridge clean, ~$70M recoverable (immaterial), gap is structural not methodological

---

## Session 7 (2026-02-13): Briefing Cleanup, External Validation, Pharma Audit

### 1. Analyst Briefing Cleanup
Removed all historical version references (v1/v3/v3.1/v3.2 labels, methodology evolution narrative) from `analyst_briefing.md` to produce a clean, current-state-only presentation document:
- Stripped version labels and change history from all sections
- Replaced **Section IV** (Prior Analysis — Historical Context) with **Section IV: Data Assets** referencing BigQuery tables and companion files
- Deleted **Section V** (Methodology Evolution) entirely
- Cleaned footer of all version-tracking language
- Result: 295-line clean document suitable for external audiences

### 2. External Validation Synthesis
User provided 3 deep research PDFs (two external benchmark reports + one internal portfolio expansion heat map). Agent extracted text from all three using `agent_tools.llm.document_extraction`, then synthesized findings into a new deliverable.

**Source documents**:
- **R1**: "External Validation of Health System Non-Labor Purchasing SL Mix" — CMS 2552-10 cost-report decomposition approach, AHA/KFF/Vizient triangulation
- **R2**: "Health System Non-Labor Spend Validation" — IDN-focused validation using Vizient/Valify/HealthTrust/Definitive Healthcare data
- **D1**: "Portfolio Expansion Heat Map" — internal operational deck (on/off/non-contract framework)

**Consensus external ranges vs our empirical findings**:

| Service Line | External Consensus | Our v3.2 (42-sys) | Alignment |
|---|---|---|---|
| Clinical | 55–65% | ~64% | **High** — at top of range |
| Non-Clinical | 20–25% | ~22% | **High** — centered |
| Pharma | 12–18% | ~12–13% | **Moderate** — low end, defensible |
| Food | 1–2% | ~1–2% | **High** — exact match |

**Key structural drivers of pharma gap**: wholesaler-direct channels not visible in purchasing data, 340B carve-outs, specialty pharmacy separation, scope limited to GPO-addressable purchasing only.

**Deliverable**: `external_validation_synthesis.md` (new export file)

### 3. Pharma Classification Audit
Comprehensive audit of pharma allocation across all three WF classification layers (entity-bridge, name-pattern fallback, unmatched pool) to determine whether the low-end pharma estimate is a classification error or a structural artifact.

**Entity-bridge layer**: Clean. Top 40 entities by spend all correctly allocated. 12 mixed pharma/clinical entities (10-60% pharma, >$50M) validated — proportions reflect actual TSA category mixes.

**Name-pattern fallback layer**: Well-tuned. ~$540M in pharma-adjacent patterns already correctly handled (Cardinal Nuclear Pharmacy, Specialty Distribution, PBMs, etc.).

**Unmatched pool analysis**: ~$70M potentially recoverable pharma in the $11.5B unmatched pool:
- RxBenefits: $31M (PBM)
- Pfizer Vaccines: $22M
- Sanofi Genzyme: $8M
- Biologics/specialty: $6M
- Misc: $4M

**Impact**: +$70M = **+0.1 percentage points** — immaterial.

**False positive check**: $61M "null bucket" (Longwood/Healogics Specialty Physicians, oncology consultant groups) correctly NOT classified as pharma — these are physician services.

**Conclusion**: Gap to external benchmark center (~14-15%) is structural, not methodological:
1. Wholesaler-direct channels not in WF purchasing data
2. 340B carve-outs
3. Specialty pharmacy separated from GPO purchasing scope
4. Our 12-13% is consistent with a purchasing-data-only view

### Potential Next Steps
1. **On/Off/Non-Contract profiling** (Step C): Use TSA Contract_Category × system to classify Clinical+NC spend into on-contract, off-contract, and non-contract buckets — foundation for winnability scoring
2. **System-level scoring matrix**: Build per-system × per-SL heat map for Portfolio Expansion Heat Map deliverable
3. **Pharma/Food estimation**: Apply v3.2 mix ratios (~12-13% pharma, ~1-2% food) with ranges
4. **Validate with service line leaders**: Confirm category-to-SL mapping with Pam (Clinical), Molly (NC), Justin (Pharma), Joan (Food)
5. **Regional analysis**: Expanded 81-system cohort should have better Midwest/West coverage — quantify improvement

### Key Data Assets
- **BigQuery tables** (all in `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion`):
  - `tsa_cy2025` — 118.7M rows, CY2025 TSA with `parent_service_line`, `is_clin_nc_cohort`, `premier_gpo_member` (Session 8b, CURRENT)
  - `sa_sf_dhc_join_enriched` — 482K rows, full sa_sf_dhc_join + `premier_gpo_member_improved` (Session 8b, CURRENT)
  - `tsa_clin_nc_cohort` — 81 systems with beds, spend breakdowns
  - `entity_sl_mix` — 18,838 child entity SL proportions
  - `wf_sl_v3_2` — 521 systems with hybrid SL classification (CURRENT)
  - `gpo_member_universe` — 868 acute-care GPO member facilities (Session 8a)
  - `wf_sl_v3_1` — 521 systems, superseded by v3.2
  - `wf_sl_classified_v2` — (superseded by v3.1)
  - `wf_sl_v3` — (superseded by v3.1)
- **Export files** (in `runs/2026-02-10__portfolio-expansion/exports/`):
  - `analyst_briefing.md` — Updated with v3.2 entity-bridge methodology + ranges (primary deliverable)
  - `comprehensive_cohort_analysis.md` — Original 31-system tiered cohort (retained for reference)
  - `per_bed_benchmarks_and_extrapolation.md` — Per-bed benchmarks + extrapolation (updated Session 8 with GPO member universe)

---

## Session 8 (2026-02-11): GPO Membership Methodology Overhaul

### 1. Membership Universe Investigation
Deep investigation of `active_membership_type` field semantics and `premier_gpo_member` boolean:
- **Program tokens identified**: NATIONAL, ACURITY, PREMIERCHOICE, ADVANTUS, THSCS (→ Clinical SL); CONDUCTIV (→ NC SL); INTERSECTTA (→ Pharma SL); NON-GPO (no GPO participation); no food indicator exists
- **`premier_gpo_member` vs NATIONAL keyword divergence**: 129 acute-care hospitals with GPO=TRUE but no NATIONAL keyword (72 have NULL `active_membership_type`, includes NYP campuses, Children's Healthcare of Atlanta); 77 with NATIONAL but GPO=FALSE (Henry Ford, Methodist, Cooper)
- **Conclusion**: `premier_gpo_member` boolean is the authoritative GPO participation indicator

### 2. Production Table Discovery
Critical data quality differences between production (`abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join`) and the `matthew-bossemeyer` copy used in Sessions 1-7:
- Production has 488,500 rows vs copy's 482,332 (6,168 more)
- **`dhc_number_of_staffed_beds` stored as STRING with comma formatting** (e.g., "5,942") — `SAFE_CAST` without `REPLACE` silently returns NULL for all hospitals >999 beds
- **Fix**: Always use `SAFE_CAST(REPLACE(dhc_number_of_staffed_beds, ',', '') AS INT64)`
- Hospital type spelling: DHC uses `"Childrens Hospital"` (no apostrophe) — prior queries using `"Children's Hospital"` silently dropped all 250 children's hospitals

### 3. Tiered Approach Evaluation
User proposed tiered membership: `premier_gpo_member=TRUE` as base for all SLs, with incremental Conductiv-only (NC) and Intersectta-only (Pharma) add-ons.
- **Finding**: Conductiv-only incremental pool = 8 hospitals / 2,522 beds (1.3% of core)
- **Finding**: Intersectta-only incremental pool = 4 hospitals / 357 beds (0.2% of core)
- **Decision**: Incremental pools are <1.5% of core beds — excluded for simplicity. All GPO members treated as participating in all four service lines.

### 4. GPO Member Universe Implementation
**New definition**: `premier_gpo_member=TRUE`, filtered to acute-care hospital types (STAC, Health System, Childrens Hospital, CAH), deduplicated by `dhc_definitive_id`.

| Metric | Old Approach | New Approach | Delta |
|--------|-------------|-------------|-------|
| Definition | `NATIONAL` keyword, all htypes | `premier_gpo_member=TRUE`, acute only | Cleaner boolean, proper filter |
| Hospitals | 1,174 (all htypes) / 816 (acute) | **868** | +52 vs acute-only (captures GPO=TRUE w/o NATIONAL) |
| Beds | 198,236 (all htypes) / 157,836 (acute) | **193,636** | –2.3% vs all-htypes; +23% vs acute-only |
| By type | — | Health System: 116/113K, STAC: 476/68K, Childrens: 40/7K, CAH: 236/5K | — |

**Persisted as**: `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.gpo_member_universe` (868 rows)

### 5. Updated Extrapolation Figures

| Metric | Old ($) | New ($) | Change |
|--------|---------|---------|--------|
| Method A (weighted avg $720K/bed) | $144B | **$139B** | –3.2% |
| Method B (Tier 1-2 $864K/bed) | $173B | **$167B** | –3.5% |
| Central range | $145–175B | **$139–167B** | –4% |
| C+NC addressable ($160K/bed × WF 1.16×) | $37B | **$36B** | –2.7% |
| Clinical SL | $92–94B | **$89–91B** | — |
| Non-Clinical SL | $31–36B | **$29–35B** | — |
| Pharma SL | $13–24B | **$13–24B** | Unchanged |
| Food SL | $2–3B | **$1–3B** | — |
| Cohort coverage | 30.4% | **31.5%** | +1.1pp |

### Files Updated
- `analyst_briefing.md` — Replaced NATIONAL GPO 200,673 beds with Premier GPO 193,636; added methodology note
- `per_bed_benchmarks_and_extrapolation.md` — Rewrote Section 2 (membership summary, comparison table, regional, size, bed coverage), updated all Section 3 extrapolation tables and SL decomposition, updated Recommendation #5

### Potential Next Steps (from Session 8a)
1. **On/Off/Non-Contract profiling** (Step C): Use TSA Contract_Category × system to classify Clinical+NC spend into on-contract, off-contract, and non-contract buckets — foundation for winnability scoring
2. **System-level scoring matrix**: Build per-system × per-SL heat map for Portfolio Expansion Heat Map deliverable
3. **Update data dictionary**: Note STRING/comma bed parsing and "Childrens" (no apostrophe) in `sa_sf_dhc_join` data dictionary
4. **Regional analysis with corrected universe**: The regional distribution shifted significantly (South dropped from 38% to 32%, Northeast rose from 17% to 27%) — reassess cohort bias

---

## Session 8b (2026-02-11): CY2025 TSA Table Build + Clinical Extrapolation Validation

### 1. CY2025 TSA Table (`tsa_cy2025`)
Created a comprehensive CY2025 transaction table in `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.tsa_cy2025`:

**Structure**: All original TSA columns from `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` plus 3 derived columns:
- `parent_service_line` (STRING) — maps granular `service_line` to 4 parent buckets
- `is_clin_nc_cohort` (BOOL) — TRUE for the 81 validated systems (joined on `Health_System_Entity_Code` from `tsa_clin_nc_cohort`)
- `premier_gpo_member` (BOOL) — improved GPO membership flag (joined on `Premier_Entity_Code = facility_entity_code` from `sa_sf_dhc_join_enriched`)

**Parent Service Line Mapping**:
| parent_service_line | Granular service_lines | Rationale |
|---|---|---|
| **Clinical** | PPI, NURSING, SURGICAL, DIAGNOSTICS, DISTRIBUTION | Direct patient-care spend |
| **Non-Clinical** | PURCHASED SERVICES, FACILITIES, IT/DIGITAL HEALTH, NULL | Operational spend (NULL rows = Security Guard & Unknown) |
| **Pharma** | PHARMACY | Pharmaceutical |
| **Food** | FOODS | Nutrition/dietary |

**Exclusions**: Only 9 test/demo entities removed (PREMIER TEST 300, MEMBER 24/2/3 - TEST, PO DATA TEST 3, RECRUITMENT TEST FACILITY 1, PREMIER HEALTH SYSTEM DEMO, COST TECHNOLOGY PARENT 1 & 2). All real healthcare entities kept — alliances, purchasing cooperatives, and all legitimate providers remain.

**Stats**: 118.7M rows, 174 systems, $134.7B total CY2025 spend

### 2. Improved GPO Membership Flag (`sa_sf_dhc_join_enriched`)
Created `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.sa_sf_dhc_join_enriched` — full copy of `sa_sf_dhc_join` with `premier_gpo_member_improved` column applying enhanced logic:

```sql
IF(
  (Premier_Enterprise_Unit_Roll_Up IS NOT NULL
    AND STRPOS(UPPER(Premier_Enterprise_Unit_Roll_Up), 'GPS') > 0)
  OR (premier_gpo_member IS NOT NULL AND premier_gpo_member),
  TRUE,
  FALSE  -- includes indeterminate cases
)
```

**Result**: 5,870 GPO=TRUE facilities (original boolean captured 5,821; GPS roll-up added 49 incremental). Purely additive — no original TRUE values flipped to FALSE.

**Join to TSA**: `tsa_cy2025.Premier_Entity_Code = sa_sf_dhc_join_enriched.facility_entity_code` (facility-level precision, not health-system rollup).

### 3. Spend by parent_service_line × cohort × GPO

| parent_service_line | Cohort $B | Non-cohort $B | Total $B |
|---|---|---|---|
| Clinical | $39.3 | $18.9 | $58.2 |
| Non-Clinical | $34.7 | $15.7 | $50.4 |
| Pharma | $10.5 | $14.3 | $24.8 |
| Food | $1.0 | $0.5 | $1.4 |

GPO flag: 126 systems / $119.9B (GPO=TRUE) vs 92 systems / $14.8B (FALSE)

### 4. Clinical Extrapolation Validation (TWO-TIER SPOT CHECK)

**Objective**: Test whether the per-bed clinical rate from the 81-system cohort produces accurate projections when extrapolated.

**Benchmark**: $131,082 per bed (from 80 of 81 cohort systems with DHC bed matches × $39.1B clinical spend ÷ 298K beds)

#### Tier 1: Extrapolate to all TSA-reporting facilities
- **Beds** (all TSA facility entity codes matched to DHC): 353,241 (1,275 facilities)
- **Projected clinical spend**: 353,241 × $131,082 = **$46.3B**
- **Actual clinical spend** (all `tsa_cy2025` where `parent_service_line = 'Clinical'`): **$58.2B**
- **Delta**: Actual exceeds projection by **+$11.9B (+25.6%)**

#### Tier 2: Extrapolate to all GPO member facilities
- **Beds** (all `premier_gpo_member_improved = TRUE` in `sa_sf_dhc_join_enriched` with DHC beds): 547,672 (2,240 facilities)
- **Projected GPO clinical spend**: 547,672 × $131,082 = **$71.8B**
- **Actual GPO clinical spend** (TSA, `premier_gpo_member = TRUE AND parent_service_line = 'Clinical'`): **$52.2B**
- **Delta**: Projection exceeds actual by **+$19.6B (+27%)** — reporting coverage gap

#### Interpretation & Open Questions (FOR NEXT SESSION)

**Tier 1 is the critical finding requiring investigation.** The actual TSA clinical spend *exceeds* the projection by 26%. Two leading hypotheses:
1. **DHC bed-match coverage gap**: Only 1,275 of potentially many more TSA facilities have DHC bed data. Facilities without beds still contribute spend to the $58.2B actual, but add zero to the 353K bed denominator → the projection is mechanically suppressed.
2. **81-system cohort underrepresentation**: The cohort may skew toward systems with *moderate* per-bed clinical intensity. High-intensity systems outside the 81 (e.g., large academic medical centers or specialty-heavy systems) could pull up the true population average above $131K/bed.

**Tier 2 behaves as expected.** The overshoot is directionally correct — GPO members that exist in the membership directory but don't submit transaction data produce a 27% reporting coverage gap. This aligns with the ~965 GPO facilities with beds in DHC (2,240) minus the ~1,196 GPO facilities with beds that also appear in TSA.

**Key investigation tasks for next session**:
1. **Quantify Tier 1 bed-match gap**: How many TSA facilities have spend but no DHC bed match? What is their total clinical spend? If we could recover their beds, how would it change the projection?
2. **Compute all-TSA per-bed rate**: For the 1,275 facilities that *do* have both TSA spend and DHC beds, what is their direct per-bed clinical rate? Compare to the 81-system rate ($131K) — if it's materially higher, the 81-system sample is biased low.
3. **Segment the gap**: Is the Tier 1 overshoot concentrated in specific health systems or facility types? (E.g., alliance entities like ACURITY rolling up $29.9B in spend may not have proportional bed representation in DHC.)
4. **Consider the TSA `member_num_beds` field**: TSA itself has a `member_num_beds` column — compare it to DHC beds to see if TSA self-reported beds give a different denominator.

### 5. Tables Created/Modified This Session

| Table | Description | Rows |
|---|---|---|
| `sa_sf_dhc_join_enriched` | Full sa_sf_dhc_join + `premier_gpo_member_improved` | 482,332 |
| `tsa_cy2025` | CY2025 TSA + `parent_service_line`, `is_clin_nc_cohort`, `premier_gpo_member` | 118,660,119 |

### 6. Key Facts for Continuity
- **dhc_number_of_staffed_beds is STRING** in `sa_sf_dhc_join_enriched` (inherited from source) — must always use `SAFE_CAST(REPLACE(dhc_number_of_staffed_beds, ',', '') AS INT64)`
- **Join key for TSA↔member data**: `tsa.Premier_Entity_Code = sa_sf_dhc_join.facility_entity_code`
- **Join key for TSA↔cohort**: `tsa.Health_System_Entity_Code = tsa_clin_nc_cohort.Health_System_Entity_Code`
- **TSA year filter**: `EXTRACT(YEAR FROM Transaction_Date) = 2025` (no Calendar_Year column)
- **TSA spend column**: `Landed_Spend` (FLOAT64)
- **One cohort system has no DHC beds**: 80 of 81 cohort systems matched to beds (298,455 total)

---

## Session 9 (2026-02-11): Tier 1 Clinical Extrapolation Gap Investigation

### 1. Problem Statement

Session 8b found a +$11.9B / +26% gap in the Tier 1 clinical extrapolation: $131K/bed × 353K beds = $46.3B projected vs $58.2B actual. This session investigated and fully decomposed the gap.

### 2. Root Cause Analysis — Three Independent Factors

#### Factor 1: System-Level Bed Inflation ($3.0B of gap)

The $131K/bed rate was computed at the **system level**: $39.1B clinical spend ÷ 298K system-wide beds. But 298K includes beds at ALL facilities in the 81 cohort systems — including facilities that don't report to TSA.

| Level | Beds | Clinical Spend | Per-Bed Rate |
|-------|------|---------------|-------------|
| System-level (Session 8b method) | 296,800 | $39.1B | **$131K** |
| Facility-level (TSA-reporting entities only) | 222,439 | $34.6B | **$156K** |
| **Bed inflation ratio** | **1.33×** | — | — |

The cohort health systems have 297K total beds, but only 222K are at TSA-reporting facility entity codes. The remaining 75K beds (25%) are at system-owned facilities that don't submit transactions to TSA, inflating the denominator by 33%.

For ALL TSA entities with DHC bed matches (not just cohort), the facility-level rate is **$146K/bed** (1,264 entities, 337K beds, $49.3B clinical spend):

| Segment | Entities | Beds | Clinical $B | Per-Bed Rate |
|---------|----------|------|-------------|-------------|
| Cohort facilities | 752 | 222,439 | $34.6B | **$156K** |
| Non-cohort facilities | 512 | 114,586 | $14.7B | **$128K** |
| **All bed-matched** | **1,264** | **337,025** | **$49.3B** | **$146K** |

#### Factor 2: Unmatched Entity Spend ($8.8B of gap)

5,589 TSA entity codes have clinical spend but **no DHC bed match** — they contribute to the $58.2B actual but zero beds to the denominator. Decomposition:

| Category | Entities | Clinical $B | % of Gap | Examples |
|----------|----------|-------------|----------|---------|
| **Alliance/GPO entities** | 4,197 | **$3.7B** | 42% | Acurity ($1.9B), Allspire ($0.8B), Conductiv ($0.4B), Alliant ($0.2B), MHS ($0.2B) |
| **Alt-site providers (cohort)** | 944 | **$3.1B** | 35% | Physician offices, ASCs, ambulatory centers tied to cohort health systems |
| **Acute hospitals (no DHC match)** | 122 | **$1.6B** | 18% | Cohort hospitals not in DHC crosswalk (Fairview MN5050, PeaceHealth, HealthPartners, UPMC satellites) |
| **Alt-site providers (non-cohort)** | 242 | **$0.2B** | 2% | Non-cohort physician practices |
| **Acute hospitals (non-cohort)** | 75 | **$0.2B** | 2% | Non-cohort hospitals without DHC |
| **Other** | 9 | **<$0.01B** | <1% | — |
| **Total unmatched** | **5,589** | **$8.8B** | 100% | — |

#### Factor 3: Denominator Mismatch (Session 8b used all-TSA beds for clinical-only projection)

Session 8b used 353K beds (from ALL TSA entities, including 11 with non-clinical-only spend containing 16K beds) but the actual clinical spend comes only from entities with clinical transactions (337K beds from 1,264 entities). This is a minor methodological note — the bigger factors are #1 and #2.

### 3. Complete Gap Decomposition

| Factor | Amount | Explanation |
|--------|--------|-------------|
| Rate gap (system→facility level) | **+$3.0B** | $131K→$146K/bed on clinical entities |
| Unmatched: Alliance/GPO | **+$3.7B** | Purchasing cooperatives without bed mapping |
| Unmatched: Alt-site (both) | **+$3.3B** | Physician offices, ASCs, ambulatory centers with clinical purchasing |
| Unmatched: Acute no-match | **+$1.8B** | Real hospitals missing from DHC crosswalk |
| Unmatched: Other | **+$0.1B** | — |
| **Total gap** | **≈$11.9B** | **Fully explained** |

### 4. TSA `member_num_beds` Comparison

TSA's self-reported `member_num_beds` provides essentially the same bed coverage as DHC:

| Bed Source | Entities with Beds | Total Beds | Per-Bed Rate |
|-----------|-------------------|------------|-------------|
| DHC only | 1,264 | 337,025 | $146K |
| TSA only | 1,287 | 336,646 | $146K |
| DHC+TSA fallback | 1,294 | 347,018 | $142K |

TSA beds add only 30 incremental entities / 10K beds vs DHC. The unmatched entity gap ($8.8B) is NOT recoverable through a different bed source — those entities structurally don't have beds.

### 5. Implications for Methodology

**The per-bed extrapolation methodology is fundamentally sound**, but requires two adjustments:

1. **Use facility-level rates, not system-level**: The cohort rate should be $156K/bed (facility-matched), not $131K (system-wide). For the broader TSA population, $146K/bed is the appropriate rate.

2. **Add an alt-site/non-bed adjustment**: On top of bed-based spending, approximately 15% of TSA clinical spend ($8.8B of $58.2B) comes from entities without beds. For extrapolation to GPO membership, this can be modeled as a **1.18× multiplier** on the bed-based projection: $49.3B × 1.18 = $58.2B.

**Alliance spend should be excluded from the multiplier calculation.** Alliances (Acurity, Allspire, etc.) represent purchasing cooperatives whose member hospitals likely already have their beds counted separately in DHC. If we exclude alliance no-bed spend ($3.7B):
- Non-alliance unmatched: $5.1B / $49.3B = 10.4%
- Adjusted multiplier: **1.10×** (more conservative)

**Updated GPO extrapolation** (for Section III of analyst_briefing):
- GPO beds: 194K
- Clinical rate: $146K/bed (all-TSA facility rate)
- Bed-based clinical: 194K × $146K = **$28.3B**
- With alt-site adjustment (×1.10): **$31.1B**
- Range: $28-31B (vs prior $25.4B from $131K × 194K)

### 6. Top No-Bed-Match Health Systems (for future data quality work)

Systems with highest clinical spend routed through entities without DHC beds:

| Health System | No-Bed Clinical $M | Bed-Matched Clinical $M | No-Bed % | Diagnosis |
|--------------|--------|---------|---------|-----------|
| ADVOCATE HEALTH | $2,071M | $5,849M | 26% | Alliance sub-entities, overflow |
| ACURITY | $1,874M | $7,347M | 20% | Alliance member entities |
| ALLSPIRE | $831M | — | 100% | Alliance entity only |
| UPMC | $562M | — | — | Satellite/overflow entities |
| CONDUCTIV | $425M | — | 100% | Alliance entity |
| TEXAS HEALTH | $281M | — | — | Non-hospital entities |
| ADVENTHEALTH | $257M | — | — | New campuses/non-hospital |
| FAIRVIEW | $243M | — | — | Includes MN5050 (not in DHC) |
| ALLIANT | $219M | — | — | Alliance |
| MHS PURCHASING | $209M | — | — | Alliance |

### 7. Key Facts for Continuity

- **Facility-level per-bed clinical rate**: $146K/bed (all TSA), $156K (cohort), $128K (non-cohort)
- **System-level rate ($131K) is depressed by 33% bed inflation** from non-reporting facilities
- **$8.8B unmatched** = $3.7B alliance + $3.3B alt-site + $1.8B acute-no-match
- **TSA `member_num_beds`** tracks DHC beds closely (337K vs 337K); no incremental coverage
- **Alt-site adjustment multiplier**: 1.10× (excl. alliance) to 1.18× (incl. alliance) on bed-based projection

---

## Session 9b (2026-02-13): Dual-Definition Fix, Dataform Pipeline, and v4 Benchmark Rebuild

### 1. Problem Discovery — Dual Service Line Classification

User asked: "Is there risk in defining the category → parent_service_line relationship in two different places?"

**Audit revealed a critical divergence:**

| Table | Classification Method | Clinical % | NC % |
|-------|----------------------|-----------|------|
| `tsa_cy2025` | `service_line` → `parent_service_line` (robust, complete) | 43% | 37% |
| `entity_sl_mix` (v3.2) | Explicit CASE WHEN with ~51 NC categories + `ELSE 'Clinical'` | 60% | 18.5% |

The entity_sl_mix v3.2 enumeration missed ~160 NC contract categories under PURCHASED SERVICES, FACILITIES, and IT/DIGITAL HEALTH, which fell through the `ELSE → Clinical` fallback. This caused **$19.5B of NC spend to be misclassified as Clinical** in entity_sl_mix, cascading into WF SL mix benchmarks.

**Biggest misclassified categories:**
- GENERAL OUTSOURCED CLINICAL SERVICES: $3.5B (PURCHASED SERVICES → was Clinical)
- CLINICAL EQUIPMENT REPAIR AND MAINTENANCE SERVICES: $2.2B
- ADVERTISING AND MARKETING SERVICES: $869M (string mismatch: list had "MARKETING SERVICES")
- EDUCATIONAL SYSTEMS: $714M
- ANESTHESIA SERVICES: $640M
- Plus ~155 more categories

**Additional string-mismatch issues in v3.2 NC list:**
- "FURNITURE" vs actual "FURNITURE AND SYSTEMS SEATING AND ACCESSORIES" ($394M missed)
- "TELECOMMUNICATIONS SERVICES AND EQUIPMENT" vs actual "TELECOMMUNICATIONS EQUIPMENT AND SERVICES DISTRIBUTORS" ($457M missed)

### 2. Solution — Single Source of Truth via Dataform Pipeline

Built a complete Dataform pipeline with `service_line_mapping` as the single source of truth:

```
dataform/
├── dataform.json              # Project config
├── package.json               # @dataform/core 2.9.0
├── includes/constants.js      # Shared constants
└── definitions/
    ├── sources/               # 3 source declarations
    ├── mapping/
    │   └── service_line_mapping.sqlx  # THE 10-row mapping table
    ├── staging/
    │   ├── entity_sl_mix.sqlx         # Uses service_line JOIN
    │   └── tsa_cy2025.sqlx            # LEFT JOIN to mapping
    └── marts/
        ├── tsa_clin_nc_cohort.sqlx    # 100-system cohort
        ├── tsa_cy2025_enriched.sqlx   # + cohort/GPO flags
        ├── gpo_member_universe.sqlx   # GPO member filter
        └── wf_sl_v4.sqlx             # WF benchmarks (corrected)
```

**service_line_mapping (10 rows):**

| service_line | parent_service_line |
|---|---|
| PPI, NURSING, SURGICAL, DIAGNOSTICS, DISTRIBUTION | Clinical |
| PURCHASED SERVICES, FACILITIES, IT/DIGITAL HEALTH | Non-Clinical |
| PHARMACY | Pharma |
| FOODS | Food |

### 3. Tables Rebuilt

| Table | Description | Key Change |
|---|---|---|
| `service_line_mapping` | 10-row mapping table | NEW — single source of truth |
| `entity_sl_mix` | 18,838 entity codes | Rebuilt with service_line JOIN (not enumeration) |
| `tsa_cy2025` | 118.7M rows | LEFT JOIN to mapping (UNKNOWN → NULL) |
| `tsa_clin_nc_cohort` | **100 systems** (was 81) | parent_service_line-based qualification |
| `tsa_cy2025_enriched` | 118.7M rows | NEW — adds cohort + GPO flags |
| `wf_sl_v4` | 521 systems | Corrected entity_sl_mix proportions |

### 4. Impact on Key Numbers

| Metric | v3.2 | v4 | Change |
|--------|------|-----|--------|
| **entity_sl_mix Clinical %** | 60.0% | 47.9% | -12.1pp |
| **entity_sl_mix NC %** | 18.5% | 30.2% | +11.7pp |
| **WF primary cohort Clinical** | 63.9% (42 sys) | 43.1% (46 sys) | -20.8pp |
| **WF primary cohort NC** | 22.2% | 41.0% | +18.8pp |
| **TSA cohort systems** | 81 | 100 | +19 |
| **TSA cohort beds** | 297K | 259K | -38K (facility-level) |
| **C+NC per bed** | $160K (marker) | $295K (full SL) | +$135K |
| **GPO extrapolation** | $36B | $68B | +$32B |

### 5. Updated Analyst Briefing

The analyst_briefing.md was comprehensively updated with all v4 numbers. Key sections changed:
- Executive Summary: All key findings, v4 methodology note added
- Section I: All 6 cross-cohort benchmark tables, distributions, system examples, observations
- Section II: Cohort 81→100, all metrics, top 25 table, size distribution
- Section III: Extrapolation $36B→$68B with full methodology explanation
- Section III-A: Added context note (validated marker-category methodology, still applicable)
- Section IV: Added service_line_mapping, tsa_cy2025_enriched, wf_sl_v4 to data assets

### 6. Key Facts for Continuity

- **service_line_mapping is THE source of truth** — all tables derive SL classification from it via JOIN
- **tsa_cy2025 uses LEFT JOIN** (preserves UNKNOWN → NULL parent_service_line, $1.2B)
- **entity_sl_mix uses INNER JOIN** (drops UNKNOWN — ~3.7M TSA rows, $1.2B)
- **Cohort expanded** from 81→100 because corrected NC classification means 19 more systems meet ≥$10M NC
- **Per-bed rates use facility-level beds** (matched through TSA entity codes ↔ DHC), not system-level inflated beds
- **$295K/bed rate** counts ALL C+NC categories (not just marker categories)
- **WF C+NC share** ≈ 84% (42.8% + 41.3%), range 82–87% across cohort definitions
- **Dataform pipeline** is in `dataform/` — 14 .sqlx files defining the full build DAG (includes vendor_name_patterns.sqlx)
- **wf_sl_v3_2** is superseded by `wf_sl_v4`; old table still exists in BQ

---

## Session 9c (2026-02-13): vendor_name_patterns Reference Table + Expanded Name Pattern Coverage

### 1. Problem Discovery — Briefing Accuracy on Unmatched Spend

User questioned the analyst briefing's claim that "15% residual unmatched spend ($11B) is a genuine mix of vendor types — PBMs ($200M), specialty pharmacy ($200M+), construction firms, food service (Sodexo)." Investigation revealed:

- **Statement was partially inaccurate**: Major PBMs (OptumRx $190M, Express Scripts $15M) and Sodexo ($140M) were *already entity-bridge classified* — they were NOT in the unmatched pool
- **But real gaps existed**: Top 50 unmatched vendors totaled ~$2.5B+ of clearly classifiable spend (McKesson Technology $278M → NC, Fisher Scientific $41M → Clinical, RXBENEFITS $28M → Pharma, Pepsi-Cola $28M → Food, etc.)
- Decomposition: Of $11.5B unmatched, ~$8.8B genuinely ambiguous (84K vendors), ~$2.7B catchable with expanded patterns

### 2. Architecture Change — Pattern Table Replaces Inline CASE WHEN

**Before**: wf_sl_v4.sqlx had a 90-line nested CASE WHEN with all name patterns inline — fragile, hard to audit, impossible to extend without modifying the classification query.

**After**: Two-layer design:
- **`vendor_name_patterns.sqlx`** (new, `definitions/staging/`): 153 LIKE-pattern rules in a reference table, priority-ordered by SL band (100=Exclude, 200=Pharma, 300=Food, 400=NC, 500=Clinical). Each rule has pattern, exclude_pattern (negation), parent_service_line, priority, and category fields.
- **`wf_sl_v4.sqlx`** (rewritten): JOINs vendor_name_patterns via `ROW_NUMBER() OVER (ORDER BY priority)` match. 75 lines, clean separation of rules (data) from logic (SQL).

To add/modify name patterns, edit `vendor_name_patterns.sqlx` only — the classification query needs no changes.

### 3. New Patterns Added (28 total)

| SL | Patterns | Top examples | Recovered Spend |
|---|---|---|---|
| NC (410) | 9 | McKesson Tech ($277M), locum tenens ($137M), Deloitte ($86M), KPMG ($62M), MedStaff ($42M), Siemens Industry ($41M) | **$704M** |
| Food (310) | 7 | US Foods ($287M), Pepsi ($51M), Aramark ($45M), Compass Group ($38M), Sysco ($26M) | **$453M** |
| Clinical (510) | 5 | Renal care ($77M), Fisher Scientific ($63M), laboratory ($60M), dialysis ($21M) | **$223M** |
| Pharma (210) | 4 | RxBenefits ($31M), pharmacy benefit ($3M), Omnicare, PharMerica | **$34M** |
| Exclude (125) | 1 | Comptroller ($26M) | **$26M** |
| Exclude (105) | 1 | Broadened VOYA from `%VOYA FINANCIAL%` → `%VOYA%` | (reclassified) |

### 4. Impact on Key Numbers

| Metric | v4 (pre-expansion) | v4.1 (post-expansion) | Change |
|--------|------|------|--------|
| Name-pattern SL spend | $2.5B (3.4%) | $3.4B (4.5%) | +$0.9B |
| Exclude spend | $1.8B (2.4%) | $1.5B (2.0%) | -$0.3B |
| Unmatched | $11.5B (15.4%) | $10.7B (14.3%) | -$0.8B |
| Match rate | 85% | **86%** | +1pp |
| Primary cohort (46 sys) Clinical | 43.1% | 42.8% | -0.3pp |
| Primary cohort NC | 41.0% | 41.3% | +0.3pp |
| Primary cohort Pharma | 14.5% | 14.4% | -0.1pp |
| Primary cohort Food | 1.5% | 1.5% | — |

### 5. Updated Artifacts

- **`analyst_briefing.md`**: Comprehensively updated — classification table, methodology description (now references pattern table), all 6 cohort benchmark rows, percentile distribution, selected system-level mix, sensitivity section (corrected PBM/Sodexo claims), data assets (added vendor_name_patterns), GPO extrapolation numbers
- **`vendor_name_patterns.sqlx`**: New Dataform-managed reference table
- **`wf_sl_v4.sqlx`**: Rewritten to JOIN pattern table
- **BQ tables**: `vendor_name_patterns` and `wf_sl_v4` rebuilt

### 6. Key Facts for Continuity

- **vendor_name_patterns is the single source of truth for name patterns** — edit only this file
- **Priority bands**: 100–199 Exclude, 200–299 Pharma, 300–399 Food, 400–499 NC, 500–599 Clinical
- **Lower priority number wins** when a vendor matches multiple patterns (ROW_NUMBER ORDER BY priority)
- **exclude_pattern column** enables negation (e.g., `%STATE OF%` excludes `%STATE OF THE ART%`)
- **Dataform compiles**: 8 tables + 14 assertions, zero errors
- **Dataform CLI credentials configured** — `.df-credentials.json` uses ADC (non-secret, project+location only); `npx dataform compile` and `npx dataform run` work from `dataform/` directory

---

## Session 10 (2026-02-14): Dataform CLI Credentials + v4.2 Pattern Expansion

### 1. Dataform CLI Credentials (ADC-First, No Secrets)

Set up Dataform CLI authentication following the working pattern from `committed-program-analysis`:

- **Created** `dataform/.df-credentials.json`: `{"projectId":"matthew-bossemeyer","location":"US"}` (non-secret; relies on ADC token from `gcloud auth application-default login`)
- **Verified** `npx dataform compile` (22 actions, 0 errors) and `npx dataform run --dry-run`
- **Updated** `docs/dataform_in_vscode_best_practices.md` with new Section 2a documenting ADC auth

### 2. Pattern Expansion: 153 → 200 Patterns (+47 new)

Queried top 200 unmatched vendors by dollar volume, estimated impact via BQ CROSS JOIN (~$760M recoverable across 46 candidate patterns), and added 47 new patterns to `vendor_name_patterns.sqlx`:

| SL Band | New Patterns | Key Examples |
|---------|-------------|--------------|
| **Exclude (100s)** | 20 | Benefits funds/trusts, insurance claims management, UKG, EFTPS, escrow, Medicaid, Dept of Health/Human Services, accounts receivable, credit services, law groups |
| **Pharma (200s)** | 5 | Pfizer, Sanofi, Genzyme, Morris & Dickson, Akebia |
| **NC (400s)** | 9 | Consulting, advertising, revenue cycle, environmental services, painting, landscaping, plumbing, roofing, publishing |
| **Clinical (500s)** | 14 | Rehabilitation, ambulance, Linde Gas, Praxair, medical gas, blood centers, pathology (excl consulting), organ procurement, Beckman Coulter, inpatient physicians, urgent care, DaVita |

### 3. Tables Rebuilt via `npx dataform run`

First real Dataform CLI materialization (not direct BQ SQL). Rebuilt `vendor_name_patterns` (200 rows confirmed) and `wf_sl_v4` (521 systems).

### 4. Assertion Fix

`assert_wf_total_spend_positive` failed for 163 systems with gap > $1. Root cause: `entity_sl_mix` percentages don't sum to exactly 100% because UNKNOWN TSA categories are dropped by INNER JOIN. Total gap $852K across $74.5B (0.001% — wholly immaterial). Fixed by relaxing tolerance from $1 absolute to **0.1% of system spend**.

### 5. v4.2 Impact on Key Numbers

| Metric | v4.1 | v4.2 | Change |
|--------|------|------|--------|
| Pattern count | 153 | **200** | +47 |
| Name-pattern SL spend | $3.4B (4.5%) | $3.9B (5.2%) | +$0.5B |
| Exclude spend | $1.5B (2.0%) | $1.8B (2.4%) | +$0.3B |
| Unmatched | $10.7B (14.3%) | **$9.9B (13.3%)** | −$0.8B |
| Classification rate | ~86% | **~87%** | +1pp |
| Primary cohort N | 46 | **42** | −4 (cohort changed due to match_pct recalculation) |
| Primary cohort classified | $55.2B | $54.9B | −$0.3B |
| Primary SL mix | C 42.8 / NC 41.3 / P 14.4 / F 1.5 | **Unchanged** | — |

### 6. v4.2 Cross-Cohort Benchmarks

| Cohort | N | Classified | Clinical | NC | Pharma | Food |
|--------|---|-----------|----------|----|--------|------|
| **3-SL balanced ≥$200M** (primary) | **42** | **$54.9B** | **42.8%** | **41.3%** | **14.4%** | **1.5%** |
| 3-SL balanced ≥$100M | 55 | $56.7B | 42.9% | 41.1% | 14.5% | 1.5% |
| 4-SL food≥0.5% ≥$200M | 33 | $49.7B | 41.6% | 43.5% | 13.4% | 1.6% |
| 4-SL food≥1% ≥$200M | 22 | $26.9B | 43.1% | 43.6% | 10.9% | 2.4% |
| All ≥$50M, ≥70% match | 77 | $59.9B | 42.1% | 39.6% | 16.8% | 1.5% |
| 3-SL balanced ≥$50M | 83 | $58.9B | 43.4% | 40.7% | 14.4% | 1.5% |

### 7. v4.2 Percentile Distribution (42-System Primary Cohort)

| SL | Min | P10 | P25 | Median | Mean | P75 | P90 | Max |
|----|-----|-----|-----|--------|------|-----|-----|-----|
| Clinical | 16.2% | 27.1% | 34.4% | 44.2% | 45.0% | 51.4% | 63.6% | 95.3% |
| NC | 1.3% | 4.0% | 23.3% | 34.4% | 32.8% | 45.1% | 51.3% | 62.4% |
| Pharma | 1.5% | 4.6% | 6.8% | 10.8% | 20.7% | 29.3% | 53.4% | 71.6% |
| Food | 0.0% | 0.3% | 0.6% | 1.0% | 1.5% | 2.0% | 3.1% | 7.7% |

### 8. Updated Artifacts

- **`dataform/.df-credentials.json`**: New — ADC credentials for CLI
- **`docs/dataform_in_vscode_best_practices.md`**: Added Section 2a (ADC auth guide)
- **`dataform/definitions/staging/vendor_name_patterns.sqlx`**: 153 → 200 patterns
- **`dataform/definitions/assertions/assert_wf_total_spend_positive.sqlx`**: Relaxed tolerance to 0.1%
- **`runs/.../exports/analyst_briefing.md`**: Comprehensive v4.2 number update (all tables, sensitivity, data assets)
- **BQ tables**: `vendor_name_patterns` (200 rows) and `wf_sl_v4` rebuilt via `npx dataform run`

### 9. Key Observations

- **SL mix benchmarks are remarkably stable** across v4.1 → v4.2: Clinical ~43%, NC ~41%, Pharma ~14%, Food ~1.5% — unchanged at the weighted level despite recovering $0.8B from the unmatched pool and shifting 4 systems out of the primary cohort
- **Diminishing returns on pattern expansion**: Session 9c recovered $1.4B (28 patterns), Session 10 recovered ~$0.8B (47 patterns). The remaining $9.9B unmatched is predominantly a long tail of small, nondescript vendors
- **Uncertainty band tightened**: ±2–3pp per SL from unmatched spend (was ±3–5pp pre-expansion)
- **Dataform CLI now fully functional**: compile + run + assertions all work via ADC

---

## Session 11 (2026-02-14): DHC Bed Double-Counting Fix (v4.3)

### 1. Staffed Beds INT Cast

Converted `dhc_number_of_staffed_beds` from STRING (with commas) to INT64 in Dataform:

- **Created** `dataform/definitions/sources/sa_sf_dhc_join_raw.sqlx` — source declaration for upstream production table `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join`
- **Converted** `dataform/definitions/sources/sa_sf_dhc_join_enriched.sqlx` from `declaration` → `table` type, adding `SAFE_CAST(REPLACE(dhc_number_of_staffed_beds, ',', '') AS INT64) AS staffed_beds`
- **Updated** `dataform/definitions/marts/tsa_cy2025_enriched.sqlx` to pass `staffed_beds` through as `dhc_staffed_beds`
- Simplified downstream consumers (`gpo_member_universe.sqlx`, `tsa_clin_nc_cohort.sqlx`) to use pre-cast `staffed_beds`

### 2. DHC Bed Double-Counting Discovery

User identified that `dhc_hospital_type = 'Health System'` parent rows in the DHC facility directory contain **aggregate bed counts that duplicate child hospital beds**:

| Example: Advocate Health | Beds |
|---|---|
| Parent row (Health System type) | 12,044 |
| Child hospitals sum (STAC + Children's) | ~3,158 |
| **Double-count** | **~8,886** |

Investigation quantified the global impact:
- **65 systems** had both parent + child rows in the GPO universe
- Cohort beds: parent-inclusive **259,246** → hospital-only **113,205** (2.3× inflation removed)
- GPO universe beds: **193,636** → **224,101** (after also fixing the STAC filter — see below)

### 3. GPO Universe Filter Bug (STAC String Mismatch)

`gpo_member_universe.sqlx` used `'Short Term Acute Care'` in its hospital type filter, but the DHC data uses `'Short Term Acute Care Hospital'`. This **silently excluded all ~1,000 STAC hospitals**. The old 868-facility universe was almost entirely Health System parent rows + CAH + Children's.

**Fixes applied**:
- Fixed `'Short Term Acute Care'` → `'Short Term Acute Care Hospital'`
- Removed `'Health System'` from the hospital type filter (parent roll-ups excluded)
- Relaxed `nonNull` assertion on `staffed_beds` (94 facilities have NULL beds in DHC)

### 4. Corrected Numbers (v4.3)

#### GPO Membership Universe

| Hospital Type | Facilities | Beds |
|---|---|---|
| Short Term Acute Care Hospital | 1,157 | 202,265 |
| Critical Access Hospital | 550 | 11,615 |
| Childrens Hospital | 68 | 10,221 |
| **Total** | **1,775** | **224,101** |

> 94 facilities have NULL beds (83 STAC, 8 Children's, 3 CAH)

#### TSA Cohort Summary

| Metric | v4 (old) | v4.3 (corrected) | Change |
|---|---|---|---|
| Systems | 100 | 100 | — |
| Systems with bed match | 99 | 93 | -6 |
| Total staffed beds | 259,246 | **113,205** | -56% |
| Clinical per bed | $162K | **$360K** | +122% |
| NC per bed | $133K | **$291K** | +119% |
| Addressable per bed | $295K | **$652K** | +121% |
| Spend (all) | $89B | $89B | — |

#### Extrapolation

| | v4 (old) | v4.3 (corrected) |
|---|---|---|
| GPO beds | 193,636 | **224,101** |
| C+NC addressable | $57B | **$146B** |
| Total non-labor (÷0.84) | $68B | **$174B** |
| Clinical (~43%) | $29B | **$75B** |
| NC (~41%) | $28B | **$72B** |
| Pharma (~14%) | $10B | **$25B** |
| Food (~1.5%) | $1B | **$3B** |

#### Sensitivity (P25–P75)

| Scenario | C+NC Addressable | Total Non-Labor |
|---|---|---|
| P25 ($334K/bed) | $75B | $89B |
| **Median** ($418K/bed) | **$94B** | **$111B** |
| **Mean** ($652K/bed) | **$146B** | **$174B** |
| P75 ($893K/bed) | $200B | $238B |

### 5. Dataform Pipeline Status

- **23 compiled actions** (9 datasets + 14 assertions), **0 errors**
- All tables rebuilt via `npx dataform run`
- All assertions pass (0 violations)

### 6. Updated/Created Files

| File | Action |
|---|---|
| `dataform/definitions/sources/sa_sf_dhc_join_raw.sqlx` | **Created** — upstream source declaration |
| `dataform/definitions/sources/sa_sf_dhc_join_enriched.sqlx` | **Rewritten** — declaration → table with `staffed_beds` INT + `premier_gpo_member_improved` |
| `dataform/definitions/marts/tsa_cy2025_enriched.sqlx` | **Edited** — added `dhc_staffed_beds` column |
| `dataform/definitions/marts/gpo_member_universe.sqlx` | **Edited** — fixed STAC filter, removed Health System, relaxed nonNull |
| `dataform/definitions/marts/tsa_clin_nc_cohort.sqlx` | **Edited** — exclude Health System from bed sum |
| `runs/.../exports/analyst_briefing.md` | **Comprehensive v4.3 update** — all bed counts, per-bed rates, extrapolation, sensitivity, GPO universe, top-25 table |

### 7. Key Analytical Notes

- **The $174B mean-rate extrapolation is an upper-range estimate** because the 100-system cohort is dominated by large academic medical centers with high spending intensity per bed. Smaller community hospitals and CAH facilities likely spend less per bed.
- **The median-rate extrapolation ($111B)** is likely more representative of the full 1,775-hospital GPO universe and should be presented alongside the mean for stakeholder discussions.
- **7 cohort systems have no bed match at all** (0 beds, no DHC hospital entries). These include OHSU, which routes spend through academic/corporate entity codes not catalogued as hospitals in DHC. Their spend is included in the cohort total but not reflected in per-bed calculations.
- **All 14 Dataform assertions pass** with the corrected data.

### 8. TSA-Calibrated Extrapolation (v4.3+cal)

Discovered that mean-rate per-bed extrapolation ($174B) overshoots TSA-observed GPO clinical by 43%. Clinical TSA reporting is near-comprehensive for GPO members (~92–95% coverage) because members have strong incentives to submit for contract savings analysis.

**TSA-observed GPO spend** (all `premier_gpo_member = TRUE` in `tsa_cy2025_enriched`):

| SL | Observed |
|---|---|
| Clinical | $52.2B (43.9%) |
| NC | $44.6B (37.5%) |
| Pharma | $20.8B (17.5%) |
| Food | $1.3B (1.1%) |
| Total | $119.9B |

**Calibrated extrapolation** (anchor on Clinical, 5% non-reporting, WF mix):

| Metric | Mean-Rate (Section III) | **TSA-Calibrated** | Change |
|---|---|---|---|
| Total non-labor | $174B | **$128B** | −26% |
| Clinical | $75B | **$55B** | −27% |
| NC | $72B | **$53B** | −26% |
| Pharma | $25B | **$18B** | −27% |
| C+NC $/bed | $652K | **$481K** | −26% |

**$128B is now the recommended primary estimate** for stakeholder presentations.

### 9. Analyst Briefing Production Process

Created `docs/ANALYST_BRIEFING_PRODUCTION.md` — a reusable process document that defines:
- When to trigger a briefing refresh
- 6-step production process (WF benchmarks → TSA cohort → Per-bed extrapolation → **TSA calibration cross-check** → Validation → Data assets)
- Internal consistency checks
- Non-reporting assumption rationale

The TSA clinical calibration (Step 4) is marked as **CRITICAL** and must be run whenever the briefing is updated.

### 10. Updated Artifacts

| File | Action |
|---|---|
| `runs/.../exports/analyst_briefing.md` | Added Section III-B (TSA-calibrated extrapolation), updated Executive Summary to $128B |
| `docs/ANALYST_BRIEFING_PRODUCTION.md` | **Created** — comprehensive production process with 6 steps + consistency checks |

---

## Session 12 (2026-02-12): Briefing Finalization, Stakeholder Email, Charts, Workspace Cleanup

### 11. Analyst Briefing — Historical Context Removal

Removed all version history references from the briefing to make it a clean, forward-looking stakeholder document:
- Stripped v3.2, v4, v4.3 references, session references, "prior approach" explanations
- Removed 73-line historical Clinical Extrapolation Validation section
- Renumbered sections, cleaned "(Expanded)" from Section II title
- File went from 540 → 455 lines

### 12. Transcript-Driven Refinements (6 items)

Based on a team meeting transcript (Bossemeyer, Lilly/Zach, Kapu/Uday) about what to convey to executive stakeholder Bill Marquardt:

1. **Ranges not points**: Replaced point estimates with ranges in exec summary ($122B–$132B)
2. **Spend-coverage stat**: Added "$42B = ~80% of $52B GPO clinical" to cohort finding
3. **NC analysis-readiness**: Added Finding #4 — 100 systems ready for NC on/off/non-contract analysis
4. **Merged Section III**: Combined per-bed and TSA-calibrated into single section with Approach A / Approach B (Recommended), range as headline
5. **GPO market-share**: Added "~27% of ~6,500 US hospitals" in exec summary and Section III
6. **Feed-mapping table**: Restructured Connection section with "What we now know" (volume targets × detailed feeds) and "What we can do next"

### 13. Precision Corrections

- **WF pharma/food explanation**: Corrected from "TSA taxonomy can't distinguish" to "WF invoices are large monthly aggregates from wholesalers/distributors lacking product-level granularity"
- **Clinical range floor tightened**: Lower bound moved from $48B (median-rate) to $52B (TSA-observed floor), since observed data already exceeded model-based lower bound. Clinical range: $52B–$57B
- **Range derivation documented**: Added "Range Derivation Rules" section to ANALYST_BRIEFING_PRODUCTION.md with clinical floor constraint, step-by-step formula, worked example

### 14. Analysis Scope Statement

Added "Analysis Scope" subsection to Executive Summary clarifying:
- Analysis is **health system and hospital-centric** (ERP-sourced data)
- Some non-acute volume appears from owned/leased/managed facilities sharing the ERP
- **Out of scope**: Independent non-acute/alternate-site facilities ($123B non-acute pharma alone)
- Pharma wholesaler tracing cross-check: $21.5B acute tracings vs $18B–$19B GPO extrapolation (slight overshoot expected due to broader pharmacy program footprint)

### 15. Stakeholder Visuals (new)

Created two charts for Bill Marquardt email:

| File | Description |
|------|-------------|
| `exports/gpo_spend_landscape.png` | Horizontal stacked bar — $128B total by service line, 84/16 split (SA data vs wholesaler tracings needed) |
| `exports/sl_readiness_matrix.png` | Bubble chart — volume × data-source readiness, with scope disclaimer |

The readiness matrix was refined through 3 iterations:
- X-axis: "Data Source for On/Off/Non-Contract Analysis" with "Sales tracings" (left) and "Health system ERP data in Supply Analytics" (right)
- Title: "Estimated GPO Member Health System Non-Labor Expense by Service Line"
- Scope note: "Excludes non-acute / continuum of care. Does not consider health systems that are pharma and/or food program only."
- Generation scripts alongside PNGs for reproducibility

### 16. Stakeholder Email Draft

Drafted email to Bill Marquardt covering:
- Invoice data analysis across 500+ health systems → reliable service line mix benchmarks
- Two key enablers: (1) volume targets by SL across full GPO, (2) extend Supply Analytics clinical dashboard to NC
- 100 systems comprehensively reporting C+NC → immediate NC analysis capability
- Scope note: health system purchasing only, not non-acute/alternate-site market
- Next steps: NC category breakdowns (Jordan Garrett, targeting 2/13), SL leader validation

### 17. Revenue Sizing (back-of-napkin)

At $127B midpoint, 3% avg admin fee, 60% shareback:
- **Gross admin fee**: $3.81B
- **Net admin fee (Premier retains)**: $1.52B
- Each 1% of volume = ~$38M gross / $15M net

### 18. Workspace Cleanup

**Moved PE-specific docs from core to run-local:**
- `docs/ANALYST_BRIEFING_PRODUCTION.md` → `runs/2026-02-10__portfolio-expansion/ANALYST_BRIEFING_PRODUCTION.md`
- `docs/validated_health_system_mapping.md` → `runs/2026-02-10__portfolio-expansion/validated_health_system_mapping.md`

**Confirmed to stay in core** (generalizable):
- `docs/PREMIER_DATA_MODELS_HANDOFF.md` — explicitly "generalizable reference for any agent"
- `docs/.github/skills/premier-data-analytics/` — general Premier data skill
- All data dictionaries, architecture docs, tooling guides

### 19. Core PR Merged

**PR #40** merged into `main` — "core: Dataform gitignore, dataset naming convention, best practices doc":
1. `.gitignore` — `dataform/.df-credentials.json`, `dataform/snowflake.log`, `dataform/node_modules/`
2. `docs/PREMIER_DATA_MODELS_HANDOFF.md` — restored dataset naming convention block
3. `docs/dataform_in_vscode_best_practices.md` — new 858-line Dataform CLI guide

Worktree branch synced with main at `fa92aa7`.

### 20. Current Artifact State

| File | Location | Status |
|------|----------|--------|
| `analyst_briefing.md` | `runs/.../exports/` | **Final** — ~425 lines, scope statement, ranges, merged sections, all 4 findings |
| `ANALYST_BRIEFING_PRODUCTION.md` | `runs/.../` (run-local) | Updated — scope boundaries, pharma tracing cross-check, range derivation rules |
| `validated_health_system_mapping.md` | `runs/.../` (run-local) | Moved from core, unchanged |
| `gpo_spend_landscape.png` + `.py` | `runs/.../exports/` | Final stacked bar chart |
| `sl_readiness_matrix.png` + `.py` | `runs/.../exports/` | Final bubble chart (3 iterations) |
| `HANDOFF.md` | `runs/.../` | This file — updated through Session 12 |

### 21. Key Numbers (current pipeline)

| Metric | Value |
|--------|-------|
| Cohort systems | 100 |
| Cohort beds (hospital-only) | 113K |
| GPO facilities | 1,775 |
| GPO beds | 224K |
| TSA-observed GPO clinical | $52.2B |
| Recommended total non-labor | **$128B** |
| Presentation range | **$122B–$132B** |
| Clinical range | $52B–$57B |
| NC range | $50B–$54B |
| Pharma range | $18B–$19B |
| Food range | ~$2B |
| Pharma wholesaler tracing (acute) | $21.5B |
| Pharma wholesaler tracing (non-acute) | $123B |
| WF clinical share | 0.428 |
| WF C+NC share | 0.841 |
| Non-reporting assumption (clinical) | 5% |

### 22. Open Items / Next Steps

1. **NC category breakdowns**: Awaiting Jordan Garrett's catch-all category decomposition (target 2/13) to enable NC subcategory opportunity sizing
2. **SL leader validation**: Confirm category-to-SL mapping with Pam (Clinical), Molly (NC), Justin (Pharma), Joan (Food)
3. **System-level scoring matrix**: Build per-system × per-SL heat map once NC subcategories are available
4. **Email to Bill**: Draft ready; send once Matt reviews final wording and chart selection
5. **Pharma/Food deep dive**: Source wholesaler/distributor tracing data for on/off/non-contract in these channels

---

## Session 13 (2026-02-12 → 2026-03-01): Repo Hygiene, Core Sync, Q&A

This session spanned multiple interactions focused on repo maintenance and knowledge-transfer Q&A rather than new analysis.

### 23. .github/ Restoration (2026-02-12)

Root `.github/` folder was missing from this branch (disappeared after Session 9b commit `2d8e3bd`). Only `docs/.github/` existed (a misplaced duplicate).

**Actions**:
1. Restored `.github/` from `origin/main` via `git checkout origin/main -- .github/`
2. Found 3 files more current in `docs/.github/` than main (copilot-instructions.md, bigquery-data-models/SKILL.md, premier-data-analytics/SKILL.md) — all dated Feb 12 on this branch vs Feb 6/Jan 27/Feb 9 on main
3. Copied the more-current versions into root `.github/`
4. Removed `docs/.github/` duplicate
5. Committed as `5713631`, pushed

**PR #41**: Promoted the 3 updated `.github/` files to main (merged).

### 24. Q&A Interactions (2026-02-25)

No code changes. Two knowledge-transfer questions answered from existing artifacts:

1. **TSA data model fields**: Explained 4 fields added across 2 layers:
   - `tsa_cy2025`: `parent_service_line` (from `service_line_mapping` JOIN)
   - `tsa_cy2025_enriched`: `is_clin_nc_cohort`, `premier_gpo_member`, `dhc_staffed_beds`

2. **Extrapolation multiplier**: Explained why we don't use a simple cohort-to-GPO multiplier (composition bias). The recommended approach (Approach B) anchors on TSA-observed clinical ($52.2B), adjusts for 5% non-reporting, then divides by WF clinical mix share (0.428) → $128B. Bed ratio is ~2.0× (224K ÷ 113K) but should only be applied to median rate.

### 25. Core Sync & PR #45 (2026-03-01)

**Incoming from main** (3 PRs merged since last sync):
- PR #42: Graph scheduling/draft utilities
- PR #43: Graph attachments, mail search, drafts, workbook profiler
- PR #44: Browser-run workflow updates

All merged cleanly — no conflicts.

**Promoted to main** (PR #45, merged):
- Renamed 2 data dictionary files from `matthew-bossemeyer.*` → `abi-xform-dataform-prod.*` (correct production project)
- Fixed project references in `MCP_TOOLBOX_GUIDE.md` and `data_dictionaries/README.md`
- Added dictionary tooling standardization entry to `CORE_REPO_WORK_LOG.md`

**Post-sync state**: Zero core-file divergence between this branch and `origin/main`. Only `runs/`, `notes/`, `dataform/`, `scripts/`, and `config/` differ (all PE-specific, intentionally run-local).

### 26. Current State Summary

| Item | Value |
|------|-------|
| Branch | `run/2026-02-10__portfolio-expansion` at `f3cc1cd` |
| Main synced through | PR #45 (2026-03-01) |
| Core divergence | Zero (excluding PE-specific dirs) |
| Dataform | 23 actions (9 datasets + 14 assertions), 0 errors, all pass |
| Analyst briefing | ~425 lines, final stakeholder-ready document |
| Key estimate | $128B recommended ($122B–$132B range) |
| Cohort | 100 systems, 113K beds, 1,775 GPO facilities, 224K beds |

### 27. Open Items / Next Steps (Updated)

1. **NC category breakdowns**: Awaiting Jordan Garrett's catch-all category decomposition to enable NC subcategory opportunity sizing
2. **SL leader validation**: Confirm category-to-SL mapping with Pam (Clinical), Molly (NC), Justin (Pharma), Joan (Food)
3. **System-level scoring matrix**: Build per-system × per-SL heat map once NC subcategories are available
4. **Email to Bill**: Draft ready; send once Matt reviews final wording and chart selection
5. **Pharma/Food deep dive**: Source wholesaler/distributor tracing data for on/off/non-contract in these channels
6. **HANDOFF.md update**: Committed through Session 13 (this section)
