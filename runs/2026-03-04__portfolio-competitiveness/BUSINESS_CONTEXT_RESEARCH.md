# Business Context Research: Premier Contract Competitiveness vs HCIQ

**Session:** 2026-03-04__portfolio-competitiveness  
**Research Method:** M365 Copilot (GPT-5.2 Think, Work mode) + SharePoint Word doc extraction  
**Date:** 2026-03-04  
**Purpose:** Validate analytical assumptions and gather business context for the contract-level percentile positioning analysis vs Healthcare IQ benchmarks.

---

## 1. How Premier's Performance Group Contracts Are Structured

### Overview
Premier's contracting ecosystem is intentionally **tiered by commitment and performance expectations**, rather than a flat "national contract" structure. The three primary performance groups in scope for this analysis are:

### National / Performance Program (PP)
- Baseline **national GPO contract** access; broad member eligibility.
- Lower compliance thresholds and fewer behavioral requirements.
- Functions as the **price floor reference**, not necessarily the most aggressive net price.
- Used as the "default" when members are not aligned to higher-performance tiers.
- *Source: Premier's Market Insights & Digital Supply Chain Initiative - A Strategic Analysis (Notebook LM Briefing Doc - Jan 6 2026)*

### Ascend Drive (AD)
- Mid-tier performance group.
- Often includes **dual-award scenarios**, ramp-up periods, and combined compliance calculations across awarded suppliers.
- Members may be contract-compliant without allocating 100% share to a single supplier, which creates **price dispersion at the transaction level**.
- AD pricing is typically better than PP, but not always the best observable price due to dual awards and partial activations.
- *Source: Market Insights Performance Groups – Solventum Monthly Meeting-20260213_100039-Meeting Transcript*

### Surpass (SP)
- **Highest commitment tier.** Strongest compliance requirements.
- Often single-award or dominant-share structures.
- Designed to drive predictable demand and value-aggregated pricing.
- This is where Premier and suppliers expect **best-in-class contract pricing** to appear at the invoice level.
- *Source: Premier's Market Insights & Digital Supply Chain Initiative - A Strategic Analysis (Notebook LM Briefing Doc - Jan 6 2026)*

---

## 2. Contract Type Definitions in `transaction_analysis_expanded`

The `contract_type` field reflects **scope of applicability**, not performance tier.

### PREMIER
- Nationally negotiated Premier contracts.
- Includes PP, AD, and SP performance groups.
- Pricing reflects formal GPO agreements.
- Eligible for performance incentives, rebates, and compliance tracking.

### REGIONAL
- Sub-national contracts negotiated for IDNs, regional coalitions, or specific health system groupings.
- Pricing may be **better or worse** than national Premier pricing depending on leverage and local strategy.
- **Not intended to represent a national benchmark price.**

### LOCAL
- Facility-specific or system-specific pricing.
- Often influenced by direct negotiations, legacy agreements, or conversion protections.
- Can appear as extreme low prices but are **not broadly replicable** across the Premier membership.

**Key Point:** REGIONAL and LOCAL are *real prices*, but they are *not scalable national reference prices*.

---

## 3. Is Excluding LOCAL and REGIONAL Correct for "Best Premier Tier Price"?

### Answer: ✅ Yes — Directionally Correct for National Benchmarking

**Analytical justification:**
If the objective is *"What is the best price a Premier member can reasonably expect by aligning to the highest Premier tier?"* then:
- LOCAL prices introduce **one-off negotiation noise**
- REGIONAL prices reflect **sub-national leverage not accessible to all members**
- Including them would **artificially compress percentiles downward**, making Premier appear less competitive at the national level

### Best-Practice Framing
- ✅ **Exclude LOCAL and REGIONAL** when defining: "Best Premier tier price" and national benchmark positioning
- ✅ **Limit to PREMIER contracts**
- ✅ **Stratify within PREMIER** by PP vs AD vs SP (if available) — see Section 4 below

### Required Caveat Language
> **"This analysis reflects nationally available Premier pricing, not localized exceptions."**

---

## 4. How to Infer SP vs AD vs PP Within `transaction_analysis_expanded`

### Primary Method: `Contract_Number` Prefix (Most Reliable)

The contract number prefix is documented and aligns to the performance group:

| Prefix | Program | Example Value |
|--------|---------|---------------|
| `SP-`  | Surpass (SP) | `SP-OR-2538` |
| `AD-`  | AscenDrive (AD) | `AD-NS-2112` |
| `PP-`  | Performance Program / National | `PP-FA-439`, `PP-MM-234` |

*Sources: Re: Confirmed-BBraun MI Demo - virtual; Transaction Analysis exports; Rebate Tracker*

**SQL Classification Rule:**
```sql
CASE 
  WHEN Contract_Number LIKE 'SP-%' THEN 'SP'
  WHEN Contract_Number LIKE 'AD-%' THEN 'AD'
  WHEN Contract_Number LIKE 'PP-%' THEN 'PP'
  WHEN Program_Line IS NOT NULL THEN Program_Line  -- fallback if field populated
  ELSE 'Unclassified'
END AS performance_tier
```

**Important edge case:** Rebate trackers may embed PP as a substring (e.g., `ACU Enhancement-PP-NS-1783`). Treat these as PP tier.

### Secondary Method: `Program_Line` Field

A `Program_Line` column **exists in the schema** but exact enumerated values (e.g., `'SURPASS'` vs `'ASCENDRIVE'`) are not confirmed in source documentation. Use empirically (run `SELECT DISTINCT Program_Line` to validate values in your extract), and use `Contract_Number` prefix as the canonical rule.

### Other Relevant Columns
| Column | Purpose |
|--------|---------|
| `Contract_Name` | Human-readable name |
| `Contract_Number` | Primary program classifier via prefix |
| `Contract_Type` | Scope indicator (PREMIER/REGIONAL/LOCAL) — *not* the same as SP/AD/PP |
| `Contract_Price_Found` | Boolean — use to filter to contract-matched rows only (prefix logic only applies here) |
| `Contract_Pkg_Best_Price` | Best package price on the contract |
| `Contract_Pkg_Access_Price` | Access-tier price |

*Sources: Re: Baxter Next Steps (schema export email)*

### Edge Cases
1. **Off-contract rows:** If `Contract_Price_Found` = false/null and `Contract_Number` is null → these are unmatched rows. **Cannot** be classified SP/AD/PP. Label as `Unclassified / No Contract Match`.
2. **Dual-award AD transactions:** AD compliance is calculated on *combined* spend across dual-award suppliers; this doesn't change the contract prefix but can affect "best price" interpretation.

---

## 5. HCIQ Data Collection Methodology & Methodological Limitations

### What HCIQ Collects (per PIA Review: FW: HealthCare IQ - PIA Review - RITM0446298)

HCIQ focuses exclusively on **PO/AP purchase history data (price benchmarking)**. Key statements from the PIA email chain (Hall, Brian):
- *"PHI/PII will NOT be shared"*
- *"We are only focused on price benchmarking through purchase history data (PO/AP) … shared … through the data acquisition template."*
- Data is de-identified / blinded (health system and facility identifiers)

**Source document:** `HCIQ_Data_Specification_Spend_Contracts_FastTrack_20250207_Premier.xlsx`

### HCIQ's Technical Definitions (from Data Spec)

#### Purchase History (PO)
- **Selection criteria:** `Purchase Orders that have been sent to the Vendor`
- Requires a PO status field legend

#### Invoice History
- **Selection criteria:** `Paid invoices` (explicit)
- Requires an invoice status field legend

#### Cost Fields
- `TOTAL_COST`: *"The Total Cost without shipping or additional charges"*
- `UNIT_COST`: *"purchase price … without shipping or any additional charges"*

#### UOM Normalization
- Requires `UOM` and `UOM_FACTOR` (quantity contained in the UOM)
- Comparisons are built around **cost-to-each normalization**
- UOM factor errors propagate directly into benchmark percentiles

#### Contract Structure
- `CONTRACT_GROUP_NAME` supports multi-source contracts: examples = *"Premier, Vizient, Directly Negotiated"*
- Tier fields: `TIER_CODE`, `TIER_NAME`, `TIER_DESCRIPTION`

### HCIQ SOW / Software License Agreement Findings
- **"Baseline Data"** = prices paid during the 12 months prior to the Agreement Effective Date
- **"Baseline Price"** = last price paid for each item
- **"Potential Savings"** = (Baseline Price – identified price) × projected quantity
- For the Spend Analytics module, **contract eligibility files are marked "Intentionally Omitted"** in the SOW Exhibit A

---

## 6. Key Methodological Differences: Premier vs HCIQ (Why Comparisons Are Imperfect)

| Dimension | Premier (`transaction_analysis_expanded`) | HCIQ |
|-----------|-------------------------------------------|------|
| **Eligible transactions** | PO/AP blend; may include broader PO states | POs *sent to vendor* (strict) |
| **Invoice selection** | Varies by implementation | *Paid invoices* only |
| **Cost basis** | May include freight/fees depending on field | Explicitly excludes shipping and additional charges |
| **UOM normalization** | UOM factor applied internally | Requires `UOM_FACTOR`; cost-to-each is foundational; errors shift percentiles |
| **Rebates / back-end** | SP & AD contracts carry compliance-based earn-backs; these **improve net cost** | Not captured in any HCIQ data spec reviewed; out of scope per PIA statement |
| **Contract construct alignment** | PREMIER/REGIONAL/LOCAL hierarchy | Multi-source: Premier, Vizient, Direct — `CONTRACT_GROUP_NAME` field |
| **Tier granularity** | SP/AD/PP inferred from Contract_Number prefix | `TIER_CODE`, `TIER_NAME` fields available but require HCIQ mapping |
| **Savings construct** | Percentile positioning vs market | "Baseline Price" (last price paid) → "Potential Savings" = improvement from baseline |
| **Catalog attribution** | Matched on Premier item master | AI-enhanced product recognition / ML catalog attribution (SETL process) |

**Critical implication:** HCIQ benchmarks **systematically understate Premier's net competitiveness** because:
1. Rebates/earn-backs are invisible in HCIQ invoice-level data
2. Cost basis definitions differ (shipping exclusions)
3. UOM normalization differences can shift percentile positions materially
4. HCIQ's benchmark universe may include non-Premier contract comparables by default

---

## 7. Required Disclaimer Language for Analysis

### For All Percentile Positioning Outputs
> *"Percentile positioning reflects **invoice-level pricing only** and does not capture Premier member rebates or performance incentives, which may materially improve net effective cost relative to external benchmarks."*

### For Contract Type Scope
> *"This analysis reflects nationally available Premier pricing (PREMIER-type contracts only), not localized exceptions (LOCAL or REGIONAL). Locally negotiated or facility-specific pricing has been excluded from scope to ensure comparability."*

### For SP/AD/PP Classification
> *"Performance tier classification (SP/AD/PP) is inferred from Contract_Number prefix conventions (SP- / AD- / PP-). Rows without a matched contract (Contract_Price_Found = false) are excluded from tier-level analysis."*

---

## 8. Source Documents Referenced by M365 Copilot

| Document | Relevance |
|----------|-----------|
| *Premier's Market Insights & Digital Supply Chain Initiative - A Strategic Analysis (Notebook LM Briefing Doc - Jan 6 2026)* | PP/SP/AD tier structure; MI platform capabilities |
| *Market Insights Performance Groups – Solventum Monthly Meeting-20260213_100039-Meeting Transcript* | AscenDrive dual-award mechanics |
| *FW: HealthCare IQ - PIA Review - RITM0446298* | HCIQ data sharing scope (PO/AP only, no PHI, no rebates) |
| *HCIQ_Data_Specification_Spend_Contracts_FastTrack_20250207_Premier.xlsx* | HCIQ technical field definitions, cost basis, UOM, selection criteria |
| *Healthcare-IQ, LLC-HCIQ Software License Agreement 7.1.2025 FE.pdf* | "Baseline Price" definition; contract files "intentionally omitted" in SOW |
| *Healthcare IQ-HCIQ - Premier Acurity Contract - Strategic Alliance Proposal 6.10.2025 FE.pdf* | HCIQ SETL pipeline, ML catalog attribution, UOM normalization methodology |
| *Re: Baxter Next Steps* | `transaction_analysis` schema / column list export |
| *Re: Confirmed-BBraun MI Demo - virtual* | SP- / AD- contract number examples |
| *Fw: Phys Mon question* | `Program_Line` field confirmation in schema |
| *Rebate Tracker* | Embedded SP/AD/PP in rebate tracker contract strings |

---

## 9. Implications for the Current Analysis Pipeline

### What the Analysis Did Correctly
- ✅ Used `transaction_analysis_expanded` (correct data source)
- ✅ Excluded LOCAL and REGIONAL `contract_type` rows for national benchmarking
- ✅ Focused on contract-level percentiles rather than simple averages
- ✅ Used "best price" logic (taking lowest unit price per contract-item pairing)

### Suggested Enhancements (Prioritized)

1. **Add performance tier stratification** — Apply the `Contract_Number` prefix rule (SP-/AD-/PP-) to split PREMIER contracts by tier. This would reveal if SP is consistently more competitive than AD/PP vs HCIQ, or vice versa.

2. **Add rebate disclaimer to all outputs** — Required per HCIQ methodological review. Already added to Methodology tab in Excel; ensure exec slides carry similar language.

3. **Cross-check UOM handling** — Verify that Premier `transaction_analysis_expanded` and HCIQ benchmarks use the same unit basis (e.g., per-each vs per-case). UOM mismatches can shift percentiles by up to 10+ positions.

4. **Dual-view the data** (optional enhancement) — Show both "PREMIER only" (current) and "All contracts" (including REGIONAL/LOCAL) to illustrate price dispersion context for stakeholders who may question what's being excluded.

5. **Validate `Program_Line` values empirically** — Run `SELECT DISTINCT Program_Line, COUNT(*) FROM transaction_analysis_expanded WHERE contract_type = 'PREMIER' GROUP BY 1` to confirm what values actually exist in production data. May provide a simpler classification path than prefix parsing.

---

---

## 10. Admin Fee Structure & Its Impact on Premier-vs-HCIQ Comparisons

### Background: Premier's Admin Fee Model
Premier's strategy framing describes a **two-layer model**:
- **Layer 1: Access / "The Toll"** — Base administrative fees associated with the core GPO access model
- **Layer 2: Performance / "Quantified Lift"** — Paid data/tech/services (the "Supplier Technology Fee" construct being phased in)

Internal "Supplier Tech Fee Model" slides show **"Admin Fee: 2–3%"** as the baseline, with an additional "Tech Fee: X%" layered on top.

*Sources: Premier Strategy Briefing; Supplier Tech Fee Model - Dec 2023*

---

### Q1: Are Prices in `transaction_analysis_expanded` Gross or Net of Admin Fees?

**Answer: ✅ Gross (not net-of-admin-fee)**

The `transaction_analysis_expanded` prices are **provider PO/invoice prices** ("item, price, quantity, date") as captured in the transaction feed. Admin fees are treated as a **separate supplier-to-Premier billing process** that Premier calculates from invoice/sales data separately — not embedded as a deduction within the PO/invoice unit price.

> ⚠️ **Important nuance:** Whether suppliers *strategically* set contract prices higher to offset expected admin fee obligations is a commercial behavior question that cannot be proven or quantified from available data artifacts.

*Sources: Pitch Deck_AscenDrive and SURPASS; Admin Fee Workstream SLT Readout 053024*

---

### Q2: Does HCIQ Benchmark Pricing Include or Exclude Admin Fees?

**Answer: HCIQ does not document any admin fee adjustment — comparison is at "price paid" layer**

The HCIQ data spec defines:
- `UNIT_COST`: "purchase price … without shipping or any additional charges"
- `TOTAL_COST`: "The Total Cost without shipping or additional charges"
- No "administrative fee" fields, no admin fee subtraction, no fee adjustment in benchmark construction

**Conclusion:**
> ✅ **HCIQ and Premier `transaction_analysis_expanded` are aligned at the "price paid on the PO/invoice" layer**, not at the "supplier net revenue after fees" layer. If admin fee economics are embedded *indirectly* in the negotiated contract price (supplier sets a higher gross price to offset expected fees), that effect would be present in *both* Premier transaction prices and HCIQ benchmarks — but neither system's documented methodology isolates it.

*Sources: HCIQ_Data_Specification_Spend_Contracts_FastTrack_20250207_Premier; Transaction Analysis Grid*

---

### Q3: Typical Admin Fee % Range — Does It Vary by SP/AD/PP?

| Source | Range/Example |
|--------|---------------|
| Supplier Tech Fee Model slides | **2–3%** (modeled baseline) |
| Stryker example (RE: Stryker Trauma Project Update Nov 2024) | Current: **0.3%**, average: **2.6%** |
| Member RFP draft (LVH_Jefferson) | Varies by category/commitment/program, **up to 9%**, blended example ~**1.6%** |
| Industry GPO safe harbor (federal) | Generally **< 3%** |

**Does it vary by SP/AD/PP tier?**
- Internal Premier materials explicitly state admin fees vary by **"category, commitment, and program"** — which includes committed programs like Surpass/AscenDrive.
- A sample contract worksheet (Ambu Math Aug 2025) shows different rates by contract: PP rows at 3–4%, AD rows at 4–6%, SP rows at ~4%.
- ⚠️ **No definitive policy statement** documenting a fixed SP > AD > PP ordering; variability can occur even within the same supplier across tiers.

*Sources: LVH_Jefferson RFP DRAFT; Ambu Math Aug 2025; Supplier Tech Fee Model - Dec 2023*

---

### Admin Fee Impact on Analysis "Fairness"

**Verdict: Comparison is directionally fair at the invoice-price layer, with a required caveat**

What makes it fair:
- Both Premier TSA and HCIQ are anchored on PO/invoice transaction costs
- Neither system deducts admin fees from the price field

Where distortion can occur (but is unmeasurable from these datasets):
- Admin fees influence **supplier economics and member shareback** (GAF/NAF/WAAF constructs)
- Two GPOs could show identical invoice pricing, but the supplier's net revenue after fees differs — influencing their *willingness* to offer that price going forward
- This is a commercial/incentive layer that neither TSA nor HCIQ adjusts for

**Required caveat language for analysis output:**
> *"Percentiles reflect **invoice/PO transaction prices** and do not adjust for supplier-side administrative fee economics or member fee shareback structures; these factors can influence negotiated pricing but are not separately observable in the benchmarked unit-cost fields."*

*Sources: Admin Fee Workstream SLT Readout 053024; Pitch Deck_AscenDrive and SURPASS*

---

## 11. Additional Source Documents Referenced in Q3

| Document | Relevance |
|----------|-----------|
| *Supplier Tech Fee Model - Dec 2023* | Admin fee 2–3% baseline; tech fee model structure |
| *Admin Fee Workstream SLT Readout 053024* | Admin fee as separate supplier billing process; GAF/NAF/WAAF concepts |
| *Pitch Deck_AscenDrive and SURPASS* | Transaction price is PO/invoice price (not net-of-fee) |
| *RE: Stryker Trauma Project Update Nov 2024* | Specific admin fee rates: 0.3% current, 2.6% average |
| *LVH_Jefferson RFP DRAFT* | Admin fee range up to 9%; varies by category/commitment/program |
| *Ambu Math Aug 2025* | PP/AD/SP contract rows with different admin fee % examples |
| *Premier Strategy Briefing* | Two-layer model: Access/"Toll" + Performance/"Quantified Lift" |
| *hiscionline.com; natlawreview.com* | Industry context: GPO fees generally < 3%; federal safe harbor reference |
| *Internal analytics requirement - Jan 26 - measures tab* | GAF/NAF/WAAF measurement concepts |

---

*Research conducted via M365 Copilot (GPT-5.2 Think, Work mode) on 2026-03-04. Sources cited by Copilot are from internal Premier M365 content (SharePoint, Outlook, Teams). All quoted language reflects Copilot's synthesis of internal documents. Treat as directional business context, not legal/contractual interpretation.*
