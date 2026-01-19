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


def daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def clamp_year(d: date, year: int) -> date:
    return date(year, d.month, d.day)


def normalize_owner_blocks(owner_blocks: list[dict], model_year: int) -> list[DateBlock]:
    blocks: list[DateBlock] = []
    for b in owner_blocks:
        start = parse_date(b["start"])
        end = parse_date(b["end"])
        start = clamp_year(start, model_year)

        # Allow blocks that roll into the next year (e.g., Dec 26 -> Jan 08)
        if end.month == 1 and start.month == 12:
            end = date(model_year + 1, end.month, end.day)
        else:
            end = clamp_year(end, model_year)

        blocks.append(DateBlock(start=start, end=end))

    # Merge overlapping blocks (defensive)
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
    """Returns (leasable_days, lease_count) assuming 30/60/90-day leases but min is min_lease_days.

    Because lease sizes are multiples of 30 in this model, and min lease is 30, the maximum leasable
    time in a window is simply floor(window_len / min_lease_days) * min_lease_days.
    """

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
    if r == 0:
        return max(0.0, principal * (1 - months_paid / n))

    pmt = monthly_payment(principal, annual_rate, term_years)
    # Standard amortization formula for remaining balance after k payments
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
            }
        )

    return scenarios


def compute_metrics(inputs: dict, scenario: dict, model_year: int = 2026) -> dict:
    purchase = inputs["property"]["purchase"]
    recurring = inputs["recurring_costs"]
    rental = inputs["rental"]
    budget = inputs["cash_budget"]
    owner_scenarios = inputs["owner_use"]["scenarios"]

    purchase_price = float(purchase["purchase_price"])
    closing_cost = purchase_price * float(purchase["buyer_closing_cost_rate"])
    down_payment = purchase_price * float(scenario["down_payment_pct"])
    loan_amount = max(0.0, purchase_price - down_payment)

    liquidity_reserve = float(budget["recommended_liquidity_reserve"])
    upfront_spend = down_payment + closing_cost + float(scenario["furnish_budget"])
    upfront_cash_required = upfront_spend + liquidity_reserve
    within_cash_budget = upfront_cash_required <= float(budget["max_total_cash_available"])

    annual_rate = float(scenario["interest_rate"])
    term_years = int(scenario["term_years"])
    pmt = monthly_payment(loan_amount, annual_rate, term_years)

    year_start = date(model_year, 1, 1)
    year_end = date(model_year, 12, 31)

    owner_blocks_raw = owner_scenarios[scenario["owner_use_scenario"]]["blocks"]
    owner_blocks = normalize_owner_blocks(owner_blocks_raw, model_year=model_year)

    # For lease feasibility, treat owner blocks + buffer days as unavailable
    blocked_for_leasing = apply_buffer(owner_blocks, int(rental["turnover_buffer_days"]))
    free_windows = invert_blocks(year_start, year_end, blocked_for_leasing)

    leasable_days, lease_count = leasable_days_from_windows(
        free_windows, int(rental["min_lease_days"])
    )
    effective_tenant_days = leasable_days * float(scenario["fill_rate"])
    tenant_months = effective_tenant_days / AVG_DAYS_PER_MONTH

    gross_rent = tenant_months * float(scenario["monthly_rent"])

    mgmt_fee = gross_rent * float(scenario["management_fee_pct_of_rent"])
    leasing_fees = lease_count * float(scenario["leasing_fee_per_lease"]) * float(scenario["fill_rate"])
    cleaning = lease_count * float(rental["cleaning_cost_per_turnover"]) * float(scenario["fill_rate"])

    hoa = 12 * float(recurring["hoa_monthly"])
    taxes = float(recurring["property_tax_annual"])
    insurance = float(recurring["insurance_annual"])

    utilities_gross = 12 * float(recurring["utilities_owner_paid_monthly"])
    utilities_reimb = utilities_gross * float(recurring["utilities_tenant_reimbursement_rate"]) * (
        effective_tenant_days / 365.25
    )
    utilities_net = utilities_gross - utilities_reimb

    maintenance = float(recurring["maintenance_fixed_annual"]) + tenant_months * float(
        recurring["maintenance_per_tenant_month"]
    )

    mortgage_annual = 12 * pmt

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

    # Rent-instead baseline for owner-use weeks
    rent_anchor_two_weeks = float(inputs["rent_instead"]["two_weeks_cost_anchor"])
    owner_days = sum(b.days_inclusive() for b in owner_blocks)
    owner_weeks_equiv = owner_days / 7.0
    rent_instead_cost = (owner_weeks_equiv / 2.0) * rent_anchor_two_weeks

    ownership_premium = (-net_operating_cashflow) - rent_instead_cost

    # Terminal sale (simple): appreciate from market value at purchase, subtract selling costs, pay off remaining loan
    horizon_years = int(scenario["horizon_years"])
    sale_price = float(purchase["market_value_at_purchase"]) * (1 + float(purchase["annual_appreciation_rate"])) ** (
        horizon_years
    )
    selling_costs = sale_price * float(purchase["selling_cost_rate"])
    balance = remaining_balance(loan_amount, annual_rate, term_years, months_paid=horizon_years * 12)
    net_sale_proceeds_before_tax = sale_price - selling_costs - balance

    # Tax calculations: 280A "Residence" Rules (No W-2 Offset)
    tax = inputs["tax"]
    marginal_rate = float(tax["income_tax_rate_marginal"])
    section_280a = tax.get("section_280a_apply", True)

    # 1. Calculate Mortgage Interest (Sum of monthly interest over horizon)
    total_mortgage_interest = 0.0
    balance_sim = loan_amount
    for year in range(horizon_years):
        for _ in range(12):
            monthly_interest = balance_sim * (annual_rate / 12)
            total_mortgage_interest += monthly_interest
            balance_sim -= (pmt - monthly_interest)
            if balance_sim <= 0: break
    avg_annual_mortgage_interest = total_mortgage_interest / horizon_years

    # 2. Allocation Ratios (IRS "Days Used" Method for Tier 2/3)
    # Note: For Tier 1 (Interest/Taxes), courts allow "Bolton" (Days/365), but IRS prefers Days/Days.
    # We use Days/Days for conservatism and consistency.
    total_days_used = effective_tenant_days + owner_days
    rental_use_ratio = effective_tenant_days / total_days_used if total_days_used > 0 else 0
    personal_use_ratio = 1.0 - rental_use_ratio

    # 3. Categorize Expenses (Annualized)
    # Direct Rental Expenses (100% deductible against rental income)
    direct_rental_expenses = mgmt_fee + leasing_fees + cleaning
    
    # Indirect Expenses (Prorated)
    indirect_operating = float(recurring["insurance_annual"]) + utilities_net + maintenance + (12 * float(recurring["hoa_monthly"]))
    indirect_taxes = float(recurring["property_tax_annual"])
    indirect_interest = avg_annual_mortgage_interest

    # 4. Tiered Deduction Logic (Annual)
    # Tier 1: Interest & Taxes (Rental Portion)
    tier_1_deduction = (indirect_interest + indirect_taxes) * rental_use_ratio
    
    # Tier 2: Operating Expenses (Direct + Prorated Indirect)
    tier_2_deduction = direct_rental_expenses + (indirect_operating * rental_use_ratio)
    
    # Tier 3: Depreciation
    land_value = float(purchase["purchase_price"]) * float(tax["land_value_pct_of_purchase"])
    building_value = float(purchase["purchase_price"]) - land_value
    building_depreciation_years = float(tax["building_depreciation_years"])
    furnish_depreciation_years = float(tax["furnishing_depreciation_years"])
    
    annual_bldg_dep = building_value / building_depreciation_years
    annual_furn_dep = float(scenario["furnish_budget"]) / furnish_depreciation_years
    # Note: Furnishing depreciation stops after 5 years, but for annual avg we smooth it or check horizon
    potential_depreciation = annual_bldg_dep + (annual_furn_dep if horizon_years <= 5 else annual_furn_dep * (5/horizon_years))

    # Calculate Net Rental Income (The 280A Limit)
    # Income = Gross Rent
    # Limit: Deductions cannot exceed income. Ordering: Tier 1 -> Tier 2 -> Tier 3
    
    net_rent_after_tier_1 = max(0.0, gross_rent - tier_1_deduction)
    # Tier 2 is fully deductible if space remains? 
    # Actually 280A says: Tier 2 is deductible. If it creates loss, that loss is suspended.
    # Tier 3 (Deprec) is deductible ONLY if Income > Tier 1 + Tier 2.
    
    rent_remaining_for_deprec = max(0.0, gross_rent - tier_1_deduction - tier_2_deduction)
    
    if section_280a:
        allowed_depreciation = min(potential_depreciation, rent_remaining_for_deprec)
        # Any operating loss is also suspended, but for "Tax Benefit" calculation:
        # If we have a loss, Taxable Income is 0. Benefit = 0.
        # If we have profit, Depreciation shields it. Benefit = Refund Avoided.
        
        # Taxable Income Calculation:
        # Taxable = Gross - Tier 1 - Tier 2 - Allowed_Deprec
        # Under 280A, this floor is 0.
        taxable_rental_income = max(0.0, gross_rent - tier_1_deduction - tier_2_deduction - allowed_depreciation)
    else:
        # Investment property rules (losses allowed against W-2 if within PAL limits, OR suspended but released on sale)
        # If we assume "released on sale", we can count the tax benefit (discounted).
        # But user is "Residence".
        allowed_depreciation = potential_depreciation
        taxable_rental_income = gross_rent - tier_1_deduction - tier_2_deduction - allowed_depreciation
    
    # 5. Total Tax Benefit Calculation
    # Benefit = (Taxable Income WITHOUT Strategy) - (Taxable Income WITH Strategy)
    # Without Strategy (i.e. if you just held cash): You pay 0 tax on rental (logic stretch).
    # Simpler: Tax Benefit = (Tax Liability if Expenses were Non-Deductible) - (Actual Tax Liability)
    # Real World: Tax Benefit = Reduction in Total Tax Bill.
    # Since rental likely runs at a loss (pre-deprec), Taxable Income is 0. Tax Bill is 0.
    # W-2 Tax Bill is unchanged.
    # So Total Tax Benefit = 0.
    
    # Exception: If net_rent_after_tier_1_and_2 > 0, then we ARE making taxable profit.
    # Depreciation shields this.
    # Benefit = Allowed_Depreciation * Marginal_Rate.
    
    depreciation_tax_benefit_annual = allowed_depreciation * marginal_rate
    
    # Mortgage Interest Benefit (Schedule A - Personal Portion)
    # User likely capped ($10k SALT hit, $750k Debt limited). Conservative = 0.
    mortgage_interest_tax_benefit_annual = 0.0 

    mortgage_interest_tax_benefit = mortgage_interest_tax_benefit_annual * horizon_years
    depreciation_tax_benefit = depreciation_tax_benefit_annual * horizon_years
    total_tax_benefits = mortgage_interest_tax_benefit + depreciation_tax_benefit
    
    # 6. Recapture on Sale (Only on ALLOWED depreciation)
    total_depreciation_taken = allowed_depreciation * horizon_years
    depreciation_recapture_tax = total_depreciation_taken * float(tax["depreciation_recapture_rate"])
    
    # Cost basis for cap gains: includes improvements (furnishings already in scenario)
    cost_basis = float(purchase["purchase_price"]) + closing_cost + float(scenario["furnish_budget"])
    
    # Adjusted Basis
    adjusted_basis = cost_basis - total_depreciation_taken
    
    # Capital Gain
    gain_on_sale = max(0.0, sale_price - selling_costs - adjusted_basis)
    # Recapture portion is taxed at 25% (or marginal?), remaining at 20%
    # Recapture is strictly lesser of Gain or Deprec Taken
    recapture_portion = min(gain_on_sale, total_depreciation_taken)
    capital_gain_portion = max(0.0, gain_on_sale - recapture_portion)
    
    cap_gains_tax = capital_gain_portion * float(tax["capital_gains_tax_rate"])
    total_sale_taxes = (recapture_portion * float(tax["depreciation_recapture_rate"])) + cap_gains_tax
    
    # Re-calculate correct net sale proceeds using new tax logic
    # Original 'net_sale_proceeds_before_tax' was: sale_price - selling_costs - balance
    # Taxes are paid from that.
    net_sale_proceeds = (sale_price - selling_costs - balance) - total_sale_taxes

    # Total Economic Cost
    # We treat 'total_tax_benefits' as a reduction in cost (cash saved).
    # But wait, if benefit is 0, cost is high.
    
    total_net_cost_before_tax_benefits = upfront_spend + (-net_operating_cashflow * horizon_years) - ((sale_price - selling_costs - balance) - 0.0) # approx
    total_net_cost = upfront_spend + (-net_operating_cashflow * horizon_years) - net_sale_proceeds - total_tax_benefits
    avg_annual_cost = total_net_cost / horizon_years
    ownership_premium_economic = avg_annual_cost - rent_instead_cost

    return {
        **scenario,
        "purchase_price": purchase_price,
        "loan_amount": loan_amount,
        "monthly_payment": pmt,
        "liquidity_reserve": liquidity_reserve,
        "upfront_spend": upfront_spend,
        "upfront_cash_required": upfront_cash_required,
        "within_cash_budget": within_cash_budget,
        "owner_days": owner_days,
        "leasable_days": leasable_days,
        "effective_tenant_days": effective_tenant_days,
        "lease_count": lease_count,
        "tenant_months": tenant_months,
        "gross_rent": gross_rent,
        "operating_costs": operating_costs,
        "net_operating_cashflow": net_operating_cashflow,
        "rent_instead_cost": rent_instead_cost,
        "ownership_premium": ownership_premium,
        "ownership_premium_economic": ownership_premium_economic,
        "sale_price": sale_price,
        "net_sale_proceeds": net_sale_proceeds,
        "total_mortgage_interest": total_mortgage_interest,
        "total_depreciation_taken": total_depreciation_taken,
        "mortgage_interest_tax_benefit": mortgage_interest_tax_benefit,
        "depreciation_tax_benefit": depreciation_tax_benefit,
        "total_tax_benefits": total_tax_benefits,
        "depreciation_recapture_tax": depreciation_recapture_tax,
        "cap_gains_tax": cap_gains_tax,
        "total_net_cost": total_net_cost,
        "avg_annual_cost": avg_annual_cost,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("no rows")
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = []
    for row in rows:
        for k in row.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_summary(path: Path, rows: list[dict], top_n: int = 12) -> None:
    if not rows:
        raise ValueError("no rows")

    rows_sorted = sorted(rows, key=lambda r: (not r["within_cash_budget"], r["ownership_premium"]))

    lines: list[str] = []
    lines.append("# Vineyard Point — Scenario Summary\n")
    lines.append("Generated by `runs/2026-01-19__vineyard-point/scripts/vineyard_point_model.py`.\n")
    lines.append("\n")
    lines.append("## Top scenarios (lowest ownership premium)\n")
    lines.append("\n")
    lines.append(
        "| ok cash? | horizon | down | rate | rent | fill | mgmt | lease fee | furnish | owner-use | owner days | tenant months | net op CF | rent-instead | premium | econ premium | avg annual cost |"
    )
    lines.append(
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|"
    )

    for r in rows_sorted[:top_n]:
        lines.append(
            "| {ok} | {h} | {down:.0%} | {rate:.1%} | {rent:.0f} | {fill:.0%} | {mgmt:.0%} | {lease_fee:.0f} | {furn:.0f} | {owner} | {od} | {tm:.1f} | {cf} | {ri} | {prem} | {eprem} | {aac} |".format(
                ok="yes" if r["within_cash_budget"] else "no",
                h=int(r["horizon_years"]),
                down=float(r["down_payment_pct"]),
                rate=float(r["interest_rate"]),
                rent=float(r["monthly_rent"]),
                fill=float(r["fill_rate"]),
                mgmt=float(r["management_fee_pct_of_rent"]),
                lease_fee=float(r["leasing_fee_per_lease"]),
                furn=float(r["furnish_budget"]),
                owner=str(r["owner_use_scenario"]),
                od=int(r["owner_days"]),
                tm=float(r["tenant_months"]),
                cf=format_money(float(r["net_operating_cashflow"])),
                ri=format_money(float(r["rent_instead_cost"])),
                prem=format_money(float(r["ownership_premium"])),
                eprem=format_money(float(r["ownership_premium_economic"])),
                aac=format_money(float(r["avg_annual_cost"])),
            )
        )

    lines.append("\n")
    lines.append("Notes:\n")
    lines.append("- 'Premium' is: (out-of-pocket after rent offset) minus 'rent-instead' cost for the owner-use weeks.\n")
    lines.append("- 'Econ premium' is: average annual cost (includes a simplified sale estimate) minus 'rent-instead'.\n")
    lines.append("- This model is intentionally simple; treat it as directional until HOA rules + rent comps are verified.\n")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputs",
        type=Path,
        default=Path("runs/2026-01-19__vineyard-point/inputs/model_inputs.json"),
    )
    parser.add_argument(
        "--out_csv",
        type=Path,
        default=Path("runs/2026-01-19__vineyard-point/exports/scenario_results.csv"),
    )
    parser.add_argument(
        "--out_md",
        type=Path,
        default=Path("runs/2026-01-19__vineyard-point/exports/scenario_summary.md"),
    )
    args = parser.parse_args()

    inputs = json.loads(args.inputs.read_text())
    scenarios = build_scenarios(inputs)

    rows: list[dict] = []
    for s in scenarios:
        rows.append(compute_metrics(inputs, s))

    write_csv(args.out_csv, rows)
    write_markdown_summary(args.out_md, rows)

    # Minimal console output for quick sanity
    best = sorted(rows, key=lambda r: (not r["within_cash_budget"], r["ownership_premium"]))[:5]
    print(f"Wrote {len(rows)} scenarios -> {args.out_csv}")
    for r in best:
        ok = "OK" if r["within_cash_budget"] else "OVER"
        print(
            f"{ok} premium={format_money(r['ownership_premium'])} avg_annual_cost={format_money(r['avg_annual_cost'])} "
            f"rent={format_money(r['monthly_rent'])}/mo fill={r['fill_rate']:.0%} down={r['down_payment_pct']:.0%} rate={r['interest_rate']:.1%} "
            f"owner={r['owner_use_scenario']} furnish={format_money(r['furnish_budget'])} horizon={r['horizon_years']}y"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
