#!/usr/bin/env python3
"""Render the static PNG scatter plot for the README from the comparison CSV."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "processed" / "plateD002_input_comparison.csv"
OUT_PATH = ROOT / "figures" / "plateD002_gg_vs_neither_scatter.png"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

COLORS = {
    "Neither": "#2a78d6",     # categorical slot 1 (blue)
    "Index2_GG": "#1baf7a",   # categorical slot 2 (aqua)
}

rows = []
with CSV_PATH.open(newline="") as fh:
    rows = list(csv.DictReader(fh))

# One sample (IM-24-030-QCFP, GG_category=Neither) has Input=1 on both
# platforms -- a near-total dropout unrelated to the GG-index question
# (neither of its indexes starts GG). It skews the shared log-log axes by
# five orders of magnitude, so it is excluded from this plot and called out
# separately; it remains in data/processed/plateD002_input_comparison.csv.
DROPOUT_FLOOR = 100
plotted_rows = [
    r for r in rows
    if int(r["Input_Run131_MiSeq"]) >= DROPOUT_FLOOR
    and int(r["Input_NextSeq001_NextSeq"]) >= DROPOUT_FLOOR
]
excluded_rows = [r for r in rows if r not in plotted_rows]
rows = plotted_rows

fig, ax = plt.subplots(figsize=(7, 6), dpi=150)
fig.patch.set_facecolor("#fcfcfb")
ax.set_facecolor("#fcfcfb")

CAT_TITLES = {"Neither": "Neither index starts GG", "Index2_GG": "Index2 (i5) starts GG"}
for cat in ["Neither", "Index2_GG"]:
    cat_rows = [r for r in rows if r["GG_category"] == cat]
    xs = [int(r["Input_Run131_MiSeq"]) for r in cat_rows]
    ys = [int(r["Input_NextSeq001_NextSeq"]) for r in cat_rows]
    ax.scatter(
        xs, ys, s=64, color=COLORS[cat], label=f"{CAT_TITLES[cat]} (n={len(cat_rows)})",
        edgecolors="#fcfcfb", linewidths=1.5, zorder=3,
    )

all_vals = [int(r["Input_Run131_MiSeq"]) for r in rows] + [int(r["Input_NextSeq001_NextSeq"]) for r in rows]
lo, hi = min(all_vals) * 0.7, max(all_vals) * 1.3
ax.plot([lo, hi], [lo, hi], color="#898781", linestyle="-", linewidth=1, zorder=1, label="y = x (equal Input reads)")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))

ax.set_xlabel("Input reads — Run131 (MiSeq)", color="#0b0b0b")
ax.set_ylabel("Input reads — NextSeq001 (NextSeq)", color="#0b0b0b")
ax.set_title("PlateD002 / Dual003 — Input reads by platform, colored by GG-index status", color="#0b0b0b", fontsize=11)

ax.grid(True, which="both", color="#e1e0d9", linewidth=0.6, zorder=0)
for spine in ax.spines.values():
    spine.set_color("#c3c2b7")
ax.tick_params(colors="#52514e")

legend = ax.legend(loc="upper left", frameon=False, fontsize=9)
for text in legend.get_texts():
    text.set_color("#0b0b0b")

if excluded_rows:
    names = ", ".join(r["Sample_ID"] for r in excluded_rows)
    fig.text(
        0.5, 0.005,
        f"Not shown (Input < {DROPOUT_FLOOR} reads on one or both platforms, likely complete dropout): {names}",
        ha="center", fontsize=7.5, color="#898781",
    )

fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT_PATH, facecolor=fig.get_facecolor())
print(f"Wrote {OUT_PATH}")
