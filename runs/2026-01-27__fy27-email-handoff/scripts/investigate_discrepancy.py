import pandas as pd
from pathlib import Path

RUN_ID = "2026-01-27__fy27-email-handoff"
CSV_FILE = Path(f"runs/{RUN_ID}/exports/iv_solutions__gap_products.csv")

def investigate():
    if not CSV_FILE.exists():
        print(f"File not found: {CSV_FILE}")
        return

    print("Loading Gap Products CSV...")
    df = pd.read_csv(CSV_FILE)
    
    # 1. Total Spend Breakdown
    total_spend = df['spend'].sum()
    print(f"\nTotal Spend: ${total_spend:,.2f}")
    
    # 2. Spend by Data Source
    print("\n--- Spend by Data Source ---")
    source_stats = df.groupby('data_source')['spend'].agg(['sum', 'count']).reset_index()
    source_stats['sum_formatted'] = source_stats['sum'].apply(lambda x: f"${x:,.2f}")
    print(source_stats)
    
    # 3. Spend by Manufacturer (as listed in the file)
    print("\n--- Spend by Manufacturer (Top Parent) ---")
    mfr_stats = df.groupby('manufacturer_top_parent_name')['spend'].sum().sort_values(ascending=False).reset_index()
    mfr_stats['sum_formatted'] = mfr_stats['spend'].apply(lambda x: f"${x:,.2f}")
    print(mfr_stats.head(10))

    # 4. Top spending Reference Numbers (and their source breakdown)
    print("\n--- Top 5 Spend Reference Numbers ---")
    top_refs = df.groupby('reference_number')['spend'].sum().sort_values(ascending=False).head(5).index.tolist()
    
    for ref in top_refs:
        subset = df[df['reference_number'] == ref]
        ref_spend = subset['spend'].sum()
        mfrs = subset['manufacturer_top_parent_name'].unique()
        ndcs = subset['ndc11'].unique()
        sources = subset.groupby('data_source')['spend'].sum().to_dict()
        desc = subset['item_description'].iloc[0] if not subset.empty else "N/A"
        
        print(f"\nRef: {ref}")
        print(f"  Description: {desc}")
        print(f"  Mfr(s) in File: {mfrs}")
        print(f"  NDCs: {ndcs}")
        print(f"  Total Spend: ${ref_spend:,.2f}")
        print(f"  Breakdown: {sources}")

    # 5. Check if any Reference Numbers in the file map to multiple Manufacturers in PM? 
    # (The file has one mfr column joined from PM via ANY_VALUE, so it won't show variation per row unless I grouped differently, 
    # but let's check if the 'vendor_name' in RB rows gives a clue, mistakenly.)
    
    # Actually, the user questioned the Mfr name. 
    # Let's check rows where data_source is Wholesaler vs Direct.
    
if __name__ == "__main__":
    investigate()
