# Architecture

## Overview
This repo is a local-first “computer-use” agent: it executes user-directed work across web UIs (via Playwright MCP), terminal automation, and deterministic local transforms, while maintaining durable, repo-based memory in docs + skills.

Core principles:
- Local-first and reproducible: prefer deterministic transforms over manual UI edits when possible.
- Safety first: human-in-the-loop (HITL) for auth and irreversible actions.
- Durable memory: instructions are always-on; skills are loaded on demand; run logs are sanitized.
- Parallel-run isolation: each run uses a unique `RUN_ID` and isolated artifacts/state.

## Components

### Agent runtime (Copilot in VS Code)
- The “agent” is the Copilot chat + tool-using runtime.
- Operates against the current workspace, and can edit files, run terminal commands, and call MCP tools.

### Browser automation (Playwright MCP)
- Primary mechanism for interacting with web UIs.
- Policy:
  - Stop for SSO/MFA/CAPTCHA.
  - Ask immediately before clicks that submit/approve/pay/finish.
  - Prefer stable selectors (`data-testid`, roles + accessible names).

Config lives in `.vscode/mcp.json`.

### Deterministic local transforms
- Prefer scripted, deterministic transforms over manual UI operations.
- Typical tooling: Python (e.g., `pandas`, `openpyxl`, `python-pptx`) when justified.
- One-off scripts and artifacts should be namespaced under `runs/<RUN_ID>/`.

### Database queries (DB MCP)
- Optional component when the run requires querying a data warehouse.
- Prefer exporting results and applying deterministic local transforms.

## Repository “memory” model

### Always-on instructions
- `.github/copilot-instructions.md` is the always-loaded operating policy.

### Skills (loaded on demand)
- Skills are repo-based procedural memory.
- Before most tasks: open `.github/skills/README.md` and 1–3 relevant skills.
- Skills should be vendor-agnostic and focus on repeatable tactics.

### Logging
- Per-run artifacts: `runs/<RUN_ID>/...` (often uncommitted; no secrets/URLs/tokens).
- Per-session narrative notes: `notes/agent-runs/` (sanitized; durable).
- Core repo work log: `docs/CORE_REPO_WORK_LOG.md` (append-only; repo changes only).

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
   - Write `notes/agent-runs/<date>_<slug>.md` when meaningful
   - Update `docs/CORE_REPO_WORK_LOG.md` only if the repo changed

## Non-goals
- Building a generic autonomous agent that runs unsupervised.
- Persisting secrets, internal tokens, or privileged deep links.
- Adding “nice-to-have” UX features beyond what the user requested.

## Open Questions / TODOs
- DB MCP: which backends are expected (BigQuery, Snowflake, etc.) and how should their MCP servers be configured?
- Standard run folder layout: should we commit a `runs/_template/` directory or keep it purely documented?
- Dependency packs: do we want optional requirements files (e.g., `requirements-excel.txt`) or keep guidance-only?
