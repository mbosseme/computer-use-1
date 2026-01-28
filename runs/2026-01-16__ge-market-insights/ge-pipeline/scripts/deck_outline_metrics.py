#!/usr/bin/env python3
"""Generate reusable deck outline metrics from a pipeline snapshot."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import pandas as pd

TARGET_DELTA = 0.02


@dataclass
class CohortHighlight:
    program_id: str
    category_id: str
    delta_7_12: float
    t0_event_month: str | None
    n_members_measured: int
    n_controls_measured: int
    member_t0_total_spend_6m: float


def load_prd_answers(snapshot_dir: Path) -> pd.DataFrame:
    path = snapshot_dir / "prd_answers.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def compute_metrics(df: pd.DataFrame) -> Dict:
    eligible_mask = df["delta_missing_reason"].fillna("").str.lower().eq("ok")
    eligible = df[eligible_mask].copy()

    total_cohorts = int(len(df))
    eligible_cohorts = int(len(eligible))
    sustained_mask = eligible["delta_7_12"] >= TARGET_DELTA
    sustained_count = int(sustained_mask.sum())
    pct_sustained = sustained_count / eligible_cohorts if eligible_cohorts else 0.0

    median_ttt = (
        float(eligible.loc[sustained_mask, "delta_time_to_target_month"].dropna().median())
        if sustained_count
        else None
    )
    portfolio_mean = float(eligible["delta_7_12"].mean()) if eligible_cohorts else 0.0

    positive_mask = eligible["delta_7_12"] > 0
    positive_pct = float(positive_mask.mean()) if eligible_cohorts else 0.0
    positive_avg = float(eligible.loc[positive_mask, "delta_7_12"].mean()) if positive_mask.any() else None
    negative_avg = (
        float(eligible.loc[~positive_mask, "delta_7_12"].mean()) if (~positive_mask).any() else None
    )

    impact_positive = float(
        (eligible.loc[positive_mask, "delta_7_12"] * eligible.loc[positive_mask, "member_t0_total_spend_6m"]).sum()
    )
    impact_negative = float(
        (eligible.loc[~positive_mask, "delta_7_12"] * eligible.loc[~positive_mask, "member_t0_total_spend_6m"]).sum()
    )
    impact_total = impact_positive + impact_negative

    eligible["early_win"] = eligible["delta_0_6"] >= TARGET_DELTA
    eligible["sustained_win"] = eligible["delta_7_12"] >= TARGET_DELTA

    early_winners = int(eligible["early_win"].sum())
    late_winners = int(eligible["sustained_win"].sum())
    both = int((eligible["early_win"] & eligible["sustained_win"]).sum())
    early_only = int((eligible["early_win"] & ~eligible["sustained_win"]).sum())
    late_bloomers = int((~eligible["early_win"] & eligible["sustained_win"]).sum())

    eligible["t0_event_month"] = pd.to_datetime(eligible["t0_event_month"], errors="coerce")
    recent_full = eligible[
        (eligible["t0_event_month"].dt.year >= 2025) & (eligible["member_post_7_12_months"] >= 6)
    ]
    recent_full_mean = float(recent_full["delta_7_12"].mean()) if not recent_full.empty else None
    recent_full_count = int(len(recent_full))

    def top_highlights(program: str, ascending: bool) -> List[CohortHighlight]:
        subset = eligible[eligible["program_id"] == program]
        if subset.empty:
            return []
        sorted_subset = subset.sort_values("delta_7_12", ascending=ascending)
        records: List[CohortHighlight] = []
        for _, row in sorted_subset.head(3).iterrows():
            t0 = row["t0_event_month"]
            t0_str = t0.strftime("%Y-%m") if pd.notna(t0) else None
            records.append(
                CohortHighlight(
                    program_id=row["program_id"],
                    category_id=row["category_id"],
                    delta_7_12=float(row["delta_7_12"]),
                    t0_event_month=t0_str,
                    n_members_measured=int(row["N_members_measured"]),
                    n_controls_measured=int(row["N_controls_measured"]),
                    member_t0_total_spend_6m=float(row["member_t0_total_spend_6m"]),
                )
            )
        return records

    metrics = {
        "total_cohorts": total_cohorts,
        "eligible_cohorts": eligible_cohorts,
        "ineligible_cohorts": total_cohorts - eligible_cohorts,
        "sustained_count": sustained_count,
        "pct_sustained": pct_sustained,
        "median_ttt": median_ttt,
        "portfolio_mean": portfolio_mean,
        "positive_pct": positive_pct,
        "positive_avg": positive_avg,
        "negative_avg": negative_avg,
        "impact_positive": impact_positive,
        "impact_negative": impact_negative,
        "impact_total": impact_total,
        "early_winners": early_winners,
        "sustained_winners": late_winners,
        "both_winners": both,
        "early_only": early_only,
        "late_bloomers": late_bloomers,
        "recent_full_count": recent_full_count,
        "recent_full_mean": recent_full_mean,
        "surpass_winners": [asdict(h) for h in top_highlights("Surpass", ascending=False)],
        "ascend_winners": [asdict(h) for h in top_highlights("Ascend", ascending=False)],
        "surpass_losses": [asdict(h) for h in top_highlights("Surpass", ascending=True)],
        "ascend_losses": [asdict(h) for h in top_highlights("Ascend", ascending=True)],
    }
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deck outline metrics from snapshot")
    parser.add_argument("--snapshot", required=True, help="Path to snapshot directory")
    parser.add_argument(
        "--out",
        default="docs/generated/deck_outline_metrics.json",
        help="Path to output JSON file",
    )
    args = parser.parse_args()

    snapshot_dir = Path(args.snapshot)
    df = load_prd_answers(snapshot_dir)
    metrics = compute_metrics(df)
    metrics["snapshot"] = snapshot_dir.name

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2))
    print(f"Wrote metrics to {out_path}")
    print(
        f"Snapshot: {metrics['snapshot']} | Eligible {metrics['eligible_cohorts']} / {metrics['total_cohorts']}"
        f" (sustained {metrics['pct_sustained']:.1%})"
    )


if __name__ == "__main__":
    main()
