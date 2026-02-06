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
- Type: `STRING`
- Description: Any additional information available for the NDC (Additional drug information - ultimately PIMODS_PRODUCTS.DRUG_ADDITIONAL_DESCRIPTOR)
- Nulls: 403,270,490 (58.45%)
- Distinct: 4,029
- Top values: None (403,270,490), OUTER (41,983,512), F/C (39,797,399), OUTER, SUV, P/F (20,410,064), OUTER, SUV (18,221,471)


### ahfs_code
- Type: `STRING`
- Description: Therapeutic class code as defined by AHFS (American Hospital Formulary Service). A 4-tier hierarchy grouping drugs with similar pharmacologic/therapeutic/chemical characteristics.
- Nulls: 0 (0.00%)
- Distinct: 524
- Top values: 68200600 (52,169,775), 00000000 (26,377,579), 28080800 (25,560,340), 94000000 (24,981,363), 28200400 (23,613,729)


### ahfs_desc
- Type: `STRING`
- Description: Description for therapeutic class as defined by AHFS.
- Nulls: 0 (0.00%)
- Distinct: 484
- Top values: INCRETIN MIMETICS (52,169,775), NO DESCRIPTION (26,490,842), OPIOID AGONISTS (28:08) (25,560,340), DEVICES (24,981,363), AMPHETAMINES (23,613,729)


### ahfs_tier1 / ahfs_tier1_code / ahfs_tier1_desc
- Description: AHFS Tier 1 number, code, and description.

### ahfs_tier2 / ahfs_tier2_code / ahfs_tier2_desc
- Description: AHFS Tier 2 number, code, and description.

### ahfs_tier3 / ahfs_tier3_code / ahfs_tier3_desc
- Description: AHFS Tier 3 number, code, and description.

### ahfs_tier4 / ahfs_tier4_code / ahfs_tier4_desc
- Description: AHFS Tier 4 number, code, and description.

### award_status_key
- Type: `FLOAT64`
- Description: Key indicating contract status.
- Nulls: 0 (0.00%)
- Distinct: 4

  - 0: On Contract
  - 1: Off Exact
  - 2: Non-Contract
  - 3: Unknown
  - 4: Off Equivalent
  - 5: 340B
  - 6: WAC (Wholesaler Acquisition Cost)
  - 7: Premier 503B

### brand_name
- Type: `STRING`
- Description: The trademark-protected name of the product.
- Nulls: 106,090 (0.02%)
- Distinct: 10,826
- Top values: Unknown (25,154,970), MOUNJARO (12,432,975), OZEMPIC (11,463,137), WEGOVY (11,330,085), DEXTROAMPHETAMINE-AMPHETAMINE (7,056,590)


### case_size
- Type: `INT64`
- Description: Divisor used to calculate single package price from catalog case price.
- Nulls: 27,303,199 (3.96%)
- Distinct: 61


### charge_bk_key
- Type: `INT64`
- Description: Lookup key for chargebacks on `lk_charge_back`.
- Nulls: 0 (0.00%)
- Distinct: 1,202


### consignment
- Type: `STRING`
- Description: Flag indicating if the stock is consignment inventory.
- Nulls: 418,142 (0.06%)
- Distinct: 2
- Top values: N (689,521,603), None (418,142), Y (20,815)

  - `N`: Non-consignment (99.9%)
  - `Y`: Consignment

### contract_lead_key
- Type: `INT64`
- Description: Key for contract lead name (see `dim_contract_lead`).
- Nulls: 418,142 (0.06%)
- Distinct: 13,135


### contract_lead_name
- Type: `STRING`
- Description: Wholesaler Contract Name (internal name used to define a contract).
- Nulls: 418,142 (0.06%)
- Distinct: 13,116
- Top values: UNKNOWN (224,685,125), OTHER CONTRACT (218,002,387), NO CONTRACT (157,472,141), OTHER (23,471,744), N (9,330,893)


### cost_of_distribution
- Type: `FLOAT64`
- Description: Wholesaler mark-up/mark-down for this product as a multiplier.
- Nulls: 0 (0.00%)
- Distinct: 68,700


### dea_code
- Type: `STRING`
- Description: DEA Schedule Code indicating controlled substance status.
- Nulls: 27,866,024 (4.04%)
- Distinct: 7
- Top values: 0 (555,685,606), 2 (60,876,032), None (27,866,024), 4 (21,095,918), 3 (15,640,588)

  - `0`: Non-controlled (80%)
  - `2`, `3`, `4`, `5`: Controlled substance schedules

### distribution_center_name
- Type: `STRING`
- Description: Wholesaler distribution Center name.
- Nulls: 418,142 (0.06%)
- Distinct: 279
- Top values: CARDINAL HEALTH-SWEDESBORO (46,132,028), GREENSBORO FDC (40,881,972), BOSTON FDC (40,726,904), WHEELING FDC (38,329,591), SYRACUSE FDC (37,628,759)


### dosage_form_desc
- Type: `STRING`
- Description: Physical form of the drug (tablet, capsule, injectable, etc.).
- Nulls: 27,235,427 (3.95%)
- Distinct: 348
- Top values: TABLET (197,689,362), PEN INJCTR (54,646,016), CAPSULE (51,308,778), VIAL (45,468,814), None (26,431,913)


### drug_class
- Type: `STRING`
- Description: Dispensing limitation indicator.
- Nulls: 27,366,755 (3.97%)
- Distinct: 3
- Top values: F (576,776,729), O (63,587,774), None (27,366,755), Q (22,229,302)

  - `F`: Prescription/physician supervision required.
  - `O`: No dispensing limitations (OTC).

### drug_form_code
- Type: `STRING`
- Description: Code identifying the basic measurement unit for price calculations.
- Nulls: 27,366,747 (3.97%)
- Distinct: 3
- Top values: EA (405,140,812), ML (195,932,806), GM (61,520,195), None (27,366,747)


### drug_id_22 / drug_id_24 / drug_id_37 / drug_id_38
- Description: NDDF Functional Equivalent Codes (varying character lengths).

### dsh_id
- Type: `STRING`
- Description: Disproportionate Share Hospital (DSH) ID if the reporting facility is a DSH facility.
- Nulls: 643,458,791 (93.26%)
- Distinct: 642
- Top values: None (643,458,791), DSH230053 (2,299,559), DSH450213 (860,576), DSH180088 (854,207), DSH220077 (575,951)


### facility
- Type: `STRING`
- Description: The name of the facility reporting the data.
- Nulls: 0 (0.00%)
- Distinct: 78,219
- Top values: Unknown - 00 -  (8,429,388), ETH ANESTHESIA DBA FUSION ANESTHESIA - BE6656 -  (3,095,209), HENRY FORD HOSPITAL - MI2016 - AH4337526 (2,243,881), OPTUMRX - OVERLAND PARK - 661753 - BP9587847 (926,496), UNIVERSITY HEALTH SYSTEM - 804303 - AM1472579 (801,855)


### facility_account_key
- Type: `INT64`
- Description: Key used in `dim_facility_account` to lookup facility account numbers.
- Nulls: 418,142 (0.06%)
- Distinct: 198,256


### facility_address / facility_address_secondary
- Description: Primary and secondary address of the facility.

### facility_city
- Type: `STRING`
- Description: City of the reporting facility.
- Nulls: 8,854,899 (1.28%)
- Distinct: 6,953
- Top values: BROOKLYN (10,141,611), NEW YORK (9,941,418), None (8,777,566), BRONX (8,012,042), HOUSTON (5,101,542)


### facility_dea
- Type: `STRING`
- Description: DEA number for the facility (controlled substance tracking).
- Nulls: 20,362,660 (2.95%)
- Distinct: 52,836
- Top values: None (20,362,660), AH4337526 (2,245,372), BP9587847 (926,496), AM1472579 (802,245), AL6453586 (680,391)


### facility_direct_parent
- Type: `STRING`
- Description: Purchasing Facility's Direct Parent Name.
- Nulls: 418,142 (0.06%)
- Distinct: 4,859
- Top values: CVS PHARMACY - RETAIL HQ -  AP7026 (387,542,189), INNOVATIX, LLC NATIONAL HEADQUARTERS -  605082 (40,725,697), WALGREENS - PHARMACY PURCHASING -  698144 (21,872,623), Unknown -  0 (13,363,887), PHARMERICA CORPORATE OFFICE -  729516 (11,420,914)


### facility_direct_parent_id
- Type: `STRING`
- Description: Purchasing Facility's Direct Parent Entity Code.
- Nulls: 418,142 (0.06%)
- Distinct: 4,858
- Top values: AP7026 (387,542,189), 605082 (40,725,697), 698144 (21,872,358), 0 (13,363,887), 729516 (11,420,914)


### facility_direct_parent_key
- Type: `INT64`
- Description: Key from `member_direct_parent` table for the facility's direct parent.
- Nulls: 418,142 (0.06%)
- Distinct: 4,858


### facility_direct_parent_name
- Type: `STRING`
- Description: Name of the top direct parent reporting the data (closest to top parent).
- Nulls: 418,142 (0.06%)
- Distinct: 4,801
- Top values: CVS PHARMACY - RETAIL HQ (387,542,189), INNOVATIX, LLC NATIONAL HEADQUARTERS (40,725,697), WALGREENS - PHARMACY PURCHASING (21,872,623), Unknown (13,363,887), PHARMERICA CORPORATE OFFICE (11,420,914)


### facility_hin
- Type: `STRING`
- Description: Facility HIN (Hospital Identification Number).
- Nulls: 303,703,499 (44.02%)
- Distinct: 36,721
- Top values: None (303,703,499), 000000000 (3,139,317), 440550I00 (2,296,686), 745160N00 (803,835), K0WVKVQF1 (680,391)


### facility_id
- Type: `STRING`
- Description: Entity Code of purchasing facility.
- Nulls: 0 (0.00%)
- Distinct: 78,804
- Top values: 00 (8,429,388), BE6656 (3,095,743), MI2016 (2,243,881), 661753 (926,496), 804303 (801,855)


### facility_name
- Type: `STRING`
- Description: Name of the facility reporting the data.
- Nulls: 0 (0.00%)
- Distinct: 63,366
- Top values: CVS PHARMACY (387,011,339), Unknown (8,428,306), ETH ANESTHESIA DBA FUSION ANESTHESIA (3,087,144), AURORA PHARMACY, INC. (2,956,793), HENRY FORD HOSPITAL (2,243,495)


### facility_state
- Type: `STRING`
- Description: State of the reporting facility.
- Nulls: 8,854,899 (1.28%)
- Distinct: 54
- Top values: NY (79,463,954), CA (59,976,954), TX (46,264,540), FL (43,663,845), PA (34,336,578)


### facility_zip_code
- Type: `STRING`
- Description: Zip Code of the reporting facility.
- Nulls: 8,854,899 (1.28%)
- Distinct: 68,849
- Top values: None (8,854,899), 68135 (3,085,489), 48202-2689 (2,243,495), 66211-9838 (926,715), 78229-4493 (803,672)


### gcn_sequence_number
- Type: `FLOAT64`
- Description: A unique number representing a generic formulation.
- Nulls: 27,303,458 (3.96%)
- Distinct: 12,376


### generic_name
- Type: `STRING`
- Description: Generic name of the drug (USAN adopted name). Must match active ingredients/quality of brand name.
- Nulls: 26,045,173 (3.77%)
- Distinct: 5,373
- Top values: None (25,197,896), SEMAGLUTIDE (24,593,696), TIRZEPATIDE (17,737,888), DEXTROAMPHETAMINE/AMPHETAMINE (13,852,484), METHYLPHENIDATE HCL (9,210,225)


### health_system / health_system_name
- Description: Name of the Top Parent / Health System of the reporting facility.

### health_system_address / health_system_address_secondary
- Description: Address of the top parent.

### health_system_city
- Type: `STRING`
- Description: City of the top parent.
- Nulls: 8,854,899 (1.28%)
- Distinct: 291
- Top values: NEW YORK (548,289,294), CHARLOTTE (13,028,401), None (8,854,899), CLEVELAND (7,386,485), CHICAGO (7,294,009)


### health_system_dea
- Type: `STRING`
- Description: DEA number for the health system.
- Nulls: 677,979,583 (98.26%)
- Distinct: 125
- Top values: None (677,979,583), AW1712202 (1,512,852), BR4502642 (950,227), AC3758692 (796,573), BU6476407 (582,780)


### health_system_hin
- Type: `STRING`
- Description: Health System HIN (Hospital Identification Number).
- Nulls: 59,930,242 (8.69%)
- Distinct: 276
- Top values: 2C0MR0R00 (533,195,909), None (59,930,242), 51H0H0400 (15,070,645), CDF4EJ500 (6,103,688), LKNW6F900 (5,629,132)


### health_system_id
- Type: `STRING`
- Description: Entity code of the Top Parent/Health System.
- Nulls: 0 (0.00%)
- Distinct: 398
- Top values: 605082 (533,195,909), NY5011 (15,070,645), AQ9425 (12,510,397), 0 (8,428,695), CO5012 (6,103,688)


### health_system_state
- Type: `STRING`
- Description: State of the top parent.
- Nulls: 8,854,899 (1.28%)
- Distinct: 46
- Top values: NY (551,341,879), NC (18,185,052), OH (12,201,809), PA (11,821,932), IL (10,414,756)


### health_system_zip_code
- Type: `STRING`
- Description: Zip Code of the top parent.
- Nulls: 8,854,899 (1.28%)
- Distinct: 387
- Top values: 10019-2925 (533,210,504), 10019-2974 (15,070,645), 28203-5812 (12,510,397), None (8,854,899), 60606-0097 (6,103,688)


### hic_code
- Type: `STRING`
- Description: First 3 characters of Hierarchical Ingredient Code (FDB specific therapeutic class).
- Nulls: 27,285,875 (3.95%)
- Distinct: 866
- Top values: None (26,305,937), C4G (24,298,557), J5B (23,573,670), H4B (22,971,906), C4I (21,758,549)


### hic_desc
- Type: `STRING`
- Description: Description of the Hierarchical Ingredient Code.
- Nulls: 27,367,783 (3.97%)
- Distinct: 888
- Top values: None (26,381,158), INSULINS (24,298,557), ADRENERGICS, AROMATIC, NON-CATECHOLAMINE (23,573,670), ANTICONVULSANTS (22,971,906), ANTIHYPERGLY,INCRETIN MIMETIC(GLP-1 RECEP.AGONIST) (21,758,549)


### invoice_date
- Type: `STRING`
- Description: Wholesaler reported invoice date.
- Nulls: 0 (0.00%)
- Distinct: 2,488
- Top values: 2024-01-02 (1,921,484), 2023-09-05 (1,737,973), 2024-07-11 (1,706,675), 2023-12-26 (1,601,465), 2024-09-03 (1,598,020)


### invoice_number
- Type: `STRING`
- Description: Number assigned to the invoice recording the sale.
- Nulls: 418,691 (0.06%)
- Distinct: 92,983,699
- Top values: None (418,689), 7364194387 (2,319), 3190590077 (1,665), 7432489684 (1,374), 355853253 (1,195)


### invoice_price
- Type: `FLOAT64`
- Description: Final unit invoice price (sale +/- wholesaler markup).
- Nulls: 0 (0.00%)
- Distinct: 517,713


### label_name
- Type: `STRING`
- Description: NDDF Label Name. (Brand name + Drug strength + Package description).
- Nulls: 27,289,991 (3.96%)
- Distinct: 20,121
- Top values: None (27,288,166), OZEMPIC 0.25-0.5 MG/DOSE PEN (4,086,094), OZEMPIC 1 MG/DOSE (4 MG/3 ML) (3,739,355), WEGOVY 0.25 MG/0.5 ML PEN (3,461,204), OZEMPIC 2 MG/DOSE (8 MG/3 ML) (3,378,451)


### labeler_id
- Type: `STRING`
- Description: Code uniquely identifying the distributor of the drug.
- Nulls: 27,312,475 (3.96%)
- Distinct: 1,569
- Top values: A00169 (37,880,338), A00002 (34,039,806), None (26,330,866), C65162 (21,818,768), A65862 (18,144,765)


### last_price_paid
- Type: `FLOAT64`
- Description: Last price paid per the submitted invoice.
- Nulls: 2,277,112 (0.33%)
- Distinct: 376,981


### last_price_paid_date
- Type: `STRING`
- Description: Invoice date for the latest submitted invoice.
- Nulls: 2,277,112 (0.33%)
- Distinct: 2,404
- Top values: 2025-04-17 (28,123,630), 2025-06-27 (18,784,498), 2025-04-16 (16,613,280), 2026-01-23 (16,024,327), 2025-04-14 (14,143,844)


### line_number_from_invoice
- Type: `STRING`
- Description: Line number from the invoice as reported by the wholesaler.
- Nulls: 422,363,394 (61.22%)
- Distinct: 6,788
- Top values: None (422,363,394), 1 (24,270,287), 2 (15,954,205), 3 (13,412,846), 4 (11,655,414)


### manufacturer_chargeback_id
- Type: `STRING`
- Description: Contract definition Chargeback ID (not manufacturer-assigned).
- Nulls: 2,486,225 (0.36%)
- Distinct: 1,071
- Top values: UNKNOWN (460,567,460), 2000004-18 (16,704,348), 30000207 (10,934,906), PREMIER18 (10,917,796), 661492-1 (10,879,875)


### member_key
- Type: `INT64`
- Description: Unique identifier for member (Primary key in `dim_member`).
- Nulls: 418,142 (0.06%)
- Distinct: 78,511


### member_top_corp_parent_id
- Type: `STRING`
- Description: ID of the corporate parent entity (e.g., `AP7026`).
- Nulls: 9,197,335 (1.33%)
- Distinct: 23,102
- Top values: AP7026 (387,464,775), 698144 (21,854,018), AQ9425 (12,406,614), 729516 (11,399,208), None (9,119,968)


### member_top_corp_parent_name
- Type: `STRING`
- Description: Name of the corporate parent entity (e.g., `CVS PHARMACY - RETAIL HQ`, `WALGREENS - PHARMACY PURCHASING`).
- Nulls: 9,197,335 (1.33%)
- Distinct: 22,824
- Top values: CVS PHARMACY - RETAIL HQ (387,464,775), WALGREENS - PHARMACY PURCHASING (21,855,013), ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE (12,406,614), PHARMERICA CORPORATE OFFICE (11,399,208), None (9,119,968)


### member_top_parent_key
- Type: `INT64`
- Description: Key from `member_top_parent` table for the purchasing facility's Top Parent.
- Nulls: 418,142 (0.06%)
- Distinct: 397


### month
- Type: `STRING`
- Description: Month the invoice/PO was submitted.
- Nulls: 0 (0.00%)
- Distinct: 85
- Top values: Jan-24 (27,388,345), Jul-24 (24,965,327), Apr-24 (24,906,935), Dec-23 (24,878,869), Aug-23 (24,670,615)


### month_num
- Type: `INT64`
- Description: YYYYQMM format of submission date.
- Nulls: 0 (0.00%)
- Distinct: 85


### month_year
- Type: `TIMESTAMP`
- Description: First of the month of the invoice date (e.g., 2021-08-01).
- Nulls: 0 (0.00%)
- Distinct: 85


### ncpdp
- Type: `STRING`
- Description: National Council for Prescription Drug Programs ID.
- Nulls: 439,220,605 (63.66%)
- Distinct: 16,171
- Top values: None (439,220,605), 000000000000 (29,043,900), 0000000 (18,743,530), 0568305 (572,249), 5807574 (552,089)


### ndc
- Type: `STRING`
- Description: National Drug Code (3-segment unique FDA identifier).
- Nulls: 0 (0.00%)
- Distinct: 63,633
- Top values: 0 (26,001,178), 00169418113 (3,797,779), 00169413013 (3,778,282), 00169477212 (3,534,716), 00169452514 (3,462,539)


### non_contract_spend / non_contract_units
- Description: Spend/Units for drugs purchased NOT on a Premier agreement (where no clinical equivalent exists on agreement).

### npi
- Type: `STRING`
- Description: National Provider Identifier (NPI) ID.
- Nulls: 444,975,106 (64.49%)
- Distinct: 28,137
- Top values: None (444,975,106), 000000000000 (17,034,365), 0000000000 (8,254,125), 1134100134 (727,546), 1689789315 (572,474)


### obsolete_date
- Type: `STRING`
- Description: Date the product became obsolete.
- Nulls: 678,881,423 (98.39%)
- Distinct: 1,719
- Top values: None (678,881,423), 2023-12-18 (1,362,345), 1900-01-01 (935,448), 2023-01-01 (678,712), 2023-05-14 (345,991)


### off_contract_exact_and_equiv_spend / off_contract_exact_and_equiv_units
- Description: Sum of Off Exact and Off Equivalent Spend/Units (full view of OFF contract volume).

### off_equivalent_spend / off_equivalent_units
- Description: Spend/Units for purchases where a generic equivalent (package size/qty match) exists On Contract.

### off_exact_spend / off_exact_units
- Description: Spend/Units for items valid on a Premier contract but purchased on alternate/non-Premier contracts.

### on_contract_spend / on_contract_units
- Description: Total invoiced dollars/units for items purchased via a Premier Contract.

### orange_book_code
- Type: `STRING`
- Description: FDA therapeutic equivalence rating (from "Approved Drug Products with Therapeutic Equivalence Evaluations").
- Nulls: 27,366,745 (3.97%)
- Distinct: 16
- Top values: AB (304,060,021), ZB (145,937,394), ZC (99,481,014), AP (34,054,115), AA (29,677,423)


### order_date
- Type: `STRING`
- Description: Date the product was ordered.
- Nulls: 414,954,469 (60.14%)
- Distinct: 2,270
- Top values: None (414,954,469), 2024-10-13 (355,434), 2025-12-15 (328,900), 2025-12-22 (315,079), 2025-11-24 (311,802)


### original_invoice_number
- Type: `STRING`
- Description: If credit issued, refers to the original invoice # being credited.
- Nulls: 519,153,270 (75.24%)
- Distinct: 8,319,262
- Top values: None (519,153,270), 0 (151,426,062), - (1,550,485), 
 (67,746), 7442116076 (11,492)


### pkg_desc
- Type: `STRING`
- Description: Description of the drug product container.
- Nulls: 27,285,149 (3.95%)
- Distinct: 55
- Top values: BOTTLE (319,928,147), SYRINGE (86,760,868), BLIST PACK (51,938,913), VIAL (51,460,543), BOX (36,694,124)


### pkg_qty
- Type: `STRING`
- Description: Number of salable units packed together.
- Nulls: 26,001,178 (3.77%)
- Distinct: 63
- Top values: 1 (540,186,756), 4 (39,275,700), None (26,001,178), 5 (18,800,676), 10 (16,425,213)


### pkg_size
- Type: `STRING`
- Description: Quantity per unit of measure (e.g., number of vials/bottles in a case).
- Nulls: 26,001,178 (3.77%)
- Distinct: 596
- Top values: 100 (159,336,440), 30 (81,948,138), 1 (46,012,941), 3 (38,346,174), 60 (36,227,191)


### premier_award_status
- Type: `STRING`
- Description: Contract status code (0=On Contract, 1=Off Exact, 2=Non-Contract, etc.). See `award_status_key`.
- Nulls: 0 (0.00%)
- Distinct: 4
- Top values: ON CONTRACT (241,737,032), NON CONTRACT (222,037,273), OFF CONTRACT (196,148,067), UNKNOWN (30,038,188)


### premier_contract_number
- Description: Premier contract number containing this product.

### premier_contract_unit_price
- Type: `FLOAT64`
- Description: Premier Contract Unit Price for this Product.
- Nulls: 750,567 (0.11%)
- Distinct: 19,580


### premier_fillrate
- Type: `FLOAT64`
- Description: Ratio of Orders Filled to Orders Placed.
- Nulls: 527,056,411 (76.39%)
- Distinct: 49,234


### premier_reason_code
- Type: `STRING`
- Description: Standardized reason code translation (based on wholesaler submitted code).
- Nulls: 0 (0.00%)
- Distinct: 22
- Top values: ORDER FILLED (517,333,978), UNKNOWN (100,581,888), BACKORDER - MANUFACTURER (31,717,056), ALLOCATION - DISTRIBUTOR (14,141,639), TEMP OUT - DISTRIBUTOR (11,096,969)


### premier_relation
- Type: `STRING`
- Description: Identifies the member’s relationship to its top parent.
- Nulls: 8,854,899 (1.28%)
- Distinct: 2
- Top values: AFFILIATE (572,971,271), OLM (108,134,390), None (8,854,899)


### price_effective_date / price_expiration_date
- Description: Start and end dates for pricing effectiveness.

### price_type_code
- Type: `STRING`
- Description: Price Type code description.
- Nulls: 553,067 (0.08%)
- Distinct: 6
- Top values:   (665,322,538), D (17,075,504), L (5,381,185), G (1,324,449), None (553,067)

  - 1: DSH
  - 4: PP
  - 6: Autosub
  - 7: Direct Only
  - 8: ProRx

### provider_class_id
- Type: `INT64`
- Description: Key for Provider Class/SPC/COT this facility belongs to.
- Nulls: 0 (0.00%)
- Distinct: 25


### qa_oid
- Type: `INT64`
- Description: Price Type code key (matches usage of `price_type_code`).
- Nulls: 553,067 (0.08%)
- Distinct: 6


### quantity_ordered
- Type: `FLOAT64`
- Description: Number of units ordered.
- Nulls: 0 (0.00%)
- Distinct: 5,783


### quarter / quarter_num
- Description: Quarter the invoice/PO was submitted (and YYYYQ format).

### route
- Type: `STRING`
- Description: Site or method of drug administration.
- Nulls: 27,367,464 (3.97%)
- Distinct: 42
- Top values: ORAL (351,019,184), SUBCUT (87,399,468), TOPICAL (43,307,629), INHALATION (35,794,160), MISCELL (27,833,568)


### service_provider_class
- Type: `STRING`
- Description: Description of Provider Class/CPT/COT.
- Nulls: 0 (0.00%)
- Distinct: 25
- Top values: RETAIL - PHARMACY (506,702,225), ACUTE - PHARMACY (88,851,891), LONG TERM CARE - PROVIDER SELECT (40,738,626), NON ACUTE - PHARMACY (14,871,816), UNKNOWN - NOT AVAILABLE (13,538,348)


### ship_method
- Type: `STRING`
- Description: Code for shipping method.
- Nulls: 216,037,580 (31.31%)
- Distinct: 5
- Top values: N (268,930,326), None (216,037,580), I (190,446,002), D (14,543,998), S (2,175)

  - `I`: Indirect
  - `D`: Direct/Drop Ship
  - `C`: Courtesy Bill

### shipping_date
- Type: `STRING`
- Description: Date the product was shipped.
- Nulls: 575,523,299 (83.41%)
- Distinct: 1,973
- Top values: None (575,523,299), 2026-01-05 (460,533), 2025-11-10 (450,129), 2025-12-01 (440,896), 2026-01-12 (430,343)


### strength
- Type: `STRING`
- Description: Measurement of the active ingredient per dose.
- Nulls: 49,814,699 (7.22%)
- Distinct: 4,642
- Top values: None (49,814,699), 10 MG (27,919,176), 5 MG (19,471,911), 20 MG (18,957,480), 100 MG (17,644,430)


### supplier
- Type: `STRING`
- Description: The supplier of record for the product according to the FDA.
- Nulls: 26,001,178 (3.77%)
- Distinct: 1,618
- Top values: NOVO NORDISK (37,877,360), ELI LILLY & CO. (34,039,806), None (25,154,970), AMNEAL PHARMACE (22,698,244), AUROBINDO PHARM (18,140,664)


### supplier_wac / supplier_wac_effective_date
- Description: Wholesaler Acquisition Cost and its effective date.

### t340b_id
- Type: `STRING`
- Description: 340B Account ID (populated for 340B purchases).
- Nulls: 492,458,736 (71.37%)
- Distinct: 5,283
- Top values: None (492,458,736), 000000000000000 (155,175,910), DSH450213 (1,930,558), DSH230053 (1,470,294), DSH490009 (1,072,827)


### t340b_spend / t340b_units
- Description: Total sales dollars/units invoiced at 340B pricing.

### tier_effective_date / tier_expiration_date
- Description: Start and end dates for tier effectiveness.

### total_quantity_ordered_includes_unknowns
- Type: `FLOAT64`
- Description: Total sales units (Commonized Units + unknown qty).
- Nulls: 0 (0.00%)
- Distinct: 6,791


### total_spend
- Type: `FLOAT64`
- Description: Total dollar amount spent (invoice level, includes +/-).
- Nulls: 0 (0.00%)
- Distinct: 1,810,281


### total_spend_excluding_340b_wac
- Type: `FLOAT64`
- Description: Total spend minus 340B and WAC spend.
- Nulls: 0 (0.00%)
- Distinct: 1,448,263


### total_spend_ordered_includes_unknowns
- Type: `FLOAT64`
- Description: Total spend (invoice level) plus unknown units spend.
- Nulls: 0 (0.00%)
- Distinct: 1,871,523


### total_units
- Type: `FLOAT64`
- Description: Total sales units purchased (Commonized Units for same NDC).
- Nulls: 0 (0.00%)
- Distinct: 4,714


### total_units_excluding_340b_wac
- Type: `FLOAT64`
- Description: Total units minus 340B and WAC units.
- Nulls: 0 (0.00%)
- Distinct: 4,674


### total_units_ordered_includes_unknowns
- Type: `FLOAT64`
- Description: Total sales units (Commonized Units + unknown units).
- Nulls: 0 (0.00%)
- Distinct: 5,984


### unit_dose
- Type: `STRING`
- Description: Indicates if package contains a single administration dose (note: not always single unit package).
- Nulls: 27,154,628 (3.94%)
- Distinct: 3
- Top values: NO (631,055,971), YES (31,749,909), None (27,154,628), UNKNOWN (52)


### unit_of_measure
- Type: `STRING`
- Description: Description of package type (case, packet, box, bottle).
- Nulls: 128,030 (0.02%)
- Distinct: 65
- Top values: EA (479,380,417), TB (71,470,437), CT (54,319,126), UN (26,730,234), CP (22,255,792)


### unknown_quantity_ordered / unknown_spend / unknown_units
- Description: Quantity/Spend/Units for unknown/unmatched products.

### upc / upc_key
- Description: Universal Product Code (12 digits) and lookup key.

### upn / upn_key
- Description: Universal Product Number and lookup key.

### wac_spend / wac_units
- Description: Total sales dollars/units invoiced at WAC pricing.

### wholesaler
- Type: `STRING`
- Description: Name of Wholesaler who submitted the purchase.
- Nulls: 0 (0.00%)
- Distinct: 40
- Top values: Cardinal Health (369,490,691), McKesson (210,568,171), AmerisourceBergen Drug Corporation (84,234,211), Morris & Dickson (7,340,004), Henry Schein (5,534,165)


### wholesaler_account_attribute
- Type: `STRING`
- Description: Indicator for account type.
- Nulls: 4,027,471 (0.58%)
- Distinct: 3
- Top values: GPO (619,369,935), 340B (44,692,600), WAC (21,870,554), None (4,027,471)

  - `WAC`: Apexus/340B prime vendor
  - `GPO`: Group Purchasing Organization
  - `340B`: 340B Account

### wholesaler_account_name
- Type: `STRING`
- Description: Wholesaler Account Description.
- Nulls: 85,315,824 (12.37%)
- Distinct: 98,712
- Top values: MCKESSON US PHARMA (155,189,545), None (85,315,824), WALGREEN CO. (7,564,565), WALGREENS CO (4,784,712), MEDICAL, DRUG STORES (4,653,882)


### wholesaler_account_number
- Type: `STRING`
- Description: Wholesaler Internal Account Number for Facility.
- Nulls: 418,142 (0.06%)
- Distinct: 200,275
- Top values: 2057200456 (659,400), 300740 (552,088), UNKNOWN (504,208), 2057201399 (409,473), 2052025582 (358,745)


### wholesaler_catalog_number
- Type: `STRING`
- Description: Wholesaler Product or Item Number.
- Nulls: 1,799,141 (0.26%)
- Distinct: 446,671
- Top values: 5830005 (2,309,687), 5707542 (2,280,040), 5728282 (2,213,911), 5780358 (2,065,266), 5728290 (1,838,782)


### wholesaler_chargeback_id
- Type: `STRING`
- Description: Wholesaler Chargeback Number.
- Nulls: 610,270,503 (88.45%)
- Distinct: 106,629
- Top values: None (610,270,503), OTHER (24,474,971), 2000004-18 (3,295,427), 00107012 (1,156,934), C21979-1 (1,084,363)


### wholesaler_id
- Type: `INT64`
- Description: Internal Identifier for Wholesaler.
- Nulls: 0 (0.00%)
- Distinct: 40


### wholesaler_invoice_wac
- Type: `FLOAT64`
- Description: Wholesaler Reported WAC price.
- Nulls: 0 (0.00%)
- Distinct: 91,035


### wholesaler_load_price
- Type: `FLOAT64`
- Description: Wholesaler Reported Invoice Price.
- Nulls: 0 (0.00%)
- Distinct: 177,522


### wholesaler_order_line_number
- Type: `STRING`
- Description: Line number on order.
- Nulls: 56,908,808 (8.25%)
- Distinct: 25,535
- Top values: 000000 (87,173,309), None (56,908,808), 000010 (19,359,414), 10 (12,914,069), 000020 (12,713,393)


### wholesaler_pkg_qty
- Type: `FLOAT64`
- Description: Number of sellable units in a package (wholesaler reported).
- Nulls: 0 (0.00%)
- Distinct: 340
- **Data Quality Warning:** Significant data leakage observed where "Volume" (e.g., 1000 for 1000mL) is populated instead of "Pack Count".
  - **Heuristic:** Compare `wholesaler_pkg_qty` vs `pkg_size` (Volume). If `wholesaler_pkg_qty == pkg_size` (and > 1), treat as 1 (leakage).
  - **Usage:** To calculate Units (Eaches), use: `Quantity Ordered * (wholesaler_pkg_qty if valid else 1)`.


### wholesaler_purchase_type
- Type: `STRING`
- Description: Code for wholesaler view of transaction.
- Nulls: 0 (0.00%)
- Distinct: 10
- Top values: Other Contract (345,362,112), Non Contract (193,902,862), Premier Contract (47,544,734), 340B (43,368,689), Wholesaler Contract (34,228,422)

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
- Type: `INT64`
- Description: Key for `lk_charge_back` table lookup.
- Nulls: 0 (0.00%)
- Distinct: 106,003


### whsl_purch_type_code
- Type: `STRING`
- Description: Code matching `wholesaler_purchase_type` (plus `8` = Premier 503B).
- Nulls: 0 (0.00%)
- Distinct: 12
- Top values: O (345,362,112), N (193,902,862), P (47,544,734), B (43,368,689), 4 (32,490,157)


### year
- Type: `INT64`
- Description: Year the invoice/PO was submitted.
- Nulls: 0 (0.00%)
- Distinct: 8


