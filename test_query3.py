from google.cloud import bigquery
client = bigquery.Client(project="matthew-bossemeyer")

query = """
SELECT 
    COUNT(*) as num_rows,
    SUM(CASE WHEN Spend_at_Best_Tier > Total_Spend_6mo * 2 THEN 1 ELSE 0 END) as bad_uom_rows,
    SUM(Total_Spend_6mo) as sum_total,
    SUM(Spend_at_Best_Tier) as sum_best
FROM `matthew-bossemeyer.dataform_hciq.contract_item_benchmark_summary` 
WHERE Portfolio_Prefix = 'PP'
"""
df = client.query(query).to_dataframe()
print(df)
