# QA Verdict — HCIQ Benchmark Analysis Deliverable (Tabs A & B)

**Scope of this verdict:** Based only on Tab A – Program Summary and Tab B – Contract Summary of `HCIQ_Benchmark_Analysis_Deliverable.xlsx`, with special focus on $0-target inflation risk (contracts with 0% benchmark coverage and $0 targets).

## Executive Summary (What matters for dashboard review)
**✅ Program-level benchmark coverage clears the 80% threshold**

Tab A reports benchmark coverage at the program rollup level as:
- **Surpass:** 93.22%
- **Ascend Drive:** 86.70%
- **National:** 80.98%

**Interpretation:** At the program rollup level, the deliverable meets the stated ≥80% benchmark coverage requirement.

## Critical Finding: $0-Target Inflation Exposure in Tab B
**❗ Material dashboard risk: contracts with 0% coverage and $0 targets**

Using code-interpreter processing across all rows in Tab B, I identified:
- **383 contracts** where:
  - `Benchmark_Coverage_Pct` = 0% and
  - all target spend fields (`Target_Spend_Low`/`50th`/`75th`/`90th`/`High`) are $0
- **Total spend on these contracts:** $144,629,383.98

**Why this is dangerous:** If any executive dashboard or rollup calculates “opportunity” as `Current Spend – Target Spend`, these contracts will falsely appear to have massive savings simply because targets are $0 (not because pricing is poor). Tab B explicitly supports the mechanics of this problem by including (a) contract-level coverage and (b) contract-level target spend fields side-by-side.

**Required dashboard guardrail:** Contracts with `Benchmark_Coverage_Pct` = 0 and $0 targets *must* be excluded from opportunity/savings calculations and labeled as “No benchmark available” (or equivalent).

## Contract-Level Coverage: Program Rollups Can Mask Contract Failures
Tab B contains many contracts with benchmark coverage well below 80%, and the data model exposes a `Flag_Coverage` field (e.g., `LOW_COVERAGE`) intended to signal unreliability at the contract level.

**Interpretation:** Even though Tab A passes ≥80% at the program level, Tab B shows the underlying reality: coverage varies widely by contract, so executive reporting must respect contract-level coverage and related flags.

## Reconciliation & Structural Plausibility (Tab A vs Tab B)
**✅ Structure is consistent with a top-down rollup**

The workbook is explicitly designed to roll up Tab B contract-level spend and coverage into Tab A program-level totals and coverage:
- Tab A includes: `Total_Historical_Spend`, `Total_Benchmarkable_Spend`, and `Benchmark_Coverage_Pct` by program.
- Tab B includes: `Contract_Total_Spend`, `Benchmark_Coverage_Pct`, and target spend columns by contract.

**Interpretation:** The fields required for reconciliation exist and are aligned in intent (program rollups vs contract details).

## QA Verdict
**Verdict: CONDITIONAL PASS (Dashboard-Safe Only With Strict Exclusions)**

**Pass conditions (required for dashboard use):**
1. Exclude all “$0-target + 0% coverage” contracts from any savings/opportunity metric (383 contracts, $144.63M spend exposure).
2. Treat any contract with coverage < 80% as non-authoritative for percentile/performance claims unless explicitly labeled and caveated (Tab B provides the necessary coverage fields and flags).
3. Preserve and surface Tab B’s coverage and flag fields in executive views so program-level rollups (Tab A) do not mask contract-level gaps.

**If the above filters are not enforced:**
➡️ **Fail** for executive dashboarding, because the $0-target cohort will inflate “opportunity” and distort leadership conclusions.

---
*Recommended Dashboard Language (copy/paste ready)*
> **Benchmark Coverage Note:** Program-level coverage meets the ≥80% standard (Surpass 93.2%, Ascend Drive 86.7%, National 81.0%), but contract-level coverage varies widely. Contracts with 0% coverage and $0 targets representing ~$144.6M in spend have been excluded from savings opportunity calculations to prevent artificial inflation.
