import pandas as pd
import pytest

from src.steps import charts_step


def test_summarize_cohort_aggregates_correctly() -> None:
    data = pd.DataFrame(
        {
            "program_id": ["A", "A", "A", "A"],
            "category_id": ["X", "X", "X", "X"],
            "facility_id": ["f1", "f2", "f1", "f2"],
            "event_month": [-1, -1, 0, 0],
            "awarded_spend": [50.0, 30.0, 60.0, 40.0],
            "total_cat_spend": [100.0, 50.0, 120.0, 80.0],
        }
    )

    rolled = charts_step._rolling_sums(data, window=2)
    cohort = charts_step._summarize_cohort(rolled)

    assert not cohort.empty
    row_pre = cohort.loc[cohort["event_month"] == -1].iloc[0]
    row_post = cohort.loc[cohort["event_month"] == 0].iloc[0]

    assert row_pre["facility_count"] == 2
    assert pytest.approx(row_pre["awarded_share_6m_cohort"], rel=1e-6) == 80.0 / 150.0
    assert pytest.approx(row_pre["awarded_share_1m_cohort"], rel=1e-6) == 80.0 / 150.0

    assert row_post["facility_count"] == 2
    assert pytest.approx(row_post["awarded_share_6m_cohort"], rel=1e-6) == 180.0 / 350.0
    assert pytest.approx(row_post["awarded_share_1m_cohort"], rel=1e-6) == 100.0 / 200.0


def test_merge_chart_warnings_prefers_earliest_clamp() -> None:
    dynamic_warns = ["weight_coverage_clamped_from_7", "dropped_zero_denom_months"]
    lasp_warns = ["weight_coverage_clamped_from_3"]

    merged = charts_step._merge_chart_warnings(dynamic_warns, lasp_warns)

    assert "weight_coverage_clamped_from_3" in merged
    assert all("weight_coverage_clamped_from_7" != warn for warn in merged if "clamped_from" in warn)
    assert "dropped_zero_denom_months" in merged


def test_awarded_set_title_line_formats_codes(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = pd.DataFrame(
        {
            "program_id": ["A"],
            "category_id": ["X"],
            "t0_awarded_suppliers": ["['CODE1' 'CODE2']"],
        }
    )
    monkeypatch.setattr(charts_step, "_AWARD_SUPPLIER_LOOKUP", {"CODE1": "Name One", "CODE2": "Name Two"})

    title_line = charts_step._awarded_set_title_line(answers, "A", "X")

    assert title_line == "Awarded set: [Name One (CODE1), Name Two (CODE2)]"


def test_format_warning_label_handles_laspeyres_clamp() -> None:
    label = charts_step._format_warning_label(
        "laspeyres_weight_coverage_clamp_empty",
        {"weight_coverage_clamp_month": 9},
    )
    assert "Laspeyres series unavailable" in label
    assert "9" in label


def test_format_warning_label_handles_weight_clamp() -> None:
    label = charts_step._format_warning_label("weight_coverage_clamped_from_9")
    assert label == "Weight coverage clamp from 9"
