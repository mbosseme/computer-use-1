# Charity CT Product Presence: Validation Summary

**Date:** 2026-01-16  
**Focus:** Validation of specific GE CT product lines in the Premier transaction feed.

## 1. Search Strategy & Scope
To ensure maximum recall, we implemented a **"proof of absence"** search strategy that goes beyond standard classification:

*   **GE Gating:** Matches are restricted to GE products (Manufacturer/Vendor = GE). If manufacturer fields are blank, we infer GE presence from strong brand/catalog evidence.
*   **"Anywhere" Matching:** We search for product terms (e.g., "Revolution Apex", "Optima CT540") across **20 distinct identity fields**, including:
    *   Descriptions (Facility-submitted + Backfilled)
    *   Manufacturer & Vendor Names (Standard + Facility-submitted)
    *   Catalog Numbers (Contracted, Forecasted, Manufacturer, Vendor)
    *   Brand Names
*   **Safe Aliasing:** We include safe, token-bounded aliases (e.g., "REVO" for Revolution, "ELITE"/"EXTREME" for Frontier subtypes) to catch variations without false positives.

## 2. Findings Summary

### A. Confirmed Present (GE-Gated Evidence Found)
We found clear transaction evidence for the following lines. "Anywhere" counts include matches in descriptions or catalog numbers, even if not formally classified as "Computed Tomography" in the contract hierarchy.

*   **Revolution Family:** Apex, CT, CT ES, HD, Ascend, EVO, Maxima.
*   **Frontier:** "Revolution Frontier" is present, but typically appears without a subtype suffix (e.g., just "Frontier" or "Frontier Lift").
*   **Legacy/Other:** Discovery RT, Optima CT540, VCT Console Upgrades.
*   **Workstations:** AW Workstation, AW Server (Physical & Virtualized).

### B. No Evidence Found (Zero Matches Verified)
The following terms returned **0 matches** across all 20 searched fields in the GE-gated data slice (Oct 2023 – Sep 2025). This implies they are either absent from this slice of the market or not reported with these specific model identifiers.

*   **Revolution Frontier EX / EL:** While "Frontier" exists, the specific text tokens for "EX" (or "Extreme") and "EL" (or "Elite") do not appear in conjunction with Frontier.
    *   *Note:* These transactions likely roll up into the generic "Revolution Frontier" (unspecified) bucket.
*   **Optima CT520:** No evidence found for "CT520", "520 CT", or variants.
*   **CardioGraphe:** No evidence found for this specific brand trademark.

## 3. Data Dictionary Notes
*   **Backfilled Description:** We prioritize the standard `Product_Description`. If missing/unknown, we fall back to `Facility_Product_Description`.
*   **CT-Mapped:** A subset of "Anywhere" matches that also align with the `COMPUTED TOMOGRAPHY` contract category or have strong CT hierarchy cues. Discrepancies between "Anywhere" and "CT-Mapped" often indicate miscategorized capital equipment (e.g., accessories listed as MedSurg).

## 4. Validation Artifacts
*   **`ct_charity_presence_summary.csv`**: Main counts and spend metrics per term.
*   **`ct_charity_zero_match_discovery.csv`**: Detailed "0-match" proof, showing absence per field.
*   **`ct_charity_term_debug_samples.csv`**: Sample rows showing exactly which text strings triggered a match.
