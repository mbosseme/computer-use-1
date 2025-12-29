# notes/agent-runs/ (per-session run notes)

This folder holds **per-session narrative logs** that you intentionally want to keep **versioned** (auditable summaries of what happened).

Conventions:
- Filenames: `YYYY-MM-DD_<slug>.md`
- Keep entries vendor-agnostic and high-signal (goal, key steps, HITL points, verification signals, and lessons learned).
- Prefer one file per session to avoid merge conflicts.

Sanitization rules:
- Do not store sensitive internal deep links/session URLs/tokens/secrets.
- Use placeholders like `<TASK_URL>` / `<TRAINING_URL>` and describe destinations generically.

How this differs from other logs:
- `notes/agent-runs/`: per-session narratives (durable, sanitized)
- `runs/<RUN_ID>/HANDOFF.md`: rolling handoff journal for the current instantiation (run-local; default continuity)
- `docs/CORE_REPO_WORK_LOG.md`: core repo improvements only (append-only index)

Git posture:
- By default, new `notes/agent-runs/*.md` files may be ignored by `.gitignore` to keep the main branch clean.
- If you want to version a specific session log anyway, add it intentionally (e.g., `git add -f notes/agent-runs/YYYY-MM-DD_<slug>.md`).
