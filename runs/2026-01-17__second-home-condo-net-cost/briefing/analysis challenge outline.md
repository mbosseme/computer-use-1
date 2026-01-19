---
status: ARCHIVED
archived_date: 2026-01-19
archived_reason: Switched target property to Vineyard Point / Dockside condos (18861 Vineyard Point Ln)
current_focus: runs/2026-01-19__vineyard-point/
---

## Independent Analysis Task: “Second-Home Condo Ownership Net Cost + Retirement Tradeoff” (ARCHIVED)

This document is **ARCHIVED / NO LONGER ACTIVE**. It is retained for historical context only.

Current active property focus:
- Vineyard Point / Dockside condos (Lake Norman-adjacent)
- Address anchor: 18861 Vineyard Point Ln, Cornelius, NC 28031
- Active run: `runs/2026-01-19__vineyard-point/`

### Context / Scenario

We are evaluating whether to purchase a condo in **Cornelius, North Carolina** as a **family vacation / second home**. This is **not intended to be a rental property** (no rental income assumed). Expected personal use is roughly **2–6 weeks per year**.

The property under consideration is:

* **17151 Doe Valley Court, Cornelius, NC**
* Listed price observed in research: **~$293,900**
* Condo built ~2005, ~1,476 sq ft, 2 bed / 2 bath
* HOA fee observed: **~$253/month**
* Public property tax history observed: **~$1,792/year** (2024) and **~$1,761/year** (2023)

The goal is to compute the **true net cost per year** of owning this condo for family vacation purposes, incorporating the major economic offsets (equity build, tax effects, sale proceeds, opportunity cost), and then translate this into a **retirement timing impact** (years earlier/later) relative to investing instead.

---

## Primary Analysis Objective

Estimate the **economic “net expense” of owning the condo**, expressed as:

1. Total net economic cost over a defined holding period (baseline example: **4 years**)
2. Average annual economic cost
3. Equivalent “opportunity cost” vs investing instead
4. (Separate step) retirement timeline impact from investing the money instead of owning the condo

You should produce your own calculation, but keep the scenario assumptions consistent unless you explain why a change is warranted.

---

## Core Assumptions (use these as baseline inputs)

### Financing

* Down payment: **20%**
* Mortgage type: **30-year fixed**
* Interest rate assumption used in baseline: **6.5%**
* Loan amount = purchase price × 80%
* Mortgage payment decomposition matters: separate **principal** vs **interest** (early years are interest-heavy)

### Recurring ownership costs (annualize)

* HOA: **$253/month**
* Property taxes: use the observed public history (**~$1,792/year**) unless you have better verified data
* Home insurance: unknown; assume a reasonable placeholder (e.g., **$1,200/year**) but call out uncertainty
* Maintenance/repairs inside unit: not explicitly estimated—note it as risk/uncertainty
* Optional / advanced: estimate probability-adjusted condo “special assessment risk” but do not invent facts; treat as scenario sensitivity if needed

### Tax assumptions

* Household already **itemizes substantially above the standard deduction**, so incremental mortgage interest is assumed to generate an actual tax benefit.
* Use marginal tax bracket: **25%**
* Mortgage interest deduction rule: applies across first + second homes, but the binding constraint is whether the interest deduction is incremental (we assume yes since itemizing already).
* Important: capture that SALT/property tax deductibility may be constrained by caps—flag this as a sensitivity if needed, but don’t require deep tax law unless you can source it confidently.

### Hold period, appreciation, and sale

* Holding period baseline: **4 years**
* Expected appreciation assumption: **4% compounded annually**
* Sale transaction cost assumption: **7% of sale price** (commissions + closing costs + basic pre-sale improvements)
* Capital gains tax: assume **15%** on net gain (federal); optionally consider state tax as a sensitivity, but keep the core model aligned with the assumption.

### Opportunity cost assumption

* Treat **$80,000** as the upfront cash “tied up” that could have been invested instead of used for down payment / transaction/equity.
* Assume market return: **7% compounded annually**
* (Do not add additional yearly opportunity cost beyond that unless explicitly requested; keep it simple and comparable.)

---

## What “Net Expense” Means in This Analysis

The analysis should explicitly separate:

### A) Raw cash outflows (annual and total)

Include:

* Mortgage **principal + interest** payments
* HOA dues
* Property taxes
* Insurance

### B) Offsets and economic recapture

Include:

* **Principal paydown** (equity build; not “lost” expense assuming eventual sale)
* **Tax benefit of mortgage interest deduction** (since already itemizing)
* **Appreciation / sale proceeds**, net of:

  * 7% transaction costs
  * capital gains tax (15% applied to net gain as modeled)

### C) Opportunity cost

Add the foregone gain from investing $80,000 instead:

* $80,000 × (1.07^4 – 1) over 4 years
  This represents economic cost even though it’s not a direct cash payment.

### Output definition

Economic net cost (4-year) =
**(total cash outflows) − (principal paydown) − (tax benefit) − (after-tax net sale gain)** + (opportunity cost)

Then convert to:

* **Average annual economic net cost** = 4-year economic net cost ÷ 4

---

## Key Angles / Checks the Agent Must Validate

These were important in the original discussion and should be explicitly addressed:

1. **Principal vs interest split**

   * Ensure correct amortization logic (year 1 principal is small, but cumulative principal over 4 years is meaningful).
   * If you don’t model a full amortization schedule, use a reliable approximation but show reasoning.

2. **Mortgage interest deduction realism**

   * Because the household already itemizes well above standard deduction, treat the mortgage interest deduction as incremental.
   * Still flag: SALT/property tax caps or any second-home mortgage interest limits as potential constraints.
   * Do not assume the deduction is worthless unless you justify it.

3. **Primary residence capital gains exclusion**

   * Evaluate whether the **Section 121 exclusion** applies.
   * The scenario is a second/vacation home used 2–6 weeks/year, so generally it is **not** a primary residence.
   * If you model any exclusion path (e.g., converting to primary), make it a separate scenario and follow the rules carefully.

4. **Selling costs treatment**

   * Confirm that commissions/closing costs reduce net proceeds and/or reduce taxable gain appropriately.
   * Apply the 7% assumption as total friction before computing capital gain.

5. **Property tax accuracy**

   * Use public record history if accessible rather than a guess.
   * Explain any difference between assessed taxes and estimated taxes.

6. **Opportunity cost definition**

   * Opportunity cost is strictly the $80k upfront investable lump sum, compounded at 7%.
   * Do not double-count opportunity cost on principal paydown unless you intentionally broaden the scope (and then call it out).

7. **Sensitivity acknowledgment**

   * The agent should mention which inputs dominate the model:

     * appreciation rate
     * interest rate
     * sale friction %
     * tax benefit assumptions
     * insurance/assessment risk (unknown)

---

## Retirement Timing Extension (separate calculation)

Once the annual economic cost is estimated, evaluate the retirement tradeoff:

### Retirement assumptions

* Current investment portfolio: **$1,000,000**
* Retirement target portfolio value: **$3,500,000**
* Market return: **7% compounded annually**
* Compare scenarios:

  1. **Baseline**: portfolio grows at 7% with no added contributions
  2. **Invest $80,000 now instead of tying it up**
  3. **Invest the annual economic cost each year instead of paying it**

     * Use annual contributions equal to the estimated annual economic condo cost
  4. **Combine**: invest $80k now + invest annual economic cost each year

### Required outputs (for retirement section)

* Estimated time to reach $3.5M in each scenario
* “Years earlier” (or later) relative to baseline

---

## Deliverable Format

Provide an analysis write-up with:

1. A clearly labeled **assumptions section**
2. A step-by-step model:

   * annualized cash outflows
   * offsets (principal + tax benefit + sale profit)
   * opportunity cost
3. Final outputs:

   * 4-year economic net cost
   * average annual economic net cost
4. Retirement timing comparison (4 scenarios above)
5. A short list of **top sensitivities** and which variable would most change the conclusion

---

## Notes / Intent

This analysis is not meant to “prove” the condo is good or bad. It’s intended to quantify the **true economic cost per year** of owning a second home for family vacations, and then to quantify the **tradeoff against investing and accelerating retirement**.

The key is precision and correctness around:

* amortization and equity build
* tax deduction realism
* sale proceeds net of costs and taxes
* opportunity cost framing
* translating the “annual economic cost” into time-to-retirement deltas