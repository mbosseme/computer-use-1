# GitHub Copilot Agent Instructions (Local-First Browser Agent)

## Background briefing (source of truth)
- Consult [docs/Local-First Browser Agent Briefing.md](../docs/Local-First%20Browser%20Agent%20Briefing.md) whenever unsure.
- Consult [docs/PRD.md](../docs/PRD.md) to stay aligned to scope and non-goals.
- Prefer minimal, safe, reproducible changes.

## How Copilot uses Skills in practice
- Skills are **repo-based memory**, but Copilot does **not** automatically ingest skill files every turn.
- The Playwright MCP server does not “read” skills — **Copilot reads skills** when the agent opens/references the files.
- Therefore: at the start of each task/session, the agent must explicitly open the Skills Index and 1–3 relevant skills to load them into context.

## Memory Warmup (Start of EVERY Task)
1. **Classify the task domain** (pick one): training, general browser automation, research, terminal automation, or a known app/workflow.
2. **Read Context**: Read `docs/PRD.md` (scope + guardrails).
3. **Read Skills Index**: Read `.github/skills/README.md`.
4. **Load Skills (max 1–3)**: Open the most relevant skill(s). If unsure and it’s a web UI task, default to `browser-automation-core/SKILL.md`.
5. **Execute**: Proceed using the loaded patterns.

## Tooling: Playwright MCP (official)
- Use the Playwright MCP server tools for browser actions (navigate, click, fill, screenshot, etc.).
- Keep workflows deterministic: explicit waits, stable selectors, and clear stop conditions.

## General-Purpose Stance
- This agent is for **any** browser or terminal task, not just training.
- Examples:
  - Timesheet entry / form filling.
  - Approving/reviewing items.
  - Online research / data extraction.
  - Terminal-based automation.
- **Safety First**: Always apply HITL for auth and irreversible actions (Submit/Approve/Pay).

## Selector strategy (stability first)
- Prefer `data-testid` / `data-test` attributes when available.
- Else prefer role-based selectors with accessible names (e.g., `getByRole('button', { name: 'Next' })`).
- Avoid brittle CSS selectors, XPath, and selectors tied to layout/visual order.

## Waiting strategy (no flaky sleeps)
- Prefer explicit waits on elements becoming **attached/visible/enabled** or on clear UI state changes.
- Avoid hard sleeps; use them only when the UI offers no reliable signal, and only as **bounded** waits.

## Human-in-the-loop (HITL) policy
- AUTH: Stop and ask the user to take over for SSO/MFA/CAPTCHA/login. Resume only after the user says “Done”.
- SAFE-CLICK POLICY (irreversible actions): Never click **Complete / Submit / Attest / Finish** (or any irreversible UI action) without asking for explicit confirmation immediately before the click.
- Ambiguity: If it’s unclear whether an action is irreversible, ask before acting.

## No URL storage (session-only)
- If the user provides a training URL, treat it as **session-only**; do **not** write it to any repo file.
- Use placeholders like `<TRAINING_URL>` in skills/logs.

## Logging policy (durable repo memory)
- After each meaningful run, write a run note in `notes/agent-runs/` using the template.
- Keep notes vendor-agnostic; avoid storing secrets, URLs, or personal data.
- Maintain `docs/AGENT_WORK_LOG.md` as append-only after meaningful repo work (commands run, files changed, decisions, next steps).

## When Stuck (Escalation Ladder)
1. **Consult Skills**: Re-read the "Recovery rules" in the relevant skill file.
2. **Bounded Recovery**: Try 2–3 specific tactics (e.g., dismiss overlay, scroll container, reload with warning).
3. **Ask User**: If recovery fails, stop and ask for help.
4. **Learning loop**: If the user provides a workaround, **immediately**:
  - Update the most relevant existing skill (vendor-agnostic wording).
  - Write a run note (`notes/agent-runs/`) linking to the skill update.
  - Optionally append a short entry to `docs/AGENT_WORK_LOG.md` **only if repo work occurred**.

## Output discipline (general-purpose)
- For “extract values and report back” tasks, include how the result was verified (e.g., on-screen KPI label, tooltip, exported data, audit/log view).

## Skill Update Rule
- **Generalize**: If a workaround is reusable, add it to the skill under "Recovery rules" or "Detection signal".
- **No new skill folders unless asked**: Do not create new skill folders unless Matt explicitly asks. If a new recurring workflow emerges, propose a new skill name/path and wait for approval.

## Commit policy (major milestones)
- Do **not** propose commits for log-only changes (e.g., `docs/AGENT_WORK_LOG.md`) or minor doc tweaks.
- Propose a commit only when at least one is true:
	- A new capability is added (e.g., MCP validated + first training workflow + skill enhancements).
	- A structural repo change occurs (new folders/files that materially change the system).
	- A bug fix affects core functionality (MCP config changes, workflow logic changes).
- Target cadence: commit at major milestones (roughly every few hours or after a meaningful end-to-end success).
