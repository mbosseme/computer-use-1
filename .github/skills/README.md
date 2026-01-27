# Skills Index

This directory contains reusable "skills" (workflows, heuristics, and recovery rules) for the GitHub Copilot Agent.

## Available Skills

- **[_template](_template/SKILL.md)**: Structure for creating new skills. Use when a new recurring workflow emerges.
- **[training-navigation](training-navigation/SKILL.md)**: Specialized logic for navigating gated training modules (timers, videos, quizzes).
- **[browser-automation-core](browser-automation-core/SKILL.md)**: **(Start here for web tasks)** General-purpose browser automation patterns (selectors, waiting, scrolling, overlays, HITL). **Now includes**: Visual Evidence Mode (when to screenshot) + Two-Speed Execution Policy (FAST vs DELIBERATE lanes).
- **[research-ladder](research-ladder/SKILL.md)**: Choose the right research depth; escalate Bing → Tavily → Playwright; capture evidence consistently.
- **[graph-email-search](graph-email-search/SKILL.md)**: Microsoft Graph mail search/export patterns (SentItems, $filter → $search fallback, paging, safety).
- **[document-synthesis-llm](document-synthesis-llm/SKILL.md)**: **(Start here for document summarization)** Extract text from PDFs/EMLs, synthesize via LLM with retry/backoff, handle context limits.
- **[google-drive-download](google-drive-download/README.md)**: Authenticate with Google Drive (OAuth 2.0 / HITL) and download files/export Sheets to Excel reliably.
- **[gmail-search](gmail-search/README.md)**: Authenticate with Gmail (OAuth 2.0 / HITL), search specific queries, and read email bodies safely.
- **[gmail-draft](gmail-draft/README.md)**: Authenticate with Gmail (requires `compose` scope), and create **draft** emails for user review. (Does not send).
- **[analysis-decision-modeling](analysis-workflow/decision-modeling.md)**: **(Start here for "Build vs Buy" / Underwriting)** Comprehensive workflow for scenario modeling (Evidence Ledger → Data/Logic Split → Scenario Grid → Decision Memo).
  - Includes **[model_template.py](analysis-workflow/model_template.py)**: A minimal Python template for scenario-grid analyses. Copy to `runs/<RUN_ID>/scripts/` and customize.
- **[bigquery-data-models](bigquery-data-models/SKILL.md)**: **(Start here for BigQuery work)** Authentication, MCP toolbox usage, data dictionaries, query patterns, and privacy guardrails for documented BigQuery tables.
- **[bigquery-data-dictionaries](bigquery-data-dictionaries/SKILL.md)**: Profile BigQuery tables and generate/update markdown data dictionaries with schema metadata and column statistics. Uses `tools/bigquery-profiling/`.

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
