# CAPS/503B Category Validation Slice — Summary

**Generated:** 2025-01-27  
**Timeframe:** 24 months (January 2024 – December 2025)  
**NDC Cohort:** 71 NDCs (B. Braun / Fresenius Kabi IV therapy products)

---

## Data Sources

| Source | Table | Key Fields |
|--------|-------|------------|
| **Provider ERP** | `transaction_analysis_expanded` | `Premier_Entity_Code`, `Ndc`, `Transaction_Date`, `Landed_Spend`, `Quantity` |
| **Wholesaler Tracing** | `report_builder` | `facility_id`, `ndc`, `month_year`, `total_spend`, `total_units` |

**Join Key:** `Premier_Entity_Code` (provider) → `facility_id` (wholesaler)  
*(Empirically validated: 117 of 2,180 wholesaler facility_ids matched; Facility_Code yielded 0 matches)*

---

## Coverage Analysis (Top 300 by Combined Spend)

### Distribution by Feed Overlap

| Coverage Type | Description | Prevalence |
|---------------|-------------|------------|
| **PROVIDER_ONLY** | Facility has ERP purchasing data but no wholesaler tracing | Dominant |
| **WHOLESALER_ONLY** | Facility has wholesaler tracing but no ERP purchasing data | Moderate |
| **BOTH** | Cross-feed overlap on facility + month + NDC | Rare |

### Top Health Systems by Data Feed

**Provider ERP (PROVIDER_ONLY):**
- ECU HEALTH
- BAPTIST HEALTH SOUTH FLORIDA
- UPMC HEALTH SYSTEM
- SUMMA HEALTH
- METHODIST HEALTH SYSTEM
- BAPTIST HEALTHCARE SYSTEM

**Wholesaler Tracing (WHOLESALER_ONLY):**
- NORTHWESTERN MEMORIAL HEALTHCARE
- CONDUCTIV
- ST LUKE'S UNIVERSITY HEALTH NETWORK
- COMMONSPIRIT HEALTH

**Cross-Feed Overlap (BOTH):**
- TEXAS HEALTH RESOURCES
- H. LEE MOFFITT HOSPITAL CENTER
- TIDALHEALTH INC
- ACURITY FKA GNYHA SERVICES, INC.

---

## Key Observations

1. **Sparse Overlap:** Most facility-month-NDC combinations appear in only one feed, limiting direct cross-validation.

2. **Spend Alignment (where BOTH exist):**
   - Some records show perfect alignment: e.g., TX0226 (Texas Health Resources) @ $4,069.15 provider = $4,069.15 wholesaler → **delta = $0**
   - Others show significant gaps: e.g., 714817 (ECU Health) @ $228,750 provider vs. $1,647 wholesaler → **delta = $227K+**

3. **Large Provider-Only Concentrations:**
   - Baptist Health South Florida: Multi-$100K monthly transactions on IV fluids (65219047410, 65219047910, 65219047030)
   - ECU Health: High-volume NDC 65219046850 and 65219038910

4. **Wholesaler-Specific Facilities:**
   - Northwestern Memorial Healthcare and Conductiv appear primarily in wholesaler tracing with minimal/no ERP data

---

## Sample Records (Top 10 by Spend)

| Facility | Month | NDC | Coverage | Provider Spend | Wholesaler Spend | Delta |
|----------|-------|-----|----------|----------------|------------------|-------|
| 714817 | 2025-07 | 65219046850 | BOTH | $228,750 | $1,647 | $227,103 |
| FL2221 | 2025-04 | 65219047410 | PROVIDER_ONLY | $212,872 | — | — |
| FL2221 | 2025-05 | 65219047410 | PROVIDER_ONLY | $128,725 | — | — |
| 799963 | 2024-10 | 65219038910 | PROVIDER_ONLY | $116,762 | — | — |
| 714817 | 2024-11 | 65219038910 | PROVIDER_ONLY | $114,911 | — | — |
| IL2386 | 2024-01 | 65219025810 | WHOLESALER_ONLY | — | $7,721 | — |
| 674291 | 2024-10 | 65219038910 | WHOLESALER_ONLY | — | $7,246 | — |
| PA2111 | 2025-05 | 65219046850 | WHOLESALER_ONLY | — | $6,068 | — |
| TX0226 | 2024-08 | 65219047410 | BOTH | $4,069 | $4,069 | $0 |
| TX2003 | 2024-10 | 65219047910 | BOTH | $2,704 | $1,832 | $872 |

---

## Artifacts

| File | Description |
|------|-------------|
| `caps_503b_validation_slice__integrated_comparison.sql` | Reusable BigQuery SQL for full dataset |
| `caps_503b_validation_slice__provider_sample.sql` | Provider-only aggregate query |
| `caps_503b_validation_slice__wholesaler_sample.sql` | Wholesaler-only aggregate query |

---

## Next Steps

1. **Expand overlap analysis:** Investigate why high-spend provider facilities have minimal wholesaler tracing coverage
2. **NDC category enrichment:** Map NDCs to product descriptions for easier interpretation
3. **Temporal trend analysis:** Track month-over-month spend patterns across feeds
