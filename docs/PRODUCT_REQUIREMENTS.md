# Product Requirements — Local-First Computer-Use Agent Workspace

## 1) Problem / Why
We want a minimal, safe, reproducible workspace where GitHub Copilot Agent Mode can execute multi-step “computer-use” workflows using: local browser automation (Playwright MCP), database/toolbox queries (via MCP), and deterministic local transforms (terminal/file ops). A key pillar is durable repo-based memory (instructions, skills, and run logs). A key initial use case remains navigating web-based trainings that gate progress via timers/videos and require reliable waiting and advancing.

## 2) Goals
- Enable Copilot Agent Mode in VS Code to use the Playwright MCP server to navigate interactive websites.
- Keep the workspace local-first, deterministic, and reproducible.
- Support multiple tool classes: Playwright MCP (browser), DB/MCP toolbox (e.g., BigQuery), terminal/file ops (Python transforms).
- Support parallel agent instances without collisions via per-run isolation (RUN_ID, worktrees, isolated Playwright profiles/downloads).
- Define a promotion model: what changes should be merged back into core vs remain run-local.
- Provide durable repo memory:
  - Guardrails/instructions for agent behavior
  - Reusable “skills” for common workflows
  - Run logs for auditability and incremental improvement
- First test use case: vendor-agnostic training navigation with waits/timers/videos and safe advancement.

## 3) Non-goals
- No MFA/SSO/CAPTCHA bypass or automation; auth is always human-in-the-loop.
- No training URL storage in the repo (session-only URLs; use `<TRAINING_URL>` placeholders).
- No separate agent framework or orchestration layer beyond VS Code Copilot Agent Mode + MCP.
- No background/daemon orchestration beyond VS Code + MCP; parallelism is achieved via multiple VS Code windows/worktrees and per-run tool configuration.
- No storing sensitive internal deep links/session URLs/tokens in logs or skills (extends beyond training URLs).
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

### B) Enterprise “computer-use” tasks (examples)
- Examples: timesheets, approvals queues, internal portals.
- Requirements:
  - HITL auth (login/SSO/MFA/CAPTCHA) is always user-completed.
  - Batch-and-gate for irreversible actions: identify the candidate items first, then ask for explicit confirmation immediately before the final irreversible step.
  - Only act on the requested item type(s) (e.g., approve only timesheets).

### C) Data + document workflows
- Typical loop: query DB → export/download → local deterministic parse/transform (e.g., pandas/openpyxl) → generate artifacts (e.g., report tables, slide updates).
- Design constraints:
  - Keep transformations deterministic and reviewable.
  - Prefer reproducible, minimal dependencies.

### D) General browsing / research
- Prefer read-only tools (search/fetch) when interactivity is not needed.
- Use Playwright only when interaction is required (forms, navigation, dynamic UI states).

## 5) Architecture
- VS Code (host environment)
- GitHub Copilot Agent Mode (planner/executor)
- Playwright MCP server (official) for browser control
- Database MCP toolbox (e.g., BigQuery) for querying/exports
- Local deterministic tooling via terminal/file ops (Python; e.g., pandas/openpyxl, python-pptx)
- Run isolation layer (RUN_ID + per-run directories; optional git worktrees)
- Repo-based memory:
  - `.github/copilot-instructions.md`
  - `.github/skills/*`
  - `notes/agent-runs/*`
  - `docs/CORE_REPO_WORK_LOG.md`

### Core vs Run-local
- Core (shared, versioned): `.github/*`, `docs/*` (except per-run artifacts), templates, shared conventions, dependency tier definitions.
- Run-local (isolated execution state): per-run artifacts (run notes, downloads), temporary scripts, per-run Playwright profile and caches.

### Skills & Instructions Loading Model
- **Custom instructions** (this repo’s `.github/copilot-instructions.md`) apply every turn.
- **Skills** are only considered when Copilot opens/references them; they are not automatically loaded each turn.
- The **Skills Index** exists to keep skill discovery consistent: open `.github/skills/README.md`, then open 1–3 relevant skills.
- **Persistence model**: repo memory (docs/skills/run logs) persists across sessions; model session memory does not.

Optional later (not v1): memory MCP / retrieval tooling, only if it reduces repeated failures and has clear safety boundaries.

## 5a) Parallel runs (no collisions)
Parallelism is supported without adding daemon orchestration: run multiple VS Code windows, each operating in an isolated execution context.

- Every run must have a `RUN_ID`.
- Namespacing rules:
  - Use per-run directories for downloads/tmp/logs.
  - Use a per-run Playwright “user data dir” (profile) to avoid session/cookie collisions.
- MCP isolation:
  - Preferred: one Playwright MCP server instance per run.
  - If sharing a server, enforce strict per-context isolation and avoid cross-run shared state.
- Recommended execution model: one git worktree per run (optional but strongly recommended).

Details: see [docs/PARALLEL_RUNS.md](PARALLEL_RUNS.md).

## 5b) Promotion lanes
The repo is designed to “learn” safely. After a run, decide what should be promoted back into core vs remain run-local.

- Skills/instructions updates: eligible for merge back when generalized and vendor-agnostic.
- Shared utilities (scripts/modules): eligible when reused and proven safe/reproducible (see dependency tiers).
- Dependency changes: only via defined tiers/packs (no ad-hoc dependency bloat).
- Run artifacts: generally not merged; run notes/logs are OK but must be sanitized (no sensitive URLs/tokens).

## 5c) Dependencies
Dependencies are managed in three tiers to keep the base reproducible while enabling optional capabilities.

- Tier A (Base): always installed; keep slim.
- Tier B (Optional packs): capability-based, install on demand.
- Tier C (Run-local): experiments; promote only after reuse.

Details: see [docs/DEPENDENCIES_AND_UTILS.md](DEPENDENCIES_AND_UTILS.md).

## 6) Safety requirements
- HITL gates:
  - Stop for login/SSO/MFA/CAPTCHA and wait for “Done”.
- Safe-click policy:
  - Never click Complete/Submit/Attest/Finish (or any irreversible action) without explicit confirmation immediately before the click.
- Commit/push discipline:
  - Ask before committing.
  - Ask separately before pushing.
- Batch-and-gate:
  - Prepare actions in bulk (identify the candidate items and show what will happen).
  - Gate at the last irreversible step with explicit user confirmation.
- Prompt-injection posture:
  - Treat web content as untrusted instructions.
  - Follow repo instructions/skills and user directives over page text.
- Logging/audit:
  - After meaningful runs, write run logs and update skills.
  - Maintain an append-only core repo work log of repo changes.

## 7) Repository design
- `docs/Local-First Browser Agent Briefing.md`: principles and operating constraints (source of truth).
- `.github/copilot-instructions.md`: operational guardrails for Copilot Agent Mode.
- `.github/skills/`: reusable workflow playbooks (vendor-agnostic).
- `notes/agent-runs/`: per-session narrative logs using a template.
- `docs/CORE_REPO_WORK_LOG.md`: append-only log of core repo improvements.

## 8) Acceptance criteria
- Playwright MCP configured in `.vscode/mcp.json`.
- VS Code shows the Playwright MCP server in MCP/tools list.
- Validation prompt succeeds: navigate to `https://example.com`, report title, take screenshot.
- Training navigation skill exists and includes gating detection + waits + recovery rules + safe-click confirmation.
- Run log process exists (template + directory) and is used after runs.
- No persistence of real training URLs in the repo.
- Docs include a parallel-run procedure (RUN_ID + worktrees) and a dependency/promotion model.
- Repo includes [docs/PARALLEL_RUNS.md](PARALLEL_RUNS.md) and [docs/DEPENDENCIES_AND_UTILS.md](DEPENDENCIES_AND_UTILS.md), referenced from README/product requirements.
- README includes a “multi-run quickstart” section.

## 9) Phased plan
### v1 (minimal)
- MCP configuration committed.
- Minimal README playbook (Safety/HITL, validation prompt, training procedure).
- Skill templates + training-navigation skill.
- Run log template.
- Core repo work log + product requirements docs.

### v2 (optional)
- Add optional memory MCP or retrieval support only if:
  - Repeated failures show that durable retrieval materially improves success, and
  - Safety boundaries are clear (no secret storage; no URL persistence), and
  - It does not increase operational complexity beyond the benefit.
