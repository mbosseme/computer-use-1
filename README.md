# Local-First Browser Agent (Copilot Agent Mode + Playwright MCP)

## What this is
A minimal, local-first workspace for running GitHub Copilot “Agent mode” in VS Code to drive a local browser via the official Playwright MCP server, with durable repo-based memory (instructions, skills, and run logs).

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

If the MCP server fails to start, switch the package in `.vscode/mcp.json` to `@microsoft/mcp-server-playwright` and record what worked in this README.

## Reference docs
- [docs/Local-First Browser Agent Briefing.md](docs/Local-First%20Browser%20Agent%20Briefing.md)
- [docs/PRD.md](docs/PRD.md)
- [docs/AGENT_WORK_LOG.md](docs/AGENT_WORK_LOG.md)
- **Skills Index**: [.github/skills/README.md](.github/skills/README.md) (Skills live in `.github/skills/`)

## Validation prompt
Use Copilot Agent Mode with Playwright MCP tools enabled:

- Navigate to `https://example.com`
- Report the page title
- Take a screenshot

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
