"""Pipeline step to render the executive summary outline from deck_vars.json."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from ..runner.orchestrator import RunContext
from ..templates import render_outline as render_outline_fn


def _outline_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    reports_cfg = cfg.get("reports") if isinstance(cfg, dict) else {}
    if not isinstance(reports_cfg, dict):
        return {}
    outline_cfg = reports_cfg.get("outline", {}) or {}
    return outline_cfg if isinstance(outline_cfg, dict) else {}


@dataclass
class Step:
    """Render the Markdown outline using the deck variables JSON."""

    name: str = "outline"

    def run(self, ctx: RunContext) -> None:
        run_dir = Path(ctx.paths["run_dir"]).resolve()
        repo_root = Path(ctx.paths.get("repo_root", run_dir.parent)).resolve()

        deck_vars_path = run_dir / "deck_vars.json"
        if not deck_vars_path.exists():
            raise RuntimeError(
                f"deck_vars.json not found at {deck_vars_path}; selector step must run before outline."
            )

        cfg = _outline_config(ctx.cfg if isinstance(ctx.cfg, dict) else {})
        template_cfg = cfg.get("template", "templates/executive_summary_outline.jinja2")
        output_cfg = cfg.get("output", "executive_summary_outline.md")

        template_path = Path(template_cfg)
        if not template_path.is_absolute():
            template_path = (repo_root / template_cfg).resolve()
        if not template_path.exists():
            raise RuntimeError(f"Outline template not found: {template_path}")

        output_path = Path(output_cfg)
        if not output_path.is_absolute():
            output_path = (run_dir / output_cfg).resolve()
        else:
            try:
                output_path.relative_to(run_dir)
            except ValueError:
                raise RuntimeError("Outline output path must reside within the run directory.")

        rendered = render_outline_fn(deck_vars_path, template_path, output_path)

        ctx.cache["outline"] = {
            "path": str(output_path),
            "length": len(rendered),
            "template": str(template_path),
        }
        ctx.logger.info(
            {
                "event": "outline_rendered",
                "path": str(output_path),
                "length": len(rendered),
            }
        )
