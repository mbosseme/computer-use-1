import pandas as pd
import os

csv_path = 'runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping.csv'

# Load the CSV
df = pd.read_csv(csv_path)

# Manual updates based on catalog number research
updates = {
    '6521924110': {'reference_number': '420997418', 'match_method': 'MANUAL_CATALOG_MATCH_310241'},
    '6521924350': {'reference_number': '420997417', 'match_method': 'MANUAL_CATALOG_MATCH_310243'},
    '6521924610': {'reference_number': '420586448', 'match_method': 'MANUAL_CATALOG_MATCH_65219024610'}
}

# Apply updates
for ndc, info in updates.items():
    mask = df['original_ndc'] == int(ndc)
    if not mask.any():
        # Maybe it's string?
        mask = df['original_ndc'].astype(str) == str(ndc)
    
    if mask.any():
        print(f"Updating {ndc} with {info['reference_number']}")
        df.loc[mask, 'reference_number'] = info['reference_number']
        df.loc[mask, 'match_method'] = info['match_method']
    else:
        print(f"Warning: NDC {ndc} not found in CSV")

# For the remaining unmatched, add notes if possible? 
# The CSV structure is simple, let's just leave them as NO_MATCH but maybe print them out.
unmatched = df[df['reference_number'] == 'NO_MATCH']
print(f"\nRemaining Unmatched NDCs: {len(unmatched)}")
print(unmatched)

# Save
df.to_csv(csv_path, index=False)
print(f"\nUpdated CSV saved to {csv_path}")
