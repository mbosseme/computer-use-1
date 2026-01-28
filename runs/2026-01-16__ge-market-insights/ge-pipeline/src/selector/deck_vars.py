from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


REQUIRED_TOP_LEVEL_KEYS = {"headline", "program_split", "recon_policy", "drivers", "examples", "appendix"}
REQUIRED_HEADLINE_KEYS = {
    "pct_sustained",
    "median_time_to_target_mo",
    "portfolio_mean_pp",
    "eligible_total",
    "cohorts_total",
}
REQUIRED_DRIVERS_KEYS = {"start_buckets", "dollars_shifted"}
REQUIRED_DOLLARS_KEYS = {"positive", "negative", "net"}
REQUIRED_EXAMPLES_KEYS = {"wins", "no_gain", "losses"}
REQUIRED_RECON_KEYS = {"gap_max_pct", "overlap_min"}
REQUIRED_APPENDIX_KEYS = {"manufacturers", "by_manufacturer"}


def validate_deck_payload(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("deck_vars payload must be a dictionary.")
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in payload]
    if missing:
        raise ValueError(f"deck_vars payload missing keys: {missing}")

    headline = payload["headline"]
    if not isinstance(headline, dict):
        raise ValueError("headline must be a dictionary.")
    missing_headline = [key for key in REQUIRED_HEADLINE_KEYS if key not in headline]
    if missing_headline:
        raise ValueError(f"headline missing keys: {missing_headline}")

    drivers = payload["drivers"]
    if not isinstance(drivers, dict):
        raise ValueError("drivers must be a dictionary.")
    missing_drivers = [key for key in REQUIRED_DRIVERS_KEYS if key not in drivers]
    if missing_drivers:
        raise ValueError(f"drivers missing keys: {missing_drivers}")
    dollars = drivers["dollars_shifted"]
    if not isinstance(dollars, dict):
        raise ValueError("drivers.dollars_shifted must be a dictionary.")
    missing_dollars = [key for key in REQUIRED_DOLLARS_KEYS if key not in dollars]
    if missing_dollars:
        raise ValueError(f"dollars_shifted missing keys: {missing_dollars}")

    examples = payload["examples"]
    if not isinstance(examples, dict):
        raise ValueError("examples must be a dictionary.")
    missing_examples = [key for key in REQUIRED_EXAMPLES_KEYS if key not in examples]
    if missing_examples:
        raise ValueError(f"examples missing keys: {missing_examples}")
    for key in REQUIRED_EXAMPLES_KEYS:
        if not isinstance(examples[key], list):
            raise ValueError(f"examples.{key} must be a list.")

    recon_policy = payload["recon_policy"]
    if not isinstance(recon_policy, dict):
        raise ValueError("recon_policy must be a dictionary.")
    missing_recon = [key for key in REQUIRED_RECON_KEYS if key not in recon_policy]
    if missing_recon:
        raise ValueError(f"recon_policy missing keys: {missing_recon}")

    appendix = payload["appendix"]
    if not isinstance(appendix, dict):
        raise ValueError("appendix must be a dictionary.")
    missing_appendix = [key for key in REQUIRED_APPENDIX_KEYS if key not in appendix]
    if missing_appendix:
        raise ValueError(f"appendix missing keys: {missing_appendix}")
    if not isinstance(appendix["manufacturers"], list):
        raise ValueError("appendix.manufacturers must be a list.")
    if not isinstance(appendix["by_manufacturer"], dict):
        raise ValueError("appendix.by_manufacturer must be a dictionary.")

    filters = payload.get("filters")
    if filters is not None and not isinstance(filters, dict):
        raise ValueError("filters must be a dictionary when provided.")

    integrity = payload.get("integrity")
    if integrity is not None:
        if not isinstance(integrity, dict):
            raise ValueError("integrity must be a dictionary when provided.")
        expected = {"pretrend_risk", "placebo_risk", "retention_issues"}
        missing_integrity = [key for key in expected if key not in integrity]
        if missing_integrity:
            raise ValueError(f"integrity missing keys: {missing_integrity}")

    reconciliation = payload.get("reconciliation")
    if reconciliation is not None and not isinstance(reconciliation, dict):
        raise ValueError("reconciliation must be a dictionary when provided.")


def _coerce_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return float(value)
    if isinstance(value, (int,)):
        return float(value)
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(converted):
        return None
    return converted


def _coerce_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int,)):
        return int(value)
    try:
        converted = int(float(value))
    except (TypeError, ValueError):
        return None
    return converted


def _safe_percent(value: float, decimals: int = 1) -> float:
    return round(float(value) * 100.0, decimals)


def _percent_from_fraction(value: float, decimals: int = 2) -> float:
    return round(float(value) * 100.0, decimals)


def _sanitize_for_json(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {key: _sanitize_for_json(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_sanitize_for_json(item) for item in payload]
    if isinstance(payload, (pd.Timestamp,)):
        return payload.isoformat()
    if isinstance(payload, float) and math.isnan(payload):
        return None
    return payload


@dataclass
class PortfolioStats:
    pct_sustained: float
    median_time_to_target: Optional[float]
    portfolio_mean_delta: float
    eligible_count: int
    total_count: int
    recent_mean_delta: Optional[float] = None
    direction_positive_pct: Optional[float] = None
    direction_positive_mean: Optional[float] = None
    direction_negative_mean: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "pct_sustained": self.pct_sustained,
            "median_time_to_target": self.median_time_to_target,
            "portfolio_mean_delta": self.portfolio_mean_delta,
            "eligible_count": self.eligible_count,
            "total_count": self.total_count,
            "recent_mean_delta": self.recent_mean_delta,
            "direction_positive_pct": self.direction_positive_pct,
            "direction_positive_mean": self.direction_positive_mean,
            "direction_negative_mean": self.direction_negative_mean,
        }
        return _sanitize_for_json(payload)


@dataclass
class ShowcaseCase:
    program_id: str
    category_id: str
    delta_7_12: float
    delta_0_6: Optional[float]
    t0_event_month: Optional[str]
    n_members: Optional[int]
    n_controls: Optional[int]
    member_t0_spend_6m: Optional[float]
    recon_spend_gap_pct: Optional[float]
    overlap_ratio: Optional[float]
    dollars_shifted: Optional[float]
    case_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    integrity_flags: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self, *, precision_pp: int = 2) -> Dict[str, Any]:
        payload = {
            "program_id": self.program_id,
            "category_id": self.category_id,
            "delta_pp": round(self.delta_7_12 * 100.0, precision_pp),
            "delta_0_6_pp": round(self.delta_0_6 * 100.0, precision_pp) if self.delta_0_6 is not None else None,
            "t0": self.t0_event_month,
            "members": self.n_members,
            "controls": self.n_controls,
            "member_t0_spend_6m": round(self.member_t0_spend_6m, 2) if self.member_t0_spend_6m is not None else None,
            "spend_gap_pct": round(self.recon_spend_gap_pct, 2) if self.recon_spend_gap_pct is not None else None,
            "overlap": round(self.overlap_ratio, 3) if self.overlap_ratio is not None else None,
            "dollars_shifted": round(self.dollars_shifted, 2) if self.dollars_shifted is not None else None,
            "case_type": self.case_type,
        }
        payload.update(self.metadata)
        if self.integrity_flags:
            payload["integrity_flags"] = self.integrity_flags
        return _sanitize_for_json(payload)


def _eligible_mask(df: pd.DataFrame) -> pd.Series:
    mask = df["delta_7_12"].notna()
    if "delta_missing_reason" in df.columns:
        mask &= df["delta_missing_reason"].fillna("").str.lower().eq("ok")
    if "eligible_for_delta" in df.columns:
        mask &= df["eligible_for_delta"].fillna(False).astype(bool)
    return mask


def _meaningful_mask(df: pd.DataFrame, threshold: float) -> pd.Series:
    mask = _eligible_mask(df)
    return mask & (df["delta_7_12"].fillna(float("-inf")) >= threshold)


def compute_portfolio_stats(
    df: pd.DataFrame,
    target_lift: float,
    *,
    recent_year_cutoff: Optional[int] = None,
) -> PortfolioStats:
    total = int(df.shape[0])
    if total == 0:
        return PortfolioStats(
            pct_sustained=0.0,
            median_time_to_target=None,
            portfolio_mean_delta=0.0,
            eligible_count=0,
            total_count=0,
        )

    work = df.copy()
    for col in ("delta_7_12", "delta_0_6", "delta_time_to_target_month"):
        if col in work:
            work[col] = pd.to_numeric(work[col], errors="coerce")

    eligible_mask = _eligible_mask(work)
    eligible = work.loc[eligible_mask].copy()
    eligible_count = int(eligible.shape[0])
    if eligible_count == 0:
        return PortfolioStats(
            pct_sustained=0.0,
            median_time_to_target=None,
            portfolio_mean_delta=0.0,
            eligible_count=0,
            total_count=total,
        )

    sustained_mask = eligible["delta_7_12"] >= target_lift
    pct_sustained = float(sustained_mask.mean()) if eligible_count else 0.0

    time_to_target = eligible.loc[sustained_mask, "delta_time_to_target_month"].dropna()
    median_ttt = float(time_to_target.median()) if not time_to_target.empty else None
    if median_ttt is not None:
        median_ttt = round(median_ttt, 1)

    portfolio_mean_pp = float(eligible["delta_7_12"].mean())

    recent_mean_pp: Optional[float] = None
    if "t0_event_month" in eligible.columns:
        t0 = pd.to_datetime(eligible["t0_event_month"], format="%Y-%m", errors="coerce")
        if recent_year_cutoff is None:
            recent_year_cutoff = datetime.now(timezone.utc).year
        recent = eligible.loc[t0.dt.year >= recent_year_cutoff, "delta_7_12"].dropna()
        if not recent.empty:
            recent_mean_pp = float(recent.mean())

    positive = eligible.loc[eligible["delta_7_12"] > 0.0, "delta_7_12"]
    negative = eligible.loc[eligible["delta_7_12"] < 0.0, "delta_7_12"]
    direction_positive_pct = float(len(positive) / eligible_count) if eligible_count else 0.0
    direction_positive_mean = (
        float(positive.mean()) if not positive.empty else None
    )
    direction_negative_mean = (
        float(negative.mean()) if not negative.empty else None
    )

    return PortfolioStats(
        pct_sustained=pct_sustained,
        median_time_to_target=median_ttt,
        portfolio_mean_delta=portfolio_mean_pp,
        eligible_count=eligible_count,
        total_count=total,
        recent_mean_delta=recent_mean_pp,
        direction_positive_pct=direction_positive_pct,
        direction_positive_mean=direction_positive_mean,
        direction_negative_mean=direction_negative_mean,
    )


def _resolve_gap_threshold(series: pd.Series, threshold: float) -> float:
    if series.dropna().empty:
        return threshold
    max_abs = series.dropna().abs().max()
    if max_abs <= 1.0 + 1e-9:
        return threshold
    return threshold * 100.0


def _bool_from_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"}).fillna(False)


def _collect_overlap(df: pd.DataFrame) -> Optional[str]:
    for candidate in ("facility_overlap_ratio", "overlap", "overlap_ratio"):
        if candidate in df.columns:
            return candidate
    return None


def _collect_gap(df: pd.DataFrame) -> Optional[str]:
    for candidate in ("recon_spend_gap_pct", "spend_gap_pct", "dashboard_gap_pct"):
        if candidate in df.columns:
            return candidate
    return None


def _collect_taxonomy(df: pd.DataFrame) -> Optional[List[str]]:
    cols = [c for c in ("taxonomy_mapped", "category_mapped", "mapped_taxonomy_flag", "mapped_taxonomy") if c in df.columns]
    return cols or None


def _sort_key(df: pd.DataFrame, ascending: bool = False) -> List[str]:
    key = [
        "delta_7_12",
        "member_t0_total_spend_6m",
        "N_members_measured",
        "N_members",
    ]
    return key


def _prepare_for_ranking(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for col in [
        "delta_7_12",
        "delta_0_6",
        "member_t0_total_spend_6m",
        "N_members_measured",
        "N_members",
        "N_controls_measured",
        "N_controls",
    ]:
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors="coerce")
    if "t0_event_month" in work.columns:
        work["_t0_dt"] = pd.to_datetime(work["t0_event_month"], format="%Y-%m", errors="coerce")
    else:
        work["_t0_dt"] = pd.NaT
    return work


def _rank_cases(df: pd.DataFrame, *, ascending: bool, include_datetime: bool = True) -> pd.DataFrame:
    work = _prepare_for_ranking(df)
    candidate_columns = [
        ("delta_7_12", ascending),
        ("member_t0_total_spend_6m", False),
        ("N_members_measured", False),
        ("N_members", False),
    ]
    sort_columns: List[str] = []
    ascending_flags: List[bool] = []
    for column, asc in candidate_columns:
        if column in work.columns:
            sort_columns.append(column)
            ascending_flags.append(asc)
    if include_datetime and "_t0_dt" in work.columns:
        sort_columns.append("_t0_dt")
        ascending_flags.append(True)
    if not sort_columns:
        return work
    work = work.sort_values(sort_columns, ascending=ascending_flags, na_position="last")
    return work


def select_showcase_cases(
    df: pd.DataFrame,
    *,
    target_lift: float,
    recon_gap_max_pct: float = 0.30,
    overlap_min: float = 0.30,
    no_gain_window_pp: float = 1.0,
    max_wins: int = 2,
    max_no_gain: int = 1,
    max_losses: int = 2,
    min_members_for_losses: int = 20,
) -> Dict[str, List[ShowcaseCase]]:
    if df.empty:
        return {"wins": [], "no_gain": [], "losses": []}

    work = df.copy()
    work["member_t0_total_spend_6m"] = pd.to_numeric(work["member_t0_total_spend_6m"], errors="coerce")
    work["control_t0_total_spend_6m"] = pd.to_numeric(work["control_t0_total_spend_6m"], errors="coerce")

    gap_col = _collect_gap(work)
    overlap_col = _collect_overlap(work)
    taxonomy_cols = _collect_taxonomy(work)

    if gap_col:
        gap_series = pd.to_numeric(work[gap_col], errors="coerce")
        if gap_series.notna().any():
            gap_threshold = _resolve_gap_threshold(gap_series, recon_gap_max_pct)
            work["gate_recon_gap"] = gap_series.abs() <= gap_threshold
            work.loc[gap_series.isna(), "gate_recon_gap"] = False
        else:
            work["gate_recon_gap"] = False
    else:
        work["gate_recon_gap"] = False

    if overlap_col:
        overlap_series = pd.to_numeric(work[overlap_col], errors="coerce")
        if overlap_series.notna().any():
            work["gate_overlap"] = overlap_series >= overlap_min
            work.loc[overlap_series.isna(), "gate_overlap"] = False
        else:
            work["gate_overlap"] = False
    else:
        work["gate_overlap"] = False

    if "member_t0_total_spend_6m" in work.columns and "control_t0_total_spend_6m" in work.columns:
        member_zero = work["member_t0_total_spend_6m"].fillna(0.0) <= 0.0
        control_zero = work["control_t0_total_spend_6m"].fillna(0.0) <= 0.0
        work["gate_nonzero_symmetry"] = ~(member_zero ^ control_zero)
    else:
        work["gate_nonzero_symmetry"] = True

    if taxonomy_cols:
        taxonomy_flag = pd.Series(False, index=work.index)
        for col in taxonomy_cols:
            taxonomy_flag = taxonomy_flag | _bool_from_series(work[col])
        work["gate_taxonomy_mapped"] = taxonomy_flag
    else:
        work["gate_taxonomy_mapped"] = True

    work["passes_gates"] = (
        work["gate_recon_gap"]
        & work["gate_overlap"]
        & work["gate_nonzero_symmetry"]
        & work["gate_taxonomy_mapped"]
    )

    eligible_mask = _eligible_mask(work)
    eligible = work.loc[eligible_mask & work["passes_gates"]].copy()
    if eligible.empty:
        return {"wins": [], "no_gain": [], "losses": []}

    wins = eligible.loc[eligible["delta_7_12"] >= target_lift]
    wins_ranked = _rank_cases(wins, ascending=False)
    if len(wins_ranked) < max_wins:
        fallback = eligible.loc[eligible["delta_7_12"] > 0]
        fallback_ranked = _rank_cases(fallback, ascending=False)
        wins_ranked = pd.concat([wins_ranked, fallback_ranked]).drop_duplicates(subset=["program_id", "category_id"])
    wins_ranked = wins_ranked.head(max_wins)

    no_gain_window = no_gain_window_pp / 100.0 if no_gain_window_pp > 1 else no_gain_window_pp
    no_gain_candidates = eligible.loc[eligible["delta_7_12"].abs() <= no_gain_window]
    if no_gain_candidates.empty:
        no_gain_candidates = eligible.copy()
    no_gain_ranked = _rank_cases(no_gain_candidates, ascending=True)
    no_gain_ranked = no_gain_ranked.head(max_no_gain)

    members_measured = (
        pd.to_numeric(eligible["N_members_measured"], errors="coerce")
        if "N_members_measured" in eligible.columns
        else pd.to_numeric(eligible["N_members"], errors="coerce")
    )
    losses = eligible.loc[
        (eligible["delta_7_12"] < 0)
        & (members_measured.fillna(0) >= float(min_members_for_losses))
    ]
    losses_ranked = _rank_cases(losses, ascending=True)
    if len(losses_ranked) < max_losses:
        fallback_losses = eligible.loc[eligible["delta_7_12"] < 0]
        fallback_ranked = _rank_cases(fallback_losses, ascending=True)
        losses_ranked = pd.concat([losses_ranked, fallback_ranked]).drop_duplicates(
            subset=["program_id", "category_id"]
        )
    losses_ranked = losses_ranked.head(max_losses)

    def _build_cases(frame: pd.DataFrame, case_type: str) -> List[ShowcaseCase]:
        cases: List[ShowcaseCase] = []
        for _, row in frame.iterrows():
            dollars_shifted = None
            if pd.notna(row.get("member_t0_total_spend_6m")) and pd.notna(row.get("delta_7_12")):
                dollars_shifted = float(row["member_t0_total_spend_6m"]) * float(row["delta_7_12"])
            sustained = bool(row.get("meaningful_lift_7_12")) or (pd.notna(row.get("delta_7_12")) and float(row.get("delta_7_12", 0.0)) >= target_lift)
            delta_0_6_val = _coerce_float(row.get("delta_0_6"))
            pretrend_risk = bool(row.get("thin_pre", False)) or not bool(row.get("has_pre_common_ge_MIN", True))
            retention_ok = not bool(row.get("weight_coverage_clamped", False))
            placebo_flag = bool(delta_0_6_val is not None and delta_0_6_val >= target_lift and not sustained)
            integrity_flags = {
                "pretrend_risk_flag": pretrend_risk,
                "placebo_flag": placebo_flag,
                "retention_ok": retention_ok,
            }
            case = ShowcaseCase(
                program_id=str(row.get("program_id", "") or ""),
                category_id=str(row.get("category_id", "") or ""),
                delta_7_12=float(row.get("delta_7_12", 0.0)),
                delta_0_6=_coerce_float(row.get("delta_0_6")),
                t0_event_month=str(row.get("t0_event_month")) if pd.notna(row.get("t0_event_month")) else None,
                n_members=_coerce_int(row.get("N_members_measured") or row.get("N_members")),
                n_controls=_coerce_int(row.get("N_controls_measured") or row.get("N_controls")),
                member_t0_spend_6m=_coerce_float(row.get("member_t0_total_spend_6m")),
                recon_spend_gap_pct=_coerce_float(row.get(gap_col)) if gap_col else None,
                overlap_ratio=_coerce_float(row.get(overlap_col)) if overlap_col else None,
                dollars_shifted=dollars_shifted,
                case_type=case_type,
                metadata={
                    "passes_gates": True,
                },
                integrity_flags=integrity_flags,
            )
            cases.append(case)
        return cases

    return {
        "wins": _build_cases(wins_ranked, "win"),
        "no_gain": _build_cases(no_gain_ranked, "no_gain"),
        "losses": _build_cases(losses_ranked, "loss"),
    }


def _program_split(
    df: pd.DataFrame,
    *,
    target_lift: float,
) -> List[Dict[str, Any]]:
    if df.empty or "program_id" not in df.columns:
        return []
    work = df.copy()
    work["program_id"] = work["program_id"].astype(str)
    eligible_mask = _eligible_mask(work)
    aggregates: List[Dict[str, Any]] = []
    for program, portion in work.loc[eligible_mask].groupby("program_id"):
        sustained = (portion["delta_7_12"] >= target_lift).sum()
        entry = {
            "program_id": program,
            "eligible": int(portion.shape[0]),
            "sustained": int(sustained),
            "delta_mean_pp": _percent_from_fraction(float(portion["delta_7_12"].mean())) if not portion.empty else 0.0,
            "delta_median_pp": _percent_from_fraction(float(portion["delta_7_12"].median())) if not portion.empty else 0.0,
        }
        aggregates.append(entry)
    aggregates.sort(key=lambda item: item["program_id"])
    return aggregates


def _bucket_label(value: Optional[float]) -> Optional[str]:
    if value is None or math.isnan(value):
        return None
    if value < 0.20 - 1e-9:
        return "0–20%"
    if value < 0.50 - 1e-9:
        return "20–50%"
    return "50%+"


def _bucketed_drivers(
    df: pd.DataFrame,
    *,
    target_lift: float,
) -> List[Dict[str, Any]]:
    if df.empty:
        return []
    work = df.copy()
    member_pre_series = work.get("member_pre_mean", pd.Series(index=work.index, dtype="float64"))
    work["member_pre_mean"] = pd.to_numeric(member_pre_series, errors="coerce")
    work["bucket"] = work["member_pre_mean"].apply(_bucket_label)
    eligible_mask = _eligible_mask(work)
    payload: List[Dict[str, Any]] = []
    for bucket, portion in work.loc[eligible_mask].groupby("bucket", dropna=True):
        if bucket is None:
            continue
        win_rate = (portion["delta_7_12"] >= target_lift).mean() if not portion.empty else 0.0
        entry = {
            "bucket": bucket,
            "cohorts": int(portion.shape[0]),
            "win_rate_pct": _safe_percent(win_rate),
            "avg_delta_pp": _percent_from_fraction(float(portion["delta_7_12"].mean())) if not portion.empty else 0.0,
        }
        payload.append(entry)
    payload.sort(key=lambda item: {"0–20%": 0, "20–50%": 1, "50%+": 2}.get(item["bucket"], 99))
    return payload


def _dollar_shift(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {"positive": 0.0, "negative": 0.0, "net": 0.0}
    work = df.copy()
    member_spend_series = work.get("member_t0_total_spend_6m", pd.Series(index=work.index, dtype="float64"))
    delta_series = work.get("delta_7_12", pd.Series(index=work.index, dtype="float64"))
    work["member_t0_total_spend_6m"] = pd.to_numeric(member_spend_series, errors="coerce")
    work["delta_7_12"] = pd.to_numeric(delta_series, errors="coerce")
    eligible_mask = _eligible_mask(work)
    eligible = work.loc[eligible_mask].copy()
    if eligible.empty:
        return {"positive": 0.0, "negative": 0.0, "net": 0.0}
    eligible["dollars_shifted"] = eligible["member_t0_total_spend_6m"] * eligible["delta_7_12"]
    eligible["dollars_shifted"] = eligible["dollars_shifted"].fillna(0.0)
    positive = eligible.loc[eligible["dollars_shifted"] > 0.0, "dollars_shifted"].sum()
    negative = eligible.loc[eligible["dollars_shifted"] < 0.0, "dollars_shifted"].sum()
    net = positive + negative
    return {
        "positive": round(float(positive), 2),
        "negative": round(float(negative), 2),
        "net": round(float(net), 2),
    }


def build_deck_variables(
    answers_df: pd.DataFrame,
    *,
    target_lift: float,
    recon_gap_max_pct: float = 0.30,
    overlap_min: float = 0.30,
    no_gain_window_pp: float = 1.0,
    max_wins: int = 2,
    max_no_gain: int = 1,
    max_losses: int = 2,
    min_members_for_losses: int = 20,
    recent_year_cutoff: Optional[int] = None,
    min_members: int = 0,
    min_controls: int = 0,
    min_member_spend_6m: float = 0.0,
    category_excludes: Optional[Iterable[str]] = None,
    manufacturer_focus: Optional[Iterable[str]] = None,
    reconciliation_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    original_row_count = int(answers_df.shape[0])
    work = answers_df.copy()

    required_columns_defaults: Dict[str, Any] = {
        "program_id": pd.Series(dtype="string"),
        "category_id": pd.Series(dtype="string"),
        "delta_7_12": pd.Series(dtype="float64"),
        "delta_0_6": pd.Series(dtype="float64"),
        "delta_time_to_target_month": pd.Series(dtype="float64"),
        "N_members": pd.Series(dtype="float64"),
        "N_controls": pd.Series(dtype="float64"),
        "member_t0_total_spend_6m": pd.Series(dtype="float64"),
        "recon_spend_gap_pct": pd.Series(dtype="float64"),
        "facility_overlap_ratio": pd.Series(dtype="float64"),
    }
    for column, default_series in required_columns_defaults.items():
        if column not in work.columns:
            work[column] = default_series

    category_excludes_set = {
        str(item).strip().lower() for item in (category_excludes or []) if item not in (None, "")
    }
    applied_category_excludes: List[str] = []
    if category_excludes_set and "category_id" in work.columns:
        category_series = work["category_id"].astype(str)
        applied_category_excludes = sorted(
            {
                cat
                for cat in category_series.unique()
                if cat.strip().lower() in category_excludes_set
            }
        )
        mask = ~category_series.str.strip().str.lower().isin(category_excludes_set)
        work = work.loc[mask].copy()

    numeric_columns = [
        "N_members",
        "N_controls",
        "N_members_measured",
        "N_controls_measured",
        "member_t0_total_spend_6m",
        "control_t0_total_spend_6m",
        "delta_7_12",
        "delta_0_6",
        "delta_time_to_target_month",
    ]
    for column in numeric_columns:
        if column in work.columns:
            work[column] = pd.to_numeric(work[column], errors="coerce")

    if min_members and "N_members" in work.columns:
        work = work.loc[work["N_members"].fillna(0) >= min_members]
    if min_controls and "N_controls" in work.columns:
        work = work.loc[work["N_controls"].fillna(0) >= min_controls]
    if min_member_spend_6m and "member_t0_total_spend_6m" in work.columns:
        work = work.loc[work["member_t0_total_spend_6m"].fillna(0.0) >= float(min_member_spend_6m)]

    filtered_row_count = int(work.shape[0])

    stats = compute_portfolio_stats(
        work,
        target_lift,
        recent_year_cutoff=recent_year_cutoff,
    )

    showcase = select_showcase_cases(
        work,
        target_lift=target_lift,
        recon_gap_max_pct=recon_gap_max_pct,
        overlap_min=overlap_min,
        no_gain_window_pp=no_gain_window_pp,
        max_wins=max_wins,
        max_no_gain=max_no_gain,
        max_losses=max_losses,
        min_members_for_losses=min_members_for_losses,
    )

    eligible_mask = _eligible_mask(work)
    eligible = work.loc[eligible_mask].copy()
    eligible["delta_0_6"] = pd.to_numeric(eligible["delta_0_6"], errors="coerce")
    eligible["delta_7_12"] = pd.to_numeric(eligible["delta_7_12"], errors="coerce")
    early_mask = eligible["delta_0_6"] >= target_lift
    sustained_mask = eligible["delta_7_12"] >= target_lift
    both_mask = early_mask & sustained_mask
    early_only_mask = early_mask & ~sustained_mask
    late_bloom_mask = sustained_mask & ~early_mask

    program_split = _program_split(work, target_lift=target_lift)
    drivers = _bucketed_drivers(work, target_lift=target_lift)
    dollars_shifted = _dollar_shift(work)

    recent_mean_pp = (
        _percent_from_fraction(stats.recent_mean_delta) if stats.recent_mean_delta is not None else None
    )
    direction_positive_pct = (
        round(stats.direction_positive_pct * 100.0, 1) if stats.direction_positive_pct is not None else None
    )
    direction_positive_mean_pp = (
        _percent_from_fraction(stats.direction_positive_mean) if stats.direction_positive_mean is not None else None
    )
    direction_negative_mean_pp = (
        _percent_from_fraction(stats.direction_negative_mean) if stats.direction_negative_mean is not None else None
    )

    headline = {
        "eligible_total": stats.eligible_count,
        "cohorts_total": stats.total_count,
        "pct_sustained": round(stats.pct_sustained * 100.0, 1),
        "median_time_to_target_mo": stats.median_time_to_target,
        "portfolio_mean_pp": _percent_from_fraction(stats.portfolio_mean_delta),
        "recent_mean_pp": recent_mean_pp,
        "early": int(early_mask.sum()),
        "sustained": int(sustained_mask.sum()),
        "both": int(both_mask.sum()),
        "early_only": int(early_only_mask.sum()),
        "late_bloom": int(late_bloom_mask.sum()),
        "direction_positive_pct": direction_positive_pct,
        "direction_positive_mean_pp": direction_positive_mean_pp,
        "direction_negative_mean_pp": direction_negative_mean_pp,
        "target_lift_pp": _percent_from_fraction(target_lift),
    }

    recon_policy = {
        "gap_max_pct": recon_gap_max_pct,
        "overlap_min": overlap_min,
        "no_zero_vs_nonzero": True,
        "require_mapped_taxonomy": True,
    }

    examples = {
        "wins": [case.to_dict() for case in showcase["wins"]],
        "no_gain": [case.to_dict() for case in showcase["no_gain"]],
        "losses": [case.to_dict() for case in showcase["losses"]],
    }

    def _flag_counts(cases: List[ShowcaseCase], flag: str) -> int:
        return sum(1 for case in cases if case.integrity_flags.get(flag))

    integrity_summary = {
        "pretrend_risk": _flag_counts(showcase["wins"], "pretrend_risk_flag")
        + _flag_counts(showcase["no_gain"], "pretrend_risk_flag")
        + _flag_counts(showcase["losses"], "pretrend_risk_flag"),
        "placebo_risk": _flag_counts(showcase["wins"], "placebo_flag")
        + _flag_counts(showcase["no_gain"], "placebo_flag")
        + _flag_counts(showcase["losses"], "placebo_flag"),
        "retention_issues": (
            sum(1 for case in showcase["wins"] if not case.integrity_flags.get("retention_ok", True))
            + sum(1 for case in showcase["no_gain"] if not case.integrity_flags.get("retention_ok", True))
            + sum(1 for case in showcase["losses"] if not case.integrity_flags.get("retention_ok", True))
        ),
    }

    manufacturers_focus_list = [str(item).strip() for item in manufacturer_focus or [] if item not in (None, "")]
    appendix = {
        "manufacturers": manufacturers_focus_list,
        "category_excludes": applied_category_excludes,
        "by_manufacturer": {},
    }

    filters_meta = {
        "recon_gap_max_pct": recon_gap_max_pct,
        "overlap_min": overlap_min,
        "no_gain_window_pp": no_gain_window_pp,
        "max_wins": max_wins,
        "max_no_gain": max_no_gain,
        "max_losses": max_losses,
        "min_members_for_losses": min_members_for_losses,
        "min_members": min_members,
        "min_controls": min_controls,
        "min_member_spend_6m": float(min_member_spend_6m),
        "recent_year_cutoff": recent_year_cutoff,
        "category_excludes": applied_category_excludes,
        "filtered_rows_before": original_row_count,
        "filtered_rows_after": filtered_row_count,
    }

    result = {
        "headline": _sanitize_for_json(headline),
        "program_split": _sanitize_for_json(program_split),
        "recon_policy": _sanitize_for_json(recon_policy),
        "drivers": {
            "start_buckets": _sanitize_for_json(drivers),
            "dollars_shifted": _sanitize_for_json(dollars_shifted),
        },
        "examples": examples,
        "appendix": _sanitize_for_json(appendix),
        "filters": _sanitize_for_json(filters_meta),
        "integrity": _sanitize_for_json(integrity_summary),
    }

    if reconciliation_summary is not None:
        result["reconciliation"] = _sanitize_for_json(reconciliation_summary)

    validate_deck_payload(result)

    return result
