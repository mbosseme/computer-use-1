from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd

from src.validation.parity import compare_prd_answers

FIXTURE_EXPECTED = Path(__file__).resolve().parent / "fixtures" / "golden_expected" / "prd_answers.csv"


def test_compare_prd_answers_identical(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.csv"
    shutil.copy(FIXTURE_EXPECTED, candidate)

    result = compare_prd_answers(FIXTURE_EXPECTED, candidate)
    assert result.matched
    assert result.numeric_max_diff == {}
    assert result.categorical_mismatches == {}


def test_compare_prd_answers_detects_numeric_diff(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.csv"
    df = pd.read_csv(FIXTURE_EXPECTED)
    df["delta_7_12"] = pd.to_numeric(df["delta_7_12"], errors="coerce")
    base_value = float(df.loc[0, "delta_7_12"])
    df.loc[0, "delta_7_12"] = base_value + 0.5
    df.to_csv(candidate, index=False)

    result = compare_prd_answers(FIXTURE_EXPECTED, candidate, tolerance=1e-9)
    assert not result.matched
    assert "delta_7_12" in result.numeric_max_diff

