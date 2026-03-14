---
description: Scan for Disney Advanced Dining Reservations (ADRs) against our waitlist.
---

# Task: Routine Disney ADR Scan

Please execute the routine check for our Disney Advanced Dining Reservations (ADRs) to see if any cancellations have opened up spots for our priority waitlist.

## Pre-flight (read these before touching the browser)

1. **Load the core browser skill:** Read `.github/skills/browser-automation-core/SKILL.md` — pay special attention to the "Working with Large / Complex SPA Snapshots" section (SPA ref invalidation, calendar widgets, systematic scanning).
2. **Load the Disney site reference:** Read `docs/DISNEY_SITE_NAVIGATION.md` — this has Disney-specific UI patterns (search form controls, calendar widget, how results are structured, accordion behavior).
3. **Read the central state file:** Read `docs/DISNEY_ADR_STATE.md` to get the current Secured Itinerary, the Waitlist of target restaurants, and our explicit Constraints.

## Execution

4. **Scan the Waitlist:**
   For each restaurant in the "Waitlist" section, use the Playwright MCP server to navigate to Disney's dining availability (`https://disneyworld.disney.go.com/dine-res/availability` or just by navigating the UI directly) and aggressively check for openings. Follow the patterns described in `docs/DISNEY_SITE_NAVIGATION.md` for interacting with the search form and interpreting results. Key reminders:
   - Always re-snapshot after changing a date or filter — refs are invalidated.
   - Grep the snapshot for the target restaurant name to check results efficiently.
   - If grep returns exit code 1, the restaurant has no availability for that date — move on.

5. **Respect Constraints:**
   * Adhere strictly to the "Global Constraints" (e.g., party size is ALWAYS 4, dinner times ALWAYS <= 7:30 PM).
   * Ensure the available times do not conflict with the "Secured Itinerary".

6. **Handle Success / Booking:**
   If a match is found that fits all criteria, attempt to proceed through the booking UI until you reach the final confirmation screen. *Pause and request Human-in-the-Loop (HITL) confirmation* from me before you click the final "Confirm" or "Complete Bookings" button. Only complete it after I say "done".

7. **Report & Update:**
   Once the scan is complete, summarize the outcome. If any new reservations were successfully secured through our HITL workflow, document the confirmation number and immediately update `docs/DISNEY_ADR_STATE.md` by moving the restaurant from the Waitlist to the Secured Itinerary section.
