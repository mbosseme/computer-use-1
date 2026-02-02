from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT reference_number, description, manufacturer_catalog_number 
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
WHERE manufacturer_catalog_number = '060-10109'
LIMIT 5
"""

df = client.query(query).to_dataframe()
print(df)
