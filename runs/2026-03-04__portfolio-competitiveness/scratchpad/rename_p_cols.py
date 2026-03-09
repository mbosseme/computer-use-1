import os

files_to_update = [
    'dataform/definitions/models/contract_benchmark_summary.sqlx',
    'dataform/definitions/models/program_benchmark_summary.sqlx',
    'scripts/export_deliverable.py'
]

for filepath in files_to_update:
    with open(filepath, 'r') as f:
        content = f.read()

    # Replaces
    content = content.replace('Target_Spend_P10', 'Target_Spend_90th')
    content = content.replace('Target_Spend_P25', 'Target_Spend_75th')
    content = content.replace('Target_Spend_P50', 'Target_Spend_50th')
    
    with open(filepath, 'w') as f:
        f.write(content)
