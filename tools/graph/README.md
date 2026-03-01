# Graph Utilities (Reusable)

Reusable CLI scripts for Graph-based mailbox and scheduling workflows across worktrees.

## Prerequisites
- Repo `.env` configured for Graph auth/scopes.
- Python env active.

## 1) Find mutual slots
`find_mutual_slots.py` computes overlap via `POST /me/calendar/getSchedule`.

Use this for **multi-attendee overlap lookups** across runs/worktrees. For auth/config diagnostics, use `python -m agent_tools.graph.validate`.

Example:

```bash
/Users/matt_bossemeyer/Projects/wt-2026-01-20__o365-outlook-general/.venv/bin/python tools/graph/find_mutual_slots.py \
  --emails matt_bossemeyer@premierinc.com edward_haggett@premierinc.com cindy_koulentianos@premierinc.com \
  --days 7 \
  --duration 30 \
  --day-start 08:30 \
  --day-end 16:30 \
  --allow-tentative
```

Notes:
- Availability codes treat `tentative` as bookable only with `--allow-tentative`.
- Results are printed in local planner timezone from `.env` (normalized to IANA).

## 2) Draft structured email
`draft_structured_email.py` creates a mailbox draft from a JSON template.

Use this for **repeatable multi-section request emails**. For simple markdown-driven drafts/replies, use `python -m agent_tools.graph.create_draft_from_md`.

Example:

```bash
/Users/matt_bossemeyer/Projects/wt-2026-01-20__o365-outlook-general/.venv/bin/python tools/graph/draft_structured_email.py \
  --input runs/<RUN_ID>/inputs/email_spec.json
```

Optional fallback substitution file:

```bash
/Users/matt_bossemeyer/Projects/wt-2026-01-20__o365-outlook-general/.venv/bin/python tools/graph/draft_structured_email.py \
  --input runs/<RUN_ID>/inputs/email_spec.json \
  --fallbacks runs/<RUN_ID>/inputs/link_fallbacks.json
```

### JSON shape for `--input`

```json
{
  "subject": "Subject line",
  "to": ["person1@example.com"],
  "cc": ["person2@example.com"],
  "greeting": "Hi team,",
  "context": [
    "Context line 1",
    "Context line 2"
  ],
  "sections": [
    {
      "title": "1) Item name",
      "budget": "$123,456",
      "link_label": "Epic link",
      "link_key": "found_s31_link",
      "extra_lines": ["Related artifacts: [PASTE HERE]"],
      "summary_bullets": ["Problem", "Outcome", "Scope"],
      "confirm": "Please confirm needed/not needed and owner."
    }
  ],
  "asks": [
    "Still needed / Not needed",
    "If needed: why + what specifically + owner",
    "Risk if not funded"
  ],
  "touchpoint_line": "Ideally before our next touchpoint.",
  "close": "Thanks,",
  "signer": "Matt"
}
```
