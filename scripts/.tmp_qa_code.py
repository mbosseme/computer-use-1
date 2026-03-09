import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np

fp = "runs/2026-03-04__portfolio-competitiveness/HCIQ_Benchmark_Analysis_Deliverable.xlsx"

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 240)
pd.set_option("display.float_format", lambda x: f"{x:,.6f}")

def hdr(t):
    print("\n" + "=" * 120)
    print(t)
    print("=" * 120)

def print_df(df, cols=None, sort_col=None, ascending=False, n=12):
    if len(df) == 0:
        print("None")
        return
    x = df.copy()
    if sort_col is not None:
        x = x.sort_values(sort_col, ascending=ascending)
    if cols is not None:
        x = x[cols]
    print(x.head(n).to_string(index=False))

# Load
a = pd.read_excel(fp, sheet_name="Tab A - Program Summary")
b = pd.read_excel(fp, sheet_name="Tab B - Contract Summary")

# Standardize
a["Program_key"] = a["Program"].astype(str).str.strip()
b["Program_key"] = b["Program"].astype(str).str.strip()

num_a = [
    "Total_Contracts","Total_Historical_Spend","Total_Benchmarkable_Spend",
    "Benchmark_Coverage_Pct","Total_Spend_at_Best_Tier",
    "Avg_Program_Percentile","Weighted_Avg_Program_Percentile"
]
num_b = [
    "Contract_Total_Spend","Contract_Total_Units","Benchmark_Coverage_Pct","Spend_at_Best_Tier",
    "Target_Spend_Low","Target_Spend_90th","Target_Spend_75th","Target_Spend_50th","Target_Spend_High",
    "Estimated_Percentile_Linear"
]
for c in num_a:
    a[c] = pd.to_numeric(a[c], errors="coerce")
for c in num_b:
    b[c] = pd.to_numeric(b[c], errors="coerce")

targets = ["Target_Spend_Low","Target_Spend_90th","Target_Spend_75th","Target_Spend_50th","Target_Spend_High"]

# Derived fields
b["Derived_Benchmarkable_Spend"] = b["Contract_Total_Spend"] * b["Benchmark_Coverage_Pct"]
b["Current_PPU"] = np.where(b["Contract_Total_Units"] > 0, b["Contract_Total_Spend"] / b["Contract_Total_Units"], np.nan)
b["Target50_PPU"] = np.where(b["Contract_Total_Units"] > 0, b["Target_Spend_50th"] / b["Contract_Total_Units"], np.nan)
b["Target50_to_Current_PPU"] = b["Target50_PPU"] / b["Current_PPU"]

b["LowCov"] = b["Flag_Coverage"].astype(str).str.upper().eq("LOW_COVERAGE")
b["UnknownBucket"] = b["Percentile_Bucket"].astype(str).str.upper().eq("UNKNOWN")
b["BestInMarket"] = b["Percentile_Bucket"].astype(str).str.contains("Best in Market", case=False, na=False)
b["AllTargetsMissingOrZero"] = b[targets].isna().all(axis=1) | b[targets].fillna(0).eq(0).all(axis=1)

# Reconcile / program summary
g = b.groupby("Program_key", dropna=False).agg(
    Contracts=("Contract_Number","size"),
    Spend=("Contract_Total_Spend","sum"),
    Benchmarkable=("Derived_Benchmarkable_Spend","sum"),
    Best_Tier=("Spend_at_Best_Tier","sum"),
    LowCov_Contracts=("LowCov","sum"),
    LowCov_Spend=("Contract_Total_Spend", lambda s: s[b.loc[s.index, "LowCov"]].sum()),
    Unknown_Contracts=("UnknownBucket","sum"),
    Unknown_Spend=("Contract_Total_Spend", lambda s: s[b.loc[s.index, "UnknownBucket"]].sum())
).reset_index()
g["Coverage_Pct"] = g["Benchmarkable"] / g["Spend"]
g["BestTier_minus_Benchmarkable"] = g["Best_Tier"] - g["Benchmarkable"]
g["BestTier_GT_Benchmarkable"] = g["Best_Tier"] > g["Benchmarkable"]

hdr("1) PROGRAM-LEVEL SUMMARY / 80% RULE / BEST-TIER VS BENCHMARKABLE")
print(g.sort_values("Program_key").to_string(index=False))

hdr("2) CONTRACT-LEVEL ANOMALY COUNTS")
anomaly_rows = []

m = b["Spend_at_Best_Tier"] > b["Contract_Total_Spend"]
anomaly_rows.append(["Spend_at_Best_Tier > Contract_Total_Spend", int(m.sum()), float((b.loc[m, "Spend_at_Best_Tier"] - b.loc[m, "Contract_Total_Spend"]).sum()), float(b.loc[m, "Contract_Total_Spend"].sum())])

m = b["Spend_at_Best_Tier"] > b["Derived_Benchmarkable_Spend"]
anomaly_rows.append(["Spend_at_Best_Tier > Derived_Benchmarkable_Spend", int(m.sum()), float((b.loc[m, "Spend_at_Best_Tier"] - b.loc[m, "Derived_Benchmarkable_Spend"]).sum()), float(b.loc[m, "Contract_Total_Spend"].sum())])

m = (b["Contract_Total_Spend"] > 0) & b["AllTargetsMissingOrZero"]
anomaly_rows.append(["Positive spend, all targets missing/zero", int(m.sum()), float(b.loc[m, "Derived_Benchmarkable_Spend"].sum()), float(b.loc[m, "Contract_Total_Spend"].sum())])

m = (b["Contract_Total_Spend"] > 0) & (b["Benchmark_Coverage_Pct"] > 0) & (b["Target_Spend_50th"].isna() | (b["Target_Spend_50th"] <= 0))
anomaly_rows.append(["Positive coverage, missing/zero 50th target", int(m.sum()), float(b.loc[m, "Derived_Benchmarkable_Spend"].sum()), float(b.loc[m, "Contract_Total_Spend"].sum())])

m = b["LowCov"] & b["BestInMarket"]
anomaly_rows.append(["LOW_COVERAGE + Best in Market", int(m.sum()), float(b.loc[m, "Derived_Benchmarkable_Spend"].sum()), float(b.loc[m, "Contract_Total_Spend"].sum())])

m = (b["Benchmark_Coverage_Pct"] == 0) & (~b["UnknownBucket"])
anomaly_rows.append(["Zero coverage but non-Unknown bucket", int(m.sum()), float(b.loc[m, "Derived_Benchmarkable_Spend"].sum()), float(b.loc[m, "Contract_Total_Spend"].sum())])

ladder_mask = b[targets].notna().all(axis=1)
m = ladder_mask & ~(
    (b["Target_Spend_Low"] <= b["Target_Spend_90th"]) &
    (b["Target_Spend_90th"] <= b["Target_Spend_75th"]) &
    (b["Target_Spend_75th"] <= b["Target_Spend_50th"]) &
    (b["Target_Spend_50th"] <= b["Target_Spend_High"])
)
anomaly_rows.append(["Non-monotonic target ladder", int(m.sum()), float(b.loc[m, "Target_Spend_50th"].sum()), float(b.loc[m, "Contract_Total_Spend"].sum())])

m = (b["Contract_Total_Units"] > 0) & (b["Current_PPU"] > 0) & (b["Target50_PPU"].notna()) & (b["Target50_to_Current_PPU"] < 0.05)
anomaly_rows.append(["Target50 PPU < 5% of current PPU", int(m.sum()), float(b.loc[m, "Target50_to_Current_PPU"].min() if m.sum() else np.nan), float(b.loc[m, "Contract_Total_Spend"].sum())])

m = (b["Contract_Total_Units"] > 0) & (b["Current_PPU"] > 0) & (b["Target50_PPU"].notna()) & (b["Target50_to_Current_PPU"] > 20)
anomaly_rows.append(["Target50 PPU > 20x current PPU", int(m.sum()), float(b.loc[m, "Target50_to_Current_PPU"].max() if m.sum() else np.nan), float(b.loc[m, "Contract_Total_Spend"].sum())])

anom = pd.DataFrame(anomaly_rows, columns=["Issue","Count","Metric_1","Affected_Spend_or_Base"])
print(anom.to_string(index=False))

hdr("3) TOP EXAMPLES: Spend_at_Best_Tier > Derived_Benchmarkable_Spend")
m = b["Spend_at_Best_Tier"] > b["Derived_Benchmarkable_Spend"]
tmp = b.loc[m].copy()
tmp["Excess_vs_Benchmarkable"] = tmp["Spend_at_Best_Tier"] - tmp["Derived_Benchmarkable_Spend"]
print_df(
    tmp,
    cols=[
        "Program","Contract_Number","Contract_Name","Contracted_Supplier",
        "Contract_Total_Spend","Benchmark_Coverage_Pct","Derived_Benchmarkable_Spend",
        "Spend_at_Best_Tier","Excess_vs_Benchmarkable","Flag_Coverage","Percentile_Bucket"
    ],
    sort_col="Excess_vs_Benchmarkable",
    ascending=False,
    n=12
)

hdr("4) TOP EXAMPLES: LOW_COVERAGE + Best in Market")
m = b["LowCov"] & b["BestInMarket"]
print_df(
    b.loc[m].copy(),
    cols=[
        "Program","Contract_Number","Contract_Name","Contracted_Supplier",
        "Contract_Total_Spend","Benchmark_Coverage_Pct","Derived_Benchmarkable_Spend",
        "Spend_at_Best_Tier","Target_Spend_Low","Target_Spend_50th","Target_Spend_High",
        "Estimated_Percentile_Linear","Flag_Coverage"
    ],
    sort_col="Contract_Total_Spend",
    ascending=False,
    n=12
)

hdr("5) TOP EXAMPLES: ZERO COVERAGE BUT NON-UNKNOWN BUCKET")
m = (b["Benchmark_Coverage_Pct"] == 0) & (~b["UnknownBucket"])
print_df(
    b.loc[m].copy(),
    cols=[
        "Program","Contract_Number","Contract_Name","Contracted_Supplier",
        "Contract_Total_Spend","Benchmark_Coverage_Pct","Percentile_Bucket",
        "Estimated_Percentile_Linear","Flag_Coverage"
    ],
    sort_col="Contract_Total_Spend",
    ascending=False,
    n=12
)

hdr("6) TOP EXAMPLES: POSITIVE COVERAGE BUT MISSING/ZERO 50TH TARGET")
m = (b["Contract_Total_Spend"] > 0) & (b["Benchmark_Coverage_Pct"] > 0) & (b["Target_Spend_50th"].isna() | (b["Target_Spend_50th"] <= 0))
print_df(
    b.loc[m].copy(),
    cols=[
        "Program","Contract_Number","Contract_Name","Contracted_Supplier",
        "Contract_Total_Spend","Benchmark_Coverage_Pct","Derived_Benchmarkable_Spend",
        "Target_Spend_50th","Flag_Coverage","Percentile_Bucket"
    ],
    sort_col="Contract_Total_Spend",
    ascending=False,
    n=12
)

hdr("7) TOP EXAMPLES: UOM / PPU EXTREMES")
m_low = (b["Contract_Total_Units"] > 0) & (b["Current_PPU"] > 0) & (b["Target50_PPU"].notna()) & (b["Target50_to_Current_PPU"] < 0.05)
print("Lowest ratios:")
print_df(
    b.loc[m_low].copy(),
    cols=[
        "Program","Contract_Number","Contract_Name","Contracted_Supplier",
        "Contract_Total_Spend","Contract_Total_Units","Current_PPU",
        "Target_Spend_50th","Target50_PPU","Target50_to_Current_PPU",
        "Benchmark_Coverage_Pct","Flag_Coverage"
    ],
    sort_col="Target50_to_Current_PPU",
    ascending=True,
    n=10
)

m_high = (b["Contract_Total_Units"] > 0) & (b["Current_PPU"] > 0) & (b["Target50_PPU"].notna()) & (b["Target50_to_Current_PPU"] > 20)
print("\nHighest ratios:")
print_df(
    b.loc[m_high].copy(),
    cols=[
        "Program","Contract_Number","Contract_Name","Contracted_Supplier",
        "Contract_Total_Spend","Contract_Total_Units","Current_PPU",
        "Target_Spend_50th","Target50_PPU","Target50_to_Current_PPU",
        "Benchmark_Coverage_Pct","Flag_Coverage"
    ],
    sort_col="Target50_to_Current_PPU",
    ascending=False,
    n=10
)

hdr("8) BEST_TIER_DESCRIPTION PATTERN CHECK FOR LOCAL/REGIONAL RESTRICTION HINTS")
# We cannot fully validate mapping restrictions from Tab B columns alone, but we can surface clue text
desc = b["best_tier_description"].fillna("").astype(str)
pattern_mask = desc.str.contains("LOCAL|REGIONAL|NATIONAL|PARTICIPATION|BRACKET", case=False, na=False)
sample_desc = (
    b.loc[pattern_mask, ["Program","Contract_Number","Contract_Name","best_tier_description"]]
    .drop_duplicates()
    .head(20)
)
print("Sample best-tier descriptions containing restriction cues:")
print(sample_desc.to_string(index=False))

print("\nDone. Send me the output and I will give you the skeptical director verdict.")