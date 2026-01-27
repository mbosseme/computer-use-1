# Data Dictionary: `supplier_spend`

- Description: The Supplier Spend data source contains manufacturer-reported contract sales tracings from Premier contracted manufacturers. It represents purchases made by Premier members that are associated with active Premier agreements at the time of purchase. Unlike other data models sourced from health systems or distributors, this data comes directly from the manufacturer of record.

  **Key Characteristics:**
  - **Comprehensive Scope:** Covers all sites of care (hospitals, long-term care, physician practices, etc.) leveraging Premier agreements, avoiding the acute-centric bias of some other datasets.
  - **Direct Source:** Data is reported directly by the manufacturer back to Premier.

  **Limitations:**
  - **Reporting Reliance:** Relies on manufacturers accurately reporting what they consider "on-contract" spend.
  - **Contract Scope:** Limited to spend associated with a Premier agreement. It does not capture off-contract spend with the manufacturer or spend with non-contracted manufacturers in the same category.
  - **Membership Dynamics:** Reporting ceases if a facility leaves the Premier GPO, even if they continue purchasing from the manufacturer.

  This data has been cleansed by Premier, adding standardized identifiers/names for category, manufacturer, and other dimensions.
- Estimated rows: 87,518,545
- Distinct months: 36
- Generated via MCP BigQuery profiling.

## Columns

### Admin_Fees_Paid
- Type: `FLOAT`
- Description: The total admin fees paid
- Nulls: 0 (0.00%)
- Distinct: 6,167,677
- Distribution: min -180,000.00 | p25 1.31 | p50 3.73 | p75 13.42 | p90 54.62 | p95 138.49 | p99 727.10 | max 1,667,461.60

### Award_Type
- Type: `STRING`
- Description: This denotes whether one or more than once supplier is sourcing this contract category
- Nulls: 0 (0.00%)
- Distinct: 7
- Top values: MULTI SOURCE (68,842,390), OTHER (9,360,096), SOLE SOURCE (5,583,989), DUAL SOURCE (3,126,104), UNKNOWN (592,095)

### Bed_Size
- Type: `STRING`
- Description: The reporting facility's band of number of beds: <=100, 101-200, 201-300, 301-400, 401-500, >= 501
- Nulls: 0 (0.00%)
- Distinct: 1
- Top values: NOT AVAILABLE (87,518,545)

### Capital_Equipment_Flag
- Type: `STRING`
- Description: This denotes whether the contract category is for capital expenditure equipment
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: N (84,202,685), Y (3,315,860)

### Chargeback_ID
- Type: `STRING`
- Description: Pharmacy chargeback ID provide from CAMS
- Nulls: 71,892,813 (82.15%)
- Distinct: 9,965
- Top values: 17670-3 (135,058), 22902-3 (113,189), 21563-3 (113,148), 21451-4 (106,841), 21451-3 (106,839)

### Contract_Category
- Type: `STRING`
- Description: A Premier-defined taxonomy that reflects the contract group for which the product resides
- Nulls: 0 (0.00%)
- Distinct: 612
- Top values: PHARMACEUTICAL (9,959,189), FOODSERVICE DISPOSABLES (3,564,453), FROZEN BAKERY PRODUCTS (2,294,762), SALAD DRESSINGS MAYONNAISE AND RTU SAUCES (1,829,943), RTS COOKIES AND CRACKERS (1,686,532)

### Contract_Group
- Type: `STRING`
- Description: A Premier-defined group of similar contracts.
- Nulls: 0 (0.00%)
- Distinct: 612
- Top values: PHARMACEUTICAL (9,959,189), FOODSERVICE DISPOSABLES (3,564,453), FROZEN BAKERY PRODUCTS (2,294,762), SALAD DRESSINGS MAYONNAISE AND RTU SAUCES (1,829,943), RTS COOKIES AND CRACKERS (1,686,532)

### Contract_Name
- Type: `STRING`
- Description: The name of the contract
- Nulls: 0 (0.00%)
- Distinct: 780
- Top values: Generic Pharmaceuticals (4,308,864), Foodservice Disposables (3,564,435), Salad Dressings Mayonnaise and (1,827,268), RTS Cookies and Crackers (1,685,755), Frozen Bakery (1,677,652)

### Contract_Number
- Type: `STRING`
- Description: The identifying letter and number combination assigned to the contract
- Nulls: 0 (0.00%)
- Distinct: 5,182
- Top values: PP-DI-001D (959,737), PP-DI-2191 (559,565), PP-DI-2133 (533,908), PP-DI-1960 (514,563), PP-DI-2111 (494,217)

### Contracted_Supplier
- Type: `STRING`
- Description: The name of the company that holds the contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: 0 (0.00%)
- Distinct: 1,696
- Top values: US FOODS, INC. (17,524,210), TYSON FOODS, INC. (1,763,856), CARDINAL HEALTH 200, LLC (1,743,300), KRAFT HEINZ FOODS COMPANY, FOODSERVICE D (1,688,851), BECTON, DICKINSON AND COMPANY (1,502,432)

### Contracted_Supplier_Entity_Code
- Type: `STRING`
- Description: The entity code of the company that holds the contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: 0 (0.00%)
- Distinct: 1,697
- Top values: IL2111 (17,524,210), 613438 (1,763,450), IL5027 (1,743,300), 773763 (1,688,851), NJ2019 (1,502,432)

### Contracted_Supplier_Parent_Entity_Code
- Type: `STRING`
- Description: The entity code of the parent company that holds the contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: 0 (0.00%)
- Distinct: 1,425
- Top values: 703169 (18,123,539), OH5010 (2,190,261), NJ2019 (1,824,770), 613438 (1,754,653), 773763 (1,688,002)

### Contracted_Supplier_Parent_Name
- Type: `STRING`
- Description: The name of the parent company that holds the contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: 0 (0.00%)
- Distinct: 1,423
- Top values: USF HOLDING CORPORATION (18,123,539), CARDINAL HEALTH 414, LLC (2,190,260), BECTON, DICKINSON AND COMPANY (1,824,770), TYSON FOODS, INC. (1,754,747), KRAFT HEINZ FOODS COMPANY, FOO (1,688,002)

### Direct_Parent_Entity_Code
- Type: `STRING`
- Description: The entity code for the top direct parent reporting the data. This is the direct parent closest to the top parent. If there are other direct parents under the top direct parent, they will be considered facilities in this report.
- Nulls: 1,335,519 (1.53%)
- Distinct: 14,665
- Top values: 605082 (3,453,153), 665014 (2,294,812), AV5234 (2,266,806), 645118 (1,907,281), 718653 (1,583,030)

### Direct_Parent_Level_1_Entity_Code
- Type: `STRING`
- Description: Field refers to the highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. This would the GPO top parent.
- Nulls: 105,311 (0.12%)
- Distinct: 410
- Top values: 605082 (19,356,828), 682732 (10,248,971), NY0029 (4,982,270), 672187 (4,053,328), OH2041 (3,372,799)

### Direct_Parent_Level_1_Name
- Type: `STRING`
- Description: Field refers to the highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. This would the GPO top parent.
- Nulls: 105,311 (0.12%)
- Distinct: 409
- Top values: INNOVATIX, LLC NATIONAL HEADQUARTERS (19,356,828), OMNIA PARTNERS (10,248,971), PANDION OPTIMIZATION ALLIANCE (4,982,270), VALUE 4, LLC (4,053,328), WELLLINK GROUP PURCHASING - CHAMPS HEALTHCARE (3,372,799)

### Direct_Parent_Level_1_Premier_Relation
- Type: `STRING`
- Description: Field refers to the highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. This would the GPO top parent.
- Nulls: 105,340 (0.12%)
- Distinct: 2
- Top values: OLM (87,410,947), AFFILIATE (2,258)

### Direct_Parent_Level_2_Entity_Code
- Type: `STRING`
- Description: Field refers to the 2nd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L1 entity is the lowest reporting level, L2 will be the same as L1.
- Nulls: 105,311 (0.12%)
- Distinct: 52,626
- Top values: AV5234 (6,869,669), AU5708 (2,886,397), KY2085 (1,996,577), 645118 (1,909,231), 698144 (1,388,184)

### Direct_Parent_Level_2_Name
- Type: `STRING`
- Description: Field refers to the 2nd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L1 entity is the lowest reporting level, L2 will be the same as L1.
- Nulls: 105,311 (0.12%)
- Distinct: 50,875
- Top values: OMNIA PARTNERS - NONHEALTHCARE (6,869,669), PANDION OPTIMIZATION ALLIANCE_OMNIA NON-HEALTHCARE (2,886,397), ALLIANT PURCHASING, LLC (1,996,577), BROOKDALE SENIOR LIVING CORPORATE HEADQUARTERS (1,909,231), WALGREENS - PHARMACY PURCHASING (1,388,184)

### Direct_Parent_Level_2_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 2nd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L1 entity is the lowest reporting level, L2 will be the same as L1.
- Nulls: 105,340 (0.12%)
- Distinct: 2
- Top values: AFFILIATE (44,850,853), OLM (42,562,352)

### Direct_Parent_Level_3_Entity_Code
- Type: `STRING`
- Description: Field refers to the 3rd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L2 entity is the lowest reporting level, L3 will be the same as L2.
- Nulls: 105,311 (0.12%)
- Distinct: 185,781
- Top values: AP7026 (1,223,161), 673820 (1,107,599), AA8999 (792,419), 842122 (527,862), 606365 (515,052)

### Direct_Parent_Level_3_Name
- Type: `STRING`
- Description: Field refers to the 3rd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L2 entity is the lowest reporting level, L3 will be the same as L2.
- Nulls: 105,311 (0.12%)
- Distinct: 169,326
- Top values: CVS PHARMACY - RETAIL HQ (1,223,161), METZ & ASSOCIATES (1,107,599), UPPER CRUST FOOD SERVICE (792,419), AURORA HEALTH CARE, INC (527,933), HEALTHCARE PROCUREMENT SOLUTIONS (515,052)

### Direct_Parent_Level_3_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 3rd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L2 entity is the lowest reporting level, L3 will be the same as L2.
- Nulls: 105,340 (0.12%)
- Distinct: 2
- Top values: AFFILIATE (62,871,723), OLM (24,541,482)

### Direct_Parent_Level_4_Entity_Code
- Type: `STRING`
- Description: Field refers to the 4th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L3 entity is the lowest reporting level, L4 will be the same as L3.
- Nulls: 105,311 (0.12%)
- Distinct: 257,304
- Top values: AE6060 (325,434), 784669 (176,788), AW4626 (132,141), AM9590 (129,490)

### Direct_Parent_Level_4_Name
- Type: `STRING`
- Description: Field refers to the 4th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L3 entity is the lowest reporting level, L4 will be the same as L3.
- Nulls: 105,311 (0.12%)
- Distinct: 218,846
- Top values: CVS PHARMACY (1,220,823), COLLEGE FRESH (325,434), PAN GREGORIAN ENTERPRISES OF METRO NY & LI (176,788), METZ & ASSOCIATES_HEALTHCARE (132,141), SCHOOL SERVICES OF MONTANA (129,490)

### Direct_Parent_Level_4_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 4th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L3 entity is the lowest reporting level, L4 will be the same as L3.
- Nulls: 105,340 (0.12%)
- Distinct: 2
- Top values: AFFILIATE (63,409,824), OLM (24,003,381)

### Direct_Parent_Level_5_Entity_Code
- Type: `STRING`
- Description: Field refers to the 5th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L4 entity is the lowest reporting level, L5 will be the same as L4.
- Nulls: 105,311 (0.12%)
- Distinct: 270,396
- Top values: SC0047 (32,483), 803856 (31,819), OK0138 (31,250), IL2017 (31,143)

### Direct_Parent_Level_5_Name
- Type: `STRING`
- Description: Field refers to the 5th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L4 entity is the lowest reporting level, L5 will be the same as L4.
- Nulls: 105,311 (0.12%)
- Distinct: 229,862
- Top values: CVS PHARMACY (1,220,823), CASEY'S GENERAL STORES (57,079), HOLIDAY INN EXPRESS (46,293), AURORA PHARMACY, INC (42,456)

### Direct_Parent_Level_5_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 5th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L4 entity is the lowest reporting level, L5 will be the same as L4.
- Nulls: 105,340 (0.12%)
- Distinct: 2
- Top values: AFFILIATE (63,422,148), OLM (23,991,057)

### Direct_Parent_Name
- Type: `STRING`
- Description: The name for the top direct parent reporting the data. This is the direct parent closest to the top parent. If there are other direct parents under the top direct parent, they will be considered facilities in this report.
- Nulls: 1,335,548 (1.53%)
- Distinct: 14,497
- Top values: INNOVATIX, LLC NATIONAL HEADQUARTERS (3,453,153), KINDERCARE EDUCATION LLC (2,294,812), OMNIA PARTNERS - NONHEALTHCARE (2,266,806), BROOKDALE SENIOR LIVING CORPORATE HEADQUARTERS (1,907,281), UHS OF DELAWARE, INC. (1,583,030)

### Diversity_Type
- Type: `STRING`
- Description: Indicates the different types of diversity for Premier's contracted suppliers. Veteran Owned, Women Owned, Non Diverse, Minority Owned, Small Business Owned or Not Applicable
- Nulls: 0 (0.00%)
- Distinct: 5
- Top values: Non Diverse (86,207,541), Small Business Owned (786,653), Women Owned (387,547), Minority Owned (119,642), Veteran Owned (17,162)

### Effective_Date
- Type: `STRING`
- Description: The first day the contract is effective (contract start date).
- Nulls: 0 (0.00%)
- Distinct: 224
- Top values: 2015-07-01 (6,714,952), 2023-07-01 (4,562,981), 2022-02-01 (3,157,735), 2023-05-01 (2,876,750), 2022-01-01 (2,642,885)

### Expiration_Date
- Type: `STRING`
- Description: The last day the contract is effective (contract end date).
- Nulls: 0 (0.00%)
- Distinct: 197
- Top values: 2026-06-30 (4,418,692), 2026-04-30 (3,274,364), 2029-06-30 (3,269,145), 2025-09-30 (2,916,598), 2030-06-30 (2,824,944)

### Facility_Name
- Type: `STRING`
- Description: The name of the facility reporting the data
- Nulls: 0 (0.00%)
- Distinct: 271,124
- Top values:  (35,200), LEXINGTON MEDICAL CENTER - SC0047 (32,483), UNIVERSITY OF VIRGINIA MEDICAL CENTER - 803856 (31,819), SAINT FRANCIS HOSPITAL, INC. - OK0138 (31,250), CARLE HOSPITAL - IL2017 (31,143)

### Facility_Status
- Type: `STRING`
- Description: -
- Nulls: 105,340 (0.12%)
- Distinct: 3
- Top values: ACTIVE (83,197,567), TERMINATED (4,210,898), INACTIVE (4,740)

### Facility_Type
- Type: `STRING`
- Description: The type of the facility reporting the data as submitted by the supplier: ACUTE, NON-HEALTHCARE, ALTERNATE SITE.
- Nulls: 0 (0.00%)
- Distinct: 5
- Top values: ALTERNATE SITE (41,012,246), NON-HEALTHCARE (25,014,879), ACUTE (21,453,864), 0 (37,527), UNKNOWN (29)

### Health_System_Entity_Code
- Type: `STRING`
- Description: The entity code for the top parent reporting the data
- Nulls: 0 (0.00%)
- Distinct: 417
- Top values: 605082 (19,356,552), 682732 (10,248,971), NY0029 (4,982,165), 672187 (4,053,328), OH2041 (3,372,799)

### Health_System_Entity_Code_Primary
- Type: `STRING`
- Description: The Health System Primary field is a new field to ABI. It was developed by the Margin Improvement Insights team with feedback from the Commercial Analytics Team. The field is intended to the provide easy identification of the highest reporting level of an organization which may be a health system corporate parent, hospital, or facility. Under circumstances where the entity is under an Aggregation Affiliate or Sponsor (such as Acurity or Yankee) in the hierarchy, the Health System Primary would be the health system entity under the Aggregate Affiliate or Sponsor. This is intended to assist in identifying the expected top-level entity for analytics.
- Nulls: 67,514 (0.08%)
- Distinct: 43,462
- Top values: 682732 (10,248,971), 672187 (4,053,328), AU5708 (2,886,397), 665014 (2,443,645), 714747 (2,408,045)

### Health_System_Name
- Type: `STRING`
- Description: The name for top parent reporting the data
- Nulls: 0 (0.00%)
- Distinct: 417
- Top values: INNOVATIX, LLC NATIONAL HEADQUARTERS - 605082 (19,356,552), OMNIA PARTNERS - 682732 (10,248,971), PANDION OPTIMIZATION ALLIANCE - NY0029 (4,982,165), VALUE 4, LLC - 672187 (4,053,328), WELLLINK GROUP PURCHASING - CHAMPS HEALTHCARE - OH2041 (3,372,799)

### Health_System_Name_Primary
- Type: `STRING`
- Description: The Health System Primary field is a new field to ABI. It was developed by the Margin Improvement Insights team with feedback from the Commercial Analytics Team. The field is intended to the provide easy identification of the highest reporting level of an organization which may be a health system corporate parent, hospital, or facility. Under circumstances where the entity is under an Aggregation Affiliate or Sponsor (such as Acurity or Yankee) in the hierarchy, the Health System Primary would be the health system entity under the Aggregate Affiliate or Sponsor. This is intended to assist in identifying the expected top-level entity for analytics.
- Nulls: 67,514 (0.08%)
- Distinct: 42,675
- Top values: OMNIA PARTNERS (10,248,971), VALUE 4, LLC (4,053,328), PANDION OPTIMIZATION ALLIANCE_OMNIA NON-HEALTHCARE (2,886,397), KINDERCARE EDUCATION LLC (2,443,645), THE BUYING NETWORKS, LLC (2,408,045)

### Health_System_Name_row_id
- Type: `INTEGER`
- Description: IT added field for purpose of partitioning
- Nulls: 67,500 (0.08%)
- Distinct: 416
- Top values: 409 (19,356,552), 236 (10,248,971), 62 (4,982,165), 406 (4,053,328), 217 (3,372,799)

### Initiation_Date
- Type: `STRING`
- Description: The date activation were initiated.
- Nulls: 71,782,917 (82.02%)
- Distinct: 3,597
- Top values: 2024-09-27 (81,788), 2025-02-06 (68,519), 2024-02-29 (60,527), 2025-01-03 (59,344), 2024-09-26 (58,992)

### Line_of_Business
- Type: `STRING`
- Description: Line of Business description
- Nulls: 0 (0.00%)
- Distinct: 7
- Top values: Food Services (50,369,735), General GPO (24,318,832), Pharmacy (11,096,961), Capital Equipment (975,531), Clinical Laboratory Services (656,956)

### Local_Negotiation_Allowed_Flag
- Type: `STRING`
- Description: This denotes whether the contract terms allow the member to negotiate local terms
- Nulls: 0 (0.00%)
- Distinct: 6
- Top values: N (37,798,477), Y (26,266,111), Pays admin fees on all local agreements whether entered prior to or during the Premier agreement (18,639,442), Pays admin fees only on locals entered into during term of Premier agreement (3,516,431), Admin fees not due on locals and/or Member Agreement language struck (1,289,853)

### Market_Segment_Group
- Type: `STRING`
- Description: This is the members Group in Dynamics
- Nulls: 37,559 (0.04%)
- Distinct: 17
- Top values: LONG TERM CARE FACILITIES (23,439,920), HOSPITAL (19,294,851), ALTERNATE MARKETS (16,118,793), SCHOOLS (6,026,112), PHARMACY (5,705,889)

### Market_Segment_Primary_Service
- Type: `STRING`
- Description: This is the members Class of Trade in Dynamics
- Nulls: 32 (0.00%)
- Distinct: 79
- Top values: GENERAL MEDICAL AND SURGICAL (15,872,044), SKILLED NURSING (10,106,361), ASSISTED LIVING (8,005,830), DAY CARE (5,935,520), K-12 PUBLIC (4,827,755)

### MDF_Date
- Type: `STRING`
- Description: The effective date on the price activation or signed member designation form
- Nulls: 71,780,518 (82.02%)
- Distinct: 3,628
- Top values: 2022-07-01 (503,409), 2023-04-01 (425,504), 2023-05-01 (368,829), 2023-08-01 (346,776), 2023-01-01 (345,992)

### MDF_Required
- Type: `STRING`
- Description: A yes/no indicator identifying if a price activation or signed member designation form is required for access to base price
- Nulls: 11,132,101 (12.72%)
- Distinct: 3
- Top values: N (67,693,466), Y (8,658,996), DO NOT USE (33,982)

### Month
- Type: `STRING`
- Description: The month the invoice/purchase order was submitted by the supplier
- Nulls: 0 (0.00%)
- Distinct: 36
- Top values: October 2024 (2,687,139), April 2024 (2,673,995), January 2025 (2,626,626), April 2025 (2,624,803), October 2023 (2,623,318)

### PA_ID
- Type: `STRING`
- Description: Price Activation number
- Nulls: 71,850,417 (82.10%)
- Distinct: 361,769
- Top values: 3180074 (37,127), 2877781 (30,525), 2823707 (19,735), 3024062 (15,182), 3024063 (15,182)

### Premier_Entity_Code
- Type: `STRING`
- Description: Premier assigned alpha numeric and numeric code for the facility
- Nulls: 0 (0.00%)
- Distinct: 271,776
- Top values:  (34,596), SC0047 (32,483), 803856 (31,819), OK0138 (31,250), IL2017 (31,143)

### Premier_Spend
- Type: `FLOAT`
- Description: Total spend submitted by the supplier
- Nulls: 0 (0.00%)
- Distinct: 6,624,013
- Distribution: min -20,167,135.54 | p25 39.74 | p50 115.60 | p75 442.19 | p90 2,120.20 | p95 5,977.40 | p99 35,099.43 | max 94,029,992.58

### Program_Line
- Type: `STRING`
- Description: A descriptor for the kinds of products on the contract (MS – Nursing, MS - Surgical Services, MS – Cardiology, CE – Imaging, LA – Laboratory, CE – Facilities, CE - IT/ Telecom, MS – Distribution, SV - Purchased Services, FS – Chemicals, FS – Food, FS - Non-Foods, FS – Nutritionals, Rx – Hospital, Rx - Wholesaler)
- Nulls: 0 (0.00%)
- Distinct: 24
- Top values: FS - Food (50,362,131), Nursing (10,728,913), Rx - Pharmaceuticals (10,160,887), Surgical (3,443,282), Environmental Services (2,662,501)

### Quarter
- Type: `STRING`
- Description: The quarter the invoice/purchase order was submitted by the supplier
- Nulls: 0 (0.00%)
- Distinct: 13
- Top values: Jan - Mar 2025 (7,688,038), Oct - Dec 2024 (7,644,134), Jul - Sep 2024 (7,552,674), Jan - Mar 2024 (7,542,120), Apr - Jun 2024 (7,470,101)

### Rebate_Available_Flag
- Type: `STRING`
- Description: This denotes whether there is a rebate for products on the contract
- Nulls: 2,449,523 (2.80%)
- Distinct: 2
- Top values: N (59,542,795), Y (25,526,227)

### Replacement_Contracts
- Type: `STRING`
- Description: This provides contract numbers for subsequent replacement contracts
- Nulls: 50,733,196 (57.97%)
- Distinct: 1,772
- Top values: PP-DI-2401, Cheese and Cheese Sauce (529,263), PP-DI-2482, Breakfast Sausage (482,605), PP-DI-2473, Canned Fruit (448,929), PP-DI-2394, Frozen Bread (428,315), PP-DI-2474, Canned Vegetables (427,929)

### Response_Accepted_Date
- Type: `STRING`
- Description: vnet response accepted date for price activations from SCA
- Nulls: 71,850,417 (82.10%)
- Distinct: 3,670
- Top values: 2025-01-03 (63,622), 2024-02-29 (61,547), 2023-07-20 (55,419), 2024-02-02 (46,096), 2024-09-27 (45,992)

### SA
- Type: `STRING`
- Description: System Aggregation Flag from CAMS
- Nulls: 0 (0.00%)
- Distinct: 2
- Top values: N (80,880,129), Y (6,638,416)

### Signed_Tier_Description
- Type: `STRING`
- Description: Brief description of the tier the facility price activated or signed via the member designation form. This price activation is at the time of the purchase. If a price activation occurred after the transaction, there will be no signed tier description.
- Nulls: 71,930,036 (82.19%)
- Distinct: 6,870
- Top values: TIER 1:  No Commitment Required, PMDF Not Required. Total Product Purchases ($ Per Calendar Year). (737,666), AscenDrive TIER:  80% Participation. AscenDrive Pricing (% Participation In Annual Dollars). (456,244), TIER 2:  80% Commitment/Aggregation Groups. Total Product Purchases ($ Per Calendar Year) (134,017), SURPASS TIER:  90% Participation. Surpass Pricing (% Participation In Annual Dollars). (128,750), TIER 2:  80% Commitment/Aggregation Groups. Total Product Purchases ($ Per Calendar Year). (127,992)

### Signed_Tier_Status
- Type: `STRING`
- Description: Progress of the price activation or member designation form. Can be Accepted, Initialed or Pending. This price activation is at the time of the purchase. If a price activation occurred after the transaction, there will be no signed tier description.
- Nulls: 71,848,018 (82.09%)
- Distinct: 3
- Top values: ACCEPTED (15,668,128), PENDING (1,862), INITIALED (537)

### Spend_Period_YYYYQMM
- Type: `INTEGER`
- Description: The month key is the YYYYQMM (2018101 = Jan, Q1, 2018) used for blends or joins.
- Nulls: 0 (0.00%)
- Distinct: 36
- Top values: 2024410 (2,687,139), 2024204 (2,673,995), 2025101 (2,626,626), 2025204 (2,624,803), 2023410 (2,623,318)

### Tier_ID
- Type: `INTEGER`
- Description: A unique ID for the tier. This is not a key.
- Nulls: 0 (0.00%)
- Distinct: 9,988
- Top values: 0 (71,780,518), 10034345 (135,058), 10050214 (113,189), 10045717 (113,150), 10045305 (106,843)

### Year
- Type: `INTEGER`
- Description: The year the invoice/purchase order was submitted by the supplier
- Nulls: 0 (0.00%)
- Distinct: 4
- Top values: 2024 (30,209,029), 2023 (29,042,639), 2025 (23,730,716), 2022 (4,536,161)

### contract_gpo_name
- Type: `STRING`
- Description: Denotes the type of contract. Example values for this field: Premier, Conductiv, etc.
- Nulls: 0 (0.00%)
- Distinct: 3
- Top values: PREMIER (87,418,047), ACURITY (66,883), CONDUCTIV CONTRACTS (33,615)
