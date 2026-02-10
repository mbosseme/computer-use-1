# Premier Healthcare Data Models & BigQuery MCP Toolbox Handoff

> **Purpose:** Generalizable reference for any Copilot agent working with Premier's core healthcare purchasing data models via BigQuery. This guide captures patterns, schemas, and interaction techniques developed through real use cases.

---

## 1. Quick Start: Authentication & Access

### Non-Negotiable: Application Default Credentials (ADC) Only
```bash
gcloud auth application-default login
export BIGQUERY_PROJECT_ID=matthew-bossemeyer  # ALWAYS use this project 
```
- **Standard Project:** Always use `matthew-bossemeyer` as the default execution project for queries, Dataform, and table creation.
- **Never embed secrets or commit keys.** If auth fails, prompt the user to run the gcloud command.
- Service account JSON files (`GOOGLE_APPLICATION_CREDENTIALS`) are not supported for interactive work.

### MCP Server Configuration
For interactive BigQuery exploration inside VS Code Copilot Chat, configure an MCP server:

**Naming convention:** `bigquery_<workspace_folder_name>` (prevents collisions across repos).

**VS Code config (`.vscode/mcp.json`):**
```json
{
  "servers": {
    "bigquery_<your_workspace>": {
      "command": "toolbox",
      "args": ["--prebuilt", "bigquery", "--stdio"]
    }
  }
}
```

---

## 2. Core Data Models Overview

| Model | Full Table Path | Source | Rows (approx) | Key Use Case |
|-------|-----------------|--------|---------------|--------------|
| **Transaction Analysis** | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` | Provider-submitted POs/Invoices | ~820M | Provider-side purchasing visibility |
| **Supplier Spend** | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_supplier_sales.supplier_spend` | Manufacturer-reported sales tracings | ~87M | Manufacturer-side contract sales |
| **SASF DHC Join** | `matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join` | Definitive Healthcare enrichment | ~7K (hospitals) | Facility/IDN enrichment, hospital metadata |

### When to Use Which

| Question | Use This Model |
|----------|----------------|
| "What did health systems actually buy?" | Transaction Analysis |
| "What did manufacturers report selling?" | Supplier Spend |
| "Who are these facilities? What IDN?" | SASF DHC Join |
| "Why don't provider and supplier totals match?" | Both + compare timing/scope |

---

## 3. Transaction Analysis Expanded (`transaction_analysis_expanded`)

### Purpose
Rolling 7-year transactional purchase feed from **provider-submitted POs and Invoices**. This is the "ground truth" for what health systems recorded in their ERPs.

### Critical Context
- **Coverage varies by health system.** Some exclude capital invoices from feeds.
- Represents **"Observed Transactional Share,"** not 100% market.
- Large capital equipment (MRI, CT) often lacks Item Master mapping → appears as "UNKNOWN" category.

### Key Columns for Analysis

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `Transaction_Date` | TIMESTAMP | PO submission date by facility | Partitioning key (DAY) |
| `Month` | STRING | Formatted month ("October 2023") | Human-readable |
| `Contract_Category` | STRING | Premier taxonomy (~870 values) | "UNKNOWN" is largest bucket |
| `Manufacturer_Top_Parent_Name` | STRING | Ultimate parent manufacturer | Normalized |
| `Manufacturer_Name` | STRING | Direct manufacturer | May differ from top parent |
| `Vendor_Name` | STRING | Distributor/seller | Same as manufacturer if direct |
| `Base_Spend` | FLOAT | Total spend (no markup) | Primary spend metric |
| `Base_Each_Price` | FLOAT | Unit price (no markup) | Use for capital thresholds |
| `Product_Description` | STRING | Free-text PO description | Text-mine for capital equipment |
| `Spend_Type` | STRING | Contract status | ON CONTRACT, NON CONTRACT, CATEGORIZED ONLY, OFF CONTRACT |
| `Member_Type` | STRING | Facility type in provider view | ACUTE, NON-ACUTE |
| `Facility_Name` | STRING | Reporting facility | **Privacy: aggregate only** |
| `Health_System_Name` | STRING | Top parent org | **Privacy: aggregate only** |

### Exclusion Rules (Apply Always)
```sql
-- Exclude test/demo entities
WHERE Health_System_Name NOT LIKE '%TEST%'
  AND Health_System_Name NOT LIKE '%PREMIER%'
  AND Health_System_Name NOT LIKE '%DEMO%'
```

### Capital Equipment Identification Heuristic
Since there's no explicit "Capital" flag, use this tiered logic:

```sql
-- Tier 1: Price threshold (strongest signal)
WHERE Base_Each_Price > 25000

-- Tier 2: Unmatched proxy (capital often non-contract)
AND Spend_Type IN ('NON CONTRACT', 'CATEGORIZED ONLY')

-- Tier 3: Exclusion (remove services/software)
AND Product_Description NOT REGEXP_CONTAINS(
  r'(?i)SERVICE|MAINTENANCE|WARRANTY|AGREEMENT|REPAIR|SOFTWARE|LICENSE|RENEWAL'
)
```

### Sample Exploration Query
```sql
SELECT 
  Contract_Category,
  Manufacturer_Top_Parent_Name,
  COUNT(*) as txn_count,
  SUM(Base_Spend) as total_spend,
  AVG(Base_Each_Price) as avg_unit_price
FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
WHERE Transaction_Date >= '2023-10-01'
  AND Transaction_Date < '2025-10-01'
  AND Contract_Category LIKE '%COMPUTED TOMOGRAPHY%'
GROUP BY 1, 2
ORDER BY total_spend DESC
LIMIT 20
```

---

## 4. Supplier Spend (`supplier_spend`)

### Purpose
Manufacturer-reported **contract sales tracings** back to Premier. This is what manufacturers claim they sold under Premier agreements.

### Critical Context
- **Comprehensive scope:** All sites of care (not just acute).
- **Contract-only:** Only captures on-Premier-agreement spend.
- **Manufacturer-reported timing:** Uses invoice/booking dates from manufacturer systems.
- Reporting stops if facility leaves Premier GPO.

### Key Columns for Analysis

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `Month` | STRING | Supplier-submitted month | Formatted ("October 2024") |
| `Quarter` | STRING | Supplier-submitted quarter | "Oct - Dec 2024" |
| `Spend_Period_YYYYQMM` | INTEGER | Month key for joins | 2024410 = Oct Q4 2024 |
| `Contract_Category` | STRING | Premier taxonomy | ~612 values |
| `Contracted_Supplier` | STRING | Company holding contract | May be manufacturer or distributor |
| `Contracted_Supplier_Parent_Name` | STRING | Parent of contracted supplier | |
| `Capital_Equipment_Flag` | STRING | Y/N capital designation | Direct flag (unlike TA) |
| `Premier_Spend` | FLOAT | Total spend submitted | Primary spend metric |
| `Admin_Fees_Paid` | FLOAT | Admin fees | Useful for validation |
| `Facility_Type` | STRING | ACUTE, NON-HEALTHCARE, ALTERNATE SITE | Filter for analysis scope |
| `Facility_Name` | STRING | Reporting facility | **Privacy: aggregate only** |
| `Health_System_Name` | STRING | Top parent | **Privacy: aggregate only** |
| `Health_System_Name_Primary` | STRING | Preferred rollup entity | Handles aggregation affiliates |

### Timing Field: YYYYQMM Decoding
The `Spend_Period_YYYYQMM` field encodes year, quarter, and month:
```
2024410 = 2024, Q4, October (month 10)
2025101 = 2025, Q1, January (month 01)
```
Extract components:
```sql
CAST(FLOOR(Spend_Period_YYYYQMM / 1000) AS INT64) as year,
MOD(CAST(FLOOR(Spend_Period_YYYYQMM / 100) AS INT64), 10) as quarter,
MOD(Spend_Period_YYYYQMM, 100) as month_num
```

### Sample Exploration Query
```sql
SELECT 
  Contract_Category,
  Contracted_Supplier_Parent_Name,
  Facility_Type,
  SUM(Premier_Spend) as total_spend,
  COUNT(DISTINCT Facility_Name) as facility_count
FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_supplier_sales.supplier_spend`
WHERE Year >= 2023
  AND Contract_Category LIKE '%MAGNETIC RESONANCE%'
  AND Facility_Type = 'ACUTE'
GROUP BY 1, 2, 3
ORDER BY total_spend DESC
LIMIT 20
```

---

## 5. SASF DHC Join (`sa_sf_dhc_join`)

### Purpose
Enrichment table joining **Definitive Healthcare** hospital/facility metadata. Use for IDN rollups, hospital type classification, and facility identification.

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| `dhc_hospital_name` | STRING | Hospital name from DHC |
| `dhc_hospital_type` | STRING | Short Term Acute, Critical Access, Psychiatric, LTACH, etc. |
| `dhc_firm_type` | STRING | Hospital, Clinic, etc. |
| `dhc_definitive_id` | INTEGER | DHC unique identifier |
| `dhc_provider_number` | STRING | CMS provider number (CCN) |
| `dhc_idn` | STRING | IDN name |
| `dhc_idn_parent` | STRING | Ultimate IDN parent |
| `dhc_state` | STRING | State |
| `dhc_city` | STRING | City |
| `dhc_bed_count` | INTEGER | Licensed beds |

### Common Use: Filter to Hospitals
```sql
SELECT * FROM `matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join`
WHERE dhc_firm_type = 'Hospital'
```

---

## 6. Report Builder (`report_builder`)

### Purpose
Transactional sales data reported by **Pharmaceutical Wholesalers** (McKesson, Cardinal, AmerisourceBergen, etc.).
This table is critical for "indirect" sales visibility, capturing spend that flows through distribution channels rather than direct-from-manufacturer.

### Key Context
- **Full Path**: `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder`
- **Visibility**: Often captures smaller non-acute facilities or pharmacy spend not seen in the main ERP feed (`transaction_analysis_expanded`).
- **Vendor Name Nuance**: The `wholesaler` column contains the specific distributor name (e.g., "Cardinal Health"), while other columns might just say "Wholesaler". Use `wholesaler` for specificity.

### Key Columns
| Column | Description |
|--------|-------------|
| `invoice_date` | Date of sale (YYYY-MM-DD or similar) |
| `facility_id` | Premier Entity Code of the purchasing facility |
| `ndc` | National Drug Code (raw format) |
| `total_spend` | Invoiced spend amount |
| `wholesaler` | Name of the specific wholesaler (Source of truth for Vendor) |

---

## 7. Premier Primary Item Master (`premier_primary_item_master`)

### Purpose
The definitive catalog for product metadata (Brands, Mfr Names, Catalog Numbers, Packaging).
Used to enrich strictly transactional tables (RB, TA) with human-readable product details.

### Key Context
- **Full Path**: `abi-inbound-prod.abi_inbound_bq_stg_master_data_premier_product.premier_primary_item_master`
- **Join Key**: `ndc` (cleaned to 11-digit) or `reference_number`.

### Manufacturer Name Logic (Critical)
The item master contains both Manufacturer and Distributor records for the same product.
**To find the true OEM (Original Equipment Manufacturer):**
Prioritize records where `vend_type = 'M'` (Manufacturer) and `pkg_uom = 'EA'` (Each).
Distributor records (`vend_type = 'D'`) often list themselves (e.g., "McKesson") as the manufacturer name, which is incorrect for brand attribution.

```sql
-- Pattern: Select best product metadata
SELECT * FROM premier_primary_item_master
WHERE reference_number = '...'
ORDER BY 
  CASE WHEN vend_type = 'M' AND pkg_uom = 'EA' THEN 1 
       WHEN vend_type = 'M' THEN 2 
       ELSE 3 END
LIMIT 1
```

---

## 8. MCP Toolbox Interaction Patterns

### Available Tools (via prebuilt BigQuery server)

| Tool | Purpose | Example |
|------|---------|---------|
| `list_dataset_ids` | List datasets in a project | `project="abi-inbound-prod"` |
| `list_table_ids` | List tables in a dataset | `dataset="abi_inbound_bq_stg_purchasing_provider_transaction"` |
| `get_table_info` | Get schema + metadata | `table="transaction_analysis_expanded"` |
| `execute_sql` | Run SQL queries | Include LIMIT for safety |
| `ask_data_insights` | Natural language questions | For quick exploration |

### Recommended Workflow

1. **Orient to schema first:**
   ```
   Use get_table_info to understand columns before querying.
   ```

2. **Start with bounded queries:**
   ```sql
   -- Always include LIMIT when exploring
   SELECT * FROM `table` WHERE ... LIMIT 100
   ```

3. **Use dry_run for cost estimation:**
   ```
   execute_sql with dry_run=true to check bytes scanned.
   ```

4. **Profile before aggregating:**
   ```sql
   -- Check distinct values and nulls
   SELECT column, COUNT(*) FROM table GROUP BY 1 ORDER BY 2 DESC LIMIT 20
   ```

### Example MCP Invocations

**List tables:**
```
/mcp bigquery_<workspace> callTool list_table_ids project="abi-inbound-prod" dataset="abi_inbound_bq_stg_purchasing_supplier_sales"
```

**Get schema:**
```
/mcp bigquery_<workspace> callTool get_table_info project="abi-inbound-prod" dataset="abi_inbound_bq_stg_purchasing_supplier_sales" table="supplier_spend"
```

**Run query:**
```
/mcp bigquery_<workspace> callTool execute_sql sql="SELECT Contract_Category, SUM(Premier_Spend) FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_supplier_sales.supplier_spend` WHERE Year = 2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
```

---

## 9. Key Analytical Patterns & Lessons Learned

### Pattern 1: Parity Analysis (Provider vs Supplier)
Compare what providers reported vs what manufacturers reported:

```sql
-- Provider side (aggregate by category, manufacturer, period)
SELECT 
  'Provider' as source,
  Contract_Category,
  Manufacturer_Top_Parent_Name,
  FORMAT_DATE('%Y-%m', Transaction_Date) as month,
  SUM(Base_Spend) as spend
FROM `...transaction_analysis_expanded`
WHERE Member_Type = 'ACUTE'
GROUP BY 1, 2, 3, 4

UNION ALL

-- Supplier side
SELECT 
  'Supplier' as source,
  Contract_Category,
  Contracted_Supplier_Parent_Name,
  Month,
  SUM(Premier_Spend) as spend
FROM `...supplier_spend`
WHERE Facility_Type = 'ACUTE'
GROUP BY 1, 2, 3, 4
```

### Pattern 2: Timing Reconciliation
Provider and supplier timing differ systematically:
- **Provider `Transaction_Date`:** When facility submitted PO (can be earlier than invoice)
- **Supplier `Month`:** When manufacturer recorded the sale (typically invoice timing)

This causes **Q4 timing differences**: PO-based provider data may pull December activity into earlier months, while invoice-based supplier data may push activity later.

### Pattern 3: Manufacturer Name Normalization
Supplier Spend uses `Contracted_Supplier_Parent_Name` which may not match Transaction Analysis `Manufacturer_Top_Parent_Name`. Build a lookup:

```sql
-- Find the TA manufacturer name for each supplier name
SELECT DISTINCT
  ss.Contracted_Supplier_Parent_Name as supplier_name,
  ta.Manufacturer_Top_Parent_Name as ta_manufacturer_name
FROM supplier_spend ss
LEFT JOIN transaction_analysis_expanded ta
  ON UPPER(ss.Contracted_Supplier_Parent_Name) LIKE CONCAT('%', UPPER(ta.Manufacturer_Top_Parent_Name), '%')
```

### Pattern 4: Capital Equipment Text Mining
For uncategorized capital in Transaction Analysis:

```sql
-- Find likely MRI/CT equipment in UNKNOWN category
SELECT Product_Description, Base_Each_Price, Base_Spend
FROM transaction_analysis_expanded
WHERE Contract_Category = 'UNKNOWN'
  AND Base_Each_Price > 25000
  AND REGEXP_CONTAINS(UPPER(Product_Description), r'MRI|CT|TOMOGRAPHY|RESONANCE|MONITORING')
  AND NOT REGEXP_CONTAINS(UPPER(Product_Description), r'SERVICE|MAINTENANCE|WARRANTY')
LIMIT 100
```

---

## 10. Privacy & Compliance Guardrails

**Aggregated data only.** Never export or display:
- Individual `Facility_Name` values
- Individual `Health_System_Name` values  
- `Facility_Hin` (Hospital Identification Number)

When building reports, always aggregate to:
- Category level
- Manufacturer level
- Time period level
- Geographic region (state) level

---

## 11. Data Dictionary Resources

Detailed column-level documentation with null rates, distinct counts, and sample values:

| Model | Data Dictionary Location |
|-------|-------------------------|
| Transaction Analysis | `docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md` |
| Supplier Spend | `docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_purchasing_supplier_sales.supplier_spend.md` |
| SASF DHC Join | `docs/data_dictionaries/matthew-bossemeyer.cdx_sample_size.sa_sf_dhc_join__dhc_firm_type=Hospital.md` |

---

## 12. Reusable Techniques Checklist

When starting a new analysis with these models:

- [ ] Authenticate: `gcloud auth application-default login`
- [ ] Use MCP `get_table_info` to confirm schema before writing queries
- [ ] Apply test/demo entity exclusions
- [ ] Start with LIMIT clauses, remove only when aggregating
- [ ] For parity analysis, align on same time window and facility type
- [ ] For capital analysis, use $25K+ price threshold + text mining
- [ ] Document timing assumptions (PO vs invoice dates)
- [ ] Aggregate to protect privacy (no facility-level exports)
- [ ] Log findings to a run log (e.g., `SUMMARY_OF_RECENT_ITERATION.md`)

---

*Generated from ge-sample repo learnings, January 2026.*
