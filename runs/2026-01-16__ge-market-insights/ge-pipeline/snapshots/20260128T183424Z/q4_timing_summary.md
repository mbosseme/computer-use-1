# Q4 timing reconciliation (Supplier vs Provider)

Window: 2023-10-01 through 2025-09-30 (calendar quarters; Q4 = Oct–Dec).

This summarizes why Calendar Q4 can look low in provider-reported transactional insights even when supplier-reported spend shows a strong Q4. Provider timing here is based strictly on `Transaction_Date` (ERP operational timing), not revenue/invoice timing.

## What the data shows (GE bucket)

- Supplier: 2024-Q4 vs 2024-Q3: $74.6M vs $65.0M (14.8% uplift)
- Provider: 2025-Q1 vs 2024-Q4: $52.5M vs $33.0M (59.2% rebound)
- Provider vs Supplier in 2024-Q4: provider is 44.2% of supplier (same quarter, GE bucket)
- Supplier: 2024 Q4 share of 2024 total: 30.5%
- Provider: 2024 Q4 share of 2024 total: 21.5%
- Provider monthly diagnostic (GE): Jan 2025 / Dec 2024: 1.20x
- System variability (top 75 systems): median Jan/Dec (2024 season): 0.63x
- System variability: % systems with Jan > Dec (2024 season): 44.6% (and 35.4% with Jan > 1.5× Dec)

## Interpretation (timing mechanics)

Taken together, the pattern is consistent with a timing shift in provider ERP transaction capture around year-end: Q4 looks suppressed in provider `Transaction_Date` while Q1 rebounds, even when the supplier spend proxy shows Q4 strength. This should be communicated as a *timing reconciliation* issue, not automatically a demand decline.

## Constraints / what we are NOT claiming
- No attempt is made to separate PO date vs invoice date vs install date.
- Provider timing is based strictly on `Transaction_Date` (operational timing), not revenue timing.
- System-level results are summarized by `Health_System_Entity_Code` only (no names exported).

