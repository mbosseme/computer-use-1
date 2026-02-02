import json
import os

def generate_scaffold(json_file, output_md):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Sort by column name
    data.sort(key=lambda x: x['col_name'])

    with open(output_md, 'w') as f:
        f.write("# Data Dictionary: premier_primary_item_master\n\n")
        f.write("## Table Details\n")
        f.write("- **Project**: abi-inbound-prod\n")
        f.write("- **Dataset**: abi_inbound_bq_stg_master_data_premier_product\n")
        f.write("- **Table**: premier_primary_item_master\n\n")

        for row in data:
            col = row['col_name']
            dtype = row.get('data_type', 'UNKNOWN')
            
            f.write(f"### {col}\n\n")
            f.write(f"- **Description**: TBD\n")
            f.write(f"- **Data Type**: {dtype}\n")
            
            # stats will be populated by the update script, but we can just do it here since we have the data
            nulls = row.get('null_count', 0)
            distinct = row.get('distinct_count', 0)
            
            # Assuming TOTAL_ROWS is constant for now, or sum nulls + non-nulls if we had it. 
            # We don't have total rows easily accessible here unless we sum top_values counts? No.
            # But we can format without percentages or just "N/A"
            
            f.write(f"- **Nulls**: {nulls}\n")
            f.write(f"- **Distinct Values**: {distinct}\n")
            f.write("- **Top Values**:\n")
            
            top_vals = row.get('top_values', [])
            for v in top_vals:
                val = v.get('value', 'NULL')
                count = v.get('count', 0)
                f.write(f"  - `{val}`: {count:,}\n")
            
            f.write("\n---\n\n")
            
    print(f"Dictionary scaffold generated at {output_md}")

if __name__ == "__main__":
    generate_scaffold('scripts/profiling_results_complete.json', 'docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master.md')
