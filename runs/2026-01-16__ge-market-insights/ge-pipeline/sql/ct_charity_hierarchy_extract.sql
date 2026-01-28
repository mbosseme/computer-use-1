-- ct_charity_hierarchy_extract.sql
-- Rendered/executed by scripts/ct_charity_outputs.py
--
-- Requirements (NEXT_ITERATION_PLAN.md):
-- - Row-level evidence including both anywhere matches and CT-mapped matches
-- - Include facility-submitted fields + hierarchy fields
-- - Sampling: top ~50 rows per term by Base_Spend (and include is_ct_mapped flag)

WITH
  terms AS (
{{TERMS_CTE}}
  ),
  base_raw AS (
    SELECT
      DATE(Transaction_Date) AS txn_date,
      FORMAT_DATE('%Y-%m', DATE(Transaction_Date)) AS txn_month,
      {{SPEND_FIELD}} AS base_spend,
      {{QUANTITY_FIELD}} AS quantity,
      SAFE_DIVIDE({{SPEND_FIELD}}, NULLIF(CAST({{QUANTITY_FIELD}} AS FLOAT64), 0)) AS unit_price,
      {{PRODUCT_DESCRIPTION_BACKFILLED_EXPR}} AS product_description_backfilled,
      {{FACILITY_PRODUCT_DESCRIPTION_FIELD}} AS facility_product_description,
      {{FACILITY_MANUFACTURER_NAME_FIELD}} AS facility_manufacturer_name,
      {{FACILITY_VENDOR_NAME_FIELD}} AS facility_vendor_name,
      {{FACILITY_MANUFACTURER_CATALOG_NUM_FIELD}} AS facility_manufacturer_catalog_num,
      {{FACILITY_VENDOR_CATALOG_NUM_FIELD}} AS facility_vendor_catalog_num,
      {{PRODUCT_DESCRIPTION_FIELD}} AS product_description,
      {{MANUFACTURER_NAME_FIELD}} AS manufacturer_name,
      {{MANUFACTURER_TOP_PARENT_NAME_FIELD}} AS manufacturer_top_parent_name,
      {{VENDOR_NAME_FIELD}} AS vendor_name,
      {{VENDOR_TOP_PARENT_NAME_FIELD}} AS vendor_top_parent_name,
      {{BRAND_NAME_FIELD}} AS brand_name,
      {{MANUFACTURER_CATALOG_NUMBER_FIELD}} AS manufacturer_catalog_number,
      {{VENDOR_CATALOG_NUMBER_FIELD}} AS vendor_catalog_number,
      {{CONTRACT_CATEGORY_FIELD}} AS contract_category,
      {{HIERARCHY_FIELDS_SELECT}}
      {{IS_GE_MFR_EXPR}} AS is_ge_mfr,
      {{MATCH_TEXT_EXPR}} AS match_text
    FROM `{{TABLE_FQN}}`
    WHERE 1 = 1
{{DATE_WHERE}}
      AND {{SPEND_FIELD}} IS NOT NULL
  ),
  base AS (
    SELECT *
    FROM base_raw
    WHERE REGEXP_CONTAINS(match_text, r'{{ANY_PATTERN}}')
      AND is_ge_mfr
  ),
  matched_raw AS (
    SELECT
      t.term_order,
      t.term_key,
      t.term_label,
      b.*,
      ARRAY_TO_STRING(
        ARRAY(
          SELECT x
          FROM UNNEST(
            [
              IF(REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description_backfilled AS STRING), '')), t.pattern), 'backfilled_description', NULL),
              IF(
                REGEXP_CONTAINS(
                  UPPER(IFNULL(IFNULL(CAST(b.facility_manufacturer_catalog_num AS STRING), CAST(b.manufacturer_catalog_number AS STRING)), '')),
                  t.pattern
                ),
                'mfr_catalog_num',
                NULL
              ),
              IF(
                REGEXP_CONTAINS(
                  UPPER(IFNULL(IFNULL(CAST(b.facility_vendor_catalog_num AS STRING), CAST(b.vendor_catalog_number AS STRING)), '')),
                  t.pattern
                ),
                'vendor_catalog_num',
                NULL
              )
            ]
          ) x
          WHERE x IS NOT NULL
        ),
        ' | '
      ) AS match_evidence_fields,
      {{IS_CT_MAPPED_EXPR}} AS is_ct_mapped
    FROM base b
    CROSS JOIN terms t
    WHERE REGEXP_CONTAINS(b.match_text, t.pattern)

    UNION ALL

    -- Frontier appears frequently without ES/EX/EL suffix; map those unspecified cases to the ES row
    SELECT
      t.term_order,
      t.term_key,
      t.term_label,
      b.*,
      ARRAY_TO_STRING(
        ARRAY(
          SELECT x
          FROM UNNEST(
            [
              IF(REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description_backfilled AS STRING), '')), r'\bFRONTIER\b'), 'backfilled_description', NULL),
              IF(
                REGEXP_CONTAINS(
                  UPPER(IFNULL(IFNULL(CAST(b.facility_manufacturer_catalog_num AS STRING), CAST(b.manufacturer_catalog_number AS STRING)), '')),
                  r'\bFRONTIER\b'
                ),
                'mfr_catalog_num',
                NULL
              ),
              IF(
                REGEXP_CONTAINS(
                  UPPER(IFNULL(IFNULL(CAST(b.facility_vendor_catalog_num AS STRING), CAST(b.vendor_catalog_number AS STRING)), '')),
                  r'\bFRONTIER\b'
                ),
                'vendor_catalog_num',
                NULL
              )
            ]
          ) x
          WHERE x IS NOT NULL
        ),
        ' | '
      ) AS match_evidence_fields,
      {{IS_CT_MAPPED_EXPR}} AS is_ct_mapped
    FROM base b
    JOIN terms t
      ON t.term_key = 'REVOLUTION_FRONTIER_ES'
    WHERE REGEXP_CONTAINS(b.match_text, r'\bFRONTIER\b')
      AND NOT REGEXP_CONTAINS(b.match_text, r'\b(ES|EX|EL)\b')
  ),
  matched AS (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY term_key, is_ct_mapped
        ORDER BY base_spend DESC, txn_date DESC
      ) AS rn
    FROM matched_raw
  ),
  limited AS (
    SELECT *
    FROM matched
    WHERE rn <= 50
  )
SELECT
  term_order,
  term_key,
  term_label,
  is_ct_mapped,
  match_evidence_fields,
  txn_date AS Transaction_Date,
  txn_month AS Month,
  base_spend AS Base_Spend,
  quantity AS Quantity,
  unit_price AS unit_price,
  product_description_backfilled AS Product_Description_Backfilled,
  facility_product_description AS Facility_Product_Description,
  facility_manufacturer_name AS Facility_Manufacturer_Name,
  facility_vendor_name AS Facility_Vendor_Name,
  facility_manufacturer_catalog_num AS Facility_Manufacturer_Catalog_Num,
  facility_vendor_catalog_num AS Facility_Vendor_Catalog_Num,
  brand_name AS Brand_Name,
  manufacturer_name AS Manufacturer_Name,
  manufacturer_top_parent_name AS Manufacturer_Top_Parent_Name,
  vendor_name AS Vendor_Name,
  vendor_top_parent_name AS Vendor_Top_Parent_Name,
  manufacturer_catalog_number AS Manufacturer_Catalog_Number,
  vendor_catalog_number AS Vendor_Catalog_Number,
  contract_category AS Contract_Category{{HIERARCHY_FIELDS_OUTPUT}}
FROM limited
ORDER BY term_order, is_ct_mapped DESC, Base_Spend DESC, Transaction_Date DESC;
-- ct_charity_hierarchy_extract.sql
