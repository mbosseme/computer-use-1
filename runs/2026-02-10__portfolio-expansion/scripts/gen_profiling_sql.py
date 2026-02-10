
import json

columns = [
    "health_system_name", "account_name", "entity_code", "org_number", "org_description", 
    "department_number", "charge_to_department", "department_description", "invoice_match_header_id", 
    "invoice_line_id", "invoice_number", "invoice_line_number", "erp_item_number", "item_description", 
    "invoiced_quantity", "invoiced_uom", "invoiced_unit_cost", "invoiced_line_amount", "received_quantity", 
    "received_uom", "received_uom_conversion_factor", "received_unit_cost", "received_line_amount", 
    "quantity_variance", "price_variance", "vendor_item_number", "purchase_order_uom", 
    "purchase_uom_conversion_factor", "purchase_order_unit_cost", "assigned_buyer", "vendor_number", 
    "vendor_name", "manufacturer_item_number", "manufacturer_id", "manufacturer_name", "expense_code", 
    "expense_code_description", "invoice_create_date", "last_modified_date", "invoice_due_date", 
    "invoice_date", "invoice_received_date", "approved_date", "transaction_date", "posted_date", 
    "fiscal_period", "fiscal_year", "payment_terms", "po_number", "po_header_id", "po_line_id", 
    "contract_number", "contract_name", "contract_type", "contract_type_description", "lowest_uom", 
    "lowest_uom_contract_price", "purchase_uom_contract_price", "premier_reference_number", 
    "premier_product_category", "premier_item_description", "premier_manufacturer_name", 
    "premier_manufacturer_entity_code", "premier_manufacturer_top_parent_entity_code", 
    "premier_manufacturer_item_number", "premier_vendor_name", "premier_vendor_entity_code", 
    "premier_top_parent_entity_code", "packaging_string", "user_id", "invoice_match_status", 
    "invoice_match_status_description", "invoice_workflow_status", "invoice_workflow_status_description", 
    "invoice_create_type", "invoice_create_type_description", "payment_method", "payment_method_description", 
    "invoice_810_yn", "ocr_invoice_yn", "invoice_has_exception_yn", "invoice_line_exception_status", 
    "invoice_line_exception_status_description", "invoice_header_exception_status", "missing_line_exception_yn", 
    "price_exception_yn", "quantity_exception_yn", "uom_variance_yn", "edi_invoice_quantity", 
    "edi_invoice_unit_cost", "edi_invoice_line_amount", "edi_import_detail_status", 
    "edi_import_detail_status_description", "snapshot_date"
]

def generate_batch_sql(batch_cols, start_idx):
    select_parts = []
    for col in batch_cols:
        select_parts.append(f"COUNTIF({col} IS NULL) as {col}_nulls")
        select_parts.append(f"APPROX_COUNT_DISTINCT({col}) as {col}_distinct")
        select_parts.append(f"APPROX_TOP_COUNT({col}, 5) as {col}_top")
    
    query = "SELECT \n  " + ",\n  ".join(select_parts) + "\nFROM `premierinc-com-data.invoicing_provider_match.provider_invoice_match`"
    
    print(f"--- BATCH {start_idx} ---")
    print(query)
    print("\n")

batch_size = 20
for i in range(0, len(columns), batch_size):
    batch = columns[i:i + batch_size]
    generate_batch_sql(batch, i)
