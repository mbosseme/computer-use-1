#!/usr/bin/env python3
"""Second-home condo ownership net cost model.

Run-local script for:
- 48-month amortization
- 4-year cashflow + economic net cost reconciliation
- Sensitivity table
- Retirement timing extension

Outputs are written under runs/<RUN_ID>/exports/.

This intentionally avoids extra dependencies (pure stdlib).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


RUN_ID = "2026-01-17__second-home-condo-net-cost"
RUN_DIR = Path(__file__).resolve().parents[1]
EXPORTS_DIR = RUN_DIR / "exports"
DEFAULT_INPUTS_PATH = RUN_DIR / "inputs" / "model_inputs.json"


@dataclass(frozen=True)
class Assumptions:
    # Property / hold
    # market_value_at_purchase is used for appreciation/sale-price trajectory.
    # purchase_price is what you actually pay (basis/cash-to-close are driven off this).
    market_value_at_purchase: float = 284_990.0
    purchase_price: float = 284_990.0
    hold_years: int = 4
    appreciation_rate: float = 0.04
    selling_friction_rate: float = 0.07

    # Financing
    down_payment_rate: float = 0.25
    mortgage_rate_annual: float = 0.0625
    mortgage_term_months: int = 360

    # Upfront
    furnishings: float = 10_000.0
    furnishings_salvage_rate: float = 0.0  # treated as an end-of-hold cash inflow; tax ignored by default
    buyer_closing_cost_rate: float = 0.02  # all-in cash to close, excluding down payment
    closing_cost_basis_fraction: float = 0.50  # portion assumed capitalizable into basis

    # Recurring
    hoa_monthly: float = 200.0
    property_tax_annual: float = 1_576.0
    insurance_annual: float = 900.0
    maintenance_annual: float = 0.0
    utilities_monthly: float = 75.0

    # Tax (federal + NY; NYC excluded)
    federal_ordinary_rate: float = 0.25
    ny_ordinary_rate: float = 0.0685

    federal_ltcg_plus_niit_rate: float = 0.238  # 20% LTCG + 3.8% NIIT (baseline at ~$400k income)
    ny_cap_gains_rate: float = 0.0685

    # Opportunity cost (taxable brokerage)
    portfolio_return_nominal: float = 0.06
    tax_drag_annual: float = 0.005

    # Special assessment stress
    special_assessment_year2: float = 0.0

    # Conservative guardrails
    tax_benefit_haircut: float = 0.75

    # Retirement
    retirement_P0: float = 1_000_000.0
    retirement_target: float = 3_500_000.0


@dataclass(frozen=True)
class MonthRow:
    month: int
    year: int
    payment: float
    interest: float
    principal: float
    balance: float


def monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    r = annual_rate / 12.0
    if r == 0:
        return principal / term_months
    return principal * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)


def build_amortization(principal: float, annual_rate: float, term_months: int, months: int) -> List[MonthRow]:
    pay = monthly_payment(principal, annual_rate, term_months)
    r = annual_rate / 12.0

    balance = principal
    rows: List[MonthRow] = []
    for m in range(1, months + 1):
        interest = balance * r
        principal_paid = pay - interest
        # Clamp to avoid tiny negative balances due to floating-point drift.
        balance = max(0.0, balance - principal_paid)
        year = (m - 1) // 12 + 1
        rows.append(
            MonthRow(
                month=m,
                year=year,
                payment=pay,
                interest=interest,
                principal=principal_paid,
                balance=balance,
            )
        )
    return rows


def sum_by_year(rows: Iterable[MonthRow]) -> Dict[int, Dict[str, float]]:
    out: Dict[int, Dict[str, float]] = {}
    for r in rows:
        bucket = out.setdefault(r.year, {"payment": 0.0, "interest": 0.0, "principal": 0.0, "ending_balance": 0.0})
        bucket["payment"] += r.payment
        bucket["interest"] += r.interest
        bucket["principal"] += r.principal
        bucket["ending_balance"] = r.balance
    return out


def retirement_years_to_target(P0: float, target: float, annual_return: float, annual_contrib: float = 0.0) -> float:
    """Annual-step simulation with fractional-year interpolation in the terminal year."""
    if P0 <= 0 or target <= 0:
        raise ValueError("P0 and target must be positive")
    if annual_return <= -1.0:
        raise ValueError("annual_return must be > -1")

    if P0 >= target:
        return 0.0

    value = P0
    years = 0
    while years < 200:  # hard safety stop
        start = value
        end = start * (1.0 + annual_return) + annual_contrib
        years += 1
        if end >= target:
            # Linear interpolation within the year between start->end.
            # This is approximate but good enough for decision-grade directionality.
            if end == start:
                return float(years)
            frac = (target - start) / (end - start)
            return (years - 1) + max(0.0, min(1.0, frac))
        value = end

    raise RuntimeError("Retirement simulation did not converge within 200 years")


def write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def fmt_money(x: float) -> str:
    return f"${x:,.0f}"


def load_assumptions(path: Path) -> Assumptions:
    if not path.exists():
        return Assumptions()
    data = json.loads(path.read_text(encoding="utf-8"))
    return Assumptions(**data)


def run_model(a: Assumptions) -> Tuple[Dict[str, float], Dict[str, float], List[MonthRow], List[Dict[str, object]]]:
    # Default behavior: if market value isn't explicitly set, treat it as equal to purchase.
    market_value_at_purchase = a.market_value_at_purchase or a.purchase_price

    down_payment = a.purchase_price * a.down_payment_rate
    loan_amount = a.purchase_price - down_payment

    amort = build_amortization(
        principal=loan_amount,
        annual_rate=a.mortgage_rate_annual,
        term_months=a.mortgage_term_months,
        months=a.hold_years * 12,
    )
    annual = sum_by_year(amort)

    # Upfront costs
    buyer_closing_costs = a.purchase_price * a.buyer_closing_cost_rate
    closing_costs_capitalizable = buyer_closing_costs * a.closing_cost_basis_fraction

    # Recurring costs
    hoa_annual = a.hoa_monthly * 12.0
    utilities_annual = a.utilities_monthly * 12.0

    # Special assessment (stress) applied in Year 2
    special_assessment_by_year = {2: a.special_assessment_year2} if a.special_assessment_year2 else {}

    cashflows: List[Dict[str, object]] = []
    total_mortgage_payments = 0.0
    total_interest = 0.0
    total_principal = 0.0
    total_recurring = 0.0

    for y in range(1, a.hold_years + 1):
        mortgage_payment = annual[y]["payment"]
        interest = annual[y]["interest"]
        principal = annual[y]["principal"]

        hoa = hoa_annual
        prop_tax = a.property_tax_annual
        ins = a.insurance_annual
        maint = a.maintenance_annual
        util = utilities_annual
        assess = float(special_assessment_by_year.get(y, 0.0))

        total_outflow = mortgage_payment + hoa + prop_tax + ins + maint + util + assess

        cashflows.append(
            {
                "year": y,
                "mortgage_payment": round(mortgage_payment, 2),
                "interest": round(interest, 2),
                "principal": round(principal, 2),
                "hoa": round(hoa, 2),
                "property_tax": round(prop_tax, 2),
                "insurance": round(ins, 2),
                "maintenance": round(maint, 2),
                "utilities": round(util, 2),
                "special_assessment": round(assess, 2),
                "total_outflow": round(total_outflow, 2),
                "ending_balance": round(annual[y]["ending_balance"], 2),
            }
        )

        total_mortgage_payments += mortgage_payment
        total_interest += interest
        total_principal += principal
        total_recurring += (hoa + prop_tax + ins + maint + util + assess)

    remaining_balance = amort[-1].balance

    furnishings_salvage = a.furnishings * a.furnishings_salvage_rate

    # Sale
    sale_price = market_value_at_purchase * (1.0 + a.appreciation_rate) ** a.hold_years
    selling_costs = sale_price * a.selling_friction_rate
    amount_realized = sale_price - selling_costs

    adjusted_basis = a.purchase_price + closing_costs_capitalizable  # no improvements assumed
    taxable_gain = amount_realized - adjusted_basis

    total_cap_gains_rate = a.federal_ltcg_plus_niit_rate + a.ny_cap_gains_rate
    cap_gains_tax = max(0.0, taxable_gain) * total_cap_gains_rate

    # Treat furnishings salvage as a separate personal-property recovery at exit.
    # We ignore tax on this salvage by default; include as sensitivity only.
    net_cash_at_close = amount_realized - remaining_balance - cap_gains_tax + furnishings_salvage

    # Tax benefit on mortgage interest (incremental, itemizing assumed)
    total_ordinary_rate = a.federal_ordinary_rate + a.ny_ordinary_rate
    tax_benefit_A = total_interest * total_ordinary_rate
    tax_benefit_B = a.tax_benefit_haircut * tax_benefit_A

    # Opportunity cost (taxable brokerage, after-tax gain)
    lumpsum = down_payment + a.furnishings  # per spec: excludes buyer closing costs
    r_after = max(-0.999, a.portfolio_return_nominal - a.tax_drag_annual)
    ending_value = lumpsum * (1.0 + r_after) ** a.hold_years
    inv_gain = ending_value - lumpsum
    opp_cost_after_tax_gain = max(0.0, inv_gain) * (1.0 - total_cap_gains_rate)

    # Economic net cost reconciliation
    upfront_outflows = down_payment + buyer_closing_costs + a.furnishings

    econ_ex_opp_A = upfront_outflows + total_mortgage_payments + total_recurring - net_cash_at_close - tax_benefit_A
    econ_ex_opp_B = upfront_outflows + total_mortgage_payments + total_recurring - net_cash_at_close - tax_benefit_B

    econ_incl_opp_A = econ_ex_opp_A + opp_cost_after_tax_gain
    econ_incl_opp_B = econ_ex_opp_B + opp_cost_after_tax_gain

    results = {
        "market_value_at_purchase": market_value_at_purchase,
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "buyer_closing_costs": buyer_closing_costs,
        "closing_costs_capitalizable": closing_costs_capitalizable,
        "furnishings": a.furnishings,
        "total_mortgage_payments": total_mortgage_payments,
        "total_interest": total_interest,
        "total_principal": total_principal,
        "total_recurring": total_recurring,
        "sale_price": sale_price,
        "selling_costs": selling_costs,
        "amount_realized": amount_realized,
        "adjusted_basis": adjusted_basis,
        "taxable_gain": taxable_gain,
        "cap_gains_tax": cap_gains_tax,
        "furnishings_salvage": furnishings_salvage,
        "remaining_balance": remaining_balance,
        "net_cash_at_close": net_cash_at_close,
        "tax_benefit_A": tax_benefit_A,
        "tax_benefit_B": tax_benefit_B,
        "opportunity_cost": opp_cost_after_tax_gain,
        "econ_net_cost_ex_opp_A": econ_ex_opp_A,
        "econ_net_cost_ex_opp_B": econ_ex_opp_B,
        "econ_net_cost_incl_opp_A": econ_incl_opp_A,
        "econ_net_cost_incl_opp_B": econ_incl_opp_B,
        "annualized_econ_incl_opp_A": econ_incl_opp_A / a.hold_years,
        "annualized_econ_incl_opp_B": econ_incl_opp_B / a.hold_years,
        "total_cap_gains_rate": total_cap_gains_rate,
        "total_ordinary_rate": total_ordinary_rate,
        "lumpsum": lumpsum,
        "r_after": r_after,
        "ending_value": ending_value,
        "inv_gain": inv_gain,
    }

    # Retirement timing (two return baselines: 6% = forward-looking, 7% = original outline)
    retirement = {}
    for label, r in [("6%", 0.06), ("7%", 0.07)]:
        base = retirement_years_to_target(a.retirement_P0, a.retirement_target, r)
        with_lump = retirement_years_to_target(a.retirement_P0 + lumpsum, a.retirement_target, r)

        # Use the annualized economic net cost INCLUDING opportunity cost as a clean “economic equivalent” contribution.
        # This is not pure cash flow; the report calls this out explicitly.
        contrib_A = results["annualized_econ_incl_opp_A"]
        contrib_B = results["annualized_econ_incl_opp_B"]

        with_contrib_A = retirement_years_to_target(a.retirement_P0, a.retirement_target, r, annual_contrib=contrib_A)
        with_contrib_B = retirement_years_to_target(a.retirement_P0, a.retirement_target, r, annual_contrib=contrib_B)

        with_both_A = retirement_years_to_target(a.retirement_P0 + lumpsum, a.retirement_target, r, annual_contrib=contrib_A)
        with_both_B = retirement_years_to_target(a.retirement_P0 + lumpsum, a.retirement_target, r, annual_contrib=contrib_B)

        retirement[f"retirement_years_baseline_{label}"] = base
        retirement[f"retirement_years_plus_lumpsum_{label}"] = with_lump
        retirement[f"retirement_years_annual_contrib_A_{label}"] = with_contrib_A
        retirement[f"retirement_years_annual_contrib_B_{label}"] = with_contrib_B
        retirement[f"retirement_years_both_A_{label}"] = with_both_A
        retirement[f"retirement_years_both_B_{label}"] = with_both_B

    return results, retirement, amort, cashflows


def sensitivity_cases(a: Assumptions) -> List[Tuple[str, Assumptions]]:
    cases: List[Tuple[str, Assumptions]] = []

    def add(name: str, **kwargs: float) -> None:
        cases.append((name, Assumptions(**{**asdict(a), **kwargs})))

    # Appreciation
    for ar in [0.00, 0.02, 0.04, 0.06]:
        add(f"appreciation_{int(ar*100)}pct", appreciation_rate=ar)

    # Interest rate
    for mr in [0.055, 0.065, 0.075]:
        add(f"mortgage_rate_{mr*100:.1f}pct", mortgage_rate_annual=mr)

    # Selling friction
    for sf in [0.06, 0.07, 0.08]:
        add(f"sell_friction_{int(sf*100)}pct", selling_friction_rate=sf)

    # Buyer closing costs
    for cc in [0.01, 0.02, 0.04]:
        add(f"buyer_closing_{int(cc*100)}pct", buyer_closing_cost_rate=cc)

    # HOA assessment stress
    add("assessment_stress_5000_y2", special_assessment_year2=5_000.0)

    # Furnishings salvage sensitivity
    add("furnishings_salvage_25pct", furnishings_salvage_rate=0.25)

    # Maintenance
    add("maintenance_2000", maintenance_annual=2_000.0)

    # Cap gains scenarios (federal component only; NY is modeled separately)
    # 15% LTCG
    add("fed_capgains_15pct", federal_ltcg_plus_niit_rate=0.15)
    # 15% + 3.8% NIIT
    add("fed_capgains_18_8pct", federal_ltcg_plus_niit_rate=0.188)
    # 20% + 3.8% NIIT
    add("fed_capgains_23_8pct", federal_ltcg_plus_niit_rate=0.238)

    # Portfolio return
    for pr in [0.045, 0.06, 0.075]:
        add(f"portfolio_return_{pr*100:.1f}pct", portfolio_return_nominal=pr)

    return cases


def build_report_md(
    a: Assumptions,
    results: Dict[str, float],
    retirement: Dict[str, float],
    sensitivity_summary: Dict[str, object],
) -> str:
    annual_A = results["annualized_econ_incl_opp_A"]
    annual_B = results["annualized_econ_incl_opp_B"]

    lines: List[str] = []
    lines.append("# Condo Net Cost Report (4-year hold)")
    lines.append("")
    lines.append(f"Run: `{RUN_ID}`")
    lines.append("")

    lines.append("## Baseline assumptions (key)")
    if results["market_value_at_purchase"] != a.purchase_price:
        lines.append(f"- Market value at purchase (used for appreciation): {fmt_money(results['market_value_at_purchase'])}")
        lines.append(f"- Purchase price paid (basis/cash-to-close): {fmt_money(a.purchase_price)}")
    else:
        lines.append(f"- Purchase price: {fmt_money(a.purchase_price)}")
    lines.append(f"- Down payment: {a.down_payment_rate:.0%} ({fmt_money(results['down_payment'])})")
    lines.append(f"- Mortgage rate: {a.mortgage_rate_annual*100:.2f}%, 30-year fixed, no points, no PMI")
    lines.append(f"- Hold period: {a.hold_years} years")
    lines.append(f"- Appreciation: {a.appreciation_rate*100:.1f}%")
    lines.append(f"- Selling friction: {a.selling_friction_rate*100:.1f}%")
    lines.append(f"- Buyer closing costs + prepaids: {a.buyer_closing_cost_rate*100:.1f}% of price ({fmt_money(results['buyer_closing_costs'])})")
    lines.append(f"- Furnishings: {fmt_money(a.furnishings)}")
    if a.furnishings_salvage_rate:
        lines.append(f"- Furnishings salvage (sensitivity): {a.furnishings_salvage_rate:.0%} ({fmt_money(results['furnishings_salvage'])} recovered at exit; tax ignored)")
    lines.append(f"- HOA: {fmt_money(a.hoa_monthly)}/mo, Property tax: {fmt_money(a.property_tax_annual)}/yr, Insurance: {fmt_money(a.insurance_annual)}/yr")
    lines.append(f"- Utilities (not in HOA): {fmt_money(a.utilities_monthly)}/mo")
    lines.append(f"- Tax: Federal ordinary {a.federal_ordinary_rate:.0%} + NY ordinary {a.ny_ordinary_rate:.2%} = {results['total_ordinary_rate']:.2%}")
    lines.append(
        f"- Cap gains (sale + taxable brokerage liquidation): (Fed LTCG+NIIT {a.federal_ltcg_plus_niit_rate:.1%} + NY {a.ny_cap_gains_rate:.2%}) = {results['total_cap_gains_rate']:.2%}"
    )
    lines.append("")

    lines.append("## Core 4-year results")
    lines.append(f"- Total mortgage payments (48 mo): {fmt_money(results['total_mortgage_payments'])}")
    lines.append(f"- Total interest paid: {fmt_money(results['total_interest'])}")
    lines.append(f"- Total principal paid: {fmt_money(results['total_principal'])}")
    lines.append(f"- Total recurring (HOA/tax/ins/maint/util/assess): {fmt_money(results['total_recurring'])}")
    lines.append("")

    lines.append("### Sale math (end of Year 4)")
    lines.append(f"- Sale price: {fmt_money(results['sale_price'])}")
    lines.append(f"- Selling costs: {fmt_money(results['selling_costs'])}")
    lines.append(f"- Amount realized: {fmt_money(results['amount_realized'])}")
    lines.append(f"- Adjusted basis (incl. capitalizable closing costs): {fmt_money(results['adjusted_basis'])}")
    lines.append(f"- Taxable gain: {fmt_money(results['taxable_gain'])}")
    lines.append(f"- Cap gains tax: {fmt_money(results['cap_gains_tax'])}")
    lines.append(f"- Remaining mortgage balance: {fmt_money(results['remaining_balance'])}")
    lines.append(f"- Net cash at close: {fmt_money(results['net_cash_at_close'])}")
    lines.append("")

    lines.append("### Tax benefit + opportunity cost")
    lines.append(f"- Mortgage-interest tax benefit (A baseline): {fmt_money(results['tax_benefit_A'])}")
    lines.append(f"- Mortgage-interest tax benefit (B haircut 25%): {fmt_money(results['tax_benefit_B'])}")
    lines.append(f"- Opportunity cost (foregone after-tax gain in taxable brokerage): {fmt_money(results['opportunity_cost'])}")
    lines.append("")

    lines.append("## Economic net cost")
    lines.append(
        f"- Annualized economic net cost (A baseline): {fmt_money(annual_A)}/yr (4-year total {fmt_money(results['econ_net_cost_incl_opp_A'])})"
    )
    lines.append(
        f"- Annualized economic net cost (B conservative): {fmt_money(annual_B)}/yr (4-year total {fmt_money(results['econ_net_cost_incl_opp_B'])})"
    )
    lines.append("")

    lines.append("## Retirement timing extension")
    lines.append(
        "Note: The ‘annual contribution’ scenarios treat the annualized economic net cost as an ‘economic equivalent’ contribution. "
        "This is not pure cash flow (because sale proceeds occur at the end of the hold), but it matches the outline’s requested framing."
    )
    lines.append("")

    def rblock(label: str) -> None:
        base = retirement[f"retirement_years_baseline_{label}"]
        plus_lump = retirement[f"retirement_years_plus_lumpsum_{label}"]
        ann_A = retirement[f"retirement_years_annual_contrib_A_{label}"]
        ann_B = retirement[f"retirement_years_annual_contrib_B_{label}"]
        both_A = retirement[f"retirement_years_both_A_{label}"]
        both_B = retirement[f"retirement_years_both_B_{label}"]

        lines.append(f"### Using {label} annual return")
        lines.append(f"- Baseline years to {fmt_money(a.retirement_target)}: {base:.2f}")
        lines.append(f"- + Invest LumpSum now ({fmt_money(results['lumpsum'])}): {plus_lump:.2f} (Δ {base - plus_lump:+.2f} yrs)")
        lines.append(f"- + Invest annual net cost (A): {ann_A:.2f} (Δ {base - ann_A:+.2f} yrs)")
        lines.append(f"- + Invest annual net cost (B): {ann_B:.2f} (Δ {base - ann_B:+.2f} yrs)")
        lines.append(f"- + Both (A): {both_A:.2f} (Δ {base - both_A:+.2f} yrs)")
        lines.append(f"- + Both (B): {both_B:.2f} (Δ {base - both_B:+.2f} yrs)")
        lines.append("")

    rblock("6%")
    rblock("7%")

    lines.append("## Files generated")
    lines.append(f"- `exports/amortization_48mo.csv`")
    lines.append(f"- `exports/annual_cashflows.csv`")
    lines.append(f"- `exports/sensitivity_table.csv`")
    lines.append(f"- `exports/condo_net_cost_report.md`")

    lines.append("")
    lines.append("## How to rerun with negotiated terms")
    lines.append(f"- Edit: `inputs/model_inputs.json` (recommended for most changes)")
    lines.append("- Or override a few key negotiated items on the CLI:")
    lines.append(
        "  - `python runs/2026-01-17__second-home-condo-net-cost/scripts/condo_net_cost_model.py --price 290000 --mortgage-rate 0.06 --buyer-closing 0.02`"
    )
    lines.append("  - Supported overrides: `--price`, `--mortgage-rate`, `--buyer-closing`, `--selling-friction`, `--appreciation`")

    lines.append("")
    lines.append("## Sensitivity highlights (annualized net cost)")
    lines.append(
        f"- Min/Max across built-in scenarios (A): {fmt_money(float(sensitivity_summary['min_A']))}/yr to {fmt_money(float(sensitivity_summary['max_A']))}/yr"
    )
    lines.append(
        f"- Min/Max across built-in scenarios (B): {fmt_money(float(sensitivity_summary['min_B']))}/yr to {fmt_money(float(sensitivity_summary['max_B']))}/yr"
    )
    lines.append("- Top drivers in this setup:")
    for line in sensitivity_summary["driver_lines"]:  # type: ignore[index]
        lines.append(f"  - {line}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Second-home condo net cost model")
    parser.add_argument(
        "--inputs",
        type=Path,
        default=DEFAULT_INPUTS_PATH,
        help="Path to model_inputs.json (defaults to run-local inputs/model_inputs.json)",
    )

    # Keep overrides to the handful of negotiated items that may change.
    parser.add_argument("--price", type=float, default=None)
    parser.add_argument(
        "--market-value",
        type=float,
        default=None,
        help="Market value at purchase used for appreciation/sale price (defaults to purchase price)",
    )
    parser.add_argument("--mortgage-rate", type=float, default=None)
    parser.add_argument("--buyer-closing", type=float, default=None)
    parser.add_argument("--selling-friction", type=float, default=None)
    parser.add_argument("--appreciation", type=float, default=None)
    args = parser.parse_args()

    a = load_assumptions(args.inputs)
    overrides = {}
    if args.price is not None:
        overrides["purchase_price"] = args.price
    if args.market_value is not None:
        overrides["market_value_at_purchase"] = args.market_value
    if args.mortgage_rate is not None:
        overrides["mortgage_rate_annual"] = args.mortgage_rate
    if args.buyer_closing is not None:
        overrides["buyer_closing_cost_rate"] = args.buyer_closing
    if args.selling_friction is not None:
        overrides["selling_friction_rate"] = args.selling_friction
    if args.appreciation is not None:
        overrides["appreciation_rate"] = args.appreciation
    if overrides:
        a = Assumptions(**{**asdict(a), **overrides})

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results, retirement, amort, cashflows = run_model(a)

    # Write amortization CSV
    amort_rows = [
        {
            "month": r.month,
            "year": r.year,
            "payment": round(r.payment, 2),
            "interest": round(r.interest, 2),
            "principal": round(r.principal, 2),
            "balance": round(r.balance, 2),
        }
        for r in amort
    ]
    write_csv(
        EXPORTS_DIR / "amortization_48mo.csv",
        ["month", "year", "payment", "interest", "principal", "balance"],
        amort_rows,
    )

    # Write annual cashflows CSV
    write_csv(
        EXPORTS_DIR / "annual_cashflows.csv",
        [
            "year",
            "mortgage_payment",
            "interest",
            "principal",
            "hoa",
            "property_tax",
            "insurance",
            "maintenance",
            "utilities",
            "special_assessment",
            "total_outflow",
            "ending_balance",
        ],
        cashflows,
    )

    # Sensitivity table
    sens_rows: List[Dict[str, object]] = []
    for name, a_case in sensitivity_cases(a):
        res_case, _, _, _ = run_model(a_case)
        sens_rows.append(
            {
                "scenario": name,
                "annual_net_cost_A": round(res_case["annualized_econ_incl_opp_A"], 2),
                "annual_net_cost_B": round(res_case["annualized_econ_incl_opp_B"], 2),
                "total_net_cost_A": round(res_case["econ_net_cost_incl_opp_A"], 2),
                "total_net_cost_B": round(res_case["econ_net_cost_incl_opp_B"], 2),
            }
        )

    write_csv(
        EXPORTS_DIR / "sensitivity_table.csv",
        ["scenario", "annual_net_cost_A", "annual_net_cost_B", "total_net_cost_A", "total_net_cost_B"],
        sens_rows,
    )

    # Build a short sensitivity summary for the report.
    annual_As = [float(r["annual_net_cost_A"]) for r in sens_rows]
    annual_Bs = [float(r["annual_net_cost_B"]) for r in sens_rows]
    sensitivity_summary = {
        "min_A": min(annual_As) if annual_As else results["annualized_econ_incl_opp_A"],
        "max_A": max(annual_As) if annual_As else results["annualized_econ_incl_opp_A"],
        "min_B": min(annual_Bs) if annual_Bs else results["annualized_econ_incl_opp_B"],
        "max_B": max(annual_Bs) if annual_Bs else results["annualized_econ_incl_opp_B"],
        "driver_lines": [
            f"Appreciation 0%→6%: {fmt_money(annual_As[0])}/yr to {fmt_money(annual_As[3])}/yr (A)",
            f"Mortgage rate 5.5%→7.5%: {fmt_money(annual_As[4])}/yr to {fmt_money(annual_As[6])}/yr (A)",
            f"Selling friction 6%→8%: {fmt_money(annual_As[7])}/yr to {fmt_money(annual_As[9])}/yr (A)",
        ],
    }

    # Report
    report_md = build_report_md(a, results, retirement, sensitivity_summary)
    (EXPORTS_DIR / "condo_net_cost_report.md").write_text(report_md, encoding="utf-8")

    # Lightweight console summary
    print("Baseline annualized net cost (A):", fmt_money(results["annualized_econ_incl_opp_A"]))
    print("Baseline annualized net cost (B):", fmt_money(results["annualized_econ_incl_opp_B"]))
    print("Wrote outputs to:", str(EXPORTS_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
