# July 1+ Contract Competitive Heat Map (Executive View)

## Goal
Show Bruce which expiring national contracts (Jul–Dec 2026) have the biggest dollar-valued pricing gaps versus HCIQ benchmarks, ranked by opportunity size based on Joe's proposed targets.

## Methodology
- Leveraged the validated `contract_item_benchmark_summary` dataform model.
- Mapped expiration dates continuously from the root `transaction_analysis_expanded` table.
- Gated to contracts expiring between `2026-07-01` and `2026-12-31`.
- Calculated unit gaps explicitly substituting Joe's target tiers per line item:
  - **Surpass (SP)**: `hciq_low_benchmark`
  - **Ascend Drive (AD)**: `hciq_90_benchmark` (10th percentile equivalent)
  - **National (PP)**: `hciq_75_benchmark` (25th percentile equivalent)
- Opportunity modeled strictly (no negative upside dilution): `Max(0, current_price - target_price) * units_6mo`.
- Extrapolated metrics to Annualized figures (6-month rate * 2) aligned to Bruce's portfolio goals.
- Reduced output deliverable exclusively to 'Program Summary' and 'Top 50 Contract Opportunities'.

## Key Outcomes
- **266** matched national/AD/SP expiring contracts (Jul–Dec 2026).
- **$2.75B** in Annualized Benchmarked Spend on these expiries.
- **$415M** Total Annualized Savings Opportunity if re-contracted purely at Joe's targets.
- Saved strictly formatted executive cut at `runs/2026-03-04__portfolio-competitiveness/Contract_Competitive_Heat_Map.xlsx`.