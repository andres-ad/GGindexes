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
# 9=Index2 seq for MiSeq/HiSeq 2000-2500 (Workflow A, forward strand),
# 10=Index2 seq for MiniSeq/NextSeq/HiSeq 3000-4000 (Workflow B, reverse
# complement -- this is the 2-channel-chemistry orientation).
i7, i5_fwd, i5_rc = {}, {}, {}
for r in data:
    if len(r) < 11:
        continue
    i7.setdefault(r[6], r[7])
    i5_fwd.setdefault(r[8], r[9])
    i5_rc.setdefault(r[8], r[10])


def gg_stats(d):
    n = len(d)
    gg = [k for k, v in d.items() if v.startswith("GG")]
    return n, len(gg), gg


n_i7, gg_i7, gg_i7_ids = gg_stats(i7)
n_i5f, gg_i5f, gg_i5f_ids = gg_stats(i5_fwd)
n_i5r, gg_i5r, gg_i5r_ids = gg_stats(i5_rc)

summary_csv = OUT / "catalog_gg_summary.csv"
with summary_csv.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Index_role", "Orientation", "n_unique_oligos", "n_starting_GG", "pct_starting_GG"])
    w.writerow(["Index1 (i7)", "as sequenced (all instruments)", n_i7, gg_i7, round(100 * gg_i7 / n_i7, 2)])
    w.writerow(["Index2 (i5)", "MiSeq, HiSeq 2000/2500 (Workflow A, forward strand)", n_i5f, gg_i5f, round(100 * gg_i5f / n_i5f, 2)])
    w.writerow(["Index2 (i5)", "MiniSeq, NextSeq, HiSeq 3000/4000 (Workflow B, reverse complement)", n_i5r, gg_i5r, round(100 * gg_i5r / n_i5r, 2)])
print(f"Wrote {summary_csv}")

# The orientation-flip detail: does GG-start status survive reverse-complementing?
detail_csv = OUT / "catalog_i5_gg_orientation_detail.csv"
with detail_csv.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Index2_ID", "seq_MiSeq_workflowA", "starts_GG_MiSeq", "seq_NextSeq_workflowB", "starts_GG_NextSeq"])
    for k in sorted(i5_fwd):
        f, rc = i5_fwd[k], i5_rc[k]
        if f.startswith("GG") or rc.startswith("GG"):
            w.writerow([k, f, f.startswith("GG"), rc, rc.startswith("GG")])
print(f"Wrote {detail_csv}")

print(f"\nIndex1 (i7): {n_i7} unique oligos, {gg_i7} start with GG ({100*gg_i7/n_i7:.1f}%)")
print(f"Index2 (i5), MiSeq/HiSeq2000-2500 orientation: {n_i5f} unique oligos, {gg_i5f} start with GG ({100*gg_i5f/n_i5f:.1f}%)")
print(f"Index2 (i5), NextSeq/MiniSeq/HiSeq3000-4000 orientation: {n_i5r} unique oligos, {gg_i5r} start with GG ({100*gg_i5r/n_i5r:.1f}%)")
