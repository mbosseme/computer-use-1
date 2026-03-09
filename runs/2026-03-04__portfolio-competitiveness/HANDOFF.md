# Handoff Journal: 2026-03-04__portfolio-competitiveness

## Summary

## Verification

## Next steps

## Blockers

## Summary
- Created isolation directories and environment.
- Used `agent_tools/llm/summarize_incremental.py` to synthezise the 'Portfolio Competitiveness' folder.
- Successfully extracted content and produced aggregate synthesis for `Connect.pdf` and `Urgent Request.pdf`.

## Verification
- Executed incremental synthesizer successfully. 
- Validated `runs/<RUN_ID>/corpus/synthesis.md` and index generation.

## Next steps
- Ready for further requests on the newly synthesized context.

## Blockers
- None.
## Summary
- Leveraged `mcp_bigquery_execute_sql` to extract table schema and row profiling statistics for `premierinc-com-data.hciq_benchmarking.received_benchmarks`.
- Created a base dictionary markdown and injected queried statistics locally via python scripting and `update_dictionary.py`.

## Verification
- Data Dictionary successfully matches the layout/parameters of `transaction_analysis_expanded.md` and is saved at `docs/data_dictionaries/premierinc-com-data.hciq_benchmarking.received_benchmarks.md`.


---

## Session: 2026-03-04 (M365 Copilot Business Context Research)

### Summary
Conducted extensive business context research via M365 Copilot (GPT-5.2 Think, Work mode) across 3 multi-turn questions. All findings documented in `runs/2026-03-04__portfolio-competitiveness/BUSINESS_CONTEXT_RESEARCH.md`.

**Research questions answered:**
1. How are Premier PP/AD/SP contracts structured? What do REGIONAL/LOCAL/PREMIER contract types mean in `transaction_analysis_expanded`? Is excluding LOCAL/REGIONAL correct? Do HCIQ rebate exclusions matter?
2. How to infer SP/AD/PP tier from transaction data (columns/values)? What does the HCIQ PIA Review say about data definitions and methodological gaps?
3. Are prices gross or net of admin fees? Does HCIQ adjust for admin fees? What is the typical admin fee range by tier?

### Key Findings
- PREMIER vs SP/AD/PP: `Contract_Type = PREMIER` is national GPO scope; `Contract_Number` prefix (SP-/AD-/PP-) is the tier classifier
- Exclusion of LOCAL/REGIONAL is correct for national benchmarking; including them compresses percentiles artificially
- HCIQ is PO/invoice price only (POs sent to vendor, paid invoices); no rebates, no admin fee adjustment
- Admin fees are a separate billing process; not embedded in unit prices; both systems operate at the "price paid" layer
- Admin fee range: ~0.3% to 9% (common modeled baseline 2-3%); varies by category/commitment/program, not a fixed tier ordering
- UOM normalization differences (HCIQ requires UOM_FACTOR) can materially shift benchmark percentiles
- Required disclaimer language documented for all analysis outputs (3 variants: rebates, contract scope, tier classification)

### New Artifacts Created
- `runs/2026-03-04__portfolio-competitiveness/BUSINESS_CONTEXT_RESEARCH.md` -- Comprehensive research notes (11 sections)
- `runs/2026-03-04__portfolio-competitiveness/playwright-output/copilot-q2-complete.md` -- Raw Q2 Copilot snapshot
- `runs/2026-03-04__portfolio-competitiveness/playwright-output/copilot-q3-admin-fees.md` -- Raw Q3 Copilot snapshot
- `runs/2026-03-04__portfolio-competitiveness/playwright-output/briefing-doc-snapshot.md` -- Briefing doc Word snapshot

### Suggested Next Steps
1. Apply Contract_Number prefix logic (SP-/AD-/PP-) in Dataform pipeline to stratify by performance tier
2. Add admin fee + UOM caveat row to Excel Methodology tab
3. Validate Program_Line distinct values in production data
4. Run a "dual view" sensitivity -- PREMIER-only vs All Contracts -- to quantify percentile shift from LOCAL/REGIONAL exclusion

### Blockers
- None.
---

## Session: 2026-03-05 (Dataform Refinement and Output Formatting)

### Summary
Built out the full execution logic in BigQuery/Dataform mapping the `transaction_analysis_expanded` table against the `received_benchmarks` table and outputting a multi-tab deliverable via Python export. Handled iterative refinements around data anomalies (UOM drops) and final deliverable formatting.

**Major Deliverables & Fixes:**
1. **Dataform Build Out**:
   - `transaction_analysis_6mo`: Base clean 6-month historical view. Also implemented UOM drop logic to filter mathematical outliers (`Base_Each_Price = 1.0 AND Quantity_in_Eaches = Base_Spend`).
   - `received_benchmarks_stg`: Handled benchmark ingestion and implicit deduplication (via `QUALIFY ROW_NUMBER() OVER(PARTITION BY manufacturer_entity_code, manufacturer_catalog_number ORDER BY abi_snapshot_date DESC) = 1`).
   - Downstream mapped/merged views (`contract_item_best_price`, `contract_item_benchmark_summary`, `contract_benchmark_summary`, `program_benchmark_summary`).
2. **Data Pipeline Enhancements**:
   - Pulled `Contracted_Supplier`, `Manufacturer_Top_Parent_Name`, `Manufacturer_Name`, and `Manufacturer_Catalog_Number` through the whole pipeline into the final tab outputs.
   - Handled intentional transaction subsetting limiting output to purely `PP`, `AD`, and `SP` portfolios (mapping $12.6B raw spend vs $8.6B final eligible spend).
   - Produced weighted linear percentile logic (`Weighted_Avg_Program_Percentile`).
3. **Python Execution Pipeline**:
   - Scaled out Python export scripting (`scripts/export_deliverable.py`) to systematically apply precise openpyxl formatting (`0%`, `$`, `0`) explicitly and implemented conditional red-yellow-green formatting bars for estimated benchmark percentiles. 
4. **Drafted Communication**:
   - Formally wrote out the `METHODOLOGY.md` rules and compiled them directly into Tab E of the delivery Excel workbook.
   - Pushed a locally staged Outlook Draft mapping the context.

### Next Steps / Standing Assumptions for New Agent:
- The codebase state is currently complete, committed, and stable. You do not need to restart or run `dataform compile/run` unless the user implicitly requests schema changes. 
- The project structure pushes `transaction_analysis_expanded` and `received_benchmarks` through Dataform -> Python -> Excel Output (`HCIQ_Benchmark_Analysis_Deliverable.xlsx`). 

### Blockers
- None.

---

## Session: 2026-03-06 (Critical Review, UOM Refinement, Email Finalization)

### Summary
Performed a deep critical review of the deliverable, refined the UOM flagging methodology, fixed a subtle but impactful consistency bug, improved Excel formatting, and finalized a reply-all email draft to Brian Hall / Joe via Outlook Graph API.

### Key Decisions & Rationale

1. **Contract_Best_Price is the correct metric (validated)**
   - Agent initially questioned whether `Contract_Best_Price` (best GPO tier price) was a ceiling vs. actual member price.
   - Matt clarified: Contract_Best_Price IS the best GPO tier price. When members pay less, they are locally negotiating outside the GPO — which is exactly the dynamic this analysis surfaces. This is a feature, not a bug.

2. **UOM Flag Thresholds — 4-tier system (refined from 3)**
   - Old system: PRICE_QTY_UOM_MISMATCH (>10x), CRITICAL_UOM_MISMATCH (>10x/<0.1x), HIGH_VARIANCE_WARNING (>1.7x/<0.59x), OK
   - New system:
     - `PRICE_QTY_UOM_MISMATCH` (>10x qty×price/spend) — excluded
     - `CRITICAL_UOM_MISMATCH` (>10x or <0.1x price ratio) — excluded
     - `HIGH_VARIANCE_EXCLUDED` (>3x or <0.333x price ratio) — **NEW, excluded**
     - `MODERATE_VARIANCE` (>1.7x or <0.59x price ratio) — **renamed** from HIGH_VARIANCE_WARNING, **still benchmarked**
     - `OK` — benchmarked
   - Matt's rationale: "Unless the actual price paid is less than a third or more than three times what was paid, we shouldn't eliminate it automatically."

3. **Spend_at_Best_Tier consistency fix (bug found and fixed)**
   - After implementing new thresholds, initial numbers went DOWN (Surpass 64→62). Root cause: excluded items still contributed inflated `Spend_at_Best_Tier` to the numerator while contributing zero target spend.
   - Fix: `contract_benchmark_summary.sqlx` changed from `SUM(Spend_at_Best_Tier)` to `SUM(CASE WHEN is_benchmarked THEN Spend_at_Best_Tier ELSE 0 END)`.
   - After fix, numbers moved correctly upward: Surpass 64→68, AD 47→53, National 39→46.

4. **Member actual spend gap**
   - Observation: members consistently pay LESS than Contract_Best_Price (locally negotiated pricing). This is a separate research question for later, not a methodology flaw.

### Final Numbers
| Program | Avg Percentile | Weighted Percentile |
|---------|---------------|---------------------|
| Surpass | 67th | 68th |
| AD | 56th | 53rd |
| National | 42nd | 46th |

### Files Modified
- `dataform/definitions/models/contract_item_benchmark_summary.sqlx` — 4-tier UOM flag, updated is_benchmarked, spend guards at 3x/0.333x
- `dataform/definitions/models/contract_benchmark_summary.sqlx` — Spend_at_Best_Tier gated by is_benchmarked
- `scripts/export_deliverable.py` — 3-decimal price formatting (`price_format`)
- `runs/.../METHODOLOGY.md` — Section 6 updated with 5-row flag table and Spend_at_Best_Tier guard note
- `runs/.../draft_email_to_brian.md` — Finalized email reply content
- `runs/.../create_reply_draft.py` — Script to create Outlook reply-all draft via Graph API
- `runs/.../find_thread.py` — Utility to search HCIQ email thread

### Email Thread
- Found 3 messages: original send (Matt, Mar 5 12:56), Matt's reply (Mar 5 15:27), Brian's reply (Mar 5 21:56)
- Reply-all draft created against Brian's latest message
- Email covers: supplier fix, benchmark skew fix, UOM flagging, consistency guard, Excel formatting, member spend gap observation

### Deliverable Stats
- Tab A (Program Summary): 3 rows
- Tab B (Contract Summary): 1,781 rows
- Tab C (Item Drilldown): 198,375 rows
- Tab D (QA Flags): 558 rows
- Tab E (Methodology): embedded markdown

### Next Steps
- Matt reviews and sends the Outlook draft
- Member actual spend vs. Contract_Best_Price gap is a separate follow-up investigation
- Further tightening of variance thresholds possible but deferred pending stakeholder feedback

### Blockers
- None.
## 2026-03-06 Wrap-Up

- Completed Excel deliverable for Brian.
- Created and sent reply-all thread using Graph API.
- Identified and promoted pipeline learnings (UOM mismatch / percentile scale / SP calling logic) to `.github/skills`.
- Created PR #53, merged to main, synced worktree.
- Workspace is ready for the next iteration.

## 2026-03-06 (Joe QA feedback and XML cleanup)

- Fixed an aggregation bug in `contract_item_benchmark_summary.sqlx` where matched items with a /bin/zsh benchmark falsely inflated best-tier spend rollup.
- Fixed an XML corruption bug in the Python export logic by stripping illegal hex characters from text fields in dataframes.
- Emailed Joe an explanation on the shifting percentiles and the state of recent pipeline data.

## 2026-03-06 Session 3: Strategic Planning + Data Model Assessment

### Context
- Synced corpus with 3 new OneDrive documents (kick-off meeting transcript, Joe's email, Healthcare IQ email) using GPT-5.4 incremental synthesis.
- Reviewed all 5 per-doc syntheses + master synthesis to develop strategic recommendations.
- Boss's guidance: "wow Bruce with an output, not an approach."

### Decision: July 1+ Contract Competitive Heat Map
Selected Option 1 from 3 candidates — a competitive positioning view of contracts expiring July 1+ with dollar-valued pricing gaps. Rationale: directly answers what Bruce asked his task force to figure out; delivering fast demonstrates speed > methodology.

### Data Model Assessment (Completed)
**Tables needed:** `transaction_analysis_expanded` + `received_benchmarks` — no additional models required.

**Scope: Jul-Dec 2026 Expiring Contracts**

| Program | Contracts | w/ Benchmarks | 6mo Spend | Benchmarked Spend | Coverage |
|---------|-----------|---------------|-----------|-------------------|----------|
| National (PP-) | 302 | 293 | $1,413M | $1,308M | 92.6% |
| ASCENDRIVE (AD-) | 38 | 38 | $114M | $103M | 91.0% |
| Surpass (SP-) | 18 | 18 | $80M | $80M | 99.8% |
| **Total** | **358** | **349** | **$1,607M** | **$1,491M** | **92.8%** |

**Key data elements confirmed:**
- `Contract_Expiration_Date` — 0 nulls, range 2025-09-30 to 2032-10-31
- `Contract_Best_Price` — contract tier price per unit
- `Base_Each_Price` — actual price paid per unit per transaction
- `hciq_low/90/75/50/high_benchmark` — 5 percentile tiers from HCIQ
- Contract metadata (Number, Name, Type, Category, Supplier) — all populated
- Spend/volume (`Base_Spend`, `Quantity`) — all populated

**Nuances discovered:**
- ASCEND type is stored as `ASCENDRIVE` (not `ASCEND`) — use `Contract_Number LIKE 'AD-%'` or `Contract_Type = 'ASCENDRIVE'`
- Custom Procedure Trays (PP-OR-1967, Medline, $168M) only 66% benchmark coverage — inherently hard to benchmark
- `Contract_Best_Price` has 36.6% nulls overall but coverage is strong within scope
- End-to-end item-level pricing vs. benchmark join confirmed working (tested on PP-OR-2234 Stryker Ortho Trauma)

**Joe's proposed targets (from email synthesis):**
- Surpass: at HCIQ low benchmark
- ASCENDRIVE: at 10th percentile
- National (PP-): at 25th percentile

### Next Step: Build the Heat Map
Pipeline work to: filter Jul-Dec 2026 expiring contracts → join with HCIQ benchmarks → calculate current percentile position → calculate gap to Joe's proposed targets → quantify dollar-valued pricing opportunity → rank by opportunity size → format as a tight visual deliverable (top 20-30 contracts ranked by dollar gap).

## 2026-03-07 Session
Created BigQuery-based python pipeline `scripts/export_heat_map.py` to extract Jul-Dec 2026 expiries and apply Joe's percentile targets (Surpass -> HCIQ_Low, AD -> 10th/90_benchmark, National -> 25th/75_benchmark). Total estimated portfolio impact: $415M in annualized savings opportunity. Output formatted and saved as `runs/2026-03-04__portfolio-competitiveness/Contract_Competitive_Heat_Map.xlsx`.

## 2026-03-09 Wrap-Up (QA Defect Fixes & Agent Generalization)

- **Pipeline Math Corrections (Dataform)**: Addressed critical aggregation anomalies identified by the Skeptical QA Agent.
  - *Zero-Dollar Target Masking*: Nullified extended targets where benchmarks were $0.00 to prevent artificial 100% savings inflation (`contract_item_benchmark_summary.sqlx`).
  - *UOM Mismatches*: Enforced bounding thresholds (0.33x -> 3.0x). Transactions outside logic bounds are now explicitly `NULL`ed instead of blowing up Multi-Million dollar variances.
  - *Program Summary Weighting*: Weighted average percentiles mapped firmly against `Benchmarked_Spend` instead of the unfiltered denominator (`program_benchmark_summary.sqlx`).
- **Deliverable Enhancements**:
  - Inserted `Average_Purchase_Price_6mo` into Tab C so hospital purchasing values can be immediately cross-referenced against `contract_best_price` and outlier flags.
  - Completely rewrote Dataform Methodology (`METHODOLOGY.md`) to explicitly document the zero-dollar masking, UOM outlier guarding, and weighted benchmark subsets. 
  - Rendered fresh `HCIQ_Benchmark_Analysis_Deliverable.xlsx`.
- **System Architecture**: Promoted the one-off interpreter agent into a permanent, mult-tree capability.
  - Created `tools/validation_agent/runner.py` with parameter-based CLI architecture.
  - Implemented persistent QA learning memory (`tools/validation_agent/known_traps.md`).
  - Authored `.github/skills/out-of-band-validation/SKILL.md`.
  - Merged cleanly back to `main` via core promotion PR and synced back to `run/2026-03-04__portfolio-competitiveness`.

## 2026-03-09 Wrap-Up (QA Defect Fixes & Agent Generalization)

- **Pipeline Math Corrections (Dataform)**: Addressed critical aggregation anomalies identified by the Skeptical QA Agent.
  - *Zero-Dollar Target Masking*: Nullified extended targets where benchmarks were $0.00 to prevent artificial 100% savings inflation (`contract_item_benchmark_summary.sqlx`).
  - *UOM Mismatches*: Enforced bounding thresholds (0.33x -> 3.0x). Transactions outside logic bounds are now explicitly `NULL`ed instead of blowing up Multi-Million dollar variances.
  - *Program Summary Weighting*: Weighted average percentiles mapped firmly against `Benchmarked_Spend` instead of the unfiltered denominator (`program_benchmark_summary.sqlx`).
- **Deliverable Enhancements**:
  - Inserted `Average_Purchase_Price_6mo` into Tab C so hospital purchasing values can be immediately cross-referenced against `contract_best_price` and outlier flags.
  - Completely rewrote Dataform Methodology (`METHODOLOGY.md`) to explicitly document the zero-dollar masking, UOM outlier guarding, and weighted benchmark subsets. 
  - Rendered fresh `HCIQ_Benchmark_Analysis_Deliverable.xlsx`.
- **System Architecture**: Promoted the one-off interpreter agent into a permanent, mult-tree capability.
  - Created `tools/validation_agent/runner.py` with parameter-based CLI architecture.
  - Implemented persistent QA learning memory (`tools/validation_agent/known_traps.md`).
  - Authored `.github/skills/out-of-band-validation/SKILL.md`.
  - Merged cleanly back to `main` via core promotion PR and synced back to `run/2026-03-04__portfolio-competitiveness`.

## 2026-03-09 Session 2: Stakeholder Feedback & Visual Adjustments
- **Parsed Stakeholder Feedback**: Retrieved and read the "RE: Healthcare IQ Benchmark Analysis - Beta Workbook" email thread via Graph API. Extracted email body using `bs4` and reviewed native images to confirm Joe's mockup specs (X-axis=Expiration, Y-axis=Percentile Gap, Size=Opportunity \$).
- **Refined Analytic Outputs**: 
  - Altered `scripts/export_heat_map.py` to scope specifically to **FY27 Expirations** (Jul 2026 – Jun 2027).
  - Upgraded the bubble chart generation in `scripts/generate_opportunity_viz.py`: implemented `adjustText` to resolve label overlapping, abbreviated long contract names, and mapped the Y-axis to the exact target gap instead of raw percentiles.
  - Rendered updated `FY27_Contract_Competitive_Heat_Map.xlsx` and `Opportunity_Timing_Bubble_Chart.png`.
- **Managed Stakeholder Comms**: Scripted and injected an HTML-formatted draft reply directly into the user's Outlook Drafts.
  - Consolidated the recent architecture/dataway improvements (UOM guarding, Program benchmarking logic).
  - Provided annualized FY27 outlook numbers.
  - Included the new visualization as an inline CID attachment.
  - Acknowledged and tabled the "recent contract launch" nuance for later manager-level rollouts.
  - User successfully verified and sent the communication. 
- **Workspace Status**: Ready for the next phase, which will likely involve fielding subsequent feedback from Joe or pivoting to cut these dashboards down for individual contract managers.
