# runs/ (run-local state)

This folder is reserved for **per-run / per-instantiation** state, namespaced by `RUN_ID`.

Conventions:
- `runs/<RUN_ID>/HANDOFF.md` is the rolling state/handoff journal for that instantiation.
- Put run-local artifacts under `runs/<RUN_ID>/` (downloads/tmp/exports/scripts).

Default posture:
- Contents under `runs/<RUN_ID>/` are typically **local/uncommitted** unless explicitly requested.
- Do not store sensitive internal URLs, session links, tokens, or secrets.
