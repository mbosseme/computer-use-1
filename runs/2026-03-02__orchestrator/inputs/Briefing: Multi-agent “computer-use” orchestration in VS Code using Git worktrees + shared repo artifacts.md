# Briefing: Multi-agent “computer-use” orchestration in VS Code using Git worktrees + shared repo artifacts

**Intended audience:** the orchestrator worktree instance (Copilot-driven) that will design and implement the system.
**Where to place:** `runlocal/input/` (or equivalent) for the orchestrator agent to reference during implementation.
**Date context:** March 3, 2026 (America/New_York).

---

## 1) Executive summary

We want a practical, durable way to run multiple “computer-use” agents inside **VS Code** (backed by **GitHub Copilot agentic behaviors**) where each agent operates in its own **Git worktree** but shares a **common repo** containing skills/runbooks, data dictionaries, and scripts. The orchestrator coordinates specialist agents primarily via **shared artifacts** (files) and **Git-native integration** (commits/PRs/apply/merge), with **human-in-the-loop gates** for sensitive actions (email/calendar, auth, irreversible actions).

The research indicates that the most reliable approach in 2025–2026 is a **Git- and file-native hybrid**:

* **Worktrees** provide execution isolation and reduce live collisions.
* **A lightweight control-plane** (queue + run logs + locks) implemented as files in the repo (often on a dedicated branch/worktree) provides coordination without requiring native cross-communication between VS Code windows.
* **Durable context** is best managed through a layered set of repo artifacts (AGENTS.md + scoped instructions + skills + agent profiles), not through ephemeral chat alone.
* **Deterministic hooks/policy gates** are critical for reliability and safety, especially with tool bridges (e.g., MCP/Graph/API access).
* Escalate to a formal multi-agent framework only if/when file+git primitives stop scaling (state machines, retries, observability needs).

This briefing intentionally **does not over-specify** one final design. It captures the constraints, the practical primitives, and implementable patterns so the orchestrator agent can choose the best implementation.

---

## 2) Current usage and constraints (as provided)

### Operating environment

* **MacBook**, multiple **VS Code windows/workspaces** open simultaneously.
* Using **GitHub Copilot** not only for coding, but as a *computer-use/automation agent* doing:

  * drafting emails
  * interacting with APIs (e.g., Microsoft Graph)
  * scheduling meetings
  * research
  * data analysis
  * creating deliverable artifacts (docs, slides, etc.)

### Repo / worktree strategy

* Primary model: **single shared repo** with multiple **Git worktrees**.
* Each worktree corresponds to a “specialist agent workspace,” for example:

  * Baxter client analysis agent
  * Viberon client analysis/presentation agent
  * Email/calendar drafting agent
  * Task prioritization agent
  * Orchestrator agent
* The shared repo contains:

  * shared **skills/runbooks**
  * shared **data dictionaries / data models**
  * shared **scripts/tools**
* Worktrees periodically **sync against main** to pull updated shared assets.
* If a worktree develops a generally useful capability, it can propose changes back to the shared core set via merge into main.

### Reality: some standalone repos/workspaces exist

* Some workspaces/repos are **not** part of the shared repo (legacy, or truly standalone).
* The orchestrator should still be able to interact with/coordinate those environments.

### Non-negotiables (governance and safety)

* Human-in-the-loop for:

  * authentication/MFA/CAPTCHA
  * irreversible actions
  * outbound side effects (e.g., sending email, creating calendar events)
* Avoid sensitive URL/token storage in plain text.
* Batch-and-gate execution (plan → execute → verify → integrate).
* Ask-before-commit and separately ask-before-push (when applicable).
* Emphasis on explicit verification steps and auditability.

---

## 3) What the research recommends (translated into practical primitives)

### 3.1 Worktrees are the core isolation primitive

* One active branch per active worktree is a natural invariant.
* Worktrees reduce live conflicts but do **not** eliminate merge conflicts; they shift conflicts to integration time.
* Parallelism works best when tasks are scoped to non-overlapping paths/modules.

### 3.2 A unified control surface exists, but “cross-window agent-to-agent messaging” is not the baseline

* VS Code has increasingly explicit “agent session” patterns; background agent workflows use worktrees and commit history as audit trail.
* Still: don’t assume native cross-communication between separate VS Code windows. Use file-based coordination.

### 3.3 Durable context must be repo-encoded (layered)

The most effective “memory” is a layered, file-based approach:

* **AGENTS.md**: durable, repo-wide guidance for agents (build steps, rules, conventions).
* **Scoped instructions**: path-based instructions that apply to specific folders (clients/, scripts/, etc.).
* **Skills/runbooks**: reusable procedures with optional resources loaded on-demand.
* **Agent profiles**: explicit specialist personas + tool access boundaries.

### 3.4 Deterministic governance is mandatory (hooks + policy)

* Hooks/scripts can enforce “never do X” policies, run quality gates, and block dangerous commands.
* This matters most when agents have access to tool bridges (Graph/MCP/CLI) that can cause real-world effects.

### 3.5 Treat tool bridges (MCP, Graph, etc.) as security boundaries

* Use explicit trust boundaries and least privilege.
* Prefer “draft artifacts” over direct execution for outbound actions.
* Treat “allow all” / “yolo” modes as break-glass only.

### 3.6 “Framework later” unless/until scaling pain requires it

File+git orchestration should be the default until you hit:

* need for robust retries/backoff/compensation
* richer observability than git history + run logs
* complex multi-party routing beyond straightforward dispatch/handoff
* enterprise checkpointing inside the orchestration engine itself

---

## 4) Target operating model (roles and responsibilities)

### 4.1 Roles (conceptual)

* **Orchestrator agent**

  * Owns intake, normalization, task routing, coordination, and integration gates.
  * Maintains the queue and ensures tasks have proper scope, constraints, and acceptance criteria.
  * Ensures “shared core” changes follow governance and are reviewed.
* **Specialist agents** (worktree-based)

  * Execute tasks within assigned scope (client folder, domain folder, etc.).
  * Produce outputs + evidence; minimize edits outside assigned scope.
* **Maintainer lane** (recommended)

  * Narrow role allowed to modify shared core assets (`/skills`, `/docs`, shared utilities).
  * Reduces churn and prevents accidental broad coupling.
* **Human executor**

  * Performs side-effect actions (send email, create meetings) based on agent-produced drafts.
  * Approves plans, merges, and risky steps.

### 4.2 “Outbound effects” rule of thumb

* Agents can **draft**; humans (or controlled scripts invoked by humans) **execute**.

---

## 5) Practical coordination approach (simplest viable design)

### 5.1 “Shared core set” in main + worktree-specific execution

**Main branch** contains shared assets:

* `skills/` runbooks
* `docs/` architecture + data dictionaries
* `scripts/` deterministic helpers (“tools”)
* `instructions/` (scoped guidance)
* `AGENTS.md` (top-level “agent README”)

Each agent worktree:

* syncs from main regularly
* works on scoped tasks
* contributes back to main when it produces generally useful skills/tools/docs

### 5.2 A file-based task protocol (message passing via artifacts)

Even without native agent-to-agent communication, all agents can coordinate by reading/writing a shared task artifact format.

At minimum, the orchestrator should standardize:

* **Task definition** (immutable after claim)
* **Run state** (mutable; updated during execution)
* **Outputs and handoffs** (human-readable + machine-readable pointers)
* **Evidence** (logs, diffs, references)

This can be implemented as:

* a folder in main (`tasks/`), or
* a dedicated “HQ/control-plane” branch/worktree that contains only operational files (queue, runs, locks)

Research leans toward a dedicated HQ worktree/branch when operational churn is high, but the orchestrator can start simpler and evolve.

---

## 6) Suggested repo layout (illustrative, not mandatory)

### 6.1 Shared repo (default branch: `main`)

```text
/
  AGENTS.md
  docs/
    operating_model.md
    data_dictionaries/
    runbooks/
  skills/
    email_calendar/
    data_analysis/
    research/
    reporting/
  instructions/
    global.instructions.md
    clients.instructions.md
    scripts.instructions.md
  agents/
    orchestrator.agent.md
    email_calendar.agent.md
    analyst.agent.md
    prioritizer.agent.md
    maintainer.agent.md
  scripts/
    quality_gates.sh
    render_report.py
    draft_email.py
    draft_calendar_event.py
  clients/
    baxter/
    viberon/
  tasks/                # optional if not using separate HQ branch
  outputs/
```

### 6.2 Optional HQ/control-plane worktree (branch: `hq/main`)

```text
hq/
  queue/
    ready/
    claimed/
    blocked/
    done/
  runs/
    <task_id>/
      status.json
      plan.md
      summary.md
      handoff.md
      evidence/
  locks/
  memory/
    org/
    clients/
```

---

## 7) Task and run artifacts (schemas the orchestrator can refine)

### 7.1 Task definition (YAML) — intended to be stable after claim

```yaml
version: 1
task_id: "task-YYYYMMDD-###"
created_at: "ISO-8601"
priority: "P0|P1|P2|P3"
specialty: "orchestrator|email|calendar|analysis|code|research"
title: "Short summary"
objective: "What success looks like"
scope_paths:
  - "clients/baxter/**"
inputs:
  - "path/to/context.md"
constraints:
  forbidden_actions:
    - "send_email"
    - "create_calendar_event"
deliverables:
  - "outputs/task-.../result.md"
acceptance_criteria:
  - "Concrete verifiable checks"
human_gates:
  - "plan_approval"
  - "merge_approval"
```

### 7.2 Run state (JSON) — updated frequently

```json
{
  "task_id": "task-20260303-001",
  "state": "running",
  "assigned_agent": "analyst",
  "worktree": "wt-task-20260303-001",
  "branch": "agent/task-20260303-001",
  "last_heartbeat": "2026-03-03T10:02:00-05:00",
  "current_step": "analyzing_data",
  "risks": [],
  "evidence": ["hq/runs/task-20260303-001/evidence/query.log"],
  "next_human_gate": "merge_approval"
}
```

### 7.3 Handoff (Markdown) — human-readable, crisp

* What changed
* Where outputs are
* How verified
* Open questions / recommended next steps
* Risks / caveats (especially for data + interpretation)

---

## 8) Collision avoidance strategy (must be explicit)

Worktrees help, but the orchestrator should enforce **project-level scoping**:

1. **Scope paths are required**

   * Every task must declare `scope_paths`.
   * Agents should be instructed to avoid edits outside scope unless the orchestrator explicitly expands scope.

2. **Locks for hot paths**

   * Introduce lock keys for shared areas (skills, core utilities, data dictionaries, shared schemas).
   * One writer at a time for lock-protected zones.

3. **Shared core treated as “read-mostly”**

   * Most specialists treat shared core as read-only.
   * Route core changes through a maintainer lane or explicit PR gate.

---

## 9) Governance and verification gates (HITL + deterministic checks)

### 9.1 Plan gate

* For complex tasks, require:

  * a written plan artifact
  * explicit human approval before executing modifications

### 9.2 Outbound action gate (email/calendar)

* Agents produce drafts only:

  * `outputs/<task_id>/email_draft.md`
  * `outputs/<task_id>/calendar_event_draft.json`
* Human reviews and triggers a controlled script or manual step.

### 9.3 Integration gate

* Merge/apply changes only after:

  * acceptance criteria satisfied
  * quality gates passed (tests/lints/data checks)
  * human approves merge/apply

### 9.4 Tool boundary enforcement

* Enforce policies via hooks/scripts where possible:

  * block commands / APIs that cause outbound effects
  * require “ask” behavior for sensitive tool usage
  * log evidence of tool runs

---

## 10) Handling standalone repos/workspaces (outside the shared repo)

Goal: orchestrator can still coordinate without needing native VS Code cross-instance messaging.

Suggested patterns the orchestrator can choose from:

### Pattern A: “Task packet” handoff (manual but reliable)

* Orchestrator writes a self-contained task packet:

  * objective
  * steps
  * required inputs
  * acceptance criteria
  * risk flags
* Human (or another agent operating in that standalone repo) executes and returns a result packet.

### Pattern B: Shared “dispatch” directory outside repos (lightweight bridge)

* Use a shared folder (outside git) as a mailbox:

  * `dispatch/outbox/<target>/<task_id>/...`
  * `dispatch/inbox/orchestrator/<task_id>/...`
* The orchestrator drops standardized task packets; the standalone environment returns standardized results.

### Pattern C: Git submodule or “vendor-in” mirror (only if worthwhile)

* For some legacy repos, create a lightweight integration path so they can consume shared `/skills` and conventions without fully merging repos.
* This is higher effort; only do it when repeated coordination friction justifies it.

The orchestrator should implement at least one bridging mechanism so “not in the shared repo” doesn’t mean “not orchestratable.”

---

## 11) Implementation guidance (phased rollout)

### Phase 1: Establish durable context + guardrails

* Create/standardize:

  * `AGENTS.md`
  * instructions (scoped)
  * skills directory structure
  * agent profiles (orchestrator, analyst, email/calendar, maintainer)
  * basic scripts (quality gates, draft generators)
* Decide whether the queue lives in `main/tasks/` initially or in a dedicated `hq/main` branch.

### Phase 2: Stand up a minimal task protocol + one specialist flow

* Implement task YAML + run state JSON + output conventions.
* Pilot with:

  * orchestrator + one client analyst agent (e.g., Baxter)
  * email/calendar drafting agent (draft-only)

### Phase 3: Add collision controls + structured review gates

* Implement `scope_paths` enforcement as a hard convention.
* Add locks for hot paths.
* Standardize merge/apply review.

### Phase 4: Scale to multiple client agents + standalone bridges

* Add Viberon analysis/presentation agent
* Add prioritization agent integration (e.g., converts inbox to tasks)
* Add dispatch mechanism for standalone repos

### Phase 5: Evaluate if/when a framework is needed

* Only if you observe repeated pain that file+git cannot handle well:

  * complex retries and long-running flows
  * routing/coordination complexity
  * need for richer observability

---

## 12) Success criteria (what “good” looks like)

* **Throughput:** multiple agent worktrees can run in parallel without constant conflicts.
* **Reliability:** tasks have clear acceptance criteria and evidence; outputs are reproducible.
* **Safety:** outbound effects are gated; accidental sends/creates don’t occur.
* **Auditability:** every meaningful change is traceable to a task, a plan, evidence, and a review/approval.
* **Maintainability:** shared core assets improve over time without becoming a churn hotspot.

---

## 13) Open decisions for the orchestrator to make (deliberately left flexible)

1. **Queue location**

   * Keep in `main/tasks/` (simpler) vs `hq/main` worktree (cleaner separation once volume grows)

2. **Integration style**

   * PR-first vs apply/merge from background worktrees, depending on how you want review to feel

3. **Lock mechanism**

   * Pure file locks vs git-based locks vs lightweight local lock service

4. **Standalone repo bridging**

   * Task packets only vs shared dispatch folder vs partial repo integration

5. **How strongly to centralize shared-core edits**

   * Any agent can PR to core vs maintainer-only lane

---

## 14) Immediate next actions the orchestrator agent can take

* Draft the initial repo conventions:

  * AGENTS.md
  * initial agent profiles
  * initial skills (email draft, calendar draft, client analysis template)
  * initial task schema
* Decide initial queue implementation:

  * start in `main/tasks/` or create `hq/main` worktree now
* Implement the first end-to-end loop:

  * create task → plan gate → execute in a worker worktree → validate → integrate → handoff

---

**End of briefing.**