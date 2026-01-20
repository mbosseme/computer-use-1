import pandas as pd
import numpy as np

# Load
df = pd.read_csv('runs/2026-01-19__vineyard-point/exports/scenario_results.csv')

# Use EXACT same logic as check_scenarios_v3.py to find the "Memo Scenario"
rent = 2800
occ = 0.75
interest = 0.07
furnish = 20000
mgmt_pct = 0.18
lease_fee = 250

subset = df[
    (df['monthly_rent'] == rent) &
    (df['fill_rate'] == occ) &
    (df['interest_rate'] == interest) &
    (df['furnish_budget'] == furnish) &
    (np.isclose(df['management_fee_pct_of_rent'], mgmt_pct)) &
    (df['leasing_fee_per_lease'] == lease_fee)
]

# Sort as the v3 script did
best_row = subset.sort_values('avg_annual_cost', ascending=True).iloc[0]

# Now display what hidden variables determined this outcome
print("\n[MEMO 'MODERATE' SCENARIO DIAGNOSIS]")
print(f"Cost Found:      ${best_row['avg_annual_cost']:,.0f}")
print(f"Owner Use:       {best_row['owner_use_scenario']}")
print(f"Down Payment:    {best_row['down_payment_pct']*100:.0f}%")
print(f"Rent Instead:    ${best_row['rent_instead_cost']:,.0f}")
print(f"Net Premium:     ${best_row['avg_annual_cost'] - best_row['rent_instead_cost']:,.0f}")
