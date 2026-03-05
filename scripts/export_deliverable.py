import pandas as pd
from google.cloud import bigquery
import os

print("Connecting to BigQuery...")
client = bigquery.Client()

def extract_to_excel(project_id, dataset_id, run_id):
    print("Exporting data to Excel...")
    
    output_dir = f"runs/{run_id}/"
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "HCIQ_Benchmark_Analysis_Deliverable.xlsx")

    # Tab A: Contract-level Summary
    tab_a_query = f"""
    SELECT 
        Portfolio,
        Contract_Number,
        Contract_Name,
        Contract_Total_Spend,
        Contract_Total_Units,
        Benchmark_Coverage_Pct,
        Spend_at_Best_Tier,
        Target_Spend_P10,
        Target_Spend_P25,
        Target_Spend_P50,
        Target_Spend_High,
        Percentile_Bucket,
        Estimated_Percentile_Linear,
        Flag_Coverage,
        Flag_Ambiguity,
        sample_tier_description
    FROM `{project_id}.{dataset_id}.contract_benchmark_summary`
    ORDER BY Portfolio, Contract_Number
    """
    
    # Tab B: Contract-product Drilldown
    tab_b_query = f"""
    SELECT 
        Portfolio_Prefix,
        Contract_Number,
        Contract_Name,
        Product_Identifier,
        Product_Description,
        Total_Units_6mo,
        Total_Spend_6mo,
        contract_best_tier_description,
        contract_best_price,
        is_benchmarked,
        Spend_at_HCIQ90 as Target_Spend_P10,
        Spend_at_HCIQ75 as Target_Spend_P25,
        Spend_at_HCIQ50 as Target_Spend_P50,
        Spend_at_High as Target_Spend_High,
        Spend_at_Best_Tier,
        contract_type_context,
        flag_multiple_best_prices,
        Match_Contexts,
        Original_Contract_Types
    FROM `{project_id}.{dataset_id}.contract_item_benchmark_summary`
    ORDER BY Portfolio_Prefix, Contract_Number, Total_Spend_6mo DESC
    """
    
    # Tab C: QA Flags
    # This tab highlights any contracts from Tab A that have LOW_COVERAGE or MULTIPLE_BEST_PRICES
    tab_c_query = f"""
    SELECT 
        Contract_Number,
        Contract_Name,
        Portfolio,
        Benchmark_Coverage_Pct,
        Flag_Coverage,
        Flag_Ambiguity,
        Contract_Total_Spend
    FROM `{project_id}.{dataset_id}.contract_benchmark_summary`
    WHERE Flag_Coverage = 'LOW_COVERAGE' OR Flag_Ambiguity = 'MULTIPLE_BEST_PRICES'
    ORDER BY Contract_Total_Spend DESC
    """
    
    # Tab D: Methodology
    methodology_path = os.path.join(output_dir, "METHODOLOGY.md")
    with open(methodology_path, "r") as f:
        methodology_text = f.read()
    
    df_d = pd.DataFrame({"Methodology Documentation": methodology_text.split('\n')})

    print("Executing queries...")
    df_a = client.query(tab_a_query).to_dataframe()
    print(f"Tab A loaded: {len(df_a)} rows.")
    
    df_b = client.query(tab_b_query).to_dataframe()
    print(f"Tab B loaded: {len(df_b)} rows.")
    
    df_c = client.query(tab_c_query).to_dataframe()
    print(f"Tab C loaded: {len(df_c)} rows.")

    print(f"Writing to {out_file}...")
    with pd.ExcelWriter(out_file, engine='openpyxl') as writer:
        df_a.to_excel(writer, sheet_name='Tab A - Contract Summary', index=False)
        df_b.to_excel(writer, sheet_name='Tab B - Item Drilldown', index=False)
        df_c.to_excel(writer, sheet_name='Tab C - QA Flags', index=False)
        df_d.to_excel(writer, sheet_name='Tab D - Methodology', index=False)

    print("Done! ✅")

if __name__ == "__main__":
    project_id = "matthew-bossemeyer"
    dataset_id = "dataform_hciq"
    run_id = "2026-03-04__portfolio-competitiveness"
    extract_to_excel(project_id, dataset_id, run_id)
