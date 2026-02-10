
import json
import os

schema_path = "/Users/matt_bossemeyer/Projects/wt-2026-02-10__portfolio-expansion/config/workflow_schema.json"

with open(schema_path, 'r') as f:
    schema_data = json.load(f)

schema = schema_data['Schema']
full_id = "premierinc-com-data.invoicing_provider_workflow.provider_invoice_workflow_history"

# Construct the SELECT clause
select_parts = []

for field in schema:
    col_name = field['Name']
    col_type = field['Type']
    
    # Escape keywords if necessary (not strictly needed for these column names but good practice)
    # But for simplicity, we'll assume standard names.
    
    # 1. Distinct Count
    # Use APPROX_COUNT_DISTINCT for efficiency on large tables
    select_parts.append(f"APPROX_COUNT_DISTINCT({col_name}) as {col_name}_distinct")
    
    # 2. Null Count
    select_parts.append(f"COUNTIF({col_name} IS NULL) as {col_name}_nulls")
    
    # 3. Top Values
    # APPROX_TOP_COUNT supports standard types.
    select_parts.append(f"APPROX_TOP_COUNT({col_name}, 5) as {col_name}_top")

query = "SELECT \n" + ",\n".join(select_parts) + f"\nFROM `{full_id}`"

print(query)
