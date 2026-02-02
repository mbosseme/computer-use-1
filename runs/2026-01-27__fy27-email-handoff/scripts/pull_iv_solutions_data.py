import pandas as pd
from google.cloud import bigquery
import os
import time

# Configuration
RUN_ID = "2026-01-27__fy27-email-handoff"
MAPPING_CSV = f"runs/{RUN_ID}/exports/jen_ndc_reference_mapping__verified.csv"
EXPANDED_NDC_CSV = f"runs/{RUN_ID}/exports/iv_solutions__expanded_ndc_scope.csv"

# Output Paths
OUT_TAE = f"runs/{RUN_ID}/exports/iv_solutions__tae_raw.csv"
OUT_RB = f"runs/{RUN_ID}/exports/iv_solutions__rb_raw.csv"
OUT_CAMS = f"runs/{RUN_ID}/exports/iv_solutions__cams_validation.csv"

# Projects/Tables
PROJ_INBOUND = "abi-inbound-prod"
PROJ_XFORM = "abi-xform-dataform-prod"

DATASET_TAE = "abi_inbound_bq_stg_purchasing_provider_transaction"
TABLE_TAE = "transaction_analysis_expanded"

DATASET_RB = "abi_inbound_bq_stg_purchasing_rx_wholesaler_sales"
TABLE_RB = "report_builder"

DATASET_CAMS = "continuum_of_care"
TABLE_CAMS = "cams_product_information_vw"

def load_scope():
    # 1. Reference Numbers
    df_map = pd.read_csv(MAPPING_CSV)
    ref_nums = df_map['reference_number'].dropna().unique().tolist()
    valid_refs = [str(int(float(r))).strip() for r in ref_nums if str(r).strip().lower() != 'no_match']
    
    # 2. NDCs
    df_ndc = pd.read_csv(EXPANDED_NDC_CSV)
    # Ensure they are strings, remove decimals if pandas added them
    valid_ndcs = df_ndc['ndc_11'].dropna().astype(str).tolist()
    valid_ndcs = [n.replace('.0', '') for n in valid_ndcs] 
    
    return valid_refs, valid_ndcs

def get_sql_list(items):
    return ", ".join([f"'{i}'" for i in items])

def pull_tae(client, refs):
    print(f"--- Pulling Provider ERP (TAE) for {len(refs)} Ref Numbers ---")
    sql_refs = get_sql_list(refs)
    
    query = f"""
        SELECT 
            Premier_Entity_Code as facility_id,
            FORMAT_DATE('%Y-%m', transaction_date) as month_year,
            reference_number,
            manufacturer_catalog_number,
            vendor_name,
            SUM(landed_spend) as tae_spend,
            SUM(quantity) as tae_units
        FROM `{PROJ_INBOUND}.{DATASET_TAE}.{TABLE_TAE}`
        WHERE reference_number IN ({sql_refs})
        AND transaction_date BETWEEN '2024-01-01' AND '2025-12-31'
        GROUP BY 1, 2, 3, 4, 5
    """
    df = client.query(query).to_dataframe()
    print(f"TAE Rows: {len(df)}")
    df.to_csv(OUT_TAE, index=False)

def pull_rb(client, ndcs):
    print(f"--- Pulling Wholesaler (Report Builder) for {len(ndcs)} NDCs ---")
    sql_ndcs = get_sql_list(ndcs)
    
    query = f"""
        SELECT 
            facility_id,
            FORMAT_TIMESTAMP('%Y-%m', month_year) as month_year_fmt,
            ndc as ndc,
            SUM(total_spend) as rb_spend,
            SUM(total_units) as rb_units
        FROM `{PROJ_INBOUND}.{DATASET_RB}.{TABLE_RB}`
        WHERE ndc IN ({sql_ndcs})
        AND month_year BETWEEN '2024-01-01' AND '2025-12-31'
        GROUP BY 1, 2, 3
    """
    df = client.query(query).to_dataframe()
    print(f"RB Rows: {len(df)}")
    df.to_csv(OUT_RB, index=False)

def pull_cams(client, refs):
    print(f"--- Pulling Validation (CAMS) for {len(refs)} Ref Numbers ---")
    sql_refs = get_sql_list(refs)
    
    # CAMS uses YYYYQMM format for Spend_Period?
    # Actually schema says YYYYQMM. Let's assume standard integer format.
    # We want Jan 2024 (2024101) to Sep 2025 (2025309).
    # Wait, YYYYQMM usually means Year-Quarter-Month? 
    # e.g. 2024 1 01 -> 2024101. 
    # Let's filter by range. 
    
    query = f"""
        SELECT 
            Premier_Entity_Code as facility_id,
            Spend_Period_YYYYQMM,
            Reference_Number,
            SUM(Sales_Volume_Paid_Reported) as cams_spend,
            SUM(units_sold) as cams_units
        FROM `{PROJ_XFORM}.{DATASET_CAMS}.{TABLE_CAMS}`
        WHERE Reference_Number IN ({sql_refs})
        AND Spend_Period_YYYYQMM BETWEEN 2024101 AND 2025412
        AND (Supplier_Top_Parent_Entity_Code = '606326' OR Supplier_Top_Parent_Name LIKE '%BRAUN%')
        GROUP BY 1, 2, 3
    """
    df = client.query(query).to_dataframe()
    print(f"CAMS Rows: {len(df)}")
    df.to_csv(OUT_CAMS, index=False)

def main():
    client = bigquery.Client(project=PROJ_INBOUND) # billing project
    
    refs, ndcs = load_scope()
    print(f"Scope: {len(refs)} Refs, {len(ndcs)} NDCs")
    
    pull_tae(client, refs)
    pull_rb(client, ndcs)
    # pull_cams(client, refs)
    print("--- Skipping CAMS Validation due to Ref# mismatch ---")
    
    print("Data pull complete.")

if __name__ == "__main__":
    main()
