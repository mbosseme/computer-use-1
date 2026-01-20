import pandas as pd

# Load
df = pd.read_csv('runs/2026-01-19__vineyard-point/exports/scenario_results.csv')

def analyze(label, rent, occ, interest, furnish, mgmt, lease_fee, owner_scenario='three_trips_feb_aug_dec', down_pct=0.20):
    # Filter for exact scenario
    # Note: Using down_pct=0.20 to align with "Over 100k" cash target
    subset = df[
        (df['monthly_rent'] == rent) &
        (df['fill_rate'] == occ) &
        (df['interest_rate'] == interest) &
        (df['furnish_budget'] == furnish) &
        (df['management_fee_pct_of_rent'] == mgmt) &
        (df['leasing_fee_per_lease'] == lease_fee) &
        (df['owner_use_scenario'] == owner_scenario) &
        (df['down_payment_pct'] == down_pct)
    ]
    
    if subset.empty:
        print(f"WARN: Exact match missing for {label} (Down={down_pct}), searching broad...")
        subset = df[
            (df['monthly_rent'] == rent) &
            (df['management_fee_pct_of_rent'] == mgmt) &
            (df['owner_use_scenario'] == owner_scenario)
        ].sort_values('avg_annual_cost')

    row = subset.iloc[0]
    
    own_cost = row['avg_annual_cost']
    rent_cost = row['rent_instead_cost']
    premium = own_cost - rent_cost
    cash_burn = -row['net_operating_cashflow']
    upfront = row['upfront_cash_required']
    
    print(f"\n[{label}] (6 Weeks / 20% Down)")
    print(f"Invested Upfront:        ${upfront:,.0f}")
    print(f"Total Economic Cost (Own): ${own_cost:,.0f} /yr")
    print(f"Alternative Cost (Rent):   ${rent_cost:,.0f} /yr")
    print(f"Premium to Own:            ${premium:,.0f} /yr ({(premium/12):.0f}/mo)")
    print(f"Annual Cash Burn (Own):    ${cash_burn:,.0f} /yr")

# SCENARIO PARAMS (Moderate: $2800, 75%, 7%, $20k, 18%, $250)
analyze("MODERATE", 2800, 0.75, 0.07, 20000, 0.18, 250)

# SCENARIO PARAMS (Best: $3100, 90%, 6%, $10k, 15%, $150)
analyze("BEST", 3100, 0.90, 0.06, 10000, 0.15, 150)

# SCENARIO PARAMS (Stress: $2400, 60%, 8%, $30k, 25%, $500)
analyze("STRESS", 2400, 0.60, 0.08, 30000, 0.25, 500)
