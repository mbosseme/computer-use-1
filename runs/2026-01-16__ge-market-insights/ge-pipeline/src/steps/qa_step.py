"""Pipeline step enforcing QA invariants."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from ..qa import qa
from ..runner.orchestrator import RunContext


@dataclass
class Step:
    """QA step wrapping notebook diagnostics."""

    name: str = "qa"

    def run(self, ctx: RunContext) -> None:
        panels: Dict[str, pd.DataFrame] = ctx.cache.get("panels", {})  # type: ignore[assignment]
        if not panels:
            raise RuntimeError("materialize step must populate panels before QA step runs")

        coverage_df = panels.get("coverage_df", pd.DataFrame())
        membership_df = panels.get("membership_monthly_df", pd.DataFrame())
        shares_df = panels.get("shares_member_df", pd.DataFrame())
        controls_df = panels.get("shares_control_df", pd.DataFrame())

        qa.invariants(coverage_df, membership_df, shares_df, controls_df)
        qa.assert_single_anchor(shares_df, controls_df)
        anchor_counts_df = qa.anchor_counts(shares_df, controls_df)

        answers_df = ctx.cache.get("answers_df")
        if isinstance(answers_df, pd.DataFrame):
            answers_work = answers_df.copy()
            for col in ("program_id", "category_id"):
                if col in answers_work.columns:
                    answers_work[col] = answers_work[col].astype(str)

            drop_cols = [
                "ragged_tail_flag",
                "ragged_tail_clamp_month",
                "ragged_tail_reason",
                "ragged_tail_threshold",
                "member_min_post_facilities",
                "control_min_post_facilities",
            ]
            answers_work = answers_work.drop(columns=drop_cols, errors="ignore")
            ctx.cache["answers_df"] = answers_work

        ctx.cache["qa"] = {
            "anchor_counts_df": anchor_counts_df,
        }
        ctx.logger.info(
            {
                "event": "qa_summary",
                "anchor_rows": int(anchor_counts_df.shape[0]) if isinstance(anchor_counts_df, pd.DataFrame) else 0,
            }
        )
