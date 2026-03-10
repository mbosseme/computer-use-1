from google.cloud import bigquery
client = bigquery.Client()
q = '''
SELECT Contract_Number, MAX(Contract_Category) as cat, MAX(service_line) as sl
FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
WHERE Contract_Number LIKE 'PP-%'
GROUP BY 1 LIMIT 5
'''
print(client.query(q).to_dataframe())
