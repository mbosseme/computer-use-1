import json
import itertools

def generate_11_digit_candidates(ndc10):
    """
    Generates potential 11-digit NDCs from a 10-digit string
    by inserting a zero at the standard 3 positions.
    """
    if len(ndc10) != 10:
        return [ndc10] # Return as is if not 10 digits (sanity check)
    
    candidates = []
    # Case 1: 5-4-1 -> 05-4-1 (Insert at index 0)
    # Actually, standard conversion:
    # 4-4-2 --> 0xxxx-xxxx-xx (Labeler padding)
    # 5-3-2 --> xxxxx-0xxx-xx (Product padding)
    # 5-4-1 --> xxxxx-xxxx-0x (Package padding)
    
    # 1. Pad Labeler (Index 0)
    c1 = "0" + ndc10
    candidates.append(c1)
    
    # 2. Pad Product (Index 5) - i.e. after 5 digits
    c2 = ndc10[:5] + "0" + ndc10[5:]
    candidates.append(c2)
    
    # 3. Pad Package (Index 9) - i.e. after 9 digits (before last one) - wait.
    # 5-4-1 means the last segment is 1 char. Padding it makes it 2 chars.
    # So we insert before the last char: index 9.
    c3 = ndc10[:9] + "0" + ndc10[9:]
    candidates.append(c3)
    
    return list(set(candidates))

def main():
    json_path = "runs/2026-01-27__fy27-email-handoff/tmp/re_confirmed_bbraun_mi_demo_virtual__39e24a0260__ndcs.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    ndcs = data['ndcs']
    print(f"Loaded {len(ndcs)} NDCs.")
    
    ndc_map = {}
    all_candidates = set()
    
    for n in ndcs:
        cands = generate_11_digit_candidates(str(n))
        cands.append(str(n)) # Also check exact 10-digit match
        
        # Also check with hyphens? 
        # The DB profile showed no hyphens in top values, but maybe they exist?
        # Let's stick to clean numbers first.
        
        ndc_map[str(n)] = cands
        for c in cands:
            all_candidates.add(c)
            
    # Generate SQL
    candidates_list = list(all_candidates)
    quoted_candidates = [f"'{c}'" for c in candidates_list]
    
    # Chunking query because list might be large (71 * 4 = ~280 items). fits in one query.
    
    in_clause = ", ".join(quoted_candidates)
    
    sql = f"""
    SELECT 
        ndc, 
        reference_number, 
        product_description,
        manufacturer_name
    FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
    WHERE ndc IN ({in_clause})
    """
    
    with open('scripts/find_jen_ndc_matches.sql', 'w') as f:
        f.write(sql)
        
    print(f"SQL generated with {len(candidates_list)} potential NDCs to look for.")
    
    # Also save the map to verify later
    with open('scripts/jen_ndc_map.json', 'w') as f:
        json.dump(ndc_map, f, indent=2)

if __name__ == "__main__":
    main()
