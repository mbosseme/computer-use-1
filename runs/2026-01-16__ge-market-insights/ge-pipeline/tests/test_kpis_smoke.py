from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from src.kpis import kpis
from src.steps import kpis_step
from src.steps.materialize_step import _build_controls_sufficiency
from src.steps.export_step import EXPORT_COLUMNS, _ensure_columns

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "golden_inputs"
EXPECTED_PATH = Path(__file__).resolve().parent / "fixtures" / "golden_expected" / "prd_answers.csv"


def _load(name: str) -> pd.DataFrame:
    path = FIXTURE_DIR / name
    assert path.exists(), f"Missing KPI fixture: {path}"
    return pd.read_csv(path)


def _build_expected_answers() -> pd.DataFrame:
    members = _load("shares_member.csv")
    controls = _load("shares_control.csv")
    awarded = _load("awarded_block.csv")

    for df in (members, controls, awarded):
        for col in ("program_id", "category_id", "facility_id"):
            if col in df.columns:
                df[col] = df[col].astype(str)

    params = {
        "MIN_PRE_MONTHS": 3,
        "MIN_COMMON_MONTHS": 3,
        "TARGET_LIFT_PP": 0.02,
    }

    suff_df = _build_controls_sufficiency(members, controls, params["MIN_PRE_MONTHS"])
    answers = kpis.build_delta_summary(
        members,
        controls,
        target_pp=params["TARGET_LIFT_PP"],
        min_pre_months=params["MIN_PRE_MONTHS"],
        min_common_months=params["MIN_COMMON_MONTHS"],
    )
    answers = kpis_step._merge_sufficiency(answers, suff_df)
    answers = kpis_step._apply_common_month_flags(answers, params["MIN_COMMON_MONTHS"])
    award_meta = kpis_step._award_metadata(members, awarded)
    if not award_meta.empty:
        answers = answers.merge(award_meta, on=["program_id", "category_id"], how="left")
    answers = answers.sort_values(["program_id", "category_id"]).reset_index(drop=True)
    answers = _ensure_columns(answers, EXPORT_COLUMNS)
    return answers


def test_kpis_golden_fixture_matches_expected() -> None:
    expected = pd.read_csv(EXPECTED_PATH)
    assert not expected.empty, "Golden expected prd_answers.csv must not be empty"
    answers = _build_expected_answers()
    answers = answers.loc[:, expected.columns]
    assert_frame_equal(
        answers.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_dtype=False,
        rtol=1e-6,
        atol=1e-9,
    )
