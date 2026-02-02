import json

with open('scripts/premier_primary_item_master_schema.json', 'r') as f:
    schema = json.load(f)

with open('scripts/profiling_results.json', 'r') as f:
    profiling = json.load(f)

schema_cols = set(c['column_name'] for c in schema)
profiled_cols = set(c['col_name'] for c in profiling)

missing = schema_cols - profiled_cols
print(list(missing))
