# Skill: Premier Data Analytics

**Status**: Recommended / Core
**Context**: Use when extracting or analyzing Premier purchasing data (`transaction_analysis_expanded`, `report_builder`) and enriching it with `premier_primary_item_master`.

## 1. The "Dual-Source" Reality (Purchasing)
Purchasing data exists in two parallel universes. Use both for complete coverage.

| Feature | Provider Feed (`transaction_analysis_expanded`) | Wholesaler Feed (`report_builder`) |
| :--- | :--- | :--- |
| **Source** | ERP / Accounts Payable (Direct) | Distributor Sales Tracings (Indirect) |
| **Scope** | Acute Care / Large IDNs — **med/surg supply chain only** | Physician Offices / Non-Acute / Pharmacy |
| **Date Field** | `Transaction_Date` (PO Date) | `invoice_date` (Sale Date) |
| **Vendor Field** | `Vendor_Name` | **`wholesaler`** (Specific) / `source` (Generic) |

## 1b. Workflow History — The "Full AP" Model
The `provider_invoice_workflow_history` table (`abi-xform-prod.abi_xform_bq_erp_hardening`) captures **all Accounts Payable invoices** (ERP + Remitra), not just med/surg supply chain.

| Aspect | Workflow History | TSA (transaction_analysis_expanded) |
| :--- | :--- | :--- |
| **Scope** | Full AP: pharma, insurance, staffing, IT, capital, food, intercompany, AND med/surg | Med/surg supply chain only |
| **Granularity** | Header-level (per invoice) | Line-item-level (per product) |
| **Amount Field** | `invoice_total_amount` | `Base_Spend` / `Landed_Spend` |
| **Category Taxonomy** | None — must classify by vendor name patterns | `Contract_Category` (~870 values) |

**Critical insight**: When comparing WF to TSA, WF will typically show 1.5–2.7× more spend. This is NOT duplication — it's because WF includes non-supply-chain categories (pharma distributors ~12%, insurance ~10%, intercompany ~12%, staffing ~10%, IT ~4%, capital ~5%, food ~1%). After removing these via vendor name pattern matching, the residual gap is ~20%, explained by vendor hierarchy fragmentation and TSA overhead allocations.

**Broken fields in WF** (do NOT rely on):
- `health_system_entity_code`: 50% NULL, only 33 distinct values
- `direct_parent_entity_code`: 100% NULL (literal string `null`)
- `facility_entity_name`: 100% NULL
- Must use `health_system_name` for system-level joins (name-based mapping required)

### Warning: The "Wholesaler" Trap
In `report_builder`, the `source` or `vendor_name` columns often just say "WHOLESALER" or "Wholesaler".
*   **Resolution**: You **must** query the `wholesaler` column to get the actual name (e.g., "CARDINAL HEALTH", "MCKESSON").

## 2. Product Master: Who is the Manufacturer?
The `premier_primary_item_master` table contains records for both Manufacturers and Distributors.
*   **Problem**: A Distributor (e.g., "Morris & Dickson") will often be listed as the `manufacturer_name` for a product they distribute.
*   **Golden Rule**: To find the true OEM (Original Equipment Manufacturer), prioritize records where:
    1.  `vend_type = 'M'` (Manufacturer)
    2.  `pkg_uom = 'EA'` (Base Unit)

**SQL Pattern for Manufacturer Resolution**:
```sql
SELECT * FROM premier_primary_item_master
WHERE reference_number = '...'
ORDER BY 
    CASE WHEN vend_type = 'M' AND pkg_uom = 'EA' THEN 1 
         WHEN vend_type = 'M' THEN 2 
         ELSE 3 END
LIMIT 1
```

## 3. Safe Blinding of Facilities
Creating public-safe extracts requires converting sensitive IDs (Entity Codes) to blinded IDs (FAC_XXXX).
*   **Requirement**: IDs must be consistent across multiple extracts (Extract 1 vs Extract 2).
*   **Tool**: Use `tools/data-utilities/blinding_manager.py`.
    *   Do not write ad-hoc blinding scripts.
    *   The tool handles loading the map, finding *new* facilities in your data, assigning next-sequential IDs, and saving the map.

## 4. Query Parity Checklist
When combining Provider (TAE) and Wholesaler (RB) data, ensure schema parity:
*   [ ] **Date**: `FORMAT_DATE('%Y-%m', t.Transaction_Date)` vs `FORMAT_DATE('%Y-%m', PARSE_DATE('%Y-%m-%d', rb.invoice_date))`
*   [ ] **Vendor**: `t.Vendor_Name` vs `rb.wholesaler`
*   [ ] **Spend**: `t.Landed_Spend` vs `rb.total_spend`
*   [ ] **ID**: `t.Premier_Entity_Code` vs `rb.facility_id`

## 5. Pricing Waterfall Strategy
When looking for a "Price Benchmark," start here (Order of Operations):

1.  **Primary Benchmark**: `premier_primary_item_master.benchmark_median_price`.
    *   *Why*: The most reliable aggregation of what facilities actually pay. If this is NULL, proceed to step 2.

2.  **Drug List Price**: `premier_primary_item_master.drug_product_wac_price`.
    *   *Why*: If it is a drug, this is the Wholesale Acquisition Cost (List Price). Useful proxy if no benchmark exists.

3.  **Transaction History (Derived Contract Price)**:
    *   *Why*: If Master Data is empty, check actual facility purchasing history in `transaction_analysis_expanded`.
    *   *Columns to check*:
        *   `Base_Each_Price` (Check `Last_Base_Each_Price` or average).
        *   `Contract_Access_Price` (if checking specific contract availability).
        *   `Contract_Best_Price`.

## 6. Zero-Result Protocol
If a standard search (e.g. by mapped Reference Number or NDC) returns **zero** transaction rows, assume identifiers may be stripped/missing in the facility feed.

**Escalation Ladder:**
1.  **Identifier Search (Standard)**: Query by Mapped Reference Number and NDC (checking formatted vs unformatted).
2.  **Keyword Fallback (Critical)**: If #1 fails, search `Facility_Product_Description` using distinct brand/generic keywords (e.g. `%AMYVID%`, `%FLUTEMETAMOL%`).
    *   *Validation Required*: Verify the results by checking the `Vendor_Name` aligns with the known manufacturer/distributor (e.g. "Petnet", "Sofie Co").
    *   **Transparency Rule**: If you find data via this method, you **MUST** explicitly notify the user: "Standard identifiers (NDC/Ref #) yielded no results. Data was located via keyword text matching on descriptions." Do not present these results as ID-matched.
3.  **Rx vs Med-Surg Check**:
    *   Rx: Query `report_builder` by NDC.
    *   Med-Surg: Query `transaction_analysis_expanded` by Ref # or Keyword.

## 7. Pricing Analysis Heuristics
When deriving "Median Unit Price" from raw transaction data:
1.  **Blanket PO Detection**: Watch for high `Landed_Spend` with `Quantity <= 1`. These are often service contracts or blanket orders, not per-unit pricing.
    *   *Action*: Filter `WHERE Quantity > 0` (or `> 1` if noisy).
2.  **Use Robust Statistics**: Prefer `APPROX_QUANTILES(Unit_Price, 100)[OFFSET(50)]` over `AVG()`.
    *   *Why*: Transaction data contains extreme outliers (returns, corrections, bulk sums) that skew the mean.
3.  **Sanity Bounds**: Apply heuristic filters (e.g. `Unit_Price BETWEEN 100 AND 10000`) based on expected cost to strip data entry errors (e.g. price entered as quantity).

## 8. Market Insights / Self-Service Data Models
Premier provides a set of **self-service analytical models** (often called "Market Insights") that pre-aggregate purchasing data at the product/manufacturer/facility level.  These complement the raw transactional tables in §1 and are the foundation for benchmarking decks, GPO evaluation, and consulting extracts.

### Key tables

| Table | Grain | Primary Use |
| :--- | :--- | :--- |
| `provider_purchasing_txn` | Facility × Product × Month | Self-service transaction-level purchasing data; de-identified Entity Codes for external sharing |
| `ppt_stable_sample` | xref_group × Manufacturer × Month | Product penetration / market share with stable facility sample; ~1-month production lag vs live data |
| `week_xref_mfr_analysis` | xref_group × Manufacturer × Week | Weekly manufacturer breakdown by product group |
| `supply_signals_week_refnum` | Reference Number × Week | Weekly product-level supply signals (e.g. shortage indicators, sourcing shifts) |

### The `xref_group` concept
Products are grouped into **xref_groups** — cross-reference groups that represent clinically equivalent product families (e.g., all brands/generics of a particular surgical glove size).

*   A single `xref_group` may contain dozens of individual Reference Numbers from different manufacturers.
*   This is the fundamental unit for market share analysis: "what % of this product group does Manufacturer X capture?"
*   The `xref_group` label itself is a text description (e.g., "GLOVE EXAM NITRILE PF SM") — not a numeric ID.

### 4-level product taxonomy
The Market Insights models organize products into a hierarchy:

1.  **Category** — Broadest grouping (e.g., "SURGICAL SUPPLIES")
2.  **Sub-Category** — Mid-level (e.g., "GLOVES")
3.  **xref_group** — Clinically equivalent product family
4.  **Reference Number** — Individual SKU / catalog number

When building extracts or analyses, decide which level is appropriate:
- **Category/Sub-Category**: Executive dashboards, high-level spend allocation
- **xref_group**: Competitive benchmarking, manufacturer market share, contract evaluation
- **Reference Number**: Product-level pricing, compliance audits, specific item sourcing

### Stable sample methodology (`ppt_stable_sample`)
This table uses a *stable sample* of facilities — meaning the set of contributing facilities is held constant over a rolling period to enable apples-to-apples trending.

*   **Production lag**: Expect ~1 month delay.  If the current month is February, the latest data may only go through December or January.
*   **Coverage**: Not all facilities report in every period; the stable sample controls for this by only including facilities with consistent reporting.
*   **Columns of note**: `pct_penetration`, `total_spend`, `total_units`, `facility_count`, `mfr_name`, `xref_group`

### De-identified facilities (self-service / external sharing)
When data is shared externally (e.g., consulting extracts for McKinsey, Bain):
*   Entity Codes are replaced with blinded IDs (e.g., `FAC_0001`, `FAC_0002`).
*   Blinding must be **consistent across multiple extracts** — same facility always gets the same blinded ID.
*   Use `tools/data-utilities/blinding_manager.py` (see §3 above) for blinding operations.
*   The `provider_purchasing_txn` table already uses de-identified entity codes in its self-service variant — check which variant you're querying before applying additional blinding.

### Trending / consistency checks
When profiling Market Insights data:
1.  Check **date range** coverage per table — are there gaps or trailing-edge partial months?
2.  Check **weekly continuity** (for `week_xref_mfr_analysis` and `supply_signals_week_refnum`) — are all ISO weeks present with no gaps?
3.  Compare **stable sample lag** (`ppt_stable_sample`) against live transactional data (`provider_purchasing_txn`) — the stable sample is expected to trail by ~1 month.
4.  Validate **row count stability** — large week-over-week swings in row count may indicate feed issues.
