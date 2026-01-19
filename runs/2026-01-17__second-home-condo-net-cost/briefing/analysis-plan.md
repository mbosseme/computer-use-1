---
status: ARCHIVED
archived_date: 2026-01-19
archived_reason: Switched target property to Vineyard Point / Dockside condos (18861 Vineyard Point Ln)
current_focus: runs/2026-01-19__vineyard-point/
---

# Plan — Second-Home Condo Ownership Net Cost + Retirement Tradeoff (ARCHIVED)

Run: `2026-01-17__second-home-condo-net-cost`

## Status
This plan is **ARCHIVED / NO LONGER ACTIVE**.

Current active property focus:
- Vineyard Point / Dockside condos (Lake Norman-adjacent)
- Address anchor: 18861 Vineyard Point Ln, Cornelius, NC 28031
- Active run: `runs/2026-01-19__vineyard-point/`

## Objective
Produce a decision-grade, auditable model that estimates:
1) 4-year **economic net cost** of owning the condo (total + annualized)
2) A retirement timeline delta (years earlier/later) versus investing instead

This plan follows the attached spec in `analysis challenge outline.md` and incorporates refinements to avoid common errors around capital gains, tax benefits, and opportunity cost.

## Baseline Inputs (from spec)
**Property / hold**
- Purchase price:
  - Baseline for modeling: $284,990
  - Validation note (as-of 2026-01-15): multiple public listing aggregators show an active list price of ~$284,990 (with recent history showing ~$294k–$300k in late 2025).
  - Sensitivity: $285k–$300k (list price may differ from negotiated purchase price).
- Holding period: 4 years
- Appreciation: 4% compounded annually
  - Validation note: long-run metro-level indices for the Charlotte-Concord-Gastonia area show mid-single-digit average growth over multi-decade horizons, with much higher growth in the 2020–2022 period and lower growth more recently.
  - Sensitivity: 2%–6% (dominant driver).
- Selling friction: 7% of sale price
  - Validation note: typical NC seller costs often combine ~5%–6% agent commission plus additional seller closing costs, making ~6%–8% a reasonable all-in range.
  - Sensitivity: 6%–8%.
- Capital gains tax:
  - Baseline (given ~$400k baseline income at sale): 23.8% on taxable gain (20% LTCG + 3.8% NIIT), if gain is positive
  - Sensitivity: 15%, 18.8%, 23.8% (bracket + NIIT uncertainty)
  - Validation note: NIIT is 3.8% on net investment income (including capital gains) above MAGI thresholds ($250k MFJ / $200k single / $125k MFS).

**State/local taxes (NY)**
- Apply NY state tax to capital gains and interest-deduction benefit where relevant (baseline assumes NY residency / NY return treatment).
- Baseline NY state marginal rate placeholder: 6.85% (sensitivity: 4%–10%).
- NYC residency: assume **no** (Buffalo-area resident). If this changes, treat NYC income tax as a separate toggle.

**Upfront transaction costs (buyer)**
- Buyer closing costs + prepaids/escrows:
  - Baseline planning value: 2.0% of purchase price (all-in cash needed at closing, excluding down payment)
  - Sensitivity: 1.0%–4.0% (depends heavily on lender fees/points, escrow setup, and local title/recording fees)
  - Validation note: some sources cite a low “average closing costs” percentage for NC that likely excludes meaningful loan/escrow/prepaid items; many mortgage/real-estate sources advise budgeting a higher all-in range when including prepaids.
  - Tax/basis note: many settlement fees for *buying* property are capitalizable into basis (e.g., title/recording/transfer taxes, owner’s title insurance), while loan-origination items and certain prepaids are not (per IRS Pub. 551 / Pub. 523).
  - Loan note: assume no discount points are purchased.

**Financing**
- Down payment: 25%
- Mortgage: 30-year fixed
- Interest rate: 6.25%
- Points: none
- PMI: none expected (confirm in final worksheet, but assume $0)

**Recurring costs (annualize)**
- HOA: $200/month
  - Validation note (as-of 2026-01-17): multiple listing aggregators for this unit show HOA fees in the ~$196–$204/month range.
  - Scope note: at least one other Alexander Chase unit listing states “HOA dues include water and trash service.” Treat water/trash as included in baseline unless HOA docs indicate otherwise.
  - Risk note: condo HOAs can levy special assessments and/or raise dues for master-policy deductibles, capital projects, or reserve shortfalls; model a special-assessment sensitivity.
  - Sensitivity: $196–$253/month (to cover the possibility of underreported fees or master-policy/assessment differences).
- Property taxes: $1,576/year
  - Validation note (as-of 2026-01-17): public “tax history” shown by major listing aggregators indicates ~$1,548 (2023) and ~$1,576 (2024).
  - Forward-path note: Mecklenburg County property values are typically on a multi-year revaluation cycle (commonly cited as 4 years). Model assessed value as stable mid-cycle with sensitivity for annual tax-rate changes and/or a step-change at the next revaluation.
  - Sensitivity: $1,500–$2,000/year (assessment/reval risk and bill-year variability).
- Insurance: $900/year
  - Validation note (as-of 2026-01-17): state-level HO-6 condo insurance averages cited by consumer insurance aggregators cluster around ~$800–$900/year (coverage assumptions vary).
  - Coverage note: HO-6 “loss assessment” coverage is often low by default (commonly around $1,000); consider explicitly assuming increased loss-assessment limits (e.g., $25k–$50k) for condo master-policy deductible/special-assessment risk.
  - Sensitivity: $700–$1,200/year (coverage limits, deductibles, and loss-assessment coverage can move this).
- Maintenance/repairs (unit interior): $0 baseline; sensitivity $1k–$3k/year
- Utilities not included in HOA (internet + misc):
  - Baseline: $75/month total when active (with an assumption you may pause service when not there)
  - Sensitivity: $0–$100/month
  - Notes: do not assume internet is included in HOA; do not model more than ~$75/month unless later bills show higher.

**Tax**
- Household itemizes materially above standard deduction
- Marginal tax rate: 25%
- Mortgage interest tax benefit treated as incremental (baseline)
- Guardrail sensitivity: haircut the benefit by 25% (conservative scenario)

**Opportunity cost**
- Upfront investable lump sum (if you *don’t* buy): 25% down amount + $10,000 furnishings
  - Baseline formula: (0.25 × purchase price) + 10,000
  - With $284,990 price: $81,247.50
  - Scope note: this LumpSum definition intentionally excludes buyer closing costs (per spec). If you want, add a sensitivity where buyer closing costs are also investable in the “don’t buy” scenario.
- Market return (taxable brokerage, for opportunity-cost and retirement scenarios):
  - Baseline: 6% nominal compounded annually (forward-looking)
  - Sensitivity: 4.5%–7.5% (use 7% as an optimistic historical-style case)
  - Tax drag (dividends/distributions): baseline 0.5%/year (sensitivity 0.25%–1.0%), implemented as r_after = r_nominal − tax_drag
  - Liquidation tax assumption: for apples-to-apples against a 4-year condo sale, treat the opportunity-cost investment as liquidated at Year 4 and apply cap gains tax (federal + NIIT + NY) to the investment gain.
  - Validation note: institutional capital-market forecasts in late-2025 generally imply muted 10-year nominal returns (mid-single digits) for equity-heavy portfolios; FDEWX is currently ~90% equity.
- Opportunity cost is **foregone gains** only:
  - Compute pre-tax ending value = LumpSum × (1 + r_after)^4
  - Compute investment gain = ending value − LumpSum
  - Compute after-tax gain = gain × (1 − total_cap_gains_rate)
  - Opportunity cost (foregone after-tax gain) = after-tax gain

## Modeling Conventions (to prevent unit errors)
- Mortgage is modeled monthly (48 months) to correctly capture principal vs interest.
- HOA is monthly and annualized as (baseline HOA) × 12 each year.
- Property taxes, insurance, and maintenance are treated as annual line items.
- Buyer closing costs are treated as an upfront cash outflow at purchase; split into “capitalizable to basis” vs “not capitalizable” only if needed for tax sensitivity (default: include in cash outflows; include the capitalizable portion in basis).
- Output includes both:
  - Year-by-year totals (Years 1–4)
  - Full 4-year totals

## Step-by-step Execution Plan

### 1) Establish derived inputs
Compute:
- Down payment = 0.25 × price
- Loan amount = 0.75 × price
- Monthly rate r = 0.0625 / 12
- Term n = 360
- Monthly payment (P&I) using standard fixed-payment formula

### 2) Build amortization schedule (Months 1–48)
For each month:
- Interest = balance × r
- Principal = payment − interest
- Balance = balance − principal

Aggregate by year:
- Total mortgage payments
- Total interest paid
- Total principal paid
- Ending balance per year

Verification checks:
- Month 1 is interest-heavy; principal small but positive.
- Balance declines monotonically.
- Sum(principal) over 48 months equals original loan − ending balance.

### 3) Compute cash outflows
Upfront (at purchase):
- Down payment
- Buyer closing costs + prepaids/escrows
- Furnishings (explicitly treated as a cash outflow; not part of real-property basis)

For each year:
- Mortgage cash outflow = total payments (principal + interest)
- HOA = (baseline HOA) × 12
- Property taxes = (baseline property taxes)
- Insurance = (baseline insurance)
- Maintenance (baseline) = 0
- Utilities not included in HOA = (baseline utilities) × 12

Outputs:
- Annual cash outflow table
- Total 4-year cash outflow

### 4) Compute offsets (economic recapture)

#### 4a) Principal paydown (equity build)
- Principal offset = total principal paid over 48 months

#### 4b) Tax benefit of mortgage interest (incremental)
Two scenarios:
- **A (baseline)**: Tax benefit = (federal marginal rate + NY marginal rate) × (total interest paid)
- **B (conservative guardrail)**: Tax benefit = 0.75 × [(federal marginal rate + NY marginal rate) × (total interest paid)]

Notes:
- Do not model property-tax deductibility as a benefit in baseline (to avoid SALT-cap ambiguity). Mention as sensitivity only.

#### 4c) Sale math (explicit basis/gain structure)
Compute sale price:
- Sale price = purchase price × 1.04^4

Use explicit definitions to avoid double-counting:
- **Adjusted basis** = purchase price + capital improvements (baseline improvements = $0) + capitalizable buyer settlement costs (if modeled separately)
- **Amount realized** = sale price − selling costs (7% × sale price)
- **Taxable gain** = amount realized − adjusted basis
- **Cap gains tax** = (cap gains rate scenario) × max(taxable gain, 0)
- **Net cash at close** = amount realized − remaining mortgage balance − cap gains tax

Also report:
- Gross appreciation = sale price − purchase price (informational)
- Taxable gain (as defined above)

Important separation:
- “Gain on asset” is not the same as “cash you walk away with” because mortgage payoff reduces cash proceeds.

### 5) Opportunity cost (strictly foregone gains)
- Opportunity cost (foregone after-tax gain in taxable brokerage):
  - Pre-tax ending value = LumpSum × (1 + r_after)^4
  - Investment gain = ending value − LumpSum
  - After-tax gain = gain × (1 − total_cap_gains_rate)
  - Opportunity cost = after-tax gain

Explicitly label as “foregone gains” (not the ending value of the investment).

### 6) Economic net cost reconciliation
Compute (4-year) with a cash-in/cash-out identity to avoid principal double-counting:
- Economic net cost (ex-opportunity-cost) =
  - (Down payment + buyer closing costs + furnishings)
  + (Total mortgage payments over 48 months)
  + (HOA + property taxes + insurance + maintenance)
  − (Net cash at close)
  − (Tax benefit; scenario A or B)

Then add opportunity cost (foregone gains only):
- Economic net cost (incl. opportunity cost) = economic net cost (ex-opportunity-cost) + opportunity cost

Also report:
- Average annual economic net cost = 4-year net cost ÷ 4

Verification check:
- Reconciliation table ties exactly to computed components.

### 7) Retirement timing extension (four scenarios)
Given:
- Current portfolio P0 = $1,000,000
- Target PT = $3,500,000
- Return r = 6% annually (baseline), with sensitivity consistent with the Opportunity Cost section

Scenarios:
1) **Baseline**: no added contributions
2) **+LumpSum now**: initial portfolio is P0 + LumpSum
3) **Invest annual net cost**: contribute C each year (end-of-year) where C = annual economic net cost
4) **Combine**: P0 + LumpSum plus annual contributions C

Method:
- Solve for time to reach target for each scenario.
  - Baseline closed-form:
    - t = ln(PT/P0) / ln(1+r)
  - With contributions:
    - Use an annual simulation loop (year-by-year) for clarity and to avoid formula mistakes.

Output:
- Time-to-target in years (can report fractional years)
- Delta vs baseline (“years earlier/later”)

### 8) Sensitivities (top drivers)
Run a small scenario table (keep it simple):
- Appreciation: 0%, 2%, 4%, 6%
- Interest rate: 5.5%, 6.5%, 7.5%
- Selling friction: 6%, 7%, 8%
- Buyer closing costs + prepaids: 1%, 2%, 4% of purchase price
- HOA special assessment: $0 (base) vs one-time $5,000 in Year 2 (stress)
- Furnishings salvage value at exit: 0% (base) vs 25% of furnishings cost (sensitivity)
- Tax benefit: scenario A vs B
- Cap gains tax: 15% vs 18.8% (NIIT scenario)
- Maintenance: $0 vs $2,000/year
- Portfolio return r: 4.5%, 6.0%, 7.5%

Report:
- Annualized net cost under each scenario
- Qualitative ranking of which inputs move results most

## Implementation Artifacts (run-local)
Planned outputs under this run:
- Script: `runs/2026-01-17__second-home-condo-net-cost/scripts/condo_net_cost_model.py`
- Report: `runs/2026-01-17__second-home-condo-net-cost/exports/condo_net_cost_report.md`
- Optional CSVs (for auditability):
  - `exports/amortization_48mo.csv`
  - `exports/annual_cashflows.csv`
  - `exports/sensitivity_table.csv`

## Deliverable Requirements Checklist
- Correct principal vs interest split via amortization schedule
- Explicit gain/basis/amount-realized definitions
- Tax benefit modeled as incremental; includes conservative guardrail
- Opportunity cost computed as foregone gains only
- Clean reconciliation table
- Retirement timeline comparison across 4 scenarios
- Sensitivity summary highlighting dominant variables

## Non-goals / boundaries
- No rental income modeling
- No tax-code deep dive beyond the guardrail sensitivity
- No claim of exact insurance/maintenance without verified inputs
