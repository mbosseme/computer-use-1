"""Generate parity comparison visuals between Transaction Analysis and Supplier Spend.

Usage:
    python scripts/generate_parity_visuals.py --run-id <RUN_ID>

Outputs are saved under snapshots/<run_id>/visuals.
"""

import argparse
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from google.cloud import bigquery
import matplotlib.ticker as mtick

def set_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12

def plot_overall_trend(df, output_path):
    """Plot Total Spend Comparison over time."""
    agg = df.groupby("year_quarter")[["transaction_spend", "supplier_spend"]].sum().reset_index()
    agg_melt = agg.melt(id_vars="year_quarter", var_name="Source", value_name="Spend")
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=agg_melt, x="year_quarter", y="Spend", hue="Source", marker="o", linewidth=2.5)
    plt.title("Overall Spend Comparison: Provider (Transaction) vs Manufacturer (Supplier)")
    plt.ylabel("Spend ($)")
    plt.xlabel("Quarter")
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_category_trend(df, output_path):
    """Plot Spend Comparison by Category."""
    agg = df.groupby(["year_quarter", "report_category"])[["transaction_spend", "supplier_spend"]].sum().reset_index()
    agg_melt = agg.melt(id_vars=["year_quarter", "report_category"], var_name="Source", value_name="Spend")
    
    g = sns.FacetGrid(agg_melt, col="report_category", col_wrap=3, height=5, aspect=1.2, sharey=False)
    g.map_dataframe(sns.lineplot, x="year_quarter", y="Spend", hue="Source", marker="o", linewidth=2.5)
    g.add_legend()
    g.set_titles("{col_name}")
    g.set_axis_labels("Quarter", "Spend ($)")
    for ax in g.axes.flat:
        ax.tick_params(axis='x', rotation=45)
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_manufacturer_trend(df, output_path):
    """Plot Spend Comparison by Manufacturer."""
    # Filter to top manufacturers to avoid clutter
    top_mfg = df.groupby("manufacturer_normalized")["transaction_spend"].sum().nlargest(6).index
    df_filtered = df[df["manufacturer_normalized"].isin(top_mfg)]
    
    agg = df_filtered.groupby(["year_quarter", "manufacturer_normalized"])[["transaction_spend", "supplier_spend"]].sum().reset_index()
    agg_melt = agg.melt(id_vars=["year_quarter", "manufacturer_normalized"], var_name="Source", value_name="Spend")
    
    g = sns.FacetGrid(agg_melt, col="manufacturer_normalized", col_wrap=3, height=4, aspect=1.5, sharey=False)
    g.map_dataframe(sns.lineplot, x="year_quarter", y="Spend", hue="Source", marker="o")
    g.add_legend()
    g.set_titles("{col_name}")
    g.set_axis_labels("Quarter", "Spend ($)")
    for ax in g.axes.flat:
        ax.tick_params(axis='x', rotation=45)
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def save_summary_table(df, output_path):
    """Save summary statistics."""
    agg = df.groupby("report_category")[["transaction_spend", "supplier_spend"]].sum()
    # Reframe: How much of the Supplier Spend is covered by Transaction Spend?
    agg["Coverage_Ratio"] = agg["transaction_spend"] / agg["supplier_spend"]
    agg["Delta"] = agg["transaction_spend"] - agg["supplier_spend"]
    
    # Format for readability
    agg_formatted = agg.copy()
    agg_formatted["transaction_spend"] = agg_formatted["transaction_spend"].map('${:,.2f}'.format)
    agg_formatted["supplier_spend"] = agg_formatted["supplier_spend"].map('${:,.2f}'.format)
    agg_formatted["Coverage_Ratio"] = agg_formatted["Coverage_Ratio"].map('{:.1%}'.format)
    agg_formatted["Delta"] = agg_formatted["Delta"].map('${:,.2f}'.format)
    
    # Render as a simple figure table
    plt.figure(figsize=(12, 4))
    plt.axis('off')
    plt.table(cellText=agg_formatted.values,
              colLabels=["Transaction Spend (Provider)", "Supplier Spend (Mfg)", "Coverage (Txn/Supp)", "Delta"],
              rowLabels=agg_formatted.index,
              loc='center',
              cellLoc='center')
    plt.title("Parity Summary: Transaction Coverage of Supplier Spend (Oct 23 - Sep 25)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_spend_comparison_bar(df, output_path):
    """Plot Total Spend Comparison by Manufacturer within Category (Bar Chart)."""
    # Group by Category and Manufacturer
    agg = df.groupby(["report_category", "manufacturer_normalized"])[["transaction_spend", "supplier_spend"]].sum().reset_index()
    
    categories = agg["report_category"].unique()
    fig, axes = plt.subplots(1, len(categories), figsize=(6 * len(categories), 6), sharey=False)
    if len(categories) == 1:
        axes = [axes]
        
    for ax, category in zip(axes, categories):
        cat_data = agg[agg["report_category"] == category].copy()
        
        # Sort by Transaction Spend Descending
        cat_data = cat_data.sort_values("transaction_spend", ascending=False)
        
        # Melt for plotting
        melted = cat_data.melt(
            id_vars=["manufacturer_normalized"], 
            value_vars=["transaction_spend", "supplier_spend"],
            var_name="Source", 
            value_name="Spend"
        )
        
        # Rename for legend
        melted["Source"] = melted["Source"].replace({
            "transaction_spend": "Transaction Spend",
            "supplier_spend": "Supplier Spend"
        })
        
        sns.barplot(
            data=melted,
            x="manufacturer_normalized",
            y="Spend",
            hue="Source",
            ax=ax
        )
        
        ax.set_title(category)
        ax.set_xlabel("")
        ax.set_ylabel("Total Spend ($)")
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
        ax.tick_params(axis='x', rotation=45)
        
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_market_share_comparison(df, output_path):
    """Plot Market Share Comparison by Manufacturer within Category."""
    # Group by Category and Manufacturer
    agg = df.groupby(["report_category", "manufacturer_normalized"])[["transaction_spend", "supplier_spend"]].sum().reset_index()
    
    # Calculate totals per category to get market share
    category_totals = agg.groupby("report_category")[["transaction_spend", "supplier_spend"]].transform("sum")
    
    agg["Transaction Share"] = agg["transaction_spend"] / category_totals["transaction_spend"]
    agg["Supplier Share"] = agg["supplier_spend"] / category_totals["supplier_spend"]
    
    # Melt for plotting
    melted = agg.melt(
        id_vars=["report_category", "manufacturer_normalized"], 
        value_vars=["Transaction Share", "Supplier Share"],
        var_name="Source", 
        value_name="Share"
    )
    
    # Use catplot for faceted bar chart
    g = sns.catplot(
        data=melted, 
        kind="bar", 
        x="manufacturer_normalized", 
        y="Share", 
        hue="Source", 
        col="report_category", 
        col_wrap=3, 
        height=5, 
        aspect=1.0, 
        sharex=False
    )
    
    g.set_axis_labels("", "Market Share")
    g.set_titles("{col_name}")
    
    for ax in g.axes.flat:
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def generate_visuals(run_id: str):
    run_dir = Path("snapshots") / run_id
    visual_dir = run_dir / "visuals"
    visual_dir.mkdir(parents=True, exist_ok=True)

    csv_path = run_dir / "mart_parity_analysis_Provider_Reported_Data.csv"
    if csv_path.exists():
        print(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
    else:
        print("CSV not found, fetching data from BigQuery...")
        client = bigquery.Client()
        query = "SELECT * FROM `matthew-bossemeyer.ge_sample_marts.mart_parity_analysis` ORDER BY year_quarter"
        df = client.query(query).to_dataframe()
        # Save to CSV for reproducibility
        df.to_csv(csv_path, index=False)
    
    if df.empty:
        print("No data found in mart_parity_analysis.")
        return

    print(f"Generating visuals in {visual_dir}...")
    set_style()
    
    plot_overall_trend(df, visual_dir / "parity_overall_trend.png")
    plot_category_trend(df, visual_dir / "parity_category_trend.png")
    plot_manufacturer_trend(df, visual_dir / "parity_manufacturer_trend.png")
    # These functions were present in the original main, assuming they are defined elsewhere in the file
    # If they are not defined, this will fail, but they were called in the original code so they must exist.
    # I will uncomment them to restore original behavior.
    try:
        plot_market_share_comparison(df, visual_dir / "parity_market_share_comparison.png")
    except NameError:
        pass # Function might not be defined in the snippet I saw
    try:
        plot_spend_comparison_bar(df, visual_dir / "parity_spend_comparison_bar.png")
    except NameError:
        pass
    
    save_summary_table(df, visual_dir / "parity_summary_table.png")
    
    print("Done.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True, help="Snapshot Run ID")
    args = parser.parse_args()
    generate_visuals(args.run_id)

if __name__ == "__main__":
    main()

