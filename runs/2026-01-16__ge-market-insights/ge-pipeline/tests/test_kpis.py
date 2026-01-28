import pandas as pd
import pytest

from src.kpis import kpis


def _build_member_panel():
    rows = []

    def add_row(facility_id: str, event_month: int, spend: float, share: float, *, member_flag: bool, member_at_t0: bool) -> None:
        rows.append({
            "program_id": "P",
            "category_id": "C",
            "facility_id": facility_id,
            "event_month": event_month,
            "total_cat_spend": spend,
            "total_cat_spend_6m": spend * 6,
            "awarded_share_6m": share,
            "member_flag": member_flag,
            "member_at_t0": member_at_t0,
        })

    # Facility F1 (weight 0.25 at t0)
    for evt, share in [(-3, 0.10), (-2, 0.11), (-1, 0.09), (0, 0.18), (1, 0.19), (2, 0.2), (3, 0.21), (4, 0.22), (5, 0.23), (6, 0.24)]:
        add_row("F1", evt, 100.0, share, member_flag=(evt >= 0), member_at_t0=(evt == 0))
    # Post 7-12
    for evt, share in [(7, 0.32), (8, 0.31), (9, 0.33), (10, 0.34), (11, 0.32), (12, 0.35)]:
        add_row("F1", evt, 100.0, share, member_flag=True, member_at_t0=False)

    # Facility F2 (weight 0.75 at t0, exits after month 5)
    for evt, share in [(-3, 0.20), (-2, 0.19), (-1, 0.21), (0, 0.22), (1, 0.23), (2, 0.22), (3, 0.21), (4, 0.20), (5, 0.19)]:
        add_row("F2", evt, 300.0, share, member_flag=(evt >= 0), member_at_t0=(evt == 0))
    # provide rows after exit flagged member_flag False (should be censored)
    for evt, share in [(6, 0.18), (7, 0.17), (8, 0.18), (9, 0.19)]:
        add_row("F2", evt, 300.0, share, member_flag=False, member_at_t0=False)
    return pd.DataFrame(rows)


def _build_control_panel():
    rows = []

    def add_row(facility_id: str, event_month: int, spend: float, share: float) -> None:
        rows.append({
            "program_id": "P",
            "category_id": "C",
            "facility_id": facility_id,
            "event_month": event_month,
            "total_cat_spend": spend,
            "total_cat_spend_6m": spend * 6,
            "awarded_share_6m": share,
        })

    # Control facility C1 weight 0.6 (t0 spend 120)
    for evt, share in [(-3, 0.05), (-2, 0.06), (-1, 0.05), (0, 0.055), (1, 0.056), (2, 0.057), (3, 0.058), (4, 0.057), (5, 0.056), (6, 0.055)]:
        add_row("C1", evt, 120.0, share)
    for evt, share in [(7, 0.060), (8, 0.050), (9, 0.070), (10, 0.060), (11, 0.060), (12, 0.070)]:
        add_row("C1", evt, 120.0, share)

    # Control facility C2 weight 0.4 (t0 spend 80)
    for evt, share in [(-3, 0.04), (-2, 0.05), (-1, 0.04), (0, 0.045), (1, 0.046), (2, 0.047), (3, 0.046), (4, 0.045), (5, 0.044), (6, 0.043)]:
        add_row("C2", evt, 80.0, share)
    for evt, share in [(7, 0.050), (8, 0.040), (9, 0.050), (10, 0.050), (11, 0.040), (12, 0.050)]:
        add_row("C2", evt, 80.0, share)
    return pd.DataFrame(rows)


def test_build_delta_summary_laspeyres_weights():
    members = _build_member_panel()
    controls = _build_control_panel()

    result = kpis.build_delta_summary(members, controls, target_pp=0.02, min_pre_months=3, min_common_months=3)
    assert len(result) == 1
    row = result.iloc[0]

    # Weighting: pre means should match manual Laspeyres calculation
    assert row['member_pre_mean'] == pytest.approx(0.175, rel=1e-6)
    assert row['control_pre_mean'] == pytest.approx(0.049333333, rel=1e-6)

    # Dataset exit guard trims months once controls lose coverage (F2 exits the dataset after month 9)
    assert bool(row['weight_coverage_clamped']) is True
    assert int(row['weight_coverage_clamp_month']) == 10
    assert int(row['member_post_7_12_months']) == 3
    assert int(row['control_post_7_12_months']) == 3

    # Delta 7-12 vs controls (Laspeyres weighting on months 7-9 after clamp)
    assert row['member_post_7_12'] == pytest.approx(0.32, rel=1e-6)
    assert row['control_post_7_12'] == pytest.approx(0.05466666666666667, rel=1e-6)
    assert row['delta_7_12'] == pytest.approx(0.13966666666666666, rel=1e-6)
    assert row['meaningful_lift_7_12'] is True
    assert row['eligible_for_delta'] is True
    assert row['delta_missing_reason'] == 'ok'

    # Mask counts should be present even when dataset exit map is unavailable
    assert int(row['member_masked_dataset_exit_count']) == 0
    assert int(row['control_masked_dataset_exit_count']) == 0

    # Cohort sizes reflect t0 membership
    assert int(row['N_members']) == 2
    assert int(row['N_controls']) == 2
    assert int(row['N_members_measured']) == 2
    assert int(row['N_controls_measured']) == 2

    # Laspeyres t0 totals reflect weighted cohort spend at t0
    assert row['member_t0_total_spend_6m'] == pytest.approx(2400.0)
    assert row['control_t0_total_spend_6m'] == pytest.approx(1200.0)


def test_build_delta_summary_insufficient_pre_months():
    members = _build_member_panel()
    controls = _build_control_panel()

    # Drop control pre months to force insufficiency
    controls_thin = controls[controls['event_month'] >= -1].copy()

    result = kpis.build_delta_summary(members, controls_thin, target_pp=0.02, min_pre_months=3, min_common_months=3)
    row = result.iloc[0]

    assert row['eligible_for_delta'] is False
    assert row['delta_missing_reason'] == 'insufficient_pre_months'
    assert pd.isna(row['delta_7_12'])
    assert int(row['N_members_measured']) == 2
    assert int(row['N_controls_measured']) == 2
