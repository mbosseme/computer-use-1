# Architecture

## Overview
This repo is a local-first “computer-use” agent: it executes user-directed work across web UIs (via Playwright MCP), terminal automation, and deterministic local transforms, while maintaining durable, repo-based memory in docs + skills.

Core principles:
- Local-first and reproducible: prefer deterministic transforms over manual UI edits when possible.
- Safety first: human-in-the-loop (HITL) for auth and irreversible actions.
- Durable memory: instructions are always-on; skills are loaded on demand; run logs are sanitized.
- Parallel-run isolation: each run uses a unique `RUN_ID` and isolated artifacts/state.

## Components

## Operational usage pattern (how this is used in practice)
- Keep one “launcher” VS Code window opened on `main` for creating run branches + git worktrees.
- Do the run work in one VS Code window per worktree (one per `RUN_ID`).
- Treat `run/<RUN_ID>` as the long-lived run journal (runs may last multiple days).
- Promote only core changes back to `main` (see [docs/PARALLEL_RUNS.md](PARALLEL_RUNS.md)).

### Agent runtime (Copilot in VS Code)
- The “agent” is the Copilot chat + tool-using runtime.
- Operates against the current workspace, and can edit files, run terminal commands, and call MCP tools.

### Browser automation (Playwright MCP)
- Primary mechanism for interacting with web UIs.
- Policy:
  - Stop for SSO/MFA/CAPTCHA.
  - Ask immediately before clicks that submit/approve/pay/finish.
  - Prefer stable selectors (`data-testid`, roles + accessible names).

Parallel-run note:
- For parallel worktrees/windows, run a workspace-scoped Playwright MCP server per VS Code window/worktree and configure per-run `--user-data-dir` / `--output-dir` under `runs/<RUN_ID>/...`. Avoid binding tool calls to a shared/global server, which can silently defeat isolation.

Config lives in `.vscode/mcp.json` (this is the only MCP server configured in this repo by default).

### Web research (Bing + Tavily)
- **Bing web search (native)**: Best for quick lookups, broad discovery, and time-sensitive facts. No local install; policy-controlled by GitHub/Copilot settings.
- **Tavily (MCP, optional)**: Best for deep research loops (search → extract full docs). Requires an API key and runs as a local MCP server.

This repo does not commit third-party API-key-backed MCP servers. Configure Tavily in VS Code user MCP settings and use an input prompt for the API key (see [docs/Copilot Web Search Configuration and Usage.md](Copilot%20Web%20Search%20Configuration%20and%20Usage.md)).

### LLM access (Azure OpenAI GPT-5.2)
- This repo includes a starter Azure OpenAI **Responses API** client intended for reuse across runs.
- Implementation lives under [agent_tools/llm/](../agent_tools/llm/).
- Setup uses local environment variables via a repo-root `.env` (never commit secrets). See [.env.example](../.env.example).
- Guide and usage notes: [docs/GPT_5_2_INTEGRATION_GUIDE.md](GPT_5_2_INTEGRATION_GUIDE.md).

### Deterministic local transforms
- Prefer scripted, deterministic transforms over manual UI operations.
- Typical tooling: Python (e.g., `pandas`, `openpyxl`, `python-pptx`) when justified.
- One-off scripts and artifacts should be namespaced under `runs/<RUN_ID>/`.

### Database queries (DB MCP)
- Optional component when a run requires querying a data warehouse.
- Not configured in this repo by default; when added, keep exports and temp artifacts namespaced under `RUN_ID`.
- Prefer exporting results and applying deterministic local transforms.

### Microsoft Graph (Office 365)
- This repo supports delegated Microsoft Graph access via MSAL public client + interactive loopback auth.
- Implementation lives under [agent_tools/graph/](../agent_tools/graph/).
- See [docs/GRAPH_AUTH_REPLICATION_GUIDE.md](GRAPH_AUTH_REPLICATION_GUIDE.md) and [.env.example](../.env.example).
- Calendar support includes both event reads (`calendarView`) and verified free/busy via `calendar/getSchedule`.

## Repository “memory” model

### Always-on instructions
- `.github/copilot-instructions.md` is the always-loaded operating policy.

### Skills (loaded on demand)
- Skills are repo-based procedural memory.
- Before most tasks: open `.github/skills/README.md` and 1–3 relevant skills.
- Skills should be vendor-agnostic and focus on repeatable tactics.

### Logging
- Per-run continuity and artifacts (run-local): `runs/<RUN_ID>/...` (often uncommitted; no secrets/URLs/tokens).
- Per-session narrative notes (optional, intentionally-versioned): `notes/agent-runs/` (sanitized).
- Core repo work log (optional index): `docs/CORE_REPO_WORK_LOG.md` (PRs + git history are canonical).

Note:
- Run artifacts under `runs/` are tracked on run branches for rollback/continuity, but a PR guardrail blocks `runs/` changes from being merged into `main`.

## Data and artifacts
- Downloads: store under `runs/<RUN_ID>/downloads/` when explicitly approved.
- Temporary scripts/output: store under `runs/<RUN_ID>/tmp/` or `runs/<RUN_ID>/scripts/`.
- Never persist internal deep links, session tokens, or sensitive URLs in committed files.

## Execution flow
1. Create `RUN_ID` and isolate run folders under `runs/<RUN_ID>/`.
2. Load skills (skills index + 1–3 skills).
3. Perform work:
   - Browser automation via Playwright MCP
   - Terminal automation
   - Deterministic transforms
   - Optional DB queries
4. Gate irreversible actions and auth steps with HITL.
5. Record outcome:
   - Optionally write `notes/agent-runs/<date>_<slug>.md` when meaningful
   - Rely on PR descriptions + git history for core changes; optionally update `docs/CORE_REPO_WORK_LOG.md` if you want an index

## Non-goals
- Building a generic autonomous agent that runs unsupervised.
- Persisting secrets, internal tokens, or privileged deep links.
- Adding “nice-to-have” UX features beyond what the user requested.

## Open Questions / TODOs
- DB MCP: which backends are expected (BigQuery, Snowflake, etc.) and how should their MCP servers be configured?
- Standard run folder layout: should we commit a `runs/_template/` directory or keep it purely documented?
- Dependency packs: do we want optional requirements files (e.g., `requirements-excel.txt`) or keep guidance-only?
