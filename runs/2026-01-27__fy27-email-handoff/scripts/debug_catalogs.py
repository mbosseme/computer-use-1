import pandas as pd
from google.cloud import bigquery

RUN_ID = "2026-01-27__fy27-email-handoff"
MAPPING_CSV = f"runs/{RUN_ID}/exports/jen_ndc_reference_mapping__verified.csv"
PROJECT_ID = "abi-inbound-prod"
DATASET_TAE = "abi_inbound_bq_stg_purchasing_provider_transaction"
TABLE_TAE = "transaction_analysis_expanded"

def get_catalogs():
    df_map = pd.read_csv(MAPPING_CSV)
    ref_nums = df_map['reference_number'].dropna().unique().tolist()
    valid_refs = [str(int(float(r))).strip() for r in ref_nums if str(r).strip().lower() != 'no_match']
    
    client = bigquery.Client(project=PROJECT_ID)
    ref_sql = ", ".join([f"'{r}'" for r in valid_refs])
    
    query = f"""
        SELECT DISTINCT manufacturer_catalog_number, reference_number 
        FROM `{PROJECT_ID}.{DATASET_TAE}.{TABLE_TAE}`
        WHERE reference_number IN ({ref_sql})
        AND manufacturer_catalog_number IS NOT NULL
    """
    
    df = client.query(query).to_dataframe()
    print(f"Found {len(df)} catalog numbers for {len(valid_refs)} refs.")
    # Normalize: strip dashes, spaces, uppercase
    df['norm_cat'] = df['manufacturer_catalog_number'].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True).str.upper()
    
    # Save for inspection
    df.to_csv(f"runs/{RUN_ID}/tmp/tae_catalogs.csv", index=False)
    
    # Return unique normalized query list
    return df['norm_cat'].unique().tolist()

if __name__ == "__main__":
    cats = get_catalogs()
    print(cats[:10])
