import re

with open('dataform/definitions/models/contract_item_benchmark_summary.sqlx', 'r') as f:
    sql = f.read()

print("Original is_benchmarked:")
# Extract the is_benchmarked CASE statement
m = re.search(r'(CASE\s+WHEN MAX\(b\.matched_reference_number.*?)END as is_benchmarked', sql, re.DOTALL)
print(m.group(1))

