#!/usr/bin/env python3
"""Debug the TAE reference_number vs PM pm_reference_number join."""

import pandas as pd

tae = pd.read_csv('runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__tae_enriched.csv', dtype=str)
pm = pd.read_csv('runs/2026-01-27__fy27-email-handoff/exports/iv_solutions__product_master_attributes.csv', dtype=str)

print('=== TAE reference_number sample ===')
print(tae['reference_number'].head(10).tolist())
print()
print('=== PM pm_reference_number sample ===')
print(pm['pm_reference_number'].head(10).tolist())
print()
print('TAE unique refs:', tae['reference_number'].nunique())
print('PM unique refs:', pm['pm_reference_number'].nunique())
print()

# Check overlap
tae_refs = set(tae['reference_number'].unique())
pm_refs = set(pm['pm_reference_number'].unique())
print('Overlap:', len(tae_refs & pm_refs))
print()

# Show some examples from each
print('TAE sample refs (sorted):', sorted(list(tae_refs))[:5])
print('PM sample refs (sorted):', sorted(list(pm_refs))[:5])
