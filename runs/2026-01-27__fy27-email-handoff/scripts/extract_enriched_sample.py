#!/usr/bin/env python3
"""
Extract Enriched Sample Data for B. Braun IV Solutions

This script pulls enriched data from BigQuery with:
- TAE: Product/manufacturer attributes, facility geo (from TAE itself)
- RB: Facility geo columns, product identifiers
- Product Master: Additional product attributes via NDC join
- Facility Attributes: Hospital type, bed count, etc. via entity code join

Outputs raw enriched CSVs for downstream sample generation.
"""

import os
import sys
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# Configuration
RUN_ID = "2026-01-27__fy27-email-handoff"
RUN_DIR = Path(f"runs/{RUN_ID}")
EXPORTS_DIR = RUN_DIR / "exports"

# B. Braun manufacturer entity code
BBRAUN_ENTITY_CODE = "606326"

# Validated NDC scope file
NDC_SCOPE_FILE = EXPORTS_DIR / "iv_solutions__expanded_ndc_scope.csv"
REF_NUM_SCOPE_FILE = EXPORTS_DIR / "jen_ndc_reference_mapping__verified.csv"

# Sample window
DATE_START = "2024-01-01"
DATE_END = "2025-12-31"

# BigQuery tables
TAE_TABLE = "abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded"
RB_TABLE = "abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder"
FACILITY_ATTRS_TABLE = "matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join"
PRODUCT_MASTER_TABLE = "abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master"


def get_bq_client():
    """Initialize BigQuery client."""
    # Use default credentials
    return bigquery.Client()


def load_ndc_scope():
    """Load the validated NDC scope."""
    df = pd.read_csv(NDC_SCOPE_FILE)
    # Column is 'ndc_11' in the scope file
    ndcs = df['ndc_11'].astype(str).str.split('.').str[0].str.zfill(11).tolist()
    print(f"Loaded {len(ndcs)} NDCs from scope file")
    return ndcs


def load_reference_number_scope():
    """Load reference numbers for TAE filtering."""
    df = pd.read_csv(REF_NUM_SCOPE_FILE)
    ref_nums = df['reference_number'].dropna().unique().tolist()
    # Clean: convert to int then string to remove decimals
    valid_refs = [str(int(float(r))).strip() for r in ref_nums if str(r).strip().lower() != 'no_match']
    print(f"Loaded {len(valid_refs)} reference numbers from scope file")
    return valid_refs


def format_ndc_list_sql(ndcs: list) -> str:
    """Format NDC list for SQL IN clause."""
    return ", ".join([f"'{ndc}'" for ndc in ndcs])


def extract_tae_enriched(client: bigquery.Client, ref_nums: list) -> pd.DataFrame:
    """
    Extract enriched TAE data.
    
    NOTE: TAE is filtered by reference_number (PIN), not NDC, because:
    - The original raw extraction used reference_number and captured $39.5M spend
    - NDC format in TAE is variable-length (not always 11-digit)
    - Reference numbers from the verified mapping are the canonical scope
    
    Product metadata (including reference_number) will come from PM via NDC join later.
    """
    ref_list = ", ".join([f"'{r}'" for r in ref_nums])
    
    query = f"""
    SELECT
        -- Identifiers
        Premier_Entity_Code AS facility_id,
        FORMAT_DATE('%Y-%m', Transaction_Date) AS month_year,
        LPAD(CAST(NDC AS STRING), 11, '0') AS ndc11,
        reference_number,
        
        -- Spend metrics
        SUM(Landed_Spend) AS tae_spend,
        
        -- Vendor (transaction-specific, not in PM)
        ANY_VALUE(Vendor_Name) AS vendor_name
        
    FROM `{TAE_TABLE}`
    WHERE reference_number IN ({ref_list})
      AND Transaction_Date >= '{DATE_START}'
      AND Transaction_Date <= '{DATE_END}'
    GROUP BY
        Premier_Entity_Code,
        FORMAT_DATE('%Y-%m', Transaction_Date),
        NDC,
        reference_number
    ORDER BY facility_id, month_year, ndc11
    """
    
    print("Extracting enriched TAE data...")
    print(f"  Date range: {DATE_START} to {DATE_END}")
    print(f"  Reference number scope: {len(ref_nums)} PINs")
    
    df = client.query(query).to_dataframe()
    print(f"  Rows returned: {len(df):,}")
    print(f"  Total spend: ${df['tae_spend'].sum():,.2f}")
    
    return df


def get_expanded_ndcs_from_master(client: bigquery.Client, ref_nums: list) -> list:
    """
    Get Valid NDCs from Premier Primary Item Master using Reference Numbers.
    
    This bridges the gap between Reference Numbers (Group level) and 
    Specific NDCs (Product Level) for querying Report Builder.
    """
    if not ref_nums:
        return []
        
    ref_list = ", ".join([f"'{str(r).strip()}'" for r in ref_nums])
    
    query = f"""
    SELECT DISTINCT 
        LPAD(CAST(ndc AS STRING), 11, '0') as ndc11
    FROM `{PRODUCT_MASTER_TABLE}`
    WHERE reference_number IN ({ref_list})
      AND ndc IS NOT NULL
    """
    
    print("\nExpanding NDCs via Item Master...")
    df = client.query(query).to_dataframe()
    found_ndcs = df['ndc11'].dropna().unique().tolist()
    print(f"  Found {len(found_ndcs)} valid NDCs for {len(ref_nums)} Reference Numbers")
    
    return found_ndcs


def extract_rb_enriched(client: bigquery.Client, ndcs: list) -> pd.DataFrame:
    """
    Extract enriched RB (Wholesaler) data with facility geo columns.
    
    RB already has facility_state, facility_zip_code, facility_city.
    Also has generic_name, brand_name, dosage_form_desc, ahfs_desc.
    """
    ndc_list = format_ndc_list_sql(ndcs)
    
    query = f"""
    SELECT
        -- Identifiers
        facility_id AS facility_id,
        FORMAT_DATE('%Y-%m', PARSE_DATE('%Y-%m-%d', invoice_date)) AS month_year,
        ndc AS ndc11,
        
        -- Spend metrics
        SUM(SAFE_CAST(total_spend AS FLOAT64)) AS rb_spend,
        
        -- Facility geo (from RB itself)
        ANY_VALUE(facility_state) AS rb_facility_state,
        ANY_VALUE(LEFT(CAST(facility_zip_code AS STRING), 3)) AS rb_facility_zip3,
        ANY_VALUE(facility_city) AS rb_facility_city,
        
        -- Vendor (transaction-specific - wholesaler field is RB's vendor equivalent)
        ANY_VALUE(wholesaler) AS rb_vendor_name
        
    FROM `{RB_TABLE}`
    WHERE ndc IN ({ndc_list})
      AND PARSE_DATE('%Y-%m-%d', invoice_date) >= DATE('{DATE_START}')
      AND PARSE_DATE('%Y-%m-%d', invoice_date) <= DATE('{DATE_END}')
    GROUP BY
        facility_id,
        FORMAT_DATE('%Y-%m', PARSE_DATE('%Y-%m-%d', invoice_date)),
        ndc
    ORDER BY facility_id, month_year, ndc11
    """
    
    print("\nExtracting enriched RB data...")
    print(f"  Date range: {DATE_START} to {DATE_END}")
    print(f"  NDC scope: {len(ndcs)} NDCs")
    
    df = client.query(query).to_dataframe()
    print(f"  Rows returned: {len(df):,}")
    
    return df


def extract_facility_attributes(client: bigquery.Client, facility_ids: list) -> pd.DataFrame:
    """
    Extract facility attributes from sa_sf_dhc_join.
    
    Join key: facility_entity_code (or SF_Entity_Code) = Premier_Entity_Code from TAE.
    
    Columns pulled (blinded-safe):
    - facility_state: COALESCE(dhc_state, State_sa_sf)
    - facility_zip3: COALESCE(dhc_zip3, sa_sf_zip3)
    - dhc_idn_parent: System affiliation (retaining context)
    """
    fac_list = ", ".join([f"'{f}'" for f in facility_ids if f])
    
    query = f"""
    SELECT DISTINCT
        -- Join key
        COALESCE(facility_entity_code, SF_Entity_Code) AS facility_id,
        
        -- Geo (blinded: state and 3-digit zip only)
        -- Broadened logic: Use SA/SF columns if DHC is missing to maximize coverage
        COALESCE(dhc_state, State_sa_sf) AS facility_state,
        COALESCE(LEFT(dhc_zip_code, 3), LEFT(Zip_Code_sa_sf, 3)) AS facility_zip3,
        
        -- System affiliation (not identifying, useful for context)
        dhc_idn_parent AS dhc_idn_parent
        
    FROM `{FACILITY_ATTRS_TABLE}`
    WHERE COALESCE(facility_entity_code, SF_Entity_Code) IN ({fac_list})
    """
    
    print("\nExtracting facility attributes...")
    print(f"  Facility IDs to lookup: {len(facility_ids):,}")
    
    df = client.query(query).to_dataframe()
    print(f"  Rows returned: {len(df):,}")
    print(f"  Unique facilities matched: {df['facility_id'].nunique():,}")
    
    return df


def extract_product_master_attributes(client: bigquery.Client, ndcs: list) -> pd.DataFrame:
    """
    Extract product master attributes for NDC-based enrichment.
    
    Strategy for multiple records per NDC:
    - Use window function to pick the "best" record per NDC
    - Prefer: non-null description, most recent record (by row order), alphabetically first
    """
    ndc_list = format_ndc_list_sql(ndcs)
    
    query = f"""
    WITH ranked AS (
        SELECT
            LPAD(CAST(ndc AS STRING), 11, '0') AS ndc11,
            
            -- Reference number (PIN) from PM - canonical source
            CAST(reference_number AS STRING) AS pm_reference_number,
            
            -- Product metadata (canonical source for all rows)
            brand_name AS pm_brand_name,
            description AS pm_description,
            product_group_category AS pm_product_group_category,
            product_subcategory1 AS pm_product_subcategory1,
            product_subcategory2 AS pm_product_subcategory2,
            product_subcategory3 AS pm_product_subcategory3,
            product_contract_category AS pm_contract_category,
            top_parent_name AS pm_manufacturer_top_parent,
            manufacturer_name AS pm_manufacturer_name,
            
            -- Additional product attributes
            manufacturer_catalog_number AS pm_mfr_catalog_num,
            COALESCE(drug_generic_name, description) AS pm_generic_name,
            drug_form_code AS pm_dosage_form,
            
            -- Ranking: prefer records with description, then by contract info
            ROW_NUMBER() OVER (
                PARTITION BY LPAD(CAST(ndc AS STRING), 11, '0')
                ORDER BY
                    CASE WHEN description IS NOT NULL AND description != '' THEN 0 ELSE 1 END,
                    CASE WHEN contracted = 'Y' THEN 0 ELSE 1 END,
                    CAST(reference_number AS STRING)
            ) AS rn
        FROM `{PRODUCT_MASTER_TABLE}`
        WHERE LPAD(CAST(ndc AS STRING), 11, '0') IN ({ndc_list})
    )
    SELECT
        ndc11,
        pm_reference_number,
        pm_brand_name,
        pm_description,
        pm_product_group_category,
        pm_product_subcategory1,
        pm_product_subcategory2,
        pm_product_subcategory3,
        pm_contract_category,
        pm_manufacturer_top_parent,
        pm_manufacturer_name,
        pm_mfr_catalog_num,
        pm_generic_name,
        pm_dosage_form
    FROM ranked
    WHERE rn = 1
    """
    
    print("\nExtracting product master attributes...")
    print(f"  NDC scope: {len(ndcs)} NDCs")
    
    df = client.query(query).to_dataframe()
    print(f"  Rows returned: {len(df):,}")
    print(f"  NDCs matched: {df['ndc11'].nunique():,}")
    
    return df


def extract_product_master_attributes_by_reference_numbers(client: bigquery.Client, ref_nums: list) -> pd.DataFrame:
    """Extract best-available product metadata keyed by reference number.

    This is required for cases where Premier Primary Item Master has rows with
    `reference_number` present but `ndc` is NULL. Those rows
    will never be returned by NDC-based extraction.
    """
    if not ref_nums:
        return pd.DataFrame(
            columns=[
                'ndc11',
                'pm_reference_number',
                'pm_brand_name',
                'pm_description',
                'pm_product_group_category',
                'pm_product_subcategory1',
                'pm_product_subcategory2',
                'pm_product_subcategory3',
                'pm_contract_category',
                'pm_manufacturer_top_parent',
                'pm_manufacturer_name',
                'pm_mfr_catalog_num',
                'pm_generic_name',
                'pm_dosage_form',
            ]
        )

    ref_list = ", ".join([f"'{str(r).strip()}'" for r in ref_nums])

    query = f"""
    WITH ranked AS (
        SELECT
            -- IMPORTANT: This extract is used for reference-number fallback only.
            -- Keep ndc11 NULL to avoid creating duplicate ndc11 keys that can
            -- cause many-to-many joins (row explosions) downstream.
            CAST(NULL AS STRING) AS ndc11,

            -- Reference number (PIN) - canonical
            CAST(reference_number AS STRING) AS pm_reference_number,

            -- Product metadata
            brand_name AS pm_brand_name,
            description AS pm_description,
            product_group_category AS pm_product_group_category,
            product_subcategory1 AS pm_product_subcategory1,
            product_subcategory2 AS pm_product_subcategory2,
            product_subcategory3 AS pm_product_subcategory3,
            product_contract_category AS pm_contract_category,
            top_parent_name AS pm_manufacturer_top_parent,
            manufacturer_name AS pm_manufacturer_name,
            manufacturer_catalog_number AS pm_mfr_catalog_num,
            COALESCE(drug_generic_name, description) AS pm_generic_name,
            drug_form_code AS pm_dosage_form,

            ROW_NUMBER() OVER (
                PARTITION BY CAST(reference_number AS STRING)
                ORDER BY
                    CASE WHEN description IS NOT NULL AND description != '' THEN 0 ELSE 1 END,
                    CASE WHEN contracted = 'Y' THEN 0 ELSE 1 END,
                    LPAD(CAST(ndc AS STRING), 11, '0')
            ) AS rn
        FROM `{PRODUCT_MASTER_TABLE}`
        WHERE CAST(reference_number AS STRING) IN ({ref_list})
    )
    SELECT
        ndc11,
        pm_reference_number,
        pm_brand_name,
        pm_description,
        pm_product_group_category,
        pm_product_subcategory1,
        pm_product_subcategory2,
        pm_product_subcategory3,
        pm_contract_category,
        pm_manufacturer_top_parent,
        pm_manufacturer_name,
        pm_mfr_catalog_num,
        pm_generic_name,
        pm_dosage_form
    FROM ranked
    WHERE rn = 1
    """

    print("\nExtracting product master attributes by reference number...")
    print(f"  Reference number scope: {len(ref_nums)} PINs")

    df = client.query(query).to_dataframe()
    print(f"  Rows returned: {len(df):,}")
    print(f"  Reference numbers matched: {df['pm_reference_number'].nunique():,}")

    return df


def main():
    print("=" * 60)
    print("B. Braun IV Solutions — Enriched Sample Extraction")
    print("=" * 60)
    
    # Ensure output directory exists
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load scopes
    ndcs = load_ndc_scope()
    ref_nums = load_reference_number_scope()
    
    # Initialize BigQuery client
    client = get_bq_client()
    
    # 1. Extract enriched TAE (filtered by reference_number to match original $39M scope)
    df_tae = extract_tae_enriched(client, ref_nums)
    tae_output = EXPORTS_DIR / "iv_solutions__tae_enriched.csv"
    df_tae.to_csv(tae_output, index=False)
    print(f"  Saved: {tae_output}")
    
    # 2. Extract enriched RB
    # EXPANSION: Find all valid NDCs for our Reference Numbers from Product Master
    # This ensures we get the "Official" NDCs for querying Report Builder
    expanded_ndcs = get_expanded_ndcs_from_master(client, ref_nums)
    
    # Merge original scope NDCs with found ones (deduplicated)
    final_rb_ndcs = list(set(ndcs + expanded_ndcs))
    print(f"  Final RB Query Scope: {len(final_rb_ndcs)} unique NDCs")

    df_rb = extract_rb_enriched(client, final_rb_ndcs)
    rb_output = EXPORTS_DIR / "iv_solutions__rb_enriched.csv"
    df_rb.to_csv(rb_output, index=False)
    print(f"  Saved: {rb_output}")
    
    # 3. Get all unique facility IDs from both sources
    all_facility_ids = set(df_tae['facility_id'].dropna().unique()) | set(df_rb['facility_id'].dropna().unique())
    print(f"\nTotal unique facility IDs: {len(all_facility_ids):,}")
    
    # 4. Extract facility attributes
    df_fac = extract_facility_attributes(client, list(all_facility_ids))
    fac_output = EXPORTS_DIR / "iv_solutions__facility_attributes.csv"
    df_fac.to_csv(fac_output, index=False)
    print(f"  Saved: {fac_output}")
    
    # 5. Extract product master attributes
    #    - NDC-based (for joining RB + most TAE rows)
    #    - Reference-number-based (required for PINs whose Item Master rows have NULL NDC)
    df_pm_by_ndc = extract_product_master_attributes(client, final_rb_ndcs)
    df_pm_by_ref = extract_product_master_attributes_by_reference_numbers(client, ref_nums)
    df_pm = pd.concat([df_pm_by_ndc, df_pm_by_ref], ignore_index=True)
    # De-dupe to keep file size small and avoid confusing downstream merges
    df_pm = df_pm.drop_duplicates()
    pm_output = EXPORTS_DIR / "iv_solutions__product_master_attributes.csv"
    df_pm.to_csv(pm_output, index=False)
    print(f"  Saved: {pm_output}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Extraction Complete")
    print("=" * 60)
    print(f"TAE enriched: {len(df_tae):,} rows")
    print(f"RB enriched: {len(df_rb):,} rows")
    print(f"Facility attributes: {len(df_fac):,} rows ({df_fac['facility_id'].nunique():,} unique facilities)")
    print(f"Product master: {len(df_pm):,} rows")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
