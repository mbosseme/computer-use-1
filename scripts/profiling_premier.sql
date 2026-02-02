-- Batch 1: columns 1 to 40
SELECT
  'product_contract_category' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`product_contract_category` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`product_contract_category`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`product_contract_category` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'manufacturer_name' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`manufacturer_name` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`manufacturer_name`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`manufacturer_name` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'reference_number' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`reference_number` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`reference_number`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`reference_number` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'manufacturer_catalog_number' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`manufacturer_catalog_number` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`manufacturer_catalog_number`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`manufacturer_catalog_number` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'product_description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`product_description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`product_description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`product_description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'pkg_uom' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`pkg_uom` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`pkg_uom`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`pkg_uom` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'uom_conv' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`uom_conv` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`uom_conv`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`uom_conv` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_low_price' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_low_price` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_low_price`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_low_price` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_10th_percentile' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_10th_percentile` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_10th_percentile`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_10th_percentile` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_25th_percentile' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_25th_percentile` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_25th_percentile`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_25th_percentile` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_median_price' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_median_price` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_median_price`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_median_price` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_high_price' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_high_price` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_high_price`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_high_price` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_median_price_6_month' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_median_price_6_month` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_median_price_6_month`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_median_price_6_month` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_high_price_6_month' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_high_price_6_month` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_high_price_6_month`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_high_price_6_month` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_low_price_6_month' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_low_price_6_month` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_low_price_6_month`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_low_price_6_month` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_10th_percentile_6_month' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_10th_percentile_6_month` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_10th_percentile_6_month`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_10th_percentile_6_month` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'benchmark_25th_percentile_6_month' AS col_name,
  'FLOAT' AS data_type,
  COUNTIF(`benchmark_25th_percentile_6_month` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`benchmark_25th_percentile_6_month`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`benchmark_25th_percentile_6_month` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'product_group_category' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`product_group_category` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`product_group_category`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`product_group_category` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'product_subcategory1' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`product_subcategory1` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`product_subcategory1`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`product_subcategory1` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'product_subcategory2' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`product_subcategory2` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`product_subcategory2`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`product_subcategory2` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'product_subcategory3' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`product_subcategory3` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`product_subcategory3`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`product_subcategory3` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hvi_level_2_category_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hvi_level_2_category_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hvi_level_2_category_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hvi_level_2_category_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hvi_level_2_category_description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hvi_level_2_category_description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hvi_level_2_category_description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hvi_level_2_category_description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hvi_level_3_category_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hvi_level_3_category_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hvi_level_3_category_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hvi_level_3_category_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hvi_level_3_category_description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hvi_level_3_category_description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hvi_level_3_category_description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hvi_level_3_category_description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hvi_level_4_category_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hvi_level_4_category_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hvi_level_4_category_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hvi_level_4_category_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hvi_level_4_category_description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hvi_level_4_category_description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hvi_level_4_category_description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hvi_level_4_category_description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'product_id' AS col_name,
  'INTEGER' AS data_type,
  COUNTIF(`product_id` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`product_id`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`product_id` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'premier_item_number' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`premier_item_number` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`premier_item_number`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`premier_item_number` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'company_id' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`company_id` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`company_id`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`company_id` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'part_number_compressed' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`part_number_compressed` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`part_number_compressed`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`part_number_compressed` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'top_parent_entity_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`top_parent_entity_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`top_parent_entity_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`top_parent_entity_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'top_parent_name' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`top_parent_name` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`top_parent_name`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`top_parent_name` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'unspsc_description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`unspsc_description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`unspsc_description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`unspsc_description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'contracted' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`contracted` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`contracted`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`contracted` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'rx_end_date' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`rx_end_date` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`rx_end_date`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`rx_end_date` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'insert_date_time' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`insert_date_time` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`insert_date_time`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`insert_date_time` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'inserted_by_file_id' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`inserted_by_file_id` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`inserted_by_file_id`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`inserted_by_file_id` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'source_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`source_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`source_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`source_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'antibacterial_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`antibacterial_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`antibacterial_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`antibacterial_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'bisphenol_a_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`bisphenol_a_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`bisphenol_a_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`bisphenol_a_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'brand_name' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`brand_name` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`brand_name`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`brand_name` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'ca_prop_65_warning' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`ca_prop_65_warning` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`ca_prop_65_warning`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`ca_prop_65_warning` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'ca_prop_65_warning_required' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`ca_prop_65_warning_required` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`ca_prop_65_warning_required`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`ca_prop_65_warning_required` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'cons_friendly_pkg_label' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`cons_friendly_pkg_label` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`cons_friendly_pkg_label`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`cons_friendly_pkg_label` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'contract_id' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`contract_id` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`contract_id`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`contract_id` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'cont_prop_65_below_threshold' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`cont_prop_65_below_threshold` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`cont_prop_65_below_threshold`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`cont_prop_65_below_threshold` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'cont_prop_65_below_thresh_det' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`cont_prop_65_below_thresh_det` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`cont_prop_65_below_thresh_det`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`cont_prop_65_below_thresh_det` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'description_100' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`description_100` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`description_100`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`description_100` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'drug_case_size' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`drug_case_size` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`drug_case_size`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`drug_case_size` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'drug_form_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`drug_form_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`drug_form_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`drug_form_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'drug_generic_name' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`drug_generic_name` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`drug_generic_name`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`drug_generic_name` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'drug_labeler_id' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`drug_labeler_id` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`drug_labeler_id`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`drug_labeler_id` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'drug_package_size' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`drug_package_size` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`drug_package_size`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`drug_package_size` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'drug_product_wac_price' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`drug_product_wac_price` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`drug_product_wac_price`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`drug_product_wac_price` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'drug_unit_of_use' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`drug_unit_of_use` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`drug_unit_of_use`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`drug_unit_of_use` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'energy_efficient' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`energy_efficient` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`energy_efficient`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`energy_efficient` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'epp_indicator' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`epp_indicator` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`epp_indicator`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`epp_indicator` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'flame_retardant_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`flame_retardant_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`flame_retardant_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`flame_retardant_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'gtin' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`gtin` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`gtin`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`gtin` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hcpcs_description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hcpcs_description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hcpcs_description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hcpcs_description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'hcpcs_number' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`hcpcs_number` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`hcpcs_number`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`hcpcs_number` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'iec_62474_substance_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`iec_62474_substance_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`iec_62474_substance_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`iec_62474_substance_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'ingredients_declared' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`ingredients_declared` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`ingredients_declared`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`ingredients_declared` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'inner_pack_uom_quantity' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`inner_pack_uom_quantity` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`inner_pack_uom_quantity`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`inner_pack_uom_quantity` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'is_custom' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`is_custom` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`is_custom`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`is_custom` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'is_proprietary' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`is_proprietary` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`is_proprietary`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`is_proprietary` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'item_type' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`item_type` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`item_type`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`item_type` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'kit_set_pack_tray' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`kit_set_pack_tray` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`kit_set_pack_tray`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`kit_set_pack_tray` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'latex_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`latex_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`latex_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`latex_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'lead_cadmium_organitins_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`lead_cadmium_organitins_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`lead_cadmium_organitins_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`lead_cadmium_organitins_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'manufacturer_assn_pin' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`manufacturer_assn_pin` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`manufacturer_assn_pin`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`manufacturer_assn_pin` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'manufacturer_product_description' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`manufacturer_product_description` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`manufacturer_product_description`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`manufacturer_product_description` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'man_dist' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`man_dist` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`man_dist`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`man_dist` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'mercury_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`mercury_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`mercury_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`mercury_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'multi_use' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`multi_use` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`multi_use`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`multi_use` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'ndc' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`ndc` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`ndc`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`ndc` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'ndc_configuration_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`ndc_configuration_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`ndc_configuration_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`ndc_configuration_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_functional_alternative_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_functional_alternative_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_functional_alternative_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_functional_alternative_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_functional_equivalent_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_functional_equivalent_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_functional_equivalent_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_functional_equivalent_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_skey_dosage_form_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_skey_dosage_form_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_skey_dosage_form_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_skey_dosage_form_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_skey_generic' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_skey_generic` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_skey_generic`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_skey_generic` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_skey_ps' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_skey_ps` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_skey_ps`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_skey_ps` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_skey_route_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_skey_route_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_skey_route_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_skey_route_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_skey_strength_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_skey_strength_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_skey_strength_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_skey_strength_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_skey_thera' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_skey_thera` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_skey_thera`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_skey_thera` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'nddf_skey_unitdose' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`nddf_skey_unitdose` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`nddf_skey_unitdose`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`nddf_skey_unitdose` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'noun' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`noun` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`noun`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`noun` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'obsolete_date' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`obsolete_date` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`obsolete_date`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`obsolete_date` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'other_epp_attributes' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`other_epp_attributes` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`other_epp_attributes`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`other_epp_attributes` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'packaging_string' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`packaging_string` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`packaging_string`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`packaging_string` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'paper_packaging_fsc_certified' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`paper_packaging_fsc_certified` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`paper_packaging_fsc_certified`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`paper_packaging_fsc_certified` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'pbt_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`pbt_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`pbt_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`pbt_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'pediatric' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`pediatric` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`pediatric`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`pediatric` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'pediatric_indicator' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`pediatric_indicator` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`pediatric_indicator`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`pediatric_indicator` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'pfas_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`pfas_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`pfas_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`pfas_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'phthalates_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`phthalates_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`phthalates_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`phthalates_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'polystyrene_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`polystyrene_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`polystyrene_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`polystyrene_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'premier_benchmark_average' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`premier_benchmark_average` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`premier_benchmark_average`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`premier_benchmark_average` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'prim_pkg_pc_recycled' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`prim_pkg_pc_recycled` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`prim_pkg_pc_recycled`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`prim_pkg_pc_recycled` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'prim_pkg_pc_recycled_perc' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`prim_pkg_pc_recycled_perc` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`prim_pkg_pc_recycled_perc`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`prim_pkg_pc_recycled_perc` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'prim_pkg_recyclable' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`prim_pkg_recyclable` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`prim_pkg_recyclable`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`prim_pkg_recyclable` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'prim_pkg_recyclable_perc' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`prim_pkg_recyclable_perc` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`prim_pkg_recyclable_perc`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`prim_pkg_recyclable_perc` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'primary_product_image_filepath' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`primary_product_image_filepath` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`primary_product_image_filepath`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`primary_product_image_filepath` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'pvc_free' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`pvc_free` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`pvc_free`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`pvc_free` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'recyclable' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`recyclable` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`recyclable`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`recyclable` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'recyclable_content_percent' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`recyclable_content_percent` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`recyclable_content_percent`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`recyclable_content_percent` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'recy_cont_post_consumer' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`recy_cont_post_consumer` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`recy_cont_post_consumer`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`recy_cont_post_consumer` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'recy_cont_post_consumer_per' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`recy_cont_post_consumer_per` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`recy_cont_post_consumer_per`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`recy_cont_post_consumer_per` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'reprocessable' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`reprocessable` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`reprocessable`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`reprocessable` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'rohs_compliant' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`rohs_compliant` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`rohs_compliant`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`rohs_compliant` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'sec_pkg_pc_recycled' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`sec_pkg_pc_recycled` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`sec_pkg_pc_recycled`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`sec_pkg_pc_recycled` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'sec_pkg_pc_recycled_perc' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`sec_pkg_pc_recycled_perc` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`sec_pkg_pc_recycled_perc`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`sec_pkg_pc_recycled_perc` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'total_package_qty' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`total_package_qty` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`total_package_qty`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`total_package_qty` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'unspsc_category_code' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`unspsc_category_code` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`unspsc_category_code`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`unspsc_category_code` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'vend_type' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`vend_type` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`vend_type`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`vend_type` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'water_efficiency_attributes' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`water_efficiency_attributes` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`water_efficiency_attributes`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`water_efficiency_attributes` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'wooden_parts_fsc_certified' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`wooden_parts_fsc_certified` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`wooden_parts_fsc_certified`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`wooden_parts_fsc_certified` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'discontinued_reason' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`discontinued_reason` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`discontinued_reason`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`discontinued_reason` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'is_berry_compliant' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`is_berry_compliant` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`is_berry_compliant`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`is_berry_compliant` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'replaced_by_item_number' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`replaced_by_item_number` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`replaced_by_item_number`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`replaced_by_item_number` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'contract_category_key' AS col_name,
  'INTEGER' AS data_type,
  COUNTIF(`contract_category_key` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`contract_category_key`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`contract_category_key` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
UNION ALL
SELECT
  'newline' AS col_name,
  'STRING' AS data_type,
  COUNTIF(`newline` IS NULL) AS null_count,
  APPROX_COUNT_DISTINCT(`newline`) AS distinct_count,
  APPROX_TOP_COUNT(CAST(`newline` AS STRING), 5) AS top_values
FROM `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`

-- END BATCH --
