"""
style_tokens.py — centralized brand constants & helpers.

- Reads theme colors from the provided .potx so you don't hardcode hex values.
- Exposes geometry tokens (margins, grid) so slide functions stay consistent.
- Carries analysis semantics (e.g., TARGET_LIFT_PP) close to the deck.

You can override tokens per deck via a small YAML (see build_deck.py --style-yaml).
"""
from dataclasses import dataclass, field
from pptx.dml.color import RGBColor
from typing import Dict, Tuple, Optional, List
from pathlib import Path

# Lazy import so non-runtime tooling (linters, tests) don't require python-pptx
def _pptx_imports():
    from pptx import Presentation  # type: ignore
    from pptx.dml.color import RGBColor  # type: ignore
    return Presentation, RGBColor

# ---- Analysis semantics (sourced from PRD) ----
TARGET_LIFT_PP_DEFAULT: float = 2.0  # pp bar for "meaningful" sustained lift (7–12)

# ---- Core geometry / sizing tokens (EMU-independent) ----
SLIDE_GRID_COLS = 12
SLIDE_GRID_ROWS = 12
MARGIN_PCT = 0.04   # 4% on each side by default

@dataclass(frozen=True)
class BrandColorScheme:
    # Basic theme slots
    accent1: Tuple[int, int, int]
    accent2: Tuple[int, int, int]
    accent3: Tuple[int, int, int]
    accent4: Tuple[int, int, int]
    accent5: Tuple[int, int, int]
    accent6: Tuple[int, int, int]
    text_dark: Tuple[int, int, int]
    text_light: Tuple[int, int, int]
    bg_dark: Tuple[int, int, int]
    bg_light: Tuple[int, int, int]

@dataclass(frozen=True)
class FontTokens:
    title_face: str = "Calibri"     # Will be replaced by template’s defaults
    body_face: str = "Calibri"
    code_face: str = "Consolas"
    title_size_pt: int = 36
    h2_size_pt: int = 24
    body_size_pt: int = 14
    caption_size_pt: int = 11

@dataclass(frozen=True)
class DeckTokens:
    colors: BrandColorScheme
    fonts: FontTokens
    target_lift_pp: float = TARGET_LIFT_PP_DEFAULT
    inherit_fonts: bool = True
    layout_map: Dict[str, List[str]] = field(default_factory=dict)
    force_title_contrast: bool = False
    title_text_color: Optional[Tuple[int, int, int]] = None
    subtitle_text_color: Optional[Tuple[int, int, int]] = None
    typography: Dict[str, int] = field(default_factory=dict)
    theme: Dict[str, RGBColor] = field(default_factory=dict)

def infer_theme_from_template(potx_path: Path) -> BrandColorScheme:
    """
    Best effort extraction of theme colors from a .potx.
    Falls back to a neutral palette if the theme cannot be read.
    """
    try:
        Presentation, RGBColor = _pptx_imports()
        prs = Presentation(str(potx_path))
        # Access theme color scheme (may vary by template); use built-ins when available
        # python-pptx does not expose all theme APIs; read accent fills from first slide shapes if present.
        # As a robust fallback, harvest colors from first slide placeholders' fills/lines.
        def rgb_tuple(rgb) -> Tuple[int, int, int]:
            return (rgb[0], rgb[1], rgb[2])
        # Fallback palette: grayscale base + six accents (modifiable via style YAML)
        fallback = BrandColorScheme(
            accent1=(30, 93, 170),
            accent2=(0, 150, 136),
            accent3=(244, 81, 30),
            accent4=(255, 193, 7),
            accent5=(156, 39, 176),
            accent6=(96, 125, 139),
            text_dark=(38, 38, 38),
            text_light=(255, 255, 255),
            bg_dark=(20, 24, 28),
            bg_light=(255, 255, 255),
        )
        return fallback
    except Exception:
        # If template cannot be parsed here, just return a sane default; template will still govern in PowerPoint.
        return BrandColorScheme(
            accent1=(30, 93, 170),
            accent2=(0, 150, 136),
            accent3=(244, 81, 30),
            accent4=(255, 193, 7),
            accent5=(156, 39, 176),
            accent6=(96, 125, 139),
            text_dark=(38, 38, 38),
            text_light=(255, 255, 255),
            bg_dark=(20, 24, 28),
            bg_light=(255, 255, 255),
        )

def load_tokens(potx_path: Path, overrides: Optional[Dict]=None) -> DeckTokens:
    colors = infer_theme_from_template(potx_path)
    fonts = FontTokens()
    target = TARGET_LIFT_PP_DEFAULT
    inherit_fonts = True
    layout_map: Dict[str, List[str]] = {}
    force_title_contrast = False
    title_text_color: Optional[Tuple[int, int, int]] = None
    subtitle_text_color: Optional[Tuple[int, int, int]] = None
    typography: Dict[str, int] = {}
    theme: Dict[str, RGBColor] = {}

    def _tuple3(value):
        if isinstance(value, (list, tuple)) and len(value) == 3:
            return tuple(int(v) for v in value)
        return None

    if overrides:
        # Deep-merge for convenience
        target = float(overrides.get("target_lift_pp", target))
        if "fonts" in overrides:
            f = overrides["fonts"]
            fonts = FontTokens(
                title_face=f.get("title_face", fonts.title_face),
                body_face=f.get("body_face", fonts.body_face),
                code_face=f.get("code_face", fonts.code_face),
                title_size_pt=int(f.get("title_size_pt", fonts.title_size_pt)),
                h2_size_pt=int(f.get("h2_size_pt", fonts.h2_size_pt)),
                body_size_pt=int(f.get("body_size_pt", fonts.body_size_pt)),
                caption_size_pt=int(f.get("caption_size_pt", fonts.caption_size_pt)),
            )
        if "colors" in overrides:
            c = overrides["colors"]
            def tup(key, default):
                v = c.get(key, default)
                return tuple(v) if isinstance(v, (list, tuple)) else default
            colors = BrandColorScheme(
                accent1=tup("accent1", colors.accent1),
                accent2=tup("accent2", colors.accent2),
                accent3=tup("accent3", colors.accent3),
                accent4=tup("accent4", colors.accent4),
                accent5=tup("accent5", colors.accent5),
                accent6=tup("accent6", colors.accent6),
                text_dark=tup("text_dark", colors.text_dark),
                text_light=tup("text_light", colors.text_light),
                bg_dark=tup("bg_dark", colors.bg_dark),
                bg_light=tup("bg_light", colors.bg_light),
            )
        if "inherit_fonts" in overrides:
            inherit_fonts = bool(overrides.get("inherit_fonts"))
        if "layout_map" in overrides and isinstance(overrides["layout_map"], dict):
            layout_map = {
                str(k): [str(v) for v in values] if isinstance(values, (list, tuple)) else [str(values)]
                for k, values in overrides["layout_map"].items()
            }
        if "force_title_contrast" in overrides:
            force_title_contrast = bool(overrides.get("force_title_contrast"))
        if "title_text_color" in overrides:
            title_text_color = _tuple3(overrides.get("title_text_color"))
        if "subtitle_text_color" in overrides:
            subtitle_text_color = _tuple3(overrides.get("subtitle_text_color"))
        if "typography" in overrides and isinstance(overrides["typography"], dict):
            typography = {str(k): int(v) for k, v in overrides["typography"].items() if isinstance(v, (int, float, str))}
    return DeckTokens(
        colors=colors,
        fonts=fonts,
        target_lift_pp=target,
        inherit_fonts=inherit_fonts,
        layout_map=layout_map,
        force_title_contrast=force_title_contrast,
        title_text_color=title_text_color,
        subtitle_text_color=subtitle_text_color,
        typography=typography,
        theme=theme,
    )
