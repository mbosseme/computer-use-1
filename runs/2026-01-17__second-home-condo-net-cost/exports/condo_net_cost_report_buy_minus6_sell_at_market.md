---
status: ARCHIVED
archived_date: 2026-01-19
archived_reason: Switched target property to Vineyard Point / Dockside condos (18861 Vineyard Point Ln)
current_focus: runs/2026-01-19__vineyard-point/
---

# Condo Net Cost Report (4-year hold) (ARCHIVED)

This report is **ARCHIVED / NO LONGER ACTIVE**. It is retained for historical context only.

Run: `2026-01-17__second-home-condo-net-cost`

## Baseline assumptions (key)
- Market value at purchase (used for appreciation): $284,990
- Purchase price paid (basis/cash-to-close): $267,891
- Down payment: 25% ($66,973)
- Mortgage rate: 6.25%, 30-year fixed, no points, no PMI
- Hold period: 4 years
- Appreciation: 4.0%
- Selling friction: 7.0%
- Buyer closing costs + prepaids: 2.0% of price ($5,358)
- Furnishings: $10,000
- HOA: $200/mo, Property tax: $1,576/yr, Insurance: $900/yr
- Utilities (not in HOA): $75/mo
- Tax: Federal ordinary 25% + NY ordinary 6.85% = 31.85%
- Cap gains (sale + taxable brokerage liquidation): (Fed LTCG+NIIT 23.8% + NY 6.85%) = 30.65%

## Core 4-year results
- Total mortgage payments (48 mo): $59,380
- Total interest paid: $49,015
- Total principal paid: $10,366
- Total recurring (HOA/tax/ins/maint/util/assess): $23,104

### Sale math (end of Year 4)
- Sale price: $333,398
- Selling costs: $23,338
- Amount realized: $310,060
- Adjusted basis (incl. capitalizable closing costs): $270,570
- Taxable gain: $39,491
- Cap gains tax: $12,104
- Remaining mortgage balance: $190,552
- Net cash at close: $107,404

### Tax benefit + opportunity cost
- Mortgage-interest tax benefit (A baseline): $15,611
- Mortgage-interest tax benefit (B haircut 25%): $11,708
- Opportunity cost (foregone after-tax gain in taxable brokerage): $12,749

## Economic net cost
- Annualized economic net cost (A baseline): $13,637/yr (4-year total $54,548)
- Annualized economic net cost (B conservative): $14,613/yr (4-year total $58,451)

## Retirement timing extension
Note: The ‘annual contribution’ scenarios treat the annualized economic net cost as an ‘economic equivalent’ contribution. This is not pure cash flow (because sale proceeds occur at the end of the hold), but it matches the outline’s requested framing.

### Using 6% annual return
- Baseline years to $3,500,000: 21.49
- + Invest LumpSum now ($76,973): 20.22 (Δ +1.27 yrs)
- + Invest annual net cost (A): 19.06 (Δ +2.43 yrs)
- + Invest annual net cost (B): 18.91 (Δ +2.58 yrs)
- + Both (A): 18.02 (Δ +3.47 yrs)
- + Both (B): 17.88 (Δ +3.61 yrs)

### Using 7% annual return
- Baseline years to $3,500,000: 18.51
- + Invest LumpSum now ($76,973): 17.41 (Δ +1.10 yrs)
- + Invest annual net cost (A): 16.68 (Δ +1.83 yrs)
- + Invest annual net cost (B): 16.56 (Δ +1.95 yrs)
- + Both (A): 15.76 (Δ +2.75 yrs)
- + Both (B): 15.65 (Δ +2.86 yrs)

## Files generated
- `exports/amortization_48mo.csv`
- `exports/annual_cashflows.csv`
- `exports/sensitivity_table.csv`
- `exports/condo_net_cost_report.md`

## How to rerun with negotiated terms
- Edit: `inputs/model_inputs.json` (recommended for most changes)
- Or override a few key negotiated items on the CLI:
  - `python runs/2026-01-17__second-home-condo-net-cost/scripts/condo_net_cost_model.py --price 290000 --mortgage-rate 0.06 --buyer-closing 0.02`
  - Supported overrides: `--price`, `--mortgage-rate`, `--buyer-closing`, `--selling-friction`, `--appreciation`

## Sensitivity highlights (annualized net cost)
- Min/Max across built-in scenarios (A): $9,381/yr to $21,866/yr
- Min/Max across built-in scenarios (B): $10,357/yr to $22,842/yr
- Top drivers in this setup:
  - Appreciation 0%→6%: $21,866/yr to $9,381/yr (A)
  - Mortgage rate 5.5%→7.5%: $12,609/yr to $15,358/yr (A)
  - Selling friction 6%→8%: $13,059/yr to $14,215/yr (A)
