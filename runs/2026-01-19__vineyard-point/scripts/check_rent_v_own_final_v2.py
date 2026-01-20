import pandas as pd
import numpy as np

# Load
df = pd.read_csv('runs/2026-01-19__vineyard-point/exports/scenario_results.csv')

# Filter Moderate
subset = df[
    (df['monthly_rent'] == 2800) &
    (df['fill_rate'] == 0.75) &
    (df['interest_rate'] == 0.07) &
    (df['furnish_budget'] == 20000) &
    (np.isclose(df['management_fee_pct_of_rent'], 0.18)) &
    (df['leasing_fee_per_lease'] == 250) &
    (df['owner_use_scenario'] == 'three_trips_feb_aug_dec') &
    (df['down_payment_pct'] == 0.20)
]

if subset.empty:
    print("No exact match found. Showing head of filtered by Rent/Fill/Int only:")
    broad = df[
        (df['monthly_rent'] == 2800) &
        (df['fill_rate'] == 0.75)
    ]
    print(broad.head())
else:
    row = subset.iloc[0]
    own_cost = row['avg_annual_cost']
    rent_cost = row['rent_instead_cost']
    premium = own_cost - rent_cost
    cash_burn = -row['net_operating_cashflow']
    upfront = row['upfront_cash_required']
    
    print(f"\n[MODERATE CASE CONFIRMATION]")
    print(f"Scenario: 6 Weeks Use | 20% Down | Current Rates")
    print(f"------------------------------------------------")
    print(f"1. Total Cost of Ownership:  ${own_cost:,.0f} /yr")
    print(f"   (Includes: interest, taxes, HOAs, maintenance, minus rental profit)")
    print(f"   (Does NOT subtract rent savings)")
    print(f"")
    print(f"2. Cost to Rent Instead:     ${rent_cost:,.0f} /yr")
    print(f"   (Based on: {row['rent_instead_cost']/2800:.1f} months equivalent rent)")
    print(f"")
    print(f"3. Economic Premium (Net):   ${premium:,.0f} /yr")
    print(f"   (You pay ${premium:,.0f} more than your alternative)")
    print(f"")
    print(f"4. Cash Flow Impact:         ${cash_burn:,.0f} /yr outflow")
    print(f"   (This is the check you actully write each year)")
