# Data Dictionary: `report_builder`

- **Full Path:** `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`
- **Description:** Pharmaceutical wholesaler sales tracings reported to the Premier GPO.
  - **Scope:** Represents a holistic view of facility-level purchasing through reporting wholesalers for *any* facility (US-based) that uses at least one Premier agreement (or is active on one).
  - **Coverage:** Includes Acute and Non-Acute facilities.
  - **GPO Nuance:** Captures spend even for facilities where Premier is a secondary GPO (e.g., using only the pharmacy portfolio) or where the facility is primarily affiliated with another GPO.
  - **Source:** Direct reporting from pharmaceutical wholesalers.
- **Estimated Rows:** ~690,000,000
- **Generated:** Manual context + MCP extraction

## Columns

### additional_desc
- Description: Any additional information available for the NDC (Additional drug information - ultimately PIMODS_PRODUCTS.DRUG_ADDITIONAL_DESCRIPTOR)

### ahfs_code
- Description: Therapeutic class code as defined by AHFS (American Hospital Formulary Service). A 4-tier hierarchy grouping drugs with similar pharmacologic/therapeutic/chemical characteristics.

### ahfs_desc
- Description: Description for therapeutic class as defined by AHFS.

### ahfs_tier1 / ahfs_tier1_code / ahfs_tier1_desc
- Description: AHFS Tier 1 number, code, and description.

### ahfs_tier2 / ahfs_tier2_code / ahfs_tier2_desc
- Description: AHFS Tier 2 number, code, and description.

### ahfs_tier3 / ahfs_tier3_code / ahfs_tier3_desc
- Description: AHFS Tier 3 number, code, and description.

### ahfs_tier4 / ahfs_tier4_code / ahfs_tier4_desc
- Description: AHFS Tier 4 number, code, and description.

### award_status_key
- Description: Key indicating contract status.
  - 0: On Contract
  - 1: Off Exact
  - 2: Non-Contract
  - 3: Unknown
  - 4: Off Equivalent
  - 5: 340B
  - 6: WAC (Wholesaler Acquisition Cost)
  - 7: Premier 503B

### brand_name
- Description: The trademark-protected name of the product.

### case_size
- Description: Divisor used to calculate single package price from catalog case price.

### charge_bk_key
- Description: Lookup key for chargebacks on `lk_charge_back`.

### consignment
- Description: Flag indicating if the stock is consignment inventory.
  - `N`: Non-consignment (99.9%)
  - `Y`: Consignment

### contract_lead_key
- Description: Key for contract lead name (see `dim_contract_lead`).

### contract_lead_name
- Description: Wholesaler Contract Name (internal name used to define a contract).

### cost_of_distribution
- Description: Wholesaler mark-up/mark-down for this product as a multiplier.

### dea_code
- Description: DEA Schedule Code indicating controlled substance status.
  - `0`: Non-controlled (80%)
  - `2`, `3`, `4`, `5`: Controlled substance schedules

### distribution_center_name
- Description: Wholesaler distribution Center name.

### dosage_form_desc
- Description: Physical form of the drug (tablet, capsule, injectable, etc.).

### drug_class
- Description: Dispensing limitation indicator.
  - `F`: Prescription/physician supervision required.
  - `O`: No dispensing limitations (OTC).

### drug_form_code
- Description: Code identifying the basic measurement unit for price calculations.

### drug_id_22 / drug_id_24 / drug_id_37 / drug_id_38
- Description: NDDF Functional Equivalent Codes (varying character lengths).

### dsh_id
- Description: Disproportionate Share Hospital (DSH) ID if the reporting facility is a DSH facility.

### facility
- Description: The name of the facility reporting the data.

### facility_account_key
- Description: Key used in `dim_facility_account` to lookup facility account numbers.

### facility_address / facility_address_secondary
- Description: Primary and secondary address of the facility.

### facility_city
- Description: City of the reporting facility.

### facility_dea
- Description: DEA number for the facility (controlled substance tracking).

### facility_direct_parent
- Description: Purchasing Facility's Direct Parent Name.

### facility_direct_parent_id
- Description: Purchasing Facility's Direct Parent Entity Code.

### facility_direct_parent_key
- Description: Key from `member_direct_parent` table for the facility's direct parent.

### facility_direct_parent_name
- Description: Name of the top direct parent reporting the data (closest to top parent).

### facility_hin
- Description: Facility HIN (Hospital Identification Number).

### facility_id
- Description: Entity Code of purchasing facility.

### facility_name
- Description: Name of the facility reporting the data.

### facility_state
- Description: State of the reporting facility.

### facility_zip_code
- Description: Zip Code of the reporting facility.

### gcn_sequence_number
- Description: A unique number representing a generic formulation.

### generic_name
- Description: Generic name of the drug (USAN adopted name). Must match active ingredients/quality of brand name.

### health_system / health_system_name
- Description: Name of the Top Parent / Health System of the reporting facility.

### health_system_address / health_system_address_secondary
- Description: Address of the top parent.

### health_system_city
- Description: City of the top parent.

### health_system_dea
- Description: DEA number for the health system.

### health_system_hin
- Description: Health System HIN (Hospital Identification Number).

### health_system_id
- Description: Entity code of the Top Parent/Health System.

### health_system_state
- Description: State of the top parent.

### health_system_zip_code
- Description: Zip Code of the top parent.

### hic_code
- Description: First 3 characters of Hierarchical Ingredient Code (FDB specific therapeutic class).

### hic_desc
- Description: Description of the Hierarchical Ingredient Code.

### invoice_date
- Description: Wholesaler reported invoice date.

### invoice_number
- Description: Number assigned to the invoice recording the sale.

### invoice_price
- Description: Final unit invoice price (sale +/- wholesaler markup).

### label_name
- Description: NDDF Label Name. (Brand name + Drug strength + Package description).

### labeler_id
- Description: Code uniquely identifying the distributor of the drug.

### last_price_paid
- Description: Last price paid per the submitted invoice.

### last_price_paid_date
- Description: Invoice date for the latest submitted invoice.

### line_number_from_invoice
- Description: Line number from the invoice as reported by the wholesaler.

### manufacturer_chargeback_id
- Description: Contract definition Chargeback ID (not manufacturer-assigned).

### member_key
- Description: Unique identifier for member (Primary key in `dim_member`).

### member_top_corp_parent_id
- Description: ID of the corporate parent entity (e.g., `AP7026`).

### member_top_corp_parent_name
- Description: Name of the corporate parent entity (e.g., `CVS PHARMACY - RETAIL HQ`, `WALGREENS - PHARMACY PURCHASING`).

### member_top_parent_key
- Description: Key from `member_top_parent` table for the purchasing facility's Top Parent.

### month
- Description: Month the invoice/PO was submitted.

### month_num
- Description: YYYYQMM format of submission date.

### month_year
- Description: First of the month of the invoice date (e.g., 2021-08-01).

### ncpdp
- Description: National Council for Prescription Drug Programs ID.

### ndc
- Description: National Drug Code (3-segment unique FDA identifier).

### non_contract_spend / non_contract_units
- Description: Spend/Units for drugs purchased NOT on a Premier agreement (where no clinical equivalent exists on agreement).

### npi
- Description: National Provider Identifier (NPI) ID.

### obsolete_date
- Description: Date the product became obsolete.

### off_contract_exact_and_equiv_spend / off_contract_exact_and_equiv_units
- Description: Sum of Off Exact and Off Equivalent Spend/Units (full view of OFF contract volume).

### off_equivalent_spend / off_equivalent_units
- Description: Spend/Units for purchases where a generic equivalent (package size/qty match) exists On Contract.

### off_exact_spend / off_exact_units
- Description: Spend/Units for items valid on a Premier contract but purchased on alternate/non-Premier contracts.

### on_contract_spend / on_contract_units
- Description: Total invoiced dollars/units for items purchased via a Premier Contract.

### orange_book_code
- Description: FDA therapeutic equivalence rating (from "Approved Drug Products with Therapeutic Equivalence Evaluations").

### order_date
- Description: Date the product was ordered.

### original_invoice_number
- Description: If credit issued, refers to the original invoice # being credited.

### pkg_desc
- Description: Description of the drug product container.

### pkg_qty
- Description: Number of salable units packed together.

### pkg_size
- Description: Quantity per unit of measure (e.g., number of vials/bottles in a case).

### premier_award_status
- Description: Contract status code (0=On Contract, 1=Off Exact, 2=Non-Contract, etc.). See `award_status_key`.

### premier_contract_number
- Description: Premier contract number containing this product.

### premier_contract_unit_price
- Description: Premier Contract Unit Price for this Product.

### premier_fillrate
- Description: Ratio of Orders Filled to Orders Placed.

### premier_reason_code
- Description: Standardized reason code translation (based on wholesaler submitted code).

### premier_relation
- Description: Identifies the member’s relationship to its top parent.

### price_effective_date / price_expiration_date
- Description: Start and end dates for pricing effectiveness.

### price_type_code
- Description: Price Type code description.
  - 1: DSH
  - 4: PP
  - 6: Autosub
  - 7: Direct Only
  - 8: ProRx

### provider_class_id
- Description: Key for Provider Class/SPC/COT this facility belongs to.

### qa_oid
- Description: Price Type code key (matches usage of `price_type_code`).

### quantity_ordered
- Description: Number of units ordered.

### quarter / quarter_num
- Description: Quarter the invoice/PO was submitted (and YYYYQ format).

### route
- Description: Site or method of drug administration.

### service_provider_class
- Description: Description of Provider Class/CPT/COT.

### ship_method
- Description: Code for shipping method.
  - `I`: Indirect
  - `D`: Direct/Drop Ship
  - `C`: Courtesy Bill

### shipping_date
- Description: Date the product was shipped.

### strength
- Description: Measurement of the active ingredient per dose.

### supplier
- Description: The supplier of record for the product according to the FDA.

### supplier_wac / supplier_wac_effective_date
- Description: Wholesaler Acquisition Cost and its effective date.

### t340b_id
- Description: 340B Account ID (populated for 340B purchases).

### t340b_spend / t340b_units
- Description: Total sales dollars/units invoiced at 340B pricing.

### tier_effective_date / tier_expiration_date
- Description: Start and end dates for tier effectiveness.

### total_quantity_ordered_includes_unknowns
- Description: Total sales units (Commonized Units + unknown qty).

### total_spend
- Description: Total dollar amount spent (invoice level, includes +/-).

### total_spend_excluding_340b_wac
- Description: Total spend minus 340B and WAC spend.

### total_spend_ordered_includes_unknowns
- Description: Total spend (invoice level) plus unknown units spend.

### total_units
- Description: Total sales units purchased (Commonized Units for same NDC).

### total_units_excluding_340b_wac
- Description: Total units minus 340B and WAC units.

### total_units_ordered_includes_unknowns
- Description: Total sales units (Commonized Units + unknown units).

### unit_dose
- Description: Indicates if package contains a single administration dose (note: not always single unit package).

### unit_of_measure
- Description: Description of package type (case, packet, box, bottle).

### unknown_quantity_ordered / unknown_spend / unknown_units
- Description: Quantity/Spend/Units for unknown/unmatched products.

### upc / upc_key
- Description: Universal Product Code (12 digits) and lookup key.

### upn / upn_key
- Description: Universal Product Number and lookup key.

### wac_spend / wac_units
- Description: Total sales dollars/units invoiced at WAC pricing.

### wholesaler
- Description: Name of Wholesaler who submitted the purchase.

### wholesaler_account_attribute
- Description: Indicator for account type.
  - `WAC`: Apexus/340B prime vendor
  - `GPO`: Group Purchasing Organization
  - `340B`: 340B Account

### wholesaler_account_name
- Description: Wholesaler Account Description.

### wholesaler_account_number
- Description: Wholesaler Internal Account Number for Facility.

### wholesaler_catalog_number
- Description: Wholesaler Product or Item Number.

### wholesaler_chargeback_id
- Description: Wholesaler Chargeback Number.

### wholesaler_id
- Description: Internal Identifier for Wholesaler.

### wholesaler_invoice_wac
- Description: Wholesaler Reported WAC price.

### wholesaler_load_price
- Description: Wholesaler Reported Invoice Price.

### wholesaler_order_line_number
- Description: Line number on order.

### wholesaler_pkg_qty
- Description: Number of sellable units in a package (wholesaler reported).

### wholesaler_purchase_type
- Description: Code for wholesaler view of transaction.
  - P: Premier Contract
  - N: Non-Contract
  - O: Other Contract
  - D: DSH Inpatient
  - W: WAC account
  - B: 340B purchase
  - 1: Innovatix
  - 4: Wholesaler Program
  - 5: Member’s Private Agreement

### whsl_charge_bk_key
- Description: Key for `lk_charge_back` table lookup.

### whsl_purch_type_code
- Description: Code matching `wholesaler_purchase_type` (plus `8` = Premier 503B).

### year
- Description: Year the invoice/PO was submitted.

