-- ct_ct_text_discovery.sql
-- Rendered/executed by scripts/ct_charity_outputs.py
--
-- Purpose (NEXT ITERATION): lightweight alias discovery for CT-mapped records.
-- Pull top Facility_Product_Description strings in CT category that look GE-like.

WITH base AS (
  SELECT
    FORMAT_DATE('%Y-%m', DATE(Transaction_Date)) AS txn_month,
    {{SPEND_FIELD}} AS base_spend,
    {{CONTRACT_CATEGORY_FIELD}} AS contract_category,
    {{FACILITY_PRODUCT_DESCRIPTION_FIELD}} AS facility_product_description,
    {{FACILITY_MANUFACTURER_NAME_FIELD}} AS facility_manufacturer_name,
    {{FACILITY_VENDOR_NAME_FIELD}} AS facility_vendor_name,
    {{MATCH_TEXT_EXPR}} AS match_text
  FROM `{{TABLE_FQN}}`
  WHERE 1 = 1
{{DATE_WHERE}}
    AND {{SPEND_FIELD}} IS NOT NULL
    AND UPPER(CAST({{CONTRACT_CATEGORY_FIELD}} AS STRING)) = 'COMPUTED TOMOGRAPHY'
    AND REGEXP_CONTAINS(
      {{MATCH_TEXT_EXPR}},
      r'(?:\b(GE|REVOLUTION|OPTIMA|VCT|DISCOVERY)\b|G\.E\.)'
    )
)
SELECT
  CAST(facility_product_description AS STRING) AS Facility_Product_Description,
  CAST(facility_manufacturer_name AS STRING) AS Facility_Manufacturer_Name,
  CAST(facility_vendor_name AS STRING) AS Facility_Vendor_Name,
  COUNT(1) AS count_txns,
  SUM(base_spend) AS sum_base_spend,
  MAX(txn_month) AS last_month
FROM base
WHERE facility_product_description IS NOT NULL
  AND CAST(facility_product_description AS STRING) != ''
GROUP BY 1, 2, 3
ORDER BY sum_base_spend DESC
LIMIT 200;
