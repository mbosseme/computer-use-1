import csv
import os

csv_path = 'runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping.csv'
temp_path = csv_path + '.tmp'

# Manual updates based on catalog number research
updates = {
    '6521924110': {'reference_number': '420997418', 'match_method': 'MANUAL_CATALOG_MATCH_310241'},
    '6521924350': {'reference_number': '420997417', 'match_method': 'MANUAL_CATALOG_MATCH_310243'},
    '6521924610': {'reference_number': '420586448', 'match_method': 'MANUAL_CATALOG_MATCH_65219024610'},
}

updated_count = 0
unmatched_count = 0

with open(csv_path, 'r', newline='') as infile, open(temp_path, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        ndc = str(row['original_ndc'])
        if ndc in updates:
            row['reference_number'] = updates[ndc]['reference_number']
            if 'status' in row:
                row['status'] = updates[ndc]['match_method']
            print(f"Updating {ndc} with {updates[ndc]['reference_number']}")
            updated_count += 1
        
        # Check if status is explicitly NO_MATCH to count remaining errors
        if row.get('status') == 'NO_MATCH':
            unmatched_count += 1
            
        writer.writerow(row)

os.replace(temp_path, csv_path)
print(f"Updated {updated_count} rows.")
print(f"Remaining unmatched (status=NO_MATCH): {unmatched_count}")
