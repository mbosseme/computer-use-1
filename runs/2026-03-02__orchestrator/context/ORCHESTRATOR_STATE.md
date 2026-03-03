# Orchestrator Agent State

> **Purpose**: This is the orchestrator agent's persistent working memory — accumulated context, learnings, known agents, and periodic maintenance tasks that should survive across chat sessions. Read this file at session start.
>
> **Update policy**: Append/update as you learn new things. Do not delete entries — mark them superseded if outdated. Keep sections focused and scannable.
>
> **Last updated**: 2026-03-03

---

## 1. Role & Boundaries

**I am the orchestrator.** My job is to:
- Maintain broad organizational awareness about Matt's work and what's happening at Premier
- Help prioritize across the different agents and workstreams  
- Orchestrate which agents/tools to engage for what purpose
- Synthesize context from multiple sources into actionable recommendations

**I do NOT:**
- Reimplement or rebuild other agents (e.g., task-planner)
- Execute day-to-day task work directly — I coordinate and advise
- Maintain strategic priorities or stakeholder lists independently — those live upstream in task-planner and I sync from there

---

## 2. Known Agents & Input Sources

| Agent / Source | Repo / Location | What it provides | Sync method |
|----------------|-----------------|------------------|-------------|
| **Task Planner** | `mbosseme/task-planner` | Tasks queue, strategic priorities (goals + stakeholder hierarchy), daily prioritization output | Periodic GitHub repo pull → `docs/strategic_context.md` |
| **M365 Copilot (Work mode)** | Browser (m365.cloud.microsoft/chat) | Deep organizational context — Teams chats, meeting transcripts, document semantics, decision archaeology | Interactive browser session via Playwright |
| **Microsoft Graph API** | `agent_tools/graph/` | Email (inbox/sent), calendar events, drafts — structured data | Python scripts in this repo |
| **BigQuery MCP** | MCP server | Data queries, analytics context | MCP tool calls |

### Agent interaction notes
- Task-planner is a **separate app Matt controls independently**. He may evolve its design based on orchestrator needs. Treat it as an upstream data source, not something to modify.
- When Matt mentions "the task app" or "task planner," he means `mbosseme/task-planner`.

---

## 3. Periodic Maintenance Tasks

| Task | Frequency | Last done | How |
|------|-----------|-----------|-----|
| Sync strategic context from task-planner | When goals/stakeholders change; check at session start if >7 days stale | 2026-03-03 | `github_repo` search → overwrite `docs/strategic_context.md` |
| Review HANDOFF.md for continuity | Every session start | 2026-03-03 | Read `runs/2026-03-02__orchestrator/HANDOFF.md` |
| Check for new exports/briefings | Every session start | 2026-03-03 | `list_dir` on `runs/2026-03-02__orchestrator/exports/` |

---

## 4. Accumulated Learnings & Preferences

### Matt's working style
- Thinks strategically during walks; returns with crystallized priorities and decisions
- Prefers orchestration over execution — wants help deciding *what* to focus on, not just doing tasks
- Values broad organizational awareness — wants the orchestrator to know what's going on at Premier holistically
- Doesn't want context pollution across agents/worktrees — each agent should maintain its own relevant context

### Organizational context
- **Premier** is the company (Premier, Inc. — healthcare GPO/technology)
- **ABI** = Analytics & Business Intelligence — Matt's org
- **Market Insights (MI)** = Key product, revenue target $11M FY26
- **Fusion** = Near-term strategic initiative (early wins prioritized)
- **Palantir** = Technology direction confirmed, but roadmap ambiguity exists beyond two active use cases
- Key near-term pillars (from 2026-03-02 walk): early fusion wins, MI-as-GPO-value synergy, people/org scaling

### Technical preferences
- Prefers deterministic local transforms (Python/pandas) over UI manipulation
- Uses VS Code with Copilot Agent Mode as primary development environment
- Multiple worktrees for parallel agent work
- Git discipline: ask before commit, ask separately before push

---

## 5. Active Workstreams (high-level snapshot)

> Update this section as workstreams emerge, shift, or close.

| Workstream | Status | Key context |
|------------|--------|-------------|
| Orchestrator bootstrap | Complete | Playwright isolated, Graph context extracted, M365 deep scan done, walk return ingested |
| Strategic context sync | Active | `docs/strategic_context.md` synced from task-planner; sync policy established |
| Daily prioritization flow | Not started | Orchestrator's role is to advise on priorities using task-planner output + own org awareness |

---

## 6. Worktree Registry (last scanned: 2026-03-03)

26 worktrees across 8 categories:

| Category | Count | Key worktrees |
|----------|-------|---------------|
| client | 6 | baxter-market-insights, solventum-market-insights, ge-market-insights, b-braun-pdf-synthesis, mckinsey, fda-cdrh-engagement |
| strategy | 3 | orchestrator (this), portfolio-expansion, premier-strategy-development |
| people | 2 | employee-performance-management, accelerating_technology_delivery_presentation |
| operations | 3 | timesheets, o365-outlook-general, onenote-org |
| personal | 8 | disney-planning, personal-finance, personal-shopping, etc. |
| core | 3 | playwright-general-lessons, doc-synthesis-cli, validate_insight_flash_reports |
| other | 1 | nc-preschool-director-search |

Recently active (last 3 days):
- **orchestrator** — this instance
- **o365-outlook-general** — email/calendar operational agent
- **portfolio-expansion** — strategy work on MI portfolio
- **onenote-org** — OneNote organization
- **premier-strategy-development** — broader strategy
- **timesheets** — timesheet automation
- **baxter-market-insights** — Baxter client analysis (last: Caroline Gullion briefing)

> Re-scan: `python3 runs/2026-03-02__orchestrator/scripts/scan_worktrees.py`

---

## 7. Key File Map (quick reference)

| File | Purpose |
|------|---------|
| `docs/strategic_context.md` | FY26 goals + 8-tier stakeholder hierarchy (synced from task-planner) |
| `runs/2026-03-02__orchestrator/HANDOFF.md` | Chronological session journal |
| `runs/2026-03-02__orchestrator/exports/` | Accumulated briefings, Graph context, walk notes |
| `runs/2026-03-02__orchestrator/context/ORCHESTRATOR_STATE.md` | This file — persistent agent memory |
| `runs/2026-03-02__orchestrator/context/OPERATING_PROTOCOL.md` | Daily loop, decision framework, delegation format |
| `runs/2026-03-02__orchestrator/scripts/pull_my_day_tasks.py` | Pull My Day tasks from Microsoft To Do via Graph |
| `runs/2026-03-02__orchestrator/scripts/scan_worktrees.py` | Scan and categorize all git worktrees |
| `.github/prompts/orchestrator.prompt.md` | Bootstrap prompt for new sessions |

---
