# Audit Report: Healthcare IQ Benchmark Analysis

## 0) Re-Grounding & Data Understanding
- **Briefing Alignment:** The core goal is mapping Premier contracts (National, Ascend Drive, Surpass) against HCIQ percentile pricing to deliver a "percentile positioning" score (e.g. `<=10th`, `10-25th`, etc.) at the contract level for an executive review. Exclusions include dropping `TEST`/`DEMO` facilities, correctly processing non-null volumes (`Quantity_in_Eaches`), and ensuring the analysis only relies on Premier's "top tier" price per item.
- **Grain:** 
  - Source data (`transaction_analysis_expanded`) is line-item transaction level representing specific items on purchase orders. 
  - `contract_item_benchmark_summary` rolls this up to the `Contract x Product` grain over a 6-month trailing window.
  - `contract_benchmark_summary` is aggregated one level further to the `Contract` grain.
- **Join Mechanics:** Transaction products are linked to HCIQ benchmark data strictly via the `Reference_Number` mapping to the `matched_reference_number` stored in HCIQ models.
- **Percentile Reality Check:** The HCIQ 90th percentile price implies the *lowest* market price. Correspondingly, if our total extended contract spend using the premier contract best tier is *below* the `Target_Spend_P10` (which is derived from `Quantity * hciq_90_benchmark`), we correctly bin this into the `<=10th` percentile bucket as we are beating top-decile market prices.

## 1) Data Exploration & Pipeline QA
- **Sizing:** The initial staging query ingested 48.13M rows representing ~$52.6B in total 6-month transaction spend. 
- **Contract Type & Remapping:** 
  - Over $7.85B in standard portfolio spend correctly matched `PREMIER`/`SURPASS`/`ASCENDRIVE`. There were 3.9M transactions worth $2.83B labeled as `LOCAL`.
  - The pipeline dynamically attributes local matches by first assigning priority programs to each facility via historical transaction inference (`Surpass > Ascend > National`) and looking up the equivalent `contract_best_price` mapping for that product in the appropriate program, yielding a combined `Attributed_Contract_Number`. I verified the remap successfully executes and keeps local spend inside the Premier visibility net.
  - **Audit Action Taken:** New transparency columns (`Match_Contexts`, `Original_Contract_Types`) were added specifically to the Tab B model to fulfill Matt's requirement to *"Keep the original match context available in drilldown"*.
- **Benchmark Join Rates:**
  - Roughly 187k product-contract combinations joined a valid benchmark.
  - Of the ~$31B falling under our focused portfolios (PP, AD, SP), a massive **$30.49 Billion is successfully benchmarked**, reflecting a **~98.3%** coverage rate by spend.
- **Tier Analysis:**
  - Extracted the modal highest-frequency best tier per item, explicitly masking out `LOCAL`/`REGIONAL` and isolating strings matching `LIKE '%TIER%' OR NOT LIKE '%LOCAL%'`. Only a tiny fraction ($669k) of spend had Null `Contract_Best_Price`, properly filtered from `contract_item_best_price` resolution.
  - Exception paths with multiple competing tier prices are highlighted in the `flag_multiple_best_prices` field. Tab C surfaces these correctly.
  
## 2) Output Verification (Spot Checking against BigQuery)
- **High Performance (Cheaper `<=10th`):** Contracts like `PP-OR-2071` report an actual $10.43M best tier spend versus an HCIQ P10 target at $10.74M. Output maps to `<=10th`. Logic holds exactly.
- **Low Performance (Pricier `>=90th`):** Contracts like `PP-NS-2136` show $8.98M in best tier spend against a high-tier HCIQ bound of $5.79M. Output is mapped to `>=90th`. Logic holds exactly.
- **Coverage Ratio Constraints:** Calculated `IF(Total_Spend>0, Benchmarked_Spend/Total_Spend, 0)` generates precise ratios matching the Excel thresholds. Tab C reliably captures all `< 0.8` (80%) thresholds. 

## 3) Conclusion & Deliverable Fixes
The underlying pipeline and outputs are structurally sound and abide strictly by the constraint logic established in the brief.

**Actions taken during audit:**
1. Explicitly corrected an oversight where `Original_Contract_Type` and `Match_Context` were not being pushed through the final aggregated layers. Tab B explicitly shows this breakdown (`DIRECT_MATCH` or `REMAPPED_LOCAL`) so users can audit how spending was shifted under the respective portfolios.
2. Regenerated the BigQuery Tables executing Dataform via terminal.
3. Reran Python extraction script overriding `HCIQ_Benchmark_Analysis_Deliverable.xlsx` with the updated transparency flags.
4. Validated the new Contract_Name parameter carried through smoothly across all tabs.