from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import product
from pathlib import Path

def format_money(value: float) -> str:
    if value < 0:
        return f"-${abs(value):,.0f}"
    return f"${value:,.0f}"

def annual_mortgage(principal: float, rate: float, years: int) -> float:
    if principal <= 0: return 0.0
    if rate == 0: return principal / years
    r = rate / 12
    n = years * 12
    pmt = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return pmt * 12

def remaining_balance(principal: float, rate: float, years: int, months_paid: int) -> float:
    if principal <= 0: return 0.0
    r = rate / 12
    n = years * 12
    if r == 0: return max(0.0, principal * (1 - months_paid / n))
    pmt = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    k = months_paid
    return principal * (1 + r) ** k - pmt * (((1 + r) ** k - 1) / r)

def compute_v7_model(inputs: dict, scenario_overrides: dict) -> dict:
    # ---------------------------------------------------------
    # 1. SETUP & INPUTS
    # ---------------------------------------------------------
    p = inputs["property"]["purchase"]
    f = inputs["financing"]
    r = inputs["recurring_costs"]
    rental = inputs["rental"]
    tax_in = inputs["tax"]
    
    # Overrides
    owner_weeks_key = scenario_overrides.get("owner_weeks_key", "4_weeks")
    fill_rate = scenario_overrides.get("fill_rate", 0.70)
    appreciation_rate = scenario_overrides.get("appreciation_rate", 0.03)
    hoa_monthly = scenario_overrides.get("hoa_monthly", 297.0)
    
    # Map weeks key to integet
    weeks_map = {"2_weeks": 2, "4_weeks": 4, "6_weeks": 6, "8_weeks": 8}
    owner_weeks = weeks_map[owner_weeks_key]
    
    # ---------------------------------------------------------
    # 2. OCCUPANCY BRIDGE
    # ---------------------------------------------------------
    days_total = 365
    days_owner = owner_weeks * 7
    days_buffer = 0  # Per requirements: explicit number, 0 unless justified
    days_rentable = days_total - days_owner - days_buffer
    days_occupied = days_rentable * fill_rate
    months_occupied = days_occupied / 30.4
    
    # ---------------------------------------------------------
    # 3. REVENUE
    # ---------------------------------------------------------
    monthly_rent = rental["monthly_rent_options"][1] 
    gross_rent_annual = months_occupied * monthly_rent
    
    # ---------------------------------------------------------
    # 4. EXPENSE STACK (FIXED vs VARIABLE)
    # ---------------------------------------------------------
    # Fixed
    purchase_price = p["purchase_price"]
    furnish_budget = 16000.0 # Base assumption
    down_pct = 0.20
    loan_amount = purchase_price * (1 - down_pct)
    rate = 0.07
    term = 30
    
    mortgage_annual = annual_mortgage(loan_amount, rate, term)
    property_tax = r["property_tax_annual"]
    insurance = r["insurance_annual"]
    hoa_annual = hoa_monthly * 12
    utils_fixed_annual = r["utilities_fixed_monthly"] * 12
    maint_fixed_annual = r["maintenance_fixed_annual"]
    
    fixed_expenses = mortgage_annual + property_tax + insurance + hoa_annual + utils_fixed_annual + maint_fixed_annual
    
    # Variable
    # Turnovers assumption: MTR logic. Avg stay = 60 days.
    # turnovers = occupied_days / 60
    if days_occupied > 0:
        turnovers = days_occupied / 60.0
    else:
        turnovers = 0.0
        
    mgmt_fee = gross_rent_annual * 0.20 # 20% mgmt fee
    leasing_fees = turnovers * rental["leasing_fee_per_lease"]
    cleaning_fees = turnovers * rental["cleaning_cost_per_turnover"]
    supplies_fees = turnovers * rental["turnover_supplies_cost"]
    
    utils_variable = months_occupied * r["utilities_variable_monthly_occupied"]
    maint_variable = months_occupied * r["maintenance_variable_monthly_occupied"]
    
    variable_expenses = mgmt_fee + leasing_fees + cleaning_fees + supplies_fees + utils_variable + maint_variable
    
    total_cash_outflow = fixed_expenses + variable_expenses
    net_cash_flow = gross_rent_annual - total_cash_outflow
    
    # Empty Scenario (Fixed costs only, no revenue)
    # Note: Variable utilities might be near zero if truly empty, but base utilities are fixed.
    cash_flow_empty = 0.0 - fixed_expenses
    
    # ---------------------------------------------------------
    # 5. TAX BRIDGE (STRICT V7)
    # ---------------------------------------------------------
    horizon_years = 7
    
    # Cumulative Operating Position (for PAL tracking)
    # Taxable Income = Gross Rent - (Operating Expenses + Mortgage Interest + Depreciation)
    # We need average annual interest
    total_interest_paid = 0.0
    bal = loan_amount
    monthly_rate = rate / 12
    monthly_pmt = mortgage_annual / 12
    
    for _ in range(horizon_years * 12):
        inte = bal * monthly_rate
        total_interest_paid += inte
        bal -= (monthly_pmt - inte)
        
    avg_annual_interest = total_interest_paid / horizon_years
    avg_annual_principal = (mortgage_annual * horizon_years - total_interest_paid) / horizon_years
    
    # Depreciation
    bldg_val = purchase_price * (1 - 0.25) # 25% Land
    dep_bldg_annual = bldg_val / 27.5
    dep_furn_annual = furnish_budget / 5.0
    total_dep_annual = dep_bldg_annual + dep_furn_annual
    
    # Taxable P&L (Annual)
    # Deductible Cash Expenses = Total Outflow - Mortgage (Principal+Interest) + Interest
    deductible_cash_expenses = total_cash_outflow - mortgage_annual + avg_annual_interest
    taxable_income_annual = gross_rent_annual - deductible_cash_expenses - total_dep_annual
    
    # Suspended PAL accumulation
    # If taxable_income < 0, it adds to PAL. If > 0, it uses PAL (if allowed, but strict rule says NO W-2 OFFSET).
    # Since we are likely negative every year:
    annual_pal = max(0.0, -taxable_income_annual)
    total_suspended_pal = annual_pal * horizon_years
    
    # SALE EVENT
    future_value = purchase_price * ((1 + appreciation_rate) ** horizon_years)
    sale_costs = future_value * 0.07
    
    # Basis
    total_dep_taken = total_dep_annual * horizon_years
    # Note: Furnishings fully depreciated in 5 years? Simple model assumes annual. 
    # Let's cap furnishing depreciation at 5 years.
    dep_furn_total = min(furnish_budget, dep_furn_annual * horizon_years)
    dep_bldg_total = dep_bldg_annual * horizon_years
    total_dep_actual = dep_furn_total + dep_bldg_total
    
    adjusted_basis = (purchase_price + purchase_price*0.025 + furnish_budget) - total_dep_actual
    # Note: Basis includes closing costs (2.5%) and furnishing.
    
    gain_on_sale = (future_value - sale_costs) - adjusted_basis
    
    # Tax Capture Strict Rule: 
    # "Apply suspended PALs ONLY up to the taxable gain on the property sale"
    # "Any remaining PAL ... modeled as $0"
    
    # Gain Components
    recapture_gain = min(gain_on_sale, total_dep_actual)
    ltcg_gain = max(0.0, gain_on_sale - recapture_gain)
    
    # Apply PAL
    # Order: Offset Recapture first (highest tax), then LTCG.
    pal_used = min(total_suspended_pal, gain_on_sale)
    
    remaining_recapture = max(0.0, recapture_gain - pal_used)
    remaining_pal_after_recap = max(0.0, pal_used - recapture_gain)
    remaining_ltcg = max(0.0, ltcg_gain - remaining_pal_after_recap)
    
    tax_due_sale = (remaining_recapture * 0.25) + (remaining_ltcg * 0.20)
    
    net_sale_proceeds = (future_value - sale_costs) - bal - tax_due_sale
    
    # ---------------------------------------------------------
    # 6. DECISION METRICS
    # ---------------------------------------------------------
    
    # Rent Alternative
    rent_alternative_cost = owner_weeks * 2500.0
    
    # Cost of Ownership (Annualized Econ Cost)
    # Inflow: Net Cash Flow * 7 + Net Sale Proceeds
    # Outflow: Upfront Cash
    upfront_cash = (purchase_price * down_pct) + (purchase_price * 0.025) + furnish_budget
    
    total_lifetime_cash_net = (net_cash_flow * horizon_years) - upfront_cash + net_sale_proceeds
    
    # Convert to annual cost equivalent
    # Simplest: (Total Net Cash / Years) adjusted for sign
    # A positive number here means we MADE money. A negative means we LOST money.
    avg_annual_net_gain = total_lifetime_cash_net / horizon_years
    
    # Econ Cost = -Avg Annual Net Gain + Opportunity Cost?
    # No, let's use the explicit gap.
    # Econ Cost to Own = (Upfront * OppCostRate) - AvgAnnualNetGain ?? 
    # Better: Econ Cost = Rent Alt - (Diff). 
    # Let's use standard IRR or simple "Annualized Cost".
    # User asks for "Annual economic premium vs rent".
    # Annual Cost of Owning = -(Avg Annual Net Gain). 
    # WAIT. Opportunity cost is real.
    # Input V6 used opp_cost_annual.
    opp_cost_annual = upfront_cash * 0.05
    # Adjusted Net Gain = Avg Annual Net Gain - Opp Cost
    # Cost To Own = -(Adjusted Net Gain)
    
    adjusted_annual_net_gain = avg_annual_net_gain - opp_cost_annual
    cost_to_own_annual = -adjusted_annual_net_gain
    
    premium_to_own = cost_to_own_annual - rent_alternative_cost
    
    # Verdict
    if premium_to_own < -1000: verdict = "Strong Buy"
    elif premium_to_own < 2000: verdict = "Acceptable"
    elif premium_to_own < 5000: verdict = "Expensive"
    else: verdict = "Avoid"

    return {
        "owner_weeks": owner_weeks,
        "hoa_monthly": hoa_monthly,
        "fill_rate": fill_rate,
        "appreciation": appreciation_rate,
        
        "days_rentable": days_rentable,
        "days_occupied": days_occupied,
        "gross_rent": gross_rent_annual,
        
        "fixed_expenses": fixed_expenses,
        "variable_expenses": variable_expenses,
        "net_cash_flow": net_cash_flow, 
        "cash_flow_empty": cash_flow_empty,
        "incremental_cash_benefit": net_cash_flow - cash_flow_empty,
        
        "rent_alternative": rent_alternative_cost,
        "cost_to_own": cost_to_own_annual,
        "premium": premium_to_own,
        "verdict": verdict,
        
        # Tax details
        "sale_price": future_value,
        "adjusted_basis": adjusted_basis, 
        "gain_on_sale": gain_on_sale,
        "recapture_amt": recapture_gain,
        "ltcg_amt": ltcg_gain,
        "total_pal": total_suspended_pal,
        "pal_used": pal_used,
        "tax_due": tax_due_sale,
        "net_proceeds": net_sale_proceeds
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=Path("runs/2026-01-19__vineyard-point/inputs/model_inputs.json"))
    parser.add_argument("--out_md", type=Path, default=Path("runs/2026-01-19__vineyard-point/exports/v7_memo_content.md"))
    args = parser.parse_args()
    
    with open(args.inputs) as f:
        inputs = json.load(f)
        
    md = []
    
    # ------------------------------------------------------------------
    # TABLE 1: Base Case (HOA 297, Occ 70%, Appr 3%) for 2/4/6/8 Weeks
    # ------------------------------------------------------------------
    md.append("## Decision 1: Buy vs Rent Vacations\n")
    md.append("**Base Assumptions:** HOA $297, Occ 70%, Appr 3%, 7y Hold.\n\n")
    md.append("| Owner Weeks | Rent Alt ($/yr) | Cost to Own ($/yr) | Premium ($/yr) | Verdict |\n")
    md.append("| :--- | :--- | :--- | :--- | :--- |\n")
    
    weeks_list = ["2_weeks", "4_weeks", "6_weeks", "8_weeks"]
    base_results = {}
    
    for w in weeks_list:
        res = compute_v7_model(inputs, {
            "owner_weeks_key": w,
            "hoa_monthly": 297.0,
            "fill_rate": 0.70,
            "appreciation_rate": 0.03
        })
        base_results[w] = res
        md.append(f"| {res['owner_weeks']} | {format_money(res['rent_alternative'])} | {format_money(res['cost_to_own'])} | **{format_money(res['premium'])}** | {res['verdict']} |\n")
        
    # ------------------------------------------------------------------
    # TABLE 2: Rent vs Empty (Base Case - 4 Weeks)
    # ------------------------------------------------------------------
    r4 = base_results["4_weeks"]
    md.append("\n## Decision 2: Operational Strategy (Rent vs Empty)\n")
    md.append("Scenario: 4 Weeks Owner Use.\n\n")
    md.append("| Metric | Buy & Rent Out | Buy & Keep Empty | Incremental Benefit |\n")
    md.append("| :--- | :--- | :--- | :--- |\n")
    
    # We need to compute empty specifically or just use the cache
    # The function returns "cash_flow_empty"
    
    md.append(f"| Annual Cash Flow | {format_money(r4['net_cash_flow'])} | {format_money(r4['cash_flow_empty'])} | **{format_money(r4['incremental_cash_benefit'])}** |\n")
    
    md.append(f"\n*Analysis: Renting reduces annual cash bleed by {format_money(r4['incremental_cash_benefit'])}.*")
    
    # ------------------------------------------------------------------
    # SENSITIVITY: HOA
    # ------------------------------------------------------------------
    md.append("\n\n## Sensitivity: HOA Impact on Premium (4 Weeks Use)\n")
    md.append("| HOA Monthly | Cost to Own | Premium vs Rent ($10k) |\n")
    md.append("| :--- | :--- | :--- |\n")
    for hoa in [297.0, 400.0, 550.0]:
        s = compute_v7_model(inputs, {"owner_weeks_key": "4_weeks", "hoa_monthly": hoa})
        md.append(f"| ${hoa:.0f} | {format_money(s['cost_to_own'])} | {format_money(s['premium'])} |\n")
        
    # ------------------------------------------------------------------
    # SENSITIVITY: SWING DRIVERS
    # ------------------------------------------------------------------
    md.append("\n## Sensitivity: Swing Drivers (Impact on Premium)\n")
    # Note: Baseline is now $297 HOA
    base_prem = base_results["4_weeks"]['premium']
    verdict = base_results["4_weeks"]['verdict']
    md.append(f"Baseline Premium (4 Wks, $297 HOA): **{format_money(base_prem)}** ({verdict})\n\n")
    
    # driver 1: HOA
    s_hoa_low = compute_v7_model(inputs, {"owner_weeks_key": "4_weeks", "hoa_monthly": 297.0}) # Now base
    s_hoa_high = compute_v7_model(inputs, {"owner_weeks_key": "4_weeks", "hoa_monthly": 550.0}) # Stress
    delta_hoa = s_hoa_high['premium'] - s_hoa_low['premium']
    
    # driver 2: Occupancy
    # Use base HOA 297 for these
    s_occ_low = compute_v7_model(inputs, {"owner_weeks_key": "4_weeks", "fill_rate": 0.60, "hoa_monthly": 297.0})
    s_occ_high = compute_v7_model(inputs, {"owner_weeks_key": "4_weeks", "fill_rate": 0.75, "hoa_monthly": 297.0})
    delta_occ = s_occ_low['premium'] - s_occ_high['premium'] 
    
    # driver 3: Appreciation
    s_app_low = compute_v7_model(inputs, {"owner_weeks_key": "4_weeks", "appreciation_rate": 0.01, "hoa_monthly": 297.0})
    s_app_high = compute_v7_model(inputs, {"owner_weeks_key": "4_weeks", "appreciation_rate": 0.05, "hoa_monthly": 297.0})
    delta_app = s_app_low['premium'] - s_app_high['premium']
    
    md.append(f"1. **Appreciation (1% -> 5%)**: Swing of {format_money(delta_app)} (Premium {format_money(s_app_low['premium'])} -> {format_money(s_app_high['premium'])})\n")
    md.append(f"2. **Occupancy (60% -> 75%)**: Swing of {format_money(delta_occ)} (Premium {format_money(s_occ_low['premium'])} -> {format_money(s_occ_high['premium'])})\n")
    md.append(f"3. **HOA ($297 -> $550)**: Swing of {format_money(delta_hoa)} (Premium {format_money(s_hoa_low['premium'])} -> {format_money(s_hoa_high['premium'])})\n")

    # ------------------------------------------------------------------
    # APPENDICES
    # ------------------------------------------------------------------
    md.append("\n\n# Appendix\n")
    
    # A) Occupancy Bridge
    md.append("### A. Occupancy Reconciliation (Base Case)\n")
    md.append("| Scenario | Total | Owner | Buffer | Rentable | Occupied (70%) | Month Eq |\n")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for w in weeks_list:
        res = base_results[w]
        md.append(f"| {res['owner_weeks']} Weeks | 365 | {res['owner_weeks']*7} | 0 | {res['days_rentable']} | {res['days_occupied']:.1f} | {res['days_occupied']/30.4:.1f} |\n")
        
    # B) Cost Stack
    md.append("\n### B. Operating Cost Stack (4 Weeks Use)\n")
    r = base_results["4_weeks"]
    md.append(f"* **Fixed Costs ({format_money(r['fixed_expenses'])}):** Mortgage, Tax, Ins, HOA ($297), Maint ($1k), Utils ($1.8k)\n")
    md.append(f"* **Variable Costs ({format_money(r['variable_expenses'])}):** Mgmt (20%), Cleaning/Leasing (Est 4-5 turns/yr), Variable Utils/Maint.\n")
    
    # C) Sale Tax Bridge
    md.append("\n### C. Sale Year Tax Bridge (Strict V7 Rule)\n")
    md.append("Assumption: 3% Aprrec, 7y Hold. **Suspended losses ONLY offset sale gain.**\n\n")
    
    md.append("| Line Item | Value | Notes |\n")
    md.append("| :--- | :--- | :--- |\n")
    md.append(f"| Sale Price | {format_money(r['sale_price'])} | |\n")
    md.append(f"| Adjusted Basis | {format_money(r['adjusted_basis'])} | (Price + Closing + Furnish - Deprec) |\n")
    md.append(f"| **Taxable Gain** | **{format_money(r['gain_on_sale'])}** | Sale - Costs - Basis |\n")
    md.append(f"| Recapture Portion | {format_money(r['recapture_amt'])} | Taxed @ 25% max |\n")
    md.append(f"| LTCG Portion | {format_money(r['ltcg_amt'])} | Taxed @ 20% |\n")
    md.append(f"| Suspended PAL Available | {format_money(r['total_pal'])} | Total accumulated |\n")
    md.append(f"| PAL Applied | {format_money(r['pal_used'])} | **Capped at Gain Amount** |\n")
    md.append(f"| **Tax Due** | **{format_money(r['tax_due'])}** | After PAL offset |\n")
    md.append(f"| Net Proceeds | {format_money(r['net_proceeds'])} | |\n")
    
    md.append(f"\n*Confirmation: Rent Alternative = Weeks * $2,500 checked.*")
    
    args.out_md.write_text("".join(md))
    print("V7 Content Generated.")

if __name__ == "__main__":
    main()
