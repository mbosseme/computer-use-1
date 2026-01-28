from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.runner.orchestrator import RunContext
from src.steps import qa_step


def _sample_panels() -> dict[str, pd.DataFrame]:
    coverage_df = pd.DataFrame({"is_covered": [1]})
    membership_df = pd.DataFrame({"member_flag": [1]})
    shares_df = pd.DataFrame(
        [
            {"program_id": "P", "category_id": "Cat", "facility_id": "m1", "event_month": -1, "awarded_share_6m": 0.45},
            {"program_id": "P", "category_id": "Cat", "facility_id": "m1", "event_month": 0, "awarded_share_6m": 0.52},
        ]
    )
    controls_df = pd.DataFrame(
        [
            {"program_id": "P", "category_id": "Cat", "facility_id": "c1", "event_month": -1, "awarded_share_6m": 0.30},
            {"program_id": "P", "category_id": "Cat", "facility_id": "c1", "event_month": 0, "awarded_share_6m": 0.31},
        ]
    )
    return {
        "coverage_df": coverage_df,
        "membership_monthly_df": membership_df,
        "shares_member_df": shares_df,
        "shares_control_df": controls_df,
    }


@dataclass
class _Logger:
    events: list[dict[str, object]] = field(default_factory=list)

    def info(self, payload: dict[str, object]) -> None:  # pragma: no cover - trace-only helper
        self.events.append(payload)


def test_qa_step_drops_legacy_ragged_columns() -> None:
    answers_df = pd.DataFrame(
        {
            "program_id": ["P"],
            "category_id": ["Cat"],
            "delta_0_6": [0.1],
            "ragged_tail_flag": [True],
            "ragged_tail_threshold": [123],
            "ragged_tail_reason": ["legacy"],
        }
    )
    ctx = RunContext(cfg={}, run_id="test", paths={}, logger=_Logger())
    ctx.cache["answers_df"] = answers_df
    ctx.cache["panels"] = _sample_panels()

    qa_step.Step().run(ctx)

    updated = ctx.cache["answers_df"]
    assert list(updated.columns) == ["program_id", "category_id", "delta_0_6"]
    qa_cache = ctx.cache.get("qa", {})
    assert isinstance(qa_cache, dict)
    assert "anchor_counts_df" in qa_cache


def test_qa_step_leaves_answers_when_no_ragged_columns() -> None:
    answers_df = pd.DataFrame(
        {
            "program_id": ["P"],
            "category_id": ["Cat"],
            "delta_0_6": [0.2],
        }
    )
    ctx = RunContext(cfg={}, run_id="test", paths={}, logger=_Logger())
    ctx.cache["answers_df"] = answers_df.copy()
    ctx.cache["panels"] = _sample_panels()

    qa_step.Step().run(ctx)

    updated = ctx.cache["answers_df"]
    pd.testing.assert_frame_equal(updated, answers_df)
