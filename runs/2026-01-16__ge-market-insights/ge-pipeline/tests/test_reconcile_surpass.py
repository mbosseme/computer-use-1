from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.reconciliation import (
    compare_to_prd,
    filter_measured_members,
    resolve_latest_prd_answers,
    summarize_by_category,
)


def test_filter_measured_members_basic() -> None:
    shares = pd.DataFrame(
        {
            "program_id": ["Surpass", "Surpass", "Surpass", "Ascend"],
            "category_id": ["A", "A", "B", "A"],
            "facility_id": ["f1", "f2", "f3", "f4"],
            "event_month": [0, 0, 0, 0],
            "member_at_t0": [True, True, False, True],
            "t0_total_cat_spend_6m": [100.0, 200.0, 50.0, 999.0],
        }
    )

    result = filter_measured_members(shares)

    assert set(result["facility_id"]) == {"f1", "f2"}
    assert result["t0_total_cat_spend_6m"].sum() == pytest.approx(300.0)


def test_summarize_by_category() -> None:
    facility_df = pd.DataFrame(
        {
            "category_id": ["A", "A", "B"],
            "facility_id": ["f1", "f2", "f3"],
            "t0_total_cat_spend_6m": [100.0, 200.0, 50.0],
        }
    )

    summary = summarize_by_category(facility_df)

    assert summary.loc[summary["category_id"] == "A", "facility_count"].iat[0] == 2
    assert summary.loc[summary["category_id"] == "A", "t0_spend_6m"].iat[0] == pytest.approx(300.0)


def test_compare_to_prd_aligns_counts_and_spend() -> None:
    category_summary = pd.DataFrame(
        {
            "category_id": ["A", "B"],
            "facility_count": [2, 1],
            "t0_spend_6m": [300.0, 50.0],
        }
    )
    prd_answers = pd.DataFrame(
        {
            "program_id": ["Surpass", "Surpass"],
            "category_id": ["A", "B"],
            "N_members_measured": [2, 1],
            "member_t0_total_spend_6m": [300.0, 50.0],
        }
    )

    comparison = compare_to_prd(category_summary, prd_answers)

    assert comparison["delta_facility_count"].abs().max() == 0
    assert comparison["delta_t0_spend_6m"].abs().max() == pytest.approx(0.0)


def test_resolve_latest_prd_answers(tmp_path: Path) -> None:
    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir()
    older = snapshots_dir / "2025-01-01_00-00-00"
    interim = snapshots_dir / "2025-01-15_00-00-00"
    newer = snapshots_dir / "2025-02-01_00-00-00"
    older.mkdir()
    interim.mkdir()
    newer.mkdir()
    (older / "prd_answers.csv").write_text("program_id,category_id\n", encoding="utf-8")
    expected = newer / "prd_answers.csv"
    expected.write_text("program_id,category_id\n", encoding="utf-8")

    resolved = resolve_latest_prd_answers(snapshots_dir=snapshots_dir)

    assert resolved == expected
