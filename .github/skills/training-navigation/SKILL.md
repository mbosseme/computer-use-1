---
name: "Training navigation (vendor-agnostic)"
description: "Navigate web-based trainings that gate progress via timers/videos/disabled Next buttons."
tools:
  - playwright
---

## Preconditions
- User is signed in (or is ready to sign in when prompted).
- Training URL is provided in chat as session-only: `<TRAINING_URL>` (do not store in repo files).

## Wait & Progress Detection
- Prefer waiting for **observable UI state changes** over fixed sleeps.
- Prefer waiting for “Next/Continue” to become **visible and enabled**.
- Detect gating signals:
  - Disabled Next (`disabled`, `aria-disabled="true"`, or clearly non-clickable state)
  - Countdown timers (“You can continue in 00:30”)
  - “Must watch video” / “watch until the end” / completion-required messaging
  - Required acknowledgements/quizzes
- Use bounded polling loops instead of long blind sleeps:
  - Re-check every 10–20s, up to a maximum window (e.g., 5–15 minutes depending on the lesson).
  - Between polls, keep verifying the same landmark(s) (button enabled, timer reached 0, completion badge).
- Completion landmarks (examples):
  - Next/Continue enables
  - Timer reaches 0 then disappears/changes state
  - “Completed” badge/checkmark appears
  - Progress bar/stepper advances or % complete increases
  - "Certificate of Completion" page appears (strong signal to exit).

## Scrolling & Hidden Controls
- Differentiate **window scroll** vs **scrollable containers** (training shells often use an inner scroll region).
- Scan common regions for advance controls, then scroll in small increments:
  - Bottom of lesson content / footer action bar (often bottom-right)
  - Side navigation (TOC) “Next” control
  - Header controls (less common)
- After each scroll, re-scan for Next/Continue and for gating messages.

## Steps (with page landmarks)
1. **Open training**
   - Navigate to `<TRAINING_URL>`.
   - Identify primary page landmarks: header/nav, main content region, sidebar table-of-contents, and footer.

2. **Find the “advance” control**
   - Prefer role-based discovery:
     - Buttons/links labeled: “Next”, “Continue”, “Start”, “Resume”, “Proceed”.
   - If multiple, pick the one closest to the main content progression (often within the main region or at the bottom of the lesson).

3. **Detect gating (why you can’t advance yet)**
   - Check if the Next/Continue control is disabled.
   - Look for any of:
     - Countdown timer (“You can continue in 00:30”).
     - Video player requirement (“Watch until the end”).
     - Quiz/acknowledgement required.
     - Progress indicator not yet complete.

4. **Wait for completion signals (prefer explicit UI signals)**
   - Prefer waiting for one of:
     - Next/Continue button becomes enabled.
     - Timer reaches 0 and disappears or changes state.
     - “Completed” badge/checkmark appears for the current section.
     - Progress bar/stepper advances.
   - Avoid hard sleeps; only use bounded sleeps if there is no observable signal.

5. **Scroll/scan for hidden controls**
   - Determine scroll context:
     - If the page has an inner scroll container (common in training shells), scroll that container, not the window.
   - Use a “find in viewport” approach:
     - Scroll to the bottom of the content region to reveal bottom action bars.
     - Re-scan for Next/Continue controls after each scroll.

6. **Handle common blockers (recovery rules)**
  - Cookie banners: dismiss via clearly labeled “Accept/Reject” without changing optional preferences.
  - Overlays/modals: close via “Close”, “X”, or `Escape` when safe.
  - Popups/new tabs: if a link opens a new tab, switch to it only if required, then return.
  - Focus traps: tab/shift-tab to find actionable controls; close the dialog if it blocks progress.
  - Click intercepted:
    - Close the overlay, scroll the target into view, and retry once.
  - Quizzes/assessments:
    - If a question blocks progression, answer it and submit (don’t assume you can “Next” past it).
    - Prefer clicking the **label text** for a radio option (often more reliable than clicking the radio input).
  - Exit/close confirmations:
    - Content players often require a two-step exit (e.g., "Exit and Receive Credit" -> "Exit this course? [YES/NO]").
    - Treat the secondary confirmation (YES/Confirm) as an irreversible action.
    - Always ask for confirmation before clicking the final "YES" or "Confirm" in an exit dialog.

7. **Advance section-by-section**
   - After each advancement, verify you landed on a new section (title/step index changes).
   - Repeat gating detection and waits until the training is ready for the next advance.

## HITL points
- AUTH: If login/SSO/MFA/CAPTCHA appears, stop and ask the user to take over; resume only after “Done”.
- SAFE-CLICK POLICY: Before clicking **Complete / Submit / Attest / Finish** (or any irreversible action), ask the user for explicit confirmation immediately before the click.

## Final Gate
- Must ask Matt immediately before any **Complete / Submit / Attest / Finish** click (or anything that finalizes or records completion).

## Recovery rules
- If the Next button never enables:
  - Re-check for required interactions: play/unmute video, scroll to end, expand collapsed content, answer a prompt.
  - Look for inline validation errors or required checkboxes (e.g., “I acknowledge…”).
  - Refresh only if the app appears stuck and progress is preserved; warn user before refresh.

## When to stop and ask
- Any sign the next action will finalize/submit/attest/complete the course.
- Any ambiguous action that might change account state, submit answers, or record completion.
- Persistent blockers after reasonable recovery attempts.

## Validation landmarks
- Next/Continue advances to a new section (title/step changes).
- Current section shows a completion indicator (badge/checkmark) or progress advances.

## Field Notes from 3 real runs (platform-agnostic)
- **Menu Exits:** Some courses hide the exit button in a top-level hamburger menu (e.g., "Close") rather than placing it in the content footer.
- **Secondary Dialogs:** Clicking "Exit" often triggers a secondary "Are you sure?" dialog. Treat the *second* confirmation (YES/Confirm) as the irreversible action requiring HITL.
- **Quiz Logic:** For knowledge checks, selecting the radio button via its **label text** is more reliable than targeting the input directly. The pattern `Select -> Submit -> Continue` is standard.
- **Certificate Signal:** Reaching a "Certificate of Completion" page is a definitive signal that the course is done and it is safe to exit.
- **Video Gating:** Videos often gate the "Next" button. Bounded polling (checking every 10-20s) is effective for waiting out the duration.
