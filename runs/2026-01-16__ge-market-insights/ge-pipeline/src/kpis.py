"""
PRD-aligned KPI helpers for event-study analysis.
- Computes lift series (members minus controls) by event_month
- Time-to-target and sustained lift metrics
- ATT window averages and narrative rows
- Delta (change-from-pre) helpers for manufacturer-centric analysis
"""
from __future__ import annotations
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np

class kpis:
    @staticmethod
    def lift_series(members_df: pd.DataFrame, controls_df: pd.DataFrame, program_id: str, category_id: str) -> pd.Series:
        m = (
            members_df.query("program_id == @program_id and category_id == @category_id")
            .groupby("event_month")["awarded_share_6m"].mean()
        )
        d = (
            controls_df.query("program_id == @program_id and category_id == @category_id")
            .groupby("event_month")["awarded_share_6m"].mean()
        )
        return (m - d).dropna()

    @staticmethod
    def time_to_target(lift: pd.Series, target_pp: float = 8) -> Optional[int]:
        """Return the first event_month >= 0 where lift meets/exceeds target in percentage points.

        Parameters
        ----------
        lift : pd.Series
            Index: event_month (int). Values: fractional lift (0.0–1.0).
        target_pp : float
            Threshold in percentage points (e.g., 8 for 8 pp).

        Returns
        -------
        Optional[int]
            First month index hitting threshold, or None if never hits.
        """
        if lift is None or len(lift) == 0:
            return None
        # Convert fraction -> percentage points for comparison
        post_pp = (lift * 100.0)
        post_pp = post_pp[post_pp.index >= 0]
        hit = post_pp[post_pp >= float(target_pp)]
        return None if hit.empty else int(hit.index.min())

    @staticmethod
    def sustained_lift(lift: pd.Series, lo: int = 7, hi: int = 12) -> Optional[float]:
        w = lift[(lift.index >= lo) & (lift.index <= hi)]
        return None if w.empty else float(w.mean())

    @staticmethod
    def att_windows(lift: pd.Series) -> Dict[str, Optional[float]]:
        def wmean(l: int, h: int) -> Optional[float]:
            w = lift[(lift.index >= l) & (lift.index <= h)]
            return None if w.empty else float(w.mean())
        return {"ATT_0_6": wmean(0, 6), "ATT_7_12": wmean(7, 12), "ATT_0_12": wmean(0, 12)}

    @staticmethod
    def narrative_row(program_id: str, category_id: str, lift: pd.Series, n_mem: int, n_ctrl: int, target_pp: float = 8) -> Dict[str, object]:
        aw = kpis.att_windows(lift)
        return {
            "program_id": program_id,
            "category_id": category_id,
            "time_to_target_month": kpis.time_to_target(lift, target_pp),
            "sustained_lift_pp": kpis.sustained_lift(lift, 7, 12),
            "pp_lift_0_6": aw["ATT_0_6"],
            "pp_lift_7_12": aw["ATT_7_12"],
            "N_members": int(n_mem),
            "N_controls": int(n_ctrl),
        }

    # ===== Delta (change-from-pre) helpers =====
    @staticmethod
    def _standardize_panel(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            return pd.DataFrame()
        rename_map = {
            "program": "program_id",
            "category": "category_id",
            "entity_code": "facility_id",
        }
        out = df.copy()
        cols = {k: v for k, v in rename_map.items() if k in out.columns and v not in out.columns}
        if cols:
            out = out.rename(columns=cols)
        for col in ("program_id", "category_id", "facility_id"):
            if col in out.columns:
                out[col] = out[col].astype(str)
        if "event_month" in out.columns:
            out["event_month"] = out["event_month"].astype(int)
        return out

    @staticmethod
    def _member_weights(df: pd.DataFrame) -> pd.Series:
        if df.empty:
            return pd.Series(dtype=float)
        base = df[(df["event_month"] == 0) & df.get("member_at_t0", pd.Series(dtype=bool)).fillna(False)]
        if base.empty:
            base = df[(df["event_month"] == 0) & df.get("member_flag", pd.Series(dtype=bool)).fillna(False)]
        if base.empty:
            min_evt = df["event_month"].min()
            base = df[df["event_month"] == min_evt]
        if base.empty or "total_cat_spend" not in df.columns:
            return pd.Series(dtype=float)

        cohort_ids = base["facility_id"].unique()
        if len(cohort_ids) == 0:
            return pd.Series(dtype=float)

        trailing_mask = df["event_month"].between(-5, 0)
        trailing = df[trailing_mask & df["facility_id"].isin(cohort_ids)]
        trailing_totals = trailing.groupby("facility_id")["total_cat_spend"].sum()

        baseline_totals = base.groupby("facility_id")["total_cat_spend"].sum()
        numerators = trailing_totals.reindex(cohort_ids, fill_value=0)
        fallback = baseline_totals.reindex(cohort_ids, fill_value=0)
        numerators = numerators.where(numerators > 0, fallback)
        numerators = numerators[numerators > 0]
        if numerators.empty:
            return pd.Series(dtype=float)
        total = numerators.sum()
        if total <= 0:
            return pd.Series(dtype=float)
        return (numerators / total).rename(None)

    @staticmethod
    def _control_weights(df: pd.DataFrame) -> pd.Series:
        if df.empty:
            return pd.Series(dtype=float)
        base = df[df["event_month"] == 0]
        if base.empty:
            min_evt = df["event_month"].min()
            base = df[df["event_month"] == min_evt]
        if base.empty or "total_cat_spend" not in df.columns:
            return pd.Series(dtype=float)

        facility_ids = base["facility_id"].unique()
        if len(facility_ids) == 0:
            return pd.Series(dtype=float)

        trailing_mask = df["event_month"].between(-5, 0)
        trailing = df[trailing_mask & df["facility_id"].isin(facility_ids)]
        trailing_totals = trailing.groupby("facility_id")["total_cat_spend"].sum()

        baseline_totals = base.groupby("facility_id")["total_cat_spend"].sum()
        numerators = trailing_totals.reindex(facility_ids, fill_value=0)
        fallback = baseline_totals.reindex(facility_ids, fill_value=0)
        numerators = numerators.where(numerators > 0, fallback)
        numerators = numerators[numerators > 0]
        if numerators.empty:
            return pd.Series(dtype=float)
        total = numerators.sum()
        if total <= 0:
            return pd.Series(dtype=float)
        return (numerators / total).rename(None)

    @staticmethod
    def _laspeyres_total(
        df: pd.DataFrame,
        weights: pd.Series,
        *,
        value_col: str = "total_cat_spend_6m",
    ) -> float | None:
        """Aggregate t0 cohort spend aligned with Laspeyres weights.

        Parameters
        ----------
        df : pd.DataFrame
            Panel data for members or controls.
        weights : pd.Series
            Facility weights produced by ``_member_weights`` or ``_control_weights``.
        value_col : str, keyword-only
            Column containing trailing 6m spend denominators. Falls back to ``total_cat_spend``
            if the preferred column is missing.

        Returns
        -------
        Optional[float]
            Sum of the latest pre/t0 denominators across the weighted cohort, or None if unavailable.
        """
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            return None
        if weights is None or weights.empty:
            return None
        if "facility_id" not in df.columns or "event_month" not in df.columns:
            return None

        subset = df[df["facility_id"].isin(weights.index)].copy()
        if subset.empty:
            return None

        if value_col not in subset.columns:
            if "total_cat_spend" not in subset.columns:
                return None
            subset[value_col] = subset["total_cat_spend"].astype(float)

        subset["event_month"] = pd.to_numeric(subset["event_month"], errors="coerce")
        subset = subset.dropna(subset=["event_month"])
        if subset.empty:
            return None
        subset["event_month"] = subset["event_month"].astype(int)

        pre_subset = subset[subset["event_month"] <= 0]
        if pre_subset.empty:
            pre_subset = subset

        latest = pre_subset.sort_values(["facility_id", "event_month"]).groupby("facility_id", sort=False).tail(1)
        totals = latest.set_index("facility_id")[value_col].astype(float)
        totals = totals.reindex(weights.index)
        totals = totals.dropna()
        totals = totals[totals > 0]
        if totals.empty:
            return None
        return float(totals.sum())

    @staticmethod
    def apply_exposure_mask(
        df: pd.DataFrame,
        consecutive_false: int = 2,
        *,
        flag_col: str = "member_flag",
        return_masked: bool = False,
    ) -> pd.DataFrame | Tuple[pd.DataFrame, set[str]]:
        """Drop post-t0 facility-months after consecutive absent membership flags.

        Parameters
        ----------
        df : pd.DataFrame
            Facility-month level panel. Must include ``facility_id`` and ``event_month``.
        consecutive_false : int
            Number of consecutive post-t0 months with ``flag_col`` False/NaN required
            before masking subsequent rows (default 2).
        flag_col : str, keyword-only
            Column containing membership indicators (default ``member_flag``).

        Returns
        -------
        pd.DataFrame
            Filtered DataFrame where rows on/after the ``consecutive_false``-th
            consecutive False month have been removed per facility.
        """

        if not isinstance(df, pd.DataFrame) or df.empty:
            return df
        if consecutive_false <= 1:
            consecutive_false = 1

        required_cols = {"facility_id", "event_month", flag_col}
        if not required_cols <= set(df.columns):
            return df

        work = df.copy()
        work["event_month"] = pd.to_numeric(work["event_month"], errors="coerce")
        work = work.dropna(subset=["event_month"])
        if work.empty:
            return work
        work["event_month"] = work["event_month"].astype(int)

        keep_masks: list[pd.Series] = []
        masked_facilities: set[str] = set()

        for _, group in work.groupby("facility_id", sort=False):
            group = group.sort_values("event_month")
            keep = pd.Series(True, index=group.index)
            fac_id = str(group["facility_id"].iloc[0]) if "facility_id" in group.columns and not group.empty else None

            post = group[group["event_month"] >= 0]
            if not post.empty:
                max_post = int(post["event_month"].max())
                idx_range = range(0, max_post + 1)

                membership = (
                    post.set_index("event_month")[flag_col]
                    .apply(lambda v: bool(v) if pd.notna(v) else False)
                    .reindex(idx_range)
                )
                membership = membership.where(membership.notna(), False).astype(bool)

                consecutive = 0
                exit_month: Optional[int] = None
                for month in idx_range:
                    flag = bool(membership.loc[month])
                    if flag:
                        consecutive = 0
                    else:
                        consecutive += 1
                        if consecutive >= consecutive_false:
                            exit_month = month
                            break

                if exit_month is not None:
                    keep &= group["event_month"] < exit_month
                    if fac_id is not None:
                        masked_facilities.add(fac_id)

            keep_masks.append(keep)

        if not keep_masks:
            return (work, masked_facilities) if return_masked else work

        keep_mask = pd.concat(keep_masks).reindex(work.index, fill_value=True)
        filtered = work.loc[keep_mask].sort_index()
        return (filtered, masked_facilities) if return_masked else filtered

    @staticmethod
    def _apply_dataset_exit_mask(
        df: pd.DataFrame,
        exit_map: Optional[Dict[str, pd.Timestamp]],
    ) -> tuple[pd.DataFrame, set[str]]:
        if (
            exit_map is None
            or not exit_map
            or not isinstance(df, pd.DataFrame)
            or df.empty
            or "facility_id" not in df.columns
            or "month" not in df.columns
        ):
            return df, set()
        work = df.copy()
        work["facility_id"] = work["facility_id"].astype(str)
        work["month"] = pd.to_datetime(work["month"], errors="coerce")
        work = work.dropna(subset=["facility_id", "month"])
        if work.empty:
            return work, set()
        exit_series = work["facility_id"].map(exit_map)
        mask = exit_series.notna() & (work["month"] >= exit_series)
        masked = set(work.loc[mask, "facility_id"].unique())
        filtered = work.loc[~mask]
        return filtered, masked

    @staticmethod
    def _weighted_series(
        df: pd.DataFrame,
        weights: pd.Series,
        drop_post_inactive: bool = False,
        *,
        exit_map: Optional[Dict[str, pd.Timestamp]] = None,
        masked_tracker: Optional[Dict[str, Dict[str, set[str]]]] = None,
        label: Optional[str] = None,
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        if df.empty or weights.empty:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        sub = df[df["facility_id"].isin(weights.index)].copy()
        if sub.empty or "awarded_share_6m" not in sub.columns:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        sub = sub.merge(weights.rename("w_i0"), left_on="facility_id", right_index=True, how="inner")
        sub, masked_exit = kpis._apply_dataset_exit_mask(sub, exit_map)
        if masked_tracker is not None and label and masked_exit:
            masked_tracker.setdefault(label, {}).setdefault("dataset_exit", set()).update(masked_exit)
        sub = sub.dropna(subset=["event_month"])
        if sub.empty:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        sub["event_month"] = sub["event_month"].astype(int)
        dataset_cov = sub.groupby("event_month")["w_i0"].sum().sort_index()

        if drop_post_inactive:
            sub, masked_exposure = kpis.apply_exposure_mask(
                sub,
                consecutive_false=2,
                return_masked=True,
            )
            if masked_tracker is not None and label and masked_exposure:
                masked_tracker.setdefault(label, {}).setdefault("program_exit", set()).update(masked_exposure)
        if sub.empty:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        sub = sub.dropna(subset=["event_month"])
        if sub.empty:
            return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
        sub["event_month"] = sub["event_month"].astype(int)
        final_cov = sub.groupby("event_month")["w_i0"].sum().sort_index()
        dataset_cov = dataset_cov.reindex(final_cov.index, fill_value=0.0)

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
        ).sort_index()
        return series, dataset_cov, final_cov

    @staticmethod
    def _apply_weight_coverage_guard(
        member_series: pd.Series,
        control_series: pd.Series,
        member_dataset_cov: pd.Series,
        control_dataset_cov: pd.Series,
        member_final_cov: pd.Series,
        control_final_cov: pd.Series,
        threshold: float,
    ) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, Dict[str, Any]]:
        metadata: Dict[str, Any] = {
            "weight_coverage_clamped": False,
            "weight_coverage_clamp_month": pd.NA,
            "pre_contract_baseline_included": False,
        }
        if threshold is None or not np.isfinite(threshold) or threshold <= 0:
            metadata["member_weight_coverage_min"] = (
                float(member_final_cov.min()) if isinstance(member_final_cov, pd.Series) and not member_final_cov.empty else np.nan
            )
            metadata["control_weight_coverage_min"] = (
                float(control_final_cov.min()) if isinstance(control_final_cov, pd.Series) and not control_final_cov.empty else np.nan
            )
            return (
                member_series,
                control_series,
                member_dataset_cov,
                control_dataset_cov,
                member_final_cov,
                control_final_cov,
                metadata,
            )

        clamp_months: list[int] = []
        pre_coverage_short: bool = False
        for cov in (member_dataset_cov, control_dataset_cov):
            if isinstance(cov, pd.Series) and not cov.empty:
                failing = cov[cov < threshold]
                if not failing.empty:
                    for idx in failing.index:
                        try:
                            idx_int = int(idx)
                        except (TypeError, ValueError):
                            continue
                        if idx_int < 0:
                            pre_coverage_short = True
                        else:
                            clamp_months.append(idx_int)

        if clamp_months:
            clamp_from = min(clamp_months)
            metadata["weight_coverage_clamped"] = True
            metadata["weight_coverage_clamp_month"] = clamp_from
            member_series = member_series[member_series.index < clamp_from]
            control_series = control_series[control_series.index < clamp_from]
            member_dataset_cov = member_dataset_cov[member_dataset_cov.index < clamp_from]
            control_dataset_cov = control_dataset_cov[control_dataset_cov.index < clamp_from]
            member_final_cov = member_final_cov[member_final_cov.index < clamp_from]
            control_final_cov = control_final_cov[control_final_cov.index < clamp_from]

        if pre_coverage_short:
            metadata["pre_contract_baseline_included"] = True

        metadata["member_weight_coverage_min"] = (
            float(member_final_cov.min()) if isinstance(member_final_cov, pd.Series) and not member_final_cov.empty else np.nan
        )
        metadata["control_weight_coverage_min"] = (
            float(control_final_cov.min()) if isinstance(control_final_cov, pd.Series) and not control_final_cov.empty else np.nan
        )
        metadata["member_weight_coverage"] = member_final_cov
        metadata["control_weight_coverage"] = control_final_cov
        return (
            member_series,
            control_series,
            member_dataset_cov,
            control_dataset_cov,
            member_final_cov,
            control_final_cov,
            metadata,
        )

    @staticmethod
    def _window_stats(series: pd.Series, lo: int, hi: int) -> tuple[Optional[float], int]:
        window = series[(series.index >= lo) & (series.index <= hi)].dropna()
        if window.empty:
            return None, 0
        return float(window.mean()), int(len(window))

    @staticmethod
    def _common_months(a: pd.Series, b: pd.Series, lo: int, hi: int) -> int:
        wa = set(a[(a.index >= lo) & (a.index <= hi)].dropna().index)
        wb = set(b[(b.index >= lo) & (b.index <= hi)].dropna().index)
        return int(len(wa & wb))

    @staticmethod
    def _delta_series(member_series: pd.Series, control_series: pd.Series, m_pre: float, c_pre: float) -> pd.Series:
        aligned = pd.DataFrame({
            "member": member_series,
            "control": control_series,
        })
        aligned = aligned.dropna(subset=["member", "control"])
        if aligned.empty:
            return pd.Series(dtype=float)
        aligned["delta"] = (aligned["member"] - m_pre) - (aligned["control"] - c_pre)
        return aligned["delta"].dropna().sort_index()

    @staticmethod
    def _time_to_target(delta: pd.Series, target: float) -> Optional[int]:
        if delta.empty:
            return None
        post = delta[delta.index >= 0]
        hit = post[post >= target]
        return None if hit.empty else int(hit.index.min())

    @staticmethod
    def _window_mean(delta: pd.Series, lo: int, hi: int) -> Optional[float]:
        if delta.empty:
            return None
        window = delta[(delta.index >= lo) & (delta.index <= hi)].dropna()
        if window.empty:
            return None
        return float(window.mean())

    @staticmethod
    def build_delta_summary(
        members_df: pd.DataFrame,
        controls_df: pd.DataFrame,
        target_pp: float = 0.02,
        min_pre_months: int = 3,
        min_common_months: int = 3,
        *,
        dataset_exit_map: Optional[Dict[str, pd.Timestamp]] = None,
        weight_coverage_guard: float = 0.5,
    ) -> pd.DataFrame:
        PRE_WINDOW = (-6, -1)
        POST_0_6 = (0, 6)
        POST_7_12 = (7, 12)

        members = kpis._standardize_panel(members_df)
        controls = kpis._standardize_panel(controls_df)

        def _t0_ids(
            df: pd.DataFrame,
            *,
            require_member: bool,
            positive_only: bool,
        ) -> set[str]:
            if df.empty or "facility_id" not in df.columns or "event_month" not in df.columns:
                return set()
            work = df[df["event_month"].astype("Int64", copy=False).eq(0)].copy()
            if work.empty:
                return set()
            if require_member:
                if "member_at_t0" in work.columns:
                    work = work[work["member_at_t0"].fillna(False).astype(bool)]
                elif "member_flag" in work.columns:
                    work = work[work["member_flag"].fillna(False).astype(bool)]
            if positive_only:
                spend_candidates = [
                    "t0_total_cat_spend_6m",
                    "total_cat_spend_6m",
                    "total_cat_spend",
                ]
                spend_col = next((c for c in spend_candidates if c in work.columns), None)
                if spend_col is not None:
                    spend_vals = pd.to_numeric(work[spend_col], errors="coerce")
                    work = work[spend_vals.fillna(0) > 0]
            if work.empty or "facility_id" not in work.columns:
                return set()
            return set(work["facility_id"].astype(str))

        member_program_counts = pd.Series(dtype=int)
        member_program_counts_dict: Dict[str, int] = {}
        program_t0_counts: Dict[Tuple[str, str], int] = {}
        category_t0_map: Dict[Tuple[str, str], Optional[str]] = {}

        if "program_id" in members.columns and "event_month" in members.columns:
            member_t0 = members[members["event_month"].astype("Int64", copy=False).eq(0)].copy()
            if "member_at_t0" in member_t0.columns:
                member_t0 = member_t0[member_t0["member_at_t0"].fillna(False).astype(bool)]
            elif "member_flag" in member_t0.columns:
                member_t0 = member_t0[member_t0["member_flag"].fillna(False).astype(bool)]

            if not member_t0.empty:
                member_t0["program_id"] = member_t0["program_id"].astype(str)
                if "category_id" in member_t0.columns:
                    member_t0["category_id"] = member_t0["category_id"].astype(str)
                if "facility_id" not in member_t0.columns:
                    member_t0["facility_id"] = pd.Series(pd.NA, index=member_t0.index, dtype="string")
                member_t0["facility_id"] = member_t0["facility_id"].astype(str)
                if "month" in member_t0.columns:
                    member_t0["t0_month"] = pd.to_datetime(member_t0["month"], errors="coerce")
                else:
                    member_t0["t0_month"] = pd.NaT
                member_t0["t0_month_key"] = member_t0["t0_month"].dt.strftime("%Y-%m")

                member_program_counts = (
                    member_t0.dropna(subset=["program_id", "facility_id"])
                    .drop_duplicates(subset=["program_id", "facility_id"])
                    .groupby("program_id")["facility_id"]
                    .nunique()
                )
                member_program_counts_dict = {str(k): int(v) for k, v in member_program_counts.items()}

                t0_counts_series = (
                    member_t0.dropna(subset=["program_id", "facility_id", "t0_month_key"])
                    .drop_duplicates(subset=["program_id", "facility_id", "t0_month_key"])
                    .groupby(["program_id", "t0_month_key"])
                    .size()
                )
                if not t0_counts_series.empty:
                    t0_counts_df = t0_counts_series.reset_index(name="count")
                    program_t0_counts = {
                        (str(row["program_id"]), str(row["t0_month_key"])): int(row["count"])
                        for _, row in t0_counts_df.iterrows()
                    }

                category_t0_series = (
                    member_t0.dropna(subset=["program_id", "category_id"])
                    .drop_duplicates(subset=["program_id", "category_id"])
                    .set_index(["program_id", "category_id"])["t0_month_key"]
                )
                if not category_t0_series.empty:
                    category_t0_df = category_t0_series.reset_index(name="t0_month_key")
                    category_t0_map = {
                        (str(row["program_id"]), str(row["category_id"])): (
                            row["t0_month_key"] if pd.notna(row["t0_month_key"]) else None
                        )
                        for _, row in category_t0_df.iterrows()
                    }
            else:
                member_program_counts_dict = {}
                program_t0_counts = {}
                category_t0_map = {}
        else:
            member_program_counts_dict = {}
            program_t0_counts = {}
            category_t0_map = {}

        if members.empty and controls.empty:
            return pd.DataFrame(columns=[
                "program_id", "category_id", "delta_missing_reason", "eligible_for_delta"
            ])

        key_union = (
            members[["program_id", "category_id"]]
            .drop_duplicates()
            .merge(
                controls[["program_id", "category_id"]].drop_duplicates(),
                on=["program_id", "category_id"],
                how="outer"
            )
        )

        rows: list[Dict[str, Any]] = []

        for _, key in key_union.iterrows():
            prog = key["program_id"]
            cat = key["category_id"]
            member_slice = members[(members["program_id"] == prog) & (members["category_id"] == cat)]
            control_slice = controls[(controls["program_id"] == prog) & (controls["category_id"] == cat)]

            member_measured_ids = _t0_ids(member_slice, require_member=True, positive_only=True)
            control_measured_ids = _t0_ids(control_slice, require_member=False, positive_only=True)

            member_slice_measured = member_slice[member_slice["facility_id"].astype(str).isin(member_measured_ids)]
            control_slice_measured = control_slice[control_slice["facility_id"].astype(str).isin(control_measured_ids)]

            member_weights = kpis._member_weights(member_slice_measured)
            control_weights = kpis._control_weights(control_slice_measured)

            raw_t0_key = category_t0_map.get((prog, cat))
            t0_key: Optional[str]
            if raw_t0_key is None:
                t0_key = None
            else:
                t0_key = str(raw_t0_key)

            program_month_count = None
            if t0_key is not None:
                program_month_count = program_t0_counts.get((prog, t0_key))

            if program_month_count is not None:
                member_total_count = int(program_month_count)
            elif member_program_counts_dict:
                member_total_count = int(member_program_counts_dict.get(prog, 0))
            else:
                member_total_count = int(len(_t0_ids(member_slice, require_member=True, positive_only=False)))

            control_total_ids = _t0_ids(control_slice, require_member=False, positive_only=False)
            control_total_count = int(len(control_total_ids))

            row: Dict[str, Any] = {
                "program_id": prog,
                "category_id": cat,
                "N_members": member_total_count,
                "N_controls": control_total_count,
                "N_members_measured": int(len(member_measured_ids)),
                "N_controls_measured": int(len(control_measured_ids)),
                "delta_missing_reason": "ok",
                "eligible_for_delta": True,
                "thin_pre": False,
                "kpi_spec": "T0_LOCKED_RIGHT_CENSORED_LASPEYRES",
                "t0_event_month": t0_key if t0_key is not None else pd.NA,
            }

            member_total = kpis._laspeyres_total(member_slice_measured, member_weights)
            control_total = kpis._laspeyres_total(control_slice_measured, control_weights)
            row.update({
                "member_t0_total_spend_6m": float(member_total) if member_total is not None else np.nan,
                "control_t0_total_spend_6m": float(control_total) if control_total is not None else np.nan,
            })

            if member_weights.empty:
                row.update({
                    "delta_missing_reason": "missing_member_t0_weights",
                    "eligible_for_delta": False,
                })
            if control_weights.empty:
                row.update({
                    "delta_missing_reason": "missing_control_t0_weights",
                    "eligible_for_delta": False,
                })

            masked_tracker: Dict[str, Dict[str, set[str]]] = {}

            member_series, member_dataset_cov, member_final_cov = kpis._weighted_series(
                member_slice_measured,
                member_weights,
                drop_post_inactive=True,
                exit_map=dataset_exit_map,
                masked_tracker=masked_tracker,
                label="members",
            )
            control_series, control_dataset_cov, control_final_cov = kpis._weighted_series(
                control_slice_measured,
                control_weights,
                drop_post_inactive=False,
                exit_map=dataset_exit_map,
                masked_tracker=masked_tracker,
                label="controls",
            )

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
                member_dataset_cov,
                control_dataset_cov,
                member_final_cov,
                control_final_cov,
                weight_coverage_guard,
            )

            row.update({
                "weight_coverage_clamped": bool(coverage_meta.get("weight_coverage_clamped", False)),
                "weight_coverage_clamp_month": coverage_meta.get("weight_coverage_clamp_month", pd.NA),
                "member_masked_dataset_exit_count": int(len(masked_tracker.get("members", {}).get("dataset_exit", set()))),
                "member_masked_program_exit_count": int(len(masked_tracker.get("members", {}).get("program_exit", set()))),
                "control_masked_dataset_exit_count": int(len(masked_tracker.get("controls", {}).get("dataset_exit", set()))),
                "control_masked_program_exit_count": int(len(masked_tracker.get("controls", {}).get("program_exit", set()))),
                "member_weight_coverage_min": coverage_meta.get("member_weight_coverage_min", np.nan),
                "control_weight_coverage_min": coverage_meta.get("control_weight_coverage_min", np.nan),
                "pre_contract_baseline_included": bool(coverage_meta.get("pre_contract_baseline_included", False)),
            })

            member_pre_mean, member_pre_months = kpis._window_stats(member_series, *PRE_WINDOW)
            control_pre_mean, control_pre_months = kpis._window_stats(control_series, *PRE_WINDOW)
            member_post06_mean, member_post06_months = kpis._window_stats(member_series, *POST_0_6)
            control_post06_mean, control_post06_months = kpis._window_stats(control_series, *POST_0_6)
            member_post712_mean, member_post712_months = kpis._window_stats(member_series, *POST_7_12)
            control_post712_mean, control_post712_months = kpis._window_stats(control_series, *POST_7_12)

            pre_common = kpis._common_months(member_series, control_series, *PRE_WINDOW)
            post06_common = kpis._common_months(member_series, control_series, *POST_0_6)
            post712_common = kpis._common_months(member_series, control_series, *POST_7_12)

            row.update({
                "member_pre_mean": member_pre_mean,
                "control_pre_mean": control_pre_mean,
                "member_post_0_6": member_post06_mean,
                "control_post_0_6": control_post06_mean,
                "member_post_7_12": member_post712_mean,
                "control_post_7_12": control_post712_mean,
                "member_pre_months": member_pre_months,
                "control_pre_months": control_pre_months,
                "member_post_0_6_months": member_post06_months,
                "control_post_0_6_months": control_post06_months,
                "member_post_7_12_months": member_post712_months,
                "control_post_7_12_months": control_post712_months,
                "pre_common_months": pre_common,
                "post06_common_months": post06_common,
                "post712_common_months": post712_common,
            })

            if not row["eligible_for_delta"]:
                row.update({
                    "delta_0_6": np.nan,
                    "delta_7_12": np.nan,
                    "delta_0_12": np.nan,
                    "delta_time_to_target_month": np.nan,
                    "delta_sustained_lift_pp": np.nan,
                    "meaningful_lift_7_12": False,
                })
                row["thin_pre"] = True
                rows.append(row)
                continue

            if member_pre_mean is None or control_pre_mean is None:
                row.update({
                    "delta_missing_reason": "insufficient_pre_months",
                    "eligible_for_delta": False,
                    "delta_0_6": np.nan,
                    "delta_7_12": np.nan,
                    "delta_0_12": np.nan,
                    "delta_time_to_target_month": np.nan,
                    "delta_sustained_lift_pp": np.nan,
                    "meaningful_lift_7_12": False,
                    "thin_pre": True,
                })
                rows.append(row)
                continue

            thin_pre = (member_pre_months < min_pre_months) or (control_pre_months < min_pre_months)
            if thin_pre:
                row["thin_pre"] = True
                row.update({
                    "delta_missing_reason": "insufficient_pre_months",
                    "eligible_for_delta": False,
                    "delta_0_6": np.nan,
                    "delta_7_12": np.nan,
                    "delta_0_12": np.nan,
                    "delta_time_to_target_month": np.nan,
                    "delta_sustained_lift_pp": np.nan,
                    "meaningful_lift_7_12": False,
                })
                rows.append(row)
                continue

            if pre_common < min_common_months:
                row.update({
                    "delta_missing_reason": "insufficient_pre_common_months",
                    "eligible_for_delta": False,
                    "delta_0_6": np.nan,
                    "delta_7_12": np.nan,
                    "delta_0_12": np.nan,
                    "delta_time_to_target_month": np.nan,
                    "delta_sustained_lift_pp": np.nan,
                    "meaningful_lift_7_12": False,
                })
                rows.append(row)
                continue

            delta_series = kpis._delta_series(member_series, control_series, member_pre_mean, control_pre_mean)

            delta_0_6 = kpis._window_mean(delta_series, *POST_0_6)
            delta_7_12 = kpis._window_mean(delta_series, *POST_7_12)
            delta_0_12 = kpis._window_mean(delta_series, 0, 12)
            delta_ttt = kpis._time_to_target(delta_series, target_pp)

            if delta_7_12 is None:
                if member_post712_months == 0:
                    row["delta_missing_reason"] = "missing_member_post712_mean"
                elif control_post712_months == 0:
                    row["delta_missing_reason"] = "missing_control_post712_mean"
                else:
                    row["delta_missing_reason"] = "delta_unavailable"
            else:
                row["delta_missing_reason"] = "ok"

            row.update({
                "delta_0_6": delta_0_6,
                "delta_7_12": delta_7_12,
                "delta_0_12": delta_0_12,
                "delta_time_to_target_month": delta_ttt,
                "delta_sustained_lift_pp": delta_7_12,
                "meaningful_lift_7_12": bool(delta_7_12 is not None and delta_7_12 >= target_pp),
                "eligible_for_delta": row.get("delta_missing_reason") == "ok",
            })

            rows.append(row)

        result = pd.DataFrame(rows)
        if not result.empty:
            for col in [
                "delta_0_6",
                "delta_7_12",
                "delta_0_12",
                "delta_time_to_target_month",
                "delta_sustained_lift_pp",
                "member_pre_mean",
                "control_pre_mean",
                "member_post_0_6",
                "control_post_0_6",
                "member_post_7_12",
                "control_post_7_12",
                "member_t0_total_spend_6m",
                "control_t0_total_spend_6m",
            ]:
                if col in result.columns:
                    result[col] = result[col].astype(float)
            for col in [
                "member_pre_months",
                "control_pre_months",
                "member_post_0_6_months",
                "control_post_0_6_months",
                "member_post_7_12_months",
                "control_post_7_12_months",
                "pre_common_months",
                "post06_common_months",
                "post712_common_months",
                "N_members",
                "N_controls",
                "N_members_measured",
                "N_controls_measured",
            ]:
                if col in result.columns:
                    result[col] = result[col].astype("Int64")

            for col in [
                "eligible_for_delta",
                "thin_pre",
                "meaningful_lift_7_12",
            ]:
                if col in result.columns:
                    result[col] = result[col].apply(lambda v: bool(v) if pd.notna(v) else False).astype(object)
            if "t0_event_month" in result.columns:
                result["t0_event_month"] = result["t0_event_month"].astype("string")
        return result


if __name__ == "__main__":
    # Tiny self-test
    import pandas as pd
    s = pd.Series({-2: 0.01, -1: 0.03, 0: 0.05, 1: 0.09, 2: 0.06})
    assert kpis.time_to_target(s, target_pp=8) == 1
