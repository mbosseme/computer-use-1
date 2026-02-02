SELECT
          'product_contract_category' as col_name,
          'STRING' as data_type,
          COUNTIF(product_contract_category IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(product_contract_category) as distinct_count,
          APPROX_TOP_COUNT(CAST(product_contract_category AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'manufacturer_name' as col_name,
          'STRING' as data_type,
          COUNTIF(manufacturer_name IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(manufacturer_name) as distinct_count,
          APPROX_TOP_COUNT(CAST(manufacturer_name AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'reference_number' as col_name,
          'STRING' as data_type,
          COUNTIF(reference_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(reference_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(reference_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'manufacturer_catalog_number' as col_name,
          'STRING' as data_type,
          COUNTIF(manufacturer_catalog_number IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(manufacturer_catalog_number) as distinct_count,
          APPROX_TOP_COUNT(CAST(manufacturer_catalog_number AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'product_description' as col_name,
          'STRING' as data_type,
          COUNTIF(product_description IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(product_description) as distinct_count,
          APPROX_TOP_COUNT(CAST(product_description AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`