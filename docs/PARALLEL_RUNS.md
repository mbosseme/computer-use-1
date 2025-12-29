# Parallel Runs (No Collisions)

This doc is the repo’s single “how-to” for running multiple agent instances in parallel without collisions, while keeping `main` clean.

## Intended usage pattern (Launcher + Worktrees)
Do not open multiple VS Code windows on the same working directory.

Recommended posture:
- **1 launcher window** opened on `main`: creates branches + git worktrees.
- **1 VS Code window per run/worktree**: does the actual run work.
- Runs can last multiple days; keep the run branch as the run’s long-lived journal.

## Terminology (standard)
**RUN_ID**
- Format: `YYYY-MM-DD__short-slug`
- Examples:
  - `2025-12-29__training-phi`
  - `2025-12-29__timesheets`

**Branch naming**
- Run branch: `run/<RUN_ID>`
- Optional promotion branch: `core/<RUN_ID>` (used to merge core-only changes back to `main`)

**Worktree folder naming**
- Recommended path: `../wt-<RUN_ID>`

## Quick parallel run creation (launcher window)
From the launcher window opened on `main`:

```bash
git switch main
git pull --ff-only

RUN_ID="YYYY-MM-DD__short-slug"

# Create a new run branch + worktree rooted at main
git worktree add -b "run/${RUN_ID}" "../wt-${RUN_ID}" main

# Open the worktree in its own VS Code window
code -n "../wt-${RUN_ID}"
```

Inside the new worktree window:
- Follow the bootstrap prompt in `.github/prompts/bootstrap_computer_use_agent.prompt.md`.
- Use `runs/<RUN_ID>/HANDOFF.md` as default run continuity across chat resets.

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

## Core vs run-local (promotion lanes)
### Core paths allowlist (eligible to merge to `main`)
This repo’s core/shared paths are:
- `AGENTS.md`
- `README.md`
- `.github/**`
- `docs/**`
- `.vscode/**`
- `requirements.txt`

If you add a reusable utilities directory later, treat `tools/**` as core.

### Run-local quarantine paths (do not merge to `main`)
- `runs/<RUN_ID>/**` (default location for run continuity + artifacts)
- Other ephemeral state (repo defaults): `.playwright-mcp/`, `.venv/`, `downloads/` (see `.gitignore`)

## Versioning run artifacts safely (without polluting main)
Runs may produce one-off scripts/notes that are useful for that run and worth keeping on the run branch.

Recommended posture:
- Keep run artifacts under `runs/<RUN_ID>/`.
- It’s OK to commit small, reviewable text artifacts (e.g., `runs/<RUN_ID>/scripts/*.py`, `runs/<RUN_ID>/HANDOFF.md`) to the **run branch**.
- Do **not** merge run artifacts to `main`; use the promotion workflow below.
- Avoid binaries and never store secrets/session URLs/tokens (use placeholders like `<TRAINING_URL>`).

Note: the repo’s `.gitignore` may ignore `runs/<RUN_ID>/` by default to keep `main` clean. If you intentionally want to version a specific run artifact on the run branch, add it explicitly (e.g., `git add -f runs/<RUN_ID>/scripts/foo.py`).

## Promotion to main (core-only)
The goal is: keep `run/<RUN_ID>` as the run journal (may include run artifacts), while merging only core improvements back to `main`.

Recommendation:
- When making core improvements during a run, keep them in separate commits with a `core:` prefix in the commit message.

### Option A: cherry-pick core commits onto `core/<RUN_ID>`
1. Create promotion branch from `main`:

```bash
git switch main
git pull --ff-only
git switch -c "core/${RUN_ID}"
```

2. Cherry-pick only the `core:` commits from `run/<RUN_ID>`.
3. Merge `core/<RUN_ID>` into `main`.

### Option B: path-limited promotion (diff only core paths)
If you prefer not to cherry-pick, generate a patch that only includes changes under core paths and apply it on a `core/<RUN_ID>` branch.

This is intentionally stricter: even if the run branch contains run artifacts, the promotion patch only includes allowlisted paths.
