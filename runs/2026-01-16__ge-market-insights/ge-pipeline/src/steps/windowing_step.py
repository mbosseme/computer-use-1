"""Pipeline step for computing analysis windows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from ..runner.orchestrator import RunContext
from ..windowing import AnalysisWindow, compute_analysis_window


@dataclass
class Step:
    """Wrap the existing windowing helpers into a pipeline step."""

    name: str = "windowing"

    def run(self, ctx: RunContext) -> None:
        cfg_window: Dict[str, Any] = ctx.cfg.get("window", {}) if isinstance(ctx.cfg, dict) else {}
        window = compute_analysis_window()
        target_raw = float(ctx.cfg.get("guards", {}).get("target_lift_pp_raw", 2.0))
        target_fraction = target_raw / 100.0 if target_raw > 1 else target_raw
        coverage_raw = float(ctx.cfg.get("guards", {}).get("coverage_guard_pp", 2.0))
        coverage_fraction = coverage_raw / 100.0 if coverage_raw > 1 else coverage_raw
        anchor_guard_raw = float(ctx.cfg.get("guards", {}).get("anchor_contract_guard_pp", 2.0))
        anchor_guard_fraction = anchor_guard_raw / 100.0 if anchor_guard_raw > 1 else anchor_guard_raw
        window_params = {
            "CURRENT_MONTH": window.current_month,
            "DATA_CUTOFF_MONTH": window.data_cutoff_month,
            "START_MONTH": cfg_window.get("start_month") or window.pre_start,
            "END_MONTH": cfg_window.get("end_month") or window.post_end,
            "CORE_START": window.core_start,
            "CORE_END": window.core_end,
        }
        ctx.cache["window_params"] = {
            **window_params,
            "ROLLING_M": int(cfg_window.get("rolling_m", 6)),
            "MIN_PRE_MONTHS": int(cfg_window.get("min_pre_months", 3)),
            "MIN_COMMON_MONTHS": int(cfg_window.get("min_common_months", cfg_window.get("min_pre_months", 3))),
            "TARGET_LIFT_PP_RAW": target_raw,
            "TARGET_LIFT_PP": target_fraction,
            "COVERAGE_GUARD": coverage_fraction,
            "COVERAGE_GUARD_PP_RAW": coverage_raw,
            "ANCHOR_CONTRACT_GUARD": anchor_guard_fraction,
            "ANCHOR_CONTRACT_GUARD_PP_RAW": anchor_guard_raw,
        }
        ctx.cache["window_analysis"] = window
        params = {
            "MIN_PRE_MONTHS": ctx.cache["window_params"]["MIN_PRE_MONTHS"],
            "MIN_COMMON_MONTHS": ctx.cache["window_params"]["MIN_COMMON_MONTHS"],
            "START_MONTH": window_params["START_MONTH"],
            "END_MONTH": window_params["END_MONTH"],
            "CORE_START": window_params["CORE_START"],
            "CORE_END": window_params["CORE_END"],
            "DATA_CUTOFF_MONTH": window_params["DATA_CUTOFF_MONTH"],
            "CURRENT_MONTH": window_params["CURRENT_MONTH"],
            "ROLLING_M": ctx.cache["window_params"]["ROLLING_M"],
            "TARGET_LIFT_PP_RAW": target_raw,
            "TARGET_LIFT_PP": target_fraction,
            "COVERAGE_GUARD": coverage_fraction,
            "COVERAGE_GUARD_PP_RAW": coverage_raw,
            "ANCHOR_CONTRACT_GUARD": anchor_guard_fraction,
            "ANCHOR_CONTRACT_GUARD_PP_RAW": anchor_guard_raw,
        }
        ctx.cache["params"] = params
