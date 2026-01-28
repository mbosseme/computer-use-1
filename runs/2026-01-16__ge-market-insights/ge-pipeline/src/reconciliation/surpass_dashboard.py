"""Utilities to reconcile Surpass PRD cohorts with the legacy dashboard export."""

from __future__ import annotations

import codecs
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import pandas as pd
import yaml

from .surpass import filter_measured_members

_TRAILING_CONTRACT_REGEX = re.compile(r"\s+-\s*(?:SP|AD|AS)-.*$", re.IGNORECASE)
_CONTRACT_NUMBER_PATTERN = re.compile(r"^(?:[A-Z]{2}-[A-Z0-9]{2,}-[A-Z0-9]+)$")


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def normalize_category(value: Any) -> str:
    """Trim, uppercase, collapse whitespace, and strip trailing ``- SP-*`` suffixes."""

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    text = str(value).strip().upper()
    if not text:
        return ""
    text = " ".join(text.split())
    text = _TRAILING_CONTRACT_REGEX.sub("", text).strip()
    return text


def extract_contract_number(value: Any) -> str:
    """Extract a normalized contract number from a compound dashboard label."""

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    text = str(value).strip().upper()
    if not text:
        return ""

    # Prefer the suffix after the final " - " delimiter when it matches the contract pattern.
    if " - " in text:
        candidate = text.rsplit(" - ", 1)[-1].strip()
        if _CONTRACT_NUMBER_PATTERN.match(candidate):
            return candidate

    if _CONTRACT_NUMBER_PATTERN.match(text):
        return text

    return ""


def _ensure_str(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def load_category_map(path: Path | None) -> Dict[str, str]:
    """Load a YAML mapping of dashboard labels to canonical PRD labels."""

    if path is None:
        return {}
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        return {}
    with resolved.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, Mapping):
        raise ValueError("category map yaml must contain a mapping")

    mapping: Dict[str, str] = {}
    for raw_key, raw_value in data.items():
        key_norm = normalize_category(raw_key)
        value_norm = normalize_category(raw_value)
        if key_norm:
            mapping[key_norm] = value_norm or key_norm
    return mapping


def load_contract_number_mapping(path: Path | None) -> Dict[str, str]:
    """Load a mapping of contract numbers to canonical categories from a CSV."""

    if path is None:
        return {}

    resolved = path.expanduser().resolve()
    if not resolved.exists():
        return {}

    with resolved.open("rb") as raw_handle:
        prefix = raw_handle.read(4)

    if prefix.startswith(codecs.BOM_UTF16_LE) or prefix.startswith(codecs.BOM_UTF16_BE):
        encoding = "utf-16"
    elif prefix.startswith(codecs.BOM_UTF8):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"

    frame = pd.read_csv(resolved, sep=None, engine="python", encoding=encoding)
    expected_columns = {"Contract Number", "Contract Category"}
    if not expected_columns <= set(frame.columns):
        missing = ", ".join(sorted(expected_columns - set(frame.columns)))
        raise ValueError(f"Contract mapping CSV missing required columns: {missing}")

    mapping: Dict[str, str] = {}
    for _, row in frame.iterrows():
        number_raw = row.get("Contract Number", "")
        category_raw = row.get("Contract Category", "")
        number = extract_contract_number(number_raw)
        category = normalize_category(category_raw)
        if not number or not category:
            continue
        previous = mapping.get(number)
        if previous and previous != category:
            raise ValueError(
                f"Conflicting categories for contract number {number}: '{previous}' vs '{category}'"
            )
        mapping[number] = category

    return mapping


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class DashboardNormalizationResult:
    """Container describing the normalised dashboard export."""

    frame: pd.DataFrame
    filter_counts: Dict[str, int]
    mapping_counts: Dict[str, Any]
    mapped_category_details: pd.DataFrame
    unmapped_categories: pd.DataFrame


@dataclass
class DashboardReconciliationResult:
    """Structured reconciliation bundle consumed by the CLI."""

    members: pd.DataFrame
    spend: pd.DataFrame
    members_intersection: Optional[pd.DataFrame]
    spend_intersection: Optional[pd.DataFrame]
    dashboard_stats: Dict[str, int]
    filter_counts: Dict[str, int]
    mapping_counts: Dict[str, Any]
    mapped_category_details: pd.DataFrame
    unmapped_categories: pd.DataFrame
    overlap_summary: Dict[str, float]


# ---------------------------------------------------------------------------
# Dashboard normalisation
# ---------------------------------------------------------------------------


def prepare_dashboard_dataframe(
    dashboard_df: pd.DataFrame,
    *,
    status_column: str = "System Status",
    required_status: str = "PA-Completed",
    category_column: str = "Contract Category",
    facility_column: str = "Entity Code",
    spend_column: str = "Category Spend",
    category_map: Mapping[str, str] | None = None,
    contract_number_column: str | None = None,
    contract_map: Mapping[str, str] | None = None,
) -> DashboardNormalizationResult:
    """Normalise dashboard columns, record filter counts, and compute mapping stats."""

    work = dashboard_df.copy()
    required_columns = {status_column, category_column, facility_column, spend_column}
    missing = required_columns - set(work.columns)
    if missing:
        joined = ", ".join(sorted(missing))
        raise KeyError(f"Dashboard export missing required columns: {joined}")

    total_rows = int(len(work))
    work[status_column] = _ensure_str(work[status_column])
    work = work.loc[work[status_column].eq(required_status)].copy()

    category_series = _ensure_str(work[category_column])
    work["category_raw"] = category_series.map(normalize_category)

    if contract_number_column and contract_number_column in work.columns:
        contract_series = _ensure_str(work[contract_number_column])
    else:
        contract_series = category_series
    work["contract_number"] = contract_series.map(extract_contract_number)

    category_norm = work["category_raw"].copy()
    mapping_source = pd.Series("", index=work.index, dtype="object")

    if category_map:
        mapped_by_label = work["category_raw"].map(category_map)
        mask_label = mapped_by_label.notna()
        if mask_label.any():
            category_norm.loc[mask_label] = mapped_by_label.loc[mask_label].astype(str)
            mapping_source.loc[mask_label] = "category_map"

    if contract_map:
        mapped_by_contract = work["contract_number"].map(contract_map)
        mask_contract = mapped_by_contract.notna() & mapping_source.eq("")
        if mask_contract.any():
            category_norm.loc[mask_contract] = mapped_by_contract.loc[mask_contract].astype(str)
            mapping_source.loc[mask_contract] = "contract_number"

    work["category_norm"] = category_norm.fillna("").astype(str)
    work["category_mapping_source"] = mapping_source.replace("", pd.NA)
    work["category_mapped"] = mapping_source.ne("")

    work["facility_id"] = _ensure_str(work[facility_column])
    spend_converted = pd.to_numeric(work[spend_column], errors="coerce")
    if spend_converted.isna().any():
        bad_rows = work.loc[spend_converted.isna(), [facility_column, category_column, spend_column]]
        raise ValueError(
            "Encountered non-numeric values in Category Spend column: "
            + bad_rows.to_json(orient="records")
        )
    work["spend"] = spend_converted.fillna(0.0).astype(float)
    if (work["spend"] < 0).any():
        negative = work.loc[work["spend"] < 0, [facility_column, category_column, spend_column]]
        raise ValueError(
            "Negative spend detected in dashboard export: " + negative.to_json(orient="records")
        )
    work["has_positive_spend"] = work["spend"].gt(0)

    filter_counts = {
        "rows_total": total_rows,
        "rows_status_filtered": int(len(work)),
        "rows_positive_spend": int(work["has_positive_spend"].sum()),
        "distinct_facilities_status_filtered": int(work["facility_id"].nunique()),
        "distinct_facilities_positive_spend": int(
            work.loc[work["has_positive_spend"], "facility_id"].nunique()
        ),
    }

    mapped_rows = int(work["category_mapped"].sum())
    rows_status_filtered = filter_counts["rows_status_filtered"]
    rows_mapped_by_label = int(work.loc[work["category_mapping_source"].eq("category_map")].shape[0])
    rows_mapped_by_contract = int(work.loc[work["category_mapping_source"].eq("contract_number")].shape[0])
    mapping_counts: Dict[str, Any] = {
        "rows_total": rows_status_filtered,
        "rows_mapped": mapped_rows,
        "rows_unmapped": rows_status_filtered - mapped_rows,
        "mapped_pct": float(mapped_rows / rows_status_filtered) if rows_status_filtered else 0.0,
        "rows_mapped_by_category_map": rows_mapped_by_label,
        "rows_mapped_by_contract_number": rows_mapped_by_contract,
    }

    mapped_detail = (
        work.loc[
            work["category_mapped"],
            ["category_raw", "category_norm", "category_mapping_source"],
        ]
        .value_counts()
        .reset_index(name="row_count")
        .rename(
            columns={
                "category_raw": "raw_category",
                "category_norm": "mapped_category",
                "category_mapping_source": "mapping_source",
            }
        )
        .sort_values("row_count", ascending=False)
        .reset_index(drop=True)
    )

    unmapped = (
        work.loc[~work["category_mapped"], "category_raw"]
        .value_counts()
        .rename_axis("raw_category")
        .reset_index(name="row_count")
        .sort_values("row_count", ascending=False)
        .reset_index(drop=True)
    )

    return DashboardNormalizationResult(
        frame=work,
        filter_counts=filter_counts,
        mapping_counts=mapping_counts,
        mapped_category_details=mapped_detail,
        unmapped_categories=unmapped,
    )


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def _collect_facility_sets(df: pd.DataFrame) -> Dict[str, set[str]]:
    result: Dict[str, set[str]] = {}
    if df.empty:
        return result
    for category, values in df.groupby("category_norm")["facility_id"]:
        key = str(category).strip()
        result[key] = {fid for fid in (str(v).strip() for v in values) if fid}
    return result


def _collect_spend_per_facility(df: pd.DataFrame, value_column: str) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}
    if df.empty:
        return result
    grouped = (
        df.groupby(["category_norm", "facility_id"], dropna=False)[value_column]
        .sum()
        .reset_index()
    )
    for _, row in grouped.iterrows():
        category = str(row["category_norm"]).strip()
        facility = str(row["facility_id"]).strip()
        if not facility:
            continue
        result.setdefault(category, {})[facility] = float(row[value_column])
    return result


def _collect_raw_labels(df: pd.DataFrame, source_column: str) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    if df.empty:
        return result
    grouped = df.groupby("category_norm")[source_column]
    for category, labels in grouped:
        key = str(category).strip()
        values = sorted({normalize_category(label) for label in labels if label})
        result[key] = values
    return result


def _aggregate_prd(
    facility_df: pd.DataFrame,
    category_map: Mapping[str, str] | None,
) -> Dict[str, Dict[str, Any]]:
    if facility_df.empty:
        return {}

    work = facility_df.copy()
    work["category_raw"] = work["category_id"].map(normalize_category)
    if category_map:
        mapped = work["category_raw"].map(category_map)
        work["category_norm"] = mapped.fillna(work["category_raw"]).astype(str)
    else:
        work["category_norm"] = work["category_raw"]
    work["facility_id"] = _ensure_str(work.get("facility_id", pd.Series(dtype=str)))
    if "t0_total_cat_spend_6m" in work.columns:
        spend_series = pd.to_numeric(work["t0_total_cat_spend_6m"], errors="coerce").fillna(0.0)
    else:
        spend_series = pd.Series(0.0, index=work.index, dtype=float)
    work["t0_total_cat_spend_6m"] = spend_series

    facilities = _collect_facility_sets(work[["category_norm", "facility_id"]])
    spend_per_facility = _collect_spend_per_facility(work, "t0_total_cat_spend_6m")
    total_spend = (
        work.groupby("category_norm")["t0_total_cat_spend_6m"].sum().astype(float)
        if not work.empty
        else pd.Series(dtype=float)
    )
    raw_labels = _collect_raw_labels(work, "category_raw")

    result: Dict[str, Dict[str, Any]] = {}
    for category in facilities:
        result[category] = {
            "facilities": facilities.get(category, set()),
            "spend_per_facility": spend_per_facility.get(category, {}),
            "total_spend": float(total_spend.get(category, 0.0)),
            "raw_labels": raw_labels.get(category, []),
        }
    return result


def _aggregate_dashboard(work: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    if work.empty:
        return {}

    facilities_all = _collect_facility_sets(work[["category_norm", "facility_id"]])
    facilities_spendpos = _collect_facility_sets(
        work.loc[work["has_positive_spend"], ["category_norm", "facility_id"]]
    )
    spend_pos = (
        work.loc[work["has_positive_spend"]]
        .groupby("category_norm")["spend"]
        .sum()
        .astype(float)
    )
    spend_per_facility_pos = _collect_spend_per_facility(
        work.loc[work["has_positive_spend"]], "spend"
    )
    raw_labels = _collect_raw_labels(work, "category_raw")

    categories = set(facilities_all) | set(facilities_spendpos) | set(spend_pos.index)
    result: Dict[str, Dict[str, Any]] = {}
    for category in categories:
        result[category] = {
            "facilities_all": facilities_all.get(category, set()),
            "facilities_spendpos": facilities_spendpos.get(category, set()),
            "total_spend": float(spend_pos.get(category, 0.0)),
            "spend_per_facility": spend_per_facility_pos.get(category, {}),
            "raw_labels": raw_labels.get(category, []),
        }
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def reconcile_dashboard(
    shares_df: pd.DataFrame,
    dashboard_df: pd.DataFrame,
    *,
    category_map: Mapping[str, str] | None = None,
    contract_map: Mapping[str, str] | None = None,
    contract_number_column: str | None = None,
    status_column: str = "System Status",
    required_status: str = "PA-Completed",
    category_column: str = "Contract Category",
    facility_column: str = "Entity Code",
    spend_column: str = "Category Spend",
    spend_positive_only: bool = True,
    emit_intersection: bool = True,
) -> DashboardReconciliationResult:
    """Compare PRD facility cohorts against the dashboard export."""

    facility_df = filter_measured_members(shares_df)
    if facility_df.empty:
        raise ValueError("No measured-in-category facilities found for the selected program.")

    norm = prepare_dashboard_dataframe(
        dashboard_df,
        status_column=status_column,
        required_status=required_status,
        category_column=category_column,
        facility_column=facility_column,
        spend_column=spend_column,
        category_map=category_map,
        contract_number_column=contract_number_column,
        contract_map=contract_map,
    )

    prd_metrics = _aggregate_prd(facility_df, category_map)
    dash_metrics = _aggregate_dashboard(norm.frame)

    categories = sorted(set(prd_metrics) | set(dash_metrics))

    member_rows: List[Dict[str, Any]] = []
    spend_rows: List[Dict[str, Any]] = []
    members_intersection_rows: List[Dict[str, Any]] = []
    spend_intersection_rows: List[Dict[str, Any]] = []

    for category in categories:
        prd_snapshot = prd_metrics.get(category, {})
        dash_snapshot = dash_metrics.get(category, {})

        prd_facilities = set(prd_snapshot.get("facilities", set()))
        dash_all = set(dash_snapshot.get("facilities_all", set()))
        dash_spendpos = set(dash_snapshot.get("facilities_spendpos", set()))

        dash_members = dash_spendpos if spend_positive_only else dash_all

        prd_total_spend = float(prd_snapshot.get("total_spend", 0.0))
        dash_total_spend = float(dash_snapshot.get("total_spend", 0.0))

        prd_spend_per_fac = dict(prd_snapshot.get("spend_per_facility", {}))
        dash_spend_per_fac = dict(dash_snapshot.get("spend_per_facility", {}))

        intersection = prd_facilities & dash_members
        union = prd_facilities | dash_members
        overlap_rate = (len(intersection) / len(union)) if union else math.nan

        members_prd = len(prd_facilities)
        members_dash_all = len(dash_all)
        members_dash_spendpos = len(dash_spendpos)

        prd_only = members_prd - len(intersection)
        dash_only = len(dash_members - prd_facilities)
        members_zero_spend = max(len(dash_all) - len(dash_spendpos), 0)

        prd_intersection_spend = sum(prd_spend_per_fac.get(fid, 0.0) for fid in intersection)
        dash_intersection_spend = sum(dash_spend_per_fac.get(fid, 0.0) for fid in intersection)

        raw_labels = sorted(
            set(prd_snapshot.get("raw_labels", [])) | set(dash_snapshot.get("raw_labels", []))
        )
        raw_label_str = " | ".join(raw_labels) if raw_labels else category

        member_rows.append(
            {
                "mapped_label": category,
                "raw_labels": raw_label_str,
                "members_prd_measured_in_category": members_prd,
                "prd_6m_spend": prd_total_spend,
                "members_dashboard_all": members_dash_all,
                "members_dashboard_spendpos": members_dash_spendpos,
                "members_dashboard_zero_spend": members_zero_spend,
                "delta_members_all": members_dash_all - members_prd,
                "delta_members_spendpos": members_dash_spendpos - members_prd,
                "members_intersection": len(intersection),
                "members_prd_only": prd_only,
                "members_dashboard_spendpos_only": dash_only,
                "dashboard_6m_spend": dash_total_spend,
                "facility_overlap_rate": overlap_rate,
            }
        )

        spend_rows.append(
            {
                "mapped_label": category,
                "raw_labels": raw_label_str,
                "prd_6m_spend": prd_total_spend,
                "dashboard_6m_spend": dash_total_spend,
                "delta_spend": dash_total_spend - prd_total_spend,
                "members_prd_measured_in_category": members_prd,
                "members_dashboard_spendpos": members_dash_spendpos,
                "facility_overlap_rate": overlap_rate,
            }
        )

        if emit_intersection:
            members_intersection_rows.append(
                {
                    "mapped_label": category,
                    "members_intersection": len(intersection),
                    "members_union": len(union),
                }
            )

            spend_intersection_rows.append(
                {
                    "mapped_label": category,
                    "prd_6m_spend_intersection": prd_intersection_spend,
                    "dashboard_6m_spend_intersection": dash_intersection_spend,
                }
            )

    members_df = pd.DataFrame(member_rows)
    spend_df = pd.DataFrame(spend_rows)
    members_intersection_df = pd.DataFrame(members_intersection_rows) if emit_intersection else None
    spend_intersection_df = pd.DataFrame(spend_intersection_rows) if emit_intersection else None

    for frame in (members_df, spend_df, members_intersection_df, spend_intersection_df):
        if frame is None or frame.empty:
            continue
        frame.sort_values("mapped_label", inplace=True)
        frame.reset_index(drop=True, inplace=True)

    _cast_integer_columns(members_df, spend_df, members_intersection_df)
    _cast_overlap_rate(members_df, spend_df)
    _select_output_columns(members_df, spend_df)

    if not members_df.empty and members_df["mapped_label"].duplicated().any():
        duplicates = members_df.loc[members_df["mapped_label"].duplicated(), "mapped_label"].tolist()
        raise ValueError(
            "Duplicate mapped categories detected after normalisation: " + json.dumps(duplicates)
        )

    overlap_summary = _summarise_overlap(members_df)

    dashboard_stats = {
        "members_rows": int(len(members_df)),
        "spend_rows": int(len(spend_df)),
    }

    return DashboardReconciliationResult(
        members=members_df,
        spend=spend_df,
        members_intersection=members_intersection_df,
        spend_intersection=spend_intersection_df,
        dashboard_stats=dashboard_stats,
        filter_counts=norm.filter_counts,
        mapping_counts=norm.mapping_counts,
        mapped_category_details=norm.mapped_category_details,
        unmapped_categories=norm.unmapped_categories,
        overlap_summary=overlap_summary,
    )


# ---------------------------------------------------------------------------
# Summary helpers for CLI
# ---------------------------------------------------------------------------


def compute_summary_metrics(
    members_df: pd.DataFrame,
    *,
    member_delta_threshold: float,
    overlap_threshold: float,
) -> Dict[str, Any]:
    """Compute summary metrics used in CLI reporting."""

    if members_df is None or members_df.empty:
        return {
            "member_delta_threshold": member_delta_threshold,
            "overlap_threshold": overlap_threshold,
            "member_delta_gt_threshold_pct": 0.0,
            "overlap_lt_threshold_pct": 0.0,
            "top_member_deltas": pd.DataFrame(columns=["mapped_label", "delta_members_spendpos"]),
            "top_spend_deltas": pd.DataFrame(columns=["mapped_label", "delta_spend"]),
        }

    work = members_df.copy()
    work["abs_member_delta"] = work["delta_members_spendpos"].abs()
    work["abs_spend_delta"] = (work["dashboard_6m_spend"] - work["prd_6m_spend"]).abs()

    delta_pct = float((work["abs_member_delta"] > member_delta_threshold).mean()) if len(work) else 0.0
    overlap_pct = float((work["facility_overlap_rate"].fillna(0.0) < overlap_threshold).mean()) if len(work) else 0.0

    top_member_deltas = (
        work.sort_values("abs_member_delta", ascending=False)
        [["mapped_label", "delta_members_spendpos", "members_prd_measured_in_category"]]
        .head(5)
        .reset_index(drop=True)
    )

    top_spend_deltas = (
        work.sort_values("abs_spend_delta", ascending=False)
        [["mapped_label", "prd_6m_spend", "dashboard_6m_spend"]]
        .head(5)
        .reset_index(drop=True)
    )

    return {
        "member_delta_threshold": member_delta_threshold,
        "overlap_threshold": overlap_threshold,
        "member_delta_gt_threshold_pct": delta_pct,
        "overlap_lt_threshold_pct": overlap_pct,
        "top_member_deltas": top_member_deltas,
        "top_spend_deltas": top_spend_deltas,
    }


def render_summary_markdown(
    summary_metrics: Dict[str, Any],
    *,
    mapping_counts: Mapping[str, Any],
    overlap_summary: Mapping[str, float],
    notes: Mapping[str, Any],
) -> str:
    """Render a Markdown summary for CLI output."""

    lines = ["# Surpass dashboard reconciliation summary", ""]
    lines.append(
        f"- Member delta threshold: {summary_metrics['member_delta_threshold']} (share {summary_metrics['member_delta_gt_threshold_pct']:.0%} above)"
    )
    lines.append(
        f"- Overlap threshold: {summary_metrics['overlap_threshold']} (share {summary_metrics['overlap_lt_threshold_pct']:.0%} below)"
    )
    lines.append(
        f"- Mapping coverage: {mapping_counts.get('rows_mapped', 0)} / {mapping_counts.get('rows_total', 0)} rows mapped"
    )
    if overlap_summary.get("count", 0):
        lines.append(
            "- Facility overlap rate: "
            f"mean {overlap_summary.get('mean', math.nan):.2f}, "
            f"median {overlap_summary.get('median', math.nan):.2f}, "
            f"min {overlap_summary.get('min', math.nan):.2f}, "
            f"max {overlap_summary.get('max', math.nan):.2f}"
        )

    lines.append("")

    top_member = summary_metrics.get("top_member_deltas")
    if isinstance(top_member, pd.DataFrame) and not top_member.empty:
        lines.append("## Largest member deltas")
        lines.append(_safe_to_markdown(top_member))
        lines.append("")

    top_spend = summary_metrics.get("top_spend_deltas")
    if isinstance(top_spend, pd.DataFrame) and not top_spend.empty:
        lines.append("## Largest spend deltas")
        lines.append(_safe_to_markdown(top_spend))
        lines.append("")

    if notes:
        lines.append("## Notes")
        for key, value in notes.items():
            lines.append(f"- {key}: {value}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal casting utilities
# ---------------------------------------------------------------------------


def _safe_to_markdown(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except ImportError:
        return df.to_string(index=False)


def _cast_integer_columns(
    members: pd.DataFrame,
    spend: pd.DataFrame,
    members_intersection: Optional[pd.DataFrame],
) -> None:
    int_columns = [
        "members_prd_measured_in_category",
        "members_dashboard_all",
        "members_dashboard_spendpos",
        "members_dashboard_zero_spend",
        "delta_members_all",
        "delta_members_spendpos",
        "members_intersection",
        "members_prd_only",
        "members_dashboard_spendpos_only",
    ]
    for column in int_columns:
        if column in members.columns:
            members[column] = members[column].astype("Int64")

    if {"members_prd_measured_in_category", "members_dashboard_spendpos"} <= set(spend.columns):
        spend[["members_prd_measured_in_category", "members_dashboard_spendpos"]] = (
            spend[["members_prd_measured_in_category", "members_dashboard_spendpos"]].astype("Int64")
        )

    if members_intersection is not None and not members_intersection.empty:
        for column in ["members_intersection", "members_union"]:
            if column in members_intersection.columns:
                members_intersection[column] = members_intersection[column].astype("Int64")


def _cast_overlap_rate(members: pd.DataFrame, spend: pd.DataFrame) -> None:
    for frame in (members, spend):
        if "facility_overlap_rate" in frame.columns and not frame.empty:
            frame["facility_overlap_rate"] = frame["facility_overlap_rate"].astype(float)


def _select_output_columns(members: pd.DataFrame, spend: pd.DataFrame) -> None:
    if not members.empty:
        members_columns = [
            "mapped_label",
            "raw_labels",
            "members_prd_measured_in_category",
            "prd_6m_spend",
            "members_dashboard_all",
            "members_dashboard_spendpos",
            "members_dashboard_zero_spend",
            "delta_members_all",
            "delta_members_spendpos",
            "members_intersection",
            "members_prd_only",
            "members_dashboard_spendpos_only",
            "dashboard_6m_spend",
            "facility_overlap_rate",
        ]
        members.drop(columns=set(members.columns) - set(members_columns), inplace=True)

    if not spend.empty:
        spend_columns = [
            "mapped_label",
            "raw_labels",
            "prd_6m_spend",
            "dashboard_6m_spend",
            "delta_spend",
            "members_prd_measured_in_category",
            "members_dashboard_spendpos",
            "facility_overlap_rate",
        ]
        spend.drop(columns=set(spend.columns) - set(spend_columns), inplace=True)


def _summarise_overlap(members_df: pd.DataFrame) -> Dict[str, float]:
    if members_df is None or members_df.empty:
        return {"count": 0, "mean": math.nan, "median": math.nan, "min": math.nan, "max": math.nan}

    overlap_values = members_df["facility_overlap_rate"].dropna().tolist()
    if not overlap_values:
        return {"count": 0, "mean": math.nan, "median": math.nan, "min": math.nan, "max": math.nan}

    return {
        "count": float(len(overlap_values)),
        "mean": float(mean(overlap_values)),
        "median": float(median(overlap_values)),
        "min": float(min(overlap_values)),
        "max": float(max(overlap_values)),
    }
