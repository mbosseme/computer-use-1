---
name: "Training navigation (vendor-agnostic)"
description: "Navigate web-based trainings that gate progress via timers/videos/disabled Next buttons."
tools:
  - playwright
---

## Preconditions
- User is signed in (or is ready to sign in when prompted).
- Training URL is provided in chat as session-only: `<TRAINING_URL>` (do not store in repo files).

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
   - Focus traps: tab/shift-tab to find actionable controls; close the dialog if it blocks progress.
   - Popups/new tabs: if a link opens a new tab, switch to it only if required, then return.

7. **Advance section-by-section**
   - After each advancement, verify you landed on a new section (title/step index changes).
   - Repeat gating detection and waits until the training is ready for the next advance.

## HITL points
- AUTH: If login/SSO/MFA/CAPTCHA appears, stop and ask the user to take over; resume only after “Done”.
- SAFE-CLICK POLICY: Before clicking **Complete / Submit / Attest / Finish** (or any irreversible action), ask the user for explicit confirmation immediately before the click.

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
