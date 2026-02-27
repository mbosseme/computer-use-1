# Data Dictionary: provider_invoice_line_level_history
**Table**: `abi-outbound-prod.abi_outbound_bq_tgt_invoicing_provider_match.provider_invoice_line_level_details`
**Description**: This table contains detailed line-level information for provider invoices, including item descriptions, quantities, costs, and matching status against purchase orders and receipts. It serves as a comprehensive record of invoice transactions within the health system's financial and procurement processes.
**Total Records**: 148,592,826

## Columns
### health_system_name
- **Type**: `STRING`
- **Description**: The name of the health system to which the invoice is associated. It identifies the larger healthcare organization within the context of the ERP system.
- **Distinct Values**: 245
- **Nulls**: 5881 (<0.01%)
- **Top Values**:
  - `UC San Diego Health`: 9,763,717 (6.57%)
  - `Adventist Health`: 8,607,144 (5.79%)
  - `Baptist Health (Jacksonville, FL)`: 7,729,577 (5.20%)
  - `UCI Health`: 4,943,985 (3.33%)
  - `OSF Healthcare System`: 4,818,789 (3.24%)

---
### entity_code
- **Type**: `STRING`
- **Description**: A unique code representing the entity within the health system, such as a specific hospital or department, involved in the invoice transaction.
- **Distinct Values**: 235
- **Nulls**: 23416398 (15.76%)
- **Top Values**:
  - `NULL`: 23,416,398 (15.76%)
  - `GHX`: 3,240,294 (2.18%)
  - `050`: 2,891,969 (1.95%)
  - `5078`: 2,343,467 (1.58%)
  - `8920`: 2,297,545 (1.55%)

---
### direct_parent_name
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 1279
- **Nulls**: 23416398 (15.76%)
- **Top Values**:
  - `NULL`: 23,416,398 (15.76%)
  - `Baptist Health System - AL`: 1,725,286 (1.16%)
  - `Banner Health - AZ`: 1,441,099 (0.97%)
  - `PeaceHealth`: 1,438,965 (0.97%)
  - `Saint Francis Health System - OK`: 1,341,857 (0.90%)

---
### direct_parent_entity_code
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 1298
- **Nulls**: 23416752 (15.76%)
- **Top Values**:
  - `NULL`: 23,416,752 (15.76%)
  - `255986`: 1,725,286 (1.16%)
  - `261699`: 1,441,099 (0.97%)
  - `260273`: 1,438,965 (0.97%)
  - `513478`: 1,341,857 (0.90%)

---
### org_number
- **Type**: `STRING`
- **Description**: A number identifying the organizational unit within the health system, such as facility.
- **Distinct Values**: 226
- **Nulls**: 23725596 (15.97%)
- **Top Values**:
  - `NULL`: 23,725,596 (15.97%)
  - `03791`: 3,393,343 (2.28%)
  - `050`: 2,891,969 (1.95%)
  - `05078`: 2,343,467 (1.58%)
  - `08920`: 2,297,545 (1.55%)

---
### org_description
- **Type**: `STRING`
- **Description**: A textual description providing details about the organizational unit mentioned in org_number.
- **Distinct Values**: 226
- **Nulls**: 23725596 (15.97%)
- **Top Values**:
  - `NULL`: 23,725,596 (15.97%)
  - `GHX`: 10,547,781 (7.10%)
  - `UC San Diego Health System`: 9,662,136 (6.50%)
  - `Adventist Health`: 8,980,327 (6.04%)
  - `Baptist Medical Center Jacksonvle`: 7,083,163 (4.77%)

---
### remitra_invoice_header_id
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 12204550
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `21110825`: 1,374 (<0.01%)
  - `21128362`: 600 (<0.01%)
  - `28169123`: 597 (<0.01%)
  - `28167812`: 597 (<0.01%)

---
### department_number
- **Type**: `STRING`
- **Description**: A code or number representing the specific department within the organizational unit mentioned in org_number.
- **Distinct Values**: 23432
- **Nulls**: 23725596 (15.97%)
- **Top Values**:
  - `NULL`: 23,725,596 (15.97%)
  - `0`: 372,996 (0.25%)
  - `7010`: 327,916 (0.22%)
  - `7310`: 316,315 (0.21%)
  - `7020`: 307,553 (0.21%)

---
### charge_to_department
- **Type**: `STRING`
- **Description**: Indicates the department to which the charges in the invoice are attributed or assigned.
- **Distinct Values**: 22466
- **Nulls**: 138406132 (93.14%)
- **Top Values**:
  - `NULL`: 138,406,132 (93.14%)
  - `18650`: 68,478 (0.05%)
  - `4039.63000`: 39,999 (0.03%)
  - `71050`: 36,124 (0.02%)
  - `71110`: 30,737 (0.02%)

---
### department_description
- **Type**: `STRING`
- **Description**: A description explaining the nature or purpose of the department mentioned in charge_to_department.
- **Distinct Values**: 37025
- **Nulls**: 23727546 (15.97%)
- **Top Values**:
  - `NULL`: 23,727,546 (15.97%)
  - `Pharmacy`: 12,975,070 (8.73%)
  - `OR`: 9,110,190 (6.13%)
  - `Surgery`: 3,678,037 (2.48%)
  - `Cath Lab`: 3,533,927 (2.38%)

---
### invoice_match_header_id
- **Type**: `INTEGER`
- **Description**: A unique identifier linking the invoice line to a corresponding invoice match header. It facilitates grouping related invoice lines for processing and management.
- **Distinct Values**: 12204550
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `21110825`: 1,374 (<0.01%)
  - `21128362`: 600 (<0.01%)
  - `28169123`: 597 (<0.01%)
  - `28167812`: 597 (<0.01%)

---
### invoice_line_id
- **Type**: `INTEGER`
- **Description**: A unique identifier for each individual invoice line within the hospital invoice database. It distinguishes one line item from another.
- **Distinct Values**: 148633390
- **Nulls**: 0 (0%)
- **Top Values**:
  - `1568205462`: 1 (<0.01%)
  - `1568205463`: 1 (<0.01%)
  - `1568205464`: 1 (<0.01%)
  - `1568205465`: 1 (<0.01%)
  - `1568205466`: 1 (<0.01%)

---
### invoice_number
- **Type**: `STRING`
- **Description**: A unique identifier for the invoice, allowing it to be tracked and referenced in the hospital's ERP system.
- **Distinct Values**: 12579169
- **Nulls**: 0 (0%)
- **Top Values**:
  - `90632349`: 5,190 (<0.01%)
  - `90779774`: 2,342 (<0.01%)
  - `3000627584`: 2,236 (<0.01%)
  - `3000639906`: 1,874 (<0.01%)
  - `90632832`: 1,815 (<0.01%)

---
### invoice_line_number
- **Type**: `INTEGER`
- **Description**: A sequential number indicating the position of the line item within the invoice.
- **Distinct Values**: 4680
- **Nulls**: 1824 (<0.01%)
- **Top Values**:
  - `1`: 10,985,226 (7.39%)
  - `2`: 8,766,436 (5.90%)
  - `3`: 7,091,605 (4.77%)
  - `4`: 5,960,417 (4.01%)
  - `5`: 5,136,893 (3.46%)

---
### vendor_item_number
- **Type**: `STRING`
- **Description**: The unique identifier or code used by the vendor/supplier to identify the item or product being invoiced.
- **Distinct Values**: 2598370
- **Nulls**: 6045 (<0.01%)
- **Top Values**:
  - `FREIGHT`: 235,282 (0.16%)
  - `SHIPPING`: 74,971 (0.05%)
  - `TAX`: 54,531 (0.04%)
  - `1052`: 25,218 (0.02%)
  - `MISC`: 20,658 (0.01%)

---
### item_description
- **Type**: `STRING`
- **Description**: A description providing details about the invoice line, explaining the product or service being invoiced.
- **Distinct Values**: 6467060
- **Nulls**: 738739 (0.50%)
- **Top Values**:
  - `NULL`: 738,739 (0.50%)
  - `FREIGHT`: 365,738 (0.25%)
  - `SHIPPING`: 153,406 (0.10%)
  - `TAX`: 132,646 (0.09%)
  - `Freight`: 77,708 (0.05%)

---
### invoiced_quantity
- **Type**: `FLOAT`
- **Description**: The quantity of the item or service invoiced, represented as a floating-point number to allow for decimal values.
- **Distinct Values**: 36894
- **Nulls**: 7066 (<0.01%)
- **Top Values**:
  - `1`: 46,387,062 (31.22%)
  - `2`: 20,265,147 (13.64%)
  - `3`: 9,984,954 (6.72%)
  - `4`: 7,153,920 (4.81%)
  - `6`: 5,140,366 (3.46%)

---
### invoiced_uom
- **Type**: `STRING`
- **Description**: The unit of measure (UOM) for the invoiced quantity, indicating how the quantity is measured (e.g., kilograms, hours, units).
- **Distinct Values**: 1441
- **Nulls**: 83625 (0.06%)
- **Top Values**:
  - `EA`: 51,754,020 (34.83%)
  - `EACH`: 31,153,770 (20.97%)
  - `CA`: 16,616,032 (11.18%)
  - `CS`: 12,643,542 (8.51%)
  - `BX`: 10,036,631 (6.75%)

---
### invoiced_unit_cost
- **Type**: `FLOAT`
- **Description**: The cost per unit of the invoiced item or service, represented as a floating-point number.
- **Distinct Values**: 483424
- **Nulls**: 6045 (<0.01%)
- **Top Values**:
  - `0`: 20,743,126 (13.96%)
  - `0.01`: 471,850 (0.32%)
  - `15`: 261,494 (0.18%)
  - `18`: 240,656 (0.16%)
  - `20`: 201,460 (0.14%)

---
### invoiced_line_amount
- **Type**: `FLOAT`
- **Description**: The total monetary amount for the invoiced line, calculated by multiplying the invoiced quantity by the invoiced unit cost.
- **Distinct Values**: 553313
- **Nulls**: 7458 (<0.01%)
- **Top Values**:
  - `0`: 3,572,237 (2.40%)
  - `0.01`: 368,739 (0.25%)
  - `15`: 196,504 (0.13%)
  - `30`: 166,827 (0.11%)
  - `20`: 144,414 (0.10%)

---
### received_quantity
- **Type**: `FLOAT`
- **Description**: The quantity of the item or service received, represented as a floating-point number.
- **Distinct Values**: 21835
- **Nulls**: 94318788 (63.47%)
- **Top Values**:
  - `NULL`: 94,318,788 (63.47%)
  - `1`: 16,609,939 (11.18%)
  - `2`: 7,607,421 (5.12%)
  - `3`: 3,999,909 (2.69%)
  - `4`: 2,834,044 (1.91%)

---
### received_uom
- **Type**: `STRING`
- **Description**: The unit of measure (UOM) for the received quantity, indicating how the received quantity is measured.
- **Distinct Values**: 838
- **Nulls**: 94323223 (63.48%)
- **Top Values**:
  - `NULL`: 94,323,223 (63.48%)
  - `EA`: 20,267,866 (13.64%)
  - `EACH`: 13,964,972 (9.40%)
  - `CA`: 4,847,321 (3.26%)
  - `CS`: 3,950,488 (2.66%)

---
### received_unit_cost
- **Type**: `FLOAT`
- **Description**: The cost per unit of the received item or service, represented as a floating-point number.
- **Distinct Values**: 225439
- **Nulls**: 94285800 (63.45%)
- **Top Values**:
  - `NULL`: 94,285,800 (63.45%)
  - `0`: 7,894,372 (5.31%)
  - `0.01`: 103,606 (0.07%)
  - `18`: 79,626 (0.05%)
  - `15`: 78,000 (0.05%)

---
### received_line_amount
- **Type**: `FLOAT`
- **Description**: The total monetary amount for the received line, calculated by multiplying the received quantity by the received unit cost.
- **Distinct Values**: 233983
- **Nulls**: 94379435 (63.52%)
- **Top Values**:
  - `NULL`: 94,379,435 (63.52%)
  - `0`: 4,045,811 (2.72%)
  - `15`: 99,975 (0.07%)
  - `30`: 82,766 (0.06%)
  - `20`: 76,077 (0.05%)

---
### quantity_variance
- **Type**: `FLOAT`
- **Description**: The numerical difference between the invoiced quantity and the received quantity, indicating any variance or discrepancy.
- **Distinct Values**: 29019
- **Nulls**: 68925587 (46.39%)
- **Top Values**:
  - `0`: 75,531,478 (50.83%)
  - `NULL`: 68,925,587 (46.39%)
  - `1`: 17,290 (0.01%)
  - `-1`: 11,624 (<0.01%)
  - `11`: 10,543 (<0.01%)

---
### price_variance
- **Type**: `FLOAT`
- **Description**: The numerical difference between the invoiced unit cost and the received unit cost, indicating any variance or discrepancy in price.
- **Distinct Values**: 79477
- **Nulls**: 68925587 (46.39%)
- **Top Values**:
  - `0`: 64,292,193 (43.27%)
  - `NULL`: 68,925,587 (46.39%)
  - `0.01`: 17,808 (0.01%)
  - `-0.01`: 17,621 (0.01%)
  - `0.02`: 10,657 (<0.01%)

---
### erp_item_number
- **Type**: `STRING`
- **Description**: The item number or code used in the ERP system to identify the product or service being invoiced.
- **Distinct Values**: 1084285
- **Nulls**: 66649727 (44.85%)
- **Top Values**:
  - `NULL`: 66,649,727 (44.85%)
  - `FREIGHT`: 269,550 (0.18%)
  - `16537`: 262,276 (0.18%)
  - `DEFAULT`: 107,736 (0.07%)
  - `SHIPPING`: 92,317 (0.06%)

---
### purchase_order_uom
- **Type**: `STRING`
- **Description**: The unit of measure (UOM) specified in the purchase order, indicating how the ordered quantity is measured.
- **Distinct Values**: 1216
- **Nulls**: 61271617 (41.23%)
- **Top Values**:
  - `NULL`: 61,271,617 (41.23%)
  - `EA`: 33,123,847 (22.29%)
  - `EACH`: 19,623,696 (13.21%)
  - `CA`: 8,677,490 (5.84%)
  - `CS`: 7,664,654 (5.16%)

---
### purchase_uom_conversion_factor
- **Type**: `FLOAT`
- **Description**: A numerical factor used to convert between the purchase order UOM and the invoiced/received UOM.
- **Distinct Values**: 370
- **Nulls**: 60920409 (41.00%)
- **Top Values**:
  - `1`: 76,063,519 (51.19%)
  - `NULL`: 60,920,409 (41.00%)
  - `0`: 1,160,358 (0.78%)
  - `10`: 1,067,272 (0.72%)
  - `12`: 970,668 (0.65%)

---
### purchase_order_unit_cost
- **Type**: `FLOAT`
- **Description**: The unit cost specified in the purchase order, representing the cost per unit agreed upon with the vendor.
- **Distinct Values**: 226685
- **Nulls**: 60721759 (40.86%)
- **Top Values**:
  - `NULL`: 60,721,759 (40.86%)
  - `0`: 8,539,266 (5.75%)
  - `0.01`: 134,149 (0.09%)
  - `15`: 128,148 (0.09%)
  - `18`: 118,683 (0.08%)

---
### assigned_buyer
- **Type**: `STRING`
- **Description**: The name or identifier of the individual responsible for handling the procurement and purchase order processes for the items or services mentioned in the invoice.
- **Distinct Values**: 932
- **Nulls**: 23946006 (16.12%)
- **Top Values**:
  - `PHS`: 69,542,566 (46.80%)
  - `NULL`: 23,946,006 (16.12%)
  - `INTERFAC`: 16,603,598 (11.17%)
  - `GHX`: 10,080,345 (6.78%)
  - `LAWSON`: 922,444 (0.62%)

---
### vendor_number
- **Type**: `STRING`
- **Description**: A unique identifier for the vendor or supplier providing the invoiced items or services.
- **Distinct Values**: 49280
- **Nulls**: 23992055 (16.15%)
- **Top Values**:
  - `NULL`: 23,992,055 (16.15%)
  - `101016`: 2,642,197 (1.78%)
  - `280140`: 1,824,707 (1.23%)
  - `100155`: 1,780,302 (1.20%)
  - `1004`: 1,660,993 (1.12%)

---
### vendor_invoice_date
- **Type**: `DATE`
- **Description**: -
- **Distinct Values**: 7029
- **Nulls**: 23946006 (16.12%)
- **Top Values**:
  - `NULL`: 23,946,006 (16.12%)
  - `2023-01-31`: 97,063 (0.07%)
  - `2023-04-30`: 96,150 (0.06%)
  - `2023-03-31`: 95,066 (0.06%)
  - `2023-08-31`: 93,992 (0.06%)

---
### vendor_name
- **Type**: `STRING`
- **Description**: The name of the vendor or supplier providing the invoiced items or services.
- **Distinct Values**: 122421
- **Nulls**: 24151322 (16.25%)
- **Top Values**:
  - `NULL`: 24,151,322 (16.25%)
  - `MEDLINE INDUSTRIES INC`: 7,659,477 (5.15%)
  - `OWENS & MINOR`: 7,514,101 (5.06%)
  - `CARDINAL HEALTH`: 4,160,408 (2.80%)
  - `MCKESSON GENERAL MEDICAL`: 3,169,733 (2.13%)

---
### vendor_entity_code
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 1276
- **Nulls**: 24018305 (16.16%)
- **Top Values**:
  - `NULL`: 24,018,305 (16.16%)
  - `UCSD`: 9,662,136 (6.50%)
  - `3791`: 3,393,343 (2.28%)
  - `51001`: 3,056,070 (2.06%)
  - `050`: 2,891,969 (1.95%)

---
### vendor_top_parent_name
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 1191
- **Nulls**: N/A
- **Top Values**:
  - `NULL`: 24,018,305 (16.16%)
  - `Providence St. Joseph Health`: 23,419,827 (15.76%)
  - `CommonSpirit Health`: 12,523,809 (8.43%)
  - `Baptist Health (Jacksonville, FL)`: 7,729,577 (5.20%)
  - `Banner Health`: 6,990,494 (4.70%)

---
### vendor_top_parent_entity_code
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 1207
- **Nulls**: 24018305 (16.16%)
- **Top Values**:
  - `NULL`: 24,018,305 (16.16%)
  - `1653`: 23,554,446 (15.85%)
  - `2844`: 12,658,428 (8.52%)
  - `261755`: 7,729,577 (5.20%)
  - `261695`: 6,990,494 (4.70%)

---
### facility_entity_name
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 935
- **Nulls**: 24021278 (16.17%)
- **Top Values**:
  - `NULL`: 24,021,278 (16.17%)
  - `UC San Diego Health System`: 9,662,136 (6.50%)
  - `UC Irvine Health Medical Center`: 3,393,343 (2.28%)
  - `OSF Healthcare System`: 3,056,070 (2.06%)
  - `Adventist Health`: 2,891,969 (1.95%)

---
### facility_entity_code
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 1289
- **Nulls**: 24021278 (16.17%)
- **Top Values**:
  - `NULL`: 24,021,278 (16.17%)
  - `UCSD`: 9,662,136 (6.50%)
  - `3791`: 3,393,343 (2.28%)
  - `51001`: 3,056,070 (2.06%)
  - `050`: 2,891,969 (1.95%)

---
### manufacturer_item_number
- **Type**: `STRING`
- **Description**: The unique identifier or code used by the item's manufacturer to identify the product being invoiced.
- **Distinct Values**: 2705844
- **Nulls**: 4444976 (2.99%)
- **Top Values**:
  - `NULL`: 4,444,976 (2.99%)
  - `FREIGHT`: 237,497 (0.16%)
  - `SHIPPING`: 75,024 (0.05%)
  - `TAX`: 54,530 (0.04%)
  - `1052`: 40,582 (0.03%)

---
### manufacturer_id
- **Type**: `STRING`
- **Description**: A unique identifier for the manufacturer of the invoiced item or product.
- **Distinct Values**: 3844
- **Nulls**: 24222079 (16.30%)
- **Top Values**:
  - `NULL`: 24,222,079 (16.30%)
  - `12668`: 3,288,869 (2.21%)
  - `55350`: 2,379,555 (1.60%)
  - `16075`: 2,352,136 (1.58%)
  - `19069`: 2,178,224 (1.47%)

---
### manufacturer_name
- **Type**: `STRING`
- **Description**: The name of the manufacturer of the invoiced item or product.
- **Distinct Values**: 7367
- **Nulls**: 23725596 (15.97%)
- **Top Values**:
  - `NULL`: 23,725,596 (15.97%)
  - `Medline`: 4,049,216 (2.73%)
  - `Stryker`: 2,026,880 (1.36%)
  - `Johnson & Johnson`: 1,966,579 (1.32%)
  - `Cardinal`: 1,534,005 (1.03%)

---
### expense_code
- **Type**: `STRING`
- **Description**: A code representing the expense category or type to which the invoice line is allocated in the hospital's financial records.
- **Distinct Values**: 32997
- **Nulls**: 23916962 (16.10%)
- **Top Values**:
  - `NULL`: 23,916,962 (16.10%)
  - `6315`: 1,090,623 (0.73%)
  - `6460`: 1,038,596 (0.70%)
  - `500000`: 1,018,698 (0.69%)
  - `68000`: 867,622 (0.58%)

---
### expense_code_description
- **Type**: `STRING`
- **Description**: A description explaining the nature or purpose of the expense category mentioned in expense_code.
- **Distinct Values**: 37659
- **Nulls**: 30954316 (20.83%)
- **Top Values**:
  - `NULL`: 30,954,316 (20.83%)
  - `Medical Supplies`: 26,738,947 (17.99%)
  - `Implants`: 6,724,623 (4.53%)
  - `Operating Room Supplies`: 6,281,358 (4.23%)
  - `Pharmaceuticals`: 3,165,243 (2.13%)

---
### invoice_create_date
- **Type**: `DATE`
- **Description**: The date on which the invoice was created or generated in the ERP system, represented in DATE format.
- **Distinct Values**: 420601
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `2023-01-30`: 177,309 (0.12%)
  - `2023-08-01`: 174,573 (0.12%)
  - `2023-09-08`: 173,516 (0.12%)
  - `2023-08-16`: 170,725 (0.11%)

---
### last_modified_date
- **Type**: `DATE`
- **Description**: The date and time when the invoice line was last modified or updated in the database, represented in DATE format.
- **Distinct Values**: 430
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `2023-08-14`: 661,386 (0.45%)
  - `2023-06-22`: 660,946 (0.44%)
  - `2023-08-01`: 658,249 (0.44%)
  - `2023-08-16`: 655,355 (0.44%)

---
### invoice_due_date
- **Type**: `DATETIME`
- **Description**: The date and time by which the payment for the invoice is due, represented in DATETIME format, which includes both date and time information.
- **Distinct Values**: 11394
- **Nulls**: 23725596 (15.97%)
- **Top Values**:
  - `NULL`: 23,725,596 (15.97%)
  - `2023-04-29T00:00:00`: 62,719 (0.04%)
  - `2023-07-29T00:00:00`: 62,334 (0.04%)
  - `2023-03-30T00:00:00`: 62,024 (0.04%)
  - `2023-06-29T00:00:00`: 61,763 (0.04%)

---
### invoice_date
- **Type**: `DATETIME`
- **Description**: The date and time when the invoice was issued or created, represented in DATETIME format.
- **Distinct Values**: 6986
- **Nulls**: 0 (0%)
- **Top Values**:
  - `2023-01-31T00:00:00`: 86,835 (0.06%)
  - `2023-04-30T00:00:00`: 86,071 (0.06%)
  - `2023-03-31T00:00:00`: 84,915 (0.06%)
  - `2023-08-31T00:00:00`: 84,379 (0.06%)
  - `2023-05-31T00:00:00`: 80,970 (0.05%)

---
### invoice_received_date
- **Type**: `DATETIME`
- **Description**: The date and time when the invoice was received by the hospital, represented in DATETIME format.
- **Distinct Values**: 10850024
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `2023-09-14T08:37:24`: 35,898 (0.02%)
  - `2023-10-11T11:15:52`: 30,113 (0.02%)
  - `2023-11-14T16:10:31`: 27,039 (0.02%)
  - `2023-08-10T09:42:08`: 25,021 (0.02%)

---
### approved_date
- **Type**: `DATETIME`
- **Description**: The date and time when the invoice or invoice line was approved for payment or processing, represented in DATETIME format.
- **Distinct Values**: 6281734
- **Nulls**: 94002621 (63.26%)
- **Top Values**:
  - `NULL`: 94,002,621 (63.26%)
  - `2023-08-31T00:00:00`: 12,015 (<0.01%)
  - `2023-11-30T00:00:00`: 11,590 (<0.01%)
  - `2024-03-31T00:00:00`: 11,204 (<0.01%)
  - `2024-04-30T00:00:00`: 10,950 (<0.01%)

---
### transaction_date
- **Type**: `DATETIME`
- **Description**: The date and time of the underlying transaction or event related to the invoice line, represented in DATETIME format.
- **Distinct Values**: 6475
- **Nulls**: 23416431 (15.76%)
- **Top Values**:
  - `NULL`: 23,416,431 (15.76%)
  - `2023-01-31T00:00:00`: 85,724 (0.06%)
  - `2023-03-31T00:00:00`: 84,915 (0.06%)
  - `2023-05-31T00:00:00`: 84,687 (0.06%)
  - `2023-08-31T00:00:00`: 84,412 (0.06%)

---
### posted_date
- **Type**: `DATETIME`
- **Description**: The date and time when the invoice line was posted or recorded in the hospital's financial records, represented in DATETIME format.
- **Distinct Values**: 11333
- **Nulls**: 624003 (0.42%)
- **Top Values**:
  - `NULL`: 624,003 (0.42%)
  - `2023-01-31T00:00:00`: 117,326 (0.08%)
  - `2023-08-31T00:00:00`: 101,831 (0.07%)
  - `2023-06-30T00:00:00`: 100,790 (0.07%)
  - `2023-05-31T00:00:00`: 100,346 (0.07%)

---
### fiscal_period
- **Type**: `FLOAT`
- **Description**: The specific fiscal period to which the invoice line belongs, represented as a floating-point number (e.g., 1 for January, 2 for February, and so on).
- **Distinct Values**: 12
- **Nulls**: 24905202 (16.76%)
- **Top Values**:
  - `NULL`: 24,905,202 (16.76%)
  - `6`: 14,400,261 (9.69%)
  - `3`: 12,895,697 (8.68%)
  - `4`: 11,252,084 (7.57%)
  - `2`: 10,757,276 (7.24%)

---
### fiscal_year
- **Type**: `FLOAT`
- **Description**: The fiscal year to which the invoice line belongs, represented as a floating-point number (e.g., 2023).
- **Distinct Values**: 9
- **Nulls**: 24898624 (16.76%)
- **Top Values**:
  - `2023`: 70,428,587 (47.40%)
  - `2024`: 37,260,580 (25.08%)
  - `NULL`: 24,898,624 (16.76%)
  - `2022`: 15,682,855 (10.55%)
  - `2025`: 326,164 (0.22%)

---
### payment_terms
- **Type**: `STRING`
- **Description**: The terms and conditions specifying the period within which the payment for the invoice is due, provided by the vendor.
- **Distinct Values**: 458
- **Nulls**: 25287514 (17.02%)
- **Top Values**:
  - `NET 30`: 35,227,763 (23.71%)
  - `NULL`: 25,287,514 (17.02%)
  - `0005`: 8,677,093 (5.84%)
  - `30`: 5,891,784 (3.97%)
  - `N30`: 5,873,752 (3.95%)

---
### po_number
- **Type**: `STRING`
- **Description**: The purchase order number associated with the invoice, allowing for tracking and linking the invoice to the corresponding purchase order.
- **Distinct Values**: 10884242
- **Nulls**: 60195741 (40.51%)
- **Top Values**:
  - `NULL`: 60,195,741 (40.51%)
  - `1001-20`: 19,503 (0.01%)
  - `1001-10`: 17,855 (0.01%)
  - `1006-20`: 16,757 (0.01%)
  - `1006-10`: 16,259 (0.01%)

---
### po_header_id
- **Type**: `INTEGER`
- **Description**: A unique identifier representing the header or main information of the purchase order related to the invoice.
- **Distinct Values**: 10363242
- **Nulls**: 61678144 (41.51%)
- **Top Values**:
  - `NULL`: 61,678,144 (41.51%)
  - `15456382`: 1,326 (<0.01%)
  - `16346261`: 655 (<0.01%)
  - `17904071`: 601 (<0.01%)
  - `15424855`: 600 (<0.01%)

---
### po_line_id
- **Type**: `INTEGER`
- **Description**: A unique identifier representing the specific line item within the purchase order related to the invoice.
- **Distinct Values**: 37827598
- **Nulls**: 61765103 (41.57%)
- **Top Values**:
  - `NULL`: 61,765,103 (41.57%)
  - `193690460`: 1,326 (<0.01%)
  - `224632598`: 601 (<0.01%)
  - `192823611`: 600 (<0.01%)
  - `208752044`: 599 (<0.01%)

---
### po_line_number
- **Type**: `FLOAT`
- **Description**: -
- **Distinct Values**: 2243
- **Nulls**: 60904128 (40.99%)
- **Top Values**:
  - `NULL`: 60,904,128 (40.99%)
  - `1`: 26,017,042 (17.51%)
  - `2`: 16,694,371 (11.23%)
  - `3`: 10,505,166 (7.07%)
  - `4`: 7,046,830 (4.74%)

---
### contract_number
- **Type**: `STRING`
- **Description**: The unique identifier or code associated with a contract, if applicable. Contracts specify agreed-upon terms and conditions for procurement.
- **Distinct Values**: 22097
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `MS31000`: 1,061,971 (0.71%)
  - `PP-OR-1793`: 644,783 (0.43%)
  - `PP-OR-2158`: 599,661 (0.40%)
  - `PP-OR-2544`: 568,600 (0.38%)

---
### contract_name
- **Type**: `STRING`
- **Description**: The name or description of the contract specifying the terms and conditions for procurement, if applicable.
- **Distinct Values**: 14389
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `Medical Surgical Distribution`: 4,561,008 (3.07%)
  - `Medical Surgical Distribution Services`: 2,897,669 (1.95%)
  - `Med-Surg Distribution`: 2,255,734 (1.52%)
  - `Custom Procedural Trays`: 1,837,968 (1.24%)

---
### contract_type
- **Type**: `FLOAT`
- **Description**: A numerical code representing the type or category of the contract, such as a service contract or a product supply contract.
- **Distinct Values**: 3
- **Nulls**: 148566440 (99.98%)
- **Top Values**:
  - `NULL`: 148,566,440 (99.98%)
  - `1`: 66,042 (0.04%)
  - `3`: 875 (<0.01%)
  - `2`: 105 (<0.01%)

---
### contract_type_description
- **Type**: `STRING`
- **Description**: A description explaining the nature or purpose of the contract type mentioned in contract_type.
- **Distinct Values**: 3
- **Nulls**: 148566440 (99.98%)
- **Top Values**:
  - `NULL`: 148,566,440 (99.98%)
  - `GPO`: 66,042 (0.04%)
  - `LOC`: 875 (<0.01%)
  - `REG`: 105 (<0.01%)

---
### lowest_uom_contract_price
- **Type**: `FLOAT`
- **Description**: The contracted price per unit for the item or service, represented as a floating-point number, based on the lowest unit of measure (UOM) specified in the contract.
- **Distinct Values**: 45187
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `0`: 55,850,989 (37.59%)
  - `NULL`: 51,579,752 (34.71%)
  - `0.01`: 283,838 (0.19%)
  - `15`: 76,662 (0.05%)
  - `10`: 52,787 (0.04%)

---
### purchase_uom_contract_price
- **Type**: `FLOAT`
- **Description**: The contracted price per unit for the item or service, represented as a floating-point number, based on the purchase unit of measure (UOM) specified in the contract.
- **Distinct Values**: 45187
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `0`: 55,850,989 (37.59%)
  - `NULL`: 51,579,752 (34.71%)
  - `0.01`: 283,838 (0.19%)
  - `15`: 76,662 (0.05%)
  - `10`: 52,787 (0.04%)

---
### premier_reference_number
- **Type**: `STRING`
- **Description**: A unique reference number provided by Premier to identify the invoiced item.
- **Distinct Values**: 597651
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `0`: 150,604 (0.10%)
  - `11571597`: 21,182 (0.01%)
  - `11559814`: 21,182 (0.01%)
  - `11571587`: 15,810 (0.01%)

---
### premier_product_category
- **Type**: `STRING`
- **Description**: The category or type of product to which the invoiced item belongs, as classified by Premier.
- **Distinct Values**: 9363
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `General Medical Products`: 2,522,513 (1.70%)
  - `Suture Endomechanical`: 2,449,767 (1.65%)
  - `Orthopedic`: 2,178,652 (1.47%)
  - `Interventional Cardiology`: 2,147,171 (1.45%)

---
### premier_item_description
- **Type**: `STRING`
- **Description**: A description explaining the item or product as classified by Premier.
- **Distinct Values**: 610264
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `Solution Saline 0.9% 10Ml Syringe`: 240,212 (0.16%)
  - `Unidentified Item`: 150,604 (0.10%)
  - `Solution Saline Ns 100Ml Bag`: 96,850 (0.07%)
  - `Administration Set Pri Iv 15Dpm 112In`: 84,900 (0.06%)

---
### premier_manufacturer_name
- **Type**: `STRING`
- **Description**: The name of the manufacturer of the item or product as classified by Premier.
- **Distinct Values**: 2754
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `MEDLINE INDUSTRIES INC.`: 12,903,120 (8.68%)
  - `BAXTER HEALTHCARE`: 4,137,025 (2.78%)
  - `STRYKER CORP.`: 3,936,611 (2.65%)
  - `CARDINAL HEALTH`: 3,729,986 (2.51%)

---
### premier_manufacturer_entity_code
- **Type**: `STRING`
- **Description**: A code or identifier representing the entity or manufacturer within the classification system used by Premier.
- **Distinct Values**: 3139
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `12668`: 12,665,679 (8.52%)
  - `9749`: 4,130,089 (2.78%)
  - `55350`: 3,999,127 (2.69%)
  - `16075`: 3,791,011 (2.55%)

---
### premier_manufacturer_top_parent_entity_code
- **Type**: `STRING`
- **Description**: A code or identifier representing the top-level parent entity or manufacturer within the classification system used by Premier.
- **Distinct Values**: 1845
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `12668`: 20,144,983 (13.56%)
  - `16075`: 7,729,235 (5.20%)
  - `9749`: 4,914,986 (3.31%)
  - `55350`: 4,677,931 (3.15%)

---
### premier_manufacturer_item_number
- **Type**: `STRING`
- **Description**: The unique identifier or code used by the manufacturer to identify the item or product as classified by Premier.
- **Distinct Values**: 580041
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `306546`: 239,999 (0.16%)
  - `UNKNOWN`: 149,174 (0.10%)
  - `L8002`: 100,858 (0.07%)
  - `C2C6500`: 85,089 (0.06%)

---
### premier_vendor_name
- **Type**: `STRING`
- **Description**: The name of the vendor or supplier as classified by Premier.
- **Distinct Values**: 1833
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `MEDLINE INDUSTRIES INC.`: 25,492,160 (17.16%)
  - `OWENS & MINOR`: 7,447,432 (5.01%)
  - `BAXTER HEALTHCARE`: 5,857,201 (3.94%)
  - `STRYKER CORP.`: 4,679,237 (3.15%)

---
### premier_vendor_entity_code
- **Type**: `STRING`
- **Description**: A code or identifier representing the vendor or supplier within the classification system used by Premier.
- **Distinct Values**: 1710
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `12668`: 25,492,160 (17.16%)
  - `13164`: 7,447,432 (5.01%)
  - `9749`: 5,857,201 (3.94%)
  - `55350`: 4,679,237 (3.15%)

---
### premier_top_parent_entity_code
- **Type**: `STRING`
- **Description**: A code or identifier representing the top-level parent entity within the classification system used by Premier.
- **Distinct Values**: 1738
- **Nulls**: 51579752 (34.71%)
- **Top Values**:
  - `NULL`: 51,579,752 (34.71%)
  - `12668`: 20,387,556 (13.72%)
  - `9749`: 5,857,211 (3.94%)
  - `55350`: 4,718,449 (3.18%)
  - `13164`: 3,888,365 (2.62%)

---
### packaging_string
- **Type**: `STRING`
- **Description**: Textual information describing the packaging or container of the invoiced item, providing details about how the item is packaged.
- **Distinct Values**: 19137
- **Nulls**: 50380844 (33.91%)
- **Top Values**:
  - `NULL`: 50,380,844 (33.91%)
  - `EACH`: 33,121,544 (22.29%)
  - `CASE`: 12,560,875 (8.45%)
  - `BOX`: 7,734,407 (5.21%)
  - `PACK`: 717,658 (0.48%)

---
### user_id
- **Type**: `STRING`
- **Description**: The unique identifier or name of the user who created or last modified the invoice line in the database.
- **Distinct Values**: 4381
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `SYSTEM`: 11,867,160 (7.99%)
  - `MIGRATE`: 5,231,795 (3.52%)
  - `12613`: 2,088,891 (1.41%)
  - `11843`: 1,535,780 (1.03%)

---
### invoice_match_status
- **Type**: `FLOAT`
- **Description**: A numerical code representing the status of the invoice match process, indicating whether the invoice line has been successfully matched or if there are discrepancies or issues in the matching process.
- **Distinct Values**: 6
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `3`: 87,483,665 (58.87%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 51,906 (0.03%)
  - `4`: 40,454 (0.03%)
  - `0`: 29,007 (0.02%)

---
### invoice_match_status_description
- **Type**: `STRING`
- **Description**: A description explaining the meaning of the invoice match status code, providing additional details or context regarding the status of the invoice line matching process.
- **Distinct Values**: 6
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `Matched`: 87,483,665 (58.87%)
  - `NULL`: 61,016,663 (41.06%)
  - `No Match`: 51,906 (0.03%)
  - `Matched w/ Exception`: 40,454 (0.03%)
  - `Void`: 29,007 (0.02%)

---
### invoice_workflow_status
- **Type**: `FLOAT`
- **Description**: A numerical code representing the workflow status of the invoice line, indicating its position or progress within the approval or processing workflow.
- **Distinct Values**: 10
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `90`: 65,285,330 (43.94%)
  - `NULL`: 61,016,663 (41.06%)
  - `85`: 21,647,416 (14.57%)
  - `20`: 492,551 (0.33%)
  - `5`: 88,420 (0.06%)

---
### invoice_workflow_status_description
- **Type**: `STRING`
- **Description**: A description explaining the meaning of the invoice workflow status code, providing additional details or context regarding the position of the invoice line within the approval or processing workflow.
- **Distinct Values**: 10
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `Paid-in-Full`: 65,285,330 (43.94%)
  - `NULL`: 61,016,663 (41.06%)
  - `Completed`: 21,647,416 (14.57%)
  - `Approved`: 492,551 (0.33%)
  - `Exception`: 88,420 (0.06%)

---
### invoice_create_type
- **Type**: `FLOAT`
- **Description**: A numerical code representing the type or method of invoice creation, indicating how the invoice line was generated or entered into the system.
- **Distinct Values**: 3
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `1`: 87,576,139 (58.94%)
  - `NULL`: 61,016,663 (41.06%)
  - `3`: 12 (<0.01%)
  - `2`: 12 (<0.01%)

---
### invoice_create_type_description
- **Type**: `STRING`
- **Description**: A description explaining the meaning of the invoice create type code, providing additional details or context regarding how the invoice line was generated or entered into the system.
- **Distinct Values**: 5
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `EDI 810`: 48,694,747 (32.77%)
  - `From PO`: 19,925,497 (13.41%)
  - `IDS PO`: 18,955,895 (12.76%)
  - `Manually`: 12 (<0.01%)

---
### payment_method
- **Type**: `FLOAT`
- **Description**: A numerical code representing the payment method specified for the invoice, indicating how the payment for the invoice will be made (e.g., credit card, wire transfer, check).
- **Distinct Values**: 8
- **Nulls**: 82527488 (55.54%)
- **Top Values**:
  - `NULL`: 82,527,488 (55.54%)
  - `0`: 30,679,027 (20.65%)
  - `1`: 22,955,705 (15.45%)
  - `2`: 4,701,665 (3.16%)
  - `5`: 4,470,995 (3.01%)

---
### payment_method_description
- **Type**: `STRING`
- **Description**: A description explaining the meaning of the payment method code, providing additional details or context regarding the method specified for the invoice payment.
- **Distinct Values**: 5
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `NULL`: 61,016,663 (41.06%)
  - `Local Print`: 32,787,955 (22.07%)
  - `ACH`: 24,638,163 (16.58%)
  - `Not Paid`: 22,373,904 (15.06%)
  - `Check`: 4,636,546 (3.12%)

---
### invoice_810_yn
- **Type**: `FLOAT`
- **Description**: A flag indicating whether the invoice corresponds to an EDI (Electronic Data Interchange) transaction of type 810. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `1`: 67,644,596 (45.52%)
  - `NULL`: 61,016,663 (41.06%)
  - `0`: 19,931,567 (13.41%)

---
### ocr_invoice_yn
- **Type**: `FLOAT`
- **Description**: A flag indicating whether the invoice was processed using OCR (Optical Character Recognition) technology. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `0`: 68,620,256 (46.18%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 18,955,907 (12.76%)

---
### invoice_line_exception_status
- **Type**: `STRING`
- **Description**: A field indicating the exception status of the invoice line. It may include information about discrepancies, errors, or issues related to the specific line item.
- **Distinct Values**: 7
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `N`: 80,628,437 (54.26%)
  - `NULL`: 61,016,663 (41.06%)
  - `IT`: 6,838,471 (4.60%)
  - `X`: 54,578 (0.04%)
  - `R`: 30,734 (0.02%)

---
### invoice_current_exception_status_description
- **Type**: `STRING`
- **Description**: A description explaining the current exception status of the invoice line, providing additional details or context regarding any discrepancies, errors, or issues.
- **Distinct Values**: 7
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `No Exception`: 80,628,437 (54.26%)
  - `NULL`: 61,016,663 (41.06%)
  - `In Tolerance Price Exception`: 6,838,471 (4.60%)
  - `Missing Line Exception`: 54,578 (0.04%)
  - `Receiving Exception`: 30,734 (0.02%)

---
### invoice_header_exception_status
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 4
- **Nulls**: 148581084 (99.99%)
- **Top Values**:
  - `NULL`: 148,581,084 (99.99%)
  - `Dollar Limit`: 7,423 (<0.01%)
  - `Total Invoice`: 4,014 (<0.01%)
  - `Tax EDI`: 161 (<0.01%)
  - `Expired`: 144 (<0.01%)

---
### price_exception_yn
- **Type**: `INTEGER`
- **Description**: A flag indicating whether a price exception exists for the invoice line. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `0`: 87,240,533 (58.71%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 335,630 (0.23%)

---
### quantity_exception_yn
- **Type**: `INTEGER`
- **Description**: A flag indicating whether a quantity exception exists for the invoice line. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `0`: 87,324,224 (58.77%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 251,939 (0.17%)

---
### receipt_exception_yn
- **Type**: `INTEGER`
- **Description**: A flag indicating whether a receipt exception exists for the invoice line. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `0`: 86,467,054 (58.19%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 1,109,109 (0.75%)

---
### missing_line_exception_yn
- **Type**: `INTEGER`
- **Description**: A flag indicating whether a missing line exception exists for the invoice line. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `0`: 87,502,608 (58.89%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 73,555 (0.05%)

---
### other_exception_type_yn
- **Type**: `INTEGER`
- **Description**: A flag indicating whether other types of exceptions exist for the invoice line, apart from price, quantity, receipt, or missing line exceptions. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `0`: 87,063,593 (58.59%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 512,570 (0.34%)

---
### uom_variance_yn
- **Type**: `INTEGER`
- **Description**: A flag indicating whether a unit of measure (UOM) variance exists for the invoice line. A value of 1 may indicate 'yes,' while 0 may indicate 'no.'
- **Distinct Values**: 2
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `0`: 87,560,874 (58.93%)
  - `NULL`: 61,016,663 (41.06%)
  - `1`: 15,289 (0.01%)

---
### snapshot_date
- **Type**: `DATE`
- **Description**: The date on which the data was captured from the ERP system.
- **Distinct Values**: 1
- **Nulls**: 61016663 (41.06%)
- **Top Values**:
  - `2026-02-10`: 87,576,163 (58.94%)
  - `NULL`: 61,016,663 (41.06%)

---
### invoice_type
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 57
- **Nulls**: 109219717 (73.50%)
- **Top Values**:
  - `NULL`: 109,219,717 (73.50%)
  - `INVOICE`: 33,928,101 (22.83%)
  - `INVOICE - GHX`: 3,966,757 (2.67%)
  - `INVOICE - MISSING SHIP TO DETAILS`: 512,823 (0.35%)
  - `CREDIT`: 433,251 (0.29%)

---
### client_name
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 261964
- **Nulls**: 78686998 (52.95%)
- **Top Values**:
  - `NULL`: 78,686,998 (52.95%)
  - `ADVENTIST HEALTH SYSTEM`: 3,589,959 (2.42%)
  - `BAPTIST HEALTH SYSTEMS`: 1,725,286 (1.16%)
  - `UNIVERSITY OF MARYLAND A/P DEPT`: 1,589,727 (1.07%)
  - `BANNER HEALTH`: 1,441,099 (0.97%)

---
### ap_location
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 12890
- **Nulls**: 120307498 (80.96%)
- **Top Values**:
  - `NULL`: 120,307,498 (80.96%)
  - `MAIN`: 7,691,794 (5.18%)
  - ``: 6,990,494 (4.70%)
  - `1`: 1,023,681 (0.69%)
  - `CHICAGO`: 638,090 (0.43%)

---
### billto
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 144118
- **Nulls**: 48440524 (32.60%)
- **Top Values**:
  - `NULL`: 48,440,524 (32.60%)
  - `UC San Diego Health System`: 9,747,097 (6.56%)
  - `Adventist Health Accounts Payable`: 9,115,634 (6.13%)
  - `BAPTIST MEDICAL CENTER`: 5,107,690 (3.44%)
  - `UC Irvine Health Medical Center`: 4,943,985 (3.33%)

---
### bill_to_address_line_1
- **Type**: `STRING`
- **Description**: 
- **Distinct Values**: 318
- **Nulls**: 62283831 (41.92%)
- **Top Values**:
  - `NULL`: 62,283,831 (41.92%)
  - `PO BOX 619085`: 8,778,911 (5.91%)
  - `Attention: Accounts Payable Department`: 7,437,028 (5.00%)
  - `PO BOX 45128`: 5,128,420 (3.45%)
  - `Attention:  Accounts Payable`: 5,035,488 (3.39%)

---
### bill_to_address_line_2
- **Type**: `STRING`
- **Description**: 
- **Distinct Values**: 137
- **Nulls**: 99233367 (66.78%)
- **Top Values**:
  - `NULL`: 99,233,367 (66.78%)
  - `PO Box 33268`: 9,763,170 (6.57%)
  - `PO Box C-11917`: 4,943,985 (3.33%)
  - `1155 Mill Street`: 3,964,872 (2.67%)
  - `THE NEBRASKA MEDICAL CENTER`: 3,931,122 (2.65%)

---
### bill_to_address_line_3
- **Type**: `STRING`
- **Description**: 
- **Distinct Values**: 20
- **Nulls**: 132101854 (88.90%)
- **Top Values**:
  - `NULL`: 132,101,854 (88.90%)
  - `987512 NEBRASKA MEDICAL CENTER`: 4,397,057 (2.96%)
  - `hcpayable@health.ucsd.edu`: 2,977,021 (2.00%)
  - `PO BOX 14890`: 2,494,352 (1.68%)
  - `OSFHealthcare.AP@OSFHealthcare.org`: 1,872,194 (1.26%)

---
### bill_to_city
- **Type**: `STRING`
- **Description**: 
- **Distinct Values**: 177
- **Nulls**: 62283831 (41.92%)
- **Top Values**:
  - `NULL`: 62,283,831 (41.92%)
  - `San Diego`: 9,763,170 (6.57%)
  - `Roseville`: 9,113,117 (6.13%)
  - `JACKSONVILLE`: 8,312,651 (5.59%)
  - `Santa Ana`: 4,943,985 (3.33%)

---
### bill_to_state
- **Type**: `STRING`
- **Description**: 
- **Distinct Values**: 40
- **Nulls**: 62283831 (41.92%)
- **Top Values**:
  - `NULL`: 62,283,831 (41.92%)
  - `CA`: 27,724,730 (18.66%)
  - `FL`: 9,691,557 (6.52%)
  - `TX`: 5,161,224 (3.47%)
  - `NV`: 4,712,945 (3.17%)

---
### bill_to_country
- **Type**: `STRING`
- **Description**: 
- **Distinct Values**: 2
- **Nulls**: 62283831 (41.92%)
- **Top Values**:
  - `USA`: 86,163,015 (57.99%)
  - `NULL`: 62,283,831 (41.92%)
  - `US`: 145,980 (0.10%)

---
### bill_to_zipcode
- **Type**: `STRING`
- **Description**: 
- **Distinct Values**: 225
- **Nulls**: 62283831 (41.92%)
- **Top Values**:
  - `NULL`: 62,283,831 (41.92%)
  - `92163-3268`: 9,763,170 (6.57%)
  - `32232-5128`: 9,156,021 (6.16%)
  - `95661-9085`: 9,066,008 (6.10%)
  - `92711`: 4,943,985 (3.33%)

---
### shipto_name
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 493539
- **Nulls**: 1267310 (0.85%)
- **Top Values**:
  - `UCSD MEDICAL CENTER`: 6,337,864 (4.27%)
  - `THE NEBRASKA MEDICAL CENTER`: 3,452,339 (2.32%)
  - `UCSD Medical Center`: 2,233,486 (1.50%)
  - ``: 1,383,045 (0.93%)
  - `NULL`: 1,267,310 (0.85%)

---
### shipto_address
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 551864
- **Nulls**: 1267200 (0.85%)
- **Top Values**:
  - ``: 5,088,882 (3.42%)
  - `800 PRUDENTIAL DRIVE`: 4,917,677 (3.31%)
  - `UC Irvine Health Medical Center`: 3,124,638 (2.10%)
  - `Renown Regional Medical Center`: 2,194,843 (1.48%)
  - `MEDICAL CENTER`: 2,032,920 (1.37%)

---
### shipto_city
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 26604
- **Nulls**: 1575564 (1.06%)
- **Top Values**:
  - `JACKSONVILLE`: 8,726,376 (5.87%)
  - `LA JOLLA`: 4,172,812 (2.81%)
  - `Reno`: 3,938,849 (2.65%)
  - `OMAHA`: 3,793,205 (2.55%)
  - `SAN ANTONIO`: 3,264,742 (2.20%)

---
### shipto_state
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 2411
- **Nulls**: 1575564 (1.06%)
- **Top Values**:
  - `CA`: 36,893,586 (24.83%)
  - `FL`: 17,595,276 (11.84%)
  - `TX`: 9,757,784 (6.57%)
  - `IL`: 7,407,193 (4.98%)
  - `AZ`: 7,353,684 (4.95%)

---
### shipto_postalcode
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 74746
- **Nulls**: 1267201 (0.85%)
- **Top Values**:
  - `92037`: 5,526,138 (3.72%)
  - `32207`: 5,304,381 (3.57%)
  - `68105`: 3,695,640 (2.49%)
  - `92103`: 3,442,893 (2.32%)
  - `89502`: 3,428,719 (2.31%)

---
### routing_category
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 4108
- **Nulls**: 147473945 (99.25%)
- **Top Values**:
  - `NULL`: 147,473,945 (99.25%)
  - `750000`: 62,031 (0.04%)
  - `222222`: 36,418 (0.02%)
  - `834000`: 30,493 (0.02%)
  - `5100100`: 28,648 (0.02%)

---
### hospital_id
- **Type**: `INTEGER`
- **Description**: -
- **Distinct Values**: 220
- **Nulls**: 131271864 (88.34%)
- **Top Values**:
  - `NULL`: 131,271,864 (88.34%)
  - `3791`: 3,393,343 (2.28%)
  - `5078`: 2,343,467 (1.58%)
  - `8920`: 2,297,545 (1.55%)
  - `35197`: 1,380,519 (0.93%)

---
### remitra_created_date
- **Type**: `DATETIME`
- **Description**: -
- **Distinct Values**: 15222781
- **Nulls**: 99328958 (66.85%)
- **Top Values**:
  - `NULL`: 99,328,958 (66.85%)
  - `2024-01-03T07:50:10.691000000`: 9,539 (<0.01%)
  - `2023-10-11T11:24:52.580000000`: 9,505 (<0.01%)
  - `2024-07-02T14:42:03.871000000`: 9,476 (<0.01%)
  - `2023-11-30T08:23:28.280000000`: 9,426 (<0.01%)

---
### remitra_modified_date
- **Type**: `DATETIME`
- **Description**: -
- **Distinct Values**: 9243184
- **Nulls**: 99328958 (66.85%)
- **Top Values**:
  - `NULL`: 99,328,958 (66.85%)
  - `2024-01-03T08:07:13.427000000`: 9,539 (<0.01%)
  - `2023-10-11T11:24:54.485000000`: 9,505 (<0.01%)
  - `2024-07-02T14:42:03.914000000`: 9,472 (<0.01%)
  - `2023-11-30T08:23:29.506000000`: 9,426 (<0.01%)

---
### remitra_received_date
- **Type**: `DATETIME`
- **Description**: -
- **Distinct Values**: 7118016
- **Nulls**: 99407128 (66.90%)
- **Top Values**:
  - `NULL`: 99,407,128 (66.90%)
  - `2023-09-14T08:37:24`: 38,680 (0.03%)
  - `2023-10-11T11:15:52`: 31,218 (0.02%)
  - `2023-11-14T16:10:31`: 28,095 (0.02%)
  - `2023-08-10T09:42:08`: 26,721 (0.02%)

---
### data_source
- **Type**: `STRING`
- **Description**: -
- **Distinct Values**: 3
- **Nulls**: 0 (0%)
- **Top Values**:
  - `ERP`: 78,686,998 (52.95%)
  - `Remitra`: 61,016,663 (41.06%)
  - `ERP/Remitra`: 8,889,165 (5.98%)

---
