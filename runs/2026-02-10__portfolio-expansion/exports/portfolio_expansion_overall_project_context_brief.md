# Portfolio Expansion — Overall Project Context Briefing

Generated (UTC): 2026-03-01  
Run ID: `2026-02-10__portfolio-expansion`

## Objective
Provide a detailed, decision-ready context briefing on Portfolio Expansion with emphasis on:
- leadership ask and business intent,
- work completed so far,
- risks/concerns that could affect confidence or delivery,
- concrete planned next steps and owners.

## Leadership Ask (What leadership is asking for)

### Core ask
Leadership requested a clear, defensible view of the full spend opportunity and growth potential across key service lines, then asked the team to classify spend into actionable buckets to support execution planning.

### Practical expectations from leadership communications
1. Establish a high-level but credible Total Addressable Market narrative.
2. Break spend into operational buckets (On-Contract, Off-Contract, Non-Contract, Unknown/Needs Review).
3. Show enough progress quickly for executive updates while deeper drill-downs are being built.
4. Align this work with related strategic efforts (especially admin-fee/growth modeling) so one coherent model can serve multiple initiatives.
5. Add business actionability (for example, savings/increase layering) as the model matures.

## Business Outcome Sought
Convert a largely directional leadership narrative into measurable, repeatable analytics that can:
- explain current coverage,
- estimate upside potential,
- identify what is addressable vs non-addressable,
- and guide service-line owners toward prioritized actions.

---

## Project Scope and Method Context

### Primary service-line scope
- Clinical
- Non-Clinical
- Pharmacy
- Food

### Current methodological shape
- Clinical + Non-Clinical analysis is being driven through TSA/invoice-informed modeling and category cleanup workflows.
- Pharmacy + Food require additional service-line-specific tracing/proxy methods and owner-led interpretation.

### Important framing constraints already discussed by team
- Invoice/AP data is useful for high-level mix and benchmarking but has limits for precise on/off attribution in some domains.
- Source asymmetry across service lines means confidence levels are not uniform.

---

## Work Completed So Far

## 1) Program mobilization and operating model
- A fusion-team operating model was stood up, with recurring check-ins and explicit role participation from product, SME, and technical leads.
- Weekly cadence and work-tracking discipline were put in place.
- Team aligned around staged delivery: rapid top-level rollup first, deeper detail refinement immediately after.

## 2) Initial TAM and service-line estimates delivered
- Team communicated a first leadership-facing estimate set for non-labor purchasing opportunity, including service-line-level ranges.
- Working narrative included the notion of a practical ceiling and conversion sensitivity framing.

## 3) Bucket framework advanced from concept to execution logic
- On/Off/Non/Unknown categories were not only requested but operationalized into specific analytical definitions.
- Non-clinical decomposition and category cleansing workflows were started to improve assignability and reduce Unknown.

## 4) Service-line owner collaboration initiated
- Clinical and non-clinical threads were actively coordinated.
- Pharmacy and Food leads were pulled in for methods where direct AP-level decomposition is insufficient.

## 5) Data model and implementation work progressed
- Teams/transcript context indicates concrete model integration steps, including remapping/merge mechanics and flagging logic in CY2025-enriched workflows.
- Additional transcript-level detail surfaced implementation architecture decisions and known pain points in dashboard consumption.

## 6) Leadership reporting cadence established
- Draft and follow-up rollups were delivered to Bill/Bruce.
- Leadership requested continued refinement and improved actionability overlays.

---

## Quantitative Signals (Current)

Repeatedly cited in working materials:
- Total non-labor TAM-style range: **~$122B–$132B**
- Clinical: **~$52B–$57B**
- Non-Clinical: **~$50B–$54B**
- Pharmacy: **~$18B–$19B**
- Food: **~$2B**
- Theoretical NAF ceiling framing used in narrative: **~$1.52B**
- Large-scale data footprint references in implementation context (for example, 100M+ row-scale tables).

Interpretation note:
- These values are fit-for-guidance in current leadership updates but still depend on method harmonization and service-line-specific confidence reconciliation.

---

## Risks and Concerns (Detailed)

## 1) Methodology alignment risk (high)
### Issue
Evidence shows tension between “TSA-only” communication in some leadership contexts and extrapolation-enabled methodology in model documentation.

### Impact
- Can reduce trust in numbers if audiences perceive methodology drift.
- Risks conflicting executive interpretations of what is measured vs estimated.

### What is needed
- One explicit and reusable methodology statement that defines approved use-cases for TSA-only and extrapolated views.

## 2) Data quality and classification risk (high)
### Issue
Transcript-level context and working notes indicate ongoing category/supplier cleanup challenges and potential logic defects in reporting paths.

### Impact
- Bucket misclassification can materially distort prioritization and action planning.
- Unknown/Needs Review may remain too large without structured remediation.

### What is needed
- Defect register + remediation tracking tied to release cadence.
- Clear “known limitations” callouts in each leadership update.

## 3) Service-line confidence asymmetry (medium-high)
### Issue
Clinical/non-clinical and pharmacy/food rely on different data pathways and operational assumptions.

### Impact
- Aggregate totals may imply precision that does not exist uniformly.
- Decisions may over-index to stronger-measured domains.

### What is needed
- Confidence tiers by service line in all rollups.

## 4) Traceability and auditability risk (medium)
### Issue
Operational users raised concern about mapping dashboard outputs back to source logic and tables.

### Impact
- Slows decision cycles.
- Increases rework and challenge loops from stakeholders.

### What is needed
- Short lineage annex from metric → table → transformation rule.

## 5) Adoption/usability risk (medium)
### Issue
Transcript context showed practical difficulty navigating and interpreting Tableau artifacts without guided walkthrough.

### Impact
- Good analysis may be under-used or misinterpreted.
- Business value realization delayed.

### What is needed
- Standard enablement pack: walkthrough + quick interpretation guide.

## 6) Scope-boundary narrative risk (medium)
### Issue
Acute vs non-acute membership and inclusion assumptions were questioned in live discussions.

### Impact
- Leadership may compare unlike scopes across updates.

### What is needed
- Consistent scope labels on every chart/table.

---

## Planned Next Steps (Execution Plan)

## Immediate (next 1–2 weeks)
1. Publish method policy note (TSA-only vs extrapolated usage) and apply to all rollups.
2. Refresh leadership pack with confidence-by-service-line and explicit limitations.
3. Complete current round of category/supplier cleanup and re-run bucket outputs.
4. Validate and fix known logic defects affecting bucket assignment/reporting.
5. Deliver short dashboard enablement session and reference guide for business users.

## Near-term (2–4 weeks)
1. Converge Portfolio Expansion and adjacent strategic model work into a unified data model roadmap.
2. Operationalize a recurring decision log (decision, owner, date, evidence type, downstream impact).
3. Build a stable executive view and separate analyst drill-down view to reduce narrative mismatch.

## Decision requests for leadership
1. Confirm official methodology language for external/internal audiences.
2. Confirm acceptable confidence threshold by service line for executive updates.
3. Confirm prioritization order for deeper drill-down investment (which domains first).

---

## Ownership and Responsibility Snapshot

- **Bill Marquardt**: executive sponsor, urgency/framing, decision direction.
- **Bruce Radcliff**: executive consumer, business-impact/actionability expectations.
- **Brian Hall**: operating lead for cross-service-line coordination and reporting integration.
- **Jordan Garrett**: product ownership path, non-clinical decomposition and prioritization.
- **Zach Lilly**: technical/business execution, model/query pipeline and analytical delivery.
- **Jennie Hendrix**: SME reporting interpretation and business enablement support.
- **UdayKumar Kapu (supporting)**: integration/enrichment implementation support.

---

## Current Status Assessment

### What is strong now
- Clear leadership alignment on objective and urgency.
- Repeatable cadence established.
- Early top-level outputs delivered and iterated.

### What blocks confidence at scale
- Method reconciliation and communication consistency.
- Remaining data quality/logic hardening.
- Usability and traceability gaps for non-technical consumers.

### Overall status
**Progressing with momentum, but entering a quality-and-governance hardening phase.**

---

## Primary Source Set Used

- `m365_context_summary.md`
- `m365_project_context_brief.md`
- `m365_copilot_browser_context.md`
- `m365_threads/portfolio_expansion_update.md`
- `m365_threads/on_off_non-contract_analysis.md`
- `m365_threads/fusion_team_weekly_check-in.md`
- `m365_threads/data_to_support_portfolio_expansion.md`
- `m365_threads/extrapolating_from_core_hs_set.md`
- `m365_threads/data_and_analytics_to_support_strategic_initiatives.md`
