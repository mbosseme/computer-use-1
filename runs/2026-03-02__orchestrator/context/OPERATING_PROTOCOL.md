# Orchestrator Operating Protocol

> **Purpose**: Defines how the orchestrator agent operates day-to-day — the daily intake loop, decision framework, delegation convention, and context enrichment workflow.
>
> **Last updated**: 2026-03-03

---

## 1. Daily Intake Loop

When Matt starts a session and wants orchestration help, the flow is:

```
1. SCAN     → Pull My Day tasks from To Do (Graph API)
2. SCAN     → Scan worktree registry (git worktree list)
3. ENRICH   → For the top candidate task, gather context:
               a. Graph email search for related threads
               b. Graph calendar for related meetings
               c. M365 Copilot (via Playwright) for broader org awareness
4. ASSESS   → Decide: Do it myself? Delegate to existing worktree? Propose new worktree?
5. ACT/HAND → Either execute directly or produce a delegation brief
6. LOG      → Update ORCHESTRATOR_STATE.md + append to HANDOFF.md
```

### Scripts available:
- `python3 runs/2026-03-02__orchestrator/scripts/pull_my_day_tasks.py` — Pull tasks from To Do
- `python3 runs/2026-03-02__orchestrator/scripts/scan_worktrees.py` — Scan worktree registry

---

## 2. Decision Framework: Do vs Delegate

**Do it myself when:**
- The task is quick (< 30 min) and doesn't require deep domain context from a specialist worktree
- The task is cross-cutting (touches multiple domains, needs synthesis)
- The task is about email drafting, calendar review, or general research
- No existing worktree matches the domain

**Delegate when:**
- An existing worktree has accumulated context for this client/project
- The task requires sustained focus in a specific domain (client analysis, data work)
- The task will produce artifacts that belong in a specific project scope
- The orchestrator would need to rebuild context that already exists elsewhere

**Propose a new worktree when:**
- The task is substantial enough to justify a dedicated workspace (multi-day effort)
- It doesn't fit any existing worktree's domain
- It will produce reusable outputs that should be tracked in their own branch

---

## 3. Delegation Protocol

When delegating, the orchestrator produces a **task brief** — a markdown file that Matt carries to the target worktree's VS Code window.

### Task brief format:

```markdown
# Task Brief: [Short title]

**From**: Orchestrator (run/2026-03-02__orchestrator)
**To**: [Target worktree slug] ([target path])
**Date**: [YYYY-MM-DD]
**Priority**: [P0-P3]

## Objective
[What success looks like — 1-3 sentences]

## Context
[Key background the specialist needs. Include:]
- Relevant email threads or meeting notes (summarized or linked)
- Strategic alignment (Goal X)
- Stakeholder impact (Tier X: Name)
- Deadline constraints

## Scope
[What files/areas the specialist should work in]

## Deliverables
- [ ] [Concrete output 1]
- [ ] [Concrete output 2]

## Constraints
- [Any safety gates, forbidden actions, review requirements]

## Acceptance Criteria
- [How we know this is done]

## Orchestrator Notes
[Anything the orchestrator has already gathered or tried]
```

### Where task briefs go:
- Save in the **target worktree's** `runs/<RUN_ID>/inputs/` directory
- Also save a copy in the orchestrator's `runs/2026-03-02__orchestrator/exports/task_briefs/` for tracking

### How Matt uses a task brief:
1. Orchestrator says: "I've written a task brief for [worktree]. Open that VS Code window and paste this into chat: [instructions]"
2. Matt opens the target window, uses the task brief as context for the specialist agent
3. When the specialist completes, Matt returns to orchestrator to report status

---

## 4. Context Enrichment Patterns

### 4a. Email context (Graph API)
```python
# Search for emails related to a task/person/topic
from agent_tools.graph.mail_search import search_mail
results = search_mail(client, query="subject:Baxter OR from:baxter.com", top=20)
```
Or use the Graph client directly:
```python
client.get("me/messages", params={
    "$search": '"Baxter market insights"',
    "$select": "subject,from,receivedDateTime,bodyPreview",
    "$top": 10
})
```

### 4b. Calendar context (Graph API)
```python
# Check upcoming meetings related to a topic
from datetime import datetime, timedelta
now = datetime.now().isoformat()
week = (datetime.now() + timedelta(days=7)).isoformat()
client.calendar_view(start_iso=now, end_iso=week)
```

### 4c. M365 Copilot secondary research (Playwright MCP)
Use the `m365-copilot-secondary-research` skill for deep org awareness:
- Navigate to M365 Copilot Work mode
- Set model to GPT-5.2 Think
- Ask targeted questions about recent decisions, commitments, or context
- Extract and save to orchestrator exports

---

## 5. Worktree Registry Categories

| Category | What it covers | Examples |
|----------|---------------|----------|
| client | Customer-specific analysis, presentations, engagement | baxter, solventum, ge, b-braun, mckinsey |
| strategy | Organizational strategy, portfolio decisions | premier-strategy, portfolio-expansion, orchestrator |
| people | Team management, HR, performance | employee-performance |
| operations | Recurring operational tasks | timesheets, outlook-general, onenote-org |
| personal | Non-work tasks | disney-planning, personal-finance |
| core | Shared infrastructure, skill development | playwright improvements, doc-synthesis |
| research | Deep research projects | (as needed) |

---

## 6. Safety Reminders (always apply)

- **Never send emails or create calendar events** — only draft them
- **Stop for auth** (SSO/MFA/CAPTCHA) and wait for Matt
- **Stop before irreversible actions** (Submit/Approve/Send) and ask
- **Don't modify files outside the orchestrator's run directory** unless explicitly scoped
- **Delegate** rather than stretch into domains where an existing worktree has better context

---
