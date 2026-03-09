import os

filepath = 'scripts/export_deliverable.py'
with open(filepath, 'r') as f:
    orig = f.read()

# I want to add UOM_Outlier_Flag to tab C.
# It is just before is_benchmarked
replacement = """
        best_tier_description,
        Best_Tier_Unit_Price,
        UOM_Outlier_Flag,
        is_benchmarked,
"""
orig = orig.replace('\n        contract_best_tier_description as best_tier_description,\n        contract_best_price as Best_Tier_Unit_Price,\n        is_benchmarked,', replacement)
with open(filepath, 'w') as f:
    f.write(orig)
