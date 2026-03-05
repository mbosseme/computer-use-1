# Folder Synthesis

Generated on: 2026-03-04
Rebuilt on: 2026-03-04T12:01:31
Documents included: 2

## Executive Summary (8–12 bullets)

- Two connected workstreams emerge: (1) improving national contract competitiveness through a structured review process and (2) rapidly quantifying “how competitive” national pricing is vs external benchmarks. *(Connect.pdf; Urgent Request.pdf)*
- Leadership concern is explicit and recurring: stakeholders are hearing that “our national contracts aren’t competitive,” and want a measurable view of the gap. *(Connect.pdf; Urgent Request.pdf)*
- Bruce initiated an immediate contract review for agreements launching **“July 1 or later”** with authority to “send it back” if it fails predefined tests—implying an upcoming gating / quality-control mechanism. *(Connect.pdf)*
- In parallel, Bruce requested an **aggregate, weighted contract ranking vs benchmarks** (not SKU-by-SKU), including separate views for **PP, AD, and SP** constructs. *(Urgent Request.pdf)*
- The benchmark approach is to use **6 months** of volume/spend, attach transactions to contracts via match logic, and infer positioning using **discrete HCIQ percentile points** (low/10th/25th/50th/high). *(Urgent Request.pdf)*
- Data and interpretation constraints are material: HCIQ data access is limited (no full dump), benchmark coverage may be incomplete, and benchmarks **exclude rebates**, requiring clear caveats. *(Urgent Request.pdf)*
- Execution success depends on an operating model: defined methodology (“gates”), cadence, roles (Team Lead/PM), and shared tooling (starting small, scaling to monday.com). *(Connect.pdf)*
- Adoption/conversion realities matter alongside price: complex tier structures and member buying behavior can limit realized value even if benchmark rank improves. *(Connect.pdf)*
- Immediate enablement actions were already volunteered: Matt to set up a workspace (monday.com) and tag analyst support; Brian to connect data resources (BigQuery snapshot logic, SharePoint benchmark files). *(Connect.pdf; Urgent Request.pdf)*
- Several critical unknowns remain: contract list/portfolio size for July 1+, team composition/ownership, contract match hierarchy (locals/SCAs masking nationals), and acceptable benchmark coverage thresholds. *(Connect.pdf; Urgent Request.pdf)*

---

## Themes (with evidence references)

### 1) National contract competitiveness is the central business driver
- Persistent feedback that national contracts “aren’t competitive,” with urgency to quantify and remediate. *(Connect.pdf)*
- Explicit ask to determine where “top tier national pricing” ranks vs benchmarks (e.g., 10th/25th/38th). *(Urgent Request.pdf)*

### 2) Move from anecdote to measurement via weighted benchmark ranking
- Aggregate, weighted measure requested (not SKU-by-SKU) using 6 months of spend and contract match logic. *(Urgent Request.pdf)*
- Modeled spend at discrete benchmark points to infer percentile/rank ranges. *(Urgent Request.pdf)*

### 3) Need for a repeatable operating model (gates, cadence, ownership)
- Agreement that a structured methodology is necessary: “gates,” cadence, roles, and PM discipline. *(Connect.pdf)*
- Contract review workstream explicitly framed as “if it doesn’t pass the test, send it back,” implying governance checkpoints. *(Connect.pdf)*

### 4) Data limitations and attribution logic are key dependencies/risks
- HCIQ will not provide a full benchmark dump; reliance on returned files + BigQuery monthly snapshots. *(Urgent Request.pdf)*
- Spend attribution is complicated by locals/SCAs potentially masking national-eligible matches. *(Urgent Request.pdf)*
- Benchmark coverage gaps must be quantified; threshold for acceptability not yet decided. *(Urgent Request.pdf)*

### 5) Practical execution enablement: tooling + analytics capacity
- Start with simple tooling (Planner) and scale to monday.com; Matt to stand up a workspace. *(Connect.pdf)*
- Analyst-level support is assumed/needed to “drive analytics work.” *(Connect.pdf; Urgent Request.pdf)*

### 6) Contract design complexity vs member behavior affects realized competitiveness
- Example concern: “12 tier contract” while members only use four tiers; conversion challenges in certain categories (sutures/gloves). *(Connect.pdf)*

### 7) AI productivity is present but ancillary to the core competitiveness problem
- Team discussed using AI (NotebookLM, Gemini) to transform user guides into training assets; advice to use brand templates to avoid “AI-looking” decks. *(Connect.pdf)*

---

## Notable Decisions / Confirmations

- Proceed with contract review participation for July 1+ launches; contracts failing criteria will be sent back. *(Connect.pdf)*
- Adopt an operating model approach (methodology/gates/cadence/roles) to avoid ad hoc reviews. *(Connect.pdf)*
- Stand up a shared work space (monday.com) and start small, evolve over time; Matt to help drive PM/cadence. *(Connect.pdf)*
- Benchmark analysis parameters confirmed:
  - Use **6 months** of volume/spend. *(Urgent Request.pdf)*
  - Weight by spend attached to each contract via match logic. *(Urgent Request.pdf)*
  - Deliver **contract-level** results first (tier rollups explicitly not required initially). *(Urgent Request.pdf)*
  - Use the **most recent** HCIQ BigQuery snapshot. *(Urgent Request.pdf)*

---

## Open Questions / Follow-ups

- What is the definitive list and count of contracts launching “July 1 or later,” and when will it be provided? *(Connect.pdf)*
- Final working group roster and how Tyson Hofeling fits; whether others are included beyond Ken/Matt/speaker. *(Connect.pdf)*
- Who owns PM/cadence long-term (Team Lead / project manager)? *(Connect.pdf)*
- Will Shimshock provide additional context before Friday, and what is it? *(Connect.pdf)*
- How to define contract match hierarchy when locals/SCAs mask national-eligible spend attribution. *(Urgent Request.pdf)*
- How to infer percentile rank between discrete HCIQ points (low/10th/25th/50th/high). *(Urgent Request.pdf)*
- What benchmark coverage threshold is acceptable before manual pulls are required. *(Urgent Request.pdf)*
- Whether leadership ultimately wants rollups beyond contract level (e.g., “service line level at minimum”). *(Urgent Request.pdf)*
- Whether previously excluded categories will be excluded again or included in the new analysis. *(Urgent Request.pdf)*

---

## Recommended Next Actions

1) **Confirm scope + governance**
- Obtain and lock the **July 1+ contract inventory** (list + counts) and define the review “test” criteria and gating steps. *(Connect.pdf)*
- Finalize team roster, roles, and **PM/cadence owner**; document in the shared workspace. *(Connect.pdf)*

2) **Deliver the urgent benchmark output with clear caveats**
- Produce the **contract-level weighted ranking** vs HCIQ using the **most recent BigQuery snapshot** and **6-month** spend window; clearly annotate that **rebates are excluded** (price-point only). *(Urgent Request.pdf)*

3) **Resolve the two biggest methodological risks**
- Decide and document the **contract match hierarchy** treatment for locals/SCAs vs national contracts (and how that impacts weighting). *(Urgent Request.pdf)*
- Set an explicit **benchmark coverage threshold** and required “gap reporting” standard for missing benchmarks. *(Urgent Request.pdf)*

4) **Stand up execution infrastructure**
- Implement the initial **monday.com** (or Planner) workspace with: contract list, owners, gates, due dates, and analytics artifacts/links (BigQuery table reference, SharePoint benchmark files). *(Connect.pdf; Urgent Request.pdf)*

5) **Align remediation to adoption realities**
- In review gates, incorporate checks for **tier complexity vs member buying behavior** (e.g., excessive tiers) and conversion risk signals, not just benchmark rank. *(Connect.pdf)*

## Individual Document Syntheses

- connect__c349351683__synthesis.md

- urgent_request__c7a54da9ab__synthesis.md
