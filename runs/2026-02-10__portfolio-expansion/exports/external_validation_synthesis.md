# External Validation Synthesis: Service Line Mix Benchmarks

**Date**: February 11, 2026  
**Purpose**: Synthesize two independent external research reports on health system non-labor spend composition, derive consensus external ranges, and compare against our empirical WF-derived benchmarks (42 systems, $52.3B classified).

---

## Source Documents

| # | Document | Type | Primary Data Sources |
|---|----------|------|---------------------|
| **R1** | "External Validation of Health System Non-Labor Purchasing Service Line Mix" | Deep research — cost-report decomposition + published benchmarks | CMS Cost Reports (2552-10), AHA, KFF, Vizient, Definitive Healthcare, Premier/Conductiv purchased services |
| **R2** | "Health System Non-Labor Spend Validation: A Comparative Analysis of IDN Spend Composition" | Deep research — IDN-focused external validation | AHA, Definitive Healthcare, Vizient, Valify/HealthTrust, KFF, CMS cost reports, HFMA |
| **D1** | "Portfolio Expansion Heat Map" | Internal deck — working session framework | N/A (operational framework, not benchmark data) |

D1 is the operational framework for the Portfolio Expansion initiative (on/off/non-contract heat map, winnability scoring, working session flow). It does not contain external benchmark data and is not included in the comparison below.

---

## Consensus External Ranges by Service Line

### Methodology for Deriving External Ranges

Both research reports face the same fundamental challenge: published benchmarks describe **hospital operating expenses** (financial statement view), not **externally purchased, invoice-level spend** (procurement/AP view). Both reports therefore perform denominator conversion — translating "X% of total operating expense" into "Y% of non-labor purchasing" by dividing by the non-labor share (~40–55% of total opex, depending on source and year).

Key denominator conventions:
- **AHA/Kaufman Hall**: Labor = 55–60% of total opex → non-labor = 40–45%
- **KFF (2023)**: Labor = 46% → non-labor = 54% (but KFF "labor" excludes contract labor)
- **CMS cost report (2018)**: Non-capital, non-labor = 54.9% of total opex (the most procurement-like denominator available)

The two reports produce overlapping but not identical ranges because they weight different source datasets and time periods. Below I synthesize a **consensus range** from both.

---

### Clinical / Med-Surg

| Dimension | R1 (Cost-Report Focused) | R2 (IDN-Focused) | Consensus |
|-----------|--------------------------|-------------------|-----------|
| **Implied range** | ~50–65% | 55–65% | **~55–65%** |
| **Alignment verdict** | "Directionally consistent" — your 64% is within range | "High" alignment | **High** |
| **Key insight** | Standard "supplies" benchmarks (15–20% of total opex = 37–50% of non-labor) understate clinical because they fragment PPI, implants, and clinical purchased services into separate categories | The 64% correctly aggregates consumables (~40–44% of non-labor alone) + PPI/implants (can be 40–60% of total supply costs) + clinical distribution fees + clinical services (labs, HTM) — bridging the gap from ~45% "supplies" to ~64% "total clinical" | Clinical is the most scope-dependent SL; the exact number turns on whether clinical purchased services (outsourced labs, dialysis, clinical engineering) are classified as "clinical" or "purchased services" |

**Variance drivers identified by both reports**:
- Teaching status: AMCs have ~19.3% supply expense/total opex vs 14.7% for non-academic (R2), consistent with R1's observation that high case-mix hospitals can reach 30–40% of total expenses as supplies
- OR + Cath Lab concentration: 42.3% of supply budget in OR alone, 19.2% in ICU (R2)
- Definition breadth: Including clinical distribution (Cardinal/McKesson fees) and clinical purchased services adds ~10–15pp vs a narrow "supplies only" definition

---

### Non-Clinical (NC)

| Dimension | R1 (Cost-Report Focused) | R2 (IDN-Focused) | Consensus |
|-----------|--------------------------|-------------------|-----------|
| **Implied range** | ~25–40% (broad purchased services scope) | 20–25% (indirect spend scope) | **~20–25%** (when clinical purchased services are correctly excluded) |
| **Alignment verdict** | "Most sensitive to definitional/channel coverage differences" — tension between your 22% and the ~35% purchased services benchmark | "Exact" — Valify says 20–25% of non-labor; your 22% is a direct match | **High (with caveats)** |
| **Key insight** | The Conductiv benchmark ($49B, 102 orgs) found purchased services = 34.8% of "non-direct labor spend," but this includes *clinical* purchased services (staffing agencies, reference labs) | Valify explicitly scopes to "indirect spend" at 20–25% of non-labor — the best like-for-like comparator to how we define NC | The two reports converge when you control for definition: narrow "indirect/NC" = 20–25%; broad "all purchased services" = 30–40% |

**The definitional wedge**: R1 flags a ~13pp gap (22% vs 35%) and attributes it to: (a) clinical purchased services being classified as clinical in our data vs NC in purchased-services benchmarks, (b) outsourced categories not captured in procurement/GPO data, (c) large-system insourcing (costs move from purchased services to labor). R2 resolves this by noting that specialists (Valify, BroadJump) who focus on *indirect* spend consistently land at 20–25%, validating our 22%.

**Variance drivers**:
- Insource vs outsource: Systems that employ security, janitorial, and IT staff have lower NC (costs in labor); heavily outsourced systems push toward 32%+ (R2)
- System size: Larger IDNs centralize and get economies of scale, potentially driving NC lower
- Teaching status: AMCs have 25.3% higher plant ops costs, pushing NC higher (R2)

---

### Pharmacy / Pharma

| Dimension | R1 (Cost-Report Focused) | R2 (IDN-Focused) | Consensus |
|-----------|--------------------------|-------------------|-----------|
| **Implied range** | ~11% (2018 cost-report decomposition) to ~14–20% (2023–24 big-bucket conversions) | 12.5–20% (Definitive Healthcare supply costs to KFF total pharmacy) | **~12–18%** |
| **Alignment verdict** | "Plausible but slightly low versus recent big-bucket conversions (mid-teens)" | "Moderate" — aligns with supply-cost benchmarks (12.5%) but below revenue-cycle views (22.5%) | **Moderate — our 12–13% is at the low end but defensible** |
| **Key insight** | Cost-report decomposition (2018): Pharmacy (3.8%) + Drugs Charged to Patients (2.1%) = 5.9% of total opex → 5.9/54.9 = **10.8% of non-labor** | KFF's 9% of total opex → 22.5% of non-labor **includes** pharmacist labor and retail pharmacy revenue; Definitive Healthcare's 5–7% of total opex → 12.5–17.5% of non-labor is the true **supply cost** comparator | Both reports agree: the "true acquisition cost" benchmark (excluding pharmacist labor, retail margin, and allocated overhead) is ~12–15%; higher published figures conflate gross charges or total departmental costs |

**Why our 12–13% is defensible (per both reports)**:
1. **340B effect**: 340B hospitals purchase outpatient drugs at 25–50% below WAC. Our cohort is large-IDN-weighted, and many are DSH-eligible 340B entities → lower acquisition cost → lower pharma share (R1 + R2)
2. **Channel separation**: Some pharma flows through direct wholesaler channels not captured in WF/ERP (R1, R2). This structurally depresses observed pharma percentage
3. **Supply cost vs total departmental cost**: Our denominator is *purchasing* (invoice-level), not total pharmacy department opex. Pharmacist labor, compounding overhead, and allocated costs are excluded (R2)
4. **CMS cost report flexibility**: Lines 15 vs 73 allow hospitals to route drug costs differently, creating wide observed variation even with similar underlying drug intensity (R1)

**Why external sources suggest our estimate might be slightly low**:
1. **Time trend**: 2018 cost-report data yielded ~11%; 2023–24 "big bucket" views suggest ~14–20% after denominator conversion, reflecting drug price inflation and specialty pharmacy growth (R1)
2. **Vizient/Fierce Healthcare**: Pharma in acute care = ~7–8% of total opex in 2023 → implies low-to-high teens as share of non-labor (R1)
3. **Specialty pharmacy growth**: Autoimmune therapies alone = ~25% of wholesaler-based pharmacy spend; IDNs insourcing specialty pharmacy will see higher pharma share (R2)

**Our TSA cross-check provides the strongest independent validation**: TSA Pharmacy = **15.1%** of $139.8B CY2025 spend. This sits right in the middle of the external consensus range (12–18%) and above our WF-derived 12.5%, suggesting our WF estimate is a plausible lower bound but the true system-level average is likely closer to 14–15%.

**IQR explanation (both reports converge)**: The 6–23% IQR is a predicable artifact of:
- 340B participation levels (lower bound ≈ heavy 340B systems)
- Insource vs outsource specialty pharmacy (upper bound ≈ large in-house specialty programs)
- Wholesaler-direct channels bypassing WF/ERP capture (lower bound)

---

### Food / Nutrition

| Dimension | R1 (Cost-Report Focused) | R2 (IDN-Focused) | Consensus |
|-----------|--------------------------|-------------------|-----------|
| **Implied range** | ~1–2% of non-labor | 1–2.5% of non-labor | **~1–2%** |
| **Alignment verdict** | "Well-aligned" — "food/nutrition spend typically appears around ~0.5–1.0% of total opex, consistent with ~1–2% of non-labor" | "High" — "Definitive Healthcare: avg dietary = $2.6M / avg opex $251M = 1.03% of total opex → ~2.5% of non-labor" | **High** |
| **Key insight** | Cost-report dietary non-labor = 0.8% of total opex → 0.8/54.9 = **1.5% of non-labor** — directly in our 1–2% band | Raw food costs = 35–40% of total dietary budget (rest is labor). If our data tracks purchasing only (excluding cooks/dietitians), 1–2% is exactly right | Both reports strongly validate. Food is structurally small, low-variance, and tied to patient days |

**Outsourcing effect (both reports)**:
- Outsourced systems (Sodexo, Aramark, Morrison) pay a single "purchased service" fee that often lands in NC, not Food → depresses Food percentage → explains our 0.7% lower bound of IQR
- Self-operated systems purchase raw food directly (Sysco, US Foods) → food appears at 2–3% → explains our upper bound

---

## Side-by-Side: Our Empirical Findings vs External Consensus

| Service Line | Our Weighted Estimate | Our IQR (system-level) | External Consensus Range | Our TSA Cross-Check | Alignment |
|-------------|----------------------|----------------------|-------------------------|---------------------|-----------|
| **Clinical** | **~64%** | 50–69% | **~55–65%** | 44% (broader defs) | **High** — our 64% sits at the top of the consensus range; explained by our broader "total clinical" definition (includes distribution, PPI, clinical services) |
| **NC** | **~22%** | 16–32% | **~20–25%** | 38% (broader defs) | **High** — dead center of the indirect-spend-specific benchmark range (Valify 20–25%) |
| **Pharma** | **~12–13%** | 6–23% | **~12–18%** | **15.1%** | **Moderate** — at the low end of consensus; defensible due to 340B, channel separation, and purchasing-only scope, but the TSA cross-check (15.1%) and recent big-bucket views suggest true center is closer to 14–15% |
| **Food** | **~1–2%** | 0.7–2.0% | **~1–2%** | 1.2% | **High** — precise alignment with cost-report decomposition and per-hospital aggregates |

### Visual Summary

```
Service Line     Our Estimate    External Consensus    Overlap Assessment
─────────────────────────────────────────────────────────────────────────
Clinical         ████████████▓   [55%════════════65%]   64% = top of range ✓
NC               ████▓           [20%════25%]           22% = center ✓
Pharma           ███▒            [12%════════18%]       12-13% = low end ⚠
Food             ▓               [1%══2%]               1-2% = center ✓
```

---

## Key Takeaways

### Where we have strong external validation (3 of 4 SLs)

1. **Food (~1–2%)**: The most precisely validated metric. Both reports converge on 1–2% of non-labor. Our estimate is a structural match. No action needed.

2. **NC (~22%)**: Both reports validate when the right comparator is used (Valify/Vizient "indirect spend" at 20–25%, not broad "purchased services" at 30–40%). Our 22% is dead center. The wider published-services benchmarks (~35%) include clinical purchased services that we correctly classify under Clinical.

3. **Clinical (~64%)**: At the top of the external range (55–65%), but both reports explain *why* it should be high for large IDNs: our definition correctly aggregates consumables + PPI/implants + clinical distribution + clinical services — categories that standard benchmarks fragment. R2 specifically calls our approach a "total cost of ownership" view that is "more representative of modern IDN economics than legacy med-surg benchmarks."

### Where we have partial validation — and a known gap

4. **Pharma (~12–13%)**: Both reports agree our estimate is plausible and defensible, but flag it as sitting at the **low end** of external ranges:
   - 2018 cost-report baseline: ~11% (we're above this)
   - 2023–24 converted benchmarks: ~14–18% (we're below center)
   - Our own TSA cross-check: **15.1%** (above our WF estimate)

   **Recommended interpretation**: Present our 12–13% weighted estimate with the caveat that the "true" pharma share of total non-labor is likely **closer to 14–15%**, with the gap explained by:
   - Wholesaler-direct channels not visible in WF (~2–3pp)
   - 340B acquisition cost advantage (depresses our observed dollars vs WAC-based benchmarks)
   - The TSA cross-check (15.1%) and the external consensus midpoint (~15%) corroborate this adjusted view

### Clinical + NC share: the extrapolation-critical metric

Our key extrapolation ratio — **C+NC = ~86% of total non-labor** — is supported by both reports:
- If pharma is truly ~14–15% (adjusted for channel leakage) and food ~1–2%, then C+NC = ~83–85%
- Our WF-derived 86% is at the top of this range, but plausible for large IDNs with 340B (which compresses pharma dollars)
- The resulting 1.16× multiplier (total non-labor = C+NC / 0.86) is a reasonable estimate; an adjusted view with pharma at ~15% would yield ~1.18× — a minor difference

---

## Structural Drivers of Variance (Consensus from Both Reports)

Both research reports identify the same set of structural factors that explain our wide IQRs:

| Factor | Effect on Clinical | Effect on NC | Effect on Pharma | Effect on Food |
|--------|-------------------|--------------|-----------------|----------------|
| **Teaching/AMC status** | ↑ Higher (more PPI, complex procedures) | ↑ Higher (research infrastructure) | ↑ Higher (specialty drugs, clinical trials) | Neutral |
| **340B participation** | Neutral | Neutral | ↓ Lower (discounted acquisition costs) | Neutral |
| **Insource vs outsource** | Neutral | ↑↓ (outsource = higher NC; insource = lower NC, higher labor) | ↑↓ (insource specialty = higher; outsource = lower) | ↑↓ (self-op = higher food; outsource = lower, shifts to NC) |
| **System size (>$1B)** | ↑ High (volume of complex procedures) | ↓ Lower (centralization economies) | Variable | Neutral |
| **For-profit vs non-profit** | Neutral | Neutral | ↑ Higher for FP (ineligible for 340B → pay WAC) | Neutral |
| **Outpatient vs inpatient mix** | Variable | Variable | ↑ Higher with ambulatory networks (GLP-1s, oncology) | Neutral |

---

## Methodological Notes

### Why the two research reports sometimes disagree

R1 anchors heavily on **CMS cost-report decomposition** (2018 data, private general acute care hospitals) and is more conservative. R2 anchors on **IDN-specific benchmarks** from purchasing analytics firms (Valify, Vizient, Definitive Healthcare) and is more bullish on validating our higher clinical share. Where they differ:

| Topic | R1 View | R2 View | Resolution |
|-------|---------|---------|------------|
| Clinical range | 50–65% (wide) | 55–65% (narrower, higher floor) | R2's tighter range reflects IDN-specific data; R1's wider range incorporates community hospitals |
| NC range | 25–40% | 20–25% | R1 includes clinical purchased services in its higher NC range; R2 correctly isolates indirect-only |
| Pharma center | ~14–20% "mid-teens" | 12.5–20% | Both agree mid-teens is the center for *total department*; R2 provides the crucial distinction that *supply cost only* = 12.5% |

### CMS Cost Report mapping (from R1)

For reference, the cost-report line items that map to our four SLs:

| Our SL | CMS 2552-10 Lines | Notes |
|--------|-------------------|-------|
| **Clinical** | Line 14 (Central Services & Supply), Line 71 (Medical Supplies), Line 72 (Implantable Devices), Lines 50–60 (Ancillary) | Supplies can be distributed across many patient-care cost centers unless reclassified |
| **NC** | Line 5 (A&G), Lines 6–9 (Plant Ops, Laundry, Housekeeping) | "Purchased services" spans clinical and non-clinical in cost reports |
| **Pharma** | Line 15 (Pharmacy), Line 73 (Drugs Charged to Patients) | Hospitals choose between booking in Line 15 vs Line 73 → drives cross-system variance |
| **Food** | Line 10 (Dietary), Line 11 (Cafeteria) | Outsourced arrangements may land in purchased services |

---

*Source reports extracted from: `/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/Portfolio Expansion/`*  
*Empirical benchmarks from: `analyst_briefing.md` (42-system primary cohort, $52.3B classified, entity-bridge classification)*
