"""Helpers to rebuild Surpass reconciliation metrics from pipeline panels."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

SURPASS_PROGRAM_ID = "Surpass"


@dataclass(frozen=True)
class ReconciliationFrames:
    """Structured bundle of reconciliation data."""

    facility: pd.DataFrame
    category: pd.DataFrame
    comparison: pd.DataFrame


def filter_measured_members(
    shares_df: pd.DataFrame,
    *,
    program_id: str = SURPASS_PROGRAM_ID,
) -> pd.DataFrame:
    """Return Surpass facilities measured in-category at t0 with positive spend."""

    if not isinstance(shares_df, pd.DataFrame) or shares_df.empty:
        return pd.DataFrame(columns=[
            "program_id",
            "category_id",
            "facility_id",
            "event_month",
            "member_at_t0",
            "t0_total_cat_spend_6m",
        ])

    work = shares_df.copy()
    for col in ("program_id", "category_id", "facility_id"):
        if col in work.columns:
            work[col] = work[col].astype(str)
    if "event_month" in work.columns:
        work["event_month"] = pd.to_numeric(work["event_month"], errors="coerce")
    if "member_at_t0" in work.columns:
        work["member_at_t0"] = work["member_at_t0"].fillna(False).astype(bool)
    if "t0_total_cat_spend_6m" in work.columns:
        spend_col = "t0_total_cat_spend_6m"
    elif "total_cat_spend_6m" in work.columns:
        spend_col = "total_cat_spend_6m"
    else:
        spend_col = "total_cat_spend"
    if spend_col not in work.columns:
        return work.loc[[]]

    spend_vals = pd.to_numeric(work[spend_col], errors="coerce")
    mask = (
        work["program_id"].eq(program_id)
        & work["event_month"].eq(0)
        & work["member_at_t0"].fillna(False)
        & spend_vals.gt(0)
    )
    columns = [
        "program_id",
        "category_id",
        "facility_id",
        "event_month",
        "member_at_t0",
        spend_col,
    ]
    optional_cols = [
        "awarded_share_6m",
        "total_cat_spend_6m",
        "awarded_spend_6m",
        "member_flag",
    ]
    for opt in optional_cols:
        if opt in work.columns:
            columns.append(opt)
    filtered = work.loc[mask, columns].copy()
    filtered.rename(columns={spend_col: "t0_total_cat_spend_6m"}, inplace=True)
    return filtered.reset_index(drop=True)


def summarize_by_category(facility_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate facility-level rows into category-level counts and spend."""

    if not isinstance(facility_df, pd.DataFrame) or facility_df.empty:
        return pd.DataFrame(columns=["category_id", "facility_count", "t0_spend_6m"])
    required = {"category_id", "facility_id", "t0_total_cat_spend_6m"}
    if not required <= set(facility_df.columns):
        missing = ", ".join(sorted(required - set(facility_df.columns)))
        raise ValueError(f"facility_df missing required columns: {missing}")

    grouped = (
        facility_df
        .groupby("category_id", dropna=False)
        .agg(
            facility_count=("facility_id", "nunique"),
            t0_spend_6m=("t0_total_cat_spend_6m", "sum"),
        )
        .reset_index()
    )
    grouped["facility_count"] = grouped["facility_count"].astype("Int64")
    grouped["t0_spend_6m"] = grouped["t0_spend_6m"].astype(float)
    return grouped


def compare_to_prd(
    category_summary: pd.DataFrame,
    prd_answers: pd.DataFrame,
    *,
    program_id: str = SURPASS_PROGRAM_ID,
) -> pd.DataFrame:
    """Join the category summary with PRD answers to quantify deltas."""

    if not isinstance(category_summary, pd.DataFrame) or category_summary.empty:
        cols = [
            "category_id",
            "facility_count",
            "t0_spend_6m",
            "prd_N_members_measured",
            "prd_member_t0_total_spend_6m",
            "delta_facility_count",
            "delta_t0_spend_6m",
        ]
        return pd.DataFrame(columns=cols)

    if not isinstance(prd_answers, pd.DataFrame) or prd_answers.empty:
        raise ValueError("prd_answers must contain Surpass rows for comparison")

    prd = prd_answers.copy()
    for col in ("program_id", "category_id"):
        if col in prd.columns:
            prd[col] = prd[col].astype(str)
    prd = prd.loc[prd["program_id"].eq(program_id), [
        "category_id",
        "N_members_measured",
        "member_t0_total_spend_6m",
    ]].copy()
    prd.rename(
        columns={
            "N_members_measured": "prd_N_members_measured",
            "member_t0_total_spend_6m": "prd_member_t0_total_spend_6m",
        },
        inplace=True,
    )

    merged = category_summary.merge(prd, on="category_id", how="left")
    merged["delta_facility_count"] = (
        merged["facility_count"].astype("Int64")
        - merged["prd_N_members_measured"].astype("Int64")
    )
    merged["delta_t0_spend_6m"] = (
        merged["t0_spend_6m"].astype(float)
        - merged["prd_member_t0_total_spend_6m"].astype(float)
    )
    return merged


def resolve_latest_prd_answers(
    *,
    snapshots_dir: Path,
    explicit_path: Optional[Path] = None,
) -> Path:
    """Resolve a PRD answers CSV path, falling back to the latest snapshot."""

    if explicit_path is not None:
        path = explicit_path.expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Provided answers path does not exist: {path}")
        return path

    candidates = sorted(
        (p for p in snapshots_dir.iterdir() if p.is_dir() and _looks_like_snapshot(p.name)),
        key=lambda p: p.name,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError("No timestamped snapshot directories found in snapshots_dir")

    for snapshot_dir in candidates:
        candidate_path = snapshot_dir / "prd_answers.csv"
        if candidate_path.exists():
            return candidate_path
    raise FileNotFoundError("No prd_answers.csv found in timestamped snapshots")


def build_output_directory(base_dir: Path) -> Path:
    """Create a timestamped output directory for reconciliation exports."""

    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    out = base_dir / run_id
    out.mkdir(parents=True, exist_ok=False)
    return out


def _looks_like_snapshot(name: str) -> bool:
    try:
        datetime.strptime(name, "%Y-%m-%d_%H-%M-%S")
        return True
    except ValueError:
        return False
