# Folder Synthesis

Generated on: 2026-01-16
Source folder: /Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/B Braun
Documents included: 2

## Executive Summary (8–12 bullets)

- B. Braun is seeking improved forecasting to better manage supply planning under heightened volatility, especially from rapidly shifting **product mix** and demand uncertainty (81222).
- A key planning requirement is a **unit forecast at the product family + month level** to support planning for **shared components** across products (81222).
- Product-family/month forecasting is seen as **more accurate than SKU-level** and less likely to create planning-system “**nervousness**,” with SKU variability managed via **safety stock** (81222).
- In parallel, B. Braun’s demand planning stakeholders also emphasized the need to forecast **at SKU level if possible**, starting with **top-volume SKUs**, and to deliver outputs as **raw Excel data** aligned to current workflows (84).
- B. Braun’s demand signal is distorted by channel structure: **most demand comes from distributors**, which creates **lumpy ordering**, and the team is **blind to Point-of-Sale (POS)** consumption signals (84).
- The preferred near-term operational forecasting horizon is **8–10 weeks**, with typical **safety stock ~5 weeks**; today, forecasts are built monthly and then **divided evenly across weeks** (84).
- There is strong interest in monitoring **supply-chain signals**, but B. Braun explicitly needs help **interpreting** what those signals mean and how to act on them (81222).
- Competitive/market disruptions can materially impact demand patterns (e.g., **“Teleflex troubles spilled over to B. Braun”**), leading B. Braun to protect customers by **restricting / allocating** supply (84).
- The teams aligned on an initial **deep dive pilot** in a high-priority problem area: **regional anesthesia (epidurals)**, showing **the data Jennifer would actually receive**, with **month + week** views for both **group** and **individual SKUs** (84).
- External market insight relationships (e.g., **Karen & Premier**) are viewed as valuable for **hospital insights and industry themes** (81222).

---

## Themes (with evidence references)

### 1) Forecast granularity tension: product-family/month vs SKU-level needs
- **Product family + month** forecast preferred for planning shared components and reducing system “nervousness” (81222: “unit forecast at the product family and month level”; “likely more accurate than SKU level”).
- **SKU-level** forecasting requested for execution, starting with **top-volume SKUs**, and requiring group + SKU-level views (84: “focus on top volume SKUs initially”; “forecasting at SKU level if possible”; “group + individual SKU” views).
- **Synthesis:** The documents point to a two-layer requirement—aggregate planning signals (product family/month) alongside SKU-level execution outputs (month/week), even though stakeholders emphasize different levels in different contexts (81222, 84).

### 2) Volatility drivers: product mix changes, channel lumpiness, and disruptions
- Accelerating **product mix changes** are a major operational challenge (81222: “keeping up with changes in product mix, which have greatly accelerated”).
- Demand is **lumpy** because it is distributor-driven, with limited visibility into **POS consumption** (84: “most demand comes from distributors”; “blind to the ‘Point of Sale’”).
- Market disruption spillover affects demand and allocations (84: “Teleflex troubles spilled over to B. Braun”; “restricting / going on allocation”).
- **Synthesis:** Forecast instability is not just statistical noise; it is structurally driven by channel opacity (distributors/POS), changing clinical practice/physician preferences, and competitive disruptions (81222, 84).

### 3) Need for interpretation support: turning signals into decisions
- Supply-chain signals are valuable, but B. Braun needs help **interpreting the data** (81222: “Seeing the trends… is very helpful”; “needs help interpreting the data”).
- Stakeholders want visibility into **where problems will occur soon** to support **manual forecast modifiers** (84: “visibility into where problems will occur soon,” including competitor impacts).
- **Synthesis:** Both documents converge on a “decision-support gap”: data exists (signals, historicals, market view, sales inputs) but the organization needs actionable interpretation and early-warning framing (81222, 84).

### 4) Planning windows, cadence, and output format must match operating reality
- Desired forecast window: **8–10 weeks**; safety stock around **5 weeks** (84).
- Current workflow: forecast built **monthly**, then **split evenly across weeks**; output desired as **raw Excel data** (84).
- Constraints include **long lead times** for some raw materials, increasing cost of forecast error and timing requirements (81222).
- **Synthesis:** Any solution must bridge differing time scales—short-term 8–10 week execution needs vs longer lead-time commitments—while fitting the practical cadence and format used by demand planning (81222, 84).

### 5) Focused pilot approach in a critical category
- Confirmed pilot focus: **regional anesthesia (epidurals)**, including month/week forecasting and realistic data views (84).
- Broader pain point: the team is “currently struggling” in pain control/regional anesthesia across multiple sub-areas (84).
- **Synthesis:** The pilot is positioned as a pragmatic wedge into a high-volatility, high-importance area rather than attempting an enterprise-wide rollout immediately (84).

---

## Notable Decisions / Confirmations

- **Pilot scope confirmed:** Deep dive **regional anesthesia (epidurals)** first (84).
- **Output realism confirmed:** Pilot should show **the same data Jennifer would actually receive** (84).
- **Forecast output requirements confirmed:** **Month + week level**, with **group + individual SKU** views; start with **top-volume SKUs**; deliver **raw Excel data** (84).
- **Planning preference (position, not formal decision):** Product-family/month forecasting is viewed as preferable for accuracy and reduced system “nervousness,” with SKU variability addressed via safety stock (81222).

---

## Open Questions / Follow-ups

- **Demand inflection:** When will high demand **fall off**? (81222)
- **Spike detection:** Where is demand **about to spike**? (81222)
- **Signal interpretation scope:** Which **supply-chain signals** are monitored today and where is interpretation support most needed? (81222)
- **Forecast deliverable definition:** Scope/cadence/format for the **product family/month unit forecast** (81222)
- **Order validity:** A **large order sitting for 90 days**—is it still real demand or has the hospital found alternate supply? (84)
- **Switch-back behavior:** If a hospital switches to an alternative, **how long until switching back**? (84)
- **Clarification needed:** Sales comment that they “**current ramp up fast enough**” (exact meaning unclear) (84)

---

## Recommended Next Actions

1. **Lock the pilot inputs and SKU mapping**
   - Obtain the **full epidurals SKU list** and required identifiers to match to available data (84).
   - Confirm the initial focus on **top-volume SKUs** within epidurals (84).

2. **Define a dual-level forecast deliverable (aggregate + SKU)**
   - Specify the **product family/month unit forecast** needed for shared-component planning (81222).
   - In parallel, deliver **month + week** forecasts for the epidurals pilot at **group + SKU** level in **raw Excel** (84).

3. **Stand up a “signal interpretation” working session**
   - Inventory current **supply-chain signals** being monitored and document the exact interpretation decisions they need to support (81222).
   - Explicitly incorporate near-term “**where problems will occur soon**” views to support manual modifiers (84).

4. **Address distributor/POS blindness explicitly in the pilot narrative**
   - Document how distributor lumpiness and lack of POS will be handled/communicated in outputs (84), and where supplemental insight (e.g., **Karen & Premier** hospital themes) can contextualize patterns (81222).

5. **Resolve key demand validity questions during the build**
   - Investigate the **90-day outstanding order** status and define criteria for “real demand” vs “stale signal” (84).
   - Capture and validate assumptions on **switch-away / switch-back timing** to avoid misreading disruption-driven ordering (84).

## Individual Document Syntheses

- 81222 Call With B. Braun.pdf

- 84 Interview With B. Braun.pdf
