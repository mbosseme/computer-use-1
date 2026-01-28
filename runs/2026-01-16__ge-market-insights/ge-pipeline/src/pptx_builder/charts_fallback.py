"""
charts_fallback.py — generate simple portfolio visuals when snapshot PNGs are missing.
"""
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def _safe_series(df: pd.DataFrame, key: str, default: float = 0.0) -> pd.Series:
    if key in df.columns:
        return df[key].fillna(default)
    return pd.Series([default] * len(df), index=df.index, dtype=float)


def render_histogram(df: pd.DataFrame, out_png: Path) -> None:
    values = df.get("delta_7_12")
    if values is None:
        values = pd.Series(dtype=float)
    values = values.dropna()
    if values.empty:
        # Seed with a zero bucket so chart renders
        values = pd.Series([0.0])

    fig, ax = plt.subplots(figsize=(6.5, 4), dpi=200)
    ax.hist(values, bins=20, color="#3f51b5", alpha=0.75, edgecolor="white")
    ax.set_xlabel("Δ7–12 (share lift, proportion)")
    ax.set_ylabel("Cohort count")
    ax.set_title("Portfolio lift distribution (fallback)", fontsize=14)
    ax.grid(axis="y", alpha=0.3, linestyle="--", linewidth=0.5)
    ax.tick_params(labelsize=10)
    ax.xaxis.label.set_size(12)
    ax.yaxis.label.set_size(12)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, transparent=True)
    plt.close(fig)


def render_bubble(df: pd.DataFrame, out_png: Path) -> None:
    x = _safe_series(df, "delta_7_12")
    y = _safe_series(df, "member_t0_total_spend_6m")
    size = _safe_series(df, "N_members", default=1.0).clip(lower=1.0)

    if len(df) == 0:
        # Populate with a benign placeholder point
        x = pd.Series([0.0])
        y = pd.Series([0.0])
        size = pd.Series([1.0])

    area = (size.astype(float) ** 0.5) * 20.0  # scale bubble size gently

    fig, ax = plt.subplots(figsize=(6.5, 4), dpi=200)
    scatter = ax.scatter(x, y, s=area, alpha=0.6, color="#009688", edgecolors="white", linewidth=0.5)
    ax.set_xlabel("Δ7–12 (share lift, proportion)")
    ax.set_ylabel("Member t₀ total spend (6m)")
    ax.set_title("Case-study sizing (fallback bubble)", fontsize=14)
    ax.axvline(0, color="#888888", linestyle="--", linewidth=0.6)
    ax.grid(alpha=0.3, linestyle="--", linewidth=0.5)
    ax.tick_params(labelsize=10)
    ax.xaxis.label.set_size(12)
    ax.yaxis.label.set_size(12)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, transparent=True)
    plt.close(fig)
