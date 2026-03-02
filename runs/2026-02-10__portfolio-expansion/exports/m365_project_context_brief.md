# M365 Project Context Brief — Portfolio Expansion

Generated: 2026-03-01 (run-local)

## Access Method + Constraints

- Successfully authenticated to Microsoft Graph with delegated scopes: `Calendars.ReadWrite`, `Mail.ReadWrite`, `Tasks.ReadWrite`, `User.Read`.
- Teams chat/message APIs are **not accessible** in this token because `Chat.Read*` scopes are missing.
- As a result, this brief uses:
  - Email threads (full exports)
  - Teams meeting invite/acceptance artifacts present in email/calendar
- Not used in this run: direct M365 Copilot UI via Playwright (no Playwright browser tools were available in this execution environment).

## Collected Artifacts

### Primary outputs
- `runs/2026-02-10__portfolio-expansion/exports/m365_context_raw.json`
- `runs/2026-02-10__portfolio-expansion/exports/m365_context_summary.md`
- `runs/2026-02-10__portfolio-expansion/exports/m365_threads/portfolio_expansion_update.md`
- `runs/2026-02-10__portfolio-expansion/exports/m365_threads/on_off_non-contract_analysis.md`
- `runs/2026-02-10__portfolio-expansion/exports/m365_threads/fusion_team_weekly_check-in.md`
- `runs/2026-02-10__portfolio-expansion/exports/m365_threads/data_to_support_portfolio_expansion.md`
- `runs/2026-02-10__portfolio-expansion/exports/m365_threads/extrapolating_from_core_hs_set.md`
- `runs/2026-02-10__portfolio-expansion/exports/m365_threads/data_and_analytics_to_support_strategic_initiatives.md`

### Coverage metrics from pull
- Unique messages retrieved across query set: **1,324**
- Project-signal messages: **727**
- Priority sender hits:
  - Bill Marquardt: **51**
  - Bruce Radcliff: **12**
  - Brian Hall: **31**
- Mentions / participation hits:
  - Zach Lilly: **338**
  - Brian Hall: **361**
  - Jennie Hendrix: **100**
  - Jordan Garrett: **132**
- Relevant calendar events detected: **5**

## High-Value Context (Project-Relevant)

## 1) Project kickoff intent from leadership (Bill/Bruce)
Source: `data_to_support_portfolio_expansion.md`

- Bill set the objective to "significantly expand portfolio coverage" and explicitly asked for collaboration between data + business leads.
- Bill directed urgency and asked Matt to set up strategy sessions with Jordan/Brian quickly.
- Jordan responded affirmatively and aligned to collaborate.

Implication:
- Confirms origin story and urgency for the fusion-team execution model.

## 2) Fusion team operating model, roles, and cadence
Source: `fusion_team_weekly_check-in.md`

- Weekly check-in thread and recurring Teams meeting were established.
- Captured role model in meeting notes:
  - Jordan = PO
  - Zach = BizTech
  - Jennie (Jenny) = SME
- Scope captured in meeting agenda/notes:
  - Refine invoice-centric model
  - Integrate ERP + Rometra + TSA
  - Resolve data quality / supplier categorization blockers

Implication:
- Confirms who was expected to drive execution and the intended integration architecture.

## 3) Key narrative and estimates shared to Bill
Source: `portfolio_expansion_update.md`

- Zach’s update message communicates the now-familiar topline range:
  - Total non-labor estimate: **$122B–$132B**
  - Clinical: **$52B–$57B**
  - Non-Clinical: **$50B–$54B**
  - Pharma: **$18B–$19B**
  - Food: **~$2B**
- Message explicitly states clinical+non-clinical extension path via 100-system cohort and ~80% observed clinical coverage.
- Bill immediately requested On/Off/Non-Contract breakdown availability.
- Follow-up from Matt confirms immediate limitation for non-clinical granularity timing and points to Jordan’s decomposition work.

Implication:
- Reinforces that the estimate framework and the current open item (NC decomposition) are directly responsive to leadership asks.

## 4) On/Off/Non-Contract methodology decisions
Source: `on_off_non-contract_analysis.md`

- Matt states Pharma/Food On/Off/Non splits cannot be credibly derived from AP invoice data alone due to aggregated wholesaler/distributor invoices lacking product detail.
- Brian validates Rx wholesaler data as the likely proxy and brings in Justin (Pharma) + Joan (Food).
- Jordan refines definitions, especially **Off-Contract** into two distinct scenarios:
  1. Spend with Premier-contracted supplier/category but not transacting through Premier contract.
  2. Spend in a category where Premier has a contract, but member uses non-Premier-contracted supplier.
- Joan directs Food support path through Bob Lough.

Implication:
- Confirms the rationale behind the current project stance:
  - Clinical/NC can be modeled via TSA-driven pipeline
  - Pharma/Food require tracing-led methods and service-line owner input

## 5) Expansion to broader strategic initiatives
Source: `data_and_analytics_to_support_strategic_initiatives.md`

- Bill asks for a unified data model supporting growth + admin fee objectives with consistent nomenclature.
- Calls out deep-domain ownership by service line and one cohesive rollup for Bruce/Karr.
- Follow-up alignment from Caitlin confirms team structure and next-step governance cadence.

Implication:
- Confirms expectation that this work should be reusable and harmonized across initiatives, not a one-off analysis.

## Named-Person Context (Requested Focus)

### Zach Lilly
- Co-authored core leadership update and owned communication framing to Bill.
- Listed as BizTech role in fusion team.
- Directly involved in model refinement and update messaging.

### Brian Hall
- Central operator for Clinical/NC analytics and stakeholder communication.
- Pulled in Justin/Joan for Pharma/Food method alignment under deadline pressure.
- Repeatedly tied to dashboard extension and strategic rollup asks.

### Jennie Hendrix
- Named SME in fusion team role assignment.
- Explicitly referenced for Clinical service-line assessment asks.

### Jordan Garrett
- Named PO in fusion team role assignment.
- Owner of NC category decomposition path.
- Added important definition precision for Off-Contract handling.

### Bill Marquardt
- Leadership sponsor pressing for urgency, clarity, and practical On/Off/Non outputs.
- Reinforced need for cohesive, cross-team data model and clear executive rollups.

### Bruce Radcliff (email evidence)
- Included in Portfolio Expansion leadership threads.
- Signals urgency around status/progress and practical metrics framing.

## Current Gaps / Follow-up Needed

1. **Direct Teams chat content** is still missing due scope constraints (`Chat.Read*` not granted).
2. If chat transcripts are required, rerun after adding one of:
   - `Chat.ReadBasic`, `Chat.Read`, or `Chat.ReadWrite`
3. Optional next pull after scope update:
   - `me/chats`
   - chat membership filtering by named participants
   - targeted export of message windows around Jan–Feb 2026 kickoff/decision dates

## Operational Notes

- All files above are run-local under `runs/2026-02-10__portfolio-expansion/exports/`.
- No core repo files changed.
