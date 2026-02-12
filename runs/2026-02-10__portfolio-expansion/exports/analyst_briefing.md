# Portfolio Expansion: Multi-Source Spend Analysis

**From**: Matt Bossemeyer  
**Date**: February 12, 2026  
**Re**: Health System Spend Landscape — Service Line Mix, Cohort Expansion, and Extrapolation Framework

---

## Executive Summary

We have built a **multi-data-source analytical framework** for the Portfolio Expansion initiative, using two complementary Premier datasets:

| Data Source | Role | Systems | Beds | Spend |
|-------------|------|---------|------|-------|
| **Workflow History (WF)** | Establishes expected **service line mix** benchmarks | 521 CY2025 systems (46 balanced 3-SL reporters) | — | $74.5B total |
| **Transaction Analysis (TSA)** | Provides the **addressable Clinical + NC cohort** for on/off/non-contract profiling | **100 systems** | **113K** | **$89B total** |

### Analysis Scope

This analysis focuses on **health system and hospital purchasing** — the spend that flows through health system ERPs where Premier has data visibility. Both WF and TSA are sourced from health system ERP data. Some non-acute volume appears (facilities owned, leased, or managed by the health system that share the same ERP), but the overwhelming majority of spend reflects acute-care hospital operations.

**What is NOT in scope**: Independent non-acute and alternate-site facilities (retail pharmacies, specialty pharmacies, infusion centers, mail-order pharmacies, physician offices, ambulatory surgery centers not owned by a health system, etc.) that order directly through wholesaler/distributor platforms outside health system ERPs. This is an enormous market — CY2025 pharmaceutical wholesaler tracings show **$123B in non-acute/alternate-site pharma volume alone**, essentially as large as the entire GPO acute estimate presented here. The Portfolio Expansion initiative may eventually address portions of this market, but the current analytical framework does not cover it.

### Why two sources, and why Clinical + Non-Clinical only for TSA?

**Pharma and food purchasing flows through wholesalers and distributors** (McKesson, Cardinal, Sysco, US Foods). The invoices Premier sees in WF are simply not detailed enough to distinguish on-contract vs. off-contract for these channels — wholesaler/distributor invoices are typically large monthly aggregates covering a broad collection of products purchased, and even line-level detail lacks the granularity to identify specific drugs or food products consumed. WF invoice data *can* establish the expected proportion of pharma and food spending relative to clinical and NC — giving us a benchmark service line mix — but for on/off/non-contract analysis in pharma and food, we must rely on **wholesaler and distributor sales tracings**, which provide product-level detail. TSA cohort selection therefore narrows to Clinical + Non-Clinical, where Premier has direct contracting visibility and on/off/non-contract status is determinable.

This reframing **more than triples the qualifying cohort** (from 31 systems requiring 3+ SLs to 100 systems with comprehensive Clinical + NC reporting), while maintaining analytical rigor.

### Key Findings

1. **WF Service Line Mix** (entity-bridge classification, balanced 3-SL reporters, 42 systems, $54.9B classified):
   - Clinical: **~43%** (IQR 34–51%) | Non-Clinical: **~41%** (IQR 26–46%) | Pharma: **~14%** (IQR 6–27%) | Food: **~1–2%**
   - Clinical and NC are roughly balanced at ~43%/41% across cohort definitions
   - TSA external cross-check: Pharma = 18.6% of $133.5B TSA CY2025 mapped spend — consistent with our WF-derived 14–17% range

2. **TSA Clinical+NC Cohort**: **100 health systems**, 113K hospital-only beds, $89B total TSA spend
   - Clinical spend: $42.0B | NC spend: $34.5B
   - Within addressable (Clinical+NC): **55% Clinical / 45% NC**
   - Per-bed: $360K Clinical + $291K NC = **$652K addressable per bed**
   - 25 systems ≥$1B, 19 at $500M–$1B, 38 at $100M–$500M
   - **Spend coverage**: The cohort's $42B clinical spend represents **~80% of all GPO-observed clinical** ($52B) — a highly representative sample for extrapolating on/off/non-contract findings to the full membership

3. **GPO Membership Extrapolation**: Premier's GPO membership universe — **1,775 acute-care hospital facilities, 224K staffed beds** (~27% of ~6,500 US acute-care hospitals, consistent with Premier's known GPO market share) — represents an estimated **$122B–$132B in total non-labor purchasing**. These volume targets tell us how much spend to look for in each detailed feed:

   | Service Line | Estimated GPO Range | Detailed Feed for On/Off/Non-Contract |
   |-------------|--------------------|-----------------------------------------|
   | **Clinical** | **$52B–$57B** | TSA (100-system cohort) |
   | **Non-Clinical** | **$50B–$54B** | TSA (100-system cohort) |
   | **Pharma** | **$18B–$19B** | Pharmaceutical wholesaler tracings |
   | **Food** | **$1.8B–$2B** | Distributor tracings |
   | **Total** | **$122B–$132B** | — |

   - *Range basis*: Lower bound = TSA-observed GPO clinical ($52.2B) as floor (since observed data already exceeds the median-rate projection), scaled to total via WF mix ($122B); upper bound = 8% non-reporting assumption ($132B). See Section III for full methodology.

4. **NC analysis-ready**: These 100 systems comprehensively report both Clinical AND Non-Clinical in the TSA. The existing Clinical on/off/non-contract dashboard (Jenny/Brian's team) can be **extended to Non-Clinical immediately** for this cohort — no new data sourcing required. Once Jordan Garrett delivers the catch-all category breakdowns, we can decompose NC subcategories for detailed opportunity sizing.

---

## Section I: WF Service Line Mix Benchmarks

### Methodology: Entity-Bridge Hybrid Classification

We classified CY2025 WF invoice spend across 521 health systems using a two-layer approach:

1. **Primary — Entity-code bridge (79% of spend)**: Each WF invoice has a `vendor_entity_code`. We matched these to TSA's 18,838 child entity codes, where each entity has a known service line mix derived from TSA's `Contract_Category` classifications. Invoice amounts are then distributed proportionally across the four service lines based on that entity's TSA-derived mix. This approach uses **double-attribution** (both `Vendor_Entity_Code` and `Manufacturer_Entity_Code` from TSA) and applies at the **child entity level** (not top-parent), so that the same parent company (e.g., Cardinal Health) is correctly split: OH5010 (med-surg) → 81% clinical, 682446 (drug distribution) → 90% pharma.

2. **Fallback — Name-pattern rules (4.5% of spend)**: For invoices without a matching entity code, we apply vendor-name LIKE patterns from a persistent `vendor_name_patterns` reference table (200 patterns, priority-ordered by service line band). The pattern table assigns 100% of the invoice to a single SL based on vendor type (e.g., PBM → pharma, construction → NC, anesthesia groups → clinical, Fisher Scientific → clinical). Priority bands ensure pharma-specific patterns (Nuclear Pharmacy, 340B, Specialty Pharmacy, McKesson Drug/Spec/Rx) fire before broader distributor catch-all rules. The pattern table is a Dataform-managed asset — adding or modifying rules requires editing only `vendor_name_patterns.sqlx`, not the classification query.

3. **Exclude identification (2.4% of spend)**: The pattern table also identifies non-addressable spend — taxes (IRS), insurance claims (Aetna, BCBS, Cigna), retirement/investment (Fidelity, Vanguard, VOYA, TIAA), payroll, banking, intercompany transfers, placeholder vendors, government remittances (State Comptroller, Healthcare & Family Services), ASO/benefits funds, and one-time pass-through entries — and removes it from the addressable denominator.

| Classification Layer | WF CY2025 Spend | Share of Total |
|---------------------|----------------|----------------|
| Entity-bridge classified | $58.9B | 79.1% |
| Name-pattern classified (SL) | $3.9B | 5.2% |
| Name-pattern identified (EXCLUDE) | $1.8B | 2.4% |
| Unmatched (residual) | $9.9B | 13.3% |
| **Total** | **$74.5B** | 100% |

This approach achieves an **~87% addressable classification rate** across $74.5B in CY2025 WF spend. The entity-bridge method is critical for multi-SL distributors: a naive vendor-name approach would assign all Cardinal Health or McKesson invoices to a single SL, when in reality these companies have distinct child entities (e.g., Cardinal OH5010 = 81% clinical med-surg, Cardinal 682446 = 90% pharma drug distribution). Operating at the child-entity level correctly splits this spend.

### Benchmark Service Line Mix — Ranges & Confidence Intervals

We present benchmarks as **ranges** rather than point estimates, reflecting genuine system-to-system variation and sensitivity to cohort selection. The primary cohort is the **3-SL balanced** set (42 systems), which requires ≥1% in Clinical, NC, and Pharma but does not impose a food floor — avoiding the selection bias that the ≥1% food requirement introduces (it drops systems and preferentially removes higher-pharma systems).

#### Central Estimates (Spend-Weighted, by Cohort)

| Cohort | N | Classified | Clinical | NC | Pharma | Food |
|--------|---|-----------|----------|----|--------|------|
| **3-SL balanced ≥$200M** (primary) | **42** | **$54.9B** | **42.8%** | **41.3%** | **14.4%** | **1.5%** |
| 3-SL balanced ≥$100M | 55 | $56.7B | 42.9% | 41.1% | 14.5% | 1.5% |
| 4-SL food≥0.5% ≥$200M | 33 | $49.7B | 41.6% | 43.5% | 13.4% | 1.6% |
| 4-SL food≥1% ≥$200M | 22 | $26.9B | 43.1% | 43.6% | 10.9% | 2.4% |
| All ≥$50M, ≥70% match | 77 | $59.9B | 42.1% | 39.6% | 16.8% | 1.5% |
| 3-SL balanced ≥$50M | 83 | $58.9B | 43.4% | 40.7% | 14.4% | 1.5% |

**3-SL balanced definition**: Systems with ≥$200M classified spend, ≥70% addressable match rate, and ≥1% of classified spend in Clinical, NC, and Pharma.

#### System-Level Distribution (Primary 42-System Cohort, Unweighted)

| Service Line | Min | P10 | P25 | Median | Mean | P75 | P90 | Max |
|-------------|-----|-----|-----|--------|------|-----|-----|-----|
| **Clinical** | 16.2% | 27.1% | 34.4% | 44.2% | 45.0% | 51.4% | 63.6% | 95.3% |
| **NC** | 1.3% | 4.0% | 23.3% | 34.4% | 32.8% | 45.1% | 51.3% | 62.4% |
| **Pharma** | 1.5% | 4.6% | 6.8% | 10.8% | 20.7% | 29.3% | 53.4% | 71.6% |
| **Food** | 0.0% | 0.3% | 0.6% | 1.0% | 1.5% | 2.0% | 3.1% | 7.7% |

#### Recommended Presentation Ranges

| Service Line | Central Estimate | IQR (System-Level) | Cross-Cohort Range | External Check (TSA) |
|-------------|-----------------|--------------------|--------------------|---------------------|
| **Clinical** | ~43% | 34–51% | 42–43% | 43% (parent_service_line) |
| **NC** | ~41% | 23–45% | 40–44% | 37% (parent_service_line) |
| **Pharma** | ~14% | 7–29% | 11–17% | **18.6%** |
| **Food** | ~1–2% | 0.6–2.0% | 1.5–2.4% | 1.1% |

> **TSA cross-check**: TSA Pharmacy = **18.6%** of $133.5B CY2025 mapped spend, consistent with our WF-derived 14–17% range (the range widens to include higher-pharma cohort definitions). TSA uses `service_line` → `parent_service_line` via the same mapping table as WF, so the Clinical and NC comparisons are directly aligned.

**Key observations**:
- **Clinical and NC are roughly balanced** (~43%/41%) across all cohort definitions
- **Pharma is ~14% in the primary cohort** (weighted); system-level median is 10.8% with wide IQR (7–29%), reflecting genuine variation in how much pharma flows through WF vs. direct wholesaler channels. The strict 4-SL food≥1% cohort depresses pharma to 10.9% due to selection bias (food-floor drops pharma-heavy systems)
- **TSA pharma cross-check validates**: TSA Pharmacy = 18.6% on $133.5B mapped spend; our 14.4% weighted central falls within range given different scope (WF captures invoices routed through ERP, TSA captures contract-specific transactional data)
- **NC at ~41%** is stable across all cuts (40–44%), reflecting the inclusion of PURCHASED SERVICES, FACILITIES, and IT/DIGITAL HEALTH categories
- **Food at ~1–2%** is structurally small in WF; the 4-SL cohort inflates it to 2.4% by definition (food floor = 1%)
- **System-level variation is substantial**: Pharma ranges from 1.5% to 71.6% across the 42-system cohort, driven by differences in ERP capture (some systems route all pharma through wholesaler-direct channels not visible in WF)

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

The ~13% residual unmatched spend ($9.9B) is predominantly a long tail of small, nondescript vendors (84K+ distinct names). Pattern-based classification (200 `vendor_name_patterns` rules) reclassified identifiable vendor types:

- **Recovered → NC ($704M):** McKesson Technology ($277M), locum tenens ($137M), Deloitte/KPMG/Accenture ($167M), Siemens Industry ($41M), MedStaff ($42M), NTT Data ($24M), janitorial ($16M)
- **Recovered → Food ($453M):** US Foods ($287M), Pepsi ($51M), Aramark ($45M), Compass Group ($38M), Sysco ($26M), Coca-Cola ($6M)
- **Recovered → Clinical ($223M):** Renal care ($77M), Fisher Scientific ($63M), laboratory vendors ($60M), dialysis ($21M)
- **Recovered → Pharma ($34M):** RxBenefits ($31M), pharmacy benefit managers ($3M)
- **Recovered → Exclude ($26M):** Comptroller/government entities

**Additional pattern recoveries (~$0.8B):** 47 patterns targeting top unmatched vendors by dollar volume. Key additions: benefits funds/trusts/insurance claims → Exclude (~$0.3B); consulting/advertising/revenue cycle/environmental services → NC; rehabilitation/ambulance/medical gas/blood centers/pathology/organ procurement/DaVita → Clinical; Pfizer/Sanofi/Morris & Dickson → Pharma. Cumulative pattern-based recovery totals ~$2.2B.

Note: Major PBMs (OptumRx $190M, Express Scripts $15M) and food service providers (Sodexo $140M) were already classified via the entity-bridge layer, not name patterns. Scenario analysis shows the benchmark remains robust:

| Scenario | Clinical | NC | Pharma | Food |
|----------|----------|----|--------|------|
| Matched only (current) | 43.0% | 38.8% | 16.7% | 1.5% |
| Estimated actual unmatched mix | ~41% | ~40% | ~16% | ~2% |
| Extreme: all unmatched = pharma | ~37% | ~33% | ~29% | ~1% |

Uncertainty band: ±2–3pp on each SL from unmatched spend.

### Implications for Extrapolation

For any system where you know the Clinical + NC spend from TSA, you can estimate total non-labor purchasing:
- If Clinical + NC = **~84%** of total (per primary benchmark: 42.8% + 41.3%), then total ≈ Clinical+NC / 0.84
- Pharma ≈ total × 0.14–0.15 (range: 0.11–0.17 across cohort definitions)
- Food ≈ total × 0.01–0.02

These ratios should be applied **directionally** — individual system mix varies substantially (pharma IQR: 6–27%).

---

## Section II: TSA Clinical + Non-Clinical Cohort

### Qualification Criteria

A system qualifies if it reports:
- **Clinical spend ≥$10M** across all `parent_service_line = 'Clinical'` categories (maps from TSA `service_line` values: PPI, NURSING, SURGICAL, DIAGNOSTICS, DISTRIBUTION via `service_line_mapping`)
- **NC spend ≥$10M** across all `parent_service_line = 'Non-Clinical'` categories (maps from: PURCHASED SERVICES, FACILITIES, IT/DIGITAL HEALTH)
- **≥5 distinct clinical contract categories** with spend (breadth check)
- **≥5 distinct NC contract categories** with spend (breadth check)

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
| Systems with bed match | 93 (93%) |
| Total staffed beds (hospital-only) | 113,205 |
| Total TSA spend | $89.0B |
| Clinical spend (parent_service_line) | $42.0B |
| NC spend (parent_service_line) | $34.5B |
| Addressable (Clinical+NC) | $76.5B |
| Clinical share of addressable | 55% |
| NC share of addressable | 45% |
| Wtd avg Clinical per bed | **$360K** |
| Wtd avg NC per bed | **$291K** |
| Wtd avg addressable per bed | **$652K** |

> **Methodology note**: Health System parent rows in the DHC facility directory carry aggregate bed counts that duplicate their child hospitals' beds. All bed calculations use hospital-level rows only (excluding `dhc_hospital_type = 'Health System'`), ensuring beds are counted once.

### Size Distribution

| Tier | Systems | Beds |
|------|---------|------|
| ≥$1B total TSA spend | 25 | 70K |
| $500M–$1B | 19 | 17K |
| $100M–$500M | 38 | 21K |
| <$100M | 18 | 4K |

### Top 25 Systems by Total Spend

| System | Entity Code | Spend ($M) | Clin ($M) | NC ($M) | Beds | $/bed (K) |
|--------|-------------|-----------|----------|---------|------|-----------|
| ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE | AQ9425 | 17,603 | 7,921 | 7,491 | 11,343 | 1,359 |
| UPMC HEALTH SYSTEM | 743692 | 5,341 | 1,802 | 3,103 | 4,471 | 1,097 |
| MCLAREN HEALTH CARE | MI2002 | 3,726 | 594 | 2,485 | 1,826 | 1,686 |
| ADVENTHEALTH | FL0343 | 3,720 | 2,845 | 666 | 9,247 | 380 |
| WEST VIRGINIA UNITED HEALTH SYSTEM | WV0541 | 3,663 | 1,476 | 1,486 | 2,522 | 1,175 |
| TEXAS HEALTH RESOURCES | TX2246 | 3,443 | 1,878 | 1,220 | 6,763 | 458 |
| PRISMA HEALTH | AI6913 | 2,905 | 913 | 1,176 | 2,276 | 918 |
| OREGON HEALTH SCIENCES UNIVERSITY | OR2023 | 1,969 | 335 | 493 | 0 | — |
| UVA HEALTH SYSTEM | VA0019 | 1,959 | 576 | 602 | 206 | 5,718 |
| UNIVERSITY HEALTH SYSTEM | TX0488 | 1,691 | 433 | 989 | 779 | 1,825 |
| HONORHEALTH | 649419 | 1,558 | 746 | 731 | 1,654 | 893 |
| FAIRVIEW HEALTH SERVICES | MN2013 | 1,465 | 731 | 285 | 2,035 | 499 |
| BANNER HEALTH | AZ2090 | 1,426 | 1,246 | 108 | 5,767 | 235 |
| BAPTIST HEALTHCARE SYSTEM | KY0074 | 1,402 | 698 | 471 | 1,952 | 599 |
| CHILDREN'S HOSPITAL CORPORATION | 847014 | 1,400 | 330 | 536 | 572 | 1,513 |
| UNIVERSITY OF CALIFORNIA - IRVINE | CA3550 | 1,312 | 381 | 428 | 911 | 888 |
| ST LUKE'S UNIVERSITY HEALTH NETWORK | PA0023 | 1,294 | 560 | 630 | 1,742 | 683 |
| SOUTH BROWARD HOSPITAL DISTRICT | FL0085 | 1,226 | 407 | 743 | 1,818 | 633 |
| UHS OF DELAWARE, INC. | 718653 | 1,205 | 1,727 | 19 | 6,438 | 271 |
| ECU HEALTH | 714757 | 1,186 | 385 | 379 | 1,367 | 559 |
| PEACEHEALTH | WA0014 | 1,181 | 439 | 487 | 1,344 | 689 |
| HEALTH FIRST SHARED SERVICES, INC | 712579 | 1,116 | 280 | 613 | 918 | 972 |
| BAYSTATE HEALTH INC. | MA2022 | 1,070 | 548 | 459 | 921 | 1,093 |
| MTWY HEALTH | AW6643 | 1,024 | 416 | 532 | 917 | 1,035 |
| OSF HEALTHCARE SYSTEM | IL5043 | 1,000 | 673 | 306 | 2,535 | 386 |

> **Note**: Systems like OHSU and UVA show near-zero hospital-only beds because their TSA entity codes map to academic medical centers/corporate offices rather than DHC-catalogued hospital campuses.

*Full 100-system list persisted in BigQuery table `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion.tsa_clin_nc_cohort`.*

---

## Section III: Extrapolation to GPO Membership

This section bridges from the 100-system TSA cohort (Section II) to an estimate of total non-labor purchasing across Premier's full GPO membership. We use two complementary approaches — a per-bed extrapolation and a TSA-calibrated anchor — to produce a **defensible range** rather than a single point estimate.

### Approach A: Per-Bed Extrapolation

**Step 1 — Empirical per-bed rate** from the TSA cohort (93 bed-matched systems, 113K beds):

| Metric | Clinical | NC | Addressable (C+NC) |
|--------|----------|----|--------------------|
| Weighted avg $/bed | **$360K** | **$291K** | **$652K** |
| Median $/bed | — | — | **$418K** |

This rate covers all contract categories under `parent_service_line` = 'Clinical' or 'Non-Clinical' — every category where Premier has direct contracting visibility. It does not include pharma or food.

**Step 2 — GPO membership universe** (see Section II for full definition):

| GPO Universe | Hospitals | Beds |
|-------------|-----------|------|
| Short Term Acute Care Hospital | 1,157 | 202,265 |
| Critical Access Hospital | 550 | 11,615 |
| Childrens Hospital | 68 | 10,221 |
| **Total** | **1,775** | **224,101** |

> *94 facilities have NULL beds in DHC; counted in facility total but excluded from bed-based extrapolation.*

1,775 hospitals represents **~27% of ~6,500 US acute-care hospitals**, consistent with Premier's known GPO market share.

The TSA cohort covers **50.5%** of GPO member beds (113K of 224K) and **~80% of GPO clinical spend** ($42B of $52B observed) — a strong empirical foundation.

**Step 3 — WF mix multiplier**: The WF-derived SL mix (Section I) tells us Clinical+NC represent **~84%** of total non-labor (43.1% + 41.0%). Scaling from C+NC to the full envelope:

| Rate Basis | C+NC per bed | × 224K beds → C+NC | ÷ 0.84 → Total Non-Labor |
|-----------|-------------|---------------------|--------------------------|
| Mean rate | $652K | $146B | **$174B** |
| Median rate | $418K | $94B | **$111B** |
| P25 rate | $334K | $75B | **$89B** |
| P75 rate | $893K | $200B | **$238B** |

The cohort's 100 systems are disproportionately large academic medical centers and multi-hospital systems with high purchasing intensity per bed. Given that ~1,100 of the 1,775 GPO hospitals are community hospitals and CAHs, the **mean-rate estimate ($174B) likely overstates the GPO total**. The median ($111B) is more representative of the full universe.

### Approach B: TSA-Calibrated Anchor (Recommended)

Rather than relying solely on per-bed extrapolation, we can anchor on **what TSA actually observes**. TSA clinical reporting is near-comprehensive for GPO members (estimated 92–95% coverage) because Premier's supply chain analytics tools create strong incentive to submit clinical purchasing data for contract savings analysis.

**TSA-Observed GPO Spend by Service Line** (`tsa_cy2025_enriched`, `premier_gpo_member = TRUE`):

| Service Line | TSA Observed | Share |
|-------------|-------------|-------|
| **Clinical** | **$52.2B** | 43.9% |
| Non-Clinical | $44.6B | 37.5% |
| Pharma | $20.8B | 17.5% |
| Food | $1.3B | 1.1% |
| Unmapped (NULL) | $1.0B | 0.9% |
| **Total** | **$119.9B** | 100% |

**Calibration check**: The mean-rate extrapolation ($74.5B clinical) overshoots TSA-observed clinical ($52.2B) by **43%**, confirming cohort composition bias. The median-rate extrapolation ($47.7B) falls slightly below observed — consistent with it not capturing non-reporting facilities.

Using Clinical as the anchor (highest reporting completeness) and scaling via WF mix (Clinical = ~42.8% of total):

| Scenario | Est. Clinical | → Total Non-Labor | → C+NC | Implied $/bed |
|----------|--------------|-------------------|--------|---------------|
| TSA observed (floor) | $52.2B | $121.9B | $102.5B | $457K |
| **5% non-reporting** | **$54.9B** | **$128.3B** | **$107.9B** | **$481K** |
| 8% non-reporting | $56.7B | $132.5B | $111.4B | $497K |

The effective GPO-wide per-bed rate is **~$481K** (C+NC), sitting between the cohort median ($418K) and mean ($652K).

**Cross-validation — TSA-observed NC**: GPO NC observed = $44.6B. At 92–95% reporting coverage, implied true NC = $47–49B, somewhat below our WF-inferred $53B but within ~10%. This minor gap likely reflects slightly lower NC reporting completeness (PURCHASED SERVICES and FACILITIES categories may be less systematically submitted than med-surg supply transactions).

### Recommended Estimates

| Service Line | Estimated GPO Range | Recommended (5% non-reporting) | Detailed Feed for On/Off Analysis |
|-------------|--------------------|---------------------------------|------------------------------------|
| **Clinical** | **$52B–$57B** | **$55B** | TSA (100-system cohort) |
| **Non-Clinical** | **$50B–$54B** | **$53B** | TSA (100-system cohort) |
| **Pharma** | **$18B–$19B** | **$18B** | Pharmaceutical wholesaler tracings |
| **Food** | **$1.8B–$2B** | **$1.9B** | Distributor tracings |
| **Total Non-Labor** | **$122B–$132B** | **$128B** | — |

> **Interpretation**: These are estimates of what Premier GPO members spend in each service line across their total non-labor purchasing — not what flows through Premier contracts. The gap between this total and Premier's contracted volume is the opportunity the Portfolio Expansion Heat Map is designed to quantify.

> **Caveat on pharma and food**: The pharma estimate reflects only GPO-addressable pharma purchasing visible in WF invoices. Wholesaler-direct channels, 340B carve-outs, and specialty pharmacy flows are not captured — actual pharma spend is likely higher. Similarly, food is a structural undercount relative to industry benchmarks (3–5% of operating expenses).

> **Pharma wholesaler tracing cross-check**: CY2025 pharmaceutical wholesaler tracings show **$21.5B in acute-facility pharma volume** — slightly above our GPO extrapolation of $18B–$19B. The modest overshoot is expected: some acute-care hospitals participate in Premier's pharmacy purchasing program without being part of the core clinical GPO, so wholesaler tracings capture a somewhat broader acute footprint than our GPO-member-only model. This validates that our pharma estimate is in the right ballpark for the GPO membership. (For context: the same tracings show $123B in non-acute/alternate-site pharma — see Analysis Scope above.)

### Why Ranges Matter

| Method | Total Non-Labor | Basis |
|--------|----------------|-------|
| Per-bed mean-rate | $174B | Cohort average — biased high (AMCs, large systems) |
| Per-bed median-rate | $111B | Less sensitive to outliers |
| **TSA-calibrated (5%)** | **$128B** | **Anchored on observed clinical; recommended** |
| TSA-calibrated (8%) | $132B | Upper bound on non-reporting |
| TSA observed floor | $122B | Zero non-reporting assumption |
| P25–P75 per-bed range | $89B–$238B | Full system-level variation |

The TSA-calibrated estimate ($128B) is our recommended central figure. It sidesteps cohort composition bias by anchoring on directly observed clinical volume, then scaling via WF mix. The **$122B–$132B range** (TSA-observed floor through 8% non-reporting) brackets the most defensible estimates. The median-rate per-bed extrapolation ($111B) falls slightly below this range because the median is depressed by systems with incomplete TSA reporting.

### For Portfolio Expansion Heat Map Purposes

- **Clinical + NC represent ~84% of total non-labor purchasing**, making them the directly addressable service lines for TSA profiling and the overwhelming majority of the spend envelope
- **Pharma (~14%) and Food (~1–2%)** are comparatively small at the GPO-purchasable level; much of what flows through wholesaler entities like Cardinal and McKesson is actually med-surg supply chain rather than pharma distribution
- The 100-system cohort provides the foundation for the service-line-by-system scoring matrix

---

## Connection to Portfolio Expansion Initiative

This analysis feeds directly into the **Portfolio Expansion Heat Map** initiative (Bill Marquardt / Bruce, with service line leaders Pam-Clinical, Molly-NC, Justin-Pharma, Joan-Food).

### What we now know

We have established the **total GPO purchasing volume by service line** — the benchmark against which detailed-feed analysis will measure coverage and identify opportunity:

| Service Line | Estimated GPO Range | Detailed Feed | On/Off/Non-Contract Path |
|-------------|--------------------|--------------|--------------------------| 
| **Clinical** | **$52B–$57B** | TSA | 100-system cohort; existing dashboard (Jenny/Brian) |
| **Non-Clinical** | **$50B–$54B** | TSA | 100-system cohort; extend Clinical dashboard to NC |
| **Pharma** | **$18B–$19B** | Pharmaceutical wholesaler tracings | Wholesaler/distributor tracing data |
| **Food** | **$1.8B–$2B** | Distributor tracings | Distributor tracing data |
| **Total** | **$122B–$132B** | — | — |

These ranges tell us how much total volume to look for when we dive into each detailed feed. The gap between observed Premier-contracted volume and these totals is the addressable opportunity.

### What we can do next

1. **Extend TSA on/off/non-contract to Non-Clinical** (immediate): The 100 cohort systems comprehensively report both C and NC. The existing Clinical dashboard framework can be expanded to NC service line categories. Once Jordan Garrett delivers the catch-all category breakdowns (target: 2/13), we can decompose NC subcategories for detailed opportunity sizing.
2. **Pharma and Food volume sizing**: Apply WF mix ratios to estimate the GPO envelope; source wholesaler/distributor tracing data to establish on/off/non-contract status in these channels.
3. **System-level scoring matrix**: Build per-system × per-SL heat map showing opportunity size and winnability.
4. **Validate with service line leaders**: Confirm category-to-SL mapping with Pam (Clinical), Molly (NC), Justin (Pharma), Joan (Food).

---

## Appendix: Data Assets

### BigQuery Tables

| Table | Contents |
|-------|---------| 
| `service_line_mapping` | 10 rows — Single source of truth mapping TSA `service_line` → `parent_service_line` (Clinical, Non-Clinical, Pharma, Food) |
| `tsa_cy2025` | 118.7M rows — CY2025 TSA with `parent_service_line` from service_line_mapping JOIN |
| `tsa_cy2025_enriched` | 118.7M rows — tsa_cy2025 + `is_clin_nc_cohort`, `premier_gpo_member` flags |
| `sa_sf_dhc_join_enriched` | 482K rows — Full facility directory with improved `premier_gpo_member_improved` flag |
| `entity_sl_mix` | 18,838 child entity codes with SL proportions (from TSA double-attribution, using service_line_mapping) |
| `vendor_name_patterns` | 200 LIKE-pattern rules for WF name-based classification (priority-ordered, auditable, Dataform-managed) |
| `wf_sl_v4` | 521 systems with distributed SL spend, exclude spend, match rates (uses vendor_name_patterns for fallback layer) |
| `tsa_clin_nc_cohort` | 100 systems with hospital-only beds, Clinical/NC/total spend |
| `gpo_member_universe` | 1,775 acute-care GPO member hospital facilities (STAC, CAH, Children's) with beds, hospital type, program flags |

*All tables in project `matthew-bossemeyer`, dataset `wt_2026_02_10__portfolio_expansion`.*

### Companion Files

- `comprehensive_cohort_analysis.md` — Detailed tiered cohort analysis with WF calibration and capture ratios
- `per_bed_benchmarks_and_extrapolation.md` — Per-bed benchmarks, GPO membership mapping, extrapolation model
- `dataform/` — Persistent Dataform pipeline (.sqlx files) defining all table builds with a single `service_line_mapping` source of truth
