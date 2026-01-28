from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.steps.export_step import EXPORT_COLUMNS

FIXTURE_EXPECTED = Path(__file__).resolve().parent / "fixtures" / "golden_expected" / "prd_answers.csv"


def test_prd_answers_schema_matches_contract() -> None:
    assert FIXTURE_EXPECTED.exists(), "Golden expected prd_answers.csv fixture is missing"
    df = pd.read_csv(FIXTURE_EXPECTED)
    assert list(df.columns) == EXPORT_COLUMNS, "prd_answers.csv columns diverge from export contract"
