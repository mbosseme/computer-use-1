# Meeting Notes Automation Pipeline

## Overview
This repository contains a daily automation script (`tools/meeting_notes.py`) that bridges Microsoft Outlook calendar events with local Microsoft Word documents (synced via OneDrive) and automatically merges in Otter.ai meeting transcripts using LLM-driven disambiguation.

## Goal
To eliminate manual prep for back-to-back meetings and ensure that both structured notes and raw AI transcripts live in a single source of truth without overwriting manual context or creating duplicates.

## How it Works

### 1. Daily Document Scaffolding (Calendar → Word)
When run, the script fetches 1-2 days of Microsoft Graph calendar data (`/me/calendarView` via `agent_tools.graph.client`) and generates a structured `.docx` file for every event, skipping meetings that are canceled or marked as "HOLD". 

**Directory Structure:**
Files are safely generated idempotently into a standard OneDrive-synced folder:
`/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notetaking/Meeting Notes/YYYY/MM/DD/`

**File Naming Convention:**
`<YYYY-MM-DD> <HHMM> - <Short Subject> - <AttendeeLastNames> - eid<EventHash>.docx`
*(Example: `2026-03-05 1330 - Project Catalyst - Team Status Update - Holly-Stephen-Jim - eid94823d92.docx`)*

**Document Structure:**
*   H1: Event Subject
*   Metadata block (Time, Organizer, Location/Join Link)
*   H2: Attendees (with response status)
*   H2: Description (Meeting invite body preview)
*   H1: Manual Notes (with sections for Decisions, Action Items, Open Questions)
*   H1: Otter Transcript Imports (Append-Only) -> Reserved for transcript ingestion.

### 2. Intelligent Transcript Matching (Otter → LLM → Calendar ID)
Otter.ai transcript exports (both `.txt` files and `.zip` bundles containing a full transcript and tagged "Takeaways" sections) drop into:
`/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Otter Exports/`

Because Otter's auto-generated meeting titles rarely match outlook subject lines (e.g., "Note.zip" vs "Urgent Request"), the system uses a **Time-Bounded LLM Disambiguation loop**:
1.  **Time Filtering:** The script queries all calendar events from the last 48 hours to +10 hours. It strictly drops any event that started *after* the transcript was exported.
2.  **Top 5 Proximity List:** The 5 chronologically closest valid meetings are compiled into a candidate list, enriched with exact Outlook Subject lines, Time slots, and Attendee Lists.
3.  **LLM Routing (`azure-gpt-5.2`):** The script parses the first 4000 characters of the transcript + all explicitly tagged comments/takeaways. It sends this extracted text alongside the top 5 candidates to Azure OpenAI.
4.  **Verification:** The LLM cross-references speaker tags and discussion context against attendee lists to pick the exact Graph Event ID.

### 3. Weaving Transcripts into Notes (Word Merge)
Once matched to a specific event ID, the script locates the generated `.docx` file.

*   **Idempotency Check:** It scans the Word document for a specific identifier (`(Source ZIP: <Filename>)`). If found, it skips to avoid duplicating content.
*   **Safety:** It appends the transcript at the very bottom of the document so any manual notes typed by the user at the top are not impacted.
*   **Sections Added:**
    *   `H2: Import: <Timestamp> (Source ZIP: <Filename>)`
    *   `H3: Full Transcript` -> The complete raw discussion.
    *   `H3: Portions of transcript Tagged with speaker names for speaker identification` -> The contents of the `_Takeaways` or `_Comments` file to provide heavily clustered highlights.

## For Downstream Agents & Processing
Agents operating on this repository should treat `/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notetaking/Meeting Notes/` as the single source of truth for conversational context.

*   You can read these `.docx` files using `python-docx` or MacOS `textutil`.
*   Note that the bottom of the files will be heavy with transcript data—when generating summaries or tracking action items, ensure you differentiate between the "Manual Notes" section at the top (source of truth from the user) and the "Otter Transcript Imports" section at the bottom (raw conversational context).
### 4. Teams Copilot Native Extraction (Alternative to Otter)
For meetings recorded natively within Microsoft Teams, we utilize a "Loss-Less Extraction" strategy via Teams Copilot (see `docs/TEAMS_COPILOT_EXTRACTION_GUIDE.md`). Instead of relying on Otter transcripts, automation (via Playwright) can inject a structured meta-prompt into the Teams Recap Custom Summary, bypassing summarization entirely to pull out every system name, metric, and friction point directly from the Teams UI.
