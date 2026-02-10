# Data Dictionary: Provider Purchasing Transaction (Identified, Month Aggregated)
**Table**: `abi-xform-dataform-prod.ssp_create_provider_transaction_base.provider_purchasing_transaction_identified_month_agg`
**Description**: Monthly aggregated provider purchasing transactions, identified by facility and product, with Premier roster information attached.
**Total Records**: 320,248,524 (as of Feb 2026)

## Columns

### health_system_name
- **Type**: `STRING`
- **Description**: Name of the health system (IDN) associated with the purchasing facility.

### health_system_entity_code
- **Type**: `STRING`
- **Description**: Unique entity code for the health system.

### direct_parent_name
- **Type**: `STRING`
- **Description**: Name of the direct parent entity of the facility.

### direct_parent_entity_code
- **Type**: `STRING`
- **Description**: Code for the direct parent entity.

### facility_name
- **Type**: `STRING`
- **Description**: Name of the individual facility where the purchase occurred.

### facility_entity_code
- **Type**: `STRING`
- **Description**: Premier unique entity code for the facility.

### facility_id
- **Type**: `INTEGER`
- **Description**: Internal integer identifier for the facility.

### SF_Entity_Code
- **Type**: `STRING`
- **Description**: Salesforce entity code linkage.

### Salesforce_ID
- **Type**: `STRING`
- **Description**: Salesforce unique identifier (18-char string).

### dhc_id
- **Type**: `INTEGER`
- **Description**: Definitive Healthcare ID linkage.

### has_rights
- **Type**: `BOOLEAN`
- **Description**: Indicator if the user/entity has rights to view this data.

### SF_Account_Family
- **Type**: `STRING`
- **Description**: Account family grouping from Salesforce.

### Account_Name
- **Type**: `STRING`
- **Description**: Account name as defined in the source system (Salesforce/Premier).

### facility_type
- **Type**: `STRING`
- **Description**: Classification of the facility (e.g., Acute, Non-Acute, Alternate Site).

### facility_primary_service
- **Type**: `STRING`
- **Description**: Primary service line or clinical focus of the facility.

### member_premier_relation
- **Type**: `STRING`
- **Description**: Relationship type with Premier (e.g., Owner, Member, Affiliate).

### Premier_Enterprise_Unit_Roll_Up
- **Type**: `STRING`
- **Description**: Hierarchical rollup for Premier Enterprise reporting.

### member_state
- **Type**: `STRING`
- **Description**: State abbreviation of the facility (e.g., NY, CA).

### dominant_zip3
- **Type**: `STRING`
- **Description**: First 3 digits of the zip code where the facility has dominant share/presence.

### member_end_date
- **Type**: `STRING`
- **Description**: Date membership ended (if applicable).

### member_start_date
- **Type**: `STRING`
- **Description**: Date membership started.

### ascend_end_date
- **Type**: `STRING`
- **Description**: End date of Ascend collaborative participation.

### ascend_start_date
- **Type**: `STRING`
- **Description**: Start date of Ascend collaborative participation.

### surpass_end_date
- **Type**: `STRING`
- **Description**: End date of SURPASS participation.

### surpass_start_date
- **Type**: `STRING`
- **Description**: Start date of SURPASS participation.

### premier_ascend_surpass_member
- **Type**: `BOOLEAN`
- **Description**: Flag indicating if facility matches Premier/Ascend/Surpass membership criteria.

### premier_gpo_member
- **Type**: `BOOLEAN`
- **Description**: Flag indicating active GPO membership.

### facility_department_id
- **Type**: `STRING`
- **Description**: Identifier for the specific department within the facility.

### predicted_standard_department_descr
- **Type**: `STRING`
- **Description**: Standardized description of the department (predicted by model).

### predicted_standard_department_group_descr
- **Type**: `STRING`
- **Description**: Group-level standardized department description.

### predicted_standard_department_type_descr
- **Type**: `STRING`
- **Description**: Type-level standardized classification of the department.

### manufacturer_top_parent_name
- **Type**: `STRING`
- **Description**: Name of the top-level parent company of the manufacturer.

### premier_manufacturer_top_parent_entity_code
- **Type**: `STRING`
- **Description**: Entity code for the manufacturer top parent.

### manufacturer_name
- **Type**: `STRING`
- **Description**: Name of the manufacturer.

### premier_manufacturer_entity_code
- **Type**: `STRING`
- **Description**: Entity code for the manufacturer.

### manufacturer_part_number
- **Type**: `STRING`
- **Description**: Manufacturer's catalog or part number.

### product_description
- **Type**: `STRING`
- **Description**: Description of the product sold.

### premier_reference_number
- **Type**: `STRING`
- **Description**: Premier internal reference number for the product.

### premier_product_category
- **Type**: `STRING`
- **Description**: Broad product category classification.

### product_contract_category
- **Type**: `STRING`
- **Description**: Contract-specific alignment category.

### product_group_category
- **Type**: `STRING`
- **Description**: Hierarchical product grouping.

### product_subcategory_l1
- **Type**: `STRING`
- **Description**: Product taxonomy Level 1.

### product_subcategory_l2
- **Type**: `STRING`
- **Description**: Product taxonomy Level 2.

### product_subcategory_l3
- **Type**: `STRING`
- **Description**: Product taxonomy Level 3.

### product_subcategory_l4
- **Type**: `STRING`
- **Description**: Product taxonomy Level 4.

### full_path_to_lowest_populated_product_subcategory
- **Type**: `STRING`
- **Description**: Full concatenated string of the product taxonomy path.

### brand_name
- **Type**: `STRING`
- **Description**: Brand name of the product.

### xref_group
- **Type**: `STRING`
- **Description**: Cross-reference group identifier.

### health_system_primary_indicator_txn
- **Type**: `STRING`
- **Description**: Indicator if this product is the primary selection for the health system (based on transaction volume).

### primary_premier_manufacturer_top_parent_entity_code_for_facility_department_and_xref_group
- **Type**: `STRING`
- **Description**: Entity code of the primary manufacturer for this facility/dept/xref group.

### primary_manufacturer_top_parent_name_for_facility_department_and_xref_group
- **Type**: `STRING`
- **Description**: Name of the primary manufacturer for this facility/dept/xref group.

### business_unit
- **Type**: `STRING`
- **Description**: Business unit associated with the product/sale.

### profit_center
- **Type**: `STRING`
- **Description**: Profit center associated with the product/sale.

### product_group_1
- **Type**: `STRING`
- **Description**: Additional product grouping 1.

### product_group_2
- **Type**: `STRING`
- **Description**: Additional product grouping 2.

### gsc
- **Type**: `STRING`
- **Description**: Global Supply Chain code or similar classification.

### catalog_code
- **Type**: `STRING`
- **Description**: Catalog identifier.

### health_system_primary_indicator_txn_gsc
- **Type**: `STRING`
- **Description**: Primary indicator calculated at the GSC level.

### primary_premier_manufacturer_top_parent_entity_code_for_facility_department_and_gsc
- **Type**: `STRING`
- **Description**: Primary mfr entity code (GSC scope).

### primary_manufacturer_top_parent_name_for_facility_department_and_gsc
- **Type**: `STRING`
- **Description**: Primary mfr name (GSC scope).

### vendor_top_parent_name
- **Type**: `STRING`
- **Description**: Top parent name of the vendor (distributor/seller).

### vendor_top_parent_entity_code
- **Type**: `STRING`
- **Description**: Entity code for vendor top parent.

### vendor_name
- **Type**: `STRING`
- **Description**: Name of the vendor.

### premier_vendor_entity_code
- **Type**: `STRING`
- **Description**: Entity code for the vendor.

### sold_in_kit_txn_tf
- **Type**: `BOOLEAN`
- **Description**: Flag (True/False) indicating if the item was sold as part of a kit.

### original_refnum_if_kit
- **Type**: `STRING`
- **Description**: Original reference number if the item is a component of a kit.

### original_manufacturer_if_kit
- **Type**: `STRING`
- **Description**: Original manufacturer if the item is a component of a kit.

### transaction_month
- **Type**: `DATE`
- **Description**: The month of the transaction (aggregated).

### total_transaction_count
- **Type**: `INTEGER`
- **Description**: Number of transactions in the aggregation period.

### total_transaction_line_amount
- **Type**: `FLOAT`
- **Description**: Total dollar amount of the transactions.

### total_transaction_quantity_in_predicted_uom
- **Type**: `FLOAT`
- **Description**: Total quantity sold (normalized to predicted unit of measure).

### weighted_avg_selling_price
- **Type**: `FLOAT`
- **Description**: Weighted average selling price (Total Amount / Total Quantity).

### mfr_tp_gained_primary_status_count
- **Type**: `INTEGER`
- **Description**: Count of times this manufacturer gained primary status.

### mfr_tp_gained_primary_status_count_gsc
- **Type**: `INTEGER`
- **Description**: Count of times this manufacturer gained primary status (GSC scope).

### count_of_departments_where_mfr_tp_is_primary
- **Type**: `INTEGER`
- **Description**: Number of departments where this manufacturer is the primary supplier.

### count_of_departments_where_mfr_tp_is_primary_gsc
- **Type**: `INTEGER`
- **Description**: Number of departments where this manufacturer is the primary supplier (GSC scope).
