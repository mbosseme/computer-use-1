# PowerPoint Iteration Workflow (Repository Operating Narrative)

This document explains how we have been iteratively building and refining the
PowerPoint presentation in this repository. It is written for a reader with no
prior context and describes the key inputs, tooling, technical approach, and
interaction pattern used across working sessions.

## 1) Goal and guiding principles

The objective is to refine an existing source deck into a brand-compliant,
polished presentation using deterministic, code-driven edits. The source deck is
never modified in place. Each run produces a new output PPTX (and optional PDF
and PNG renders) so changes are repeatable and auditable.

Guiding principles:
- Treat the source deck as immutable input.
- Make targeted, deterministic edits (text, geometry, alignment) rather than
  broad redesigns unless explicitly requested.
- Prefer direct, automatable updates; warn or block when elements are not safely
  editable (e.g., SmartArt or charts).
- Keep the loop repeatable and transparent: inspect, plan, apply, render, review.

## 2) Key inputs and reference resources

Source and requirements:
- `Premier_Evolution_Chunk1_Updated.pptx` is the immutable source deck.
- `CHANGE_REQUESTS.md` is the authoritative list of requested changes for each
  iteration. It is updated over time and drives the edit plan.

Brand references (read-only):
- `brand/Premier-FY25-PPT 16x9-Feb25.potx` (template reference).
- `brand/Premier-SlideStyleGuide-Feb25.pdf` (style guide).
- `brand/Premier-SlideStyleGuide-Feb25.pptx` (style guide deck).

Generated artifacts:
- `edits/edits.yaml` is the edit plan (deterministic ops in a strict schema).
- `build/shape_index.json` indexes slide shapes and geometry for targeting.
- `out/deck_latest.pptx` is the latest rendered output deck.
- `out/deck_latest.pdf` is a PDF export of the latest deck when requested.
- `out/png/...` are optional PNG renders for visual QA (when conversion is
  available).

## 3) Tooling and technical approach

We use Python and `python-pptx` to manipulate the PPTX file in a fully code-
controlled, repeatable way. The pipeline is organized into scripts under
`scripts/`.

Core scripts:
- `scripts/inspect_deck.py`
  - Reads a PPTX and produces `build/shape_index.json` plus a terminal report.
  - Enumerates slides and shapes with names, types, geometry, and text previews.
  - Helps identify stable targets for edits (shape names are critical).

- `scripts/build_from_change_requests.py`
  - Parses `CHANGE_REQUESTS.md` into a machine-readable checklist and a starter
    `edits/edits.yaml` skeleton.
  - Avoids guessing: extracts explicit slide numbers, required changes, and
    acceptance signals.

- `scripts/apply_edits.py`
  - Applies operations from `edits/edits.yaml` to the input deck, then writes a
    new output deck. The input deck is never modified.
  - Supports deterministic operations such as:
    - `rename_shape`
    - `replace_text`
    - `set_text` (preserving formatting when possible)
    - `set_geometry`
    - `set_text_frame` (auto-size, wrap, margins)
    - `set_font_size`
    - `set_fill`
    - `align` and `distribute`
    - `add_shape` / `add_textbox`
    - `delete_shape` / `delete_slide`
    - `clone_slide` (for inserting a new slide based on an existing one)
    - `swap_line_ends` (fix arrow direction)
    - `fix_footer_logo` (post-process background media to move clipped logos)
  - Includes safeguards:
    - Warns on missing targets.
    - Skips unsafe elements (e.g., groups/charts) unless explicitly handled.
    - Normalizes negative extents to avoid PowerPoint repair errors.

- `scripts/render_slides.py`
  - Renders slides to PNG for QA:
    - On Windows: uses PowerPoint COM if available.
    - Else: uses LibreOffice headless if available.
    - Else: prints clear instructions and exits gracefully.

- `scripts/qa_critic.py` (optional)
  - Uses OpenAI API to propose a patch in the same edits schema for
    layout/wording improvements.
  - Produces `build/qa_suggestions.yaml` but never auto-applies it.

- `scripts/run_iteration.py`
  - Orchestrates the iteration loop: apply edits, create a timestamped output,
    render PNGs, optionally run QA, and print a change status report.

Dependencies:
- Minimal set via `requirements.txt`: `python-pptx`, `pyyaml`, `Pillow`, plus
  optional `pypdf` and `openai` for advanced steps.

## 4) The iteration loop and interaction pattern

The working pattern between the user and the agent follows a structured loop:

1) Inspect
   - Run `inspect_deck.py` to map shapes and geometry.
   - Use `build/shape_index.json` to identify which shapes correspond to
     requested changes.

2) Translate change requests into operations
   - Read `CHANGE_REQUESTS.md` carefully.
   - Update `edits/edits.yaml` with precise operations targeting known shapes.
   - Avoid guessing; if a request is ambiguous, call it out before proceeding.

3) Apply edits
   - Run `apply_edits.py` to create a new output PPTX.
   - Ensure all operations are deterministic and logged.

4) Render for QA (optional but preferred)
   - Run `render_slides.py` to produce PNGs for visual inspection.
   - When PNG rendering is limited, export a PDF for a closer view.

5) Review and refine
   - The user reviews output in PowerPoint or via PDF/PNGs.
   - New or corrected requests are added to `CHANGE_REQUESTS.md`.
   - The cycle repeats with incremental edits rather than sweeping changes.

This loop supports iterative collaboration: the user updates requirements, the
agent applies targeted edits, and the output is reviewed, adjusted, and refined.

## 5) Handling special cases and known limitations

- Slide Master edits: In this deck, the master layout contained no shapes, so
  logo/footer clipping appeared baked into the background images instead of
  editable master shapes. To resolve this, a post-process step was added to move
  the logo region inside the background media. This is implemented via
  `fix_footer_logo` in `apply_edits.py`.

- Unsafe elements: Groups, charts, or SmartArt are treated as potentially
  unsafe. The system warns and skips these unless a safe fallback is provided
  (e.g., leave as-is or replace with an image).

- Formatting preservation: `set_text` attempts to preserve formatting by
  manipulating XML runs where possible. If not possible, formatting may be
  reset and the script warns.

- Rendering: The environment supports LibreOffice conversion when available.
  When it is not available, rendering does not block the iteration; it simply
  provides instructions for enabling it.

## 6) Practical example of a typical iteration

A typical iteration has looked like this:

- `CHANGE_REQUESTS.md` is updated with a list of slide-by-slide changes.
- `edits/edits.yaml` is revised to:
  - Update slide titles and body text.
  - Adjust shape sizes, alignment, and spacing.
  - Insert a new slide using `clone_slide` where needed.
  - Swap arrow direction and fix text wrapping issues.
- `apply_edits.py` writes a new `out/deck_latest.pptx`.
- `render_slides.py` generates PNGs or a PDF is exported for visual review.
- The user reviews and posts a new change request list, iterating the cycle.

## 7) Where to look for key files

- Source deck: `Premier_Evolution_Chunk1_Updated.pptx`
- Requirements: `CHANGE_REQUESTS.md`
- Edit plan: `edits/edits.yaml`
- Scripts: `scripts/`
- Output deck: `out/deck_latest.pptx`
- Optional PDF: `out/deck_latest.pdf`
- Shape index: `build/shape_index.json`

## 8) Summary

We are using a deterministic, code-first pipeline to refine a PowerPoint deck
iteratively. The user supplies updated change requests, the agent translates
those into explicit operations in `edits.yaml`, then the pipeline applies the
changes to produce a new output PPTX (and optional PDF/PNG renders). The approach
prioritizes repeatability, auditability, and brand compliance while respecting
constraints around unsafe elements and the immutable source deck.
