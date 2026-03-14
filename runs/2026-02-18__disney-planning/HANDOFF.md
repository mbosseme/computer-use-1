# Run Handoff Journal: 2026-02-18__disney-planning

## Summary
- Run for Disney ADR (dining reservation) booking automation.
- Using Playwright MCP server for browser automation against disneyworld.disney.go.com.

## Session 1 (Feb 18-19, 2026)
- Booked: Grand Floridian Café, Whispering Canyon Café, San Ángel Inn.
- Attempted & unavailable: Sci-Fi Dine-In, Yak & Yeti, Hollywood Brown Derby.
- Remaining: Beak and Barrel, Sanaa, plus substitutions needed.

## Session 2 (Mar 14, 2026)
- Resumed. Pulled latest from main. Attempted to check Sci-Fi availability again.
- **Lesson learned (critical)**: When the Disney dining SPA widget failed to load (Angular errors, timeouts), the agent incorrectly pivoted to writing a standalone Python Playwright script (`check_scifi.py`). This caused:
  - Ghost Chromium tabs flashing on the user's screen.
  - Profile lock conflicts with the MCP-managed browser.
  - Dependency installation failures (`playwright install` blocked by cert errors).
  - Complete loss of the authenticated MCP session.
- **Resolution**: Killed the rogue script, reconnected to the MCP browser, and updated core docs (`copilot-instructions.md`, `browser-automation-core/SKILL.md`) with an anti-pattern rule to prevent recurrence.
- **Correct approach**: Always use MCP tools. If a widget won't load, reload the page, try alternate URLs (e.g., `/dining/` info page vs `/dine-res/` SPA), adjust selectors, or ask the user. Never spawn a competing browser.

## Disney site notes
- **Party Size**: The party size for all reservations should always be **4**.
- The `/dine-res/restaurant/<slug>/` URL pattern uses an Angular SPA that can fail to load the booking widget (shows error page or empty widget area).
- The `/dining/<park>/<restaurant>/` URL pattern loads the restaurant info page with an embedded date picker and "Check Availability" link — this may be a more reliable entry point.
- The site shows "We See-See-See There is a Problem!" when the SPA crashes.
- The user is logged in as "Matt" in the MCP browser profile.

## Next steps
- Continue with Task B (Sci-Fi Dine-In check) using MCP tools only.
- Then Task C ('Ohana) and Task D (Diamond Horseshoe).

## Blockers
- Disney dining SPA widget intermittently fails to load (Angular errors). May need alternate approach via the info page date picker.

- **Progress UPDATE**: Checked Sci-Fi for Apr 10, Party Size 4 (Unavailable). Progressed to Diamond Horseshoe on Apr 8. Selected 4:55 PM. Triggered wait/hold. Need user to authenticate through HITL.

- **Progress UPDATE:** User authenticated and completed the booking for Diamond Horseshoe (Wed Apr 8 at 4:55 PM). Moved on to Yak & Yeti.
- **Progress UPDATE:** Checked Yak & Yeti for Tue Apr 7, Lunch (Unavailable). Progressed to 'Ohana for Dinner. Found a table on Tue Apr 7 at 9:25 PM! Reached the final confirmation screen and waiting for HITL confirmation to click 'Confirm'.
- **Time Restrictions**: Dinners cannot be booked for later than **7:30 PM**.
- **Progress UPDATE:** User requested a summary of all booked reservations by day, so I verified against the active My Plans page.
- **Progress UPDATE:** Consolidated ADR planning, waitlist, and constraints into docs/DISNEY_ADR_STATE.md and created .github/prompts/scan-adrs.prompt.md to act as a saved prompt for checking the list iteratively going forward.

## Session 2 Wrap-up (Mar 14, 2026)

### What was accomplished
1. Ran the first routine ADR scan via `scan-adrs.prompt.md`:
   - Sci-Fi Dine-In (Apr 10): No availability.
   - Yak & Yeti (Apr 7): No availability.
   - 'Ohana (Apr 5, 7, 9): Available but only at 9:20+ PM — rejected per 7:30 PM constraint.
2. Created `docs/DISNEY_SITE_NAVIGATION.md` — Disney-specific UI patterns for efficient browser automation.
3. Updated `scan-adrs.prompt.md` with a Pre-flight section that loads the core browser skill, Disney site reference, and ADR state before scanning.
4. Promoted general SPA automation patterns to core (`main` via PR #60):
   - browser-automation-core: SPA snapshot triage, accordion expansion, ref invalidation, calendar widgets, systematic scanning.
   - copilot-instructions: MCP-first rule with escalation ladder.
   - Local-First Briefing: auth/login protocol for MCP browser.

### Key files for next session
| File | Purpose |
|------|---------|
| `docs/DISNEY_ADR_STATE.md` | Single source of truth: constraints, waitlist, secured itinerary |
| `docs/DISNEY_SITE_NAVIGATION.md` | Disney site-specific UI patterns for the agent |
| `.github/prompts/scan-adrs.prompt.md` | Reusable prompt — just invoke it to run a scan |
| `.github/skills/browser-automation-core/SKILL.md` | General SPA automation patterns (now on main) |

### Current waitlist status (as of Mar 14)
- **Sci-Fi Dine-In Theater** — Target: Fri Apr 10 (Lunch or Dinner) — No availability
- **Yak & Yeti Restaurant** — Target: Tue Apr 7 (Lunch) — No availability
- **'Ohana** — Target: Dinner on Apr 9, 7, or 5 — Only 9 PM+ slots available (violates 7:30 PM rule)

### What to do next
- Run the `scan-adrs.prompt.md` prompt again to check for new cancellations.
- The browser may need re-authentication (login state may have expired). Expect HITL for Disney login.
- If availability opens up for any waitlist item within constraints, the prompt will guide through booking with HITL confirmation.
