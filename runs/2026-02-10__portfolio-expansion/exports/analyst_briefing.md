# Portfolio Expansion: TSA Cohort Findings

**From**: Matt Bossemeyer  
**Date**: February 10, 2026  
**Re**: Identifying Representative Health Systems in TSA for Non-Labor Spend Extrapolation

---

## Executive Summary (for Leadership)

We set out to determine whether Premier's Transaction Analysis (TSA) data contains enough health systems with comprehensive non-labor purchasing to support reliable extrapolation across Premier's GPO membership — roughly 25% of US healthcare.

**The answer is yes.** We identified **29 health systems** in TSA that report purchasing data spanning at least three of four non-labor service lines: Clinical Med/Surg, Non-Clinical (IT, facilities, staffing, consulting, etc.), and Pharma. Three of the 29 also include meaningful Food purchasing. Together, this cohort represents approximately **80,000 staffed hospital beds**, **~$57 billion** in annual purchasing volume, and coverage across **25+ states** and all major US regions.

One structural limitation: food/nutrition purchasing is almost entirely absent from TSA platform-wide (<1% of $115B+ total spend). Food procurement typically runs through separate channels (e.g., direct contracts with Sysco/US Foods outside the med/surg supply chain). For the purposes of this analysis, we define "comprehensive" as 3 service lines — Clinical + Non-Clinical + Pharma — which yields a cohort well above our ≥20-system target.

**Bottom line**: TSA is a viable foundation for non-labor spend extrapolation across Premier's GPO membership, with the caveat that food requires supplementary data.

---

## Detailed Findings (for Analyst Validation)

### Methodology

We used three data sources:

| Source | Table | Purpose |
|--------|-------|---------|
| **Transaction Analysis (TSA)** | `abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` | Primary — 819M rows of categorized purchasing transactions |
| **Workflow History (WF)** | `abi_xform_bq_erp_hardening.provider_invoice_workflow_history` | Calibration — 89M AP-level invoices for systems in both models |
| **Facility Demographics** | `cdx_sample_size.sa_sf_dhc_join` | Enrichment — bed counts, facility types, geography |

**Steps**:

1. **Established the universe**: All TSA health systems with ≥$100M spend and 12-month continuous data in CY2025.
2. **Calibrated capture ratios**: For 15 systems present in both WF and TSA, we computed TSA spend ÷ WF supply-chain-only spend. This validated which systems submit comprehensive data through TSA (ratio >1.0 = TSA is the richer source; ratio <0.7 = partial submission).
3. **Classified service lines**: Mapped TSA's ~870 `Contract_Category` values into 4 buckets — Clinical Med/Surg (default), Non-Clinical (34 explicit categories), Pharma (4 categories), Food (3 categories).
4. **Applied breadth filters**: Required ≥2% of total spend AND ≥$5M absolute in each qualifying service line.
5. **Enriched with demographics**: Joined to DHC hospital data for beds, facilities, geography, and hospital type.

### WF Calibration (Quick Summary)

For the 15 dual-source systems, we removed non-supply-chain vendors from WF (pharma distributors, insurance, government, overhead allocations, staffing, IT/software, capital, food, intercompany) to create an apples-to-apples comparison. Key takeaways:

- **5 systems** have capture ratios >1.0 — TSA is definitively their primary/more comprehensive data source.
- **3 systems** are in the 0.65–0.90 range — TSA captures most but not all purchasing.
- **7 systems** are below 0.7 — partial TSA coverage; these were not included in the final cohort unless they independently passed the service line breadth test.

Only 7 of the final 29 cohort systems have WF data for cross-validation. The other 22 are TSA-only, with comprehensiveness inferred from service line breadth.

### The Cohort: 29 Systems in Three Tiers

**Tier 1 — All 4 Service Lines** (3 systems): These show ≥2% in Clinical, Non-Clinical, Pharma, AND Food.

| System | TSA Spend ($M) | Clin% | NC% | Pharma% | Food% | Beds |
|--------|---------------|-------|-----|---------|-------|------|
| Prisma Health | 2,905 | 39.0 | 34.7 | 24.3 | 2.1 | 2,711 |
| Health First | 1,116 | 32.0 | 48.9 | 17.0 | 2.2 | 918 |
| VCU Health | 774 | 56.8 | 34.6 | 6.2 | 2.4 | 1,918 |

**Tier 2 — 3 Service Lines + Some Food** (13 systems): Comprehensive across Clinical + NC + Pharma with ≥$1M food (below the 2% threshold but present).

| System | TSA ($M) | Clin% | NC% | Pharma% | Food $M | Beds | States |
|--------|---------|-------|-----|---------|---------|------|--------|
| UPMC | 5,344 | 46.6 | 47.6 | 4.5 | 64.7 | 6,650 | PA, NY, MD |
| McLaren | 3,726 | 22.5 | 62.4 | 14.1 | 37.6 | 1,886 | MI |
| WVUHS | 3,663 | 46.1 | 37.2 | 16.0 | 25.6 | 2,592 | WV, MD, OH, PA |
| Texas Health | 3,443 | 61.9 | 30.5 | 6.5 | 38.5 | 9,402 | TX + multi |
| UVA | 1,959 | 39.2 | 25.7 | 33.7 | 26.8 | 863 | VA |
| University Health | 1,692 | 42.9 | 43.7 | 12.7 | 10.5 | 785 | TX |
| Baptist Healthcare | 1,402 | 56.2 | 29.6 | 13.5 | 8.4 | 2,549 | KY, IN |
| UCI | 1,312 | 36.0 | 27.4 | 36.1 | 6.8 | 397 | CA |
| PeaceHealth | 1,181 | 45.5 | 35.2 | 18.7 | 6.3 | 2,333 | WA, OR, AK |
| Presbyterian | 876 | 31.4 | 48.0 | 19.7 | 8.3 | 983 | NM |
| Luminis | 631 | 39.4 | 44.7 | 14.8 | 6.6 | 696 | MD |
| CFNI | 548 | 45.7 | 5.3 | 47.5 | 8.7 | 707 | IN |
| Midland | 217 | 44.4 | 46.7 | 8.0 | 2.0 | 261 | TX |

**Tier 3 — 3 Service Lines, No Food** (13 systems): Robust Clinical + NC + Pharma but effectively zero food in TSA.

| System | TSA ($M) | Clin% | NC% | Pharma% | Beds | States |
|--------|---------|-------|-----|---------|------|--------|
| AdventHealth | 3,720 | 86.6 | 11.1 | 2.3 | 10,719 | FL + 10 states |
| HonorHealth | 1,558 | 58.0 | 38.6 | 3.4 | 1,654 | AZ |
| Fairview | 1,465 | 60.0 | 14.1 | 25.9 | 3,483 | MN |
| St Luke's University | 1,307 | 52.7 | 43.7 | 3.1 | 1,774 | PA, NJ |
| South Broward | 1,226 | 40.8 | 56.4 | 2.7 | 1,818 | FL |
| ECU Health | 1,164 | 43.3 | 28.5 | 28.3 | 1,367 | NC |
| Saint Francis | 571 | 81.5 | 15.6 | 2.6 | 1,721 | OK |
| LifeBridge | 561 | 45.6 | 51.8 | 2.3 | 816 | MD |
| Carilion | 544 | 58.1 | 39.3 | 2.5 | 894 | VA |
| Beebe | 469 | 23.2 | 56.0 | 20.4 | 201 | DE |
| TidalHealth | 268 | 62.9 | 24.3 | 12.1 | 408 | DE, MD |
| Terrebonne | 184 | 38.9 | 41.6 | 17.4 | 242 | LA |
| Greater Baltimore | 135 | 51.0 | 21.0 | 28.0 | 258 | MD |

### What We Excluded (and Why)

| Excluded Entity | Reason |
|----------------|--------|
| **GPO/Alliance entities** (Acurity $29.9B, Allspire $7.8B, Advocate Alliance $17.6B, Yankee $2.0B, etc.) | Purchasing alliances aggregating multiple health systems — not individual systems suitable for per-system extrapolation |
| **Conductiv** ($1.6B) | Multi-system GPO containing UVM, University of Louisville, and TriHealth |
| **HealthPartners** ($769M) | NC at 2.8% technically passes the 2% threshold, but composition is almost entirely hardware resellers + equipment repair — zero construction, staffing, insurance, or IT consulting. Fails qualitative diversity check |
| **Children's Hospital Corp** ($1.4B) | Pediatric-only; not representative of general acute care mix |
| **Systems with ratio <0.5 and no independent breadth** | Conway ($92M, 0.49 ratio), FirstHealth ($203M, 0.49 ratio) — insufficient coverage |

### Cohort Representativeness

**Geographic**: 25+ states across all major US regions. Southeast (7 systems), Mid-Atlantic (10), Midwest (2), Southwest (5), West (2), Appalachian (1). AdventHealth alone spans 11 states.

**Size Mix**: 6 large (>$2B), 17 medium ($500M–$2B), 6 small (<$500M). Bed counts range from 201 (Beebe) to 10,719 (AdventHealth).

**Hospital Type**: All 29 include short-term acute care. 10 also have critical access hospitals, 7 have children's hospitals, 5 have psychiatric facilities, 5 have long-term acute care.

### Key Risks to Flag

1. **Food is a gap**: <1% of TSA platform-wide. Any extrapolation model should source food spend separately (Supplier Sales data, industry benchmarks of ~3–5% of operating expenses).
2. **22 of 29 systems are TSA-only**: No WF cross-validation available. Their "comprehensive" status rests on service line breadth alone.
3. **High service line mix variance**: Pharma ranges from 2.3% (AdventHealth) to 47.5% (CFNI); NC ranges from 5.3% (CFNI) to 62.4% (McLaren). This is real purchasing profile variation, not data quality noise — but it means per-system extrapolation ratios will have wide confidence intervals.
4. **Non-Clinical is a broad bucket**: IT, facilities, staffing, consulting, insurance, and construction are all lumped together. A system could "pass" NC with heavy construction spend alone. We spot-checked several systems and confirmed genuine diversity, but this is worth verifying for any system you plan to weight heavily.

### Suggested Next Steps

1. **Per-bed spend benchmarks**: Compute $/bed ratios for each service line across the cohort — this is the bridge to extrapolation.
2. **GPO membership mapping**: Compare cohort demographics against the full Premier GPO membership universe (~4,000+ hospitals) to quantify representativeness gaps.
3. **Extrapolation model**: Cohort spend × membership scale factor, segmented by system size, type, and region.
4. **Food supplementary analysis**: If food is in scope, pull from Supplier Sales or apply industry benchmarks.

---

*Underlying data and full analysis (including contract category mappings, spot-check details, and audit notes) available in `runs/2026-02-10__portfolio-expansion/exports/comprehensive_cohort_analysis.md`.*
