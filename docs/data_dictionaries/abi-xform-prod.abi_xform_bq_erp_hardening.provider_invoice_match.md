# Data Dictionary: `provider_invoice_match`

- **Full Path:** `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_match`
- **Description:** This table stores a daily history of open invoices with exception and matching status prior to payment through an ERP. Unique records in this table can be identified by org_number, invoice_match_header_id, invoice_line_number, and snapshot_date. New or changed records can be identified from the created_date and last_modified_date. This table is updated Monday through Friday by 5PM EST.
- **Estimated Rows:** 291,575,862
- **Generated:** Manual context + MCP extraction

## Columns


### health_system_name
- Type: `STRING`
- Description: The name of the health system in Premier's ERP
- Nulls: 0 (0.00%)
- Distinct: 87
- Top values: EM_UCSD (25,733,316), EM_ULHealth (25,466,868), EM_CCH (24,582,555), EM_CCH_Rework (18,072,421), EM_HonorHealth (14,777,790)

### account_name
- Type: `STRING`
- Description: The account name associated with the health system.
- Nulls: 945,428 (0.32%)
- Distinct: 88
- Top values: University of California San Diego Health System (AKA UC San Diego Health) (25,733,316), UofL Hospital (AKA University of Louisville Hospital) (25,466,868), Coastal Community Health (24,582,555), CCH_Rework (18,072,421), HonorHealth (FKA Scottsdale Lincoln Health Network) (14,777,790)

### entity_code
- Type: `STRING`
- Description: Internal Premier ERP customer code
- Nulls: 942,823 (0.32%)
- Distinct: 208
- Top values: 743158 (25,733,316), N/A CCH Duplicate (18,070,596), FL0091 (14,330,258), CA3550 (12,771,329), KY0080 (11,353,669)

### org_number
- Type: `STRING`
- Description: The number assigned to an organization in the health system. This value may be a hospital-sized unit, larger, or smaller, depending on how the medical center is structured.
- Nulls: 0 (0.00%)
- Distinct: 284
- Top values: 001 (39,367,017), 1 (30,699,160), 101080 (25,274,616), 10 (21,413,479), 01 (15,949,457)

### org_description
- Type: `STRING`
- Description: The name for an organization in the health system.
- Nulls: 13,672,851 (4.69%)
- Distinct: 369
- Top values: UCSD MEDICAL CENTER (23,171,435), BAPTIST MEDICAL CENTER - JACKSONVILLE (22,854,678), None (12,717,108), Renown Regional Medical Center (8,517,319), University Medical Center (7,849,847)

### department_number
- Type: `STRING`
- Description: The deliver to department number listed on the purchase order associated with the invoice
- Nulls: 114,821,255 (39.38%)
- Distinct: 18,021
- Top values: None (114,821,255), 4400 (7,354,204), 7420-00 (2,262,755), 6600 (2,193,655), 6210 (2,158,881)

### charge_to_department
- Type: `STRING`
- Description: An override charge to department number if the deliver to department number is not the correct cost center
- Nulls: 250,388,783 (85.87%)
- Distinct: 9,266
- Top values: None (250,388,783), 6600 (1,806,083), 7211 (1,077,226), 6210 (1,021,965), 7420-00PC (793,735)

### department_description
- Type: `STRING`
- Description: A description of the deliver to department number
- Nulls: 115,831,522 (39.73%)
- Distinct: 18,796
- Top values: None (115,831,522), OPERATING ROOM (11,556,308), SURGERY (6,058,129), OR Operating Room-Main (2,689,608), JHHL OPERATING ROOM (2,454,867)

### invoice_match_header_id
- Type: `INTEGER`
- Description: The internal unique ID used to identify for matching an invoice header
- Nulls: 71,441,367 (24.50%)
- Distinct: 2,656,433
- Top values: None (71,441,367), 45343 (87,768), 5209041 (77,437), 23520 (73,139), 5205385 (67,468)

### invoice_line_id
- Type: `INTEGER`
- Description: Ther internal unique ID for each line on an invoice
- Nulls: 71,441,367 (24.50%)
- Distinct: 9,700,479
- Top values: None (71,441,367), 4604911 (536), 4363959 (465), 4414259 (459), 486045 (409)

### invoice_number
- Type: `STRING`
- Description: The invoice document number provide by the invoicing vendor
- Nulls: 0 (0.00%)
- Distinct: 3,851,854
- Top values: CLEAR OPEN PO (145,332), CLEAR RNI (127,349), RNI (92,387), 2048892902 (87,588), 2049284215 (71,857)

### invoice_line_number
- Type: `INTEGER`
- Description: The row number of a line on an invoice
- Nulls: 70,431,013 (24.16%)
- Distinct: 461
- Top values: 1 (74,914,178), None (70,431,013), 2 (25,998,443), 3 (16,357,423), 4 (12,172,731)

### erp_item_number
- Type: `STRING`
- Description: The health system's internal identifier for an item stored in the item catalog
- Nulls: 63,611,731 (21.82%)
- Distinct: 503,555
- Top values: None (63,611,731), 877410100 (233,394), 877410090 (218,526), 881208715 (207,305), 171072 (205,917)

### item_description
- Type: `STRING`
- Description: The health system's defined description for an erp item number
- Nulls: 11,723 (0.00%)
- Distinct: 1,710,400
- Top values: SYRINGE FLSH PSFLSH IV SAL PREFL PRSV FR 10ML (241,360), Hill Rom Bed Rentals (196,553), BAG READYBATH FRAG FREE (174,677), GLOVE PROTEXIS PI PF SYNTH SIZ (147,988), PACK WARM RAPID RELIEF 6x9 (143,821)

### invoiced_quantity
- Type: `FLOAT`
- Description: The quantity listed on the invoice line
- Nulls: 71,441,367 (24.50%)
- Distinct: 7,147
- Top values: 1 (103,238,331), None (71,441,367), 2 (34,954,210), 3 (14,303,404), 4 (12,871,472)

### invoiced_uom
- Type: `STRING`
- Description: The unit of measure for the quantity listed on the invoice line
- Nulls: 71,441,367 (24.50%)
- Distinct: 210
- Top values: EA (113,951,690), None (71,441,367), CA (39,330,571), BX (36,320,752), PK (12,086,186)

### invoiced_unit_cost
- Type: `FLOAT`
- Description: The unit cost for each item or service listed on an invoice line
- Nulls: 71,441,367 (24.50%)
- Distinct: 292,372
- Top values: None (71,441,367), 0 (4,218,868), 100 (616,657), 150 (547,758), 200 (527,515)

### invoiced_line_amount
- Type: `FLOAT`
- Description: The total extended cost for an invoice line, the unit cost multiplied by the invoice quantity
- Nulls: 71,441,367 (24.50%)
- Distinct: 325,822
- Top values: None (71,441,367), 0 (4,376,405), 600 (537,882), 300 (523,050), 200 (491,221)

### received_quantity
- Type: `FLOAT`
- Description: The quantity that has been physically received from a purchase order
- Nulls: 71,441,367 (24.50%)
- Distinct: 7,093
- Top values: 1 (101,996,098), None (71,441,367), 2 (34,688,552), 3 (14,199,795), 4 (12,773,257)

### received_uom
- Type: `STRING`
- Description: The unit of measure that was used when a purchase order receipt was completed
- Nulls: 73,463,794 (25.20%)
- Distinct: 193
- Top values: EA (112,442,160), None (73,463,794), CA (39,203,479), BX (36,229,386), PK (12,036,158)

### received_uom_conversion_factor
- Type: `FLOAT`
- Description: The conversion factor to the lowest unit of measure from the received unit of measure
- Nulls: 189,964,676 (65.15%)
- Distinct: 417
- Top values: None (189,964,676), 1 (54,077,767), 10 (6,261,844), 50 (4,130,279), 5 (3,909,456)

### received_unit_cost
- Type: `FLOAT`
- Description: The unit cost of the items physically received from a purchase order
- Nulls: 71,441,367 (24.50%)
- Distinct: 306,057
- Top values: None (71,441,367), 0 (6,444,021), 100 (615,571), 200 (545,554), 150 (536,522)

### received_line_amount
- Type: `FLOAT`
- Description: The extended cost of a receipt line being the unit cost multiplied by the received quantity
- Nulls: 71,441,367 (24.50%)
- Distinct: 331,168
- Top values: None (71,441,367), 0 (6,496,867), 600 (527,871), 300 (516,685), 200 (512,448)

### quantity_variance
- Type: `FLOAT`
- Description: The difference in the invoiced quantity and the received quantity
- Nulls: 71,441,367 (24.50%)
- Distinct: 1,011
- Top values: 0 (217,630,439), None (71,441,367), 1 (1,469,608), 2 (281,165), 4 (128,962)

### price_variance
- Type: `FLOAT`
- Description: The difference in the invoiced line amount and the received line amount
- Nulls: 71,441,367 (24.50%)
- Distinct: 60,103
- Top values: 0 (205,797,877), None (71,441,367), 0.01 (951,704), -0.01 (880,767), 0.02 (530,497)

### vendor_item_number
- Type: `STRING`
- Description: The item number provide by the primary vendor for an ERP item number
- Nulls: 4,710,753 (1.62%)
- Distinct: 717,531
- Top values: None (4,710,753), Service (716,362), UNKNOWN (621,965), DYND80235S (444,636), NONE (359,894)

### purchase_order_uom
- Type: `STRING`
- Description: The unit of measure listed on the purchase order
- Nulls: 73,596,030 (25.24%)
- Distinct: 205
- Top values: EA (112,019,936), None (73,596,030), CA (39,273,026), BX (36,277,624), PK (12,047,478)

### purchase_uom_conversion_factor
- Type: `FLOAT`
- Description: The conversion factor to the lowest unit of measure from the purchase order uom
- Nulls: 73,596,030 (25.24%)
- Distinct: 450
- Top values: 1 (134,264,090), None (73,585,587), 10 (11,007,146), 50 (7,278,338), 5 (6,913,470)

### purchase_order_unit_cost
- Type: `FLOAT`
- Description: The unit cost listed on the purchase order line associated with the invoice
- Nulls: 73,596,030 (25.24%)
- Distinct: 201,870
- Top values: None (73,471,549), 0 (11,563,976), 100 (564,487), 200 (546,008), 150 (526,820)

### assigned_buyer
- Type: `STRING`
- Description: The user id for the buyer assigned to the invoiced purchase order
- Nulls: 71,441,913 (24.50%)
- Distinct: 1,957
- Top values: None (71,441,367), Admin (21,536,422), WWEWE001 (21,270,535), SSOUR001 (9,393,093), mkkastner (6,630,842)

### vendor_number
- Type: `STRING`
- Description: The unique number set up in the health system's ERP for the vendor providing the invoice
- Nulls: 0 (0.00%)
- Distinct: 42,366
- Top values: 101016 (28,473,160), 0034560 (15,649,720), 902047 (9,670,104), 6510 (7,704,851), 101732 (5,849,542)

### vendor_name
- Type: `STRING`
- Description: The name of the vendor listed on the invoice
- Nulls: 12,887,435 (4.42%)
- Distinct: 32,927
- Top values: MEDLINE INDUSTRIES INC (38,134,829), OWENS AND MINOR INC (26,318,979), MEDLINE INDUSTRIES INC (STOCK ONLY LUM) (15,043,035), None (12,688,111), OWENS & MINOR INC (8,577,075)

### manufacturer_item_number
- Type: `STRING`
- Description: The item number provide by the manufacturer
- Nulls: 64,209,489 (22.02%)
- Distinct: 606,863
- Top values: None (64,201,118), UNKNOWN (1,813,393), 1 (1,534,481), Service (628,875), none (479,936)

### manufacturer_id
- Type: `STRING`
- Description: The internal ID used to identify a unique manufacturer in the ERP
- Nulls: 73,331,386 (25.15%)
- Distinct: 30,445
- Top values: None (73,331,119), UNKNOWN (10,946,047), MEDLINE (6,980,853), MEDL (3,474,215), 1 (3,138,144)

### manufacturer_name
- Type: `STRING`
- Description: The name of the manufacturer listed on the invoice
- Nulls: 77,580,453 (26.61%)
- Distinct: 28,755
- Top values: None (77,580,453), MEDLINE INDUSTRIES INC (16,551,563), UNKNOWN (13,120,232), MEDLINE (4,878,450), NONE (3,787,889)

### expense_code
- Type: `STRING`
- Description: The expense code on the purchase order line associated with the invoice line
- Nulls: 83,175,000 (28.53%)
- Distinct: 6,092
- Top values: None (83,175,000), 6210000 (25,864,825), 520500 (11,551,418), 602140 (5,304,843), 70050 (3,860,634)

### expense_code_description
- Type: `STRING`
- Description: A description of the expense code on the purchase order line
- Nulls: 83,937,864 (28.79%)
- Distinct: 4,795
- Top values: None (83,937,864), MED/SURG SUPPLIES (26,722,372), MEDICAL CARE MATERIALS AND SUPPLIES (11,551,418), MEDICAL SUPPLIES (9,449,422), Supplies-Other Medical (5,268,215)

### invoice_create_date
- Type: `DATE`
- Description: The date that the invoice was created in the health system's ERP
- Nulls: 0 (0.00%)
- Distinct: 3,838
- Top values: 2019-08-14 (2,120,020), 2019-08-17 (1,914,834), 2019-08-16 (1,853,183), 2019-08-20 (1,850,610), 2019-08-13 (1,724,841)

### last_modified_date
- Type: `DATE`
- Description: The date that invoice line or header was last modified in the health system's ERP
- Nulls: 921,007 (0.32%)
- Distinct: 3,540
- Top values: 2019-08-20 (4,099,540), 2025-04-04 (2,157,304), 2025-05-29 (1,814,363), 2019-08-14 (1,664,531), 2019-08-16 (1,612,140)

### invoice_due_date
- Type: `DATETIME`
- Description: The due date for payment listed on the invoice
- Nulls: 71,449,974 (24.50%)
- Distinct: 3,157
- Top values: None (71,441,367), 2019-08-28T00:00:00 (2,181,718), 2019-08-30T00:00:00 (2,139,008), 2019-08-31T00:00:00 (1,560,732), 2019-08-27T00:00:00 (1,439,462)

### invoice_date
- Type: `DATETIME`
- Description: The date listed on the invoice from the vendor
- Nulls: 71,441,367 (24.50%)
- Distinct: 2,836
- Top values: None (71,441,367), 2019-08-13T00:00:00 (2,135,493), 2019-08-15T00:00:00 (2,014,950), 2019-08-12T00:00:00 (1,585,362), 2019-08-16T00:00:00 (1,571,493)

### invoice_received_date
- Type: `DATETIME`
- Description: The date that the invoice was received from the vendor by the health system
- Nulls: 71,441,367 (24.50%)
- Distinct: 2,451
- Top values: None (71,441,367), 2019-08-14T00:00:00 (2,170,842), 2019-08-17T00:00:00 (1,941,250), 2019-08-16T00:00:00 (1,856,069), 2019-08-20T00:00:00 (1,621,627)

### approved_date
- Type: `DATETIME`
- Description: The date that the invoice was approved by accounts payable
- Nulls: 114,734,272 (39.35%)
- Distinct: 2,236
- Top values: None (114,734,272), 2019-08-14T00:00:00 (1,538,756), 2019-08-16T00:00:00 (1,476,866), 2019-08-13T00:00:00 (1,377,566), 2019-08-20T00:00:00 (1,167,558)

### transaction_date
- Type: `DATETIME`
- Description: The date that the transaction is recorded for GL purposes
- Nulls: 71,441,367 (24.50%)
- Distinct: 2,372
- Top values: None (71,441,367), 2019-08-14T00:00:00 (2,165,322), 2019-08-17T00:00:00 (1,955,970), 2019-08-16T00:00:00 (1,848,706), 2019-08-20T00:00:00 (1,624,571)

### posted_date
- Type: `DATETIME`
- Description: The date that the invoice payment was processed and posted in the accounting system
- Nulls: 114,734,272 (39.35%)
- Distinct: 2,236
- Top values: None (114,734,272), 2019-08-14T00:00:00 (1,538,756), 2019-08-16T00:00:00 (1,476,866), 2019-08-13T00:00:00 (1,377,566), 2019-08-20T00:00:00 (1,167,558)

### fiscal_period
- Type: `FLOAT`
- Description: A 1-12 month indicator of the financial period varying based on a health system's defined fiscal year
- Nulls: 71,441,367 (24.50%)
- Distinct: 12
- Top values: None (71,441,367), 11 (30,571,821), 5 (23,296,425), 2 (17,794,524), 4 (17,694,462)

### fiscal_year
- Type: `FLOAT`
- Description: The financial year that the invoice transaction took place
- Nulls: 71,441,367 (24.50%)
- Distinct: 18
- Top values: 2025 (120,184,703), None (71,441,367), 2026 (62,481,800), 2019 (19,532,728), 2022 (6,117,056)

### payment_terms
- Type: `STRING`
- Description: The payment terms on the purchase order determining when final payment is due
- Nulls: 71,449,974 (24.50%)
- Distinct: 339
- Top values: None (71,441,367), N30 (43,045,356), 30 (27,074,432), Net15 (22,141,564), NET30 (13,215,825)

### po_number
- Type: `STRING`
- Description: The purchase order number linked to the invoice number
- Nulls: 0 (0.00%)
- Distinct: 2,478,505
- Top values: B14197 (201,664), 611852 (151,286), 611859 (119,612), 101080003917 (94,473), 10006 (92,191)

### po_header_id
- Type: `INTEGER`
- Description: The internal ID used to identify a unique purchase order
- Nulls: 71,441,367 (24.50%)
- Distinct: 1,732,681
- Top values: None (71,441,367), 101566 (180,688), 5306 (94,444), 1999821 (89,181), 101595 (84,589)

### po_line_id
- Type: `INTEGER`
- Description: The ERP internal id used to identify the row level detail on a purchase order
- Nulls: 71,492,916 (24.52%)
- Distinct: 8,566,185
- Top values: None (71,492,916), 0 (1,970,878), 377163 (83,853), 375246 (68,407), 316814 (65,091)

### contract_number
- Type: `STRING`
- Description: The contract number listed on the purchase order for the invoice
- Nulls: 203,830,906 (69.91%)
- Distinct: 14,159
- Top values: None (203,830,906), redacted (2,819,180), ML-2025-020 (1,599,381), LC71287 (1,404,731), G5725CM-2025-08 (810,703)

### contract_name
- Type: `STRING`
- Description: The description and name of the contract listed on the purchase order for the invoice
- Nulls: 205,593,269 (70.51%)
- Distinct: 7,605
- Top values: None (205,593,269), redacted (2,819,180), Medline CatchAll (1,894,848), Stryker Wright Trauma Amendment (1,405,969), Medline UC Misc Products 2025-08 (810,703)

### contract_type
- Type: `FLOAT`
- Description: A numerical indicator for the contract type
- Nulls: 207,871,691 (71.29%)
- Distinct: 2
- Top values: None (207,871,691), 1 (83,704,073), 0 (98)

### contract_type_description
- Type: `STRING`
- Description: A description of the numerical indicator for the contract type
- Nulls: 207,871,789 (71.29%)
- Distinct: 1
- Top values: None (207,871,789), Supply (83,704,073)

### lowest_uom
- Type: `STRING`
- Description: The lowest unit of measure for the item listed on the invoice
- Nulls: 189,964,676 (65.15%)
- Distinct: 188
- Top values: None (189,964,676), EA (87,255,559), BX (3,305,446), PK (3,108,449), CA (2,089,049)

### lowest_uom_contract_price
- Type: `FLOAT`
- Description: The contract price for the item at the lowest unit of measure
- Nulls: 228,238,249 (78.28%)
- Distinct: 49,656
- Top values: None (228,238,249), 0 (292,090), 7.771 (242,328), 100 (225,437), 0.33 (198,898)

### purchase_uom_contract_price
- Type: `FLOAT`
- Description: The lowest unit of measure contract price multiplied by the purchase order uom conversion factor
- Nulls: 228,238,249 (78.28%)
- Distinct: 72,471
- Top values: None (228,238,249), 0 (292,090), 1942.75 (252,109), 100 (215,622), 0.33 (195,275)

### premier_reference_number
- Type: `STRING`
- Description: An internal Premier reference number used for matching item attributes
- Nulls: 104,835,984 (35.95%)
- Distinct: 291,156
- Top values: None (104,835,984), 6736361 (421,393), 4289350 (306,265), 4119324 (283,506), 9870642 (279,451)

### premier_product_category
- Type: `STRING`
- Description: The product category provide by Premier through item cleansing and matching
- Nulls: 105,236,535 (36.09%)
- Distinct: 603
- Top values: None (105,236,535), GENERAL ORTHOPEDIC TRAUMA PRODUCTS (9,068,667), ORTHOPEDIC TOTAL JOINT IMPLANTS (6,156,982), BANDAGES DRESSINGS AND GAUZE (4,853,804), PATIENT BEDSIDE PRODUCTS (3,859,343)

### premier_item_description
- Type: `STRING`
- Description: The standard item description provide by Premier thorugh item matching and cleansing
- Nulls: 105,236,535 (36.09%)
- Distinct: 289,066
- Top values: None (105,236,535), URINAL PATIENT SUPREME GLOW-IN-DARK STRAIGHT HANDLE HANGING RIBBED BOTTOM GRADUATED TRANSLUCENT W/COVER 1000ML MALE PLASTIC LATEX-FREE NON-STERILE DISPOSABLE 4/CA (421,393), SYRINGE FLUSH POSIFLUSH PRE-FILLED 10ML IN 10ML LUER-LOCK TIP PRESERVATIVE-FREE NORMAL SALINE LATEX-FREE DEHP-FREE PVC-FREE 0.5ML GRAD (339,042), SOLUTION IV LACTATED RINGERS USP 1000ML LVP INJECTION VIAFLEX PLASTIC CONTAINER PRESERVATIVE-FREE LATEX-FREE DEHP PVC SGL PACK (306,265), SOLUTION IV 0.9% SODIUM CHLORIDE USP 1000ML LVP INJECTION VIAFLEX PLASTIC CONTAINER PRESERVATIVE-FREE LATEX-FREE DEHP PVC SGL PACK (283,506)

### premier_manufacturer_name
- Type: `STRING`
- Description: A standardized name for a manufacturer provide by Premier
- Nulls: 92,720,920 (31.80%)
- Distinct: 8,183
- Top values: None (92,720,920), MEDLINE INDUSTRIES, LP (25,653,708), CARDINAL HEALTH 200, LLC (9,493,761), BECTON, DICKINSON AND COMPANY (7,990,530), HOWMEDICA OSTEONICS CORP. DBA STRYKER ORTHOPAEDICS (6,279,868)

### premier_manufacturer_entity_code
- Type: `STRING`
- Description: The entity code used by Premier to identify a manufacturer
- Nulls: 99,563,727 (34.15%)
- Distinct: 8,576
- Top values: None (99,563,727), IL2114 (24,638,041), NJ2019 (7,588,024), OH5010 (7,536,995), MA2109 (4,439,583)

### premier_manufacturer_top_parent_entity_code
- Type: `STRING`
- Description: The top parent entity code used by Premier to identify a parent manufacturer
- Nulls: 100,797,998 (34.57%)
- Distinct: 5,747
- Top values: None (100,797,998), IL2114 (24,880,174), MI5003 (11,599,004), NJ2019 (11,591,613), OH5010 (9,528,341)

### premier_manufacturer_item_number
- Type: `STRING`
- Description: A standardized manufacturer item number provide by Premier through item cleansing and matching
- Nulls: 105,236,535 (36.09%)
- Distinct: 283,229
- Top values: None (105,236,535), DYND80235S (421,393), 2B2324X (306,265), 2B1324X (283,506), 302995 (279,411)

### premier_vendor_name
- Type: `STRING`
- Description: The cleansed vendor name provided by Premier
- Nulls: 17,110,777 (5.87%)
- Distinct: 7,587
- Top values: MEDLINE INDUSTRIES, LP (64,572,313), OWENS & MINOR DISTRIBUTION, INC. (43,330,481), None (17,110,777), CARDINAL HEALTH 414, LLC (16,285,432), STRYKER CORPORATION (13,331,471)

### premier_vendor_entity_code
- Type: `STRING`
- Description: The entity code provided by Premier used to identify a specific vendor
- Nulls: 16,868,933 (5.79%)
- Distinct: 8,865
- Top values: IL2114 (64,547,116), VA2023 (43,321,154), None (16,868,933), OH5010 (9,155,025), IL5027 (6,943,172)

### premier_top_parent_entity_code
- Type: `STRING`
- Description: The top parent manufacturer entity code for the invoice line
- Nulls: 27,204,857 (9.33%)
- Distinct: 5,116
- Top values: IL2114 (64,572,313), VA2023 (43,330,481), None (27,204,857), OH5010 (16,285,432), MI5003 (13,331,394)

### packaging_string
- Type: `STRING`
- Description: The expression of the packaging from the outer UOM to the inner UOM (e.g. 1CA/5BX/20EA)
- Nulls: 119,359,371 (40.94%)
- Distinct: 4,308
- Top values: None (119,359,371), 1EA (48,363,443), 1CA/50EA (4,240,017), 1CA/12EA (3,810,567), 1BX/5EA (3,441,800)

### user_id
- Type: `STRING`
- Description: The user ID that created the invoice in the ERP system, which can be listed as EDI if the invoice import is automated
- Nulls: 70,161,521 (24.06%)
- Distinct: 645
- Top values: EDI (158,739,836), None (70,161,521), HartleyC (3,562,423), kpage (1,711,859), P Norwood (1,364,301)

### invoice_match_status
- Type: `FLOAT`
- Description: A numerical indicator that determines if an invoice has fully matched and is ready for payment or if there are exceptions that are under review
- Nulls: 71,441,367 (24.50%)
- Distinct: 4
- Top values: 3 (203,730,394), None (71,441,367), 4 (16,390,429), 2 (13,088), 1 (584)

### invoice_match_status_description
- Type: `STRING`
- Description: The text string description of the numerical indicator for the review status of an invoice
- Nulls: 71,441,367 (24.50%)
- Distinct: 4
- Top values: Matched (203,730,394), None (71,441,367), Exception (16,390,429), Part Matched (13,088), Unmatched (584)

### invoice_workflow_status
- Type: `FLOAT`
- Description: A numerical indicator that determines the status of an invoice from the exception and matching, approval, and payment.
- Nulls: 71,441,367 (24.50%)
- Distinct: 8
- Top values: 7 (176,716,544), None (71,441,367), 2 (33,951,884), 1 (7,417,567), 6 (1,093,290)

### invoice_workflow_status_description
- Type: `STRING`
- Description: A text string description of the workflow status of an invoice if it is incomplete, has exceptions or is matched, the approval, and final payment status
- Nulls: 71,441,367 (24.50%)
- Distinct: 8
- Top values: Approved (176,716,544), None (71,441,367), Exception (33,951,884), Incomplete (7,417,567), Entered (1,093,290)

### invoice_create_type
- Type: `FLOAT`
- Description: A numerical indicator of how an invoice was created such as from a purchase order, imported, if it is recurring, or if it was created manually
- Nulls: 71,441,367 (24.50%)
- Distinct: 2
- Top values: 1 (220,133,949), None (71,441,367), 3 (546)

### invoice_create_type_description
- Type: `STRING`
- Description: A text string description of how an invoice was created
- Nulls: 71,441,367 (24.50%)
- Distinct: 4
- Top values: EDI 810 (89,442,196), None (71,441,367), IDS PO (70,599,274), From PO (60,092,479), IDS Non-PO (546)

### payment_method
- Type: `FLOAT`
- Description: A numerical indicator of how an invoice was paid, unpaid invoices are listed as local print until paid
- Nulls: 84,475,891 (28.97%)
- Distinct: 8
- Top values: 0 (86,373,281), None (84,475,891), 1 (77,827,069), 5 (15,393,378), 2 (15,269,748)

### payment_method_description
- Type: `STRING`
- Description: A text string description of the payment method including ACH payments, credit payments, and printed checks
- Nulls: 0 (0.00%)
- Distinct: 5
- Top values: Not Paid (220,010,085), Local Print (71,546,917), Credit Card (8,865), ACH (5,291), Check (4,704)

### invoice_810_yn
- Type: `FLOAT`
- Description: A yes or no indicator if an invoice was submitted via EDI
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: 1 (231,482,837), 0 (60,093,025)

### ocr_invoice_yn
- Type: `FLOAT`
- Description: A yes or no indicator if the invoice was imported and transformed using optical character recognition to convert from a pdf or image to searchable text fields
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: 0 (220,976,042), 1 (70,599,820)

### invoice_has_exception_yn
- Type: `FLOAT`
- Description: A yes or no indicator if the invoice has any exceptions
- Nulls: 71,441,367 (24.50%)
- Distinct: 2
- Top values: 0 (129,985,348), 1 (90,149,147), None (71,441,367)

### invoice_line_exception_status
- Type: `STRING`
- Description: An indicator for the current exception type for an invoice line
- Nulls: 71,441,367 (24.50%)
- Distinct: 7
- Top values: N (194,581,129), None (71,441,367), IT (9,162,937), R (8,975,270), P (4,623,779)

### invoice_line_exception_status_description
- Type: `STRING`
- Description: A text string description for the current exception type for an invoice line
- Nulls: 71,441,367 (24.50%)
- Distinct: 7
- Top values: No Exception (194,581,129), None (71,441,367), In Tolerance Price Exception (9,162,937), Receiving Exception (8,975,270), Price Exception (4,623,779)

### invoice_header_exception_status
- Type: `STRING`
- Description: Status of exceptions at the invoice header level.
- Nulls: 289,913,589 (99.43%)
- Distinct: 4
- Top values: None (289,913,589), Total Invoice (1,014,629), Dollar Limit (415,838), Tax EDI (155,833), Expired (75,973)

### missing_line_exception_yn
- Type: `FLOAT`
- Description: A yes or no indicator if the invoice is missing a line causing an exception
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: 0 (288,237,827), 1 (3,338,035)

### price_exception_yn
- Type: `INTEGER`
- Description: A yes or no indicator if there was a price variance from the original purchase order or receipt to the invoice price
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: 0 (277,239,244), 1 (14,336,618)

### quantity_exception_yn
- Type: `INTEGER`
- Description: A yes or no indicator of there was an exception from the original quantity on the purchase order or receipt versus the quantity invoiced
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: 0 (289,071,806), 1 (2,504,056)

### uom_variance_yn
- Type: `INTEGER`
- Description: A yes or no indicator if the units of measure from purchase and receipt to not match the invoiced unit of measure
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: 0 (291,488,515), 1 (87,347)

### edi_invoice_quantity
- Type: `FLOAT`
- Description: Invoiced quantity reported via EDI.
- Nulls: 172,584,902 (59.19%)
- Distinct: 1,355
- Top values: None (172,584,902), 1 (55,217,264), 2 (18,085,256), 3 (7,362,322), 4 (6,560,396)

### edi_invoice_unit_cost
- Type: `FLOAT`
- Description: Unit cost reported via EDI.
- Nulls: 172,584,902 (59.19%)
- Distinct: 168,627
- Top values: None (172,584,902), 0 (2,848,673), 50 (325,675), 75 (306,346), 200 (274,705)

### edi_invoice_line_amount
- Type: `FLOAT`
- Description: Line amount reported via EDI.
- Nulls: 172,584,902 (59.19%)
- Distinct: 206,781
- Top values: None (172,584,902), 0 (4,176,233), 20 (313,555), 600 (273,596), 300 (272,349)

### edi_import_detail_status
- Type: `FLOAT`
- Description: Status code for the EDI import detail.
- Nulls: 172,584,902 (59.19%)
- Distinct: 13
- Top values: None (172,584,902), 1 (48,106,846), 10 (47,577,879), 13 (9,881,376), 5 (5,853,055)

### edi_import_detail_status_description
- Type: `STRING`
- Description: Description of the EDI import detail status.
- Nulls: 172,584,902 (59.19%)
- Distinct: 13
- Top values: None (172,584,902), Ready for Processing (48,106,846), Invoiced (47,577,879), Exception - Receipt Line not found (9,881,376), Exception - PO Line does not exist (5,853,055)

### snapshot_date
- Type: `DATE`
- Description: The date that the invoice match detail was recorded from the health system's ERP
- Nulls: 0 (0.00%)
- Distinct: 368
- Top values: 2026-01-07 (1,102,446), 2026-02-08 (1,043,832), 2025-10-08 (862,051), 2025-11-30 (850,279), 2026-02-10 (804,555)
