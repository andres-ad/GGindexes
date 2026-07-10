#!/usr/bin/env python3
"""Render the interactive HTML scatter-plot artifact from the comparison CSV."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "processed" / "plateD002_input_comparison.csv"
OUT_PATH = ROOT / "figures" / "plateD002_gg_vs_neither.html"

with CSV_PATH.open(newline="") as fh:
    rows = list(csv.DictReader(fh))

points = []
for r in rows:
    points.append({
        "id": r["Sample_ID"],
        "index1": r["Index"],
        "index2": r["Index2"],
        "cat": r["GG_category"],
        "type": r["Sample_type"],
        "x": int(r["Input_Run131_MiSeq"]),
        "y": int(r["Input_NextSeq001_NextSeq"]),
        "ratio": round(int(r["Input_NextSeq001_NextSeq"]) / int(r["Input_Run131_MiSeq"]), 3)
                 if int(r["Input_Run131_MiSeq"]) else None,
    })

DATA_JSON = json.dumps(points)

HTML = """<!doctype html>
<title>PlateD002 GG-index Input read comparison</title>
<style>
  :root {
    --surface-1: #fcfcfb;
    --page: #f9f9f7;
    --text-primary: #0b0b0b;
    --text-secondary: #52514e;
    --text-muted: #898781;
    --gridline: #e1e0d9;
    --baseline: #c3c2b7;
    --border: rgba(11,11,11,0.10);
    --series-neither: #2a78d6;
    --series-gg: #1baf7a;
    --refline: #898781;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --surface-1: #1a1a19;
      --page: #0d0d0d;
      --text-primary: #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted: #898781;
      --gridline: #2c2c2a;
      --baseline: #383835;
      --border: rgba(255,255,255,0.10);
      --series-neither: #3987e5;
      --series-gg: #199e70;
      --refline: #6b6a64;
    }
  }
  :root[data-theme="light"] {
    --surface-1: #fcfcfb; --page: #f9f9f7; --text-primary: #0b0b0b; --text-secondary: #52514e;
    --text-muted: #898781; --gridline: #e1e0d9; --baseline: #c3c2b7; --border: rgba(11,11,11,0.10);
    --series-neither: #2a78d6; --series-gg: #1baf7a; --refline: #898781;
  }
  :root[data-theme="dark"] {
    --surface-1: #1a1a19; --page: #0d0d0d; --text-primary: #ffffff; --text-secondary: #c3c2b7;
    --text-muted: #898781; --gridline: #2c2c2a; --baseline: #383835; --border: rgba(255,255,255,0.10);
    --series-neither: #3987e5; --series-gg: #199e70; --refline: #6b6a64;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--page); color: var(--text-primary);
    font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
    padding: 32px 16px 64px;
  }
  .wrap { max-width: 880px; margin: 0 auto; }
  h1 { font-size: 18px; margin: 0 0 4px; }
  p.sub { color: var(--text-secondary); margin: 0 0 20px; font-size: 13px; }
  .card {
    background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px 20px 12px;
  }
  .toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; gap: 12px; flex-wrap: wrap; }
  .legend { display: flex; gap: 18px; flex-wrap: wrap; }
  .legend-item { display: flex; align-items: center; gap: 7px; font-size: 12.5px; color: var(--text-primary); }
  .swatch { width: 10px; height: 10px; border-radius: 50%; flex: none; }
  .swatch.neither { background: var(--series-neither); }
  .swatch.gg { background: var(--series-gg); }
  .swatch.ref { width: 14px; height: 0; border-top: 1px solid var(--refline); border-radius: 0; }
  button.toggle {
    font: inherit; font-size: 12.5px; color: var(--text-primary); background: transparent;
    border: 1px solid var(--border); border-radius: 6px; padding: 5px 10px; cursor: pointer;
  }
  button.toggle:hover { background: var(--gridline); }
  svg { width: 100%; height: auto; display: block; overflow: visible; }
  .axis-label { fill: var(--text-secondary); font-size: 12px; }
  .tick-label { fill: var(--text-muted); font-size: 10.5px; }
  .gridline { stroke: var(--gridline); stroke-width: 1; }
  .baseline { stroke: var(--baseline); stroke-width: 1; }
  .refline { stroke: var(--refline); stroke-width: 1; }
  .dot { stroke: var(--surface-1); stroke-width: 1.5; }
  .hit { fill: transparent; cursor: pointer; }
  .dot.dim { opacity: 0.25; }
  .tooltip {
    position: fixed; pointer-events: none; z-index: 10; background: var(--surface-1);
    border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px;
    font-size: 12px; color: var(--text-secondary); box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    opacity: 0; transform: translate(-9999px, -9999px); transition: opacity 0.08s;
    max-width: 240px;
  }
  .tooltip.show { opacity: 1; }
  .tooltip .val { color: var(--text-primary); font-weight: 600; }
  .tooltip .row { display: flex; justify-content: space-between; gap: 14px; }
  .tooltip .key { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; font-size: 11.5px; }
  .tooltip .key-line { width: 10px; height: 2px; }
  .foot { color: var(--text-muted); font-size: 11.5px; margin-top: 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  th, td { text-align: right; padding: 6px 8px; border-bottom: 1px solid var(--gridline); font-variant-numeric: tabular-nums; }
  th:first-child, td:first-child { text-align: left; font-variant-numeric: normal; }
  th { color: var(--text-secondary); font-weight: 600; position: sticky; top: 0; background: var(--surface-1); }
  td { color: var(--text-primary); }
  .table-wrap { max-height: 480px; overflow-y: auto; display: none; }
  .cat-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
</style>
<div class="wrap">
  <h1>PlateD002 / Dual003 — Input reads by platform, colored by GG-index status</h1>
  <p class="sub">Run131 (MiSeq) vs NextSeq001 (NextSeq) · same 88 matched samples · Input-stage reads (log-log) · hover a point for details</p>
  <div class="card">
    <div class="toolbar">
      <div class="legend" id="legend"></div>
      <button class="toggle" id="toggleView">Show table view</button>
    </div>
    <svg id="chart" viewBox="0 0 820 600"></svg>
    <div class="table-wrap" id="tableWrap"></div>
    <p class="foot">Excluded from the plot: the 6 negative controls (near-zero reads by design — a QC pass, not a performance signal) and IM-24-030-QCFP (Input = 1 read on both platforms, a likely complete dropout, index category "Neither" — unrelated to GG status). All remain in the table view and in <code>data/processed/plateD002_input_comparison.csv</code>.</p>
  </div>
</div>
<div class="tooltip" id="tooltip"></div>
<script>
const DATA = __DATA_JSON__;
const DROPOUT_FLOOR = 100;
const plotted = DATA.filter(d => d.type !== "negative_control" && d.x >= DROPOUT_FLOOR && d.y >= DROPOUT_FLOOR);

const CAT_META = {
  Neither: { label: "Neither index starts GG", varName: "--series-neither", cls: "neither" },
  Index2_GG: { label: "Index2 (i5) starts GG", varName: "--series-gg", cls: "gg" },
};

// ---- Legend ----
const legend = document.getElementById("legend");
["Neither", "Index2_GG"].forEach(cat => {
  const n = plotted.filter(d => d.cat === cat).length;
  const item = document.createElement("div");
  item.className = "legend-item";
  const sw = document.createElement("span");
  sw.className = "swatch " + CAT_META[cat].cls;
  item.appendChild(sw);
  const txt = document.createElement("span");
  txt.textContent = CAT_META[cat].label + " (n=" + n + ")";
  item.appendChild(txt);
  legend.appendChild(item);
});
const refItem = document.createElement("div");
refItem.className = "legend-item";
const refSw = document.createElement("span");
refSw.className = "swatch ref";
refItem.appendChild(refSw);
const refTxt = document.createElement("span");
refTxt.textContent = "y = x (equal Input reads)";
refItem.appendChild(refTxt);
legend.appendChild(refItem);

// ---- Chart geometry ----
const svg = document.getElementById("chart");
const W = 820, H = 600;
const M = { top: 16, right: 24, bottom: 46, left: 64 };
const plotW = W - M.left - M.right;
const plotH = H - M.top - M.bottom;

const allVals = plotted.flatMap(d => [d.x, d.y]);
const lo = Math.pow(10, Math.floor(Math.log10(Math.min(...allVals)) * 10) / 10 - 0.05);
const hi = Math.pow(10, Math.ceil(Math.log10(Math.max(...allVals)) * 10) / 10 + 0.05);

function xScale(v) { return M.left + (Math.log10(v) - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo)) * plotW; }
function yScale(v) { return M.top + plotH - (Math.log10(v) - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo)) * plotH; }

function niceTicks(lo, hi) {
  const ticks = [];
  const startExp = Math.floor(Math.log10(lo));
  const endExp = Math.ceil(Math.log10(hi));
  for (let e = startExp; e <= endExp; e++) {
    for (const m of [1, 2, 5]) {
      const v = m * Math.pow(10, e);
      if (v >= lo && v <= hi) ticks.push(v);
    }
  }
  return ticks;
}
function fmt(v) {
  return v >= 1000 ? Math.round(v).toLocaleString() : String(Math.round(v));
}

const ns = "http://www.w3.org/2000/svg";
function el(tag, attrs) {
  const e = document.createElementNS(ns, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  return e;
}

const ticks = niceTicks(lo, hi);
ticks.forEach(t => {
  const x = xScale(t), y = yScale(t);
  svg.appendChild(el("line", { class: "gridline", x1: x, x2: x, y1: M.top, y2: M.top + plotH }));
  svg.appendChild(el("line", { class: "gridline", x1: M.left, x2: M.left + plotW, y1: y, y2: y }));
  const xt = el("text", { class: "tick-label", x, y: M.top + plotH + 16, "text-anchor": "middle" });
  xt.textContent = fmt(t);
  svg.appendChild(xt);
  const yt = el("text", { class: "tick-label", x: M.left - 8, y: y + 3, "text-anchor": "end" });
  yt.textContent = fmt(t);
  svg.appendChild(yt);
});
svg.appendChild(el("line", { class: "baseline", x1: M.left, x2: M.left, y1: M.top, y2: M.top + plotH }));
svg.appendChild(el("line", { class: "baseline", x1: M.left, x2: M.left + plotW, y1: M.top + plotH, y2: M.top + plotH }));

const xlab = el("text", { class: "axis-label", x: M.left + plotW / 2, y: H - 6, "text-anchor": "middle" });
xlab.textContent = "Input reads — Run131 (MiSeq)";
svg.appendChild(xlab);
const ylab = el("text", { class: "axis-label", x: -(M.top + plotH / 2), y: 16, "text-anchor": "middle", transform: "rotate(-90)" });
ylab.textContent = "Input reads — NextSeq001 (NextSeq)";
svg.appendChild(ylab);

svg.appendChild(el("line", {
  class: "refline", x1: xScale(lo), y1: yScale(lo), x2: xScale(hi), y2: yScale(hi),
}));

const tooltip = document.getElementById("tooltip");
plotted.forEach(d => {
  const cx = xScale(d.x), cy = yScale(d.y);
  const color = "var(" + CAT_META[d.cat].varName + ")";
  const hit = el("circle", { class: "hit", cx, cy, r: 14 });
  const dot = el("circle", { class: "dot", cx, cy, r: 5, fill: color });
  const group = el("g", {});
  group.appendChild(hit);
  group.appendChild(dot);
  function show(evt) {
    dot.setAttribute("r", 6.5);
    tooltip.innerHTML = "";
    const key = document.createElement("div");
    key.className = "key";
    const line = document.createElement("span");
    line.className = "key-line";
    line.style.background = color;
    key.appendChild(line);
    const kt = document.createElement("span");
    kt.textContent = d.id;
    key.appendChild(kt);
    tooltip.appendChild(key);

    const rows = [
      ["Category", CAT_META[d.cat].label],
      ["Run131 (MiSeq) Input", d.x.toLocaleString()],
      ["NextSeq001 Input", d.y.toLocaleString()],
      ["Ratio (NextSeq / MiSeq)", d.ratio],
    ];
    rows.forEach(([k, v]) => {
      const row = document.createElement("div");
      row.className = "row";
      const kEl = document.createElement("span");
      kEl.textContent = k;
      const vEl = document.createElement("span");
      vEl.className = "val";
      vEl.textContent = v;
      row.appendChild(kEl);
      row.appendChild(vEl);
      tooltip.appendChild(row);
    });
    tooltip.classList.add("show");
    const rect = svg.getBoundingClientRect();
    const scale = rect.width / W;
    let left = rect.left + cx * scale + 14;
    let top = rect.top + cy * scale - 10;
    if (left + 240 > window.innerWidth) left = rect.left + cx * scale - 254;
    tooltip.style.transform = "translate(" + left + "px," + top + "px)";
  }
  function hide() {
    dot.setAttribute("r", 5);
    tooltip.classList.remove("show");
  }
  hit.addEventListener("pointerenter", show);
  hit.addEventListener("pointermove", show);
  hit.addEventListener("pointerleave", hide);
  hit.setAttribute("tabindex", "0");
  hit.addEventListener("focus", show);
  hit.addEventListener("blur", hide);
  svg.appendChild(group);
});

// ---- Table view ----
const tableWrap = document.getElementById("tableWrap");
const table = document.createElement("table");
const thead = document.createElement("thead");
thead.innerHTML = "";
const headRow = document.createElement("tr");
["Sample", "Category", "Input — Run131 (MiSeq)", "Input — NextSeq001", "Ratio (NextSeq/MiSeq)"].forEach(h => {
  const th = document.createElement("th");
  th.textContent = h;
  headRow.appendChild(th);
});
thead.appendChild(headRow);
table.appendChild(thead);
const tbody = document.createElement("tbody");
DATA.forEach(d => {
  const tr = document.createElement("tr");
  const tdId = document.createElement("td");
  tdId.textContent = d.id;
  tr.appendChild(tdId);
  const tdCat = document.createElement("td");
  const catDot = document.createElement("span");
  catDot.className = "cat-dot";
  catDot.style.background = "var(" + CAT_META[d.cat].varName + ")";
  tdCat.appendChild(catDot);
  tdCat.appendChild(document.createTextNode(CAT_META[d.cat].label));
  tr.appendChild(tdCat);
  const tdX = document.createElement("td");
  tdX.textContent = d.x.toLocaleString();
  tr.appendChild(tdX);
  const tdY = document.createElement("td");
  tdY.textContent = d.y.toLocaleString();
  tr.appendChild(tdY);
  const tdR = document.createElement("td");
  tdR.textContent = d.ratio;
  tr.appendChild(tdR);
  tbody.appendChild(tr);
});
table.appendChild(tbody);
tableWrap.appendChild(table);

const toggleBtn = document.getElementById("toggleView");
let showingTable = false;
toggleBtn.addEventListener("click", () => {
  showingTable = !showingTable;
  svg.style.display = showingTable ? "none" : "block";
  tableWrap.style.display = showingTable ? "block" : "none";
  toggleBtn.textContent = showingTable ? "Show chart view" : "Show table view";
});
</script>
"""

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(HTML.replace("__DATA_JSON__", DATA_JSON))
print(f"Wrote {OUT_PATH}")
