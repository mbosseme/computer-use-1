WITH tx AS (
  SELECT 
    Reference_Number, 
    Manufacturer_Catalog_Number,
    SUM(Base_Spend) as base_spend
  FROM matthew-bossemeyer.dataform_hciq.transaction_analysis_mapped
  GROUP BY 1, 2
),
old_match AS (
  SELECT DISTINCT matched_reference_number
  FROM matthew-bossemeyer.dataform_hciq.received_benchmarks_stg_add_refnum
  WHERE matched_reference_number IS NOT NULL
),
new_match AS (
  SELECT DISTINCT matched_reference_number, manufacturer_catalog_number
  FROM matthew-bossemeyer.dataform_hciq.received_benchmarks_stg_add_refnum
  WHERE matched_reference_number IS NOT NULL AND manufacturer_catalog_number IS NOT NULL
),
tx_matches AS (
  SELECT
    tx.base_spend,
    IF(o.matched_reference_number IS NOT NULL, 1, 0) as is_matched_old,
    IF(n.matched_reference_number IS NOT NULL, 1, 0) as is_matched_new
  FROM tx
  LEFT JOIN old_match o ON tx.Reference_Number = o.matched_reference_number
  LEFT JOIN new_match n ON tx.Reference_Number = n.matched_reference_number AND tx.Manufacturer_Catalog_Number = n.manufacturer_catalog_number
)
SELECT
  SUM(base_spend) as Total_Transaction_Spend,
  SUM(IF(is_matched_old = 1, base_spend, 0)) as Matched_Spend_Old_Method,
  SUM(IF(is_matched_new = 1, base_spend, 0)) as Matched_Spend_New_Method,
  ROUND(SUM(IF(is_matched_old = 1, base_spend, 0)) / SUM(base_spend) * 100, 2) as Cov_Pct_Old,
  ROUND(SUM(IF(is_matched_new = 1, base_spend, 0)) / SUM(base_spend) * 100, 2) as Cov_Pct_New
FROM tx_matches;
