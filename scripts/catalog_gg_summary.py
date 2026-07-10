#!/usr/bin/env python3
"""Summarize GG-start prevalence across the full CZB master index catalog
(all available 12bp TruSeq indexes, not just the ones used on PlateD002).

Usage: python3 scripts/catalog_gg_summary.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "CZB_Master_Index_Catalog.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

with CATALOG.open(newline="") as fh:
    rows = list(csv.reader(fh))
header, data = rows[0], rows[1:]

# Columns (0-indexed): 6=Index1_ID, 7=Index1, 8=Index2_ID,
# 9=Index2 sequence (Workflow A).
i7, i5 = {}, {}
for r in data:
    if len(r) < 10:
        continue
    i7.setdefault(r[6], r[7])
    i5.setdefault(r[8], r[9])


def gg_stats(d):
    n = len(d)
    gg = [k for k, v in d.items() if v.startswith("GG")]
    return n, len(gg), gg


n_i7, gg_i7, gg_i7_ids = gg_stats(i7)
n_i5, gg_i5, gg_i5_ids = gg_stats(i5)

summary_csv = OUT / "catalog_gg_summary.csv"
with summary_csv.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Index_role", "n_unique_oligos", "n_starting_GG", "pct_starting_GG"])
    w.writerow(["Index1 (i7)", n_i7, gg_i7, round(100 * gg_i7 / n_i7, 2)])
    w.writerow(["Index2 (i5)", n_i5, gg_i5, round(100 * gg_i5 / n_i5, 2)])
print(f"Wrote {summary_csv}")

print(f"\nIndex1 (i7): {n_i7} unique oligos, {gg_i7} start with GG ({100*gg_i7/n_i7:.1f}%)")
print(f"Index2 (i5): {n_i5} unique oligos, {gg_i5} start with GG ({100*gg_i5/n_i5:.1f}%)")
