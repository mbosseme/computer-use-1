# Meeting Analysis & Action Items: B Braun MI Demo

Source: Confirmed-BBraun MI Demo - virtual.pdf
Generated on: 2026-01-15

## 1) Executive Summary
Premier (Matt Bossemeyer, Sachin Shah, Audrey Siepiela) conducted a focused demo for B. Braun’s marketing/insights/pricing stakeholders (Tracy Butryn, Jennifer Gotto, Jake Astarita, Claire Concowich, Aime Lenz, team) on Premier’s **Market Insights** capabilities—separate from the prior session’s heavier emphasis on **contract compliance** tools.

Key discussion points:
- **Data foundation & differentiation:** Premier emphasized that its purchasing data is sourced directly from provider systems (primarily hospital ERPs, plus pharmaceutical wholesaler tracings), with ~55% acute hospital coverage and strong non-acute representation. The team stressed **granularity (SKU-level), accuracy (provider-validated), and latency (some daily refresh)** as primary differentiators vs. third-party industry datasets.
- **Custom dashboard concept (“triple play” / fluid-path cross-sell):** Premier demoed an early Tableau concept to identify facility-level cross-sell/leakage across related IV therapy categories (devices, infusion sets/accessories, safety IV catheters; plus additional categories like fluids/connectors/pharmacy).
- **Segmentation/launch & portfolio gap use cases:** B. Braun asked about using the data to support **launch targeting**, **portfolio gap analysis**, **competitor tracking**, and **pricing benchmarks** by segment/class-of-trade and geography.
- **Delivery model discussion:** B. Braun expressed interest in dashboards for actionability, but requested **visibility into attributes/data dictionary** to validate what is informing the outputs; they noted they often extract data into their own Power BI environment today.
- **CAPS (503B) validation need:** Claire/Jake specifically explored whether Premier can represent CAPS/compounding/nutrition/anesthesia/cardioplegia markets and key competitors; Premier proposed a SKU-list-driven validation sample.
- **Standard app demo (Audrey):** Premier briefly demonstrated the standard Market Insights application (portfolio/competitor views, taxonomy search). A notable limitation was confirmed: the **standard app is currently acute ERP-focused and does not yet include wholesaler data**, though integration is planned soon.

The meeting concluded with B. Braun agreeing to **debrief internally** and then re-engage Premier on the preferred path (standard app vs. custom dashboards vs. data feed / pilot).

---

## 2) Key Follow-up Actions (Owner, Deliverable, Timeline)
| # | Action / Deliverable | Owner | Timeline / Timing Mentioned |
|---|---|---|---|
| 1 | **Internal debrief to select preferred engagement approach** (e.g., custom dashboards for cross-sell/leakage, portfolio gap analysis, or data feed) and **communicate decision back to Premier** | **B. Braun** (Tracy Butryn, Jennifer Gotto, broader B. Braun team) | “**A few days**” to debrief (verbal); then follow up with Premier |
| 2 | Provide **SKU list + product details** for **CAPS and related categories** (compounding/nutrition/etc.) so Premier can produce a **sample data cut** validating representation and competitor visibility (e.g., Fresenius Kabi/others referenced; specifically mentioned competitors included “Fragran Sterl Service” and “QUVA”) | **Claire Concowich (B. Braun)** (with implied support from Jake/team as needed) | No date stated; implied as next-step item after meeting |
| 3 | Share **attribute list / data dictionary** (and optionally a **sample raw data extract**) to support B. Braun’s validation of dashboard outputs | **Premier (Matt Bossemeyer team)** | Offered during meeting; no explicit due date stated |
| 4 | Produce **sample analysis/cut** based on B. Braun SKU inputs (CAPS-focused) to confirm coverage across ERP + wholesaler tracings | **Premier (Matt Bossemeyer team)** | After receipt of SKU list; no explicit due date stated |
| 5 | Potential **follow-up demo** focused on whichever use case B. Braun prioritizes post-debrief (e.g., leakage targeting filters/sorts; portfolio gap views; pricing benchmarks) | **Premier + B. Braun** | After B. Braun internal alignment; no date stated |
| 6 | Product roadmap: incorporate **pharmaceutical wholesaler data into the standard Market Insights app** (currently acute ERP-only) | **Premier** | Mentioned expected in “**next 3–4 months**” |

*Notes on implied configuration requests (not explicitly assigned as tasks but clearly requested for the next iteration of a custom build):*
- Add **filters/sorts** such as “IV fluids share ≥ X%” and sorting by **market share** (not just spend).
- Provide clearer **category definitions** (what SKUs sit inside “infusion sets/accessories,” “IV therapy products,” etc.).
- Enable/validate **taxonomy mapping** from B. Braun’s internal hierarchy and apply it to competitor items via Premier cross-references (including a mechanism for B. Braun influence/control over competitor mapping in edge cases).

---

## 3) Strategic Pain Points / Feature Requests from B. Braun
### A. Data completeness gaps (especially pharmacy-related)
- B. Braun described a recurring issue in their own annual utilization work: they are **missing pharmacy-related devices/products** (e.g., pharmacy admixture, duplex, related competitive products) when trying to build denominators and utilization views.
- They probed whether Premier can unify **ERP purchasing + pharmaceutical wholesaler channels** to close these gaps (Premier indicated yes at the dataset level; but acknowledged the **standard app** currently lacks wholesaler integration).

### B. Need for trust/validation in outputs (data transparency)
- B. Braun wants dashboards, but emphasized the need to understand **“what’s informing the outputs”** (attribute lists, data dictionary, sample extracts) to validate accuracy/representation before committing.

### C. Segmentation/targeting for commercial strategy and launches is hard today
- They stated they spend substantial time **cobbling together** segmentation, competitor presence, and targeting insights from multiple sources; they want a faster path to:
  - Identify **best targets** by segment/class-of-trade/geography
  - Support **new product launches** (including specific drug examples like naloxone/magnesium sulfate)
  - Run **portfolio gap analysis** (where markets are growing, underserved, or oversaturated)

### D. Feature requests for usability in custom analytics
- Requested ability to **filter and rank/sort** accounts by:
  - Market share thresholds (e.g., high IV fluids share)
  - Leakage against other categories (e.g., pharmacy/compounding category leakage)
- Asked about **roll-ups** (IDN/system hierarchy) but recognized blinding constraints; still, the desire is to analyze both **facility-level** and **parent/IDN-level** patterns where possible.

### E. Taxonomy mapping + competitor classification control
- B. Braun wants clear access to Premier’s **product taxonomy** and the ability to align it to B. Braun’s internal taxonomy.
- They specifically requested clarity on how Premier will **subcategorize competitive products** into B. Braun-defined segments, and asked about access to Premier’s **cross-reference** logic and the ability to override mappings where needed.

### F. Pricing benchmarks—granularity constraints acknowledged
- They expressed interest in pricing analysis by segment/geography/competitor; Premier noted pricing can be provided in aggregated ways (class-of-trade/region/product) but **not in a way that exposes facility-specific contract prices**.