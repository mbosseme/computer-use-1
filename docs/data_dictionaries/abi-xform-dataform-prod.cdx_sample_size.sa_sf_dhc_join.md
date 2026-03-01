# Data Dictionary: sa_sf_dhc_join

## Table Metadata

| Property | Value |
|----------|-------|
| **Project** | abi-xform-dataform-prod |
| **Dataset** | cdx_sample_size |
| **Table** | sa_sf_dhc_join |
| **Row Count** | 482,332 |
| **Description** | Crosswalk joining Premier facilities (from Salesforce/SA) with DHC (Definitive Healthcare) attributes. Contains all facility types (not filtered to hospitals). Approximately 1.5% of records have DHC enrichment. |

---

## Column Details

### dhc_hospital_name
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC hospital/facility name from Definitive Healthcare master data |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 7,216 |
| **Sample Values** | Texas Health Harris Methodist Hospital Fort Worth, AdventHealth Orlando |

---

### dhc_hospital_type
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Classification of hospital type (Short Term Acute Care, Critical Access, Psychiatric, etc.) |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 9 |
| **Top Values** | Short Term Acute Care (3,889), Critical Access (1,380), Psychiatric (632), Long Term Acute Care (403), Children's (312), Rehabilitation (286), Veterans (203), Religious Non-Medical Health Care Institutions (150) |

---

### dhc_firm_type
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC classification of facility as Hospital or Health System |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 2 |
| **Top Values** | Hospital (6,781), Health System (530) |

---

### dhc_definitive_id
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Unique Definitive Healthcare identifier for the facility/system |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 7,311 |
| **Sample Values** | Numeric IDs from DHC master database |

---

### dhc_provider_number
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | CMS Provider Number (CCN) assigned by Medicare/Medicaid |
| **Nulls** | 476,089 (98.7%) |
| **Distinct** | 6,086 |
| **Sample Values** | 6-digit CMS provider certification numbers |

---

### dhc_idn
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Integrated Delivery Network name - immediate health system affiliation |
| **Nulls** | 476,355 (98.7%) |
| **Distinct** | 913 |
| **Sample Values** | Health system names the facility directly belongs to |

---

### dhc_idn_parent
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Parent Integrated Delivery Network name - ultimate health system parent |
| **Nulls** | (see distinct below) |
| **Distinct** | ~1,000 |
| **Top Values** | HCA Healthcare (210), Dept of Veterans Affairs (183), Universal Health Services (164), CommonSpirit Health (162), Select Medical (105), Ascension Health (99), Trinity Health (92), LifePoint Health (84), Tenet Healthcare (82), ScionHealth (74) |

---

### dhc_zip_code
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC facility 5-digit ZIP code |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 5,302 |
| **Sample Values** | 5-digit US ZIP codes |

---

### dhc_address
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC facility full street address (line 1) |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 6,641 |

---

### dhc_address1
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC facility alternate/secondary address line |
| **Nulls** | 481,943 (99.9%) |
| **Distinct** | 145 |

---

### dhc_city
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC facility city name |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 3,218 |

---

### dhc_fips_county_code
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Federal Information Processing Standard (FIPS) county code (5-digit: 2-digit state + 3-digit county) |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 2,515 |
| **Sample Values** | 26125, 29095, 49003, 25027, 6097 |

---

### dhc_county
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC facility county name |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 2,514 |

---

### dhc_state
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | DHC facility 2-letter state abbreviation |
| **Nulls** | 475,021 (98.5%) |
| **Distinct** | 56 |
| **Top Values** | TX (704), CA (505), FL (342), NY (288), OH (260), PA (256), IL (235), MI (202) |

---

### dhc_number_of_staffed_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Number of staffed beds at the facility (beds ready for patient use) |
| **Nulls** | 475,510 (98.6%) |
| **Distinct** | 951 |
| **Stats** | Avg: 240, Min: 1, Max: 41,234 |

---

### dhc_number_of_discharges
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Annual number of patient discharges (stored as string, may contain formatted numbers) |
| **Nulls** | 476,264 (98.7%) |
| **Distinct** | 4,194 |

---

### dhc_net_patient_revenue
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Annual net patient revenue in dollars (stored as string, may contain formatted currency) |
| **Nulls** | 476,371 (98.8%) |
| **Distinct** | 5,884 |

---

### dhc_average_length_of_stay
| Property | Value |
|----------|-------|
| **Type** | FLOAT |
| **Description** | Average patient length of stay in days |
| **Nulls** | 476,261 (98.7%) |
| **Stats** | Avg: 18.0 days |

---

### dhc_bed_utilization_rate
| Property | Value |
|----------|-------|
| **Type** | FLOAT |
| **Description** | Bed utilization rate as decimal (0.0-1.0) representing percentage of beds occupied |
| **Nulls** | 476,262 (98.7%) |
| **Stats** | Avg: 0.508 (50.8%) |

---

### dhc_total_acute_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Total acute care beds (general medical/surgical beds) |
| **Nulls** | 476,262 (98.7%) |
| **Distinct** | 933 |

---

### dhc_total_other_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Total non-acute beds (LTC, rehab, psych, etc.) |
| **Nulls** | 480,125 (99.5%) |
| **Distinct** | 300 |

---

### dhc_subcomponent_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Beds in hospital subcomponent units |
| **Nulls** | 482,300 (99.99%) |
| **Distinct** | 19 |

---

### dhc_skilled_nursing_facility_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Skilled nursing facility (SNF) beds within the hospital |
| **Nulls** | 481,628 (99.9%) |
| **Distinct** | 198 |

---

### dhc_payor_mix_medicare
| Property | Value |
|----------|-------|
| **Type** | FLOAT |
| **Description** | Medicare payor mix as decimal (0.0-1.0) representing percentage of patients with Medicare |
| **Nulls** | 476,353 (98.8%) |
| **Stats** | Avg: 0.293 (29.3%) |

---

### dhc_nursing_facility_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Nursing facility beds (distinct from skilled nursing) |
| **Nulls** | 482,278 (99.99%) |
| **Distinct** | 32 |

---

### dhc_other_long_term_care_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Other long-term care beds not classified elsewhere |
| **Nulls** | 482,185 (99.97%) |
| **Distinct** | 75 |

---

### dhc_hospice_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Hospice/palliative care beds |
| **Nulls** | 482,218 (99.98%) |
| **Distinct** | 26 |

---

### dhc_other_special_care_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Other specialty care beds not classified in specific ICU categories |
| **Nulls** | 482,059 (99.94%) |
| **Distinct** | 80 |

---

### dhc_rehabilitation_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Inpatient rehabilitation unit beds |
| **Nulls** | 481,257 (99.8%) |
| **Distinct** | 118 |

---

### dhc_psychiatric_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Inpatient psychiatric unit beds |
| **Nulls** | 481,182 (99.8%) |
| **Distinct** | 169 |

---

### dhc_detox_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Detoxification intensive care unit beds |
| **Nulls** | 482,321 (99.998%) |
| **Distinct** | 5 |

---

### dhc_trauma_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Trauma ICU beds |
| **Nulls** | 482,300 (99.99%) |
| **Distinct** | 12 |

---

### dhc_psychiatric_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Psychiatric ICU beds |
| **Nulls** | 482,319 (99.997%) |
| **Distinct** | 7 |

---

### dhc_pediatric_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Pediatric ICU (PICU) beds |
| **Nulls** | 482,081 (99.95%) |
| **Distinct** | 52 |

---

### dhc_premature_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Premature infant ICU beds |
| **Nulls** | 482,323 (99.998%) |
| **Distinct** | 5 |

---

### dhc_neonatal_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Neonatal ICU (NICU) beds |
| **Nulls** | 481,036 (99.7%) |
| **Distinct** | 166 |

---

### dhc_surgical_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Surgical ICU (SICU) beds |
| **Nulls** | 482,089 (99.95%) |
| **Distinct** | 59 |

---

### dhc_coronary_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Coronary care unit (CCU) beds |
| **Nulls** | 481,697 (99.87%) |
| **Distinct** | 96 |

---

### dhc_burn_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Burn ICU beds |
| **Nulls** | 482,199 (99.97%) |
| **Distinct** | 24 |

---

### dhc_routine_service_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Routine medical/surgical service beds |
| **Nulls** | 476,273 (98.7%) |
| **Distinct** | 807 |

---

### dhc_medicare_certified_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Number of Medicare-certified beds |
| **Nulls** | 476,150 (98.7%) |
| **Distinct** | 1,061 |

---

### dhc_number__of_licensed_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Total licensed beds (regulatory capacity ceiling) |
| **Nulls** | 477,001 (98.9%) |
| **Distinct** | 718 |

---

### dhc_intensive_care_unit_days
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Annual ICU patient days |
| **Nulls** | 479,018 (99.3%) |
| **Distinct** | 2,762 |

---

### dhc_intensive_care_unit_beds
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Total ICU beds (all types combined) |
| **Nulls** | 478,990 (99.3%) |
| **Distinct** | 253 |

---

### dhc_state_trauma_center
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | State-designated trauma center level |
| **Nulls** | 475,551 (98.6%) |
| **Distinct** | 6 |
| **Top Values** | No (4,692), Level IV (923), Level III (492), Level II (316), Level I (247), Level V (111) |

---

### dhc_acs_trauma_center
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | American College of Surgeons verified trauma center level |
| **Nulls** | 475,551 (98.6%) |
| **Distinct** | 4 |
| **Top Values** | No (6,253), Level II (198), Level I (192), Level III (138) |

---

### facility_entity_code
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier's internal facility entity code identifier |
| **Nulls** | (negligible) |
| **Distinct** | 480,366 |
| **Notes** | Nearly unique per row - primary identifier linking to transaction data |

---

### health_system_name
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier's health system name (often GPO affiliations rather than operating health systems) |
| **Nulls** | (minimal) |
| **Distinct** | ~6,000 |
| **Top Values** | INNOVATIX, LLC NATIONAL HEADQUARTERS (114,666), CNECT (51,525), OMNIA PARTNERS (46,165), PANDION OPTIMIZATION ALLIANCE (35,667), WELLLINK GROUP PURCHASING (20,562), VALUE 4, LLC (19,924), ALLIANT HOLDING (19,372), PREMIER, INC. (14,610), YANKEE ALLIANCE (13,347) |

---

### health_system_entity_code
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier entity code for the health system |
| **Nulls** | 2,043 (0.4%) |
| **Distinct** | 6,264 |

---

### direct_parent_name
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Direct parent organization name in Premier hierarchy |
| **Nulls** | 8,206 (1.7%) |
| **Distinct** | 19,689 |

---

### direct_parent_entity_code
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier entity code for direct parent organization |
| **Nulls** | 8,206 (1.7%) |
| **Distinct** | 20,065 |

---

### facility_name
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier facility name |
| **Nulls** | (minimal) |
| **Distinct** | 395,000+ |

---

### facility_primary_service
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Primary service classification of the facility |
| **Nulls** | (minimal) |
| **Distinct** | 86 |
| **Top Values** | PHYSICIAN(S) (111,345), AMBULATORY CARE CENTER (44,585), BUSINESS AND INDUSTRY (37,628), RETAIL PHARMACY (34,891), HOME HEALTH SERVICES (19,116), EDUCATIONAL INSTITUTION (14,909), GOVERNMENT (14,285), LONG TERM CARE FACILITIES (12,958), AMBULATORY SURGERY CENTER (12,419), CLINIC (11,898), HOSPITAL (8,898), SKILLED NURSING FACILITY (8,547), DISTRIBUTOR (7,938) |

---

### Salesforce_ID
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Salesforce record ID for the account |
| **Nulls** | 472,476 (97.96%) |
| **Distinct** | 9,856 |

---

### Account_Name
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Salesforce account name |
| **Nulls** | 472,476 (97.96%) |
| **Distinct** | 9,763 |

---

### SF_Account_Family
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Salesforce account family grouping (health system affiliation per Premier CRM) |
| **Nulls** | 472,476 (97.96%) |
| **Distinct** | 3,928 |
| **Top Values** | Advocate Health (615), HCA Healthcare (199), CommonSpirit Health (191), Universal Health Services (187), Ascension Health (124), Dept of Veterans Affairs (124), Bon Secours Mercy Health (118), Trinity Health (102) |

---

### Premier_Enterprise_Unit_Roll_Up
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier enterprise unit roll-up grouping for reporting |
| **Nulls** | 477,031 (98.9%) |
| **Distinct** | 119 |

---

### active_membership_type
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Current Premier membership type(s) - comma-separated if multiple |
| **Nulls** | 93,281 (19.3%) |
| **Distinct** | 43 |
| **Top Values** | NATIONAL (218,216), NATIONAL,ACURITY (143,449), NATIONAL,CONDUCTIV CONTRACTS (8,262), NON-GPO (5,664), NATIONAL,ACURITY,CONDUCTIV CONTRACTS (4,153), NATIONAL,ACURITY,CONDUCTIV CONTRACTS,THSCS (3,415) |

---

### SF_Entity_Code
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Salesforce-linked entity code |
| **Nulls** | (minimal) |
| **Distinct** | 8,381 |

---

### SiebelEC
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Legacy Siebel entity code (from former CRM system) |
| **Nulls** | 472,476 (97.96%) |
| **Distinct** | 9,856 |

---

### dhc_id
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Alternate DHC identifier (may differ from dhc_definitive_id) |
| **Nulls** | 475,253 (98.5%) |
| **Distinct** | 7,079 |

---

### member_start_date
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier membership start date (stored as string, format YYYY-MM-DD) |
| **Nulls** | 4,189 (0.9%) |
| **Distinct** | 7,902 |
| **Range** | 1978-07-01 to 2026-04-01 |

---

### member_end_date
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Premier membership end date (null if currently active) |
| **Nulls** | 395,038 (81.9%) |
| **Distinct** | 5,499 |

---

### ascend_start_date
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Ascend program start date |
| **Nulls** | 464,728 (96.4%) |
| **Distinct** | 1,155 |

---

### ascend_end_date
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Ascend program end date |
| **Nulls** | (high null rate expected) |

---

### surpass_start_date
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Surpass program start date |
| **Nulls** | 453,353 (94.0%) |
| **Distinct** | 1,492 |

---

### surpass_end_date
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Surpass program end date |
| **Nulls** | (high null rate expected) |

---

### data_source
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Source of transaction data (ERP vs PO/Receipt/Invoice) |
| **Nulls** | 476,714 (98.8%) |
| **Distinct** | 2 |
| **Top Values** | Blended PO/Receipt/Invoice (5,410), ERP Receipts Only (208) |

---

### total_spend
| Property | Value |
|----------|-------|
| **Type** | FLOAT |
| **Description** | Total spend in dollars (appears to be aggregate at facility level) |
| **Nulls** | 476,714 (98.8%) |
| **Stats** | Avg: $8.68M, Min: -$271,250, Max: $915.5M |
| **Notes** | Negative values may indicate credit/adjustment records |

---

### count_of_transactions
| Property | Value |
|----------|-------|
| **Type** | INTEGER |
| **Description** | Count of transactions for this facility |
| **Nulls** | 476,714 (98.8%) |
| **Stats** | Avg: 10,909, Min: 1, Max: 1,183,345 |

---

### Zip_Code_sa_sf
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | ZIP code from SA/Salesforce data (may include ZIP+4 or have formatting variations) |
| **Nulls** | 2,024 (0.4%) |
| **Distinct** | 348,946 |
| **Notes** | High distinct count suggests includes ZIP+4 and/or data quality issues |

---

### State_sa_sf
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | State from SA/Salesforce data |
| **Nulls** | 2,157 (0.4%) |
| **Distinct** | 73 |
| **Notes** | More than 50 distinct may include territories, provinces, or data quality issues |

---

### City_sa_sf
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | City from SA/Salesforce data |
| **Nulls** | 1,998 (0.4%) |
| **Distinct** | 12,535 |

---

### hospital_type_sa_sf
| Property | Value |
|----------|-------|
| **Type** | STRING |
| **Description** | Hospital type classification from SA/Salesforce |
| **Nulls** | 2,002 (0.4%) |
| **Distinct** | 7 |
| **Top Values** | ALTERNATE SITE (345,751), NON-HEALTHCARE (122,649), ACUTE (9,021), OTHER (2,678), NON MEMBER CUSTOMER (227), PROVIDER SELECT (2), DISTRIBUTOR (2) |

---

### premier_gpo_member
| Property | Value |
|----------|-------|
| **Type** | BOOLEAN |
| **Description** | Flag indicating if facility is a Premier GPO member |
| **Nulls** | 0 (0%) |
| **Values** | FALSE (476,499), TRUE (5,833) |

---

### premier_ascend_surpass_member
| Property | Value |
|----------|-------|
| **Type** | BOOLEAN |
| **Description** | Flag indicating if facility participates in Ascend or Surpass programs |
| **Nulls** | 0 (0%) |
| **Values** | FALSE (481,182), TRUE (1,150) |

---

## Notes

1. **DHC Coverage**: Approximately 98.5% of records have NULL values for DHC fields. This means only ~7,300 facilities (1.5%) have been matched to Definitive Healthcare master data.

2. **facility_primary_service Distribution**: The table includes a wide variety of facility types. Only ~8,900 are classified as "HOSPITAL" - most are alternate site providers (physicians, pharmacies, ambulatory care, etc.).

3. **health_system_name vs dhc_idn_parent**: `health_system_name` often contains GPO/network names (Innovatix, CNECT, Omnia) rather than operating health systems, while `dhc_idn_parent` contains true health system affiliations from DHC.

4. **Salesforce Coverage**: Only ~2% of records have Salesforce integration (Salesforce_ID populated).

5. **Membership Dates**: `member_start_date` has excellent coverage (99%+), while `member_end_date` is 82% null (indicating active members).

6. **Spend/Transaction Data**: Only ~5,600 records have spend data populated - these appear to be aggregate facility-level metrics.

---

*Generated: 2026-01-28*
