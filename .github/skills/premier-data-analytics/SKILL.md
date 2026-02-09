# Skill: Premier Data Analytics

**Status**: Recommended / Core
**Context**: Use when extracting or analyzing Premier purchasing data (`transaction_analysis_expanded`, `report_builder`) and enriching it with `premier_primary_item_master`.

## 1. The "Dual-Source" Reality
Purchasing data exists in two parallel universes. Use both for complete coverage.

| Feature | Provider Feed (`transaction_analysis_expanded`) | Wholesaler Feed (`report_builder`) |
| :--- | :--- | :--- |
| **Source** | ERP / Accounts Payable (Direct) | Distributor Sales Tracings (Indirect) |
| **Scope** | Acute Care / Large IDNs | Physician Offices / Non-Acute / Pharmacy |
| **Date Field** | `Transaction_Date` (PO Date) | `invoice_date` (Sale Date) |
| **Vendor Field** | `Vendor_Name` | **`wholesaler`** (Specific) / `source` (Generic) |

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

