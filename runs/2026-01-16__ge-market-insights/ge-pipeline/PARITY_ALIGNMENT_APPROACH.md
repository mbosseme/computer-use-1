# Parity Alignment Approach: Transaction Analysis vs Supplier Spend

> **Purpose:** Reference document for aligning two disparate data models to enable apples-to-apples spend comparison. Developed for the GE Market Insights Pilot; generalizable to any provider-vs-supplier reconciliation.

---

## 1. The Problem

We have two data sources reporting "spend" for the same products at the same facilities, but they don't match:

| Dimension | Transaction Analysis (Provider) | Supplier Spend (Manufacturer) |
|-----------|--------------------------------|------------------------------|
| **Source** | Health system ERPs (POs/Invoices) | Manufacturer sales tracings |
| **Reporter** | Facility submits to Premier | Manufacturer reports to Premier |
| **Timing field** | `Transaction_Date` (PO submission) | `Spend_Period_YYYYQMM` (invoice/booking) |
| **Facility type field** | `Member_Type` | `Facility_Type` |
| **Manufacturer field** | `Manufacturer_Top_Parent_Name` | `Contracted_Supplier_Parent_Name` |
| **Spend field** | `Base_Spend` | `Premier_Spend` |

**Why they differ:**
- Different reporting timing (PO date vs invoice date)
- Different entity naming conventions
- Different scope (provider data is what facilities chose to send; supplier data is contract-only)
- Different categorization granularity

---

## 2. Alignment Strategy: Five Dimensions

To compare these datasets, we aligned on **five dimensions**:

### Dimension 1: Time Period
**Problem:** Different date fields with different semantics.

**Solution:** Align to the same 24-month window using comparable date extractions.

```sql
-- Transaction Analysis: Use Transaction_Date
WHERE DATE(Transaction_Date) BETWEEN DATE('2023-10-01') AND DATE('2025-09-30')

-- Supplier Spend: Decode Spend_Period_YYYYQMM to a date
-- Format: YYYYQMM where 2024410 = October (10) of Q4 2024
DATE(
  CAST(LEFT(CAST(Spend_Period_YYYYQMM AS STRING), 4) AS INT64),  -- year
  CAST(RIGHT(CAST(Spend_Period_YYYYQMM AS STRING), 2) AS INT64), -- month
  1  -- first of month
) as spend_date

WHERE spend_date BETWEEN DATE('2023-10-01') AND DATE('2025-09-30')
```

**Note:** Even with aligned windows, timing semantics differ. Provider `Transaction_Date` is when the facility submitted the PO; Supplier `Month` is when the manufacturer recorded the sale. This causes systematic Q4 divergence (see Section 5).

---

### Dimension 2: Facility Type
**Problem:** Different field names and potentially different value encoding.

**Solution:** Filter both to Acute-care facilities using the equivalent field.

```sql
-- Transaction Analysis
WHERE Member_Type = 'ACUTE'

-- Supplier Spend
WHERE Facility_Type = 'ACUTE'
```

**Validation:** Confirmed both fields have 'ACUTE' as a top value with similar facility counts.

---

### Dimension 3: Product Category
**Problem:** Both use `Contract_Category` but need to ensure exact match on target categories.

**Solution:** Explicit category list applied to both sources.

```sql
-- Both sources (identical filter)
WHERE Contract_Category IN (
  'COMPUTED TOMOGRAPHY',
  'MAGNETIC RESONANCE IMAGING', 
  'PHYSIOLOGICAL MONITORING SYSTEMS'
)
```

**Note:** Supplier Spend has a `Capital_Equipment_Flag` (Y/N) that Transaction Analysis lacks. For capital-specific analysis, we supplemented with a price threshold heuristic on the provider side:

```sql
-- Transaction Analysis capital proxy (no explicit flag available)
WHERE Base_Each_Price > 25000
  AND NOT REGEXP_CONTAINS(UPPER(Product_Description), 
      r'SERVICE|MAINTENANCE|WARRANTY|AGREEMENT|REPAIR|SOFTWARE|LICENSE|RENEWAL')
```

---

### Dimension 4: Entity/Manufacturer Name Normalization
**Problem:** Manufacturer names differ between sources.
- Transaction Analysis: `Manufacturer_Top_Parent_Name`
- Supplier Spend: `Contracted_Supplier_Parent_Name`

These often don't match exactly (e.g., "GE HEALTHCARE" vs "GE HEALTHCARE TECHNOLOGIES INC.").

**Solution:** Build a lookup table from Transaction Analysis (source of truth for entity names) and join to Supplier Spend.

```sql
-- Lookup table: Extract entity codes → names from Transaction Analysis
WITH manufacturers AS (
  SELECT DISTINCT
    Manufacturer_Top_Parent_Entity_Code as entity_code,
    Manufacturer_Top_Parent_Name as entity_name
  FROM transaction_analysis_expanded
  WHERE Manufacturer_Top_Parent_Entity_Code IS NOT NULL
),
vendors AS (
  SELECT DISTINCT
    Vendor_Top_Parent_Entity_Code as entity_code,
    Vendor_Top_Parent_Name as entity_name
  FROM transaction_analysis_expanded
  WHERE Vendor_Top_Parent_Entity_Code IS NOT NULL
)
SELECT entity_code, MAX(entity_name) as entity_name
FROM (SELECT * FROM manufacturers UNION ALL SELECT * FROM vendors)
GROUP BY 1

-- Then in Supplier Spend staging:
SELECT
  COALESCE(lookup.entity_name, s.Contracted_Supplier_Parent_Name) as manufacturer_name,
  ...
FROM supplier_spend s
LEFT JOIN lookup_table lookup
  ON s.Contracted_Supplier_Parent_Entity_Code = lookup.entity_code
```

**Key insight:** Entity codes (like `NJ2019`) are stable identifiers across both systems, even when display names differ.

---

### Dimension 5: Data Quality Exclusions
**Problem:** Both sources contain anomalies that distort comparison.

**Solution:** Apply exclusion rules to both sources.

#### Transaction Analysis Exclusions:
```sql
-- Exclude test/demo entities
WHERE NOT (
    UPPER(Health_System_Name) LIKE '% TEST' OR
    UPPER(Health_System_Name) LIKE '% TEST %' OR
    UPPER(Health_System_Name) LIKE '%PREMIER%' OR
    UPPER(Health_System_Name) LIKE '% DEMO' OR
    UPPER(Health_System_Name) LIKE '% DEMO %'
)

-- Exclude known bad data loads (temporary, document reason)
AND Health_System_Name != "ST. JOSEPH'S - CANDLER HEALTH SYSTEM, INC."

-- Exclude outlier transactions (data entry errors)
AND Base_Spend <= 10000000
```

#### Coverage-Based Exclusions (Applied After Initial Aggregation):
Some facilities appear in Transaction Analysis but have little/no Supplier Spend coverage (they may not be on Premier contracts for these categories). Exclude facility-quarters with <10% coverage:

```sql
-- Identify low-coverage facility-quarters
SELECT
  t.Health_System_Entity_Code,
  t.year_quarter,
  t.total_transaction_spend,
  COALESCE(s.total_supplier_spend, 0) as total_supplier_spend,
  SAFE_DIVIDE(s.total_supplier_spend, t.total_transaction_spend) as coverage_ratio
FROM transaction_agg t
LEFT JOIN supplier_agg s ON t.Health_System_Entity_Code = s.Health_System_Entity_Code
WHERE coverage_ratio < 0.10 OR s.total_supplier_spend IS NULL
```

---

## 3. Resulting Staging Views

We implemented the alignment as Dataform staging views:

| View | Source | Purpose |
|------|--------|---------|
| `stg_transaction_parity_basis` | Transaction Analysis | Provider-side spend, filtered and normalized |
| `stg_supplier_spend_parity` | Supplier Spend | Supplier-side spend, filtered with name lookup |
| `int_supplier_parent_lookup` | Transaction Analysis | Entity code → name mapping table |
| `int_parity_exclusion_list` | Both (joined) | Facility-quarters to exclude from comparison |

---

## 4. Aggregation Grain

For comparison, aggregate both sources to the same grain:

```sql
-- Common aggregation grain
SELECT
  Health_System_Entity_Code,
  FORMAT_DATE('%Y-Q%q', date_field) as year_quarter,  -- or month
  Contract_Category,
  manufacturer_name,  -- normalized
  SUM(spend) as total_spend
FROM staging_view
GROUP BY 1, 2, 3, 4
```

Then join:
```sql
SELECT
  COALESCE(t.Health_System_Entity_Code, s.Health_System_Entity_Code) as entity_code,
  COALESCE(t.year_quarter, s.year_quarter) as year_quarter,
  COALESCE(t.manufacturer_name, s.manufacturer_name) as manufacturer,
  t.total_spend as provider_spend,
  s.total_spend as supplier_spend,
  t.total_spend - s.total_spend as delta
FROM transaction_agg t
FULL OUTER JOIN supplier_agg s
  ON t.Health_System_Entity_Code = s.Health_System_Entity_Code
  AND t.year_quarter = s.year_quarter
  AND t.manufacturer_name = s.manufacturer_name
```

---

## 5. Known Residual Differences (Timing Reconciliation)

Even after alignment, systematic differences remain—**this is expected**.

### The "Two Clocks" Problem
- **Provider clock:** `Transaction_Date` = when facility submitted PO (can precede invoice)
- **Supplier clock:** `Month` = when manufacturer recorded the sale (typically invoice timing)

### Q4 Amplification
Year-end creates larger gaps:
- Provider PO-based data may record December purchases in October/November (when PO was submitted)
- Supplier invoice-based data records them in December (when invoiced)
- Fiscal year-end accounting adjustments compound the effect

### How We Handled It
We did **not** try to eliminate timing differences. Instead, we:
1. Documented the root cause (different accounting clocks)
2. Quantified the magnitude (quarterly overlays show the pattern)
3. Framed it as a "timing reconciliation" rather than a data error
4. Used indexed comparisons (normalize each source to its own baseline) for trend analysis

---

## 6. Checklist for Applying This Approach

When aligning any two spend datasets:

- [ ] **Time period:** Identify date fields; align to same window; document semantic differences
- [ ] **Facility scope:** Find equivalent facility type filters; validate value overlap
- [ ] **Product scope:** Use identical category/product filters on both sides
- [ ] **Entity normalization:** Build lookup table using stable identifiers (codes > names)
- [ ] **Exclusions:** Remove test data, known anomalies, outliers
- [ ] **Coverage filter:** Exclude entities with sparse coverage on one side
- [ ] **Aggregation grain:** Match grain before comparing (entity × period × category × manufacturer)
- [ ] **Residual differences:** Document rather than force-fit; timing and scope differences are often legitimate

---

## 7. Reference Implementation

See these files in the ge-sample repo:

| File | Purpose |
|------|---------|
| `dataform/definitions/staging/stg_transaction_parity_basis.sqlx` | Provider staging view |
| `dataform/definitions/staging/stg_supplier_spend_parity.sqlx` | Supplier staging view |
| `dataform/definitions/staging/int_supplier_parent_lookup.sqlx` | Name normalization lookup |
| `dataform/definitions/staging/int_parity_exclusion_list.sqlx` | Coverage-based exclusions |
| `dataform/definitions/marts/mart_parity_analysis.sqlx` | Final comparison mart |
| `scripts/analyze_q4_seasonality.py` | Timing reconciliation analysis |

---

*Developed for GE Market Insights Pilot, January 2026.*
