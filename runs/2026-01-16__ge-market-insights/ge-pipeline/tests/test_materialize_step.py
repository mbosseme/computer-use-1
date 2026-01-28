from __future__ import annotations

import pandas as pd
import pytest

from src.runner.orchestrator import RunContext
from src.steps import materialize_step, windowing_step
from src.steps.materialize_step import _rename_frame
from src.windowing import AnalysisWindow


class _Logger:
    def info(self, _payload):
        pass


def test_rename_frame_preserves_columns_on_empty_frame() -> None:
    source = pd.DataFrame(columns=["program", "category", "entity_code", "month"])[:0]
    renamed = _rename_frame(source, "shares")
    assert {"program_id", "category_id", "facility_id"}.issubset(set(renamed.columns))
    assert len(renamed) == 0


def test_windowing_step_converts_coverage_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_window = AnalysisWindow(
        current_month="2025-02",
        data_cutoff_month="2024-12",
        core_start="2022-02",
        core_end="2024-12",
        pre_start="2021-02",
        post_end="2026-06",
    )
    monkeypatch.setattr(windowing_step, "compute_analysis_window", lambda: fake_window)

    cfg = {
        "guards": {
            "coverage_guard_pp": 2.0,
            "anchor_contract_guard_pp": 2.0,
            "target_lift_pp_raw": 2.0,
        },
        "bigquery": {"table": "project.dataset.table"},
    }
    ctx = RunContext(cfg=cfg, run_id="test", paths={}, logger=_Logger())

    windowing_step.Step().run(ctx)
    assert pytest.approx(ctx.cache["window_params"]["COVERAGE_GUARD"], rel=1e-9) == 0.02
    assert ctx.cache["window_params"]["COVERAGE_GUARD_PP_RAW"] == 2.0
    assert pytest.approx(ctx.cache["window_params"]["ANCHOR_CONTRACT_GUARD"], rel=1e-9) == 0.02
    assert ctx.cache["window_params"]["ANCHOR_CONTRACT_GUARD_PP_RAW"] == 2.0

    params = materialize_step._build_param_dict(ctx)
    assert pytest.approx(params["coverage_guard"], rel=1e-9) == 0.02
    assert params["coverage_guard_pp_raw"] == 2.0
    assert pytest.approx(params["anchor_contract_guard_pp"], rel=1e-9) == 0.02
    assert params["anchor_contract_guard_pp_raw"] == 2.0
