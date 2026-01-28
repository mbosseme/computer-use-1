"""Pipeline step for KPI computations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import numpy as np
import pandas as pd

from ..kpis import kpis
from ..runner.orchestrator import RunContext


def _merge_sufficiency(base: pd.DataFrame, suff: pd.DataFrame) -> pd.DataFrame:
    if suff is None or not isinstance(suff, pd.DataFrame) or suff.empty:
        return base
    work = base.merge(suff, on=["program_id", "category_id"], how="outer", suffixes=("", "_suff"))
    for col in [
        "N_members",
        "N_controls",
        "N_members_measured",
        "N_controls_measured",
        "member_pre_months",
        "control_pre_months",
        "eligible_for_delta",
        "delta_missing_reason",
        "t0_event_month",
    ]:
        suff_col = f"{col}_suff"
        if suff_col in work.columns:
            if col in work.columns:
                work[col] = work[col].where(work[col].notna(), work[suff_col])
            else:
                work[col] = work[suff_col]
            work.drop(columns=[suff_col], inplace=True)
    for col in [
        "N_members",
        "N_controls",
        "N_members_measured",
        "N_controls_measured",
        "member_pre_months",
        "control_pre_months",
    ]:
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors="coerce").astype("Int64")
    if "t0_event_month" in work.columns:
        work["t0_event_month"] = work["t0_event_month"].astype("string")
    if "eligible_for_delta" in work.columns:
        eligible = work["eligible_for_delta"].astype("boolean", copy=False).fillna(False)
    else:
        eligible = pd.Series(False, index=work.index, dtype="boolean")
    work["eligible_for_delta"] = eligible.astype(bool)
    if "delta_missing_reason" in work.columns:
        work["delta_missing_reason"] = work["delta_missing_reason"].replace("", pd.NA).fillna("delta_unavailable")
    else:
        work["delta_missing_reason"] = "delta_unavailable"
    object_cols = work.select_dtypes(include="object").columns
    for col in object_cols:
        series = work[col]
        if series.isna().any():
            work[col] = pd.Series(
                [np.nan if pd.isna(value) else value for value in series],
                index=series.index,
                dtype=object,
            )
    return work


def _apply_common_month_flags(df: pd.DataFrame, min_common_months: int) -> pd.DataFrame:
    for src, label in [
        ("pre_common_months", "has_pre_common_ge_MIN"),
        ("post06_common_months", "has_post06_common_ge_MIN"),
        ("post712_common_months", "has_post712_common_ge_MIN"),
    ]:
        if src in df.columns:
            vals = pd.to_numeric(df[src], errors="coerce").fillna(0)
            df[label] = (vals >= min_common_months).astype(bool)
        else:
            df[label] = False
    return df


def _award_metadata(members_df: pd.DataFrame, awarded_df: pd.DataFrame) -> pd.DataFrame:
    if not all(
        isinstance(df, pd.DataFrame) and not df.empty
        for df in (members_df, awarded_df)
    ):
        return pd.DataFrame(columns=["program_id", "category_id", "t0_awarded_suppliers", "controls_other_pg_overlap_excluded"])
    required_members = {"program_id", "category_id", "month", "event_month"}
    required_awards = {"program_id", "category_id", "month", "awarded_block"}
    if not (required_members <= set(members_df.columns) and required_awards <= set(awarded_df.columns)):
        return pd.DataFrame(columns=["program_id", "category_id", "t0_awarded_suppliers", "controls_other_pg_overlap_excluded"])

    shares = members_df.copy()
    shares["program_id"] = shares["program_id"].astype(str)
    shares["category_id"] = shares["category_id"].astype(str)
    anchor = (
        shares.loc[shares["event_month"] == 0, ["program_id", "category_id", "month"]]
        .dropna()
        .copy()
    )
    if anchor.empty:
        return pd.DataFrame(columns=["program_id", "category_id", "t0_awarded_suppliers", "controls_other_pg_overlap_excluded"])
    anchor["t0_month"] = pd.to_datetime(anchor["month"], errors="coerce")
    anchor = anchor.drop(columns="month").dropna(subset=["t0_month"]).drop_duplicates(subset=["program_id", "category_id"])

    awards = awarded_df.copy()
    awards["program_id"] = awards["program_id"].astype(str)
    awards["category_id"] = awards["category_id"].astype(str)
    awards["month"] = pd.to_datetime(awards["month"], errors="coerce")

    merged = anchor.merge(
        awards,
        left_on=["program_id", "category_id", "t0_month"],
        right_on=["program_id", "category_id", "month"],
        how="left",
    )
    if merged.empty:
        return pd.DataFrame(columns=["program_id", "category_id", "t0_awarded_suppliers", "controls_other_pg_overlap_excluded"])

    def _normalize(value: Any) -> list[str]:
        if isinstance(value, (list, tuple, set)):
            cleaned = {str(v).strip() for v in value if v is not None and str(v).strip()}
            return sorted(cleaned)
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return []
        text = str(value).strip()
        return [text] if text else []

    def _pg(program: Any) -> str | None:
        if program is None or (isinstance(program, float) and pd.isna(program)):
            return None
        label = str(program).strip().lower()
        if "surpass" in label:
            return "surpass"
        if "ascend" in label:
            return "ascend"
        return None

    merged["t0_awarded_suppliers_list"] = merged["awarded_block"].apply(_normalize)
    merged["t0_awarded_suppliers"] = merged["t0_awarded_suppliers_list"].apply(lambda tokens: "|".join(tokens))
    merged["pg_tag"] = merged["program_id"].apply(_pg)
    merged["other_pg_tag"] = merged["pg_tag"].map({"surpass": "ascend", "ascend": "surpass"})

    lookup = (
        merged[["category_id", "pg_tag", "t0_awarded_suppliers_list", "program_id"]]
        .dropna(subset=["pg_tag"])
        .drop_duplicates(subset=["category_id", "pg_tag"])
        .rename(columns={
            "pg_tag": "lookup_pg_tag",
            "t0_awarded_suppliers_list": "other_awards_list",
            "program_id": "other_program_id",
        })
    )

    merged["award_set"] = merged["t0_awarded_suppliers_list"].apply(lambda tokens: frozenset(tokens))
    merged = merged.merge(
        lookup,
        left_on=["category_id", "other_pg_tag"],
        right_on=["category_id", "lookup_pg_tag"],
        how="left",
    )
    merged["other_award_set"] = merged["other_awards_list"].apply(
        lambda tokens: frozenset(tokens) if isinstance(tokens, list) else frozenset()
    )
    merged["controls_other_pg_overlap_excluded"] = (
        merged["other_pg_tag"].notna()
        & merged["award_set"].apply(lambda s: len(s) > 0)
        & (merged["award_set"] == merged["other_award_set"])
    )

    return (
        merged[["program_id", "category_id", "t0_awarded_suppliers", "controls_other_pg_overlap_excluded"]]
        .drop_duplicates(subset=["program_id", "category_id"])
    )


@dataclass
class Step:
    """Compute KPI-ready answers table using existing helpers."""

    name: str = "kpis"

    def run(self, ctx: RunContext) -> None:
        panels: Dict[str, pd.DataFrame] = ctx.cache.get("panels", {})  # type: ignore[assignment]
        if not panels:
            raise RuntimeError("materialize step must run before kpis step")

        members_df = panels.get("shares_member_df", pd.DataFrame())
        controls_df = panels.get("shares_control_df", pd.DataFrame())
        suff_df = panels.get("controls_sufficiency_df", pd.DataFrame())
        awarded_df = panels.get("awarded_block_df", pd.DataFrame())
        dataset_exit_map = panels.get("dataset_exit_map", {})

        params = ctx.cache.get("params", {})
        min_pre = int(params.get("MIN_PRE_MONTHS", 3))
        min_common = int(params.get("MIN_COMMON_MONTHS", min_pre))
        target_lift = float(params.get("TARGET_LIFT_PP", 0.02))
        weight_guard = float(params.get("WEIGHT_COVERAGE_GUARD", 0.5))

        delta_df = kpis.build_delta_summary(
            members_df,
            controls_df,
            target_pp=target_lift,
            min_pre_months=min_pre,
            min_common_months=min_common,
            dataset_exit_map=dataset_exit_map if isinstance(dataset_exit_map, dict) else {},
            weight_coverage_guard=weight_guard,
        )
        if not isinstance(delta_df, pd.DataFrame):
            delta_df = pd.DataFrame()

        answers = _merge_sufficiency(delta_df, suff_df)
        answers = _apply_common_month_flags(answers, min_common)

        award_meta = _award_metadata(members_df, awarded_df)
        if not award_meta.empty:
            answers = answers.merge(award_meta, on=["program_id", "category_id"], how="left")
        else:
            answers["t0_awarded_suppliers"] = ""
            answers["controls_other_pg_overlap_excluded"] = False
        answers["t0_awarded_suppliers"] = answers["t0_awarded_suppliers"].fillna("")
        answers["controls_other_pg_overlap_excluded"] = answers["controls_other_pg_overlap_excluded"].fillna(False).astype(bool)

        answers = answers.sort_values(["program_id", "category_id"]).reset_index(drop=True)
        for col in ("program_id", "category_id"):
            if col in answers.columns:
                answers[col] = answers[col].astype(str)
        if "weight_coverage_clamped" in answers.columns:
            answers["weight_coverage_clamped"] = answers["weight_coverage_clamped"].fillna(False).astype(bool)
        int_mask_cols = [
            "member_masked_dataset_exit_count",
            "member_masked_program_exit_count",
            "control_masked_dataset_exit_count",
            "control_masked_program_exit_count",
        ]
        for col in int_mask_cols:
            if col in answers.columns:
                answers[col] = pd.to_numeric(answers[col], errors="coerce").astype("Int64")
        if "weight_coverage_clamp_month" in answers.columns:
            answers["weight_coverage_clamp_month"] = pd.to_numeric(
                answers["weight_coverage_clamp_month"], errors="coerce"
            ).astype("Int64")
        ctx.cache["answers_df"] = answers
        ctx.cache["controls_sufficiency_df"] = suff_df
