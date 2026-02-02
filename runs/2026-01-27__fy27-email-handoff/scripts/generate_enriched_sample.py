#!/usr/bin/env python3
"""Generate enriched, de-identified IV solutions sample.

Combines enriched TAE and RB (wholesaler) data with:
- Facility attributes (state, zip3)
- Product master attributes (description, manufacturer)
- De-identified facility IDs

Output: Enriched, de-identified sample for external sharing.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# Configuration
RUN_ID = "2026-01-27__fy27-email-handoff"
RUN_DIR = Path(f"runs/{RUN_ID}")
EXPORTS_DIR = RUN_DIR / "exports"

# Input files (from enriched extraction)
TAE_FILE = EXPORTS_DIR / "iv_solutions__tae_enriched.csv"
RB_FILE = EXPORTS_DIR / "iv_solutions__rb_enriched.csv"
FAC_ATTRS_FILE = EXPORTS_DIR / "iv_solutions__facility_attributes.csv"
PM_ATTRS_FILE = EXPORTS_DIR / "iv_solutions__product_master_attributes.csv"
REF_MAP_FILE = EXPORTS_DIR / "jen_ndc_reference_mapping__verified.csv"

# Sample window
SAMPLE_START = "2024-01"
SAMPLE_END = "2025-12"


def create_blinding_map(all_facility_ids):
    """Create consistent blinding map for facility IDs."""
    sorted_ids = sorted(set(str(f) for f in all_facility_ids if pd.notna(f)))
    blinding_map = {}
    for i, fac_id in enumerate(sorted_ids, 1):
        blinding_map[fac_id] = f"FAC_{i:05d}"
    return blinding_map


def load_enriched_tae():
    """Load enriched TAE data."""
    print("Loading enriched TAE data...")
    df = pd.read_csv(TAE_FILE, dtype=str)
    
    # Convert numeric columns
    df['tae_spend'] = pd.to_numeric(df['tae_spend'], errors='coerce')
    
    # Add source flag
    df['source'] = 'ERP'
    
    # Rename for consistency
    # TAE now has ndc11 (proper 11-digit NDC) for PM join
    df = df.rename(columns={
        'tae_spend': 'spend'
        # ndc11 and reference_number are kept as-is
    })
    
    # Filter to sample window
    df = df[(df['month_year'] >= SAMPLE_START) & (df['month_year'] <= SAMPLE_END)]
    print(f"  Loaded {len(df):,} rows (after window filter)")
    print(f"  Total spend: ${df['spend'].sum():,.2f}")
    
    return df


def load_enriched_rb():
    """Load enriched RB data."""
    print("Loading enriched RB data...")
    df = pd.read_csv(RB_FILE, dtype=str)
    
    # Convert numeric columns
    df['rb_spend'] = pd.to_numeric(df['rb_spend'], errors='coerce')
    
    # Add source flag
    df['source'] = 'WHOLESALER'
    
    # Rename for consistency
    df = df.rename(columns={
        'rb_spend': 'spend'
    })
    
    # Filter to sample window
    df = df[(df['month_year'] >= SAMPLE_START) & (df['month_year'] <= SAMPLE_END)]
    print(f"  Loaded {len(df):,} rows (after window filter)")
    
    return df


def load_facility_attributes():
    """Load facility attributes lookup."""
    print("Loading facility attributes...")
    df = pd.read_csv(FAC_ATTRS_FILE, dtype=str)
    print(f"  Loaded {len(df):,} rows")
    return df


def load_product_master():
    """Load product master attributes lookup."""
    print("Loading product master attributes...")
    df = pd.read_csv(PM_ATTRS_FILE, dtype=str)
    print(f"  Loaded {len(df):,} rows")
    return df


def load_ref_map():
    """Load reference mapping for backfilling NDCs."""
    print("\nLoading reference map...")
    df = pd.read_csv(REF_MAP_FILE, dtype=str)
    if 'matched_ndc_11' in df.columns:
        df['matched_ndc_11'] = df['matched_ndc_11'].str.zfill(11)
    # Ensure reference_number is string/stripped
    if 'reference_number' in df.columns:
        df['reference_number'] = df['reference_number'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    return df[['reference_number', 'matched_ndc_11']].drop_duplicates()


def combine_and_enrich(df_tae, df_rb, df_fac, df_pm, blinding_map):
    """Combine TAE and RB with enrichment lookups and de-identification."""
    print("\nCombining and enriching data...")
    
    # Load reference map for validation/backfill
    df_map = load_ref_map()

    # Select columns for combination (keep source-specific columns)
    # Match TAE reference_number to bridge missing NDCs
    tae_cols = ['facility_id', 'month_year', 'ndc11', 'reference_number', 'spend', 'source',
                'vendor_name']
    
    # RB has ndc11 which is 11-digit NDC for PM join
    rb_cols = ['facility_id', 'month_year', 'ndc11', 'spend', 'source',
               'rb_facility_state', 'rb_facility_zip3', 'rb_facility_city', 'rb_vendor_name']
    
    # Subset to available columns
    tae_available = [c for c in tae_cols if c in df_tae.columns]
    rb_available = [c for c in rb_cols if c in df_rb.columns]
    
    df_tae_sub = df_tae[tae_available].copy()
    df_rb_sub = df_rb[rb_available].copy()
    
    # Backfill missing/null ndc11 in TAE using reference_number map
    print("  Backfilling missing TAE NDCs from reference map...")
    if 'reference_number' in df_tae_sub.columns:
        # Ensure join key is clean
        df_tae_sub['reference_number'] = df_tae_sub['reference_number'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
        
        df_tae_sub = df_tae_sub.merge(df_map, on='reference_number', how='left')
        
        # If ndc11 is null or empty, use matched_ndc_11
        df_tae_sub['ndc11'] = df_tae_sub['ndc11'].replace(['nan', 'None', '', 'null', 'NaN'], pd.NA)
        df_tae_sub['ndc11'] = df_tae_sub['ndc11'].fillna(df_tae_sub['matched_ndc_11'])
        
        # Drop temp column
        df_tae_sub = df_tae_sub.drop(columns=['matched_ndc_11'])
    
    # Join TAE/RB to PM via ndc11
    # IMPORTANT: Pandas merge treats NaN keys as equal.
    # We MUST exclude PM rows with ndc11=NULL from the ndc11 join to avoid
    # many-to-many explosions when transactions have missing ndc11.
    df_pm_all = df_pm.copy()
    df_pm_by_ndc = df_pm_all[df_pm_all['ndc11'].notna()].copy() if 'ndc11' in df_pm_all.columns else df_pm_all.copy()

    # Guardrail: ensure PM is unique on ndc11 for joining
    if 'ndc11' in df_pm_by_ndc.columns:
        dup_mask = df_pm_by_ndc['ndc11'].duplicated(keep='first')
        dup_count = int(dup_mask.sum())
        if dup_count:
            print(f"  WARNING: Dropping {dup_count:,} duplicate PM rows by ndc11 to avoid join explosion")
            df_pm_by_ndc = df_pm_by_ndc[~dup_mask].copy()

    df_tae_enriched = df_tae_sub.merge(df_pm_by_ndc, on='ndc11', how='left', suffixes=('', '_pm'))
    print(f"  TAE after PM join: {len(df_tae_enriched):,} rows")

    # Fallback: For TAE rows with missing product metadata, use best available PM record for the same reference_number
    pm_cols = [
        'pm_reference_number', 'pm_brand_name', 'pm_description', 'pm_product_group_category',
        'pm_product_subcategory1', 'pm_product_subcategory2', 'pm_product_subcategory3',
        'pm_contract_category', 'pm_manufacturer_top_parent', 'pm_manufacturer_name',
        'pm_mfr_catalog_num', 'pm_generic_name', 'pm_dosage_form'
    ]
    # Consider both null and empty string as missing
    missing_desc = (df_tae_enriched['pm_description'].isna()) | (df_tae_enriched['pm_description'] == '')
    fallback_candidate_count = int(missing_desc.sum())
    fallback_filled_count = 0
    for idx, row in df_tae_enriched[missing_desc].iterrows():
        ref_num = row.get('reference_number')
        if pd.notna(ref_num) and ref_num != '':
            pm_matches = df_pm_all[df_pm_all['pm_reference_number'] == ref_num]
            if not pm_matches.empty:
                # Pick the best record: prefer non-null/nonnull/filled description, then most recent, then alphabetically first
                best = pm_matches.copy()
                # Rank by completeness (explicit columns; pandas can't sort by raw boolean Series)
                best['__has_desc'] = best['pm_description'].notna() & (best['pm_description'] != '')
                best['__has_brand'] = best['pm_brand_name'].notna() & (best['pm_brand_name'] != '')
                best['__has_group'] = best['pm_product_group_category'].notna() & (best['pm_product_group_category'] != '')
                best = (
                    best.sort_values(
                        by=['__has_desc', '__has_brand', '__has_group'],
                        ascending=[False, False, False],
                    )
                    .drop(columns=['__has_desc', '__has_brand', '__has_group'], errors='ignore')
                    .iloc[0]
                )
                for col in pm_cols:
                    # Always fill if missing or blank
                    if col in df_tae_enriched.columns:
                        if pd.isna(df_tae_enriched.at[idx, col]) or df_tae_enriched.at[idx, col] == '':
                            df_tae_enriched.at[idx, col] = best.get(col, '')
                    else:
                        df_tae_enriched.at[idx, col] = best.get(col, '')

                fallback_filled_count += 1

    if fallback_candidate_count:
        print(f"  Applied reference-number fallback for {fallback_filled_count:,} / {fallback_candidate_count:,} TAE rows missing PM metadata")

    # Join RB to PM via ndc11
    df_rb_enriched = df_rb_sub.merge(df_pm_by_ndc, on='ndc11', how='left')
    print(f"  RB after PM join: {len(df_rb_enriched):,} rows")

    # Add missing columns with nulls for union
    all_cols = set(df_tae_enriched.columns) | set(df_rb_enriched.columns)
    for col in all_cols:
        if col not in df_rb_enriched.columns:
            df_rb_enriched[col] = None
        if col not in df_tae_enriched.columns:
            df_tae_enriched[col] = None

    # Union datasets
    combined = pd.concat([df_tae_enriched, df_rb_enriched], ignore_index=True)
    print(f"  Combined rows: {len(combined):,}")
    print(f"  Combined spend: ${combined['spend'].sum():,.2f}")

    # Join facility attributes
    df_fac_lookup = df_fac.copy()
    combined = combined.merge(df_fac_lookup, on='facility_id', how='left')
    print(f"  After facility join: {len(combined):,} rows")

    # Apply blinding
    print("Applying de-identification...")
    combined['blinded_facility_id'] = combined['facility_id'].astype(str).map(blinding_map)

    # Remove identifying columns
    cols_to_drop = ['facility_id', 'rb_facility_city', 'dhc_idn_parent']
    cols_to_drop = [c for c in cols_to_drop if c in combined.columns]
    combined = combined.drop(columns=cols_to_drop)

    # Consolidate geo columns (prefer Facility attrs over RB)
    # Note: 'facility_state' comes from the broadened lookup (COALESCE(dhc, sa_sf))
    combined['state'] = combined.get('facility_state', combined.get('rb_facility_state'))
    combined['zip3'] = combined.get('facility_zip3', combined.get('rb_facility_zip3'))

    # Consolidate vendor_name (TAE has vendor_name, RB has rb_vendor_name)
    if 'vendor_name' not in combined.columns:
        combined['vendor_name'] = None
    if 'rb_vendor_name' in combined.columns:
        combined['vendor_name'] = combined['vendor_name'].fillna(combined['rb_vendor_name'])

    # Consolidate reference_number for the final external sample:
    # Prefer the Premier Primary Item Master reference number inferred via ndc11 join.
    # This keeps `reference_number` populated for WHOLESALER rows as well.
    if 'pm_reference_number' in combined.columns:
        if 'reference_number' in combined.columns:
            combined['reference_number'] = combined['pm_reference_number'].combine_first(combined['reference_number'])
        else:
            combined['reference_number'] = combined['pm_reference_number']

        combined = combined.drop(columns=['pm_reference_number'])

    # Drop redundant geo and vendor columns
    geo_drop = ['facility_state', 'rb_facility_state', 'facility_zip3', 'rb_facility_zip3', 'rb_vendor_name']
    geo_drop = [c for c in geo_drop if c in combined.columns]
    combined = combined.drop(columns=geo_drop, errors='ignore')

    # Rename PM columns to remove prefix (cleaner for external sharing)
    pm_rename = {
        'pm_brand_name': 'brand_name',
        'pm_description': 'description',
        'pm_product_group_category': 'product_group_category',
        'pm_product_subcategory1': 'product_subcategory1',
        'pm_product_subcategory2': 'product_subcategory2',
        'pm_product_subcategory3': 'product_subcategory3',
        'pm_contract_category': 'contract_category',
        'pm_manufacturer_top_parent': 'manufacturer_top_parent',
        'pm_manufacturer_name': 'manufacturer_name',
        'pm_mfr_catalog_num': 'mfr_catalog_num',
        'pm_generic_name': 'generic_name',
        'pm_dosage_form': 'dosage_form'
    }
    combined = combined.rename(columns=pm_rename)

    # Reorder columns for output
    # Product metadata sourced from PM (canonical), vendor_name is transaction-specific
    priority_cols = [
        'blinded_facility_id', 'month_year', 'ndc11', 'reference_number',
        'spend', 'source',
        'state', 'zip3', 'vendor_name',
        'brand_name', 'description', 'product_group_category',
        'product_subcategory1', 'product_subcategory2', 'product_subcategory3',
        'contract_category', 'manufacturer_top_parent', 'manufacturer_name',
        'mfr_catalog_num', 'generic_name', 'dosage_form'
    ]
    
    # Keep only columns that exist
    output_cols = [c for c in priority_cols if c in combined.columns]
    # Add any remaining columns not in priority list
    remaining = [c for c in combined.columns if c not in output_cols]
    output_cols.extend(remaining)
    
    combined = combined[output_cols]
    
    # Sort for clean output
    combined = combined.sort_values(['blinded_facility_id', 'month_year', 'source', 'ndc11'])
    
    return combined


def generate_coverage_summary(combined):
    """Generate coverage statistics for the enriched sample."""
    
    total_rows = len(combined)
    erp_rows = len(combined[combined['source'] == 'ERP'])
    wholesaler_rows = len(combined[combined['source'] == 'WHOLESALER'])
    
    total_spend = combined['spend'].sum()
    erp_spend = combined[combined['source'] == 'ERP']['spend'].sum()
    wholesaler_spend = combined[combined['source'] == 'WHOLESALER']['spend'].sum()
    
    unique_facilities = combined['blinded_facility_id'].nunique()
    unique_ndcs = combined['ndc11'].nunique()
    
    months_covered = sorted(combined['month_year'].dropna().unique())
    
    # Facilities with both sources
    erp_facilities = set(combined[combined['source'] == 'ERP']['blinded_facility_id'].unique())
    wholesaler_facilities = set(combined[combined['source'] == 'WHOLESALER']['blinded_facility_id'].unique())
    both_sources = erp_facilities & wholesaler_facilities
    
    # Enrichment coverage
    has_state = int(combined['state'].notna().sum()) if 'state' in combined.columns else 0
    has_zip3 = int(combined['zip3'].notna().sum()) if 'zip3' in combined.columns else 0
    has_pm_desc = int(combined['description'].notna().sum()) if 'description' in combined.columns else 0
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "run_id": RUN_ID,
        "sample_window": f"{SAMPLE_START} to {SAMPLE_END}",
        "months_included": len(months_covered),
        "record_counts": {
            "total_rows": total_rows,
            "erp_rows": erp_rows,
            "wholesaler_rows": wholesaler_rows
        },
        "spend": {
            "total": round(total_spend, 2),
            "erp": round(erp_spend, 2),
            "wholesaler": round(wholesaler_spend, 2),
            "erp_pct": round(100 * erp_spend / total_spend, 1) if total_spend > 0 else 0
        },
        "coverage": {
            "unique_facilities": unique_facilities,
            "unique_ndcs": unique_ndcs,
            "facilities_with_erp": len(erp_facilities),
            "facilities_with_wholesaler": len(wholesaler_facilities),
            "facilities_with_both_sources": len(both_sources)
        },
        "enrichment_coverage": {
            "rows_with_state": has_state,
            "rows_with_zip3": has_zip3,
            "rows_with_pm_description": has_pm_desc,
            "pct_with_state": round(100 * has_state / total_rows, 1) if total_rows > 0 else 0,
            "pct_with_pm_description": round(100 * has_pm_desc / total_rows, 1) if total_rows > 0 else 0
        }
    }
    
    return summary


def generate_data_dictionary():
    """Generate data dictionary for the enriched external sample."""

    dictionary = """# IV Solutions Enriched Sample — Data Dictionary

**Generated:** {generated_at}  
**Run ID:** {run_id}  
**Sample Period:** January 2024 – December 2025 (24 months)

## Core Fields

| Column | Description |
|--------|-------------|
| `blinded_facility_id` | De-identified facility identifier (FAC_00001, FAC_00002, ...) |
| `month_year` | Month of transaction (YYYY-MM format) |
| `ndc11` | 11-digit National Drug Code |
| `reference_number` | Premier `reference_number` inferred via the Premier Primary Item Master join on `ndc11` (present for both sources); ERP rows fall back to TAE reference_number if needed |
| `spend` | Total spend in USD |
| `source` | Data source: ERP (Provider direct) or WHOLESALER |

## Facility Attributes (Blinded-Safe)

| Column | Description |
|--------|-------------|
| `state` | State code (2-letter) |
| `zip3` | 3-digit ZIP prefix |

## Transaction-Specific Attributes

| Column | Description |
|--------|-------------|
| `vendor_name` | Distributor/vendor name (from TAE or RB wholesaler field) |

## Product Attributes (from Premier Primary Item Master)

All product metadata is sourced from the Premier Primary Item Master table, joined via `ndc11`.
For records where direct NDC mapping is missing, a reference-number fallback may be applied for ERP rows.

| Column | Description |
|--------|-------------|
| `brand_name` | Product brand name |
| `description` | Full product description |
| `product_group_category` | High-level product category |
| `product_subcategory1` | Product subcategory level 1 |
| `product_subcategory2` | Product subcategory level 2 |
| `product_subcategory3` | Product subcategory level 3 |
| `contract_category` | Premier contract category |
| `manufacturer_top_parent` | Top parent manufacturer name |
| `manufacturer_name` | Direct manufacturer name |
| `mfr_catalog_num` | Manufacturer catalog number |
| `generic_name` | Generic drug name |
| `dosage_form` | Dosage form code |

## Notes

- **De-identification**: Facility identifiers have been blinded. City and IDN affiliation have been removed.
- **Geography**: State and 3-digit ZIP are retained for regional analysis.
- **Source Attribution**: Each row indicates whether it originated from ERP (Provider direct) or WHOLESALER data.
- **Product Metadata**: All product attributes are sourced from the Premier Primary Item Master for consistency across data sources.
- **Vendor Name**: Transaction-specific; sourced from TAE (Vendor_Name) or RB (Wholesaler field).
- **Reference Numbers**:
    - `reference_number`: Premier Primary Item Master `reference_number` inferred via `ndc11` (used to tag both ERP and wholesaler rows consistently)
"""
    return dictionary


def main():
    print("=" * 60)
    print("IV Solutions — Enriched Sample Generation")
    print("=" * 60)
    
    # Load all data
    df_tae = load_enriched_tae()
    df_rb = load_enriched_rb()
    df_fac = load_facility_attributes()
    df_pm = load_product_master()
    
    # Create blinding map
    all_facility_ids = set(df_tae['facility_id'].dropna().unique()) | set(df_rb['facility_id'].dropna().unique())
    blinding_map = create_blinding_map(all_facility_ids)
    print(f"\nBlinding map created for {len(blinding_map):,} facilities")
    
    # Combine and enrich
    combined = combine_and_enrich(df_tae, df_rb, df_fac, df_pm, blinding_map)
    
    # Generate coverage summary
    summary = generate_coverage_summary(combined)
    
    # Save outputs
    output_file = EXPORTS_DIR / "iv_solutions__external_sample_enriched.csv"
    combined.to_csv(output_file, index=False)
    print(f"\nSaved enriched sample: {output_file}")
    print(f"  Rows: {len(combined):,}")
    print(f"  Columns: {len(combined.columns)}")
    print(f"  File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Save summary
    summary_file = EXPORTS_DIR / "iv_solutions__external_sample_enriched_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary: {summary_file}")
    
    # Save data dictionary
    dictionary = generate_data_dictionary()
    dict_file = EXPORTS_DIR / "iv_solutions__external_sample_enriched_dictionary.md"
    with open(dict_file, 'w') as f:
        f.write(dictionary.format(generated_at=summary['generated_at'], run_id=RUN_ID))
    print(f"Saved data dictionary: {dict_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Enriched Sample Summary")
    print("=" * 60)
    print(f"Total rows: {summary['record_counts']['total_rows']:,}")
    print(f"  ERP: {summary['record_counts']['erp_rows']:,}")
    print(f"  Wholesaler: {summary['record_counts']['wholesaler_rows']:,}")
    print(f"\nTotal spend: ${summary['spend']['total']:,.2f}")
    print(f"  ERP: ${summary['spend']['erp']:,.2f} ({summary['spend']['erp_pct']}%)")
    print(f"  Wholesaler: ${summary['spend']['wholesaler']:,.2f}")
    print(f"\nUnique facilities: {summary['coverage']['unique_facilities']:,}")
    print(f"Unique NDCs: {summary['coverage']['unique_ndcs']}")
    print(f"\nEnrichment coverage:")
    print(f"  Rows with state: {summary['enrichment_coverage']['pct_with_state']:.1f}%")
    print(f"  Rows with PM description: {summary['enrichment_coverage']['pct_with_pm_description']:.1f}%")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
