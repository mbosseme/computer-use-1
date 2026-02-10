# Portfolio Expansion Analysis — Agent Briefing Document

**Date**: 2026-02-10
**Purpose**: Enable a GitHub Copilot agent in a separate workspace to continue the Portfolio Expansion analysis comparing Premier's `provider_invoice_workflow_history` (Workflow History) table against the legacy `transaction_analysis_expanded` (TSA) table.

> **Instructions for the receiving agent**: Read this entire document before taking any action. It contains the full analytical context, tooling setup, data model knowledge, critical gotchas, completed work, and prioritized next steps. After reading, set up the MCP BigQuery toolbox (Section 2), then copy the required files (Section 8) into your workspace. You will then be ready to continue the analysis from where Session 1 left off.

---

## Table of Contents

1. [Mission & Background](#1-mission--background)
2. [Tooling Setup (MCP BigQuery)](#2-tooling-setup-mcp-bigquery)
3. [Data Model Reference](#3-data-model-reference)
4. [Completed Work — Session 1](#4-completed-work--session-1)
5. [Completed Work — Session 2 (Partial)](#5-completed-work--session-2-partial)
6. [Critical Gotchas & Data Quirks](#6-critical-gotchas--data-quirks)
7. [Prioritized Next Steps](#7-prioritized-next-steps)
8. [Files to Copy from Source Repo](#8-files-to-copy-from-source-repo)

---

## 1. Mission & Background

### The Question
Can Premier's `provider_invoice_workflow_history` table (89M rows, Accounts Payable-level) replace or supplement the legacy `transaction_analysis_expanded` table (819M rows, Med/Surg supply chain purchasing) for health-system-level spend analytics?

### Why This Matters
The Workflow History table captures invoice data from ERP systems and Remitra (Premier's e-invoicing platform). If it can serve as a reliable proxy or complement to the TSA purchasing feed, it opens up broader spend visibility (AP-level) beyond the narrow med/surg supply chain scope of TSA.

### Key Discovery (Root Cause)
**Workflow History is an Accounts Payable data model** — it captures every invoice processed through a health system's ERP and/or Remitra, including pharma wholesale, insurance premiums, payroll deductions, IT contracts, professional services, and intercompany transfers.

**TSA is a Med/Surg Supply Chain purchasing feed** — narrowly scoped to product-level transactions with vendor/manufacturer normalization.

This scope difference is the primary driver of the spend discrepancies between the two tables. It is **not** duplication.

---

## 2. Tooling Setup (MCP BigQuery)

### Prerequisites
1. **Google Cloud SDK** installed (`gcloud` CLI available)
2. **MCP Toolbox for BigQuery** binary installed (the `toolbox` binary)
   - On macOS with Homebrew: the binary is at `/opt/homebrew/bin/toolbox`
   - Alternatively, download from Google's MCP Toolbox releases
3. **Application Default Credentials (ADC)** configured:
   ```bash
   gcloud auth application-default login
   ```
4. **BigQuery access**: Your Google account needs read access to:
   - `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
   - `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
   - `matthew-bossemeyer` project (for creating temp tables/exports)

### VS Code MCP Configuration
Create `.vscode/mcp.json` in your workspace root:

```json
{
  "servers": {
    "bigquery": {
      "command": "/opt/homebrew/bin/toolbox",
      "args": ["--prebuilt", "bigquery", "--stdio"],
      "env": {
        "BIGQUERY_PROJECT": "matthew-bossemeyer",
        "BIGQUERY_PROJECT_ID": "matthew-bossemeyer"
      }
    }
  }
}
```

> **Note**: Adjust the `command` path if your `toolbox` binary is installed elsewhere. Run `which toolbox` to find it.

### Available MCP Tools
Once configured, the BigQuery MCP server provides these tools (invoked automatically by the Copilot agent):
- `mcp_bigquery_execute_sql` — Execute SQL queries (supports `dry_run` mode)
- `mcp_bigquery_list_dataset_ids` — List datasets in a project
- `mcp_bigquery_list_table_ids` — List tables in a dataset
- `mcp_bigquery_get_table_info` — Get schema/metadata for a table
- `mcp_bigquery_ask_data_insights` — Natural language questions about table data
- `mcp_bigquery_forecast` — Time series forecasting

### Authentication Troubleshooting
| Issue | Fix |
|-------|-----|
| `Permission denied` | Re-run `gcloud auth application-default login` |
| Empty tool list | Ensure env vars are set; restart VS Code |
| `BIGQUERY_PROJECT` not found | Add both `BIGQUERY_PROJECT` and `BIGQUERY_PROJECT_ID` to env |

---

## 3. Data Model Reference

### 3.1 Workflow History (New — AP-Level)

| Property | Value |
|----------|-------|
| **Full table** | `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history` |
| **Total rows** | ~89M |
| **Scope** | All ERP + Remitra invoices (Accounts Payable-level) |
| **Granularity** | Invoice header (one row per invoice) |
| **Date field** | `vendor_invoice_date` (DATE) |
| **Amount field** | `invoice_total_amount` (FLOAT, header-level total) |
| **Health system** | `health_system_name` (STRING, 796 distinct values) |
| **Vendor (raw)** | `vendor_name` (STRING, 360K distinct) |
| **Vendor (cleansed)** | `premier_vendor_name` (STRING, 18.7K distinct) |
| **Vendor code** | `vendor_entity_code` (STRING, 21.7K distinct, 15% null) |
| **Facility** | `org_description` + `facility_entity_code` (NOT `facility_entity_name` — that's 100% NULL) |
| **Data source** | `data_source` — values: `ERP`, `Remitra`, `ERP/Remitra` |
| **Data dictionary** | See `docs/data_dictionaries/abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history.md` |

**Key fields that are BROKEN** (do not rely on them):
- `health_system_entity_code` — 50% NULL, only 33 distinct values
- `direct_parent_entity_code` — 100% NULL (literally every row = string "null")
- `facility_entity_name` — 100% NULL

### 3.2 TSA (Legacy — Med/Surg Supply Chain)

| Property | Value |
|----------|-------|
| **Full table** | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` |
| **Total rows** | ~819M |
| **Scope** | Med/surg supply chain purchasing only (product-level) |
| **Granularity** | Line item (one row per product per transaction) |
| **Date field** | `Transaction_Date` (TIMESTAMP) |
| **Amount fields** | `Base_Spend` (no markup), `Landed_Spend` (with markup) |
| **Health system** | `Health_System_Name` (STRING); also `Direct_Parent_Name` for parent rollups |
| **Vendor** | `Vendor_Name` (STRING, 25K distinct), `Vendor_Entity_Code` |
| **Facility** | `Facility_Name` (STRING, 13K distinct) |
| **Product** | `Product_Description`, `Manufacturer_Catalog_Number`, `PIN` |
| **Contract** | `Contract_Number`, `Contract_Name`, `Contract_Type`, `Contract_Category` |
| **Partitioning** | DAY on `Transaction_Date` |
| **Clustering** | `Contract_Category`, `Manufacturer_Top_Parent_Name`, `Manufacturer_Name` |
| **Exclusions** | Filter out health systems containing "TEST", "PREMIER", or "DEMO" (these are dummy entities) |
| **Data dictionary** | See `docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md` |

### 3.3 Cross-Reference Strategy

Since entity codes are broken in Workflow History, we use **name-based mapping**:

| Join Dimension | Workflow Field | TSA Field | Strategy |
|----------------|---------------|-----------|----------|
| Health System | `health_system_name` | `Health_System_Name` or `Direct_Parent_Name` | Hardcoded CASE mapping (see mapping table below). Some WF systems map to TSA parent names, not direct system names. |
| Vendor | `vendor_entity_code` | `Vendor_Entity_Code` | Direct join possible but subject to hierarchy fragmentation (same parent vendor → different child codes). |
| Facility | `org_description` + `facility_entity_code` | `Facility_Name` | Name-based fuzzy match (not yet formalized). |

---

## 4. Completed Work — Session 1

### 4.1 Entity Code Mapping Attempt (FAILED)
Attempted to join on `health_system_entity_code`. Failed because the field is 50% NULL with only 33 distinct non-null values. `direct_parent_entity_code` is 100% null.

### 4.2 Name-Based Mapping (SUCCEEDED)
Pivoted to mapping by health system name:
1. Extracted Top 20 health systems by spend from each table.
2. Ran Python fuzzy matching (`scripts/map_health_systems.py` using `difflib.SequenceMatcher`).
3. User manually validated and corrected the output.
4. **9 high-confidence mappings locked in**:

| Mapping Key | Workflow Name | TSA Name | Notes |
|---|---|---|---|
| **ADVOCATE** | Advocate Health | ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE | |
| **ADVENTHEALTH** | AdventHealth (AHS Florida) | ADVENTHEALTH | 226% capture ratio |
| **OSF** | EM_OSF | OSF HEALTHCARE SYSTEM | 272% capture ratio |
| **UHS** | EM_UHS | UHS OF DELAWARE, INC. | ~100% match |
| **RENOWN** | EM_Renown | RENOWN HEALTH | 142% |
| **ADVENTIST** | Adventist Health (California HQ) | ADVENTIST HEALTH | 167% |
| **HONORHEALTH** | EM_HonorHealth | HONORHEALTH | 155% |
| **UVM** | EM_Fletcher | THE UNIVERSITY OF VERMONT HEALTH NETWORK | Parent mapping: EM_Fletcher is a child of UVM. TSA join uses `Direct_Parent_Name`, not `Health_System_Name`. |
| **UCI** | EM_UCI | UNIVERSITY OF CALIFORNIA IRVINE | Note: TSA uses `UNIVERSITY OF CALIFORNIA - IRVINE` (with dash). ~100% match. |

### 4.3 Spend Comparison Results (9 Systems, 2025)

| Mapping Key | WF Spend ($B) | TSA Spend ($B) | Capture Ratio | Pattern |
|---|---|---|---|---|
| ADVENTHEALTH | 8.4 | 3.7 | 226% | Over-capture |
| OSF | 2.7 | 1.0 | 272% | Over-capture |
| UVM | 2.1 | 0.9 | 221% | Over-capture |
| ADVOCATE | 1.6 | 3.0 | 54% | **Under-capture** (anomaly) |
| ADVENTIST | 1.5 | 0.9 | 167% | Over-capture |
| UHS | 1.4 | 1.4 | ~100% | Matched |
| HONORHEALTH | 1.0 | 0.7 | 155% | Over-capture |
| RENOWN | 0.6 | 0.4 | 142% | Over-capture |
| UCI | 0.4 | 0.4 | ~100% | Matched |

### 4.4 OSF Deep Dive — Root Cause Analysis (COMPLETED)

Drilled into OSF HealthCare (the most extreme case at 272%) to explain the gap. **Full working paper with all queries and tables is in `exports/osf_deep_dive_analysis.md`.**

#### Key Findings from the OSF Deep Dive

**No double-counting**: ERP vs ERP/Remitra invoice numbers are 99.7% non-overlapping.

**Vendor Categorization Waterfall** — classified all $2,717M of OSF Workflow spend:

| # | Category | Spend ($M) | % of WF Total | In TSA? |
|---|---|---|---|---|
| 1 | Pharma / Drug Distributors | $334 | 12.3% | Barely ($4M) |
| 2 | Insurance / Benefits / Payroll | $267 | 9.8% | No |
| 3 | Intercompany / Internal | $333 | 12.2% | No |
| 4 | Staffing / Professional / Academic | $284 | 10.4% | No |
| 5 | IT / Software | $98 | 3.6% | Minimal |
| 6 | Capital / Utilities / Real Estate | $128 | 4.7% | Partially |
| 7 | Food / Nutrition | $21 | 0.8% | Minimal |
| 8 | Legal / Consulting / Other Services | $23 | 0.8% | No |
| 9 | OneTime Vendors | $13 | 0.5% | No |
| **A** | **Med/Surg Supply Chain** | **$1,217** | **44.8%** | **Yes** |

**55.2% of OSF Workflow spend ($1,500M) is out of TSA scope.**

After removing non-supply-chain categories:
- **Workflow Med/Surg only**: $1,217M
- **TSA total**: $1,000M
- **Residual gap**: $217M (22%)

The 22% residual is explained by:
1. **TSA overhead allocations**: $149M in "HOSPITALS SERVICES EXPENSES" ($85M) + "UNKNOWN" ($64M) — allocated categories in TSA that don't correspond to vendor invoices.
2. **Vendor hierarchy fragmentation**: Same vendor, different entity code (e.g., Medtronic = `MN2140` in WF, `643965` in TSA).
3. **Long-tail vendor scope differences**: ~$70–80M.

#### Top Non-Supply-Chain Vendors (OSF examples)
| Vendor | Entity Code | Spend ($M) | Category |
|---|---|---|---|
| AmerisourceBergen Drug Corp | OH2129 | 326 | Pharma |
| Healthcare Solutions LLC | 614248 | 236 | Intercompany |
| Blue Cross Blue Shield Assn | AB8123 | 213 | Insurance |
| Medical Solutions L.L.C. | 630845 | 56 | Staffing |
| Touchette Regional Hospital | — | 52 | Intercompany |
| University of Kentucky College of Agriculture | 734262 | 47 | Academic |
| Illinois Tool Works Inc. | 616773 | 31 | Capital |
| SYNNEX Corporation | 748029 | 29 | IT |
| Epic Systems Corporation | 625484 | 18 | IT |
| Microsoft Corporation | 613412 | 18 | IT |

#### Vendor Categorization SQL Pattern

The categorization uses `CASE WHEN` on `UPPER(COALESCE(premier_vendor_name, vendor_name))` with LIKE patterns. The general structure:

```sql
CASE
  -- Pharma
  WHEN UPPER(COALESCE(premier_vendor_name, vendor_name)) LIKE '%AMERISOURCE%' THEN 'Pharma / Drug Distributors'
  WHEN ... LIKE '%MCKESSON%' AND NOT LIKE '%MCKESSON MEDICAL%' ... THEN 'Pharma / Drug Distributors'
  
  -- Insurance / Benefits
  WHEN ... LIKE '%BLUE CROSS%' THEN 'Insurance / Benefits / Payroll'
  WHEN ... LIKE '%INSURANCE%' THEN 'Insurance / Benefits / Payroll'
  
  -- Intercompany (system-specific: use the health system's own name)
  WHEN ... LIKE '%<HEALTH_SYSTEM_NAME>%' THEN 'Intercompany / Internal'
  
  -- Staffing
  WHEN ... LIKE '%STAFFING%' THEN 'Staffing / Professional / Academic'
  WHEN ... LIKE '%MEDICAL SOLUTIONS%' THEN 'Staffing / Professional / Academic'
  WHEN ... LIKE '%UNIVERSITY%' THEN 'Staffing / Professional / Academic'
  
  -- IT
  WHEN ... LIKE '%EPIC SYSTEM%' THEN 'IT / Software'
  WHEN ... LIKE '%MICROSOFT%' THEN 'IT / Software'
  WHEN ... LIKE '%CDW%' THEN 'IT / Software'
  
  -- Capital / Utilities
  WHEN ... LIKE '%CONSTRUCTION%' THEN 'Capital / Utilities / Real Estate'
  WHEN ... LIKE '%ELECTRIC%' AND NOT LIKE '%ELECTRO%SURG%' THEN 'Capital / Utilities / Real Estate'
  
  -- Food
  WHEN ... LIKE '%SYSCO%' THEN 'Food / Nutrition'
  WHEN ... LIKE '%COMPASS GROUP%' THEN 'Food / Nutrition'
  
  -- Legal / Consulting
  WHEN ... LIKE '%KPMG%' THEN 'Legal / Consulting'
  WHEN ... LIKE '%DELOITTE%' THEN 'Legal / Consulting'
  WHEN ... LIKE '% LLP' THEN 'Legal / Consulting'
  
  -- Government / Regulatory
  WHEN ... LIKE '%AGENCY FOR HEALTH CARE%' THEN 'Government / Regulatory'
  
  -- Overhead Allocations (pseudo-vendors, not real vendor invoices)
  WHEN ... LIKE '%HOSPITALS SERVICES EXPENSES%' THEN 'Overhead Allocations'
  WHEN ... = 'MEDSERVE' THEN 'Overhead Allocations'
  
  -- DEFAULT: everything else is assumed Med/Surg supply chain
  ELSE 'Med/Surg Supply Chain'
END as category
```

> **Important**: The Intercompany category must be customized per health system. For OSF, match on `'%OSF%'`, `'%HEALTHCARE SOLUTIONS%'`, `'%POINTCORE%'`, `'%TOUCHETTE%'`. For AdventHealth, match on `'%ADVENTHEALTH%'`, `'%ADVENT HEALTH%'`, `'%FLORIDA HOSPITAL%'`. Each system has its own internal entities.

---

## 5. Completed Work — Session 2 (Partial)

### 5.1 AdventHealth Vendor Categorization (In Progress)

The same vendor categorization waterfall was run for AdventHealth. Key discovery: **AdventHealth is Remitra-only** (no ERP data), which means it's already partially scoped toward supply chain, unlike OSF which was ERP + ERP/Remitra.

#### AdventHealth Categorization Results (Refined)

| Category | Spend ($M) | % of WF Total | Distinct Vendors |
|---|---|---|---|
| Med/Surg Supply Chain | $5,545 | 65.9% | 11,381 |
| Government / Regulatory | $893 | 10.6% | 9 |
| Overhead Allocations | $592 | 7.0% | 2 |
| IT / Software | $429 | 5.1% | 34 |
| Pharma / Drug Distributors | $378 | 4.5% | 6 |
| Legal / Consulting | $209 | 2.5% | 117 |
| Food / Nutrition | $124 | 1.5% | 9 |
| Staffing / Professional / Academic | $120 | 1.4% | 132 |
| Insurance / Benefits / Payroll | $63 | 0.8% | 9 |
| Capital / Utilities / Real Estate | $57 | 0.7% | 187 |
| Intercompany / Internal | $0.03 | 0.0% | 5 |

**34.1% of AdventHealth Workflow spend is non-supply-chain** (vs 55% for OSF).

Key differences from OSF:
- **Government / Regulatory is huge ($893M)**: Dominated by "FLORIDA AGENCY FOR HEALTH CARE ADMINISTRATION" ($771M) — likely Medicaid/regulatory payments. This category didn't exist at OSF.
- **Overhead Allocations also large ($592M)**: "HOSPITALS SERVICES EXPENSES" ($536M) + "MEDSERVE" ($56M). These are allocated overhead, the same pseudo-vendor pattern as TSA.
- **Intercompany is negligible**: AdventHealth's intercompany transactions are minimal in Remitra (they'd be in ERP, which AdventHealth doesn't have in Workflow).

#### Top AdventHealth Vendors (all categories)
| Vendor | Entity Code | Spend ($M) | Category Note |
|---|---|---|---|
| Florida Agency for Health Care Admin | 835710 | $771 | Government |
| Hospitals Services Expenses | 838317 | $536 | Overhead allocation |
| Boston Scientific Corp | MA2109 | $235 | Med/Surg |
| Intuitive Surgical | 605385 | $205 | Med/Surg |
| Medline Industries | IL2114 | $188 | Med/Surg |
| CDW Corporation | 601983 | $172 | IT |
| AmerisourceBergen | OH2129 | $164 | Pharma |
| Johnson & Johnson | NJ5015 | $140 | Med/Surg |
| Royal Philips Electronics | CT2024 | $134 | Med/Surg |
| GE Healthcare Technologies | IL2105 | $132 | Med/Surg |

#### What This Means
The **hypothesis partially generalizes** but with a twist:
- For **ERP-based systems** (like OSF): ~55% non-supply-chain (broad AP scope)
- For **Remitra-only systems** (like AdventHealth): ~34% non-supply-chain (narrower scope, but still includes government payments, overhead allocations, IT, pharma, etc.)
- The `data_source` field is a strong predictor of how much non-supply-chain spend will be present

**This analysis is still in progress** — the receiving agent should verify the categorization accuracy for AdventHealth by spot-checking the top vendors in the "Med/Surg" bucket (there may be misclassifications in the long tail).

---

## 6. Critical Gotchas & Data Quirks

These are hard-won lessons from Session 1 that will save you significant debugging time:

### 6.1 NULL Representation
Workflow History uses **both** the string literal `'NULL'` and actual SQL NULL for missing values. Always filter with:
```sql
WHERE col IS NOT NULL AND col != 'NULL'
```

### 6.2 Header vs Line-Item Granularity
- **Workflow**: `invoice_total_amount` is per-invoice header. One row = one invoice.
- **TSA**: `Base_Spend` / `Landed_Spend` is per-product line item. Many rows per purchase order.
- **Rule**: Compare at aggregated totals only (SUM). Never compare row counts directly.

### 6.3 Vendor Hierarchy Fragmentation
The same parent vendor can appear under different subsidiary entity codes in each system:
- **Medtronic**: `MN2140` (Medtronic Inc) in Workflow, `643965` (Medtronic USA Inc) in TSA
- **Solution**: Use `vendor_top_parent_entity_code` for roll-up when available (but it's 21% null in Workflow).

### 6.4 Broken Entity Code Fields
- `health_system_entity_code`: 50% NULL, only 33 distinct
- `direct_parent_entity_code`: 100% NULL (all = string "null")
- `facility_entity_name`: 100% NULL
- **Must use name-based approaches** for health system/facility identification.

### 6.5 `facility_entity_name` is 100% NULL
Use `org_description` + `facility_entity_code` instead.

### 6.6 TSA Overhead Categories
TSA contains pseudo-vendor entries like "HOSPITALS SERVICES EXPENSES" and "UNKNOWN" that represent allocated overhead, not actual vendor invoices. These inflate TSA spend by ~$100–200M per large health system.

### 6.7 UVM/Fletcher Mapping
`EM_Fletcher` in Workflow maps to "THE UNIVERSITY OF VERMONT HEALTH NETWORK" in TSA. But in TSA, this match must use `Direct_Parent_Name`, not `Health_System_Name`. See the SQL in `scripts/gen_mapped_spend_comparison.sql`.

### 6.8 TSA Test/Demo Exclusions
Always exclude health systems containing "TEST", "PREMIER", or "DEMO" from TSA analysis.

### 6.9 Data Source Implications
| `data_source` Value | Implication |
|---------------------|-------------|
| `ERP` | Full AP scope (all invoice types) — expect high non-supply-chain % |
| `Remitra` | Somewhat narrower (supply chain focus) but still includes non-med/surg |
| `ERP/Remitra` | Invoice exists in both systems; no double-counting (99.7% non-overlapping invoice numbers confirmed for OSF) |

### 6.10 TSA Amount Fields
- `Base_Spend`: spend without distributor markup (used in the OSF deep dive)
- `Landed_Spend`: spend with distributor markup (used in the 9-system comparison)
- The difference is typically small but be consistent within a single analysis.

---

## 7. Prioritized Next Steps

### Priority 1: Verify AdventHealth Categorization
The vendor categorization waterfall for AdventHealth has been run (see Section 5.1), but needs verification:
- Spot-check the top 20–30 vendors in the "Med/Surg Supply Chain" bucket for misclassifications.
- Compare the filtered Med/Surg-only Workflow spend ($5,545M) against TSA's AdventHealth total ($3,718M) to compute the adjusted capture ratio.
- Look specifically at whether CDW ($172M, classified as IT) and FFF Enterprises ($55M, classified as Pharma) should be partially in-scope for TSA.

### Priority 2: Investigate Advocate Under-Capture (54%)
Advocate Health shows only 54% capture ratio (WF $1.6B < TSA $3.0B). Hypotheses:
- **Post-merger entity split**: "ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE" in TSA may include the combined Advocate + Aurora Health Care entities, while Workflow may only capture from one side.
- **Investigation approach**:
  1. Query TSA for all `Direct_Parent_Name` values under "ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE" — does it include Aurora facilities?
  2. Query Workflow for any `health_system_name` LIKE `'%Aurora%'` or `'%Advocate Aurora%'` — is there a second entity?
  3. If separate, add the Aurora entity to the Advocate mapping and re-run the comparison.

### Priority 3: Build a Reusable "TSA-Scope Filter"
Create a SQL view/CTE that removes non-supply-chain vendors from Workflow History to make it comparable to TSA. Requirements:
- Should be parameterized (work for any health system, not just OSF or AdventHealth).
- Base it on the vendor categorization CASE logic from Section 4.4.
- Must handle the system-specific intercompany patterns (each health system has its own internal entities).
- Consider making the intercompany filter dynamic by matching `vendor_name LIKE '%' || health_system_name || '%'`.
- Should also exclude `HOSPITALS SERVICES EXPENSES` and `UNKNOWN`/`MEDSERVE` overhead allocations.
- Output: a reusable CTE or view that can be added to any per-system comparison query.

### Priority 4: Expand the Health System Mapping Table
Currently 9 systems mapped. The Top 20 by Workflow spend (from `scripts/map_health_systems.py`) includes candidates not yet mapped:
- **Dignity Health** ($4.3B WF) — large system, likely in TSA
- **Catholic Health Initiatives** ($3.9B WF) — may be under CommonSpirit Health in TSA
- **Northwell Health** ($2.9B WF) — was rejected in Session 1 (fuzzy-matched to Acurity, which was wrong). Try direct TSA lookup.
- **EM_UCSD** ($2.1B WF) — look for "UNIVERSITY OF CALIFORNIA SAN DIEGO" in TSA
- **Northwestern Memorial HealthCare** ($1.7B WF)
- **Henry Ford Health System** ($1.4B WF)
- **Beth Israel Lahey Health** ($1.4B WF)

**Approach**:
1. Query TSA for `SELECT DISTINCT Health_System_Name FROM ... WHERE Health_System_Name LIKE '%DIGNITY%'` (etc.) to find exact matches.
2. Cross-check with `Direct_Parent_Name` in case the system rolls up differently.
3. Add validated mappings to the mapping table and the CASE logic in the comparison SQL.

### Priority 5: Vendor Entity Code Roll-Up Strategy
Build a vendor parent-to-child crosswalk to normalize vendor codes across the two data models:
- Leverage `vendor_top_parent_entity_code` in Workflow (21% null) and `Manufacturer_Top_Parent_Name`/`Vendor_Name` in TSA.
- Goal: enable vendor-level spend comparison between the two tables despite hierarchy fragmentation.

### Strategic Questions (for the human stakeholder)
1. Should Workflow **replace** TSA, or **supplement** it with non-supply-chain categories?
2. Is a ~20% residual gap acceptable for portfolio analytics?
3. Should the health system crosswalk be a persistent BigQuery table (instead of hardcoded CASE)?

---

## 8. Files to Copy from Source Repo

Copy these files from the source repository (`wt-2026-02-10__portfolio-expansion`) into your workspace, preserving the directory structure:

### Required Files

```
docs/
  validated_health_system_mapping.md          # The 9 validated health system name mappings
  data_dictionaries/
    abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history.md
    abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md

scripts/
  gen_mapped_spend_comparison.sql             # SQL with hardcoded CASE logic for 9-system comparison
  map_health_systems.py                       # Python fuzzy matcher for health system name mapping

runs/2026-02-10__portfolio-expansion/
  exports/
    osf_deep_dive_analysis.md                 # Full OSF deep dive working paper (queries, tables, root cause)
```

### Optional but Recommended

```
docs/
  MCP_TOOLBOX_GUIDE.md                        # Detailed MCP BigQuery setup guide
  data_dictionaries/
    _TEMPLATE.md                              # Template for creating new data dictionaries
    README.md                                 # Index of available data dictionaries

scripts/
  gen_spend_comparison_2025.sql               # Earlier iteration of comparison SQL
  gen_stable_systems_spend_comparison.sql     # Earlier iteration for "stable" systems
  gen_profiling_sql.py                        # SQL generator for table profiling
  gen_workflow_profiling_sql.py               # SQL generator for workflow table profiling
  update_dictionary.py                        # Script to update data dictionary files
  create_dictionary_md_workflow.py            # Script to create data dictionary markdown
```

### File Copy Command
If both repos are on the same machine, from the **destination** workspace root:

```bash
SOURCE="/path/to/wt-2026-02-10__portfolio-expansion"

# Required files
mkdir -p docs/data_dictionaries scripts runs/portfolio-expansion/exports

cp "$SOURCE/docs/validated_health_system_mapping.md" docs/
cp "$SOURCE/docs/data_dictionaries/abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history.md" docs/data_dictionaries/
cp "$SOURCE/docs/data_dictionaries/abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md" docs/data_dictionaries/
cp "$SOURCE/scripts/gen_mapped_spend_comparison.sql" scripts/
cp "$SOURCE/scripts/map_health_systems.py" scripts/
cp "$SOURCE/runs/2026-02-10__portfolio-expansion/exports/osf_deep_dive_analysis.md" runs/portfolio-expansion/exports/

# Optional
cp "$SOURCE/docs/MCP_TOOLBOX_GUIDE.md" docs/
cp "$SOURCE/scripts/gen_spend_comparison_2025.sql" scripts/
cp "$SOURCE/scripts/gen_stable_systems_spend_comparison.sql" scripts/
cp "$SOURCE/scripts/gen_profiling_sql.py" scripts/
cp "$SOURCE/scripts/gen_workflow_profiling_sql.py" scripts/
cp "$SOURCE/scripts/update_dictionary.py" scripts/
cp "$SOURCE/scripts/create_dictionary_md_workflow.py" scripts/
```

---

## Appendix A: Quick-Reference SQL Patterns

### Compare spend for mapped systems (already exists in `scripts/gen_mapped_spend_comparison.sql`)
```sql
-- See scripts/gen_mapped_spend_comparison.sql for the complete query.
-- Pattern: CTE per source with CASE mapping → JOIN on mapping_key → compute capture_ratio
```

### Vendor categorization waterfall (adapt per health system)
```sql
SELECT 
  category,
  SUM(invoice_total_amount) / 1e6 as spend_millions,
  ROUND(SUM(invoice_total_amount) / SUM(SUM(invoice_total_amount)) OVER() * 100, 1) as pct_of_total
FROM (
  SELECT invoice_total_amount,
    CASE
      WHEN UPPER(COALESCE(premier_vendor_name, vendor_name)) LIKE '%AMERISOURCE%' THEN 'Pharma'
      -- ... (full CASE logic from Section 4.4)
      ELSE 'Med/Surg Supply Chain'
    END as category
  FROM `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
  WHERE EXTRACT(YEAR FROM vendor_invoice_date) = 2025
    AND health_system_name = '<HEALTH_SYSTEM_NAME>'
)
GROUP BY category
ORDER BY spend_millions DESC
```

### Find TSA name for a Workflow health system
```sql
SELECT DISTINCT Health_System_Name, Direct_Parent_Name, COUNT(*) as cnt
FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
WHERE UPPER(Health_System_Name) LIKE '%<SEARCH_TERM>%'
   OR UPPER(Direct_Parent_Name) LIKE '%<SEARCH_TERM>%'
GROUP BY 1, 2
ORDER BY cnt DESC
LIMIT 20
```

### Check data_source composition for a health system
```sql
SELECT data_source, COUNT(*) as row_cnt, SUM(invoice_total_amount)/1e6 as spend_m
FROM `abi-xform-prod.abi_xform_bq_erp_hardening.provider_invoice_workflow_history`
WHERE health_system_name = '<NAME>'
  AND EXTRACT(YEAR FROM vendor_invoice_date) = 2025
GROUP BY 1
```

---

*End of briefing.*
