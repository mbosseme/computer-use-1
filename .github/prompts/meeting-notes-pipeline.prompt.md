---
name: run-meeting-pipeline
description: Executes the daily meeting notes pipeline, creates notes docs, matches Otter transcripts (including from Downloads), and selectively extracts high-fidelity meeting recaps from Microsoft Teams using Playwright based on pending status.
---

# Meeting Notes Pipeline

## Objective
Automatically generate, enrich, and process daily meeting notes. This process incorporates scaffolding notes files, mapping Otter.ai transcripts (checking both the OneDrive inbox and `~/Downloads`), and automating the extraction of high-fidelity details from Microsoft Teams "Recap" functionality via Playwright MCP. The pipeline is stateful and tracks which meetings have already been checked for Teams Recaps.

## The Process

Please execute the following pipeline chronologically:

### 1. Initialization & Finding Pending Work
Run the local `tools/meeting_notes.py` tool.
- **Action**: In the terminal, execute `PYTHONPATH=. python3 tools/meeting_notes.py --list-pending-teams --target-date <DATE>`. The agent should prompt the user for the target date if not provided.
- **Purpose**: This scaffolds `.docx` files for calendar events, skips PTO/hold events, and parses `Otter Exports` and `~/Downloads` for matching ZIPs/TXT files. It intelligently appends transcript data into existing docs.
- **State Tracking**: At the end of its output, it will print a section titled `PENDING TEAMS RECAP CHECKS FOR TARGET DATES`. This is your task list! Only the items listed here need to be checked in Teams.
- **Wait**: Ensure the command finishes completely and note the list of pending meetings before proceeding to Step 2.

### 2. Teams Recap Extraction Loop (Playwright MCP)
Use the Playwright MCP to access the Microsoft Teams web UI (`https://teams.microsoft.com/v2/`).

For **EACH** meeting listed in the `PENDING TEAMS RECAP CHECKS` output:

#### 2a. Navigate to the calendar
1. Open the Teams Calendar tab.
2. Navigate to the specific date of the pending meeting using the mini-calendar date picker.

#### 2b. Check meeting for recap availability
1. **Click the meeting event button** on the calendar to open its popover/detail card.
2. **Look for a "View recap" button** in the popover. This is the definitive signal that a Teams recording + recap exists.
   
   - **If no "View recap" button is present**:
     The meeting was not recorded. Mark it as checked via the terminal so the pipeline doesn't ask you again:
     ```bash
     PYTHONPATH=. python3 tools/meeting_notes.py --mark-teams-checked "<doc_path>"
     ```
     Then move to the next pending meeting on your list.

   - **If "View recap" IS present**: 
     Click it to open the full recap view. Proceed to extract the AI and Custom summaries as done previously using the clipboard and DOM extraction scripts. Then inject them into the corresponding `<doc_path>`.
     After extraction and injection is complete, mark the meeting as checked:
     ```bash
     PYTHONPATH=. python3 tools/meeting_notes.py --mark-teams-checked "<doc_path>"
     ```

### 3. Review & Validate
Once you have processed ALL pending meetings for the target dates, you can quickly verify there's nothing left by running:
`PYTHONPATH=. python3 tools/meeting_notes.py --list-pending-teams --target-date <DATE>`
Summarize your actions cleanly here in chat.
