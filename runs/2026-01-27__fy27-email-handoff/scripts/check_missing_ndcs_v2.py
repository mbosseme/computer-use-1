#!/usr/bin/env python3
"""Check for missing NDCs from Jen's original scope - v2 with better debugging."""

import pandas as pd

# Load files
mapping = pd.read_csv('runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping__verified.csv')
output = pd.read_csv('runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__external_sample_enriched.csv')

# Get the NDCs from the mapping file (only where matched_ndc_11 is not null)
mapping_clean = mapping[mapping['matched_ndc_11'].notna()].copy()
mapping_clean['ndc11'] = mapping_clean['matched_ndc_11'].astype(str).str.split('.').str[0].str.zfill(11)
scope_ndcs = set(mapping_clean['ndc11'].unique())

# Get the NDCs in the final output - ensure they're strings and same format
output['ndc11_str'] = output['ndc11'].astype(str).str.split('.').str[0].str.zfill(11)
output_ndcs = set(output['ndc11_str'].unique())

print(f"Scope NDCs (from Jen mapping with matched_ndc_11): {len(scope_ndcs)}")
print(f"Output NDCs: {len(output_ndcs)}")

# Sample of each to compare format
print("\nSample scope NDCs:", sorted(list(scope_ndcs))[:3])
print("Sample output NDCs:", sorted(list(output_ndcs))[:3])

# Find missing NDCs
missing_ndcs = scope_ndcs - output_ndcs
found_ndcs = scope_ndcs & output_ndcs

print(f"\nNDCs in scope AND in output: {len(found_ndcs)}")
print(f"NDCs in scope but NOT in output: {len(missing_ndcs)}")

if missing_ndcs:
    print("\n=== Missing NDCs ===")
    for ndc in sorted(missing_ndcs):
        row = mapping_clean[mapping_clean['ndc11'] == ndc].iloc[0]
        desc = str(row.get('description', 'N/A'))[:60]
        ref = row.get('reference_number', 'N/A')
        print(f"  {ndc}: ref={ref}")
        print(f"    {desc}")

# Also check: are there rows in mapping with NO matched_ndc_11?
no_match = mapping[mapping['matched_ndc_11'].isna()]
print(f"\n\n=== Rows with NO matched_ndc_11 (5 manual matches): {len(no_match)} ===")
for _, row in no_match.iterrows():
    ref = row.get('reference_number', 'N/A')
    status = row.get('status', 'N/A')
    print(f"  original_ndc={row['original_ndc']}, ref={ref}")
    print(f"    status: {status}")
