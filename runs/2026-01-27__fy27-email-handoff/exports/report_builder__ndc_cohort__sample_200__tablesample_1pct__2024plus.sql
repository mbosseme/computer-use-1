-- Wholesaler-side sample extract for Jen's NDC cohort (derived from PDF list)
-- Notes:
-- - PDF list was parsed as 10-digit digits-only NDCs; report_builder.ndc appears to store 11-digit NDCs.
-- - Normalization applied here: insert '0' after first 5 digits (5-3-2 => 5-4-2).
-- - Uses TABLESAMPLE to keep scan cost bounded (not exhaustive).

WITH ndc10_list AS (
  SELECT ndc10 FROM UNNEST([
    '6332317876','6332353075','6332362600','6332362610','6332362625','6332362650','6332362655','6332366710','6332366910','6332368310','6332368610','6332368810','6332382474','6332382475','6332382476','6332386710','6332386774','6332386910','6332386974','6332386975','6332387010','6332387074','6332387310','6332387374','6332387375','6521900401','6521900601','6521900851','6521901001','6521901201','6521911810','6521911910','6521914210','6521914410','6521914610','6521914810','6521915075','6521915310','6521921850','6521922010','6521922225','6521922450','6521923410','6521923610','6521923825','6521924050','6521924110','6521924350','6521924610','6521925810','6521938905','6521938910','6521945660','6521945830','6521946020','6521946210','6521946450','6521946660','6521946850','6521947030','6521947220','6521947410','6521947530','6521947720','6521947910','6521949510','6521949720','6521949930','6521950210','6521950420','6521950630'
  ]) AS ndc10
), ndc_list AS (
  SELECT CONCAT(SUBSTR(ndc10, 1, 5), '0', SUBSTR(ndc10, 6)) AS ndc
  FROM ndc10_list
)
SELECT
  month_year,
  facility_id,
  facility_state,
  member_top_corp_parent_name,
  ndc,
  label_name,
  supplier,
  wholesaler,
  wholesaler_purchase_type,
  premier_award_status,
  total_spend,
  total_units
FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`
  TABLESAMPLE SYSTEM (1 PERCENT)
WHERE ndc IN (SELECT ndc FROM ndc_list)
  AND month_year >= TIMESTAMP('2024-01-01')
ORDER BY month_year DESC, total_spend DESC
LIMIT 200;
