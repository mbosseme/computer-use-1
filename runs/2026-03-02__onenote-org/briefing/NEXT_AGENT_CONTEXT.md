# Next Agent Context — 2026-03-02__onenote-org

## Purpose
This brief captures session context so a fresh agent can quickly orient before starting the next related task.

## What was completed across sessions (chronological)

### Session 1-2: Foundation
- Run bootstrap, Playwright per-run isolation, OneNote API research
- Playwright profile configured at `runs/2026-03-02__onenote-org/playwright-profile`

### Session 3: Meeting Notes Pipeline Scaffolding
- Built `tools/meeting_notes.py` — scaffolds Word docs from Outlook Graph calendar
- Built Otter transcript matching + injection via LLM disambiguation
- Created `.github/prompts/meeting-notes-pipeline.prompt.md` slash command

### Session 4: Teams Recap Extraction via Playwright MCP
- Navigated Teams web UI via Playwright MCP to extract AI summaries + custom summaries
- Discovered that `pbpaste` drops images from AI summary (rich HTML with base64 data URIs)
- Built `inject_ai_summary_rich.py` — reads macOS rich clipboard via `osascript`, preserves images
- Built `inject_teams_recap.py` — injects custom summary plain text
- Created the "Loss-Less Extraction Template" meta-prompt for Teams Copilot custom summaries

### Session 5: Content Ordering Fix + Template Restructure
- Fixed content ordering bug: `lxml.addprevious()` with `reversed()` caused reversed content → switched to forward iteration
- Restructured Word doc template to 4 clean H1 sections: Manual Notes → Teams AI Summary → Teams Custom Summary → Otter Transcript Imports
- Built `rebuild_doc.py` for migrating existing docs to new template

### Session 6: E2E Validation + Parameterization
- Added `--date`, `--scaffold-only`, `--force` CLI flags to `meeting_notes.py`
- Cleared March 10 folder, scaffolded 5 fresh docs, ran full pipeline
- **Platform Showcase**: AI summary (19 text + 12 images) + custom summary (89 lines) extracted and injected
- **SC Internal Deal Desk**: AI summary (17 text + 9 images) + custom summary (85 lines) extracted and injected
- 3 other meetings had no Teams recap (not recorded)
- **User verified**: AI summary extraction matches manual copy-paste perfectly (ordering + screenshots)
- Committed (439e867) and pushed to `origin/run/2026-03-02__onenote-org`

### Session 7: March 11 Full Pipeline Run + Reliability Improvements
- Scaffolded 6 March 12 docs, processed all 8 March 11 meetings (5 had recaps)
- **Critical discovery**: `pbpaste` consistently truncates custom summary clipboard content (only 12-23 lines captured instead of 70-100+). Workaround: extract text directly from DOM via Playwright `browser_evaluate` on `[role="region"]` elements.
- **DOM extraction chunking**: Large texts (>3000 chars) need to be extracted in chunks via `text.substring()` to avoid `browser_evaluate` return truncation.
- Updated pipeline prompt with: `pbpaste` deprecation for custom summaries, DOM extraction approach, stale ref handling, heredoc garbling workaround, Teams generation truncation documentation.
- Updated HANDOFF.md with new gotchas and March 11 results.
- All 5 recap meetings fully injected (AI summary + custom summary).

## Current state of the worktree
- Branch: `run/2026-03-02__onenote-org` — pushed and up-to-date with origin
- OneDrive folder has 5 March 10 docs (2 enriched), 8 March 11 docs (5 enriched), 6 March 12 docs (scaffold only)
- Pipeline is validated and ready for daily use
- **Key change**: Custom summary capture now uses DOM extraction via `browser_evaluate` instead of `pbpaste` (which truncates)

## Files to read first in next chat
1. `runs/2026-03-02__onenote-org/HANDOFF.md` — status, quick reference, gotchas
2. `runs/2026-03-02__onenote-org/briefing/NEXT_AGENT_CONTEXT.md` (this file)
3. `.github/prompts/meeting-notes-pipeline.prompt.md` — the pipeline slash command
4. `docs/MEETING_NOTES_PIPELINE.md` — architecture overview
5. `docs/TEAMS_COPILOT_EXTRACTION_GUIDE.md` — Loss-Less Extraction Template details

## Notes for the next agent
- The pipeline is operational. To run for a specific date: use the `/run-meeting-pipeline` prompt or run steps manually per HANDOFF.md.
- **Critical**: Do NOT use `pbpaste` for custom summaries — it truncates. Use DOM extraction via `browser_evaluate` (see pipeline prompt step 2d).
- **Critical**: Save extracted text using `create_file` tool, NOT terminal heredoc (which garbles multi-line content).
- Keep all run-local artifacts under `runs/2026-03-02__onenote-org/`.
- Do not store sensitive URLs/tokens/secrets in run notes.
- Playwright isolation is already configured; kill stale Chrome before restarting: `pkill -f "user-data-dir.*playwright-profile"`.
- The worktree is on `run/2026-03-02__onenote-org` branch. Core-path files (`tools/`, `docs/`, `.github/`) can be promoted to `main` via clean PR protocol (see AGENTS.md).
