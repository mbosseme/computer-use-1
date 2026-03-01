# Skills Index

This directory contains reusable "skills" (workflows, heuristics, and recovery rules) for the GitHub Copilot Agent.

## Available Skills

### Browser & Research
- **[browser-automation-core](browser-automation-core/SKILL.md)**: **(Start here for web tasks)** General-purpose browser automation patterns (selectors, waiting, scrolling, overlays, HITL). **Now includes**: Visual Evidence Mode (when to screenshot) + Two-Speed Execution Policy (FAST vs DELIBERATE lanes) + M365 Copilot model heuristic (`GPT-5.2 Think` by default).
- **[training-navigation](training-navigation/SKILL.md)**: Specialized logic for navigating gated training modules (timers, videos, quizzes).
- **[research-ladder](research-ladder/SKILL.md)**: Choose the right research depth; escalate Bing → Tavily → Playwright; capture evidence consistently.
### Data & Analytics
- **[bigquery-data-exploration](bigquery-data-exploration/SKILL.md)**: **(Start here for cross-project BQ queries)** BigQuery patterns for cross-project access, schema discovery, product/entity matching, and Dataform transformations.
- **[bigquery-data-models](bigquery-data-models/SKILL.md)**: **(Start here for BigQuery work)** Authentication, MCP toolbox usage, data dictionaries, query patterns, and privacy guardrails for documented BigQuery tables.
- **[bigquery-data-dictionaries](bigquery-data-dictionaries/SKILL.md)**: Profile BigQuery tables and generate/update markdown data dictionaries with schema metadata and column statistics. Uses `tools/bigquery-profiling/`.
- **[product-entity-resolution](product-entity-resolution/SKILL.md)**: **(Start here for "Messy" ID Matching)** Workflow for mapping non-standard external IDs (NDCs, Vendor SKUs) to internal Master Data using web search, bridge identifiers, and transaction history lookups.
- **[premier-data-analytics](premier-data-analytics/SKILL.md)**: **(Start here for Premier Purchasing Data)** Critical "Tribal Knowledge" for working with ERP vs. Wholesaler datasets, resolving true OEMs vs. Distributors, and joining strictly safe facility blinds. Use this to avoid common traps like misidentified manufacturers or mismatched vendor names.
- **[analysis-decision-modeling](analysis-workflow/decision-modeling.md)**: **(Start here for "Build vs Buy" / Underwriting)** Comprehensive workflow for scenario modeling (Evidence Ledger → Data/Logic Split → Scenario Grid → Decision Memo).
  - Includes **[model_template.py](analysis-workflow/model_template.py)**: A minimal Python template for scenario-grid analyses. Copy to `runs/<RUN_ID>/scripts/` and customize.

### Document Generation
- **[document-synthesis-llm](document-synthesis-llm/SKILL.md)**: **(Start here for document summarization)** Extract text from PDFs/EMLs, synthesize via LLM with retry/backoff, handle context limits.
- **[document-generation-sow](document-generation-sow.md)**: Draft and generate formal SOW documents using Premier Standard formatting.
- **[pptx-deck-generation](pptx-deck-generation/SKILL.md)**: **(Start here for presentations)** Build branded PowerPoint decks with python-pptx, charts, and PDF export.

### Email & Integrations
- **[graph-email-search](graph-email-search/SKILL.md)**: Microsoft Graph mail search/export patterns (SentItems, $filter → $search fallback, paging, safety).
- **[graph-calendar-scheduling](graph-calendar-scheduling/SKILL.md)**: Read calendars, find availability, and analyze meeting history.
- **[tools/graph](../../tools/graph/README.md)**: Reusable Graph CLI utilities for mutual slot finding and structured draft-email creation.
- **[google-drive-download](google-drive-download/README.md)**: Authenticate with Google Drive (OAuth 2.0 / HITL) and download files/export Sheets to Excel reliably.
- **[gmail-search](gmail-search/README.md)**: Authenticate with Gmail (OAuth 2.0 / HITL), search specific queries, and read email bodies safely.
- **[gmail-draft](gmail-draft/README.md)**: Authenticate with Gmail (requires `compose` scope), and create **draft** emails for user review. (Does not send).

### Templates
- **[_template](_template/SKILL.md)**: Structure for creating new skills. Use when a new recurring workflow emerges.

## Skill selection heuristic
- Choose **1 primary** skill + up to **2 supporting** skills.
- For any web UI task, default the primary skill to **browser-automation-core**.
- Skills are **on-demand memory**: the agent must open the `SKILL.md` file to load it into context.
- If a workflow repeats 2+ times and doesn’t fit existing skills, **propose** a new skill folder name/path and ask Matt (do not create it unless asked).

## How Copilot should use skills

1.  **At task start**:
    - Open this index (`.github/skills/README.md`).
    - Identify 1–3 relevant skills.
    - Open those skill files to load them into context.
    - *Then* proceed with the task.

2.  **When stuck**:
    - Re-open the relevant skill file.
    - Check the "Recovery rules" section before trying random fixes.

3.  **After a workaround is learned**:
    - Update the relevant skill file immediately (vendor-agnostic rules).
    - Add a run note referencing the update.
