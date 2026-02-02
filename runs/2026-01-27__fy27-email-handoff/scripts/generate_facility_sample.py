#!/usr/bin/env python3
"""
Generate de-identified facility-level sample data cut for B. Braun IV Solutions.

Loads TAE (Provider) and RB (Wholesaler) raw extracts, aggregates by facility,
validates cross-source consistency, and outputs a blinded facility summary.

Run ID: 2026-01-27__fy27-email-handoff
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# === Config ===
RUN_ID = "2026-01-27__fy27-email-handoff"
RUN_DIR = Path(f"runs/{RUN_ID}")
EXPORTS_DIR = RUN_DIR / "exports"

TAE_FILE = EXPORTS_DIR / "iv_solutions__tae_raw.csv"
RB_FILE = EXPORTS_DIR / "iv_solutions__rb_raw.csv"

OUTPUT_SAMPLE = EXPORTS_DIR / "iv_solutions__facility_sample.csv"
OUTPUT_SUMMARY = EXPORTS_DIR / "iv_solutions__facility_sample_summary.json"


def load_data():
    """Load TAE and RB raw CSVs."""
    print(f"Loading TAE data from {TAE_FILE}...")
    df_tae = pd.read_csv(TAE_FILE)
    print(f"  → {len(df_tae):,} rows, columns: {list(df_tae.columns)}")

    print(f"Loading RB data from {RB_FILE}...")
    df_rb = pd.read_csv(RB_FILE)
    print(f"  → {len(df_rb):,} rows, columns: {list(df_rb.columns)}")

    return df_tae, df_rb


def aggregate_tae(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate TAE (Provider) data by facility."""
    agg = df.groupby("facility_id").agg(
        tae_total_spend=("tae_spend", "sum"),
        tae_total_units=("tae_units", "sum"),
        tae_months=("month_year", "nunique"),
        tae_vendors=("vendor_name", "nunique"),
        tae_first_month=("month_year", "min"),
        tae_last_month=("month_year", "max"),
    ).reset_index()
    agg["source"] = "TAE"
    return agg


def aggregate_rb(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate RB (Wholesaler) data by facility."""
    agg = df.groupby("facility_id").agg(
        rb_total_spend=("rb_spend", "sum"),
        rb_total_units=("rb_units", "sum"),
        rb_months=("month_year_fmt", "nunique"),
        rb_ndcs=("ndc", "nunique"),
        rb_first_month=("month_year_fmt", "min"),
        rb_last_month=("month_year_fmt", "max"),
    ).reset_index()
    agg["source"] = "RB"
    return agg


def merge_and_validate(tae_agg: pd.DataFrame, rb_agg: pd.DataFrame) -> pd.DataFrame:
    """Merge TAE and RB by facility_id and compute cross-source metrics."""
    # Outer join to capture facilities in either/both sources
    merged = pd.merge(
        tae_agg,
        rb_agg,
        on="facility_id",
        how="outer",
        suffixes=("_tae", "_rb"),
    )

    # Fill NaNs for facilities only in one source
    merged["tae_total_spend"] = merged["tae_total_spend"].fillna(0)
    merged["tae_total_units"] = merged["tae_total_units"].fillna(0)
    merged["rb_total_spend"] = merged["rb_total_spend"].fillna(0)
    merged["rb_total_units"] = merged["rb_total_units"].fillna(0)

    # Combined metrics
    merged["combined_spend"] = merged["tae_total_spend"] + merged["rb_total_spend"]
    merged["combined_units"] = merged["tae_total_units"] + merged["rb_total_units"]

    # Source coverage flag
    def source_flag(row):
        has_tae = row["tae_total_spend"] > 0
        has_rb = row["rb_total_spend"] > 0
        if has_tae and has_rb:
            return "BOTH"
        elif has_tae:
            return "TAE_ONLY"
        else:
            return "RB_ONLY"

    merged["source_coverage"] = merged.apply(source_flag, axis=1)

    return merged


def deidentify(df: pd.DataFrame) -> pd.DataFrame:
    """Replace facility_id with blinded identifiers, sorted by spend."""
    # Sort by combined spend descending
    df = df.sort_values("combined_spend", ascending=False).reset_index(drop=True)

    # Create blinded ID
    df["blinded_facility_id"] = [f"FAC_{i+1:04d}" for i in range(len(df))]

    # Select and reorder columns for output
    output_cols = [
        "blinded_facility_id",
        "source_coverage",
        "combined_spend",
        "combined_units",
        "tae_total_spend",
        "tae_total_units",
        "tae_months",
        "tae_vendors",
        "rb_total_spend",
        "rb_total_units",
        "rb_months",
        "rb_ndcs",
    ]

    return df[output_cols]


def generate_summary(df: pd.DataFrame, tae_raw: pd.DataFrame, rb_raw: pd.DataFrame) -> dict:
    """Generate summary statistics for the sample."""
    return {
        "generated_at": datetime.now().isoformat(),
        "run_id": RUN_ID,
        "raw_data": {
            "tae_rows": len(tae_raw),
            "rb_rows": len(rb_raw),
        },
        "facility_counts": {
            "total": len(df),
            "both_sources": int((df["source_coverage"] == "BOTH").sum()),
            "tae_only": int((df["source_coverage"] == "TAE_ONLY").sum()),
            "rb_only": int((df["source_coverage"] == "RB_ONLY").sum()),
        },
        "spend_totals": {
            "combined": float(df["combined_spend"].sum()),
            "tae": float(df["tae_total_spend"].sum()),
            "rb": float(df["rb_total_spend"].sum()),
        },
        "unit_totals": {
            "combined": float(df["combined_units"].sum()),
            "tae": float(df["tae_total_units"].sum()),
            "rb": float(df["rb_total_units"].sum()),
        },
        "top_10_facilities": df.head(10)[
            ["blinded_facility_id", "source_coverage", "combined_spend", "combined_units"]
        ].to_dict(orient="records"),
    }


def main():
    print("=" * 60)
    print("B. Braun IV Solutions — Facility-Level Sample Generation")
    print("=" * 60)

    # Load
    df_tae, df_rb = load_data()

    # Aggregate
    print("\nAggregating TAE by facility...")
    tae_agg = aggregate_tae(df_tae)
    print(f"  → {len(tae_agg):,} unique facilities in TAE")

    print("Aggregating RB by facility...")
    rb_agg = aggregate_rb(df_rb)
    print(f"  → {len(rb_agg):,} unique facilities in RB")

    # Merge and validate
    print("\nMerging datasets and computing cross-source metrics...")
    merged = merge_and_validate(tae_agg, rb_agg)
    print(f"  → {len(merged):,} total unique facilities")

    # De-identify
    print("\nDe-identifying facility IDs...")
    sample = deidentify(merged)

    # Summary
    summary = generate_summary(sample, df_tae, df_rb)

    # Output
    print(f"\nWriting sample to {OUTPUT_SAMPLE}...")
    sample.to_csv(OUTPUT_SAMPLE, index=False)

    print(f"Writing summary to {OUTPUT_SUMMARY}...")
    with open(OUTPUT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total facilities: {summary['facility_counts']['total']:,}")
    print(f"  - Both sources: {summary['facility_counts']['both_sources']:,}")
    print(f"  - TAE only: {summary['facility_counts']['tae_only']:,}")
    print(f"  - RB only: {summary['facility_counts']['rb_only']:,}")
    print(f"\nTotal spend: ${summary['spend_totals']['combined']:,.2f}")
    print(f"  - TAE: ${summary['spend_totals']['tae']:,.2f}")
    print(f"  - RB: ${summary['spend_totals']['rb']:,.2f}")
    print(f"\nTotal units: {summary['unit_totals']['combined']:,.0f}")
    print("\nTop 10 facilities by combined spend:")
    for fac in summary["top_10_facilities"]:
        print(f"  {fac['blinded_facility_id']}: ${fac['combined_spend']:,.2f} ({fac['source_coverage']})")

    print("\nDone.")


if __name__ == "__main__":
    main()
