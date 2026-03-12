## Status: 2026-03-12 — Session 7: March 11 Full Pipeline Run
### What was accomplished
*   **March 12 scaffolded**: 6 Word docs created for today's meetings.
*   **March 11 fully processed**: 8 meetings checked, 5 had recaps, all 5 extracted (AI summary + custom summary).
*   **Critical `pbpaste` truncation bug discovered and worked around**: macOS `pbpaste` consistently truncates long text from Teams clipboard (captures only 12-23 lines instead of 70-100+). Root cause unclear. Workaround: extract text directly from the DOM via `browser_evaluate`, then save via `create_file`.
*   **Pipeline prompt updated**: `.github/prompts/meeting-notes-pipeline.prompt.md` now documents the `pbpaste` truncation issue, DOM extraction approach, stale ref handling, and terminal heredoc garbling.

### March 11 Pipeline Results
| Meeting | Time | Recap? | AI Summary | Custom Summary |
|---------|------|--------|------------|----------------|
| Growth Core Project Team | 9:00 AM | ✅ | 15 text + 3 images | 89 lines |
| Data Science Review/Update | 9:30 AM | ✅ | 19 text + 3 images | 73 lines |
| Matt B / Lucky Connect | 12:00 PM | ❌ | — | — |
| CRM Kickoff/Orientation | 12:30 PM | ✅ | 11 text + 0 images | 83 lines |
| ABI Data Science Weekly Sync | 1:00 PM | ✅ | 11 text + 4 images | 74 lines |
| Lets Geek On AI | 2:00 PM | ✅ | 15 text + 0 images | 83 lines (Teams truncated at end) |
| Matt Jesse 1:1 | 3:00 PM | ❌ | — | — |
| HonorHealth RFP | 3:30 PM | ❌ | — | — |

Skipped: Matt Sri 1:1 (not scaffolded), Weekly 1:1 Audrey (not scaffolded), HOLDs, Watch Kids, test call.

### New Learnings (Session 7)
*   **`pbpaste` is UNRELIABLE for custom summaries** — always use DOM extraction via `browser_evaluate` instead. The agent should extract `innerText` from `[role="region"]` elements and save to file using `create_file` (not terminal heredoc).
*   **DOM extraction may need chunking**: If text > ~3000 chars, `browser_evaluate` return values can be truncated. Extract in chunks using `text.substring(0, 2900)` / `text.substring(2900)`.
*   **Stale Playwright refs**: After clicking "Copy all" (or any interaction), element refs change. Always take a fresh `browser_snapshot` before re-interacting with the same area.
*   **Teams generation truncation**: Occasionally Teams Copilot itself truncates long custom summaries mid-sentence. Not fixable; note in output.
*   **Terminal heredocs garble multi-line content** in this workspace shell. Use `create_file` tool instead.

## Status: 2026-03-11 — Full E2E Pipeline Validated
### What was accomplished
*   **End-to-end pipeline validated** for March 10, 2026 — scaffold → Teams recap extraction → Word doc injection, all via Playwright MCP + macOS clipboard.
*   **`tools/meeting_notes.py` parameterized**: Added `--date YYYY-MM-DD`, `--scaffold-only`/`--create-only`, `--force` flags for targeted single-day runs.
*   **Pipeline prompt updated**: `.github/prompts/meeting-notes-pipeline.prompt.md` now documents CLI flags.
*   **AI Summary extraction proven reliable**: Rich clipboard capture via `osascript` preserves base64 images inline. Verified by manual comparison — ordering, screenshots, and text all match a fresh copy-paste from Teams UI.
*   **Custom Summary (Loss-Less Extraction Template) extraction proven reliable**: ~~`pbpaste` captures the full structured text~~ **UPDATE (Session 7)**: `pbpaste` truncates; use DOM extraction via `browser_evaluate` instead (see Session 7 learnings above).
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

**Custom Summary** (DOM extraction — do NOT use pbpaste):
```js
// In browser_evaluate after clicking "Copy all":
() => {
  const regions = document.querySelectorAll('[role="region"]');
  for (const r of regions) {
    const text = r.innerText;
    if (text.length > 200) return text; // or chunk if > 3000 chars
  }
}
```
Save result to file using `create_file` tool, then inject:
```bash
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
*   **`pbpaste` truncates custom summaries**: macOS clipboard (`pbpaste`) consistently captures only 12-23 lines of Teams custom summary text instead of the full 70-100+ lines. **Always use DOM extraction** via Playwright `browser_evaluate` to get the full text from `[role="region"]` elements. Save using `create_file` tool, not terminal heredoc.
*   **DOM extraction chunking**: If the DOM text exceeds ~3000 characters, `browser_evaluate` may truncate the return value. Extract in chunks: `text.substring(0, 2900)` + `text.substring(2900)`.
*   **Calendar resets to today** when clicking the Calendar sidebar button to return from a recap view. Always re-click the target date on the mini calendar.
*   **Rich clipboard required** for AI summaries — `pbpaste` drops embedded images. Use `osascript` via `inject_ai_summary_rich.py`.
*   **Stale Playwright refs**: After browser interactions (clicking buttons), element refs change. Take a fresh `browser_snapshot` before re-interacting with the same page area.
*   **Content ordering** in Word docs: use forward iteration with `lxml.addprevious()`. Using `reversed()` causes reversed content.
*   **Playwright profile** lives at `runs/2026-03-02__onenote-org/playwright-profile` — kill stale Chrome processes before launching: `pkill -f "user-data-dir.*playwright-profile"`.
*   **Meetings without recap**: No "View recap" button means no Teams recording/transcription was enabled. The meeting gets a scaffold doc but no Teams content.
*   **Attendee filter**: `meeting_notes.py` skips meetings with ≤1 non-organizer attendee (solo calendar blocks).
*   **Terminal heredocs garble**: Multi-line content via shell heredoc (`cat << EOF`) gets corrupted in this workspace shell. Use `create_file` tool instead.
*   **Teams generation truncation**: Teams Copilot may truncate long custom summaries mid-sentence (its own generation limit). Not fixable; document in output.

## Next Steps / Open Questions
*   **Daily operation**: The pipeline is validated and ready for daily use via the `/run-meeting-pipeline` prompt. Run it each morning for the prior day's meetings.
*   **Skill creation**: Consider converting the Playwright navigation steps into a `.github/skills/` file so any agent session can run it without re-reading docs.
*   **Otter integration**: Otter transcript matching (Step 1) runs alongside scaffold. Both sources can coexist in the same doc.
*   **Promotion candidates**: `tools/meeting_notes.py`, `.github/prompts/meeting-notes-pipeline.prompt.md`, `docs/MEETING_NOTES_PIPELINE.md`, `docs/TEAMS_COPILOT_EXTRACTION_GUIDE.md` are all candidates for merge to `main` via clean PR.
