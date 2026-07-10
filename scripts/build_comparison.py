#!/usr/bin/env python3
"""Build the PlateD002 GG-index Input-read comparison between Run131 (MiSeq)
and NextSeq001 (NextSeq), and write summary stats.

Usage: python3 scripts/build_comparison.py
Reads from ../data, writes to ../data/processed relative to this file.
"""
import csv
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "processed"
OUT.mkdir(parents=True, exist_ok=True)

INDEX_CSV = DATA / "PlateD002_CZB_Dual_Indexes.csv"
RUN131_COV = DATA / "sample_coverage_Run131.txt"
NEXTSEQ_COV = DATA / "sample_coverage_NextSeq001.txt"

SUFFIX_RE = re.compile(r"_S\d+(_L\d+)?$")


def gg_category(index1: str, index2: str) -> str:
    g1 = index1.startswith("GG")
    g2 = index2.startswith("GG")
    if g1 and g2:
        return "Both"
    if g1:
        return "Index1_GG"
    if g2:
        return "Index2_GG"
    return "Neither"


def load_index_sheet():
    samples = {}
    with INDEX_CSV.open(newline="") as fh:
        for row in csv.DictReader(fh):
            sample_id = row["Sample_ID"]
            samples[sample_id] = {
                "Sample_ID": sample_id,
                "Index": row["Index"],
                "Index2": row["Index2"],
                "GG_category": gg_category(row["Index"], row["Index2"]),
            }
    return samples


def load_input_reads(path: Path) -> dict:
    reads = {}
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["Stage"] != "Input":
                continue
            base_id = SUFFIX_RE.sub("", row["SampleID"])
            reads[base_id] = int(row["Reads"])
    return reads


def main():
    samples = load_index_sheet()
    run131 = load_input_reads(RUN131_COV)
    nextseq = load_input_reads(NEXTSEQ_COV)

    merged_rows = []
    unmatched = []
    for sample_id, info in samples.items():
        r131 = run131.get(sample_id)
        nseq = nextseq.get(sample_id)
        if r131 is None or nseq is None:
            unmatched.append(sample_id)
            continue
        log2_fc = (nseq / r131) and __import__("math").log2(nseq / r131)
        merged_rows.append({
            **info,
            "Input_Run131_MiSeq": r131,
            "Input_NextSeq001_NextSeq": nseq,
            "log2_fold_change_NextSeq_over_MiSeq": round(log2_fc, 4),
        })

    merged_rows.sort(key=lambda r: (r["GG_category"], r["Sample_ID"]))

    comparison_csv = OUT / "plateD002_input_comparison.csv"
    with comparison_csv.open("w", newline="") as fh:
        fieldnames = [
            "Sample_ID", "Index", "Index2", "GG_category",
            "Input_Run131_MiSeq", "Input_NextSeq001_NextSeq",
            "log2_fold_change_NextSeq_over_MiSeq",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)

    # Summary stats per GG_category per run.
    # IM-24-030-QCFP (Neither) has Input=1 on both platforms -- a near-total
    # dropout unrelated to GG-index status -- and is excluded here so it
    # doesn't dominate the mean/stdev of its group. It stays in the
    # comparison CSV above.
    DROPOUT_FLOOR = 100
    stats_rows = [
        r for r in merged_rows
        if r["Input_Run131_MiSeq"] >= DROPOUT_FLOOR
        and r["Input_NextSeq001_NextSeq"] >= DROPOUT_FLOOR
    ]
    by_cat = {}
    for row in stats_rows:
        by_cat.setdefault(row["GG_category"], []).append(row)

    summary_csv = OUT / "summary_stats.csv"
    with summary_csv.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "GG_category", "n",
            "mean_Input_Run131_MiSeq", "median_Input_Run131_MiSeq",
            "stdev_Input_Run131_MiSeq",
            "mean_Input_NextSeq001", "median_Input_NextSeq001",
            "stdev_Input_NextSeq001",
            "mean_ratio_NextSeq_over_MiSeq",
        ])
        for cat, rows in sorted(by_cat.items()):
            r131_vals = [r["Input_Run131_MiSeq"] for r in rows]
            nseq_vals = [r["Input_NextSeq001_NextSeq"] for r in rows]
            ratios = [n / r for n, r in zip(nseq_vals, r131_vals)]
            writer.writerow([
                cat, len(rows),
                round(statistics.mean(r131_vals), 1),
                statistics.median(r131_vals),
                round(statistics.stdev(r131_vals), 1) if len(r131_vals) > 1 else "",
                round(statistics.mean(nseq_vals), 1),
                statistics.median(nseq_vals),
                round(statistics.stdev(nseq_vals), 1) if len(nseq_vals) > 1 else "",
                round(statistics.mean(ratios), 3),
            ])

    print(f"Matched samples: {len(merged_rows)} / {len(samples)}")
    print(f"Unmatched (excluded): {len(unmatched)} -> {sorted(unmatched)}")
    print(f"Wrote {comparison_csv}")
    print(f"Wrote {summary_csv}")


if __name__ == "__main__":
    main()
