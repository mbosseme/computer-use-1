import pandas as pd
from google.cloud import bigquery
import os

# Configuration
RUN_ID = "2026-01-27__fy27-email-handoff"
INPUT_MAPPING_CSV = f"runs/{RUN_ID}/exports/jen_ndc_reference_mapping__verified.csv"
OUTPUT_EXPANSION_CSV = f"runs/{RUN_ID}/exports/iv_solutions__expanded_ndc_scope.csv"
PROJECT_ID = "abi-inbound-prod" 
DATASET_ID = "abi_inbound_bq_stg_purchasing_provider_transaction"
TABLE_ID = "transaction_analysis_expanded"

def expand_ndc_scope():
    # 1. Load Verified Mapping
    print(f"Loading mapping from {INPUT_MAPPING_CSV}")
    df_map = pd.read_csv(INPUT_MAPPING_CSV)
    
    # Get unique Reference Numbers (anchor keys)
    ref_nums = df_map['reference_number'].dropna().unique().tolist()
    valid_refs = [str(int(float(r))).strip() for r in ref_nums if str(r).strip().lower() != 'no_match']
    
    # Get original normalized NDCs (to ensure we don't lose them)
    original_ndcs = df_map['matched_ndc_11'].dropna().unique().tolist()
    original_ndcs = [str(n).strip().replace('-', '') for n in original_ndcs] # Ensure clean, no dashes
    
    print(f"Found {len(valid_refs)} anchor Reference Numbers.")
    print(f"Found {len(original_ndcs)} original anchor NDCs.")
    
    if not valid_refs:
        print("No valid reference numbers found. Aborting.")
        return

    # 2. Query BigQuery for ALL NDCs associated with these Reference Numbers
    client = bigquery.Client(project=PROJECT_ID)
    
    ref_list_sql = ", ".join([f"'{r}'" for r in valid_refs])
    
    query = f"""
        SELECT DISTINCT 
            reference_number,
            ndc as expanded_ndc,
            manufacturer_catalog_number,
            facility_product_description
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE reference_number IN ({ref_list_sql})
        AND ndc IS NOT NULL
        AND CHAR_LENGTH(ndc) >= 10
    """
    
    print("Executing expansion query...")
    df_expanded = client.query(query).to_dataframe()
    
    print(f"Expansion query returned {len(df_expanded)} rows.")
    
    # Extract expanded NDCs
    query_ndcs = df_expanded['expanded_ndc'].unique().tolist()
    # Normalize (remove dashes just in case)
    query_ndcs = [str(n).strip().replace('-', '') for n in query_ndcs]
    
    # 3. Create Superset
    final_ndc_set = set(original_ndcs).union(set(query_ndcs))
    
    print(f"Original Anchor NDCs: {len(original_ndcs)}")
    print(f"TAE Expanded NDCs: {len(query_ndcs)}")
    print(f"Combined Union NDCs: {len(final_ndc_set)}")
    
    # Create output dataframe
    # We want a list of NDCs to iterate over for Report Builder
    df_output = pd.DataFrame({'ndc_11': list(final_ndc_set)})
    
    # 4. Save Expanded List
    df_output.to_csv(OUTPUT_EXPANSION_CSV, index=False)
    print(f"Saved combined NDC scope to {OUTPUT_EXPANSION_CSV}")
    
    # Profiling output included in print statements above

if __name__ == "__main__":
    expand_ndc_scope()
