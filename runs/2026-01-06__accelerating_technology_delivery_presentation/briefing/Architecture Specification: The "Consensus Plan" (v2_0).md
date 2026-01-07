This document is written directly for the **GitHub Copilot Agent** operating in your VS Code environment. It serves as the authoritative specification for refactoring the existing `premier-evolution` repository from its legacy "blind generation" state to the new **"Consensus Plan" Architecture**.

---

# Architecture Specification: The "Consensus Plan" (v2.0)

**Target System:** Automated PowerPoint Generation Pipeline (macOS/Python)
**Primary Objective:** Transition from "Open-Loop Generation" (blind code execution) to a **"Safe-Fail" Agentic Loop** that separates generation, verification, and design.

## 1. Executive Summary & Design Philosophy

**Current State (Legacy):** The pipeline writes code to generate slides from scratch. It relies on `python-pptx` to estimate layout.

* *Failure Mode:* "Blind Painter." The agent cannot see if text overflows or overlaps because it lacks a rendering feedback loop.
* *Constraint:* Generating complex visuals via code is fragile and aesthetically poor.

**Target State (Consensus Plan):** The pipeline assumes the code is likely wrong and requires verification. It implements a three-stage quality gate:

1. **Gate 1 (Math):** A deterministic **Geometry Linter** rejects gross errors (collisions, bounds) instantly.
2. **Gate 2 (Vision):** A **Visual Critic** (Azure OpenAI GPT-5.2) views a high-fidelity render to catch aesthetic/brand defects.
3. **Design Strategy:** The agent shifts from "Drawing" (creating shapes) to "Assembling" (cloning pre-validated components).

## 2. System Architecture Diff

| Component | Legacy (`v1`) | Target (`v2` - Consensus Plan) |
| --- | --- | --- |
| **Orchestrator** | `run_iteration.py` (Linear) | `run_consensus_loop.py` (Recursive: Plan  Lint  Render  Critique  Fix) |
| **Layout Logic** | `apply_edits.py` (Guesswork) | **Component Library** (Clone & Fill strategy) |
| **Validation** | User Review (Manual) | **Geometry Linter** (Auto-fail) + **Visual Critic** (Auto-patch) |
| **Rendering** | LibreOffice/COM (Fragile) | **AppleScript/OSAScript** (Native macOS PowerPoint control) |
| **AI Model** | Text-only Logic | **Azure OpenAI GPT-5.2** (Multimodal Vision + Set-of-Mark Prompting) |

---

## 3. Core Technical Pillars

### Pillar 1: The Geometry Linter (Gate 1)

**Goal:** Catch 80% of errors (overflows, collisions) deterministically before paying for LLM tokens.
**New File:** `scripts/lint_layout.py`
**Key Dependencies:** `shapely`, `rtree`

**Implementation Rules:**

1. **Shape abstraction:** Convert every visible shape in the slide into a `shapely.geometry.Polygon`.
2. **The "No-Fly Zone":** Define a bounding box for the **Header** and **Footer**. If any `Body` content intersects this zone, return `CRITICAL_FAIL`.
3. **Collision Logic:**
* Iterate through all content shapes.
* If `shape_A.intersects(shape_B)` is `True` AND `z_order` does not imply background/foreground layering: Flag as `COLLISION`.


4. **Overflow Heuristic:**
* Calculate `text_volume = char_count * avg_char_area`.
* If `text_volume > shape_area`, flag as `POTENTIAL_OVERFLOW`.



### Pillar 2: "Truthful" Rendering (macOS)

**Goal:** Generate a PNG that matches *exactly* what the user sees. The Visual Critic is useless without this.
**New Logic in:** `scripts/render_slides.py`
**Constraint:** Host OS is macOS. Windows COM is unavailable. LibreOffice is banned due to font inaccuracies.

**Reference Implementation (AppleScript):**
The agent must use Python's `subprocess` to execute this JXA/AppleScript. This controls the locally installed "Microsoft PowerPoint.app".

```applescript
-- Reference AppleScript for VS Code Agent
on run {pptxPath, outputFolder}
    tell application "Microsoft PowerPoint"
        open pptxPath
        set thePres to the active presentation
        -- Export simply saves every slide as PNG in the target folder
        export thePres to outputFolder as slide images with properties {image format: PNG, scale width: 1920, scale height: 1080}
        close thePres saving no
    end tell
end run

```

### Pillar 3: The Visual Critic (Gate 2)

**Goal:** Catch aesthetic errors (bad alignment, awkward line breaks, brand inconsistency).
**New File:** `scripts/qa_vision.py`
**Model:** Azure OpenAI GPT-5.2 (via Azure OpenAI Responses API).

**The "Set-of-Mark" Strategy (Crucial):**

1. **Pre-processing:** Before sending the PNG to GPT-5.2, use `PIL` (Python Imaging Library) to draw a semi-transparent bounding box with a **unique ID** over every element in the `shape_index.json`.
2. **Prompt Engineering:**
* *Do not ask:* "Does this look good?"
* *Do ask:* "Inspect the image. Element `ID_5` (Title) appears to be touching Element `ID_9` (Logo). Calculate the `dy` (vertical shift) required to fix this in inches."


3. **Coordinate Space:** Instruct GPT-5.2 to output coordinates in **Normalized 1000-space** (0-1000).
* *Example:* "Move ID_5 `y` from 50 to 150."
* *Agent Action:* Convert 100/1000 to slide height (e.g., 10% of 7.5 inches) and apply the edit.



### Pillar 4: The Component Library ("Fill, Don't Build")

**Goal:** Stop "drawing" ugly charts. Start "cloning" beautiful ones.
**Asset:** `assets/Premier_Components.pptx` (You must create or designate this file).

**Workflow:**

1. **Inventory:** The agent indexes this deck. Slide 1 = "3-Col List", Slide 2 = "Big Stat", Slide 3 = "Bar Chart".
2. **Selection:** When `CHANGE_REQUESTS.md` asks for "Financial Overview", the agent selects Slide 3.
3. **Action:**
* Legacy: `slide.shapes.add_chart(...)` (Fragile).
* Consensus: `deck.slides.add_slide(component_slide_layout)` OR `clone_slide(source=3)`.
* Then: `shape.text = "New Data"`.



---

## 4. Implementation Roadmap for VS Code Agent

### Phase 1: Infrastructure & "Truth" (Days 1-2)

* [ ] **Dependencies:** Add `shapely`, `rtree`, `pillow` (requests is in core) to `requirements.txt`.
* [ ] **Renderer:** Refactor `render_slides.py` to drop LibreOffice support and implement the macOS AppleScript logic. Verify it produces HD PNGs.
* [ ] **Linter:** Create `lint_layout.py`. Implement simple bounds checking (off-slide detection).

### Phase 2: The Visual Critic (Days 3-4)

* [ ] **SoM Overlay:** Create a helper function `draw_overlays(image_path, shape_index)` that draws red boxes + IDs on the render.
* [ ] **Vision Client:** Create `qa_vision.py`. Connect to Azure OpenAI GPT-5.2. Pass the SoM image.
* [ ] **Patch Loop:** Define a JSON schema for "Visual Fixes" (e.g., `{ "op": "move", "id": "Title 1", "dy": 0.5 }`).

### Phase 3: The Component Switch (Day 5+)

* [ ] **Library Setup:** Create a dummy `Premier_Components.pptx` with 3 standard layouts.
* [ ] **Logic Update:** Modify `build_from_change_requests.py` to prioritize `clone_slide` operations over `add_shape`.

---

## 5. Reference: The "Safe-Fail" Loop Logic

**Pseudocode for `run_consensus_loop.py`:**

```python
def run_loop(change_requests):
    # 1. PLAN & EXECUTE (Existing Logic)
    edits = plan_edits(change_requests)
    apply_edits(edits) # Modifies deck_latest.pptx

    # 2. GATE 1: GEOMETRY LINTER (New)
    lint_report = lint_layout("deck_latest.pptx")
    if lint_report.has_critical_errors:
        print("Linter Fail:", lint_report.errors)
        # Auto-generate fixes for overlaps/overflows
        apply_edits(lint_report.fixes)
        return "RETRY_NEEDED"

    # 3. RENDER (Mac Native)
    # Renders deck_latest.pptx -> /out/pngs/slide_01.png
    render_slides_mac("deck_latest.pptx")

    # 4. GATE 2: VISUAL CRITIC (Azure OpenAI GPT-5.2)
    # Overlays bounding boxes on PNGs
    som_image = overlay_shapes("slide_01.png", "shape_index.json")
    
    critique = gpt5_2_vision.review(som_image)
    if critique.has_defects:
        print("Visual Critic Fail:", critique.patches)
        apply_edits(critique.patches)
        return "RETRY_NEEDED"

    print("Consensus Achieved. Deck ready.")

```

**End of Specification**