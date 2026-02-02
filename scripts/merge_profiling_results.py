import json

def merge_results():
    all_results = []
    
    # Load original results
    try:
        with open('scripts/profiling_results.json', 'r') as f:
            original = json.load(f)
            # Ensure it is a list
            if isinstance(original, list):
                all_results.extend(original)
            else:
                print("Warning: original profiling_results.json is not a list")
    except Exception as e:
        print(f"Error loading original results: {e}")

    # Load new results (line-delimited JSON)
    try:
        with open('scripts/missing_cols_results.json', 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        obj = json.loads(line)
                        all_results.append(obj)
                    except json.JSONDecodeError as e:
                         print(f"Error decoding line: {line[:50]}... {e}")
    except Exception as e:
        print(f"Error loading new results: {e}")
    
    # Verify uniqueness (optional, but good for sanity)
    seen_cols = set()
    unique_results = []
    for row in all_results:
        if row['col_name'] not in seen_cols:
            seen_cols.add(row['col_name'])
            unique_results.append(row)
        else:
            print(f"Duplicate column found and skipped: {row['col_name']}")

    print(f"Total columns: {len(unique_results)}")
    
    # Write complete results
    with open('scripts/profiling_results_complete.json', 'w') as f:
        json.dump(unique_results, f, indent=2)
    
    print("Complete results saved to scripts/profiling_results_complete.json")

if __name__ == "__main__":
    merge_results()
