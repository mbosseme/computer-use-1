"""Render the executive summary outline from deck variables using Jinja2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def _load_deck_vars(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def render_outline(
    deck_vars_path: Path,
    template_path: Path,
    output_path: Path,
    *,
    extra_context: Optional[Dict[str, Any]] = None,
) -> str:
    deck_vars = _load_deck_vars(deck_vars_path)
    template_dir = template_path.parent
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    template = env.get_template(template_path.name)

    context: Dict[str, Any] = {}
    context.update(deck_vars)
    if extra_context:
        context.update(extra_context)

    rendered = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return rendered
