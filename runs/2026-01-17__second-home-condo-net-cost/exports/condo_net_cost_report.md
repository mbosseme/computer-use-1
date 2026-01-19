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
- Purchase price: $284,990
- Down payment: 25% ($71,248)
- Mortgage rate: 6.25%, 30-year fixed, no points, no PMI
- Hold period: 4 years
- Appreciation: 4.0%
- Selling friction: 7.0%
- Buyer closing costs + prepaids: 2.0% of price ($5,700)
- Furnishings: $10,000
- HOA: $200/mo, Property tax: $1,576/yr, Insurance: $900/yr
- Utilities (not in HOA): $75/mo
- Tax: Federal ordinary 25% + NY ordinary 6.85% = 31.85%
- Cap gains (sale + taxable brokerage liquidation): (Fed LTCG+NIIT 23.8% + NY 6.85%) = 30.65%

## Core 4-year results
- Total mortgage payments (48 mo): $63,170
- Total interest paid: $52,143
- Total principal paid: $11,027
- Total recurring (HOA/tax/ins/maint/util/assess): $23,104

### Sale math (end of Year 4)
- Sale price: $333,398
- Selling costs: $23,338
- Amount realized: $310,060
- Adjusted basis (incl. capitalizable closing costs): $287,840
- Taxable gain: $22,220
- Cap gains tax: $6,811
- Remaining mortgage balance: $202,715
- Net cash at close: $100,534

### Tax benefit + opportunity cost
- Mortgage-interest tax benefit (A baseline): $16,608
- Mortgage-interest tax benefit (B haircut 25%): $12,456
- Opportunity cost (foregone after-tax gain in taxable brokerage): $13,457

## Economic net cost
- Annualized economic net cost (A baseline): $17,384/yr (4-year total $69,536)
- Annualized economic net cost (B conservative): $18,422/yr (4-year total $73,688)

## Retirement timing extension
Note: The ‘annual contribution’ scenarios treat the annualized economic net cost as an ‘economic equivalent’ contribution. This is not pure cash flow (because sale proceeds occur at the end of the hold), but it matches the outline’s requested framing.

### Using 6% annual return
- Baseline years to $3,500,000: 21.49
- + Invest LumpSum now ($81,248): 20.16 (Δ +1.34 yrs)
- + Invest annual net cost (A): 18.49 (Δ +3.00 yrs)
- + Invest annual net cost (B): 18.34 (Δ +3.15 yrs)
- + Both (A): 17.44 (Δ +4.05 yrs)
- + Both (B): 17.31 (Δ +4.19 yrs)

### Using 7% annual return
- Baseline years to $3,500,000: 18.51
- + Invest LumpSum now ($81,248): 17.35 (Δ +1.15 yrs)
- + Invest annual net cost (A): 16.24 (Δ +2.26 yrs)
- + Invest annual net cost (B): 16.13 (Δ +2.38 yrs)
- + Both (A): 15.31 (Δ +3.20 yrs)
- + Both (B): 15.21 (Δ +3.30 yrs)

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
- Min/Max across built-in scenarios (A): $13,128/yr to $26,936/yr
- Min/Max across built-in scenarios (B): $14,166/yr to $27,974/yr
- Top drivers in this setup:
  - Appreciation 0%→6%: $26,936/yr to $13,128/yr (A)
  - Mortgage rate 5.5%→7.5%: $16,290/yr to $19,215/yr (A)
  - Selling friction 6%→8%: $16,806/yr to $17,962/yr (A)
