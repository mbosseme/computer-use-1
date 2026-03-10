from google.cloud import bigquery
client = bigquery.Client(project="matthew-bossemeyer")

query = """
WITH contract_meta AS (
    SELECT 
        Contract_Number,
        MAX(CAST(Contract_Expiration_Date AS DATE)) as Expiration_Date,
        MAX(Contract_Category) as Contract_Category,
        MAX(service_line) as Service_Line
    FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
    WHERE Contract_Number LIKE 'PP-%'
    GROUP BY 1
),
item_gaps AS (
    SELECT 
        c.Manufacturer_Catalog_Number,
        c.Contract_Number,
        e.Contract_Category,
        c.Total_Spend_6mo,
        c.Spend_at_Best_Tier,
        c.Total_Units_6mo,
        c.contract_best_price,
        c.hciq_75_benchmark
    FROM `matthew-bossemeyer.dataform_hciq.contract_item_benchmark_summary` c
    JOIN contract_meta e ON c.Contract_Number = e.Contract_Number
    WHERE c.Portfolio_Prefix = 'PP'
        AND c.is_benchmarked = TRUE
        AND e.Expiration_Date BETWEEN '2026-07-01' AND '2027-06-30'
    AND e.Contract_Category = 'GASTROINTESTINAL ENDOSCOPY PRODUCTS'
)
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT Manufacturer_Catalog_Number) as dist_items,
    SUM(Total_Spend_6mo) as sum_total,
    SUM(Spend_at_Best_Tier) as sum_best,
    SUM(CASE WHEN contract_best_price > hciq_75_benchmark AND hciq_75_benchmark > 0 
        THEN (contract_best_price - hciq_75_benchmark) * Total_Units_6mo ELSE 0 END) as savings
FROM item_gaps
"""
df = client.query(query).to_dataframe()
print(df)
