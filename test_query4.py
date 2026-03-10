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
        c.*, e.Contract_Category
    FROM `matthew-bossemeyer.dataform_hciq.contract_item_benchmark_summary` c
    JOIN contract_meta e ON c.Contract_Number = e.Contract_Number
    WHERE c.Portfolio_Prefix = 'PP'
    AND e.Contract_Category IN ('GASTROINTESTINAL ENDOSCOPY PRODUCTS', 'INTERVENTIONAL SHEATHS AND INTRODUCERS')
    AND c.is_benchmarked = TRUE
    AND e.Expiration_Date BETWEEN '2026-07-01' AND '2027-06-30'
    AND c.Spend_at_Best_Tier <= c.Total_Spend_6mo * 1.5
)
SELECT 
    Contract_Category,
    SUM(Total_Spend_6mo) as total,
    SUM(Spend_at_Best_Tier) as best,
    SUM(
        CASE WHEN contract_best_price > hciq_75_benchmark AND hciq_75_benchmark > 0 
        THEN (contract_best_price - hciq_75_benchmark) * Total_Units_6mo ELSE 0 END
    ) as savings
FROM item_gaps
GROUP BY 1
"""
df = client.query(query).to_dataframe()
print(df)