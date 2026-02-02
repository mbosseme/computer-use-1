#!/usr/bin/env python3
"""Check for missing NDCs from Jen's original scope."""

import pandas as pd

# Load files
mapping = pd.read_csv('runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping__verified.csv')
output = pd.read_csv('runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched.csv')

# Get the NDCs from the mapping file (only where matched_ndc_11 is not null)
mapping_clean = mapping[mapping['matched_ndc_11'].notna()].copy()
mapping_clean['ndc11'] = mapping_clean['matched_ndc_11'].astype(str).str.split('.').str[0].str.zfill(11)
scope_ndcs = set(mapping_clean['ndc11'].unique())
print(f"Scope NDCs (from Jen mapping with matched_ndc_11): {len(scope_ndcs)}")

# Get the NDCs in the final output
output_ndcs = set(output['ndc11'].dropna().astype(str).unique())
print(f"Output NDCs: {len(output_ndcs)}")

# Find missing NDCs
missing_ndcs = scope_ndcs - output_ndcs
print(f"\nNDCs in scope but NOT in output: {len(missing_ndcs)}")

if missing_ndcs:
    print("\nMissing NDCs and their details:")
    for ndc in sorted(missing_ndcs):
        row = mapping_clean[mapping_clean['ndc11'] == ndc].iloc[0]
        desc = str(row.get('description', 'N/A'))[:70]
        status = row.get('status', 'N/A')
        ref = row.get('reference_number', 'N/A')
        print(f"  {ndc}: ref={ref}, status={status}")
        print(f"    desc: {desc}...")

# Also check: are there rows in mapping with NO matched_ndc_11?
no_match = mapping[mapping['matched_ndc_11'].isna()]
print(f"\n\nRows in Jen mapping with NO matched_ndc_11: {len(no_match)}")
if len(no_match) > 0:
    print(no_match[['original_ndc', 'reference_number', 'status']].to_string())
