from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.runner.orchestrator import RunContext
from src.selector import build_deck_variables
from src.steps import outline_step
from src.templates import render_outline


def _sample_answers() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "program_id": "SURPASS",
                "category_id": "ADVANCED INTRACAVITY ILLUMINATION & VISUALIZATION",
                "delta_7_12": 0.2203,
                "delta_0_6": 0.105,
                "delta_time_to_target_month": 1.0,
                "delta_missing_reason": "ok",
                "eligible_for_delta": True,
                "N_members": 109,
                "N_controls": 199,
                "member_t0_total_spend_6m": 3_679_471.0,
                "control_t0_total_spend_6m": 4_200_000.0,
                "recon_spend_gap_pct": -23.5,
                "facility_overlap_ratio": 0.50,
                "t0_event_month": "2024-12",
                "member_pre_mean": 0.15,
            },
            {
                "program_id": "ASCEND",
                "category_id": "PATIENT LATERAL TRANSFER DEVICES",
                "delta_7_12": 0.1393,
                "delta_0_6": 0.045,
                "delta_time_to_target_month": 2.0,
                "delta_missing_reason": "ok",
                "eligible_for_delta": True,
                "N_members": 174,
                "N_controls": 384,
                "member_t0_total_spend_6m": 7_642_718.0,
                "control_t0_total_spend_6m": 8_900_000.0,
                "recon_spend_gap_pct": -12.2,
                "facility_overlap_ratio": 0.50,
                "t0_event_month": "2024-11",
                "member_pre_mean": 0.35,
            },
            {
                "program_id": "SURPASS",
                "category_id": "SUTURE PRODUCTS",
                "delta_7_12": -0.0067,
                "delta_0_6": 0.010,
                "delta_time_to_target_month": None,
                "delta_missing_reason": "ok",
                "eligible_for_delta": True,
                "N_members": 306,
                "N_controls": 1_254,
                "member_t0_total_spend_6m": 24_564_737.0,
                "control_t0_total_spend_6m": 30_000_000.0,
                "recon_spend_gap_pct": 14.1,
                "facility_overlap_ratio": 0.57,
                "t0_event_month": "2024-10",
                "member_pre_mean": 0.55,
            },
        ]
    )


class _Logger:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def info(self, payload: dict[str, object]) -> None:
        self.events.append(payload)


def _make_context(tmp_path: Path, cfg: dict | None = None) -> RunContext:
    run_dir = tmp_path / "snapshots" / "test-run"
    result_dir = run_dir / "result_sheets"
    run_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parent.parent
    paths = {
        "run_dir": str(run_dir),
        "result_sheets_dir": str(result_dir),
        "repo_root": str(repo_root),
        "config_path": str(tmp_path / "config.yaml"),
    }
    return RunContext(cfg=cfg or {}, run_id="test-run", paths=paths, logger=_Logger())


def test_render_outline_writes_markdown(tmp_path: Path) -> None:
    answers = _sample_answers()
    deck_core = build_deck_variables(answers, target_lift=0.02)
    deck_vars = {"snapshot": {"run_id": "test-run"}, **deck_core}
    deck_path = tmp_path / "deck_vars.json"
    deck_path.write_text(json.dumps(deck_vars, indent=2), encoding="utf-8")

    template_path = Path("templates/executive_summary_outline.jinja2").resolve()
    output_path = tmp_path / "outline.md"

    rendered = render_outline(deck_path, template_path, output_path)

    assert output_path.exists()
    text = output_path.read_text(encoding="utf-8")
    assert "ADVANCED INTRACAVITY ILLUMINATION & VISUALIZATION" in text
    assert "PATIENT LATERAL TRANSFER DEVICES" in text
    assert rendered == text


def test_outline_step_renders_into_snapshot(tmp_path: Path) -> None:
    ctx = _make_context(tmp_path)
    answers = _sample_answers()
    deck_vars = {"snapshot": {"run_id": "test-run"}, **build_deck_variables(answers, target_lift=0.02)}
    deck_path = Path(ctx.paths["run_dir"]) / "deck_vars.json"
    deck_path.write_text(json.dumps(deck_vars, indent=2), encoding="utf-8")

    outline_step.Step().run(ctx)

    output_path = Path(ctx.paths["run_dir"]) / "executive_summary_outline.md"
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Headline Findings" in content
    assert ctx.cache["outline"]["length"] == len(content)


def test_outline_step_requires_deck_vars(tmp_path: Path) -> None:
    ctx = _make_context(tmp_path)
    with pytest.raises(RuntimeError):
        outline_step.Step().run(ctx)
