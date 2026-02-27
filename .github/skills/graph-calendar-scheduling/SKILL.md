---
name: "Microsoft Graph Calendar Scheduling"
description: "Find mutual availability and create Outlook calendar events safely (including true draft events that are not sent to attendees yet)."
tools:
  - terminal
---

## When to use
- The user asks to **find** a meeting on the calendar, **reschedule**, **find a mutual time**, or **create a meeting invite**.
- Especially relevant when the user says **"draft the Outlook invite"** or **"create it but don’t send it yet"**.

## Key distinction (common confusion)
### A) Draft email with .ics attachment (email Drafts)
- This creates a **draft email** in *Drafts* with a calendar attachment.
- It does **not** create an event on the organizer’s calendar.
- Useful when the user explicitly wants an email draft they will send manually.

### B) Draft meeting on the calendar (Safe "no-send" workaround)
- **Constraint**: The Microsoft Graph API **immediately sends invites** if you populate the `attendees` array in a `POST /me/events` call. The `isDraft` property is read-only and cannot be set to `true`.
- **Solution**: Create the event **without** populating the `attendees` array.
- **Workaround**: List the desired attendees in the **event body** (HTML) in a clearly marked "Copy-Paste" block.
- This creates a real event on the organizer's calendar for the correct time/context, but guarantees no emails are sent until the user manually adds the attendees in Outlook.

## Preconditions
- Delegated Graph auth configured and working (see docs/GRAPH_AUTH_REPLICATION_GUIDE.md).
- Scopes: `Calendars.ReadWrite` (and `User.Read` for /me).
- **Default Scheduling Profile**:
  - Timezone: `Eastern Standard Time` (EST/EDT).
  - Business Hours: **08:30** to **16:30**. Do not schedule earlier than 8:30 AM or later than 4:30 PM unless explicitly requested.

## Recommended approach (safe + repeatable)
### 1) Determine the target time window
- Default to **08:30 - 16:30 Eastern Standard Time**.
- Normalize time zone:
  - **Graph getSchedule/findMeetingTimes** expects a **Windows timezone name** (e.g., `Eastern Standard Time`).
  - Local formatting (Python) can use IANA (e.g., `America/New_York` or `US/Eastern`).

### 2) Compute mutual availability (organizer + attendees)
- Use `POST /me/calendar/getSchedule` (granular) or `POST /me/findMeetingTimes` (high-level suggestions).
- Reusable CLI utility (preferred for quick runs):
  - `python tools/graph/find_mutual_slots.py --emails <email1> <email2> ... --days 7 --duration 30 --day-start 08:30 --day-end 16:30 --allow-tentative`
- For `findMeetingTimes`:
  - Pass `maxCandidates`, `meetingDuration`, and `timeConstraint` (restricted to 8:30-4:30 EST).
  - Note: `findMeetingTimes` may fail or error with >20 attendees. Fall back to checking the specific date/time directly if the list is large.

### 3) Create the **calendar event as a draft** (do not send)
- Create event: `POST /me/events` with `subject`, `start`, `end`, `location`, `body`.
- **Crucial**: Leave `attendees` array **empty** (`[]`).
- **Body Pattern**: Append a "Proposed Attendees" HTML block to the body.
  - **Start** with a clear header text (e.g., "AGENT NOTE: Attendees to Copy").
  - **No background colors** (avoid yellow highlighting).
  - **Content**: Provide **only** the email addresses, separated by semicolons (e.g., `email1@domain.com; email2@domain.com`). Do not include names, as Outlook handles raw emails best for copy-paste.
  ```html
  <div style="padding: 10px; border: 1px dashed #666; font-family: sans-serif;">
      <strong>⚠️ AGENT NOTE: Attendees not yet invited</strong><br/>
      Copy the email list below and paste into the "Add attendees" field:<br/><br/>
      <div style="font-family: monospace; user-select: all; padding: 5px; border: 1px solid #ccc;">
          user1@example.com; user2@example.com
      </div>
  </div>
  <hr/>
  (Original Body Content)
  ```

## HITL / safety
- “Sending” meeting updates/invites is effectively **irreversible**.
- Never send invites/updates without explicit user confirmation immediately before sending.

## Troubleshooting
- If created event returns `isDraft: false`, do not proceed; stop and ask the user before any sending action.
- If `getSchedule` returns empty/invalid, fall back to:
  - Narrow the date window
  - Smaller attendee set (debug)
  - Or use organizer-only availability to propose candidates
