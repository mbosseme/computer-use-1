"""
PRD-aligned QA invariants and light diagnostics.
- No silent data changes here; enforce assertions and allow caller to coerce/clip earlier.
- Event window clamp [-12,18] must already be applied by SQL or materialize step.
"""
from __future__ import annotations
import pandas as pd

class qa:
    @staticmethod
    def invariants(coverage_df: pd.DataFrame, membership_df: pd.DataFrame, shares_df: pd.DataFrame, controls_df: pd.DataFrame) -> None:
        # coverage is_covered is boolean-like
        cov_vals = coverage_df["is_covered"].dropna()
        assert cov_vals.isin([0,1,True,False]).all(), "coverage.is_covered must be boolean-like"

        # membership member_flag must be normalized to 0/1 already
        assert "member_flag" in membership_df.columns, "membership.member_flag missing"
        mem = membership_df["member_flag"].dropna()
        assert mem.isin([0,1,True,False]).all(), "membership.member_flag must be boolean-like"

        # event_month bounds on both panels
        for name, d in {"shares": shares_df, "controls": controls_df}.items():
            assert "event_month" in d.columns, f"{name}.event_month missing"
            assert d["event_month"].between(-12, 18).all(), f"{name}.event_month outside [-12,18]"

        # awarded_share_6m exists and within [0,1] (caller should have coerced/clipped and disclosed)
        tol = 1e-9
        for name, d in {"shares": shares_df, "controls": controls_df}.items():
            assert "awarded_share_6m" in d.columns, f"{name}.awarded_share_6m missing"
            vals = d["awarded_share_6m"].dropna()
            ok = ((vals >= -tol) & (vals <= 1 + tol)).all()
            assert ok, f"{name}.awarded_share_6m must be within [0,1] (±{tol}) when present"

    @staticmethod
    def rowcount_waterfall(named: dict) -> None:
        print("\nRow-count waterfall")
        for k, v in named.items():
            try:
                print(f"  {k:<28} {len(v):>10,}")
            except Exception:
                print(f"  {k:<28} n/a")

    @staticmethod
    def window_coverage(df: pd.DataFrame, by=("program_id","category_id"), col="event_month") -> pd.DataFrame:
        bins=[-999,-1,6,12,18,999]; labels=["pre","0-6","7-12","13-18","19+"]
        t=df.copy(); t["window"]=pd.cut(t[col], bins=bins, labels=labels)
        return (t.groupby([*by,"window"], observed=True).size().rename("n_rows").reset_index())

    @staticmethod
    def anchor_counts(shares: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
        """
        Count distinct go-live anchors detected per (program, category) using event_month==0 rows.
        Returns a dataframe with columns: program_id, category_id, anchors_in_members, anchors_in_controls.
        """
        def count_anchors(df: pd.DataFrame, label: str) -> pd.DataFrame:
            t = df.loc[df["event_month"] == 0, ["program_id", "category_id"]].drop_duplicates()
            return t.groupby(["program_id", "category_id"], observed=True).size().rename(label).reset_index()

        am = count_anchors(shares, "anchors_in_members")
        ac = count_anchors(controls, "anchors_in_controls")
        return am.merge(ac, on=["program_id", "category_id"], how="outer").fillna(0).astype({"anchors_in_members":"int64","anchors_in_controls":"int64"})

    @staticmethod
    def assert_single_anchor(shares: pd.DataFrame, controls: pd.DataFrame) -> None:
        """Assert at most one anchor per (program, category) in both panels."""
        counts = qa.anchor_counts(shares, controls)
        bad = counts[(counts["anchors_in_members"] > 1) | (counts["anchors_in_controls"] > 1)]
        assert bad.empty, f"Multiple anchors detected for: {bad.to_dict(orient='records')}"
