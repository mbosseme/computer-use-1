"""Pipeline step for materializing source panels."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Tuple

import pandas as pd

try:  # pragma: no cover - guard for environments without BigQuery client
    from google.cloud import bigquery
except Exception as exc:  # pragma: no cover - fail fast with actionable hint
    bigquery = None  # type: ignore
    _BIGQUERY_IMPORT_ERROR = exc
else:
    _BIGQUERY_IMPORT_ERROR = None

from ..runner import bq
from ..runner.orchestrator import RunContext
if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from google.cloud import bigquery as _bq_mod

    _ScalarParamT = _bq_mod.ScalarQueryParameter
else:  # pragma: no cover - runtime fallback to Any
    _ScalarParamT = Any  # type: ignore[assignment]

_DATAFORM_TABLES = {
    "coverage": ("staging", "stg_program_coverage"),
    "awarded_block": ("staging", "stg_awarded_block"),
    "membership": ("staging", "stg_membership_monthly"),
    "presence": ("staging", "stg_presence_monthly"),
    "shares_member": ("marts", "mart_shares_member"),
    "shares_control": ("marts", "mart_shares_control"),
}


def _ensure_bigquery_available() -> None:
    if bigquery is None:  # pragma: no cover - dependency missing
        raise RuntimeError(
            "google-cloud-bigquery is required for the materialize step."
        ) from _BIGQUERY_IMPORT_ERROR


def _fixture_mode(cfg: Dict[str, Any]) -> bool:
    mat_cfg = cfg.get("materialize") if isinstance(cfg, dict) else None
    if not isinstance(mat_cfg, dict):
        return False
    return str(mat_cfg.get("mode", "")).lower() == "fixtures"


def _fixture_dir(cfg: Dict[str, Any]) -> Path:
    mat_cfg = cfg.get("materialize") if isinstance(cfg, dict) else None
    if not isinstance(mat_cfg, dict):
        raise ValueError("materialize.fixtures_dir must be configured when mode=fixtures")
    raw_path = mat_cfg.get("fixtures_dir")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("materialize.fixtures_dir must be a non-empty string when mode=fixtures")
    base = Path(raw_path).expanduser()
    if not base.is_absolute():
        repo_root = cfg.get("_repo_root")
        if isinstance(repo_root, str) and repo_root:
            base = Path(repo_root) / base
        else:
            base = Path.cwd() / base
    return base.resolve()


def _load_fixture_panel(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Fixture file missing: {path}")
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _load_fixture_panels(ctx: RunContext) -> Dict[str, Any]:
    fixtures_root = _fixture_dir(ctx.cfg)
    ctx.logger.info({"event": "materialize_fixtures", "fixtures_dir": str(fixtures_root)})
    panels: Dict[str, Any] = {}
    mapping = {
        "coverage_df": "coverage",
        "membership_monthly_df": "membership_monthly",
        "shares_member_df": "shares_member",
        "shares_control_df": "shares_control",
        "awarded_block_df": "awarded_block",
    }
    for key, stem in mapping.items():
        path = fixtures_root / f"{stem}.csv"
        df = _load_fixture_panel(path)
        if key == "shares_member_df":
            df = _clamp_event_month(_rename_frame(df, "shares"))
        elif key == "shares_control_df":
            df = _clamp_event_month(_rename_frame(df, "controls"))
        elif key == "membership_monthly_df":
            df = _coerce_ids(df)
        elif key == "coverage_df":
            df = _coerce_ids(df)
        elif key == "awarded_block_df":
            df = _coerce_ids(df)
        panels[key] = df

    members_df = panels.get("shares_member_df", pd.DataFrame())
    controls_df = panels.get("shares_control_df", pd.DataFrame())
    min_pre = int(ctx.cache.get("params", {}).get("MIN_PRE_MONTHS", 3))
    panels["controls_sufficiency_df"] = _build_controls_sufficiency(members_df, controls_df, min_pre)
    panels.setdefault("pulse_summary_df", pd.DataFrame())
    panels.setdefault("did_summary_df", pd.DataFrame())
    panels.setdefault("presence_df", pd.DataFrame())
    panels.setdefault("dataset_exit_map", {})
    panels["params"] = dict(ctx.cache.get("params", {}))
    return panels


def _coerce_ids(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    df = df.copy()
    for col in ("program_id", "category_id", "facility_id"):
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df


def _rename_frame(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    mappings: Dict[str, Dict[str, str]] = {
        "coverage": {"program": "program_id", "category": "category_id", "month": "month"},
        "membership": {"program": "program_id", "entity_code": "facility_id", "month": "month"},
        "shares": {"program": "program_id", "category": "category_id", "entity_code": "facility_id", "month": "month"},
        "controls": {"program": "program_id", "category": "category_id", "entity_code": "facility_id", "month": "month"},
        "presence": {"facility_id": "facility_id", "month": "month"},
    }
    if df is None or not isinstance(df, pd.DataFrame):
        return pd.DataFrame()
    renamed = df.rename(columns=mappings.get(kind, {}))
    if renamed.empty:
        # Ensure expected columns exist even when the frame has no rows.
        expected_cols = set(mappings.get(kind, {}).values()) & {"program_id", "category_id", "facility_id", "month"}
        for col in expected_cols:
            if col not in renamed.columns:
                renamed[col] = pd.Series(dtype=str)
    return _coerce_ids(renamed)


def _clamp_event_month(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    df = df.copy()
    if "event_month" in df.columns:
        df["event_month"] = pd.to_numeric(df["event_month"], errors="coerce")
        df = df[(df["event_month"] >= -12) & (df["event_month"] <= 18)]
    return df


def _build_dataset_exit_map(
    presence_df: pd.DataFrame,
    *,
    start_month: str,
    end_month: str,
    consecutive_absence: int = 2,
) -> Dict[str, pd.Timestamp]:
    """Identify the first calendar month where a facility leaves the dataset.

    A facility is considered exited once ``consecutive_absence`` consecutive calendar
    months elapse with no presence. Exit detection is based on the last observed month.
    """
    if (
        not isinstance(presence_df, pd.DataFrame)
        or presence_df.empty
        or "facility_id" not in presence_df.columns
        or "month" not in presence_df.columns
    ):
        return {}

    try:
        start = pd.Period(start_month, freq="M")
        end = pd.Period(end_month, freq="M")
    except Exception:
        return {}

    if start > end or consecutive_absence <= 0:
        return {}

    timeline = pd.period_range(start=start, end=end, freq="M")
    if timeline.empty:
        return {}

    work = presence_df.copy()
    work["facility_id"] = work["facility_id"].astype(str)
    work["month"] = pd.to_datetime(work["month"], errors="coerce")
    work = work.dropna(subset=["facility_id", "month"])
    if work.empty:
        return {}
    work["month"] = work["month"].dt.to_period("M")

    exit_map: Dict[str, pd.Timestamp] = {}
    for fid, group in work.groupby("facility_id", sort=False):
        months = sorted(set(group["month"]))
        if not months:
            continue
        last_period = months[-1]
        if last_period >= end:
            continue
        exit_period = None
        consecutive_missing = 0
        candidate_period = last_period + 1
        # Check consecutive months after the last observed period
        while candidate_period <= end:
            if candidate_period in months:
                consecutive_missing = 0
                exit_period = None
            else:
                consecutive_missing += 1
                if consecutive_missing == 1:
                    exit_period = candidate_period
                if consecutive_missing >= consecutive_absence:
                    break
            candidate_period += 1
        if exit_period is not None and consecutive_missing >= consecutive_absence:
            exit_map[fid] = exit_period.to_timestamp()
    return exit_map


def _build_param_dict(ctx: RunContext) -> Dict[str, Any]:
    base = dict(ctx.cache.get("params", {}))
    window = ctx.cache.get("window_params", {})
    guards = ctx.cfg.get("guards", {}) if isinstance(ctx.cfg, dict) else {}
    bigquery_cfg = ctx.cfg.get("bigquery", {}) if isinstance(ctx.cfg, dict) else {}

    table = bigquery_cfg.get("table")
    if not table:
        raise ValueError("bigquery.table must be configured.")

    # Carry notebook naming conventions forward for SQL templates
    coverage_pp_raw = None
    anchor_pp_raw = None
    if isinstance(guards, dict):
        raw_val = guards.get("coverage_guard_pp")
        if isinstance(raw_val, (int, float)):
            coverage_pp_raw = float(raw_val)
        anchor_val = guards.get("anchor_contract_guard_pp")
        if isinstance(anchor_val, (int, float)):
            anchor_pp_raw = float(anchor_val)
    if coverage_pp_raw is None:
        coverage_pp_raw = window.get("COVERAGE_GUARD_PP_RAW") or base.get("COVERAGE_GUARD_PP_RAW")
    if anchor_pp_raw is None:
        anchor_pp_raw = window.get("ANCHOR_CONTRACT_GUARD_PP_RAW") or base.get("ANCHOR_CONTRACT_GUARD_PP_RAW")
    coverage_fraction = window.get("COVERAGE_GUARD") or base.get("COVERAGE_GUARD")
    anchor_fraction = window.get("ANCHOR_CONTRACT_GUARD") or base.get("ANCHOR_CONTRACT_GUARD")
    if coverage_fraction is None and coverage_pp_raw is not None:
        coverage_fraction = coverage_pp_raw / 100.0 if coverage_pp_raw > 1 else float(coverage_pp_raw)
    if anchor_fraction is None and anchor_pp_raw is not None:
        anchor_fraction = anchor_pp_raw / 100.0 if anchor_pp_raw > 1 else float(anchor_pp_raw)
    if coverage_fraction is None:
        coverage_fraction = 0.02
    if anchor_fraction is None:
        anchor_fraction = 0.02
    params: Dict[str, Any] = {
        "START_MONTH": window.get("START_MONTH"),
        "END_MONTH": window.get("END_MONTH"),
        "CORE_START": window.get("CORE_START"),
        "CORE_END": window.get("CORE_END"),
        "DATA_CUTOFF_MONTH": window.get("DATA_CUTOFF_MONTH"),
        "CURRENT_MONTH": window.get("CURRENT_MONTH"),
        "ROLLING_M": window.get("ROLLING_M", base.get("ROLLING_M", 6)),
        "MIN_PRE_MONTHS": window.get("MIN_PRE_MONTHS", base.get("MIN_PRE_MONTHS", 3)),
        "MIN_COMMON_MONTHS": window.get("MIN_COMMON_MONTHS", base.get("MIN_COMMON_MONTHS", 3)),
        "TARGET_LIFT_PP": base.get("TARGET_LIFT_PP"),
        "TARGET_LIFT_PP_RAW": base.get("TARGET_LIFT_PP_RAW"),
        "table": table,
        "coverage_guard": coverage_fraction,
        "coverage_guard_pp_raw": coverage_pp_raw,
        "anchor_contract_guard_pp": anchor_fraction,
        "anchor_contract_guard_pp_raw": anchor_pp_raw,
        "anchor_contract_guard_abs_usd": guards.get("anchor_contract_guard_abs_usd", 0.0),
        "membership_threshold": guards.get("membership_threshold", 0.25),
        "sp": f"{guards.get('surpass_prefix', 'SP-')}%",
        "ad": f"{guards.get('ascend_prefix', 'AD-')}%",
        "ad_re": guards.get("ascend_regex", r"^A(D|S)-"),
        "WEIGHT_COVERAGE_GUARD": float(guards.get("weight_coverage_guard", 0.5)),
        "project": bigquery_cfg.get("project"),
    }
    return params


def _scalar_params(par: Dict[str, Any]) -> Tuple[_ScalarParamT, ...]:
    _ensure_bigquery_available()
    assert bigquery is not None
    return (
        bigquery.ScalarQueryParameter("START_MONTH", "STRING", par["START_MONTH"]),
        bigquery.ScalarQueryParameter("END_MONTH", "STRING", par["END_MONTH"]),
        bigquery.ScalarQueryParameter("CORE_START", "STRING", par["CORE_START"]),
        bigquery.ScalarQueryParameter("CORE_END", "STRING", par["CORE_END"]),
        bigquery.ScalarQueryParameter("coverage_guard", "FLOAT64", par["coverage_guard"]),
        bigquery.ScalarQueryParameter("anchor_contract_guard_pp", "FLOAT64", par["anchor_contract_guard_pp"]),
        bigquery.ScalarQueryParameter("anchor_contract_guard_abs_usd", "FLOAT64", par["anchor_contract_guard_abs_usd"]),
        bigquery.ScalarQueryParameter("membership_threshold", "FLOAT64", par["membership_threshold"]),
        bigquery.ScalarQueryParameter("sp", "STRING", par["sp"]),
        bigquery.ScalarQueryParameter("ad", "STRING", par["ad"]),
        bigquery.ScalarQueryParameter("ad_re", "STRING", par["ad_re"]),
    )



def _count_pre_months(df: pd.DataFrame) -> pd.Series:
    work = _coerce_ids(df)
    if not isinstance(work, pd.DataFrame) or work.empty or "event_month" not in work.columns:
        return pd.Series(dtype="Int64")
    work["event_month"] = pd.to_numeric(work["event_month"], errors="coerce")
    pre = work[work["event_month"].isin(range(-6, 0))]
    if pre.empty:
        return pd.Series(dtype="Int64")
    return pre.groupby(["program_id", "category_id"])["event_month"].nunique()


def _count_facilities(df: pd.DataFrame) -> pd.Series:
    required = {"program_id", "category_id", "facility_id"}
    if not isinstance(df, pd.DataFrame) or df.empty or not required <= set(df.columns):
        return pd.Series(dtype="Int64")
    return df.groupby(["program_id", "category_id"])["facility_id"].nunique()


def _count_measured_facilities(df: pd.DataFrame, *, require_member: bool) -> pd.Series:
    work = _coerce_ids(df)
    if not isinstance(work, pd.DataFrame) or work.empty or "event_month" not in work.columns:
        return pd.Series(dtype="Int64")
    if "t0_total_cat_spend_6m" in work.columns:
        spend_col = "t0_total_cat_spend_6m"
    elif "total_cat_spend_6m" in work.columns:
        spend_col = "total_cat_spend_6m"
    else:
        spend_col = "total_cat_spend"
    if spend_col not in work.columns:
        return pd.Series(dtype="Int64")
    mask = work["event_month"].astype("Int64", copy=False).eq(0)
    if require_member:
        if "member_at_t0" in work.columns:
            mask &= work["member_at_t0"].fillna(False).astype(bool)
        elif "member_flag" in work.columns:
            mask &= work["member_flag"].fillna(False).astype(bool)
    spend_vals = pd.to_numeric(work[spend_col], errors="coerce")
    mask &= spend_vals.fillna(0) > 0
    measured = work.loc[mask, ["program_id", "category_id", "facility_id"]].dropna()
    if measured.empty:
        return pd.Series(dtype="Int64")
    counts = measured.drop_duplicates().groupby(["program_id", "category_id"]).size()
    return counts.astype("Int64")


def _t0_member_rows(df: pd.DataFrame) -> pd.DataFrame:
    work = _coerce_ids(df)
    if work.empty or "event_month" not in work.columns:
        return pd.DataFrame(columns=["program_id", "category_id", "facility_id", "month", "t0_month", "t0_month_key"])
    t0 = work[work["event_month"].astype("Int64", copy=False).eq(0)].copy()
    if t0.empty:
        return pd.DataFrame(columns=["program_id", "category_id", "facility_id", "month", "t0_month", "t0_month_key"])
    if "member_at_t0" in t0.columns:
        t0 = t0[t0["member_at_t0"].fillna(False).astype(bool)]
    elif "member_flag" in t0.columns:
        t0 = t0[t0["member_flag"].fillna(False).astype(bool)]
    if t0.empty:
        return pd.DataFrame(columns=["program_id", "category_id", "facility_id", "month", "t0_month", "t0_month_key"])
    if "month" in t0.columns:
        month_source = t0["month"]
    else:
        month_source = pd.Series(pd.NA, index=t0.index, dtype="object")
    t0["t0_month"] = pd.to_datetime(month_source, errors="coerce")
    t0["t0_month_key"] = t0["t0_month"].dt.strftime("%Y-%m")
    return t0


def _member_cohort(df: pd.DataFrame) -> pd.DataFrame:
    work = _coerce_ids(df)
    if work.empty:
        return pd.DataFrame(columns=["program_id", "category_id", "facility_id", "event_month"])
    if "member_at_t0" in work.columns:
        mask = work["member_at_t0"].fillna(False).astype(bool)
    elif "member_flag" in work.columns and "event_month" in work.columns:
        mask = work["member_flag"].fillna(False).astype(bool) & work["event_month"].eq(0)
    else:
        return pd.DataFrame(columns=["program_id", "category_id", "facility_id", "event_month"])
    cohort = work[mask]
    if cohort.empty:
        return pd.DataFrame(columns=["program_id", "category_id", "facility_id", "event_month"])
    return cohort.drop_duplicates(subset=["program_id", "category_id", "facility_id"])


def _build_controls_sufficiency(members_df: pd.DataFrame, controls_df: pd.DataFrame, min_pre_months: int) -> pd.DataFrame:
    members_cohort = _member_cohort(members_df)
    pre_m = _count_pre_months(members_df).rename("member_pre_months")
    pre_c = _count_pre_months(controls_df).rename("control_pre_months")
    n_members = _count_facilities(members_cohort).rename("N_members")
    n_controls = _count_facilities(
        _coerce_ids(controls_df).drop_duplicates(subset=["program_id", "category_id", "facility_id"])
    ).rename("N_controls")
    measured_members = _count_measured_facilities(members_df, require_member=True).rename("N_members_measured")
    measured_controls = _count_measured_facilities(controls_df, require_member=False).rename("N_controls_measured")
    summary = pd.concat([pre_m, pre_c, n_members, n_controls, measured_members, measured_controls], axis=1).reset_index()
    for col in ("member_pre_months", "control_pre_months", "N_members", "N_controls"):
        if col in summary.columns:
            summary[col] = pd.to_numeric(summary[col], errors="coerce").astype("Int64")
    for col in ("N_members_measured", "N_controls_measured"):
        if col in summary.columns:
            summary[col] = pd.to_numeric(summary[col], errors="coerce").astype("Int64")

    t0_rows = _t0_member_rows(members_df)
    if not t0_rows.empty:
        t0_category = (
            t0_rows.dropna(subset=["program_id", "category_id", "t0_month_key"])
            .drop_duplicates(subset=["program_id", "category_id"])
            .rename(columns={"t0_month_key": "t0_event_month"})
        )
        t0_counts = (
            t0_rows.dropna(subset=["program_id", "facility_id", "t0_month_key"])
            .drop_duplicates(subset=["program_id", "facility_id", "t0_month_key"])
            .groupby(["program_id", "t0_month_key"])
            .size()
            .rename("_N_members_program_t0")
            .reset_index()
        )
        summary = summary.merge(t0_category, on=["program_id", "category_id"], how="left")
        summary = summary.merge(
            t0_counts,
            left_on=["program_id", "t0_event_month"],
            right_on=["program_id", "t0_month_key"],
            how="left",
        )
        if "_N_members_program_t0" in summary.columns:
            summary["N_members"] = summary["_N_members_program_t0"].where(
                summary["_N_members_program_t0"].notna(), summary["N_members"]
            )
            summary.drop(columns=["_N_members_program_t0"], inplace=True)
        if "t0_month_key" in summary.columns:
            summary.drop(columns=["t0_month_key"], inplace=True)
    else:
        summary["t0_event_month"] = pd.NA

    members_total = _coerce_ids(members_df)
    if "event_month" in members_total.columns:
        t0_mask = members_total["event_month"].astype("Int64", copy=False).eq(0)
        if "member_at_t0" in members_total.columns:
            t0_mask &= members_total["member_at_t0"].fillna(False).astype(bool)
        elif "member_flag" in members_total.columns:
            t0_mask &= members_total["member_flag"].fillna(False).astype(bool)
        member_program_counts = (
            members_total.loc[t0_mask, ["program_id", "facility_id"]]
            .dropna()
            .drop_duplicates()
            .groupby("program_id")
            .size()
            .astype("Int64")
        )
        summary["N_members"] = summary["program_id"].map(member_program_counts).astype("Int64")

    controls_total = _coerce_ids(controls_df)
    if "event_month" in controls_total.columns:
        t0_controls = controls_total[controls_total["event_month"].astype("Int64", copy=False).eq(0)]
        control_counts = (
            t0_controls.dropna(subset=["program_id", "category_id", "facility_id"])
            .drop_duplicates(subset=["program_id", "category_id", "facility_id"])
            .groupby(["program_id", "category_id"])
            .size()
            .astype("Int64")
            .reset_index(name="_N_controls_total")
        )
        summary = summary.merge(control_counts, on=["program_id", "category_id"], how="left")
        if "_N_controls_total" in summary.columns:
            summary["N_controls"] = summary["_N_controls_total"].where(summary["_N_controls_total"].notna(), summary["N_controls"])
            summary["N_controls"] = pd.to_numeric(summary["N_controls"], errors="coerce").astype("Int64")
            summary.drop(columns=["_N_controls_total"], inplace=True)

    summary["eligible_for_delta"] = (
        summary["member_pre_months"].fillna(0) >= min_pre_months
    ) & (
        summary["control_pre_months"].fillna(0) >= min_pre_months
    )
    summary["delta_missing_reason"] = pd.NA
    summary.loc[~summary["eligible_for_delta"], "delta_missing_reason"] = "insufficient_pre_months"
    if "t0_event_month" in summary.columns:
        summary["t0_event_month"] = summary["t0_event_month"].astype("string")
    summary["N_members"] = pd.to_numeric(summary["N_members"], errors="coerce").astype("Int64")
    summary["N_controls"] = pd.to_numeric(summary["N_controls"], errors="coerce").astype("Int64")
    return summary


@dataclass
class Step:
    """Materialize BigQuery panels used across downstream steps."""

    name: str = "materialize"

    def run(self, ctx: RunContext) -> None:
        if _fixture_mode(ctx.cfg):
            ctx.cfg.setdefault("_repo_root", ctx.paths.get("repo_root"))
            ctx.cache["panels"] = _load_fixture_panels(ctx)
            return

        _ensure_bigquery_available()
        params = _build_param_dict(ctx)
        dataform_cfg = {}
        mat_cfg = ctx.cfg.get("materialize") if isinstance(ctx.cfg, dict) else None
        if isinstance(mat_cfg, dict):
            dataform_cfg = mat_cfg.get("dataform", {}) or {}
        project = (
            dataform_cfg.get("project")
            or params.get("project")
            or ctx.cfg.get("bigquery", {}).get("project")
        )
        if not project:
            raise ValueError("Dataform project not configured for materialize step.")

        schema_overrides = dataform_cfg.get("schemas", {}) if isinstance(dataform_cfg, dict) else {}

        def _load_dataform_table(label: str) -> pd.DataFrame:
            schema, table = _DATAFORM_TABLES[label]
            dataset = schema_overrides.get(schema, schema)
            fqtn = f"{project}.{dataset}.{table}"
            ctx.logger.info({"event": "materialize_fetch_table", "table": fqtn})
            return bq.query_df(f"SELECT * FROM `{fqtn}`")

        panels = {
            "coverage": _load_dataform_table("coverage"),
            "awarded_block": _load_dataform_table("awarded_block"),
            "membership": _load_dataform_table("membership"),
            "shares": _load_dataform_table("shares_member"),
            "presence": _load_dataform_table("presence"),
            "controls": _load_dataform_table("shares_control"),
        }

        coverage_df = _rename_frame(panels["coverage"], "coverage")
        membership_df = _rename_frame(panels["membership"], "membership")
        shares_df = _clamp_event_month(_rename_frame(panels["shares"], "shares"))
        controls_df = _clamp_event_month(_rename_frame(panels["controls"], "controls"))
        awarded_block_df = panels["awarded_block"].rename(
            columns={"program": "program_id", "category": "category_id", "month_date": "month"}
        )
        awarded_block_df = _coerce_ids(awarded_block_df)
        presence_df = _rename_frame(panels.get("presence"), "presence")

        controls_sufficiency_df = _build_controls_sufficiency(
            shares_df,
            controls_df,
            int(params.get("MIN_PRE_MONTHS", 3)),
        )

        dataset_exit_map = _build_dataset_exit_map(
            presence_df,
            start_month=str(params.get("START_MONTH")),
            end_month=str(params.get("END_MONTH")),
            consecutive_absence=2,
        )

        ctx.cache["panels"] = {
            "coverage_df": coverage_df,
            "awarded_block_df": awarded_block_df,
            "membership_monthly_df": membership_df,
            "shares_member_df": shares_df,
            "shares_control_df": controls_df,
            "controls_sufficiency_df": controls_sufficiency_df,
            "presence_df": presence_df,
            "dataset_exit_map": dataset_exit_map,
            "pulse_summary_df": pd.DataFrame(),
            "did_summary_df": pd.DataFrame(),
            "params": params,
        }
