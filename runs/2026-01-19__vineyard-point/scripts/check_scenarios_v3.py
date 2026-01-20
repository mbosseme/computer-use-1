import pandas as pd

# Load the full results
df = pd.read_csv('runs/2026-01-19__vineyard-point/exports/scenario_results.csv')

# --- DEFINITIONS ---

def get_scenario(rent, occ, interest, furnish, mgmt_pct, lease_fee):
    # Filter with tolerance because floating point matching can be tricky, though these inputs should be exact
    subset = df[
        (df['monthly_rent'] == rent) &
        (df['fill_rate'] == occ) &
        (df['interest_rate'] == interest) &
        (df['furnish_budget'] == furnish) &
        (df['management_fee_pct_of_rent'] == mgmt_pct) &
        (df['leasing_fee_per_lease'] == lease_fee)
    ]
    if subset.empty:
        # Fallback for close matches if exact combo missing
        print(f"WARNING: No exact match for Rent={rent}, Mgmt={mgmt_pct}, Lease=${lease_fee}. Picking closest...")
        subset = df[
            (df['monthly_rent'] == rent) &
            (df['management_fee_pct_of_rent'] == mgmt_pct)
        ]
        
    return subset.sort_values('avg_annual_cost', ascending=True).iloc[0]

# BEST CASE:
# - High Rent ($3100), High Occupancy (90%), Low Interest (6%)
# - Costs: $10k Furnish, 15% Mgmt (Best available MTR rate), $150 Leasing
best_case = get_scenario(3100, 0.9, 0.06, 10000, 0.15, 150)

# MODERATE CASE:
# - Median Rent ($2800), Median Occupancy (75%), Median Interest (7%)
# - Costs: $20k Furnish, 18% Mgmt (Typical MTR), $250 Leasing
moderate_case = get_scenario(2800, 0.75, 0.07, 20000, 0.18, 250)

# STRESS CASE:
# - Low Rent ($2400), Low Occupancy (60%), High Interest (8%)
# - Costs: $30k Furnish, 25% Mgmt (High operational friction), $500 Leasing
stress_case = get_scenario(2400, 0.60, 0.08, 30000, 0.25, 500)

# --- REPORTING ---

def print_case(label, row):
    print(f"\n[{label} CASE]")
    print(f"Invested Upfront: ${row['upfront_cash_required']:,.0f} (Furnish: ${row['furnish_budget']:,.0f})")
    print(f"Revenue: ${row['monthly_rent']:,.0f}/mo @ {row['fill_rate']*100:.0f}% occ = ${row['gross_rent']:,.0f}/yr")
    print(f"Fees: Mgmt {row['management_fee_pct_of_rent']*100:.1f}% + Leasing ${row['leasing_fee_per_lease']:.0f}/lease")
    print(f"Net Annual Cost (Wealth Drag): ${row['avg_annual_cost']:,.0f}/yr")
    print(f"Avg Monthly Cost: ${row['avg_annual_cost']/12:,.0f}/mo")

print_case("BEST", best_case)
print_case("MODERATE", moderate_case)
print_case("STRESS", stress_case)
