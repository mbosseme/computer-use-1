# GitHub Copilot Agent Instructions (Local-First Browser Agent)

## Background briefing (source of truth)
- Consult [docs/Local-First Browser Agent Briefing.md](../docs/Local-First%20Browser%20Agent%20Briefing.md) whenever unsure.
- Prefer minimal, safe, reproducible changes.

## Tooling: Playwright MCP (official)
- Use the Playwright MCP server tools for browser actions (navigate, click, fill, screenshot, etc.).
- Keep workflows deterministic: explicit waits, stable selectors, and clear stop conditions.

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

## Skill policy (generalize learnings)
- After a successful workflow (or after resolving a recurring failure), extract/update a skill in `.github/skills/`.
- Skills should be general and reusable across sites; include HITL points and recovery rules.
