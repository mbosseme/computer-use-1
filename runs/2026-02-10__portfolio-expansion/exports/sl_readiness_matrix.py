"""
Generate: Service Line Readiness Matrix — volume × data-source status (bubble chart)
Output:   sl_readiness_matrix.png (same directory)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import os

# ── data ──────────────────────────────────────────────────────────────
#              name            midpoint($B)  readiness(0-10)  color
service_lines = [
    ("Clinical",       54.9,   8.5,  "#2563EB"),   # blue — SA data ready, dashboard exists
    ("Non-Clinical",   52.2,   7.0,  "#0EA5E9"),   # sky — SA data ready, dashboard extension needed
    ("Pharma",         18.5,   3.0,  "#8B5CF6"),   # purple — wholesaler tracings needed
    ("Food",            1.9,   2.0,  "#F59E0B"),   # amber — distributor tracings needed
]

names      = [s[0] for s in service_lines]
volumes    = np.array([s[1] for s in service_lines])
readiness  = np.array([s[2] for s in service_lines])
colors     = [s[3] for s in service_lines]
ranges     = ["$52B–$57B", "$50B–$54B", "$18B–$19B", "~$2B"]
statuses   = [
    "SA dashboard live\n(Jenny/Brian's team)",
    "SA data ready\nextend dashboard to NC",
    "Wholesaler tracings\nneeded",
    "Distributor tracings\nneeded",
]

# bubble sizes — scale so the largest bubble is visually prominent
bubble_scale = 45
sizes = volumes * bubble_scale

# ── figure ────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 7.5))
fig.patch.set_facecolor("white")
ax.set_facecolor("#FAFBFC")

# subtle quadrant shading
ax.axvspan(5.0, 10.5, ymin=0, ymax=1, color="#ECFDF5", alpha=0.45, zorder=0)
ax.axvspan(-0.5, 5.0, ymin=0, ymax=1, color="#FFF7ED", alpha=0.45, zorder=0)

# divider
ax.axvline(5.0, color="#CBD5E1", ls="--", lw=1.0, zorder=1)

# ── draw bubbles ──────────────────────────────────────────────────────
for i in range(len(names)):
    ax.scatter(readiness[i], volumes[i], s=sizes[i] * 18, c=colors[i],
               alpha=0.82, edgecolors="white", linewidths=2.5, zorder=3)

# ── labels on/near each bubble ────────────────────────────────────────
# Clinical — label inside (large bubble) -> WHITE text
ax.text(8.5, 56.5, "Clinical", ha="center", va="center",
        fontsize=13, fontweight="bold", color="white", zorder=4)
ax.text(8.5, 52.5, "$52B–$57B", ha="center", va="center",
        fontsize=10, color="white", alpha=1.0, zorder=4)
ax.text(8.5, 47.0, statuses[0], ha="center", va="top",
        fontsize=8.5, color="white", fontstyle="italic", zorder=4) # Status inside, white

# Non-Clinical — label inside -> WHITE text
ax.text(7.0, 56.0, "Non-\nClinical", ha="center", va="center",
        fontsize=12, fontweight="bold", color="white", zorder=4, linespacing=0.85)
ax.text(7.0, 52.0, "$50B–$54B", ha="center", va="center",
        fontsize=10, color="white", alpha=1.0, zorder=4)
ax.text(7.0, 46.5, statuses[1], ha="center", va="top",
        fontsize=8.5, color="white", fontstyle="italic", zorder=4) # Status inside, white

# Pharma — label to the side (medium bubble) -> Dark text
ax.annotate("Pharma\n$18B–$19B", xy=(3.0, 18.5), xytext=(4.3, 28),
            fontsize=10, fontweight="bold", ha="center", va="center",
            color="#5B21B6", zorder=4, # Darker purple for readability
            arrowprops=dict(arrowstyle="-", color="#7C3AED", lw=1.0))
ax.text(3.0, 8.0, statuses[2], ha="center", va="top",
        fontsize=8.5, color="#5B21B6", fontstyle="italic", zorder=4) # Below bubble, darker purple

# Food — label to the side (small bubble) -> Dark text
ax.annotate("Food\n~$2B", xy=(2.0, 1.9), xytext=(0.8, 10),
            fontsize=9.5, fontweight="bold", ha="center", va="center",
            color="#B45309", zorder=4, # Darker amber
            arrowprops=dict(arrowstyle="-", color="#D97706", lw=1.0))
ax.text(2.0, -2.5, statuses[3], ha="center", va="top",
        fontsize=8.5, color="#B45309", fontstyle="italic", zorder=4) # Below bubble, darker amber

# ── axes styling ──────────────────────────────────────────────────────
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-8, 68)

ax.set_xlabel("Data Source for On/Off/Non-Contract Analysis", fontsize=11, fontweight="bold",
              color="#374151", labelpad=10)
ax.set_ylabel("Estimated Total Non-Labor Expense ($B)", fontsize=11, fontweight="bold",
              color="#374151", labelpad=10)

# Custom x-axis labels
ax.set_xticks([1.5, 5.0, 8.0])
ax.set_xticklabels(["Sales tracings", "", "Health system ERP data\nin Supply Analytics"],
                   fontsize=10, color="#475569", fontweight="medium")

# y-axis
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}B"))
ax.set_yticks([0, 10, 20, 30, 40, 50, 60])
ax.tick_params(axis="y", labelsize=9, colors="#64748B")

# Arrow along x-axis
ax.annotate("", xy=(10.2, -5.5), xytext=(0.5, -5.5),
            arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=1.5),
            annotation_clip=False)

# grid
ax.yaxis.grid(True, color="#E2E8F0", lw=0.6, zorder=0)
ax.xaxis.grid(False)

for spine in ax.spines.values():
    spine.set_visible(False)

# ── title ─────────────────────────────────────────────────────────────
ax.set_title("Estimated GPO Member Health System Non-Labor Expense by Service Line",
             fontsize=16, fontweight="bold", color="#0F172A", pad=40, loc="left")
ax.text(0, 1.06, "Based on data source required for deep analysis  ·  CY2025  ·  1,775 GPO facilities",
        transform=ax.transAxes, fontsize=10.5, color="#475569", va="bottom")
ax.text(0, 1.015, "Note: Excludes non-acute / continuum of care (not owned by health system). Does not consider health systems that are pharma and/or food program only.",
        transform=ax.transAxes, fontsize=9.5, color="#EF4444", va="bottom", fontstyle="italic") # Red disclaimer

# need this import for the formatter — already imported at top

plt.tight_layout()

out_path = os.path.join(os.path.dirname(__file__), "sl_readiness_matrix.png")
fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved → {out_path}")
plt.close()
