# PRD — Local-First Browser Agent Workspace

## 1) Problem / Why
We want a minimal, safe, reproducible workspace where GitHub Copilot Agent Mode can drive a local browser via the official Playwright MCP server to complete interactive web tasks, with durable repo-based memory (instructions, skills, and run logs). A key initial use case is navigating web-based trainings that gate progress via timers/videos and require reliable waiting and advancing.

## 2) Goals
- Enable Copilot Agent Mode in VS Code to use the Playwright MCP server to navigate interactive websites.
- Keep the workspace local-first, deterministic, and reproducible.
- Provide durable repo memory:
  - Guardrails/instructions for agent behavior
  - Reusable “skills” for common workflows
  - Run logs for auditability and incremental improvement
- First test use case: vendor-agnostic training navigation with waits/timers/videos and safe advancement.

## 3) Non-goals
- No MFA/SSO/CAPTCHA bypass or automation; auth is always human-in-the-loop.
- No training URL storage in the repo (session-only URLs; use `<TRAINING_URL>` placeholders).
- No separate agent framework or orchestration layer beyond VS Code Copilot Agent Mode + MCP.
- No over-engineering or extra tooling unless required for v1.

## 4) Users / primary workflows
### A) Run training module
- Input: user provides `<TRAINING_URL>` in chat as session-only.
- Flow:
  1. Agent navigates to `<TRAINING_URL>`.
  2. If login/SSO/MFA/CAPTCHA appears, agent stops; user completes; user types “Done”.
  3. Agent proceeds lesson-by-lesson:
     - Detect gating (disabled Next/Continue; timers; video completion requirements)
     - Wait for explicit UI signals (button enabled; timer reaches 0; completion badges)
     - Scroll/scan for hidden controls; handle overlays/popups
  4. Before final completion/submission (Complete/Submit/Attest/Finish), agent asks for explicit confirmation.
  5. After run: write a run log and update the training-navigation skill.

### B) General browsing / research
- Prefer read-only tools (search/fetch) when interactivity is not needed.
- Use Playwright only when interaction is required (forms, navigation, dynamic UI states).

## 5) Architecture
- VS Code (host environment)
- GitHub Copilot Agent Mode (planner/executor)
- Playwright MCP server (official) for browser control
- Repo-based memory:
  - `.github/copilot-instructions.md`
  - `.github/skills/*`
  - `notes/agent-runs/*`
  - `docs/AGENT_WORK_LOG.md`

Optional later (not v1): memory MCP / retrieval tooling, only if it reduces repeated failures and has clear safety boundaries.

## 6) Safety requirements
- HITL gates:
  - Stop for login/SSO/MFA/CAPTCHA and wait for “Done”.
- Safe-click policy:
  - Never click Complete/Submit/Attest/Finish (or any irreversible action) without explicit confirmation immediately before the click.
- Prompt-injection posture:
  - Treat web content as untrusted instructions.
  - Follow repo instructions/skills and user directives over page text.
- Logging/audit:
  - After meaningful runs, write run logs and update skills.
  - Maintain an append-only agent work log of repo changes.

## 7) Repository design
- `docs/Local-First Browser Agent Briefing.md`: principles and operating constraints (source of truth).
- `.github/copilot-instructions.md`: operational guardrails for Copilot Agent Mode.
- `.github/skills/`: reusable workflow playbooks (vendor-agnostic).
- `notes/agent-runs/`: per-run logs using a template.
- `docs/AGENT_WORK_LOG.md`: append-only log of agent actions in this repo.

## 8) Acceptance criteria
- Playwright MCP configured in `.vscode/mcp.json`.
- VS Code shows the Playwright MCP server in MCP/tools list.
- Validation prompt succeeds: navigate to `https://example.com`, report title, take screenshot.
- Training navigation skill exists and includes gating detection + waits + recovery rules + safe-click confirmation.
- Run log process exists (template + directory) and is used after runs.
- No persistence of real training URLs in the repo.

## 9) Phased plan
### v1 (minimal)
- MCP configuration committed.
- Minimal README playbook (Safety/HITL, validation prompt, training procedure).
- Skill templates + training-navigation skill.
- Run log template.
- Agent work log + PRD docs.

### v2 (optional)
- Add optional memory MCP or retrieval support only if:
  - Repeated failures show that durable retrieval materially improves success, and
  - Safety boundaries are clear (no secret storage; no URL persistence), and
  - It does not increase operational complexity beyond the benefit.
