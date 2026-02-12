# Portfolio Expansion: Multi-Source Spend Analysis

**From**: Matt Bossemeyer  
**Date**: February 12, 2026 (updated — v4 SL mapping correction + v4.1 vendor_name_patterns expansion)  
**Re**: Health System Spend Landscape — Service Line Mix, Cohort Expansion, and Extrapolation Framework

---

## Executive Summary

We have built a **multi-data-source analytical framework** for the Portfolio Expansion initiative, using two complementary Premier datasets:

| Data Source | Role | Systems | Beds | Spend |
|-------------|------|---------|------|-------|
| **Workflow History (WF)** | Establishes expected **service line mix** benchmarks | 521 CY2025 systems (46 balanced 3-SL reporters) | — | $74.5B total |
| **Transaction Analysis (TSA)** | Provides the **addressable Clinical + NC cohort** for on/off/non-contract profiling | **100 systems** | **259K** | **$89B total** |

### Why two sources, and why Clinical + Non-Clinical only for TSA?

**Pharma and food purchasing flows through wholesalers and distributors** (McKesson, Cardinal, Sysco, US Foods). The invoices Premier sees in WF reflect these flows, but TSA's `Contract_Category` taxonomy cannot reliably distinguish on-contract vs. off-contract for these channels. WF invoice data *can* establish the expected proportion of pharma and food spending relative to clinical and NC — giving us a benchmark service line mix — but TSA cohort selection should narrow to Clinical + Non-Clinical, where Premier has direct contracting visibility and on/off/non-contract status is determinable.

This reframing **more than triples the qualifying cohort** (from 31 systems requiring 3+ SLs to 100 systems with comprehensive Clinical + NC reporting), while maintaining analytical rigor.

> **v4 Methodology Correction (Session 9b)**: The WF entity-bridge service line proportions (`entity_sl_mix`) were rebuilt using TSA's `service_line` field joined to a single `service_line_mapping` table, replacing the prior explicit `Contract_Category` enumeration. The old approach (v3.2) listed ~51 NC categories in a CASE WHEN with `ELSE → Clinical` fallback, which **misclassified $19.5B of Non-Clinical spend as Clinical** across ~160 categories that were not in the explicit NC list (e.g., PURCHASED SERVICES subcategories like "General Outsourced Clinical Services" $3.5B, "Clinical Equipment Repair & Maintenance" $2.2B, etc.). The corrected v4 mapping uses TSA's own `service_line` taxonomy (10 values → 4 parent service lines) as the single source of truth. All benchmarks below reflect this correction. The Dataform pipeline in `dataform/` makes this mapping auditable and reproducible.

### Key Findings

1. **WF Service Line Mix** (entity-bridge classification, balanced 3-SL reporters, 46 systems, $55.2B classified):
   - Clinical: **~43%** (IQR 34–51%) | Non-Clinical: **~41%** (IQR 26–46%) | Pharma: **~14%** (IQR 6–27%) | Food: **~1–2%**
   - Clinical and NC are roughly balanced at ~43%/41% across cohort definitions
   - TSA external cross-check: Pharma = 18.6% of $133.5B TSA CY2025 mapped spend — consistent with our WF-derived 14–17% range

2. **TSA Clinical+NC Cohort**: **100 health systems**, 259K beds, $89B total TSA spend
   - Clinical spend: $42.0B | NC spend: $34.5B
   - Within addressable (Clinical+NC): **55% Clinical / 45% NC**
   - Per-bed: $162K Clinical + $133K NC = **$295K addressable per bed**
   - 25 systems ≥$1B, 19 at $500M–$1B, 38 at $100M–$500M

3. **Cohort expansion**: All 81 original systems are retained; 19 new systems join the cohort because corrected NC classification means more systems now meet the ≥$10M NC threshold.

4. **GPO Membership Extrapolation**: Premier's GPO membership universe — **868 acute-care facilities, 194K staffed beds** — represents an estimated **$68B in total non-labor purchasing**:
   - TSA-observable C+NC addressable: **$57B** ($295K/bed × 194K beds)
   - Total non-labor (WF-adjusted, C+NC ÷ 0.84): **$68B**
   - By service line: Clinical **~$29B** (43%) | NC **~$28B** (41%) | Pharma **~$10B** (14%) | Food **~$1B** (1.5%)
   - *Note: The prior $36B estimate used marker-category per-bed rates ($160K/bed), which counted only specific contract categories. The v4 rate ($295K/bed) counts ALL categories under parent_service_line Clinical/NC, providing a more complete measure of the same spend.*

---

## Section I: WF Service Line Mix Benchmarks

### Methodology: Entity-Bridge Hybrid Classification

We classified CY2025 WF invoice spend across 521 health systems using a two-layer approach:

1. **Primary — Entity-code bridge (79% of spend)**: Each WF invoice has a `vendor_entity_code`. We matched these to TSA's 18,838 child entity codes, where each entity has a known service line mix derived from TSA's `Contract_Category` classifications. Invoice amounts are then distributed proportionally across the four service lines based on that entity's TSA-derived mix. This approach uses **double-attribution** (both `Vendor_Entity_Code` and `Manufacturer_Entity_Code` from TSA) and applies at the **child entity level** (not top-parent), so that the same parent company (e.g., Cardinal Health) is correctly split: OH5010 (med-surg) → 81% clinical, 682446 (drug distribution) → 90% pharma.

2. **Fallback — Name-pattern rules (4.5% of spend)**: For invoices without a matching entity code, we apply vendor-name LIKE patterns from a persistent `vendor_name_patterns` reference table (153 patterns, priority-ordered by service line band). The pattern table assigns 100% of the invoice to a single SL based on vendor type (e.g., PBM → pharma, construction → NC, anesthesia groups → clinical, Fisher Scientific → clinical). Priority bands ensure pharma-specific patterns (Nuclear Pharmacy, 340B, Specialty Pharmacy, McKesson Drug/Spec/Rx) fire before broader distributor catch-all rules. The pattern table is a Dataform-managed asset — adding or modifying rules requires editing only `vendor_name_patterns.sqlx`, not the classification query.

3. **Exclude identification (2.0% of spend)**: The pattern table also identifies non-addressable spend — taxes (IRS), insurance claims (Aetna, BCBS, Cigna), retirement/investment (Fidelity, Vanguard, VOYA, TIAA), payroll, banking, intercompany transfers, placeholder vendors, government remittances (State Comptroller, Healthcare & Family Services), ASO/benefits funds, and one-time pass-through entries — and removes it from the addressable denominator.

| Classification Layer | WF CY2025 Spend | Share of Total |
|---------------------|----------------|----------------|
| Entity-bridge classified | $58.9B | 79.1% |
| Name-pattern classified (SL) | $3.4B | 4.5% |
| Name-pattern identified (EXCLUDE) | $1.5B | 2.0% |
| Unmatched (residual) | $10.7B | 14.3% |
| **Total** | **$74.5B** | 100% |

This approach achieves an **86% addressable classification rate** across $74.5B in CY2025 WF spend (up from 85% after expanding the vendor_name_patterns reference table with 28 additional patterns recovering ~$1.4B from the unmatched pool). The entity-bridge method is critical for multi-SL distributors: a naive vendor-name approach would assign all Cardinal Health or McKesson invoices to a single SL, when in reality these companies have distinct child entities (e.g., Cardinal OH5010 = 81% clinical med-surg, Cardinal 682446 = 90% pharma drug distribution). Operating at the child-entity level correctly splits this spend.

### Benchmark Service Line Mix — Ranges & Confidence Intervals

We present benchmarks as **ranges** rather than point estimates, reflecting genuine system-to-system variation and sensitivity to cohort selection. The primary cohort is the **3-SL balanced** set (46 systems), which requires ≥1% in Clinical, NC, and Pharma but does not impose a food floor — avoiding the selection bias that the ≥1% food requirement introduces (it drops systems and preferentially removes higher-pharma systems).

#### Central Estimates (Spend-Weighted, by Cohort)

| Cohort | N | Classified | Clinical | NC | Pharma | Food |
|--------|---|-----------|----------|----|--------|------|
| **3-SL balanced ≥$200M** (primary) | **46** | **$55.2B** | **42.8%** | **41.3%** | **14.4%** | **1.5%** |
| 3-SL balanced ≥$100M | 57 | $56.4B | 43.0% | 41.0% | 14.5% | 1.5% |
| 4-SL food≥0.5% ≥$200M | 39 | $52.0B | 42.3% | 43.0% | 13.1% | 1.6% |
| 4-SL food≥1% ≥$200M | 26 | $27.3B | 43.0% | 43.6% | 10.9% | 2.4% |
| All ≥$50M, ≥70% match | 79 | $59.5B | 42.1% | 39.5% | 16.8% | 1.6% |
| 3-SL balanced ≥$50M | 74 | $57.5B | 43.1% | 40.9% | 14.5% | 1.5% |

**3-SL balanced definition**: Systems with ≥$200M total spend, ≥70% addressable match rate, and ≥1% of classified spend in Clinical, NC, and Pharma.

#### System-Level Distribution (Primary 46-System Cohort, Unweighted)

| Service Line | Min | P10 | P25 | Median | Mean | P75 | P90 | Max |
|-------------|-----|-----|-----|--------|------|-----|-----|-----|
| **Clinical** | 16.2% | 26.9% | 34.4% | 43.9% | 44.5% | 51.0% | 63.6% | 95.3% |
| **NC** | 1.3% | 3.8% | 25.7% | 34.3% | 34.2% | 46.3% | 55.3% | 76.3% |
| **Pharma** | 1.5% | 3.4% | 6.3% | 10.8% | 19.7% | 27.4% | 53.4% | 71.6% |
| **Food** | 0.0% | 0.3% | 0.6% | 1.1% | 1.6% | 2.1% | 3.1% | 7.9% |

#### Recommended Presentation Ranges

| Service Line | Central Estimate | IQR (System-Level) | Cross-Cohort Range | External Check (TSA) |
|-------------|-----------------|--------------------|--------------------|---------------------|
| **Clinical** | ~43% | 34–51% | 42–43% | 43% (parent_service_line) |
| **NC** | ~41% | 26–46% | 40–44% | 37% (parent_service_line) |
| **Pharma** | ~14% | 6–27% | 11–17% | **18.6%** |
| **Food** | ~1–2% | 0.6–2.1% | 1.5–2.4% | 1.1% |

> **TSA cross-check**: TSA Pharmacy = **18.6%** of $133.5B CY2025 mapped spend, consistent with our WF-derived 14–17% range (the range widens to include higher-pharma cohort definitions). TSA uses `service_line` → `parent_service_line` via the same mapping table as WF v4, so the Clinical and NC comparisons are now directly aligned.

**Key observations**:
- **Clinical and NC are roughly balanced** (~43%/41%) across all cohort definitions, a dramatic shift from the v3.2 estimate of 64%/22%. The prior overcount of Clinical was caused by ~160 NC contract categories falling through the explicit enumeration's `ELSE → Clinical` fallback. The corrected entity-bridge proportions show NC is nearly as large as Clinical.
- **Pharma is ~14% in the primary cohort** (weighted); system-level median is 10.8% with wide IQR (6–27%), reflecting genuine variation in how much pharma flows through WF vs. direct wholesaler channels. The strict 4-SL food≥1% cohort depresses pharma to 10.9% due to selection bias (food-floor drops pharma-heavy systems)
- **TSA pharma cross-check validates**: TSA Pharmacy = 18.6% on $133.5B mapped spend; our 14.4% weighted central falls within range given different scope (WF captures invoices routed through ERP, TSA captures contract-specific transactional data)
- **NC at ~41%** is the most dramatic correction — stable across all cuts (40–44%), reflecting the proper inclusion of PURCHASED SERVICES, FACILITIES, and IT/DIGITAL HEALTH categories that were previously misclassified as Clinical
- **Food at ~1–2%** is structurally small in WF; the 4-SL cohort inflates it to 2.4% by definition (food floor = 1%)
- **System-level variation is substantial**: Pharma ranges from 1.5% to 71.6% across the 46-system cohort, driven by differences in ERP capture (some systems route all pharma through wholesaler-direct channels not visible in WF)

### Selected System-Level Mix (Primary 3-SL Cohort)

| System | Total ($B) | Match % | Clinical | NC | Pharma | Food |
|--------|-----------|---------|----------|----|--------|------|
| AdventHealth (AHS Florida) | 8.51 | 88.7% | 50.8% | 40.0% | 7.0% | 2.2% |
| Catholic Health Initiatives | 4.51 | 83.2% | 30.2% | 62.5% | 5.3% | 2.0% |
| Dignity Health | 4.34 | 80.3% | 29.3% | 61.7% | 6.3% | 2.7% |
| EM_CCH | 1.60 | 84.9% | 49.9% | 37.5% | 10.8% | 1.8% |
| Beth Israel Lahey Health | 1.36 | 71.5% | 43.9% | 48.8% | 5.7% | 1.6% |
| EM_Renown | 1.30 | 88.3% | 49.7% | 29.1% | 19.7% | 1.5% |
| Adventist Health (California HQ) | 1.29 | 84.0% | 35.4% | 47.5% | 9.2% | 7.9% |
| EM_ULHealth | 1.25 | 90.1% | 45.5% | 50.5% | 3.4% | 0.6% |
| EM_SouthAlabama | 0.29 | 92.6% | 68.5% | 23.2% | 5.2% | 3.1% |

> Match rates >100% occur when exclude-type spending (taxes, insurance) is identified and removed from the denominator, making the addressable base smaller than classified spend.

### Sensitivity to Unmatched Spend

The ~15% residual unmatched spend ($10.7B) is predominantly a long tail of small, nondescript vendors (84K+ distinct names). Prior to pattern expansion (Session 9c), the unmatched pool contained identifiable vendor types that have since been reclassified:

- **Recovered → NC ($704M):** McKesson Technology ($277M), locum tenens ($137M), Deloitte/KPMG/Accenture ($167M), Siemens Industry ($41M), MedStaff ($42M), NTT Data ($24M), janitorial ($16M)
- **Recovered → Food ($453M):** US Foods ($287M), Pepsi ($51M), Aramark ($45M), Compass Group ($38M), Sysco ($26M), Coca-Cola ($6M)
- **Recovered → Clinical ($223M):** Renal care ($77M), Fisher Scientific ($63M), laboratory vendors ($60M), dialysis ($21M)
- **Recovered → Pharma ($34M):** RxBenefits ($31M), pharmacy benefit managers ($3M)
- **Recovered → Exclude ($26M):** Comptroller/government entities

Note: Major PBMs (OptumRx $190M, Express Scripts $15M) and food service providers (Sodexo $140M) were already classified via the entity-bridge layer, not name patterns. Scenario analysis shows the benchmark remains robust:

| Scenario | Clinical | NC | Pharma | Food |
|----------|----------|----|--------|------|
| Matched only (current) | 43.0% | 38.8% | 16.7% | 1.5% |
| Estimated actual unmatched mix | ~41% | ~40% | ~16% | ~2% |
| Extreme: all unmatched = pharma | ~37% | ~33% | ~29% | ~1% |

Uncertainty band: ±2–4pp on each SL from unmatched spend (tightened from ±3–5pp after pattern expansion).

### Implications for Extrapolation

For any system where you know the Clinical + NC spend from TSA, you can estimate total non-labor purchasing:
- If Clinical + NC = **~84%** of total (per primary benchmark: 42.8% + 41.3%), then total ≈ Clinical+NC / 0.84
- Pharma ≈ total × 0.14–0.15 (range: 0.11–0.17 across cohort definitions)
- Food ≈ total × 0.01–0.02

These ratios should be applied **directionally** — individual system mix varies substantially (pharma IQR: 6–27%).

---

## Section II: TSA Clinical + Non-Clinical Cohort (Expanded)

### Qualification Criteria

A system qualifies if it reports:
- **Clinical spend ≥$10M** across all `parent_service_line = 'Clinical'` categories (maps from TSA `service_line` values: PPI, NURSING, SURGICAL, DIAGNOSTICS, DISTRIBUTION via `service_line_mapping`)
- **NC spend ≥$10M** across all `parent_service_line = 'Non-Clinical'` categories (maps from: PURCHASED SERVICES, FACILITIES, IT/DIGITAL HEALTH)
- **≥5 distinct clinical contract categories** with spend (breadth check)
- **≥5 distinct NC contract categories** with spend (breadth check)

> **v4 change**: The prior cohort (v3.2) used explicit "marker category" lists (~50 clinical + ~43 NC) to qualify systems. The v4 cohort uses `parent_service_line` from the `service_line_mapping` table, which includes ALL contract categories under each service line. This expanded the cohort from 81 → 100 systems because more systems now meet the ≥$10M NC threshold with proper NC classification.

### Excluded Entities

| Excluded | Reason |
|----------|--------|
| ACURITY ($29.9B), ALLSPIRE ($7.8B), YANKEE ALLIANCE ($2.0B), CONDUCTIV ($1.6B) | GPO/purchasing alliances — not individual health systems |
| ALLIANT, HOSPITAL SHARED SERVICES, HEALTH ENTERPRISES, PRAIRIE HEALTH VENTURES, WELLLINK, MHS PURCHASING, OPTUM | GPO or multi-system purchasing cooperatives |
| Entities containing "TEST", "DEMO", or "COST TECHNOLOGY" | Non-production data |

### Cohort Summary

**100 health systems** with comprehensive Clinical AND Non-Clinical TSA reporting in CY2025.

| Metric | Value |
|--------|-------|
| Total systems | 100 |
| Systems with bed match | 99 (99%) |
| Total staffed beds | 259,246 |
| Total TSA spend | $89.0B |
| Clinical spend (parent_service_line) | $42.0B |
| NC spend (parent_service_line) | $34.5B |
| Addressable (Clinical+NC) | $76.5B |
| Clinical share of addressable | 55% |
| NC share of addressable | 45% |
| Wtd avg Clinical per bed | **$162K** |
| Wtd avg NC per bed | **$133K** |
| Wtd avg addressable per bed | **$295K** |

> **Note on per-bed rate change**: The prior $160K/bed used marker-category spend only (~93 categories). The v4 $295K/bed uses ALL categories classified under parent_service_line Clinical or Non-Clinical (~300+ categories). This is a more complete measure of the same underlying spend — it doesn't represent more purchasing, just more complete classification.

### Size Distribution

| Tier | Systems | Beds |
|------|---------|------|
| ≥$1B total TSA spend | 25 | 169K |
| $500M–$1B | 19 | 37K |
| $100M–$500M | 38 | 47K |
| <$100M | 18 | 6K |

### Top 25 Systems by Total Spend

| System | Entity Code | Spend ($M) | Clin ($M) | NC ($M) | Beds | $/bed (K) |
|--------|-------------|-----------|----------|---------|------|-----------|
| ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE | AQ9425 | 17,603 | 7,921 | 7,491 | 35,440 | 497 |
| UPMC HEALTH SYSTEM | 743692 | 5,341 | 1,802 | 3,103 | 11,549 | 462 |
| MCLAREN HEALTH CARE | MI2002 | 3,726 | 594 | 2,485 | 3,647 | 1,022 |
| ADVENTHEALTH | FL0343 | 3,720 | 2,845 | 666 | 18,166 | 205 |
| WEST VIRGINIA UNITED HEALTH SYSTEM | WV0541 | 3,663 | 1,476 | 1,486 | 5,141 | 713 |
| TEXAS HEALTH RESOURCES | TX2246 | 3,443 | 1,878 | 1,220 | 11,326 | 304 |
| PRISMA HEALTH | AI6913 | 2,905 | 913 | 1,176 | 5,042 | 576 |
| OREGON HEALTH SCIENCES UNIVERSITY | OR2023 | 1,969 | 335 | 493 | 1,118 | 1,761 |
| UVA HEALTH SYSTEM | VA0019 | 1,959 | 576 | 602 | 1,169 | 1,676 |
| UNIVERSITY HEALTH SYSTEM | TX0488 | 1,691 | 433 | 989 | 779 | 2,171 |
| HONORHEALTH | 649419 | 1,558 | 746 | 731 | 3,308 | 471 |
| FAIRVIEW HEALTH SERVICES | MN2013 | 1,465 | 731 | 285 | 3,905 | 375 |
| BANNER HEALTH | AZ2090 | 1,426 | 1,246 | 108 | 11,812 | 121 |
| BAPTIST HEALTHCARE SYSTEM | KY0074 | 1,402 | 698 | 471 | 4,314 | 325 |
| CHILDREN'S HOSPITAL CORPORATION | 847014 | 1,400 | 330 | 536 | 572 | 2,447 |
| UNIVERSITY OF CALIFORNIA - IRVINE | CA3550 | 1,312 | 381 | 428 | 911 | 1,440 |
| ST LUKE'S UNIVERSITY HEALTH NETWORK | PA0023 | 1,294 | 560 | 630 | 3,677 | 352 |
| SOUTH BROWARD HOSPITAL DISTRICT | FL0085 | 1,226 | 407 | 743 | 3,636 | 337 |
| UHS OF DELAWARE, INC. | 718653 | 1,205 | 1,727 | 19 | 28,826 | 42 |
| ECU HEALTH | 714757 | 1,186 | 385 | 379 | 2,734 | 434 |
| PEACEHEALTH | WA0014 | 1,181 | 439 | 487 | 2,562 | 461 |
| HEALTH FIRST SHARED SERVICES | 712579 | 1,116 | 280 | 613 | 1,836 | 608 |
| BAYSTATE HEALTH INC. | MA2022 | 1,070 | 548 | 459 | 1,952 | 548 |
| MTWY HEALTH | AW6643 | 1,024 | 416 | 532 | 917 | 1,117 |
| OSF HEALTHCARE SYSTEM | IL5043 | 1,000 | 673 | 306 | 4,896 | 204 |

> **Notable changes from v3.2**: UHS of Delaware dropped from #3 ($3.8B) to #19 ($1.2B) because its $1.7B "Clinical" + $19M NC reflected UNKNOWN category rows now excluded. McLaren's NC jumped from $1.3B to $2.5B with corrected classification. Banner Health's Clinical went from $600M to $1.2B as more categories are properly attributed.

*Full 100-system list persisted in BigQuery table `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.tsa_clin_nc_cohort`.*

---

## Section III: Extrapolation to GPO Membership

This section bridges from the 100-system TSA cohort (Section II) to an estimate of total non-labor purchasing across Premier's full GPO membership. The extrapolation follows a three-step chain:

1. **Empirical per-bed rate** from the TSA cohort (what we observe)
2. **Membership bed count** from the GPO universe (what we scale to)
3. **WF mix multiplier** to estimate the total non-labor envelope beyond C+NC (what we infer)

### Step 1: Addressable Per-Bed Benchmarks (Clinical + NC)

From the 100-system cohort with matched beds (99 systems, 259K beds):

| Metric | Clinical | NC | Addressable (C+NC) |
|--------|----------|----|--------------------|
| Weighted avg $/bed | **$162K** | **$133K** | **$295K** |

This $295K/bed rate is the **TSA-observable** Clinical+NC spend — all contract categories classified under `parent_service_line` = 'Clinical' or 'Non-Clinical'. It includes every category where Premier has direct contracting visibility and where on/off/non-contract status is determinable. It does not include pharma or food spend.

> **v4 change**: The prior $160K/bed rate used only ~93 "marker categories" to define Clinical+NC. The v4 rate uses ALL categories under the Clinical and Non-Clinical parent service lines (~300+ categories), providing a more complete measure. This is the primary reason the extrapolation increased from $36B to $68B — it's not more purchasing, but more complete classification of the same underlying spend.

### Step 2: GPO Membership Universe

The target population for extrapolation is Premier's GPO membership, defined as:

| Filter | Value |
|--------|-------|
| Source table | `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join` |
| Membership indicator | `premier_gpo_member = TRUE` |
| Hospital types | Short Term Acute Care, Health System, Childrens Hospital, Critical Access Hospital |
| Deduplication | One row per `dhc_definitive_id` |

| GPO Universe | Hospitals | Beds |
|-------------|-----------|------|
| Health System | 116 | 113,387 |
| Short Term Acute Care | 476 | 68,275 |
| Childrens Hospital | 40 | 7,030 |
| Critical Access Hospital | 236 | 4,944 |
| **Total** | **868** | **193,636** |

The TSA cohort covers **31.5%** of GPO member beds (61K of 194K) — a strong empirical foundation for extrapolation.

> **Why `premier_gpo_member` instead of `NATIONAL` keyword?** The `premier_gpo_member` boolean is the authoritative GPO participation flag. The prior approach — filtering by the `NATIONAL` keyword in `active_membership_type` — included 260 psychiatric hospitals, 57 LTACs, and 34 VA hospitals not relevant to med-surg extrapolation. It also missed 129 acute-care facilities that are GPO=TRUE but carry no NATIONAL keyword (including NYP campuses, Children's Healthcare of Atlanta, and PREMIERCHOICE-only members). The new definition yields fewer facilities (868 vs 1,174) but a cleaner, acute-care-only denominator with comparable bed volume (194K vs 198K).

### Step 3: Total Non-Labor Estimates via WF Mix

The WF-derived SL mix (Section I) tells us that Clinical+NC represent **~84%** of total non-labor purchasing (43.1% + 41.0%). We use this to scale from the TSA-observable addressable spend to the full non-labor envelope:

| | Calculation | Result |
|---|---|---|
| GPO beds | — | 193,636 |
| C+NC addressable | 194K beds × $295K/bed | **$57B** |
| Total non-labor | $57B ÷ 0.84 | **$68B** |

### Service Line Decomposition

Applying the WF benchmark mix percentages to the $68B total non-labor estimate:

| Service Line | Share | Estimated GPO Spend | Per Bed |
|-------------|-------|--------------------|---------| 
| **Clinical** | ~43% | **$29.2B** | $151K |
| **Non-Clinical** | ~41% | **$27.9B** | $144K |
| **Pharma** | ~14% | **$9.5B** | $49K |
| **Food** | ~1.5% | **$1.0B** | $5K |
| **Total** | 100% | **$68.1B** | $352K |

> **Interpretation**: These are estimates of what Premier GPO members spend in each service line across their total non-labor purchasing — not what flows through Premier contracts. The gap between this total and Premier's contracted volume is the opportunity the Portfolio Expansion Heat Map is designed to quantify.

> **Caveat on pharma and food**: The pharma estimate ($9.5B) reflects only GPO-addressable pharma purchasing visible in WF invoices. Wholesaler-direct channels, 340B carve-outs, and specialty pharmacy flows are not captured — the actual pharma spend is likely significantly higher. Similarly, food ($1.0B) is a structural undercount relative to industry benchmarks suggesting 3–5% of operating expenses.

### Sensitivity

The $68B estimate is sensitive to two inputs:

| Input | Range | Impact on Total |
|-------|-------|-----------------| 
| C+NC per-bed rate | $175K–$464K (P25–P75 of cohort systems) | $40B–$107B |
| WF C+NC share of total | 82%–87% (cross-cohort) | $66B–$70B |

The combined range across both inputs is approximately **$40B–$107B**. The $68B central estimate uses the bed-weighted average per-bed rate, which appropriately weights large systems with more complete TSA submissions. The system-level P25–P75 range ($175K–$464K) reflects individual system variation — the wide spread is driven by differences in TSA reporting completeness rather than genuine purchasing variation.

### For Portfolio Expansion Heat Map Purposes

- **Clinical + NC represent ~84% of total non-labor purchasing**, making them not only the directly addressable service lines for TSA profiling, but also the overwhelming majority of the spend envelope
- **Pharma (~14%) and Food (~1–2%)** are comparatively small at the GPO-purchasable level; much of what flows through wholesaler entities like Cardinal and McKesson is actually med-surg supply chain rather than pharma distribution
- The 100-system cohort provides the foundation for the service-line-by-system scoring matrix

---

## Section III-A: Clinical Extrapolation Validation (Session 9)

> **Context note**: This validation section was performed using the v3.2 marker-category definition of clinical spend ($131K/bed system-level, $146K/bed facility-level). The v4 full-parent_service_line clinical rate is $162K/bed (cohort, facility-level). The gap decomposition factors identified below (bed inflation, alt-site entities, alliance roll-ups, unmatched facilities) remain valid and apply equally to the v4 rate. No re-run is needed — the findings about *methodology soundness* are unchanged; only the *absolute rates* differ.

### Spot-Check Methodology

To validate the per-bed extrapolation approach, we projected CY2025 clinical spend across all TSA-reporting facilities using the cohort's per-bed rate, then compared to actual TSA clinical spend ($58.2B).

**Initial finding**: The projection undershot actuals by 26% ($46.3B projected vs $58.2B actual). A thorough investigation **fully explained** this gap through three independent factors.

### Gap Decomposition

| Factor | Amount | % of Gap | Root Cause |
|--------|--------|----------|-----------|
| **System-level bed inflation** | $3.0B | 25% | Cohort rate ($131K/bed) used system-wide beds (297K) including non-TSA-reporting facilities; only 222K beds have TSA-reporting entities (1.33× inflation) |
| **Alliance/GPO unmatched spend** | $3.7B | 31% | Purchasing cooperatives (Acurity $1.9B, Allspire $0.8B, Conductiv $0.4B, etc.) route clinical spend through entity codes that don't map to hospital beds |
| **Alt-site unmatched spend** | $3.3B | 28% | Physician offices (2,969 entities, $0.8B), ASCs (262 entities, $0.3B), ambulatory centers, corporate offices, and other non-bed-bearing entities within health systems |
| **Acute hospitals missing from DHC** | $1.8B | 15% | 197 actual hospitals not matched to DHC beds (data quality gap — includes Fairview, PeaceHealth, HealthPartners, UPMC satellites) |
| **Other** | $0.1B | 1% | — |
| **Total** | **$11.9B** | **100%** | **Fully explained** |

### Corrected Per-Bed Clinical Rates

The facility-level rate (matching only entities that actually report TSA clinical spend to their DHC beds) is materially higher than the system-level rate:

| Rate Basis | Entities | Beds | Clinical Spend | Per-Bed Rate |
|-----------|----------|------|---------------|-------------|
| Cohort system-level (Session 8b) | 80 systems | 297K | $39.1B | **$131K** |
| Cohort facility-level | 752 entities | 222K | $34.6B | **$156K** |
| All-TSA facility-level | 1,264 entities | 337K | $49.3B | **$146K** |
| Non-cohort facility-level | 512 entities | 115K | $14.7B | **$128K** |

The **$131K system-level rate is biased low** by 33% bed inflation from facilities within cohort health systems that don't report to TSA. The correct facility-level rate is **$146K/bed** (all TSA) or **$156K** (cohort only).

### TSA `member_num_beds` vs DHC Beds

TSA's self-reported bed field tracks DHC almost exactly (337K vs 337K beds) with only 30 incremental entities. The unmatched entity gap is **not recoverable** through a different bed source — those entities (physician offices, ASCs, alliance roll-ups) structurally don't have beds.

### Methodology Adjustment: Alt-Site Multiplier

On top of bed-based hospital purchasing, approximately 10–18% of TSA clinical spend comes from non-bed-bearing entities. For extrapolation:

| Multiplier Scope | Non-Bed Clinical | % of Bed-Matched | Multiplier |
|-----------------|-----------------|-------------------|-----------|
| Excluding alliances (conservative) | $5.1B | 10.4% of $49.3B | **1.10×** |
| Including alliances (upper bound) | $8.8B | 17.9% of $49.3B | **1.18×** |

**Recommended**: Use 1.10× (excluding alliance spend, which represents purchasing cooperatives whose member hospitals' beds are already counted individually in DHC).

### Updated GPO Clinical Extrapolation

| | Old (Session 8b) | Corrected | Change |
|---|---|---|---|
| Per-bed rate | $131K (system-level) | $146K (facility-level) | +11% |
| GPO beds | 194K | 194K | — |
| Bed-based clinical | $25.4B | $28.3B | +$2.9B |
| With alt-site adjustment (×1.10) | — | **$31.1B** | — |
| **Estimated GPO clinical** | $25.4B | **$28–31B** | +$3–6B |

> **Note**: The Section III extrapolation ($57B C+NC addressable via $295K/bed) uses the v4 `parent_service_line` definition, which includes ALL clinical and NC categories. The Section III-A validation above used the v3.2 marker-category definition ($131K→$146K/bed), which is a subset. The two are complementary: Section III provides the comprehensive estimate, while Section III-A validates the per-bed methodology using directly-observable marker categories.

### Conclusion

**The per-bed extrapolation methodology is fundamentally sound.** The 26% Tier 1 gap is entirely explained by:
1. A correctable methodological issue (system vs. facility bed denominator)
2. Structural data features (alliances and alt-site providers that purchase clinical supplies without having beds)

The v4 full-service-line rate ($295K/bed C+NC) supersedes the v3.2 marker-category rate ($160K/bed) as the primary extrapolation input. The marker-category validation here confirms the methodology is reliable.

---

## Section IV: Data Assets

### BigQuery Tables

| Table | Contents |
|-------|---------| 
| `service_line_mapping` | 10 rows — Single source of truth mapping TSA `service_line` → `parent_service_line` (Clinical, Non-Clinical, Pharma, Food) |
| `tsa_cy2025` | 118.7M rows — CY2025 TSA with `parent_service_line` from service_line_mapping JOIN |
| `tsa_cy2025_enriched` | 118.7M rows — tsa_cy2025 + `is_clin_nc_cohort`, `premier_gpo_member` flags |
| `sa_sf_dhc_join_enriched` | 482K rows — Full facility directory with improved `premier_gpo_member_improved` flag |
| `entity_sl_mix` | 18,838 child entity codes with SL proportions (from TSA double-attribution, using service_line_mapping) |
| `vendor_name_patterns` | 153 LIKE-pattern rules for WF name-based classification (priority-ordered, auditable, Dataform-managed) |
| `wf_sl_v4` | 521 systems with distributed SL spend, exclude spend, match rates (uses vendor_name_patterns for fallback layer) |
| `tsa_clin_nc_cohort` | 100 systems with beds, Clinical/NC/total spend |
| `gpo_member_universe` | 868 acute-care GPO member facilities with beds, hospital type, program flags |

*All tables in project `matthew-bossemeyer`, dataset `wt_2026_02_10__portfolio_expansion`.*

### Companion Files

- `comprehensive_cohort_analysis.md` — Detailed tiered cohort analysis with WF calibration and capture ratios
- `per_bed_benchmarks_and_extrapolation.md` — Per-bed benchmarks, GPO membership mapping, extrapolation model
- `dataform/` — Persistent Dataform pipeline (.sqlx files) defining all table builds with a single `service_line_mapping` source of truth

---

## Connection to Portfolio Expansion Initiative

This analysis feeds directly into the **Portfolio Expansion Heat Map** initiative (Bill Marquardt / Bruce, with service line leaders Pam-Clinical, Molly-NC, Justin-Pharma, Joan-Food):

1. **Service line segmentation**: The 100-system cohort enables on/off/non-contract profiling for Clinical and Non-Clinical — the two service lines where TSA has direct contracting visibility
2. **Winnability scoring**: Per-system contract category detail supports identification of off-contract and non-contract spend opportunities
3. **Expected mix benchmarks**: WF-derived SL mix (**~43% Clinical / ~41% NC / ~14% Pharma / ~1–2% Food**, with IQRs) provides the denominator for expressing opportunity as a percentage of total addressable spend — and shows that C+NC represent ~84% of the total envelope
4. **Data timeline alignment**: Jordan Garrett targets data cleanup by 2/13 and winnability framework by 2/27; this cohort and benchmark work provides the analytical foundation

### Next Steps (Recommended)

1. **On/Off/Non-Contract profiling** (Clinical + NC): Use TSA `Contract_Category` × system to classify spend into on-contract (Premier contract), off-contract (competitor contract), and non-contract (no GPO agreement) buckets
2. **Pharma and Food estimation**: Apply WF mix ratios (~14–15% pharma, ~1–2% food) to estimate total envelope; source wholesaler/distributor tracing data for on/off status in these channels
3. **System-level scoring matrix**: Build per-system × per-SL heat map showing opportunity size and winnability
4. **Validate with service line leaders**: Confirm category-to-SL mapping with Pam (Clinical), Molly (NC), Justin (Pharma), Joan (Food)

---


