# Data Dictionary: `transaction_analysis_expanded`

- Description: Rolling 7-year (≈85 month) transactional purchase feed (clone of upstream staging) with enriched contract matching, manufacturer/vendor normalization, product taxonomy (UNSPSC & HVI), unit-of-measure normalization, sustainability attributes, benchmarking (current + 6‑month), and outlier / aggregation flags. Supports price benchmarking, contract compliance, category performance analysis, and opportunity identification.
- **Exclusions:** Any health system whose name contains "% TEST", "% TEST %", "%PREMIER%", "% DEMO", or "% DEMO %" (case-insensitive) must be excluded from analysis to remove dummy/test entities.
- Estimated rows: 819,455,583
- Distinct months: 85
- Partitioning: DAY on `Transaction_Date`
- Clustering: `Contract_Category`, `Manufacturer_Top_Parent_Name`, `Manufacturer_Name`
- Generated via MCP BigQuery profiling (null counts, distincts, top values, quantiles). Columns marked (Inferred) have synthesized definitions.

## Columns

### Transaction_Date
- Type: `TIMESTAMP`
- Description: The date on the purchase order submitted by the facility
- Nulls: 0 (0.00%)
- Distinct: 2,563

### Month (Inferred)
- Type: `STRING`
- Description: The month the invoice/purchase order was submitted by the facility (formatted: MonthYear, October 2020)
- Nulls: 0 (0.00%)
- Distinct: 85

### Contract_Category
- Type: `STRING`
- Description: A Premier-defined taxonomy that reflects the contract group for which the product resides
- Nulls: 0 (0.00%)
- Distinct: ~870
- Top values: UNKNOWN (78,613,326), BANDAGES DRESSINGS AND GAUZE (29,190,146), PATIENT BEDSIDE PRODUCTS (23,471,350), IV THERAPY PRODUCTS - IV FLUIDS BAG-BASED DRUG DELIVERY AND TPN MACRONUTRIENTS (21,110,450), GENERAL ORTHOPEDIC TRAUMA PRODUCTS (19,141,509)

### Manufacturer_Top_Parent_Name
- Type: `STRING`
- Description: The name of the top parent manufacturer that makes the product
- Nulls: 0 (0.00%)
- Distinct: ~23,575
- Top values: MEDLINE INDUSTRIES, LP (106,424,728), UNKNOWN (80,318,314), CARDINAL HEALTH 414, LLC (72,635,455), BECTON, DICKINSON AND COMPANY (60,780,772), JOHNSON & JOHNSON (27,908,002)

### Manufacturer_Name (Inferred)
- Type: `STRING`
- Description: The title of a company which owns and/or runs a manufacturing plant.
- Nulls: 0 (0.00%)
- Distinct: ~27,107
- Top values: MEDLINE INDUSTRIES, LP (104,569,684), UNKNOWN (80,861,213), CARDINAL HEALTH 200, LLC (71,368,986), BECTON, DICKINSON AND COMPANY (47,356,183), BAXTER HEALTHCARE CORPORATION (18,661,729)

### Vendor_Name
- Type: `STRING`
- Description: The name of the distributor/vendor that sells the product
- Nulls: 0 (0.00%)
- Distinct: ~25,372
- Top values: MEDLINE INDUSTRIES, LP (150,671,977), OWENS & MINOR DISTRIBUTION, INC. (67,304,054), UNKNOWN (63,783,384), CARDINAL HEALTH 414, LLC (62,399,676), OWENS & MINOR, INC. (54,066,690)

### Brand_Name (Inferred)
- Type: `STRING`
- Description: The name that products are associated with
- Nulls: 259,048,085 (31.62%)
- Distinct (non-null): ~75,705
- Top values (non-null): PREMIERPRO (10,287,638), MEDICHOICE (7,718,996), SODIUM CHLORIDE (7,101,990), LUER-LOK (6,076,077), VACUTAINER (6,023,746)

### Base_Spend
- Type: `FLOAT`
- Description: Total spend without distributor markup applied
- Nulls: 0 (0.00%)
- Distinct: ~4,356,050
- Distribution: min -76,964,027.76 | p25 10.124 | p50 47.53 | p75 206.8 | p90 792 | p95 1,649.94 | p99 4,787 | max 9,000

### Landed_Spend (Inferred)
- Type: `FLOAT`
- Description: Total spend with distributor markup applied (mark up is only applied if put into the distributor mark up tool)
- Nulls: 0 (0.00%)
- Distinct: ~3,954,305
- Distribution: min -76,964,027.76 | p25 10.172 | p50 47.66 | p75 207 | p90 793.8 | p95 1,650 | p99 4,787 | max 9,000

### Quantity
- Type: `FLOAT`
- Description: sum of products purchased
- Nulls: 0 (0.00%)
- Distinct: ~419,293
- Distribution: min -25,677,960 | p25 1 | p50 2 | p75 6 | p90 20 | p95 30 | p99 96 | max 144

### Base_Each_Price (Inferred)
- Type: `FLOAT`
- Description: The price paid at the time of the transaction per unit for the product without distributor markup applied. Facility Base Price / UOM Conv Factor
- Nulls: 1,447,586 (0.18%)
- Distribution: min -367,434.31 | p50 2.08 | p90 239.47 | p99 2,690 | max 4,792.87

### Landed_Each_Price (Inferred)
- Type: `FLOAT`
- Description: The price paid per unit for the product with distributor markup applied. Facility Landed Price / UOM Conv Factor (if the markup was entered in the distributor markup tool)
- Nulls: 1,447,586 (0.18%)
- Distribution: min -367,434.31 | p50 2.09 | p90 240 | p99 2,690 | max 4,792.87

### Contract_Number
- Type: `STRING`
- Description: The identifying letter and number combination assigned to the contract
- Nulls: 0 (0.00%)
- Distinct: ~16,252

### Contract_Name (Inferred)
- Type: `STRING`
- Description: The name of the contract
- Nulls: 0 (0.00%)
- Distinct: ~7,102

### Contract_Type
- Type: `STRING`
- Description: A denotes if a contract is an ASCEND, Local, Premier, or Regional
- Nulls: 0 (0.00%)
- Distinct: 9
- Top values: UNKNOWN (343,871,736), PREMIER (327,538,083), ASCEND (46,204,061), LOCAL (36,319,188), SURPASS (35,228,390)

### Contract_Price_Found (Inferred)
- Type: `STRING`
- Description: A yes/no indicator identifying whether or not pricing is available on a Premier or Non Premier Contract
- Nulls: 0 (0.00%)
- Distinct: 2
- Distribution: Y 475,623,854 (58.07%), N 343,831,729 (41.93%)

### Contract_Access_Price (Inferred)
- Type: `FLOAT`
- Description: The price per unit at the access level of the contract
- Nulls: 299,732,468 (36.58%)

### Contract_Best_Price (Inferred)
- Type: `FLOAT`
- Description: The price per unit at the best level of the contract
- Nulls: 299,732,468 (36.58%)

### Contracted_Supplier_Parent (Inferred)
- Type: `STRING`
- Description: The top parent name of the company that holds the contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: 0 (0.00%)
- Distinct: ~6,822

### Contracted_Supplier (Inferred)
- Type: `STRING`
- Description: The name of the company that holds the contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: 0 (0.00%)
- Distinct: ~2,410

### Manufacturer_Catalog_Number
- Type: `STRING`
- Description: The manufacturer's identification number for the product.
- Nulls: 0 (0.00%)
- Distinct: ~1,399,549

### Vendor_Entity_Code (Inferred)
- Type: `STRING`
- Description: The Premier assigned alpha numeric and numeric code for the distributor/vendor that sells the product.
- Nulls: 0 (0.00%)
- Distinct: ~25,424

### PIN (Inferred)
- Type: `STRING`
- Description: Premier assigned Product Identification Number. A PIN is unique to a Vendor Entity Code, Catalog Num and Pkg UOM. Items distributed in multiple Pkg UOMs could generate additional PINs for a product.
- Nulls: 0 (0.00%)
- Distinct: ~1,821,747

### Product_Description (Inferred)
- Type: `STRING`
- Description: A brief description of the product
- Nulls: 0 (0.00%)
- Distinct: ~1,419,681

### Facility_Name
- Type: `STRING`
- Description: The name of the facility reporting the data
- Nulls: 0 (0.00%)
- Distinct: ~13,250

### Facility_Hin (Inferred)
- Type: `STRING`
- Description: Reporting facility HIN number (Hospital Identification Number)
- Nulls: 261,169,700 (31.87%)
- Distinct: ~6,557

### Facility_Department_Name (Inferred)
- Type: `STRING`
- Description: Brief description of the facility cost center (this data is submitted via the cost center fields when the user submits data to Premier)
- Nulls: 671,141 (0.08%)
- Distinct: ~350,875

### UOM_Conv (Inferred)
- Type: `INTEGER`
- Description: The number of individual products in a package
- Nulls: 124,207,086 (15.16%)

### Pkg_UOM (Inferred)
- Type: `STRING`
- Description: The unit of measure description of the package type (case, box, carton)
- Nulls: 124,207,078 (15.16%)
- Distinct: 73

### UNSPSC_Segment_Code
- Type: `STRING`
- Description: The first level of the United Nations Standard Products and Services Code taxonomy
- Nulls: 0 (0.00%)
- Distinct: 58
- Top values: 42 (559,750,363), 41 (46,833,090), 0 (45,718,033), 51 (44,068,965), 53 (38,354,391)

### UNSPSC_Class_Code
- Type: `STRING`
- Description: The third level of the United Nations Standard Products and Services Code taxonomy
- Nulls: 0 (0.00%)
- Distinct: 2,404
- Top values: 423115 (53,909,026), 0 (45,718,033), 531316 (26,458,037), 422034 (24,080,217), 421322 (23,586,920)

### UNSPSC_Commodity_Code
- Type: `STRING`
- Description: The fourth level of the United Nations Standard Products and Services Code taxonomy
- Nulls: 0 (0.00%)
- Distinct: 13,071
- Top values: 0 (45,718,033), 42000000 (14,705,100), 42132203 (14,362,638), 42311512 (14,120,941), 51000000 (12,566,141)

### HVI_Level_2_Category_Description (Inferred)
- Type: `STRING`
- Description: High-Value Implant product categorization, Level 2 description
- Nulls: 54,829,085 (6.69%)
- Distinct: 66
- Top values: UNKNOWN (721,560,137), GENERAL FIXATION (8,226,447), DISPOSABLES & INSTRUMENTATION (5,559,370), KNEE ARTHROPLASTY (4,838,928), HIP ARTHROPLASTY (4,648,046)

### HVI_Level_3_Category_Description (Inferred)
- Type: `STRING`
- Description: High-Value Implant product categorization, Level 3 description
- Nulls: 54,829,085 (6.69%)
- Distinct: 1,437
- Top values: UNKNOWN (721,691,880), DISPOSABLES & INSTRUMENTATION (5,712,864), SCREW - CORTICAL - NON LOCKING (3,135,201), DISPOSABLES AND INSTRUMENTATION (2,632,026), SCREW - CORTICAL - LOCKING (2,504,084)

### HVI_Level_4_Category_Description (Inferred)
- Type: `STRING`
- Description: High-Value Implant product categorization, Level 4 description
- Nulls: 54,829,085 (6.69%)
- Distinct: 745
- Top values: UNKNOWN (721,691,886), TITANIUM (9,382,201), DISPOSABLES & INSTRUMENTATION (5,712,864), STAINLESS STEEL (5,569,927), CEMENTLESS (2,298,265)

### Spend_Type
- Type: `STRING`
- Description: Indicates the state of the products purchased at the time of the transaction. On Contract Spend - The products purchased are on a Premier, local and regional contract. Products categorized as On Contract are included a completed price activation; fully executed paper member designation form (PMDF); or a PMDF is not required to access base pricing for products to fall into this category. Off Contract Spend - The products purchased did not utilize a contract and a functional equivalent is available on a contract Non Contract Spend - The products purchased did not utilize a contact and no functional equivalent is available on a contract. On Contract Spend (PA Op) - The products purchased are on a Premier contract that does not have a completed price activation or a fully executed PMDF. Categorized Spend - The products purchased are in the data cleansing review process or products purchased contain incomplete or incorrect information.
- Nulls: 0 (0.00%)
- Distinct: 5
- Distribution: ON CONTRACT (PA OP) 259,882,378, ON CONTRACT 215,741,476, NON CONTRACT 189,569,413, CATEGORIZED ONLY 124,044,012, OFF CONTRACT 30,218,304

### product_group_category (Inferred)
- Type: `STRING`
- Description: Common recognized group of interrelated items that identifies what the product is.
- Nulls: 166,686,038 (20.35%)
- Distinct: 2,637
- Top values: IV FLUIDS BAG-BASED - SOLUTIONS (18,029,867), GENERAL ORTHOPEDIC TRAUMA PRODUCTS (17,875,578), PATIENT BEDSIDE - AMENITIES (15,721,449), ORTHOPEDIC TOTAL JOINT IMPLANTS (15,270,365), EXAM GLOVES - NITRILE / NON-STERILE (12,726,747)

### product_subcategory1 (Inferred)
- Type: `STRING`
- Description: Groups of items sharing a primary function or use. Represents a sub-group of the Product Group.
- Nulls: 179,180,016 (21.87%)
- Distinct: 10,713
- Top values: POWDER - FREE (23,214,076), STANDARD (13,344,006), SPONGES (11,317,800), 0.9% NACL (11,251,559), ACCESSORIES (9,159,412)

### product_subcategory2 (Inferred)
- Type: `STRING`
- Description: Groups of similar items with shared characteristics. Represents items in Subcategory 1 at a more granular level, grouped by similar attributes.
- Nulls: 199,547,738 (24.35%)
- Distinct: 36,783
- Top values: TEXTURED / CHEMO TESTED (12,601,971), 1000ML (12,054,144), ADULT (10,060,233), UNSCENTED (8,014,894), SCENTED (7,456,301)

### product_subcategory3 (Inferred)
- Type: `STRING`
- Description: Product attributes that are more granular than Subcategory 2 as needed.
- Nulls: 311,520,054 (38.03%)
- Distinct: 33,665
- Top values: SYSTEM SPECIFIC (17,929,867), FLEXIBLE CONTAINER/BAG (16,500,673), STANDARD CUFF (13,256,037), TITANIUM (9,567,771), STERILE (9,198,539)

### service_line (Inferred)
- Type: `STRING`
- Description: Indicates the service line
- Nulls: 78,629,081 (9.60%)
- Distinct: 7
- Distribution: MEDICAL/SURGICAL 469,251,085, PPI 127,745,751, DIAGNOSTICS 51,557,656, SERVICES & TECHNOLOGY 28,803,194, FACILITIES & CONSTRUCTION 25,514,023

### line_of_business (Inferred)
- Type: `STRING`
- Description: Line of Business description
- Nulls: 78,629,081 (9.60%)
- Distinct: 8
- Distribution: GENERAL GPO 669,925,106, THSCS GENERAL GPO 27,512,819, PHARMACY 20,301,702, FOOD SERVICES 17,649,956, ACURITY 2,617,440

### outlier_flag
- Type: `STRING`
- Description: E1 excludes facilities without an "active" status in Dynamics; E2 excludes records with fewer than 10 transactions; E3 excludes products purchased by fewer than two Top Parents; E4 excludes cases where more than one member top parent is not available for the Minimum Each Price; E5 excludes recruitment facilities; E6 excludes all CommonSpirit records; and E7 excludes all Atrium Medtronic purchases. P excludes records where each price is less than or equal to zero at two-decimal precision (e.g., .001, 0.0000002) or where total PO line cost is less than or equal to 0.01. Y identifies outliers using the Interquartile Range (IQR) method.
- Nulls: 804,039,824 (98.12%)
- Distinct: 9
- Top values: E6 (3,240,327), E3 (3,131,368), E1 (2,984,333), Y (2,951,972), E4 (1,569,948)

### HVI_Outlier_Flg
- Type: `STRING`
- Description: Transaction price was determined to be invalid for High-Value Implant benchmarking calculations
- Nulls: 303,881,362 (37.06%)
- Distinct: 2
- Distribution: Y 2,293,183, (others/blank) remainder

### ABI_Outlier_Flag (Inferred)
- Type: `STRING`
- Description: ABI outlier flag definition: Denotes if the transaction is deemed as an abnormal data point by the ABI team. In these instances, the upstream team is aware of the data point as well and may be working to resolve. Examples of when this flag may occur is when a single transaction is overall $5,000,000 or if the same transaction repeats the same day and totals more than $3,000,000 when summed.
- Nulls: 819,439,637 (99.998%)
- Distinct: 1

### aggregation_flag
- Type: `INTEGER`
- Description: The definition of this field is under investigation and the field should be ignored.
- Nulls: 0 (0.00%)
- Distinct: 2
- Distribution: 1 = 475,803,151 (58.1%), 0 = remainder

### Antibacterial_Free
- Type: `STRING`
- Description: Item free of intentionally added antimicrobial/antibacterial agents? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Ascend_End_Date
- Type: `STRING`
- Description: The date the member ends ASCEND membership.
- Nulls: TBD
- Distinct: TBD

### Ascend_Start_Date
- Type: `STRING`
- Description: The date the member starts ASCEND membership.
- Nulls: TBD
- Distinct: TBD

### Bed_Size
- Type: `STRING`
- Description: The reporting facility's band of number of beds: <=100, 101-200, 201-300, 301-400, 401-500, >= 501
- Nulls: TBD
- Distinct: TBD

### Benchmark_10th_Percentile
- Type: `STRING`
- Description: Premier benchmark pricing based on the 10th percentile
- Nulls: TBD
- Distinct: TBD

### Benchmark_10th_Percentile_6_Month
- Type: `STRING`
- Description: Premier benchmark pricing based on the 10th percentile calculated using six months of data
- Nulls: TBD
- Distinct: TBD

### Benchmark_25th_Percentile
- Type: `STRING`
- Description: Premier benchmark pricing based on the 25th percentile
- Nulls: TBD
- Distinct: TBD

### Benchmark_25th_Percentile_6_Month
- Type: `STRING`
- Description: Premier benchmark pricing based on the 25th percentile calculated using six months of data
- Nulls: TBD
- Distinct: TBD

### Benchmark_High_Price
- Type: `STRING`
- Description: Premier benchmark pricing, based on the 95th percentile
- Nulls: TBD
- Distinct: TBD

### Benchmark_High_Price_6_Month
- Type: `STRING`
- Description: Premier benchmark pricing, based on the 95th percentile calculated using six months of data
- Nulls: TBD
- Distinct: TBD

### Benchmark_Low_Price
- Type: `STRING`
- Description: Premier benchmark pricing based on the 5th percentile
- Nulls: TBD
- Distinct: TBD

### Benchmark_Low_Price_6_Month
- Type: `STRING`
- Description: Premier benchmark pricing based on the 5th percentile calculated using six months of data
- Nulls: TBD
- Distinct: TBD

### Benchmark_Median_Price
- Type: `STRING`
- Description: Premier benchmark pricing based on the median price
- Nulls: TBD
- Distinct: TBD

### Benchmark_Median_Price_6_Month
- Type: `STRING`
- Description: Premier benchmark pricing based on the median price calculated using six months of data
- Nulls: TBD
- Distinct: TBD

### Bisphenol_A_Free
- Type: `STRING`
- Description: Indicates if an item is free of intentionally added bisphenols. (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Ca_Prop_65_Warning
- Type: `STRING`
- Description: Item requires a California Proposition 65 warning? (If yes, provide the warning language.) (If No, leave blank.)
- Nulls: TBD
- Distinct: TBD

### Ca_Prop_65_Warning_Required
- Type: `STRING`
- Description: Item requires a California Proposition 65 warning? (Yes/No/Do not sell in California)
- Nulls: TBD
- Distinct: TBD

### Calculated_Facility_Base_Each_Price
- Type: `STRING`
- Description: Facility Base Price / Facility Conv Factor
- Nulls: TBD
- Distinct: TBD

### Calculated_Facility_Landed_Each_Price
- Type: `STRING`
- Description: Facility Landed Price / Facility Conv Factor
- Nulls: TBD
- Distinct: TBD

### Category_Cleansing_Status
- Type: `STRING`
- Description: Initiative end date as defined in the category template
- Nulls: TBD
- Distinct: TBD

### Census_Division
- Type: `STRING`
- Description: Identifies one of nine possible Census divisions for the facility location
- Nulls: TBD
- Distinct: TBD

### Census_Region
- Type: `STRING`
- Description: Identifies one of four possible Census Regions for the facility location.
- Nulls: TBD
- Distinct: TBD

### Cons_Friendly_Pkg_Label
- Type: `STRING`
- Description: Consumer friendly packaging label? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Cont_Prop_65_Below_Thresh_Det
- Type: `STRING`
- Description: Item contains intentionally added Proposition 65 chemicals at a level below that requiring a warning? (If Yes, specify.) (If No, leave blank.) (If Don't Know leave blank.)
- Nulls: TBD
- Distinct: TBD

### Cont_Prop_65_Below_Threshold
- Type: `STRING`
- Description: Indicates if an item contains intentionally added Proposition 65 chemicals at a level below that requires a warning.
- Nulls: TBD
- Distinct: TBD

### Contract_Access_Tier_Description
- Type: `STRING`
- Description: The access level purchasing requirements of the contract
- Nulls: TBD
- Distinct: TBD

### Contract_Best_Tier_Description
- Type: `STRING`
- Description: The best level purchasing requirements of the contract
- Nulls: TBD
- Distinct: TBD

### Contract_Category_Key
- Type: `STRING`
- Description: Unique identifier for the contract category
- Nulls: TBD
- Distinct: TBD

### Contract_Designation_Key
- Type: `STRING`
- Description: Unique identifier for the contract designation
- Nulls: TBD
- Distinct: TBD

### Contract_Effective_Date
- Type: `STRING`
- Description: The contract start date.
- Nulls: TBD
- Distinct: TBD

### Contract_Expiration_Date
- Type: `STRING`
- Description: The contract end date.
- Nulls: TBD
- Distinct: TBD

### Contract_Group
- Type: `STRING`
- Description: A Premier-defined group of similar contracts.
- Nulls: TBD
- Distinct: TBD

### Contract_Pkg_Access_Price
- Type: `STRING`
- Description: The cost to purchase the product(s) in a package rather than an each at the access level of the contract
- Nulls: TBD
- Distinct: TBD

### Contract_Pkg_Best_Price
- Type: `STRING`
- Description: The cost to purchase the product(s) in a package rather than an each at the best level of the contract
- Nulls: TBD
- Distinct: TBD

### Contract_Pkg_Uom
- Type: `STRING`
- Description: The unit of measure description of the package type on the contract (case, box, carton)
- Nulls: TBD
- Distinct: TBD

### Contract_Type_Key
- Type: `STRING`
- Description: Unique identifier for the contract type.
- Nulls: TBD
- Distinct: TBD

### Contract_Uom_Conv
- Type: `STRING`
- Description: The number of individual products in a package on the contract as cleansed by Premier
- Nulls: TBD
- Distinct: TBD

### Contracted_Catalog_Number
- Type: `STRING`
- Description: The catalog number for the company that holds the contract. Applies to Premier contracts only. This catalog number could be a supplier, business partner, vendor, distributor or manufacturer, whoever is on the contract.
- Nulls: TBD
- Distinct: TBD

### Contracted_Supplier_Entity_Code
- Type: `STRING`
- Description: The entity code of the company that holds the contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: TBD
- Distinct: TBD

### Contracted_Supplier_Tp_Key
- Type: `STRING`
- Description: Unique identifier for the contracted supplier top parent
- Nulls: TBD
- Distinct: TBD

### Corporate_Parent_Ein
- Type: `STRING`
- Description: The identifier of the Corporate Top Parent of the facility
- Nulls: TBD
- Distinct: TBD

### Corporate_Parent_Name
- Type: `STRING`
- Description: The Corporate Top Parent of the facility
- Nulls: TBD
- Distinct: TBD

### Ctr_Flag
- Type: `STRING`
- Description: A yes/no indicator identifying whether a transaction was categorized as On Contract
- Nulls: TBD
- Distinct: TBD

### Current_Contract_Effective_Date
- Type: `STRING`
- Description: The contract start date as of the present date.
- Nulls: TBD
- Distinct: TBD

### Current_Contract_Expiration_Date
- Type: `STRING`
- Description: The contract end date as of the present date.
- Nulls: TBD
- Distinct: TBD

### Current_Contract_Name
- Type: `STRING`
- Description: The name of the contract as of the present date
- Nulls: TBD
- Distinct: TBD

### Current_Contract_Number
- Type: `STRING`
- Description: The identifying letter and number combination assigned to the contract as of the present date; the contract must be active as of the present date. The entity mush also have access to the tier and the tier must be active as of today. The order of preference if the item is on multiple contracts is: local contracts, SP, AS, AD, KI, CO, ES, SD, CC, PPP, TX, ACU, PP
- Nulls: TBD
- Distinct: TBD

### Current_Contracted_Catalog_Number
- Type: `STRING`
- Description: The catalog number for the company that holds the contract matched to as of the present date. Applies to Premier contracts only. This catalog number could be a supplier, business partner, vendor, distributor or manufacturer, whoever is on the contract.
- Nulls: TBD
- Distinct: TBD

### Current_Contracted_Product_Description
- Type: `STRING`
- Description: A brief description of the product on the contract matched to as of the present date
- Nulls: TBD
- Distinct: TBD

### Current_Contracted_Supplier_Parent
- Type: `STRING`
- Description: The top parent name of the company that holds the contract matched to as of the present date. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: TBD
- Distinct: TBD

### Current_Price_Activated_Each_Price
- Type: `STRING`
- Description: The price per each on the contract matched to as of the present date
- Nulls: TBD
- Distinct: TBD

### Current_Price_Activated_Effective_Date
- Type: `STRING`
- Description: The date the price activation of the contract matched to as of the present date starts
- Nulls: TBD
- Distinct: TBD

### Current_Price_Activated_Package_Price
- Type: `STRING`
- Description: The price per unit on the contract matched to as of the present date
- Nulls: TBD
- Distinct: TBD

### Current_Price_Activated_Pkg_Uom
- Type: `STRING`
- Description: The unit of measure description of the package type on the contract matched to as of the present date (case, box, carton)
- Nulls: TBD
- Distinct: TBD

### Current_Price_Activated_Tier_Description
- Type: `STRING`
- Description: Brief description of the tier the facility price activated or signed via the member designation form. This price activation is as of the present date.
- Nulls: TBD
- Distinct: TBD

### Current_Price_Activated_Uom_Conv
- Type: `STRING`
- Description: The number of individual products in a package as cleansed by Premier on the contract matched to as of the present date
- Nulls: TBD
- Distinct: TBD

### Current_Spend_Type
- Type: `STRING`
- Description: This field indicates the status of products purchased as of the current date. Categorized Spend includes products undergoing data cleansing or containing incomplete or incorrect information. On Contract Spend (PA Op) refers to products on a Premier or local contract that do not yet have a completed price activation or fully executed PMDF. On Contract means the products are on a Premier, local, or regional contract and are included on a completed price activation, have a fully executed PMDF, or do not require one to access base pricing. Non Contract applies to products purchased without a contract and that have no functional equivalent on a national contract. Off Contract indicates that the products were purchased without a contract, but a functional equivalent is available on a national contract.
- Nulls: TBD
- Distinct: TBD

### Custom_Product
- Type: `STRING`
- Description: Non-standard product customized for specific members that is not reflected on Premier's contract price lists or cross references.
- Nulls: TBD
- Distinct: TBD

### Data_Cleansing_Code
- Type: `STRING`
- Description: Current state of the cleansing process:In Process - Product is in the reviewing process. Matched - Product has been matched. No Match - Product has been reviewed and was unable to find match
- Nulls: TBD
- Distinct: TBD

### Data_Cleansing_Status
- Type: `STRING`
- Description: Coding to distinguish the cleansing status for a product: UNWR - Unworkable, UNCL - Un-cleansable, PCLN - Premier matched, NSUB - Not submitted for cleansing, SBSL - Submitted for cleansing, OPR - Orphan
- Nulls: TBD
- Distinct: TBD

### Department_Key
- Type: `STRING`
- Description: Unique key for the department
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Entity_Code
- Type: `STRING`
- Description: The entity code for the top direct parent reporting the data. This is the direct parent closest to the top parent. If there are other direct parents under the top direct parent, they will be considered facilities in this report.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_1_Entity_Code
- Type: `STRING`
- Description: Field refers to the highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. This would the GPO top parent.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_1_Name
- Type: `STRING`
- Description: Field refers to the highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. This would the GPO top parent.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_1_Premier_Relation
- Type: `STRING`
- Description: Field refers to the highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. This would the GPO top parent.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_2_Entity_Code
- Type: `STRING`
- Description: Field refers to the 2nd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L1 entity is the lowest reporting level, L2 will be the same as L1.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_2_Name
- Type: `STRING`
- Description: Field refers to the 2nd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L1 entity is the lowest reporting level, L2 will be the same as L1.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_2_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 2nd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L1 entity is the lowest reporting level, L2 will be the same as L1.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_3_Entity_Code
- Type: `STRING`
- Description: Field refers to the 3rd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L2 entity is the lowest reporting level, L3 will be the same as L2.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_3_Name
- Type: `STRING`
- Description: Field refers to the 3rd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L2 entity is the lowest reporting level, L3 will be the same as L2.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_3_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 3rd highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L2 entity is the lowest reporting level, L3 will be the same as L2.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_4_Entity_Code
- Type: `STRING`
- Description: Field refers to the 4th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L3 entity is the lowest reporting level, L4 will be the same as L3.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_4_Name
- Type: `STRING`
- Description: Field refers to the 4th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L3 entity is the lowest reporting level, L4 will be the same as L3.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_4_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 4th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L3 entity is the lowest reporting level, L4 will be the same as L3.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_5_Entity_Code
- Type: `STRING`
- Description: Field refers to the 5th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L4 entity is the lowest reporting level, L5 will be the same as L4.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_5_Name
- Type: `STRING`
- Description: Field refers to the 5th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L4 entity is the lowest reporting level, L5 will be the same as L4.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Level_5_Premier_Relation
- Type: `STRING`
- Description: Field refers to the 5th highest reporting level of an organization, which may be an Aggregation Affiliate or Sponsor (such as Acurity or Yankee), health system corporate parent, hospital, or facility. If the L4 entity is the lowest reporting level, L5 will be the same as L4.
- Nulls: TBD
- Distinct: TBD

### Direct_Parent_Name
- Type: `STRING`
- Description: The name for the top direct parent reporting the data. This is the direct parent closest to the top parent. If there are other direct parents under the top direct parent, they will be considered facilities in this report.
- Nulls: TBD
- Distinct: TBD

### Distributor_Key
- Type: `STRING`
- Description: Unique identifier for the distributor
- Nulls: TBD
- Distinct: TBD

### Distributor_Markup_Percent
- Type: `STRING`
- Description: The markup percentage applied to transactions based on the submitted facility distributor. The distributor markup % can be positive or negative.
- Nulls: TBD
- Distinct: TBD

### Distributor_Tp_Key
- Type: `STRING`
- Description: Unique identifier for the distributor top parent
- Nulls: TBD
- Distinct: TBD

### Diversity_Type_Id
- Type: `STRING`
- Description: Unique identifier for the diversity type: MIN (Minority Owned), NON (Non Diverse), VET (Veteran Owned), WOMEN (Women Owned), SMALL BUS (Small Business Owned)
- Nulls: TBD
- Distinct: TBD

### Equivalent_On_Contract
- Type: `STRING`
- Description: Flag noting if an equivalent product as defined by Premier's cross reference information is available on a PP agreement on a standard tier as of the present date.
- Nulls: TBD
- Distinct: TBD

### Facility_Address_1
- Type: `STRING`
- Description: The address of the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Address_2
- Type: `STRING`
- Description: The address of the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Base_Price
- Type: `STRING`
- Description: The price paid for the product submitted by the facility without distributor markup applied.
- Nulls: TBD
- Distinct: TBD

### Facility_Code
- Type: `STRING`
- Description: This field is used to help create the flattened hierarchy and is the Premier assigned alpha numeric and numeric code for the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Contract_Name
- Type: `STRING`
- Description: The name of the contract submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Contract_Number
- Type: `STRING`
- Description: The identifying letter and number combination assigned to the contract submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Contract_Price
- Type: `STRING`
- Description: The product price for the contract submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Contract_Type
- Type: `STRING`
- Description: The type of contract submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_1
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_10
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_2
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_3
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_4
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_5
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_6
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_7
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_8
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Custom_Field_9
- Type: `STRING`
- Description: Pass through field which user can submit data untouched by Premier cleansing.
- Nulls: TBD
- Distinct: TBD

### Facility_Dea
- Type: `STRING`
- Description: Drug Enforcement Administration number used to track controlled substances
- Nulls: TBD
- Distinct: TBD

### Facility_Department_Number
- Type: `STRING`
- Description: The identification number for the facility cost center (this data is submitted via the cost center fields when the user submits data to Premier)
- Nulls: TBD
- Distinct: TBD

### Facility_Direct_Parent_Name_1
- Type: `STRING`
- Description: The name for the top direct parent reporting the data. This is the direct parent closest to the top parent.
- Nulls: TBD
- Distinct: TBD

### Facility_Direct_Parent_Name_2
- Type: `STRING`
- Description: The name for the top direct parent reporting the data. This is the direct parent closest to the top parent.
- Nulls: TBD
- Distinct: TBD

### Facility_Landed_Price
- Type: `STRING`
- Description: The price paid for the product submitted by the facility with distributor markup applied. Distributor markup will only be applied if it was submitted into the distributor markup tool.
- Nulls: TBD
- Distinct: TBD

### Facility_Manufacturer_Catalog_Num
- Type: `STRING`
- Description: The identification number for the manufacturer that makes the product submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Manufacturer_Entity_Code
- Type: `STRING`
- Description: The alpha numeric and numeric code for the manufacturer that makes the product submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Manufacturer_Name
- Type: `STRING`
- Description: The name of the manufacturer that makes the product submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Mmis
- Type: `STRING`
- Description: The Materials Management Information System number submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Facility_Name_2
- Type: `STRING`
- Description: The name of the facility reporting the data
- Nulls: TBD
- Distinct: TBD

### Facility_Phone
- Type: `STRING`
- Description: The facility's phone number
- Nulls: TBD
- Distinct: TBD

### Facility_Pkg_Uom
- Type: `STRING`
- Description: The unit of measure description of the package type (case, box, carton) submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Product_Description
- Type: `STRING`
- Description: The description of the product submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Status
- Type: `STRING`
- Description: -
- Nulls: TBD
- Distinct: TBD

### Facility_Submitted_Name
- Type: `STRING`
- Description: The name of the facility reporting the data as submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Top_Parent_Name_2
- Type: `STRING`
- Description: The name for top parent reporting the data.
- Nulls: TBD
- Distinct: TBD

### Facility_Uom_Conv
- Type: `STRING`
- Description: The number of individual products in a package submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Vendor_Catalog_Num
- Type: `STRING`
- Description: The identification number for the company that sells the product submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Vendor_Entity_Code
- Type: `STRING`
- Description: The alpha numeric and numeric code for the company that sells the product submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Facility_Vendor_Name
- Type: `STRING`
- Description: The name of the distributor/vendor that sells the product submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### File_Id
- Type: `STRING`
- Description: A unique identification number assigned by Premier to each file submitted by the facility.
- Nulls: TBD
- Distinct: TBD

### Flame_Retardant_Free
- Type: `STRING`
- Description: Item free of intentionally added flame retardants? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Forecasted_Commitment_Doc_Access
- Type: `STRING`
- Description: The documents or steps required to have access to the contract's pricing (PMDF, price activation, LOP, etc)
- Nulls: TBD
- Distinct: TBD

### Forecasted_Contract_Effective_Date
- Type: `STRING`
- Description: The contract start date of the forecasted contract.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Contract_Expiration_Date
- Type: `STRING`
- Description: The contract end date of the forecasted contract.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Contract_Name
- Type: `STRING`
- Description: The name of the forecasted contract.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Contract_Number
- Type: `STRING`
- Description: The idenfitying letter and number combination assigned to the future contract. The member must have access to the contract and tier for it to show. The contract must be more than thirty days out from expiring and start after the current contract ends or the current contract must be blank. The order of preference if the item is on multiple contracts is the same as the Current Contract logic: Local contracts, SP, AS, AD, KI, CO, ES, SD, CC, PPP, TX, ACU, and PP.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Contracted_Catalog_Number
- Type: `STRING`
- Description: The catalog number for the company that holds the forecasted contract. Applies to Premier contracts only. This catalog number could be a supplier, business partner, vendor, distributor or manufacturer, whoever is on the contract.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Contracted_Product_Description
- Type: `STRING`
- Description: A brief description of the product on the forecasted contract.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Contracted_Supplier_Parent
- Type: `STRING`
- Description: The top parent name of the company that holds the forecasted contract. Could be a supplier, business partner, vendor, distributor or manufacturer
- Nulls: TBD
- Distinct: TBD

### Forecasted_Equivalent_On_Contract
- Type: `STRING`
- Description: Flag noting if an equivalent product as defined by Premier's cross reference information is available on a PP agreement on a futre standard tier. The contract the item is on must be more than thirty days out from expiring.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Price_Activated_Each_Price
- Type: `STRING`
- Description: The price per each on the forecasted contract.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Price_Activated_Effective_Date
- Type: `STRING`
- Description: The date the price activation of the forecasted contract starts
- Nulls: TBD
- Distinct: TBD

### Forecasted_Price_Activated_Package_Price
- Type: `STRING`
- Description: The price per unit on the forecasted contract
- Nulls: TBD
- Distinct: TBD

### Forecasted_Price_Activated_Pkg_Uom
- Type: `STRING`
- Description: The unit of measure description of the package type on the forecasted contract (case, box, carton)
- Nulls: TBD
- Distinct: TBD

### Forecasted_Price_Activated_Tier_Description
- Type: `STRING`
- Description: The number of individual products in a package as cleansed by Premier on the forecasted contract.
- Nulls: TBD
- Distinct: TBD

### Forecasted_Price_Activated_Uom_Conv
- Type: `STRING`
- Description: The number of individual products in a package as cleansed by Premier on the forecasted contract
- Nulls: TBD
- Distinct: TBD

### Forecasted_Spend_Type
- Type: `STRING`
- Description: Indicates the state of the products purchased on the forecasted contract. Categorized Spend: The products purchased are in the data cleansing review process or products purchased contain incomplete or incorrect information as of the present date. On Contract Spend (PA Op): The pproducts purchased are on a forecasted Premier contract or forecasted local contract that does not have a completed price activation or a fully executed PMDF as of the present date. On Contract: The products purchased are on a forecasted Premier, local and/or regional contract. Products categorized as On Contract are included on a forecasted contract with a completed price activation, fully executed paper member designate form (PMDF), or a PMDF is not required to access base pricing for products to fall into this category. Non Contract: The products purchased did not utilize a forecasted contract and do not have a functional equivalent that is available on a forecasted contract.
- Nulls: TBD
- Distinct: TBD

### Four_Level_Stripe
- Type: `STRING`
- Description: A Product Group Category consists of interrelated items that define the nature of the product. Within this category, Subcategory 1 groups items by their primary function or use. Subcategory 2 narrows it further by clustering similar items based on shared characteristics. Finally, Subcategory 3 delves deeper into more granular product attributes as necessary.
- Nulls: TBD
- Distinct: TBD

### Gtin
- Type: `STRING`
- Description: A globally unique 14-digit number used to identify trade items, products, or services.
- Nulls: TBD
- Distinct: TBD

### Hci_Status
- Type: `STRING`
- Description: Designates the status for a Non-GPO member
- Nulls: TBD
- Distinct: TBD

### Hci_Status_Start_Date
- Type: `STRING`
- Description: Designates the start date for a Non-GPO member
- Nulls: TBD
- Distinct: TBD

### Health_System_Entity_Code
- Type: `STRING`
- Description: The entity code for the top parent reporting the data
- Nulls: TBD
- Distinct: TBD

### Health_System_Entity_Code_Primary
- Type: `STRING`
- Description: Field refers to the entity code of the highest reporting level of an organization, which may be a health system corporate parent, hospital, or facility. Under circumstances where the entity is under an Aggregation Affiliate or Sponsor (such as Acurity or Yankee) in the hierarchy, the Health System Primary would be the health system entity under the Aggregate Affiliate or Sponsor.
- Nulls: TBD
- Distinct: TBD

### Health_System_Name
- Type: `STRING`
- Description: The name for top parent reporting the data
- Nulls: TBD
- Distinct: TBD

### Health_System_Name_Primary
- Type: `STRING`
- Description: The field is intended to the provide easy identification of the highest reporting level of an organization which may be a health system corporate parent, hospital, or facility. Under circumstances where the entity is under an Aggregation Affiliate or Sponsor (such as Acurity or Yankee) in the hierarchy, the Health System Primary would be the health system entity under the Aggregate Affiliate or Sponsor. This is intended to assist in identifying the expected top-level entity for analytic
- Nulls: TBD
- Distinct: TBD

### Health_System_Name_Row_Id
- Type: `STRING`
- Description: IT added field for purpose of partitioning
- Nulls: TBD
- Distinct: TBD

### Hvi_Four_Level_Stripe
- Type: `STRING`
- Description: Specific to the HVI categories, a Product Group Category consists of interrelated items that define the nature of the product. Within this category, Subcategory 1 groups items by their primary function or use. Subcategory 2 narrows it further by clustering similar items based on shared characteristics. Finally, Subcategory 3 delves deeper into more granular product attributes as necessary.
- Nulls: TBD
- Distinct: TBD

### Hvi_Level_2_Category_Code
- Type: `STRING`
- Description: Unique identifier code for High-Value Implant product categorization, Level 2 of Hierarchy
- Nulls: TBD
- Distinct: TBD

### Hvi_Level_3_Category_Code
- Type: `STRING`
- Description: Unique identifier code for High-Value Implant product categorization, Level 3 of Hierarchy
- Nulls: TBD
- Distinct: TBD

### Hvi_Level_4_Category_Code
- Type: `STRING`
- Description: Unique identifier code for High-Value Implant product categorization, Level 4 of Hierarchy
- Nulls: TBD
- Distinct: TBD

### Iec_62474_Substance_Free
- Type: `STRING`
- Description: Item free of substances requiring IEC 62474 disclosure? (Yes/No/NA/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Ingredients_Declared
- Type: `STRING`
- Description: Materials or ingredients fully declared? (Yes, on-pack/Yes, online/Yes, both/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Inner_Pack_Quantity
- Type: `STRING`
- Description: The number of individual products in the inner package. The inner pack quantity is the quantity of the package type within a total package. (E.G. 18 rolls of toilet paper in a case. The case contains 3 packs of 6. The packs are the inner package)
- Nulls: TBD
- Distinct: TBD

### Inner_Pack_Uom
- Type: `STRING`
- Description: The unit of measure description of the inner package type. The inner pack quantity is the quantity of the package type within a total package. (E.G. 18 rolls of toilet paper in a case. The case contains 3 packs of 6. The packs are the inner package)
- Nulls: TBD
- Distinct: TBD

### Last_Base_Each_Price
- Type: `STRING`
- Description: The most recent price paid per unit for the product without distributor markup applied for the selected time frame.
- Nulls: TBD
- Distinct: TBD

### Last_Base_Price
- Type: `STRING`
- Description: The most recent price paid for the product without distributor markup applied for the selected time frame.
- Nulls: TBD
- Distinct: TBD

### Last_Landed_Each_Price
- Type: `STRING`
- Description: The most recent price paid per unit for the product with distributor markup applied for the selected time frame. (mark up is only applied if put into the distributor mark up tool)
- Nulls: TBD
- Distinct: TBD

### Last_Landed_Price
- Type: `STRING`
- Description: The most recent price paid for the product with distributor markup applied for the selected time frame. (mark up is only applied if put into the distributor mark up tool)
- Nulls: TBD
- Distinct: TBD

### Last_Transaction_Date
- Type: `STRING`
- Description: The most recent date on the purchase order/invoice number submitted by the facility for the selected time frame.
- Nulls: TBD
- Distinct: TBD

### Latex_Free
- Type: `STRING`
- Description: Indicates if an item is free of intentionally added Latex. (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Lead_Cadmium_Organitins_Free
- Type: `STRING`
- Description: Item free of intentionally added lead, cadmium and organotins? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Location_Type
- Type: `STRING`
- Description: -
- Nulls: TBD
- Distinct: TBD

### Manufacturer_Diversity_Type
- Type: `STRING`
- Description: Indicates the different types of diversity for Premier's contracted suppliers. Veteran Owned, Women Owned, Non Diverse, Minority Owned, Small Business Owned or Not Applicable
- Nulls: TBD
- Distinct: TBD

### Manufacturer_Entity_Code
- Type: `STRING`
- Description: The Premier assigned alpha numeric and numeric code for the manufacturer that makes the product.
- Nulls: TBD
- Distinct: TBD

### Manufacturer_Top_Parent_Entity_Code
- Type: `STRING`
- Description: The Premier assigned entity code for the parent manufacturer that makes the product
- Nulls: TBD
- Distinct: TBD

### Market_Type
- Type: `STRING`
- Description: Indicates the market type
- Nulls: TBD
- Distinct: TBD

### Matched_Product_Status
- Type: `STRING`
- Description: Indicates if the product match was automatched, matched via CMS (cleansed myspend) or PO Override
- Nulls: TBD
- Distinct: TBD

### Mdf_Date
- Type: `STRING`
- Description: The effective date on the price activation or signed member designation form
- Nulls: TBD
- Distinct: TBD

### Mdf_Each_Price
- Type: `STRING`
- Description: The price per unit as agreed on the price activation or signed member designation form
- Nulls: TBD
- Distinct: TBD

### Mdf_Found
- Type: `STRING`
- Description: A yes/no indicator identifying whether or not a completed price activation or fully executed member designation form was found
- Nulls: TBD
- Distinct: TBD

### Mdf_Price
- Type: `STRING`
- Description: The price paid as agreed on the price activation or signed member designation form. MDF Each Price * Contract UOM Conv
- Nulls: TBD
- Distinct: TBD

### Mdf_Required
- Type: `STRING`
- Description: A yes/no indicator identifying if a price activation or signed member designation form is required for access to base price
- Nulls: TBD
- Distinct: TBD

### Member_City
- Type: `STRING`
- Description: The city where top parent reporting the data locates
- Nulls: TBD
- Distinct: TBD

### Member_Key
- Type: `STRING`
- Description: Unique identifier for the member
- Nulls: TBD
- Distinct: TBD

### Member_Premier_Relation
- Type: `STRING`
- Description: Indicator on how the facility is related to the top parent
- Nulls: TBD
- Distinct: TBD

### Member_Primary_Service
- Type: `STRING`
- Description: The type of service provide by the member
- Nulls: TBD
- Distinct: TBD

### Member_State
- Type: `STRING`
- Description: The State where top parent reporting the data locates
- Nulls: TBD
- Distinct: TBD

### Member_Type
- Type: `STRING`
- Description: Type of member: Acute, Non-Healthcare, Alternate Site
- Nulls: TBD
- Distinct: TBD

### Member_Zip
- Type: `STRING`
- Description: The Zip Code where the member reporting the data locates
- Nulls: TBD
- Distinct: TBD

### Mercury_Free
- Type: `STRING`
- Description: Indicates if an item is free of intentionally added Mercury. (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Month_Key_Lfe
- Type: `STRING`
- Description: The month the invoice/purchase order was submitted by the facility (formatted: YYYYQMM, 2020410)
- Nulls: TBD
- Distinct: TBD

### Multi_Use
- Type: `STRING`
- Description: Item intended to be a multi-use Item? (Yes/No)
- Nulls: TBD
- Distinct: TBD

### Ndc
- Type: `STRING`
- Description: For applicable pharmaceutical products that have an NDC assigned, this field will now be visible in the TSA, in addition to the product catalog number.
- Nulls: TBD
- Distinct: TBD

### Noiseless_Catalog_Number
- Type: `STRING`
- Description: The Manufacturer Catalog Number when available, else the Facility Manufacturer Catalog Number. Noiseless indicates all extra characters have been removed. E.g. - , ( / { ], etc
- Nulls: TBD
- Distinct: TBD

### Obsolete_Date
- Type: `STRING`
- Description: The date the product became obsolete
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_10th_Percentile
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark 10th percentile price) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_10th_Percentile_6_Month
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark 10th percentile price 6 month) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_25th_Percentile
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark 25th percentile Price) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_25th_Percentile_6_Month
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark 25th percentile Price 6 month) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_High
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark High Price) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_High_6_Month
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark High Price 6 month) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_Low
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark Low Price) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_Low_6_Month
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark Low Price 6 month) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_Median
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark Median Price) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Opportunity_To_Benchmark_Median_6_Month
- Type: `STRING`
- Description: (Last Base Each Price - Benchmark Median Price 6 month) * Quantity * UOM Conv Factor
- Nulls: TBD
- Distinct: TBD

### Original_Pin_Number
- Type: `STRING`
- Description: The original Premier assigned product identification number
- Nulls: TBD
- Distinct: TBD

### Other_Epp_Attributes
- Type: `STRING`
- Description: Highlight any other sustainability attributes, especially 3rd party certifications. (Open Text)
- Nulls: TBD
- Distinct: TBD

### Packaging_String
- Type: `STRING`
- Description: The expression of the packaging from the outer UOM to the inner UOM (e.g. 1CA/5BX/20EA)
- Nulls: TBD
- Distinct: TBD

### Paper_Packaging_Fsc_Certified
- Type: `STRING`
- Description: Paper packaging is Forest Stewardship Council (FSC) certified? (Yes/No/Don't Know/NA)
- Nulls: TBD
- Distinct: TBD

### Participation_Type
- Type: `STRING`
- Description: Type of Participation by member: STANDARD, FOOD SERVICE SOLUTIONS, PROVIDER SELECT: MD
- Nulls: TBD
- Distinct: TBD

### Pbt_Free
- Type: `STRING`
- Description: Item free of intentionally added Persistent Bioaccumulative Toxins (PBTs)? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Pfas_Free
- Type: `STRING`
- Description: Item free of perfluorinated compounds? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Phthalates_Free
- Type: `STRING`
- Description: Item free of intentionally added phthalates? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Pin_On_Contract
- Type: `STRING`
- Description: The contracted Premier assigned product identification number
- Nulls: TBD
- Distinct: TBD

### Pkg_Uom_Predicted
- Type: `STRING`
- Description: The newly predicted unit of measure description of the package type (case, box, carton) - with z-score less than 2
- Nulls: TBD
- Distinct: TBD

### Polystyrene_Free
- Type: `STRING`
- Description: Polystyrene free packaging? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Premier_Entity_Code
- Type: `STRING`
- Description: Premier assigned alpha numeric and numeric code for the facility
- Nulls: TBD
- Distinct: TBD

### Premier_Member
- Type: `STRING`
- Description: Indicates if member is active or not
- Nulls: TBD
- Distinct: TBD

### Prim_Pkg_Pc_Recycled
- Type: `STRING`
- Description: Primary packaging contains post-consumer recycled content (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Prim_Pkg_Pc_Recycled_Perc
- Type: `STRING`
- Description: Primary packaging contains post-consumer recycled content (If Yes, provide the percentage as a number. Example 50.) (Do not enter % or other special characters.) (If No, leave blank.) (If Don't Know, leave blank)
- Nulls: TBD
- Distinct: TBD

### Prim_Pkg_Recyclable
- Type: `STRING`
- Description: Primary packaging recyclable? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Prim_Pkg_Recyclable_Perc
- Type: `STRING`
- Description: Primary packaging recyclable? (If Yes, provide the percentage as a number. Example 50.) (Do not enter % or other special characters.) (If No, leave blank.) (If Don't Know, leave blank)
- Nulls: TBD
- Distinct: TBD

### Product_Join_Key_Tsa
- Type: `STRING`
- Description: IT supported keys
- Nulls: TBD
- Distinct: TBD

### Product_Key
- Type: `STRING`
- Description: Unique identifier for a product
- Nulls: TBD
- Distinct: TBD

### Product_Key_Left_Join
- Type: `STRING`
- Description: IT supported keys
- Nulls: TBD
- Distinct: TBD

### Program_Line
- Type: `STRING`
- Description: A descriptor for the kinds of products on the contract (MS – Nursing, MS - Surgical Services, MS – Cardiology, CE – Imaging, LA – Laboratory, CE – Facilities, CE - IT/ Telecom, MS – Distribution, SV - Purchased Services, FS – Chemicals, FS – Food, FS - Non-Foods, FS – Nutritionals, Rx – Hospital, Rx - Wholesaler)
- Nulls: TBD
- Distinct: TBD

### Proprietary_Product
- Type: `STRING`
- Description: Product that only fits a specific manufacturer's device
- Nulls: TBD
- Distinct: TBD

### Pvc_Free
- Type: `STRING`
- Description: Indicates if the item is free of PVC (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Quantity_In_Eaches
- Type: `STRING`
- Description: Quantity * UOM Conv
- Nulls: TBD
- Distinct: TBD

### Record_Number
- Type: `STRING`
- Description: A unique identification number generated by Premier for each transaction within the file id
- Nulls: TBD
- Distinct: TBD

### Recy_Cont_Post_Consumer
- Type: `STRING`
- Description: Item contains post-consumer recycled content? (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Recy_Cont_Post_Consumer_Per
- Type: `STRING`
- Description: Item contains post-consumer recycled content? (If Yes, provide the percentage as a number. Example 50.) (Do not enter % or other special characters.) (If No, leave blank.) (If Don't Know, leave blank)
- Nulls: TBD
- Distinct: TBD

### Recyclable_Content_Percent
- Type: `STRING`
- Description: Item contains recyclable content? (If Yes, provide the percentage as a number. Example 50.) (Do not enter % or other special characters.) (If No, leave blank.) (If Don't Know, leave blank)
- Nulls: TBD
- Distinct: TBD

### Reference_Number
- Type: `STRING`
- Description: A unique identification number generated by Premier to link manufacturer and distributor versions of a product
- Nulls: TBD
- Distinct: TBD

### Reference_Number_Surrogate
- Type: `STRING`
- Description: The Reference Number when present, else a concatenation of the Manufacturer Top Parent Entity Code and Facility Manufacturer Catalog Number
- Nulls: TBD
- Distinct: TBD

### Release_Number
- Type: `STRING`
- Description: Unique number for a PO to differentiate a PO number when duplicative
- Nulls: TBD
- Distinct: TBD

### Replaced_By_Manufacturer_Catalog_Number
- Type: `STRING`
- Description: The manufacturer item# that replaces the manufacturer’s discontinued item. If populated as “no replacement” the manufacturer has confirmed that there is no replacement for the discontinued item.
- Nulls: TBD
- Distinct: TBD

### Reportable_Under
- Type: `STRING`
- Description: Revenue Recovery mapping logic to identify the contract ID under which we would expect the member’s spend to be reported by a supplier.
- Nulls: TBD
- Distinct: TBD

### Reportable_Under_Matched_Rule
- Type: `STRING`
- Description: Level of certaintenty memer spend is matched to "Reportable Under"
- Nulls: TBD
- Distinct: TBD

### Reportable_Under_Pa_Date
- Type: `STRING`
- Description: Revenue Recovery mapping logic to identify the price activation date for the contract under which we would expect the member’s spend to be reported by a supplier.
- Nulls: TBD
- Distinct: TBD

### Reprocessable
- Type: `STRING`
- Description: Item intended to be reprocessable? (Yes/No/NA)
- Nulls: TBD
- Distinct: TBD

### Rohs_Compliant
- Type: `STRING`
- Description: Item compliant with RoHS (Yes/No/NA/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Sec_Pkg_Pc_Recycled
- Type: `STRING`
- Description: Secondary packaging contains post-consumer recycled content (Yes/No/Don't Know)
- Nulls: TBD
- Distinct: TBD

### Sec_Pkg_Pc_Recycled_Perc
- Type: `STRING`
- Description: Secondary packaging contains post-consumer recycled content (If Yes, provide the percentage as a number. Example 50.) (Do not enter % or other special characters.) (If No, leave blank.) (If Don't Know, leave blank)
- Nulls: TBD
- Distinct: TBD

### Shipment
- Type: `STRING`
- Description: Health System provide shipment information included in PO
- Nulls: TBD
- Distinct: TBD

### Signed_Custom_Tier_Description
- Type: `STRING`
- Description: Brief description of the custom tier the facility price activated or signed via the member designation form
- Nulls: TBD
- Distinct: TBD

### Signed_Preferred_Tier_Indicator
- Type: `STRING`
- Description: A yes/no indicator identifying whether or not the signed tier description was designated as the preferred tier by the top parent. This price activation is at the time of the purchase. If a price activation occurred after the transaction, there will be no signed tier description.
- Nulls: TBD
- Distinct: TBD

### Signed_Tier_Description
- Type: `STRING`
- Description: Brief description of the tier the facility price activated or signed via the member designation form. This price activation is at the time of the purchase. If a price activation occurred after the transaction, there will be no signed tier description.
- Nulls: TBD
- Distinct: TBD

### Signed_Tier_Status
- Type: `STRING`
- Description: Progress of the price activation or member designation form. Can be Accepted, Initialed or Pending. This price activation is at the time of the purchase. If a price activation occurred after the transaction, there will be no signed tier description.
- Nulls: TBD
- Distinct: TBD

### Signed_Tier_Status_Date
- Type: `STRING`
- Description: The effective date agreed to by the facility and the contracted supplier. This price activation is at the time of the purchase. If a price activation occurred after the transaction, there will be no signed tier description.
- Nulls: TBD
- Distinct: TBD

### Size
- Type: `STRING`
- Description: A grouping of the type of facility submitting the data according to number of beds. Facilities without beds are labeled as "Non-Acute".
- Nulls: TBD
- Distinct: TBD

### Spend_Period_Yyyyqmm
- Type: `STRING`
- Description: The month key is the YYYYQMM (2018101 = Jan, Q1, 2018) used for blends or joins.
- Nulls: TBD
- Distinct: TBD

### Subcategory
- Type: `STRING`
- Description: Second level of taxonomy in Premier item categorization.
- Nulls: TBD
- Distinct: TBD

### Supplier_Top_Parent
- Type: `STRING`
- Description: The name of the top parent supplier
- Nulls: TBD
- Distinct: TBD

### Third_Party_Non_Val_Id
- Type: `STRING`
- Description: A unique identification number generated by Premier used to support product research
- Nulls: TBD
- Distinct: TBD

### Transaction_Line_Number
- Type: `STRING`
- Description: The number of the line on the purchase order submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Transaction_Number
- Type: `STRING`
- Description: The purchase order identification number submitted by the facility
- Nulls: TBD
- Distinct: TBD

### Txn_Key
- Type: `STRING`
- Description: Internal field for the transaction
- Nulls: TBD
- Distinct: TBD

### Unspsc_Class_Description
- Type: `STRING`
- Description: The standard class description of the purchased product
- Nulls: TBD
- Distinct: TBD

### Unspsc_Commodity_Description
- Type: `STRING`
- Description: The standard commodity description of the purchased product
- Nulls: TBD
- Distinct: TBD

### Unspsc_Family_Code
- Type: `STRING`
- Description: The second level of the United Nations Standard Products and Services Code taxonomy
- Nulls: TBD
- Distinct: TBD

### Unspsc_Family_Description
- Type: `STRING`
- Description: The standard family description of the purchased product
- Nulls: TBD
- Distinct: TBD

### Unspsc_Segment_Description
- Type: `STRING`
- Description: The standard segment description of the purchased product
- Nulls: TBD
- Distinct: TBD

### Uom_Conv_Predicted
- Type: `STRING`
- Description: The newly predicted number of individual products in a package
- Nulls: TBD
- Distinct: TBD

### Update_Date
- Type: `STRING`
- Description: Date this record was updated
- Nulls: TBD
- Distinct: TBD

### Vendor_Hl_Dist_Key
- Type: `STRING`
- Description: Unique identifier for the vendor HI distributor
- Nulls: TBD
- Distinct: TBD

### Vendor_Hl_Mfg_Key
- Type: `STRING`
- Description: Unique identifier for the vendor HI manufacturer
- Nulls: TBD
- Distinct: TBD

### Vendor_Key
- Type: `STRING`
- Description: Unique identifier for the vendor
- Nulls: TBD
- Distinct: TBD

### Vendor_Top_Parent_Entity_Code
- Type: `STRING`
- Description: The Premier assigned entity code for the parent distributor/vendor that sells the product
- Nulls: TBD
- Distinct: TBD

### Vendor_Top_Parent_Name
- Type: `STRING`
- Description: The name of the parent distributor/vendor that sells the product
- Nulls: TBD
- Distinct: TBD

### Water_Efficiency_Attributes
- Type: `STRING`
- Description: Please highlight any water efficiency attributes (reduced water consumption, watersense, auto shut-off etc) (Open text)
- Nulls: TBD
- Distinct: TBD

### Wooden_Parts_Fsc_Certified
- Type: `STRING`
- Description: Wooden parts are Forest Stewardship Council (FSC) certified? (Yes/No/Don't Know/NA)
- Nulls: TBD
- Distinct: TBD

## Data Quality & Notes
- Heavy head distribution across a small set of categories and service lines; long-tail taxonomy values produce high distinct counts.
- Significant NULLs for Brand_Name, HVI levels (≈6–7%), and higher-level product subcategories (up to 38% at subcategory3) indicating classification gaps or non-applicability.
- Negative spend / quantity / price rows reflect credits or adjustments. Recommend excluding negatives for median price benchmarking.
- Large number of contract-related NULLs (access/best price) suggests conditional enrichment pipeline; interpret absence as not-applicable rather than missing in some analyses.
- Outlier code granularity (E1–E7, P, Y) enables more nuanced exclusion than a binary approach.

## Profiling Method Summary
Executed via BigQuery MCP server:
1. Aggregate null + approx distinct query over selected columns.
2. Top-N categorical extraction using ROW_NUMBER partitioned ranking.
3. Quantile distributions (APPROX_QUANTILES) for spend, quantity, unit price.
4. Manual synthesis of descriptions where business definitions absent (marked Inferred).

## Recommended Usage Patterns
1. Price Benchmark: Filter negatives; exclude records where outlier_flag in ('Y','E1','E2','E3','E4','E5','E6','E7').
2. Contract Coverage: Share of Base_Spend with Contract_Price_Found = 'Y'.
3. Category Mix: Track monthly shift using Contract_Category + service_line.
4. Classification Quality: Monitor Brand_Name and product_subcategory* NULL % over time.

(End of dictionary)