# Synthesis: 84_interview_with_b_braun__ca8c7c7c73.pdf

Generated on: 2026-01-27

## Coverage / Limit Warnings
- None

## Extraction Stats
- Pages total: 1
- Pages de-duplicated (identical extraction): 0
- Pages with text: 1
- Pages with extraction errors: 0
- Total extracted chars: 2177

## Chunking Stats
- Chunks: 1
- target_chunk_chars: 30000
- max_chunk_chars: 45000
- overlap_pages: 1
- max_chunks: None
- page_timeout_s: 15

---
## 1) Executive Summary (6–10 bullets)

- The team aligned to **start with top-volume SKUs** as the initial scope for the forecasting work.
- Current forecast accuracy is challenged by **practice/physician-driven mix changes**, including situations where a **physician leaves a practice and the supplier is not notified**.
- Demand is largely **distributor-driven and “lumpy,”** and distributors are described as **blind to point-of-sale (POS)** information.
- The preferred operating cadence is an **8–10 week forecast window** (with “8 weeks would help”), supported by typical **~5 weeks of safety stock**.
- Current planning inputs include **historical data, standard SIOP, “Market View” (marketing growth estimate out 18 months, including sales estimates), and seasonality**.
- The team indicated they already have a **categorization hierarchy** and can **add incremental quantity at higher levels and allocate down**.
- A specific area of difficulty called out is **pain control / regional anesthesia**, including **spine, epidurals, peripheral nerve block, and combined**.
- Preferred outputs are **raw data in Excel**, and there is interest in **early warning indicators** to guide **manual modifiers** (including awareness of potential competitor impacts).
- There is a strong preference for **SKU-level detail** “if possible.”

---

## 2) Meeting Context

- Discussion focused on improving demand planning/forecasting, particularly given:
  - **Distributor-led ordering variability** and lack of POS visibility.
  - **Mix shifts** driven by clinical practice changes and physician preference.
  - The need for a **near-term forecast horizon** that supports operational decisions (inventory/safety stock, allocation, early warnings).
- Participants referenced include:
  - **Jennifer (Demand Planner)** — described current planning inputs and preferred outputs.
  - **Alan (Director of Demand Planning)** — raised questions about stale orders and customer switching behavior.
  - **Carmel (VP Sales)** — highlighted supply/market context (including a reference to Teleflex impacts; exact meaning unclear/unknown).

---

## 3) Key Decisions / Confirmations

- **Initial scope:** Focus on **top volume SKUs**.
- **Forecast horizon target:** **8–10 weeks** is ideal (8 weeks would help).
- **Granularity:** Forecasting at **SKU level if possible**.
- **Deliverable format:** **Raw data in Excel** is preferred.
- **Approach compatibility:** Their existing hierarchy can support **top-down incremental adjustments allocated downward**.

---

## 4) Open Questions / Follow-ups

- **Stale large orders:** For “a large order… sitting out there for 90 days,” is it still needed, or has the hospital already received an alternate supply? *(Status unknown.)*
- **Switching behavior:** When a hospital switches to an alternative product, **how long do they stay** before switching back? *(Unknown.)*
- **POS / demand visibility:** Whether B. Braun can provide or approximate **distributor POS visibility** (noted as lacking today). *(Unknown.)*
- **Teleflex → B. Braun context:** “Teleflex troubles spilled over to B. Braun…” — specific meaning/implications are **unclear/unknown** based on notes.

---

## 5) Risks / Dependencies

- **Data limitations:** Distributor ordering is “lumpy” and POS-blindness may limit forecast signal quality and early warning effectiveness.
- **Mix volatility:** Practice/physician-driven shifts (including unreported physician departures) can cause rapid mix changes that degrade forecast accuracy.
- **Process dependency:** Current forecasting is **monthly and spread evenly across weeks**, which may not match true intra-month demand patterns unless improved inputs/methods are introduced.
- **Category complexity:** The pain control / regional anesthesia area is explicitly described as a current struggle, suggesting higher model/process risk there.

---

## 6) Suggested Next-Step Email (short draft)

Subject: Next steps: Top SKUs forecast pilot + regional anesthesia deep dive

Hi team,  
Thanks for the discussion. Confirming the agreed path forward:

- We’ll start with the **top volume SKUs**, targeting an **8–10 week forecast window** (8 weeks minimum helpful), with **SKU-level detail where possible**.  
- Deliverables will be **raw Excel outputs**.  
- As a first deep dive, we’ll focus on **regional anesthesia (e.g., epidurals)** and show the data in the format Jennifer would typically receive, then **match and forecast at month and week levels** (for the overall group and individual SKUs).  

Carmel—please send the **list of all SKUs** when available.  
Also, could you advise on (1) how to treat **large orders outstanding ~90 days** and (2) any guidance/data on how long hospitals typically remain on **alternate supply** after switching?

Best regards,  
[Your Name]
