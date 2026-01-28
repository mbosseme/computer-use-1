# Product Requirements Document (PRD): GE Market Insights Pilot
**Version:** 3.0 (Context-Aware & Schema-Corrected)
**Date:** November 19, 2025
**Target Audience:** Coding Agent (VS Code / BigQuery)

## 1. Executive Summary
We need to generate data artifacts to validate Premier’s visibility into GE’s "Big Capital" equipment (MRI, CT, Patient Monitoring).
**Crucial Context:** The source data (`transaction_analysis_expanded`) is derived from **provider-submitted POs and Invoices**. Coverage of large capital equipment varies by health system (some exclude capital invoices from their data feeds). Therefore, this analysis represents **"Observed Transactional Share,"** not a 100% theoretical market total.

## 2. Data Source & Scope
* **Source Table:** `abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
* **Period of Analysis:** 24 months ending and inclusive of September 2025 (2023-10-01 to 2025-09-30).
* **Privacy Constraint:** Aggregated data only. **NO** `Facility_Name`, `Health_System_Name`, or `Facility_Hin`.

## 3. Domain Logic & Filtering Strategy

### A. Category Selection (The "Bucket" Filter)
Filter records where `Contract_Category` matches the target categories. Since Capital is often uncategorized ("UNKNOWN"), we must also text-mine the `Product_Description`.

* **Primary Filter:** `Contract_Category` LIKE:
    * '%MAGNETIC RESONANCE%' (MRI)
    * '%COMPUTED TOMOGRAPHY%' (CT)
    * '%PHYSIOLOGICAL MONITORING%' (Monitoring)
* **Secondary Filter (Catch-All for Uncategorized Capital):**
    * If `Contract_Category` = 'UNKNOWN' (or NULL), check if `Product_Description` contains "MRI", "CT", "TOMOGRAPHY", "RESONANCE", or "MONITORING" **AND** meets the Price Threshold below.

### B. Capital Identification Logic (The "Big Iron" Heuristic)
Because this data mixes capital with consumables, and lacks a dedicated "Capital" flag, use this tiered logic to isolate Systems:

* **Tier 1: Price Threshold (Strongest Signal)**
    * Filter where `Base_Each_Price` > **$25,000** (Configurable).
    * *Reasoning:* High unit price differentiates a System from a coil or lead wire.
* **Tier 2: The "Unmatched" Proxy**
    * Include rows where `Spend_Type` is 'NON CONTRACT' or 'CATEGORIZED ONLY'.
    * *Context:* Large capital POs often do not match the standard Item Master, resulting in "Non-Contract" status despite being on a GPO agreement.
* **Tier 3: Exclusion Logic (Negative Matching)**
    * **Exclude** rows where `Product_Description` contains:
        * 'SERVICE', 'MAINTENANCE', 'WARRANTY', 'AGREEMENT', 'REPAIR', 'SOFTWARE', 'LICENSE', 'RENEWAL'.

### C. Data Preparation Context
When processing transactions from health systems, we perform multiple levels of matching and enrichment:
1.  **Categorization**: We attempt to assign a Premier standard `Contract_Category` based on manufacturer, vendor, or product description clues.
2.  **Product Matching**: We attempt to match the transaction to a specific product in the Premier Item Master.
    *   *Note*: Heavy capital equipment (CT, MRI) is often not kept in a health system's Item Master (ERP) or Premier's central Item Master, meaning these transactions often lack a specific product match (null Premier reference number).
3.  **Entity Standardization**: We standardize `Manufacturer_Name` (who makes it) and `Vendor_Name` (who sells it). If sold direct, these are the same; if via distribution, the vendor is the distributor.

## 4. Required Artifacts (Output Specifications)

### Artifact 1: The "Validation Mapping" File (CSV)
**Purpose:** To show GE *what* we are catching. By sharing the raw descriptions, we let their analysts see the "PO Text" reality (e.g., "GE SIGNA PREMIER MRI SYS...").
**Granularity:** Manufacturer + SKU + Description.

**Query Fields (Select & Group By):**
1.  `Manufacturer_Name` (Cleaned).
2.  `Manufacturer_Catalog_Number` (If empty/null, replace with "NO_SKU").
3.  `Product_Description` (The raw text is critical here).
4.  `Contract_Category` (To show if it was bucketed or UNKNOWN).

**Metrics:**
* `Total_Observed_Spend`: Sum of `Base_Spend`.
* `Transaction_Count`: Count of rows (Frequency).

**Sorting:** Descending by `Total_Observed_Spend`.

### Artifact 2: The "Observed Trends" Dataset (CSV)
**Purpose:** Source data for the "Executive Snapshot" visualization.
**Naming Convention Change:** Use terms like "Observed Volume" instead of "Market Share" to accurately reflect the data source limitations.
**Granularity:** Manufacturer + Time Period.

**Query Fields:**
1.  **Category:** Derive `Report_Category` ('MRI', 'CT', 'Monitoring').
2.  **Manufacturer:** `Manufacturer_Name` (Normalize: 'GE', 'SIEMENS', 'PHILIPS', 'CANON', 'OTHER').
3.  **Time:** `Year_Quarter` (Extracted from `Transaction_Date`).

**Metrics:**
* `Total_Observed_Spend`: Sum of `Base_Spend`.
* `Share_of_Observed_Spend`: (Percent of total observed spend for that category/quarter).
* `YoY_Growth`: (Calculated vs same quarter previous year).

## 5. Implementation Notes for Coding Agent
1.  **Field Mapping:**
    * Use `Base_Spend` (not `line_total_amount`).
    * Use `Base_Each_Price` for the $25k threshold.
    * Use `Transaction_Date`.
    * Use `Contract_Category`.
2.  **Data Disclaimer:** In the generated CSV filename or header, append `_Provider_Reported_Data` to reinforce that this is the ERP extract view.
3.  **Null Handling:** If `Manufacturer_Catalog_Number` is missing (common in custom capital POs), group by `Product_Description` to ensure we don't lose the row.

## 6. Data Alignment & Exclusion Methodology
To ensure the analysis reflects valid Premier GPO member activity, we align the Provider-Reported data (`transaction_analysis`) with Manufacturer-Reported data (`supplier_spend`).

### A. Parity Comparison Scope
*   **Filters:** Acute facilities only (`Member_Type` / `Facility_Type` = 'ACUTE').
*   **Categories:** CT, MRI, Physiological Monitoring.
*   **Timeframe:** Oct 2023 - Sep 2025.

### B. Facility Exclusion Logic (The "Dark Facility" Filter)
We align the datasets by excluding facilities from the Supplier Spend analysis if they are not reporting transaction data for the same period.

*   **Granularity:** `Premier_Entity_Code` + `Year_Quarter`.
*   **Exclusion Rule:** A `Premier_Entity_Code` is **EXCLUDED** from Supplier Spend for a given quarter if:
    1.  It is **NOT** present as a `Premier_Entity_Code` (Facility) in the Transaction Analysis dataset for that quarter.
    2.  **AND** it is **NOT** present as a `Health_System_Entity_Code` (System Parent) in the Transaction Analysis dataset for that quarter.

*   **Rationale:**
    *   **Condition 1:** Removes facilities that are completely "dark" (no transaction feed).
    *   **Condition 2 (The "System Safety Net"):** Retains records where the supplier reports at the System level (e.g., `OH2062`) and the System is active/reporting, even if the specific System Entity Code doesn't appear as a facility in the transaction feed. This prevents the accidental exclusion of valid System-level volume.
    2.  Sum `Premier_Spend` from Supplier Spend (Manufacturer-Reported).
    3.  Calculate Coverage: `Supplier_Spend / Transaction_Spend`.
*   **Exclusion:** If `Supplier_Spend` is less than **10%** of `Transaction_Spend` for a given Health System in a given Quarter, that Health System's data for that Quarter is **excluded** from the final analysis.
*   **Rationale:** A low ratio indicates the Health System is likely not a Premier GPO member for that period (or not purchasing on-contract), and their data should not be counted towards the "Observed" market share.