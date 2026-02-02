import json
import os

def generate_profiling_sql():
    # Load already profiled columns
    if os.path.exists('scripts/profiling_results.json'):
        with open('scripts/profiling_results.json', 'r') as f:
            profiled_data = json.load(f)
            profiled_cols = {row['col_name'] for row in profiled_data}
    else:
        profiled_cols = set()

    # Load live schema
    with open('scripts/live_schema.json', 'r') as f:
        schema_data = json.load(f)
        live_cols = schema_data['Schema']

    # Identify missing columns
    cols_to_profile = [col for col in live_cols if col['Name'] not in profiled_cols]

    print(f"Total live columns: {len(live_cols)}")
    print(f"Already profiled columns: {len(profiled_cols)}")
    print(f"Missing columns to profile: {len(cols_to_profile)}")

    if not cols_to_profile:
        print("No missing columns to profile.")
        return

    # Generate SQL
    project_id = "abi-inbound-prod"
    dataset_id = "abi_inbound_bq_stg_master_data_premier_product"
    table_id = "premier_primary_item_master"
    full_table_name = f"`{project_id}.{dataset_id}.{table_id}`"

    sqls = []
    
    # Process in batches of 5 to isolate errors
    batch_size = 5
    for i in range(0, len(cols_to_profile), batch_size):
        batch = cols_to_profile[i:i + batch_size]
        
        select_clauses = []
        for col in batch:
            col_name = col['Name']
            col_type = col['Type']
            
            # Use safe casting for all types to string for simple profiling
            val_expression = f"CAST({col_name} AS STRING)"
            
            sql_part = f"""SELECT
          '{col_name}' as col_name,
          '{col_type}' as data_type,
          COUNTIF({col_name} IS NULL) as null_count,
          APPROX_COUNT_DISTINCT({col_name}) as distinct_count,
          APPROX_TOP_COUNT({val_expression}, 5) as top_values
        FROM {full_table_name}"""
            select_clauses.append(sql_part.strip())

        full_query = " UNION ALL ".join(select_clauses)
        sqls.append(full_query)

    # Write to files
    for idx, sql in enumerate(sqls):
        filename = f'scripts/missing_profiling_batch_{idx+1}.sql'
        with open(filename, 'w') as f:
            f.write(sql)
        print(f"SQL generated in {filename}")

if __name__ == "__main__":
    generate_profiling_sql()
