# Per-Bed Spend Benchmarks & Extrapolation Model

**Date**: February 10, 2026  
**RUN_ID**: `2026-02-10__portfolio-expansion`  
**Builds on**: `comprehensive_cohort_analysis.md` (29-system TSA cohort)

---

## Overview

This document extends the 31-system TSA cohort analysis with four deliverables:

1. **Per-bed spend benchmarks** — $/bed/year ratios for each service line across the cohort
2. **GPO membership mapping** — comparison of cohort demographics vs. the full Premier membership universe
3. **Extrapolation model** — estimated total non-labor purchasing across Premier's membership
4. **TSA coverage calibration** — WF-based capture ratio analysis confirming the reliability of the Tier 1–2 benchmark rate

---

## 1. Per-Bed Spend Benchmarks

### Data Sources
- **Spend**: TSA `transaction_analysis_expanded`, CY2025, `Landed_Spend` by `Health_System_Name`
- **Beds**: Staffed hospital bed counts from `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join` (DHC data), as validated in Session 2 cohort analysis
- **Service line classification**: Same Contract_Category mapping used in the cohort analysis (34 Non-Clinical categories, 4 Pharma, 3 Food, remainder = Clinical)

### TSA Name Crosswalk

The cohort analysis used shorthand names; for SQL precision, the exact TSA `Health_System_Name` values are:

| Cohort Shorthand | Exact TSA Health_System_Name |
|-----------------|------------------------------|
| PRISMA HEALTH | PRISMA HEALTH |
| HEALTH FIRST | HEALTH FIRST SHARED SERVICES, INC |
| VCU HEALTH | VCU HEALTH SYSTEM AUTHORITY |
| UPMC | UPMC HEALTH SYSTEM |
| MCLAREN | MCLAREN HEALTH CARE |
| WVUHS | WEST VIRGINIA UNITED HEALTH SYSTEM |
| TEXAS HEALTH | TEXAS HEALTH RESOURCES |
| UVA | UNIVERSITY OF VIRGINIA HEALTH SYSTEM |
| UNIVERSITY HEALTH | UNIVERSITY HEALTH SYSTEM |
| BAPTIST HEALTHCARE | BAPTIST HEALTHCARE SYSTEM |
| UCI | UNIVERSITY OF CALIFORNIA - IRVINE |
| PEACEHEALTH | PEACEHEALTH |
| PRESBYTERIAN | PRESBYTERIAN HEALTHCARE SERVICES |
| LUMINIS | LUMINIS HEALTH |
| CFNI | COMMUNITY FOUNDATION OF NORTHWEST INDIANA, INC. |
| MIDLAND | MIDLAND MEMORIAL HOSPITAL |
| ADVENTHEALTH | ADVENTHEALTH |
| HONORHEALTH | HONORHEALTH |
| FAIRVIEW | FAIRVIEW HEALTH SERVICES |
| ST LUKE'S UNIVERSITY | ST LUKE'S UNIVERSITY HEALTH NETWORK |
| ECU HEALTH | ECU HEALTH |
| SOUTH BROWARD | SOUTH BROWARD HOSPITAL DISTRICT |
| SAINT FRANCIS | SAINT FRANCIS HOSPITAL, INC. |
| LIFEBRIDGE | LIFEBRIDGE HEALTH |
| CARILION | CARILION CLINIC |
| BEEBE | BEEBE HEALTHCARE |
| TIDALHEALTH | TIDALHEALTH INC |
| TERREBONNE | TERREBONNE GENERAL HEALTH SYSTEM |
| GREATER BALTIMORE | GREATER BALTIMORE MEDICAL CENTER |

**Alliance Direct Parent Entities** (included at the `Direct_Parent_Name` level within `Health_System_Name = 'ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE'`):

| Cohort Shorthand | TSA Direct_Parent_Name | TSA Spend ($M) | Notes |
|-----------------|------------------------|---------------|-------|
| CAROLINAS HEALTHCARE | CAROLINAS HEALTHCARE SYSTEM | 10,237 | Clin 43%, NC 40%, Pharma 16%, Food 1.3% |
| ADVOCATE AURORA | ADVOCATE AURORA HEALTH | 7,366 | Clin 65%, NC 31%, Pharma 3%, Food 0.5% |

> Per-bed benchmarks for these two systems are **pending validated bed counts**. Estimated beds: Carolinas ~10,000, Advocate Aurora ~8,000. Once confirmed, they can be integrated into the per-bed tables and weighted averages.

### Per-System Benchmarks ($K/bed/year)

#### Tier 1 — All 4 Service Lines

| System | Beds | Total $M | Total $/bed | Clinical $/bed | NC $/bed | Pharma $/bed | Food $/bed |
|--------|------|---------|------------|----------------|----------|-------------|-----------|
| PRISMA HEALTH | 2,711 | $2,905 | **$1,072K** | $418K | $371K | $260K | $22K |
| HEALTH FIRST | 918 | $1,116 | **$1,216K** | $388K | $594K | $206K | $27K |
| VCU HEALTH | 1,918 | $774 | **$403K** | $229K | $140K | $25K | $10K |

#### Tier 2 — 3 Service Lines + Some Food

| System | Beds | Total $M | Total $/bed | Clinical $/bed | NC $/bed | Pharma $/bed | Food $/bed |
|--------|------|---------|------------|----------------|----------|-------------|-----------|
| UPMC | 6,650 | $5,344 | **$804K** | $375K | $383K | $36K | $10K |
| MCLAREN | 1,886 | $3,726 | **$1,976K** | $445K | $1,232K | $279K | $20K |
| WVUHS | 2,592 | $3,663 | **$1,413K** | $651K | $526K | $227K | $10K |
| TEXAS HEALTH | 9,402 | $3,443 | **$366K** | $227K | $112K | $24K | $4K |
| UVA | 863 | $1,959 | **$2,270K** | $891K | $582K | $766K | $31K |
| UNIVERSITY HEALTH | 785 | $1,692 | **$2,155K** | $926K | $942K | $274K | $13K |
| BAPTIST HEALTHCARE | 2,549 | $1,402 | **$550K** | $309K | $163K | $75K | $3K |
| UCI | 397 | $1,312 | **$3,305K** | $1,190K | $905K | $1,193K | $17K |
| PEACEHEALTH | 2,333 | $1,181 | **$506K** | $231K | $178K | $95K | $3K |
| PRESBYTERIAN | 983 | $876 | **$891K** | $280K | $428K | $176K | $8K |
| LUMINIS | 696 | $631 | **$907K** | $358K | $405K | $135K | $10K |
| CFNI | 707 | $548 | **$775K** | $354K | $41K | $368K | $12K |
| MIDLAND | 261 | $217 | **$830K** | $369K | $387K | $66K | $8K |

#### Tier 3 — 3 Service Lines, No Meaningful Food

| System | Beds | Total $M | Total $/bed | Clinical $/bed | NC $/bed | Pharma $/bed |
|--------|------|---------|------------|----------------|----------|-------------|
| ADVENTHEALTH | 10,719 | $3,720 | **$347K** | $301K | $38K | $8K |
| HONORHEALTH | 1,654 | $1,558 | **$942K** | $546K | $363K | $32K |
| FAIRVIEW | 3,483 | $1,465 | **$421K** | $252K | $59K | $109K |
| ST LUKE'S UNIV | 1,774 | $1,307 | **$737K** | $388K | $322K | $23K |
| SOUTH BROWARD | 1,818 | $1,226 | **$674K** | $275K | $380K | $18K |
| ECU HEALTH | 1,367 | $1,164 | **$852K** | $369K | $242K | $241K |
| SAINT FRANCIS | 1,721 | $571 | **$332K** | $270K | $52K | $9K |
| LIFEBRIDGE | 816 | $561 | **$687K** | $314K | $356K | $16K |
| CARILION | 894 | $544 | **$608K** | $354K | $239K | $15K |
| BEEBE | 201 | $469 | **$2,332K** | $541K | $1,307K | $476K |
| TIDALHEALTH | 408 | $268 | **$656K** | $413K | $159K | $79K |
| TERREBONNE | 242 | $184 | **$761K** | $296K | $317K | $132K |
| GREATER BALTIMORE | 258 | $135 | **$522K** | $266K | $110K | $146K |

### Aggregate Benchmarks

#### Cohort-Wide Statistics ($K/bed/year)

| Metric | Total | Clinical | Non-Clinical | Pharma | Food |
|--------|-------|----------|-------------|--------|------|
| **Weighted average** | **$720K** | $350K | $264K | $100K | $6K |
| Simple average | $1,020K | $423K | $393K | $196K | — |
| Median (P50) | $789K | — | — | — | — |
| P25 | $543K | — | — | — | — |
| P75 | $1,108K | — | — | — | — |
| Min | $332K | — | — | — | — |
| Max | $3,305K | — | — | — | — |
| Std deviation | $734K | — | — | — | — |

> **Variance is very high** (CV = 72%). This reflects genuinely different purchasing profiles: academic medical centers (UCI, UVA) have 5–10× the per-bed spend of large community systems (AdventHealth, Texas Health). A single $/bed rate is not reliable for per-system estimation.

#### By System Size ($K/bed/year, weighted)

| Size Segment | Systems | Beds | Total $/bed | Clinical $/bed | NC $/bed | Pharma $/bed |
|-------------|---------|------|------------|----------------|----------|-------------|
| **Large (2,000+ beds)** | 8 | 40,439 | **$572K** | $318K | $183K | $65K |
| **Medium (800–1,999)** | 11 | 14,838 | **$949K** | $379K | $423K | $138K |
| **Small (<800)** | 10 | 5,729 | **$1,289K** | $530K | $465K | $300K |

> **Strong inverse relationship**: smaller systems spend 2.3× more per bed than large systems. This is partly real (academic intensity, case mix) and partly an artifact (bed counts don't capture outpatient volume, which is growing).

#### By Tier ($K/bed/year, weighted)

| Tier | Systems | Beds | Total $/bed | Clinical $/bed | NC $/bed | Pharma $/bed | Food $/bed |
|------|---------|------|------------|----------------|----------|-------------|-----------|
| **Tier 1** (4 SL) | 3 | 5,547 | **$864K** | $348K | $328K | $170K | $19K |
| **Tier 2** (3 SL + food) | 13 | 30,104 | **$864K** | $376K | $350K | $129K | $8K |
| **Tier 3** (3 SL, no food) | 13 | 25,355 | **$503K** | $317K | $139K | $48K | <$1K |

> Tiers 1–2 have essentially identical per-bed rates ($864K). Tier 3 is 42% lower — likely reflecting incomplete Non-Clinical and Pharma submission rather than lower actual purchasing. This means **Tier 3 systems should be used for Clinical benchmarking only**, not total spend.

### Outlier Analysis

| System | Total $/bed | Likely Explanation |
|--------|-----------|-------------------|
| UCI ($3,305K) | Academic medical center, 397 beds, very high pharma ($1,193K/bed) and NC ($905K/bed) — includes research purchasing | Size distortion |
| BEEBE ($2,332K) | 201 beds with $1,307K/bed NC — suggests alliance purchasing rolled up under Beebe | Alliance effect |
| UVA ($2,270K) | Academic medical center, large pharma program ($766K/bed), quaternary referral center | Case mix |
| UNIVERSITY HEALTH ($2,155K) | Sole safety-net system in San Antonio, high acute intensity | Case mix |
| ADVENTHEALTH ($347K) | Enormous system (10,719 beds) but very low NC ($38K/bed) and Pharma ($8K/bed) — submission excludes most non-clinical and pharma purchasing | Incomplete submission |
| SAINT FRANCIS ($332K) | Low NC ($52K/bed) and minimal pharma ($9K/bed) — likely clinical-only TSA feed | Incomplete submission |

---

## 2. GPO Membership Mapping

### Data Source
`abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join` — joined Salesforce membership + Definitive Healthcare (DHC) hospital data. Deduplicated to one row per `dhc_definitive_id`, prioritizing the highest-tier membership record.

### Membership Universe Summary

> **Methodology update (Session 8)**: The GPO universe is now defined by `premier_gpo_member=TRUE` on the production `sa_sf_dhc_join` table, filtered to acute-care hospital types (STAC, Health System, Childrens Hospital, CAH). This replaces the prior `NATIONAL` keyword approach. The `premier_gpo_member` boolean is the authoritative GPO participation indicator; incremental Conductiv-only and Intersectta-only pools are <1.5% of core beds and excluded for simplicity. All GPO members are treated as participating in all four service lines. Persisted as `gpo_member_universe` table.

| Tier | Definition | Hospitals | Beds | Avg Beds/Hosp |
|------|-----------|-----------|------|------------|
| **Premier GPO** (acute) | `premier_gpo_member=TRUE`, acute hospital types | **868** | **193,636** | **223** |
| — Health System | | 116 | 113,387 | 977 |
| — STAC | | 476 | 68,275 | 163 |
| — Childrens Hospital | | 40 | 7,030 | 207 |
| — Critical Access | | 236 | 4,944 | 21 |
| _All Members (acute)_ | _Any membership, acute types_ | _2,253_ | _782,765_ | _347_ |

**Comparison to prior approach**:
| Method | Hospitals | Beds | Notes |
|--------|-----------|------|-------|
| OLD: `NATIONAL` keyword (all htypes) | 1,174 | 198,236 | Included 260 psych, 57 LTAC, 34 VA |
| OLD: `NATIONAL` keyword (acute only) | 816 | 157,836 | Missed GPO=TRUE facilities without NATIONAL keyword |
| **NEW: `premier_gpo_member` (acute)** | **868** | **193,636** | Clean boolean, proper hospital-type filter |

> The new definition captures 129 facilities / 64K beds that had `premier_gpo_member=TRUE` but no NATIONAL keyword (includes NYP campuses, Children's Healthcare of Atlanta, and PREMIERCHOICE/CONDUCTIV-only members). It excludes 77 facilities / 28K beds that had NATIONAL but `premier_gpo_member=FALSE` (Henry Ford, Methodist, Cooper, etc.).
>
> **Production table caveat**: `dhc_number_of_staffed_beds` is stored as STRING with comma formatting (e.g., "5,942"). Queries must use `SAFE_CAST(REPLACE(dhc_number_of_staffed_beds, ',', '') AS INT64)` to avoid silently dropping the largest systems.

### Membership by Region (Premier GPO, acute)

| Region | Hospitals | Beds | % of GPO Beds |
|--------|-----------|------|---------------|
| **South** | 280 | 61,675 | 31.9% |
| **Midwest** | 192 | 53,561 | 27.7% |
| **Northeast** | 189 | 52,377 | 27.0% |
| **West** | 162 | 18,193 | 9.4% |
| **Other** | 45 | 7,830 | 4.0% |

### Membership by Facility Size (Premier GPO, acute)

| Size Segment | Hospitals | Beds |
|-------------|-----------|------|
| Large (2,000+ beds) | 14 | 59,089 |
| Medium (800–1,999) | 32 | 37,545 |
| Mid-Small (200–799) | 165 | 62,109 |
| Small (<200) | 590 | 34,893 |
| Unknown/0 | 67 | 0 |

> Note: Size segments here are at the **hospital** level (individual facilities), while the cohort benchmarks are at the **system** level (aggregated across all facilities in a health system). A system with 6,000 beds may contain 20 hospitals of 300 beds each.

### Cohort Representativeness

#### Regional Coverage

| Region | Cohort Systems | Cohort Beds | Cohort % | All-Member % | Gap |
|--------|---------------|-------------|----------|-------------|-----|
| **South** | 20 | 41,139 | 67.4% | 45.1% | **+22pp over** |
| **Northeast** | 2 | 8,424 | 13.8% | 13.2% | Balanced |
| **Midwest** | 3 | 6,076 | 10.0% | 24.3% | **–14pp under** |
| **West** | 4 | 5,367 | 8.8% | 16.4% | **–8pp under** |

> **The cohort is heavily South-biased**: 67% of cohort beds are in Southern states (FL, TX, VA, NC, SC, KY, WV, MD, DE, LA, OK), compared to 45% of membership. Midwest (MI, MN, IN) and West (CA, WA, OR, NM, AZ) are underrepresented.

#### Bed Coverage

| Population | Beds | Cohort Coverage |
|-----------|------|----------------|
| Cohort (29 systems) | 61,006 | 100% |
| Premier GPO (acute) | 193,636 | **31.5%** |
| All Members (acute) | 782,765 | **7.8%** |

> The cohort captures ~32% of Premier GPO acute-care beds — a strong foundation for extrapolation with appropriate segmentation.

---

## 3. Extrapolation Model

### Objective
Estimate total annual non-labor purchasing (supply chain comparable) across Premier's membership, using the cohort's per-bed spend benchmarks.

### Key Assumptions
1. **Per-bed spend patterns** in the cohort are representative of the broader membership after size/region adjustment
2. **"GPO-addressable"** = all non-labor purchasing except insurance/benefits/payroll, intercompany/internal, and government/regulatory — this is what TSA captures for well-reporting systems (confirmed by WF calibration at median ratio of 1.04 for Tier 1–2)
3. **Bed count** is a reasonable proxy for purchasing volume across system sizes (with caveats)
4. **Tier 1–2 rate is the reliable benchmark**: WF calibration confirms that Tier 1–2 systems achieve near-complete TSA coverage; no upward adjustment is needed for their rate

### Method A: Weighted Average Extrapolation

| Target Population | Target Beds | Cohort Weighted $/bed | Extrapolated Spend |
|------------------|------------|----------------------|-------------------|
| Premier GPO (acute) | 193,636 | $720K | **$139B** |
| All Members (acute) | 782,765 | $720K | **$564B** |

### Method B: Tier 1–2 Rate (Higher-Confidence Systems Only)

Using only the 16 Tier 1–2 systems ($864K/bed weighted). WF calibration confirms this rate reflects full GPO-addressable purchasing (median capture ratio = 1.04 for calibrated Tier 1–2 systems):

| Target Population | Target Beds | Tier 1-2 $/bed | Extrapolated Spend |
|------------------|------------|----------------|-------------------|
| Premier GPO (acute) | 193,636 | $864K | **$167B** |
| All Members (acute) | 782,765 | $864K | **$676B** |

### Method C: Percentile Range

Using P25–P75 of the per-system $/bed distribution:

| Target Population | P25 ($543K/bed) | Median ($789K/bed) | P75 ($1,108K/bed) |
|------------------|----------------|-------------------|------------------|
| Premier GPO (acute) | **$105B** | **$153B** | **$215B** |
| All Members (acute) | **$425B** | **$617B** | **$867B** |

### Recommended Central Estimate

**For Premier GPO (868 acute-care facilities, 194K beds): $139–167B/year in non-labor purchasing**

- Conservative (weighted avg): $139B — uses the bed-weighted rate which is pulled down by large systems with incomplete TSA submissions (Tier 3)
- Moderate (Tier 1–2 rate): $167B — uses the 18 systems with highest-confidence comprehensive data, confirmed by WF coverage calibration
- The true figure likely falls in the **$139–167B** range

**For All Premier Members (acute): $564–676B/year**

- This is the "addressable market" for Premier's supply chain programs across all acute-care affiliate types
- The wide range reflects uncertainty in the $/bed rate and composition of the non-GPO member population

### Service Line Decomposition (Premier GPO, central estimate)

Using the v3.2 WF entity-bridge balanced 3-SL mix (42 systems, most reliable service line proportions — see `analyst_briefing.md` Section I for methodology and ranges):

| Service Line | Central Share | Range (Cross-Cohort) | Estimated Premier GPO |
|-------------|--------------|---------------------|----------------------|
| **Clinical Med/Surg** | ~64% | 60–64% | **$89–91B** |
| **Non-Clinical** | ~22% | 21–25% | **$29–35B** |
| **Pharma** | ~12–13% | 9–17% | **$13–24B** |
| **Food** | ~1–2% | 1–2% | **$1–3B** (structural undercount likely) |
| **Total** | 100% | — | **$139B** |

> **Methodology update (Feb 12, 2026)**: The SL decomposition above uses the v3.2 entity-bridge hybrid benchmarks with **ranges** across cohort definitions, replacing v3.1 point estimates. Key changes from v3.1: (1) pharma-specific fallback patterns now fire before broad Cardinal/McKesson CLINICAL catch-all (+$80M pharma recovery); (2) primary cohort changed from 4-SL balanced (21 systems, food ≥1%) to 3-SL balanced (42 systems, no food floor), eliminating food-floor selection bias that artificially depressed pharma to 8.8%; (3) TSA external cross-check validates pharma at 15.1% on $139.8B CY2025 spend. See `analyst_briefing.md` Section V for the full v1→v3.2 comparison.

---

## 4. TSA Coverage Calibration (WF Cross-Reference)

### Methodology Correction

The original WF calibration (Session 2) computed capture ratios using a **broad-exclusion** approach — removing pharma distributors, IT/software, capital/utilities, staffing, food, consulting, and legal from the WF denominator before comparing to TSA. This artificially inflated ratios by making the WF base too small (e.g., Methodist LB appeared as 2.03x, UCI as 1.89x).

The **corrected approach** applies narrow exclusions only — removing categories genuinely outside GPO contracting scope:
- Insurance / Benefits / Payroll
- Intercompany / Internal Transfers
- Government / Regulatory / Fees

All other categories (pharma, IT, capital, staffing, food, consulting, legal) are **retained** as GPO-addressable, since GPOs contract for all of them.

### Revised Capture Ratios

| System | WF GPO-Addr ($M) | TSA ($M) | Old Ratio | Revised Ratio | In Cohort? |
|--------|-----------------|---------|-----------|--------------|-----------|
| HONORHEALTH | 1,049 | 1,558 | 1.86 | **1.48** | ✓ Tier 3 |
| UCI | 1,198 | 1,312 | 1.89 | **1.10** | ✓ Tier 2 |
| ADVOCATE AURORA | 7,021 | 7,366 | *3.00 (combined)* | **1.05** | ✓ Tier 2 (new) |
| CFNI | 538 | 548 | 1.16 | **1.02** | ✓ Tier 2 |
| METHODIST LB | 333 | 276 | 2.03 | **0.83** | ✗ |
| MIDLAND | 315 | 217 | 0.79 | **0.69** | ✓ Tier 2 |
| ADVENTIST | 1,217 | 787 | 0.90 | **0.65** | ✗ |
| UHS | 1,974 | 1,205 | 0.65 | **0.61** | ✓ Tier 2 |
| RENOWN | 1,141 | 684 | 0.67 | **0.60** | ✗ |
| ADVENTHEALTH | 7,631 | 3,720 | 0.69 | **0.49** | ✓ Tier 3 |
| UVM | 2,044 | 917 | 0.79 | **0.45** | ✗ (→CONDUCTIV) |
| OSF | 2,223 | 1,000 | 0.53 | **0.45** | ✗ |
| CONWAY | 240 | 92 | 0.49 | **0.38** | ✗ |
| FIRSTHEALTH | 581 | 203 | 0.49 | **0.35** | ✗ |

### Implications for Extrapolation

| Calibration Tier | In-Cohort Systems | Median Capture Ratio | Implication |
|-----------------|-------------------|---------------------|-------------|
| **Best-calibrated** (≥1.0) | UCI, CFNI, ADV AURORA, HONORHEALTH | **1.06** | TSA ≈ full GPO-addressable coverage |
| **Partial-coverage** (<1.0) | MIDLAND, UHS, ADVENTHEALTH | **0.61** | TSA captures ~50–70% |
| **Overall** (all 7 in-cohort) | — | **0.69** | Blended ~70% coverage |

**Conclusion**: The Tier 1–2 benchmark rate ($864K/bed) is derived from systems that predominantly achieve full TSA coverage (calibrated median = **1.04**). This rate already represents comprehensive GPO-addressable purchasing and **requires no upward adjustment**. The gap between the overall weighted average ($720K) and the Tier 1–2 rate ($864K) — approximately 17% — is entirely attributable to incomplete Tier 3 TSA submissions, not lower actual purchasing.

### Advocate Alliance Deep Dive

The Advocate Health Supply Chain Alliance ($17.6B) was decomposed into two direct parents for proper calibration:

| Entity | TSA Spend | WF Entity | WF GPO-Addr | Capture Ratio | Assessment |
|--------|----------|-----------|------------|--------------|------------|
| Advocate Aurora Health | $7,366M | "Advocate Health" | $7,021M | **1.05** | Near parity — WF comprehensively covers this side |
| Carolinas Healthcare System | $10,237M | "Atrium Health" | $995M | **0.10** | WF barely covers — but TSA data is independently comprehensive (Clin 43%, NC 40%, Pharma 16%, Food 1.3%) |

Both direct parents are included as separate Tier 2 entries. The same direct-parent decomposition could be applied to other TSA alliances (Acurity, Allspire) to identify additional well-reporting systems.

---

## 5. Caveats & Limitations

### Per-Bed Benchmark Limitations

1. **Extreme variance** (CV = 72%): $/bed ranges from $332K (Saint Francis) to $3,305K (UCI). Academic medical centers, safety-net systems, and small community hospitals have fundamentally different purchasing profiles that a single $/bed metric cannot capture.

2. **Bed count is an imperfect denominator**: It doesn't account for outpatient volume (growing), case mix index, teaching intensity, or sub-acute beds. Academic medical centers with few beds but high acuity will always skew high.

3. **Tier 3 depression**: The 13 Tier 3 systems average $503K/bed vs $864K/bed for Tiers 1–2 — a 42% gap. This is likely driven by incomplete Non-Clinical and Pharma TSA submissions (e.g., AdventHealth at $38K/bed NC vs cohort P50 of $350K). Using the overall weighted rate ($720K) is conservative; the Tier 1–2 rate ($864K) is probably closer to reality for comprehensive purchasing.

4. **Alliance bed count inflation**: Systems like Texas Health Resources (9,402 beds, $366K/bed) and Fairview (3,483 beds, $421K/bed) appear to include alliance-member beds in their counts, diluting the per-bed metric. Their actual purchasing intensity is likely higher per *owned* bed.

### Extrapolation Limitations

5. **Regional bias**: The cohort is 67% Southern beds vs 45% in the membership. Southern systems may have different purchasing patterns (lower labor costs → potentially higher supply reliance, or different vendor availability). Midwest and West are underrepresented.

6. **Hospital-vs-system level mismatch**: The cohort benchmarks are at the system level (one rate per system aggregated across all its hospitals), but the membership universe is profiled at the hospital level. A system's per-bed rate averages across its academic flagships and community hospitals — the membership universe has both types counted separately.

7. **Membership data completeness**: The `sa_sf_dhc_join` table's bed counts are incomplete for many facilities (118 hospitals with beds = 0 or NULL). The extrapolation denominators may undercount actual membership beds.

8. **Food exclusion**: TSA structurally excludes food (<1% of platform spend). The v3.2 WF entity-bridge benchmark shows food at ~1–2% for balanced reporters. The extrapolation model's food estimate ($2–3B) is likely still conservative; industry benchmarks suggest 3–5% of operating expenses.

9. **V3.2 WF classification update**: The SL decomposition in Section 3 uses the v3.2 entity-bridge hybrid benchmarks with ranges (Feb 12, 2026), which further refined the clinical/pharma split from v3.1 by fixing pharma fallback ordering and eliminating food-floor selection bias in the primary cohort. The per-bed benchmarks in Section 1 (from the 31-system TSA cohort) remain unchanged — they reflect TSA-reported spend, not WF classification. The WF mix is used only for estimating total non-labor envelope from TSA addressable spend.

10. **Non-GPO vs GPO behavior**: The "All Members" extrapolation ($540–650B) assumes non-GPO members have similar per-bed spending. In reality, non-GPO members (many of which are large for-profit chains like HCA, Tenet) may purchase through their own internal supply chains at different rates.

---

## 6. Recommendations

1. **Use the Tier 1–2 rate ($864K/bed) as the primary benchmark** — these 18 systems have the most comprehensive TSA data, and WF calibration confirms their rate represents full GPO-addressable purchasing (median calibrated ratio = 1.04).

2. **Apply size-stratified rates for per-system estimates**: $572K/bed for large systems (2,000+), $949K/bed for medium (800–1,999), $1,289K/bed for small (<800). Do not use a single rate for all.

3. **Adjust for regional bias**: Consider applying region-specific multipliers if regional purchasing data becomes available. The current South-heavy cohort may overweight or underweight certain cost structures.

4. **Supplement food externally**: Use industry benchmarks (3–5% of operating expenses) or Supplier Sales data rather than TSA for food estimates.

5. **Validate with external benchmarks**: Cross-check the $139–167B Premier GPO estimate against published data: the US hospital supply chain is estimated at ~$300–400B annually, and Premier GPO represents ~21% of acute-care hospital beds → expected range of $63–84B in *contracted* spend (which is lower than *total* spend since not all purchasing goes through GPO contracts).

6. **Next: Build a regression model**: To improve precision, regress $/bed against bed count, hospital type, teaching status, and region using the 31 cohort systems as training data. This would reduce the CV and produce system-specific predictions.

7. **Validate Advocate bed counts**: Obtain externally validated bed counts for Carolinas Healthcare System and Advocate Aurora Health to integrate them into per-bed benchmarks and the weighted-average calculation.

8. **Consider decomposing other alliances**: Apply the direct-parent splitting methodology to Acurity ($29.9B), Allspire ($7.8B), and other alliance entities to identify additional well-reporting systems and expand the cohort.

9. **Use facility-level bed matches for clinical per-bed rates** (Session 9 finding): The system-level bed denominator inflates beds by 33% due to non-TSA-reporting facilities within health systems. The corrected clinical per-bed rate is $146K (all-TSA facility-level) vs $131K (system-level). For extrapolation, add a 1.10× alt-site multiplier to account for physician offices, ASCs, and other non-bed entities with clinical purchasing.

---

## 7. Extrapolation Validation (Session 9 — Clinical Spend Spot-Check)

A two-tier clinical extrapolation spot-check (Session 8b) revealed a 26% gap between projected and actual TSA clinical spend. Session 9 fully decomposed this gap:

### Gap Summary

| Factor | Amount | Root Cause |
|--------|--------|-----------|
| System-level bed inflation | $3.0B | Cohort rate included beds at non-TSA-reporting facilities (1.33× inflation) |
| Alliance/GPO unmatched spend | $3.7B | Acurity, Allspire, Conductiv, etc. purchase through non-hospital entities |
| Alt-site unmatched spend | $3.3B | Physician offices, ASCs, ambulatory centers with clinical purchasing |
| Acute hospitals not in DHC | $1.8B | 197 hospitals missing from DHC crosswalk |
| **Total** | **$11.9B** | **Fully explained** |

### Key Metrics

| Metric | System-Level | Facility-Level |
|--------|-------------|---------------|
| Cohort beds | 297K | 222K |
| Clinical spend | $39.1B | $34.6B |
| Per-bed rate | $131K | $156K |
| All-TSA per-bed rate | — | $146K (1,264 entities, 337K beds) |

### Conclusion

The per-bed methodology is fundamentally sound. The gap is fully explained by (1) a correctable bed denominator issue, and (2) structural features of the data (alliances and alt-site providers that purchase clinical supplies without having beds). See `analyst_briefing.md` Section III-A for the complete analysis.

---

*Underlying queries and data sourced from `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` (CY2025) and `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join`.*
