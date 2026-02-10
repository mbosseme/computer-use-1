WITH invoice_stats AS (
  SELECT 
    health_system_entity_code,
    EXTRACT(QUARTER FROM vendor_invoice_date) as quarter,
    SUM(invoice_total_amount) as invoice_spend,
    COUNT(DISTINCT facility_entity_code) as invoice_facility_cnt
  FROM `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
  WHERE EXTRACT(YEAR FROM vendor_invoice_date) = 2025
  GROUP BY 1, 2
),
txn_stats AS (
  SELECT
    Health_System_Entity_Code as health_system_entity_code,
    EXTRACT(QUARTER FROM Transaction_Date) as quarter,
    SUM(Base_Spend) as txn_spend,
    COUNT(DISTINCT Facility_Code) as txn_facility_cnt
  FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
  WHERE EXTRACT(YEAR FROM Transaction_Date) = 2025
  GROUP BY 1, 2
)
SELECT
  COALESCE(i.health_system_entity_code, t.health_system_entity_code) as health_system_entity_code,
  COALESCE(i.quarter, t.quarter) as quarter,
  i.invoice_spend,
  t.txn_spend,
  i.invoice_facility_cnt,
  t.txn_facility_cnt,
  -- Calculate differences
  (i.invoice_spend - t.txn_spend) as spend_diff,
  SAFE_DIVIDE(i.invoice_spend, t.txn_spend) as spend_ratio_inv_to_txn
FROM invoice_stats i
FULL OUTER JOIN txn_stats t
  ON i.health_system_entity_code = t.health_system_entity_code
  AND i.quarter = t.quarter
ORDER BY 1, 2;
