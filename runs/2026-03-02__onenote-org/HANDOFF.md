## Status: 2026-03-11 — Full E2E Pipeline Validated
### What was accomplished
*   **End-to-end pipeline validated** for March 10, 2026 — scaffold → Teams recap extraction → Word doc injection, all via Playwright MCP + macOS clipboard.
*   **`tools/meeting_notes.py` parameterized**: Added `--date YYYY-MM-DD`, `--scaffold-only`/`--create-only`, `--force` flags for targeted single-day runs.
*   **Pipeline prompt updated**: `.github/prompts/meeting-notes-pipeline.prompt.md` now documents CLI flags.
*   **AI Summary extraction proven reliable**: Rich clipboard capture via `osascript` preserves base64 images inline. Verified by manual comparison — ordering, screenshots, and text all match a fresh copy-paste from Teams UI.
*   **Custom Summary (Loss-Less Extraction Template) extraction proven reliable**: `pbpaste` captures the full structured text from the "Copy all" button on the Custom summary tab.
*   **Two injection scripts finalized**:
    *   `inject_ai_summary_rich.py` — reads macOS rich clipboard HTML, extracts text + base64 images, injects under "Teams AI Summary" H1 heading.
    *   `inject_teams_recap.py` — injects plain text custom summary under "Teams Custom Summary (Loss-Less Extraction)" H1 heading.
*   **Content ordering fix**: Forward iteration with `lxml.addprevious()` (not `reversed()`) preserves correct document order.
*   **Word doc template**: 4-section structure (Manual Notes → Teams AI Summary → Teams Custom Summary → Otter Transcript Imports) confirmed working.

### March 10 Pipeline Results
| Meeting | Recap? | AI Summary | Custom Summary |
|---------|--------|------------|----------------|
| Platform Showcase (9:30) | ✅ | 19 text + 12 images | 89 lines |
| BBraun MI Demo (10:30) | ❌ | — | — |
| Quick Sync Pod Types (12:00) | ❌ | — | — |
| SC Deal Desk (1:00) | ✅ | 17 text + 9 images | 85 lines |
| TJ-Matt 1:1 (3:30) | ❌ | — | — |

Skipped: Jonathan 1:1 (≤1 non-organizer attendee), Tyson Connect (no doc scaffolded), HOLDs, Watch Kids, Canceled Andi/Matt.

### Key Scripts (run-local)
*   `runs/2026-03-02__onenote-org/scripts/inject_ai_summary_rich.py` — Rich clipboard → Word doc (text + images)
*   `runs/2026-03-02__onenote-org/scripts/inject_teams_recap.py` — Custom summary text → Word doc
*   `runs/2026-03-02__onenote-org/scripts/rebuild_doc.py` — Rebuild docs from old template to new

## Status: 2026-03-10
*   Transitioned Teams Meeting recap usage out of manual processes and into an automated workflow using Playwright MCP.
*   Determined that Teams Copilot "summarization" drops dense figures (e.g. $1 Billion metric).
*   Refined and finalized a "Loss-Less Extraction Template" meta-prompt that succeeds across broad domains without hardcoding details.
*   Documented findings in `docs/TEAMS_COPILOT_EXTRACTION_GUIDE.md` and added a reference to it in `docs/MEETING_NOTES_PIPELINE.md`.

## How the Pipeline Works (Quick Reference)

### Step 1: Scaffold Word Docs
```bash
PYTHONPATH=. python3 tools/meeting_notes.py --date 2026-03-10 --scaffold-only
```
Creates `.docx` files in OneDrive-synced folder with 4 H1 sections:
1. Manual Notes
2. Teams AI Summary
3. Teams Custom Summary (Loss-Less Extraction)
4. Otter Transcript Imports (Append-Only)

### Step 2: Teams Recap Extraction (Playwright MCP)
For each meeting on the target date with a "View recap" button:

**AI Summary** (rich clipboard with images):
```bash
python3 runs/2026-03-02__onenote-org/scripts/inject_ai_summary_rich.py "<doc_path>" \
  --from-clipboard --save-html runs/2026-03-02__onenote-org/tmp/<slug>_ai_summary.html
```
- Uses `osascript` to read macOS rich clipboard (hex-encoded HTML with base64 images)
- Injects text + images under the "Teams AI Summary" H1 heading

**Custom Summary** (plain text):
```bash
pbpaste > runs/2026-03-02__onenote-org/tmp/<slug>_custom_summary.txt
python3 runs/2026-03-02__onenote-org/scripts/inject_teams_recap.py \
  --doc "<doc_path>" --custom-summary <custom_summary_file>
```
- Injects under the "Teams Custom Summary (Loss-Less Extraction)" H1 heading

### Playwright Navigation Pattern
1. Open Teams Calendar → navigate to target date via mini-calendar date picker
2. Click each meeting → look for "View recap" button in popover
3. If recap exists: open it → copy AI summary → inject → copy custom summary → inject
4. Escape / click Calendar to return → repeat for next meeting
5. Calendar resets to today after sidebar click — must re-click target date

## Known Patterns & Gotchas
*   **Calendar resets to today** when clicking the Calendar sidebar button to return from a recap view. Always re-click the target date on the mini calendar.
*   **Rich clipboard required** for AI summaries — `pbpaste` drops embedded images. Use `osascript` via `inject_ai_summary_rich.py`.
*   **`pbpaste` is fine** for custom summaries (plain text only, no images).
*   **Content ordering** in Word docs: use forward iteration with `lxml.addprevious()`. Using `reversed()` causes reversed content.
*   **Playwright profile** lives at `runs/2026-03-02__onenote-org/playwright-profile` — kill stale Chrome processes before launching: `pkill -f "user-data-dir.*playwright-profile"`.
*   **Meetings without recap**: No "View recap" button means no Teams recording/transcription was enabled. The meeting gets a scaffold doc but no Teams content.
*   **Attendee filter**: `meeting_notes.py` skips meetings with ≤1 non-organizer attendee (solo calendar blocks).

## Next Steps / Open Questions
*   **Daily operation**: The pipeline is validated and ready for daily use via the `/run-meeting-pipeline` prompt. Run it each morning for the prior day's meetings.
*   **Skill creation**: Consider converting the Playwright navigation steps into a `.github/skills/` file so any agent session can run it without re-reading docs.
*   **Otter integration**: Otter transcript matching (Step 1) runs alongside scaffold. Both sources can coexist in the same doc.
*   **Promotion candidates**: `tools/meeting_notes.py`, `.github/prompts/meeting-notes-pipeline.prompt.md`, `docs/MEETING_NOTES_PIPELINE.md`, `docs/TEAMS_COPILOT_EXTRACTION_GUIDE.md` are all candidates for merge to `main` via clean PR.
