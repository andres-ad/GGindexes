# GG-Index Performance Review — PlateD002 / Dual003

## Background & purpose

Paragon's bioinformatics team reviewed the index sequences for the 12
12-bp indexes plates and identified **104 indexes**
that violate Illumina's requirement that index reads must not begin with
two "G" bases in the first two cycles. Per Illumina, a "GG"-leading index
generates no signal in cycles 1–2, which can cause failed demultiplexing or
a rejected run:

- https://knowledge.illumina.com/instrumentation/general/instrumentation-general-reference_material-list/000001241
- https://support-docs.illumina.com/IN/NextSeq_550-500/Content/IN/IndexingConsiderations_fNS_fMN.htm

Because these plates will ship as product, Paragon's QMS requires a risk
assessment. Illumina's own documentation classifies "GG"-leading indexes as
a risk. However, UCSF and collaborators have been using indexes with this
property in production for several years, so their run history is a
relevant source of real-world evidence on whether this risk has actually
materialized as a performance problem (low signal, cluster-registration
failures, repeated failed samples on specific index combinations).

This analysis is a first look at that evidence: one batch
(**PlateD002**, indexed with **Dual003**) that was run at CPHL on both a MiSeq
(**Run131**, 150PE reads with v3 reagents kit) and a NextSeq (**NextSeq001**,on NextSeq 1000 with P2 reagents kit
), compared sample-for-sample.

## Notes

- **2026-07-10:** `data/sample_coverage_Run131.txt` was replaced with a
  corrected export. The original file had the 2 positive controls under
  the wrong micronic ID (`8073801003`, vs `8073801533` used everywhere else),
  which made them fail to match the index sheet, and used hyphens instead
  of underscores in control names (`Negative-Control-1` vs
  `Negative_Control_1`). The corrected file fixes the lot ID and the
  matching logic was updated to normalize `-`/`_` in sample IDs, so **all
  96/96 plate samples now match in both runs** (previously 88/96). This
  added one more `Index2 (i5) starts GG` sample — the `1K_Positive_Control`
  standard — bringing that group to **n=6**, and added the 6 negative
  controls and the 2nd positive control to the `Neither` pool. See
  Methodology and Results below for how negative controls are handled.

## Data

All source files are in [`data/`](data):

| File | Description |
|---|---|
| `PlateD002_CZB_Dual_Indexes.csv` | Index sheet for PlateD002/Dual003 — 96 samples (incl. controls), `Index` (i7) + `Index2` (i5), CZB TruSeq 12bp indexes. |
| `sample_coverage_Run131.txt` | Per-sample read counts by pipeline stage (`Input`, `No Dimers`, `Amplicons`, `OutputDada2`, `OutputPostprocessing`) for the MiSeq run. 144 samples in the file (this run pooled more than just PlateD002). |
| `sample_coverage_NextSeq001.txt` | Same schema, for the NextSeq run. 624 samples in the file. |

Derived outputs are in [`data/processed/`](data/processed):

- `plateD002_input_comparison.csv` — one row per matched sample: index
  sequences, GG category, `Input` reads on each platform, and the
  NextSeq/MiSeq fold-change.
- `summary_stats.csv` — n / mean / median / stdev of `Input` reads per GG
  category per platform, and the mean NextSeq/MiSeq ratio per group.
- `lowest_ratio_samples.csv` — the 8 samples with the lowest NextSeq/MiSeq
  `Input` ratio (excluding negative controls and the dropout, same
  population as `summary_stats.csv`).

## Methodology

1. **GG classification.** For each sample in the index sheet, `Index` (i7)
   and `Index2` (i5) are each checked for a "GG" prefix, giving one of
   `Index1_GG`, `Index2_GG`, `Both`, or `Neither`.

   Within PlateD002/Dual003, **only Index2 (i5)** ever starts with "GG"
   (6/96 samples); **no sample's Index1 (i7)** does. So this dataset only
   lets us compare **"Index2 (i5) starts GG"** vs **"Neither"** — it cannot
   speak to i7-GG or double-GG cases.

2. **Sample matching across runs.** Coverage files suffix each sample name
   with `_S<number>` (NextSeq001) or `_S<number>_L001` (Run131), and use
   `-` or `_` inconsistently in control names. Stripping the suffix and
   normalizing `-`/`_` before matching against the index sheet's
   `Sample_ID` gives **96/96 matches in both runs**.

3. **Sample type.** Each matched sample is tagged `biological`,
   `positive_control`, or `negative_control`. Positive controls are
   kept in the performance comparison. **Negative controls are excluded**
   from the plot and summary statistics: near-zero `Input` reads is their
   correct, expected outcome (no template loaded), not a performance
   signal, and including them would make the `Neither` group look like it
   underperforms for a reason that has nothing to do with GG-index status.
   They remain in `plateD002_input_comparison.csv` for the record.

4. **Metric.** `Reads` at `Stage == "Input"` — the earliest pipeline stage,
   i.e. reads successfully assigned to the sample by demultiplexing, before
   any dimer/amplicon filtering. This is the most direct readout of a
   demux / cluster-registration / signal problem, which is what the GG-index
   risk is about.

5. **One further exclusion.** Sample `IM-24-030-QCFP` (`Neither` category,
   biological) has `Input = 1` read on **both** platforms — a near-total
   dropout unrelated to GG-index status (neither of its indexes starts GG).
   It's excluded from the plot and from the summary statistics below so it
   doesn't dominate the "Neither" group's mean/stdev, but it remains in
   `plateD002_input_comparison.csv` and in the table view of the chart.

Reproduce with:

```
pip install pandas matplotlib   # matplotlib only needed for the static PNG
python3 scripts/build_comparison.py     # writes data/processed/*.csv
python3 scripts/make_static_figure.py   # writes figures/*.png
python3 scripts/render_artifact.py      # writes figures/*.html
```

## Results

| GG category | n | Mean Input — Run131 (MiSeq) | Mean Input — NextSeq001 | Mean ratio (NextSeq / MiSeq) |
|---|---|---|---|---|
| Index2 (i5) starts GG | 6 | 180,666 | 287,587 | **1.60** |
| Neither (excl. negative controls & dropout) | 83 | 153,218 | 241,465 | **1.58** |

(Full detail in `data/processed/summary_stats.csv`; per-sample values in
`data/processed/plateD002_input_comparison.csv`.)

The 6 individual `Index2 (i5) starts GG` samples behind that mean — 5
biological samples plus the `1K_Positive_Control` standard, which also
carries a GG(i5) index on this plate:

| Sample | Type | Index2 (i5) primer sequence | Input — Run131 (MiSeq) | Input — NextSeq001 | Ratio (NextSeq / MiSeq) |
|---|---|---|---|---|---|
| IM-24-030-HLUN | biological | `GGAATGAGTCGT` | 122,059 | 189,942 | 1.556 |
| IM-24-030-SBPN | biological | `GGAGAATGCTTG` | 100,178 | 168,147 | 1.678 |
| IM-24-030-TMSA | biological | `GGCTAAGAGAAC` | 249,034 | 382,420 | 1.536 |
| IM-24-030-ZCCV | biological | `GGAAGAGACACT` | 247,820 | 412,307 | 1.664 |
| IM-24-044-DGQK | biological | `GGTACTGACACT` | 215,822 | 340,252 | 1.577 |
| 1K_Positive_Control_8073801533_2 | positive control | `GGTTCTTCCACT` | 149,080 | 232,456 | 1.559 |
| **Mean** | — | — | **180,666** | **287,587** | **1.595** |

All 6 ratios cluster tightly (1.54–1.68), matching the 83-sample `Neither`
group's mean ratio of 1.58 — no individual GG(i5) sample, biological or
control, stands out as an underperformer relative to the others.

![Scatter plot of Input reads, Run131 (MiSeq) vs NextSeq001 (NextSeq), colored by GG-index status](figures/plateD002_gg_vs_neither_scatter.png)

**Interactive version** (hover for per-sample detail, toggle to a full
data table): see `figures/plateD002_gg_vs_neither.html`, or the version
published for this session:
https://claude.ai/code/artifact/b91f10a5-b492-44c0-bf9c-a2527649b0d9

### Reading the chart

- Both platforms give more `Input` reads on NextSeq than MiSeq for
  essentially every sample (all points sit above the y=x line) — expected,
  since NextSeq001 and Run131 are different runs with different total
  loading/depth, not a GG effect.
- The 6 `Index2 (i5) starts GG` samples (green) fall **inside the same
  cloud** as the 83 `Neither` samples (blue), not below it. Their mean
  NextSeq/MiSeq ratio (1.60) is essentially identical to — and if anything
  slightly higher than — the `Neither` group's (1.58).
- No sample in either group shows the signature of a demux/cluster-
  registration failure (near-zero `Input` reads) except the one excluded
  dropout, which is a `Neither`-category biological sample, not a GG one
  (negative controls are near-zero by design and are excluded separately).

### Lowest-performing samples (worst 8 by NextSeq/MiSeq ratio)

The flip side of "do GG samples underperform" is "do the actual
underperformers turn out to be GG samples." They don't — the 8 samples
with the lowest NextSeq/MiSeq `Input` ratio in this batch are **all
`Neither`**, none of them GG-flagged on either index:

| Rank | Sample | Index (i7) | Index2 (i5) | Input — Run131 (MiSeq) | Input — NextSeq001 | Ratio (NextSeq / MiSeq) |
|---|---|---|---|---|---|---|
| 1 | IM-24-030-FTFR | `CAAGCATTCTCC` | `CAGACATCGAAC` | 144,431 | 185,681 | 1.286 |
| 2 | IM-24-036-JXJB | `ACGAGAACCAAC` | `CCTATAGCTCGT` | 78,678 | 102,007 | 1.297 |
| 3 | IM-24-030-RKXW | `CTCAACGAGCAT` | `AGACGACAACTC` | 191,414 | 252,080 | 1.317 |
| 4 | IM-24-044-KXJF | `TCACCTCCAACA` | `GCATACACAGCA` | 270,592 | 358,541 | 1.325 |
| 5 | IM-24-044-PXTH | `GTTCTCTGGAGT` | `ACTCGAAGACTC` | 171,776 | 228,293 | 1.329 |
| 6 | IM-24-036-GXMV | `ACGAGCTATAGG` | `CCAGATCTGAAC` | 97,509 | 129,860 | 1.332 |
| 7 | IM-24-030-XKPN | `ACGACTCATTCC` | `ACACACGTCACT` | 202,395 | 273,798 | 1.353 |
| 8 | IM-24-030-GRDR | `AGTGACGTGTGT` | `TAGGACTCGAAC` | 165,187 | 233,254 | 1.412 |

For reference, the lowest ratio among the 6 GG(i5) samples is 1.536
(`IM-24-030-TMSA`) — higher than every sample in this worst-8 table, and
that sample ranks 26th out of 89 by ratio (i.e. solidly mid-pack, not a
tail case). None of the GG(i5) samples rank in the bottom third of the
batch. (Full ranking: `data/processed/lowest_ratio_samples.csv` has the
worst 8; the complete per-sample ranking can be reproduced by sorting
`plateD002_input_comparison.csv` on `ratio_NextSeq_over_MiSeq`.)

### Interpretation

**For this one batch/run pair, we see no evidence that an i5 index
starting with "GG" reduced Input-stage read yield on the NextSeq relative
to the MiSeq**, or relative to non-GG samples on the same NextSeq run.

This should be weighed against real limitations, not treated as a
clearance:

- **n = 6** GG samples (5 biological + 1 positive control) is a very small
  group to draw a general conclusion from — a real but moderate effect
  could easily be invisible at this sample size.
- This plate has **no i7-GG or double-GG (`Both`) samples**, so this
  analysis is silent on those cases, which may behave differently (i7 is
  frequently the platform's primary/first-read index and can be more
  sensitive to a dark first two cycles depending on instrument and run
  recipe).
- Only **one plate** (PlateD002/Dual003) and **one MiSeq/NextSeq run
  pair** were examined. The other 11 flagged plates, and other
  instruments/run recipes in UCSF's history, are not yet covered.
- `Input` reads capture demux/cluster-registration success but not
  downstream data quality (e.g., elevated index-hopping or lower Q30 in
  cycles 1–2) — this analysis doesn't rule those out.

## Repository layout

```
data/
  PlateD002_CZB_Dual_Indexes.csv          # index sheet (source)
  sample_coverage_Run131.txt              # MiSeq coverage (source)
  sample_coverage_NextSeq001.txt          # NextSeq coverage (source)
  processed/
    plateD002_input_comparison.csv        # per-sample merged table
    summary_stats.csv                     # per-group summary stats
    lowest_ratio_samples.csv              # worst 8 by NextSeq/MiSeq ratio
scripts/
  build_comparison.py                     # builds data/processed/*.csv
  make_static_figure.py                   # builds the PNG in figures/
  render_artifact.py                      # builds the interactive HTML
figures/
  plateD002_gg_vs_neither_scatter.png
  plateD002_gg_vs_neither.html
```
