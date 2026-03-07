Subject: Re: HCIQ Benchmark Analysis Deliverable - Data Review

Hi Brian and Joe,

Thanks for taking the time to review the initial output and for flagging those anomalies, Brian. I've done a thorough pass through the entire pipeline — both fixing the issues you identified and stress-testing the methodology end to end. Here is a summary of everything that changed:

---

**1. Supplier Mismatch on NS-2131 Contracts (MVAP / Performance Health vs. Cardinal)**
*   **What you found:** The supplier column on several NS-2131 contracts showed MVAP Medical Supply instead of Cardinal Health.
*   **Root cause:** When local and regional contract spend gets remapped up into the national NS-2131 contract buckets to capture full volume, the original distributor names carried over. The summary logic was then arbitrarily picking the alphabetically highest supplier name (MVAP) instead of the one actually driving transaction volume.
*   **Fix:** Updated the grouping logic to elect the primary supplier based on total transaction volume. Cardinal Health now correctly appears.

**2. Surpass Benchmark Skew ($394 benchmark on a $0.01 bandage)**
*   **What you found:** A bandage line priced at pennies was showing a $394 benchmark, which made no sense.
*   **Root cause:** An improper product match in the HCIQ benchmark file. One manufacturer's record with an identical part number was matched to the wrong reference number, causing the bandage to inherit the catheter's benchmark pricing. This isn't a systemic issue — one or two bad matches on a file of this size is expected.
*   **Fix:** Tightened the join to require an exact match on both reference number and manufacturer catalog number. This eliminated the false match with virtually zero impact on total benchmark coverage (0.03% drop).

**3. UOM Data Quality Flagging System (new)**

This is the biggest methodological improvement. During the review, we identified that unit-of-measure mismatches between contract pricing and HCIQ benchmark data were systematically distorting the percentile calculations. We built a four-tier flagging system:

| Flag | Rule | Effect |
|---|---|---|
| `PRICE_QTY_UOM_MISMATCH` | Contract_Price × Qty / Actual_Spend > 10× | **Excluded** — pricing on the contract and quantity on the purchase use different UOM bases, which inflates the quantity and therefore overall contract volume, giving those items improper influence on the weighted percentile figure |
| `CRITICAL_UOM_MISMATCH` | Contract_Price / Benchmark_50th > 10× or < 0.1× | **Excluded** — order-of-magnitude gap, almost certainly a UOM issue |
| `HIGH_VARIANCE_EXCLUDED` | Contract_Price / Benchmark_50th > 3× or < ⅓ | **Excluded** — too extreme to defensibly benchmark |
| `MODERATE_VARIANCE` | Contract_Price / Benchmark_50th > 1.7× or < 0.59× | **Included but flagged** — may warrant category-level review |

Items flagged `OK` or `MODERATE_VARIANCE` remain in the benchmark calculations. Items flagged `CRITICAL`, `HIGH_VARIANCE_EXCLUDED`, or `PRICE_QTY` are removed from both sides of the comparison (best-tier spend and target spend) so they don't distort the contract's percentile position.

The 3× / ⅓ threshold for `HIGH_VARIANCE_EXCLUDED` was chosen to allow legitimate pricing variance (contract prices genuinely 70–200% above median market are common in specialty categories) while excluding items where the gap is so extreme that it almost certainly reflects a data mismatch rather than a real pricing position.

We can certainly tighten up further in this area — particularly around the UOM-related flags — and it may have a few additional percentage points of influence on the overall percentile assessment.

**4. Spend_at_Best_Tier consistency guard (new)**

Previously, an item excluded from benchmarking (e.g., CRITICAL UOM mismatch) would still contribute its inflated contract price to the contract-level Spend_at_Best_Tier total while contributing zero to the target spend comparison. This asymmetry was silently dragging contracts into worse percentile buckets. The pipeline now ensures only benchmarked items contribute to both sides of the percentile calculation.

**5. Excel formatting**

Unit prices throughout the workbook now display with 3 decimal places for precision. Spend/dollar columns remain formatted as whole-dollar amounts.

---

**Updated headline numbers:**

| Program | Avg Percentile | Weighted Avg Percentile |
|---|---|---|
| Surpass | 67th | 68th |
| Ascend Drive | 56th | 53rd |
| National | 42nd | 46th |

The tier story holds: Surpass contracts consistently outperform National and Ascend Drive contracts across comparable categories, validating the commitment-tier pricing model.

I've regenerated the deliverable with all of these changes applied. Methodology documentation is included in Tab E.

**One additional observation worth flagging:** there is a substantial gap between what members actually pay (their real transaction spend) and what our best-tier contract price would estimate. In many cases, members are paying well below the best available GPO tier. This gap is likely driven primarily by locally negotiated pricing — members securing better rates outside the GPO contract — and the size of that gap is itself a useful signal about how much local negotiation is happening across the portfolio. That said, there may be other factors in the data we haven't fully accounted for yet (e.g., invoice prices vs. PO prices, rebate adjustments, etc.). The core comparison of our best tier contract price against the HCIQ benchmarks remains valid and is still an accurate assessment of the strength of our actual contract pricing. But there's more to dig into around why actual member spend is as low as it is, and whether it can truly be explained by local agreements alone.

Let me know when you're ready for the updated file, or if you'd like to walk through any of this in more detail.

Thanks,
Matt