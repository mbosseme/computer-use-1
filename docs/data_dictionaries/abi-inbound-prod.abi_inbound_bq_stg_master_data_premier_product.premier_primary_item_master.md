# Data Dictionary: premier_primary_item_master

## Table Details
- **Project**: abi-inbound-prod
- **Dataset**: abi_inbound_bq_stg_master_data_premier_product
- **Table**: premier_primary_item_master

### antibacterial_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,208,862
  - `Y`: 2,828,738
  - `N`: 267,784
  - `None`: 15,367

---

### benchmark_10th_percentile

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15006470
- **Distinct Values**: 99159
- **Top Values**:
  - `None`: 15,006,470
  - `0.07`: 8,471
  - `0.3`: 4,794
  - `1.55`: 4,768
  - `0.22`: 4,449

---

### benchmark_10th_percentile_6_month

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15567006
- **Distinct Values**: 82458
- **Top Values**:
  - `None`: 15,567,006
  - `0.07`: 5,937
  - `1.55`: 5,014
  - `0.06`: 4,373
  - `0.3`: 4,253

---

### benchmark_25th_percentile

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15006478
- **Distinct Values**: 100085
- **Top Values**:
  - `None`: 15,006,478
  - `0.07`: 8,191
  - `0.3`: 5,092
  - `0.05`: 4,907
  - `0.2`: 4,823

---

### benchmark_25th_percentile_6_month

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15567006
- **Distinct Values**: 83095
- **Top Values**:
  - `None`: 15,567,006
  - `0.07`: 7,268
  - `0.24`: 5,080
  - `0.09`: 5,063
  - `0.2`: 5,059

---

### benchmark_high_price

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15006494
- **Distinct Values**: 109804
- **Top Values**:
  - `None`: 15,006,494
  - `100`: 4,225
  - `0.14`: 3,801
  - `2`: 3,667
  - `0.29`: 3,289

---

### benchmark_high_price_6_month

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15567006
- **Distinct Values**: 91080
- **Top Values**:
  - `None`: 15,567,006
  - `0.88`: 3,578
  - `2`: 3,386
  - `1`: 3,197
  - `5`: 3,076

---

### benchmark_low_price

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15006460
- **Distinct Values**: 99423
- **Top Values**:
  - `None`: 15,006,460
  - `0.07`: 7,591
  - `0.01`: 6,118
  - `0.385`: 5,569
  - `91.15`: 5,007

---

### benchmark_low_price_6_month

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15567006
- **Distinct Values**: 82227
- **Top Values**:
  - `None`: 15,567,006
  - `0.07`: 6,742
  - `0.01`: 5,062
  - `0.385`: 4,675
  - `0.76`: 4,212

---

### benchmark_median_price

- **Description**: The median price paid for this item across the dataset.
- **Usage Note**: This is the PRIMARY benchmark to start with. If this is NULL, other benchmarks are likely NULL as well.
- **Data Type**: FLOAT
- **Nulls**: 15006447
- **Distinct Values**: 114921
- **Top Values**:
  - `None`: 15,006,447
  - `0.15`: 5,914
  - `0.24`: 5,883
  - `0.07`: 5,663
  - `0.09`: 4,956

---

### benchmark_median_price_6_month

- **Description**: TBD
- **Data Type**: FLOAT
- **Nulls**: 15567006
- **Distinct Values**: 93907
- **Top Values**:
  - `None`: 15,567,006
  - `0.24`: 5,752
  - `0.15`: 5,605
  - `0.09`: 4,960
  - `0.5`: 4,586

---

### bisphenol_a_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15260
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 15,801,730
  - `Y`: 3,213,870
  - `N`: 289,891
  - `None`: 15,260

---

### brand_name

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 7597736
- **Distinct Values**: 124143
- **Top Values**:
  - `None`: 7,597,736
  - `VICRYL`: 75,499
  - `V.MUELLER`: 66,413
  - `MONOJECT`: 62,120
  - `PROLENE`: 51,847

---

### ca_prop_65_warning

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18901341
- **Distinct Values**: 399
- **Top Values**:
  - `None`: 18,901,341
  - `THIS PRODUCT CAN EXPOSE YOU TO CHEMICALS INCLUDING ETHYLENE OXIDE WHICH IS KNOWN TO THE STATE OF CALIFORNIA TO CAUSE CANCER AND/OR BIRTH DEFECTS OR OTHER REPRODUCTIVE HARM.  FOR MORE INFORMAITON, GO TO WWW.P65WARNINGS.CA.GOV`: 43,884
  - `CANCER AND REPRODUCTIVE HARM`: 32,597
  - `LETTER AND WEBSITE USED`: 24,729
  - `117-81-7`: 22,826

---

### ca_prop_65_warning_required

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 15,877,659
  - `N`: 2,946,784
  - `Y`: 480,941
  - `None`: 15,367

---

### company_id

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 19514
- **Top Values**:
  - `IL2114`: 1,097,231
  - `IL5027`: 1,057,831
  - `VA2021`: 984,574
  - `VA2023`: 916,037
  - `606847`: 514,621

---

### cons_friendly_pkg_label

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,537,823
  - `N`: 1,684,844
  - `Y`: 1,082,717
  - `None`: 15,367

---

### cont_prop_65_below_thresh_det

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19201658
- **Distinct Values**: 86
- **Top Values**:
  - `None`: 19,201,658
  - `NO`: 47,579
  - `BPA`: 11,826
  - `TOLUENE DIISOCYANATE`: 10,118
  - `CONTAINS CA PROP 65 LISTED CHEMICALS AT EXPOSURE LEVELS WHICH DO NOT REQUIRE A WARNING LABEL`: 8,268

---

### cont_prop_65_below_threshold

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,510,833
  - `N`: 2,544,800
  - `Y`: 249,751
  - `None`: 15,367

---

### contract_category_key

- **Description**: TBD
- **Data Type**: INTEGER
- **Nulls**: 50339
- **Distinct Values**: 736
- **Top Values**:
  - `950`: 1,528,145
  - `596`: 833,835
  - `1067`: 626,483
  - `787`: 616,760
  - `941`: 499,897

---

### contract_id

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18169277
- **Distinct Values**: 14345
- **Top Values**:
  - `None`: 18,169,277
  - `PP-FA-2016`: 37,834
  - `PP-DI-2205`: 20,212
  - `PP-FA-2158`: 17,614
  - `PP-OR-2481,AD-OR-2481`: 15,781

---

### contracted

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15215317
- **Distinct Values**: 1
- **Top Values**:
  - `None`: 15,215,317
  - `Y`: 4,105,434

---

### description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 6
- **Distinct Values**: 4933446
- **Top Values**:
  - `STRIP URINALYSIS TEST REAGENT F/BILIRUBIN BLOOD GLUCOSE KETONE LEUKOCYTE NITRITE PH PROTEIN UROBILINOGEN MULTISTIX URISTIX LATEX-FREE MERCURY-FREE DISPOSABLE 100/PK`: 3,576
  - `STRIP MONITOR TEST ACCU-CHEK INFORM II F2 POC 1-CODE KEY SOLID INSOLUABLE BLOOD GLUCOSE 36/CA`: 3,365
  - `STRIP CHEMISTRY TEST SURESTEP GLUCOSE 2-LEVEL LOW/HIGH F/DBM TEST COMMONWEALTH 50/BX`: 2,836
  - `CUP DRINKING J CUP HOT/COLD 3.2IN TOP 2IN BASE 3.5IN 8OZ WHITE STYROFOAM EXPANDED POLYSTYRENE INSULATED W/ADJUSTABLE CHROME DISPENSER CFC-FREE DISPOSABLE`: 2,510
  - `PAPER MONITORING/RECORDING CHART PREMIUM THERMAL BLACK WHITE GRID DIGITAL VIDEO IMAGING TYPE V SIZE A6 110MM X 18M ROLL F/SONY UP-895MD PRINTER 10RL/BX CARDINAL HEALTH HIGH-DENSITY/GLOSS`: 2,485

---

### description_100

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 5989572
- **Distinct Values**: 2343712
- **Top Values**:
  - `None`: 5,989,572
  - `STRIP MULTISTIX 100TST PLST F/GLU BILI KETON SLD`: 3,576
  - `CHAIR MED FACILITY DINING 23.5X37X23.5IN 20X19.5X18IN SEAT 26IN ARM WOOD POLYMER FOAM 250LB CAP`: 3,451
  - `STRIP MONITOR TEST ACCU-CHEK INFORM II F2 POC 1-CODE KEY SOLID INSOLUABLE BLOOD GLUCOSE 36/CA`: 3,372
  - `STRIP CHEM TEST SURESTEP GLUCOSE 2LVL LOW/HIGH F/DBM TEST COMMONWEALTH 50/BX`: 2,843

---

### discontinued_reason

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18336048
- **Distinct Values**: 604
- **Top Values**:
  - `None`: 18,336,048
  - `VERIFIED FROM CROSS REFERENCE`: 238,657
  - `PCLF VERIFIED FROM CROSS REFERENCE`: 86,501
  - `NDDF/PHARMACY_PRODUCTS OBSOLETE - PREVIOUSLY OVERWRITTEN BY NULL_VALUE IN FUSION`: 84,916
  - `PCLF DEC 2024;VERIFIED FROM CROSS REFERENCE`: 26,310

---

### drug_case_size

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19047656
- **Distinct Values**: 74
- **Top Values**:
  - `None`: 19,047,656
  - `1`: 242,713
  - `10`: 7,392
  - `25`: 3,931
  - `12`: 2,800

---

### drug_form_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19047750
- **Distinct Values**: 5
- **Top Values**:
  - `None`: 19,047,750
  - `EA`: 186,865
  - `ML`: 59,000
  - `GM`: 27,094
  - `NA`: 40

---

### drug_generic_name

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19039275
- **Distinct Values**: 12633
- **Top Values**:
  - `None`: 19,039,275
  - `HYDROCODONE/ACETAMINOPHEN`: 3,102
  - `IBUPROFEN`: 2,951
  - `ACETAMINOPHEN`: 2,942
  - `GABAPENTIN`: 1,940

---

### drug_labeler_id

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19047744
- **Distinct Values**: 2693
- **Top Values**:
  - `None`: 19,047,744
  - `A54569`: 8,725
  - `A63629`: 7,110
  - `B55289`: 5,824
  - `A49999`: 4,652

---

### drug_package_size

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19031172
- **Distinct Values**: 1058
- **Top Values**:
  - `None`: 19,031,172
  - `100`: 47,700
  - `1`: 31,818
  - `30`: 29,616
  - `60`: 15,380

---

### drug_product_wac_price

- **Description**: Wholesale Acquisition Cost (List Price).
- **Usage Note**: This is the SECONDARY pricing fallback for drugs. Check this if `benchmark_median_price` is NULL.
- **Data Type**: STRING
- **Nulls**: 18655080
- **Distinct Values**: 39685
- **Top Values**:
  - `None`: 18,655,080
  - `0`: 28,440
  - `.00`: 11,693
  - `15.00`: 2,232
  - `30.00`: 1,900

---

### drug_unit_of_use

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19048389
- **Distinct Values**: 3
- **Top Values**:
  - `None`: 19,048,389
  - `0`: 269,224
  - `1`: 3,098
  - `N`: 40

---

### energy_efficient

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 13263
- **Distinct Values**: 2
- **Top Values**:
  - `U`: 19,304,604
  - `None`: 13,263
  - `N`: 2,884

---

### epp_indicator

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15261
- **Distinct Values**: 2
- **Top Values**:
  - `N`: 15,459,609
  - `Y`: 3,845,881
  - `None`: 15,261

---

### flame_retardant_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,419,349
  - `Y`: 2,602,083
  - `N`: 283,952
  - `None`: 15,367

---

### gtin

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### hcpcs_description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### hcpcs_number

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 6972204
- **Distinct Values**: 768
- **Top Values**:
  - `None`: 6,972,204
  - `A9270`: 3,490,588
  - `A4649`: 2,505,541
  - `C1713`: 713,551
  - `C1776`: 302,696

---

### hvi_level_2_category_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### hvi_level_2_category_description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### hvi_level_3_category_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### hvi_level_3_category_description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### hvi_level_4_category_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### hvi_level_4_category_description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### iec_62474_substance_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 18,451,985
  - `Y`: 732,405
  - `N`: 120,994
  - `None`: 15,367

---

### ingredients_declared

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 17073163
- **Distinct Values**: 26
- **Top Values**:
  - `None`: 17,073,163
  - `NO`: 1,353,515
  - `YES, BOTH`: 194,399
  - `YES, ONLINE`: 183,145
  - `YES, ON-PACK`: 156,866

---

### inner_pack_uom_quantity

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 4407621
- **Distinct Values**: 1826
- **Top Values**:
  - `1`: 10,363,817
  - `None`: 4,407,621
  - `10`: 516,885
  - `100`: 427,598
  - `12`: 417,680

---

### insert_date_time

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 6167
- **Top Values**:
  - `2006-04-08 00:00:00`: 1,803,407
  - `2006-07-18 00:00:00`: 494,378
  - `2018-08-24 00:00:00`: 118,458
  - `2014-07-29 00:00:00`: 102,387
  - `2011-12-11 00:00:00`: 91,651

---

### inserted_by_file_id

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 65388
- **Distinct Values**: 68150
- **Top Values**:
  - ` 0`: 1,813,846
  - ` 1574`: 873,970
  - ` 61757`: 114,992
  - ` 111990`: 101,881
  - ` 439599`: 82,162

---

### is_berry_compliant

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 13036
- **Distinct Values**: 2
- **Top Values**:
  - `U`: 19,307,494
  - `None`: 13,036
  - `Y`: 221

---

### is_custom

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18606
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 17,583,580
  - `N`: 1,139,861
  - `Y`: 578,704
  - `None`: 18,606

---

### is_proprietary

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 63928
- **Distinct Values**: 2
- **Top Values**:
  - `U`: 19,247,358
  - `None`: 63,928
  - `Y`: 9,465

---

### item_type

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 5165099
- **Distinct Values**: 6491
- **Top Values**:
  - `None`: 5,165,099
  - `SURGICAL`: 892,613
  - `SPINAL`: 552,315
  - `ABSORBABLE`: 319,918
  - `BONE`: 314,395

---

### kit_set_pack_tray

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 17306033
- **Distinct Values**: 106
- **Top Values**:
  - `None`: 17,306,033
  - `KIT`: 714,490
  - `SET`: 491,141
  - `PACK`: 344,027
  - `SYSTEM`: 185,021

---

### latex_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 12665
- **Distinct Values**: 4
- **Top Values**:
  - `U`: 15,477,352
  - `Y`: 3,443,301
  - `N`: 387,372
  - `None`: 12,665
  - `1`: 61

---

### lead_cadmium_organitins_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,285,274
  - `Y`: 2,780,604
  - `N`: 239,506
  - `None`: 15,367

---

### man_dist

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19048811
- **Distinct Values**: 2717
- **Top Values**:
  - `None`: 19,048,811
  - `A-S MEDICATION`: 8,714
  - `BRYANT RANCH PR`: 7,110
  - `PD-RX PHARM`: 5,824
  - `QUALITY CARE`: 4,652

---

### manufacturer_assn_pin

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 153891
- **Distinct Values**: 7503707
- **Top Values**:
  - `None`: 153,891
  - `49417636`: 1,192
  - `48200583`: 820
  - `48200585`: 742
  - `48200584`: 732

---

### manufacturer_catalog_number

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 7806235
- **Top Values**:
  - `UPP-110HG`: 435
  - `4951`: 407
  - `3033`: 360
  - `R1547`: 344
  - `UPC-510`: 315

---

### manufacturer_name

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 44
- **Distinct Values**: 19436
- **Top Values**:
  - `MEDLINE INDUSTRIES, LP`: 1,097,231
  - `CARDINAL HEALTH 200, LLC`: 1,057,831
  - `MCKESSON MEDICAL-SURGICAL INC.`: 984,574
  - `OWENS & MINOR DISTRIBUTION, INC.`: 916,037
  - `HENRY SCHEIN, INC.`: 514,621

---

### manufacturer_product_description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 6060811
- **Distinct Values**: 5652059
- **Top Values**:
  - `None`: 6,060,811
  - `.`: 45,763
  - `EPACK KIT`: 2,767
  - `GEN4 DIRECT ACCESS`: 2,424
  - `WIPE STERILIZATION 4.4INW X 8.4INL 1-PLY ABSORBENT SOFT EXTRA LOW LINT WHITE F/DELICATE TASK KIMWIPES LATEX-FREE DISPOSABLE`: 2,074

---

### mercury_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 13263
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,068,792
  - `Y`: 3,129,209
  - `N`: 109,487
  - `None`: 13,263

---

### multi_use

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 15,707,164
  - `N`: 3,013,637
  - `Y`: 584,583
  - `None`: 15,367

---

### ndc

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18447229
- **Distinct Values**: 240392
- **Top Values**:
  - `None`: 18,447,229
  - `00000000000`: 7,317
  - `00407141348`: 2,477
  - `00990713909`: 580
  - `00409317802`: 341

---

### ndc_configuration_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19032052
- **Distinct Values**: 10
- **Top Values**:
  - `None`: 19,032,052
  - `2`: 122,030
  - `1`: 61,214
  - `3`: 39,761
  - `4`: 34,349

---

### nddf_functional_alternative_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19032435
- **Distinct Values**: 30865
- **Top Values**:
  - `None`: 19,032,435
  - `888888888888888888888888`: 16,844
  - `999999999999999999999999`: 5,974
  - `H3E001866----500 MGTA100`: 906
  - `S2B003723----200 MGTA100`: 825

---

### nddf_functional_equivalent_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19032428
- **Distinct Values**: 68239
- **Top Values**:
  - `None`: 19,032,428
  - `888888888888888888888888888888888888888888888888`: 16,852
  - `999999999999999999999999999999999999999999999999`: 5,973
  - `M4A002748----------YRM0000000005000011`: 377
  - `H3E001866----500 MGTA10000000010000011`: 219

---

### nddf_skey_dosage_form_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19048226
- **Distinct Values**: 646
- **Top Values**:
  - `None`: 19,048,226
  - `TA`: 95,924
  - `CA`: 23,437
  - `HV`: 14,147
  - `PA`: 12,365

---

### nddf_skey_generic

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19048213
- **Distinct Values**: 10555
- **Top Values**:
  - `None`: 19,048,213
  - `001730`: 3,128
  - `003723`: 2,922
  - `001866`: 2,880
  - `008831`: 1,941

---

### nddf_skey_ps

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19049331
- **Distinct Values**: 1031
- **Top Values**:
  - `None`: 19,049,331
  - `00000100000`: 42,892
  - `00000030000`: 30,404
  - `00000001000`: 23,461
  - `00000060000`: 16,191

---

### nddf_skey_route_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19048209
- **Distinct Values**: 64
- **Top Values**:
  - `None`: 19,048,209
  - `1`: 166,386
  - `M`: 31,351
  - `5`: 19,828
  - `A`: 18,271

---

### nddf_skey_strength_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19067907
- **Distinct Values**: 9262
- **Top Values**:
  - `None`: 19,067,907
  - `10 MG`: 10,845
  - `500 MG`: 8,230
  - `100 MG`: 8,028
  - `20 MG`: 6,903

---

### nddf_skey_thera

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19048241
- **Distinct Values**: 1397
- **Top Values**:
  - `None`: 19,048,241
  - `U6W`: 13,009
  - `S2B`: 7,677
  - `H4B`: 7,063
  - `H3A`: 6,133

---

### nddf_skey_unitdose

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19048249
- **Distinct Values**: 3
- **Top Values**:
  - `None`: 19,048,249
  - `0`: 255,557
  - `1`: 16,924
  - `2`: 21

---

### newline

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 1
- **Top Values**:
  - `
`: 19,320,751

---

### noun

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 5711483
- **Distinct Values**: 3570
- **Top Values**:
  - `None`: 5,711,483
  - `SUTURE`: 622,460
  - `CATHETER`: 598,574
  - `SCREW`: 488,840
  - `TUBE`: 351,183

---

### obsolete_date

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 17241472
- **Distinct Values**: 6476
- **Top Values**:
  - `None`: 17,241,472
  - `2022-11-30 00:00:00`: 94,028
  - `2025-08-07 00:00:00`: 44,846
  - `2023-09-07 00:00:00`: 40,945
  - `2022-12-31 00:00:00`: 38,319

---

### other_epp_attributes

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18787880
- **Distinct Values**: 204
- **Top Values**:
  - `None`: 18,787,880
  - `NA`: 142,657
  - `NONE`: 130,240
  - `PAPER CONTENT SOURCED FROM SUSTAINABLE FOREST RESOURCES, HOWEVER FSC LOGO IS NOT DISPLAYED IN THE BOX.`: 54,864
  - `N/A`: 48,690

---

### packaging_string

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 4840379
- **Distinct Values**: 12879
- **Top Values**:
  - `1EA`: 5,583,468
  - `None`: 4,840,379
  - `1CA/10EA`: 277,234
  - `1CA/12EA`: 273,223
  - `1BX/10EA`: 264,372

---

### paper_packaging_fsc_certified

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 17,264,558
  - `N`: 1,768,776
  - `Y`: 272,050
  - `None`: 15,367

---

### part_number_compressed

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 7136901
- **Top Values**:
  - `UPC510`: 975
  - `UPP110HG`: 950
  - `UPP110HD`: 795
  - `UPP210HD`: 580
  - `UPC21L`: 435

---

### pbt_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,460,503
  - `Y`: 2,573,953
  - `N`: 270,928
  - `None`: 15,367

---

### pediatric

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### pediatric_indicator

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 13036
- **Distinct Values**: 2
- **Top Values**:
  - `U`: 19,136,043
  - `Y`: 171,672
  - `None`: 13,036

---

### pfas_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,262,804
  - `Y`: 2,730,389
  - `N`: 312,191
  - `None`: 15,367

---

### phthalates_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 15,788,968
  - `Y`: 3,222,283
  - `N`: 294,133
  - `None`: 15,367

---

### pkg_uom

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 98
- **Top Values**:
  - `EA`: 11,322,666
  - `CA`: 2,639,715
  - `BX`: 1,785,376
  - `PK`: 1,025,101
  - `BO`: 331,226

---

### polystyrene_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,607,959
  - `Y`: 2,315,375
  - `N`: 382,050
  - `None`: 15,367

---

### premier_benchmark_average

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 12131585
- **Distinct Values**: 115541
- **Top Values**:
  - `None`: 12,131,585
  - `.15`: 11,293
  - `.07`: 11,093
  - `.24`: 10,903
  - `.09`: 9,452

---

### premier_item_number

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 16495528
- **Top Values**:
  - `9999800`: 2
  - `9998783`: 2
  - `9997770`: 2
  - `9989092`: 2
  - `99862`: 2

---

### prim_pkg_pc_recycled

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,209,338
  - `N`: 2,742,019
  - `Y`: 354,027
  - `None`: 15,367

---

### prim_pkg_pc_recycled_perc

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 44
- **Top Values**:
  - `0.00`: 19,005,219
  - `10.00`: 65,184
  - `35.00`: 57,806
  - `100.00`: 34,212
  - `60.00`: 31,175

---

### prim_pkg_recyclable

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,211,457
  - `N`: 1,872,198
  - `Y`: 1,221,729
  - `None`: 15,367

---

### prim_pkg_recyclable_perc

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 570
- **Top Values**:
  - `0.00`: 18,347,296
  - `100.00`: 629,507
  - `50.00`: 167,936
  - `10.00`: 48,086
  - `90.00`: 15,462

---

### primary_product_image_filepath

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19320751
- **Distinct Values**: 0
- **Top Values**:
  - `None`: 19,320,751

---

### product_contract_category

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 50339
- **Distinct Values**: 736
- **Top Values**:
  - `PHARMACEUTICAL`: 1,528,145
  - `SPINAL IMPLANTS AND RELATED PRODUCTS`: 833,835
  - `SURGICAL INSTRUMENTS`: 626,483
  - `SUTURE PRODUCTS`: 616,760
  - `GENERAL ORTHOPEDIC TRAUMA PRODUCTS`: 499,897

---

### product_description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 6
- **Distinct Values**: 4933446
- **Top Values**:
  - `STRIP URINALYSIS TEST REAGENT F/BILIRUBIN BLOOD GLUCOSE KETONE LEUKOCYTE NITRITE PH PROTEIN UROBILINOGEN MULTISTIX URISTIX LATEX-FREE MERCURY-FREE DISPOSABLE 100/PK`: 3,576
  - `STRIP MONITOR TEST ACCU-CHEK INFORM II F2 POC 1-CODE KEY SOLID INSOLUABLE BLOOD GLUCOSE 36/CA`: 3,365
  - `STRIP CHEMISTRY TEST SURESTEP GLUCOSE 2-LEVEL LOW/HIGH F/DBM TEST COMMONWEALTH 50/BX`: 2,836
  - `CUP DRINKING J CUP HOT/COLD 3.2IN TOP 2IN BASE 3.5IN 8OZ WHITE STYROFOAM EXPANDED POLYSTYRENE INSULATED W/ADJUSTABLE CHROME DISPENSER CFC-FREE DISPOSABLE`: 2,510
  - `PAPER MONITORING/RECORDING CHART PREMIUM THERMAL BLACK WHITE GRID DIGITAL VIDEO IMAGING TYPE V SIZE A6 110MM X 18M ROLL F/SONY UP-895MD PRINTER 10RL/BX CARDINAL HEALTH HIGH-DENSITY/GLOSS`: 2,485

---

### product_group_category

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 8771904
- **Distinct Values**: 2657
- **Top Values**:
  - `None`: 8,771,904
  - `available in commercial applications only`: 1,834,724
  - `SURGICAL INSTRUMENTS - SURGICAL GRADE`: 506,419
  - `CUSTOM TRAY - SURGICAL`: 281,508
  - `SUTURES - ABSORBABLE`: 253,357

---

### product_id

- **Description**: TBD
- **Data Type**: INTEGER
- **Nulls**: 0
- **Distinct Values**: 16433544
- **Top Values**:
  - `9999963`: 2
  - `9999686`: 2
  - `9999621`: 2
  - `9999312`: 2
  - `9999276`: 2

---

### product_subcategory1

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 9086334
- **Distinct Values**: 11136
- **Top Values**:
  - `None`: 9,086,334
  - `available in commercial applications only`: 1,834,724
  - `BRAIDED`: 243,972
  - `MONOFILAMENT`: 239,374
  - `POWDER - FREE`: 155,747

---

### product_subcategory2

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 9763547
- **Distinct Values**: 37329
- **Top Values**:
  - `None`: 9,763,547
  - `available in commercial applications only`: 1,834,724
  - `POLYGLACTIN 910`: 104,498
  - `POLYPROPYLENE`: 69,267
  - `POLYESTER`: 59,036

---

### product_subcategory3

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 11248200
- **Distinct Values**: 34442
- **Top Values**:
  - `None`: 11,248,200
  - `available in commercial applications only`: 1,834,724
  - `SYSTEM SPECIFIC`: 194,849
  - `STERILE`: 107,764
  - `2-0`: 87,819

---

### pvc_free

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 13263
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,060,378
  - `Y`: 2,605,264
  - `N`: 641,846
  - `None`: 13,263

---

### recy_cont_post_consumer

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 15,948,175
  - `N`: 3,296,787
  - `Y`: 60,422
  - `None`: 15,367

---

### recy_cont_post_consumer_per

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 23
- **Top Values**:
  - `0.00`: 19,260,786
  - `None`: 15,367
  - `65.00`: 13,160
  - `10.00`: 11,871
  - `55.00`: 4,371

---

### recyclable

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 13263
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 15,980,792
  - `N`: 3,106,962
  - `Y`: 219,734
  - `None`: 13,263

---

### recyclable_content_percent

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 36
- **Top Values**:
  - `0.00`: 19,117,481
  - `100.00`: 68,580
  - `60.00`: 38,761
  - `35.00`: 24,697
  - `None`: 15,367

---

### reference_number

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 471
- **Distinct Values**: 5422729
- **Top Values**:
  - `51812`: 3,576
  - `7868411`: 3,386
  - `472453`: 2,807
  - `7972759`: 2,560
  - `7947194`: 2,534

---

### replaced_by_item_number

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18552115
- **Distinct Values**: 12591
- **Top Values**:
  - `None`: 18,552,115
  - `NO REPLACEMENT`: 439,796
  - `36488000`: 1,524
  - `82843`: 1,238
  - `901901`: 1,071

---

### reprocessable

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,432,344
  - `N`: 2,706,325
  - `Y`: 166,715
  - `None`: 15,367

---

### rohs_compliant

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 18,086,453
  - `Y`: 845,977
  - `N`: 372,954
  - `None`: 15,367

---

### rx_end_date

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 19286231
- **Distinct Values**: 1102
- **Top Values**:
  - `None`: 19,286,231
  - `2022-06-07 00:00:00`: 1,804
  - `2018-01-12 00:00:00`: 1,762
  - `2016-01-21 00:00:00`: 1,336
  - `2017-10-03 00:00:00`: 1,227

---

### sec_pkg_pc_recycled

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 16,339,893
  - `N`: 2,297,394
  - `Y`: 668,097
  - `None`: 15,367

---

### sec_pkg_pc_recycled_perc

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 48
- **Top Values**:
  - `0.00`: 18,798,108
  - `30.00`: 127,413
  - `35.00`: 74,480
  - `100.00`: 68,901
  - `50.00`: 42,831

---

### source_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 0
- **Distinct Values**: 14
- **Top Values**:
  - `DSA`: 6,741,962
  - `PDC`: 3,069,896
  - `FUSN`: 2,867,393
  - `SL`: 2,063,781
  - `PIM`: 1,875,688

---

### top_parent_entity_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 44
- **Distinct Values**: 16187
- **Top Values**:
  - `OH5010`: 1,662,410
  - `613772`: 1,152,922
  - `IL2114`: 1,147,874
  - `VA2023`: 1,022,684
  - `774585`: 561,994

---

### top_parent_name

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 44
- **Distinct Values**: 16190
- **Top Values**:
  - `CARDINAL HEALTH 414, LLC`: 1,662,410
  - `MCKESSON CORPORATION`: 1,152,922
  - `MEDLINE INDUSTRIES, LP`: 1,147,874
  - `OWENS & MINOR DISTRIBUTION, INC.`: 1,022,684
  - `CONCORDANCE HEALTHCARE SOLUTIONS LLC`: 561,994

---

### total_package_qty

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 79909
- **Distinct Values**: 1732
- **Top Values**:
  - `1`: 12,754,903
  - `10`: 720,098
  - `12`: 667,485
  - `100`: 631,846
  - `50`: 440,577

---

### unspsc_category_code

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 10868
- **Distinct Values**: 14162
- **Top Values**:
  - `ZZ.ZZ.ZZ.ZZ`: 2,260,890
  - `42.31.22.01`: 612,062
  - `42.29.42.11`: 326,339
  - `42.32.16.10`: 307,698
  - `42.32.15.06`: 218,109

---

### unspsc_description

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 2271763
- **Distinct Values**: 14145
- **Top Values**:
  - `None`: 2,271,763
  - `SUTURES`: 612,062
  - `SURGICAL CUSTOM OR SPECIALTY INSTRUMENT OR PROCEDURE SETS`: 326,339
  - `SPINAL SCREWS OR SCREW EXTENSIONS`: 307,698
  - `BONE SCREWS OR PEGS`: 218,109

---

### uom_conv

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 4407621
- **Distinct Values**: 1826
- **Top Values**:
  - `1`: 10,363,817
  - `None`: 4,407,621
  - `10`: 516,885
  - `100`: 427,598
  - `12`: 417,680

---

### vend_type

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 6
- **Distinct Values**: 2
- **Top Values**:
  - `D`: 11,650,206
  - `M`: 7,670,539
  - `None`: 6

---

### water_efficiency_attributes

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 18521052
- **Distinct Values**: 47
- **Top Values**:
  - `None`: 18,521,052
  - `NA`: 404,860
  - `N/A`: 224,050
  - `NONE`: 121,759
  - `DOES NOT USE WATER`: 14,127

---

### wooden_parts_fsc_certified

- **Description**: TBD
- **Data Type**: STRING
- **Nulls**: 15367
- **Distinct Values**: 3
- **Top Values**:
  - `U`: 18,558,259
  - `N`: 686,289
  - `Y`: 60,836
  - `None`: 15,367

---

