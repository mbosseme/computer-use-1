
import json

total_rows = 291575862

# Schema from BigQuery metadata
schema = [
{"Name":"health_system_name","Description":"The name of the health system in Premier's ERP","Type":"STRING"},
{"Name":"account_name","Description":"-","Type":"STRING"},
{"Name":"entity_code","Description":"Internal Premier ERP customer code","Type":"STRING"},
{"Name":"org_number","Description":"The number assigned to an organization in the health system. This value may be a hospital-sized unit, larger, or smaller, depending on how the medical center is structured.","Type":"STRING"},
{"Name":"org_description","Description":"The name for an organization in the health system.","Type":"STRING"},
{"Name":"department_number","Description":"The deliver to department number listed on the purchase order associated with the invoice","Type":"STRING"},
{"Name":"charge_to_department","Description":"An override charge to department number if the deliver to department number is not the correct cost center","Type":"STRING"},
{"Name":"department_description","Description":"A description of the deliver to department number","Type":"STRING"},
{"Name":"invoice_match_header_id","Description":"The internal unique ID used to identify for matching an invoice header","Type":"INTEGER"},
{"Name":"invoice_line_id","Description":"Ther internal unique ID for each line on an invoice","Type":"INTEGER"},
{"Name":"invoice_number","Description":"The invoice document number provide by the invoicing vendor","Type":"STRING"},
{"Name":"invoice_line_number","Description":"The row number of a line on an invoice","Type":"INTEGER"},
{"Name":"erp_item_number","Description":"The health system's internal identifier for an item stored in the item catalog","Type":"STRING"},
{"Name":"item_description","Description":"The health system's defined description for an erp item number","Type":"STRING"},
{"Name":"invoiced_quantity","Description":"The quantity listed on the invoice line","Type":"FLOAT"},
{"Name":"invoiced_uom","Description":"The unit of measure for the quantity listed on the invoice line","Type":"STRING"},
{"Name":"invoiced_unit_cost","Description":"The unit cost for each item or service listed on an invoice line","Type":"FLOAT"},
{"Name":"invoiced_line_amount","Description":"The total extended cost for an invoice line, the unit cost multiplied by the invoice quantity","Type":"FLOAT"},
{"Name":"received_quantity","Description":"The quantity that has been physically received from a purchase order","Type":"FLOAT"},
{"Name":"received_uom","Description":"The unit of measure that was used when a purchase order receipt was completed","Type":"STRING"},
{"Name":"received_uom_conversion_factor","Description":"The conversion factor to the lowest unit of measure from the received unit of measure","Type":"FLOAT"},
{"Name":"received_unit_cost","Description":"The unit cost of the items physically received from a purchase order","Type":"FLOAT"},
{"Name":"received_line_amount","Description":"The extended cost of a receipt line being the unit cost multiplied by the received quantity","Type":"FLOAT"},
{"Name":"quantity_variance","Description":"The difference in the invoiced quantity and the received quantity","Type":"FLOAT"},
{"Name":"price_variance","Description":"The difference in the invoiced line amount and the received line amount","Type":"FLOAT"},
{"Name":"vendor_item_number","Description":"The item number provide by the primary vendor for an ERP item number","Type":"STRING"},
{"Name":"purchase_order_uom","Description":"The unit of measure listed on the purchase order","Type":"STRING"},
{"Name":"purchase_uom_conversion_factor","Description":"The conversion factor to the lowest unit of measure from the purchase order uom","Type":"FLOAT"},
{"Name":"purchase_order_unit_cost","Description":"The unit cost listed on the purchase order line associated with the invoice","Type":"FLOAT"},
{"Name":"assigned_buyer","Description":"The user id for the buyer assigned to the invoiced purchase order","Type":"STRING"},
{"Name":"vendor_number","Description":"The unique number set up in the health system's ERP for the vendor providing the invoice","Type":"STRING"},
{"Name":"vendor_name","Description":"The name of the vendor listed on the invoice","Type":"STRING"},
{"Name":"manufacturer_item_number","Description":"The item number provide by the manufacturer","Type":"STRING"},
{"Name":"manufacturer_id","Description":"The internal ID used to identify a unique manufacturer in the ERP","Type":"STRING"},
{"Name":"manufacturer_name","Description":"The name of the manufacturer listed on the invoice","Type":"STRING"},
{"Name":"expense_code","Description":"The expense code on the purchase order line associated with the invoice line","Type":"STRING"},
{"Name":"expense_code_description","Description":"A description of the expense code on the purchase order line","Type":"STRING"},
{"Name":"invoice_create_date","Description":"The date that the invoice was created in the health system's ERP","Type":"DATE"},
{"Name":"last_modified_date","Description":"The date that invoice line or header was last modified in the health system's ERP","Type":"DATE"},
{"Name":"invoice_due_date","Description":"The due date for payment listed on the invoice","Type":"DATETIME"},
{"Name":"invoice_date","Description":"The date listed on the invoice from the vendor","Type":"DATETIME"},
{"Name":"invoice_received_date","Description":"The date that the invoice was received from the vendor by the health system","Type":"DATETIME"},
{"Name":"approved_date","Description":"The date that the invoice was approved by accounts payable","Type":"DATETIME"},
{"Name":"transaction_date","Description":"The date that the transaction is recorded for GL purposes","Type":"DATETIME"},
{"Name":"posted_date","Description":"The date that the invoice payment was processed and posted in the accounting system","Type":"DATETIME"},
{"Name":"fiscal_period","Description":"A 1-12 month indicator of the financial period varying based on a health system's defined fiscal year","Type":"FLOAT"},
{"Name":"fiscal_year","Description":"The financial year that the invoice transaction took place","Type":"FLOAT"},
{"Name":"payment_terms","Description":"The payment terms on the purchase order determining when final payment is due","Type":"STRING"},
{"Name":"po_number","Description":"The purchase order number linked to the invoice number","Type":"STRING"},
{"Name":"po_header_id","Description":"The internal ID used to identify a unique purchase order","Type":"INTEGER"},
{"Name":"po_line_id","Description":"The ERP internal id used to identify the row level detail on a purchase order","Type":"INTEGER"},
{"Name":"contract_number","Description":"The contract number listed on the purchase order for the invoice","Type":"STRING"},
{"Name":"contract_name","Description":"The description and name of the contract listed on the purchase order for the invoice","Type":"STRING"},
{"Name":"contract_type","Description":"A numerical indicator for the contract type","Type":"FLOAT"},
{"Name":"contract_type_description","Description":"A description of the numerical indicator for the contract type","Type":"STRING"},
{"Name":"lowest_uom","Description":"The lowest unit of measure for the item listed on the invoice","Type":"STRING"},
{"Name":"lowest_uom_contract_price","Description":"The contract price for the item at the lowest unit of measure","Type":"FLOAT"},
{"Name":"purchase_uom_contract_price","Description":"The lowest unit of measure contract price multiplied by the purchase order uom conversion factor","Type":"FLOAT"},
{"Name":"premier_reference_number","Description":"An internal Premier reference number used for matching item attributes","Type":"STRING"},
{"Name":"premier_product_category","Description":"The product category provide by Premier through item cleansing and matching","Type":"STRING"},
{"Name":"premier_item_description","Description":"The standard item description provide by Premier thorugh item matching and cleansing","Type":"STRING"},
{"Name":"premier_manufacturer_name","Description":"A standardized name for a manufacturer provide by Premier","Type":"STRING"},
{"Name":"premier_manufacturer_entity_code","Description":"The entity code used by Premier to identify a manufacturer","Type":"STRING"},
{"Name":"premier_manufacturer_top_parent_entity_code","Description":"The top parent entity code used by Premier to identify a parent manufacturer","Type":"STRING"},
{"Name":"premier_manufacturer_item_number","Description":"A standardized manufacturer item number provide by Premier through item cleansing and matching","Type":"STRING"},
{"Name":"premier_vendor_name","Description":"The cleansed vendor name provided by Premier","Type":"STRING"},
{"Name":"premier_vendor_entity_code","Description":"The entity code provided by Premier used to identify a specific vendor","Type":"STRING"},
{"Name":"premier_top_parent_entity_code","Description":"The top parent manufacturer entity code for the invoice line","Type":"STRING"},
{"Name":"packaging_string","Description":"The expression of the packaging from the outer UOM to the inner UOM (e.g. 1CA/5BX/20EA)","Type":"STRING"},
{"Name":"user_id","Description":"The user ID that created the invoice in the ERP system, which can be listed as EDI if the invoice import is automated","Type":"STRING"},
{"Name":"invoice_match_status","Description":"A numerical indicator that determines if an invoice has fully matched and is ready for payment or if there are exceptions that are under review","Type":"FLOAT"},
{"Name":"invoice_match_status_description","Description":"The text string description of the numerical indicator for the review status of an invoice","Type":"STRING"},
{"Name":"invoice_workflow_status","Description":"A numerical indicator that determines the status of an invoice from the exception and matching, approval, and payment.","Type":"FLOAT"},
{"Name":"invoice_workflow_status_description","Description":"A text string description of the workflow status of an invoice if it is incomplete, has exceptions or is matched, the approval, and final payment status","Type":"STRING"},
{"Name":"invoice_create_type","Description":"A numerical indicator of how an invoice was created such as from a purchase order, imported, if it is recurring, or if it was created manually","Type":"FLOAT"},
{"Name":"invoice_create_type_description","Description":"A text string description of how an invoice was created","Type":"STRING"},
{"Name":"payment_method","Description":"A numerical indicator of how an invoice was paid, unpaid invoices are listed as local print until paid","Type":"FLOAT"},
{"Name":"payment_method_description","Description":"A text string description of the payment method including ACH payments, credit payments, and printed checks","Type":"STRING"},
{"Name":"invoice_810_yn","Description":"A yes or no indicator if an invoice was submitted via EDI","Type":"FLOAT"},
{"Name":"ocr_invoice_yn","Description":"A yes or no indicator if the invoice was imported and transformed using optical character recognition to convert from a pdf or image to searchable text fields","Type":"FLOAT"},
{"Name":"invoice_has_exception_yn","Description":"A yes or no indicator if the invoice has any exceptions","Type":"FLOAT"},
{"Name":"invoice_line_exception_status","Description":"An indicator for the current exception type for an invoice line","Type":"STRING"},
{"Name":"invoice_line_exception_status_description","Description":"A text string description for the current exception type for an invoice line","Type":"STRING"},
{"Name":"invoice_header_exception_status","Description":"-","Type":"STRING"},
{"Name":"missing_line_exception_yn","Description":"A yes or no indicator if the invoice is missing a line causing an exception","Type":"FLOAT"},
{"Name":"price_exception_yn","Description":"A yes or no indicator if there was a price variance from the original purchase order or receipt to the invoice price","Type":"INTEGER"},
{"Name":"quantity_exception_yn","Description":"A yes or no indicator of there was an exception from the original quantity on the purchase order or receipt versus the quantity invoiced","Type":"INTEGER"},
{"Name":"uom_variance_yn","Description":"A yes or no indicator if the units of measure from purchase and receipt to not match the invoiced unit of measure","Type":"INTEGER"},
{"Name":"edi_invoice_quantity","Description":"-","Type":"FLOAT"},
{"Name":"edi_invoice_unit_cost","Description":"-","Type":"FLOAT"},
{"Name":"edi_invoice_line_amount","Description":"-","Type":"FLOAT"},
{"Name":"edi_import_detail_status","Description":"-","Type":"FLOAT"},
{"Name":"edi_import_detail_status_description","Description":"-","Type":"STRING"},
{"Name":"snapshot_date","Description":"The date that the invoice match detail was recorded from the health system's ERP","Type":"DATE"}
]

# Collected stats (merged)
stats = {
"health_system_name": {"nulls": 0, "distinct": 87, "top": [{"count": 25733316, "value": "EM_UCSD"}, {"count": 25466868, "value": "EM_ULHealth"}, {"count": 24582555, "value": "EM_CCH"}, {"count": 18072421, "value": "EM_CCH_Rework"}, {"count": 14777790, "value": "EM_HonorHealth"}]},
"account_name": {"nulls": 945428, "distinct": 88, "top": [{"count": 25733316, "value": "University of California San Diego Health System (AKA UC San Diego Health)"}, {"count": 25466868, "value": "UofL Hospital (AKA University of Louisville Hospital)"}, {"count": 24582555, "value": "Coastal Community Health"}, {"count": 18072421, "value": "CCH_Rework"}, {"count": 14777790, "value": "HonorHealth (FKA Scottsdale Lincoln Health Network)"}]},
"entity_code": {"nulls": 942823, "distinct": 208, "top": [{"count": 25733316, "value": "743158"}, {"count": 18070596, "value": "N/A CCH Duplicate"}, {"count": 14330258, "value": "FL0091"}, {"count": 12771329, "value": "CA3550"}, {"count": 11353669, "value": "KY0080"}]},
"org_number": {"nulls": 0, "distinct": 284, "top": [{"count": 39367017, "value": "001"}, {"count": 30699160, "value": "1"}, {"count": 25274616, "value": "101080"}, {"count": 21413479, "value": "10"}, {"count": 15949457, "value": "01"}]},
"org_description": {"nulls": 13672851, "distinct": 369, "top": [{"count": 23171435, "value": "UCSD MEDICAL CENTER"}, {"count": 22854678, "value": "BAPTIST MEDICAL CENTER - JACKSONVILLE"}, {"count": 12717108, "value": None}, {"count": 8517319, "value": "Renown Regional Medical Center"}, {"count": 7849847, "value": "University Medical Center"}]},
"department_number": {"nulls": 114821255, "distinct": 18021, "top": [{"count": 114821255, "value": None}, {"count": 7354204, "value": "4400"}, {"count": 2262755, "value": "7420-00"}, {"count": 2193655, "value": "6600"}, {"count": 2158881, "value": "6210"}]},
"charge_to_department": {"nulls": 250388783, "distinct": 9266, "top": [{"count": 250388783, "value": None}, {"count": 1806083, "value": "6600"}, {"count": 1077226, "value": "7211"}, {"count": 1021965, "value": "6210"}, {"count": 793735, "value": "7420-00PC"}]},
"department_description": {"nulls": 115831522, "distinct": 18796, "top": [{"count": 115831522, "value": None}, {"count": 11556308, "value": "OPERATING ROOM"}, {"count": 6058129, "value": "SURGERY"}, {"count": 2689608, "value": "OR Operating Room-Main"}, {"count": 2454867, "value": "JHHL OPERATING ROOM"}]},
"invoice_match_header_id": {"nulls": 71441367, "distinct": 2656433, "top": [{"count": 71441367, "value": None}, {"count": 87768, "value": 45343}, {"count": 77437, "value": 5209041}, {"count": 73139, "value": 23520}, {"count": 67468, "value": 5205385}]},
"invoice_line_id": {"nulls": 71441367, "distinct": 9700479, "top": [{"count": 71441367, "value": None}, {"count": 536, "value": 4604911}, {"count": 465, "value": 4363959}, {"count": 459, "value": 4414259}, {"count": 409, "value": 486045}]},
"invoice_number": {"nulls": 0, "distinct": 3851854, "top": [{"count": 145332, "value": "CLEAR OPEN PO"}, {"count": 127349, "value": "CLEAR RNI"}, {"count": 92387, "value": "RNI"}, {"count": 87588, "value": "2048892902"}, {"count": 71857, "value": "2049284215"}]},
"invoice_line_number": {"nulls": 70431013, "distinct": 461, "top": [{"count": 74914178, "value": 1}, {"count": 70431013, "value": None}, {"count": 25998443, "value": 2}, {"count": 16357423, "value": 3}, {"count": 12172731, "value": 4}]},
"erp_item_number": {"nulls": 63611731, "distinct": 503555, "top": [{"count": 63611731, "value": None}, {"count": 233394, "value": "877410100"}, {"count": 218526, "value": "877410090"}, {"count": 207305, "value": "881208715"}, {"count": 205917, "value": "171072"}]},
"item_description": {"nulls": 11723, "distinct": 1710400, "top": [{"count": 241360, "value": "SYRINGE FLSH PSFLSH IV SAL PREFL PRSV FR 10ML"}, {"count": 196553, "value": "Hill Rom Bed Rentals"}, {"count": 174677, "value": "BAG READYBATH FRAG FREE"}, {"count": 147988, "value": "GLOVE PROTEXIS PI PF SYNTH SIZ"}, {"count": 143821, "value": "PACK WARM RAPID RELIEF 6x9"}]},
"invoiced_quantity": {"nulls": 71441367, "distinct": 7147, "top": [{"count": 103238331, "value": 1}, {"count": 71441367, "value": None}, {"count": 34954210, "value": 2}, {"count": 14303404, "value": 3}, {"count": 12871472, "value": 4}]},
"invoiced_uom": {"nulls": 71441367, "distinct": 210, "top": [{"count": 113951690, "value": "EA"}, {"count": 71441367, "value": None}, {"count": 39330571, "value": "CA"}, {"count": 36320752, "value": "BX"}, {"count": 12086186, "value": "PK"}]},
"invoiced_unit_cost": {"nulls": 71441367, "distinct": 292372, "top": [{"count": 71441367, "value": None}, {"count": 4218868, "value": 0}, {"count": 616657, "value": 100}, {"count": 547758, "value": 150}, {"count": 527515, "value": 200}]},
"invoiced_line_amount": {"nulls": 71441367, "distinct": 325822, "top": [{"count": 71441367, "value": None}, {"count": 4376405, "value": 0}, {"count": 537882, "value": 600}, {"count": 523050, "value": 300}, {"count": 491221, "value": 200}]},
"received_quantity": {"nulls": 71441367, "distinct": 7093, "top": [{"count": 101996098, "value": 1}, {"count": 71441367, "value": None}, {"count": 34688552, "value": 2}, {"count": 14199795, "value": 3}, {"count": 12773257, "value": 4}]},
"received_uom": {"nulls": 73463794, "distinct": 193, "top": [{"count": 112442160, "value": "EA"}, {"count": 73463794, "value": None}, {"count": 39203479, "value": "CA"}, {"count": 36229386, "value": "BX"}, {"count": 12036158, "value": "PK"}]},
"received_uom_conversion_factor": {"nulls": 189964676, "distinct": 417, "top": [{"count": 189964676, "value": None}, {"count": 54077767, "value": 1}, {"count": 6261844, "value": 10}, {"count": 4130279, "value": 50}, {"count": 3909456, "value": 5}]},
"received_unit_cost": {"nulls": 71441367, "distinct": 306057, "top": [{"count": 71441367, "value": None}, {"count": 6444021, "value": 0}, {"count": 615571, "value": 100}, {"count": 545554, "value": 200}, {"count": 536522, "value": 150}]},
"received_line_amount": {"nulls": 71441367, "distinct": 331168, "top": [{"count": 71441367, "value": None}, {"count": 6496867, "value": 0}, {"count": 527871, "value": 600}, {"count": 516685, "value": 300}, {"count": 512448, "value": 200}]},
"quantity_variance": {"nulls": 71441367, "distinct": 1011, "top": [{"count": 217630439, "value": 0}, {"count": 71441367, "value": None}, {"count": 1469608, "value": 1}, {"count": 281165, "value": 2}, {"count": 128962, "value": 4}]},
"price_variance": {"nulls": 71441367, "distinct": 60103, "top": [{"count": 205797877, "value": 0}, {"count": 71441367, "value": None}, {"count": 951704, "value": 0.01}, {"count": 880767, "value": -0.01}, {"count": 530497, "value": 0.02}]},
"vendor_item_number": {"nulls": 4710753, "distinct": 717531, "top": [{"count": 4710753, "value": None}, {"count": 716362, "value": "Service"}, {"count": 621965, "value": "UNKNOWN"}, {"count": 444636, "value": "DYND80235S"}, {"count": 359894, "value": "NONE"}]},
"purchase_order_uom": {"nulls": 73596030, "distinct": 205, "top": [{"count": 112019936, "value": "EA"}, {"count": 73596030, "value": None}, {"count": 39273026, "value": "CA"}, {"count": 36277624, "value": "BX"}, {"count": 12047478, "value": "PK"}]},
"purchase_uom_conversion_factor": {"nulls": 73596030, "distinct": 450, "top": [{"count": 134264090, "value": 1}, {"count": 73585587, "value": None}, {"count": 11007146, "value": 10}, {"count": 7278338, "value": 50}, {"count": 6913470, "value": 5}]},
"purchase_order_unit_cost": {"nulls": 73596030, "distinct": 201870, "top": [{"count": 73471549, "value": None}, {"count": 11563976, "value": 0}, {"count": 564487, "value": 100}, {"count": 546008, "value": 200}, {"count": 526820, "value": 150}]},
"assigned_buyer": {"nulls": 71441913, "distinct": 1957, "top": [{"count": 71441367, "value": None}, {"count": 21536422, "value": "Admin"}, {"count": 21270535, "value": "WWEWE001"}, {"count": 9393093, "value": "SSOUR001"}, {"count": 6630842, "value": "mkkastner"}]},
"vendor_number": {"nulls": 0, "distinct": 42366, "top": [{"count": 28473160, "value": "101016"}, {"count": 15649720, "value": "0034560"}, {"count": 9670104, "value": "902047"}, {"count": 7704851, "value": "6510"}, {"count": 5849542, "value": "101732"}]},
"vendor_name": {"nulls": 12887435, "distinct": 32927, "top": [{"count": 38134829, "value": "MEDLINE INDUSTRIES INC"}, {"count": 26318979, "value": "OWENS AND MINOR INC"}, {"count": 15043035, "value": "MEDLINE INDUSTRIES INC (STOCK ONLY LUM)"}, {"count": 12688111, "value": None}, {"count": 8577075, "value": "OWENS & MINOR INC"}]},
"manufacturer_item_number": {"nulls": 64209489, "distinct": 606863, "top": [{"count": 64201118, "value": None}, {"count": 1813393, "value": "UNKNOWN"}, {"count": 1534481, "value": "1"}, {"count": 628875, "value": "Service"}, {"count": 479936, "value": "none"}]},
"manufacturer_id": {"nulls": 73331386, "distinct": 30445, "top": [{"count": 73331119, "value": None}, {"count": 10946047, "value": "UNKNOWN"}, {"count": 6980853, "value": "MEDLINE"}, {"count": 3474215, "value": "MEDL"}, {"count": 3138144, "value": "1"}]},
"manufacturer_name": {"nulls": 77580453, "distinct": 28755, "top": [{"count": 77580453, "value": None}, {"count": 16551563, "value": "MEDLINE INDUSTRIES INC"}, {"count": 13120232, "value": "UNKNOWN"}, {"count": 4878450, "value": "MEDLINE"}, {"count": 3787889, "value": "NONE"}]},
"expense_code": {"nulls": 83175000, "distinct": 6092, "top": [{"count": 83175000, "value": None}, {"count": 25864825, "value": "6210000"}, {"count": 11551418, "value": "520500"}, {"count": 5304843, "value": "602140"}, {"count": 3860634, "value": "70050"}]},
"expense_code_description": {"nulls": 83937864, "distinct": 4795, "top": [{"count": 83937864, "value": None}, {"count": 26722372, "value": "MED/SURG SUPPLIES"}, {"count": 11551418, "value": "MEDICAL CARE MATERIALS AND SUPPLIES"}, {"count": 9449422, "value": "MEDICAL SUPPLIES"}, {"count": 5268215, "value": "Supplies-Other Medical"}]},
"invoice_create_date": {"nulls": 0, "distinct": 3838, "top": [{"count": 2120020, "value": "2019-08-14"}, {"count": 1914834, "value": "2019-08-17"}, {"count": 1853183, "value": "2019-08-16"}, {"count": 1850610, "value": "2019-08-20"}, {"count": 1724841, "value": "2019-08-13"}]},
"last_modified_date": {"nulls": 921007, "distinct": 3540, "top": [{"count": 4099540, "value": "2019-08-20"}, {"count": 2157304, "value": "2025-04-04"}, {"count": 1814363, "value": "2025-05-29"}, {"count": 1664531, "value": "2019-08-14"}, {"count": 1612140, "value": "2019-08-16"}]},
"invoice_due_date": {"nulls": 71449974, "distinct": 3157, "top": [{"count": 71441367, "value": None}, {"count": 2181718, "value": "2019-08-28T00:00:00"}, {"count": 2139008, "value": "2019-08-30T00:00:00"}, {"count": 1560732, "value": "2019-08-31T00:00:00"}, {"count": 1439462, "value": "2019-08-27T00:00:00"}]},
"invoice_date": {"nulls": 71441367, "distinct": 2836, "top": [{"count": 71441367, "value": None}, {"count": 2135493, "value": "2019-08-13T00:00:00"}, {"count": 2014950, "value": "2019-08-15T00:00:00"}, {"count": 1585362, "value": "2019-08-12T00:00:00"}, {"count": 1571493, "value": "2019-08-16T00:00:00"}]},
"invoice_received_date": {"nulls": 71441367, "distinct": 2451, "top": [{"count": 71441367, "value": None}, {"count": 2170842, "value": "2019-08-14T00:00:00"}, {"count": 1941250, "value": "2019-08-17T00:00:00"}, {"count": 1856069, "value": "2019-08-16T00:00:00"}, {"count": 1621627, "value": "2019-08-20T00:00:00"}]},
"approved_date": {"nulls": 114734272, "distinct": 2236, "top": [{"count": 114734272, "value": None}, {"count": 1538756, "value": "2019-08-14T00:00:00"}, {"count": 1476866, "value": "2019-08-16T00:00:00"}, {"count": 1377566, "value": "2019-08-13T00:00:00"}, {"count": 1167558, "value": "2019-08-20T00:00:00"}]},
"transaction_date": {"nulls": 71441367, "distinct": 2372, "top": [{"count": 71441367, "value": None}, {"count": 2165322, "value": "2019-08-14T00:00:00"}, {"count": 1955970, "value": "2019-08-17T00:00:00"}, {"count": 1848706, "value": "2019-08-16T00:00:00"}, {"count": 1624571, "value": "2019-08-20T00:00:00"}]},
"posted_date": {"nulls": 114734272, "distinct": 2236, "top": [{"count": 114734272, "value": None}, {"count": 1538756, "value": "2019-08-14T00:00:00"}, {"count": 1476866, "value": "2019-08-16T00:00:00"}, {"count": 1377566, "value": "2019-08-13T00:00:00"}, {"count": 1167558, "value": "2019-08-20T00:00:00"}]},
"fiscal_period": {"nulls": 71441367, "distinct": 12, "top": [{"count": 71441367, "value": None}, {"count": 30571821, "value": 11}, {"count": 23296425, "value": 5}, {"count": 17794524, "value": 2}, {"count": 17694462, "value": 4}]},
"fiscal_year": {"nulls": 71441367, "distinct": 18, "top": [{"count": 120184703, "value": 2025}, {"count": 71441367, "value": None}, {"count": 62481800, "value": 2026}, {"count": 19532728, "value": 2019}, {"count": 6117056, "value": 2022}]},
"payment_terms": {"nulls": 71449974, "distinct": 339, "top": [{"count": 71441367, "value": None}, {"count": 43045356, "value": "N30"}, {"count": 27074432, "value": "30"}, {"count": 22141564, "value": "Net15"}, {"count": 13215825, "value": "NET30"}]},
"po_number": {"nulls": 0, "distinct": 2478505, "top": [{"count": 201664, "value": "B14197"}, {"count": 151286, "value": "611852"}, {"count": 119612, "value": "611859"}, {"count": 94473, "value": "101080003917"}, {"count": 92191, "value": "10006"}]},
"po_header_id": {"nulls": 71441367, "distinct": 1732681, "top": [{"count": 71441367, "value": None}, {"count": 180688, "value": 101566}, {"count": 94444, "value": 5306}, {"count": 89181, "value": 1999821}, {"count": 84589, "value": 101595}]},
"po_line_id": {"nulls": 71492916, "distinct": 8566185, "top": [{"count": 71492916, "value": None}, {"count": 1970878, "value": 0}, {"count": 83853, "value": 377163}, {"count": 68407, "value": 375246}, {"count": 65091, "value": 316814}]},
"contract_number": {"nulls": 203830906, "distinct": 14159, "top": [{"count": 203830906, "value": None}, {"count": 2819180, "value": "redacted"}, {"count": 1599381, "value": "ML-2025-020"}, {"count": 1404731, "value": "LC71287"}, {"count": 810703, "value": "G5725CM-2025-08"}]},
"contract_name": {"nulls": 205593269, "distinct": 7605, "top": [{"count": 205593269, "value": None}, {"count": 2819180, "value": "redacted"}, {"count": 1894848, "value": "Medline CatchAll"}, {"count": 1405969, "value": "Stryker Wright Trauma Amendment"}, {"count": 810703, "value": "Medline UC Misc Products 2025-08"}]},
"contract_type": {"nulls": 207871691, "distinct": 2, "top": [{"count": 207871691, "value": None}, {"count": 83704073, "value": 1}, {"count": 98, "value": 0}]},
"contract_type_description": {"nulls": 207871789, "distinct": 1, "top": [{"count": 207871789, "value": None}, {"count": 83704073, "value": "Supply"}]},
"lowest_uom": {"nulls": 189964676, "distinct": 188, "top": [{"count": 189964676, "value": None}, {"count": 87255559, "value": "EA"}, {"count": 3305446, "value": "BX"}, {"count": 3108449, "value": "PK"}, {"count": 2089049, "value": "CA"}]},
"lowest_uom_contract_price": {"nulls": 228238249, "distinct": 49656, "top": [{"count": 228238249, "value": None}, {"count": 292090, "value": 0}, {"count": 242328, "value": 7.771}, {"count": 225437, "value": 100}, {"count": 198898, "value": 0.33}]},
"purchase_uom_contract_price": {"nulls": 228238249, "distinct": 72471, "top": [{"count": 228238249, "value": None}, {"count": 292090, "value": 0}, {"count": 252109, "value": 1942.75}, {"count": 215622, "value": 100}, {"count": 195275, "value": 0.33}]},
"premier_reference_number": {"nulls": 104835984, "distinct": 291156, "top": [{"count": 104835984, "value": None}, {"count": 421393, "value": "6736361"}, {"count": 306265, "value": "4289350"}, {"count": 283506, "value": "4119324"}, {"count": 279451, "value": "9870642"}]},
"premier_product_category": {"nulls": 105236535, "distinct": 603, "top": [{"count": 105236535, "value": None}, {"count": 9068667, "value": "GENERAL ORTHOPEDIC TRAUMA PRODUCTS"}, {"count": 6156982, "value": "ORTHOPEDIC TOTAL JOINT IMPLANTS"}, {"count": 4853804, "value": "BANDAGES DRESSINGS AND GAUZE"}, {"count": 3859343, "value": "PATIENT BEDSIDE PRODUCTS"}]},
"premier_item_description": {"nulls": 105236535, "distinct": 289066, "top": [{"count": 105236535, "value": None}, {"count": 421393, "value": "URINAL PATIENT SUPREME GLOW-IN-DARK STRAIGHT HANDLE HANGING RIBBED BOTTOM GRADUATED TRANSLUCENT W/COVER 1000ML MALE PLASTIC LATEX-FREE NON-STERILE DISPOSABLE 4/CA"}, {"count": 339042, "value": "SYRINGE FLUSH POSIFLUSH PRE-FILLED 10ML IN 10ML LUER-LOCK TIP PRESERVATIVE-FREE NORMAL SALINE LATEX-FREE DEHP-FREE PVC-FREE 0.5ML GRAD"}, {"count": 306265, "value": "SOLUTION IV LACTATED RINGERS USP 1000ML LVP INJECTION VIAFLEX PLASTIC CONTAINER PRESERVATIVE-FREE LATEX-FREE DEHP PVC SGL PACK"}, {"count": 283506, "value": "SOLUTION IV 0.9% SODIUM CHLORIDE USP 1000ML LVP INJECTION VIAFLEX PLASTIC CONTAINER PRESERVATIVE-FREE LATEX-FREE DEHP PVC SGL PACK"}]},
"premier_manufacturer_name": {"nulls": 92720920, "distinct": 8183, "top": [{"count": 92720920, "value": None}, {"count": 25653708, "value": "MEDLINE INDUSTRIES, LP"}, {"count": 9493761, "value": "CARDINAL HEALTH 200, LLC"}, {"count": 7990530, "value": "BECTON, DICKINSON AND COMPANY"}, {"count": 6279868, "value": "HOWMEDICA OSTEONICS CORP. DBA STRYKER ORTHOPAEDICS"}]},
"premier_manufacturer_entity_code": {"nulls": 99563727, "distinct": 8576, "top": [{"count": 99563727, "value": None}, {"count": 24638041, "value": "IL2114"}, {"count": 7588024, "value": "NJ2019"}, {"count": 7536995, "value": "OH5010"}, {"count": 4439583, "value": "MA2109"}]},
"premier_manufacturer_top_parent_entity_code": {"nulls": 100797998, "distinct": 5747, "top": [{"count": 100797998, "value": None}, {"count": 24880174, "value": "IL2114"}, {"count": 11599004, "value": "MI5003"}, {"count": 11591613, "value": "NJ2019"}, {"count": 9528341, "value": "OH5010"}]},
"premier_manufacturer_item_number": {"nulls": 105236535, "distinct": 283229, "top": [{"count": 105236535, "value": None}, {"count": 421393, "value": "DYND80235S"}, {"count": 306265, "value": "2B2324X"}, {"count": 283506, "value": "2B1324X"}, {"count": 279411, "value": "302995"}]},
"premier_vendor_name": {"nulls": 17110777, "distinct": 7587, "top": [{"count": 64572313, "value": "MEDLINE INDUSTRIES, LP"}, {"count": 43330481, "value": "OWENS & MINOR DISTRIBUTION, INC."}, {"count": 17110777, "value": None}, {"count": 16285432, "value": "CARDINAL HEALTH 414, LLC"}, {"count": 13331471, "value": "STRYKER CORPORATION"}]},
"premier_vendor_entity_code": {"nulls": 16868933, "distinct": 8865, "top": [{"count": 64547116, "value": "IL2114"}, {"count": 43321154, "value": "VA2023"}, {"count": 16868933, "value": None}, {"count": 9155025, "value": "OH5010"}, {"count": 6943172, "value": "IL5027"}]},
"premier_top_parent_entity_code": {"nulls": 27204857, "distinct": 5116, "top": [{"count": 64572313, "value": "IL2114"}, {"count": 43330481, "value": "VA2023"}, {"count": 27204857, "value": None}, {"count": 16285432, "value": "OH5010"}, {"count": 13331394, "value": "MI5003"}]},
"packaging_string": {"nulls": 119359371, "distinct": 4308, "top": [{"count": 119359371, "value": None}, {"count": 48363443, "value": "1EA"}, {"count": 4240017, "value": "1CA/50EA"}, {"count": 3810567, "value": "1CA/12EA"}, {"count": 3441800, "value": "1BX/5EA"}]},
"user_id": {"nulls": 70161521, "distinct": 645, "top": [{"count": 158739836, "value": "EDI"}, {"count": 70161521, "value": None}, {"count": 3562423, "value": "HartleyC"}, {"count": 1711859, "value": "kpage"}, {"count": 1364301, "value": "P Norwood"}]},
"invoice_match_status": {"nulls": 71441367, "distinct": 4, "top": [{"count": 203730394, "value": 3}, {"count": 71441367, "value": None}, {"count": 16390429, "value": 4}, {"count": 13088, "value": 2}, {"count": 584, "value": 1}]},
"invoice_match_status_description": {"nulls": 71441367, "distinct": 4, "top": [{"count": 203730394, "value": "Matched"}, {"count": 71441367, "value": None}, {"count": 16390429, "value": "Exception"}, {"count": 13088, "value": "Part Matched"}, {"count": 584, "value": "Unmatched"}]},
"invoice_workflow_status": {"nulls": 71441367, "distinct": 8, "top": [{"count": 176716544, "value": 7}, {"count": 71441367, "value": None}, {"count": 33951884, "value": 2}, {"count": 7417567, "value": 1}, {"count": 1093290, "value": 6}]},
"invoice_workflow_status_description": {"nulls": 71441367, "distinct": 8, "top": [{"count": 176716544, "value": "Approved"}, {"count": 71441367, "value": None}, {"count": 33951884, "value": "Exception"}, {"count": 7417567, "value": "Incomplete"}, {"count": 1093290, "value": "Entered"}]},
"invoice_create_type": {"nulls": 71441367, "distinct": 2, "top": [{"count": 220133949, "value": 1}, {"count": 71441367, "value": None}, {"count": 546, "value": 3}]},
"invoice_create_type_description": {"nulls": 71441367, "distinct": 4, "top": [{"count": 89442196, "value": "EDI 810"}, {"count": 71441367, "value": None}, {"count": 70599274, "value": "IDS PO"}, {"count": 60092479, "value": "From PO"}, {"count": 546, "value": "IDS Non-PO"}]},
"payment_method": {"nulls": 84475891, "distinct": 8, "top": [{"count": 86373281, "value": 0}, {"count": 84475891, "value": None}, {"count": 77827069, "value": 1}, {"count": 15393378, "value": 5}, {"count": 15269748, "value": 2}]},
"payment_method_description": {"nulls": 0, "distinct": 5, "top": [{"count": 220010085, "value": "Not Paid"}, {"count": 71546917, "value": "Local Print"}, {"count": 8865, "value": "Credit Card"}, {"count": 5291, "value": "ACH"}, {"count": 4704, "value": "Check"}]},
"invoice_810_yn": {"nulls": 0, "distinct": 2, "top": [{"count": 231482837, "value": 1}, {"count": 60093025, "value": 0}]},
"ocr_invoice_yn": {"nulls": 0, "distinct": 2, "top": [{"count": 220976042, "value": 0}, {"count": 70599820, "value": 1}]},
"invoice_has_exception_yn": {"nulls": 71441367, "distinct": 2, "top": [{"count": 129985348, "value": 0}, {"count": 90149147, "value": 1}, {"count": 71441367, "value": None}]},
"invoice_line_exception_status": {"nulls": 71441367, "distinct": 7, "top": [{"count": 194581129, "value": "N"}, {"count": 71441367, "value": None}, {"count": 9162937, "value": "IT"}, {"count": 8975270, "value": "R"}, {"count": 4623779, "value": "P"}]},
"invoice_line_exception_status_description": {"nulls": 71441367, "distinct": 7, "top": [{"count": 194581129, "value": "No Exception"}, {"count": 71441367, "value": None}, {"count": 9162937, "value": "In Tolerance Price Exception"}, {"count": 8975270, "value": "Receiving Exception"}, {"count": 4623779, "value": "Price Exception"}]},
"invoice_header_exception_status": {"nulls": 289913589, "distinct": 4, "top": [{"count": 289913589, "value": None}, {"count": 1014629, "value": "Total Invoice"}, {"count": 415838, "value": "Dollar Limit"}, {"count": 155833, "value": "Tax EDI"}, {"count": 75973, "value": "Expired"}]},
"missing_line_exception_yn": {"nulls": 0, "distinct": 2, "top": [{"count": 288237827, "value": 0}, {"count": 3338035, "value": 1}]},
"price_exception_yn": {"nulls": 0, "distinct": 2, "top": [{"count": 277239244, "value": 0}, {"count": 14336618, "value": 1}]},
"quantity_exception_yn": {"nulls": 0, "distinct": 2, "top": [{"count": 289071806, "value": 0}, {"count": 2504056, "value": 1}]},
"uom_variance_yn": {"nulls": 0, "distinct": 2, "top": [{"count": 291488515, "value": 0}, {"count": 87347, "value": 1}]},
"edi_invoice_quantity": {"nulls": 172584902, "distinct": 1355, "top": [{"count": 172584902, "value": None}, {"count": 55217264, "value": 1}, {"count": 18085256, "value": 2}, {"count": 7362322, "value": 3}, {"count": 6560396, "value": 4}]},
"edi_invoice_unit_cost": {"nulls": 172584902, "distinct": 168627, "top": [{"count": 172584902, "value": None}, {"count": 2848673, "value": 0}, {"count": 325675, "value": 50}, {"count": 306346, "value": 75}, {"count": 274705, "value": 200}]},
"edi_invoice_line_amount": {"nulls": 172584902, "distinct": 206781, "top": [{"count": 172584902, "value": None}, {"count": 4176233, "value": 0}, {"count": 313555, "value": 20}, {"count": 273596, "value": 600}, {"count": 272349, "value": 300}]},
"edi_import_detail_status": {"nulls": 172584902, "distinct": 13, "top": [{"count": 172584902, "value": None}, {"count": 48106846, "value": 1}, {"count": 47577879, "value": 10}, {"count": 9881376, "value": 13}, {"count": 5853055, "value": 5}]},
"edi_import_detail_status_description": {"nulls": 172584902, "distinct": 13, "top": [{"count": 172584902, "value": None}, {"count": 48106846, "value": "Ready for Processing"}, {"count": 47577879, "value": "Invoiced"}, {"count": 9881376, "value": "Exception - Receipt Line not found"}, {"count": 5853055, "value": "Exception - PO Line does not exist"}]},
"snapshot_date": {"nulls": 0, "distinct": 368, "top": [{"count": 1102446, "value": "2026-01-07"}, {"count": 1043832, "value": "2026-02-08"}, {"count": 862051, "value": "2025-10-08"}, {"count": 850279, "value": "2025-11-30"}, {"count": 804555, "value": "2026-02-10"}]}
}

header = """# Data Dictionary: `provider_invoice_match`

- **Full Path:** `premierinc-com-data.invoicing_provider_match.provider_invoice_match`
- **Description:** This table stores a daily history of open invoices with exception and matching status prior to payment through an ERP. Unique records in this table can be identified by org_number, invoice_match_header_id, invoice_line_number, and snapshot_date. New or changed records can be identified from the created_date and last_modified_date. This table is updated Monday through Friday by 5PM EST.
- **Estimated Rows:** {rows:,}
- **Generated:** Manual context + MCP extraction

## Columns
""".format(rows=total_rows)

columns_md = []

def format_value(v):
    if v is None:
        return "None"
    return str(v)

for col in schema:
    c_name = col["Name"]
    c_type = col["Type"]
    c_desc = col["Description"] if col["Description"] and col["Description"] != "-" else "Description not available."
    
    # Infer descriptions for known "-" fields (manual override)
    if c_name == "account_name" and c_desc == "Description not available.":
        c_desc = "The account name associated with the health system."
    elif c_name == "invoice_header_exception_status" and c_desc == "Description not available.":
        c_desc = "Status of exceptions at the invoice header level."
    elif c_name == "edi_invoice_quantity" and c_desc == "Description not available.":
        c_desc = "Invoiced quantity reported via EDI."
    elif c_name == "edi_invoice_unit_cost" and c_desc == "Description not available.":
         c_desc = "Unit cost reported via EDI."
    elif c_name == "edi_invoice_line_amount" and c_desc == "Description not available.":
         c_desc = "Line amount reported via EDI."
    elif c_name == "edi_import_detail_status" and c_desc == "Description not available.":
         c_desc = "Status code for the EDI import detail."
    elif c_name == "edi_import_detail_status_description" and c_desc == "Description not available.":
         c_desc = "Description of the EDI import detail status."

    
    c_stats = stats.get(c_name, {})
    nulls = c_stats.get("nulls", 0)
    distinct = c_stats.get("distinct", 0)
    top = c_stats.get("top", [])
    
    null_pct = (nulls / total_rows) * 100
    
    top_values_str = ", ".join([f"{format_value(res['value'])} ({res['count']:,})" for res in top])
    
    col_block = f"""
### {c_name}
- Type: `{c_type}`
- Description: {c_desc}
- Nulls: {nulls:,} ({null_pct:.2f}%)
- Distinct: {distinct:,}
- Top values: {top_values_str}
"""
    columns_md.append(col_block)

final_md = header + "\n" + "".join(columns_md)

import os

output_path = os.path.join(os.getcwd(), "docs/data_dictionaries/premierinc-com-data.invoicing_provider_match.provider_invoice_match.md")
print(f"Writing to {output_path}...")
try:
    with open(output_path, "w") as f:
        f.write(final_md)
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
