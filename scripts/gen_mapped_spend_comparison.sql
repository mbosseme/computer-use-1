
/*
 * GEN_MAPPED_SPEND_COMPARISON.SQL
 * 
 * Purpose: Compare spend for specifically mapped Health Systems between Workflow History and TSA.
 * Strategy: Use a UNION ALL approach with hardcoded mapping logic to ensure precision.
 */

WITH workflow_spend AS (
    SELECT 
        CASE 
            WHEN health_system_name = 'Advocate Health' THEN 'ADVOCATE'
            WHEN health_system_name = 'AdventHealth (AHS Florida)' THEN 'ADVENTHEALTH'
            WHEN health_system_name = 'EM_OSF' THEN 'OSF'
            WHEN health_system_name = 'EM_UHS' THEN 'UHS'
            WHEN health_system_name = 'EM_Renown' THEN 'RENOWN'
            WHEN health_system_name = 'Adventist Health (California HQ)' THEN 'ADVENTIST'
            WHEN health_system_name = 'EM_HonorHealth' THEN 'HONORHEALTH'
            WHEN health_system_name = 'EM_Fletcher' THEN 'UVM'
            WHEN health_system_name = 'EM_UCI' THEN 'UCI'
            ELSE 'OTHER' 
        END as mapping_key,
        health_system_name as wf_name,
        SUM(invoice_total_amount) as wf_spend
    FROM `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
    WHERE EXTRACT(YEAR FROM vendor_invoice_date) = 2025
    AND health_system_name IN (
        'Advocate Health',
        'AdventHealth (AHS Florida)',
        'EM_OSF',
        'EM_UHS',
        'EM_Renown',
        'Adventist Health (California HQ)',
        'EM_HonorHealth',
        'EM_Fletcher',
        'EM_UCI'
    )
    GROUP BY 1, 2
),

tsa_spend AS (
    SELECT 
        -- Hardcoded Mapping Logic for TSA
        CASE 
            WHEN Health_System_Name = 'ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE' THEN 'ADVOCATE'
            WHEN Health_System_Name = 'ADVENTHEALTH' THEN 'ADVENTHEALTH'
            WHEN Health_System_Name = 'OSF HEALTHCARE SYSTEM' THEN 'OSF'
            WHEN Health_System_Name = 'UHS OF DELAWARE, INC.' THEN 'UHS'
            WHEN Health_System_Name = 'RENOWN HEALTH' THEN 'RENOWN'
            WHEN Health_System_Name = 'ADVENTIST HEALTH' THEN 'ADVENTIST'
            WHEN Health_System_Name = 'HONORHEALTH' THEN 'HONORHEALTH'
            WHEN Direct_Parent_Name = 'THE UNIVERSITY OF VERMONT HEALTH NETWORK' THEN 'UVM'
            WHEN Health_System_Name = 'UNIVERSITY OF CALIFORNIA - IRVINE' THEN 'UCI'
        END as mapping_key,
        SUM(Landed_Spend) as tsa_spend
    FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
    WHERE EXTRACT(YEAR FROM Transaction_Date) = 2025
    AND (
        Health_System_Name IN (
            'ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE',
            'ADVENTHEALTH',
            'OSF HEALTHCARE SYSTEM',
            'UHS OF DELAWARE, INC.',
            'RENOWN HEALTH',
            'ADVENTIST HEALTH',
            'HONORHEALTH',
            'UNIVERSITY OF CALIFORNIA - IRVINE'
        )
        OR Direct_Parent_Name = 'THE UNIVERSITY OF VERMONT HEALTH NETWORK'
    )
    GROUP BY 1
)

SELECT 
    w.mapping_key,
    w.wf_name,
    w.wf_spend,
    t.tsa_spend,
    (w.wf_spend - t.tsa_spend) as variance_dollars,
    SAFE_DIVIDE(w.wf_spend, t.tsa_spend) as capture_ratio
FROM workflow_spend w
LEFT JOIN tsa_spend t ON w.mapping_key = t.mapping_key
ORDER BY w.wf_spend DESC
