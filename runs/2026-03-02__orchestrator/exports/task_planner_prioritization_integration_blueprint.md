# Task Planner Prioritization Design — Integration Blueprint for Orchestrator

Date: 2026-03-02  
Source reviewed: `mbosseme/task-planner` (GitHub)

## 1) What task-planner does especially well

### A. Separation of concerns in prioritization
Task Planner splits priority selection into distinct stages:
- Baseline scoring (pre-weekly-focus / pre-BigRock fit)
- Final scoring with BigRock fit
- Selection phase (MIT picking) that uses scores as the primary signal with light judgment adjustments

This separation creates:
- Stable artifacts (`scored_tasks[]` keyed by task ID)
- Better debuggability and replayability
- Clear handoff boundaries between agents/modules

### B. Strong task identity and continuity
The system uses stable IDs (`entry_id`) end-to-end instead of title matching. This enables safe updates, de-duplication, and downstream scheduling/writeback.

### C. Metadata-first task representation
Task notes carry structured metadata (deadline hard/soft, effort, dependencies, stakeholders, strategic alignment) and drive both scoring and rationale quality.

### D. Explainable output contracts
Prioritization outputs include both ranked tasks and explicit reasoning fields (e.g., work packages, interrupts, defer list), not just a top-N list.

### E. Guardrails for messy reality
- Missing metadata hygiene pass before prioritization
- Optional LLM autofill with provenance + confidence
- Conservative fallback behavior if scoring fails

## 2) Prioritization model worth reusing in orchestrator

## Recommended pipeline (portable)
1. **Normalize inputs** into canonical work items with IDs.
2. **Score pass (artifact)** with weighted components.
3. **Selection pass** that chooses today’s commitments from scored items.
4. **Packaging pass** that groups selected work into coherent execution bundles.
5. **Deferral pass** that explicitly marks non-selected work and reason codes.

### Canonical score shape
```json
{
  "task_id": "...",
  "score_total": 0.0,
  "score_components": {
    "urgency": 0.0,
    "leverage": 0.0,
    "stakeholder": 0.0,
    "effort_efficiency": 0.0,
    "calendar_fit": 0.0,
    "bigrock_fit": 0.0
  },
  "labels": {
    "is_interrupt": false,
    "is_blocked": false
  },
  "assumptions": [],
  "explanation_short": []
}
```

### Canonical selection shape
```json
{
  "day_narrative": "...",
  "work_packages": [
    {"title": "...", "entry_ids": ["..."], "outcome": "..."}
  ],
  "interrupts": [],
  "top_tasks": [{"entry_id": "...", "title": "..."}],
  "if_time_remains": [],
  "defer_not_this_week": [],
  "rationale": "..."
}
```

## 3) How to leverage this inside this orchestrator repo

## Fit with current run context
You already have:
- Cross-source context (Graph + M365 Copilot synthesis)
- A strategic layer from the walk return (fusion, MI-as-GPO-value, org scaling, Palantir-first direction)

What is missing is a **deterministic, reusable prioritization artifact** that all agents can consume.

## Proposed orchestration adaptation

### A. Create a run-local canonical work-item list
Build `orchestrator_work_items.json` from:
- Open action items from Graph (emails/calendar-derived)
- Copilot-derived commitments
- User strategic directives from walk return

Fields to include:
- `entry_id` (stable synthetic ID if no native ID)
- `title`, `source`, `owner`, `due_date`, `notes`
- metadata: `true_deadline`, `estimated_effort`, `dependencies`, `stakeholders`, `strategic_alignment`, `platform_alignment` (e.g., Palantir)

### B. Add explicit scoring phase
Write `orchestrator_task_scores.json` with component scores and assumptions. Keep weights configurable.

### C. Add explicit daily selection phase
Write `orchestrator_priorities_today.json` with:
- Top commitments (3–5)
- Interrupts/expedites
- Deferrals with reasons
- Work packages (clustered by objective/outcome)

### D. Preserve provenance
For each task, include `evidence_refs` to source files/exports so rationale is auditable.

### E. Add confidence and review flags
When metadata is inferred by LLM, stamp:
- source (`llm` / `deterministic` / `user`)
- confidence (`low|medium|high`)

## 4) Priority policy tuned to your latest strategy

Based on your walk-return direction, a practical policy order is:
1. **Fusion near-term wins** (short horizon, visible customer/exec impact)
2. **MI positioned as GPO-value enabler** (not standalone growth narratives)
3. **People/org scaling tasks** needed to execute consistently
4. **Palantir-aligned platform choices** over non-Palantir run/maintain work

Translate this into scoring by:
- Increasing `leverage` and/or dedicated `strategy_fit` points when task supports #1–#4
- Applying a deferral penalty for non-aligned run/maintain tasks unless urgent/blocking

## 5) Minimal implementation sequence in this repo

1. `scripts/build_orchestrator_work_items.py`
   - Inputs: existing run exports
   - Output: canonical work-item JSON

2. `scripts/score_orchestrator_work_items.py`
   - Inputs: canonical work items + strategy policy
   - Output: scoring artifact JSON

3. `scripts/select_orchestrator_top_work.py`
   - Inputs: scoring artifact + current-day constraints
   - Output: daily selection/work-package JSON

4. `runs/<RUN_ID>/exports/executive_briefing_orchestrator.md` update hook
   - Append “Today’s prioritized commitments” from selection artifact

## 6) Why this is the right transfer

This imports the strongest patterns from `task-planner` without forcing Outlook/ToDo coupling:
- Keep what matters: staged scoring, explicit metadata, explainable decisions, stable IDs.
- Skip what does not: app-specific UI/state complexity unless needed.

Result: cross-agent orchestration becomes measurable, debuggable, and less dependent on one-shot prompt quality.

## 7) Suggested next action

Implement the first two scripts only (canonicalization + scoring) and run them against current run exports to generate a first scoring artifact for review before introducing selection automation.
