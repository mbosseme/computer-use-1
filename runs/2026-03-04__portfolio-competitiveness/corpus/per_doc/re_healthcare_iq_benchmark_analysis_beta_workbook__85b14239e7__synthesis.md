# Synthesis: RE: Healthcare IQ Benchmark Analysis - Beta Workbook.pdf

Generated on: 2026-03-06

## Coverage / Limit Warnings
- None

## Extraction Stats
- Pages total: 4
- Pages de-duplicated (identical extraction): 0
- Pages with text: 4
- Pages with extraction errors: 0
- Total extracted chars: 10821

## Chunking Stats
- Chunks: 1
- target_chunk_chars: 30000
- max_chunk_chars: 45000
- overlap_pages: 1
- max_chunks: None
- page_timeout_s: 15

---
# Executive Summary

- Matt Bossemeyer completed a review and update of the **Healthcare IQ Benchmark Analysis - Beta Workbook** after Brian Hall identified several anomalies in the initial output.
- The most important data correction was for **NS-2131 supplier mapping**: the primary supplier is now selected using **total transaction volume**, which correctly results in **Cardinal Health** appearing as the contracted supplier.
- A key benchmark-matching issue was fixed by requiring an **exact match on both reference number and manufacturer catalog number**, which resolved an implausible low-cost bandage benchmark issue with **minimal benchmark coverage impact (0.03% drop)**.
- The team added a **four-tier UOM/data-quality flagging framework** to identify likely unit-of-measure or benchmark mismatches and exclude certain items from percentile calculations where appropriate.
- Methodology was further tightened so that excluded items do not distort contract-level results: only **benchmarked items** now contribute to **Spend_at_Best_Tier** and target spend in percentile calculations.
- Workbook presentation was improved, including **3 decimal places for unit prices** and **whole dollars for spend/dollar fields**, with methodology documentation included in **Tab E**.
- Updated headline benchmark results were confirmed as:
  - **Surpass:** Avg Percentile **67th**, Weighted Avg Percentile **68th**
  - **Ascend Drive:** Avg Percentile **56th**, Weighted Avg Percentile **53rd**
  - **National:** Avg Percentile **42nd**, Weighted Avg Percentile **46th**
- A major unresolved issue remains: why **actual member transaction spend appears materially below best-tier contract price estimates**. Possible explanations raised include **locally negotiated pricing, invoice vs. PO prices, rebates, or other unknown factors**.
- Brian remained concerned that presenting an aggregate result such as **Surpass at the 66th/67th percentile** could create a **misleading or negative message**, given contract structure nuances and potential rebate effects.
- The updated deliverable has been **regenerated and saved to OneDrive** for further review by **Brian Hall and Joe Bichler**.

# Meeting Context

This discussion centered on a review of the **Healthcare IQ Benchmark Analysis - Beta Workbook**, prompted by concerns Brian Hall raised about specific anomalies and the overall interpretation of results.

Matt Bossemeyer revisited the workbook and underlying pipeline, made targeted corrections, regenerated the deliverable, and documented the methodology in **Tab E**. The workbook structure referenced in the discussion is:

- **Tab A:** Program Summary  
- **Tab B:** Contract Summary  
- **Tab C:** Item Drilldown  
- **Tab D:** QA Flags  
- **Tab E:** Methodology  

Earlier workbook enhancements also included:

- Adding **Weighted_Avg_Program_Percentile** to **Tab A**
- Updating **Tab B** to show **Contracted_Supplier**
- Reframing **Tab C** to include **supplier** and **manufacturer** fields

The conversation appears to be part data QA, part methodology validation, and part messaging review for how the benchmark results should be interpreted and communicated.

# Key Decisions / Confirmations

- **NS-2131 supplier logic was corrected** to identify the primary supplier based on **total transaction volume**.
  - Confirmed outcome: **Cardinal Health now appears correctly**.
- **Benchmark matching logic was tightened** to require an **exact match on both reference number and manufacturer catalog number**.
  - This resolved the implausible benchmark issue for a low-cost bandage item.
- A **four-tier UOM/data-quality flagging system** was added to better identify likely mismatches:
  - **PRICE_QTY_UOM_MISMATCH**
  - **CRITICAL_UOM_MISMATCH**
  - **HIGH_VARIANCE_EXCLUDED**
  - **MODERATE_VARIANCE**
- Confirmed methodology change: items flagged as:
  - **CRITICAL_UOM_MISMATCH**
  - **HIGH_VARIANCE_EXCLUDED**
  - **PRICE_QTY_UOM_MISMATCH**
  
  are **removed from both sides of the comparison**.
- Confirmed methodology change: only **benchmarked items** contribute to:
  - **Spend_at_Best_Tier**
  - target spend used in percentile calculations
- Confirmed interpretation convention: **higher percentiles imply better (lower) target pricing**.
- Confirmed formatting updates:
  - **Unit prices** display with **3 decimal places**
  - **Spend/dollar columns** remain **whole dollars**
- Confirmed deliverable status:
  - Updated workbook was **regenerated**
  - Saved to **OneDrive**
  - Methodology included in **Tab E**
- Confirmed updated headline results:
  - **Surpass:** Avg Percentile **67th**, Weighted Avg Percentile **68th**
  - **Ascend Drive:** Avg Percentile **56th**, Weighted Avg Percentile **53rd**
  - **National:** Avg Percentile **42nd**, Weighted Avg Percentile **46th**

# Open Questions / Follow-ups

- What explains the **substantial gap between actual member transaction spend and estimated best-tier contract pricing**?
- Are lower actual member spend levels being driven by:
  - **locally negotiated pricing**
  - **invoice prices vs. PO prices**
  - **rebate adjustments**
  - **other unknown factors**
- How should the team **message aggregate percentile findings**, especially for **Surpass**, without creating a misleading negative impression?
- Should the **UOM/data-quality flagging logic** be tightened further, since Matt noted this area could still affect percentile assessments?
- **Brian Hall and Joe Bichler** need to review the updated file and provide follow-up feedback/questions.
- **Joe Bichler’s view** on Brian’s concerns is **unknown** from the provided summary.

# Risks / Dependencies

- **Interpretation / messaging risk:** Reporting a headline result such as **Surpass at the 67th percentile** may be directionally accurate under the methodology, but could be viewed as **misleading** if rebates, local deals, or other contract nuances are not reflected.
- **Data-quality dependency:** Percentile outputs remain dependent on the quality of **UOM alignment**, benchmark matching, and exclusion logic.
- **Pricing-logic dependency:** The unresolved gap between **actual spend** and **best-tier estimated spend** could materially affect how stakeholders interpret the benchmark results.
- **Stakeholder review dependency:** Next steps depend on **Brian Hall and Joe Bichler** reviewing the regenerated workbook and confirming whether the fixes address their concerns.
- **Residual methodology risk:** Even after the new exclusions and consistency guard, Matt indicated **UOM-related issues could still influence percentile assessments**.
- **Unknown external factors:** Potential effects from **rebates, locally negotiated pricing, or invoice-vs-PO differences** remain unverified.

# Suggested Next-Step Email

Subject: Updated HCIQ Benchmark Workbook Ready for Review

Hi Brian and Joe,

I’ve completed the latest pass on the Healthcare IQ Benchmark Analysis workbook and regenerated the updated file in OneDrive.

Key updates include:
- corrected **NS-2131 supplier mapping** so Cardinal Health now appears correctly
- tightened the **benchmark match logic** to require exact reference number + manufacturer catalog number
- added **UOM/data-quality flagging and exclusions**
- updated the percentile methodology so only benchmarked items contribute to **Spend_at_Best_Tier** and target spend

Current headline results are:
- **Surpass:** 67th avg / 68th weighted
- **Ascend Drive:** 56th avg / 53rd weighted
- **National:** 42nd avg / 46th weighted

Methodology details are documented in **Tab E**. Please review and let me know if you’d like to walk through the changes together, especially the remaining question around why actual member spend appears lower than best-tier estimates.

Thanks,  
Matt
