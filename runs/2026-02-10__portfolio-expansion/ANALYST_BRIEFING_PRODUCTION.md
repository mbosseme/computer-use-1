# Analyst Briefing Production Process

This document defines the steps, data dependencies, and validation checks required to produce or update the **Portfolio Expansion Analyst Briefing** (`runs/2026-02-10__portfolio-expansion/exports/analyst_briefing.md`). Any agent or analyst updating the briefing should follow this checklist to ensure all sections are internally consistent and externally validated.

---

## When to Re-Run This Process

Trigger a full or partial refresh whenever:
- Upstream Dataform pipeline changes (new tables, modified SQL, schema changes)
- Vendor name pattern expansion (affects WF classification rates and SL benchmarks)
- Cohort qualification criteria change (spend thresholds, category breadth rules)
- Service line mapping changes (`service_line_mapping.sqlx`)
- Bed source or GPO membership definition changes
- Any change to the WF entity-bridge logic (`entity_sl_mix`, `wf_sl_v4`)

---

## Prerequisites

1. **Dataform pipeline compiled and materialized** — `npx @dataform/cli@2.9.0 compile` (0 errors), then `npx @dataform/cli@2.9.0 run` from `dataform/` directory
2. **All assertions pass** — verify via `npx dataform test` or manual BQ assertion queries
3. **BigQuery tables current** — all 9 datasets in `matthew-bossemeyer.wt_2026_02_10__portfolio_expansion` reflect latest pipeline

---

## Scope & Boundaries (must be maintained in every revision)

This analysis is **health system and hospital-centric**. Both data sources (WF invoices and TSA transactions) are extracted from health system ERPs. The scope includes:

- **In scope**: Acute-care hospital purchasing, plus a small proportion of non-acute volume from facilities owned/leased/managed by the health system that share the same ERP.
- **Out of scope**: Independent non-acute and alternate-site facilities (retail pharmacies, specialty pharmacies, infusion centers, mail-order pharmacies, physician offices, non-system ambulatory surgery centers, etc.) that order directly through wholesaler/distributor platforms outside health system ERPs.

**Why this matters**: The non-acute/alternate-site market is enormous — CY2025 pharmaceutical wholesaler tracings alone show $123B in non-acute pharma volume, essentially as large as the entire GPO acute estimate. The briefing must clearly state that its estimates cover health system purchasing, not the broader healthcare market.

**Maintenance rule**: Every revision of the analyst briefing must include the "Analysis Scope" subsection in the Executive Summary. If the scope expands (e.g., to include alternate-site data), update both this section and the briefing scope statement.

---

## Pharma Wholesaler Tracing Cross-Check (validation step)

As an external validation of the pharma extrapolation, compare the GPO pharma range against CY2025 pharmaceutical wholesaler tracings for acute facilities:

| Source | Value | Notes |
|--------|-------|-------|
| GPO pharma extrapolation | $18B–$19B | WF mix × total non-labor range |
| Wholesaler tracings (acute) | $21.5B | Slightly broader footprint than GPO-only |
| Wholesaler tracings (non-acute/alternate site) | $123B | Out of scope — retail, specialty, infusion, mail order |

The acute tracing figure ($21.5B) slightly exceeding the GPO extrapolation ($18B–$19B) is expected: some acute-care hospitals participate in Premier's pharmacy purchasing program without being core clinical GPO members, so wholesaler tracings capture a somewhat broader acute footprint.

**Action**: If the GPO pharma extrapolation ever exceeds the acute wholesaler tracing figure, investigate — it would suggest either an overshoot in the WF pharma mix share or an undercount in the tracing data.

---

## Production Steps

### Step 1: WF Service Line Mix Benchmarks (Section I)

**Source tables**: `wf_sl_v4`, `vendor_name_patterns`, `entity_sl_mix`

1. Query classification layer breakdown (entity-bridge, name-pattern, exclude, unmatched) — totals and percentages
2. Compute cross-cohort SL benchmarks (primary 3-SL balanced cohort + 5 alternative definitions)
3. Compute system-level percentile distribution (Min, P10, P25, Median, Mean, P75, P90, Max) for the primary cohort
4. Verify TSA pharma cross-check: TSA `parent_service_line = 'Pharma'` share of total mapped TSA spend
5. Update sensitivity analysis: scenario table for matched-only, estimated actual, and extreme-pharma

**Key numbers to update**: Classification rate (%), unmatched pool ($B), cohort N, cohort classified spend, SL mix percentages, IQR ranges

### Step 2: TSA Clinical+NC Cohort (Section II)

**Source tables**: `tsa_clin_nc_cohort`, `tsa_cy2025_enriched`, `sa_sf_dhc_join_enriched`

1. Confirm cohort count and qualification criteria match the current pipeline
2. Query cohort summary: systems, bed-matched systems, total beds (hospital-only), total/clinical/NC/addressable spend
3. Compute per-bed rates: weighted average clinical, NC, and addressable per staffed bed
4. Query size distribution tiers (≥$1B, $500M–$1B, $100M–$500M, <$100M) with system count and beds
5. Query Top 25 systems table: system name, entity code, spend, clinical, NC, beds, $/bed
6. Verify excluded entities (alliances, test/demo) are still excluded

**Key numbers to update**: Cohort count, bed match rate, total beds, per-bed rates, tier distributions, Top 25 table

### Step 3: Per-Bed Extrapolation (Section III)

**Source tables**: `tsa_clin_nc_cohort`, `gpo_member_universe`

1. **Step 1 bench**: Weighted avg $/bed (Clinical, NC, Addressable) from cohort
2. **Step 2 GPO universe**: Query `gpo_member_universe` by hospital type — facility count and beds per type. Verify filter criteria (hospital types included/excluded) match current definition
3. **Step 3 total non-labor**: GPO beds × $/bed = C+NC addressable; ÷ 0.84 (WF C+NC share) = total non-labor
4. **SL decomposition**: Apply WF benchmark mix percentages to total non-labor
5. **Sensitivity**: Query P25/P50/P75 per-bed rates from cohort systems; compute impact range
6. **Cohort coverage**: Cohort beds ÷ GPO beds (%)

**Key numbers to update**: All per-bed rates, GPO universe counts/beds by type, extrapolation chain, SL decomposition table, sensitivity range

### Step 4: TSA Clinical Calibration Cross-Check (**CRITICAL** — Section III-B)

**Source table**: `tsa_cy2025_enriched` (all rows where `premier_gpo_member = TRUE`)

> **This step is the single most important validation in the briefing.** It anchors the extrapolation against directly observed data rather than relying solely on projected rates.

1. **Query TSA-observed GPO spend by service line**:
   ```sql
   SELECT parent_service_line,
          ROUND(SUM(Base_Spend)/1e9, 2) AS spend_B
   FROM tsa_cy2025_enriched
   WHERE premier_gpo_member = TRUE
   GROUP BY 1
   ```

2. **Compare extrapolated Clinical to TSA-observed Clinical**:
   - If extrapolated Clinical is **>15% above** TSA-observed → the per-bed rate is too high (likely cohort composition bias toward large academic systems)
   - If extrapolated Clinical is **<TSA-observed** → the per-bed rate is too low or the GPO bed count is understated

3. **Compute TSA-calibrated estimates**:
   - Floor: TSA-observed Clinical ($B)
   - Central: TSA-observed Clinical ÷ 0.95 (5% non-reporting assumption)
   - Upper: TSA-observed Clinical ÷ 0.92 (8% non-reporting assumption)
   - Scale each to total non-labor via WF mix: calibrated Clinical ÷ 0.428 (Clinical share)
   - Derive implied C+NC: total non-labor × 0.841
   - Derive implied per-bed rate: C+NC ÷ GPO beds

4. **Cross-validate NC**: Compare TSA-observed NC (GPO=TRUE) against WF-inferred NC from the calibrated estimate. NC reporting coverage may be slightly lower than Clinical (~85–92%).

5. **Record the recommended estimate**: The TSA-calibrated figure (currently $128B at 5% non-reporting) should be the **primary recommended number** for stakeholder presentations. The mean-rate extrapolation is retained as an upper bound.

6. **Derive the presentation range** (see Range Derivation Rules below): The per-SL ranges in the exec summary and recommended estimates table must be derived consistently from the total non-labor range, which is itself anchored on the clinical floor constraint.

**Why this step matters**: Premier's clinical TSA data is near-comprehensive for GPO members because members have strong incentives to submit (contract savings analysis, product-level benchmarking). This makes total GPO Clinical spend the best available ground truth. If the extrapolation diverges materially from this ground truth, the extrapolation needs recalibration — not the other way around.

**Key numbers to update**: TSA-observed by SL, calibrated estimates table, recommended figure, comparison table (mean-rate vs calibrated)

### Range Derivation Rules (**CRITICAL** — applies to exec summary, Section III, and Connection section)

The analyst briefing presents estimated GPO spend by service line as **ranges**. These ranges must be derived consistently each time the briefing is updated.

#### Clinical Floor Constraint

The lower bound of the clinical range **must not fall below TSA-observed GPO clinical spend**, because we can directly observe that amount in the data. If a model-based lower bound (e.g., median-rate per-bed extrapolation) produces a clinical estimate below the TSA-observed value, the observed value supersedes it as the floor.

**Rationale**: The median-rate per-bed extrapolation can underestimate clinical because many smaller GPO systems have incomplete TSA reporting, which suppresses their apparent per-bed rate. TSA-observed clinical ($52.2B as of the current pipeline run) is a hard floor — we know at least that much clinical purchasing exists.

#### Computing the Range

1. **Clinical lower bound** = MAX(TSA-observed clinical, median-rate clinical extrapolation)
2. **Clinical upper bound** = TSA-observed clinical ÷ 0.92 (8% non-reporting)
3. **Total non-labor lower bound** = Clinical lower bound ÷ WF clinical share (0.428)
4. **Total non-labor upper bound** = Clinical upper bound ÷ WF clinical share (0.428)
5. **Per-SL ranges**: Apply WF mix percentages to the total non-labor range
   - NC = total × 0.413
   - Pharma = total × 0.144
   - Food = total × 0.015
6. **Recommended central estimate** = TSA-observed clinical ÷ 0.95 (5% non-reporting) ÷ 0.428

#### Example (current pipeline values)

| Input | Value |
|-------|-------|
| TSA-observed GPO clinical | $52.2B |
| Median-rate clinical extrapolation | $47.7B |
| Clinical lower bound | MAX($52.2B, $47.7B) = **$52.2B** |
| Clinical upper bound | $52.2B ÷ 0.92 = **$56.7B** |
| Total non-labor lower | $52.2B ÷ 0.428 = **$122B** |
| Total non-labor upper | $56.7B ÷ 0.428 = **$132B** |
| NC range | $122B–$132B × 0.413 = **$50B–$54B** |
| Pharma range | $122B–$132B × 0.144 = **$18B–$19B** |
| Food range | $122B–$132B × 0.015 = **$1.8B–$2B** |
| Recommended total | $52.2B ÷ 0.95 ÷ 0.428 = **$128B** |

These numbers appear in three places in the briefing (exec summary Finding #3, Section III Recommended Estimates, Connection section table). All three must be kept in sync.

### Step 5: Validation Sections (Section III-A)

**Source**: Prior analysis (rarely needs re-running)

1. Verify the context note at the top accurately describes which rate version the validation used
2. Update the "Updated GPO Clinical Extrapolation" comparison table if new rate versions are added
3. Update Section III-A Conclusion to reference the current primary estimate

### Step 6: Data Assets & Connection to Initiative (Section IV + closing)

1. Verify table list matches current Dataform pipeline (add/remove tables as needed)
2. Update row counts if tables have been rebuilt
3. Verify companion file references are still valid
4. Update next steps if initiative timeline has changed

---

## Internal Consistency Checks

After all sections are updated, verify:

| Check | How |
|-------|-----|
| Clinical per-bed rate × cohort beds ≈ cohort clinical spend | Section II and III-Step 1 |
| GPO universe totals match `gpo_member_universe` table | Section III-Step 2 |
| SL decomposition sums to total non-labor | Section III SL table |
| TSA-calibrated clinical ≥ TSA-observed clinical | Section III Approach B |
| Clinical range lower bound ≥ TSA-observed clinical (floor constraint) | Exec summary, Section III, Connection |
| TSA-calibrated total = calibrated clinical ÷ WF clinical share | Section III Approach B |
| Cohort systems + beds match BQ table | Section II summary |
| WF classification layers sum to total WF spend | Section I classification table |
| Executive summary numbers match body section numbers | Exec summary vs all sections |
| Analysis Scope subsection present in Executive Summary | Exec summary — must state health-system-centric scope |
| GPO pharma range ≤ acute wholesaler tracing ($21.5B) | Pharma cross-check — broadened footprint explains gap |

---

## Non-Reporting Assumption (5%)

The 5% non-reporting assumption for Clinical is based on:
- Strong member incentive to submit clinical/med-surg data for contract savings tools
- Product-level cleansing and mapping capability creates value for submitters
- GPO membership implies active engagement with Premier's supply chain platform
- 5% is conservative; actual non-reporting may be lower for clinical

For NC, non-reporting may be higher (~8–15%) because PURCHASED SERVICES, FACILITIES, and IT/DIGITAL HEALTH categories have less standardized submission pipelines and less direct contract savings tooling.

This assumption should be revisited if:
- Premier publishes official TSA coverage/completeness metrics
- New member onboarding campaigns significantly change submission rates
- The gap between TSA-observed NC and WF-inferred NC shifts materially

---

## Document Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| v3.2 | Session 8b | Initial marker-category cohort (81 systems) |
| v4 | Session 9b | SL mapping correction — single `service_line_mapping` table, cohort expanded to 100 |
| v4.2 | Session 10 | Pattern expansion (200 patterns), Dataform CLI setup |
| v4.3 | Session 11 | Bed double-counting fix, STAC filter fix, GPO universe corrected |
| v4.3+cal | Session 11 | TSA-calibrated extrapolation ($128B), production process documented |
