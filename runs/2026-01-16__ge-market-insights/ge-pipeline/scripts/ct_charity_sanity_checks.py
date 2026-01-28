#!/usr/bin/env python3
"""ct_charity_sanity_checks.py

Performs targeted BigQuery sanity checks for 0-match Charity terms to rule out
edge naming cases not captured by standard regex patterns.

Terms checked:
- Frontier EX: FRONTIER + (EX|EXTREME) anywhere (GE-gated)
- Frontier EL: FRONTIER + (EL|ELITE) anywhere (GE-gated)
- Optima CT520: OPTIMA + variants (CT520, 520CT, etc)
- CardioGraphe: CARDIOGRAPHE + variants

Outputs:
- snapshots/<RUN_ID>/sanity_check_*.csv (only if rows found)
"""

import argparse
import os
import sys
from pathlib import Path

# Allow importing from src
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.bigquery_client import BigQueryClient

TABLE_FQN = os.getenv(
    "CT_CHARITY_TABLE_FQN",
    "abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded",
)

def run_check(bq, snapshot_dir, check_name, sql, dry_run=False):
    print(f"Running sanity check: {check_name}...")
    if dry_run:
        print(f"[Dry Run] SQL:\n{sql}")
        return

    try:
        # The wrapper exposes the underlying client via .client
        if not bq.client:
            print(f"  ERROR: BigQuery client not initialized.")
            return
            
        df = bq.client.query(sql).to_dataframe()
        if not df.empty:
            out_file = snapshot_dir / f"sanity_check_{check_name}.csv"
            print(f"  FOUND {len(df)} rows! Saving to {out_file}")
            df.to_csv(out_file, index=False)
        else:
            print("  No rows found (Clean).")
    except Exception as e:
        print(f"  ERROR: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-dir", required=True, type=Path)
    parser.add_argument("--start-date", default="2023-10-01")
    parser.add_argument("--end-date", default="2025-09-30")
    args = parser.parse_args()

    bq = BigQueryClient()

    # Base Text Expression (Concatenate ALL identity fields with space separator to allow cross-field "anywhere in row" check)
    # We use space instead of ' | ' to allow flexible regex matching if terms are adjacent across fields (unlikely but possible)
    # or just to treat the whole row as a text blob.
    
    # Using the list of 13+ fields identified earlier
    fields = [
        "Product_Description",
        "Facility_Product_Description",
        "Facility_Manufacturer_Name", 
        "Facility_Vendor_Name",
        "Facility_Manufacturer_Catalog_Num",
        "Facility_Vendor_Catalog_Num",
        "Manufacturer_Name",
        "Manufacturer_Top_Parent_Name",
        "Vendor_Name",
        "Vendor_Top_Parent_Name",
        "Brand_Name",
        "Manufacturer_Catalog_Number",
        # "Vendor_Catalog_Number",  # Not in schema
        "Contracted_Catalog_Number",
        "Current_Contracted_Catalog_Number",
        "Forecasted_Contracted_Catalog_Number",
        "Current_Contracted_Product_Description",
        "Forecasted_Contracted_Product_Description",
        "replaced_by_manufacturer_catalog_number",
        "Noiseless_Catalog_Number"
    ]
    
    # We construct a safe concatenation
    concat_parts = [f"IFNULL(CAST({f} AS STRING), '')" for f in fields]
    full_text_expr = "UPPER(CONCAT(" + ", ' ', ".join(concat_parts) + "))"
    
    # GE Gating (Strict) - reuse logic effectively
    is_ge_expr = r"""
    (
        REGEXP_CONTAINS(UPPER(IFNULL(Manufacturer_Top_Parent_Name,'')), r'(?:\bGENERAL\s+ELECTRIC(?:\s+HEALTHCARE)?\b|\bGE\s+HEALTHCARE\b|\bG\s*\.?\s*E\b|\bGE\b)')
        OR REGEXP_CONTAINS(UPPER(IFNULL(Manufacturer_Name,'')), r'(?:\bGENERAL\s+ELECTRIC(?:\s+HEALTHCARE)?\b|\bGE\s+HEALTHCARE\b|\bG\s*\.?\s*E\b|\bGE\b)')
        OR REGEXP_CONTAINS(UPPER(IFNULL(Facility_Manufacturer_Name,'')), r'(?:\bGENERAL\s+ELECTRIC(?:\s+HEALTHCARE)?\b|\bGE\s+HEALTHCARE\b|\bG\s*\.?\s*E\b|\bGE\b)')
    )
    """

    common_query = f"""
    SELECT
        Transaction_Date,
        Base_Spend,
        Product_Description,
        Facility_Product_Description,
        Manufacturer_Name,
        Manufacturer_Catalog_Number,
        {full_text_expr} as full_row_text
    FROM `{TABLE_FQN}`
    WHERE Transaction_Date BETWEEN '{args.start_date}' AND '{args.end_date}'
      AND {is_ge_expr}
    """

    # 1. Frontier EX
    sql_ex = f"""
    {common_query}
    AND REGEXP_CONTAINS({full_text_expr}, r'FRONTIER')
    AND REGEXP_CONTAINS({full_text_expr}, r'\\b(EX|EXTREME)\\b')
    LIMIT 25
    """
    run_check(bq, args.snapshot_dir, "frontier_ex", sql_ex)

    # 2. Frontier EL
    sql_el = f"""
    {common_query}
    AND REGEXP_CONTAINS({full_text_expr}, r'FRONTIER')
    AND REGEXP_CONTAINS({full_text_expr}, r'\\b(EL|ELITE)\\b')
    LIMIT 25
    """
    run_check(bq, args.snapshot_dir, "frontier_el", sql_el)

    # 3. Optima CT520 variants
    # Variants: CT520, CT 520, CT-520, 520CT, 520 CT
    sql_optima = f"""
    {common_query}
    AND REGEXP_CONTAINS({full_text_expr}, r'OPTIMA')
    AND REGEXP_CONTAINS({full_text_expr}, r'(CT\\s*-?520|520\\s*-?CT)')
    LIMIT 25
    """
    run_check(bq, args.snapshot_dir, "optima_ct520", sql_optima)

    # 4. CardioGraphe variants
    # Spacing/hyphen variants
    sql_cardio = f"""
    {common_query}
    AND REGEXP_CONTAINS({full_text_expr}, r'CARDIO\\s*[\-]?\\s*GRAPHE')
    LIMIT 25
    """
    run_check(bq, args.snapshot_dir, "cardiographe", sql_cardio)

if __name__ == "__main__":
    main()
