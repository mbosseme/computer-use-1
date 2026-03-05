# Briefing: Contract-level percentile positioning vs Healthcare IQ benchmarks (Deliverable due tomorrow)

## 1) Background and why this is urgent

Bruce requested an analysis that answers: **“Where do our Premier contracts land in percentile terms versus Healthcare IQ benchmark pricing?”** He wants a **contract/agreement-level** view, not a SKU-by-SKU presentation, and he wants it expressed in **percentile language** (or at least percentile ranges like “between 10th and 25th”). The prior framing (“savings to reach P25 / P10 / benchmark low”) is explicitly **not** what he wants for this deliverable; the deliverable is about **positioning/ranking**.

There is an executive-storytelling motivation: likely to communicate to leadership/board and/or use in member/supplier conversations (e.g., “National is around Xth percentile; Surpass around Yth”). There is also nuance that locals/IDNs may achieve very aggressive pricing (10th–15th), raising the question of whether National at 25th is “good enough” — but the immediate deliverable is **ranking**, not target-setting.

## 2) Portfolio / prefix mappings (must be treated as authoritative)

These are **one-to-one mappings** and should be used consistently in outputs:

* **PP*** prefix = **National portfolio**
* **AD*** prefix = **Ascend Drive portfolio** (spelled exactly A-S-C-E-N-D D-R-I-V-E; transcript mis-captured)
* **SP*** prefix = **Surpass portfolio**

## 3) Deliverable due tomorrow (what “done” looks like)

Start with **CSV outputs** or (preferably) an **Excel workbook with multiple tabs** that provides:

### Tab A: Contract-level summary (one row per Premier contract number)

For each **Premier contract number** (agreement-level; no tier-level breakouts yet):

* Portfolio (National / Ascend Drive / Surpass based on prefix mapping)
* Contract number and basic identifiers
* **Best Premier tier price** used for benchmarking (see Section 4)
* Spend/volume rollups over **last 6 months**
* Benchmark rollups (spend-at-P10/P25/P50/P90)
* **Percentile bucket** (≤10, 10–25, 25–50, 50–90, ≥90)
* Optional **estimated percentile** (piecewise-linear interpolation) with clear labeling that it is an estimate
* **Benchmark coverage metrics**

  * Target threshold: **≥80%** benchmark coverage
  * If <80%: **still rank**, but **flag with warning**
* QA flags (e.g., best price ambiguity, tier description ambiguity, contract type excluded, etc.)

### Tab B: Contract–product drilldown (contract × product detail)

For drilldown validation and transparency:

* Contract number + portfolio
* Product identifier + description (whatever is available)
* Units and spend (last 6 months) at product level used in rollup
* The tier and pricing fields used:

  * best tier description used to qualify “Premier tier”
  * contract best price used (unit)
  * contract type and match type context
* Benchmark fields:

  * HCIQ benchmark unit prices (P10/P25/P50/P90) if present
  * Benchmark-extended spend at each percentile (units × benchmark price)
* **Include ALL products matched to the contract**, not just benchmarked ones

  * Provide a flag for benchmark availability
  * Provide a reason / indicator for “missing benchmark” so gaps are visible

### Tab C (optional but recommended): QA Flags

A structured exceptions table:

* contract number
* issue type
* issue detail
* suggested action / follow-up

## 4) Core technical definitions and rules

### 4.1 Rollup level and tier scope

* Roll up by **Premier contract number**. This uniquely defines the agreement for this deliverable.
* A contract may have multiple tiers, but **do not** do tier-level analysis yet.
* The analysis must use **only the top-tier pricing** of each contract.

### 4.2 Which “price” to use for benchmarking

Use the Transaction Analysis model’s:

* **`contract_best_price`** (unit price at the best/top tier of the contract)

Also bring:

* **`contract_best_tier_description`**
* **`contract_type`**

Purpose:

* Ensure we are using a **Premier best tier**, not a local/IDN tier or local contract construct.

Critical filter requirement when finding the best price:

* Exclude contract types where `contract_type` is **LOCAL** or **REGIONAL**:

  * `UPPER(contract_type) NOT IN ('LOCAL', 'REGIONAL')`

Tier-description heuristic for Premier vs local tiers:

* Premier tiers typically start with **“Tier <number> …”**
* Local tiers typically contain words like **“local”** or an org/IDN/group name
* This must be assessed carefully and validated with Matt once results are produced.

### 4.3 “Find it once, apply everywhere” best-price logic

`contract_best_price` may not be populated on every row. The intended approach:

1. Over the last 6 months of Transaction Analysis rows, identify rows where:

   * contract_best_price is not null
   * contract_type is not LOCAL/REGIONAL
   * tier description indicates Premier tier (per heuristic)
2. For each Premier contract number:

   * Select a single “best premier tier price” (and store the tier description and contract_type used)
3. Join that per-contract best-price lookup back to all contract-level rollups.

Add QA checks:

* Within each contract, check whether multiple distinct best prices or tier descriptions appear after filtering. If so, flag for review (could indicate tier leakage or contract changes).

## 5) Benchmarking approach: how to get to percentile at contract level

### 5.1 Use discrete benchmark points; bucket is primary

Healthcare IQ provides discrete benchmark prices (e.g., P10/P25/P50/P90 and possibly low/high). Because pricing distributions are unknown, it is **not strictly accurate** to claim a true “65th percentile” from only these anchors without assumptions.

Primary output should be a **bucket/range**:

* ≤10th
* 10–25
* 25–50
* 50–90
* ≥90

### 5.2 Optional “estimated percentile” (roll up first, then interpolate)

If a single number is needed for communication:

* Roll up contract-level totals first (spend-at-benchmark points), then compute an **estimated percentile** via **piecewise-linear interpolation** between the bracket endpoints.
* Label this clearly as an estimate (e.g., `estimated_percentile_linear`) and do not represent it as an exact percentile.

### 5.3 Contract-level benchmark spend calculations

Compute, for each contract:

* **ActualSpend** = Σ(units × actual price measure used for spend rollup) on matched lines
* **Spend@P10** = Σ(units × HCIQ_P10_unit_price) for benchmarked lines
* **Spend@P25/P50/P90** similarly

Then determine bucket by comparing ActualSpend to Spend@P10/P25/P50/P90.

Benchmark coverage:

* Compute benchmarkable spend vs total spend (and/or benchmarkable units vs total units).
* **Coverage threshold: 80% minimum**; below that, **rank anyway but flag**.

Important known limitation:

* Benchmarks may not exist for every product (and rebates are generally excluded). Ensure missing benchmarks are visible in the drilldown tab.

## 6) Spend attribution rules (local vs Premier, eligibility remap)

A key complexity: transactions may be matched to **local contracts/tiers**. For deliverable purposes, you need to attribute that spend to the **most relevant Premier program contract** the facility is eligible for.

Rule:

* If the matched contract is local, find the facility’s eligible Premier program in priority order:

  1. **Surpass**
  2. **Ascend Drive**
  3. **National**
* A facility cannot be part of multiple programs simultaneously; assign to the **highest** program it belongs to.

Deliverable expectation:

* Contract summary should reflect this “attributed Premier contract/program” logic, not purely the local match.
* Keep the original match context available in drilldown (so analysts can see what was local vs attributed).

Implementation note:

* You will likely need a facility-to-program eligibility mapping to apply this rule. If it does not exist directly, derive it using available program enrollment indicators in the data model or a reference table. If uncertain, produce an interim output and request Matt validation.

## 7) Time window

Use **last 6 months** of data for volume/spend weighting and for sampling the best tier price (to ensure current relevance).

## 8) Output expectations for tomorrow

Preferred format:

* Excel workbook with multiple tabs (Contract Summary, Contract–Product Detail, QA Flags)
  Acceptable alternative:
* A set of CSV files with the same separation.

The immediate audience is **Brian and Joe** for validation and iteration; this is not necessarily the final board-ready format, but it must be internally credible and drillable.

## 9) Practical QA checklist (must-do before sending)

1. Validate mapping of PP/AD/SP to portfolio labels.
2. Confirm `contract_best_price` selection logic:

   * not LOCAL/REGIONAL
   * Premier tier description heuristic holds
   * “find it once” lookup doesn’t show large dispersion in best price
3. Confirm benchmark join rates and compute coverage:

   * Flag <80% but do not exclude
4. Confirm drilldown completeness:

   * All products matched to contract appear, benchmarked or not
5. Sanity-check extreme results:

   * For contracts showing very high/low percentiles, drill down and confirm drivers (a few high-volume products often dominate).

## 10) Open items requiring Matt review (do not block initial output)

* Any ambiguous tier descriptions that might be Premier vs local
* Any contracts with multiple candidate best prices in the last 6 months
* Any uncertainty in facility program eligibility mapping for local-spend attribution

---
