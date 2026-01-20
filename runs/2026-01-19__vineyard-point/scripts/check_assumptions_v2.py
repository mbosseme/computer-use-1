import pandas as pd

# Load the full results
df = pd.read_csv('runs/2026-01-19__vineyard-point/exports/scenario_results.csv')

# Define case logic
# Best: High Rent, High Occupancy, Low Interest
best_case = df[
    (df['monthly_rent'] == df['monthly_rent'].max()) &
    (df['fill_rate'] == df['fill_rate'].max()) &
    (df['interest_rate'] == df['interest_rate'].min())
].sort_values('avg_annual_cost', ascending=True).iloc[0] # Lowest cost is best

# Moderate: Median assumptions
moderate_case = df[
    (df['monthly_rent'] == df['monthly_rent'].median()) &
    (df['fill_rate'] == df['fill_rate'].median()) &
    (df['interest_rate'] == df['interest_rate'].median())
].sort_values('avg_annual_cost', ascending=True).iloc[0] # Conservative pick within median

# Stress: Low Rent, Low Occupancy, High Interest
stress_case = df[
    (df['monthly_rent'] == df['monthly_rent'].min()) &
    (df['fill_rate'] == df['fill_rate'].min()) &
    (df['interest_rate'] == df['interest_rate'].max())
].sort_values('avg_annual_cost', ascending=False).iloc[0] # Highest cost is stress

print("--- Furnish Budget ---")
print(f"Best: ${best_case['furnish_budget']:,.0f}")
print(f"Moderate: ${moderate_case['furnish_budget']:,.0f}")
print(f"Stress: ${stress_case['furnish_budget']:,.0f}")

print("\n--- Management Fee Rate ---")
print(f"Best: {best_case['management_fee_pct_of_rent']*100:.1f}%")
print(f"Moderate: {moderate_case['management_fee_pct_of_rent']*100:.1f}%")
print(f"Stress: {stress_case['management_fee_pct_of_rent']*100:.1f}%")

print("\n--- Leasing Fee (per lease) ---")
print(f"Best: ${best_case['leasing_fee_per_lease']:,.0f}")
print(f"Moderate: ${moderate_case['leasing_fee_per_lease']:,.0f}")
print(f"Stress: ${stress_case['leasing_fee_per_lease']:,.0f}")
