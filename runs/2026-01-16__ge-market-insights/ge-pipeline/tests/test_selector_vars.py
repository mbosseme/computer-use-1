from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import pandas as pd

from src.runner.orchestrator import RunContext
from src.selector import build_deck_variables, validate_deck_payload
from src.steps import selector_step
import src.pptx_builder.build_deck as deck_builder


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
                "recon_spend_gap_pct": None,
                "facility_overlap_ratio": None,
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
            {
                "program_id": "SURPASS",
                "category_id": "STERILE REPROCESSING",
                "delta_7_12": -0.1586,
                "delta_0_6": -0.032,
                "delta_time_to_target_month": None,
                "delta_missing_reason": "ok",
                "eligible_for_delta": True,
                "N_members": 174,
                "N_controls": 410,
                "member_t0_total_spend_6m": 16_538_427.0,
                "control_t0_total_spend_6m": 17_400_000.0,
                "recon_spend_gap_pct": 27.9,
                "facility_overlap_ratio": 0.54,
                "t0_event_month": "2025-02",
                "member_pre_mean": 0.65,
            },
            {
                "program_id": "ASCEND",
                "category_id": "VEIN FINDER EQUIPMENT",
                "delta_7_12": -0.7373,
                "delta_0_6": -0.420,
                "delta_time_to_target_month": None,
                "delta_missing_reason": "ok",
                "eligible_for_delta": True,
                "N_members": 24,
                "N_controls": 60,
                "member_t0_total_spend_6m": 482_331.0,
                "control_t0_total_spend_6m": 520_000.0,
                "recon_spend_gap_pct": None,
                "facility_overlap_ratio": None,
                "t0_event_month": "2024-04",
                "member_pre_mean": 0.28,
            },
            {
                "program_id": "ASCEND",
                "category_id": "CRM DEVICES",
                "delta_7_12": 0.015,
                "delta_0_6": 0.008,
                "delta_time_to_target_month": 3.0,
                "delta_missing_reason": "ok",
                "eligible_for_delta": True,
                "N_members": 98,
                "N_controls": 210,
                "member_t0_total_spend_6m": 4_500_000.0,
                "control_t0_total_spend_6m": 4_800_000.0,
                "recon_spend_gap_pct": None,
                "facility_overlap_ratio": None,
                "t0_event_month": "2025-01",
                "member_pre_mean": 0.42,
            },
        ]
    )


def test_build_deck_variables_summarises_answers() -> None:
    df = _sample_answers()
    result = build_deck_variables(df, target_lift=0.02)

    headline = result["headline"]
    assert headline["eligible_total"] == 6
    assert headline["cohorts_total"] == 6
    assert headline["pct_sustained"] == pytest.approx(33.3, rel=1e-3)
    assert headline["both"] == 2
    assert headline["sustained"] == 2
    assert headline["early"] == 2

    drivers = result["drivers"]["start_buckets"]
    buckets = {entry["bucket"]: entry for entry in drivers}
    assert buckets["0–20%"]["cohorts"] == 1
    assert buckets["20–50%"]["cohorts"] == 3
    assert buckets["50%+"]["cohorts"] == 2

    examples = result["examples"]
    assert [case["category_id"] for case in examples["wins"]] == [
        "ADVANCED INTRACAVITY ILLUMINATION & VISUALIZATION",
    ]
    assert len(examples["losses"]) == 2
    assert all(case["category_id"] != "CRM DEVICES" for case in examples["wins"])


class _Logger:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def info(self, payload: dict[str, Any]) -> None:
        self.events.append(payload)


def _context(tmp_path: Path) -> RunContext:
    run_dir = tmp_path / "snapshots" / "test-run"
    run_dir.mkdir(parents=True, exist_ok=True)
    result_dir = run_dir / "result_sheets"
    paths = {
        "run_dir": str(run_dir),
        "result_sheets_dir": str(result_dir),
        "repo_root": str(tmp_path),
        "config_path": str(tmp_path / "config.yaml"),
    }
    cfg = {"guards": {"target_lift_pp_raw": 2.0}}
    ctx = RunContext(cfg=cfg, run_id="test-run", paths=paths, logger=_Logger())
    ctx.cache["params"] = {"TARGET_LIFT_PP": 0.02}
    return ctx


def test_selector_step_writes_deck_vars(tmp_path: Path) -> None:
    ctx = _context(tmp_path)
    answers_df = _sample_answers()
    ctx.cache["export"] = {"answers_df": answers_df}

    selector_step.Step().run(ctx)

    output_path = Path(ctx.paths["run_dir"]) / "deck_vars.json"
    assert output_path.exists()
    payload = json.loads(output_path.read_text())
    assert payload["snapshot"]["run_id"] == "test-run"
    assert payload["headline"]["eligible_total"] == 6
    assert ctx.cache["deck_vars"]["examples"]["wins"]
    assert payload["filters"]["filtered_rows_before"] == 6
    assert "integrity" in payload


def test_stats_from_headline_converts_percentage_units() -> None:
    headline = {
        "pct_sustained": 45.0,
        "median_time_to_target_mo": 2.0,
        "portfolio_mean_pp": -1.5,
        "eligible_total": 10,
        "cohorts_total": 12,
        "recent_mean_pp": 0.8,
        "direction_positive_pct": 60.0,
        "direction_positive_mean_pp": 3.2,
        "direction_negative_mean_pp": -4.5,
    }
    stats = deck_builder._stats_from_headline(headline)
    assert stats.pct_sustained == pytest.approx(0.45)
    assert stats.portfolio_mean_delta == pytest.approx(-0.015)
    assert stats.recent_mean_delta == pytest.approx(0.008)
    assert stats.direction_positive_pct == pytest.approx(0.60)
    assert stats.direction_positive_mean == pytest.approx(0.032)
    assert stats.direction_negative_mean == pytest.approx(-0.045)
    assert stats.eligible_count == 10
    assert stats.total_count == 12


def test_cases_from_examples_preserves_order_and_scales() -> None:
    examples = {
        "wins": [
            {
                "program_id": "SURPASS",
                "category_id": "ADVANCED INTRACAVITY",
                "delta_pp": 22.0,
                "members": 10,
                "controls": 20,
                "spend_gap_pct": -12.5,
                "overlap": 0.55,
                "member_t0_spend_6m": 1_000_000,
                "dollars_shifted": 250000,
            }
        ],
        "no_gain": [
            {
                "program_id": "ASCEND",
                "category_id": "SUTURE PRODUCTS",
                "delta_pp": 0.5,
                "members": 30,
                "controls": 40,
                "spend_gap_pct": 5.0,
                "overlap": 0.62,
            }
        ],
        "losses": [
            {
                "program_id": "SURPASS",
                "category_id": "STERILE REPROCESSING",
                "delta_pp": -15.0,
                "members": 25,
                "controls": 33,
                "spend_gap_pct": 18.0,
                "overlap": 0.44,
            }
        ],
    }
    cases = deck_builder._cases_from_examples(examples)
    assert [case.case_type for case in cases] == ["win", "no_gain", "loss"]
    assert cases[0].program == "SURPASS"
    assert cases[0].delta_7_12 == pytest.approx(0.22)
    assert cases[0].dollars_shifted == pytest.approx(250000.0)
    assert cases[1].delta_7_12 == pytest.approx(0.005)
    assert cases[2].delta_7_12 == pytest.approx(-0.15)
    assert not cases[0].pretrend_risk_flag


def test_selector_step_respects_config_filters(tmp_path: Path) -> None:
    ctx = _context(tmp_path)
    ctx.cfg = {
        "guards": {"target_lift_pp_raw": 2.0},
        "selector": {
            "category_excludes": ["SUTURE PRODUCTS"],
            "min_members": 150,
            "min_member_spend_6m": 5_000_000,
            "manufacturer_focus": ["Stryker"],
        },
    }
    answers_df = _sample_answers()
    ctx.cache["export"] = {"answers_df": answers_df}

    selector_step.Step().run(ctx)

    deck_path = Path(ctx.paths["run_dir"]) / "deck_vars.json"
    payload = json.loads(deck_path.read_text())
    categories = [case["category_id"] for case in payload["examples"]["wins"] + payload["examples"]["losses"]]
    assert "SUTURE PRODUCTS" not in categories
    assert payload["appendix"]["manufacturers"] == ["Stryker"]
    assert payload["filters"]["category_excludes"] == ["SUTURE PRODUCTS"]
    assert payload["filters"]["filtered_rows_before"] == 6
    assert payload["filters"]["filtered_rows_after"] < payload["filters"]["filtered_rows_before"]
    assert payload["integrity"]["pretrend_risk"] >= 0


def test_validate_deck_payload_catches_missing_keys() -> None:
    bad_payload = {
        "headline": {"eligible_total": 0, "cohorts_total": 0, "pct_sustained": 0.0, "median_time_to_target_mo": None, "portfolio_mean_pp": 0.0},
        "drivers": {"start_buckets": [], "dollars_shifted": {"positive": 0.0, "negative": 0.0, "net": 0.0}},
        "examples": {"wins": [], "no_gain": [], "losses": []},
        "appendix": {"manufacturers": [], "by_manufacturer": {}},
    }
    with pytest.raises(ValueError):
        validate_deck_payload(bad_payload)  # type: ignore[arg-type]
