import json
import os

def generate_markdown():
    # Load Schema
    with open('config/workflow_schema.json', 'r') as f:
        schema_data = json.load(f)

    # Load Stats
    with open('config/workflow_stats.json', 'r') as f:
        stats_data = json.load(f)

    table_id = schema_data.get('FullID', 'premierinc-com-data.invoicing_provider_workflow.provider_invoice_workflow_history')
    table_desc = schema_data.get('Description', 'No description provided.')
    total_rows = stats_data.get('total_rows', 'Unknown')
    if isinstance(total_rows, int):
        total_rows_str = f"{total_rows:,}"
    else:
        total_rows_str = str(total_rows)
    
    # Extract short name from ID
    short_name = table_id.split('.')[-1]

    fields = schema_data.get('Schema', [])

    markdown_lines = []
    markdown_lines.append(f"# Data Dictionary: {short_name}")
    markdown_lines.append(f"**Table**: `{table_id}`")
    markdown_lines.append(f"**Description**: {table_desc}")
    markdown_lines.append(f"**Total Records**: {total_rows_str}")
    markdown_lines.append("")
    markdown_lines.append("## Columns")

    for i, field in enumerate(fields):
        field_name = field['Name']
        field_type = field['Type']
        field_desc = field['Description']

        if i > 0:
            markdown_lines.append("")
            markdown_lines.append("---")

        # Get stats
        distinct_key = f"{field_name}_distinct"
        nulls_key = f"{field_name}_nulls"
        top_key = f"{field_name}_top"

        distinct_count = stats_data.get(distinct_key, 'N/A')
        null_count = stats_data.get(nulls_key, 'N/A')
        top_values = stats_data.get(top_key, [])

        markdown_lines.append(f"### {field_name}")
        markdown_lines.append(f"- **Type**: `{field_type}`")
        markdown_lines.append(f"- **Description**: {field_desc}")
        markdown_lines.append(f"- **Distinct Values**: {distinct_count}")
        markdown_lines.append(f"- **Nulls**: {null_count}")

        if top_values:
            markdown_lines.append(f"- **Top Values**:")
            for val_obj in top_values:
                val = val_obj.get('value', 'null')
                count = val_obj.get('count', 0)
                # Handle null explicitly for display if needed, but schema usually returns null/None
                if val is None:
                    val_display = "NULL"
                else:
                    val_display = str(val)
                
                # Format numbers with commas
                count_display = f"{count:,}"
                
                markdown_lines.append(f"  - `{val_display}`: {count_display}")

    output_path = 'docs/data_dictionaries/premierinc-com-data.invoicing_provider_workflow.provider_invoice_workflow_history.md'
    with open(output_path, 'w') as f:
        f.write('\n'.join(markdown_lines))

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    generate_markdown()
