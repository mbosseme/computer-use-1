# Parallel Runs (No Collisions)

## Core idea
- **Core repo knowledge is shared**: instructions, skills, templates, and reference docs.
- **Execution state is per-run**: browser sessions, downloads, temp artifacts, and any run-local scratch files.

This repo supports parallelism without a daemon/orchestrator: run multiple VS Code windows, each operating in an isolated run context.

## RUN_ID
Every run should have a unique `RUN_ID`.

Recommended format:
- `YYYY-MM-DD_<short-workflow>`
- Examples:
  - `2025-12-29_training-run`
  - `2025-12-29_timesheet-approvals`

Use `RUN_ID` to namespace anything that could collide (downloads, profiles, logs, temp files).

## Worktrees (recommended)
Worktrees are the simplest way to isolate parallel runs while keeping the shared repo history clean.

Recommended posture:
- One git worktree per run
- One VS Code window per worktree
- Keep run-local artifacts out of core paths (or in a run-local folder)

(Keep this doc conceptual; use your preferred worktree workflow.)

## Collision avoidance checklist
**Browser state**
- Use a per-run Playwright **user data dir** (profile) to avoid session/cookie collisions.
- Use a per-run **downloads** directory.

**Temp / outputs**
- Use per-run temp directories for scraped data, exports, and intermediate files.
- Prefer deterministic transforms that read inputs and produce explicit outputs.

**MCP isolation**
- Preferred: **one Playwright MCP server per run**.
- If you must share a server: enforce strict per-context isolation and avoid cross-run shared state.

## Where artifacts should live
- **Run notes (durable but sanitized)**: `notes/agent-runs/`
- **Optional run-local folder**: `runs/<RUN_ID>/` (keep this run-local; do not promote by default)

Never store sensitive internal deep links/session URLs/tokens in run notes.

## Promotion workflow (selective merge)
Parallel runs often generate useful improvements; promote them deliberately.

- Prefer small, focused PRs.
- Promote only what’s generalizable:
  - instruction updates
  - skill updates
  - reusable utilities
  - dependency pack definitions (when justified)
- Keep run-local artifacts run-local.
