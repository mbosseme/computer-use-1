import json
import csv
import sys
import os

def load_original_ndcs(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    # The file structure is {"ndcs": [...], ...} based on inspection
    if isinstance(data, dict) and "ndcs" in data:
        return set(data["ndcs"])
    elif isinstance(data, list):
        return set(data)
    else:
        # Fallback or error
        print(f"Warning: Unexpected JSON structure in {filepath}")
        return set()

def load_matches(filepath):
    matches = {}
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip(): continue
            record = json.loads(line)
            # Map NDC -> Reference Number
            matches[record['ndc']] = record
    return matches

def normalize_ndc_for_comparison(ndc_11):
    # The originals are 10 digits. The matches are 11 digits.
    # We generated 11 digit variants from 10 digits.
    # To match back, we need to know which original 10-digit NDC generated this 11-digit match.
    # OR, we simply rely on the fact that we have the 11-digit match, and we can try to strip the padding to find the original.
    # BUT, the padding is ambiguous (that's why we generated variants).
    
    # Better approach: 
    # For each original 10-digit NDC, generate its variants again.
    # Check if any of its variants are in the 'matches' map.
    pass

def generate_ndc_variants(ndc_10):
    variants = []
    # 5-4-1 -> 0xxxxx-xxxx-x (Pad first segment) -> index 0
    variants.append("0" + ndc_10)
    
    # 5-3-2 -> xxxxx-0xxx-xx (Pad second segment) -> index 5
    variants.append(ndc_10[:5] + "0" + ndc_10[5:])
    
    # 5-4-1 -> xxxxx-xxxx-0x (Pad third segment - wait, 5-4-1 is 10 digits, usually means pad at pos 0?)
    # Let's stick to the logic used in gen_jen_ndc_search.py
    # Logic was: insert '0' at index 0, 5, and 9.
    variants.append(ndc_10[:9] + "0" + ndc_10[9:])
    
    return variants

def main():
    original_ndcs_path = "/Users/matt_bossemeyer/Projects/wt-2026-01-15__b-braun-pdf-synthesis/runs/2026-01-27__fy27-email-handoff/tmp/re_confirmed_bbraun_mi_demo_virtual__39e24a0260__ndcs.json"
    matches_path = "/Users/matt_bossemeyer/Projects/wt-2026-01-15__b-braun-pdf-synthesis/scripts/jen_ndc_matches.jsonl"
    
    original_ndcs = load_original_ndcs(original_ndcs_path)
    matches_map = load_matches(matches_path)
    
    results = []
    
    found_count = 0
    total_count = len(original_ndcs)
    
    print(f"Total Original NDCs: {total_count}")
    
    for original_ndc in original_ndcs:
        variants = generate_ndc_variants(original_ndc)
        found_match = None
        
        for variant in variants:
            if variant in matches_map:
                found_match = matches_map[variant]
                # If we find a match, we stop looking for this NDC? 
                # Theoretically an NDC could match multiple conventions but in distinct records? 
                # Unlikely to be valid for the same product in the master file, usually one canonical 11-digit NDC exists.
                break 
        
        if found_match:
            found_count += 1
            results.append({
                "original_ndc": original_ndc,
                "matched_ndc_11": found_match['ndc'],
                "reference_number": found_match['reference_number'],
                "description": found_match.get('product_description', ''),
                "manufacturer": found_match.get('manufacturer_name', ''),
                "status": "MATCHED"
            })
        else:
            results.append({
                "original_ndc": original_ndc,
                "matched_ndc_11": None,
                "reference_number": None,
                "description": None,
                "manufacturer": None,
                "status": "NO_MATCH"
            })

    print(f"Found Matches: {found_count}")
    print(f"Match Rate: {found_count/total_count:.2%}")
    
    # Output to CSV for easy reading
    output_path = "/Users/matt_bossemeyer/Projects/wt-2026-01-15__b-braun-pdf-synthesis/runs/2026-01-27__fy27-email-handoff/exports/jen_ndc_reference_mapping.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['original_ndc', 'matched_ndc_11', 'reference_number', 'description', 'manufacturer', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print(f"Results written to: {output_path}")

if __name__ == "__main__":
    main()
