# Known Data Traps & QA Heuristics

This file acts as the persistent learning memory for the Out-of-Band Validation Agent. Whenever a new class of logic error or business-plausibility trap is found, it should be generalized and appended here so the agent can actively check for it in future validations across all projects.

### 1. The "$0 Target" Inflation Risk
*   **Context:** Upstream benchmarks may be missing, prompting the pipeline to default them to `$0.00`.
*   **Trap:** If an executive dashboard calculates `Historical Spend - Target Spend = Savings`, lines missing a benchmark will falsely simulate 100% savings. 
*   **Check:** Verify that rows with exactly $0 in target formulas are truly $0, and not just Unbenchmarked/NULL masquerading as zero.

### 2. Unit of Measure (UOM) Scaling Anomalies
*   **Context:** Historical spend and quantities often sit in a "purchasing" UOM (like Cases or Eaches), while price benchmarks might sit in a completely different UOM.
*   **Trap:** The multiplication of unmatched UOMs (e.g., matching a Case price to an Eaches volume) will result in structurally valid but mathematically impossible multi-million dollar variations.
*   **Check:** Look for extreme orders of magnitude differences between `Historical_Price` and `Benchmark_Price` (e.g., >3x or <0.33x variance). Flag items where `Volume * Benchmark_Price` explodes into astronomical totals. 

### 3. Aggregate vs. Item-Level Incongruity
*   **Context:** A rollup/summary tab might average or weight a percentile score across an entire group or contract.
*   **Trap:** A Contract might look terrible overall ("not competitive") at the summary level, but when you look at the item drilldown, the handful of items that *actually have benchmarks* are highly competitive. This means the summary metric is making broad, poorly-weighted assumptions based on incomplete item-level coverage.
*   **Check:** Ensure aggregate weighting explicitly divides against the *benchmarkable subset* (e.g., `Benchmarked_Spend`), not the total overall denominator. Cross-check random contract aggregates against their individual item drilldowns to see if the semantic narrative aligns.

### 4. Semantic Matching Disconnects
*   **Context:** Joins based on imperfect string matching or cross-walking reference numbers.
*   **Trap:** A string similarity matching process might map a high-volume item to a completely unrelated benchmark because of a matching sequence string, fundamentally destroying the accuracy.
*   **Check:** Sample cross-check Product Descriptions between the local file and the benchmark reference (if provided) for semantic mismatch.