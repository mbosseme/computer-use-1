# Local-First Computer-Use Agent (Copilot Agent Mode + Playwright MCP)

## What this is
A minimal, local-first workspace for running GitHub Copilot “Agent mode” in VS Code to execute multi-step “computer-use” workflows.

- Browser automation via the official Playwright MCP server
- Optional database/toolbox MCPs (e.g., queries/exports)
- Deterministic local transforms (terminal/file ops)

Durable repo-based memory (instructions, skills, and run logs) keeps the system safe and reproducible.

Source of truth for scope/design: [docs/PRODUCT_REQUIREMENTS.md](docs/PRODUCT_REQUIREMENTS.md).

## Prereqs
- Node.js (`node`, `npx`)
  - Optional (Homebrew): `brew install node`
- Python 3 (`python3`)
  - Optional (Homebrew): `brew install python`
- VS Code with GitHub Copilot Agent Mode enabled

## Safety / HITL
- Auth handoff: If login/SSO/MFA/CAPTCHA appears, the agent stops and asks you to take over. You complete auth, then type “Done”.
- Irreversible actions: The agent must ask immediately before clicking **Complete / Submit / Attest / Finish** (or anything irreversible).
- No URL storage: Training URLs are session-only. Do not write them into repo files; use `<TRAINING_URL>` placeholders in skills/logs.

## Setup
- MCP config is committed in [.vscode/mcp.json](.vscode/mcp.json). Open this repo in VS Code.
- Ensure VS Code lists the Playwright MCP server in its MCP/tools UI.

This repo configures Playwright MCP out of the box; additional MCP servers (e.g., database/toolbox MCPs) are optional and should follow the same safety + `RUN_ID` isolation conventions.

If the MCP server fails to start, switch the package in `.vscode/mcp.json` to `@microsoft/mcp-server-playwright` and record what worked in this README.

## Reference docs
- [AGENTS.md](AGENTS.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/Local-First Browser Agent Briefing.md](docs/Local-First%20Browser%20Agent%20Briefing.md)
- [docs/PRODUCT_REQUIREMENTS.md](docs/PRODUCT_REQUIREMENTS.md)
- [docs/PARALLEL_RUNS.md](docs/PARALLEL_RUNS.md)
- [docs/DEPENDENCIES_AND_UTILS.md](docs/DEPENDENCIES_AND_UTILS.md)
- [docs/CORE_REPO_WORK_LOG.md](docs/CORE_REPO_WORK_LOG.md)
- **Skills Index**: [.github/skills/README.md](.github/skills/README.md) (Skills live in `.github/skills/`)

## How repo memory works
- **Automatic**: `.github/copilot-instructions.md` (custom instructions applied every turn).
- **On-demand**: Skills in `.github/skills/` are only used when the agent opens them (start with the Skills Index).
- **Durable logs**: Run notes in `notes/agent-runs/` + core log in `docs/CORE_REPO_WORK_LOG.md`.
- **Session vs repo**: Chat/session memory is not durable; repo memory is.

## Validation prompt
Use Copilot Agent Mode with Playwright MCP tools enabled:

- Navigate to `https://example.com`
- Report the page title
- Take a screenshot

## Multi-run quickstart (parallel agents)
Use this when you want multiple agent instances without collisions.

- Pick a unique `RUN_ID` per run (e.g., `2025-12-29_workday-timesheets`)
- Recommended: create one git worktree per run and open each worktree in a separate VS Code window
- Ensure each run uses isolated execution state (Playwright profile/user data dir + downloads/tmp dirs)
- Store run notes in `notes/agent-runs/` and keep any additional per-run artifacts run-local

Details: [docs/PARALLEL_RUNS.md](docs/PARALLEL_RUNS.md)

## Dependencies
Dependencies are managed in tiers to keep the base reproducible while enabling optional capabilities.

- Tier A (Base): always installed; keep slim
- Tier B (Optional packs): install on demand
- Tier C (Run-local): experiments

Details: [docs/DEPENDENCIES_AND_UTILS.md](docs/DEPENDENCIES_AND_UTILS.md)

## Training run procedure
1. You paste the training URL into chat as session-only: `<TRAINING_URL>`.
2. Agent opens the browser and navigates.
3. If login/SSO/MFA/CAPTCHA appears, agent stops; you complete it; you type “Done”.
4. Agent proceeds through the training:
   - Detects gating (disabled Next/Continue, timers, “video must finish”)
   - Waits for explicit completion signals (button enabled, timer hits 0, completed badge)
   - Scrolls/handles hidden controls and common overlays
5. Before the final completion/submission step (Complete/Submit/Attest/Finish), the agent asks for explicit confirmation.

## After-action
- Write a run log in [notes/agent-runs/](notes/agent-runs/) using [notes/agent-runs/_TEMPLATE.md](notes/agent-runs/_TEMPLATE.md).
- Update or extract skills in [.github/skills/](.github/skills/), especially [.github/skills/training-navigation/SKILL.md](.github/skills/training-navigation/SKILL.md), with new recovery rules or landmarks.
