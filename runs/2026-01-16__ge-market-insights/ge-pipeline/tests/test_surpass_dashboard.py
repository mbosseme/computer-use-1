"""Tests for the Surpass dashboard reconciliation helpers."""

from __future__ import annotations

from pathlib import Path

import json
import math

import pandas as pd
import pytest
from typer.testing import CliRunner

from src.reconciliation.surpass_dashboard import (
    DashboardReconciliationResult,
    load_category_map,
    load_contract_number_mapping,
    normalize_category,
    prepare_dashboard_dataframe,
    reconcile_dashboard,
)
from src.runner.cli import app


def test_normalize_category_removes_suffix_and_whitespace() -> None:
    assert normalize_category("Procedure Gloves   - SP-123  ") == "PROCEDURE GLOVES"
    assert normalize_category("  mixed   Case  Text ") == "MIXED CASE TEXT"
    assert normalize_category(None) == ""


def test_load_category_map_normalizes_keys_and_values(tmp_path: Path) -> None:
    path = tmp_path / "category_map.yml"
    path.write_text(
        """
        Procedure Gloves: Surgical Gloves
        Face Masks: Masks
        """
    )

    mapping = load_category_map(path)

    assert mapping == {
        "PROCEDURE GLOVES": "SURGICAL GLOVES",
        "FACE MASKS": "MASKS",
    }


def test_load_contract_number_mapping_parses_tab_csv(tmp_path: Path) -> None:
    path = tmp_path / "contract_mapping.csv"
    path.write_text(
        "\n".join(
            [
                "Contract Number\tContract Category",
                "SP-OR-2035\tSurgeon Gloves",
                "SP-OR-2072\tSterilization Assurance",
            ]
        )
    )

    mapping = load_contract_number_mapping(path)

    assert mapping == {
        "SP-OR-2035": "SURGEON GLOVES",
        "SP-OR-2072": "STERILIZATION ASSURANCE",
    }


def test_prepare_dashboard_dataframe_uses_contract_mapping_when_available() -> None:
    dashboard_df = pd.DataFrame(
        [
            {
                "System Status": "PA-Completed",
                "Contract Category": "Alt Gloves Label - SP-OR-2035",
                "Entity Code": "A",
                "Category Spend": 120.0,
            },
            {
                "System Status": "PA-Completed",
                "Contract Category": "Another Label - SP-OR-2035",
                "Entity Code": "B",
                "Category Spend": 80.0,
            },
        ]
    )

    result = prepare_dashboard_dataframe(
        dashboard_df,
        contract_map={"SP-OR-2035": "SURGICAL GLOVES"},
    )

    assert set(result.frame["category_norm"]) == {"SURGICAL GLOVES"}
    assert result.mapping_counts["rows_mapped_by_contract_number"] == 2
    assert result.mapping_counts["rows_mapped_by_category_map"] == 0
    assert set(result.frame["category_mapping_source"].dropna()) == {"contract_number"}
    assert set(result.mapped_category_details["mapping_source"]) == {"contract_number"}


@pytest.fixture
def sample_shares_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "program_id": "Surpass",
                "category_id": "Procedure Gloves",
                "facility_id": "A",
                "event_month": 0,
                "member_at_t0": True,
                "t0_total_cat_spend_6m": 120.0,
            },
            {
                "program_id": "Surpass",
                "category_id": "Procedure Gloves",
                "facility_id": "D",
                "event_month": 0,
                "member_at_t0": True,
                "t0_total_cat_spend_6m": 80.0,
            },
            {
                "program_id": "Surpass",
                "category_id": "Face Masks",
                "facility_id": "C",
                "event_month": 0,
                "member_at_t0": True,
                "t0_total_cat_spend_6m": 300.0,
            },
            {
                "program_id": "Surpass",
                "category_id": "Face Masks",
                "facility_id": "X",
                "event_month": 0,
                "member_at_t0": False,
                "t0_total_cat_spend_6m": 500.0,
            },
            {
                "program_id": "Other",
                "category_id": "Procedure Gloves",
                "facility_id": "A",
                "event_month": 0,
                "member_at_t0": True,
                "t0_total_cat_spend_6m": 100.0,
            },
            {
                "program_id": "Surpass",
                "category_id": "Procedure Gloves",
                "facility_id": "B",
                "event_month": 0,
                "member_at_t0": True,
                "t0_total_cat_spend_6m": 0.0,
            },
            {
                "program_id": "Surpass",
                "category_id": "Procedure Gloves",
                "facility_id": "A",
                "event_month": 1,
                "member_at_t0": True,
                "t0_total_cat_spend_6m": 60.0,
            },
        ]
    )


@pytest.fixture
def sample_dashboard_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "System Status": "PA-Completed",
                "Contract Category": "Procedure Gloves - SP-123",
                "Entity Code": "A",
                "Category Spend": 110.0,
            },
            {
                "System Status": "PA-Completed",
                "Contract Category": "Procedure Gloves - SP-123",
                "Entity Code": "B",
                "Category Spend": 0.0,
            },
            {
                "System Status": "PA-Completed",
                "Contract Category": "Face Masks",
                "Entity Code": "C",
                "Category Spend": 250.0,
            },
            {
                "System Status": "PA-Completed",
                "Contract Category": "Face Masks",
                "Entity Code": "E",
                "Category Spend": 50.0,
            },
            {
                "System Status": "PA-Completed",
                "Contract Category": " Other ",
                "Entity Code": "Z",
                "Category Spend": 75.0,
            },
            {
                "System Status": "PA-Active",
                "Contract Category": "Procedure Gloves - SP-123",
                "Entity Code": "A",
                "Category Spend": 999.0,
            },
        ]
    )


def test_reconcile_dashboard_applies_mapping_and_overlap(
    sample_shares_df: pd.DataFrame,
    sample_dashboard_df: pd.DataFrame,
) -> None:
    category_map = {
        "PROCEDURE GLOVES": "SURGICAL GLOVES",
        "FACE MASKS": "MASKS",
    }

    result = reconcile_dashboard(
        sample_shares_df,
        sample_dashboard_df,
        category_map=category_map,
    )

    assert isinstance(result, DashboardReconciliationResult)

    members_df = result.members
    spend_df = result.spend
    members_intersection_df = result.members_intersection
    spend_intersection_df = result.spend_intersection

    expected_members = pd.DataFrame(
        [
            {
                "mapped_label": "MASKS",
                "raw_labels": "FACE MASKS",
                "members_prd_measured_in_category": 1,
                "prd_6m_spend": 300.0,
                "members_dashboard_all": 2,
                "members_dashboard_spendpos": 2,
                "members_dashboard_zero_spend": 0,
                "delta_members_all": 1,
                "delta_members_spendpos": 1,
                "members_intersection": 1,
                "members_prd_only": 0,
                "members_dashboard_spendpos_only": 1,
                "dashboard_6m_spend": 300.0,
                "facility_overlap_rate": 0.5,
            },
            {
                "mapped_label": "OTHER",
                "raw_labels": "OTHER",
                "members_prd_measured_in_category": 0,
                "prd_6m_spend": 0.0,
                "members_dashboard_all": 1,
                "members_dashboard_spendpos": 1,
                "members_dashboard_zero_spend": 0,
                "delta_members_all": 1,
                "delta_members_spendpos": 1,
                "members_intersection": 0,
                "members_prd_only": 0,
                "members_dashboard_spendpos_only": 1,
                "dashboard_6m_spend": 75.0,
                "facility_overlap_rate": 0.0,
            },
            {
                "mapped_label": "SURGICAL GLOVES",
                "raw_labels": "PROCEDURE GLOVES",
                "members_prd_measured_in_category": 2,
                "prd_6m_spend": 200.0,
                "members_dashboard_all": 2,
                "members_dashboard_spendpos": 1,
                "members_dashboard_zero_spend": 1,
                "delta_members_all": 0,
                "delta_members_spendpos": -1,
                "members_intersection": 1,
                "members_prd_only": 1,
                "members_dashboard_spendpos_only": 0,
                "dashboard_6m_spend": 110.0,
                "facility_overlap_rate": 0.5,
            },
        ]
    )

    for column in [
        "members_prd_measured_in_category",
        "members_dashboard_all",
        "members_dashboard_spendpos",
        "members_dashboard_zero_spend",
        "delta_members_all",
        "delta_members_spendpos",
        "members_intersection",
        "members_prd_only",
        "members_dashboard_spendpos_only",
    ]:
        expected_members[column] = expected_members[column].astype("Int64")

    expected_members_sorted = expected_members.sort_values("mapped_label").reset_index(drop=True)
    members_df = members_df.sort_values("mapped_label").reset_index(drop=True)

    pd.testing.assert_frame_equal(members_df, expected_members_sorted, check_names=True)

    expected_spend = pd.DataFrame(
        [
            {
                "mapped_label": "MASKS",
                "raw_labels": "FACE MASKS",
                "prd_6m_spend": 300.0,
                "dashboard_6m_spend": 300.0,
                "delta_spend": 0.0,
                "members_prd_measured_in_category": 1,
                "members_dashboard_spendpos": 2,
                "facility_overlap_rate": 0.5,
            },
            {
                "mapped_label": "OTHER",
                "raw_labels": "OTHER",
                "prd_6m_spend": 0.0,
                "dashboard_6m_spend": 75.0,
                "delta_spend": 75.0,
                "members_prd_measured_in_category": 0,
                "members_dashboard_spendpos": 1,
                "facility_overlap_rate": 0.0,
            },
            {
                "mapped_label": "SURGICAL GLOVES",
                "raw_labels": "PROCEDURE GLOVES",
                "prd_6m_spend": 200.0,
                "dashboard_6m_spend": 110.0,
                "delta_spend": -90.0,
                "members_prd_measured_in_category": 2,
                "members_dashboard_spendpos": 1,
                "facility_overlap_rate": 0.5,
            },
        ]
    )
    expected_spend[["members_prd_measured_in_category", "members_dashboard_spendpos"]] = (
        expected_spend[["members_prd_measured_in_category", "members_dashboard_spendpos"]].astype("Int64")
    )
    expected_spend_sorted = expected_spend.sort_values("mapped_label").reset_index(drop=True)
    spend_df = spend_df.sort_values("mapped_label").reset_index(drop=True)
    pd.testing.assert_frame_equal(spend_df, expected_spend_sorted, check_names=True)

    expected_members_intersection = pd.DataFrame(
        [
            {"mapped_label": "MASKS", "members_intersection": 1, "members_union": 2},
            {"mapped_label": "OTHER", "members_intersection": 0, "members_union": 1},
            {"mapped_label": "SURGICAL GLOVES", "members_intersection": 1, "members_union": 2},
        ]
    )
    expected_members_intersection[["members_intersection", "members_union"]] = (
        expected_members_intersection[["members_intersection", "members_union"]].astype("Int64")
    )
    expected_members_intersection = expected_members_intersection.sort_values("mapped_label").reset_index(drop=True)
    assert members_intersection_df is not None
    members_intersection_df = members_intersection_df.sort_values("mapped_label").reset_index(drop=True)
    pd.testing.assert_frame_equal(members_intersection_df, expected_members_intersection, check_names=True)

    expected_spend_intersection = pd.DataFrame(
        [
            {
                "mapped_label": "MASKS",
                "prd_6m_spend_intersection": 300.0,
                "dashboard_6m_spend_intersection": 250.0,
            },
            {
                "mapped_label": "OTHER",
                "prd_6m_spend_intersection": 0.0,
                "dashboard_6m_spend_intersection": 0.0,
            },
            {
                "mapped_label": "SURGICAL GLOVES",
                "prd_6m_spend_intersection": 120.0,
                "dashboard_6m_spend_intersection": 110.0,
            },
        ]
    )
    expected_spend_intersection = expected_spend_intersection.sort_values("mapped_label").reset_index(drop=True)
    assert spend_intersection_df is not None
    spend_intersection_df = spend_intersection_df.sort_values("mapped_label").reset_index(drop=True)
    pd.testing.assert_frame_equal(
        spend_intersection_df,
        expected_spend_intersection,
        check_names=True,
    )

    assert result.filter_counts == {
        "rows_total": 6,
        "rows_status_filtered": 5,
        "rows_positive_spend": 4,
        "distinct_facilities_status_filtered": 5,
        "distinct_facilities_positive_spend": 4,
    }

    assert result.dashboard_stats == {
        "members_rows": 3,
        "spend_rows": 3,
    }

    overlap_values = members_df["facility_overlap_rate"].tolist()
    assert all(math.isclose(value, expected, rel_tol=1e-9) for value, expected in zip(overlap_values, [0.5, 0.0, 0.5]))


def test_reconcile_dashboard_cli_writes_outputs(
    tmp_path: Path,
    sample_shares_df: pd.DataFrame,
    sample_dashboard_df: pd.DataFrame,
) -> None:
    shares_path = tmp_path / "shares.csv"
    dashboard_path = tmp_path / "dashboard.csv"
    category_map_path = tmp_path / "category_map.yaml"
    output_dir = tmp_path / "outputs"
    snapshots_root = tmp_path / "snapshots"
    config_path = tmp_path / "config.yaml"

    sample_shares_df.to_csv(shares_path, index=False)
    sample_dashboard_df.to_csv(dashboard_path, index=False)
    category_map_path.write_text(
        """
        Procedure Gloves: Surgical Gloves
        Face Masks: Masks
        """
    )
    config_path.write_text(
        f"io:\n  snapshots_dir: '{snapshots_root}'\n"
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "reconcile-dashboard",
            str(dashboard_path),
            "--shares-path",
            str(shares_path),
            "--category-map-path",
            str(category_map_path),
            "--output-dir",
            str(output_dir),
            "--config",
            str(config_path),
            "--member-delta-threshold",
            "1",
            "--overlap-threshold",
            "0.4",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Dashboard reconciliation written to" in result.stdout

    dirs = list(output_dir.iterdir())
    assert len(dirs) == 1
    run_dir = dirs[0]

    members = pd.read_csv(run_dir / "members.csv")
    spend = pd.read_csv(run_dir / "spend.csv")
    manifest = json.loads((run_dir / "manifest.json").read_text())
    summary = json.loads((run_dir / "summary.json").read_text())

    assert set(members["mapped_label"]) == {"MASKS", "OTHER", "SURGICAL GLOVES"}
    assert not spend.empty
    assert (run_dir / "members_intersection.csv").exists()
    assert (run_dir / "spend_intersection.csv").exists()
    assert (run_dir / "summary.md").exists()

    assert manifest["counts"]["members_rows"] == 3
    assert manifest["counts"]["spend_rows"] == 3
    assert summary["mapping_counts"]["rows_total"] == 5
    assert "contract_mapping" in manifest
    assert "contract_number_column" in manifest["options"]
    assert "contract_mapping" in summary["notes"]