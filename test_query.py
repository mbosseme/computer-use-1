from google.cloud import bigquery
import json

client = bigquery.Client(project="matthew-bossemeyer")

# Let's check why there's duplication. Let's look at the contract that had ~5000 items according to GPT. Wait, GPT said 1 contract, 5052 items. This could just refer to many items. Let's look at why "Savings > Total Spend" for Gastrointestinal Endoscopy

query = """
SELECT 
    Manufacturer_Catalog_Number, 
    COUNT(*) as num_rows,
    SUM(Total_Spend_6mo) as sum_total_spend,
    SUM(Spend_at_Best_Tier) as sum_best_tier_spend,
    SUM(CASE WHEN contract_best_price > hciq_75_benchmark AND hciq_75_benchmark > 0 THEN (contract_best_price - hciq_75_benchmark) * Total_Units_6mo ELSE 0 END) as savings
FROM `matthew-bossemeyer.dataform_hciq.contract_item_benchmark_summary` 
WHERE Portfolio_Prefix = 'PP'
GROUP BY 1
HAVING num_rows > 1
ORDER BY num_rows DESC
LIMIT 5
"""

df = client.query(query).to_dataframe()
print(df)
print("\n")

