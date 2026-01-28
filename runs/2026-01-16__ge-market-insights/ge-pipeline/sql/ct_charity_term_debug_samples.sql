-- ct_charity_term_debug_samples.sql
-- Rendered/executed by scripts/ct_charity_outputs.py
--
-- Purpose:
-- - Fast QA artifact for term matching quality
-- - Shows the top backfilled descriptions per term with spend + CT-mapped split

WITH
  terms AS (
{{TERMS_CTE}}
  ),
  base_raw AS (
    SELECT
      FORMAT_DATE('%Y-%m', DATE(Transaction_Date)) AS txn_month,
      {{SPEND_FIELD}} AS base_spend,
      {{CONTRACT_CATEGORY_FIELD}} AS contract_category,
      {{PRODUCT_DESCRIPTION_BACKFILLED_EXPR}} AS product_description_backfilled,
      {{FACILITY_PRODUCT_DESCRIPTION_FIELD}} AS facility_product_description,
      {{FACILITY_MANUFACTURER_NAME_FIELD}} AS facility_manufacturer_name,
      {{FACILITY_VENDOR_NAME_FIELD}} AS facility_vendor_name,
      {{FACILITY_MANUFACTURER_CATALOG_NUM_FIELD}} AS facility_manufacturer_catalog_num,
      {{FACILITY_VENDOR_CATALOG_NUM_FIELD}} AS facility_vendor_catalog_num,
      {{IF_PRODUCT_DESCRIPTION_FIELD}} AS product_description,
      {{IF_MANUFACTURER_TOP_PARENT_NAME_FIELD}} AS manufacturer_top_parent_name,
      {{IF_MANUFACTURER_NAME_FIELD}} AS manufacturer_name,
      {{IF_VENDOR_TOP_PARENT_NAME_FIELD}} AS vendor_top_parent_name,
      {{IF_VENDOR_NAME_FIELD}} AS vendor_name,
      {{IF_BRAND_NAME_FIELD}} AS brand_name,
      {{MANUFACTURER_CATALOG_NUMBER_FIELD}} AS manufacturer_catalog_number,
      {{VENDOR_CATALOG_NUMBER_FIELD}} AS vendor_catalog_number,
      {{CONTRACTED_CATALOG_NUMBER_FIELD}} AS contracted_catalog_number,
      {{CURRENT_CONTRACTED_CATALOG_NUMBER_FIELD}} AS current_contracted_catalog_number,
      {{FORECASTED_CONTRACTED_CATALOG_NUMBER_FIELD}} AS forecasted_contracted_catalog_number,
      {{CURRENT_CONTRACTED_PRODUCT_DESCRIPTION_FIELD}} AS current_contracted_product_description,
      {{FORECASTED_CONTRACTED_PRODUCT_DESCRIPTION_FIELD}} AS forecasted_contracted_product_description,
      {{REPLACED_BY_MANUFACTURER_CATALOG_NUMBER_FIELD}} AS replaced_by_manufacturer_catalog_number,
      {{NOISELESS_CATALOG_NUMBER_FIELD}} AS noiseless_catalog_number,
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
    WHERE (
      REGEXP_CONTAINS(match_text, r'{{ANY_PATTERN}}')
      OR REGEXP_CONTAINS(match_text, r'\bFRONTIER\b')
    )
      AND is_ge_mfr
  ),
  matches AS (
    SELECT
      t.term_order,
      t.term_key,
      t.term_label,
      b.txn_month,
      b.base_spend,
      b.contract_category,
      b.product_description_backfilled,
      b.facility_product_description,
      b.facility_vendor_name,
      b.facility_manufacturer_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description_backfilled AS STRING), '')), t.pattern) AS hit_backfilled_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_product_description AS STRING), '')), t.pattern) AS hit_facility_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description AS STRING), '')), t.pattern) AS hit_product_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_manufacturer_name AS STRING), '')), t.pattern) AS hit_facility_mfr_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_vendor_name AS STRING), '')), t.pattern) AS hit_facility_vendor_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.manufacturer_name AS STRING), '')), t.pattern) AS hit_mfr_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.manufacturer_top_parent_name AS STRING), '')), t.pattern) AS hit_mfr_top_parent_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.vendor_name AS STRING), '')), t.pattern) AS hit_vendor_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.vendor_top_parent_name AS STRING), '')), t.pattern) AS hit_vendor_top_parent_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.brand_name AS STRING), '')), t.pattern) AS hit_brand_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_manufacturer_catalog_num AS STRING), '')), t.pattern) AS hit_facility_mfr_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_vendor_catalog_num AS STRING), '')), t.pattern) AS hit_facility_vendor_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.manufacturer_catalog_number AS STRING), '')), t.pattern) AS hit_mfr_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.vendor_catalog_number AS STRING), '')), t.pattern) AS hit_vendor_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.contracted_catalog_number AS STRING), '')), t.pattern) AS hit_contracted_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.current_contracted_catalog_number AS STRING), '')), t.pattern) AS hit_curr_contracted_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.forecasted_contracted_catalog_number AS STRING), '')), t.pattern) AS hit_fcast_contracted_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.current_contracted_product_description AS STRING), '')), t.pattern) AS hit_curr_contracted_prod_desc,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.forecasted_contracted_product_description AS STRING), '')), t.pattern) AS hit_fcast_contracted_prod_desc,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.replaced_by_manufacturer_catalog_number AS STRING), '')), t.pattern) AS hit_replaced_by_mfr_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.noiseless_catalog_number AS STRING), '')), t.pattern) AS hit_noiseless_catalog_num,
      {{IS_CT_MAPPED_EXPR}} AS is_ct_mapped
    FROM base b
    CROSS JOIN terms t
    WHERE REGEXP_CONTAINS(b.match_text, t.pattern)

    UNION ALL

    -- Frontier appears frequently without ES/EX/EL suffix; map those unspecified cases to the ES row.
    SELECT
      t.term_order,
      t.term_key,
      t.term_label,
      b.txn_month,
      b.base_spend,
      b.contract_category,
      b.product_description_backfilled,
      b.facility_product_description,
      b.facility_vendor_name,
      b.facility_manufacturer_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description_backfilled AS STRING), '')), r'\bFRONTIER\b') AS hit_backfilled_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_product_description AS STRING), '')), r'\bFRONTIER\b') AS hit_facility_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description AS STRING), '')), r'\bFRONTIER\b') AS hit_product_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_manufacturer_name AS STRING), '')), r'\bFRONTIER\b') AS hit_facility_mfr_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_vendor_name AS STRING), '')), r'\bFRONTIER\b') AS hit_facility_vendor_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.manufacturer_name AS STRING), '')), r'\bFRONTIER\b') AS hit_mfr_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.manufacturer_top_parent_name AS STRING), '')), r'\bFRONTIER\b') AS hit_mfr_top_parent_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.vendor_name AS STRING), '')), r'\bFRONTIER\b') AS hit_vendor_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.vendor_top_parent_name AS STRING), '')), r'\bFRONTIER\b') AS hit_vendor_top_parent_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.brand_name AS STRING), '')), r'\bFRONTIER\b') AS hit_brand_name,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_manufacturer_catalog_num AS STRING), '')), r'\bFRONTIER\b') AS hit_facility_mfr_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_vendor_catalog_num AS STRING), '')), r'\bFRONTIER\b') AS hit_facility_vendor_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.manufacturer_catalog_number AS STRING), '')), r'\bFRONTIER\b') AS hit_mfr_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.vendor_catalog_number AS STRING), '')), r'\bFRONTIER\b') AS hit_vendor_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.contracted_catalog_number AS STRING), '')), r'\bFRONTIER\b') AS hit_contracted_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.current_contracted_catalog_number AS STRING), '')), r'\bFRONTIER\b') AS hit_curr_contracted_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.forecasted_contracted_catalog_number AS STRING), '')), r'\bFRONTIER\b') AS hit_fcast_contracted_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.current_contracted_product_description AS STRING), '')), r'\bFRONTIER\b') AS hit_curr_contracted_prod_desc,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.forecasted_contracted_product_description AS STRING), '')), r'\bFRONTIER\b') AS hit_fcast_contracted_prod_desc,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.replaced_by_manufacturer_catalog_number AS STRING), '')), r'\bFRONTIER\b') AS hit_replaced_by_mfr_catalog_num,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.noiseless_catalog_number AS STRING), '')), r'\bFRONTIER\b') AS hit_noiseless_catalog_num,
      {{IS_CT_MAPPED_EXPR}} AS is_ct_mapped
    FROM base b
    JOIN terms t
      ON t.term_key = 'REVOLUTION_FRONTIER_ES'
    WHERE REGEXP_CONTAINS(b.match_text, r'\bFRONTIER\b')
      AND NOT REGEXP_CONTAINS(b.match_text, r'\b(ES|EX|EL)\b')
  ),
  desc_agg AS (
    SELECT
      term_order,
      term_key,
      term_label,
      CAST(product_description_backfilled AS STRING) AS product_description_backfilled,
      LOGICAL_OR(hit_backfilled_description) AS any_hit_backfilled_description,
      LOGICAL_OR(hit_facility_description) AS any_hit_facility_description,
      LOGICAL_OR(hit_product_description) AS any_hit_product_description,
      LOGICAL_OR(hit_facility_mfr_name) AS any_hit_facility_mfr_name,
      LOGICAL_OR(hit_facility_vendor_name) AS any_hit_facility_vendor_name,
      LOGICAL_OR(hit_mfr_name) AS any_hit_mfr_name,
      LOGICAL_OR(hit_mfr_top_parent_name) AS any_hit_mfr_top_parent_name,
      LOGICAL_OR(hit_vendor_name) AS any_hit_vendor_name,
      LOGICAL_OR(hit_vendor_top_parent_name) AS any_hit_vendor_top_parent_name,
      LOGICAL_OR(hit_brand_name) AS any_hit_brand_name,
      LOGICAL_OR(hit_facility_mfr_catalog_num) AS any_hit_facility_mfr_catalog_num,
      LOGICAL_OR(hit_facility_vendor_catalog_num) AS any_hit_facility_vendor_catalog_num,
      LOGICAL_OR(hit_mfr_catalog_num) AS any_hit_mfr_catalog_num,
      LOGICAL_OR(hit_vendor_catalog_num) AS any_hit_vendor_catalog_num,
      LOGICAL_OR(hit_contracted_catalog_num) AS any_hit_contracted_catalog_num,
      LOGICAL_OR(hit_curr_contracted_catalog_num) AS any_hit_curr_contracted_catalog_num,
      LOGICAL_OR(hit_fcast_contracted_catalog_num) AS any_hit_fcast_contracted_catalog_num,
      LOGICAL_OR(hit_curr_contracted_prod_desc) AS any_hit_curr_contracted_prod_desc,
      LOGICAL_OR(hit_fcast_contracted_prod_desc) AS any_hit_fcast_contracted_prod_desc,
      LOGICAL_OR(hit_replaced_by_mfr_catalog_num) AS any_hit_replaced_by_mfr_catalog_num,
      LOGICAL_OR(hit_noiseless_catalog_num) AS any_hit_noiseless_catalog_num,
      COUNT(1) AS match_count_anywhere,
      SUM(base_spend) AS base_spend_anywhere,
      SUM(CASE WHEN is_ct_mapped THEN 1 ELSE 0 END) AS match_count_ct_mapped,
      SUM(CASE WHEN is_ct_mapped THEN base_spend ELSE 0 END) AS base_spend_ct_mapped,
      MAX(txn_month) AS last_month_anywhere
    FROM matches
    WHERE product_description_backfilled IS NOT NULL
      AND TRIM(CAST(product_description_backfilled AS STRING)) != ''
    GROUP BY 1, 2, 3, 4
  ),
  desc_agg_evidence AS (
    SELECT
      term_order,
      term_key,
      term_label,
      product_description_backfilled,
      any_hit_backfilled_description AS matched_in_backfilled_desc,
      any_hit_facility_description AS matched_in_facility_desc,
      any_hit_product_description AS matched_in_product_desc,
      any_hit_facility_mfr_name AS matched_in_facility_mfr_name,
      any_hit_facility_vendor_name AS matched_in_facility_vendor_name,
      any_hit_mfr_name AS matched_in_mfr_name,
      any_hit_mfr_top_parent_name AS matched_in_mfr_top_parent_name,
      any_hit_vendor_name AS matched_in_vendor_name,
      any_hit_vendor_top_parent_name AS matched_in_vendor_top_parent_name,
      any_hit_brand_name AS matched_in_brand_name,
      any_hit_facility_mfr_catalog_num AS matched_in_mfr_catalog_num,
      any_hit_facility_vendor_catalog_num AS matched_in_vendor_catalog_num,
      any_hit_mfr_catalog_num AS matched_in_mfr_catalog_num_std,
      any_hit_vendor_catalog_num AS matched_in_vendor_catalog_num_std,
      any_hit_contracted_catalog_num AS matched_in_contracted_catalog_num,
      any_hit_curr_contracted_catalog_num AS matched_in_curr_contracted_catalog_num,
      any_hit_fcast_contracted_catalog_num AS matched_in_fcast_contracted_catalog_num,
      any_hit_curr_contracted_prod_desc AS matched_in_curr_contracted_prod_desc,
      any_hit_fcast_contracted_prod_desc AS matched_in_fcast_contracted_prod_desc,
      any_hit_replaced_by_mfr_catalog_num AS matched_in_replaced_by_mfr_catalog_num,
      any_hit_noiseless_catalog_num AS matched_in_noiseless_catalog_num,
      ARRAY_TO_STRING(
        ARRAY(
          SELECT x
          FROM UNNEST(
            [
              IF(any_hit_backfilled_description, 'backfilled_description', NULL),
              IF(any_hit_facility_description, 'facility_description', NULL),
              IF(any_hit_product_description, 'product_description', NULL),
              IF(any_hit_facility_mfr_name, 'facility_manufacturer_name', NULL),
              IF(any_hit_facility_vendor_name, 'facility_vendor_name', NULL),
              IF(any_hit_mfr_name, 'manufacturer_name', NULL),
              IF(any_hit_mfr_top_parent_name, 'manufacturer_top_parent_name', NULL),
              IF(any_hit_vendor_name, 'vendor_name', NULL),
              IF(any_hit_vendor_top_parent_name, 'vendor_top_parent_name', NULL),
              IF(any_hit_brand_name, 'brand_name', NULL),
              IF(any_hit_facility_mfr_catalog_num, 'facility_mfr_catalog_num', NULL),
              IF(any_hit_facility_vendor_catalog_num, 'facility_vendor_catalog_num', NULL),
              IF(any_hit_mfr_catalog_num, 'manufacturer_catalog_number', NULL),
              IF(any_hit_vendor_catalog_num, 'vendor_catalog_number', NULL),
              IF(any_hit_contracted_catalog_num, 'contracted_catalog_number', NULL),
              IF(any_hit_curr_contracted_catalog_num, 'current_contracted_catalog_number', NULL),
              IF(any_hit_fcast_contracted_catalog_num, 'forecasted_contracted_catalog_number', NULL),
              IF(any_hit_curr_contracted_prod_desc, 'current_contracted_product_description', NULL),
              IF(any_hit_fcast_contracted_prod_desc, 'forecasted_contracted_product_description', NULL),
              IF(any_hit_replaced_by_mfr_catalog_num, 'replaced_by_manufacturer_catalog_number', NULL),
              IF(any_hit_noiseless_catalog_num, 'noiseless_catalog_number', NULL)
            ]
          ) x
          WHERE x IS NOT NULL
        ),
        ' | '
      ) AS match_evidence_fields,
      match_count_anywhere,
      base_spend_anywhere,
      match_count_ct_mapped,
      base_spend_ct_mapped,
      last_month_anywhere
    FROM desc_agg
  ),
  vendor_spend AS (
    SELECT
      term_key,
      CAST(product_description_backfilled AS STRING) AS product_description_backfilled,
      CAST(facility_vendor_name AS STRING) AS facility_vendor_name,
      SUM(base_spend) AS spend
    FROM matches
    WHERE product_description_backfilled IS NOT NULL
      AND TRIM(CAST(product_description_backfilled AS STRING)) != ''
      AND facility_vendor_name IS NOT NULL
      AND TRIM(CAST(facility_vendor_name AS STRING)) != ''
    GROUP BY 1, 2, 3
  ),
  vendor_top3 AS (
    SELECT
      term_key,
      product_description_backfilled,
      ARRAY_TO_STRING(
        ARRAY_AGG(facility_vendor_name ORDER BY spend DESC LIMIT 3),
        ' | '
      ) AS top_facility_vendors
    FROM vendor_spend
    GROUP BY 1, 2
  ),
  manufacturer_spend AS (
    SELECT
      term_key,
      CAST(product_description_backfilled AS STRING) AS product_description_backfilled,
      CAST(facility_manufacturer_name AS STRING) AS facility_manufacturer_name,
      SUM(base_spend) AS spend
    FROM matches
    WHERE product_description_backfilled IS NOT NULL
      AND TRIM(CAST(product_description_backfilled AS STRING)) != ''
      AND facility_manufacturer_name IS NOT NULL
      AND TRIM(CAST(facility_manufacturer_name AS STRING)) != ''
    GROUP BY 1, 2, 3
  ),
  manufacturer_top3 AS (
    SELECT
      term_key,
      product_description_backfilled,
      ARRAY_TO_STRING(
        ARRAY_AGG(facility_manufacturer_name ORDER BY spend DESC LIMIT 3),
        ' | '
      ) AS top_facility_manufacturers
    FROM manufacturer_spend
    GROUP BY 1, 2
  ),
  category_spend AS (
    SELECT
      term_key,
      CAST(product_description_backfilled AS STRING) AS product_description_backfilled,
      CAST(contract_category AS STRING) AS contract_category,
      SUM(base_spend) AS spend
    FROM matches
    WHERE product_description_backfilled IS NOT NULL
      AND TRIM(CAST(product_description_backfilled AS STRING)) != ''
      AND contract_category IS NOT NULL
      AND TRIM(CAST(contract_category AS STRING)) != ''
    GROUP BY 1, 2, 3
  ),
  category_top3 AS (
    SELECT
      term_key,
      product_description_backfilled,
      ARRAY_TO_STRING(
        ARRAY_AGG(contract_category ORDER BY spend DESC LIMIT 3),
        ' | '
      ) AS top_contract_categories
    FROM category_spend
    GROUP BY 1, 2
  ),
  ranked AS (
    SELECT
      d.*, 
      ROW_NUMBER() OVER (
        PARTITION BY d.term_key
        ORDER BY d.base_spend_anywhere DESC, d.match_count_anywhere DESC
      ) AS sample_rank
    FROM desc_agg_evidence d
  )
SELECT
  term_order,
  term_key,
  term_label,
  sample_rank,
  product_description_backfilled,
  matched_in_backfilled_desc,
  matched_in_facility_desc,
  matched_in_product_desc,
  matched_in_facility_mfr_name,
  matched_in_facility_vendor_name,
  matched_in_mfr_name,
  matched_in_mfr_top_parent_name,
  matched_in_vendor_name,
  matched_in_vendor_top_parent_name,
  matched_in_brand_name,
  matched_in_mfr_catalog_num,
  matched_in_vendor_catalog_num,
  matched_in_mfr_catalog_num_std,
  matched_in_vendor_catalog_num_std,
  match_evidence_fields,
  match_count_anywhere,
  base_spend_anywhere,
  last_month_anywhere,
  match_count_ct_mapped,
  base_spend_ct_mapped,
  SAFE_DIVIDE(base_spend_ct_mapped, NULLIF(base_spend_anywhere, 0)) AS pct_spend_ct_mapped,
  v.top_facility_vendors,
  m.top_facility_manufacturers,
  c.top_contract_categories
FROM ranked r
LEFT JOIN vendor_top3 v
  USING (term_key, product_description_backfilled)
LEFT JOIN manufacturer_top3 m
  USING (term_key, product_description_backfilled)
LEFT JOIN category_top3 c
  USING (term_key, product_description_backfilled)
WHERE sample_rank <= 25
ORDER BY CAST(term_order AS INT64), base_spend_anywhere DESC, product_description_backfilled;
