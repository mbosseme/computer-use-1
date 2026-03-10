import json

cols_json = """
{"column_name":"month_year","data_type":"TIMESTAMP"}
{"column_name":"month_num","data_type":"INT64"}
{"column_name":"month","data_type":"STRING"}
{"column_name":"quarter_num","data_type":"INT64"}
{"column_name":"quarter","data_type":"STRING"}
{"column_name":"year","data_type":"INT64"}
{"column_name":"member_key","data_type":"INT64"}
{"column_name":"facility","data_type":"STRING"}
{"column_name":"facility_address","data_type":"STRING"}
{"column_name":"facility_address_secondary","data_type":"STRING"}
{"column_name":"facility_city","data_type":"STRING"}
{"column_name":"facility_dea","data_type":"STRING"}
{"column_name":"facility_direct_parent_key","data_type":"INT64"}
{"column_name":"facility_direct_parent","data_type":"STRING"}
{"column_name":"facility_direct_parent_id","data_type":"STRING"}
{"column_name":"facility_direct_parent_name","data_type":"STRING"}
{"column_name":"facility_id","data_type":"STRING"}
{"column_name":"facility_hin","data_type":"STRING"}
{"column_name":"facility_name","data_type":"STRING"}
{"column_name":"facility_state","data_type":"STRING"}
{"column_name":"facility_zip_code","data_type":"STRING"}
{"column_name":"member_top_parent_key","data_type":"INT64"}
{"column_name":"health_system","data_type":"STRING"}
{"column_name":"health_system_address","data_type":"STRING"}
{"column_name":"health_system_address_secondary","data_type":"STRING"}
{"column_name":"health_system_city","data_type":"STRING"}
{"column_name":"health_system_dea","data_type":"STRING"}
{"column_name":"health_system_id","data_type":"STRING"}
{"column_name":"health_system_hin","data_type":"STRING"}
{"column_name":"health_system_name","data_type":"STRING"}
{"column_name":"health_system_state","data_type":"STRING"}
{"column_name":"health_system_zip_code","data_type":"STRING"}
{"column_name":"additional_desc","data_type":"STRING"}
{"column_name":"ahfs_code","data_type":"STRING"}
{"column_name":"ahfs_desc","data_type":"STRING"}
{"column_name":"ahfs_tier1","data_type":"STRING"}
{"column_name":"ahfs_tier1_code","data_type":"STRING"}
{"column_name":"ahfs_tier1_desc","data_type":"STRING"}
{"column_name":"ahfs_tier2","data_type":"STRING"}
{"column_name":"ahfs_tier2_code","data_type":"STRING"}
{"column_name":"ahfs_tier2_desc","data_type":"STRING"}
{"column_name":"ahfs_tier3","data_type":"STRING"}
{"column_name":"ahfs_tier3_code","data_type":"STRING"}
{"column_name":"ahfs_tier3_desc","data_type":"STRING"}
{"column_name":"ahfs_tier4","data_type":"STRING"}
{"column_name":"ahfs_tier4_code","data_type":"STRING"}
{"column_name":"ahfs_tier4_desc","data_type":"STRING"}
{"column_name":"brand_name","data_type":"STRING"}
{"column_name":"case_size","data_type":"INT64"}
{"column_name":"contract_lead_key","data_type":"INT64"}
{"column_name":"contract_lead_name","data_type":"STRING"}
{"column_name":"cost_of_distribution","data_type":"FLOAT64"}
{"column_name":"distribution_center_name","data_type":"STRING"}
{"column_name":"dosage_form_desc","data_type":"STRING"}
{"column_name":"drug_class","data_type":"STRING"}
{"column_name":"drug_form_code","data_type":"STRING"}
{"column_name":"drug_id_22","data_type":"STRING"}
{"column_name":"drug_id_24","data_type":"STRING"}
{"column_name":"drug_id_37","data_type":"STRING"}
{"column_name":"drug_id_38","data_type":"STRING"}
{"column_name":"dsh_id","data_type":"STRING"}
{"column_name":"gcn_sequence_number","data_type":"FLOAT64"}
{"column_name":"generic_name","data_type":"STRING"}
{"column_name":"hic_code","data_type":"STRING"}
{"column_name":"hic_desc","data_type":"STRING"}
{"column_name":"invoice_date","data_type":"STRING"}
{"column_name":"invoice_number","data_type":"STRING"}
{"column_name":"invoice_price","data_type":"FLOAT64"}
{"column_name":"label_name","data_type":"STRING"}
{"column_name":"labeler_id","data_type":"STRING"}
{"column_name":"line_number_from_invoice","data_type":"STRING"}
{"column_name":"charge_bk_key","data_type":"INT64"}
{"column_name":"manufacturer_chargeback_id","data_type":"STRING"}
{"column_name":"ncpdp","data_type":"STRING"}
{"column_name":"ndc","data_type":"STRING"}
{"column_name":"npi","data_type":"STRING"}
{"column_name":"obsolete_date","data_type":"STRING"}
{"column_name":"orange_book_code","data_type":"STRING"}
{"column_name":"order_date","data_type":"STRING"}
{"column_name":"original_invoice_number","data_type":"STRING"}
{"column_name":"pkg_desc","data_type":"STRING"}
{"column_name":"pkg_qty","data_type":"STRING"}
{"column_name":"pkg_size","data_type":"STRING"}
{"column_name":"premier_fillrate","data_type":"FLOAT64"}
{"column_name":"award_status_key","data_type":"FLOAT64"}
{"column_name":"premier_award_status","data_type":"STRING"}
{"column_name":"Premier_contract_number","data_type":"STRING"}
{"column_name":"premier_contract_unit_price","data_type":"FLOAT64"}
{"column_name":"premier_reason_code","data_type":"STRING"}
{"column_name":"premier_relation","data_type":"STRING"}
{"column_name":"member_top_corp_parent_id","data_type":"STRING"}
{"column_name":"member_top_corp_parent_name","data_type":"STRING"}
{"column_name":"price_effective_date","data_type":"STRING"}
{"column_name":"price_expiration_date","data_type":"STRING"}
{"column_name":"qa_oid","data_type":"INT64"}
{"column_name":"price_type_code","data_type":"STRING"}
{"column_name":"route","data_type":"STRING"}
{"column_name":"provider_class_id","data_type":"INT64"}
{"column_name":"service_provider_class","data_type":"STRING"}
{"column_name":"ship_method","data_type":"STRING"}
{"column_name":"shipping_date","data_type":"STRING"}
{"column_name":"strength","data_type":"STRING"}
{"column_name":"supplier","data_type":"STRING"}
{"column_name":"supplier_wac","data_type":"FLOAT64"}
{"column_name":"supplier_wac_effective_date","data_type":"STRING"}
{"column_name":"tier_effective_date","data_type":"STRING"}
{"column_name":"tier_expiration_date","data_type":"STRING"}
{"column_name":"unit_dose","data_type":"STRING"}
{"column_name":"unit_of_measure","data_type":"STRING"}
{"column_name":"upc_key","data_type":"INT64"}
{"column_name":"upc","data_type":"STRING"}
{"column_name":"upn_key","data_type":"INT64"}
{"column_name":"upn","data_type":"STRING"}
{"column_name":"wholesaler_id","data_type":"INT64"}
{"column_name":"wholesaler","data_type":"STRING"}
{"column_name":"wholesaler_account_attribute","data_type":"STRING"}
{"column_name":"wholesaler_account_name","data_type":"STRING"}
{"column_name":"facility_account_key","data_type":"INT64"}
{"column_name":"wholesaler_account_number","data_type":"STRING"}
{"column_name":"wholesaler_catalog_number","data_type":"STRING"}
{"column_name":"whsl_charge_bk_key","data_type":"INT64"}
{"column_name":"wholesaler_chargeback_id","data_type":"STRING"}
{"column_name":"wholesaler_invoice_wac","data_type":"FLOAT64"}
{"column_name":"wholesaler_load_price","data_type":"FLOAT64"}
{"column_name":"wholesaler_order_line_number","data_type":"STRING"}
{"column_name":"wholesaler_pkg_qty","data_type":"FLOAT64"}
{"column_name":"whsl_purch_type_code","data_type":"STRING"}
{"column_name":"wholesaler_purchase_type","data_type":"STRING"}
{"column_name":"t340b_id","data_type":"STRING"}
{"column_name":"consignment","data_type":"STRING"}
{"column_name":"dea_code","data_type":"STRING"}
{"column_name":"quantity_ordered","data_type":"FLOAT64"}
{"column_name":"on_contract_units","data_type":"FLOAT64"}
{"column_name":"on_contract_spend","data_type":"FLOAT64"}
{"column_name":"off_contract_exact_and_equiv_units","data_type":"FLOAT64"}
{"column_name":"off_contract_exact_and_equiv_spend","data_type":"FLOAT64"}
{"column_name":"off_exact_units","data_type":"FLOAT64"}
{"column_name":"off_exact_spend","data_type":"FLOAT64"}
{"column_name":"off_equivalent_units","data_type":"FLOAT64"}
{"column_name":"off_equivalent_spend","data_type":"FLOAT64"}
{"column_name":"non_contract_units","data_type":"FLOAT64"}
{"column_name":"non_contract_spend","data_type":"FLOAT64"}
{"column_name":"wac_units","data_type":"FLOAT64"}
{"column_name":"wac_spend","data_type":"FLOAT64"}
{"column_name":"t340b_units","data_type":"FLOAT64"}
{"column_name":"t340b_spend","data_type":"FLOAT64"}
{"column_name":"total_units_excluding_340b_wac","data_type":"FLOAT64"}
{"column_name":"total_spend_excluding_340b_wac","data_type":"FLOAT64"}
{"column_name":"total_units","data_type":"FLOAT64"}
{"column_name":"total_spend","data_type":"FLOAT64"}
{"column_name":"last_price_paid","data_type":"FLOAT64"}
{"column_name":"last_price_paid_date","data_type":"STRING"}
{"column_name":"unknown_quantity_ordered","data_type":"FLOAT64"}
{"column_name":"unknown_units","data_type":"FLOAT64"}
{"column_name":"unknown_spend","data_type":"FLOAT64"}
{"column_name":"total_quantity_ordered_includes_unknowns","data_type":"FLOAT64"}
{"column_name":"total_units_ordered_includes_unknowns","data_type":"FLOAT64"}
{"column_name":"total_spend_ordered_includes_unknowns","data_type":"FLOAT64"}
"""

columns = []
for line in cols_json.strip().split('\n'):
    columns.append(json.loads(line))

table_name = "`abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`"

def make_sql(cols):
    parts = []
    for c in cols:
        name = c['column_name']
        dtype = c['data_type']
        
        # APPROX_TOP_COUNT only works on orderable types, usually STRINGS or INTs.
        # For UNION ALL compatibility, we MUST standardize the output type (Struct<value T, count>)
        # So we cast the input to STRING first.
        
        top_val_expr = f"APPROX_TOP_COUNT(CAST({name} AS STRING), 5)"
        
        sql = f"""
        SELECT
          '{name}' as col_name,
          '{dtype}' as data_type,
          COUNTIF({name} IS NULL) as null_count,
          APPROX_COUNT_DISTINCT({name}) as distinct_count,
          {top_val_expr} as top_values
        FROM {table_name}
        """
        parts.append(sql.strip())
    
    return " UNION ALL ".join(parts)

# Print batches
batch_size = 40
for i in range(0, len(columns), batch_size):
    batch = columns[i:i+batch_size]
    print(make_sql(batch))
    print("\n--- BATCH SEPARATOR ---\n")

