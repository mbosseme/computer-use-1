"""
layouts.py — helpers to resolve slide layouts and placeholders by (fuzzy) name.

Why: brand .potx files often rename layouts; strict indexing is brittle.
"""
from typing import Optional, List, Dict
from dataclasses import dataclass

_NON_BLANK_KEYS = {"TITLE", "TITLE_CONTENT", "MAIN_CONTENT", "SECTION", "TWO_CONTENT"}


def _is_blank_layout(name: Optional[str]) -> bool:
    return bool(name) and "blank" in name.lower()


def find_layout(
    prs,
    name_fragments: List[str],
    fallback_index: int = 0,
    preferred_names: Optional[List[str]] = None,
    layout_key: Optional[str] = None,
):
    """
    Return the first layout whose name contains ALL fragments (case-insensitive).
    Falls back to index if no match.
    """
    forbid_blank = layout_key in _NON_BLANK_KEYS if layout_key else False

    def acceptable(layout) -> bool:
        return not (forbid_blank and _is_blank_layout(layout.name))

    preferred_lower = [name.lower() for name in preferred_names] if preferred_names else []
    tentative = None
    if preferred_lower:
        for layout in prs.slide_master.slide_layouts:
            nm = (layout.name or "").lower()
            if nm in preferred_lower:
                if acceptable(layout):
                    return layout
                if tentative is None:
                    tentative = layout
    if preferred_names:
        # If we only matched blank layouts, continue searching by fragments but remember tentative.
        pass
    frags = [f.lower() for f in name_fragments]
    for layout in prs.slide_master.slide_layouts:
        nm = (layout.name or "").lower()
        if all(f in nm for f in frags):
            if acceptable(layout):
                return layout
            if tentative is None:
                tentative = layout
    if tentative is not None and acceptable(tentative):
        return tentative
    if tentative is not None and not acceptable(tentative):
        for layout in prs.slide_master.slide_layouts:
            if acceptable(layout):
                return layout
    fallback_layout = prs.slide_layouts[fallback_index]
    if acceptable(fallback_layout):
        return fallback_layout
    for layout in prs.slide_master.slide_layouts:
        if acceptable(layout):
            return layout
    return fallback_layout

@dataclass(frozen=True)
class LayoutKeys:
    title: List[str] = ("title",)
    title_content: List[str] = ("title", "content")
    section_header: List[str] = ("section", "header")
    two_content: List[str] = ("two", "content")
    big_number: List[str] = ("big", "number")
    blank: List[str] = ("blank",)

DEFAULT_LAYOUT_MAP: Dict[str, List[str]] = {
    "TITLE": ["title"],
    "TITLE_CONTENT": ["title", "content"],
    "SECTION": ["section", "header"],
    "TWO_CONTENT": ["two", "content"],
    "BIG_NUMBER": ["big", "number"],
    "BLANK": ["blank"],
}
