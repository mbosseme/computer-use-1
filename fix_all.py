import os

filepath = 'dataform/definitions/models/contract_item_benchmark_summary.sqlx'

sql_content = """config {
  type: "table",
  name: "contract_item_benchmark_summary",
  tags: ["models"]
}

SELECT
  -- Tab C: Contract-product drilldown fields
  t.Attributed_Contract_Number as Contract_Number,
  MAX(cibp.Contract_Name) as Contract_Name,
  MAX(t.Contracted_Supplier) as Contracted_Supplier,
  MAX(t.Manufacturer_Top_Parent_Name) as Manufacturer_Top_Parent_Name,
  MAX(t.Manufacturer_Name) as Manufacturer_Name,
  MAX(t.Manufacturer_Catalog_Number) as Manufacturer_Catalog_Number,
  SUBSTR(t.Attributed_Contract_Number, 1, 2) as Portfolio_Prefix,
  MAX(t.Product_Description) as Product_Description,
  
  -- Spend and Volume from transactions
  SUM(t.Quantity_in_Eaches) as Total_Units_6mo,
  SUM(t.Base_Spend) as Total_Spend_6mo,
  
  -- The tier description & best price used
  MAX(cibp.Contract_Best_Tier_Description) as contract_best_tier_description,
  MAX(cibp.Contract_Best_Price) as contract_best_price,
  MAX(cibp.Contract_Type) as contract_type_context,
  MAX(cibp.flag_multiple_prices) as flag_multiple_best_prices,
  STRING_AGG(DISTINCT t.Match_Context) as Match_Contexts,
  STRING_AGG(DISTINCT t.Original_Contract_Type) as Original_Contract_Types,
  
  -- Benchmark fields
  MAX(b.hciq_low_benchmark) as hciq_low_benchmark,
  MAX(b.hciq_50_benchmark) as hciq_50_benchmark,
  MAX(b.hciq_75_benchmark) as hciq_75_benchmark,
  MAX(b.hciq_90_benchmark) as hciq_90_benchmark,
  MAX(b.hciq_high_benchmark) as hciq_high_benchmark,

  CASE 
    WHEN MAX(b.hciq_50_benchmark) > 0 AND (MAX(cibp.Contract_Best_Price) / MAX(b.hciq_50_benchmark) > 10.0 OR MAX(cibp.Contract_Best_Price) / MAX(b.hciq_50_benchmark) < 0.1) 
      THEN 'CRITICAL_UOM_MISMATCH'
    WHEN MAX(b.hciq_50_benchmark) > 0 AND (MAX(cibp.Contract_Best_Price) / MAX(b.hciq_50_benchmark) > 1.7 OR MAX(cibp.Contract_Best_Price) / MAX(b.hciq_50_benchmark) < 0.3) 
      THEN 'HIGH_VARIANCE_WARNING'
    ELSE 'OK' 
  END as UOM_Outlier_Flag,

  CASE 
    WHEN MAX(b.matched_reference_number) IS NULL THEN FALSE
    WHEN MAX(b.hciq_50_benchmark) > 0 AND (MAX(cibp.Contract_Best_Price) / MAX(b.hciq_50_benchmark) > 10.0 OR MAX(cibp.Contract_Best_Price) / MAX(b.hciq_50_benchmark) < 0.1) THEN FALSE
    ELSE TRUE
  END as is_benchmarked,
  
  -- Benchmark-extended spend (Units * Benchmark Price)
  SUM(CASE WHEN b.hciq_50_benchmark > 0 AND (cibp.Contract_Best_Price / b.hciq_50_benchmark > 10.0 OR cibp.Contract_Best_Price / b.hciq_50_benchmark < 0.1) THEN 0 ELSE t.Quantity_in_Eaches * b.hciq_low_benchmark END) as Spend_at_Low,
  SUM(CASE WHEN b.hciq_50_benchmark > 0 AND (cibp.Contract_Best_Price / b.hciq_50_benchmark > 10.0 OR cibp.Contract_Best_Price / b.hciq_50_benchmark < 0.1) THEN 0 ELSE t.Quantity_in_Eaches * b.hciq_90_benchmark END) as Spend_at_HCIQ90,
  SUM(CASE WHEN b.hciq_50_benchmark > 0 AND (cibp.Contract_Best_Price / b.hciq_50_benchmark > 10.0 OR cibp.Contract_Best_Price / b.hciq_50_benchmark < 0.1) THEN 0 ELSE t.Quantity_in_Eaches * b.hciq_75_benchmark END) as Spend_at_HCIQ75,
  SUM(CASE WHEN b.hciq_50_benchmark > 0 AND (cibp.Contract_Best_Price / b.hciq_50_benchmark > 10.0 OR cibp.Contract_Best_Price / b.hciq_50_benchmark < 0.1) THEN 0 ELSE t.Quantity_in_Eaches * b.hciq_50_benchmark END) as Spend_at_HCIQ50,
  SUM(CASE WHEN b.hciq_50_benchmark > 0 AND (cibp.Contract_Best_Price / b.hciq_50_benchmark > 10.0 OR cibp.Contract_Best_Price / b.hciq_50_benchmark < 0.1) THEN 0 ELSE t.Quantity_in_Eaches * b.hciq_high_benchmark END) as Spend_at_High,
  
  -- Actual-extended spend using the BEST PREMIER PRICE we found
  SUM(t.Quantity_in_Eaches * cibp.Contract_Best_Price) as Spend_at_Best_Tier

FROM ${ref("transaction_analysis_mapped")} t
-- Must join to cibp to only include lines that HAVE a Premier Top Tier price
JOIN ${ref("contract_item_best_price")} cibp 
  ON t.Attributed_Contract_Number = cibp.Contract_Number 
  AND t.Reference_Number = cibp.Reference_Number
LEFT JOIN (
  SELECT 
    matched_reference_number, 
    manufacturer_catalog_number, 
    MAX(hciq_low_benchmark) as hciq_low_benchmark, 
    MAX(hciq_50_benchmark) as hciq_50_benchmark, 
    MAX(hciq_75_benchmark) as hciq_75_benchmark, 
    MAX(hciq_90_benchmark) as hciq_90_benchmark, 
    MAX(hciq_high_benchmark) as hciq_high_benchmark 
  FROM ${ref("received_benchmarks_stg_add_refnum")} 
  WHERE matched_reference_number IS NOT NULL 
  GROUP BY 1, 2
) b 
  ON t.Reference_Number = b.matched_reference_number 
  AND t.Manufacturer_Catalog_Number = b.manufacturer_catalog_number

WHERE 
  -- We only examine Premier contracts
  SUBSTR(t.Attributed_Contract_Number, 1, 2) IN ('PP', 'AD', 'SP')

GROUP BY 
  t.Attributed_Contract_Number,
  SUBSTR(t.Attributed_Contract_Number, 1, 2),
  t.Reference_Number
"""

with open(filepath, 'w') as f:
    f.write(sql_content)


filepath_cbs = 'dataform/definitions/models/contract_benchmark_summary.sqlx'
with open(filepath_cbs, 'r') as f:
    cbs = f.read()

cbs = cbs.replace('SUM(Spend_at_HCIQ90) as Target_Spend_90th,', 'SUM(Spend_at_Low) as Target_Spend_Low,\n    SUM(Spend_at_HCIQ90) as Target_Spend_90th,')
if 'Target_Spend_Low' not in cbs:
    cbs = cbs.replace('Target_Spend_90th,\n  Target_Spend_75th,', 'Target_Spend_Low,\n  Target_Spend_90th,\n  Target_Spend_75th,')

bucketing_logic_old = "WHEN Spend_at_Best_Tier <= Target_Spend_90th THEN '>=90th'"
bucketing_logic_new = "WHEN Spend_at_Best_Tier <= Target_Spend_Low THEN 'Best in Market'\n    WHEN Spend_at_Best_Tier > Target_Spend_Low AND Spend_at_Best_Tier <= Target_Spend_90th THEN '90th-Best'"
if 'Target_Spend_Low' not in bucketing_logic_old and 'Best in Market' not in cbs:
    cbs = cbs.replace(bucketing_logic_old, bucketing_logic_new)

interp_logic_old = "WHEN Spend_at_Best_Tier <= Target_Spend_90th THEN 90.0\n    WHEN Spend_at_Best_Tier > Target_Spend_90th AND Spend_at_Best_Tier <= Target_Spend_75th\n      THEN 90.0 - (15.0 * ((Spend_at_Best_Tier - Target_Spend_90th) / NULLIF(Target_Spend_75th - Target_Spend_90th, 0)))"
interp_logic_new = "WHEN Spend_at_Best_Tier <= Target_Spend_Low THEN 99.0\n    WHEN Spend_at_Best_Tier > Target_Spend_Low AND Spend_at_Best_Tier <= Target_Spend_90th\n      THEN 99.0 - (9.0 * ((Spend_at_Best_Tier - Target_Spend_Low) / NULLIF(Target_Spend_90th - Target_Spend_Low, 0)))\n    WHEN Spend_at_Best_Tier > Target_Spend_90th AND Spend_at_Best_Tier <= Target_Spend_75th\n      THEN 90.0 - (15.0 * ((Spend_at_Best_Tier - Target_Spend_90th) / NULLIF(Target_Spend_75th - Target_Spend_90th, 0)))"
if '99.0' not in cbs:
    cbs = cbs.replace(interp_logic_old, interp_logic_new)

with open(filepath_cbs, 'w') as f:
    f.write(cbs)

filepath_export = 'scripts/export_deliverable.py'
with open(filepath_export, 'r') as f:
    export = f.read()

export = export.replace('best_tier_description,', 'contract_best_tier_description,')
export = export.replace('Best_Tier_Unit_Price,', 'contract_best_price,')
if 'Benchmark_Unit_Price_Low' not in export:
    export = export.replace('hciq_90_benchmark as Benchmark_Unit_Price_90th,', 'hciq_low_benchmark as Benchmark_Unit_Price_Low,\n        hciq_90_benchmark as Benchmark_Unit_Price_90th,')
if 'Target_Spend_Low' not in export:
    export = export.replace('Spend_at_HCIQ90 as Target_Spend_90th,', 'Spend_at_Low as Target_Spend_Low,\n        Spend_at_HCIQ90 as Target_Spend_90th,')
    export = export.replace('Target_Spend_90th,\n        Target_Spend_75th,', 'Target_Spend_Low,\n        Target_Spend_90th,\n        Target_Spend_75th,')

with open(filepath_export, 'w') as f:
    f.write(export)

print("All patched!")
