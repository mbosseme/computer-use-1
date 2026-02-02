from typing import List

def generate_profiling_sql(
    project_id: str,
    dataset_id: str,
    table_id: str,
    columns: List[str]
) -> str:
    
    # We need data types for these to handle casting if necessary?
    # Schema says most are strings or floats. The original query pattern handles most.
    # Pattern:
    # SELECT 'col_name' as col_name, 'DATA_TYPE' as data_type, ...
    
    # I'll rely on the schema file to get data types to be precise.
    import json
    with open('scripts/premier_primary_item_master_schema.json', 'r') as f:
        schema = json.load(f)
    
    type_map = {c['column_name']: c['data_type'] for c in schema}
    
    queries = []
    
    for col in columns:
        dtype = type_map.get(col, 'STRING')
        
        # Safe casting for top value counts
        val_expr = col
        if dtype == 'STRING':
            val_expr = f"{col}"
        else:
            val_expr = f"CAST({col} AS STRING)"

        sql = f"""
        SELECT
            '{col}' as col_name,
            '{dtype}' as data_type,
            COUNT(DISTINCT {col}) as distinct_count,
            COUNTIF({col} IS NULL) as null_count,
            ARRAY_AGG(STRUCT(val as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT {val_expr} as val, COUNT(*) as count
            FROM `{project_id}.{dataset_id}.{table_id}`
            GROUP BY 1
        )
        """
        queries.append(sql.strip())
        
    return " UNION ALL \n".join(queries)

missing_cols = [
    'benchmark_10th_percentile_6_month', 'manufacturer_catalog_number', 'benchmark_high_price_6_month', 
    'is_proprietary', 'benchmark_median_price', 'product_description', 'product_id', 
    'manufacturer_name', 'reference_number', 'pkg_uom', 'hcpcs_description', 
    'hvi_level_2_category_code', 'product_contract_category', 'lead_cadmium_organitins_free', 
    'description_100', 'cont_prop_65_below_thresh_det', 'hvi_level_3_category_code', 
    'benchmark_median_price_6_month', 'drug_case_size'
]

sql = generate_profiling_sql(
    'abi-inbound-prod',
    'abi_inbound_bq_stg_master_data_premier_product',
    'premier_primary_item_master',
    missing_cols
)

print(sql)
