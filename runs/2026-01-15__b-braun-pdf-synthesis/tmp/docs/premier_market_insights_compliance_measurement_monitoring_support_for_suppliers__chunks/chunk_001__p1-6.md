## Chunk 1 (pages 1-6)

## Key points
- Provides a “generalized, privacy-safe approach” for IV-therapy manufacturers to measure and monitor contract compliance across Premier membership.
- Measures compliance monthly by “category, and site/department,” aligning scope to “exact contract/tier language” and manufacturer taxonomy (“families/SKUs”).
- Defines **leakage** as “off-contract competitor volume inside the tier scope.”
- Uses “triangulated” data inputs: provider ERP, med-surg distributor tracings, pharmaceutical wholesaler tracings, and “manufacturer on-contract tracings.”
- Privacy/governance approach is “Name-blind by default” using “stable, de-identified facility and department IDs” plus aggregated geography (with suppression “where N<2”).
- Reporting avoids pricing: “report units and optional standardized dollars (fixed weights), never contract prices.”
- Framework organized into **Five Pillars**:
  1. Name-blind compliance observability (acute)
  2. Expected-volume modeling for any U.S. facility (acute)
  3. Permissioned named compliance (acute)
  4. Compliance risk early-warning (acute)
  5. Non-acute compliance intelligence (Premier-centric)

## Decisions / confirmations
- Compliance measurement will “honor exact contract/tier language” and can align to manufacturer taxonomy (families/SKUs).
- Default mode is “Name-blind,” with a defined governance model (de-identified stable IDs; geo suppression “where N<2”).
- “No pricing exposure” (units and optional standardized dollars only).
- Named visibility requires explicit member permission: “Member signs Premier’s permission form (National) → flip specific facilities to named.”

## Open questions
- Unknown: specific implementation details for the “permission form (National)” process/timelines.
- Unknown: how cohorts are exactly defined for “system cohort” and “geo cohort” leaderboards beyond listed geographies (ZIP3/county/CBSA).
- Unknown: what “optional standardized dollars (fixed weights)” methodology is.
- Unknown: what the “appendix” contains (“Example Presentation to Baxter”) and any results shown there.

## Action items (with owners if present)
- Manufacturers: “Map & size” using “Pillars 1–2 to rank cohorts and quantify gaps (acute + non-acute).”
- Manufacturers: “Explain” by layering diagnostics drivers and risk signals.
- Manufacturers: “Act” by aiming field activity at top cohorts and “request permission at key accounts” to convert to named management (Pillar 3).
- Manufacturers: “Protect” by watching early-warning signals to prevent “backsliding” (Pillar 4).
- Manufacturers: “Extend” the method “to other categories beyond IV therapy.”
- Optional service (owner unknown): “Short, structured outreach to code standardized root-cause tags per anonymous target.”

## Notable metrics/claims (exact phrases where possible)
- Purpose/claims:
  - “Measure contract compliance (tier/market-share requirements) across Premier’s membership.”
  - “Locate likely compliance gaps by region, facility type, and department —without revealing names by default.”
  - “Model expected volumes for any U.S. facility (public & private attributes from 100-Top Hospitals Program).”
- Core definitions:
  - “Leakage = off-contract competitor volume inside the tier scope.”
  - “Inferred gap % = (Expected − Your observed volume) ÷ Expected, with confidence bands.”
- Privacy/governance:
  - “Name-blind by default”
  - “suppressed where N<2”
  - “No pricing exposure: report units and optional standardized dollars (fixed weights), never contract prices.”
- Operational cadence/outputs:
  - “Monthly refresh; quarterly roll-ups; named account packs for permissioned sites.”
  - Outputs include: “Dashboards + CSV/Excel,” “Anonymous Target Cards,” and “Alerts.”
- KPIs to track:
  - “On-contract share (pp) lift in targeted cohorts.”
  - “Leakage reduction by family/SKU and department.”
  - “Time-to-stabilize post-award; reversion rate.”
  - “SLA stress incidence vs. compliance trend.”
  - “Opt-in coverage (named accounts turned on) and results vs. anonymous baselines.”
