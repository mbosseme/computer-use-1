SELECT
          'pkg_uom' as col_name,
          'STRING' as data_type,
          COUNTIF(pkg_uom IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(pkg_uom) as distinct_count,
          APPROX_TOP_COUNT(CAST(pkg_uom AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'benchmark_median_price' as col_name,
          'FLOAT' as data_type,
          COUNTIF(benchmark_median_price IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(benchmark_median_price) as distinct_count,
          APPROX_TOP_COUNT(CAST(benchmark_median_price AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'benchmark_median_price_6_month' as col_name,
          'FLOAT' as data_type,
          COUNTIF(benchmark_median_price_6_month IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(benchmark_median_price_6_month) as distinct_count,
          APPROX_TOP_COUNT(CAST(benchmark_median_price_6_month AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'benchmark_high_price_6_month' as col_name,
          'FLOAT' as data_type,
          COUNTIF(benchmark_high_price_6_month IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(benchmark_high_price_6_month) as distinct_count,
          APPROX_TOP_COUNT(CAST(benchmark_high_price_6_month AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master` UNION ALL SELECT
          'benchmark_10th_percentile_6_month' as col_name,
          'FLOAT' as data_type,
          COUNTIF(benchmark_10th_percentile_6_month IS NULL) as null_count,
          APPROX_COUNT_DISTINCT(benchmark_10th_percentile_6_month) as distinct_count,
          APPROX_TOP_COUNT(CAST(benchmark_10th_percentile_6_month AS STRING), 5) as top_values
        FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`