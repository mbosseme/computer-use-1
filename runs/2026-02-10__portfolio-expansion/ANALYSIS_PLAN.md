# Analysis Plan: Identifying Representative Health Systems in TSA

**Date**: 2026-02-10
**RUN_ID**: `2026-02-10__portfolio-expansion`
**Objective**: Identify ≥20 health systems in the TSA data model that provide a comprehensive view of non-labor purchasing activity across all major service lines, suitable for extrapolation to Premier's GPO membership (~25% of US healthcare) and potentially to US health systems broadly.

---

## Definitions

### "Comprehensive" Health System
A health system is considered **comprehensive** if it meets ALL of the following criteria:

1. **Volume Match**: TSA captures ≥85% of the Workflow History spend (after cleanup — see below) for calendar year 2025.
2. **Full Year Coverage**: The health system has transactional data in **all 12 months** of 2025 in **both** data models.
3. **Service Line Breadth**: Meaningful spend volume in **all four** service line buckets:
   - **Clinical**: Medical/surgical supplies, implants, devices
   - **Non-Clinical**: IT, HR, facilities, administrative services, construction, utilities
   - **Pharma**: Pharmaceuticals, vaccines, pharmacy operations, drug distributors
   - **Food**: Dietary, cafeteria, nutrition services

### Workflow Cleanup Rules (before comparison)
Before computing the capture ratio, apply these filters to Workflow History:
- **Remove intercompany/internal transfers**: Vendor names matching the health system's own name or known internal entities
- **Remove overhead allocations**: `HOSPITALS SERVICES EXPENSES`, `UNKNOWN`, `MEDSERVE` (pseudo-vendors, not real invoices)
- **Remove outlier invoices**: Any single invoice with `invoice_total_amount > $20,000,000`
- **Remove government/regulatory payments**: e.g., "AGENCY FOR HEALTH CARE ADMINISTRATION", Medicaid/regulatory payments

### Service Line Classification
For TSA, use `Contract_Category` + `UNSPSC_Segment_Code` + vendor name patterns to classify into service lines.
For Workflow, use vendor name pattern matching (the categorization waterfall from the OSF deep dive).

---

## Phase 1: Establish the Universe

### Step 1.1 — Identify Health Systems Present in Both Data Models
Query both tables for health systems with data in CY2025. Join by name (since entity codes are broken in Workflow).

```
Goal: List of health systems that appear in BOTH Workflow History and TSA for 2025.
Approach: 
  - From Workflow: SELECT DISTINCT health_system_name, SUM(spend), COUNT(DISTINCT months)
  - From TSA: SELECT DISTINCT Health_System_Name, SUM(spend), COUNT(DISTINCT months)
  - Cross-reference by name (fuzzy + exact)
  - Filter to systems with all 12 months in both
```

**Output**: A candidate list of health systems with spend totals from both models and month coverage.

### Step 1.2 — Filter to Full-Year Coverage
Keep only health systems with data in all 12 months of 2025 in BOTH data models. This eliminates partial-year representations.

### Step 1.3 — Pre-Screen by Existing Mapped Systems
Start with the 9 already-mapped systems (validation known-good). Then expand.

---

## Phase 2: Compute Adjusted Capture Ratios

### Step 2.1 — Clean Workflow Spend (Per Health System)
For each candidate health system, compute the **adjusted Workflow spend** by removing:
1. Invoices > $20M (outliers)
2. Intercompany/internal vendors (system-specific name patterns)
3. Overhead allocations (HOSPITALS SERVICES EXPENSES, UNKNOWN, MEDSERVE)
4. Government/regulatory payments

This gives us the "cleaned Workflow total" — the best estimate of what comprehensive non-labor purchasing spend looks like.

### Step 2.2 — Compute Capture Ratio
```
Capture Ratio = TSA Spend / Cleaned Workflow Spend
```

Where:
- Numerator = SUM(Landed_Spend) from TSA for CY2025
- Denominator = SUM(invoice_total_amount) from Workflow after cleanup for CY2025

Target: **Capture Ratio ≥ 0.85** (TSA has at least 85% of the cleaned Workflow spend)

### Step 2.3 — Investigate Anomalies
For systems with capture ratio > 1.0 (TSA > Workflow), investigate whether:
- The Workflow data is incomplete (e.g., Remitra-only system with limited ERP coverage)
- TSA includes overhead allocation categories that inflate it
- The system submitted invoice-only data to TSA on top of PO/receipt data

For systems with very low capture ratio (< 0.5), investigate whether:
- Entity split issue (like Advocate/Aurora)
- Workflow includes a parent entity that TSA tracks under a different name

---

## Phase 3: Service Line Breadth Assessment

### Step 3.1 — Classify TSA Spend into Service Lines
For each candidate health system, classify TSA spend into the 4 service line buckets using a combination of:

**Primary classifier: `Contract_Category`** (~870 distinct values)
- Map the major Contract_Category values into the 4 buckets
- Use `UNSPSC_Segment_Code` as a secondary classifier for UNKNOWN categories

**Bucket mapping logic (heuristic, to be refined with data)**:
| Service Line | Contract_Category patterns | UNSPSC Segments | Vendor patterns |
|---|---|---|---|
| Clinical (Med/Surg) | BANDAGES, SUTURES, IV THERAPY, ORTHOPEDIC, SURGICAL, EXAM GLOVES, PATIENT BEDSIDE, etc. | 42 (Medical), 41 (Lab) | Medline, J&J, BD, Stryker, Medtronic, Boston Scientific |
| Non-Clinical | OFFICE SUPPLIES, IT, SOFTWARE, COPIERS, FURNITURE, JANITORIAL, PRINTING, UNIFORMS | 43 (Computing), 44 (Office), 80 (Services), 72 (Building) | CDW, Staples, Cintas |
| Pharma | PHARMACEUTICALS, PHARMACY, VACCINES, IV FLUIDS DRUG-BASED | 51 (Drugs) | AmerisourceBergen, McKesson, Cardinal Health (pharma), FFF Enterprises |
| Food | FOOD SERVICE, DIETARY, NUTRITION | 50 (Food/Bev) | Sysco, US Foods, Compass Group |

### Step 3.2 — Test for Meaningful Volume
"Meaningful volume" means:
- The service line represents at least **2%** of the system's total TSA spend, OR
- The service line has at least **$5M** in annual spend

Systems that have only Clinical (med/surg) and nothing else are NOT comprehensive — they're just sending basic supply chain purchasing data.

### Step 3.3 — Compute Service Line Mix Profile
For each comprehensive candidate, compute:
- % Clinical, % Non-Clinical, % Pharma, % Food
- Compare to the Workflow-derived "true" mix for the validated systems
- Flag outliers (e.g., a system with 0% IT spend is likely not submitting non-clinical)

---

## Phase 4: Identify the Comprehensive Cohort

### Step 4.1 — Apply All Filters
Combine the results from Phases 2 and 3:
1. ✅ Present in both data models for all 12 months of 2025
2. ✅ Capture ratio ≥ 85%
3. ✅ Meaningful volume in all 4 service line buckets

### Step 4.2 — Validate Against Advocate Exemplar
Compare the service line mix of qualifying systems against Advocate (the known exemplar of comprehensive submission). Systems should have a broadly similar distribution pattern.

### Step 4.3 — Demographic Representativeness
Using the `sa_sf_dhc_join` reference table (joined on entity codes), assess whether the cohort is demographically representative:
- **Geographic distribution**: states/regions
- **Size distribution**: bed counts, net patient revenue
- **Type distribution**: academic vs community, urban vs rural
- **System size**: number of facilities per system

If the cohort is skewed (e.g., all large urban academic centers), note this as a limitation for extrapolation.

---

## Phase 5: Expand Beyond Validated Mappings

### Step 5.1 — TSA-Only Signature Detection
For systems NOT in Workflow (or where we can't establish a mapping), look for the "comprehensive signature" in TSA alone:
- Service line mix similar to the validated comprehensive systems
- Presence of non-clinical categories (IT, facilities, construction)
- Presence of pharma distributors and food vendors
- Invoice-like transaction patterns (fewer line items per "order", broader vendor mix)

### Step 5.2 — Screen All Large TSA Systems
Query TSA for all health systems with >$500M in 2025 spend, full 12-month coverage, and compute their service line distribution. Compare against the "comprehensive" profile to identify additional candidates.

### Step 5.3 — Final Cohort Assembly
Combine:
- Workflow-validated comprehensive systems (from Phase 4)
- TSA-only comprehensive candidates (from Phase 5)

Target: ≥20 systems. If fewer than 20, note the gap and assess whether the available cohort is still analytically useful.

---

## Phase 6: Deliverables

### 6.1 — Comprehensive Health System List
Table with:
- Health system name (both model names where applicable)
- TSA spend, Workflow spend, capture ratio
- Service line mix (% breakdown)
- Demographics (beds, state, type, NPR)
- Data quality notes

### 6.2 — Service Line Spend Summary
Aggregate across the cohort:
- Total spend per service line
- Average mix percentages
- Vendor concentration (top 10 vendors per service line)

### 6.3 — Representativeness Assessment
Comparison of the cohort to the broader Premier membership and/or US hospital universe:
- How well does it cover different geographies, sizes, and types?
- What extrapolation caveats should be noted?

### 6.4 — Methodology Documentation
Reusable SQL and logic for:
- The vendor categorization waterfall (Workflow cleanup)
- The service line classification rules (TSA categories)
- The capture ratio computation
- The health system name mapping table

---

## Execution Order

| Step | Phase | Description | Dependencies | Est. Queries |
|------|-------|-------------|-------------|-------------|
| 1 | 1.1 | List health systems in both models, 2025, with months | None | 2 |
| 2 | 1.2 | Filter to 12-month coverage in both | Step 1 | 1 |
| 3 | 2.1 | Clean Workflow spend for each candidate | Step 2 | 1–3 per system |
| 4 | 2.2 | Compute capture ratios | Step 3 | 1 |
| 5 | 3.1 | Classify TSA spend by service line | Step 2 | 1–2 |
| 6 | 3.2–3.3 | Service line breadth + mix profile | Step 5 | 1 |
| 7 | 4.1–4.3 | Apply filters, validate, assess demographics | Steps 4+6 | 2–3 |
| 8 | 5.1–5.3 | TSA-only expansion | Step 7 | 2–3 |
| 9 | 6.x | Compile deliverables | All | — |

**Critical path**: Steps 1→2→3→4 and 1→2→5→6 can run in parallel, merging at Step 7.

---

## Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Too few systems pass all filters (< 20) | Weak extrapolation basis | Relax capture ratio to 75%, or accept a smaller but well-characterized cohort |
| Vendor categorization heuristics misclassify significant spend | Incorrect service line mix | Spot-check top 20 vendors per system; refine CASE logic iteratively |
| Health system name matching produces false joins | Incorrect capture ratios | Manual review of top candidates; leverage entity codes where available |
| TSA overhead categories ($HSE, $UNKNOWN) distort TSA side | Inflated capture ratios | Flag and potentially exclude HSE/UNKNOWN from TSA when computing ratios |
| The "comprehensive" systems are systematically different from non-comprehensive ones | Selection bias in extrapolation | Assess demographics; document limitations |

---

## Success Criteria

- ✅ ≥20 health systems identified as comprehensive (all 4 criteria met)
- ✅ Cohort covers multiple states/regions, size classes, and system types
- ✅ Service line mix is consistent across the cohort (low variance)
- ✅ Methodology is documented and reusable
- ✅ Clear articulation of confidence: "Yes, this is representative enough" or "No, here's what's missing"
