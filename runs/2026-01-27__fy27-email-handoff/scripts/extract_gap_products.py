import os
import sys
import json
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

# Files/Paths
RUN_ID = "2026-01-27__fy27-email-handoff"
RUN_DIR = Path(f"runs/{RUN_ID}")
EXPORTS_DIR = RUN_DIR / "exports"
OUTPUT_FILE = EXPORTS_DIR / "iv_solutions__gap_products.csv"
REF_NUM_SCOPE_FILE = EXPORTS_DIR / "jen_ndc_reference_mapping__verified.csv"
BLINDING_MAP_FILE = EXPORTS_DIR / "iv_solutions__blinding_map__INTERNAL_ONLY.json"

# Config
DATE_START = "2024-01-01"
DATE_END = "2025-12-31"

# Tables
TAE_TABLE = "abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded"
RB_TABLE = "abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder"
PRODUCT_MASTER_TABLE = "abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master"
FACILITY_ATTRS_TABLE = "matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join"

# Target Criteria
TARGET_MFR = "FRESENIUS GROUP"
TARGET_CATEGORY = "IV THERAPY PRODUCTS - IV FLUIDS BAG-BASED DRUG DELIVERY AND TPN MACRONUTRIENTS"

def get_bq_client():
    return bigquery.Client()

def load_excluded_ref_nums():
    """Load reference numbers identified in Jen's request to EXCLUDE."""
    if not REF_NUM_SCOPE_FILE.exists():
        print(f"Warning: Scope file not found at {REF_NUM_SCOPE_FILE}. Assuming no exclusions.")
        return []
        
    df = pd.read_csv(REF_NUM_SCOPE_FILE)
    ref_nums = df['reference_number'].dropna().unique().tolist()
    valid_refs = [str(int(float(r))).strip() for r in ref_nums if str(r).strip().lower() != 'no_match']
    print(f"Loaded {len(valid_refs)} reference numbers to exclude (Jen's matches).")
    return valid_refs

def load_blinding_map():
    if not BLINDING_MAP_FILE.exists():
        print("Warning: Blinding map not found.")
        return {}
    with open(BLINDING_MAP_FILE, 'r') as f:
        return json.load(f)

def extract_gap_raw(client, excluded_refs):
    """
    Extract raw transaction data + Product Master attrs.
    Return DF with: entity_code, month_year, ndc11, reference_number, spend, source, vendor_name, ...
    """
    
    # Format exclusion list for SQL
    exclude_sql = ""
    if excluded_refs:
        exclude_list = ", ".join([f"'{r}'" for r in excluded_refs])
        exclude_sql = f"AND reference_number NOT IN ({exclude_list})"
    
    print("Querying for GAP products (Fresenius IV Fluids not in Jen's list)...")

    query = f"""
    WITH GapRefs AS (
        SELECT DISTINCT reference_number
        FROM `{TAE_TABLE}`
        WHERE 
            manufacturer_top_parent_name = '{TARGET_MFR}'
            AND contract_category = '{TARGET_CATEGORY}'
            AND Transaction_Date BETWEEN '{DATE_START}' AND '{DATE_END}'
            AND Landed_Spend > 0
            {exclude_sql}
    ),
    
    -- Transaction Data (TAE) for Gap Refs
    TxnData AS (
        SELECT 
            'ERP' AS source,
            t.reference_number,
            FORMAT_DATE('%Y-%m', t.Transaction_Date) AS month_year,
            t.Premier_Entity_Code as entity_code,
            LPAD(CAST(t.NDC AS STRING), 11, '0') AS ndc11,
            SUM(t.Landed_Spend) AS spend,
            ANY_VALUE(t.Vendor_Name) AS vendor_name
        FROM `{TAE_TABLE}` t
        JOIN GapRefs g ON t.reference_number = g.reference_number
        WHERE t.Transaction_Date BETWEEN '{DATE_START}' AND '{DATE_END}'
        GROUP BY 1, 2, 3, 4, 5
    ),
    
    -- Report Builder Data (Wholesaler) via NDC Match
    GapNDCs AS (
        SELECT DISTINCT 
            pm.reference_number,
            LPAD(CAST(pm.ndc AS STRING), 11, '0') AS ndc11
        FROM `{PRODUCT_MASTER_TABLE}` pm
        JOIN GapRefs g ON pm.reference_number = g.reference_number
    ),
    
    RecapData AS (
        SELECT
            'WHOLESALER' AS source,
            gn.reference_number,
            FORMAT_DATE('%Y-%m', PARSE_DATE('%Y-%m-%d', rb.invoice_date)) AS month_year,
            rb.facility_id AS entity_code,
            LPAD(CAST(rb.ndc AS STRING), 11, '0') AS ndc11,
            SUM(SAFE_CAST(rb.total_spend AS FLOAT64)) AS spend,
            ANY_VALUE(rb.wholesaler) AS vendor_name
        FROM `{RB_TABLE}` rb
        JOIN GapNDCs gn ON LPAD(CAST(rb.ndc AS STRING), 11, '0') = gn.ndc11
        WHERE PARSE_DATE('%Y-%m-%d', rb.invoice_date) BETWEEN '{DATE_START}' AND '{DATE_END}'
        GROUP BY 1, 2, 3, 4, 5
    ),
    
    -- Union Sources
    AllTxns AS (
        SELECT * FROM TxnData
        UNION ALL
        SELECT * FROM RecapData
    ),
    
    -- Enrich with Product Master
    -- Prioritize: Manufacturer ('M') + Each ('EA'), then Manufacturer ('M'), then populated description
    ProductMeta_Ranked AS (
        SELECT 
            *,
            ROW_NUMBER() OVER (
                PARTITION BY reference_number 
                ORDER BY 
                    CASE WHEN vend_type = 'M' AND pkg_uom = 'EA' THEN 1 
                         WHEN vend_type = 'M' THEN 2 
                         ELSE 3 
                    END,
                    CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 2 END
            ) as rn
        FROM `{PRODUCT_MASTER_TABLE}`
        WHERE reference_number IN (SELECT reference_number FROM GapRefs)
    ),
    
    ProductMeta_Best AS (
        SELECT
            reference_number,
            brand_name,
            description,
            product_group_category,
            product_subcategory1,
            product_subcategory2,
            product_subcategory3,
            product_contract_category as contract_category,
            top_parent_name as manufacturer_top_parent,
            manufacturer_name,
            manufacturer_catalog_number as mfr_catalog_num,
            COALESCE(drug_generic_name, description) AS generic_name,
            drug_form_code AS dosage_form
        FROM ProductMeta_Ranked
        WHERE rn = 1
    )
    
    SELECT 
        t.*,
        pm.brand_name,
        pm.description,
        pm.product_group_category,
        pm.product_subcategory1,
        pm.product_subcategory2,
        pm.product_subcategory3,
        pm.contract_category,
        pm.manufacturer_top_parent,
        pm.manufacturer_name,
        pm.mfr_catalog_num,
        pm.generic_name,
        pm.dosage_form
    FROM AllTxns t
    LEFT JOIN ProductMeta_Best pm ON t.reference_number = pm.reference_number
    """
    
    # Run Query
    df = client.query(query).to_dataframe()
    return df

def extract_facility_attributes(client, facility_ids):
    """
    Extract facility state/zip from SA/SF table.
    """
    if not facility_ids:
        return pd.DataFrame(columns=['facility_id', 'state', 'zip3'])
        
    fac_list = ", ".join([f"'{f}'" for f in facility_ids if f])
    
    # We process in chunks if too many, but for 2-3k facilities simpler is fine. 
    # Max query length is an issue, BQ is generous.
    
    query = f"""
    SELECT DISTINCT
        COALESCE(facility_entity_code, SF_Entity_Code) AS facility_id,
        COALESCE(dhc_state, State_sa_sf) AS state,
        COALESCE(LEFT(dhc_zip_code, 3), LEFT(Zip_Code_sa_sf, 3)) AS zip3
    FROM `{FACILITY_ATTRS_TABLE}`
    WHERE COALESCE(facility_entity_code, SF_Entity_Code) IN ({fac_list})
    """
    
    print(f"Extracting facility attributes for {len(facility_ids)} facilities...")
    return client.query(query).to_dataframe()

def main():
    if not EXPORTS_DIR.exists():
        os.makedirs(EXPORTS_DIR)
        
    client = get_bq_client()
    
    excluded_refs = load_excluded_ref_nums()
    blinding_map = load_blinding_map()
    
    # 1. Extract Raw Gap Data
    df_gap = extract_gap_raw(client, excluded_refs)
    print(f"Extracted {len(df_gap)} raw rows.")
    
    # 2. Extract Facility Attributes
    unique_facs = df_gap['entity_code'].dropna().unique().tolist()
    df_facs = extract_facility_attributes(client, unique_facs)
    
    # 3. Join Attributes
    print("Joining facility attributes...")
    df_final = df_gap.merge(df_facs, left_on='entity_code', right_on='facility_id', how='left')
    
    # 4. Update & Apply Blinding
    print("Updating blinding map...")
    # Map might have changed or we loaded it earlier. Let's ensure we have the latest or just use the dict we loaded.
    # Actually, let's allow extending it.
    current_map = load_blinding_map() # Reload to be safe/consistent
    
    # Check for new keys
    # Use 'entity_code' which is the raw ID
    all_gap_facilities = df_final['entity_code'].dropna().unique()
    new_facilities = [f for f in all_gap_facilities if f not in current_map]
    
    if new_facilities:
        print(f"Found {len(new_facilities)} new facilities to blind. Extending map...")
        # Determine next ID
        existing_values = [v for v in current_map.values() if v.startswith("FAC_")]
        max_id = 0
        if existing_values:
            max_id = max([int(v.split('_')[1]) for v in existing_values])
        
        # Assign new IDs
        for i, fac_id in enumerate(sorted(new_facilities), start=1):
            new_blinded_id = f"FAC_{max_id + i:05d}"
            current_map[fac_id] = new_blinded_id
            
        # Save updated map
        with open(BLINDING_MAP_FILE, 'w') as f:
            json.dump(current_map, f, indent=2)
        print(f"Blinding map updated with {len(new_facilities)} new facilities.")
    else:
        print("No new facilities found. Using existing map.")
    
    # Apply Blinding
    df_final['blinded_facility_id'] = df_final['entity_code'].map(current_map)
    
    # Double check for missing
    missing_mask = df_final['blinded_facility_id'].isna()
    if missing_mask.any():
        print(f"Warning: {missing_mask.sum()} rows still unblinded after update! (Should not happen)")
        df_final.loc[missing_mask, 'blinded_facility_id'] = "UNMAPPED"


    # 5. Format Columns to match Extract 1
    # Target: 
    # blinded_facility_id, month_year, ndc11, reference_number, spend, source, state, zip3, 
    # vendor_name, brand_name, description, product_group_category, product_subcategory1, 
    # product_subcategory2, product_subcategory3, contract_category, manufacturer_top_parent, 
    # manufacturer_name, mfr_catalog_num, generic_name, dosage_form
    
    cols = [
        "blinded_facility_id", "month_year", "ndc11", "reference_number", "spend", "source", 
        "state", "zip3", "vendor_name", "brand_name", "description", "product_group_category", 
        "product_subcategory1", "product_subcategory2", "product_subcategory3", "contract_category", 
        "manufacturer_top_parent", "manufacturer_name", "mfr_catalog_num", "generic_name", "dosage_form"
    ]
    
    # Reorder/Select
    df_out = df_final[cols]
    
    print(f"Total Spend: ${df_out['spend'].sum():,.2f}")
    
    print(f"Saving to {OUTPUT_FILE}...")
    df_out.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
