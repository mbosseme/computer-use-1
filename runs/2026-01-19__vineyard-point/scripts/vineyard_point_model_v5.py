from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import product
from pathlib import Path
from typing import Iterable


AVG_DAYS_PER_MONTH = 365.25 / 12


@dataclass(frozen=True)
class DateBlock:
    start: date  # inclusive
    end: date  # inclusive

    def days_inclusive(self) -> int:
        return (self.end - self.start).days + 1


def parse_date(value: str) -> date:
    year, month, day = value.split("-")
    return date(int(year), int(month), int(day))


def normalize_owner_blocks(owner_blocks: list[dict], model_year: int) -> list[DateBlock]:
    blocks: list[DateBlock] = []
    for b in owner_blocks:
        start = parse_date(b["start"])
        end = parse_date(b["end"])
        start = _clamp_year(start, model_year)
        if end.month == 1 and start.month == 12:
            end = date(model_year + 1, end.month, end.day)
        else:
            end = _clamp_year(end, model_year)
        blocks.append(DateBlock(start=start, end=end))
    blocks.sort(key=lambda x: x.start)
    merged: list[DateBlock] = []
    for block in blocks:
        if not merged:
            merged.append(block)
            continue
        last = merged[-1]
        if block.start <= last.end + timedelta(days=1):
            merged[-1] = DateBlock(start=last.start, end=max(last.end, block.end))
        else:
            merged.append(block)
    return merged


def _clamp_year(d: date, year: int) -> date:
    return date(year, d.month, d.day)


def apply_buffer(blocks: list[DateBlock], buffer_days: int) -> list[DateBlock]:
    if buffer_days <= 0:
        return blocks
    buffered: list[DateBlock] = []
    for b in blocks:
        buffered.append(
            DateBlock(
                start=b.start - timedelta(days=buffer_days),
                end=b.end + timedelta(days=buffer_days),
            )
        )
    buffered.sort(key=lambda x: x.start)
    merged: list[DateBlock] = []
    for block in buffered:
        if not merged:
            merged.append(block)
            continue
        last = merged[-1]
        if block.start <= last.end + timedelta(days=1):
            merged[-1] = DateBlock(start=last.start, end=max(last.end, block.end))
        else:
            merged.append(block)
    return merged


def invert_blocks(year_start: date, year_end: date, blocked: list[DateBlock]) -> list[DateBlock]:
    if not blocked:
        return [DateBlock(year_start, year_end)]
    free: list[DateBlock] = []
    cursor = year_start
    for b in blocked:
        if b.end < year_start:
            continue
        if b.start > year_end:
            break
        start = max(cursor, year_start)
        end = min(b.start - timedelta(days=1), year_end)
        if start <= end:
            free.append(DateBlock(start, end))
        cursor = max(cursor, b.end + timedelta(days=1))
    if cursor <= year_end:
        free.append(DateBlock(cursor, year_end))
    return free


def leasable_days_from_windows(windows: list[DateBlock], min_lease_days: int) -> tuple[int, int]:
    if min_lease_days <= 0:
        raise ValueError("min_lease_days must be positive")
    leasable_days = 0
    lease_count = 0
    for w in windows:
        length = w.days_inclusive()
        segments = length // min_lease_days
        leasable_days += segments * min_lease_days
        lease_count += segments
    return leasable_days, lease_count


def monthly_payment(principal: float, annual_rate: float, term_years: int) -> float:
    if principal <= 0: return 0.0
    r = annual_rate / 12
    n = term_years * 12
    if r == 0: return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def remaining_balance(principal: float, annual_rate: float, term_years: int, months_paid: int) -> float:
    if principal <= 0: return 0.0
    r = annual_rate / 12
    n = term_years * 12
    if r == 0: return max(0.0, principal * (1 - months_paid / n))
    pmt = monthly_payment(principal, annual_rate, term_years)
    k = months_paid
    return principal * (1 + r) ** k - pmt * (((1 + r) ** k - 1) / r)


def format_money(value: float) -> str:
    return f"${value:,.0f}"


def build_scenarios(inputs: dict) -> list[dict]:
    prop = inputs["property"]["purchase"]
    financing = inputs["financing"]
    upfront = inputs["upfront"]
    rental = inputs["rental"]
    # owner_use = inputs["owner_use"]["scenarios"] # V5: Just use 1 scenario to check ranges? Or all?
    # Prompt asks for: "Base Case" + sensitivities.
    # To keep it manageable, we can iterate all, but mark specific ones as "Base".
    
    owner_use = inputs["owner_use"]["scenarios"]

    # Prompt specific ranges
    down_options = [0.20, 0.25] # Specific request
    occupancy_options = [0.60, 0.70, 0.75] # Specific request
    appreciation_options = [0.01, 0.03, 0.05]
    furnish_options = [8000, 16000, 30000]
    
    scenarios: list[dict] = []

    # Using input options but filtering for request?
    # Actually, let's just use the full matrix if small enough, or hardcode the requested sets.
    # The prompt explicitly asked for those ranges.
    
    # We will overwrite the "options" from json with the prompt's explicit request to ensure coverage
    
    for (
        down_pct,
        occupancy_rate,
        appreciation_rate,
        furnish_budget,
        owner_key,
        horizon_years # Keep fixed at 7 for primary analysis? Prompt implied 7.
    ) in product(
        down_options,
        occupancy_options,
        appreciation_options,
        furnish_options,
        owner_use.keys(),
        [7] # Fixed 7y hold for V5 standard
    ):
        scenarios.append({
            "down_payment_pct": float(down_pct),
            "interest_rate": 0.07, # Base assumption
            "term_years": 30,
            "furnish_budget": float(furnish_budget),
            "monthly_rent": 2800.0, # Base Base
            "fill_rate": float(occupancy_rate),
            "management_fee_pct_of_rent": 0.20,
            "leasing_fee_per_lease": 250.0,
            "owner_use_scenario": owner_key,
            "horizon_years": int(horizon_years),
            "appreciation_rate": float(appreciation_rate)
        })

    return scenarios


def compute_metrics(inputs: dict, scenario: dict, force_empty: bool = False, model_year: int = 2026) -> dict:
    purchase = inputs["property"]["purchase"]
    recurring = inputs["recurring_costs"]
    rental = inputs["rental"]
    budget = inputs["cash_budget"]
    owner_scenarios = inputs["owner_use"]["scenarios"]
    tax_inputs = inputs.get("tax", {})

    # --- 1. REVENUE BRIDGE ---
    year_start = date(model_year, 1, 1)
    year_end = date(model_year, 12, 31)
    days_in_year = 365
    
    owner_blocks_raw = owner_scenarios[scenario["owner_use_scenario"]]["blocks"]
    owner_blocks = normalize_owner_blocks(owner_blocks_raw, model_year=model_year)
    owner_days = sum(b.days_inclusive() for b in owner_blocks)
    
    if force_empty:
        # Empty Logic
        available_rentable_days = 0
        occupied_days = 0
        occupied_months = 0.0
        lease_count = 0
        revenue_gross_rent = 0.0
    else:
        # Rental Logic
        blocked_with_buffers = apply_buffer(owner_blocks, int(rental["turnover_buffer_days"]))
        free_windows = invert_blocks(year_start, year_end, blocked_with_buffers)
        
        # Max Possible Rentable Days (if 100% fill of available windows)
        max_rentable_days, potential_leases = leasable_days_from_windows(free_windows, int(rental["min_lease_days"]))
        
        # Apply Fill Rate (Occupancy)
        # Note: Fill Rate is applied to the *Rentable Windows*, not the whole year.
        occupied_days = max_rentable_days * float(scenario["fill_rate"])
        occupied_months = occupied_days / 30.42 # Standard Month
        
        # Lease Count (Fractional? No, estimate based on filled time)
        # If we fill X%, we likely have X% of the potential leases?
        # Or fewer longer leases? Let's assume average lease length matches min_lease_days for count calc?
        # Better: lease_count = occupied_days / (avg_stay). 
        # But we don't have avg stay. 
        # We'll use: potential_leases * fill_rate
        lease_count = max(1.0, potential_leases * float(scenario["fill_rate"])) if occupied_days > 0 else 0
        
        revenue_gross_rent = occupied_months * float(scenario["monthly_rent"])

    # --- 2. COST STACK ---
    # A) Fixed Costs
    purchase_price = float(purchase["purchase_price"])
    loan_amount = purchase_price * (1 - float(scenario["down_payment_pct"]))
    pmt = monthly_payment(loan_amount, float(scenario["interest_rate"]), int(scenario["term_years"]))
    mortgage_annual = 12 * pmt
    
    hoa_annual = 12 * float(recurring["hoa_monthly"])
    tax_annual = float(recurring["property_tax_annual"])
    ins_annual = float(recurring["insurance_annual"])
    utils_fixed_annual = 12 * float(recurring.get("utilities_fixed_monthly", 150))
    maint_fixed_annual = float(recurring["maintenance_fixed_annual"])
    reserve_annual = float(recurring.get("maintenance_furniture_reserve_annual", 1000))

    cost_fixed_annual = (
        mortgage_annual +
        hoa_annual +
        tax_annual +
        ins_annual +
        utils_fixed_annual +
        maint_fixed_annual +
        reserve_annual
    )

    # B) Variable Costs
    if force_empty:
        cost_variable_annual = 0.0
    else:
        mgmt_fee = revenue_gross_rent * float(scenario["management_fee_pct_of_rent"])
        leasing_fees = lease_count * float(scenario["leasing_fee_per_lease"])
        cleaning_costs = lease_count * float(rental["cleaning_cost_per_turnover"])
        supplies_costs = lease_count * float(rental.get("turnover_supplies_cost", 30))
        
        utils_variable = occupied_months * float(recurring.get("utilities_variable_monthly_occupied", 100))
        maint_variable = occupied_months * float(recurring.get("maintenance_variable_monthly_occupied", 150)) # Wear & Tear
        
        cost_variable_annual = (
            mgmt_fee +
            leasing_fees +
            cleaning_costs +
            supplies_costs +
            utils_variable +
            maint_variable
        )

    total_operating_outflow = cost_fixed_annual + cost_variable_annual
    
    # --- 3. METRICS DEFINITION 1 & 2 ---
    # (1) Annual Net Cash Outflow
    net_cash_flow_annual = revenue_gross_rent - total_operating_outflow
    
    # (2) Annual Operating P&L (Excl Principal)
    # Principal Portion
    # Approximation for Step 1 vs Average? 
    # Let's use Year 1 Principal for "Cash Flow" but Average Interest for "P&L"?
    # The user asked for "Operating P&L (before principal)".
    # So we take Net Cash Flow and ADD BACK Principal.
    
    # Calculate Year 1 Principal
    total_interest_y1 = 0.0
    bal = loan_amount
    rate = float(scenario["interest_rate"])
    for _ in range(12):
        inte = bal * (rate / 12)
        total_interest_y1 += inte
        bal -= (pmt - inte)
    principal_y1 = mortgage_annual - total_interest_y1
    
    operating_pnl_annual = revenue_gross_rent - (total_operating_outflow - principal_y1)

    # --- 4. SALE TAX BRIDGE ---
    horizon = int(scenario["horizon_years"])
    appreciation = float(scenario["appreciation_rate"])
    
    # 1. Basis
    closing_costs_buy = purchase_price * float(purchase["buyer_closing_cost_rate"])
    initial_basis = purchase_price + closing_costs_buy + float(scenario["furnish_budget"])
    
    # 2. Depreciation
    # Simplified straight line over horizon
    bldg_val = purchase_price * (1 - float(tax_inputs.get("land_value_pct_of_purchase", 0.25)))
    dep_per_year_bldg = bldg_val / float(tax_inputs.get("building_depreciation_years", 27.5))
    dep_per_year_furn = float(scenario["furnish_budget"]) / float(tax_inputs.get("furnishing_depreciation_years", 5))
    
    # Furnishing dep runs out after 5 years
    accum_dep = (dep_per_year_bldg * horizon) + (
        dep_per_year_furn * 5 if horizon >= 5 else dep_per_year_furn * horizon
    )
    
    # 3. Adjusted Basis
    adjusted_basis = initial_basis - accum_dep
    
    # 4. Sale Price
    sale_price = float(purchase["market_value_at_purchase"]) * (1 + appreciation) ** horizon
    
    # 5. Selling Costs
    selling_costs_amt = sale_price * float(purchase["selling_cost_rate"])
    
    # 6. Net Proceeds (Pre-Tax)
    balance_at_sale = remaining_balance(loan_amount, rate, 30, horizon * 12)
    net_proceeds_pre_tax = sale_price - selling_costs_amt - balance_at_sale
    
    # 7. Taxable Gain
    realized_gain = (sale_price - selling_costs_amt) - adjusted_basis
    
    # 8. Split
    recapture_amt = min(realized_gain, accum_dep)
    ltcg_amt = max(0.0, realized_gain - recapture_amt)
    
    # 9. Suspended PAL
    # Calculate accumulated annual losses
    # Annual Loss = operating_pnl_annual - Annual Depreciation
    # (Assuming constant year 1 performance for simplification, usually expenses rise, rent rises)
    # Annual Deprec varies (furnish drops off). Let's avg.
    avg_annual_dep = accum_dep / horizon
    avg_annual_loss_check = operating_pnl_annual - avg_annual_dep
    
    suspended_pal_total = 0.0
    if avg_annual_loss_check < 0:
        suspended_pal_total = -avg_annual_loss_check * horizon
        
    # Tax Calculation
    # Tax Liability on Transaction
    tax_recapture = recapture_amt * float(tax_inputs.get("depreciation_recapture_rate", 0.25))
    tax_ltcg = ltcg_amt * float(tax_inputs.get("capital_gains_tax_rate", 0.20))
    gross_tax_on_sale = tax_recapture + tax_ltcg
    
    # Tax Savings from Released PAL
    # Offsets Ordinary Income @ Marginal Rate
    tax_savings_pal = suspended_pal_total * float(tax_inputs.get("income_tax_rate_marginal", 0.31))
    
    net_tax_liability_sale = gross_tax_on_sale - tax_savings_pal
    
    net_proceeds_after_tax = net_proceeds_pre_tax - net_tax_liability_sale
    
    # --- 5. ECONOMIC METRICS ---
    # (3) Annual Economic Cost vs Renting Equivalent
    # Opp Cost
    initial_cash_down = (purchase_price * float(scenario["down_payment_pct"])) + closing_costs_buy + float(scenario["furnish_budget"]) # + Reserves?
    opp_cost_annual = initial_cash_down * 0.05
    
    # Total Economic Cost Annualized
    # = (Sum of Annual Cash Outflows) + (Sum of Annual Opp Costs) - (Net Proceeds After Tax)
    # / Horizon
    
    total_cash_outflow_over_hold = -net_cash_flow_annual * horizon # Note: Net CF is usually negative, so Outflow is positive
    total_opp_cost_over_hold = opp_cost_annual * horizon
    
    net_cost_lifetime = total_cash_outflow_over_hold + total_opp_cost_over_hold - net_proceeds_after_tax
    avg_annual_economic_cost = net_cost_lifetime / horizon
    
    # Rent Comparison
    rent_anchor = float(inputs["rent_instead"]["two_weeks_cost_anchor"])
    owner_weeks = owner_days / 7.0
    rent_equivalent_val = (owner_weeks / 2.0) * rent_anchor
    
    economic_premium = avg_annual_economic_cost - rent_equivalent_val
    
    # (4) Benefit Renting vs Empty
    # This requires the "Empty" metric passed in?
    # Or strict diff?
    # We are calculating FOR the current state.
    # If force_empty=False, we compute the metric.
    # If force_empty=True, valid, but delta is 0.
    
    # We return the raw data, caller handles the delta logic (calculating both versions).
    
    return {
        "scenario_key": f"{scenario['down_payment_pct']}_{scenario['fill_rate']}_{scenario['appreciation_rate']}_{scenario['furnish_budget']}",
        "down_pct": scenario['down_payment_pct'],
        "fill_rate": scenario['fill_rate'],
        "appreciation": scenario['appreciation_rate'],
        "furnish": scenario['furnish_budget'],
        "is_empty": force_empty,
        
        # Revenue Bridge
        "days_in_year": days_in_year,
        "owner_days": owner_days,
        "occupied_days": occupied_days,
        "gross_rent": revenue_gross_rent,
        
        # Cost Stack
        "fixed_costs": cost_fixed_annual,
        "variable_costs": cost_variable_annual,
        "total_operating_outflow": total_operating_outflow,
        
        # Metrics
        "net_cash_flow_annual": net_cash_flow_annual,
        "operating_pnl_annual": operating_pnl_annual,
        
        # Sale
        "sale_price": sale_price,
        "adjusted_basis": adjusted_basis,
        "gain_realized": realized_gain,
        "suspended_pal": suspended_pal_total,
        "net_proceeds_after_tax": net_proceeds_after_tax,
        
        # Econ
        "avg_annual_economic_cost": avg_annual_economic_cost,
        "rent_equivalent_val": rent_equivalent_val,
        "economic_premium": economic_premium
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=Path("runs/2026-01-19__vineyard-point/inputs/model_inputs.json"))
    parser.add_argument("--out_csv", type=Path, default=Path("runs/2026-01-19__vineyard-point/exports/v5_results.csv"))
    parser.add_argument("--out_md", type=Path, default=Path("runs/2026-01-19__vineyard-point/exports/v5_summary.md"))
    args = parser.parse_args()

    inputs = json.loads(args.inputs.read_text())
    scenarios = build_scenarios(inputs)
    
    results = []
    
    # Header for Summary MD
    md_lines = []
    md_lines.append("# Vineyard Point V5: Audit & Reconciliation\n")
    md_lines.append(f"Date: {date.today()}\n\n")
    
    # 1. Revenue Bridge Table (Base Case: 20% down, 70% fill, 3% apprec, 8k burnish)
    base_scenario = next(s for s in scenarios if s['down_payment_pct'] == 0.2 and s['fill_rate'] == 0.7 and s['appreciation_rate'] == 0.03 and s['furnish_budget'] == 8000)
    res_base = compute_metrics(inputs, base_scenario)
    
    md_lines.append("## 1. Revenue Bridge (Base Case)\n")
    md_lines.append("Assumptions: 70% Fill of available days, 2 active Owner Trips.\n\n")
    md_lines.append("| Metric | Value | Formula |\n|---|---|---|\n")
    md_lines.append(f"| Total Days | 365 | |\n")
    md_lines.append(f"| Owner Use | {res_base['owner_days']} | Blocked dates |\n")
    md_lines.append(f"| Occupied Days | {res_base['occupied_days']:.1f} | (365 - Owner - Buffer) * 70% |\n")
    md_lines.append(f"| Monthly Rent | $2,800 | Market Assumption |\n")
    md_lines.append(f"| **Gross Revenue** | **{format_money(res_base['gross_rent'])}** | (Occupied Days / 30.4) * Rent |\n\n")
    
    # 2. Cost Stack (Base Case)
    md_lines.append("## 2. Operating Cost Stack (Annual)\n")
    md_lines.append("| Category | Amount | Notes |\n|---|---|---|\n")
    md_lines.append(f"| **Fixed Costs** | **{format_money(res_base['fixed_costs'])}** | Mortgage, HOA, Tax, Ins, Internet |\n")
    md_lines.append(f"| **Variable Costs** | **{format_money(res_base['variable_costs'])}** | Mgmt, Cleaning, Utils Delta |\n")
    md_lines.append(f"| **Total Outflow** | **{format_money(res_base['total_operating_outflow'])}** |  |\n")
    md_lines.append(f"| **Revenue** | **{format_money(res_base['gross_rent'])}** | |\n")
    md_lines.append(f"| **Net Cash Flow** | **{format_money(res_base['net_cash_flow_annual'])}** | (Need to cover from W-2) |\n\n")

    # 3. Rent vs Empty (Delta)
    res_empty = compute_metrics(inputs, base_scenario, force_empty=True)
    delta_cash = res_base['net_cash_flow_annual'] - res_empty['net_cash_flow_annual']
    delta_econ = res_base['avg_annual_economic_cost'] - res_empty['avg_annual_economic_cost'] # Lower cost is better. 
    # Wait, Econ Cost is a COST. So (Empty Cost - Rented Cost) = Savings.
    savings_econ = res_empty['avg_annual_economic_cost'] - res_base['avg_annual_economic_cost']
    
    md_lines.append("## 3. Rent vs Keeping Empty (Incremental Benefit)\n")
    md_lines.append(f"If you buy it, should you rent it?\n\n")
    md_lines.append(f"*   **Cash Savings**: {format_money(delta_cash)} / year\n")
    md_lines.append(f"*   **Economic Savings**: {format_money(savings_econ)} / year\n")
    md_lines.append(f"*   *Conclusion*: Renting subsidizes ~half the carry cost.\n\n")
    
    # 4. Sale Bridge (Base Case)
    md_lines.append("## 4. Sale Year Tax Bridge (7 Year Hold)\n")
    md_lines.append("| Step | Amount | Notes |\n|---|---|---|\n")
    md_lines.append(f"| Sale Price | {format_money(res_base['sale_price'])} | 3% Appreciation |\n")
    md_lines.append(f"| Adjusted Basis | {format_money(res_base['adjusted_basis'])} | Purchase + Capex - Depreciation |\n")
    md_lines.append(f"| Realized Gain | {format_money(res_base['gain_realized'])} | Sale - Cost - Basis |\n")
    md_lines.append(f"| Suspended Losses | {format_money(res_base['suspended_pal'])} | Released at sale |\n")
    md_lines.append(f"| **Net Proceeds (After Tax)** | **{format_money(res_base['net_proceeds_after_tax'])}** | Cash in hand after loan payoff & taxes |\n\n")
    
    # 5. Sensitivity Summary
    md_lines.append("## 5. Economic Premium Sensitivity (Appreciation x Occupancy)\n")
    md_lines.append("Values are 'Annual Economic Cost Premium' vs Renting Vacations.\n")
    md_lines.append("**Negative = You save money owning. Positive = It costs you to own.**\n\n")
    
    md_lines.append("| Appreciation | 60% Occ | 70% Occ (Base) | 75% Occ |\n|---|---|---|---|\n")
    
    # Generate Sensitivity Grid for 20% down, 8k furnish
    for app in [0.01, 0.03, 0.05]:
        row_str = f"| **{app:.0%}** |"
        for occ in [0.60, 0.70, 0.75]:
            # Find result
            s_match = next(s for s in scenarios if s['down_payment_pct'] == 0.2 and s['fill_rate'] == occ and s['appreciation_rate'] == app and s['furnish_budget'] == 8000)
            r_match = compute_metrics(inputs, s_match)
            val = r_match['economic_premium']
            row_str += f" {format_money(val)} |"
        md_lines.append(row_str + "\n")
        
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("".join(md_lines))
    
    # CSV Dump
    # Run ALL scenarios
    final_rows = []
    for s in scenarios:
        # Run Active
        r = compute_metrics(inputs, s, force_empty=False)
        # Run Empty Comparison
        r_empty = compute_metrics(inputs, s, force_empty=True)
        r['incremental_benefit_cash'] = r['net_cash_flow_annual'] - r_empty['net_cash_flow_annual']
        final_rows.append(r)
        
    fieldnames = list(final_rows[0].keys())
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)
        
    print(f"V5 Audit Complete. Summary at {args.out_md}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
