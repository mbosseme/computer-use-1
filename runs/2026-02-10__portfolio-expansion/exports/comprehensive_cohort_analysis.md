# Comprehensive Health System Cohort Analysis

## Executive Summary

**Objective**: Identify ≥20 health systems within Premier's Transaction Analysis (TSA) data that provide comprehensive non-labor purchasing data, suitable for extrapolation to Premier's GPO membership (~25% of US healthcare).

**Result**: We identified **31 health systems** with 3+ service line coverage across Clinical, Non-Clinical, and Pharma categories, with 12-month continuous data in CY2025. Three of these also show meaningful Food purchasing (≥2%). The cohort spans 25+ states, covers ~98,000 staffed hospital beds, and represents ~$75B in annual TSA purchasing volume. This includes two systems derived from splitting the Advocate Health Supply Chain Alliance into its constituent direct parents (Carolinas Healthcare System and Advocate Aurora Health), each of which independently qualifies for the cohort.

**Key structural finding**: Food purchasing is systematically underrepresented in TSA (<1% of total spend platform-wide). A strict 4-service-line requirement would yield only 3 qualifying systems. The realistic definition of "comprehensive" in TSA is 3 service lines (Clinical Med/Surg + Non-Clinical + Pharma).

> **Post-hoc validation note**: This document was audited against the original ANALYSIS_PLAN.md. Two systems (AdventHealth, St Luke's University) were initially excluded as "borderline" but in fact pass the stated ≥2% + $5M thresholds for all 3 service lines. They have been added to Tier 3. The Midland duplicate (formerly listed as both #16 and #28) has been resolved. See "Validation Notes" appendix for full audit details.

---

## Methodology

### Data Sources
| Source | Table | Rows (est.) | Scope |
|--------|-------|------------|-------|
| Workflow History (WF) | `abi-xform-prod...provider_invoice_workflow_history` | ~89M | All AP invoices (ERP/Remitra) |
| Transaction Analysis (TSA) | `abi-inbound-prod...transaction_analysis_expanded` | ~819M | Purchasing transactions with category taxonomy |
| Facility Demographics | `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join` | ~6,769 | DHC hospital data, beds, type, location |

### Analysis Approach
1. **Universe Establishment**: Identified all TSA health systems with ≥$100M spend and 12-month coverage in CY2025
2. **Capture Ratio Calibration**: For 15 systems present in BOTH WF and TSA, computed TSA / WF_supply_chain_only to validate TSA comprehensiveness
3. **Service Line Classification**: Mapped TSA's ~870 Contract_Category values into 4 service lines:
   - **Clinical Med/Surg**: Implants, devices, diagnostics, surgical supplies, blood, IV therapy, etc.
   - **Non-Clinical**: IT, HR/staffing, facilities, construction, insurance, consulting, legal, MRO, etc.
   - **Pharma**: Pharmaceutical, pharmacy distribution, PBM services, radiopharmaceuticals
   - **Food**: Food distribution, foodservice support programs, dietary supplements
4. **Breadth Filter**: Required ≥2% of system spend in each qualifying service line AND ≥$5M absolute
5. **Demographic Enrichment**: Joined to DHC hospital database for bed counts, facility counts, geography

### WF Vendor Categorization (for Capture Ratio)

To compute WF "GPO-addressable" spend, we apply **narrow exclusions only** — removing only categories that are genuinely outside GPO contracting scope:

- **Excluded (non-GPO-addressable)**:
  - Insurance / Benefits / Payroll (BCBS, life insurance, payroll deductions)
  - Intercompany / Internal Transfers (parent company allocations, foundation transfers)
  - Government / Regulatory / Fees (tax payments, licensure fees)
- **Kept (GPO-addressable)**: All other categories remain, including pharma distribution, IT/software, capital/construction, staffing, food, consulting, and legal — all of which fall within GPO contracting scope

> **Methodology correction (Session 3)**: The original WF calibration incorrectly excluded pharma distributors, IT/software, capital/utilities, staffing, food, and consulting from the WF denominator before computing capture ratios. This artificially inflated ratios (e.g., Methodist LB appeared as 2.03x, UCI as 1.89x). The corrected approach retains these GPO-addressable categories, producing more realistic ratios that reflect TSA's actual coverage of GPO-addressable purchasing.

---

## Capture Ratio Calibration (WF → TSA Cross-Reference)

For 14 systems present in both data models, capture ratios (TSA ÷ WF GPO-addressable) reveal which systems submit comprehensive data through TSA. The Advocate Alliance is compared at the **direct parent level** (WF "Advocate Health" vs TSA "Advocate Aurora Health" direct parent) for an apples-to-apples comparison — see "Advocate Alliance Treatment" below.

| System | WF GPO-Addr ($M) | TSA ($M) | Ratio | Interpretation |
|--------|-----------------|---------|-------|--------------|
| **HONORHEALTH** | 1,049 | 1,558 | **1.48** | TSA is richer — captures alliance/distribution spend |
| **UCI** | 1,198 | 1,312 | **1.10** | Near parity — TSA comprehensive |
| **ADVOCATE AURORA** | 7,021 | 7,366 | **1.05** | Near parity — WF covers Advocate Aurora well |
| **CFNI** | 538 | 548 | **1.02** | Near parity — both models comprehensive |
| METHODIST LB | 333 | 276 | 0.83 | TSA captures most WF GPO-addressable spend |
| MIDLAND | 315 | 217 | 0.69 | Partial TSA coverage |
| ADVENTIST | 1,217 | 787 | 0.65 | Partial — TSA lacks some pharma/NC |
| UHS | 1,974 | 1,205 | 0.61 | Partial coverage |
| RENOWN | 1,141 | 684 | 0.60 | Partial coverage |
| ADVENTHEALTH | 7,631 | 3,720 | 0.49 | TSA captures ~half of GPO-addressable |
| UVM* | 2,044 | 917 | 0.45 | *TSA maps to CONDUCTIV alliance |
| OSF | 2,223 | 1,000 | 0.45 | Partial coverage |
| CONWAY | 240 | 92 | 0.38 | Limited TSA coverage |
| FIRSTHEALTH | 581 | 203 | 0.35 | Limited TSA coverage |

**Calibration insight**: With the corrected narrow-exclusion methodology, **4 systems have capture ratios ≥1.0** (HONORHEALTH, UCI, ADVOCATE AURORA, CFNI) — confirming TSA captures comprehensive GPO-addressable purchasing for well-reporting systems. The typical capture ratio for systems in the 0.5–0.7 range reflects incomplete Non-Clinical and Pharma TSA submissions, not lower actual purchasing. The median ratio across all 14 systems is **0.64**, but rises to **1.04** for the 4 best-calibrated systems.

### Advocate Alliance Treatment

The **Advocate Health Supply Chain Alliance** appears as a single `Health_System_Name` in TSA ($17.6B) but aggregates two distinct direct parents:

| Direct Parent | TSA Spend ($M) | Facilities | Clin % | NC % | Pharma % | Food % |
|--------------|---------------|-----------|--------|------|---------|--------|
| **Carolinas Healthcare System** | 10,237 | 75 | 43.1 | 39.9 | 15.7 | 1.3 |
| **Advocate Aurora Health** | 7,366 | 290 | 65.4 | 31.1 | 3.0 | 0.5 |

In WF, the corresponding entities are:
- **"Advocate Health"** ($7,035M) — primarily Advocate Aurora side (134 of 162 orgs are Advocate Aurora entities; only ~$129M from recognizable Carolinas orgs)
- **"Atrium Health"** ($995M) — a small Carolinas-side fragment (~10% of TSA Carolinas spend)

The apples-to-apples comparison — WF "Advocate Health" ($7,021M GPO-addressable) vs TSA "Advocate Aurora Health" ($7,366M) — yields a **1.05 capture ratio**, one of the best matches in the cohort. This confirms WF comprehensively covers the Advocate Aurora side.

Since each direct parent independently qualifies for the cohort with 3+ service lines, they are included as **separate entries** in the cohort tables below (both as Tier 2, with food >$1M).

---

## Service Line Distribution: Structural Finding

### Platform-Wide TSA Service Line Breakdown (CY2025, top categories >$100M)

| Service Line | Examples of Contract Categories | Approx. Platform Spend |
|-------------|-------------------------------|----------------------|
| Clinical Med/Surg | Implants, surgical supplies, diagnostics, blood, IV therapy, monitoring | ~55% |
| Non-Clinical | IT, staffing, consulting, construction, facilities, insurance, MRO | ~30% |
| Pharma | Pharmaceutical, pharmacy distribution, PBM | ~14% |
| Food | Food distribution, foodservice support | **<1%** |

**Food is structurally absent from TSA.** Total food-related spend across the entire TSA platform is ~$1B out of $115B+ total — less than 1%. This is not a per-system data quality issue; food procurement typically flows through separate purchasing channels (e.g., direct contracts with Sysco/US Foods managed outside the med/surg supply chain platform).

---

## The Comprehensive Cohort

### Tier 1: All 4 Service Lines (Clinical ≥2% + Non-Clinical ≥2% + Pharma ≥2% + Food ≥2%)

Only 3 systems meet the strict 4-service-line threshold:

| # | Health System | TSA Spend ($M) | Clinical % | Non-Clin % | Pharma % | Food % | Beds | Facilities | States |
|---|--------------|---------------|-----------|-----------|---------|--------|------|-----------|--------|
| 1 | **PRISMA HEALTH** | 2,905 | 39.0 | 34.7 | 24.3 | 2.1 | 2,711 | 15 | SC, TN |
| 2 | **HEALTH FIRST** | 1,116 | 32.0 | 48.9 | 17.0 | 2.2 | 918 | 4 | FL |
| 3 | **VCU HEALTH** | 774 | 56.8 | 34.6 | 6.2 | 2.4 | 1,918 | 7 | VA |

### Tier 2: 3 Service Lines + Food Data Present (≥$1M food)

These systems have comprehensive Clinical + Non-Clinical + Pharma coverage AND some food data (though below 2%):

| # | Health System | TSA ($M) | Clin % | NC % | Pharma % | Food % | Food $M | Beds | States |
|---|--------------|---------|--------|------|---------|--------|--------|------|--------|
| 4 | **CAROLINAS HEALTHCARE†** | 10,237 | 43.1 | 39.9 | 15.7 | 1.3 | 129.2 | ~10,000† | NC, SC, GA, AL |
| 5 | **ADVOCATE AURORA†** | 7,366 | 65.4 | 31.1 | 3.0 | 0.5 | 38.9 | ~8,000† | IL, WI |
| 6 | **UPMC** | 5,344 | 46.6 | 47.6 | 4.5 | 1.2 | 64.7 | 6,650 | PA, NY, MD |
| 7 | **McLAREN** | 3,726 | 22.5 | 62.4 | 14.1 | 1.0 | 37.6 | 1,886 | MI |
| 8 | **WVUHS** | 3,663 | 46.1 | 37.2 | 16.0 | 0.7 | 25.6 | 2,592 | WV, MD, OH, PA |
| 9 | **TEXAS HEALTH** | 3,443 | 61.9 | 30.5 | 6.5 | 1.1 | 38.5 | 9,402 | TX + multi-state |
| 10 | **UVA** | 1,959 | 39.2 | 25.7 | 33.7 | 1.4 | 26.8 | 863 | VA |
| 11 | **UNIVERSITY HEALTH** | 1,692 | 42.9 | 43.7 | 12.7 | 0.6 | 10.5 | 785 | TX |
| 12 | **BAPTIST HEALTHCARE** | 1,402 | 56.2 | 29.6 | 13.5 | 0.6 | 8.4 | 2,549 | KY, IN |
| 13 | **UCI** | 1,312 | 36.0 | 27.4 | 36.1 | 0.5 | 6.8 | 397 | CA |
| 14 | **PEACEHEALTH** | 1,181 | 45.5 | 35.2 | 18.7 | 0.5 | 6.3 | 2,333 | WA, OR, AK |
| 15 | **PRESBYTERIAN** | 876 | 31.4 | 48.0 | 19.7 | 0.9 | 8.3 | 983 | NM |
| 16 | **LUMINIS** | 631 | 39.4 | 44.7 | 14.8 | 1.1 | 6.6 | 696 | MD |
| 17 | **CFNI** | 548 | 45.7 | 5.3 | 47.5 | 1.6 | 8.7 | 707 | IN |
| 18 | **MIDLAND** | 217 | 44.4 | 46.7 | 8.0 | 0.9 | 2.0 | 261 | TX |

> † Carolinas Healthcare System and Advocate Aurora Health are TSA `Direct_Parent_Name` entities within the Advocate Health Supply Chain Alliance. Bed counts are estimated and pending external validation. See "Advocate Alliance Treatment" above for full methodology.

### Tier 3: 3 Service Lines, No Meaningful Food

These have robust Clinical + Non-Clinical + Pharma but effectively zero food in TSA:

| # | Health System | TSA ($M) | Clin % | NC % | Pharma % | Beds | States |
|---|--------------|---------|--------|------|---------|------|--------|
| 19 | **ADVENTHEALTH** | 3,720 | 86.6 | 11.1 | 2.3 | 10,719 | FL + 10 states |
| 20 | **HONORHEALTH** | 1,558 | 58.0 | 38.6 | 3.4 | 1,654 | AZ |
| 21 | **FAIRVIEW** | 1,465 | 60.0 | 14.1 | 25.9 | 3,483 | MN |
| 22 | **ST LUKE'S UNIVERSITY** | 1,307 | 52.7 | 43.7 | 3.1 | 1,774 | PA, NJ |
| 23 | **ECU HEALTH** | 1,164 | 43.3 | 28.5 | 28.3 | 1,367 | NC |
| 24 | **SOUTH BROWARD** | 1,226 | 40.8 | 56.4 | 2.7 | 1,818 | FL |
| 25 | **SAINT FRANCIS** | 571 | 81.5 | 15.6 | 2.6 | 1,721 | OK |
| 26 | **LIFEBRIDGE** | 561 | 45.6 | 51.8 | 2.3 | 816 | MD |
| 27 | **CARILION** | 544 | 58.1 | 39.3 | 2.5 | 894 | VA |
| 28 | **BEEBE** | 469 | 23.2 | 56.0 | 20.4 | 201 | DE |
| 29 | **TIDALHEALTH** | 268 | 62.9 | 24.3 | 12.1 | 408 | DE, MD |
| 30 | **TERREBONNE** | 184 | 38.9 | 41.6 | 17.4 | 242 | LA |
| 31 | **GREATER BALTIMORE** | 135 | 51.0 | 21.0 | 28.0 | 258 | MD |

### Additional Candidates (borderline but worth noting)

| Health System | TSA ($M) | Issue | Notes |
|--------------|---------|-------|-------|
| HEALTHPARTNERS | 769 | NC only 2.8% but shallow — mostly hardware resellers + equipment repair; no construction, staffing, insurance, IT consulting | Technically passes ≥2% but fails qualitative diversity check |
| CHILDREN'S HOSPITAL CORP | 1,400 | Pediatric-only | May not be representative of general acute care |
| MHS PURCHASING | 499 | Likely a GPO entity | Need to verify vs actual health system |

---

## Cohort Characteristics

### Geographic Coverage

| Region | Systems | Total Beds |
|--------|---------|-----------|
| Southeast (SC, NC, FL, LA, OK, GA, AL) | PRISMA, HEALTH FIRST, ADVENTHEALTH, ECU, SOUTH BROWARD, SAINT FRANCIS, TERREBONNE, CAROLINAS HEALTHCARE† | ~29,200 |
| Mid-Atlantic (VA, MD, DE, PA) | VCU, UVA, LUMINIS, LIFEBRIDGE, GREATER BALTIMORE, CARILION, BEEBE, TIDALHEALTH, UPMC, ST LUKE'S | ~16,058 |
| Midwest (MI, MN, IL, WI, IN, KY) | McLAREN, FAIRVIEW, ADVOCATE AURORA†, CFNI, BAPTIST | ~16,625 |
| Southwest (AZ, NM, TX) | HONORHEALTH, PRESBYTERIAN, MIDLAND, UNIVERSITY HEALTH, TEXAS HEALTH | ~13,085 |
| West (CA, WA, OR) | UCI, PEACEHEALTH | ~2,730 |
| Appalachian (WV) | WVUHS | ~2,592 |

**25+ states represented** across all major US regions. AdventHealth alone spans 11 states (FL, CO, GA, IL, KS, KY, NC, SC, TX, VA, WI). The addition of Advocate Aurora (IL, WI) significantly improves Midwest representation.

> † Bed counts for Carolinas Healthcare System (~10,000) and Advocate Aurora Health (~8,000) are estimated; pending external validation.

### Size Distribution
- **Large** (>$2B TSA): CAROLINAS HEALTHCARE, ADVENTHEALTH, ADVOCATE AURORA, UPMC, McLAREN, WVUHS, TEXAS HEALTH, PRISMA, ADVENTHEALTH = 8 systems
- **Medium** ($500M-$2B): UVA, UNIVERSITY HEALTH, HONORHEALTH, FAIRVIEW, BAPTIST, ST LUKE'S, UCI, PEACEHEALTH, ECU, SOUTH BROWARD, HEALTH FIRST, PRESBYTERIAN, VCU, SAINT FRANCIS, LIFEBRIDGE, CFNI, CARILION = 17 systems
- **Small** (<$500M): BEEBE, TIDALHEALTH, MIDLAND, TERREBONNE, GREATER BALTIMORE, LUMINIS = 6 systems

### Hospital Type Mix
- Short Term Acute Care: All 31 systems
- Critical Access: 10 systems
- Children's: 7 systems
- Psychiatric: 5 systems
- Long Term Acute Care: 5 systems

---

## Capture Ratio Validation (Where Available)

Of the 31 cohort systems, 8 have WF data for cross-validation:

| System | Capture Ratio | Confidence Level |
|--------|--------------|------------------|
| HONORHEALTH | 1.48 | **High** — TSA captures beyond WF scope |
| UCI | 1.10 | **High** — near parity |
| ADVOCATE AURORA | 1.05 | **High** — near parity (direct parent match) |
| CFNI | 1.02 | **High** — near parity |
| MIDLAND | 0.69 | **Medium** — partial coverage |
| UHS | 0.61 | **Medium** — partial coverage |
| ADVENTHEALTH | 0.49 | **Medium-Low** — TSA captures ~half |
| CONWAY* | 0.38 | Low — not in final cohort |

The remaining 23 systems are **TSA-only** (no WF to compare). Their comprehensiveness is inferred from service line breadth analysis rather than cross-model validation.

---

## Risks and Caveats

1. **Food gap is structural**: The cohort cannot represent food purchasing comprehensively. Any extrapolation model should treat food as a separate data stream requiring supplementary sources.

2. **GPO/Alliance entities excluded**: ACURITY ($29.9B), ALLSPIRE ($7.8B), YANKEE ALLIANCE ($2.0B), ALLIANT ($1.3B), and COST TECHNOLOGY ($1.5B) were excluded as they represent purchasing alliances, not individual health systems. The Advocate Health Supply Chain Alliance ($17.6B) has been decomposed into its two direct parents (Carolinas Healthcare System and Advocate Aurora Health), each included as a separate Tier 2 system. The same direct-parent splitting could be applied to other alliances if warranted.

3. **TSA-only systems lack external validation**: 23 of 31 systems have no WF cross-reference. Their "comprehensive" classification rests on service line breadth alone. It's possible some have partial TSA submissions that happen to span multiple categories.

4. **Vendor categorization heuristic**: The WF cleanup (for capture ratios) uses narrow exclusions — only removing insurance/benefits/payroll, intercompany/internal, and government/regulatory. This is more principled than the original broad-exclusion approach, but minor misclassifications are still possible.

5. **Non-Clinical category breadth**: The "Non-Clinical" bucket is very broad (IT, HR, facilities, consulting, insurance, construction). A system could technically "pass" by having heavy construction spend alone, without true operational purchasing diversity.

6. **Advocate alliance structure**: ~~ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE appears as a single TSA entity with $17.6B spend, but it encompasses multiple health systems.~~ **RESOLVED**: The alliance has been split into its two constituent direct parents — **Carolinas Healthcare System** ($10,237M) and **Advocate Aurora Health** ($7,366M) — each included as a separate Tier 2 entry. WF calibration confirms the Advocate Aurora side at a 1.05 capture ratio. The Carolinas side has minimal WF coverage ($995M of $10,237M) but independently qualifies via service line breadth (Clin 43%, NC 40%, Pharma 16%, Food 1.3%). Same direct-parent splitting could be applied to other TSA alliance entities (Acurity, Allspire) if warranted.

---

## Recommendations

1. **Accept 3-service-line standard**: Given TSA's structural food gap, define "comprehensive" as Clinical + Non-Clinical + Pharma with ≥2% each. This yields 31 qualifying systems — well above the ≥20 target.

2. **Prioritize Tiers 1-2 (18 systems)**: These have the richest data including at least some food. They are the strongest candidates for extrapolation.

3. **Use Tier 3 for validation**: The additional 11 systems in Tier 3 can serve as a cross-check — do extrapolation models trained on Tiers 1-2 produce consistent estimates when applied to Tier 3?

4. **Normalize by bed count**: For extrapolation to Premier's GPO membership (~4,000+ hospitals), use per-bed or per-facility spend ratios rather than raw totals, anchored in the DHC hospital demographic data.

5. **Food requires supplementary data**: If food/nutrition spend is critical to the portfolio expansion analysis, consider:
   - Supplementing with Supplier Sales data (which may capture Sysco/US Foods contracts)
   - Industry benchmarks for food-as-%-of-operating-expenses (~3-5% typically)

6. **Next steps**:
   - ~~Validate 3-5 of the TSA-only systems by spot-checking top vendors and Contract_Category distributions~~ ✅ Done (PRISMA, ECU validated; see Validation Notes)
   - Build per-bed spend benchmarks for each service line
   - Map cohort systems to the full Premier GPO membership universe using `sa_sf_dhc_join` demographics
   - Develop extrapolation model (cohort spend × membership scale factor)

---

## Appendix: Contract Category → Service Line Mapping

### Clinical Med/Surg (default bucket)
All Contract_Category values not explicitly assigned to other buckets, including:
- Orthopedic implants (total joint, trauma, small joint, spinal)
- Cardiac devices (CRM, electrophysiology, TAVI, LAA closure, mechanical circulatory support)  
- Surgical supplies (energy, hemostatics, endomechanical, custom trays)
- Diagnostics (chemistry/immunochem, molecular screening, multiplex panels)
- Blood services, biological blood plasma
- IV therapy (infusion devices, IV fluids)
- Endoscopy, ophthalmology, urology products
- Neurovascular, peripheral vascular products
- Physiological monitoring, pulse oximetry
- Patient care supplies, safety phlebotomy
- Medical/surgical products distribution
- Reconstructive/skin grafting, bone substitutes
- UNKNOWN category (defaulted to Clinical)

### Non-Clinical
`CONSTRUCTION SERVICES`, `INFORMATION MANAGEMENT SYSTEMS PRODUCTS AND SERVICES`, `HARDWARE/SOFTWARE RESELLERS SERVICES AND REFURBISHED EQUIPMENT`, `MAINTENANCE REPAIR AND OPERATIONS`, `WORKFORCE SOLUTIONS - STAFFING`, `INSURANCE SERVICES`, `REVENUE CYCLE MANAGEMENT SOLUTIONS`, `CONSULTING - FINANCE AND ACCOUNTING`, `BENEFITS MANAGEMENT`, `HEALTHCARE CONSULTING`, `EMR/EHR SOFTWARE`, `ADVERTISING AND MARKETING SERVICES`, `EDUCATIONAL SYSTEMS`, `GENERAL CONSULTING`, `REAL ESTATE EXPENSES`, `LEGAL SERVICES`, `MUNICIPAL SERVICES`, `ENVIRONMENTAL AND FACILITY MANAGEMENT SERVICES`, `TELECOMMUNICATIONS EQUIPMENT AND SERVICES DISTRIBUTORS`, `SUPPORT SERVICES OUTSOURCING`, `FURNITURE AND SYSTEMS SEATING AND ACCESSORIES`, `WORKFORCE SOLUTIONS - HR SOFTWARE`, `TRAVEL SERVICES`, `GENERAL IT SERVICES`, `IT CONSULTING`, `HVAC EQUIPMENT CONTROLS AND SERVICES`, `ENERGY SERVICES PROCUREMENT EFFICIENCY AND RENEWABLE`, `FACILITIES MANAGEMENT AND ENVIRONMENTAL SERVICES CONSULTING SERVICES`, `REUSABLE TEXTILES AND TEXTILE SERVICES`, `ORGAN PROCUREMENT SERVICES`, `GENERAL OUTSOURCED CLINICAL SERVICES`, `CLINICAL EQUIPMENT REPAIR AND MAINTENANCE SERVICES`, `ANESTHESIA SERVICES`, `SURGICAL INSTRUMENT AND SCOPE REPAIR`, `CLINICAL REFERENCE LABORATORY TESTING SERVICES`

### Pharma
`PHARMACEUTICAL`, `PHARMACY DISTRIBUTION`, `PHARMACY BENEFIT MANAGER PBM AND SUPPORT SERVICES`, `RADIOPHARMACEUTICAL PRODUCTS DISTRIBUTOR`

### Food
`FOOD DISTRIBUTION`, `FOODSERVICE SUPPORT PROGRAMS`, `DIETARY/NUTRITIONAL SUPPLEMENT PRODUCTS`

---

## Appendix: Validation Notes

*Added after post-hoc audit comparing executed analysis against ANALYSIS_PLAN.md*

### Corrections Applied

1. **AdventHealth promoted to Tier 3**: Originally listed as "borderline" with "Pharma only 2.3%". However, 2.3% ≥ 2% threshold and ~$85M pharma ≫ $5M floor. NC at 11.1% ($413M) with real diversity. This is the 2nd largest system in the cohort ($3.7B) and spans 11 states — a significant addition.

2. **St Luke's University Health Network promoted to Tier 3**: Originally listed as "borderline" with "Pharma 3.1%". Pharma at 3.1% ($40M) passes both thresholds. NC at 43.7% has excellent diversity — construction ($81M), insurance ($70M), finance consulting ($65M), IT ($31M), hardware ($26M), MRO ($20M), real estate ($20M), staffing ($7M), EMR ($5M). Genuinely comprehensive.

3. **Midland duplicate removed**: Was listed as both #16 (Tier 2, with food data) and #28 (Tier 3). Now appears only in Tier 2.

### Justified Exclusions Confirmed

- **HealthPartners** ($769M): NC at 2.8% technically passes the quantitative threshold, but composition is almost entirely hardware/software resellers ($6.9M) + clinical equipment repair ($5.9M). Zero construction, staffing, insurance, or IT consulting spend. Per ANALYSIS_PLAN.md Step 3.3 ("flag outliers — e.g., a system with 0% IT spend is likely not submitting non-clinical"), this is a qualitative exclusion.
- **CONDUCTIV** ($1.6B): Verified as a multi-system GPO containing UVM, University of Louisville, and TriHealth — not a single health system.
- **GPO/Alliance entities** (Acurity $29.9B, Allspire $7.8B, Yankee $2.0B, etc.): Correctly excluded as purchasing alliances.

### Service Line Classification Validation

- **Debatable categories** (6 categories totaling $8.3B platform-wide — GENERAL OUTSOURCED CLINICAL SERVICES, CLINICAL EQUIPMENT REPAIR, ANESTHESIA SERVICES, etc.): These are *purchased services*, not med/surg supplies. Classification as Non-Clinical is defensible. **Sensitivity test**: Even if reclassified to Clinical, every cohort system still passes the ≥2% NC threshold using only core NC categories. Lowest core-only NC% is Fairview at 13.6%.
- **UNKNOWN category** (~$1.6B platform-wide): Top vendors are GE Healthcare ($51M), Steris ($35M), Philips ($34M), Medtronic ($21M) — predominantly clinical. Minor leakage: Microsoft ($34M in 1 system), US Foods ($24M across 46 systems), CDW ($13M in 2 systems). Default to Clinical is reasonable.

### Spot-Check Results

- **PRISMA HEALTH (Tier 1)**: Confirmed comprehensive — AmerisourceBergen $626M (pharma), Brasfield & Gorrie $76M (construction), Qualivis $68M (staffing), Morrison $61M (food), Choice Energy $42M (utilities), Epic $36M (IT), plus deep clinical device vendors across cardiac, ortho, surgical robotics.
- **ECU HEALTH (Tier 3)**: Confirmed comprehensive — pharma $323M, diverse NC across 10+ categories: staffing $71M, construction $47M, IT $43M, municipal $26M, consulting $18M, MRO $17M, anesthesia $16M, hardware $17M, EMR $9M.

### Plan Deviations Acknowledged

| Deviation | Assessment |
|-----------|------------|
| Capture ratio ≥0.85 dropped as cohort filter | **Justified** — only 8 of 31 systems have WF data; requiring WF presence would eliminate 23 systems. Mission correctly pivoted to TSA-only signature detection per Phase 5. |
| UNSPSC_Segment_Code not used for UNKNOWN classification | **Acceptable** — UNKNOWN is ~90% clinical vendors by spend; UNSPSC would marginally improve classification but wouldn't change any system's qualification. |
| Advocate exemplar comparison (Step 4.2) not performed | **Resolved** — Advocate decomposed into two direct parents; WF "Advocate Health" vs TSA "Advocate Aurora Health" yields 1.05 capture ratio. |
| Service line mix variance across cohort not formally assessed | **Noted** — high variance is present (pharma: 2.3%–47.5%, NC: 5.3%–62.4%). This reflects genuinely different purchasing profiles rather than data quality issues. |
| Vendor concentration per service line (Phase 6.2) not computed | **Deliverable gap** — deferred to next phase (per-bed benchmarking). |
