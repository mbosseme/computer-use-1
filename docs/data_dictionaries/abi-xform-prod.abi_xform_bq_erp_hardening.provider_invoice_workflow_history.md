# Data Dictionary: provider_invoice_workflow_history
**Table**: `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
**Description**: This view contains a history of all ERP and Remitra invoices with details about exceptions, productivity, and workflow status. This view will be updated daily by 10 AM EST
**Total Records**: 89,066,461

## Columns
### health_system_name
- **Type**: `STRING`
- **Description**: The name of the health system in the source system
- **Distinct Values**: 796
- **Nulls**: 153881
- **Top Values**:
  - `AdventHealth (AHS Florida)`: 11,531,867
  - `EM_OSF`: 4,215,819
  - `EM_UCSD`: 4,176,237
  - `Dignity Health`: 3,715,686
  - `Catholic Health Initiatives`: 3,446,335

---
### health_system_entity_code
- **Type**: `STRING`
- **Description**: The Premier entity code for the health system
- **Distinct Values**: 33
- **Nulls**: 42610197
- **Top Values**:
  - `null`: 43,274,294
  - `NULL`: 42,610,197
  - `CA2043`: 1,620,349
  - `815090`: 359,538
  - `KY0080`: 240,815

---
### direct_parent_name
- **Type**: `STRING`
- **Description**: The Premier parent name for the health system
- **Distinct Values**: 97
- **Nulls**: 42877049
- **Top Values**:
  - `NULL`: 42,877,049
  - `OSF HealthCare`: 4,428,225
  - `University of California San Diego Health System (AKA UC San Diego Health)`: 4,176,262
  - `Adventist Health`: 3,635,136
  - `Coastal Community Health`: 2,953,445

---
### direct_parent_entity_code
- **Type**: `STRING`
- **Description**: The Premier parent entity code for the health system
- **Distinct Values**: 1
- **Nulls**: 0
- **Top Values**:
  - `null`: 89,066,461

---
### org_description
- **Type**: `STRING`
- **Description**: The name for an organization in the health system.
- **Distinct Values**: 1354
- **Nulls**: 624154
- **Top Values**:
  - `AdventHealth (AHS Florida)`: 11,531,867
  - `UCSD MEDICAL CENTER`: 3,723,439
  - `Dignity Health`: 3,715,686
  - `Catholic Health Initiatives`: 3,446,335
  - `Northwell Health`: 3,108,405

---
### org_number
- **Type**: `STRING`
- **Description**: The number assigned to an organization in the health system. This value may be a hospital-sized unit, larger, or smaller, depending on how the medical center is structured.
- **Distinct Values**: 9842
- **Nulls**: 7376880
- **Top Values**:
  - `NULL`: 7,376,880
  - `1`: 5,740,930
  - `001`: 5,271,365
  - `01`: 3,768,313
  - `10`: 3,022,389

---
### facility_entity_name
- **Type**: `STRING`
- **Description**: The Premier name for the facility
- **Distinct Values**: 1
- **Nulls**: 0
- **Top Values**:
  - `null`: 89,066,461

---
### facility_entity_code
- **Type**: `STRING`
- **Description**: The Premier entity code for the facility
- **Distinct Values**: 220
- **Nulls**: 42874448
- **Top Values**:
  - `NULL`: 42,874,448
  - `743158`: 4,176,262
  - `CA2043`: 1,682,414
  - `TX0488`: 1,594,462
  - `FL0091`: 1,377,886

---
### invoice_header_id
- **Type**: `INTEGER`
- **Description**: The internal ID used to identify a unique invoice in an ERP system
- **Distinct Values**: 5676768
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `69788`: 6
  - `42665`: 6
  - `7294`: 6
  - `4425067`: 4

---
### remitra_invoice_header_id
- **Type**: `STRING`
- **Description**: The internal ID used to identify a unique invoice in Remitra
- **Distinct Values**: 55234113
- **Nulls**: 33602034
- **Top Values**:
  - `NULL`: 33,602,034
  - `fff79176-788b-11eb-975f-0a0083640000`: 2
  - `ff5f801c-b066-11f0-bc53-0a0083cb0000`: 2
  - `feb77c4e-e38b-11ef-bc51-0a0083cb0000`: 2
  - `fe96de54-df0e-11ed-afc0-0a0083cb0000`: 2

---
### invoice_number
- **Type**: `STRING`
- **Description**: The invoice document number provide by the invoicing vendor
- **Distinct Values**: 71106107
- **Nulls**: 29
- **Top Values**:
  - `MILEAGE`: 13,589
  - `REIMBURSEMENT`: 3,454
  - `1`: 3,262
  - `REIMB`: 2,095
  - `PAYROLL`: 1,949

---
### invoice_total_amount
- **Type**: `FLOAT`
- **Description**: The total dollar amount listed on an invoice
- **Distinct Values**: 2949345
- **Nulls**: 83430
- **Top Values**:
  - `0`: 816,867
  - `20`: 212,721
  - `50`: 191,073
  - `25`: 182,347
  - `30`: 161,132

---
### invoice_paid_amount
- **Type**: `FLOAT`
- **Description**: The amount of the invoice that has been paid
- **Distinct Values**: 1948718
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 6,177,769
  - `20`: 190,883
  - `25`: 160,440
  - `10`: 143,951

---
### discount_taken_amount
- **Type**: `FLOAT`
- **Description**: The amount discounted from the invoice based on discount and payment terms
- **Distinct Values**: 26732
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 42,143,632
  - `0.08`: 9,860
  - `0.05`: 9,336
  - `0.1`: 9,169

---
### vendor_name
- **Type**: `STRING`
- **Description**: The name of the vendor listed on the invoice
- **Distinct Values**: 360146
- **Nulls**: 850465
- **Top Values**:
  - `Medline Industries, Inc.`: 2,380,259
  - `MEDLINE INDUSTRIES INC`: 2,357,539
  - `AmerisourceBergen`: 2,271,728
  - `OneTime`: 2,162,365
  - `Arthrex Inc.`: 1,662,937

---
### vendor_number
- **Type**: `STRING`
- **Description**: The unique number set up in the health system's ERP for the vendor providing the invoice
- **Distinct Values**: 324196
- **Nulls**: 12267606
- **Top Values**:
  - `NULL`: 12,267,606
  - `OneTime`: 2,562,482
  - `0000000029`: 1,737,915
  - `0034560`: 1,132,987
  - `SUP-078528`: 858,412

---
### premier_vendor_name
- **Type**: `STRING`
- **Description**: The Premier cleansed name for the invoicing vendor
- **Distinct Values**: 18676
- **Nulls**: 13324732
- **Top Values**:
  - `NULL`: 13,324,732
  - `MEDLINE INDUSTRIES, LP`: 7,316,167
  - `CARDINAL HEALTH 414, LLC`: 3,837,608
  - `AMERISOURCEBERGEN DRUG CORPORATION`: 2,996,016
  - `MCKESSON CORPORATION`: 2,924,985

---
### vendor_entity_code
- **Type**: `STRING`
- **Description**: The Premier entity code for the invoicing vendor
- **Distinct Values**: 21723
- **Nulls**: 13225317
- **Top Values**:
  - `NULL`: 13,225,317
  - `IL2114`: 7,270,802
  - `OH2129`: 2,916,231
  - `OH5010`: 2,314,414
  - `VA2023`: 2,299,203

---
### vendor_top_parent_name
- **Type**: `STRING`
- **Description**: The Premier cleansed name for the parent invoicing vendor
- **Distinct Values**: 1
- **Nulls**: 0
- **Top Values**:
  - `null`: 89,066,461

---
### vendor_top_parent_entity_code
- **Type**: `STRING`
- **Description**: The Premier parent entity code for the invoicing vendor
- **Distinct Values**: 9952
- **Nulls**: 19143628
- **Top Values**:
  - `NULL`: 19,143,628
  - `IL2114`: 7,316,167
  - `OH5010`: 3,837,608
  - `OH2129`: 2,991,928
  - `613772`: 2,924,770

---
### vendor_invoice_date
- **Type**: `DATE`
- **Description**: The date listed on the invoice that was created by the invoicing vendor
- **Distinct Values**: 9443
- **Nulls**: 23
- **Top Values**:
  - `2021-12-31`: 123,318
  - `2025-04-30`: 107,140
  - `2025-02-28`: 104,962
  - `2025-01-31`: 103,792
  - `2025-09-30`: 102,304

---
### remitra_invoice_received_date
- **Type**: `DATE`
- **Description**: The date that the invoice was received by Remitra
- **Distinct Values**: 3706
- **Nulls**: 33618096
- **Top Values**:
  - `NULL`: 33,618,096
  - `2025-10-14`: 61,255
  - `2025-12-23`: 58,740
  - `2024-11-05`: 51,953
  - `2023-11-02`: 50,105

---
### remitra_invoice_sent_date
- **Type**: `DATE`
- **Description**: The date the invoice was sent from Remitra to the provider
- **Distinct Values**: 3623
- **Nulls**: 40472190
- **Top Values**:
  - `NULL`: 40,472,190
  - `2025-08-26`: 49,936
  - `2025-10-14`: 46,035
  - `2025-11-14`: 40,079
  - `2025-07-04`: 38,118

---
### invoice_received_date
- **Type**: `DATE`
- **Description**: The date that the invoice was received from the vendor by the health system either in the ERP or Remitra.
- **Distinct Values**: 8815
- **Nulls**: 45792183
- **Top Values**:
  - `NULL`: 45,792,183
  - `2021-12-28`: 87,222
  - `2021-12-31`: 86,216
  - `2022-11-01`: 21,287
  - `2024-12-17`: 20,832

---
### invoice_create_date
- **Type**: `DATE`
- **Description**: This is the date that the invoice is created in the health system's ERP, unless it has not yet been imported, then it will reflect the date the invoice was received by Remitra
- **Distinct Values**: 8236
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `2021-12-31`: 62,754
  - `2021-12-28`: 56,037
  - `2021-12-29`: 54,110
  - `2022-01-04`: 43,275

---
### invoice_due_date
- **Type**: `DATE`
- **Description**: The due date for payment listed on the invoice
- **Distinct Values**: 9249
- **Nulls**: 45802985
- **Top Values**:
  - `NULL`: 45,802,985
  - `2022-01-30`: 89,058
  - `2022-01-27`: 86,336
  - `2025-05-30`: 32,564
  - `2023-06-30`: 29,571

---
### approval_needed_date
- **Type**: `DATE`
- **Description**: The date that invoice approval is required by
- **Distinct Values**: 4779
- **Nulls**: 83597909
- **Top Values**:
  - `NULL`: 83,597,909
  - `2022-11-30`: 6,848
  - `2024-03-01`: 5,718
  - `2023-11-30`: 5,679
  - `2022-09-30`: 5,415

---
### approved_date
- **Type**: `DATE`
- **Description**: The date that an invoice was approved for payment
- **Distinct Values**: 8300
- **Nulls**: 45855303
- **Top Values**:
  - `NULL`: 45,855,303
  - `2021-12-31`: 59,370
  - `2021-12-28`: 56,709
  - `2021-12-29`: 55,574
  - `2022-01-04`: 44,530

---
### payment_posted_date
- **Type**: `DATE`
- **Description**: The date that the payment was posted for an invoice
- **Distinct Values**: 8149
- **Nulls**: 45847916
- **Top Values**:
  - `NULL`: 45,847,916
  - `2021-12-31`: 59,362
  - `2021-12-28`: 56,698
  - `2021-12-29`: 55,544
  - `2022-01-04`: 44,537

---
### check_date
- **Type**: `DATE`
- **Description**: The date on the check for an invoice payment
- **Distinct Values**: 1181
- **Nulls**: 88087175
- **Top Values**:
  - `NULL`: 88,087,175
  - `2025-10-03`: 8,903
  - `2026-01-05`: 7,976
  - `2026-02-04`: 7,417
  - `2025-04-03`: 6,335

---
### last_modified_date
- **Type**: `DATE`
- **Description**: The date that the invoice header was last modified in the health system's ERP
- **Distinct Values**: 3037
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `2020-07-03`: 2,069,161
  - `2025-09-19`: 87,192
  - `2025-09-18`: 84,778
  - `2021-12-18`: 70,755

---
### fiscal_period
- **Type**: `FLOAT`
- **Description**: A 1-12 month indicator of the financial period varying based on a health system's defined fiscal year
- **Distinct Values**: 13
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `12`: 3,919,334
  - `4`: 3,792,267
  - `1`: 3,657,482
  - `3`: 3,642,360

---
### fiscal_year
- **Type**: `FLOAT`
- **Description**: The financial year that the invoice transaction took place
- **Distinct Values**: 31
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `2024`: 6,252,197
  - `2023`: 6,107,407
  - `2025`: 6,011,948
  - `2022`: 5,995,530

---
### payment_terms
- **Type**: `STRING`
- **Description**: The payment terms on the purchase order determining when final payment is due
- **Distinct Values**: 601
- **Nulls**: 10642
- **Top Values**:
  - `null`: 45,792,167
  - `30`: 5,561,873
  - `N30`: 5,202,931
  - `Net 30`: 4,563,137
  - `UR`: 3,556,265

---
### remitra_payment_terms
- **Type**: `STRING`
- **Description**: The payment terms on the invoice stored by Remitra
- **Distinct Values**: 1
- **Nulls**: 0
- **Top Values**:
  - `null`: 89,066,461

---
### po_number
- **Type**: `STRING`
- **Description**: The purchase order number linked to the invoice number
- **Distinct Values**: 35153740
- **Nulls**: 21789064
- **Top Values**:
  - `NULL`: 21,789,064
  - `RENT`: 60,518
  - `A4-6951D`: 57,559
  - `17959`: 23,186
  - `28715`: 21,682

---
### po_header_id
- **Type**: `INTEGER`
- **Description**: The internal ID used by the ERP system to identify a unique purchase order
- **Distinct Values**: 3178409
- **Nulls**: 61967813
- **Top Values**:
  - `NULL`: 61,967,813
  - `8736`: 56,347
  - `501874`: 23,065
  - `1034521`: 21,658
  - `192605`: 18,758

---
### remitra_po_header_id
- **Type**: `STRING`
- **Description**: The internal ID used by Remitra to identify a unique purchase order
- **Distinct Values**: 1
- **Nulls**: 0
- **Top Values**:
  - `null`: 89,066,461

---
### assigned_user_id
- **Type**: `STRING`
- **Description**: The ERP userid assigned to an invoice after it has been created in the system
- **Distinct Values**: 5887
- **Nulls**: 0
- **Top Values**:
  - `OAGIS9`: 22,169,743
  - `EDI`: 17,086,152
  - `L9MA540`: 2,841,524
  - `WRK_API_XML`: 2,477,241
  - `EDI810_4030_Tenet`: 2,452,257

---
### create_user_id
- **Type**: `STRING`
- **Description**: The ERP userid that created an invoice, if the invoice was created electronically, the user id will be EDI
- **Distinct Values**: 2230
- **Nulls**: 0
- **Top Values**:
  - `null`: 45,792,167
  - `MediClick`: 3,229,879
  - `EDI`: 2,299,889
  - `GatewayUser`: 2,235,208
  - `Admin`: 1,949,602

---
### approval_user_id
- **Type**: `STRING`
- **Description**: The userid assigned to approve an invoice for payment
- **Distinct Values**: 15581
- **Nulls**: 57591
- **Top Values**:
  - `null`: 45,792,167
  - `MediClick`: 2,551,293
  - `GatewayUser`: 2,226,284
  - `Admin`: 1,326,322
  - `EDI`: 996,453

---
### direct_approver
- **Type**: `STRING`
- **Description**: The assigned approver for an invoice
- **Distinct Values**: 8355
- **Nulls**: 87249412
- **Top Values**:
  - `NULL`: 87,249,412
  - `kquinn`: 31,687
  - `CALIMENA`: 24,035
  - `CH100705`: 23,372
  - `Eastmanli`: 20,089

---
### approver_group
- **Type**: `STRING`
- **Description**: The approver group assigned to an invoice
- **Distinct Values**: 14962
- **Nulls**: 85341655
- **Top Values**:
  - `NULL`: 85,341,655
  - `10600-BizSupSvc`: 35,313
  - `10-100-4485-I`: 26,797
  - `10-100-3015-I`: 25,251
  - `10600-BIZSUPSVC`: 23,610

---
### invoice_match_status_description
- **Type**: `STRING`
- **Description**: The text string description of the numerical indicator for the review status of an invoice
- **Distinct Values**: 5
- **Nulls**: 0
- **Top Values**:
  - `null`: 45,792,167
  - `Matched`: 27,063,843
  - `No Match`: 16,175,685
  - `Exception`: 29,205
  - `Incomplete`: 5,561

---
### invoice_status_description
- **Type**: `STRING`
- **Description**: A text string describing the current status of an invoice
- **Distinct Values**: 10
- **Nulls**: 0
- **Top Values**:
  - `null`: 45,792,167
  - `Paid-in-Full`: 37,152,770
  - `Completed`: 5,692,889
  - `Approved`: 372,659
  - `Exception`: 29,205

---
### remitra_invoice_status_description
- **Type**: `STRING`
- **Description**: A text string describing the current status of an invoice in Remitra's system
- **Distinct Values**: 18
- **Nulls**: 6870156
- **Top Values**:
  - `Acknowledged`: 48,555,435
  - `null`: 33,602,034
  - `NULL`: 6,870,156
  - `Awaiting Pickup`: 19,049
  - `Not Sent-InDoc-Normalized`: 13,696

---
### invoice_create_type_description
- **Type**: `STRING`
- **Description**: A text string description of how an invoice was created
- **Distinct Values**: 10
- **Nulls**: 0
- **Top Values**:
  - `IDS PO`: 44,311,513
  - `From PO`: 10,647,233
  - `EDI 810`: 10,285,250
  - `IDS Non-PO`: 8,285,777
  - `Manually`: 7,506,527

---
### payment_method_description
- **Type**: `STRING`
- **Description**: A text string description of the payment method including ACH payments, credit payments, and printed checks
- **Distinct Values**: 9
- **Nulls**: 7926435
- **Top Values**:
  - `null`: 45,792,167
  - `Local Print`: 20,335,199
  - `NULL`: 7,926,435
  - `ACH - CCD`: 7,059,181
  - `Check`: 3,484,401

---
### remitra_payment_method_description
- **Type**: `STRING`
- **Description**: The payment method for an invoice documented by Remitra
- **Distinct Values**: 1
- **Nulls**: 0
- **Top Values**:
  - `null`: 89,066,461

---
### remitra_invoice_yn
- **Type**: `INTEGER`
- **Description**: A yes (1) or no (0) indicator if the invoice was imported and transformed using optical character recognition to convert from a pdf or image to searchable text fields
- **Distinct Values**: 2
- **Nulls**: 478151
- **Top Values**:
  - `1`: 54,379,536
  - `0`: 34,208,774
  - `NULL`: 478,151

---
### remitra_wf_invoice_yn
- **Type**: `INTEGER`
- **Description**: Indicates if the invoice ever went into the Remitra workflow queue
- **Distinct Values**: 2
- **Nulls**: 33602034
- **Top Values**:
  - `0`: 34,643,968
  - `NULL`: 33,602,034
  - `1`: 20,820,459

---
### remitra_wf_modified_user
- **Type**: `INTEGER`
- **Description**: The user who modified the invoice in the Remitra workflow queue
- **Distinct Values**: 2564
- **Nulls**: 82038864
- **Top Values**:
  - `NULL`: 82,038,864
  - `24062`: 140,536
  - `24059`: 112,291
  - `25153`: 112,274
  - `26448`: 109,065

---
### remitra_wf_modified_date
- **Type**: `DATE`
- **Description**: The date the invoice was last modified in the Remitra workflow queue
- **Distinct Values**: 3622
- **Nulls**: 68246002
- **Top Values**:
  - `NULL`: 68,246,002
  - `2026-02-08`: 40,674
  - `2022-08-09`: 35,137
  - `2024-09-17`: 28,487
  - `2025-07-04`: 25,494

---
### remitra_wf_status_description
- **Type**: `STRING`
- **Description**: Current status description of an invoice that when into the Remitra workflow queue
- **Distinct Values**: 192
- **Nulls**: 68246002
- **Top Values**:
  - `NULL`: 68,246,002
  - `Processed`: 11,251,882
  - `Duplicates`: 3,307,187
  - `Bypassed`: 2,680,937
  - `Deleted by Customer`: 2,147,336

---
### invoice_has_active_exception_yn
- **Type**: `INTEGER`
- **Description**: A yes (1) or no (0) indicator if the invoice is currently in an exception status
- **Distinct Values**: 2
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 43,245,085
  - `1`: 29,209

---
### invoice_had_exception_yn
- **Type**: `INTEGER`
- **Description**: A yes (1) or no (0) indicator if, at any point, the invoice was in an exception status
- **Distinct Values**: 2
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 31,732,033
  - `1`: 11,542,261

---
### lines_with_price_exception
- **Type**: `INTEGER`
- **Description**: A count of the number of lines on an invoice that had a price exception
- **Distinct Values**: 53
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 43,041,385
  - `1`: 182,966
  - `2`: 29,604
  - `3`: 9,617

---
### lines_with_quantity_exception
- **Type**: `INTEGER`
- **Description**: A count of the number of lines on an invoice that had a quantity exception
- **Distinct Values**: 45
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 43,125,750
  - `1`: 122,813
  - `2`: 6,861
  - `3`: 4,036

---
### lines_with_receipt_exception
- **Type**: `INTEGER`
- **Description**: A count of the number of lines on an invoice that had a receipt exception
- **Distinct Values**: 140
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 42,675,384
  - `1`: 428,488
  - `2`: 85,502
  - `3`: 32,489

---
### lines_missing_with_exception
- **Type**: `INTEGER`
- **Description**: A count of the number of lines on an invoice that had a missing line exception
- **Distinct Values**: 43
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 43,221,825
  - `1`: 42,947
  - `2`: 5,483
  - `3`: 1,787

---
### lines_with_other_exception
- **Type**: `INTEGER`
- **Description**: A count of the number of lines on an invoice that had an other exception type not currently accounted for by exception counts above, such as a tax exception
- **Distinct Values**: 68
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 43,030,024
  - `1`: 161,784
  - `2`: 34,114
  - `3`: 15,337

---
### remitra_discrepancy_count
- **Type**: `INTEGER`
- **Description**: A count of the number of discrepancies identified by Remitra that were resolved prior to being sent to the customer
- **Distinct Values**: 0
- **Nulls**: 89066461
- **Top Values**:
  - `NULL`: 89,066,461

---
### touchless_invoice_yn
- **Type**: `INTEGER`
- **Description**: A yes (1) or no (0) indicator if an invoice was able to go directly to approval without manual intervention
- **Distinct Values**: 2
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 37,210,685
  - `1`: 6,063,609

---
### touch_count
- **Type**: `INTEGER`
- **Description**: A count of the number of times an invoice needed manual intervention to move to the next step in the workflow process
- **Distinct Values**: 18
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `1`: 37,107,921
  - `0`: 6,063,609
  - `2`: 81,297
  - `3`: 17,478

---
### rejection_count
- **Type**: `INTEGER`
- **Description**: A count of the number of times an invoice was rejected
- **Distinct Values**: 10
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 43,254,727
  - `1`: 17,198
  - `2`: 1,884
  - `3`: 350

---
### exception_date
- **Type**: `DATE`
- **Description**: The date that an EDI 810 invoice went into the exception queue
- **Distinct Values**: 2394
- **Nulls**: 88930752
- **Top Values**:
  - `NULL`: 88,930,752
  - `2025-12-09`: 488
  - `2025-03-18`: 475
  - `2026-01-08`: 465
  - `2025-12-18`: 460

---
### edi_810_exception_yn
- **Type**: `INTEGER`
- **Description**: A binary indicator if an invoice had an 810 exception
- **Distinct Values**: 2
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `0`: 43,138,585
  - `1`: 135,709

---
### import_exception_count
- **Type**: `INTEGER`
- **Description**: A count of the number of times an invoice went into the 810 exception queue
- **Distinct Values**: 2
- **Nulls**: 87188129
- **Top Values**:
  - `NULL`: 87,188,129
  - `1`: 1,874,344
  - `2`: 3,988

---
### refresh_date
- **Type**: `DATE`
- **Description**: The date that the view was last refreshed
- **Distinct Values**: 1
- **Nulls**: 45792167
- **Top Values**:
  - `NULL`: 45,792,167
  - `2026-02-10`: 43,274,294

---
### data_source
- **Type**: `STRING`
- **Description**: The source system data being ERP, Remitra, or both
- **Distinct Values**: 3
- **Nulls**: 0
- **Top Values**:
  - `Remitra`: 45,792,167
  - `ERP`: 33,602,034
  - `ERP/Remitra`: 9,672,260