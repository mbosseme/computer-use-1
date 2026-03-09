import pandas as pd
import json

def generate_evidence_bundle(file_path):
    print(f"Loading '{file_path}'...")
    
    # Load sheets
    df_prog = pd.read_excel(file_path, sheet_name='Tab A - Program Summary')
    df_cont = pd.read_excel(file_path, sheet_name='Tab B - Contract Summary')
    df_item = pd.read_excel(file_path, sheet_name='Tab C - Item Drilldown')
    
    bundle = {}
    
    # --- 1. RECONCILIATION CHECK ---
    total_spend_item = df_item['Total_Spend_6mo'].sum()
    total_spend_cont = df_cont['Contract_Total_Spend'].sum()
    total_spend_prog = df_prog['Total_Spend'].sum() if 'Total_Spend' in df_prog.columns else None
    
    bundle['reconciliation'] = {
        'total_spend_item_drilldown': float(total_spend_item),
        'total_spend_contract_summary': float(total_spend_cont),
        'total_spend_program_summary': float(total_spend_prog) if total_spend_prog else None,
        'item_vs_contract_diff': float(total_spend_item - total_spend_cont)
    }
    
    # --- 2. BENCHMARK MISSING / $0 CHECK ---
    benchmarked_items = df_item[df_item['is_benchmarked'] == 1]
    missing_bench_items = benchmarked_items[
        (benchmarked_items['Benchmark_Unit_Price_50th'].isnull()) | 
        (benchmarked_items['Benchmark_Unit_Price_50th'] == 0)
    ]
    
    bundle['benchmark_integrity'] = {
        'total_benchmarked_rows': int(len(benchmarked_items)),
        'rows_missing_or_zero_benchmark': int(len(missing_bench_items)),
        'spend_with_missing_benchmark': float(missing_bench_items['Total_Spend_6mo'].sum())
    }
    
    # --- 3. EXTREME UOM / VARIANCE CHECK ---
    uom_outliers = df_item[df_item['UOM_Outlier_Flag'] == 1]
    
    bundle['uom_outliers'] = {
        'total_uom_outlier_rows': int(len(uom_outliers)),
        'spend_with_uom_outliers': float(uom_outliers['Total_Spend_6mo'].sum()),
        'pct_spend_flagged_as_uom': float(uom_outliers['Total_Spend_6mo'].sum() / total_spend_item) if total_spend_item > 0 else 0
    }
    
    # --- 4. IMPLAUSIBLE SAVINGS (CONTRACT LEVEL) ---
    df_cont['Median_Savings'] = df_cont['Spend_at_Best_Tier'] - df_cont['Target_Spend_50th']
    df_cont['Savings_Pct'] = df_cont['Median_Savings'] / df_cont['Spend_at_Best_Tier']
    
    implausible_contracts = df_cont[df_cont['Savings_Pct'] > 0.5]
    implausible_list = []
    
    for _, row in implausible_contracts.nlargest(10, 'Median_Savings').iterrows():
        implausible_list.append({
            'contract_number': row['Contract_Number'],
            'total_spend': float(row['Contract_Total_Spend']),
            'spend_at_best_tier': float(row['Spend_at_Best_Tier']),
            'target_spend_50th': float(row['Target_Spend_50th']),
            'savings_pct': float(row['Savings_Pct'])
        })
        
    bundle['implausible_savings_contracts_gt_50pct'] = {
        'count_implausible_contracts': int(len(implausible_contracts)),
        'total_implausible_spend': float(implausible_contracts['Contract_Total_Spend'].sum()),
        'top_offenders': implausible_list
    }
    
    # --- 5. OVERALL SHAPE ---
    bundle['overall_shape'] = {
        'total_contracts': int(len(df_cont)),
        'total_items': int(len(df_item)),
        'total_spend_at_best_tier': float(df_cont['Spend_at_Best_Tier'].sum()),
        'total_target_spend_50th': float(df_cont['Target_Spend_50th'].sum())
    }
    
    with open('scripts/sniff_test_bundle.json', 'w') as f:
        json.dump(bundle, f, indent=2)
        
    print("Bundle created at 'scripts/sniff_test_bundle.json'")
    return bundle

if __name__ == "__main__":
    generate_evidence_bundle('runs/2026-03-04__portfolio-competitiveness/HCIQ_Benchmark_Analysis_Deliverable.xlsx')