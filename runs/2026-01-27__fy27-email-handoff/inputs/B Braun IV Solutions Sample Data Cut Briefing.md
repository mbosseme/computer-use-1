# B. Braun IV Solutions Sample Data Cut Briefing

Purpose: capture the full working understanding from our discussion so an analysis agent can execute (1) a facility-level sample data cut for Jen (B. Braun) and (2) an internal validation that the sample is complete/credible.

---

## 1) What Jen asked for and what we’re solving

### Jen’s stated intent

Jen is not ready for a broad engagement. She wants a **tightly scoped exploratory sample/pilot** focused on **a narrow product basket** to:

* compare against B. Braun’s current data sources,
* validate incremental value,
* keep scope controlled (one category / limited sample).

### The operational ask

Provide a **de-identified facility-level sample extract** for a defined time window, covering the specific **B. Braun SKUs + NDCs** she listed, with enough structure to let her understand:

* what we have by facility and time,
* how much volume/spend we can observe,
* how consistent it is with known baselines (internally validated).

---

## 2) The product basket: what these SKUs are

This SKU list is predominantly:

* **IV base solutions** (LVPs: saline, dextrose, LR, balanced electrolytes),
* **premixed electrolyte IV solutions** (notably potassium chloride premixes),
* **irrigation solutions** (sterile water/saline irrigation; large volumes),
* plus a few special-use solutions (3% hypertonic saline, cardioplegia).

### Why this basket matters

* It’s **high-volume, ubiquitous** across acute care settings (ED/OR/ICU/floors).
* It’s **substitution-prone** during shortages and allocation events.
* It’s exactly the type of space where manufacturers want **facility-level visibility** on switching, share, and continuity-of-supply impact.

---

## 3) Identifiers and how to think about them

### A) Manufacturer SKU / Part Number

* Jen provided **manufacturer name + part number/SKU** per line.
* This is typically the “what B. Braun actually sells” identifier, but may still vary by:

  * package configuration (each vs case),
  * internal distributor item numbers,
  * facility item master aliases.

### B) NDC (National Drug Code)

Key clarification:

* An NDC is **specific** to product identity + package configuration **and includes a “labeler” segment** that identifies the company responsible for the product label (often the manufacturer/marketer).
* NDCs therefore *can* be manufacturer-specific, but you can still see multiple NDCs across:

  * different sizes of essentially the same therapy (e.g., NS 250 mL vs 1,000 mL),
  * different packaging,
  * different labelers for comparable clinical products.

### C) Premier Reference Number (your internal roll-up key)

* You described the **Premier Reference Number** as a single numeric product key that can represent:

  * multiple package sizes,
  * vendor/manufacturer aliases,
  * SKU variants that are effectively the “same product concept” in your matching ontology.
* This key is the bridge that enables “expand beyond the single NDC” *in a controlled, defensible way*.

---

## 4) Data sources and what each one contributes

You have two complementary feeds (important: **complementary, not overlapping** in your intended use):

### 4.1 Transaction Analysis Expanded (TAE)

* Source: **provider ERP purchase order / receiving / AP-like records** extracted from hospital/health system systems (e.g., Workday, Lawson).
* Contains: **manufacturer name**, **part number/SKU**, and also **NDC** (critical).
* This is your best source for:

  * direct ERP procurement behavior,
  * non-pharmacy supply chain buys,
  * visibility at manufacturer SKU-level.

### 4.2 Report Builder (RB) – pharma wholesaler tracings

* Source: **pharmaceutical wholesaler sales tracings**.
* Does NOT contain: manufacturer part number/SKU (per your note).
* DOES contain: **NDC** (critical).
* This is your best source for:

  * pharmacy channel purchases that may not appear in ERP PO data,
  * “wholesaler platform” ordering that bypasses normal materials PO patterns.

### Why you need both for “total inflow”

To characterize total volume/spend flowing into acute care facilities for this basket, you likely need both:

* ERP-driven procurement (TAE)
* Wholesaler-driven procurement (RB)

---

## 5) Core strategy: map from Jen’s list → Reference # → expand NDC coverage (selectively)

### Step 1 — Start with Jen’s exact list

For each row in Jen’s list (SKU + NDC):

* attempt to match in **TAE** by **NDC** first (shortcut),
* confirm match coverage for every line item.

Why NDC-first in TAE is attractive:

* It reduces ambiguity vs free-text manufacturer name + SKU variants.
* It yields a direct line to the **Premier Reference Number** on the same row.

### Step 2 — Retrieve Premier Reference Number for each matched row

Once a row is found in TAE:

* extract the **Premier Reference Number** for that record.

### Step 3 — Expand to “all NDCs tied to that Reference #”

This is the key agreed logic:

* In TAE, for each Premier Reference Number associated with Jen’s list, enumerate **all distinct NDCs** that appear under that Reference # (and possibly all relevant packaging forms).
* Then, when pulling from RB (wholesaler), include:

  * the **original Jen NDC list**, PLUS
  * any **additional NDCs** discovered under those same Premier Reference Numbers.

Rationale:

* RB can only filter by NDC.
* If a Reference # represents a product concept that Jen cares about, and that concept spans multiple NDCs (sizes/configs), then limiting RB to only the single NDCs she provided may undercount.

Guardrail:

* Only expand to NDCs that are tied to Reference Numbers that are anchored to Jen’s listed SKUs (so you don’t accidentally balloon scope).

---

## 6) Joining/merging: build a combined “facility-month-product” dataset

### Principle: union, not de-dup

You stated these feeds are complementary in the intended use:

* Do **not** attempt to find overlap and subtract.
* Create a **unioned combined dataset** where each source contributes its own observed transactions.

### Recommended minimum grain

Build a combined model with at least:

* **facility identifier** (Premier entity code internally; de-ID externally),
* **time** at **month** grain (also support quarter for validation),
* **product keys**:

  * Premier Reference Number (when available),
  * NDC (always carry for RB traceability),
* **measures**:

  * units and/or quantity (as available),
  * spend / extended cost / sales dollars (as available),
  * source flag (TAE vs RB).

This becomes the canonical dataset used for:

* internal validation vs B. Braun-reported tracings,
* external sample delivery.

---

## 7) Internal validation plan: align against B. Braun supplier-reported on-contract sales

Purpose: demonstrate coverage and reduce “are we missing big chunks?” risk before handing sample to Jen.

### Validation inputs

1. **Combined TAE + RB union dataset** (facility/month/product)
2. **B. Braun supplier-reported on-contract sales tracings**

   * must be available at **product level** (Reference # and/or NDC) and **Premier entity code** level
   * time grain should support at least quarter

### Comparison method (as described)

* Aggregate to **calendar quarter**.
* Compare at the intersection of:

  * **same Premier entity codes (facilities)**,
  * **same quarters**.
* Product-level differences are the signal, not necessarily the join key:

  * You can start with facility+quarter totals for the basket (strongest coverage test),
  * then drill to product/ref# deltas to identify systematic gaps.

Important nuance you stated:

* Only compare where both sides have representation for the same facility+quarter to keep it “apples-to-apples” for Premier members in the supplier-reported dataset.

### Success criterion (practical)

* Combined dataset totals for B. Braun product basket (by facility+quarter) should be “close” to B. Braun’s own on-contract reported totals.
* Any material gaps become:

  * mapping problems (NDC not found, ref# mismatch),
  * time alignment/lags,
  * missing channel coverage.

If the combined data matches B. Braun well for Premier members, it is a credible argument that:

* your facility inflow capture is strong,
* the broader sample (including non-Premier entities) is likely directionally complete.

---

## 8) Time-window alignment and data lag (explicitly flagged)

Agreed default window:

* **24 months through December 2025**, subject to completeness checks.

Key operational constraint:

* **Supplier-reported** and/or **wholesaler** and/or **ERP** feeds may have different lags.
* If December isn’t complete across all required sources, shift the end date back to the most recent fully complete month and keep the window consistent.

Deliverable expectation:

* When presenting to Jen, you should explicitly note:

  * the selected time window,
  * known lag expectations per feed (if relevant),
  * and that the window was chosen for completeness across sources.

---

## 9) External sample to Jen: maximize inclusivity, de-identify, preserve structure

### Internal vs external scope

* **Internal validation**: restrict to Premier-member facilities present in supplier-reported on-contract tracings (because you need a ground-truth comparator).
* **External sample**: include **all facilities you have** (largest coverage), because Jen wants to see the richness of the data and potential scale.

### De-identification

* Replace Premier entity code with **blinded facility ID**.
* Keep consistent facility IDs across months so she can track trends per facility without identifying them.

### External data elements (recommended)

At minimum per facility-month-product row:

* blinded_facility_id
* month (YYYY-MM)
* ndc
* premier_reference_number (if shareable; if not, provide a surrogate product key)
* product_description (normalized)
* measure fields (spend, units/qty, etc.)
* source flag (ERP vs wholesaler) — optional but useful for interpretability

Also provide:

* data dictionary (field definitions + caveats)
* counts/coverage summary (num facilities, months, products, % with both sources)

---

## 10) Key risks / failure modes and how to handle them

### Risk A — Missing NDC matches in TAE

If some of Jen’s NDCs don’t match in TAE:

* diagnose:

  * formatting differences (hyphens, leading zeros),
  * NDC normalization (10 vs 11-digit transforms),
  * gaps in NDC population in TAE,
  * alternate packaging NDCs.
* fallback:

  * use product matching tool on manufacturer name + SKU to find reference #,
  * then recover associated NDCs.

### Risk B — Reference # expands too broadly

If a reference # maps to unexpected products:

* add guardrails:

  * require solution type consistency (NS vs D5W vs LR),
  * require volume family consistency if needed,
  * review top NDCs by spend under the reference # to confirm they’re plausible.

### Risk C — Double counting

You asserted TAE and RB are complementary. Still, sanity check:

* if both feeds capture the same downstream transaction in rare cases, you could overstate.
  Mitigation:
* keep source separation in the data model,
* quantify overlap risk by looking for identical facility-month-ndc totals across sources (not to subtract blindly, but to confirm your assumption holds).

### Risk D — Unit-of-measure mismatch

ERP may record:

* cases, eaches, liters, bags, etc.
  Wholesaler may record:
* units as shipped or eaches.
  Mitigation:
* prioritize spend comparisons for validation,
* normalize units where possible using package size and UOM mappings,
* at least provide both raw and normalized volumes if feasible.

### Risk E — Facility churn over time

Facilities may enter/exit the sample across 24 months.
Mitigation:

* include facility-month completeness indicators,
* do not force a balanced panel unless explicitly required.

---

## 11) Execution checklist (agent-ready)

1. **Normalize Jen’s NDCs**

   * consistent hyphenation and 10/11-digit normalization strategy.
2. **TAE match test**

   * for each Jen NDC, confirm at least one match in TAE.
   * capture unmatched list for investigation.
3. **Extract Premier Reference # per matched row**
4. **Expand NDC set**

   * all NDCs associated with each of those reference #s in TAE.
5. **Pull TAE transactions**

   * for expanded reference # set and/or NDC set
   * time window = 24 months through Dec 2025 (or adjusted for completeness).
6. **Pull RB wholesaler transactions**

   * filter by expanded NDC set
7. **Union dataset**

   * align to facility-month-ndc-reference# grain with consistent fields.
8. **Internal validation**

   * acquire B. Braun on-contract supplier-reported tracings at product level
   * compare by facility-quarter (primary) and optionally product-level deltas (secondary).
9. **Prepare external sample**

   * de-ID facility
   * include data dictionary + coverage summary
   * include notes on time window and feed complementarity.

---

## 12) Open questions to resolve early (to avoid rework)

* What is the exact format/availability of **B. Braun on-contract supplier-reported data** at product level (ref# vs NDC)? If only ref#, ensure ref# mapping is rock-solid.
* Which metric is preferred for Jen’s sample: **spend, units, or both**?
* Are there any restrictions on sharing **Premier Reference Number** externally (even though it’s not an ID of the facility)? If restricted, generate a surrogate product key and keep NDC as the primary product identifier.
* Confirm whether RB provides facility identifier compatible with Premier entity code (or an internal crosswalk exists).

---

## 13) Summary of the key “logic decisions” we made

* Treat Jen’s provided **SKU+NDC list as the anchor scope**.
* Use **NDC in TAE** as the fastest path to retrieve **Premier Reference #**.
* Expand to include **all NDCs under those reference #s** when querying wholesaler data (RB), because RB is NDC-only and otherwise you risk undercounting.
* Merge ERP (TAE) and wholesaler (RB) via **union**, not de-dupe, with a source flag.
* Validate internally by aligning combined totals to **B. Braun’s supplier-reported on-contract** sales for Premier members at facility-quarter level.
* Provide Jen a broad, **de-identified** facility-month-product sample to showcase richness and coverage.

If you want, I can also format this into a “runbook” style (step-by-step SQL/query pseudocode + expected outputs at each step), but the above captures the full conceptual blueprint.