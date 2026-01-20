import csv
data = list(csv.DictReader(open('runs/2026-01-19__vineyard-point/exports/scenario_results.csv')))

# Define filters
def get_scenario(rent, fill, mgmt):
    return next(row for row in data if 
        row['monthly_rent']==str(rent) and 
        row['fill_rate']==str(fill) and 
        row['management_fee_pct_of_rent']==str(mgmt) and 
        row['interest_rate']=='0.07' and 
        row['down_payment_pct']=='0.2' and 
        row['horizon_years']=='7'
    )

best = get_scenario(3100.0, 0.9, 0.07)
moderate = get_scenario(2800.0, 0.75, 0.1)
stress = get_scenario(2400.0, 0.6, 0.15)

print(f"Best: ${float(best['furnish_budget']):,.0f}")
print(f"Moderate: ${float(moderate['furnish_budget']):,.0f}")
print(f"Stress: ${float(stress['furnish_budget']):,.0f}")
