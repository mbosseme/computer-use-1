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
- Market value at purchase (used for appreciation): $275,000
- Purchase price paid (basis/cash-to-close): $250,000
- Down payment: 25% ($62,500)
- Mortgage rate: 6.25%, 30-year fixed, no points, no PMI
- Hold period: 4 years
- Appreciation: 4.0%
- Selling friction: 7.0%
- Buyer closing costs + prepaids: 2.0% of price ($5,000)
- Furnishings: $10,000
- HOA: $200/mo, Property tax: $1,576/yr, Insurance: $900/yr
- Utilities (not in HOA): $75/mo
- Tax: Federal ordinary 25% + NY ordinary 6.85% = 31.85%
- Cap gains (sale + taxable brokerage liquidation): (Fed LTCG+NIIT 23.8% + NY 6.85%) = 30.65%

## Core 4-year results
- Total mortgage payments (48 mo): $55,415
- Total interest paid: $45,741
- Total principal paid: $9,673
- Total recurring (HOA/tax/ins/maint/util/assess): $23,104

### Sale math (end of Year 4)
- Sale price: $321,711
- Selling costs: $22,520
- Amount realized: $299,191
- Adjusted basis (incl. capitalizable closing costs): $252,500
- Taxable gain: $46,691
- Cap gains tax: $14,311
- Remaining mortgage balance: $177,827
- Net cash at close: $107,054

### Tax benefit + opportunity cost
- Mortgage-interest tax benefit (A baseline): $14,569
- Mortgage-interest tax benefit (B haircut 25%): $10,926
- Opportunity cost (foregone after-tax gain in taxable brokerage): $12,008

## Economic net cost
- Annualized economic net cost (A baseline): $11,601/yr (4-year total $46,404)
- Annualized economic net cost (B conservative): $12,512/yr (4-year total $50,046)

## Retirement timing extension
Note: The ‘annual contribution’ scenarios treat the annualized economic net cost as an ‘economic equivalent’ contribution. This is not pure cash flow (because sale proceeds occur at the end of the hold), but it matches the outline’s requested framing.

### Using 6% annual return
- Baseline years to $3,500,000: 21.49
- + Invest LumpSum now ($72,500): 20.29 (Δ +1.20 yrs)
- + Invest annual net cost (A): 19.38 (Δ +2.11 yrs)
- + Invest annual net cost (B): 19.24 (Δ +2.26 yrs)
- + Both (A): 18.37 (Δ +3.12 yrs)
- + Both (B): 18.24 (Δ +3.26 yrs)

### Using 7% annual return
- Baseline years to $3,500,000: 18.51
- + Invest LumpSum now ($72,500): 17.47 (Δ +1.03 yrs)
- + Invest annual net cost (A): 16.93 (Δ +1.58 yrs)
- + Invest annual net cost (B): 16.82 (Δ +1.69 yrs)
- + Both (A): 16.04 (Δ +2.47 yrs)
- + Both (B): 15.94 (Δ +2.57 yrs)

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
- Min/Max across built-in scenarios (A): $7,494/yr to $19,133/yr
- Min/Max across built-in scenarios (B): $8,405/yr to $20,043/yr
- Top drivers in this setup:
  - Appreciation 0%→6%: $19,133/yr to $7,494/yr (A)
  - Mortgage rate 5.5%→7.5%: $10,642/yr to $13,207/yr (A)
  - Selling friction 6%→8%: $11,043/yr to $12,159/yr (A)
