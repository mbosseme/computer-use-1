import pandas as pd
import re
import sys
import os
import numpy as np

# Paths (using relative paths from workspace root which is Cwd)
JEN_FILE = "runs/2026-01-15__b-braun-pdf-synthesis/exports/jen_sku_list.csv"
MAPPING_FILE = "runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping__verified.csv"
PREMIER_ATTRS_FILE = "runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__product_master_attributes.csv"
OUTPUT_REPORT = "runs/2026-01-27__fy27-email-handoff/exports/semantic_validation_report.csv"

def clean_ndc(ndc_str):
    if pd.isna(ndc_str):
        return ""
    # Remove non-digits
    return re.sub(r'\D', '', str(ndc_str))

def main():
    print("Loading data...")
    try:
        df_jen = pd.read_csv(JEN_FILE)
        df_map = pd.read_csv(MAPPING_FILE, dtype={'original_ndc': str, 'matched_ndc_11': str, 'reference_number': str})
        df_premier = pd.read_csv(PREMIER_ATTRS_FILE, dtype={'ndc11': str, 'pm_reference_number': str})
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    print("files loaded.")

    # 1. Clean Jen's NDC
    print("Cleaning NDCs...")
    df_jen['clean_ndc'] = df_jen['ndc'].apply(clean_ndc)
    df_map['clean_ndc'] = df_map['original_ndc'].apply(clean_ndc) 

    # 2. Join Jen -> Mapping
    print("Joining Jen's list to Mapping...")
    df_merged = pd.merge(df_jen, df_map, on='clean_ndc', how='left', suffixes=('_jen', '_map'))
    
    # Clean matched_ndc_11 to be proper NaN if empty/missing
    # This prevents joining on empty strings -> empty strings
    df_merged['matched_ndc_11'] = df_merged['matched_ndc_11'].replace(r'^\s*$', np.nan, regex=True)
    df_premier['ndc11'] = df_premier['ndc11'].replace(r'^\s*$', np.nan, regex=True)

    # 3. Join -> Premier Attributes
    print("Joining to Premier Attributes...")
    # Join on matched_ndc_11 -> ndc11
    # Pandas merge with how='left' and NaN keys keeps the left row but puts NaN in right cols
    # It does NOT join NaN to NaN.
    df_final = pd.merge(df_merged, df_premier, left_on='matched_ndc_11', right_on='ndc11', how='left')
    
    # 4. Select Columns for Report
    report_cols_map = {
        'ndc': 'Jen_Original_NDC',
        'clean_ndc': 'Clean_NDC',
        'matched_ndc_11': 'Matched_NDC_11',
        'status': 'Status',
        'description_jen': 'Jen_Description',
        'pm_description': 'Premier_Description',
        'volume': 'Jen_Volume',
        'pm_product_subcategory2': 'Premier_Volume_Inferred',
        'solution_type': 'Jen_SolutionType',
        'pm_product_subcategory1': 'Premier_Type_Inferred',
        'reference_number': 'Map_RefNum',
        'pm_reference_number': 'Premier_RefNum'
    }
    
    available_cols = [c for c in report_cols_map.keys() if c in df_final.columns]
    report_df = df_final[available_cols].copy()
    report_df.rename(columns=report_cols_map, inplace=True)
    
    # Save
    print(f"Saving report to {OUTPUT_REPORT}...")
    report_df.to_csv(OUTPUT_REPORT, index=False)
    
    # Display Preview
    print("\n--- Semantic Validation Preview (First 10 matched rows) ---")
    if 'Status' in report_df.columns:
        matched_only = report_df[report_df['Status'] == 'MATCHED'].head(10)
    else:
        matched_only = report_df.head(10)
    
    for idx, row in matched_only.iterrows():
        print(f"\nRow {idx}: {row.get('Jen_Original_NDC', 'N/A')}")
        print(f"  Vol:  '{row.get('Jen_Volume', 'N/A')}' vs '{row.get('Premier_Volume_Inferred', 'N/A')}'")
        print(f"  Type: '{row.get('Jen_SolutionType', 'N/A')}' vs '{row.get('Premier_Type_Inferred', 'N/A')}'")
        print(f"  Desc: '{row.get('Jen_Description', 'N/A')}'")
        print(f"        '{row.get('Premier_Description', 'N/A')}'")

    print("\n--- Summary ---")
    print(f"Total Jen Rows: {len(df_jen)}")
    print(f"Matched Rows: {len(report_df[report_df['Status'] == 'MATCHED']) if 'Status' in report_df.columns else 'Unknown'}")
    print(f"Report location: {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
