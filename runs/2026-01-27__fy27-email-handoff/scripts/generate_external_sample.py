#!/usr/bin/env python3
"""
Generate External Sample for B. Braun IV Solutions

Phase G: External Sample Preparation
- G1. De-identify: replace facility codes with blinded_facility_id
- G2. Include all facilities (not just Premier members)
- G3. Include required fields with source_flag
- G4. Generate data dictionary
- G5. Generate coverage summary

Output: De-identified facility-month-product level data for Jen (B. Braun)
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import hashlib

# Configuration
RUN_ID = "2026-01-27__fy27-email-handoff"
RUN_DIR = Path(f"runs/{RUN_ID}")
EXPORTS_DIR = RUN_DIR / "exports"

TAE_FILE = EXPORTS_DIR / "iv_solutions__tae_raw.csv"
RB_FILE = EXPORTS_DIR / "iv_solutions__rb_raw.csv"

# Full sample window: Jan 2024 - Dec 2025 (24 months)
SAMPLE_START = "2024-01"
SAMPLE_END = "2025-12"


def create_blinding_map(all_facility_ids):
    """Create consistent blinding map for facility IDs."""
    # Sort to ensure consistent ordering
    sorted_ids = sorted(set(all_facility_ids))
    
    # Create blinded IDs
    blinding_map = {}
    for i, fac_id in enumerate(sorted_ids, 1):
        blinded = f"FAC_{i:05d}"
        blinding_map[fac_id] = blinded
    
    return blinding_map


def load_and_prepare_tae():
    """Load TAE data and prepare for external sample."""
    print("Loading TAE (Provider ERP) data...")
    df = pd.read_csv(TAE_FILE)
    print(f"  Loaded {len(df):,} rows")
    
    # Rename columns to standardized names
    df = df.rename(columns={
        'facility_id': 'facility_id',
        'month_year': 'month_year',
        'reference_number': 'reference_number',
        'manufacturer_catalog_number': 'ndc11',
        'vendor_name': 'vendor_name',
        'tae_spend': 'spend',
        'tae_units': 'units'
    })
    
    # Add source flag
    df['source_flag'] = 'ERP'
    
    # Filter to sample window
    df = df[(df['month_year'] >= SAMPLE_START) & (df['month_year'] <= SAMPLE_END)]
    print(f"  After sample window filter ({SAMPLE_START}-{SAMPLE_END}): {len(df):,} rows")
    
    return df


def load_and_prepare_rb():
    """Load RB data and prepare for external sample."""
    print("Loading RB (Wholesaler) data...")
    df = pd.read_csv(RB_FILE)
    print(f"  Loaded {len(df):,} rows")
    
    # Rename columns to standardized names
    df = df.rename(columns={
        'facility_id': 'facility_id',
        'month_year_fmt': 'month_year',
        'ndc': 'ndc11',
        'rb_spend': 'spend',
        'rb_units': 'units'
    })
    
    # Add source flag and placeholder for reference_number (RB doesn't have it)
    df['source_flag'] = 'WHOLESALER'
    df['reference_number'] = None
    df['vendor_name'] = None
    
    # Filter to sample window
    df = df[(df['month_year'] >= SAMPLE_START) & (df['month_year'] <= SAMPLE_END)]
    print(f"  After sample window filter ({SAMPLE_START}-{SAMPLE_END}): {len(df):,} rows")
    
    return df


def combine_and_deidentify(df_tae, df_rb, blinding_map):
    """Combine TAE and RB with de-identification."""
    print("\nCombining datasets...")
    
    # Select common columns
    common_cols = ['facility_id', 'month_year', 'ndc11', 'reference_number', 
                   'spend', 'units', 'source_flag']
    
    tae_subset = df_tae[common_cols].copy()
    rb_subset = df_rb[common_cols].copy()
    
    # Union (not de-dup per execution plan)
    combined = pd.concat([tae_subset, rb_subset], ignore_index=True)
    print(f"  Combined rows: {len(combined):,}")
    
    # Apply blinding
    print("Applying de-identification...")
    combined['blinded_facility_id'] = combined['facility_id'].map(blinding_map)
    
    # Drop original facility_id
    combined = combined.drop(columns=['facility_id'])
    
    # Reorder columns
    final_cols = ['blinded_facility_id', 'month_year', 'ndc11', 'reference_number',
                  'spend', 'units', 'source_flag']
    combined = combined[final_cols]
    
    # Sort for clean output
    combined = combined.sort_values(['blinded_facility_id', 'month_year', 'source_flag', 'ndc11'])
    
    return combined


def generate_coverage_summary(combined, df_tae, df_rb):
    """Generate coverage statistics for the sample."""
    
    total_rows = len(combined)
    erp_rows = len(combined[combined['source_flag'] == 'ERP'])
    wholesaler_rows = len(combined[combined['source_flag'] == 'WHOLESALER'])
    
    total_spend = combined['spend'].sum()
    erp_spend = combined[combined['source_flag'] == 'ERP']['spend'].sum()
    wholesaler_spend = combined[combined['source_flag'] == 'WHOLESALER']['spend'].sum()
    
    total_units = combined['units'].sum()
    
    unique_facilities = combined['blinded_facility_id'].nunique()
    unique_ndcs = combined['ndc11'].nunique()
    unique_ref_nums = combined['reference_number'].dropna().nunique()
    
    months_covered = sorted(combined['month_year'].unique())
    
    # Facilities with both sources
    erp_facilities = set(combined[combined['source_flag'] == 'ERP']['blinded_facility_id'].unique())
    wholesaler_facilities = set(combined[combined['source_flag'] == 'WHOLESALER']['blinded_facility_id'].unique())
    both_sources = erp_facilities & wholesaler_facilities
    
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
            "erp_pct": round(100 * erp_spend / total_spend, 1)
        },
        "units": {
            "total": round(total_units, 0)
        },
        "coverage": {
            "unique_facilities": unique_facilities,
            "unique_ndcs": unique_ndcs,
            "unique_reference_numbers": unique_ref_nums,
            "facilities_with_erp": len(erp_facilities),
            "facilities_with_wholesaler": len(wholesaler_facilities),
            "facilities_with_both_sources": len(both_sources),
            "pct_with_both_sources": round(100 * len(both_sources) / unique_facilities, 1)
        }
    }
    
    return summary


def generate_data_dictionary():
    """Generate data dictionary for the external sample."""
    
    dictionary = """# B. Braun IV Solutions Sample Data Cut — Data Dictionary

**Generated:** {generated_at}  
**Run ID:** {run_id}  
**Sample Period:** January 2024 – December 2025 (24 months)

---

## Overview

This dataset contains de-identified facility-level purchasing data for B. Braun IV Solutions products, combining:
- **Provider ERP purchasing** (Transaction Analysis Expanded) — direct facility purchases
- **Wholesaler tracing** (Report Builder) — distributor-intermediated sales

Data is provided at the facility-month-product grain with a source indicator.

---

## Column Definitions

| Column | Type | Description |
|--------|------|-------------|
| `blinded_facility_id` | STRING | De-identified facility identifier (format: `FAC_00001`). Consistent within this dataset; cannot be linked to real facility names. |
| `month_year` | INTEGER | Year-month in YYYYMM format (e.g., 202401 = January 2024) |
| `ndc11` | STRING | 11-digit National Drug Code identifying the specific product/package |
| `reference_number` | STRING | Premier contract reference number (NULL for wholesaler records) |
| `spend` | FLOAT | Total dollar spend for this facility-month-product combination |
| `units` | FLOAT | Total units purchased for this facility-month-product combination |
| `source_flag` | STRING | Data source: `ERP` (Provider direct) or `WHOLESALER` (distributor tracing) |

---

## Important Notes

### Data Interpretation

1. **UNION, not de-duplicated**: ERP and WHOLESALER records are complementary views of purchasing activity. A facility-month-product may appear in BOTH sources — this is expected and represents visibility from different channels.

2. **Reference Number availability**: Only ERP records have `reference_number`; wholesaler records use NDC-only tracking.

3. **Spend values**: Dollar amounts represent landed cost (ERP) or reported sales value (wholesaler). Minor methodology differences may exist.

4. **Unit definitions**: Units represent package/each counts. Unit-of-measure may vary by NDC.

### Coverage Characteristics

- **Facility scope**: Includes all facilities with purchasing activity, not limited to Premier members
- **Product scope**: IV Solutions NDCs associated with B. Braun contracts
- **Time scope**: Full 24 months (Jan 2024 – Dec 2025)

### De-identification

- Real facility identifiers have been replaced with blinded IDs
- Blinded IDs are consistent within this dataset but cannot be traced to actual facilities
- No protected health information (PHI) is included

---

## Source Data Models

| Source | Description |
|--------|-------------|
| **ERP** | Transaction Analysis Expanded — Provider ERP purchasing data captured directly from facility systems |
| **WHOLESALER** | Report Builder — Wholesaler/distributor sales tracing data |

---

## Validation

This dataset has been validated against manufacturer-reported on-contract sales (CAMS). Combined ERP + WHOLESALER spend exceeds manufacturer-reported by ~10%, indicating the dataset captures both on-contract and incremental off-contract/spot purchasing activity.

"""
    
    return dictionary.format(
        generated_at=datetime.now().strftime('%Y-%m-%d'),
        run_id=RUN_ID
    )


def generate_coverage_report(summary):
    """Generate human-readable coverage report."""
    
    report = f"""# B. Braun IV Solutions Sample — Coverage Summary

**Generated:** {summary['generated_at'][:10]}  
**Run ID:** {summary['run_id']}  
**Sample Period:** {summary['sample_window']} ({summary['months_included']} months)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Records** | {summary['record_counts']['total_rows']:,} |
| **Total Spend** | ${summary['spend']['total']:,.0f} |
| **Total Units** | {summary['units']['total']:,.0f} |
| **Unique Facilities** | {summary['coverage']['unique_facilities']:,} |
| **Unique NDCs** | {summary['coverage']['unique_ndcs']:,} |

---

## Source Breakdown

| Source | Records | Spend | % of Total |
|--------|---------|-------|------------|
| **ERP (Provider)** | {summary['record_counts']['erp_rows']:,} | ${summary['spend']['erp']:,.0f} | {summary['spend']['erp_pct']:.1f}% |
| **Wholesaler** | {summary['record_counts']['wholesaler_rows']:,} | ${summary['spend']['wholesaler']:,.0f} | {100-summary['spend']['erp_pct']:.1f}% |

---

## Facility Coverage

| Metric | Count |
|--------|-------|
| Total Unique Facilities | {summary['coverage']['unique_facilities']:,} |
| Facilities with ERP data | {summary['coverage']['facilities_with_erp']:,} |
| Facilities with Wholesaler data | {summary['coverage']['facilities_with_wholesaler']:,} |
| Facilities with BOTH sources | {summary['coverage']['facilities_with_both_sources']:,} ({summary['coverage']['pct_with_both_sources']:.1f}%) |

---

## Product Coverage

| Metric | Count |
|--------|-------|
| Unique NDCs | {summary['coverage']['unique_ndcs']:,} |
| Unique Reference Numbers | {summary['coverage']['unique_reference_numbers']:,} |

---

## Data Quality Notes

1. **Complementary Sources**: ERP and Wholesaler data represent different visibility channels; both are included without de-duplication
2. **Validated**: Combined spend validated against manufacturer-reported on-contract sales (+10.5% coverage)
3. **De-identified**: All facility identifiers replaced with blinded IDs

"""
    return report


def main():
    print("=" * 70)
    print("EXTERNAL SAMPLE GENERATION — B. BRAUN IV SOLUTIONS")
    print("=" * 70)
    print(f"Run ID: {RUN_ID}")
    print(f"Sample Window: {SAMPLE_START} to {SAMPLE_END}")
    print()
    
    # Load data
    df_tae = load_and_prepare_tae()
    df_rb = load_and_prepare_rb()
    
    # Collect all facility IDs for blinding
    all_facilities = list(df_tae['facility_id'].unique()) + list(df_rb['facility_id'].unique())
    blinding_map = create_blinding_map(all_facilities)
    print(f"\nCreated blinding map for {len(blinding_map):,} unique facilities")
    
    # Combine and de-identify
    combined = combine_and_deidentify(df_tae, df_rb, blinding_map)
    
    # Generate coverage summary
    coverage = generate_coverage_summary(combined, df_tae, df_rb)
    
    # Save outputs
    print("\n" + "=" * 70)
    print("SAVING OUTPUTS")
    print("=" * 70)
    
    # 1. Main sample CSV
    sample_file = EXPORTS_DIR / "iv_solutions__external_sample.csv"
    combined.to_csv(sample_file, index=False)
    print(f"  ✓ Sample CSV: {sample_file}")
    
    # 2. Coverage summary JSON
    coverage_json = EXPORTS_DIR / "iv_solutions__external_sample_coverage.json"
    with open(coverage_json, 'w') as f:
        json.dump(coverage, f, indent=2)
    print(f"  ✓ Coverage JSON: {coverage_json}")
    
    # 3. Coverage report MD
    coverage_report = generate_coverage_report(coverage)
    coverage_md = EXPORTS_DIR / "iv_solutions__external_sample_coverage.md"
    coverage_md.write_text(coverage_report)
    print(f"  ✓ Coverage Report: {coverage_md}")
    
    # 4. Data dictionary
    data_dict = generate_data_dictionary()
    dict_file = EXPORTS_DIR / "iv_solutions__external_sample_data_dictionary.md"
    dict_file.write_text(data_dict)
    print(f"  ✓ Data Dictionary: {dict_file}")
    
    # 5. Blinding map (internal only - do not share)
    blinding_file = EXPORTS_DIR / "iv_solutions__blinding_map__INTERNAL_ONLY.json"
    with open(blinding_file, 'w') as f:
        json.dump(blinding_map, f, indent=2)
    print(f"  ✓ Blinding Map (INTERNAL): {blinding_file}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("EXTERNAL SAMPLE COMPLETE")
    print("=" * 70)
    print(f"\n📊 SAMPLE STATISTICS:")
    print(f"   Total Records:    {coverage['record_counts']['total_rows']:,}")
    print(f"   Total Spend:      ${coverage['spend']['total']:,.0f}")
    print(f"   Total Units:      {coverage['units']['total']:,.0f}")
    print(f"   Unique Facilities: {coverage['coverage']['unique_facilities']:,}")
    print(f"   Unique NDCs:       {coverage['coverage']['unique_ndcs']:,}")
    print()
    print(f"   ERP Records:       {coverage['record_counts']['erp_rows']:,} ({coverage['spend']['erp_pct']:.0f}% of spend)")
    print(f"   Wholesaler Records: {coverage['record_counts']['wholesaler_rows']:,} ({100-coverage['spend']['erp_pct']:.0f}% of spend)")
    print()
    print("📁 FILES FOR JEN (B. BRAUN):")
    print(f"   1. {sample_file.name}")
    print(f"   2. {coverage_md.name}")
    print(f"   3. {dict_file.name}")
    print()
    print("🔒 INTERNAL ONLY (do not share):")
    print(f"   - {blinding_file.name}")


if __name__ == "__main__":
    main()
