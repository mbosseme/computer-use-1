import pandas as pd

# Load
df = pd.read_csv('runs/2026-01-19__vineyard-point/exports/scenario_results.csv')

print("Loaded rows:", len(df))
print("\nUnique Rents:", sorted(df['monthly_rent'].unique()))
print("Unique Fill Rates:", sorted(df['fill_rate'].unique()))
print("Unique Interest:", sorted(df['interest_rate'].unique()))
print("Unique Furnish:", sorted(df['furnish_budget'].unique()))
print("Unique Mgmt Fees:", sorted(df['management_fee_pct_of_rent'].unique()))
print("Unique Leasing Fees:", sorted(df['leasing_fee_per_lease'].unique()))
print("Unique Scenarios:", df['owner_use_scenario'].unique())
print("Unique Down Pct:", sorted(df['down_payment_pct'].unique()))
