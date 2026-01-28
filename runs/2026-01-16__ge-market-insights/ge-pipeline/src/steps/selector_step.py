"""Generate curated deck variables from pipeline outputs."""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from ..runner.orchestrator import RunContext
from ..selector import build_deck_variables


def _resolve_target_lift(ctx: RunContext) -> float:
    params = ctx.cache.get("params", {})
    if isinstance(params, dict):
        value = params.get("TARGET_LIFT_PP")
        if isinstance(value, (int, float)):
            return float(value)
    guards = ctx.cfg.get("guards", {}) if isinstance(ctx.cfg, dict) else {}
    raw = guards.get("target_lift_pp_raw")
    if isinstance(raw, (int, float)):
        return float(raw) / 100.0 if raw > 1 else float(raw)
    return 0.02


def _selector_config(ctx: RunContext) -> Dict[str, Any]:
    defaults = {
        "recon_gap_max_pct": 0.30,
        "overlap_min": 0.30,
        "no_gain_window_pp": 1.0,
        "max_wins": 2,
        "max_no_gain": 1,
        "max_losses": 2,
        "min_members_for_losses": 20,
        "recent_year_cutoff": None,
        "min_members": 0,
        "min_controls": 0,
        "min_member_spend_6m": 0.0,
        "category_excludes": [],
        "manufacturer_focus": [],
    }
    selector_cfg: Dict[str, Any] = {}
    if isinstance(ctx.cfg, dict):
        raw_selector = ctx.cfg.get("selector")
        if not isinstance(raw_selector, dict):
            raw_selector = ctx.cfg.get("reports", {}).get("selector", {})
        selector_cfg = raw_selector or {}
    if not isinstance(selector_cfg, dict):
        return defaults
    out = defaults.copy()
    for key in defaults.keys():
        value = selector_cfg.get(key)
        if value is None:
            continue
        if key in {"recon_gap_max_pct", "overlap_min", "no_gain_window_pp", "min_member_spend_6m"}:
            try:
                out[key] = float(value)
            except (TypeError, ValueError):
                continue
        elif key in {"max_wins", "max_no_gain", "max_losses", "min_members_for_losses", "recent_year_cutoff", "min_members", "min_controls"}:
            try:
                out[key] = int(value)
            except (TypeError, ValueError):
                continue
        elif key in {"category_excludes", "manufacturer_focus"}:
            if isinstance(value, (list, tuple)):
                out[key] = [str(item).strip() for item in value if item not in (None, "")]
            elif isinstance(value, str):
                out[key] = [value.strip()] if value.strip() else []
        else:
            out[key] = value
    return out


def _git_commit(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None
    commit = result.stdout.strip()
    return commit or None


def _resolve_answers_df(ctx: RunContext) -> pd.DataFrame:
    export_cache = ctx.cache.get("export")
    if isinstance(export_cache, dict):
        answers = export_cache.get("answers_df")
        if isinstance(answers, pd.DataFrame):
            return answers
    answers_df = ctx.cache.get("answers_df")
    if isinstance(answers_df, pd.DataFrame):
        return answers_df
    return pd.DataFrame()


def _normalize_category(label: str) -> str:
    normalized = str(label or "").upper()
    normalized = normalized.replace("&", " AND ")
    normalized = re.sub(r"[^A-Z0-9]+", " ", normalized)
    return normalized.strip()


def _augment_with_reconciliation_metrics(df: pd.DataFrame, recon_summary: Optional[Dict[str, Any]]) -> pd.DataFrame:
    if df.empty or not isinstance(recon_summary, dict):
        return df
    output_dir = recon_summary.get("output_dir")
    if not output_dir:
        return df
    recon_dir = Path(output_dir)
    members_path = recon_dir / "members.csv"
    spend_path = recon_dir / "spend.csv"
    if not members_path.exists() or not spend_path.exists():
        return df

    try:
        members = pd.read_csv(members_path)
        spend = pd.read_csv(spend_path)
    except Exception:
        return df

    if "mapped_label" not in members.columns or "mapped_label" not in spend.columns:
        return df

    work = df.copy()
    if "category_id" not in work.columns:
        return df

    work["_norm_category"] = work["category_id"].apply(_normalize_category)
    members = members.copy()
    spend = spend.copy()
    members["_norm_category"] = members["mapped_label"].apply(_normalize_category)
    spend["_norm_category"] = spend["mapped_label"].apply(_normalize_category)

    merged = work.merge(
        members[["_norm_category", "facility_overlap_rate"]],
        on="_norm_category",
        how="left",
    )
    spend_metrics = spend[["_norm_category", "prd_6m_spend", "dashboard_6m_spend", "delta_spend"]]
    merged = merged.merge(spend_metrics, on="_norm_category", how="left")

    def _compute_gap(row: pd.Series) -> Optional[float]:
        prd = row.get("prd_6m_spend")
        dash = row.get("dashboard_6m_spend")
        delta = row.get("delta_spend")
        if pd.isna(prd) or pd.isna(dash) or pd.isna(delta):
            return None
        if abs(dash) < 1e-9:
            return None
        try:
            return float(delta) / float(dash)
        except ZeroDivisionError:
            return None

    merged["recon_spend_gap_pct"] = merged.apply(_compute_gap, axis=1)
    merged["facility_overlap_ratio"] = pd.to_numeric(merged.get("facility_overlap_rate"), errors="coerce")

    merged = merged.drop(columns=["facility_overlap_rate", "prd_6m_spend", "dashboard_6m_spend", "delta_spend", "_norm_category"], errors="ignore")
    return merged


@dataclass
class Step:
    """Generate deck_vars.json from PRD answers."""

    name: str = "selector"

    def run(self, ctx: RunContext) -> None:
        run_dir = Path(ctx.paths["run_dir"]).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        repo_root = Path(ctx.paths.get("repo_root", run_dir.parent))

        answers_df = _resolve_answers_df(ctx)
        reconciliation_summary = ctx.cache.get("reconciliation_summary")
        answers_df = _augment_with_reconciliation_metrics(answers_df, reconciliation_summary)
        ctx.cache["answers_df"] = answers_df
        target_lift = _resolve_target_lift(ctx)
        cfg = _selector_config(ctx)

        deck_payload = build_deck_variables(
            answers_df,
            target_lift=target_lift,
            recon_gap_max_pct=cfg["recon_gap_max_pct"],
            overlap_min=cfg["overlap_min"],
            no_gain_window_pp=cfg["no_gain_window_pp"],
            max_wins=cfg["max_wins"],
            max_no_gain=cfg["max_no_gain"],
            max_losses=cfg["max_losses"],
            min_members_for_losses=cfg["min_members_for_losses"],
            recent_year_cutoff=cfg.get("recent_year_cutoff"),
            min_members=cfg.get("min_members", 0),
            min_controls=cfg.get("min_controls", 0),
            min_member_spend_6m=cfg.get("min_member_spend_6m", 0.0),
            category_excludes=cfg.get("category_excludes"),
            manufacturer_focus=cfg.get("manufacturer_focus"),
            reconciliation_summary=reconciliation_summary if isinstance(reconciliation_summary, dict) else None,
        )

        snapshot_info = {
            "run_id": ctx.run_id,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "config_path": ctx.paths.get("config_path"),
            "source": str(run_dir / "prd_answers.csv"),
            "commit": _git_commit(repo_root),
        }
        deck_output = {"snapshot": snapshot_info, **deck_payload}

        output_path = run_dir / "deck_vars.json"
        output_path.write_text(json.dumps(deck_output, indent=2, allow_nan=False), encoding="utf-8")

        ctx.cache["deck_vars"] = deck_output
        ctx.logger.info(
            {
                "event": "deck_vars_generated",
                "path": str(output_path),
                "headline": deck_payload.get("headline", {}),
                "examples_counts": {key: len(value) for key, value in deck_payload.get("examples", {}).items()},
            }
        )
