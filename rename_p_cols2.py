import os

filepath = 'scripts/export_deliverable.py'
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace('Benchmark_Unit_Price_P10', 'Benchmark_Unit_Price_90th')
content = content.replace('Benchmark_Unit_Price_P25', 'Benchmark_Unit_Price_75th')
content = content.replace('Benchmark_Unit_Price_P50', 'Benchmark_Unit_Price_50th')

with open(filepath, 'w') as f:
    f.write(content)
