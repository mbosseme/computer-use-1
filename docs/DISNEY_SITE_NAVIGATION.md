# Disney My Disney Experience — Site Navigation Reference

**Scope**: This document captures site-specific UI patterns for `disneyworld.disney.go.com`. It is only relevant in this workspace (Disney planning). The agent should consult this before interacting with the Disney site to avoid repeating past mistakes.

---

## Dining Availability Search

### Entry Point
- URL: `https://disneyworld.disney.go.com/dine-res/availability`
- Alternatively navigate from the search results page at `/dine-res/search-results`.

### Search Form Controls
The search form has three controls, each with an **"Edit"** button to modify:

1. **Party Size**: Defaults to 2. Click the "Select Party Size Edit" button → select from a dropdown. The heading reads like `"Select Party Size Edit 4 Guests"`.
2. **Date**: Click the "Date Edit Selected Date …" button → opens an inline calendar. The calendar uses `gridcell` roles (see below).
3. **Time**: Click the "Edit undefined" (or similar) time button → reveals radio buttons for `"All Day"`, `"Breakfast"`, `"Lunch"`, `"Dinner"`. Select the desired radio. The "All Day" radio's accessible name starts with `"All Day | Selecting this"`.

### Calendar Widget
- The calendar renders two months side by side (e.g., March and April).
- Each month grid is labeled like `"Calendar, April"`.
- Days are `gridcell` elements with the day number as the name.
- **Overflow days** from adjacent months appear as `[disabled]` gridcells — ignore these.
- The currently selected date has `[selected]` on its gridcell.
- After clicking a date, the page **fully re-renders the results panel** — all previous refs become stale. Re-snapshot before doing anything else.

### Search Results
- Results appear below the search form as a list of restaurant "regions".
- Each restaurant is wrapped in a `region` with the restaurant name (e.g., `region "'Ohana"`).
- Inside each region:
  - A heading (h3) with the restaurant name.
  - Location info (e.g., "Disney's Polynesian Village Resort").
  - Price tier (e.g., "American|$$$$ (over $60 per adult)").
  - Meal headings (h4): "Breakfast", "Lunch", "Dinner".
  - Time slot buttons: `button "09:15 PM 'Ohana"` — the button name contains both the time and the restaurant name.
- **If a restaurant is not in the results, it has no availability.** There is no pagination — what's shown is all that's available.

### Checking Availability for a Specific Restaurant
1. Set party size (if not already correct).
2. Select the target date via the calendar.
3. Select the time filter (typically "All Day" for maximum coverage).
4. Grep the resulting snapshot for the restaurant name: `grep -A 20 -i "restaurant name"`.
5. If found, inspect the time slot buttons to see if any fall within constraints.
6. If not found (grep exit code 1), the restaurant has **no availability** for that date.

### Booking Flow
- Click a time slot button → you'll be taken to a reservation confirmation page.
- **HITL required** before clicking final "Confirm" or "Complete Booking" buttons.

---

## My Plans (Itinerary)

### Entry Point
- Accessible via the user menu → "My Plans" or the "My Disney Experience" section.
- The itinerary page is an SPA with **collapsed accordion sections per day**.

### Accordion Behavior (Critical)
- **By default, most days are collapsed** — only the current/next day may be open.
- The snapshot will only show reservation details for expanded days.
- **Recovery**: Use `browser_evaluate` to expand all days:
  ```js
  // Find all day-header buttons and click to expand
  document.querySelectorAll('button[aria-expanded="false"]').forEach(b => b.click());
  ```
- After expanding, wait 1–2 seconds and re-snapshot.
- Alternatively, use `browser_evaluate` to scrape `document.body.innerText` and parse the full text output.

### Reservation Details (per day)
When expanded, each reservation shows:
- Restaurant name
- Time
- Party size
- Confirmation number

### Quirks
- The `'Ohana` restaurant name starts with a typographic right single quotation mark (`'`), not a standard apostrophe. Use `-i` flag and be flexible with grep patterns.
- The `50's Prime Time Café` has both an apostrophe and an accent — use partial matches like `"Prime Time"` for reliability.

---

## General Disney SPA Behavior

- The site is a **heavy Single Page Application**. Any filter change, date selection, or navigation re-renders large portions of the DOM.
- **Always re-snapshot after any interaction** — refs are invalidated aggressively.
- Console errors are common (30+ errors per page load) — these are mostly analytics/tracking failures and do not indicate broken functionality.
- The site may occasionally prompt for login. If this happens, pause for HITL.
