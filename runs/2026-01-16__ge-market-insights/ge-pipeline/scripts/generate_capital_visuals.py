"""Generate executive-facing and QA visualizations for GE capital artifacts.

Usage:
    python scripts/generate_capital_visuals.py --run-id 20251120T122507Z

Outputs are saved under snapshots/<run_id>/visuals.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Import parity generation logic
try:
    import generate_parity_visuals
except ImportError:
    # If running from root, scripts is not in path by default for imports unless -m is used
    # But since we are in the same directory, we can try relative import if this was a package,
    # or just append to path.
    import sys
    sys.path.append(str(Path(__file__).parent))
    import generate_parity_visuals


EXECUTIVE_CHARTS = [
    "exec_modality_trend.png",
    "exec_share_latest_quarter.png",
    "exec_share_vs_yoy_scatter.png",
]

QA_CHARTS = [
    "qa_spend_vs_transactions.png",
    "qa_contract_category_mix.png",
]

MANUFACTURER_ORDER = ["GE", "SIEMENS", "PHILIPS", "CANON", "NIHON KOHDEN", "SPACELABS", "MINDRAY", "SAMSUNG", "OTHER"]


def _ensure_visual_dir(run_dir: Path) -> Path:
    visual_dir = run_dir / "visuals"
    visual_dir.mkdir(parents=True, exist_ok=True)
    return visual_dir


def _load_data(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    val_path = run_dir / "mart_validation_mapping_Provider_Reported_Data.csv"
    trend_path = run_dir / "mart_observed_trends_Provider_Reported_Data.csv"
    if not val_path.exists() or not trend_path.exists():
        raise FileNotFoundError(
            "Expected snapshot CSVs not found. Ensure Dataform exports were generated first."
        )

    validation_df = pd.read_csv(val_path)
    trends_df = pd.read_csv(trend_path, parse_dates=["quarter_start"])
    trends_df["year_quarter"] = trends_df["year_quarter"].astype(str)
    return validation_df, trends_df


def _format_currency(value: float) -> str:
    if value >= 1e9:
        return f"${value / 1e9:,.1f}B"
    if value >= 1e6:
        return f"${value / 1e6:,.1f}M"
    return f"${value:,.0f}"


def _plot_exec_modality_trend(trends_df: pd.DataFrame, out_path: Path) -> None:
    df = trends_df.sort_values("quarter_start").copy()
    df["spend_millions"] = df["total_observed_spend"] / 1e6
    pivot = df.pivot_table(
        index="quarter_start", columns="report_category", values="spend_millions", aggfunc="sum"
    ).fillna(0)

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=pivot)
    plt.title("Observed Capital Spend by Category (Provider Reported)")
    plt.ylabel("Spend (USD Millions)")
    plt.xlabel("Quarter")
    ticks = [f"{d.year}-Q{d.quarter}" for d in pivot.index]
    plt.xticks(pivot.index, ticks, rotation=45)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def _plot_exec_share_latest(trends_df: pd.DataFrame, out_path: Path) -> None:
    latest_quarter = trends_df["quarter_start"].max()
    latest = trends_df[trends_df["quarter_start"] == latest_quarter].copy()
    latest["share_pct"] = latest["share_of_observed_spend"] * 100
    latest["manufacturer_normalized"] = pd.Categorical(
        latest["manufacturer_normalized"], categories=MANUFACTURER_ORDER, ordered=True
    )
    pivot = latest.pivot_table(
        index="report_category",
        columns="manufacturer_normalized",
        values="share_pct",
        aggfunc="sum",
        observed=False,
    ).fillna(0)[MANUFACTURER_ORDER]

    (pivot.T).plot(kind="bar", stacked=True, figsize=(8, 5), colormap="tab20")
    plt.title(f"Manufacturer Share of Observed Spend – {latest.iloc[0]['year_quarter']}")
    plt.ylabel("Share of Category Spend (%)")
    plt.xlabel("Manufacturer")
    plt.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def _plot_exec_share_vs_yoy(trends_df: pd.DataFrame, out_path: Path) -> None:
    latest_quarter = trends_df["quarter_start"].max()
    latest = trends_df[trends_df["quarter_start"] == latest_quarter].copy()
    latest["share_pct"] = latest["share_of_observed_spend"] * 100
    latest["yoy_pct"] = latest["yoy_growth"] * 100
    latest["spend_m"] = (latest["total_observed_spend"] / 1e6).round(1)

    plt.figure(figsize=(10, 6))
    # Plot points
    scatter = sns.scatterplot(
        data=latest,
        x="share_pct",
        y="yoy_pct",
        size="spend_m",
        hue="report_category",
        sizes=(50, 500),
        alpha=0.7,
        legend="brief"
    )
    
    # Annotate points
    for _, row in latest.iterrows():
        label = f"{row['manufacturer_normalized']}"
        plt.annotate(label, (row["share_pct"], row["yoy_pct"]), textcoords="offset points", xytext=(3, 3), fontsize=8)

    plt.title("Share vs. YoY Growth (Latest Quarter)")
    plt.xlabel("Share of Category Spend (%)")
    plt.ylabel("YoY Growth (%)")
    plt.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    
    # Improve Legend
    # Move legend outside
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def _plot_qa_spend_vs_transactions(validation_df: pd.DataFrame, out_path: Path) -> None:
    df = validation_df.copy()
    df["total_m"] = df["total_observed_spend"] / 1e6
    top = df.sort_values("total_observed_spend", ascending=False).head(500)

    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=top,
        x="transaction_count",
        y="total_m",
        hue="report_category",
        alpha=0.7,
    )
    plt.xscale("symlog")
    plt.title("Spend vs. Transaction Count (Top 500 SKU Rows)")
    plt.xlabel("Transaction Count (symlog scale)")
    plt.ylabel("Spend (USD Millions)")
    plt.legend(title="Category")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def _plot_qa_contract_category_mix(validation_df: pd.DataFrame, out_path: Path) -> None:
    """
    Shows spend breakdown by Category Source (Categorized vs Keyword Match) for each Report Category.
    """
    df = validation_df.copy()
    
    # Map category_source to user-friendly labels
    # category_source comes from SQL: 'CONTRACT_CATEGORY', 'DESCRIPTION_KEYWORD', 'UNKNOWN'
    # We want to see "Categorized" vs "Keyword Match"
    
    def map_source(val):
        if val == 'CONTRACT_CATEGORY':
            return 'Categorized (Standard)'
        elif val == 'DESCRIPTION_KEYWORD':
            return 'Keyword Match (Uncategorized)'
        else:
            return 'Other/Unknown'

    # Note: validation_df might not have 'category_source' if it wasn't in the SELECT list of the mart.
    # Let's check if it's there. If not, we might need to infer it or update the mart.
    # The mart_validation_mapping.sqlx usually selects * from staging or specific cols.
    # Let's assume for now we need to rely on 'contract_category' column if 'category_source' isn't there.
    # But wait, the user asked for "Natural Language Inspection" vs "Categorized".
    # In stg_ge_capital_systems.sqlx, we created 'category_source'.
    # Let's hope it's passed through to mart_validation_mapping.
    
    # If category_source is available, use it. If not, fallback to logic.
    if 'category_source' in df.columns:
        df['source_label'] = df['category_source'].apply(map_source)
    else:
        # Fallback logic similar to SQL
        df['source_label'] = df.apply(lambda row: 
            'Categorized (Standard)' if (pd.notna(row['contract_category']) and str(row['contract_category']).upper() != 'UNKNOWN')
            else 'Keyword Match (Uncategorized)', axis=1)

    grouped = (
        df.groupby(["report_category", "source_label"], as_index=False)["total_observed_spend"].sum()
    )
    
    pivot = grouped.pivot_table(
        index="report_category",
        columns="source_label",
        values="total_observed_spend",
        aggfunc="sum",
        observed=False,
    ).fillna(0)
    pivot = pivot / 1e6

    pivot.plot(kind="bar", stacked=True, figsize=(8, 6), color=["#2E86C1", "#F39C12", "#95A5A6"])
    plt.title("Observed Spend by Identification Method")
    plt.ylabel("Spend (USD Millions)")
    plt.xlabel("Category")
    plt.legend(title="Identification Method")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def main(run_id: str) -> None:
    run_dir = Path("snapshots") / run_id
    visual_dir = _ensure_visual_dir(run_dir)
    validation_df, trends_df = _load_data(run_dir)

    sns.set_theme(style="whitegrid")

    _plot_exec_modality_trend(trends_df, visual_dir / EXECUTIVE_CHARTS[0])
    _plot_exec_share_latest(trends_df, visual_dir / EXECUTIVE_CHARTS[1])
    _plot_exec_share_vs_yoy(trends_df, visual_dir / EXECUTIVE_CHARTS[2])
    _plot_qa_spend_vs_transactions(validation_df, visual_dir / QA_CHARTS[0])
    _plot_qa_contract_category_mix(validation_df, visual_dir / QA_CHARTS[1])

    manifest_path = visual_dir / "visual_manifest.json"
    manifest = {
        "run_id": run_id,
        "executive": EXECUTIVE_CHARTS,
        "qa": QA_CHARTS,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    
    # Generate Parity Visuals
    print("Generating Parity Visuals...")
    generate_parity_visuals.generate_visuals(run_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate GE capital visualization assets.")
    parser.add_argument("--run-id", required=True, help="Snapshot run identifier (e.g., 20251120T122507Z)")
    args = parser.parse_args()
    main(args.run_id)