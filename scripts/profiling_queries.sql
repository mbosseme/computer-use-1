SELECT
          'month_year' as col_name,
          'TIMESTAMP' as data_type,
          COUNTIF(month_year IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(month_year) as distinct_count,
          APPROX_TOP_COUNT(CAST(month_year AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'month_num' as col_name,
          'INT64' as data_type,
          COUNTIF(month_num IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(month_num) as distinct_count,
          APPROX_TOP_COUNT(CAST(month_num AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'month' as col_name,
          'STRING' as data_type,
          COUNTIF(month IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(month) as distinct_count,
          APPROX_TOP_COUNT(CAST(month AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'quarter_num' as col_name,
          'INT64' as data_type,
          COUNTIF(quarter_num IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(quarter_num) as distinct_count,
          APPROX_TOP_COUNT(CAST(quarter_num AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'quarter' as col_name,
          'STRING' as data_type,
          COUNTIF(quarter IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(quarter) as distinct_count,
          APPROX_TOP_COUNT(CAST(quarter AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'year' as col_name,
          'INT64' as data_type,
          COUNTIF(year IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(year) as distinct_count,
          APPROX_TOP_COUNT(CAST(year AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'member_key' as col_name,
          'INT64' as data_type,
          COUNTIF(member_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(member_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(member_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility' as col_name,
          'STRING' as data_type,
          COUNTIF(facility IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_address' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_address IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_address) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_address AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_address_secondary' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_address_secondary IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_address_secondary) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_address_secondary AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_city' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_city IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_city) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_city AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_dea' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_dea IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_dea) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_dea AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_direct_parent_key' as col_name,
          'INT64' as data_type,
          COUNTIF(facility_direct_parent_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_direct_parent_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_direct_parent_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_direct_parent' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_direct_parent IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_direct_parent) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_direct_parent AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_direct_parent_id' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_direct_parent_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_direct_parent_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_direct_parent_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_direct_parent_name' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_direct_parent_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_direct_parent_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_direct_parent_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_id' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_hin' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_hin IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_hin) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_hin AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_name' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_state' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_state IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_state) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_state AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_zip_code' as col_name,
          'STRING' as data_type,
          COUNTIF(facility_zip_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_zip_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_zip_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'member_top_parent_key' as col_name,
          'INT64' as data_type,
          COUNTIF(member_top_parent_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(member_top_parent_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(member_top_parent_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_address' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_address IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_address) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_address AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_address_secondary' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_address_secondary IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_address_secondary) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_address_secondary AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_city' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_city IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_city) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_city AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_dea' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_dea IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_dea) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_dea AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_id' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_hin' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_hin IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_hin) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_hin AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_name' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_state' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_state IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_state) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_state AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'health_system_zip_code' as col_name,
          'STRING' as data_type,
          COUNTIF(health_system_zip_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(health_system_zip_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(health_system_zip_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'additional_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(additional_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(additional_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(additional_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_code' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier1' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier1 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier1) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier1 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier1_code' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier1_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier1_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier1_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier1_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier1_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier1_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier1_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier2' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier2 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier2) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier2 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier2_code' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier2_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier2_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier2_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`

--- BATCH SEPARATOR ---

SELECT
          'ahfs_tier2_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier2_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier2_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier2_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier3' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier3 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier3) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier3 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier3_code' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier3_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier3_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier3_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier3_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier3_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier3_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier3_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier4' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier4 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier4) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier4 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier4_code' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier4_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier4_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier4_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ahfs_tier4_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(ahfs_tier4_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ahfs_tier4_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(ahfs_tier4_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'brand_name' as col_name,
          'STRING' as data_type,
          COUNTIF(brand_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(brand_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(brand_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'case_size' as col_name,
          'INT64' as data_type,
          COUNTIF(case_size IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(case_size) as distinct_count,
          APPROX_TOP_COUNT(CAST(case_size AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'contract_lead_key' as col_name,
          'INT64' as data_type,
          COUNTIF(contract_lead_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(contract_lead_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(contract_lead_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'contract_lead_name' as col_name,
          'STRING' as data_type,
          COUNTIF(contract_lead_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(contract_lead_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(contract_lead_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'cost_of_distribution' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(cost_of_distribution IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(cost_of_distribution) as distinct_count,
          APPROX_TOP_COUNT(CAST(cost_of_distribution AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'distribution_center_name' as col_name,
          'STRING' as data_type,
          COUNTIF(distribution_center_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(distribution_center_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(distribution_center_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'dosage_form_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(dosage_form_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(dosage_form_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(dosage_form_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'drug_class' as col_name,
          'STRING' as data_type,
          COUNTIF(drug_class IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(drug_class) as distinct_count,
          APPROX_TOP_COUNT(CAST(drug_class AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'drug_form_code' as col_name,
          'STRING' as data_type,
          COUNTIF(drug_form_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(drug_form_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(drug_form_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'drug_id_22' as col_name,
          'STRING' as data_type,
          COUNTIF(drug_id_22 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(drug_id_22) as distinct_count,
          APPROX_TOP_COUNT(CAST(drug_id_22 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'drug_id_24' as col_name,
          'STRING' as data_type,
          COUNTIF(drug_id_24 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(drug_id_24) as distinct_count,
          APPROX_TOP_COUNT(CAST(drug_id_24 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'drug_id_37' as col_name,
          'STRING' as data_type,
          COUNTIF(drug_id_37 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(drug_id_37) as distinct_count,
          APPROX_TOP_COUNT(CAST(drug_id_37 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'drug_id_38' as col_name,
          'STRING' as data_type,
          COUNTIF(drug_id_38 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(drug_id_38) as distinct_count,
          APPROX_TOP_COUNT(CAST(drug_id_38 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'dsh_id' as col_name,
          'STRING' as data_type,
          COUNTIF(dsh_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(dsh_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(dsh_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'gcn_sequence_number' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(gcn_sequence_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(gcn_sequence_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(gcn_sequence_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'generic_name' as col_name,
          'STRING' as data_type,
          COUNTIF(generic_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(generic_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(generic_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'hic_code' as col_name,
          'STRING' as data_type,
          COUNTIF(hic_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(hic_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(hic_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'hic_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(hic_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(hic_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(hic_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'invoice_date' as col_name,
          'STRING' as data_type,
          COUNTIF(invoice_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(invoice_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(invoice_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'invoice_number' as col_name,
          'STRING' as data_type,
          COUNTIF(invoice_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(invoice_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(invoice_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'invoice_price' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(invoice_price IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(invoice_price) as distinct_count,
          APPROX_TOP_COUNT(CAST(invoice_price AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'label_name' as col_name,
          'STRING' as data_type,
          COUNTIF(label_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(label_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(label_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'labeler_id' as col_name,
          'STRING' as data_type,
          COUNTIF(labeler_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(labeler_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(labeler_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'line_number_from_invoice' as col_name,
          'STRING' as data_type,
          COUNTIF(line_number_from_invoice IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(line_number_from_invoice) as distinct_count,
          APPROX_TOP_COUNT(CAST(line_number_from_invoice AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'charge_bk_key' as col_name,
          'INT64' as data_type,
          COUNTIF(charge_bk_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(charge_bk_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(charge_bk_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'manufacturer_chargeback_id' as col_name,
          'STRING' as data_type,
          COUNTIF(manufacturer_chargeback_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(manufacturer_chargeback_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(manufacturer_chargeback_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ncpdp' as col_name,
          'STRING' as data_type,
          COUNTIF(ncpdp IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ncpdp) as distinct_count,
          APPROX_TOP_COUNT(CAST(ncpdp AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ndc' as col_name,
          'STRING' as data_type,
          COUNTIF(ndc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ndc) as distinct_count,
          APPROX_TOP_COUNT(CAST(ndc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'npi' as col_name,
          'STRING' as data_type,
          COUNTIF(npi IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(npi) as distinct_count,
          APPROX_TOP_COUNT(CAST(npi AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'obsolete_date' as col_name,
          'STRING' as data_type,
          COUNTIF(obsolete_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(obsolete_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(obsolete_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'orange_book_code' as col_name,
          'STRING' as data_type,
          COUNTIF(orange_book_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(orange_book_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(orange_book_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'order_date' as col_name,
          'STRING' as data_type,
          COUNTIF(order_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(order_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(order_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'original_invoice_number' as col_name,
          'STRING' as data_type,
          COUNTIF(original_invoice_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(original_invoice_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(original_invoice_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`

--- BATCH SEPARATOR ---

SELECT
          'pkg_desc' as col_name,
          'STRING' as data_type,
          COUNTIF(pkg_desc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(pkg_desc) as distinct_count,
          APPROX_TOP_COUNT(CAST(pkg_desc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'pkg_qty' as col_name,
          'STRING' as data_type,
          COUNTIF(pkg_qty IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(pkg_qty) as distinct_count,
          APPROX_TOP_COUNT(CAST(pkg_qty AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'pkg_size' as col_name,
          'STRING' as data_type,
          COUNTIF(pkg_size IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(pkg_size) as distinct_count,
          APPROX_TOP_COUNT(CAST(pkg_size AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'premier_fillrate' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(premier_fillrate IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(premier_fillrate) as distinct_count,
          APPROX_TOP_COUNT(CAST(premier_fillrate AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'award_status_key' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(award_status_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(award_status_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(award_status_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'premier_award_status' as col_name,
          'STRING' as data_type,
          COUNTIF(premier_award_status IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(premier_award_status) as distinct_count,
          APPROX_TOP_COUNT(CAST(premier_award_status AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'Premier_contract_number' as col_name,
          'STRING' as data_type,
          COUNTIF(Premier_contract_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(Premier_contract_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(Premier_contract_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'premier_contract_unit_price' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(premier_contract_unit_price IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(premier_contract_unit_price) as distinct_count,
          APPROX_TOP_COUNT(CAST(premier_contract_unit_price AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'premier_reason_code' as col_name,
          'STRING' as data_type,
          COUNTIF(premier_reason_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(premier_reason_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(premier_reason_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'premier_relation' as col_name,
          'STRING' as data_type,
          COUNTIF(premier_relation IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(premier_relation) as distinct_count,
          APPROX_TOP_COUNT(CAST(premier_relation AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'member_top_corp_parent_id' as col_name,
          'STRING' as data_type,
          COUNTIF(member_top_corp_parent_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(member_top_corp_parent_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(member_top_corp_parent_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'member_top_corp_parent_name' as col_name,
          'STRING' as data_type,
          COUNTIF(member_top_corp_parent_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(member_top_corp_parent_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(member_top_corp_parent_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'price_effective_date' as col_name,
          'STRING' as data_type,
          COUNTIF(price_effective_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(price_effective_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(price_effective_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'price_expiration_date' as col_name,
          'STRING' as data_type,
          COUNTIF(price_expiration_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(price_expiration_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(price_expiration_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'qa_oid' as col_name,
          'INT64' as data_type,
          COUNTIF(qa_oid IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(qa_oid) as distinct_count,
          APPROX_TOP_COUNT(CAST(qa_oid AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'price_type_code' as col_name,
          'STRING' as data_type,
          COUNTIF(price_type_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(price_type_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(price_type_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'route' as col_name,
          'STRING' as data_type,
          COUNTIF(route IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(route) as distinct_count,
          APPROX_TOP_COUNT(CAST(route AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'provider_class_id' as col_name,
          'INT64' as data_type,
          COUNTIF(provider_class_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(provider_class_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(provider_class_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'service_provider_class' as col_name,
          'STRING' as data_type,
          COUNTIF(service_provider_class IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(service_provider_class) as distinct_count,
          APPROX_TOP_COUNT(CAST(service_provider_class AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'ship_method' as col_name,
          'STRING' as data_type,
          COUNTIF(ship_method IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(ship_method) as distinct_count,
          APPROX_TOP_COUNT(CAST(ship_method AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'shipping_date' as col_name,
          'STRING' as data_type,
          COUNTIF(shipping_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(shipping_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(shipping_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'strength' as col_name,
          'STRING' as data_type,
          COUNTIF(strength IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(strength) as distinct_count,
          APPROX_TOP_COUNT(CAST(strength AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'supplier' as col_name,
          'STRING' as data_type,
          COUNTIF(supplier IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(supplier) as distinct_count,
          APPROX_TOP_COUNT(CAST(supplier AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'supplier_wac' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(supplier_wac IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(supplier_wac) as distinct_count,
          APPROX_TOP_COUNT(CAST(supplier_wac AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'supplier_wac_effective_date' as col_name,
          'STRING' as data_type,
          COUNTIF(supplier_wac_effective_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(supplier_wac_effective_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(supplier_wac_effective_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'tier_effective_date' as col_name,
          'STRING' as data_type,
          COUNTIF(tier_effective_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(tier_effective_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(tier_effective_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'tier_expiration_date' as col_name,
          'STRING' as data_type,
          COUNTIF(tier_expiration_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(tier_expiration_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(tier_expiration_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'unit_dose' as col_name,
          'STRING' as data_type,
          COUNTIF(unit_dose IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(unit_dose) as distinct_count,
          APPROX_TOP_COUNT(CAST(unit_dose AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'unit_of_measure' as col_name,
          'STRING' as data_type,
          COUNTIF(unit_of_measure IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(unit_of_measure) as distinct_count,
          APPROX_TOP_COUNT(CAST(unit_of_measure AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'upc_key' as col_name,
          'INT64' as data_type,
          COUNTIF(upc_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(upc_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(upc_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'upc' as col_name,
          'STRING' as data_type,
          COUNTIF(upc IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(upc) as distinct_count,
          APPROX_TOP_COUNT(CAST(upc AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'upn_key' as col_name,
          'INT64' as data_type,
          COUNTIF(upn_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(upn_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(upn_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'upn' as col_name,
          'STRING' as data_type,
          COUNTIF(upn IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(upn) as distinct_count,
          APPROX_TOP_COUNT(CAST(upn AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_id' as col_name,
          'INT64' as data_type,
          COUNTIF(wholesaler_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_account_attribute' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler_account_attribute IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_account_attribute) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_account_attribute AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_account_name' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler_account_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_account_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_account_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'facility_account_key' as col_name,
          'INT64' as data_type,
          COUNTIF(facility_account_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(facility_account_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(facility_account_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_account_number' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler_account_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_account_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_account_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_catalog_number' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler_catalog_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_catalog_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_catalog_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`

--- BATCH SEPARATOR ---

SELECT
          'whsl_charge_bk_key' as col_name,
          'INT64' as data_type,
          COUNTIF(whsl_charge_bk_key IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(whsl_charge_bk_key) as distinct_count,
          APPROX_TOP_COUNT(CAST(whsl_charge_bk_key AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_chargeback_id' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler_chargeback_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_chargeback_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_chargeback_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_invoice_wac' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(wholesaler_invoice_wac IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_invoice_wac) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_invoice_wac AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_load_price' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(wholesaler_load_price IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_load_price) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_load_price AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_order_line_number' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler_order_line_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_order_line_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_order_line_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_pkg_qty' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(wholesaler_pkg_qty IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_pkg_qty) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_pkg_qty AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'whsl_purch_type_code' as col_name,
          'STRING' as data_type,
          COUNTIF(whsl_purch_type_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(whsl_purch_type_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(whsl_purch_type_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wholesaler_purchase_type' as col_name,
          'STRING' as data_type,
          COUNTIF(wholesaler_purchase_type IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wholesaler_purchase_type) as distinct_count,
          APPROX_TOP_COUNT(CAST(wholesaler_purchase_type AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          't340b_id' as col_name,
          'STRING' as data_type,
          COUNTIF(t340b_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(t340b_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(t340b_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'consignment' as col_name,
          'STRING' as data_type,
          COUNTIF(consignment IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(consignment) as distinct_count,
          APPROX_TOP_COUNT(CAST(consignment AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'dea_code' as col_name,
          'STRING' as data_type,
          COUNTIF(dea_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(dea_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(dea_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'quantity_ordered' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(quantity_ordered IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(quantity_ordered) as distinct_count,
          APPROX_TOP_COUNT(CAST(quantity_ordered AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'on_contract_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(on_contract_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(on_contract_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(on_contract_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'on_contract_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(on_contract_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(on_contract_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(on_contract_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'off_contract_exact_and_equiv_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(off_contract_exact_and_equiv_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(off_contract_exact_and_equiv_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(off_contract_exact_and_equiv_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'off_contract_exact_and_equiv_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(off_contract_exact_and_equiv_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(off_contract_exact_and_equiv_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(off_contract_exact_and_equiv_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'off_exact_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(off_exact_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(off_exact_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(off_exact_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'off_exact_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(off_exact_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(off_exact_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(off_exact_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'off_equivalent_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(off_equivalent_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(off_equivalent_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(off_equivalent_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'off_equivalent_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(off_equivalent_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(off_equivalent_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(off_equivalent_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'non_contract_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(non_contract_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(non_contract_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(non_contract_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'non_contract_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(non_contract_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(non_contract_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(non_contract_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wac_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(wac_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wac_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(wac_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'wac_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(wac_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(wac_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(wac_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          't340b_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(t340b_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(t340b_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(t340b_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          't340b_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(t340b_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(t340b_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(t340b_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'total_units_excluding_340b_wac' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(total_units_excluding_340b_wac IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(total_units_excluding_340b_wac) as distinct_count,
          APPROX_TOP_COUNT(CAST(total_units_excluding_340b_wac AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'total_spend_excluding_340b_wac' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(total_spend_excluding_340b_wac IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(total_spend_excluding_340b_wac) as distinct_count,
          APPROX_TOP_COUNT(CAST(total_spend_excluding_340b_wac AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'total_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(total_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(total_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(total_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'total_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(total_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(total_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(total_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'last_price_paid' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(last_price_paid IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(last_price_paid) as distinct_count,
          APPROX_TOP_COUNT(CAST(last_price_paid AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'last_price_paid_date' as col_name,
          'STRING' as data_type,
          COUNTIF(last_price_paid_date IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(last_price_paid_date) as distinct_count,
          APPROX_TOP_COUNT(CAST(last_price_paid_date AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'unknown_quantity_ordered' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(unknown_quantity_ordered IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(unknown_quantity_ordered) as distinct_count,
          APPROX_TOP_COUNT(CAST(unknown_quantity_ordered AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'unknown_units' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(unknown_units IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(unknown_units) as distinct_count,
          APPROX_TOP_COUNT(CAST(unknown_units AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'unknown_spend' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(unknown_spend IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(unknown_spend) as distinct_count,
          APPROX_TOP_COUNT(CAST(unknown_spend AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'total_quantity_ordered_includes_unknowns' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(total_quantity_ordered_includes_unknowns IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(total_quantity_ordered_includes_unknowns) as distinct_count,
          APPROX_TOP_COUNT(CAST(total_quantity_ordered_includes_unknowns AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'total_units_ordered_includes_unknowns' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(total_units_ordered_includes_unknowns IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(total_units_ordered_includes_unknowns) as distinct_count,
          APPROX_TOP_COUNT(CAST(total_units_ordered_includes_unknowns AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` UNION ALL SELECT
          'total_spend_ordered_includes_unknowns' as col_name,
          'FLOAT64' as data_type,
          COUNTIF(total_spend_ordered_includes_unknowns IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(total_spend_ordered_includes_unknowns) as distinct_count,
          APPROX_TOP_COUNT(CAST(total_spend_ordered_includes_unknowns AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`

--- BATCH SEPARATOR ---

