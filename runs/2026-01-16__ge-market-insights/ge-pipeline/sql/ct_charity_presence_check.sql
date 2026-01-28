-- ct_charity_presence_check.sql
-- Rendered/executed by scripts/ct_charity_outputs.py
--
-- Requirements (NEXT_ITERATION_PLAN.md):
-- - Output one row per term (including 0-match rows)
-- - Use PRD window (injected by DATE_WHERE)
-- - Match using facility-submitted description/vendor/manufacturer fields (via MATCH_TEXT_EXPR)
-- - "Anywhere" is GE-gated (manufacturer inference) to avoid counting non-GE matches.
-- - CT-mapped is a Charity validation signal (Premier CT mapping + inferred CT for CT-like GE terms).

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
      {{CONTRACT_CATEGORY_FIELD}} AS contract_category,
      {{PRODUCT_DESCRIPTION_BACKFILLED_EXPR}} AS product_description_backfilled,
      {{FACILITY_PRODUCT_DESCRIPTION_FIELD}} AS facility_product_description,
      {{FACILITY_MANUFACTURER_NAME_FIELD}} AS facility_manufacturer_name,
      {{FACILITY_VENDOR_NAME_FIELD}} AS facility_vendor_name,
      {{FACILITY_MANUFACTURER_CATALOG_NUM_FIELD}} AS facility_manufacturer_catalog_num,
      {{FACILITY_VENDOR_CATALOG_NUM_FIELD}} AS facility_vendor_catalog_num,
      {{PRODUCT_DESCRIPTION_FIELD}} AS product_description,
      {{MANUFACTURER_TOP_PARENT_NAME_FIELD}} AS manufacturer_top_parent_name,
      {{MANUFACTURER_NAME_FIELD}} AS manufacturer_name,
      {{VENDOR_TOP_PARENT_NAME_FIELD}} AS vendor_top_parent_name,
      {{VENDOR_NAME_FIELD}} AS vendor_name,
      {{BRAND_NAME_FIELD}} AS brand_name,
      {{MANUFACTURER_CATALOG_NUMBER_FIELD}} AS manufacturer_catalog_number,
      {{VENDOR_CATALOG_NUMBER_FIELD}} AS vendor_catalog_number,
      {{HIERARCHY_FIELDS_SELECT}}
      {{IS_GE_MFR_EXPR}} AS is_ge_mfr,
      {{MATCH_TEXT_EXPR}} AS match_text,
      {{EXAMPLE_DESC_EXPR}} AS example_desc
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
  matches_raw AS (
    SELECT
      t.term_order,
      t.term_key,
      t.term_label,
      b.txn_month,
      b.base_spend,
      b.contract_category,
      b.example_desc,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description_backfilled AS STRING), '')), t.pattern) AS hit_backfilled_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_product_description AS STRING), '')), t.pattern) AS hit_facility_description,
      REGEXP_CONTAINS(
        UPPER(IFNULL(IFNULL(CAST(b.facility_manufacturer_catalog_num AS STRING), CAST(b.manufacturer_catalog_number AS STRING)), '')),
        t.pattern
      ) AS hit_mfr_catalog_num,
      REGEXP_CONTAINS(
        UPPER(IFNULL(IFNULL(CAST(b.facility_vendor_catalog_num AS STRING), CAST(b.vendor_catalog_number AS STRING)), '')),
        t.pattern
      ) AS hit_vendor_catalog_num,
      REGEXP_CONTAINS(b.match_text, t.pattern) AS hit_other_fields,
      {{IS_CT_MAPPED_EXPR}} AS is_ct_mapped
    FROM base b
    CROSS JOIN terms t
    WHERE REGEXP_CONTAINS(b.match_text, t.pattern)

    UNION ALL

    -- Frontier appears frequently without ES/EX/EL suffix; map those unspecified cases to the ES row
    -- so Frontier presence is not falsely reported as 0.
    SELECT
      t.term_order,
      t.term_key,
      t.term_label,
      b.txn_month,
      b.base_spend,
      b.contract_category,
      b.example_desc,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.product_description_backfilled AS STRING), '')), r'\bFRONTIER\b') AS hit_backfilled_description,
      REGEXP_CONTAINS(UPPER(IFNULL(CAST(b.facility_product_description AS STRING), '')), r'\bFRONTIER\b') AS hit_facility_description,
      REGEXP_CONTAINS(
        UPPER(IFNULL(IFNULL(CAST(b.facility_manufacturer_catalog_num AS STRING), CAST(b.manufacturer_catalog_number AS STRING)), '')),
        r'\bFRONTIER\b'
      ) AS hit_mfr_catalog_num,
      REGEXP_CONTAINS(
        UPPER(IFNULL(IFNULL(CAST(b.facility_vendor_catalog_num AS STRING), CAST(b.vendor_catalog_number AS STRING)), '')),
        r'\bFRONTIER\b'
      ) AS hit_vendor_catalog_num,
      REGEXP_CONTAINS(b.match_text, r'\bFRONTIER\b') AS hit_other_fields,
      {{IS_CT_MAPPED_EXPR}} AS is_ct_mapped
    FROM base b
    JOIN terms t
      ON t.term_key = 'REVOLUTION_FRONTIER_ES'
    WHERE REGEXP_CONTAINS(b.match_text, r'\bFRONTIER\b')
      AND NOT REGEXP_CONTAINS(b.match_text, r'\b(ES|EX|EL)\b')
  ),
  matches AS (
    SELECT
      *,
      ARRAY_TO_STRING(
        ARRAY(
          SELECT x
          FROM UNNEST(
            [
              IF(hit_backfilled_description, 'backfilled_description', NULL),
              IF(hit_mfr_catalog_num, 'mfr_catalog_num', NULL),
              IF(hit_vendor_catalog_num, 'vendor_catalog_num', NULL),
              IF(NOT hit_backfilled_description AND NOT hit_mfr_catalog_num AND NOT hit_vendor_catalog_num AND hit_other_fields, 'other_fields', NULL)
            ]
          ) x
          WHERE x IS NOT NULL
        ),
        ' | '
      ) AS match_evidence_fields
    FROM matches_raw
  ),
  agg_anywhere AS (
    SELECT
      term_key,
      COUNT(1) AS match_count_anywhere,
      SUM(CASE WHEN hit_backfilled_description THEN 1 ELSE 0 END) AS matches_in_backfilled_desc,
      SUM(CASE WHEN hit_facility_description THEN 1 ELSE 0 END) AS matches_in_facility_desc,
      SUM(CASE WHEN hit_mfr_catalog_num THEN 1 ELSE 0 END) AS matches_in_mfr_catalog_num,
      SUM(CASE WHEN hit_vendor_catalog_num THEN 1 ELSE 0 END) AS matches_in_vendor_catalog_num,
      SUM(base_spend) AS base_spend_anywhere,
      MAX(txn_month) AS last_month_anywhere
    FROM matches
    GROUP BY 1
  ),
  agg_ct AS (
    SELECT
      term_key,
      COUNT(1) AS match_count_ct_mapped,
      SUM(base_spend) AS base_spend_ct_mapped,
      MAX(txn_month) AS last_month_ct_mapped
    FROM matches
    WHERE is_ct_mapped
    GROUP BY 1
  ),
  category_spend AS (
    SELECT
      term_key,
      contract_category,
      SUM(base_spend) AS spend
    FROM matches
    GROUP BY 1, 2
  ),
  top_contract_categories AS (
    SELECT
      term_key,
      ARRAY_AGG(CAST(contract_category AS STRING) ORDER BY spend DESC LIMIT 5) AS top5
    FROM category_spend
    GROUP BY 1
  ),
  top_contract_category AS (
    SELECT
      term_key,
      ARRAY_AGG(CAST(contract_category AS STRING) ORDER BY spend DESC LIMIT 1)[OFFSET(0)] AS top1
    FROM category_spend
    GROUP BY 1
  ),
  desc_spend AS (
    SELECT
      term_key,
      example_desc,
      SUM(base_spend) AS spend
    FROM matches
    WHERE example_desc IS NOT NULL AND CAST(example_desc AS STRING) != ''
    GROUP BY 1, 2
  ),
  example_descs AS (
    SELECT
      term_key,
      ARRAY_AGG(CAST(example_desc AS STRING) ORDER BY spend DESC LIMIT 5) AS top5
    FROM desc_spend
    GROUP BY 1
  ),
  evidence_spend AS (
    SELECT
      term_key,
      match_evidence_fields,
      SUM(base_spend) AS spend
    FROM matches
    WHERE match_evidence_fields IS NOT NULL AND match_evidence_fields != ''
    GROUP BY 1, 2
  ),
  evidence_top AS (
    SELECT
      term_key,
      ARRAY_TO_STRING(
        ARRAY_AGG(match_evidence_fields ORDER BY spend DESC LIMIT 5),
        ' || '
      ) AS match_evidence_fields_top5
    FROM evidence_spend
    GROUP BY 1
  )
SELECT
  t.term_order,
  t.term_key,
  t.term_label,
  COALESCE(a.match_count_anywhere, 0) AS match_count_anywhere,
  COALESCE(a.matches_in_backfilled_desc, 0) AS matches_in_backfilled_desc,
  COALESCE(a.matches_in_facility_desc, 0) AS matches_in_facility_desc,
  COALESCE(a.matches_in_mfr_catalog_num, 0) AS matches_in_mfr_catalog_num,
  COALESCE(a.matches_in_vendor_catalog_num, 0) AS matches_in_vendor_catalog_num,
  COALESCE(a.base_spend_anywhere, 0) AS base_spend_anywhere,
  a.last_month_anywhere,
  COALESCE(c.match_count_ct_mapped, 0) AS match_count_ct_mapped,
  COALESCE(c.base_spend_ct_mapped, 0) AS base_spend_ct_mapped,
  c.last_month_ct_mapped,
  SAFE_DIVIDE(COALESCE(c.base_spend_ct_mapped, 0), NULLIF(COALESCE(a.base_spend_anywhere, 0), 0)) AS pct_spend_ct_mapped,
  CASE
    WHEN t.term_key = 'REVOLUTION_FRONTIER_ES' THEN
      'Includes Frontier matches without explicit ES/EX/EL subtype (mapped to ES row)'
    ELSE NULL
  END AS notes_anywhere,
  et.match_evidence_fields_top5,
  tc1.top1 AS top_contract_category_anywhere,
  ARRAY_TO_STRING(tc5.top5, ' | ') AS top_contract_categories_anywhere_top5,
  ARRAY_TO_STRING(ed.top5, ' || ') AS example_facility_descriptions_top5
FROM terms t
LEFT JOIN agg_anywhere a USING (term_key)
LEFT JOIN agg_ct c USING (term_key)
LEFT JOIN top_contract_category tc1 USING (term_key)
LEFT JOIN top_contract_categories tc5 USING (term_key)
LEFT JOIN example_descs ed USING (term_key)
LEFT JOIN evidence_top et USING (term_key)
ORDER BY t.term_order;
-- ct_charity_presence_check.sql
