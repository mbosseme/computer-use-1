"""Pipeline step for chart generation."""
from __future__ import annotations

import csv
import json
from datetime import datetime
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")  # noqa: E402  # pragma: no mutate - ensure headless backend
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter

from ..kpis import kpis
from ..runner.orchestrator import RunContext

_VALUE_COL = "awarded_share_6m"
_CLAMP_WARNING_PATTERN = re.compile(r"^(?P<label>.+)_clamped_from_(?P<month>-?\d+)$")
_AWARD_SUPPLIER_LOOKUP: Dict[str, str] | None = None


def _canonicalize_ids(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    work = df.copy()
    rename_pairs = {
        "program": "program_id",
        "category": "category_id",
        "entity_code": "facility_id",
        "facility": "facility_id",
    }
    for src, dest in rename_pairs.items():
        if src in work.columns and dest not in work.columns:
            work[dest] = work[src]
    for ident in ("program_id", "category_id", "facility_id"):
        if ident in work.columns:
            work[ident] = work[ident].astype(str)
    if "event_month" in work.columns:
        work["event_month"] = pd.to_numeric(work["event_month"], errors="coerce")
    return work


def _ensure_panel_columns(df: pd.DataFrame) -> pd.DataFrame:
    work = _canonicalize_ids(df)
    if not isinstance(work, pd.DataFrame) or work.empty:
        return work if isinstance(work, pd.DataFrame) else pd.DataFrame()
    for col in ("awarded_spend", "total_cat_spend", "awarded_share_6m"):
        if col not in work.columns:
            work[col] = np.nan
    if "awarded_share" in work.columns and work["awarded_spend"].isna().any():
        mask = (
            work["awarded_spend"].isna()
            & work["total_cat_spend"].notna()
            & work["awarded_share"].notna()
        )
        work.loc[mask, "awarded_spend"] = work.loc[mask, "awarded_share"] * work.loc[mask, "total_cat_spend"]
    for col in ("awarded_spend", "total_cat_spend", "awarded_share_6m", "event_month"):
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors="coerce")
    return work


def _rolling_sums(df: pd.DataFrame, window: int) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
    work = _ensure_panel_columns(df)
    if work.empty:
        return work
    idx = ["program_id", "category_id", "facility_id"]
    work = work.sort_values(idx + ["event_month"])
    work["awarded_spend_6m"] = (
        work.groupby(idx, sort=False)["awarded_spend"].transform(lambda s: s.rolling(window, min_periods=1).sum())
    )
    work["total_cat_spend_6m"] = (
        work.groupby(idx, sort=False)["total_cat_spend"].transform(lambda s: s.rolling(window, min_periods=1).sum())
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        work["awarded_share_6m_fac"] = work["awarded_spend_6m"] / work["total_cat_spend_6m"]
    return work


def _summarize_cohort(df: pd.DataFrame) -> pd.DataFrame:
    cohort_keys = ["program_id", "category_id", "event_month"]
    empty_cols = cohort_keys + [
        "awarded_spend_6m",
        "total_cat_spend_6m",
        "awarded_spend_1m",
        "total_cat_spend_1m",
        "facility_count",
        "awarded_share_6m_cohort",
        "awarded_share_1m_cohort",
    ]
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(columns=empty_cols)

    work = df.copy()
    agg_6m = work.groupby(cohort_keys)[["awarded_spend_6m", "total_cat_spend_6m"]].sum().reset_index()
    agg_1m = (
        work.groupby(cohort_keys)[["awarded_spend", "total_cat_spend"]]
        .sum()
        .reset_index()
        .rename(columns={"awarded_spend": "awarded_spend_1m", "total_cat_spend": "total_cat_spend_1m"})
    )
    counts = work.groupby(cohort_keys)["facility_id"].nunique().reset_index(name="facility_count")

    out = agg_6m.merge(agg_1m, on=cohort_keys, how="outer")
    out = out.merge(counts, on=cohort_keys, how="outer")
    for col in ("awarded_spend_6m", "total_cat_spend_6m", "awarded_spend_1m", "total_cat_spend_1m"):
        if col in out.columns:
            out[col] = out[col].fillna(0.0)
    out["facility_count"] = out.get("facility_count", pd.Series(dtype="Int64")).fillna(0).astype("Int64")

    with np.errstate(divide="ignore", invalid="ignore"):
        out["awarded_share_6m_cohort"] = np.where(
            out["total_cat_spend_6m"] != 0,
            out["awarded_spend_6m"] / out["total_cat_spend_6m"],
            np.nan,
        )
        out["awarded_share_1m_cohort"] = np.where(
            out["total_cat_spend_1m"] != 0,
            out["awarded_spend_1m"] / out["total_cat_spend_1m"],
            np.nan,
        )
    return out.sort_values(cohort_keys).reset_index(drop=True)


def _build_cohort_tables(
    members_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    window: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    mem_roll = _rolling_sums(members_df, window)
    ctl_roll = _rolling_sums(controls_df, window)
    return _summarize_cohort(mem_roll), _summarize_cohort(ctl_roll)


def _event_study_series_from_cohort(
    prog: str,
    cat: str,
    mem_cohort: pd.DataFrame,
    ctl_cohort: pd.DataFrame,
) -> Tuple[pd.Series | None, pd.Series | None, Dict[str, Any]]:
    metadata: Dict[str, Any] = {"status": "ok", "strategy": "cohort_weighted_single_month", "warnings": []}
    required_cols = {
        "program_id",
        "category_id",
        "event_month",
        "awarded_share_1m_cohort",
        "total_cat_spend_1m",
        "facility_count",
    }
    if not all(isinstance(df, pd.DataFrame) and not df.empty for df in (mem_cohort, ctl_cohort)):
        metadata.update({"status": "error", "reason": "cohort_tables_missing"})
        return None, None, metadata
    if not (required_cols <= set(mem_cohort.columns) and required_cols <= set(ctl_cohort.columns)):
        metadata.update({"status": "error", "reason": "single_month_columns_missing"})
        return None, None, metadata

    prog = str(prog)
    cat = str(cat)
    mem = mem_cohort.copy()
    ctl = ctl_cohort.copy()
    for frame in (mem, ctl):
        frame["program_id"] = frame["program_id"].astype(str)
        frame["category_id"] = frame["category_id"].astype(str)

    mem = mem[(mem["program_id"] == prog) & (mem["category_id"] == cat)].copy()
    ctl = ctl[(ctl["program_id"] == prog) & (ctl["category_id"] == cat)].copy()
    if mem.empty or ctl.empty:
        metadata.update({"status": "error", "reason": "empty_cohort"})
        return None, None, metadata

    for frame in (mem, ctl):
        frame["event_month"] = pd.to_numeric(frame["event_month"], errors="coerce").astype("Int64")
    mem = mem.dropna(subset=["event_month"])
    ctl = ctl.dropna(subset=["event_month"])
    mem["event_month"] = mem["event_month"].astype(int)
    ctl["event_month"] = ctl["event_month"].astype(int)

    mem_series = mem.set_index("event_month")["awarded_share_1m_cohort"].astype(float)
    ctl_series = ctl.set_index("event_month")["awarded_share_1m_cohort"].astype(float)
    mem_counts = mem.set_index("event_month")["facility_count"].astype(float)
    ctl_counts = ctl.set_index("event_month")["facility_count"].astype(float)
    mem_totals = mem.set_index("event_month")["total_cat_spend_1m"].astype(float)
    ctl_totals = ctl.set_index("event_month")["total_cat_spend_1m"].astype(float)

    months = sorted(set(mem_series.index) | set(ctl_series.index))
    mem_series = mem_series.reindex(months)
    ctl_series = ctl_series.reindex(months)
    mem_counts = mem_counts.reindex(months)
    ctl_counts = ctl_counts.reindex(months)
    mem_totals = mem_totals.reindex(months)
    ctl_totals = ctl_totals.reindex(months)

    zero_mask = (mem_totals <= 0) | (ctl_totals <= 0)
    zero_mask = zero_mask.fillna(True)
    if bool(zero_mask.any()):
        metadata.setdefault("warnings", []).append("dropped_zero_denom_months")
        mem_series = mem_series.mask(zero_mask)
        ctl_series = ctl_series.mask(zero_mask)

    mem_series = mem_series.dropna()
    ctl_series = ctl_series.dropna()
    common_idx = sorted(set(mem_series.index) & set(ctl_series.index))
    if not common_idx:
        metadata.update({"status": "error", "reason": "no_common_months"})
        return None, None, metadata

    mem_series = mem_series.reindex(common_idx)
    ctl_series = ctl_series.reindex(common_idx)
    mem_counts = mem_counts.reindex(common_idx)
    ctl_counts = ctl_counts.reindex(common_idx)
    metadata["facility_counts"] = {
        "members": _collect_counts(mem_counts),
        "controls": _collect_counts(ctl_counts),
    }

    mem_series = mem_series.sort_index()
    ctl_series = ctl_series.sort_index()
    return mem_series, ctl_series, metadata


def _laspeyres_series(
    prog: str,
    cat: str,
    members_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    *,
    exit_map: Optional[Dict[str, pd.Timestamp]] = None,
    weight_coverage_guard: float = 0.5,
) -> Tuple[pd.Series | None, pd.Series | None, Dict[str, Any]]:
    metadata: Dict[str, Any] = {"status": "ok", "strategy": "laspeyres", "warnings": []}
    if not all(isinstance(df, pd.DataFrame) and not df.empty for df in (members_df, controls_df)):
        metadata.update({"status": "error", "reason": "panel_missing"})
        return None, None, metadata

    members = kpis._standardize_panel(members_df)
    controls = kpis._standardize_panel(controls_df)
    prog = str(prog)
    cat = str(cat)
    member_slice = members[(members["program_id"] == prog) & (members["category_id"] == cat)]
    control_slice = controls[(controls["program_id"] == prog) & (controls["category_id"] == cat)]
    if member_slice.empty or control_slice.empty:
        metadata.update({"status": "error", "reason": "missing_panel_rows"})
        return None, None, metadata

    member_weights = kpis._member_weights(member_slice)
    control_weights = kpis._control_weights(control_slice)
    if member_weights.empty or control_weights.empty:
        metadata.update({"status": "error", "reason": "missing_t0_weights"})
        return None, None, metadata

    mask_meta: Dict[str, Any] = {}

    def _series_with_counts(
        df: pd.DataFrame,
        weights: pd.Series,
        *,
        drop_post_inactive: bool,
        label: str,
        metadata: Dict[str, Any],
    ) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        if df.empty or weights.empty:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        sub = df[df["facility_id"].isin(weights.index)].copy()
        if sub.empty or "awarded_share_6m" not in sub.columns:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        sub = sub.merge(weights.rename("w_i0"), left_on="facility_id", right_index=True, how="inner")
        sub, masked_exit = kpis._apply_dataset_exit_mask(sub, exit_map)
        if masked_exit:
            key = f"{label}_masked_dataset_exit"
            metadata.setdefault(key, set()).update(masked_exit)
        if drop_post_inactive:
            sub, masked_exposure = kpis.apply_exposure_mask(sub, consecutive_false=2, return_masked=True)
            if masked_exposure:
                key = f"{label}_masked_program_exit"
                metadata.setdefault(key, set()).update(masked_exposure)
        sub = sub.dropna(subset=["event_month"])
        if sub.empty:
            return (
                pd.Series(dtype=float),
                pd.Series(dtype=float),
                pd.Series(dtype=float),
                pd.Series(dtype=float),
            )
        sub["event_month"] = sub["event_month"].astype(int)
        dataset_cov = sub.groupby("event_month")["w_i0"].sum().sort_index()
        counts = sub.groupby("event_month")["facility_id"].nunique().astype(float).sort_index()

        def _weighted_mean(group: pd.DataFrame) -> float:
            g = group.dropna(subset=["awarded_share_6m", "w_i0"])
            if g.empty:
                return np.nan
            denom = g["w_i0"].sum()
            if denom == 0:
                return np.nan
            return float((g["awarded_share_6m"] * g["w_i0"]).sum() / denom)

        series = (
            sub.groupby("event_month", sort=True, group_keys=False)[["awarded_share_6m", "w_i0"]]
            .apply(_weighted_mean)
        )
        series = series.sort_index()
        final_cov = sub.groupby("event_month")["w_i0"].sum().sort_index().reindex(series.index, fill_value=0.0)
        dataset_cov = dataset_cov.reindex(series.index, fill_value=0.0)
        counts = counts.reindex(series.index, fill_value=0.0)
        return series, counts, dataset_cov, final_cov

    member_series, member_counts, member_dataset_cov, member_final_cov = _series_with_counts(
        member_slice,
        member_weights,
        drop_post_inactive=True,
        label="members",
        metadata=mask_meta,
    )
    control_series, control_counts, control_dataset_cov, control_final_cov = _series_with_counts(
        control_slice,
        control_weights,
        drop_post_inactive=False,
        label="controls",
        metadata=mask_meta,
    )
    if member_series.empty or control_series.empty:
        metadata.update({"status": "error", "reason": "empty_laspeyres_series"})
        return None, None, metadata

    common_idx = sorted(set(member_series.index) & set(control_series.index))
    if not common_idx:
        metadata.update({"status": "error", "reason": "laspeyres_no_common_months"})
        return None, None, metadata

    member_series = member_series.reindex(common_idx).sort_index()
    control_series = control_series.reindex(common_idx).sort_index()
    member_counts = member_counts.reindex(common_idx)
    control_counts = control_counts.reindex(common_idx)
    member_dataset_cov = member_dataset_cov.reindex(common_idx)
    control_dataset_cov = control_dataset_cov.reindex(common_idx)
    member_final_cov = member_final_cov.reindex(common_idx)
    control_final_cov = control_final_cov.reindex(common_idx)

    metadata["facility_counts"] = {
        "members": _collect_counts(member_counts),
        "controls": _collect_counts(control_counts),
    }

    (
        member_series,
        control_series,
        member_dataset_cov,
        control_dataset_cov,
        member_final_cov,
        control_final_cov,
        coverage_meta,
    ) = kpis._apply_weight_coverage_guard(
        member_series,
        control_series,
        member_dataset_cov if isinstance(member_dataset_cov, pd.Series) else pd.Series(dtype=float),
        control_dataset_cov if isinstance(control_dataset_cov, pd.Series) else pd.Series(dtype=float),
        member_final_cov if isinstance(member_final_cov, pd.Series) else pd.Series(dtype=float),
        control_final_cov if isinstance(control_final_cov, pd.Series) else pd.Series(dtype=float),
        weight_coverage_guard,
    )
    metadata["weight_coverage_clamped"] = bool(coverage_meta.get("weight_coverage_clamped", False))
    metadata["weight_coverage_clamp_month"] = coverage_meta.get("weight_coverage_clamp_month", pd.NA)
    metadata["member_weight_coverage_min"] = coverage_meta.get("member_weight_coverage_min", np.nan)
    metadata["control_weight_coverage_min"] = coverage_meta.get("control_weight_coverage_min", np.nan)
    if metadata["weight_coverage_clamped"]:
        clamp_month = metadata["weight_coverage_clamp_month"]
        metadata.setdefault("warnings", []).append(f"weight_coverage_clamped_from_{clamp_month}")
    if member_series.empty or control_series.empty:
        metadata.update({"status": "error", "reason": "weight_coverage_clamp_empty"})
        return None, None, metadata

    member_counts = member_counts.reindex(member_series.index)
    control_counts = control_counts.reindex(control_series.index)
    member_dataset_cov = member_dataset_cov.reindex(member_series.index)
    control_dataset_cov = control_dataset_cov.reindex(control_series.index)
    member_final_cov = member_final_cov.reindex(member_series.index)
    control_final_cov = control_final_cov.reindex(control_series.index)

    if mask_meta.get("members_masked_dataset_exit"):
        metadata["members_masked_dataset_exit_count"] = len(mask_meta["members_masked_dataset_exit"])
    if mask_meta.get("members_masked_program_exit"):
        metadata["members_masked_program_exit_count"] = len(mask_meta["members_masked_program_exit"])
    if mask_meta.get("controls_masked_dataset_exit"):
        metadata["controls_masked_dataset_exit_count"] = len(mask_meta["controls_masked_dataset_exit"])

    return member_series, control_series, metadata


def _get_answers_row(answers_df: pd.DataFrame, prog: str, cat: str) -> pd.Series | None:
    if not isinstance(answers_df, pd.DataFrame) or answers_df.empty:
        return None
    prog = str(prog)
    cat = str(cat)
    df = answers_df.copy()
    mask = (df["program_id"].astype(str) == prog) & (df["category_id"].astype(str) == cat)
    if not mask.any():
        return None
    return df.loc[mask].iloc[0]


def _load_awarded_supplier_lookup() -> Dict[str, str]:
    global _AWARD_SUPPLIER_LOOKUP
    if _AWARD_SUPPLIER_LOOKUP is not None:
        return _AWARD_SUPPLIER_LOOKUP

    mapping: Dict[str, str] = {}
    repo_root = Path(__file__).resolve().parents[2]
    lookup_path = repo_root / "recon" / "dashboard_export_clean.csv"
    if lookup_path.exists():
        try:
            with lookup_path.open(newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                if reader.fieldnames:
                    normalized = {header.strip().lower(): header for header in reader.fieldnames if header}
                else:
                    normalized = {}
                code_key = normalized.get("mfr entity code")
                name_key = normalized.get("mfr name") or normalized.get("awarded supplier")
                for row in reader:
                    code_raw = row.get(code_key, "") if code_key else ""
                    name_raw = row.get(name_key, "") if name_key else ""
                    code = str(code_raw).strip()
                    name = str(name_raw).strip()
                    if code and name and code not in mapping:
                        mapping[code] = name
        except Exception:
            mapping = {}
    _AWARD_SUPPLIER_LOOKUP = mapping
    return mapping


def _parse_awarded_suppliers(raw: Any) -> list[str]:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return []
    text = str(raw).strip()
    if not text or text in {"<NA>", "nan"}:
        return []
    if text in {"[]", "{}", "()"}:
        return []

    single_quotes = re.findall(r"'([^']+)'", text)
    if single_quotes:
        return [token.strip() for token in single_quotes if token.strip()]
    double_quotes = re.findall(r'"([^"]+)"', text)
    if double_quotes:
        return [token.strip() for token in double_quotes if token.strip()]

    if "|" in text:
        return [token.strip() for token in text.split("|") if token.strip()]
    if "," in text:
        return [token.strip() for token in text.split(",") if token.strip()]
    return [text] if text else []


def _format_awarded_token(token: str, lookup: Dict[str, str]) -> Optional[str]:
    value = token.strip()
    if not value or value in {"<NA>", "nan"}:
        return None
    value = value.strip("'\"")

    for pattern in (r"^(?P<name>.+?)\s*\[(?P<code>[^\]]+)\]\s*$", r"^(?P<name>.+?)\s*\((?P<code>[^)]+)\)\s*$"):
        match = re.match(pattern, value)
        if match:
            name = match.group("name").strip()
            code = match.group("code").strip()
            label = name or lookup.get(code) or code
            if code:
                return f"{label} ({code})"
            return label

    if ":" in value:
        name_part, code_part = [part.strip() for part in value.split(":", 1)]
        if code_part:
            label = name_part or lookup.get(code_part) or code_part
            return f"{label} ({code_part})"

    if "-" in value and re.search(r"[A-Za-z]\d", value.split("-")[-1].strip()):
        name_part, code_part = [part.strip() for part in value.rsplit("-", 1)]
        if code_part:
            label = name_part or lookup.get(code_part) or code_part
            return f"{label} ({code_part})"

    if re.fullmatch(r"[A-Za-z0-9]+", value):
        code = value
        label = lookup.get(code) or code
        return f"{label} ({code})"

    return value


def _awarded_set_title_line(answers_df: pd.DataFrame, prog: str, cat: str) -> str:
    row = _get_answers_row(answers_df, prog, cat)
    lookup = _load_awarded_supplier_lookup()
    tokens = _parse_awarded_suppliers(row.get("t0_awarded_suppliers")) if row is not None else []

    formatted: list[str] = []
    for token in tokens:
        entry = _format_awarded_token(token, lookup)
        if entry and entry not in formatted:
            formatted.append(entry)
    if not formatted:
        formatted.append("None")
    return f"Awarded set: [{', '.join(formatted)}]"


def _collect_counts(series: pd.Series | None) -> Dict[str, float]:
    result: Dict[str, float] = {}
    if not isinstance(series, pd.Series) or series.empty:
        return result
    numeric_types = (int, float, np.integer, np.floating, str)
    for idx, val in series.dropna().items():
        if isinstance(idx, numeric_types):
            try:
                numeric_idx = float(idx)
                result[str(int(numeric_idx))] = float(val)
            except (TypeError, ValueError):
                continue
    return result


def _merge_chart_warnings(
    dynamic_warnings: Iterable[str] | None,
    laspeyres_warnings: Iterable[str] | None,
) -> list[str]:
    def _normalize(warnings: Iterable[str] | None) -> list[str]:
        if warnings is None:
            return []
        normalized: list[str] = []
        for warning in warnings:
            if not warning:
                continue
            text = str(warning).strip()
            if text:
                normalized.append(text)
        return normalized

    normalized_dynamic = _normalize(dynamic_warnings)
    normalized_laspeyres = _normalize(laspeyres_warnings)
    clamp_candidates: list[tuple[Optional[int], int, str]] = []
    merged: list[str] = []
    seen: set[str] = set()

    def _ingest(warnings: list[str], offset: int) -> None:
        for idx, warning in enumerate(warnings):
            match = _CLAMP_WARNING_PATTERN.match(warning)
            if match:
                month_text = match.group("month")
                try:
                    month_val: Optional[int] = int(month_text)
                except ValueError:
                    month_val = None
                clamp_candidates.append((month_val, offset + idx, warning))
            else:
                if warning not in seen:
                    merged.append(warning)
                    seen.add(warning)

    _ingest(normalized_dynamic, 0)
    _ingest(normalized_laspeyres, 1000)

    valid_clamps = [candidate for candidate in clamp_candidates if candidate[0] is not None]
    if valid_clamps:
        _, _, earliest_warning = min(valid_clamps, key=lambda candidate: (candidate[0], candidate[1]))
    elif clamp_candidates:
        earliest_warning = min(clamp_candidates, key=lambda candidate: candidate[1])[2]
    else:
        earliest_warning = None

    if earliest_warning and earliest_warning not in seen:
        merged.append(earliest_warning)
    return merged


def _format_warning_label(warning: str, lasp_meta: Dict[str, Any] | None = None) -> str:
    def _coerce_month(value: Any) -> Optional[int]:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        if isinstance(value, pd.Series):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    if not warning:
        return ""
    warning = str(warning)
    if warning.startswith("weight_coverage_clamped_from_"):
        try:
            month = int(warning.rsplit("_", 1)[-1])
            return f"Weight coverage clamp from {month}"
        except ValueError:
            return "Weight coverage clamp applied"
    if warning.startswith("laspeyres_"):
        reason = warning[len("laspeyres_"):]
        clamp_month = None
        if isinstance(lasp_meta, dict):
            clamp_month = _coerce_month(lasp_meta.get("weight_coverage_clamp_month"))
        if reason == "weight_coverage_clamp_empty":
            suffix = f" from {clamp_month}" if clamp_month is not None else ""
            return f"Laspeyres series unavailable: weight coverage guard removed all months{suffix}"
        if reason == "series_generation_failed":
            return "Laspeyres series unavailable: generation failed"
        return f"Laspeyres series unavailable: {reason.replace('_', ' ')}"
    return warning.replace("_", " ")


def _annotate_gaps(ax: Axes, answers_df: pd.DataFrame, prog: str, cat: str) -> None:
    row = _get_answers_row(answers_df, prog, cat)
    if row is None:
        return
    lines: list[str] = []
    pre_gap = None
    post_gap = None
    member_pre = row.get("member_pre_mean")
    control_pre = row.get("control_pre_mean")
    if pd.notna(member_pre) and pd.notna(control_pre):
        pre_gap = float(member_pre) - float(control_pre)
    member_post = row.get("member_post_0_6")
    control_post = row.get("control_post_0_6")
    if pd.notna(member_post) and pd.notna(control_post):
        post_gap = float(member_post) - float(control_post)
    delta_val = row.get("delta_0_6")
    delta_0_6 = float(delta_val) if pd.notna(delta_val) else None
    if pre_gap is not None:
        lines.append(f"Pre gap (-6:-1): {float(pre_gap):+.2%}")
    if post_gap is not None:
        lines.append(f"Post gap (0:6): {float(post_gap):+.2%}")
    if delta_0_6 is not None:
        lines.append(f"Δ0-6 (Laspeyres): {float(delta_0_6):+.2%}")
    if not lines:
        return
    ax.text(
        0.98,
        0.02,
        "\n".join(lines),
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        bbox=dict(facecolor="white", alpha=0.75, edgecolor="none"),
    )


def _slug(value: Any) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_").upper()


def _relative_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


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


def save_event_study_chart(
    prog: str,
    cat: str,
    members_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    mem_cohort: pd.DataFrame,
    ctl_cohort: pd.DataFrame,
    answers_df: pd.DataFrame,
    output_path: Path,
    *,
    allow_thin: bool,
    min_pre_months: int,
    dataset_exit_map: Optional[Dict[str, pd.Timestamp]],
    weight_coverage_guard: float,
    gap_output_path: Path | None = None,
) -> Tuple[bool, Dict[str, Any] | str]:
    output_path = output_path if isinstance(output_path, Path) else Path(output_path)
    gap_output_path = gap_output_path if (gap_output_path is None or isinstance(gap_output_path, Path)) else Path(gap_output_path)

    mem_series, ctl_series, meta = _event_study_series_from_cohort(prog, cat, mem_cohort, ctl_cohort)
    if meta.get("status") != "ok" or mem_series is None or ctl_series is None:
        return False, meta.get("reason", "series_generation_failed")

    pre_mem = mem_series[mem_series.index < 0].dropna()
    pre_ctl = ctl_series[ctl_series.index < 0].dropna()
    if not allow_thin and (len(pre_mem) < min_pre_months or len(pre_ctl) < min_pre_months):
        return False, f"thin_pre({len(pre_mem)},{len(pre_ctl)})"

    fig, ax = plt.subplots(figsize=(10, 6))
    member_line = ax.plot(
        list(mem_series.index),
        mem_series.to_numpy(),
        linestyle=":",
        label="Members (dynamic roster, single-month share)",
    )[0]
    control_line = ax.plot(
        list(ctl_series.index),
        ctl_series.to_numpy(),
        linestyle=":",
        label="Controls (dynamic roster, single-month share)",
    )[0]

    lasp_mem, lasp_ctl, lasp_meta = _laspeyres_series(
        prog,
        cat,
        members_df,
        controls_df,
        exit_map=dataset_exit_map,
        weight_coverage_guard=weight_coverage_guard,
    )
    if lasp_meta.get("status") == "ok" and lasp_mem is not None and lasp_ctl is not None:
        ax.plot(
            list(lasp_mem.index),
            lasp_mem.to_numpy(),
            linestyle="-",
            color=member_line.get_color(),
            label="Members (Laspeyres t0 weights, 6m KPI)",
        )
        ax.plot(
            list(lasp_ctl.index),
            lasp_ctl.to_numpy(),
            linestyle="-",
            color=control_line.get_color(),
            label="Controls (Laspeyres t0 weights, 6m KPI)",
        )
    else:
        reason = lasp_meta.get("reason")
        if reason:
            warning = f"laspeyres_{reason}"
            warnings = meta.setdefault("warnings", [])
            if warning not in warnings:
                warnings.append(warning)

    ax.axvline(0, color="k", linestyle="--", label="t0 (Go-live)")
    awarded_title_line = _awarded_set_title_line(answers_df, prog, cat)
    chart_warnings = _merge_chart_warnings(meta.get("warnings"), lasp_meta.get("warnings"))
    friendly_warnings = [_format_warning_label(warning, lasp_meta) for warning in chart_warnings]
    title_lines = [
        f"Event Study: {prog} / {cat}",
        awarded_title_line,
    ]
    ax.set_title("\n".join(title_lines))
    tick_months: set[int] = set()
    tick_months.update(map(int, mem_series.index.tolist()))
    tick_months.update(map(int, ctl_series.index.tolist()))
    if lasp_meta.get("status") == "ok" and lasp_mem is not None and lasp_ctl is not None:
        tick_months.update(map(int, lasp_mem.index.tolist()))
        tick_months.update(map(int, lasp_ctl.index.tolist()))
    sorted_ticks = sorted(tick_months)
    base_month_value = None
    answers_row = _get_answers_row(answers_df, prog, cat)
    if isinstance(answers_row, pd.Series):
        base_month_value = answers_row.get("t0_event_month")
    base_dt = None
    try:
        if isinstance(base_month_value, pd.Timestamp):
            base_dt = base_month_value.to_pydatetime()
        elif isinstance(base_month_value, str):
            stripped = base_month_value.strip()
            if stripped:
                base_dt = datetime.strptime(stripped, "%Y-%m")
        elif base_month_value is not None and not pd.isna(base_month_value):
            stripped = str(base_month_value).strip()
            if stripped:
                base_dt = datetime.strptime(stripped, "%Y-%m")
    except Exception:
        base_dt = None
    if base_dt is not None:
        def _format_month(event_month: Any) -> str:
            try:
                offset = int(event_month)
            except (TypeError, ValueError):
                return ""
            month_index = base_dt.month - 1 + offset
            year = base_dt.year + month_index // 12
            month = month_index % 12 + 1
            return datetime(year, month, 1).strftime("%b %Y")
        if sorted_ticks:
            ax.set_xticks(sorted_ticks)
            labels = []
            for tick in sorted_ticks:
                label = _format_month(tick)
                labels.append(f"{tick} ({label})" if label else str(tick))
            ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_xlabel(f"Event Month (t0: {base_dt.strftime('%b %Y')})")
    else:
        if sorted_ticks:
            ax.set_xticks(sorted_ticks)
        ax.set_xlabel("Event Month")
    ax.set_ylabel("Awarded Share")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.1%}"))
    ax.grid(True, which="major", linestyle="--", alpha=0.4)
    ax.legend()

    _annotate_gaps(ax, answers_df, prog, cat)

    if friendly_warnings:
        warning_text = "\n".join(friendly_warnings)
        ax.text(
            0.02,
            0.02,
            warning_text,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            bbox=dict(facecolor="mistyrose", alpha=0.8, edgecolor="none"),
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    info: Dict[str, Any] = {
        "status": meta.get("status", "unknown"),
        "warnings": friendly_warnings,
        "laspeyres_status": lasp_meta.get("status", "unknown"),
    }
    if isinstance(lasp_meta, dict):
        info["weight_coverage_clamped"] = bool(lasp_meta.get("weight_coverage_clamped", False))
        info["weight_coverage_clamp_month"] = lasp_meta.get("weight_coverage_clamp_month", pd.NA)
    if lasp_meta.get("status") == "ok" and lasp_mem is not None and lasp_ctl is not None and gap_output_path is not None:
        gap_output_path.parent.mkdir(parents=True, exist_ok=True)
        gap_fig, gap_ax = plt.subplots(figsize=(10, 6))
        gap_member_line = gap_ax.plot(
            list(lasp_mem.index),
            lasp_mem.to_numpy(),
            linestyle="-",
            color=member_line.get_color(),
            label="Members (Laspeyres t0 weights, 6m KPI)",
        )[0]
        gap_ax.plot(
            list(lasp_ctl.index),
            lasp_ctl.to_numpy(),
            linestyle="-",
            color=control_line.get_color(),
            label="Controls (Laspeyres t0 weights, 6m KPI)",
        )
        gap_ax.fill_between(
            list(lasp_mem.index),
            lasp_mem.to_numpy(),
            lasp_ctl.to_numpy(),
            color=gap_member_line.get_color(),
            alpha=0.15,
            label=None,
        )
        gap_ax.axvline(0, color="k", linestyle="--", label="t0 (Go-live)")
        gap_title_lines = [
            f"Event Study (Laspeyres Gap): {prog} / {cat}",
            awarded_title_line,
        ]
        gap_ax.set_title("\n".join(gap_title_lines))
        if base_dt is not None:
            if sorted_ticks:
                gap_ax.set_xticks(sorted_ticks)
                labels = []
                for tick in sorted_ticks:
                    try:
                        offset = int(tick)
                    except (TypeError, ValueError):
                        labels.append(str(tick))
                        continue
                    month_index = base_dt.month - 1 + offset
                    year = base_dt.year + month_index // 12
                    month = month_index % 12 + 1
                    label = datetime(year, month, 1).strftime("%b %Y")
                    labels.append(f"{offset} ({label})")
                gap_ax.set_xticklabels(labels, rotation=45, ha="right")
            gap_ax.set_xlabel(f"Event Month (t0: {base_dt.strftime('%b %Y')})")
        else:
            if sorted_ticks:
                gap_ax.set_xticks(sorted_ticks)
            gap_ax.set_xlabel("Event Month")
        gap_ax.set_ylabel("Awarded Share")
        gap_ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.1%}"))
        gap_ax.grid(True, which="major", linestyle="--", alpha=0.4)
        gap_ax.legend()
        _annotate_gaps(gap_ax, answers_df, prog, cat)
        if friendly_warnings:
            warning_text = "\n".join(friendly_warnings)
            gap_ax.text(
                0.02,
                0.02,
                warning_text,
                transform=gap_ax.transAxes,
                ha="left",
                va="bottom",
                bbox=dict(facecolor="mistyrose", alpha=0.8, edgecolor="none"),
            )
        gap_fig.savefig(gap_output_path, bbox_inches="tight")
        plt.close(gap_fig)
        info["gap_chart_path"] = gap_output_path
    if lasp_meta.get("status") != "ok" and lasp_meta.get("reason"):
        info["laspeyres_reason"] = lasp_meta["reason"]
    return True, info


def _iter_rank_rows(df: pd.DataFrame) -> Iterator[Dict[str, Any]]:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return iter(())
    def _generator() -> Iterator[Dict[str, Any]]:
        for _, row in df.iterrows():
            yield {col: row[col] for col in df.columns}
    return _generator()


@dataclass
class Step:
    """Charts step wrapping notebook plotting logic."""

    name: str = "charts"

    def run(self, ctx: RunContext) -> None:
        cfg = ctx.cfg if isinstance(ctx.cfg, dict) else {}
        run_cfg = cfg.get("run", {}) if isinstance(cfg, dict) else {}
        if isinstance(run_cfg, dict) and not run_cfg.get("write_charts", True):
            ctx.logger.info({"event": "charts_skipped", "reason": "write_charts_disabled"})
            return

        panels: Dict[str, pd.DataFrame] = ctx.cache.get("panels", {})  # type: ignore[assignment]
        if not panels:
            ctx.logger.info({"event": "charts_skipped", "reason": "panels_missing"})
            return

        members_df = panels.get("shares_member_df", pd.DataFrame())
        controls_df = panels.get("shares_control_df", pd.DataFrame())
        if members_df.empty or controls_df.empty:
            ctx.logger.info({"event": "charts_skipped", "reason": "panel_frames_empty"})
            return
        dataset_exit_map = panels.get("dataset_exit_map", {})

        answers_df = ctx.cache.get("answers_df", pd.DataFrame())
        if not isinstance(answers_df, pd.DataFrame) or answers_df.empty:
            ctx.logger.info({"event": "charts_skipped", "reason": "answers_df_missing"})
            return

        event_rank_df = ctx.cache.get("event_study_ranking_df")
        if isinstance(event_rank_df, pd.DataFrame) and not event_rank_df.empty:
            ranking_df = event_rank_df.copy()
        else:
            ranking_df = answers_df.copy()

        if not ranking_df.empty:
            sort_cols = ["member_t0_total_spend_6m", "delta_7_12"]
            existing_cols = [col for col in sort_cols if col in ranking_df.columns]
            ranking_df = ranking_df.sort_values(by=existing_cols, ascending=False, na_position="last") if existing_cols else ranking_df

        topn_df = ctx.cache.get("topn_lift_ranking_df")
        if not isinstance(topn_df, pd.DataFrame) or topn_df.empty:
            topn_limit = max(0, int(_derive_topn(cfg)))
            topn_df = ranking_df.head(topn_limit).copy() if topn_limit > 0 else pd.DataFrame(columns=ranking_df.columns)

        result_sheets_dir = Path(ctx.paths["result_sheets_dir"]).resolve()
        run_dir = Path(ctx.paths["run_dir"]).resolve()
        repo_root = Path(ctx.paths["repo_root"]).resolve()
        result_sheets_dir.mkdir(parents=True, exist_ok=True)

        window_params = ctx.cache.get("window_params", {})
        rolling_window = int(window_params.get("ROLLING_M", 6) or 6)
        min_pre_months = int(window_params.get("MIN_PRE_MONTHS", 3) or 3)

        charts_cfg = cfg.get("charts", {}) if isinstance(cfg, dict) else {}
        allow_thin = bool(charts_cfg.get("allow_thin_pre", False))
        if isinstance(charts_cfg, dict) and "min_pre_months" in charts_cfg:
            min_pre_months = int(charts_cfg["min_pre_months"])
        params = ctx.cache.get("params", {})
        if not isinstance(params, dict):
            params = {}
        weight_guard = float(params.get("WEIGHT_COVERAGE_GUARD", 0.5))

        mem_cohort, ctl_cohort = _build_cohort_tables(members_df, controls_df, rolling_window)
        if mem_cohort.empty or ctl_cohort.empty:
            ctx.logger.info({"event": "charts_skipped", "reason": "cohort_tables_empty"})
            return

        ctx.cache["mem_cohort_monthly"] = mem_cohort
        ctx.cache["ctl_cohort_monthly"] = ctl_cohort

        written: list[Dict[str, Any]] = []
        skipped: list[Dict[str, Any]] = []
        warnings: list[Dict[str, Any]] = []

        for row in _iter_rank_rows(topn_df):
            prog = row.get("program_id")
            cat = row.get("category_id")
            if prog is None or cat is None or (pd.isna(prog) or pd.isna(cat)):
                continue
            prog_str = str(prog)
            cat_str = str(cat)
            base_slug = f"{_slug(prog_str)}_{_slug(cat_str)}"
            filename = f"event_{base_slug}.png"
            gap_filename = f"event_laspeyres_{base_slug}.png"
            out_path = result_sheets_dir / filename
            gap_path = result_sheets_dir / gap_filename
            ok, info = save_event_study_chart(
                prog_str,
                cat_str,
                members_df,
                controls_df,
                mem_cohort,
                ctl_cohort,
                answers_df,
                out_path,
                allow_thin=allow_thin,
                min_pre_months=min_pre_months,
                dataset_exit_map=dataset_exit_map if isinstance(dataset_exit_map, dict) else {},
                weight_coverage_guard=weight_guard,
                gap_output_path=gap_path,
            )
            if ok:
                main_entry = {"program_id": prog_str, "category_id": cat_str, "path": _relative_path(out_path, repo_root)}
                written.append(main_entry)
                if isinstance(info, dict):
                    gap_chart_path = info.get("gap_chart_path")
                    if isinstance(gap_chart_path, Path):
                        written.append(
                            {
                                "program_id": prog_str,
                                "category_id": cat_str,
                                "path": _relative_path(gap_chart_path, repo_root),
                                "variant": "laspeyres_gap",
                            }
                        )
                    if info.get("warnings"):
                        warnings.append({"program_id": prog_str, "category_id": cat_str, "warnings": info["warnings"]})
            else:
                reason = info if isinstance(info, str) else "unknown"
                skipped.append({"program_id": prog_str, "category_id": cat_str, "reason": reason})

        chart_files = sorted(p.name for p in result_sheets_dir.glob("*.png"))
        charts_summary = {
            "count": len(chart_files),
            "files": [str(Path("result_sheets") / name) for name in chart_files],
            "written": written,
            "skipped": skipped,
            "warnings": warnings,
            "allow_thin_pre": allow_thin,
            "min_pre_months": min_pre_months,
        }
        ctx.cache["charts"] = charts_summary

        export_cache = ctx.cache.get("export", {})
        artifacts = export_cache.get("artifacts") if isinstance(export_cache, dict) else None
        if isinstance(artifacts, dict):
            artifacts["result_sheets/"] = {
                "path": _relative_path(result_sheets_dir, repo_root),
                "rows": len(chart_files),
                "exists": bool(chart_files),
                "files": [str(Path("result_sheets") / name) for name in chart_files],
            }

        manifest_path = run_dir / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
            except json.JSONDecodeError:
                manifest = {}
        else:
            manifest = {}
        manifest.setdefault("artifacts", {})
        manifest["artifacts"]["result_sheets/"] = {
            "path": _relative_path(result_sheets_dir, repo_root),
            "rows": len(chart_files),
            "exists": bool(chart_files),
            "files": [str(Path("result_sheets") / name) for name in chart_files],
        }
        manifest["charts"] = charts_summary
        manifest_path.write_text(json.dumps(manifest, indent=2))

        ctx.logger.info(
            {
                "event": "charts_complete",
                "charts_written": len(written),
                "charts_skipped": len(skipped),
                "warnings": len(warnings),
            }
        )
