# HCIQ Benchmark Analysis Methodology

## Objective
Provide an executive-level benchmark positioning that maps 6 months of transaction spend against Healthcare IQ (HCIQ) pricing benchmarks for specific Premier contract portfolios: National (PP), Ascend Drive (AD), and Surpass (SP).

## 1. Data Staging & Filtering
- **Scope**: Transactions within the last 6 months.
- **Exclusions**: Facilities marked as TEST, DEMO, or otherwise non-eligible.
- **Base Fields**: `Reference_Number`, `Quantity_in_Eaches`, `Base_Spend`, and contextual fields (Facility, Contract_Number, Contract_Type).

## 2. Resolving "Local Spend Masking"
- **Facility Program Mapping**: Identified which Premier portfolio (PP, AD, SP) each facility most frequently utilizes based on historical transaction volume.
- **Local Override**: Transactions marked as `LOCAL` or `REGIONAL` were remapped to the facility's implicitly eligible generic Premier portfolio to ensure total volume is accurately captured.

## 3. Best Price Resolution
- **Strategy**: For each Premier contract and reference item, the most frequent "Best Tier" price was extracted.
- **Conflict Handling**: In cases where multiple best prices existed for the same reference item (e.g., overriding price tiers), the row with the largest total transaction volume was selected as the representative best price. Contracts with unresolved discrepancies flag `MULTIPLE_BEST_PRICES`.

## 4. Benchmark Join and Interpretation
- **Join Key**: Matched transactions to HCIQ benchmarks via `Reference_Number`.
- **Percentile Inversion**: In accordance with HCIQ definitions, higher percentiles represent better (lower) pricing. 
  - HCIQ 90th percentile (`hciq_90_benchmark`) = Lowest Price = Target Spend P10
  - HCIQ 75th percentile (`hciq_75_benchmark`) = Target Spend P25
  - HCIQ 50th percentile (`hciq_50_benchmark`) = Target Spend P50
  - HCIQ High benchmark = Highest Price = Target Spend ^90

## 5. Summary Generation & Percentile Bucketing
- **Tab B (Item Drilldown)**: Extended spend calculated by multiplying transaction unit volume (`Quantity_in_Eaches`) by each corresponding HCIQ benchmark tier price and the actual best tier Premier price.
- **Tab A (Contract Summary)**: Aggregated item-level spend to the contract level. Contracts were assigned a `Percentile_Bucket` based on where the `Spend_at_Best_Tier` fell along the HCIQ target spend curve.
  - **Buckets**: `<=10th`, `10-25`, `25-50`, `50-90`, `>=90th`.
  - **Estimated Percentile (Linear)**: Used linear interpolation between the benchmark spend tiers to estimate an exact percentile metric.

## 6. QA Flags and Coverage
- **Coverage Minimum**: Identified contracts where total spend matching an HCIQ benchmark accounted for fewer than 80% of total spend. Flagged as `LOW_COVERAGE`.
- **Tab C (QA Flags)**: Exceptions summary showing contracts requiring review due to coverage gaps or price ambiguity.