"""
Generate: GPO Spend Landscape by Service Line — horizontal stacked bar chart
Output:   gpo_spend_landscape.png (same directory)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import os

# ── data (recommended central estimates, $B) ──────────────────────────
labels   = ["Clinical",  "Non-Clinical", "Pharma",  "Food"]
values   = [54.9,        52.2,           18.5,      1.9]       # midpoints ≈ $128B
ranges   = ["$52B–$57B", "$50B–$54B",    "$18B–$19B","~$2B"]
colors   = ["#2563EB",   "#0EA5E9",      "#8B5CF6", "#F59E0B"]  # blue, sky, purple, amber
total    = sum(values)  # ~127.5, close to $128B rec

# ── figure + axes ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 3.2))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── draw stacked bar ──────────────────────────────────────────────────
bar_height = 0.55
left = 0
rects = []
for val, color in zip(values, colors):
    r = ax.barh(0, val, left=left, height=bar_height, color=color,
                edgecolor="white", linewidth=1.5)
    rects.append((left, val))
    left += val

# ── segment labels (inside each segment) ──────────────────────────────
for i, (start, val) in enumerate(rects):
    cx = start + val / 2
    # Only label inside if segment is wide enough
    if val > 8:
        ax.text(cx, 0.02, labels[i], ha="center", va="center",
                fontsize=11, fontweight="bold", color="white")
        ax.text(cx, -0.14, ranges[i], ha="center", va="center",
                fontsize=9, color="white", alpha=0.92)
    elif val > 3:
        ax.text(cx, 0.02, labels[i], ha="center", va="center",
                fontsize=9.5, fontweight="bold", color="white")
        ax.text(cx, -0.14, ranges[i], ha="center", va="center",
                fontsize=7.5, color="white", alpha=0.92)
    else:
        # Food segment — label outside to the right
        ax.annotate(f"{labels[i]}\n{ranges[i]}", xy=(start + val, 0),
                    xytext=(start + val + 2.5, 0.35),
                    fontsize=8, ha="left", va="center", color=colors[i],
                    fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=colors[i],
                                    lw=0.8, connectionstyle="arc3,rad=-0.15"))

# ── divider line between C+NC and Pharma+Food ────────────────────────
cnc_total = values[0] + values[1]           # ~107.1
ax.axvline(cnc_total, color="#64748B", ls="--", lw=1.0, ymin=0.08, ymax=0.92)

# ── bracket annotations above the bar ────────────────────────────────
bracket_y = 0.42
ax.annotate("", xy=(0, bracket_y), xytext=(cnc_total, bracket_y),
            arrowprops=dict(arrowstyle="|-|,widthA=0.3,widthB=0.3",
                            color="#2563EB", lw=1.2))
ax.text(cnc_total / 2, bracket_y + 0.08,
        f"Supply Analytics data — ready for on/off/non-contract analysis  ({cnc_total/total*100:.0f}%)",
        ha="center", va="bottom", fontsize=9, color="#1E40AF", fontstyle="italic")

ax.annotate("", xy=(cnc_total, bracket_y), xytext=(total, bracket_y),
            arrowprops=dict(arrowstyle="|-|,widthA=0.3,widthB=0.3",
                            color="#7C3AED", lw=1.2))
ax.text(cnc_total + (total - cnc_total) / 2, bracket_y + 0.08,
        f"Wholesaler / distributor\ntracings needed  ({(total-cnc_total)/total*100:.0f}%)",
        ha="center", va="bottom", fontsize=8.5, color="#6D28D9", fontstyle="italic")

# ── total callout to the right ────────────────────────────────────────
ax.text(total + 2, 0, f"${total/1:.0f}B\ntotal", ha="left", va="center",
        fontsize=13, fontweight="bold", color="#1E293B")
ax.text(total + 2, -0.28, "($122B – $132B range)", ha="left", va="center",
        fontsize=8.5, color="#64748B")

# ── title ─────────────────────────────────────────────────────────────
ax.set_title("Estimated Premier GPO Non-Labor Purchasing by Service Line",
             fontsize=14, fontweight="bold", color="#0F172A", pad=38, loc="left")
ax.text(0, 1.02, "~1,775 acute-care hospital facilities  ·  224K staffed beds  ·  CY2025",
        transform=ax.transAxes, fontsize=9, color="#64748B", va="bottom")

# ── cleanup axes ──────────────────────────────────────────────────────
ax.set_xlim(-1, total + 18)
ax.set_ylim(-0.55, 0.85)
ax.set_yticks([])
ax.set_xticks([])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), "gpo_spend_landscape.png")
fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved → {out_path}")
plt.close()
