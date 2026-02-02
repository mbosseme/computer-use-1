# Skill: Product Entity Resolution

**Status**: Experimental / v1
**Context**: Use this skill when you have a list of products (from emails, PDFs, or external spreadsheets) identified by non-standard or "messy" IDs (NDCs, Model Numbers, Vendor Part Numbers) and need to map them to a canonical internal Reference Number (Ref #) in the Master Data.

## 1. The Entity Resolution Ladder

Do not jump straight to manual searching. Follow this ladder of decreasing specificity:

### A. Direct Exact Match
**Goal**: Quick hit on known keys.
**Action**:
1. Join your input list against `master_data` tables.
2. Try keys: `original_ndc`, `upc`, `manufacturer_catalog_number`, `reference_number`.
3. Normalize separators (remove dashes `-`, spaces, leading zeros) and try again.

### B. "Bridge Identifier" Search (Web-Augmented)
**Goal**: Find an identifier that *is* likely in the database (e.g., a Manufacturer Catalog Number) when the one you have (e.g., an obscure NDC or Vendor SKU) is not.
**Action**:
1. Perform a web search for the "messy" ID you have (e.g., `NDC 65219-497-20`).
2. Extract **Product Details**:
   - **Manufacturer Catalog Number** (crucial)
   - **Model Number**
   - **Description/Volume/Size**
3. Use those extracted "Bridge Identifiers" to query the database.

### C. Bridge Table Lookup (Transaction History)
**Goal**: Use historical transaction data to find the link. Master Data tables are often "clean" and missing weird vendor aliases. Transaction tables (`transaction_analysis`, `invoice_history`) contain the "messy" vendor numbers side-by-side with the resolved internal Reference Number.
**Action**:
1. Identify a "Bridge Table" (e.g., `transaction_analysis_expanded`).
2. Query it using the "Bridge Identifiers" found in step B (or the original ID).
3. Select `reference_number`, `facility_vendor_catalog_num`, `manufacturer_catalog_number`, `facility_product_description`.
4. **Validation**: Check `facility_product_description` to ensure it matches your target product.

### D. Pattern Inference (The "Format Shift")
**Goal**: Solve for IDs that are *almost* a match but transformed.
**Action**:
1. Observe successful matches from Step C.
   - Example: Input `495-10` matched Facility Vendor ID `495010`.
   - Pattern: `[Middle]-[Suffix]` -> `[Middle][0][Suffix]`.
2. Apply this transformation to remaining unmatched items.
   - Hypothesis: Input `497-20` -> Search `497020`.
3. Test hypothesis in the Bridge Table.

## 2. Validation & Safety

*   **Description Check**: Always cross-reference the `description` found in the database with the known product description.
    *   *Bad Match*: NDC for "Saline" maps to Ref # for "Dextrose".
    *   *Good Match*: NDC for "Sterile Water 1000ml" maps to Ref # for "Sterile Water" (even if brand varies slightly).
*   **One-to-Many Warning**: If a single external ID maps to multiple internal Ref IDs:
    *   Prioritize the one with the highest transaction volume (count).
    *   Or flag for manual review.

## 3. SQL Query Templates

### Bridge Table Lookup
```sql
SELECT 
    reference_number, 
    facility_vendor_catalog_num, 
    manufacturer_catalog_number,
    facility_product_description,
    COUNT(*) as freq
FROM \`abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded\`
WHERE 
    -- Search by known catalog numbers from web search
    manufacturer_catalog_number IN ('EXTRACTED_CAT_1', 'EXTRACTED_CAT_2')
    OR 
    -- Search by facility/vendor numbers (often contain the "messy" variations)
    facility_vendor_catalog_num IN ('EXTRACTED_CAT_1', 'INFERRED_PATTERN_1')
GROUP BY 1, 2, 3, 4
ORDER BY freq DESC
LIMIT 50
```

## 4. Recovery Rules

*   **No Match in Bridge Table?**:
    *   Broaden search: Query for the *Description* string using `LIKE '%KEYWORD%'` to find typical Reference Numbers for that product type, then work backward to see if any have a matching catalog number variant.
*   **Too Many Matches?**:
    *   Narrow by `manufacturer` or `vendor_name` if available in the input.
