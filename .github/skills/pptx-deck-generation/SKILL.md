# Skill: PowerPoint Deck Generation

This skill covers patterns for programmatically generating branded PowerPoint presentations using `python-pptx`, including chart insertion, template handling, and PDF export.

## 1. Context & Use Cases

**Trigger:** User requests to:
- Generate a PowerPoint deck from data (CSVs, DataFrames, charts)
- Apply corporate branding/templates to slides
- Build executive summaries with KPI visualizations
- Export presentations to PDF

**Tools:**
- `python-pptx` — Core library for PPTX manipulation
- `matplotlib`/`seaborn` — Chart generation (saved as PNG, inserted into slides)
- `soffice` (LibreOffice) — PDF export and template conversion

## 2. Template Handling

### 2.1 Corporate Templates (.potx)

Corporate templates are often distributed as `.potx` (PowerPoint Template) files. `python-pptx` can open these, but sometimes requires conversion.

**Conversion pattern (change content type):**
```python
import zipfile
from pathlib import Path

def convert_potx_to_pptx(src_path: Path, dst_path: Path) -> Path:
    """Convert .potx to .pptx by rewriting the content type."""
    old_type = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"
    new_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"

    with zipfile.ZipFile(src_path, "r") as zin:
        with zipfile.ZipFile(dst_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    text = text.replace(old_type, new_type)
                    data = text.encode("utf-8")
                zout.writestr(info, data)
    return dst_path
```

### 2.2 Template Location

Store templates in `templates/` at repo root for reusability:
```
templates/
├── Premier_Standard_Legal.dotx    # Word template
└── Premier_FY25_16x9.potx         # PowerPoint template
```

Or in run-local folders for project-specific templates:
```
runs/<RUN_ID>/ge-pipeline/brand/
└── Premier-FY25-PPT 16x9-Feb25.potx
```

## 3. Slide Creation Patterns

### 3.1 Remove Existing Slides (Start Fresh)

```python
from pptx import Presentation

def remove_all_slides(prs: Presentation) -> None:
    """Remove all slides from presentation."""
    for i in range(len(prs.slides) - 1, -1, -1):
        rId = prs.slides._sldIdLst[i].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[i]
```

### 3.2 Find Layouts by Name

```python
def find_layout(prs: Presentation, layout_names: list[str]):
    """Find first matching layout by name."""
    for layout in prs.slide_layouts:
        if layout.name in layout_names:
            return layout
    # Fallback to first layout
    return prs.slide_layouts[0]

# Common layout names (vary by template)
LAYOUT_MAP = {
    "TITLE": ["Premier Title Dark", "Title Slide"],
    "TITLE_CONTENT": ["Title and Content", "Premier Two Content"],
    "SECTION": ["Section Header", "Premier Section"],
    "BLANK": ["Blank"],
}
```

### 3.3 Clear Placeholder Shapes (Avoid Layout Collisions)

When adding custom content to a slide, template placeholders (subtitle, body, etc.) can create visual collisions. Clear them before adding custom shapes:

```python
def clear_placeholder_shapes(slide, keep_title: bool = True):
    """Remove placeholder shapes that would conflict with custom content.
    
    This is CRITICAL when adding tables, charts, or textboxes to slides
    with pre-existing placeholder text like 'Click to add subtitle'.
    """
    # Find subtitle if present (to preserve if needed)
    subtitle = None
    for shape in slide.placeholders:
        if shape.name.lower().find("subtitle") >= 0:
            subtitle = shape
            break

    for shape in list(slide.shapes):
        if not shape.is_placeholder:
            continue
        # Always keep the title
        if keep_title and shape == slide.shapes.title:
            continue
        # Optionally keep subtitle
        if subtitle is not None and shape == subtitle:
            continue
        # Clear text first (if present)
        if shape.has_text_frame:
            try:
                shape.text_frame.clear()
            except Exception:
                pass
        # Remove from XML
        try:
            shape.element.getparent().remove(shape.element)
        except Exception:
            # Fallback: move off-slide if XML removal fails
            try:
                from pptx.util import Inches
                shape.left = Inches(20)  # Push off visible area
            except Exception:
                pass
```

**When to use:**
- Adding custom textboxes or tables that overlap with body placeholder area
- Chart-only slides where body text would conflict
- Two-column layouts where placeholder doesn't match your design

### 3.4 Normalized Positioning

Use normalized (0-1) coordinates for consistent placement across slide sizes:

```python
from pptx.util import Pt

EMU_PER_INCH = 914400

def place_normalized(slide, x: float, y: float, w: float, h: float):
    """Add textbox using normalized (0..1) coords."""
    presentation = slide.part.package.presentation_part.presentation
    sw, sh = presentation.slide_width, presentation.slide_height
    left = int(sw * x)
    top = int(sh * y)
    width = int(sw * w)
    height = int(sh * h)
    return slide.shapes.add_textbox(left, top, width, height)
```

### 3.4 Insert Images (Charts)

```python
def add_picture_fit(slide, image_path: str, x: float, y: float, w: float, h: float):
    """Insert image at normalized position."""
    presentation = slide.part.package.presentation_part.presentation
    sw, sh = presentation.slide_width, presentation.slide_height
    left, top = int(sw * x), int(sh * y)
    width, height = int(sw * w), int(sh * h)
    return slide.shapes.add_picture(image_path, left, top, width=width, height=height)
```

## 4. Chart Generation Patterns

### 4.1 Executive-Style Charts (seaborn/matplotlib)

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def generate_market_share_chart(df: pd.DataFrame, output_path: Path) -> None:
    """Generate a stacked bar chart for market share."""
    # Consistent manufacturer colors across all charts
    COLORS = {
        "GE": "#1f77b4",
        "SIEMENS": "#ff7f0e",
        "PHILIPS": "#2ca02c",
        "CANON": "#d62728",
        "OTHER": "#9467bd",
    }
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    # ... chart logic ...
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

### 4.2 Chart Naming Convention

Use descriptive names with prefixes for organization:
```
visuals/
├── exec_modality_trend.png        # Executive summary
├── exec_share_latest_quarter.png
├── qa_spend_vs_transactions.png   # QA/validation
└── market_trend_ct.png            # Category-specific
```

## 5. Slide Content Patterns

### 5.1 Big Number KPIs

```python
def add_kpi_card(slide, value: str, label: str, x: float, y: float):
    """Add a KPI card (big number + label)."""
    box = place_normalized(slide, x, y, 0.25, 0.20)
    tf = box.text_frame
    tf.clear()
    
    # Value (big, bold)
    p1 = tf.paragraphs[0]
    p1.text = value
    p1.font.size = Pt(48)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(0, 82, 147)  # Premier Blue
    
    # Label (smaller)
    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(14)
```

### 5.2 Data Tables

```python
from pptx.util import Inches

def add_data_table(slide, df: pd.DataFrame, x: float, y: float, w: float, h: float):
    """Insert a DataFrame as a table."""
    presentation = slide.part.package.presentation_part.presentation
    sw, sh = presentation.slide_width, presentation.slide_height
    
    rows, cols = df.shape
    table = slide.shapes.add_table(
        rows + 1,  # +1 for header
        cols,
        int(sw * x), int(sh * y),
        int(sw * w), int(sh * h)
    ).table
    
    # Header row
    for j, col in enumerate(df.columns):
        table.cell(0, j).text = str(col)
    
    # Data rows
    for i, row in df.iterrows():
        for j, val in enumerate(row):
            table.cell(i + 1, j).text = str(val)
    
    return table
```

## 6. PDF Export

### 6.1 Using LibreOffice (soffice)

```python
import subprocess
from pathlib import Path

def export_to_pdf(pptx_path: Path, output_dir: Path) -> Path:
    """Convert PPTX to PDF using LibreOffice."""
    cmd = [
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_dir),
        str(pptx_path)
    ]
    subprocess.run(cmd, check=True)
    return output_dir / f"{pptx_path.stem}.pdf"
```

**Prerequisite:** LibreOffice must be installed:
```bash
# macOS
brew install --cask libreoffice

# Ubuntu
sudo apt install libreoffice
```

## 7. Deck Builder Architecture

For complex decks, use a modular builder pattern:

```
src/pptx_builder/
├── __init__.py
├── build_deck.py      # Main entry point
├── helpers.py         # Positioning, text formatting
├── layouts.py         # Layout discovery
├── slides.py          # Slide creation functions
├── charts_fallback.py # Chart generation helpers
└── style_tokens.py    # Colors, fonts, theme extraction
```

**Usage pattern:**
```python
def build_deck(snapshot_dir: Path, template_path: Path, output_path: Path):
    # 1. Load template
    template = ensure_pptx_template(template_path, snapshot_dir)
    prs = Presentation(template)
    
    # 2. Clear existing slides
    remove_all_slides(prs)
    
    # 3. Add slides in order
    add_title_slide(prs, "Market Insights Report", "Q4 2025")
    add_section_slide(prs, "Market Trends")
    add_chart_slide(prs, snapshot_dir / "visuals/exec_trend.png", "Spend by Category")
    # ...
    
    # 4. Save
    prs.save(output_path)
    
    # 5. Export PDF
    export_to_pdf(output_path, snapshot_dir)
```

## 8. Recovery Rules

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| `KeyError: "no style named 'Title'"` | Template missing expected styles | Use layout discovery; fall back to first available |
| Template changes fail silently | `.potx` content type not converted | Use `convert_potx_to_pptx()` helper |
| Charts look pixelated | Low DPI export | Use `dpi=300` in `plt.savefig()` |
| Slides appear blank | Shapes added at wrong position | Use normalized positioning with slide dimensions |
| PDF export fails | LibreOffice not installed or hung process | Install soffice; use `--headless` flag |
| Template placeholder text shows behind custom content | Layout placeholders not cleared | Use `clear_placeholder_shapes(slide)` before adding custom content (§3.3) |
| `NameError: name 'subtitle' is not defined` | Forgot to find subtitle placeholder before clearing loop | Initialize `subtitle = None`, then search `slide.placeholders` before the clearing loop |

## 9. Reference Implementation

See `runs/2026-01-16__ge-market-insights/ge-pipeline/` for:
- `src/pptx_builder/` — Complete deck builder with theming
- `scripts/generate_capital_visuals.py` — Chart generation patterns
- `scripts/run_full_pipeline.py` — End-to-end pipeline with PDF export
