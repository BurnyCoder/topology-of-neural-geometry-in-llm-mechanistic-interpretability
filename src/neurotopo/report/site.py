"""`run.py site`: the GitHub Pages explorer (docs/index.html + docs/data/*.json), built from results/.

Global context: an interactive page to inspect, for each of the 44 clouds, the top-3 PCA points (coloured by
concept or by the cohomology coordinate theta_B), the fitted shape, the loop B used for steering, the alpha
persistence diagram with the design-matched null threshold, and the Method A / Method B invariants and
travel-around-the-hole statistics. plotly.js is loaded from its CDN; everything else is static.
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
body{font-family:system-ui,sans-serif;margin:0;display:flex;height:100vh;color:#222}
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
homology (Method B) and travel around the hole. <a href="https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability">GitHub</a></small>
<div id="list"></div></div>
<div id="main"><div class="ctl">colour by: <select id="colour"><option value="concept">concept</option>
<option value="theta">theta_B (cohomology coordinate)</option></select>
<label><input type="checkbox" id="showshape" checked> fitted shape</label>
<label><input type="checkbox" id="showloop" checked> loop B</label></div>
<div id="plots"><div id="cloud"></div><div id="pd"></div></div><div id="info"></div></div>
<script>
let manifest, cur;
const fmt = v => (v === null || v === undefined) ? "-" : (typeof v === "number" ? (Math.abs(v) < 1e-3 && v !== 0 ? v.toExponential(1) : v.toFixed(3)) : v);
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


def run() -> None:
    docs = config.ROOT / "docs"
    out = docs / "data"
    out.mkdir(parents=True, exist_ok=True)
    (docs / ".nojekyll").write_text("", encoding="utf-8")
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
        (out / f"{did}.json").write_text(json.dumps(_clean(d)), encoding="utf-8")
        manifest[names[group_of(did)]].append({"id": did, "label": f"{short(did)} ({t['family']})"})
    (out / "manifest.json").write_text(json.dumps({k: v for k, v in manifest.items() if v}), encoding="utf-8")
    (docs / "index.html").write_text(PAGE, encoding="utf-8")
