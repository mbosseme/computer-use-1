import pandas as pd
from google.cloud import bigquery
import json
import os

# Configuration
RUN_ID = "2026-01-27__fy27-email-handoff"
MAPPING_CSV = f"runs/{RUN_ID}/exports/jen_ndc_reference_mapping__verified.csv"
OUTPUT_CSV = f"runs/{RUN_ID}/exports/jen_transaction_sample_data.csv"
PROJECT_ID = "abi-inbound-prod" # Standard project
DATASET_ID = "abi_inbound_bq_stg_purchasing_provider_transaction"
TABLE_ID = "transaction_analysis_expanded"

def get_reference_numbers(csv_path):
    df = pd.read_csv(csv_path)
    # Filter out NaNs if any, though we expect 100% match
    refs = df['reference_number'].dropna().unique().tolist()
    # Ensure they are strings for SQL
    return [str(int(float(r))).strip() for r in refs if str(r).strip().lower() != 'no_match']

def pull_data(refs):
    if not refs:
        print("No reference numbers found.")
        return

    client = bigquery.Client(project=PROJECT_ID)
    
    # Format list for SQL
    ref_list_str = ", ".join([f"'{r}'" for r in refs])
    
    query = f"""
        SELECT 
            transaction_date,
            reference_number,
            manufacturer_catalog_number,
            facility_vendor_catalog_num,
            facility_product_description,
            vendor_name,
            landed_spend,
            base_spend,
            quantity,
            pkg_uom
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE reference_number IN ({ref_list_str})
        AND transaction_date >= '2024-01-01'
        LIMIT 10000
    """
    
    print(f"Querying BigQuery for {len(refs)} reference numbers...")
    df = client.query(query).to_dataframe()
    
    print(f"Retrieved {len(df)} rows.")
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    refs = get_reference_numbers(MAPPING_CSV)
    print(f"Found {len(refs)} unique reference numbers.")
    pull_data(refs)
