---
name: "Personal Shopping"
description: "Rules and workflows for commercial shopping tasks (add to cart, search, product selection, checkout)."
tools:
  - playwright
---

## Core Shopping Rules
1. **Strict Precision (No Substitutions)**:
   - If the user specifies a brand, model, size, or variant, you must find that **exact** item.
   - **Do not** substitute with a "similar" or "store brand" item without explicit user permission.
   - If the specific item is out of stock or not found, **STOP** and report it. Do not add a fallback item.

2. **Negative Reporting**:
   - If a search fails to find the requested item, explicitly report: "I looked for [Item], but could not find an exact match."
   - Detail what *was* found (e.g., "I found similar Brand Y, but not the Brand X you asked for") and ask for guidance.

3. **Cart Verification**:
   - After adding items, verify the cart summary ensures the correct item and quantity were registered.

## Search Strategy (Retail Specific)
- **Exact Terms**: Use the most specific keywords first (Brand + Product Name).
- **Facets first**: If generic terms return noise (e.g., "Microfiber cloth" returning "Lens wipes"), use the **Category/Department** filters immediately to narrow the domain (e.g., Filter usually -> "Household Essentials" or "Cleaning Supplies").
- **SKU Search**: If a SKU or ID is provided, search by that ID directly.

## Handling "Out of Stock"
- If an item is "Out of Stock" or "Pickup Only" (and we need shipping), note this status and ask the user. Do not assume store pickup is acceptable unless stated.

## Visual Verification
- Use `browser_snapshot` to read product titles and specs.
- If the text is ambiguous, use screenshots to verify "Count" (e.g. 8-pack vs single) or "Scent" nuances.
