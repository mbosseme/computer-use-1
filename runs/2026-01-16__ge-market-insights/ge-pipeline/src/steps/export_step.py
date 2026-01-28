"""Pipeline step for exporting primary outputs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

import numpy as np
import pandas as pd

from ..runner.orchestrator import RunContext


EXPORT_COLUMNS: list[str] = [
    "program_id",
    "category_id",
    "N_members",
    "N_controls",
    "N_members_measured",
    "N_controls_measured",
    "delta_0_6",
    "delta_7_12",
    "delta_time_to_target_month",
    "meaningful_lift_7_12",
    "delta_missing_reason",
    "member_pre_mean_thin",
    "control_pre_mean_thin",
    "member_post_0_6",
    "control_post_0_6",
    "member_post_7_12",
    "control_post_7_12",
    "member_pre_months",
    "control_pre_months",
    "member_post_0_6_months",
    "control_post_0_6_months",
    "member_post_7_12_months",
    "control_post_7_12_months",
    "pre_common_months",
    "post06_common_months",
    "post712_common_months",
    "member_t0_total_spend_6m",
    "control_t0_total_spend_6m",
    "weight_coverage_clamped",
    "weight_coverage_clamp_month",
    "member_masked_dataset_exit_count",
    "member_masked_program_exit_count",
    "control_masked_dataset_exit_count",
    "control_masked_program_exit_count",
    "member_weight_coverage_min",
    "control_weight_coverage_min",
    "pre_contract_baseline_included",
    "member_pre_mean",
    "control_pre_mean",
    "has_pre_common_ge_MIN",
    "has_post06_common_ge_MIN",
    "has_post712_common_ge_MIN",
    "thin_pre",
    "eligible_for_delta",
    "controls_other_pg_overlap_excluded",
    "delta_0_12",
    "kpi_spec",
    "t0_awarded_suppliers",
    "t0_event_month",
]

RANK_COLUMNS: list[str] = [
    "program_id",
    "category_id",
    "delta_7_12",
    "delta_0_6",
    "meaningful_lift_7_12",
    "N_members",
    "N_controls",
    "N_members_measured",
    "N_controls_measured",
    "member_pre_months",
    "control_pre_months",
    "delta_missing_reason",
]


def _ensure_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = np.nan
    return out.loc[:, list(columns)]


def _derive_topn(cfg: Dict[str, Any]) -> int:
    run_cfg = cfg.get("run", {}) if isinstance(cfg, dict) else {}
    if isinstance(run_cfg, dict):
        topn = run_cfg.get("topn")
        if isinstance(topn, int) and topn >= 0:
            return topn
    charts_cfg = cfg.get("charts", {}) if isinstance(cfg, dict) else {}
    if isinstance(charts_cfg, dict):
        topn = charts_cfg.get("topn")
        if isinstance(topn, int) and topn >= 0:
            return topn
    return 15


def _relative_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


@dataclass
class Step:
    """Export CSV artifacts and manifest into the snapshot directory."""

    name: str = "export"

    def run(self, ctx: RunContext) -> None:
        run_dir = Path(ctx.paths["run_dir"]).resolve()
        result_sheets_dir = Path(ctx.paths["result_sheets_dir"]).resolve()
        repo_root = Path(ctx.paths["repo_root"]).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        result_sheets_dir.mkdir(parents=True, exist_ok=True)

        answers_df = ctx.cache.get("answers_df", pd.DataFrame())
        suff_df = ctx.cache.get("controls_sufficiency_df", pd.DataFrame())
        qa_cache_raw = ctx.cache.get("qa")
        qa_cache = qa_cache_raw if isinstance(qa_cache_raw, dict) else {}
        missing_pre_df = qa_cache.get("missing_pre_pairs_df")

        if not isinstance(answers_df, pd.DataFrame) or answers_df.empty:
            ctx.logger.info({"event": "export_warning", "message": "answers_df missing or empty; writing empty exports"})
            answers_df = pd.DataFrame(columns=EXPORT_COLUMNS)

        answers_clean = _ensure_columns(answers_df, EXPORT_COLUMNS)
        answers_clean = answers_clean.copy()
        for col in ("program_id", "category_id"):
            if col in answers_clean.columns:
                answers_clean[col] = answers_clean[col].astype(str)

        event_ranking_df = answers_clean.sort_values(by=["delta_7_12"], ascending=False, na_position="last")
        topn_limit = _derive_topn(ctx.cfg)
        topn_limit = max(0, int(topn_limit))
        topn_lift_ranking_df = event_ranking_df.head(topn_limit).copy() if topn_limit > 0 else pd.DataFrame(columns=EXPORT_COLUMNS)

        ctx.cache["event_study_ranking_df"] = event_ranking_df
        ctx.cache["topn_lift_ranking_df"] = topn_lift_ranking_df

        artifacts: Dict[str, Dict[str, Any]] = {}

        def _write_csv(df: pd.DataFrame, path: Path) -> None:
            df.to_csv(path, index=False)
            artifacts[path.name] = {
                "path": _relative_path(path, repo_root),
                "rows": int(df.shape[0]),
                "exists": path.exists(),
            }

        _write_csv(answers_clean, run_dir / "prd_answers.csv")
        _write_csv(_ensure_columns(event_ranking_df, EXPORT_COLUMNS), run_dir / "event_study_ranking.csv")
        _write_csv(_ensure_columns(topn_lift_ranking_df, EXPORT_COLUMNS), run_dir / "topn_lift_ranking.csv")

        panels_raw = ctx.cache.get("panels")
        panels = panels_raw if isinstance(panels_raw, dict) else {}
        shares_path = run_dir / "shares_member.csv"
        shares_df = panels.get("shares_member_df")
        if isinstance(shares_df, pd.DataFrame):
            _write_csv(shares_df, shares_path)
        else:
            placeholder = pd.DataFrame({"note": ["shares_member_df missing this run"]})
            _write_csv(placeholder, shares_path)

        if isinstance(suff_df, pd.DataFrame) and not suff_df.empty:
            suff_to_write = suff_df.reset_index(drop=True)
        else:
            suff_to_write = pd.DataFrame({"note": ["missing controls_sufficiency_df this run"]})
        _write_csv(suff_to_write, run_dir / "controls_sufficiency.csv")

        qa_missing_path = run_dir / "qa_missing_pre_pairs.csv"
        if isinstance(missing_pre_df, pd.DataFrame) and not missing_pre_df.empty:
            missing_pre_to_write = missing_pre_df.reset_index(drop=True)
            missing_pre_rows = int(missing_pre_to_write.shape[0])
        else:
            missing_pre_to_write = pd.DataFrame({"note": ["qa_missing_pre_pairs not generated earlier"]})
            missing_pre_rows = 0
        _write_csv(missing_pre_to_write, qa_missing_path)

        manifest_path = run_dir / "manifest.json"
        counts = {
            "answers_rows": int(answers_clean.shape[0]),
            "programs": int(answers_clean["program_id"].nunique()) if "program_id" in answers_clean.columns else 0,
            "categories": int(answers_clean["category_id"].nunique()) if "category_id" in answers_clean.columns else 0,
        }
        qa_status = {
            "missing_pre_pairs_rows": missing_pre_rows,
        }
        manifest = {
            "run_id": ctx.run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "config_path": ctx.paths.get("config_path"),
            "counts": counts,
            "qa": qa_status,
            "charts": {
                "count": 0,
                "files": [],
            },
            "artifacts": artifacts,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))
        artifacts[manifest_path.name] = {
            "path": _relative_path(manifest_path, repo_root),
            "rows": None,
            "exists": manifest_path.exists(),
        }

        ctx.cache["export"] = {
            "answers_df": answers_clean,
            "event_ranking_df": event_ranking_df,
            "topn_lift_ranking_df": topn_lift_ranking_df,
            "artifacts": artifacts,
            "counts": counts,
            "qa": qa_status,
        }
        ctx.logger.info(
            {
                "event": "export_complete",
                "artifacts": {name: {"rows": meta["rows"], "exists": meta["exists"]} for name, meta in artifacts.items()},
            }
        )
