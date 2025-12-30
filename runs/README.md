# runs/ (run-local state)

This folder is reserved for **per-run / per-instantiation** state, namespaced by `RUN_ID`.

Conventions:
- `runs/<RUN_ID>/HANDOFF.md` is the rolling state/handoff journal for that instantiation.
- Put run-local artifacts under `runs/<RUN_ID>/` (downloads/tmp/exports/scripts).

Standard structure (created/maintained by the bootstrap prompt):
- `runs/<RUN_ID>/HANDOFF.md` (append-only continuity journal)
- `runs/<RUN_ID>/briefing/` (briefing materials specific to this run)
- `runs/<RUN_ID>/inputs/` (raw inputs specific to this run)
- `runs/<RUN_ID>/exports/` (exports produced during the run)
- `runs/<RUN_ID>/scripts/` (one-off scripts used only for this run)
- `runs/<RUN_ID>/tmp/` (scratch)
- `runs/<RUN_ID>/downloads/` (downloads for this run)
- `runs/<RUN_ID>/playwright-profile/` (per-run Playwright user-data-dir)
- `runs/<RUN_ID>/playwright-output/` (per-run Playwright outputs)

Default posture:
- Contents under `runs/<RUN_ID>/` are typically **local/uncommitted** unless explicitly requested.
- Do not store sensitive internal URLs, session links, tokens, or secrets.
