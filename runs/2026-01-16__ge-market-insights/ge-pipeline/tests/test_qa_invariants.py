from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.qa import qa

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "golden_inputs"


def _load(name: str) -> pd.DataFrame:
    path = FIXTURE_DIR / name
    assert path.exists(), f"Missing QA fixture: {path}"
    return pd.read_csv(path)


def test_qa_invariants_pass_for_golden_fixture() -> None:
    coverage = _load("coverage.csv")
    membership = _load("membership_monthly.csv")
    members = _load("shares_member.csv")
    controls = _load("shares_control.csv")
    qa.invariants(coverage, membership, members, controls)


def test_qa_invariants_fail_on_out_of_range_awarded_share() -> None:
    coverage = _load("coverage.csv")
    membership = _load("membership_monthly.csv")
    members = _load("shares_member.csv")
    controls = _load("shares_control.csv")
    controls_bad = controls.copy()
    controls_bad.loc[controls_bad.index[0], "awarded_share_6m"] = 1.2
    with pytest.raises(AssertionError):
        qa.invariants(coverage, membership, members, controls_bad)


def test_assert_single_anchor_detects_multiple(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_anchor_counts(_shares: pd.DataFrame, _controls: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "program_id": ["P_SURPASS"],
                "category_id": ["C_WOUND"],
                "anchors_in_members": [2],
                "anchors_in_controls": [0],
            }
        )

    monkeypatch.setattr(qa, "anchor_counts", fake_anchor_counts)
    with pytest.raises(AssertionError):
        qa.assert_single_anchor(pd.DataFrame(), pd.DataFrame())
