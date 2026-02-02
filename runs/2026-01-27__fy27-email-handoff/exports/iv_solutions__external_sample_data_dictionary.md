# B. Braun IV Solutions Sample Data Cut — Data Dictionary

**Generated:** 2026-01-28  
**Run ID:** 2026-01-27__fy27-email-handoff  
**Sample Period:** January 2024 – December 2025 (24 months)

---

## Overview

This dataset contains de-identified facility-level purchasing data for B. Braun IV Solutions products, combining:
- **Provider ERP purchasing** (Transaction Analysis Expanded) — direct facility purchases
- **Wholesaler tracing** (Report Builder) — distributor-intermediated sales

Data is provided at the facility-month-product grain with a source indicator.

---

## Column Definitions

| Column | Type | Description |
|--------|------|-------------|
| `blinded_facility_id` | STRING | De-identified facility identifier (format: `FAC_00001`). Consistent within this dataset; cannot be linked to real facility names. |
| `month_year` | INTEGER | Year-month in YYYYMM format (e.g., 202401 = January 2024) |
| `ndc11` | STRING | 11-digit National Drug Code identifying the specific product/package |
| `reference_number` | STRING | Premier contract reference number (NULL for wholesaler records) |
| `spend` | FLOAT | Total dollar spend for this facility-month-product combination |
| `units` | FLOAT | Total units purchased for this facility-month-product combination |
| `source_flag` | STRING | Data source: `ERP` (Provider direct) or `WHOLESALER` (distributor tracing) |

---

## Important Notes

### Data Interpretation

1. **UNION, not de-duplicated**: ERP and WHOLESALER records are complementary views of purchasing activity. A facility-month-product may appear in BOTH sources — this is expected and represents visibility from different channels.

2. **Reference Number availability**: Only ERP records have `reference_number`; wholesaler records use NDC-only tracking.

3. **Spend values**: Dollar amounts represent landed cost (ERP) or reported sales value (wholesaler). Minor methodology differences may exist.

4. **Unit definitions**: Units represent package/each counts. Unit-of-measure may vary by NDC.

### Coverage Characteristics

- **Facility scope**: Includes all facilities with purchasing activity, not limited to Premier members
- **Product scope**: IV Solutions NDCs associated with B. Braun contracts
- **Time scope**: Full 24 months (Jan 2024 – Dec 2025)

### De-identification

- Real facility identifiers have been replaced with blinded IDs
- Blinded IDs are consistent within this dataset but cannot be traced to actual facilities
- No protected health information (PHI) is included

---

## Source Data Models

| Source | Description |
|--------|-------------|
| **ERP** | Transaction Analysis Expanded — Provider ERP purchasing data captured directly from facility systems |
| **WHOLESALER** | Report Builder — Wholesaler/distributor sales tracing data |

---

## Validation

This dataset has been validated against manufacturer-reported on-contract sales (CAMS). Combined ERP + WHOLESALER spend exceeds manufacturer-reported by ~10%, indicating the dataset captures both on-contract and incremental off-contract/spot purchasing activity.

