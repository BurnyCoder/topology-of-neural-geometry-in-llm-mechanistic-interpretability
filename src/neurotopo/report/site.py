"""`run.py site`: the GitHub Pages explorer (docs/index.html + docs/data/*.json), built from results/.

Global context: an interactive page to inspect, for each of the 44 clouds, the top-3 PCA points (coloured by
concept or by the cohomology coordinate theta_B), the fitted shape, the loop B used for steering, the alpha
persistence diagram with the design-matched null threshold, and the Method A / Method B invariants and
travel-around-the-hole statistics. A second page, docs/worked_example.html, renders docs/worked_example.md (the
step-by-step worked example on the toy cloud of experiments/toy_example.py) with live plots of that toy: balls
growing with r next to the persistence diagram, the null distribution, and the concepts around the hole.
plotly.js and marked are loaded from their CDNs; everything else is static.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import _clean, read_json
from neurotopo.report.figures import group_of, short
from neurotopo.steering import loops

PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Topology of neural geometry - explorer</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
body{font-family:system-ui,sans-serif;margin:0;display:flex;height:100vh;color:#222;background:#fff}
#side{width:250px;overflow:auto;border-right:1px solid #ddd;padding:8px;font-size:13px}
#side h3{margin:10px 0 4px;font-size:13px;color:#555}
#side a{display:block;padding:2px 4px;cursor:pointer;color:#30638e;text-decoration:none}
#side a.sel{background:#e0ecf4}
#main{flex:1;display:flex;flex-direction:column}
#plots{display:flex;flex:1}
#cloud{flex:3}#pd{flex:2}
#info{height:34%;overflow:auto;border-top:1px solid #ddd;padding:8px 12px;font-size:13px}
table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:2px 6px}
.ctl{padding:6px 12px;font-size:13px}
</style></head><body>
<div id="side"><b>Topology of neural geometry</b><br><small>Exact topology of fitted shapes (Method A), persistent
homology (Method B) and travel around the hole. <a href="https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability">GitHub</a>
<a href="worked_example.html">Worked example: how the loop and ring test works, step by step</a></small>
<div id="list"></div></div>
<div id="main"><div class="ctl">colour by: <select id="colour"><option value="concept">concept</option>
<option value="theta">theta_B (cohomology coordinate)</option></select>
<label><input type="checkbox" id="showshape" checked> fitted shape</label>
<label><input type="checkbox" id="showloop" checked> loop B</label></div>
<div id="plots"><div id="cloud"></div><div id="pd"></div></div><div id="info"></div></div>
<script>
let manifest, cur;
const fmt = v => (v === null || v === undefined) ? "-" : (typeof v === "number" ? (Number.isInteger(v) ? String(v) : (Math.abs(v) < 1e-3 && v !== 0 ? v.toExponential(1) : v.toFixed(3))) : v);
fetch("data/manifest.json").then(r => r.json()).then(m => { manifest = m; const L = document.getElementById("list");
  for (const [g, ids] of Object.entries(m)) { const h = document.createElement("h3"); h.textContent = g; L.appendChild(h);
    for (const it of ids) { const a = document.createElement("a"); a.textContent = it.label; a.onclick = () => load(it.id, a); L.appendChild(a); } }
  load(Object.values(m)[0][0].id, L.querySelector("a")); });
function load(id, el) { document.querySelectorAll("#side a").forEach(a => a.classList.remove("sel")); if (el) el.classList.add("sel");
  fetch("data/" + id + ".json").then(r => r.json()).then(d => { cur = d; draw(); }); }
["colour", "showshape", "showloop"].forEach(i => document.getElementById(i).onchange = () => draw());
function draw() { const d = cur, P = d.points, byTheta = document.getElementById("colour").value === "theta" && d.theta;
  const col = byTheta ? d.theta : d.colour, tr = [{type: "scatter3d", mode: "markers", x: P.map(p => p[0]), y: P.map(p => p[1]), z: P.map(p => p[2]),
    text: d.labels, marker: {size: 3, color: col, colorscale: d.cyclic || byTheta ? "Twilight" : "Viridis"}, name: "points"}];
  if (document.getElementById("showshape").checked && d.shape) tr.push({type: "scatter3d", mode: "markers", x: d.shape.map(p => p[0]), y: d.shape.map(p => p[1]), z: d.shape.map(p => p[2]), marker: {size: 1.5, color: "#999"}, name: "fitted " + d.family});
  if (document.getElementById("showloop").checked && d.loop) tr.push({type: "scatter3d", mode: "lines", x: d.loop.map(p => p[0]), y: d.loop.map(p => p[1]), z: d.loop.map(p => p[2]), line: {width: 6, color: "#d1495b"}, name: "loop B"});
  Plotly.react("cloud", tr, {margin: {l: 0, r: 0, t: 30, b: 0}, title: {text: d.id, font: {size: 13}}, showlegend: true});
  const pd = [], mx = Math.max(1e-3, ...d.h1.flat(), ...d.h2.flat());
  pd.push({x: d.h1.map(b => b[0]), y: d.h1.map(b => b[1]), mode: "markers", name: "H1", marker: {size: 6}});
  pd.push({x: d.h2.map(b => b[0]), y: d.h2.map(b => b[1]), mode: "markers", name: "H2", marker: {symbol: "triangle-up", size: 7}});
  pd.push({x: [0, mx], y: [0, mx], mode: "lines", line: {color: "#999"}, name: "diagonal"});
  if (d.q95_pi1) pd.push({x: [0, mx / d.q95_pi1], y: [0, mx], mode: "lines", line: {color: "red", dash: "dot"}, name: "H1 null q95 (pi)"});
  Plotly.react("pd", pd, {margin: {l: 45, r: 10, t: 30, b: 40}, title: {text: "alpha persistence (radius units)", font: {size: 12}},
    xaxis: {title: "birth"}, yaxis: {title: "death"}});
  let h = "<table><tr><th></th><th>Method A (fitted " + d.family + ")</th><th>Method B (persistent homology)</th></tr>";
  for (const [k, a, b] of d.rows) h += "<tr><td>" + k + "</td><td>" + fmt(a) + "</td><td>" + fmt(b) + "</td></tr>";
  h += "</table><p>" + (d.notes || "") + "</p>"; document.getElementById("info").innerHTML = h; }
</script></body></html>
"""

WORKED = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Worked example - topology of neural geometry</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<style>
body{font-family:system-ui,sans-serif;margin:0;color:#222;background:#fff;line-height:1.55}
header{padding:8px 16px;border-bottom:1px solid #ddd;font-size:14px}
header a{color:#30638e;margin-right:16px;text-decoration:none}
main{max-width:920px;margin:0 auto;padding:8px 20px 60px}
main img{max-width:100%}
table{border-collapse:collapse;margin:8px 0}td,th{border:1px solid #ddd;padding:3px 8px}
code{background:#f3f3f3;padding:0 3px;border-radius:3px}
#toy-widget{border:1px solid #ddd;border-radius:8px;padding:12px 14px;margin:16px 0}
.row{display:flex;flex-wrap:wrap;gap:8px}.row>div{flex:1 1 400px;height:380px}
.ctl{display:flex;flex-wrap:wrap;align-items:center;gap:10px;font-size:14px;margin:6px 0}
.ctl button{font-size:13px;padding:3px 10px}
#w-status{font-size:14px;margin:4px 0 8px;min-height:3em}
</style></head><body>
<header><a href="index.html">&larr; Explorer of the 44 clouds</a>
<a href="https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability">GitHub</a></header>
<main id="doc">Loading...</main>
<script>
// The text is docs/worked_example.md (generated by run.py report); numbers and arrays are results/toy/summary.json.
const REPO = "https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability/blob/main/";
const PAL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"];   // matplotlib tab10, as in fig_toy
const fin = v => (v === "inf" ? Infinity : v);                                                  // JSON stores infinite deaths as "inf"
Promise.all([fetch("worked_example.md").then(r => r.text()), fetch("data/worked_example.json").then(r => r.json())])
  .then(([md, toy]) => { const main = document.getElementById("doc"); main.innerHTML = marked.parse(md);
    main.querySelectorAll("a[href]").forEach(a => { const h = a.getAttribute("href");        // repo-relative links -> GitHub
      if (h.startsWith("../")) a.href = REPO + h.slice(3);
      else if (/^[\w-]+\.md(#.*)?$/.test(h)) a.href = REPO + "docs/" + h; });
    widget(document.getElementById("toy-widget"), toy); });
function widget(el, toy) {
  const N = toy.numbers, D = toy.data, P = D.points, C = D.concept, H1 = D.h1, top = 1.1, cfg = {displayModeBar: false};
  el.innerHTML = '<b>Try it: grow the balls</b> (drag a box on the cloud to zoom into one concept\'s triangle; double-click to reset)' +
    '<div class="ctl"><label for="w-r">radius r</label><input type="range" id="w-r" min="0" max="1.2" step="0.0005" value="0.2" style="flex:1"><span id="w-rv" style="min-width:4em"></span></div>' +
    '<div class="ctl" id="w-jump">jump to:</div><div id="w-status"></div>' +
    '<div class="row"><div id="w-cloud"></div><div id="w-pd"></div></div>' +
    '<p><b>The null:</b> the largest loop persistence ratio in each cluster-centre null cloud, against the toy cloud.</p><div id="w-null" style="height:300px"></div>' +
    '<p><b>Around the hole:</b> the concepts\' mean angles of the hole coordinate &theta;<sub>B</sub>, joined in weekday order.</p>' +
    '<div class="ctl"><button id="w-meas">measured &theta;<sub>B</sub></button><button id="w-twice">counter-example: around twice</button><span id="w-trav"></span></div>' +
    '<div id="w-circle" style="height:360px"></div>';
  Plotly.newPlot("w-cloud", [{x: P.map(p => p[0]), y: P.map(p => p[1]), mode: "markers", type: "scatter", text: C.map(c => D.names[c]),
    hoverinfo: "text", marker: {size: 7, color: C.map(c => PAL[c]), line: {width: 0.5, color: "#333"}}}],
    {margin: {l: 5, r: 5, t: 30, b: 5}, title: {text: "balls of radius r around the 21 points", font: {size: 13}}, showlegend: false,
     xaxis: {range: [-1.45, 1.45], visible: false}, yaxis: {range: [-1.45, 1.45], scaleanchor: "x", visible: false}}, cfg);
  Plotly.newPlot("w-pd", [{x: [0, top], y: [0, top], mode: "lines", line: {color: "#999"}, name: "diagonal (π = 1)"},
    {x: [0, top / N.null_q95], y: [0, top], mode: "lines", line: {color: "#d1495b", dash: "dash"}, name: "null 95th pct. (π = " + N.null_q95.toFixed(2) + ")"},
    {x: H1.map(b => b[0]), y: H1.map(b => fin(b[1])), mode: "markers", marker: {size: 10}, name: "loops (red = alive at r)",
     text: H1.map(b => "born " + b[0].toFixed(4) + ", dies " + fin(b[1]).toFixed(4) + ", π = " + (fin(b[1]) / b[0]).toFixed(3)), hoverinfo: "text"}],
    {margin: {l: 50, r: 10, t: 30, b: 45}, title: {text: "loop (H1) persistence diagram", font: {size: 13}},
     xaxis: {title: "birth radius b", range: [0, top]}, yaxis: {title: "death radius d", range: [0, top], scaleanchor: "x"},
     legend: {x: 0.35, y: 0.08, font: {size: 11}}}, cfg);
  const s = document.getElementById("w-r");
  function draw(r) {
    document.getElementById("w-rv").textContent = r.toFixed(4);
    Plotly.relayout("w-cloud", {shapes: P.map((p, i) => ({type: "circle", xref: "x", yref: "y", x0: p[0] - r, x1: p[0] + r, y0: p[1] - r,
      y1: p[1] + r, fillcolor: PAL[C[i]], opacity: 0.16, line: {width: 0}}))});
    const alive = H1.map(b => b[0] <= r && r < fin(b[1]));                                     // a bar is alive on [birth, death)
    Plotly.restyle("w-pd", {"marker.color": [alive.map(a => (a ? "#d1495b" : "#555"))]}, [2]);
    const rr = Math.min(r, top), dash = {color: "#d1495b", dash: "dot", width: 1};
    Plotly.relayout("w-pd", {shapes: [{type: "line", x0: rr, x1: rr, y0: rr, y1: top, line: dash}, {type: "line", x0: 0, x1: rr, y0: rr, y1: rr, line: dash}]});
    const pieces = D.h0.filter(b => b[0] <= r && r < fin(b[1])).length, loops = alive.filter(Boolean).length;
    const ev = D.events.filter(e => e.r <= r).pop();
    let txt = pieces + (pieces === 1 ? " piece, " : " pieces, ") + loops + (loops === 1 ? " loop" : " loops") + " alive.";
    if (ev) txt += " Last change: at r = " + ev.r.toFixed(4) + ", " + ev.edges + " edges and " + ev.triangles + " triangles entered the alpha complex.";
    if (loops) txt += " Alive: " + [...new Set(H1.filter((b, i) => alive[i]).map(b => "born " + b[0].toFixed(4) + ", dies " + fin(b[1]).toFixed(4) +
      " (π = " + (fin(b[1]) / b[0]).toFixed(2) + ")"))].join("; ") + ".";
    document.getElementById("w-status").textContent = txt; }
  s.oninput = () => draw(+s.value);
  [["tiny loops alive", (N.tiny_b + N.tiny_d) / 2], ["7 blobs", (N.tiny_d + N.big_b) / 2], ["ring alive", (2 * N.big_b + N.big_d) / 3], ["ring filled", N.big_d + 0.05]]
    .forEach(([label, v]) => { const b = document.createElement("button"); b.textContent = label + " (r = " + v.toFixed(3) + ")";
      b.onclick = () => { s.value = v; draw(v); }; document.getElementById("w-jump").appendChild(b); });
  draw(+s.value);
  const nm = D.null_max, vline = (x, c, d) => ({type: "line", x0: x, x1: x, yref: "paper", y0: 0, y1: 1, line: {color: c, dash: d, width: 1.5}});
  Plotly.newPlot("w-null", [{x: nm, type: "histogram", xbins: {start: 1, end: Math.max(...nm, N.big_pi) + 0.1, size: 0.025}, marker: {color: "#bbb"}}],
    {margin: {l: 55, r: 10, t: 10, b: 45}, xaxis: {title: "largest loop π in a null cloud", range: [1, Math.max(...nm, N.big_pi) + 0.15]}, yaxis: {title: "null clouds (of " + N.null_m + ")"},
     shapes: [vline(N.null_q95, "#d1495b", "dash"), vline(N.big_pi, "#222", "solid")],
     annotations: [{x: N.null_q95, yref: "paper", y: 0.95, text: " 95th pct. " + N.null_q95.toFixed(2), showarrow: false, xanchor: "left"},
                   {x: N.big_pi, yref: "paper", y: 0.95, text: "toy " + N.big_pi.toFixed(2) + ", p = " + N.null_p.toFixed(3) + " ", showarrow: false, xanchor: "right"}]}, cfg);
  function circle(twice) {
    const tc = D.concept_theta.map(t => (twice ? 2 * t : t)), xs = tc.map(Math.cos), ys = tc.map(Math.sin), k = [...Array(101).keys()];
    Plotly.react("w-circle", [{x: k.map(i => Math.cos(i * Math.PI / 50)), y: k.map(i => Math.sin(i * Math.PI / 50)), mode: "lines", line: {color: "#ccc"}, hoverinfo: "skip"},
      {x: [...xs, xs[0]], y: [...ys, ys[0]], mode: "lines", line: {color: "#555", width: 1}, hoverinfo: "skip"},
      {x: xs.map(v => 1.18 * v), y: ys.map(v => 1.18 * v), mode: "text", text: D.names, hoverinfo: "skip"},
      {x: xs, y: ys, mode: "markers", marker: {size: 13, color: PAL, line: {width: 0.5, color: "#333"}}, text: D.names, hoverinfo: "text"}],
      {margin: {l: 5, r: 5, t: 5, b: 5}, showlegend: false, xaxis: {range: [-1.5, 1.5], visible: false}, yaxis: {range: [-1.5, 1.5], scaleanchor: "x", visible: false}}, cfg);
    document.getElementById("w-trav").textContent = twice ? "R = " + N.twice_R.toFixed(3) + ", winding " + N.twice_w + ": fails"
      : "R = " + N.R.toFixed(3) + ", p = " + N.p_align.toFixed(4) + ", winding " + N.w + ": goes around once"; }
  document.getElementById("w-meas").onclick = () => circle(false);
  document.getElementById("w-twice").onclick = () => circle(true);
  circle(false); }
</script></body></html>
"""


def worked_example(docs) -> None:
    """docs/worked_example.html and docs/data/worked_example.json from results/toy/summary.json (run.py toy).
    The page renders docs/worked_example.md client-side, so its text is not duplicated here."""
    src = config.path("results") / "toy" / "summary.json"
    if not src.exists():
        return
    (docs / "data" / "worked_example.json").write_text(json.dumps(read_json(src)), encoding="utf-8", newline=chr(10))
    (docs / "worked_example.html").write_text(WORKED, encoding="utf-8", newline=chr(10))


def run() -> None:
    docs = config.ROOT / "docs"
    out = docs / "data"
    out.mkdir(parents=True, exist_ok=True)
    (docs / ".nojekyll").write_text("", encoding="utf-8", newline=chr(10))
    worked_example(docs)
    res = config.path("results")
    topo = pd.read_csv(res / "exp0" / "real_topology.csv").set_index("id")
    inv = pd.read_csv(res / "exp2" / "invariants.csv").set_index("id") if (res / "exp2" / "invariants.csv").exists() else None
    mb = read_json(res / "exp3" / "method_b.json") if (res / "exp3" / "method_b.json").exists() else {}
    th = np.load(res / "exp3" / "theta_B.npz") if (res / "exp3" / "theta_B.npz").exists() else {}
    manifest = {"cyclic concepts": [], "colours": [], "ordinal concepts": [], "controls": [], "other": []}
    names = {"cyclic": "cyclic concepts", "colours": "colours", "ordinal": "ordinal concepts", "control": "controls",
             "other": "other"}
    for did in source.dataset_ids():
        c = realdata.cloud(did)
        y = c["y"]
        viz = source.load_viz(did)
        try:
            con = source.concepts(did, c["labels"], n_bins=12)
            colour, cyclic = con.index.tolist(), group_of(did) in ("cyclic", "colours")
        except ValueError:
            colour, cyclic = [0] * len(y), False
        theta = th[did].tolist() if hasattr(th, "files") and did in th.files else None
        loop = None
        if theta is not None:
            lp = loops.loop_from_coordinate(y, np.asarray(theta), n_bins=24)
            loop = lp(np.linspace(0, 2 * np.pi, 200)).tolist()
        dg = realdata.alpha(did)
        t = topo.loc[did]
        rows = [["Betti (b0,b1,b2)", f"({t['b0']},{t['b1']},{t['b2']})",
                 f"({inv.loc[did, 'b0_rc']},{inv.loc[did, 'b1_rc']},{inv.loc[did, 'b2_rc']}) at r_c" if inv is not None else None],
                ["Euler characteristic", int(t["chi"]), int(inv.loc[did, "chi_rc"]) if inv is not None else None],
                ["genus", t["genus"] if pd.notna(t["genus"]) else "-", inv.loc[did, "genus_rc"] if inv is not None and pd.notna(inv.loc[did, "genus_rc"]) else "-"],
                ["homotopy class", t["homotopy"], inv.loc[did, "homotopy_rc"] if inv is not None else None],
                ["margin ratio rho_A / top H1 pi", float(t["rho_A"]), float(inv.loc[did, "top_pi1"]) if inv is not None else None],
                ["resolvable / loop p (MC)", bool(t["resolvable"]), float(inv.loc[did, "p_top_loop"]) if inv is not None else None]]
        rec = mb.get(did, {}).get("records3", [])
        notes = "; ".join(f"theta_B vs {r['variable']}: R={r['R']:.3f}, p={r['p']:.2g}, winding={r['winding']}" for r in rec)
        scale = c["frame"]["scale"]
        d = {"id": did, "family": t["family"], "points": np.round(y, 4).tolist(), "labels": c["labels"], "colour": colour,
             "cyclic": cyclic, "theta": theta, "loop": loop, "shape": np.round(viz["shape"] / scale, 4).tolist(),
             "h1": np.round(dg[1], 5).tolist(), "h2": np.round(dg[2], 5).tolist(),
             "q95_pi1": float(inv.loc[did, "null_q95_pi1"]) if inv is not None else None, "rows": rows, "notes": notes}
        (out / f"{did}.json").write_text(json.dumps(_clean(d)), encoding="utf-8", newline=chr(10))
        manifest[names[group_of(did)]].append({"id": did, "label": f"{short(did)} ({t['family']})"})
    (out / "manifest.json").write_text(json.dumps({k: v for k, v in manifest.items() if v}), encoding="utf-8", newline=chr(10))
    (docs / "index.html").write_text(PAGE, encoding="utf-8", newline=chr(10))
