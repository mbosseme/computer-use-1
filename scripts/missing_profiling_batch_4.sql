SELECT
          'drug_case_size' as col_name,
          'STRING' as data_type,
          COUNTIF(drug_case_size IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(drug_case_size) as distinct_count,
          APPROX_TOP_COUNT(CAST(drug_case_size AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'hcpcs_description' as col_name,
          'STRING' as data_type,
          COUNTIF(hcpcs_description IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(hcpcs_description) as distinct_count,
          APPROX_TOP_COUNT(CAST(hcpcs_description AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'is_proprietary' as col_name,
          'STRING' as data_type,
          COUNTIF(is_proprietary IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(is_proprietary) as distinct_count,
          APPROX_TOP_COUNT(CAST(is_proprietary AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'lead_cadmium_organitins_free' as col_name,
          'STRING' as data_type,
          COUNTIF(lead_cadmium_organitins_free IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(lead_cadmium_organitins_free) as distinct_count,
          APPROX_TOP_COUNT(CAST(lead_cadmium_organitins_free AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`