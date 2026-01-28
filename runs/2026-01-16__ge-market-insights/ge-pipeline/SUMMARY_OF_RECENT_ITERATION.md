# Summary of Recent Iterations

## 2026-01-28: Fix PPTX Layout Collisions (v7)
- **Intent:** Resolve overlapping text/title issues and inconsistent layouts in the automated deck generation.
- **Files Touched:** 
  - `src/pptx_builder/build_ge_deck.py` (Layout logic, positioning, font sizes)
  - `docs/PPTX_GENERATION_GUIDE.md` (New documentation)
  - `README.md` (Link improvements)
- **Changes:**
  - **Universal Layout:** Switched all content slides to use `MAIN_CONTENT` (Premier Main Content 1a) to simplify placeholder behavior.
  - **Safe Zones:** Enforced absolute positioning for charts and tables (`top >= 1.4"`) to clear the title area.
  - **Font Sizing:** Explicitly reduced slide titles to **32pt** (down from default ~44pt) using a new `_set_title` helper.
  - **Charity Tables:** Adjusted top margin to `1.65"` to accommodate multi-line titles.
- **Outcome:** 
  - Generated `snapshots/.../GE_PILOT_Validation_v7.pdf`.
  - Visual verification (via slide gallery) confirms positive gaps on all slides (no collisions).
  - Programmatic verification (`check_v7.py`) confirms all gaps > 0.1".
