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

        # Allow blocks that roll into the next year (e.g., Dec 26 -> Jan 08)
        if end.month == 1 and start.month == 12:
            end = date(model_year + 1, end.month, end.day)
        else:
            end = _clamp_year(end, model_year)

        blocks.append(DateBlock(start=start, end=end))

    # Merge overlapping blocks
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

    # Re-merge after buffering
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
    if principal <= 0:
        return 0.0
    r = annual_rate / 12
    n = term_years * 12
    if r == 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def remaining_balance(principal: float, annual_rate: float, term_years: int, months_paid: int) -> float:
    if principal <= 0:
        return 0.0
    r = annual_rate / 12
    n = term_years * 12
    # if r == 0: return principal - (principal/n)*k # Logic check: r=0 in next func
    if r == 0:
         return max(0.0, principal * (1 - months_paid / n))

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
    owner_use = inputs["owner_use"]["scenarios"]

    mgmt_fee_options = rental.get(
        "management_fee_pct_of_rent_options",
        [rental["management_fee_pct_of_rent"]],
    )
    leasing_fee_options = rental.get(
        "leasing_fee_per_lease_options",
        [rental["leasing_fee_per_lease"]],
    )
    
    appreciation_options = prop.get(
        "annual_appreciation_rate_options",
        [prop.get("annual_appreciation_rate", 0.03)]
    )

    scenarios: list[dict] = []

    for (
        down_pct,
        rate,
        furnish_budget,
        monthly_rent,
        fill_rate,
        mgmt_fee_pct,
        leasing_fee,
        owner_key,
        horizon_years,
        appreciation_rate
    ) in product(
        financing["down_payment_pct_options"],
        financing["interest_rate_options"],
        upfront["furnish_renovation_budget_options"],
        rental["monthly_rent_options"],
        rental["market_fill_rate_options"],
        mgmt_fee_options,
        leasing_fee_options,
        owner_use.keys(),
        prop["sale_horizon_years_options"],
        appreciation_options
    ):
        scenarios.append(
            {
                "down_payment_pct": float(down_pct),
                "interest_rate": float(rate),
                "term_years": int(financing["term_years"]),
                "furnish_budget": float(furnish_budget),
                "monthly_rent": float(monthly_rent),
                "fill_rate": float(fill_rate),
                "management_fee_pct_of_rent": float(mgmt_fee_pct),
                "leasing_fee_per_lease": float(leasing_fee),
                "owner_use_scenario": owner_key,
                "horizon_years": int(horizon_years),
                "appreciation_rate": float(appreciation_rate)
            }
        )

    return scenarios


def compute_metrics(inputs: dict, scenario: dict, force_empty: bool = False, model_year: int = 2026) -> dict:
    """
    Computes financial metrics (Cash Flow, Net Cost, Economic Cost) for a single scenario.
    If force_empty=True, assumes Property is held vacant (Personal Use Only, No Rent).
    """
    purchase = inputs["property"]["purchase"]
    recurring = inputs["recurring_costs"]
    rental = inputs["rental"]
    budget = inputs["cash_budget"]
    owner_scenarios = inputs["owner_use"]["scenarios"]
    tax_inputs = inputs.get("tax", {})

    # 1. Purchase & Upfront
    purchase_price = float(purchase["purchase_price"])
    closing_cost = purchase_price * float(purchase["buyer_closing_cost_rate"])
    down_payment = purchase_price * float(scenario["down_payment_pct"])
    loan_amount = max(0.0, purchase_price - down_payment)

    liquidity_reserve = float(budget.get("recommended_liquidity_reserve", 0))
    upfront_spend = down_payment + closing_cost + float(scenario["furnish_budget"])
    upfront_cash_required = upfront_spend + liquidity_reserve
    within_cash_budget = upfront_cash_required <= float(budget["max_total_cash_available"])

    # 2. Debt Service
    annual_rate = float(scenario["interest_rate"])
    term_years = int(scenario["term_years"])
    pmt = monthly_payment(loan_amount, annual_rate, term_years)
    mortgage_annual = 12 * pmt

    # 3. Usage & Operating Revenue
    year_start = date(model_year, 1, 1)
    year_end = date(model_year, 12, 31)
    
    owner_blocks_raw = owner_scenarios[scenario["owner_use_scenario"]]["blocks"]
    owner_blocks = normalize_owner_blocks(owner_blocks_raw, model_year=model_year)
    owner_days = sum(b.days_inclusive() for b in owner_blocks)

    if force_empty:
        # Empty Scenario: No tenants, no rental revenue
        leasable_days = 0
        effective_tenant_days = 0
        lease_count = 0
        tenant_months = 0.0
        gross_rent = 0.0
        mgmt_fee = 0.0
        leasing_fees = 0.0
        cleaning = 0.0
        utilities_reimb = 0.0
    else:
        # Active Rental Scenario
        blocked_for_leasing = apply_buffer(owner_blocks, int(rental["turnover_buffer_days"]))
        free_windows = invert_blocks(year_start, year_end, blocked_for_leasing)
        leasable_days, lease_count = leasable_days_from_windows(free_windows, int(rental["min_lease_days"]))
        effective_tenant_days = leasable_days * float(scenario["fill_rate"])
        tenant_months = effective_tenant_days / AVG_DAYS_PER_MONTH
        gross_rent = tenant_months * float(scenario["monthly_rent"])
        
        mgmt_fee = gross_rent * float(scenario["management_fee_pct_of_rent"])
        leasing_fees = lease_count * float(scenario["leasing_fee_per_lease"]) * float(scenario["fill_rate"])
        cleaning = lease_count * float(rental["cleaning_cost_per_turnover"]) * float(scenario["fill_rate"])
        
        utilities_gross = 12 * float(recurring["utilities_owner_paid_monthly"])
        utilities_reimb = utilities_gross * float(recurring["utilities_tenant_reimbursement_rate"]) * (effective_tenant_days / 365.25)

    # 4. Operating Expenses
    hoa = 12 * float(recurring["hoa_monthly"])
    taxes = float(recurring["property_tax_annual"])
    insurance = float(recurring["insurance_annual"])
    
    utilities_gross = 12 * float(recurring["utilities_owner_paid_monthly"])
    if force_empty:
        utilities_net = utilities_gross # No reimbursement
    else:
        utilities_net = utilities_gross - utilities_reimb

    # Maintenance
    fixed_maint = float(recurring["maintenance_fixed_annual"])
    furniture_res = float(recurring.get("maintenance_furniture_reserve_annual", 0))
    variable_maint = tenant_months * float(recurring["maintenance_per_tenant_month"])
    maintenance = fixed_maint + variable_maint + furniture_res

    operating_costs = (
        mortgage_annual
        + hoa
        + taxes
        + insurance
        + utilities_net
        + maintenance
        + mgmt_fee
        + leasing_fees
        + cleaning
    )
    
    net_operating_cashflow = gross_rent - operating_costs
    
    # 5. Sale & Appreciation
    horizon_years = int(scenario["horizon_years"])
    appreciation_rate = float(scenario["appreciation_rate"]) # Using per-scenario rate
    
    sale_price = float(purchase["market_value_at_purchase"]) * (1 + appreciation_rate) ** horizon_years
    selling_costs = sale_price * float(purchase["selling_cost_rate"])
    balance = remaining_balance(loan_amount, annual_rate, term_years, months_paid=horizon_years * 12)
    
    # 6. Tax Logic (High Income / PAL / 280A)
    # Rules:
    # - If high_income_pal_rules or section_280a: Net losses are SUSPENDED.
    # - Suspended losses are released at SALE.
    # - We assume 'high_income_pal_rules' dominates for simplicity (Annual Benefit = 0 if Loss).
    
    marginal_rate = float(tax_inputs.get("income_tax_rate_marginal", 0.35))
    high_income_rules = tax_inputs.get("high_income_pal_rules", False) or tax_inputs.get("section_280a_apply", False)

    # Calculate Interest Component (Avg Annual)
    total_interest_paid_over_hold = 0.0
    sim_balance = loan_amount
    for _ in range(horizon_years * 12):
        inte = sim_balance * (annual_rate / 12)
        total_interest_paid_over_hold += inte
        sim_balance -= (pmt - inte)
    avg_annual_interest = total_interest_paid_over_hold / horizon_years

    # Depreciation
    bldg_val = purchase_price * (1 - float(tax_inputs.get("land_value_pct_of_purchase", 0.25)))
    annual_bldg_dep = bldg_val / float(tax_inputs.get("building_depreciation_years", 27.5))
    annual_furn_dep = float(scenario["furnish_budget"]) / float(tax_inputs.get("furnishing_depreciation_years", 5))
    
    # Simple Loop for Suspended Loss Accumulation
    suspended_losses = 0.0
    accumulated_tax_benefit_annual = 0.0 # From deductible/released items during hold (not likely with PAL)
    
    # We'll use a simplified annual model for tax (assuming constant year 1 financials)
    # Taxable Income = Gross Rent - (Interest + Taxes + Insurance + HOA + Maint + Mgmt + Deprec)
    # Note: Principal paydown is NOT deductible.
    
    # SALT / Sched A Logic:
    # If high_income_rules, the specific "rental loss" is suspended. 
    # BUT, property tax and interest (allocable to personal use, or up to SALT cap) might still be deductible on Sched A.
    # The prompt asks for "Suspended Passive Losses" mechanics.
    # We will assume:
    # 1. Calculate Net Rental P&L (including all allocable deductions).
    # 2. If Loss -> Suspend.
    # 3. If Gain -> Tax it.
    
    # Annual P&L (Tax)
    annual_deductions_cash = operating_costs - (mortgage_annual - avg_annual_interest) # Remove principal
    total_deprec_annual = annual_bldg_dep + (annual_furn_dep if horizon_years <= 5 else annual_furn_dep * (5/horizon_years))
    
    taxable_pnl_annual = gross_rent - annual_deductions_cash - total_deprec_annual
    
    annual_tax_cash_impact = 0.0
    
    if taxable_pnl_annual < 0:
        if high_income_rules:
            # Loss suspended
            suspended_losses += (-taxable_pnl_annual * horizon_years)
            annual_tax_cash_impact = 0.0
        else:
            # Loss allowed (e.g. Real Estate Pro or Low Income)
            benefit = -taxable_pnl_annual * marginal_rate
            annual_tax_cash_impact = benefit # Cash IN (refund)
    else:
        # Profit -> Taxed
        cost = taxable_pnl_annual * marginal_rate
        annual_tax_cash_impact = -cost # Cash OUT (tax paid)

    # Sale Tax
    # 1. Release Suspended Losses
    # 2. Calculate Gain
    # Recapture
    total_deprec_taken = total_deprec_annual * horizon_years
    adjusted_basis = (purchase_price + closing_cost + float(scenario["furnish_budget"])) - total_deprec_taken
    
    gain_on_sale = sale_price - selling_costs - adjusted_basis
    
    # Tax on Sale:
    # Logic: Recognized Gain = gain_on_sale.
    # Offset by Suspended Losses? 
    # Yes, suspended losses are fully deductible in year of disposition.
    # Effectively: Taxable Gain = gain_on_sale - suspended_losses.
    
    recapture_amt = min(gain_on_sale, total_deprec_taken)
    cap_gain_amt = max(0.0, gain_on_sale - recapture_amt)
    
    tax_on_gain = (recapture_amt * float(tax_inputs.get("depreciation_recapture_rate", 0.25))) + \
                  (cap_gain_amt * float(tax_inputs.get("capital_gains_tax_rate", 0.20)))
    
    tax_benefit_released_losses = suspended_losses * marginal_rate
    
    net_tax_at_sale = tax_on_gain - tax_benefit_released_losses
    
    # Net Sale Proceeds (After Tax)
    net_sale_proceeds_after_tax = (sale_price - selling_costs - balance) - net_tax_at_sale

    # 7. Opportunity Cost
    # "Apply opportunity cost ONLY to upfront cash... treat as distinct economic cost"
    opp_cost_rate = 0.05 # Fixed assumption per prompt
    annual_opp_cost_equity = upfront_cash_required * opp_cost_rate
    total_opp_cost = annual_opp_cost_equity * horizon_years

    # 8. Aggregation
    
    # Cash Method Cost: (Upfront + AnnualDeficits - SaleProceeds)
    # Note: strictly cash. No opp cost.
    # 'annual_tax_cash_impact' is included as an annual cash flow (-cost or +benefit)
    
    total_cash_cost = upfront_spend + \
                      ((-net_operating_cashflow - annual_tax_cash_impact) * horizon_years) - \
                      net_sale_proceeds_after_tax
                      
    avg_annual_cash_cost = total_cash_cost / horizon_years
    
    # Economic Cost: Cash Cost + Opportunity Cost
    total_economic_cost = total_cash_cost + total_opp_cost
    avg_annual_economic_cost = total_economic_cost / horizon_years
    
    # Rent Instead Comparison
    rent_anchor_two_weeks = float(inputs["rent_instead"]["two_weeks_cost_anchor"])
    owner_weeks = owner_days / 7.0
    rent_instead_val = (owner_weeks / 2.0) * rent_anchor_two_weeks
    
    ownership_premium_cash = avg_annual_cash_cost - rent_instead_val
    ownership_premium_economic = avg_annual_economic_cost - rent_instead_val

    return {
        **scenario,
        "upfront_cash_required": upfront_cash_required,
        "within_cash_budget": within_cash_budget,
        "gross_rent": gross_rent,
        "net_operating_cashflow": net_operating_cashflow,
        "annual_appreciation_used": appreciation_rate,
        "sale_price": sale_price,
        "net_sale_procees_after_tax": net_sale_proceeds_after_tax,
        "suspended_losses_total": suspended_losses,
        "tax_save_on_sale_from_losses": tax_benefit_released_losses,
        "annual_opp_cost_equity": annual_opp_cost_equity,
        "rent_instead_val": rent_instead_val,
        "avg_annual_cash_cost": avg_annual_cash_cost,
        "avg_annual_economic_cost": avg_annual_economic_cost,
        "ownership_premium_cash": ownership_premium_cash,
        "ownership_premium_economic": ownership_premium_economic,
        "owner_days": owner_days,
        "tenant_months": tenant_months
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_summary(path: Path, rows: list[dict], empty_scenario_cost: float, top_n: int = 15) -> None:
    if not rows:
        return

    # Sort by Economic Premium (Ascending)
    rows_sorted = sorted(rows, key=lambda r: (not r["within_cash_budget"], r["ownership_premium_economic"]))

    lines: list[str] = []
    lines.append("# Vineyard Point — Financial Analysis V4 (High Income / PAL Rules)\n")
    lines.append(f"Generated: {date.today()}\n")
    lines.append(f"**Baseline 'Empty Property' Cost**: {format_money(empty_scenario_cost)} / yr (Cash Burn)\n")
    lines.append("\n")
    
    lines.append("## Top Scenarios (Lowest Economic Premium)\n")
    lines.append("Ranking metric: `ownership_premium_economic` (Annual Econ Cost - Rent Value avoided).\n")
    lines.append("\n")
    
    header = "| Horizon | Apprec | Down | Furnish | Owner Days | Net Op Cash | Opp Cost (Eq) | Avg Annual Cash | Avg Annual Econ | Premium (Econ) | Incr Benefit vs Empty |"
    lines.append(header)
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    
    for r in rows_sorted[:top_n]:
        # Incremental Benefit = Empty Cost - This Scenario Cash Cost
        # Usage: Positive means Renting is better than Empty
        incr_benefit = empty_scenario_cost - r["avg_annual_cash_cost"]
        
        lines.append(
             f"| {r['horizon_years']}y | {r['appreciation_rate']:.1%} | {r['down_payment_pct']:.0%} "
             f"| {format_money(r['furnish_budget'])} | {r['owner_days']} "
             f"| {format_money(r['net_operating_cashflow'])} | {format_money(r['annual_opp_cost_equity'])} "
             f"| {format_money(r['avg_annual_cash_cost'])} | {format_money(r['avg_annual_economic_cost'])} "
             f"| **{format_money(r['ownership_premium_economic'])}** | {format_money(incr_benefit)} |"
        )
        
    lines.append("\n")
    lines.append("## Definitions\n")
    lines.append("1. **Net Op Cash**: Rent - (Mtg + HOA + Tax + Ins + Maint + Mgmt).\n")
    lines.append("2. **Opp Cost (Eq)**: 5% return on Upfront Cash (Down + Furnish + Closing).\n")
    lines.append("3. **Avg Annual Econ**: Net Cash Cost + Opp Cost - (Sale Profit / Yrs).\n")
    lines.append("4. **Premium (Econ)**: Avg Annual Econ - Rent Value of Vacation Time (Airbnb comp).\n")
    lines.append("5. **Incr Benefit vs Empty**: How much cash renting saves vs keeping it empty (Net Cost Empty - Net Cost Rented).\n")

    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=Path("runs/2026-01-19__vineyard-point/inputs/model_inputs.json"))
    parser.add_argument("--out_csv", type=Path, default=Path("runs/2026-01-19__vineyard-point/exports/scenario_results.csv"))
    parser.add_argument("--out_md", type=Path, default=Path("runs/2026-01-19__vineyard-point/exports/scenario_summary.md"))
    args = parser.parse_args()

    inputs = json.loads(args.inputs.read_text())
    
    scenarios = build_scenarios(inputs)
    
    results = []
    median_empty_cost = 0.0
    
    for s in scenarios:
        res_actual = compute_metrics(inputs, s, force_empty=False)
        res_empty = compute_metrics(inputs, s, force_empty=True)
        res_actual["incremental_renting_cash_benefit"] = res_empty["avg_annual_cash_cost"] - res_actual["avg_annual_cash_cost"]
        
        if s["down_payment_pct"] == 0.2 and s["interest_rate"] == 0.07:
             median_empty_cost = res_empty["avg_annual_cash_cost"]
             
        results.append(res_actual)

    write_csv(args.out_csv, results)
    write_markdown_summary(args.out_md, results, median_empty_cost)
    
    best = sorted(results, key=lambda r: (not r["within_cash_budget"], r["ownership_premium_economic"]))[:3]
    print(f"Generated {len(results)} scenarios.")
    for b in best:
        print(f"EconPrem: {format_money(b['ownership_premium_economic'])} | CashIncBen: {format_money(b['incremental_renting_cash_benefit'])} | Apprec: {b['appreciation_rate']:.0%}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
