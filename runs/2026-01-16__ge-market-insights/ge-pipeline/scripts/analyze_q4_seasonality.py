#!/usr/bin/env python3
"""analyze_q4_seasonality.py

Purpose
-------
Diagnose why Calendar Q4 (Oct–Dec) can appear lower in provider-reported
transactional market insights, even when manufacturers expect Q4 to be
strongest ("group-buy" seasonality).

This script explicitly reconciles two sources:
1) Manufacturer-reported supplier spend (invoice/revenue-aligned timing proxy)
2) Provider-reported transactions (ERP operational timing via Transaction_Date)

Outputs
-------
Writes stakeholder-ready CSVs + charts into snapshots/<RUN_ID>/:
- q4_supplier_quarterly.csv
- q4_provider_quarterly.csv
- q4_quarterly_overlay_indexed.csv
- q4_provider_monthly_transition.csv
- q4_provider_system_variability.csv
Charts go to snapshots/<RUN_ID>/visuals/:
- q4_supplier_quarterly_trend.png
- q4_provider_quarterly_trend.png
- q4_quarterly_overlay_indexed.png
- q4_provider_monthly_transition.png

Notes / Constraints
-------------------
- Calendar Q4 refers to Oct–Dec.
- Provider timing MUST use Transaction_Date.
- Do NOT claim clean PO vs invoice separation.
- Avoid exporting Facility_Name / Health_System_Name / Facility_Hin.
- Be explicit: provider transactions are not revenue timing.

"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Optional

import pandas as pd

# Plotting deps are already used elsewhere in the repo.
import matplotlib.pyplot as plt
import seaborn as sns

try:  # Prefer the repo's ADC-first wrapper when available.
    from src.bigquery_client import BigQueryClient
except Exception:  # pragma: no cover
    BigQueryClient = None  # type: ignore

try:
    from google.cloud import bigquery
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "google-cloud-bigquery is required. Activate .venv and run: pip install -r requirements.txt\n"
        f"Import error: {e}"
    )


SUPPLIER_TABLE = "`abi-inbound-prod.abi_inbound_bq_stg_purchasing_supplier_sales.supplier_spend`"
PROVIDER_TABLE = "`abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`"

DEFAULT_START = "2023-10-01"
DEFAULT_END = "2025-09-30"

# PRD-tier capital heuristic (signal, not a deterministic classifier).
CAPITAL_PRICE_THRESHOLD = 25_000

MODALITY_KEYWORDS = {
    "MRI": ["MRI", "MAGNETIC", "RESONANCE"],
    "CT": ["CT", "TOMOGRAPHY"],
    "Monitoring": ["MONITOR", "MONITORING", "PHYSIOLOGICAL"],
}

EXCLUDE_DESC_TOKENS = [
    "SERVICE",
    "MAINTENANCE",
    "WARRANTY",
    "AGREEMENT",
    "REPAIR",
    "SOFTWARE",
    "LICENSE",
    "RENEWAL",
]


def _now_run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _ensure_snapshot_dir(run_id: str) -> Path:
    out = Path("snapshots") / run_id
    (out / "visuals").mkdir(parents=True, exist_ok=True)
    return out


def _get_bq_client():
    if BigQueryClient is not None:
        wrapper = BigQueryClient()
        if wrapper.client is not None:
            return wrapper.client
    # Fallback: let ADC infer project from environment.
    return bigquery.Client()


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, bbox_inches="tight", dpi=200)
    plt.close()


def _quarter_label(ts: pd.Timestamp) -> str:
  ts = pd.to_datetime(ts)
  return f"{ts.year}-Q{ts.quarter}"


def _fmt_millions(x: float) -> str:
  return f"${x/1_000_000:,.1f}M"


def _safe_pct(x: float) -> str:
  return f"{x*100:,.1f}%"


def _write_timing_summary_md(
  *,
  snapshot_dir: Path,
  supplier_df: pd.DataFrame,
  provider_df: pd.DataFrame,
  monthly_df: pd.DataFrame,
  sys_df: pd.DataFrame,
  start_date: str,
  end_date: str,
) -> None:
  # Focus narrative on GE bucket; we’re explaining *timing*, not absolute coverage differences.
  supplier_ge = (
    supplier_df[supplier_df["bucket"] == "GE"]
    .groupby(["quarter_start"], as_index=False)
    .agg(spend=("spend", "sum"))
    .reset_index(drop=True)
  )
  provider_ge = (
    provider_df[provider_df["bucket"] == "GE"]
    .groupby(["quarter_start"], as_index=False)
    .agg(spend=("spend", "sum"))
    .reset_index(drop=True)
  )
  supplier_ge = pd.DataFrame(supplier_ge)
  provider_ge = pd.DataFrame(provider_ge)

  supplier_ge["quarter_start"] = pd.to_datetime(supplier_ge["quarter_start"])
  provider_ge["quarter_start"] = pd.to_datetime(provider_ge["quarter_start"])
  supplier_ge["calendar_quarter"] = supplier_ge["quarter_start"].map(_quarter_label)
  provider_ge["calendar_quarter"] = provider_ge["quarter_start"].map(_quarter_label)

  def _spend_for(df: pd.DataFrame, q: str) -> Optional[float]:
    row = df[df["calendar_quarter"] == q]
    if row.empty:
      return None
    return float(row["spend"].iloc[0])

  sup_q4_2024 = _spend_for(supplier_ge, "2024-Q4")
  sup_q3_2024 = _spend_for(supplier_ge, "2024-Q3")
  prov_q4_2024 = _spend_for(provider_ge, "2024-Q4")
  prov_q1_2025 = _spend_for(provider_ge, "2025-Q1")

  # Annual Q4 share (only meaningful for full-ish years in-window).
  def _q4_share(df: pd.DataFrame, year: int) -> Optional[float]:
    years = pd.DatetimeIndex(df["quarter_start"]).year
    quarters = pd.DatetimeIndex(df["quarter_start"]).quarter
    d = df[years == year]
    if d.empty:
      return None
    tot = float(d["spend"].sum())
    q4 = float(d[quarters[years == year] == 4]["spend"].sum())
    if tot <= 0:
      return None
    return q4 / tot

  sup_q4_share_2024 = _q4_share(supplier_ge, 2024)
  prov_q4_share_2024 = _q4_share(provider_ge, 2024)

  # Monthly transition diagnostic: Oct–Feb (GE) — compute Dec→Jan ratio for the 2024/2025 season.
  monthly_ge = monthly_df[monthly_df["manufacturer_bucket"] == "GE"].copy()
  monthly_ge["month_start"] = pd.to_datetime(monthly_ge["month_start"])
  monthly_tot = monthly_ge.groupby("month_start", as_index=False)["spend"].sum()
  dec_2024 = float(monthly_tot[monthly_tot["month_start"] == pd.Timestamp("2024-12-01")]["spend"].sum())
  jan_2025 = float(monthly_tot[monthly_tot["month_start"] == pd.Timestamp("2025-01-01")]["spend"].sum())
  dec_to_jan_ratio = (jan_2025 / dec_2024) if dec_2024 else None

  # System variability summary for Dec 2024 vs Jan 2025.
  sys_ratio = sys_df.copy()
  ratio_col = "jan_to_dec_ratio_2024"
  if ratio_col in sys_ratio.columns:
    col = pd.Series(sys_ratio[ratio_col])
    valid_ratio = pd.Series(pd.to_numeric(col, errors="coerce")).dropna()
  else:
    valid_ratio = pd.Series([], dtype=float)
  sys_median = float(valid_ratio.median()) if not valid_ratio.empty else None
  sys_pct_gt_1 = float((valid_ratio > 1).mean()) if not valid_ratio.empty else None
  sys_pct_gt_15 = float((valid_ratio > 1.5).mean()) if not valid_ratio.empty else None

  def _line(label: str, value: Optional[str]) -> str:
    return f"- {label}: {value if value is not None else 'n/a'}"

  lines: list[str] = []
  lines.append("# Q4 timing reconciliation (Supplier vs Provider)\n")
  lines.append(f"Window: {start_date} through {end_date} (calendar quarters; Q4 = Oct–Dec).\n")
  lines.append(
    "This summarizes why Calendar Q4 can look low in provider-reported transactional insights even when supplier-reported spend shows a strong Q4. "
    "Provider timing here is based strictly on `Transaction_Date` (ERP operational timing), not revenue/invoice timing.\n"
  )

  lines.append("## What the data shows (GE bucket)\n")
  if sup_q4_2024 is not None and sup_q3_2024 is not None and sup_q3_2024:
    lines.append(
      _line(
        "Supplier: 2024-Q4 vs 2024-Q3",
        f"{_fmt_millions(sup_q4_2024)} vs {_fmt_millions(sup_q3_2024)} ({_safe_pct(sup_q4_2024/sup_q3_2024 - 1)} uplift)",
      )
    )
  else:
    lines.append(_line("Supplier: 2024-Q4 vs 2024-Q3", None))

  if prov_q4_2024 is not None and prov_q1_2025 is not None and prov_q4_2024:
    lines.append(
      _line(
        "Provider: 2025-Q1 vs 2024-Q4",
        f"{_fmt_millions(prov_q1_2025)} vs {_fmt_millions(prov_q4_2024)} ({_safe_pct(prov_q1_2025/prov_q4_2024 - 1)} rebound)",
      )
    )
  else:
    lines.append(_line("Provider: 2025-Q1 vs 2024-Q4", None))

  if sup_q4_2024 is not None and prov_q4_2024 is not None and sup_q4_2024:
    lines.append(
      _line(
        "Provider vs Supplier in 2024-Q4",
        f"provider is {_safe_pct(prov_q4_2024/sup_q4_2024)} of supplier (same quarter, GE bucket)",
      )
    )
  else:
    lines.append(_line("Provider vs Supplier in 2024-Q4", None))

  if sup_q4_share_2024 is not None:
    lines.append(_line("Supplier: 2024 Q4 share of 2024 total", _safe_pct(sup_q4_share_2024)))
  else:
    lines.append(_line("Supplier: 2024 Q4 share of 2024 total", None))

  if prov_q4_share_2024 is not None:
    lines.append(_line("Provider: 2024 Q4 share of 2024 total", _safe_pct(prov_q4_share_2024)))
  else:
    lines.append(_line("Provider: 2024 Q4 share of 2024 total", None))

  if dec_to_jan_ratio is not None:
    lines.append(_line("Provider monthly diagnostic (GE): Jan 2025 / Dec 2024", f"{dec_to_jan_ratio:,.2f}x"))
  else:
    lines.append(_line("Provider monthly diagnostic (GE): Jan 2025 / Dec 2024", None))

  if sys_median is not None:
    lines.append(_line("System variability (top 75 systems): median Jan/Dec (2024 season)", f"{sys_median:,.2f}x"))
  else:
    lines.append(_line("System variability (top 75 systems): median Jan/Dec (2024 season)", None))

  if sys_pct_gt_1 is not None and sys_pct_gt_15 is not None:
    lines.append(
      _line(
        "System variability: % systems with Jan > Dec (2024 season)",
        f"{_safe_pct(sys_pct_gt_1)} (and {_safe_pct(sys_pct_gt_15)} with Jan > 1.5× Dec)",
      )
    )
  else:
    lines.append(_line("System variability: % systems with Jan > Dec (2024 season)", None))

  lines.append("\n## Interpretation (timing mechanics)\n")
  lines.append(
    "Taken together, the pattern is consistent with a timing shift in provider ERP transaction capture around year-end: "
    "Q4 looks suppressed in provider `Transaction_Date` while Q1 rebounds, even when the supplier spend proxy shows Q4 strength. "
    "This should be communicated as a *timing reconciliation* issue, not automatically a demand decline.\n"
  )
  lines.append(
    "## Constraints / what we are NOT claiming\n"
    "- No attempt is made to separate PO date vs invoice date vs install date.\n"
    "- Provider timing is based strictly on `Transaction_Date` (operational timing), not revenue timing.\n"
    "- System-level results are summarized by `Health_System_Entity_Code` only (no names exported).\n"
  )

  out_path = snapshot_dir / "q4_timing_summary.md"
  out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _supplier_quarterly_sql(start_date: str, end_date: str) -> str:
    return f"""
    DECLARE start_date DATE DEFAULT DATE('{start_date}');
    DECLARE end_date DATE DEFAULT DATE('{end_date}');

    WITH base AS (
      SELECT
        -- supplier_spend encodes month as YYYYQMM (e.g., 2024410 = 2024 Q4 Oct).
        DATE(
          CAST(SUBSTR(CAST(Spend_Period_YYYYQMM AS STRING), 1, 4) AS INT64),
          CAST(RIGHT(CAST(Spend_Period_YYYYQMM AS STRING), 2) AS INT64),
          1
        ) AS month_date,
        UPPER(IFNULL(Contract_Category, '')) AS contract_category_up,
        IFNULL(Contracted_Supplier_Parent_Name, IFNULL(Contracted_Supplier, '')) AS supplier_parent_name,
        Premier_Spend
      FROM {SUPPLIER_TABLE}
      WHERE Spend_Period_YYYYQMM IS NOT NULL
    ),
    scoped AS (
      SELECT
        month_date,
        CASE
          WHEN contract_category_up LIKE '%MAGNETIC RESONANCE%' THEN 'MRI'
          WHEN contract_category_up LIKE '%COMPUTED TOMOGRAPHY%' THEN 'CT'
          WHEN contract_category_up LIKE '%PHYSIOLOGICAL MONITORING%' THEN 'Monitoring'
          ELSE NULL
        END AS report_category,
        CASE
          WHEN REGEXP_CONTAINS(UPPER(supplier_parent_name), r'(\\bGE\\b|GENERAL ELECTRIC|GE HEALTHCARE)') THEN 'GE'
          ELSE 'OTHER'
        END AS supplier_bucket,
        CAST(Premier_Spend AS FLOAT64) AS spend
      FROM base
      WHERE month_date BETWEEN DATE_TRUNC(start_date, MONTH) AND DATE_TRUNC(end_date, MONTH)
    )
    SELECT
      DATE_TRUNC(month_date, QUARTER) AS quarter_start,
      CONCAT(CAST(EXTRACT(YEAR FROM month_date) AS STRING), '-Q', CAST(EXTRACT(QUARTER FROM month_date) AS STRING)) AS calendar_quarter,
      report_category,
      supplier_bucket,
      SUM(spend) AS spend
    FROM scoped
    WHERE report_category IS NOT NULL
    GROUP BY 1,2,3,4
    ORDER BY quarter_start, report_category, supplier_bucket;
    """.strip()


def _provider_quarterly_sql(start_date: str, end_date: str) -> str:
    # Capital-candidate heuristic must use Transaction_Date for timing.
    # We keep this conservative: require either high unit price OR modality keyword in UNKNOWN bucket.
    return f"""
    DECLARE start_ts TIMESTAMP DEFAULT TIMESTAMP('{start_date}');
    DECLARE end_ts_exclusive TIMESTAMP DEFAULT TIMESTAMP(DATE_ADD(DATE('{end_date}'), INTERVAL 1 DAY));

    WITH base AS (
      SELECT
        DATE(Transaction_Date) AS txn_date,
        UPPER(IFNULL(Contract_Category, '')) AS contract_category_up,
        UPPER(IFNULL(Product_Description, '')) AS product_desc_up,
        UPPER(IFNULL(Manufacturer_Name, '')) AS manufacturer_up,
        UPPER(IFNULL(Vendor_Name, '')) AS vendor_up,
        Base_Each_Price,
        Base_Spend,
        Health_System_Entity_Code
      FROM {PROVIDER_TABLE}
      WHERE Transaction_Date >= start_ts AND Transaction_Date < end_ts_exclusive
    ),
    filtered AS (
      SELECT
        txn_date,
        Health_System_Entity_Code,
        Base_Each_Price,
        Base_Spend,
        CASE
          WHEN contract_category_up LIKE '%MAGNETIC RESONANCE%' THEN 'MRI'
          WHEN contract_category_up LIKE '%COMPUTED TOMOGRAPHY%' THEN 'CT'
          WHEN contract_category_up LIKE '%PHYSIOLOGICAL MONITORING%' THEN 'Monitoring'
          WHEN (contract_category_up = 'UNKNOWN' OR contract_category_up = '' OR contract_category_up IS NULL)
            AND (
              REGEXP_CONTAINS(product_desc_up, r'\\bMRI\\b|RESONANCE|MAGNETIC')
              OR REGEXP_CONTAINS(product_desc_up, r'\\bCT\\b|TOMOGRAPH')
              OR REGEXP_CONTAINS(product_desc_up, r'MONITOR')
            )
            AND SAFE_CAST(Base_Each_Price AS FLOAT64) > {CAPITAL_PRICE_THRESHOLD}
            THEN
              CASE
                WHEN REGEXP_CONTAINS(product_desc_up, r'\\bMRI\\b|RESONANCE|MAGNETIC') THEN 'MRI'
                WHEN REGEXP_CONTAINS(product_desc_up, r'\\bCT\\b|TOMOGRAPH') THEN 'CT'
                WHEN REGEXP_CONTAINS(product_desc_up, r'MONITOR') THEN 'Monitoring'
                ELSE NULL
              END
          ELSE NULL
        END AS report_category,
        -- Conservative GE bucket: Manufacturer OR Vendor indicates GE.
        CASE
          WHEN REGEXP_CONTAINS(manufacturer_up, r'(\\bGE\\b|GENERAL ELECTRIC|GE HEALTHCARE)') THEN 'GE'
          WHEN REGEXP_CONTAINS(vendor_up, r'(\\bGE\\b|GENERAL ELECTRIC|GE HEALTHCARE)') THEN 'GE'
          ELSE 'OTHER'
        END AS manufacturer_bucket,
        -- Exclusion tokens: remove obvious services/software where described.
        NOT REGEXP_CONTAINS(product_desc_up, r'(SERVICE|MAINTENANCE|WARRANTY|AGREEMENT|REPAIR|SOFTWARE|LICENSE|RENEWAL)') AS passes_exclusion
      FROM base
    ),
    scoped AS (
      SELECT
        txn_date,
        report_category,
        manufacturer_bucket,
        Health_System_Entity_Code,
        CAST(Base_Spend AS FLOAT64) AS spend,
        SAFE_CAST(Base_Each_Price AS FLOAT64) AS each_price
      FROM filtered
      WHERE report_category IS NOT NULL
        AND passes_exclusion
    )
    SELECT
      DATE_TRUNC(txn_date, QUARTER) AS quarter_start,
      CONCAT(CAST(EXTRACT(YEAR FROM txn_date) AS STRING), '-Q', CAST(EXTRACT(QUARTER FROM txn_date) AS STRING)) AS calendar_quarter,
      report_category,
      manufacturer_bucket,
      SUM(spend) AS spend
    FROM scoped
    GROUP BY 1,2,3,4
    ORDER BY quarter_start, report_category, manufacturer_bucket;
    """.strip()


def _provider_monthly_transition_sql() -> str:
    # Focused on the strongest diagnostic window: Oct–Feb across two seasons.
    # Use Transaction_Date for timing; aggregate by month.
    return f"""
    WITH base AS (
      SELECT
        DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_start,
        UPPER(IFNULL(Contract_Category, '')) AS contract_category_up,
        UPPER(IFNULL(Product_Description, '')) AS product_desc_up,
        UPPER(IFNULL(Manufacturer_Name, '')) AS manufacturer_up,
        UPPER(IFNULL(Vendor_Name, '')) AS vendor_up,
        Base_Each_Price,
        Base_Spend
      FROM {PROVIDER_TABLE}
      WHERE Transaction_Date >= TIMESTAMP('2023-10-01')
        AND Transaction_Date < TIMESTAMP('2025-03-01')
    ),
    labeled AS (
      SELECT
        month_start,
        CASE
          WHEN contract_category_up LIKE '%MAGNETIC RESONANCE%' THEN 'MRI'
          WHEN contract_category_up LIKE '%COMPUTED TOMOGRAPHY%' THEN 'CT'
          WHEN contract_category_up LIKE '%PHYSIOLOGICAL MONITORING%' THEN 'Monitoring'
          WHEN (contract_category_up = 'UNKNOWN' OR contract_category_up = '' OR contract_category_up IS NULL)
            AND (
              REGEXP_CONTAINS(product_desc_up, r'\\bMRI\\b|RESONANCE|MAGNETIC')
              OR REGEXP_CONTAINS(product_desc_up, r'\\bCT\\b|TOMOGRAPH')
              OR REGEXP_CONTAINS(product_desc_up, r'MONITOR')
            )
            AND SAFE_CAST(Base_Each_Price AS FLOAT64) > {CAPITAL_PRICE_THRESHOLD}
            THEN
              CASE
                WHEN REGEXP_CONTAINS(product_desc_up, r'\\bMRI\\b|RESONANCE|MAGNETIC') THEN 'MRI'
                WHEN REGEXP_CONTAINS(product_desc_up, r'\\bCT\\b|TOMOGRAPH') THEN 'CT'
                WHEN REGEXP_CONTAINS(product_desc_up, r'MONITOR') THEN 'Monitoring'
                ELSE NULL
              END
          ELSE NULL
        END AS report_category,
        CASE
          WHEN REGEXP_CONTAINS(manufacturer_up, r'(\\bGE\\b|GENERAL ELECTRIC|GE HEALTHCARE)') THEN 'GE'
          WHEN REGEXP_CONTAINS(vendor_up, r'(\\bGE\\b|GENERAL ELECTRIC|GE HEALTHCARE)') THEN 'GE'
          ELSE 'OTHER'
        END AS manufacturer_bucket,
        CAST(Base_Spend AS FLOAT64) AS spend,
        NOT REGEXP_CONTAINS(product_desc_up, r'(SERVICE|MAINTENANCE|WARRANTY|AGREEMENT|REPAIR|SOFTWARE|LICENSE|RENEWAL)') AS passes_exclusion
      FROM base
    )
    SELECT
      month_start,
      FORMAT_DATE('%Y-%m', month_start) AS year_month,
      report_category,
      manufacturer_bucket,
      SUM(spend) AS spend
    FROM labeled
    WHERE report_category IS NOT NULL AND passes_exclusion
    GROUP BY 1,2,3,4
    ORDER BY month_start, report_category, manufacturer_bucket;
    """.strip()


def _provider_system_variability_sql() -> str:
    # System-level variability of timing, without claiming PO vs invoice.
    # We'll focus on GE bucket + capital modalities, and compute Dec vs Jan shift.
    return f"""
    WITH base AS (
      SELECT
        DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_start,
        EXTRACT(YEAR FROM DATE(Transaction_Date)) AS cal_year,
        EXTRACT(MONTH FROM DATE(Transaction_Date)) AS cal_month,
        Health_System_Entity_Code,
        UPPER(IFNULL(Contract_Category, '')) AS contract_category_up,
        UPPER(IFNULL(Product_Description, '')) AS product_desc_up,
        UPPER(IFNULL(Manufacturer_Name, '')) AS manufacturer_up,
        UPPER(IFNULL(Vendor_Name, '')) AS vendor_up,
        Base_Each_Price,
        CAST(Base_Spend AS FLOAT64) AS spend
      FROM {PROVIDER_TABLE}
      WHERE Transaction_Date >= TIMESTAMP('2023-10-01')
        AND Transaction_Date < TIMESTAMP('2025-03-01')
        AND Health_System_Entity_Code IS NOT NULL
    ),
    labeled AS (
      SELECT
        month_start,
        Health_System_Entity_Code,
        CASE
          WHEN contract_category_up LIKE '%MAGNETIC RESONANCE%' THEN 'MRI'
          WHEN contract_category_up LIKE '%COMPUTED TOMOGRAPHY%' THEN 'CT'
          WHEN contract_category_up LIKE '%PHYSIOLOGICAL MONITORING%' THEN 'Monitoring'
          WHEN (contract_category_up = 'UNKNOWN' OR contract_category_up = '' OR contract_category_up IS NULL)
            AND (
              REGEXP_CONTAINS(product_desc_up, r'\\bMRI\\b|RESONANCE|MAGNETIC')
              OR REGEXP_CONTAINS(product_desc_up, r'\\bCT\\b|TOMOGRAPH')
              OR REGEXP_CONTAINS(product_desc_up, r'MONITOR')
            )
            AND SAFE_CAST(Base_Each_Price AS FLOAT64) > {CAPITAL_PRICE_THRESHOLD}
            THEN
              CASE
                WHEN REGEXP_CONTAINS(product_desc_up, r'\\bMRI\\b|RESONANCE|MAGNETIC') THEN 'MRI'
                WHEN REGEXP_CONTAINS(product_desc_up, r'\\bCT\\b|TOMOGRAPH') THEN 'CT'
                WHEN REGEXP_CONTAINS(product_desc_up, r'MONITOR') THEN 'Monitoring'
                ELSE NULL
              END
          ELSE NULL
        END AS report_category,
        CASE
          WHEN REGEXP_CONTAINS(manufacturer_up, r'(\\bGE\\b|GENERAL ELECTRIC|GE HEALTHCARE)') THEN 'GE'
          WHEN REGEXP_CONTAINS(vendor_up, r'(\\bGE\\b|GENERAL ELECTRIC|GE HEALTHCARE)') THEN 'GE'
          ELSE 'OTHER'
        END AS manufacturer_bucket,
        spend,
        NOT REGEXP_CONTAINS(product_desc_up, r'(SERVICE|MAINTENANCE|WARRANTY|AGREEMENT|REPAIR|SOFTWARE|LICENSE|RENEWAL)') AS passes_exclusion
      FROM base
    ),
    scoped AS (
      SELECT
        month_start,
        EXTRACT(YEAR FROM month_start) AS month_year,
        EXTRACT(MONTH FROM month_start) AS month_num,
        Health_System_Entity_Code,
        spend
      FROM labeled
      WHERE report_category IS NOT NULL
        AND passes_exclusion
        AND manufacturer_bucket = 'GE'
        AND month_start IN (
          DATE('2023-10-01'), DATE('2023-11-01'), DATE('2023-12-01'), DATE('2024-01-01'),
          DATE('2024-10-01'), DATE('2024-11-01'), DATE('2024-12-01'), DATE('2025-01-01')
        )
    ),
    monthly AS (
      SELECT
        Health_System_Entity_Code,
        month_start,
        SUM(spend) AS spend
      FROM scoped
      GROUP BY 1,2
    ),
    pivoted AS (
      SELECT
        Health_System_Entity_Code,
        SUM(CASE WHEN month_start = DATE('2023-10-01') THEN spend ELSE 0 END) AS oct_2023,
        SUM(CASE WHEN month_start = DATE('2023-11-01') THEN spend ELSE 0 END) AS nov_2023,
        SUM(CASE WHEN month_start = DATE('2023-12-01') THEN spend ELSE 0 END) AS dec_2023,
        SUM(CASE WHEN month_start = DATE('2024-01-01') THEN spend ELSE 0 END) AS jan_2024,
        SUM(CASE WHEN month_start = DATE('2024-10-01') THEN spend ELSE 0 END) AS oct_2024,
        SUM(CASE WHEN month_start = DATE('2024-11-01') THEN spend ELSE 0 END) AS nov_2024,
        SUM(CASE WHEN month_start = DATE('2024-12-01') THEN spend ELSE 0 END) AS dec_2024,
        SUM(CASE WHEN month_start = DATE('2025-01-01') THEN spend ELSE 0 END) AS jan_2025
      FROM monthly
      GROUP BY 1
    )
    SELECT
      Health_System_Entity_Code,
      (oct_2023 + nov_2023 + dec_2023 + jan_2024 + oct_2024 + nov_2024 + dec_2024 + jan_2025) AS total_spend,
      dec_2023,
      jan_2024,
      SAFE_DIVIDE(jan_2024, NULLIF(dec_2023, 0)) AS jan_to_dec_ratio_2023,
      dec_2024,
      jan_2025,
      SAFE_DIVIDE(jan_2025, NULLIF(dec_2024, 0)) AS jan_to_dec_ratio_2024
    FROM pivoted
    WHERE (oct_2023 + nov_2023 + dec_2023 + jan_2024 + oct_2024 + nov_2024 + dec_2024 + jan_2025) > 0
    ORDER BY total_spend DESC
    LIMIT 75;
    """.strip()


def _plot_quarterly_trend(df: pd.DataFrame, out_path: Path, title: str) -> None:
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 4.5))

    plot_df = df.copy()
    plot_df["quarter_start"] = pd.to_datetime(plot_df["quarter_start"])

    # Single line: sum across report_category, keep bucket.
    agg = plot_df.groupby(["quarter_start", "bucket"], as_index=False).agg(spend=("spend", "sum"))
    agg = pd.DataFrame(agg).sort_values(by=["quarter_start", "bucket"]).reset_index(drop=True)

    sns.lineplot(data=agg, x="quarter_start", y="spend", hue="bucket", marker="o")

    ax = plt.gca()
    ax.set_title(title)
    ax.set_xlabel("Calendar quarter")
    ax.set_ylabel("Spend (nominal)")

    # Visual cue for Q4 quarters.
    for q_start in sorted(agg["quarter_start"].unique()):
        if q_start.quarter == 4:
            ax.axvspan(q_start, q_start + pd.offsets.QuarterEnd(startingMonth=12), color="gray", alpha=0.08)

    plt.legend(title=None, loc="best")
    _savefig(out_path)


def _plot_overlay_indexed(df: pd.DataFrame, out_path: Path) -> None:
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 4.5))

    plot_df = df.copy()
    plot_df["quarter_start"] = pd.to_datetime(plot_df["quarter_start"])

    sns.lineplot(data=plot_df, x="quarter_start", y="index", hue="source", marker="o")

    ax = plt.gca()
    ax.set_title("Seasonality comparison (indexed): Supplier vs Provider")
    ax.set_xlabel("Calendar quarter")
    ax.set_ylabel("Index (avg quarter = 100)")

    for q_start in sorted(plot_df["quarter_start"].unique()):
        if q_start.quarter == 4:
            ax.axvspan(q_start, q_start + pd.offsets.QuarterEnd(startingMonth=12), color="gray", alpha=0.08)

    plt.legend(title=None, loc="best")
    _savefig(out_path)


def _plot_monthly_transition(df: pd.DataFrame, out_path: Path) -> None:
    sns.set_theme(style="whitegrid")

    plot_df = df.copy()
    plot_df["month_start"] = pd.to_datetime(plot_df["month_start"])

    # Focus on GE only for diagnostics.
    plot_df = plot_df[plot_df["manufacturer_bucket"] == "GE"].copy()
    plot_df = plot_df.groupby(["month_start"], as_index=False).agg(spend=("spend", "sum"))
    plot_df = pd.DataFrame(plot_df).sort_values(by="month_start").reset_index(drop=True)

    plt.figure(figsize=(10, 4.5))
    sns.barplot(data=plot_df, x="month_start", y="spend", color="#2a6fbb")

    ax = plt.gca()
    ax.set_title("Provider timing diagnostic: Oct–Feb monthly spend (GE bucket)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Spend (nominal)")

    ax.set_xticklabels([d.strftime("%Y-%m") for d in plot_df["month_start"]], rotation=45, ha="right")

    # Shade December months.
    for d in plot_df["month_start"]:
        if d.month == 12:
            ax.axvspan(
                list(plot_df["month_start"]).index(d) - 0.5,
                list(plot_df["month_start"]).index(d) + 0.5,
                color="gray",
                alpha=0.08,
            )

    _savefig(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Q4 seasonality differences between Supplier Spend and Provider Transactions")
    parser.add_argument("--run-id", type=str, help="Run ID (creates snapshots/<RUN_ID>/)")
    parser.add_argument("--snapshot-dir", type=Path, help="Existing snapshot dir to write into")
    parser.add_argument("--start-date", type=str, default=DEFAULT_START)
    parser.add_argument("--end-date", type=str, default=DEFAULT_END)
    args = parser.parse_args()

    if args.snapshot_dir:
        snapshot_dir = args.snapshot_dir
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        (snapshot_dir / "visuals").mkdir(parents=True, exist_ok=True)
        run_id = snapshot_dir.name
    else:
        run_id = args.run_id or _now_run_id()
        snapshot_dir = _ensure_snapshot_dir(run_id)

    client = _get_bq_client()

    # STEP 1 — Supplier timing pattern (truth anchor)
    supplier_sql = _supplier_quarterly_sql(args.start_date, args.end_date)
    supplier_df = client.query(supplier_sql).to_dataframe(create_bqstorage_client=False)
    supplier_df = supplier_df.rename(columns={"supplier_bucket": "bucket"})
    _write_csv(supplier_df, snapshot_dir / "q4_supplier_quarterly.csv")

    # STEP 2 — Provider transactional timing curve
    provider_sql = _provider_quarterly_sql(args.start_date, args.end_date)
    provider_df = client.query(provider_sql).to_dataframe(create_bqstorage_client=False)
    provider_df = provider_df.rename(columns={"manufacturer_bucket": "bucket"})
    _write_csv(provider_df, snapshot_dir / "q4_provider_quarterly.csv")

    # Overlay for comparison: index each source to avg=100 (so we compare seasonality, not levels).
    supplier_ge = supplier_df[supplier_df["bucket"] == "GE"].groupby("quarter_start", as_index=False)["spend"].sum()
    provider_ge = provider_df[provider_df["bucket"] == "GE"].groupby("quarter_start", as_index=False)["spend"].sum()

    supplier_ge["source"] = "supplier_spend (invoiced timing proxy)"
    provider_ge["source"] = "provider_transactions (ERP timing)"

    overlay = pd.concat([supplier_ge, provider_ge], ignore_index=True)
    overlay["quarter_start"] = pd.to_datetime(overlay["quarter_start"])

    overlay["index"] = overlay.groupby("source")["spend"].transform(lambda s: (s / s.mean()) * 100 if s.mean() else 0)
    overlay = overlay.sort_values(["source", "quarter_start"])
    _write_csv(overlay, snapshot_dir / "q4_quarterly_overlay_indexed.csv")

    # STEP 3 — Monthly transition analysis
    monthly_sql = _provider_monthly_transition_sql()
    monthly_df = client.query(monthly_sql).to_dataframe(create_bqstorage_client=False)
    _write_csv(monthly_df, snapshot_dir / "q4_provider_monthly_transition.csv")

    # STEP 4 — System-level variability
    sys_sql = _provider_system_variability_sql()
    sys_df = client.query(sys_sql).to_dataframe(create_bqstorage_client=False)
    _write_csv(sys_df, snapshot_dir / "q4_provider_system_variability.csv")

    # STEP 5 — Stakeholder-ready synthesis (Markdown) using the generated artifacts.
    _write_timing_summary_md(
      snapshot_dir=snapshot_dir,
      supplier_df=supplier_df,
      provider_df=provider_df,
      monthly_df=monthly_df,
      sys_df=sys_df,
      start_date=args.start_date,
      end_date=args.end_date,
    )

    # STEP 6 — Stakeholder-ready visuals
    visuals_dir = snapshot_dir / "visuals"

    _plot_quarterly_trend(
        supplier_df,
        visuals_dir / "q4_supplier_quarterly_trend.png",
        "Supplier Spend: Calendar-quarter trend (Q4 shaded)",
    )
    _plot_quarterly_trend(
        provider_df,
        visuals_dir / "q4_provider_quarterly_trend.png",
        "Provider Transactions: Calendar-quarter trend (Q4 shaded)",
    )
    _plot_overlay_indexed(overlay, visuals_dir / "q4_quarterly_overlay_indexed.png")
    _plot_monthly_transition(monthly_df, visuals_dir / "q4_provider_monthly_transition.png")

    # Write a small manifest for handoff.
    manifest = {
        "run_id": run_id,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "inputs": {
            "supplier_table": SUPPLIER_TABLE,
            "provider_table": PROVIDER_TABLE,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "capital_price_threshold": CAPITAL_PRICE_THRESHOLD,
        },
        "artifacts": {
            "supplier_quarterly_csv": "q4_supplier_quarterly.csv",
            "provider_quarterly_csv": "q4_provider_quarterly.csv",
            "overlay_indexed_csv": "q4_quarterly_overlay_indexed.csv",
            "provider_monthly_transition_csv": "q4_provider_monthly_transition.csv",
            "provider_system_variability_csv": "q4_provider_system_variability.csv",
            "timing_summary_md": "q4_timing_summary.md",
            "charts": [
                "visuals/q4_supplier_quarterly_trend.png",
                "visuals/q4_provider_quarterly_trend.png",
                "visuals/q4_quarterly_overlay_indexed.png",
                "visuals/q4_provider_monthly_transition.png",
            ],
        },
        "notes": [
            "Provider timing uses Transaction_Date; not revenue timing.",
            "No PO vs invoice separation is attempted.",
            "System variability is reported by Health_System_Entity_Code only (no names).",
        ],
    }
    (snapshot_dir / "q4_timing_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote Q4 timing outputs to {snapshot_dir}")


if __name__ == "__main__":
    # Ensure consistent behavior when scripts are invoked from tools.
    os.environ.setdefault("PYTHONPATH", ".")
    main()
