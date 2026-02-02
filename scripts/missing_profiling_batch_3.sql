SELECT
          'hvi_level_2_category_code' as col_name,
          'STRING' as data_type,
          COUNTIF(hvi_level_2_category_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(hvi_level_2_category_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(hvi_level_2_category_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'hvi_level_3_category_code' as col_name,
          'STRING' as data_type,
          COUNTIF(hvi_level_3_category_code IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(hvi_level_3_category_code) as distinct_count,
          APPROX_TOP_COUNT(CAST(hvi_level_3_category_code AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'product_id' as col_name,
          'INTEGER' as data_type,
          COUNTIF(product_id IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(product_id) as distinct_count,
          APPROX_TOP_COUNT(CAST(product_id AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'cont_prop_65_below_thresh_det' as col_name,
          'STRING' as data_type,
          COUNTIF(cont_prop_65_below_thresh_det IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(cont_prop_65_below_thresh_det) as distinct_count,
          APPROX_TOP_COUNT(CAST(cont_prop_65_below_thresh_det AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'description_100' as col_name,
          'STRING' as data_type,
          COUNTIF(description_100 IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(description_100) as distinct_count,
          APPROX_TOP_COUNT(CAST(description_100 AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`