# Admin Fee Data Discovery + Portfolio Expansion Relationship Brief

Generated (UTC): 2026-03-01  
Run ID: `2026-02-10__portfolio-expansion`

## Scope
This brief combines:
1. **Graph API evidence** from the Admin Fee thread and related exported project threads.
2. **M365 Copilot (Work mode) synthesis** across emails/chats/files with source-backed citations.

Focus: clarify Joe Bichler’s Admin Fee effort and how it relates to the Portfolio Expansion initiative with Justin Schneider as executive sponsor.

## What the Admin Fee effort is (Joe-led)
From the Graph-captured Admin Fee thread, Joe’s objective is to create a **leadership-aligned baseline (day-0)** of admin fee economics and then evolve it into an **interactive, refreshable dashboard**.

Core requirements in-thread include:
- views by **service line / program / supplier / team member-leader**,
- data points like **Sales Volume, Gross Admin Fee (GAF), WAAF%**,
- inclusion of other revenues (e.g., **MSAs, Market Insights, pharmacy retained components**),
- historical trendability (requested up to ~5 years),
- cross-reference dimensions (supplier top parent, service line/program mapping, commitment/program labels).

## Timeline (evidence-grounded)
- **2026-02-02**: initial Admin Fee Data Discovery meeting invite created.
- **2026-02-17**: Joe sends data-gathering framework and baseline reporting requirements.
- **2026-02-20**: follow-up session on available Admin Fee data context.
- **2026-02-23**: Joe refines scope and sets target: **first draft raw data collection by 2026-03-06**.
- **2026-02-24**: Portfolio Expansion update explicitly states overlap and need for one aligned data model across projects.

## Owners and roles (current signal)
- **Joe Bichler**: lead for Admin Fee Data Discovery questions, reporting asks, and scope definition.
- **Bill Marquardt**: executive coordination and cross-initiative alignment.
- **Rachael Rollins**: scoping/timeline partner with Joe.
- **Brian Hall + Fusion/ABI analytics team**: delivery engine for service-line analytics and rollups; explicitly connected to both initiatives.
- **Justin Schneider**: executive sponsor on Portfolio Expansion threading/cadence and pharmacy leadership context.

## How Admin Fee relates to Portfolio Expansion
Relationship is **direct, not adjacent**:
1. **Shared inputs**: both streams rely on overlapping spend/admin-fee source foundations and service-line mappings.
2. **Shared modeling need**: explicit statement from the Portfolio Expansion update says the projects should converge into **one data model** because many inputs are the same.
3. **Shared delivery capacity**: explicit plan to align/split/coordinate analytics resources across both workstreams.
4. **Shared decision layer**: both require leadership-ready baseline views first, with deeper drill-down and operational dashboards after.

## Risks / concerns to manage now
1. **Metric framing tension**: optimizing on admin-fee dollars alone can bias Portfolio Expansion prioritization if contract-strength and strategic fit are not balanced.
2. **Data completeness risk**: historical depth and alternative-revenue coverage may be uneven by source/service line.
3. **Capacity contention**: one analytics pool serving two urgent initiatives can create stop-start delivery unless priorities are explicit.
4. **Model governance risk**: without a common metric dictionary and lineage, merged outputs can diverge by audience.

## Recommended next steps
1. Publish a **joint metric dictionary** for both projects (definitions, grain, inclusions/exclusions, confidence tier).
2. Approve a **single integrated backlog** with named owners for Admin Fee + Portfolio Expansion dependencies.
3. Lock **day-0 baseline pack** (fields, views, refresh cadence) before adding downstream enhancements.
4. Add a standing **cross-project governance checkpoint** (Joe/Bill/Brian + Justin-sponsored Portfolio Expansion representation).
5. Produce one executive readout that separates:
   - factual baseline,
   - derived estimates,
   - open assumptions.

## Evidence map
### Graph artifacts
- `runs/2026-02-10__portfolio-expansion/exports/m365_context_raw.json`
  - Contains `FW: Admin Fee Data Discovery` body text with Joe’s detailed requirements and Mar 6 target.
- `runs/2026-02-10__portfolio-expansion/exports/admin_fee_discovery_graph_hits.json`
  - Fresh Graph search hit metadata for `Re: Admin Fee Data Discovery`.
- `runs/2026-02-10__portfolio-expansion/exports/m365_threads/portfolio_expansion_update.md`
  - Explicit overlap statement and one-model recommendation in the Feb 24 update.

### Copilot (Work mode) source-backed synthesis
- Retrieved source-backed response in M365 Copilot chat: **“Admin Fee Effort Analysis and Portfolio Expansion Link”**.
- Cited source types in response include:
  - Email: `Re: Admin Fee Data Discovery` (dated Feb 23, 2026)
  - File: `FW: Admin Fee Data Discovery` PDF thread compilation
  - Meeting invite: Admin Fee Data Discovery (Feb 20, 2026)
  - Teams chats: `Fusion Team Weekly Check-in`, `Portfolio Expansion Fusion Dev`, and timeline/capacity references.

## Confidence and caveats
- **High confidence**: Admin Fee purpose/scope, timeline milestones, and explicit overlap statement in Portfolio Expansion update.
- **Medium confidence**: Copilot chat-derived integration recommendations (credible and source-backed, but still synthesis-level).
- **Caveat**: Direct Teams API extraction remains constrained by Graph delegated chat scope limits; Copilot retrieval is used as the secondary path for chats/transcripts/files.
