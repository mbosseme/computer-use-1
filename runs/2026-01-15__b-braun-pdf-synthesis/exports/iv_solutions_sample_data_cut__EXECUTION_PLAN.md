# B. Braun IV Solutions Sample Data Cut — Execution Plan

**Created:** 2026-01-27  
**Run ID:** 2026-01-15__b-braun-pdf-synthesis  
**Status:** IN PROGRESS

---

## 1. Objective

Produce a de-identified facility-level sample data cut for Jen (B. Braun) covering 71 NDCs from her IV Solutions SKU list, integrating:
- **Provider ERP purchasing** (Transaction Analysis Expanded)
- **Wholesaler tracing** (Report Builder)

And validate combined totals against:
- **Manufacturer-reported on-contract sales** (CAMS Product Information View)

---

## 2. Source Data Models

| Feed | Table | Key Columns | Notes |
|------|-------|-------------|-------|
| **Provider ERP** | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` | `Premier_Entity_Code`, `Ndc`, `Reference_Number`, `Transaction_Date`, `Landed_Spend`, `Quantity`, `Manufacturer_Top_Parent_Entity_Code` | Partitioned by `Transaction_Date`; clustered by `Contract_Category`, `Manufacturer_Top_Parent_Name`, `Manufacturer_Name` |
| **Wholesaler Tracing** | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` | `facility_id`, `ndc`, `month_year`, `total_spend`, `total_units` | No Reference Number; NDC-only filtering |
| **Mfr Reported (Validation)** | `abi-xform-dataform-prod.continuum_of_care.cams_product_information_vw` | `premier_entity_code`, `reference_number`, `spend_period_yqmm`, `sales_volume_paid_reported`, `supplier_top_parent_entity_code` | Complete through Sep 2025 only |

---

## 3. Product Scope

### 3.1 NDC Cohort (Anchor)
- **71 NDCs** from Jen's list (extracted from `Re: Confirmed-BBraun MI Demo - virtual.pdf`)
- Stored at: `runs/2026-01-27__fy27-email-handoff/tmp/re_confirmed_bbraun_mi_demo_virtual__39e24a0260__ndcs_11.txt`
- Manufacturers: **Hikma/APP** (63323* prefix) and **Fresenius Kabi** (65219* prefix)

### 3.2 Reference Number Expansion Strategy
1. Match Jen's NDCs in TAE → extract distinct `Reference_Number` values
2. For each Reference Number, enumerate ALL NDCs tied to it in TAE
3. Use expanded NDC set when querying Report Builder (wholesaler)
4. Use Reference Numbers directly when querying CAMS (validation)

### 3.3 B. Braun Identification
- Filter by `supplier_top_parent_entity_code = '606326'` (or equivalent `manufacturer_top_parent_entity_code`)

---

## 4. Time Windows

| Purpose | Window | Months |
|---------|--------|--------|
| **External sample cut** | Jan 2024 – Dec 2025 | 24 |
| **Validation comparison** | Jan 2024 – Sep 2025 | 21 |

Reason: CAMS data is only complete through September 2025.

---

## 5. Execution Steps

### Phase A: Data Dictionary for CAMS Product Information View
- [ ] **A1.** Profile `cams_product_information_vw` schema + sample values
- [ ] **A2.** Generate data dictionary in standard format
- [ ] **A3.** Save to `docs/data_dictionaries/`

### Phase B: NDC → Reference Number Mapping
- [ ] **B1.** Query TAE for all rows matching Jen's 71 NDCs
- [ ] **B2.** Extract distinct (NDC, Reference_Number) pairs
- [ ] **B3.** Validate coverage (how many of 71 NDCs matched?)
- [ ] **B4.** Build expanded NDC list (all NDCs under matched Reference Numbers)

### Phase C: Pull Provider ERP Data (TAE)
- [ ] **C1.** Query TAE for expanded Reference Number set, Jan 2024 – Dec 2025
- [ ] **C2.** Aggregate to facility-month-reference_number grain
- [ ] **C3.** Include: `Premier_Entity_Code`, `month_year`, `reference_number`, `ndc11`, `landed_spend`, `quantity`, `health_system_name`

### Phase D: Pull Wholesaler Tracing Data (Report Builder)
- [ ] **D1.** Query Report Builder for expanded NDC set, Jan 2024 – Dec 2025
- [ ] **D2.** Aggregate to facility-month-ndc grain
- [ ] **D3.** Include: `facility_id`, `month_year`, `ndc11`, `total_spend`, `total_units`

### Phase E: Union Combined Dataset
- [ ] **E1.** Union TAE + RB with source flag (`ERP` vs `WHOLESALER`)
- [ ] **E2.** Align to common grain: `facility_id`, `month_year`, `ndc11` (or `reference_number` where available)
- [ ] **E3.** Do NOT de-duplicate — these are complementary feeds

### Phase F: Internal Validation (vs CAMS)
- [ ] **F1.** Query CAMS for B. Braun (entity code 606326) Reference Numbers from Phase B, Jan 2024 – Sep 2025
- [ ] **F2.** Aggregate CAMS to facility-quarter-reference_number grain
- [ ] **F3.** Aggregate combined TAE+RB to same grain (facility-quarter-reference_number), same time window
- [ ] **F4.** Join and compare: absolute spend delta, percent delta
- [ ] **F5.** Identify systematic gaps (missing facilities, missing products, time lags)

### Phase G: External Sample Preparation
- [ ] **G1.** De-identify: replace `Premier_Entity_Code` with `blinded_facility_id`
- [ ] **G2.** Include all facilities (not just Premier members)
- [ ] **G3.** Include: `blinded_facility_id`, `month_year`, `ndc11`, `reference_number`, `product_description`, `spend`, `units`, `source_flag`
- [ ] **G4.** Generate data dictionary for output fields
- [ ] **G5.** Generate coverage summary (num facilities, months, products, % with both sources)

---

## 6. Key Decisions (from Matt's clarifications)

1. **UNION, not de-dup** — TAE and RB are complementary channels; keep source flag
2. **Reference Number is the expansion key** — Match NDC → Reference # → expand to all NDCs under that Reference #
3. **Validation window = 21 months** (Jan 2024 – Sep 2025) due to CAMS completeness
4. **External sample = 24 months** (Jan 2024 – Dec 2025)
5. **B. Braun entity code = 606326** — use `supplier_top_parent_entity_code` or equivalent
6. **Same 71 NDCs** — the CAPS/503B work and this IV Solutions cut are the same scope

---

## 7. Artifacts to Produce

| File | Description |
|------|-------------|
| `docs/data_dictionaries/abi-xform-dataform-prod.continuum_of_care.cams_product_information_vw.md` | CAMS data dictionary (new) |
| `exports/iv_solutions__ndc_to_refnum_mapping.csv` | NDC → Reference Number mapping |
| `exports/iv_solutions__tae_facility_month_agg.sql` | TAE aggregation query |
| `exports/iv_solutions__rb_facility_month_agg.sql` | Report Builder aggregation query |
| `exports/iv_solutions__combined_union.sql` | Combined union query |
| `exports/iv_solutions__validation_vs_cams.sql` | Validation comparison query |
| `exports/iv_solutions__validation_summary.md` | Human-readable validation findings |
| `exports/iv_solutions__sample_data_cut.jsonl` | De-identified external sample (or CSV) |
| `exports/iv_solutions__sample_data_dictionary.md` | Data dictionary for sample output |
| `exports/iv_solutions__coverage_summary.md` | Coverage statistics |

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Some NDCs don't match in TAE | Diagnose: formatting, 10/11-digit normalization. Fallback: use Reference_Number_Surrogate |
| Reference Number expands too broadly | Validate top NDCs by spend under each Reference # are plausible (same product family) |
| Sparse cross-feed overlap | Expected; keep source separation; don't force de-dup |
| CAMS only through Sep 2025 | Use 21-month validation window; note in deliverable |
| Unit-of-measure mismatch | Prioritize spend comparisons; normalize units where possible |

---

## 9. Refer Back To

- [B Braun IV Solutions Sample Data Cut Briefing.md](../../runs/2026-01-27__fy27-email-handoff/inputs/B%20Braun%20IV%20Solutions%20Sample%20Data%20Cut%20Briefing.md) — strategic context
- [HANDOFF.md](HANDOFF.md) — run continuity
- [TAE data dictionary](../../docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md)
- [Report Builder data dictionary](../../docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder.md)

---

## 10. Execution Log

| Step | Status | Notes |
|------|--------|-------|
| A1. Profile CAMS schema | 🔄 IN PROGRESS | |
| A2. Generate CAMS data dictionary | ⏳ PENDING | |
| A3. Save data dictionary | ⏳ PENDING | |
| B1–B4. NDC → Reference Number mapping | ⏳ PENDING | |
| C1–C3. TAE aggregation | ⏳ PENDING | |
| D1–D3. Report Builder aggregation | ⏳ PENDING | |
| E1–E3. Union combined dataset | ⏳ PENDING | |
| F1–F5. Validation vs CAMS | ⏳ PENDING | |
| G1–G5. External sample preparation | ⏳ PENDING | |
