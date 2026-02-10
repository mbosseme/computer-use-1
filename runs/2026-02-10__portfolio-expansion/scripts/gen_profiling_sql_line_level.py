
columns = [
    "health_system_name", "entity_code", "direct_parent_name", "direct_parent_entity_code", "org_number", 
    "org_description", "remitra_invoice_header_id", "department_number", "charge_to_department", 
    "department_description", "invoice_match_header_id", "invoice_line_id", "invoice_number", 
    "invoice_line_number", "vendor_item_number", "item_description", "invoiced_quantity", 
    "invoiced_uom", "invoiced_unit_cost", "invoiced_line_amount", "received_quantity", 
    "received_uom", "received_unit_cost", "received_line_amount", "quantity_variance", 
    "price_variance", "erp_item_number", "purchase_order_uom", "purchase_uom_conversion_factor", 
    "purchase_order_unit_cost", "assigned_buyer", "vendor_number", "vendor_invoice_date", 
    "vendor_name", "vendor_entity_code", "vendor_top_parent_name", "vendor_top_parent_entity_code", 
    "facility_entity_name", "facility_entity_code", "manufacturer_item_number", "manufacturer_id", 
    "manufacturer_name", "expense_code", "expense_code_description", "invoice_create_date", 
    "last_modified_date", "invoice_due_date", "invoice_date", "invoice_received_date", 
    "approved_date", "transaction_date", "posted_date", "fiscal_period", "fiscal_year", 
    "payment_terms", "po_number", "po_header_id", "po_line_id", "po_line_number", 
    "contract_number", "contract_name", "contract_type", "contract_type_description", 
    "lowest_uom_contract_price", "purchase_uom_contract_price", "premier_reference_number", 
    "premier_product_category", "premier_item_description", "premier_manufacturer_name", 
    "premier_manufacturer_entity_code", "premier_manufacturer_top_parent_entity_code", 
    "premier_manufacturer_item_number", "premier_vendor_name", "premier_vendor_entity_code", 
    "premier_top_parent_entity_code", "packaging_string", "user_id", "invoice_match_status", 
    "invoice_match_status_description", "invoice_workflow_status", "invoice_workflow_status_description", 
    "invoice_create_type", "invoice_create_type_description", "payment_method", 
    "payment_method_description", "invoice_810_yn", "ocr_invoice_yn", 
    "invoice_line_exception_status", "invoice_current_exception_status_description", 
    "invoice_header_exception_status", "price_exception_yn", "quantity_exception_yn", 
    "receipt_exception_yn", "missing_line_exception_yn", "other_exception_type_yn", 
    "uom_variance_yn", "snapshot_date", "invoice_type", "client_name", "ap_location", 
    "billto", "bill_to_address_line_1", "bill_to_address_line_2", "bill_to_address_line_3", 
    "bill_to_city", "bill_to_state", "bill_to_country", "bill_to_zipcode", "shipto_name", 
    "shipto_address", "shipto_city", "shipto_state", "shipto_postalcode", "routing_category", 
    "hospital_id", "remitra_created_date", "remitra_modified_date", "remitra_received_date", 
    "data_source"
]

table_name = "`premierinc-com-data.invoicing_provider_match.provider_invoice_line_level_history`"
batch_size = 20

def generate_sql(cols):
    select_parts = []
    for col in cols:
        select_parts.append(f"COUNTIF({col} IS NULL) as {col}_nulls")
        select_parts.append(f"APPROX_COUNT_DISTINCT({col}) as {col}_distinct")
        select_parts.append(f"APPROX_TOP_COUNT({col}, 5) as {col}_top")
    
    return f"SELECT {', '.join(select_parts)} FROM {table_name}"

for i in range(0, len(columns), batch_size):
    batch = columns[i:i+batch_size]
    print(f"--- Batch {i} to {i+batch_size} ---")
    print(generate_sql(batch))
    print(f"--- Batch {i} to {i+batch_size} ---")
    print(generate_sql(batch))
