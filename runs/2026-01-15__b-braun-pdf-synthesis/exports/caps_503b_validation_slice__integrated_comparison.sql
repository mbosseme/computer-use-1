-- CAPS/503B Category Validation Slice: Integrated Provider ↔ Wholesaler Comparison
-- NDC cohort: 71 NDCs extracted from B. Braun/Fresenius Kabi PDF (Jen's list)
-- Timeframe: 24 months (Jan 2024 – Dec 2025)
-- Join key: Premier_Entity_Code (provider) = facility_id (wholesaler)
-- Generated: 2025-01-27

DECLARE start_ts TIMESTAMP DEFAULT TIMESTAMP('2024-01-01');
DECLARE end_ts   TIMESTAMP DEFAULT TIMESTAMP('2026-01-01');

WITH ndc_cohort AS (
  SELECT ndc11
  FROM UNNEST([
    '63323017876','63323053075','63323062600','63323062610','63323062625','63323062650','63323062655','63323066710','63323066910','63323068310','63323068610','63323068810','63323082474','63323082475','63323082476','63323086710','63323086774','63323086910','63323086974','63323086975','63323087010','63323087074','63323087310','63323087374','63323087375','65219000401','65219000601','65219000851','65219001001','65219001201','65219011810','65219011910','65219014210','65219014410','65219014610','65219014810','65219015075','65219015310','65219021850','65219022010','65219022225','65219022450','65219023410','65219023610','65219023825','65219024050','65219024110','65219024350','65219024610','65219025810','65219038905','65219038910','65219045660','65219045830','65219046020','65219046210','65219046450','65219046660','65219046850','65219047030','65219047220','65219047410','65219047530','65219047720','65219047910','65219049510','65219049720','65219049930','65219050210','65219050420','65219050630'
  ]) AS ndc11
),

-- Provider aggregate (ERP purchasing via Transaction Analysis Expanded)
provider_agg AS (
  SELECT
    NULLIF(TRIM(CAST(Premier_Entity_Code AS STRING)), '') AS facility_id,
    FORMAT_TIMESTAMP('%Y-%m-01', Transaction_Date) AS month_year,
    REGEXP_REPLACE(CAST(Ndc AS STRING), r'[^0-9]', '') AS ndc11,
    ANY_VALUE(Health_System_Name) AS provider_health_system,
    ANY_VALUE(Manufacturer_Name) AS manufacturer_name,
    SUM(Landed_Spend) AS provider_landed_spend,
    SUM(Base_Spend) AS provider_base_spend,
    SUM(Quantity) AS provider_qty
  FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
  WHERE Transaction_Date >= start_ts
    AND Transaction_Date < end_ts
    AND NOT REGEXP_CONTAINS(UPPER(Health_System_Name), r'(\bTEST\b|\bDEMO\b|PREMIER)')
    AND REGEXP_REPLACE(CAST(Ndc AS STRING), r'[^0-9]', '') IN (SELECT ndc11 FROM ndc_cohort)
    AND Premier_Entity_Code IS NOT NULL
  GROUP BY 1, 2, 3
),

-- Wholesaler aggregate (tracing/distribution via Report Builder)
wholesaler_agg AS (
  SELECT
    facility_id,
    FORMAT_TIMESTAMP('%Y-%m-01', month_year) AS month_year,
    REGEXP_REPLACE(CAST(ndc AS STRING), r'[^0-9]', '') AS ndc11,
    ANY_VALUE(health_system_name) AS wholesaler_health_system,
    ANY_VALUE(supplier) AS supplier,
    ANY_VALUE(wholesaler) AS wholesaler,
    SUM(total_spend) AS wholesaler_total_spend,
    SUM(total_units) AS wholesaler_total_units
  FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`
  WHERE month_year >= start_ts
    AND month_year < end_ts
    AND facility_id IS NOT NULL
    AND facility_id != '00'
    AND REGEXP_REPLACE(CAST(ndc AS STRING), r'[^0-9]', '') IN (SELECT ndc11 FROM ndc_cohort)
  GROUP BY 1, 2, 3
)

SELECT
  COALESCE(p.facility_id, w.facility_id) AS facility_id,
  COALESCE(p.month_year, w.month_year) AS month_year,
  COALESCE(p.ndc11, w.ndc11) AS ndc11,
  COALESCE(p.provider_health_system, w.wholesaler_health_system) AS health_system_name,
  p.manufacturer_name,
  w.supplier,
  w.wholesaler,
  -- Provider metrics
  ROUND(p.provider_landed_spend, 2) AS provider_landed_spend,
  ROUND(p.provider_base_spend, 2) AS provider_base_spend,
  p.provider_qty,
  -- Wholesaler metrics
  ROUND(w.wholesaler_total_spend, 2) AS wholesaler_total_spend,
  w.wholesaler_total_units,
  -- Coverage flags
  CASE WHEN p.facility_id IS NOT NULL AND w.facility_id IS NOT NULL THEN 'BOTH'
       WHEN p.facility_id IS NOT NULL THEN 'PROVIDER_ONLY'
       ELSE 'WHOLESALER_ONLY'
  END AS data_source_coverage,
  -- Delta metrics (where both exist)
  CASE WHEN p.provider_landed_spend IS NOT NULL AND w.wholesaler_total_spend IS NOT NULL
       THEN ROUND(p.provider_landed_spend - w.wholesaler_total_spend, 2)
       ELSE NULL
  END AS spend_delta_p_minus_w
FROM provider_agg p
FULL OUTER JOIN wholesaler_agg w
  ON p.facility_id = w.facility_id
  AND p.month_year = w.month_year
  AND p.ndc11 = w.ndc11
ORDER BY
  COALESCE(p.provider_landed_spend, 0) + COALESCE(w.wholesaler_total_spend, 0) DESC;
