import json
import os

TOTAL_ROWS = 19320751
JSON_FILE = 'scripts/profiling_results.json'
OUTPUT_FILE = 'docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master.md'

TABLE_NAME = 'premier_primary_item_master'
PROJECT = 'abi-inbound-prod'
DATASET = 'abi_inbound_bq_stg_master_data_premier_product'

with open(JSON_FILE, 'r') as f:
    data = json.load(f)

# Sort columns alphabetically
data.sort(key=lambda x: x['col_name'])

with open(OUTPUT_FILE, 'w') as f:
    # Header
    f.write(f"# Data Dictionary: `{TABLE_NAME}`\n\n")
    f.write(f"- **Full Path:** `{PROJECT}.{DATASET}.{TABLE_NAME}`\n")
    f.write("- **Description:** Premier Primary Item Master table containing product catalog and attributes.\n")
    f.write(f"- **Estimated Rows:** ~{TOTAL_ROWS:,}\n")
    f.write("- **Generated:** via BigQuery Profiling Tools\n\n")
    f.write("---\n\n")
    f.write("## Overview\n\n")
    f.write("This table contains master product data from Premier. It includes product identifiers (premier_item_number, gtin, ndc), descriptions, packaging information, and environmental attributes.\n\n")
    f.write("---\n\n")
    f.write("## Columns\n\n")

    for col in data:
        name = col['col_name']
        dtype = col.get('data_type', 'UNKNOWN')
        nulls = col.get('null_count', 0)
        distinct = col.get('distinct_count', 0)
        top_vals_raw = col.get('top_values', [])

        pct = (nulls / TOTAL_ROWS) * 100
        
        top_str = ""
        if top_vals_raw:
            items = []
            for item in top_vals_raw:
                val = item.get('value', 'NULL')
                cnt = item.get('count', 0)
                if val is None: val = 'NULL'
                # Truncate long values
                val_str = str(val)
                if len(val_str) > 50:
                    val_str = val_str[:47] + "..."
                items.append(f"`{val_str}` ({cnt:,})")
            top_str = ", ".join(items)

        f.write(f"### {name}\n")
        f.write(f"- Type: `{dtype}`\n")
        f.write("- Description: TBD\n")
        f.write(f"- Nulls: {nulls:,} ({pct:.2f}%)\n")
        f.write(f"- Distinct: {distinct:,}\n")
        if top_str and dtype == 'STRING':
            f.write(f"- Top values: {top_str}\n")
        f.write("\n")

print(f"Generated {OUTPUT_FILE}")
