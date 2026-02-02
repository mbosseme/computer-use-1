SELECT
            'product_contract_category' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT product_contract_category) as distinct_count,
            COUNTIF(product_contract_category IS NULL) as null_count,
            ARRAY_AGG(STRUCT(product_contract_category as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT product_contract_category as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'manufacturer_name' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT manufacturer_name) as distinct_count,
            COUNTIF(manufacturer_name IS NULL) as null_count,
            ARRAY_AGG(STRUCT(manufacturer_name as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT manufacturer_name as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'reference_number' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT reference_number) as distinct_count,
            COUNTIF(reference_number IS NULL) as null_count,
            ARRAY_AGG(STRUCT(reference_number as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT reference_number as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'manufacturer_catalog_number' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT manufacturer_catalog_number) as distinct_count,
            COUNTIF(manufacturer_catalog_number IS NULL) as null_count,
            ARRAY_AGG(STRUCT(manufacturer_catalog_number as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT manufacturer_catalog_number as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'product_description' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT product_description) as distinct_count,
            COUNTIF(product_description IS NULL) as null_count,
            ARRAY_AGG(STRUCT(product_description as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT product_description as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'pkg_uom' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT pkg_uom) as distinct_count,
            COUNTIF(pkg_uom IS NULL) as null_count,
            ARRAY_AGG(STRUCT(pkg_uom as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT pkg_uom as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'benchmark_median_price' as col_name,
            'FLOAT' as data_type,
            COUNT(DISTINCT benchmark_median_price) as distinct_count,
            COUNTIF(benchmark_median_price IS NULL) as null_count,
            ARRAY_AGG(STRUCT(CAST(benchmark_median_price AS STRING) as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT CAST(benchmark_median_price AS STRING) as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'benchmark_median_price_6_month' as col_name,
            'FLOAT' as data_type,
            COUNT(DISTINCT benchmark_median_price_6_month) as distinct_count,
            COUNTIF(benchmark_median_price_6_month IS NULL) as null_count,
            ARRAY_AGG(STRUCT(CAST(benchmark_median_price_6_month AS STRING) as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT CAST(benchmark_median_price_6_month AS STRING) as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'benchmark_high_price_6_month' as col_name,
            'FLOAT' as data_type,
            COUNT(DISTINCT benchmark_high_price_6_month) as distinct_count,
            COUNTIF(benchmark_high_price_6_month IS NULL) as null_count,
            ARRAY_AGG(STRUCT(CAST(benchmark_high_price_6_month AS STRING) as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT CAST(benchmark_high_price_6_month AS STRING) as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'benchmark_10th_percentile_6_month' as col_name,
            'FLOAT' as data_type,
            COUNT(DISTINCT benchmark_10th_percentile_6_month) as distinct_count,
            COUNTIF(benchmark_10th_percentile_6_month IS NULL) as null_count,
            ARRAY_AGG(STRUCT(CAST(benchmark_10th_percentile_6_month AS STRING) as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT CAST(benchmark_10th_percentile_6_month AS STRING) as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'hvi_level_2_category_code' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT hvi_level_2_category_code) as distinct_count,
            COUNTIF(hvi_level_2_category_code IS NULL) as null_count,
            ARRAY_AGG(STRUCT(hvi_level_2_category_code as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT hvi_level_2_category_code as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'hvi_level_3_category_code' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT hvi_level_3_category_code) as distinct_count,
            COUNTIF(hvi_level_3_category_code IS NULL) as null_count,
            ARRAY_AGG(STRUCT(hvi_level_3_category_code as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT hvi_level_3_category_code as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'product_id' as col_name,
            'INTEGER' as data_type,
            COUNT(DISTINCT product_id) as distinct_count,
            COUNTIF(product_id IS NULL) as null_count,
            ARRAY_AGG(STRUCT(CAST(product_id AS STRING) as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT CAST(product_id AS STRING) as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'cont_prop_65_below_thresh_det' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT cont_prop_65_below_thresh_det) as distinct_count,
            COUNTIF(cont_prop_65_below_thresh_det IS NULL) as null_count,
            ARRAY_AGG(STRUCT(cont_prop_65_below_thresh_det as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT cont_prop_65_below_thresh_det as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'description_100' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT description_100) as distinct_count,
            COUNTIF(description_100 IS NULL) as null_count,
            ARRAY_AGG(STRUCT(description_100 as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT description_100 as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'drug_case_size' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT drug_case_size) as distinct_count,
            COUNTIF(drug_case_size IS NULL) as null_count,
            ARRAY_AGG(STRUCT(drug_case_size as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT drug_case_size as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'hcpcs_description' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT hcpcs_description) as distinct_count,
            COUNTIF(hcpcs_description IS NULL) as null_count,
            ARRAY_AGG(STRUCT(hcpcs_description as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT hcpcs_description as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'is_proprietary' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT is_proprietary) as distinct_count,
            COUNTIF(is_proprietary IS NULL) as null_count,
            ARRAY_AGG(STRUCT(is_proprietary as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT is_proprietary as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        ) UNION ALL SELECT
            'lead_cadmium_organitins_free' as col_name,
            'STRING' as data_type,
            COUNT(DISTINCT lead_cadmium_organitins_free) as distinct_count,
            COUNTIF(lead_cadmium_organitins_free IS NULL) as null_count,
            ARRAY_AGG(STRUCT(lead_cadmium_organitins_free as value, count) ORDER BY count DESC LIMIT 5) as top_values
        FROM (
            SELECT lead_cadmium_organitins_free as val, COUNT(*) as count
            FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
            GROUP BY 1
        )