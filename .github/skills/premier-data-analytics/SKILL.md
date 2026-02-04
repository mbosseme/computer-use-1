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
