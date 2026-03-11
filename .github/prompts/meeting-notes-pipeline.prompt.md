---
name: run-meeting-pipeline
description: "Executes the daily meeting notes pipeline: creates notes docs, matches Otter transcripts, and extracts high-fidelity meeting recaps from Microsoft Teams using Playwright."
---

# Meeting Notes Pipeline

## Objective
Automatically generate, enrich, and process daily meeting notes. This process incorporates scaffolding notes files, mapping Otter.ai transcripts, and automating the extraction of high-fidelity details from Microsoft Teams "Recap" functionality via Playwright MCP.

## The Process

Please execute the following pipeline chronologically:

### 1. Daily Initialization & Otter.ai Sync
Run the local `tools/meeting_notes.py` tool.
- **Action**: In the terminal, execute `PYTHONPATH=. python3 tools/meeting_notes.py`.
- **Purpose**: This scaffolds `.docx` files for calendar events (for yesterday and today) and skips events that are PTO, holds, or 1-on-0 standalone tasks. It also parses `Downloads` or `Otter Exports` for matching ZIPs/TXT files and intelligently appends transcript data into the "Otter Transcript Imports (Append-Only)" section.
- **CLI flags**:
  - `--date YYYY-MM-DD` — target a specific date (default: yesterday + today)
  - `--scaffold-only` / `--create-only` — only create Word docs (skip Otter processing)
  - `--append-only` — only process Otter exports (skip doc creation)
  - `--force` — regenerate docs even if they already exist (overwrites)
- The generated Word docs have this heading structure:
  - **H1: [Meeting Title]** — metadata, attendees, description
  - **H1: Manual Notes** — free-form area for human notes
  - **H1: Teams AI Summary** — target for AI summary injection (step 2c)
  - **H1: Teams Custom Summary (Loss-Less Extraction)** — target for custom summary injection (step 2d)
  - **H1: Otter Transcript Imports (Append-Only)** — Otter transcripts
- **Wait**: Ensure the command finishes completely before proceeding to Step 2.

### 2. Teams Recap Extraction Loop (Playwright MCP)
Use the Playwright MCP to access the Microsoft Teams web UI (`https://teams.microsoft.com/v2/`).

#### 2a. Navigate to the prior day's calendar
1. Click the **Calendar** button in the left sidebar to open the calendar view.
2. Click the **"Go to previous day"** button in the calendar toolbar to navigate to yesterday's date.
3. **Verify** the date header shows yesterday's date before proceeding.

#### 2b. Systematically check EVERY meeting for recap availability
For each meeting event button visible on the calendar day view (skip HOLDs, Watch Kids, Canceled events):
1. **Click the meeting event button** on the calendar to open its popover/detail card.
2. **Look for a "View recap" button** in the popover. This is the definitive signal that a Teams recording + recap exists.
   - If **no "View recap" button** is present → that meeting was not recorded in Teams. Move to the next meeting.
   - If **"View recap" IS present** → click it to open the full recap view. Then proceed to steps 2c and 2d below.

#### 2c. Capture AI Summary WITH Screenshots (for each meeting with recap)
1. The recap view opens with tabs: Notes, **AI summary**, **Custom summary**, Mentions, Transcript.
2. Click the **"AI summary"** tab/pill if not already selected.
3. Click the **"Copy all"** button (top-right of the summary content area).
   - Teams places **rich HTML** on the clipboard containing both text AND embedded screenshot images (base64 data URIs). The standard `pbpaste` only captures plain text and **loses the images**.
4. **Inject directly from the rich clipboard** using the rich injection script:
   ```bash
   python3 runs/<RUN_ID>/scripts/inject_ai_summary_rich.py "<doc_path>" --from-clipboard \
     --save-html runs/<RUN_ID>/tmp/<meeting_slug>_ai_summary.html
   ```
   - This reads the macOS clipboard via `osascript` (hex-encoded HTML), decodes it, parses text + base64 images, and injects both into the Word doc under the **"Teams AI Summary"** H1 heading (or legacy names "AI Summary & Screenshots" / "Screenshots / Images").
   - The `--save-html` flag saves the raw HTML for debugging/re-injection if needed.
5. **Do NOT use `pbpaste`** for AI summaries — it strips the screenshot images.

#### 2d. Capture Custom Summary / Loss-Less Extraction (for each meeting with recap)
1. Click the **"Custom summary"** tab/pill.
2. A list of saved templates appears. Click the **"Loss-Less Extraction Template"** tab/button.
   - This triggers Teams Copilot to generate the exhaustive extraction. You will see "Generating your summary..." with a loading indicator.
3. **Wait for generation to complete** (typically 10-20 seconds). Poll the snapshot until the loading indicator disappears and a **"Copy all"** button appears.
4. Click the **"Copy all"** button.
5. **Immediately save the clipboard** to a temp file:
   ```bash
   pbpaste > runs/<RUN_ID>/tmp/<meeting_slug>_custom_summary.txt
   ```

#### 2e. Inject captured data into Word documents
After extracting both summaries for a meeting:
- **AI Summary** → already injected by the `inject_ai_summary_rich.py` script in step 2c (text + screenshots under the **"Teams AI Summary"** H1 heading).
- **Custom Summary** → inject under the **"Teams Custom Summary (Loss-Less Extraction)"** H1 heading:
```
runs/<RUN_ID>/scripts/inject_teams_recap.py --doc <doc_path> --custom-summary <custom_summary_file>
```

#### 2f. Return to calendar and repeat
After processing each meeting with a recap:
1. Click the **Calendar** sidebar button to return to the calendar view.
2. Navigate back to the target date if needed (the calendar may reset to today).
3. Click the next meeting event and repeat from step 2b.

**Do this for ALL meetings on the prior day, then repeat for today's date if any today-meetings have already concluded and have recaps.**

### 3. Review & Validate
Once you have processed all meetings for the targeted dates, browse to verifying the result formatting is intact.
- Verify `tools/meeting_notes.py` skipped events like 'PTO' and 'Watch Kids'.
- Verify that Word documents are correctly structured with no overwritten manual notes.
- Summarize your actions here in chat.