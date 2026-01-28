# PPTX Generation Guide & Formatting Standards

**Last Updated:** 2026-01-28 (v7 Release)

This document outlines the strict formatting rules and layout strategies used in `src/pptx_builder/build_ge_deck.py` to ensure consistent, professional output without layout collisions.

## 1. Core Layout Strategy: "Main Content" Only

To avoid the unpredictable behavior of complex multi-column layouts (like "Two Content"), we exclusively use the **"Premier Main Content 1a"** layout (internal name: `MAIN_CONTENT` in `LAYOUT_MAP`) for all content slides.

*   **Why:** Complex layouts often have placeholders that auto-resize or shift unexpectedly. The "Main Content" layout provides a simple Title area and a large Body area that we can treat as a "canvas".
*   **Implementation:** 
    ```python
    preferred = LAYOUT_MAP["MAIN_CONTENT"]
    layout = find_layout(prs, ["Main", "Content"], 1, preferred_names=preferred, layout_key="MAIN_CONTENT")
    ```

## 2. Absolute Positioning (The "Safe Zones")

Visual collisions between titles and content are prevented by strictly enforcing vertical zones. We do **not** rely on PowerPoint's automatic text flow.

*   **Title Zone:** Top 0.0" to 1.3"
    *   The title placeholder generally ends around `1.21"`.
*   **Content Zone:** Top >= 1.4"
    *   **Charts/Images:** Position at `top = Inches(1.4)`.
    *   **Tables:** Position at `top = Inches(1.65)` (extra buffer for potential 2-line titles).
    *   **Text Boxes:** Position at `top = Inches(1.4)` or lower.

**Critical Rule:** Any script modification adding new content types *must* check that `shape.top` is at least `1.4 inches`.

## 3. Font Sizes

*   **Slide Titles:** **32 pt** (Enforced)
    *   Default templates often use 40-44pt, which is too large for long titles (e.g., "Market Trends - Magnetic Resonance Imaging (MRI)").
    *   We use a helper function `_set_title(slide, text, font_size_pt=32)` to enforce this.
*   **Body Text:**
    *   Bullets: 18pt (Level 0), 16pt (Level 1).
    *   Tables: 10pt (Headers), 10pt (Cells).
    *   Footers/Notes: 10pt (Grey).

## 4. The "Nuclear Option" for Custom Layouts

For slides that require custom positioning (like the "Seasonality comparison" or "Charity Presence" tables), we often remove the default body placeholder entirely to prevent it from showing up as an empty text box or interfering with our custom shapes.

```python
# Example: Clearing default placeholders
for shape in list(slide.shapes):
    if shape.is_placeholder and shape != slide.shapes.title:
        # remove shape...
```

## 5. Verification

A programmatic check script (e.g., `check_v7.py`) can be used to assert these rules by iterating through shapes and checking `shape.top > title.bottom`.

## 6. Slide-Specific Coordinates

| Slide Type | Layout | Content Top | Notes |
| :--- | :--- | :--- | :--- |
| **Market Trend Charts** | MAIN_CONTENT | 1.40" | Large visual; needs max height. |
| **Data Validation Tables** | MAIN_CONTENT | 1.80" | Tables often have headers that need space. |
| **Charity Tables** | MAIN_CONTENT | 1.65" | Accommodates 2-line titles ("...Charity request"). |
| **Text Bullets** | MAIN_CONTENT | Placeholder | Uses standard placeholder positioning. |

---

**Maintenance Note:** If the branded template (`brand/Premier-FY25-PPT...`) changes, these coordinates may need recalibration. Use the `pdf2image` + `check_layout.py` workflow to validate.
