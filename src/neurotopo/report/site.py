"""`run.py site`: the GitHub Pages explorer (docs/index.html + docs/data/*.json), built from results/.

Global context: an interactive page to inspect, for each of the 44 clouds, the top-3 PCA points (coloured by
concept or by the cohomology coordinate theta_B), the fitted shape, the loop B used for steering, the alpha complex
at a radius r with a representative cycle of each loop and a shell of each void alive at r, the alpha persistence
diagram with the design-matched null thresholds (H1 and H2), and the Method A / Method B invariants and
travel-around-the-hole statistics. A second page, docs/worked_example.html, renders docs/worked_example.md (the
step-by-step worked example on the toy cloud of experiments/toy_example.py) with live plots of that toy: balls
growing with r next to the persistence diagram, the null distribution, and the concepts around the hole. A third,
docs/examples.html, replays the same steps on the six real clouds of the README's example figure (report/examples.py).
Every page has a "Method and terms" drawer that renders docs/glossary.md; "?" links open it at the term.
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
from neurotopo.report.examples import replay
from neurotopo.report.figures import group_of, short
from neurotopo.steering import loops

# Shared by all pages: the "Method and terms" drawer, which renders docs/glossary.md (each heading gets the id
# "g-<GitHub-style slug>", so a "?" link can open the drawer at that term), and the handling of markdown links.
SHARED_CSS = r"""<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<style>
#gloss{position:fixed;top:0;right:0;bottom:0;width:min(460px,92vw);overflow:auto;background:#fff;border-left:1px solid #ccc;
 box-shadow:-4px 0 12px rgba(0,0,0,.08);padding:0 16px 40px;font-size:14px;line-height:1.5;z-index:10;color:#222}
#gloss .gl-head{position:sticky;top:0;background:#fff;padding:10px 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center}
#gloss h1{font-size:18px}#gloss h2{font-size:16px;margin-top:22px}#gloss h3{font-size:14px;margin:16px 0 4px}
#gloss h3.flash{background:#fff3b0}#gloss a{color:#30638e}
#gloss h1,#gloss h2,#gloss h3{scroll-margin-top:52px}
a.q{display:inline-block;font-size:11px;line-height:14px;width:14px;height:14px;text-align:center;border-radius:7px;background:#e0ecf4;
 color:#30638e !important;text-decoration:none;margin-left:3px;cursor:pointer;padding:0 !important}
button.gl-btn{font-size:13px;padding:2px 10px;cursor:pointer}
</style>"""
DRAWER = r"""<aside id="gloss" hidden><div class="gl-head"><b>Method and terms</b><button class="gl-btn" onclick="closeGloss()">close</button></div>
<div id="gloss-body">Loading...</div></aside>"""
SHARED_JS = r"""<script>
const REPO = "https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability/blob/main/";
const slug = s => s.toLowerCase().trim().replace(/[^\w\- ]+/g, "").replace(/\s/g, "-");      // GitHub heading anchors
function fixLinks(root) {                                         // markdown links -> this site, the drawer or GitHub
  root.querySelectorAll("a[href]").forEach(a => { const h = a.getAttribute("href"), g = h.match(/^glossary\.md(?:#(.*))?$/);
    if (g) { a.href = "#"; a.onclick = e => { e.preventDefault(); term(g[1] || "method-and-terms"); }; }
    else if (h.startsWith("../")) a.href = REPO + h.slice(3);
    else if (/^worked_example\.md(#.*)?$/.test(h)) a.href = h.replace(".md", ".html");
    else if (/^[\w-]+\.md(#.*)?$/.test(h)) a.href = REPO + "docs/" + h; }); }
let glossReady = null;
function openGloss() { document.getElementById("gloss").hidden = false;
  glossReady = glossReady || fetch("glossary.md").then(r => r.text()).then(md => { const b = document.getElementById("gloss-body");
    b.innerHTML = marked.parse(md); b.querySelectorAll("h1, h2, h3").forEach(h => { h.id = "g-" + slug(h.textContent); }); fixLinks(b); });
  return glossReady; }
function closeGloss() { document.getElementById("gloss").hidden = true; }
function term(id) { openGloss().then(() => { const el = document.getElementById("g-" + id); if (!el) return;
  el.scrollIntoView({block: "start"}); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1500); }); }
const q = (id, name) => '<a class="q" href="#" title="' + (name || "What is this?") + '" onclick="term(\'' + id + '\'); return false">?</a>';
</script>"""

REPLAY_JS = r"""<script>
// Shared by the explorer and the examples page: replay persistent homology on a cloud. The radius slider is
// logarithmic (all clouds have RMS radius 1). At radius r the 3D view shows the alpha complex's edges and one
// representative cycle of every loop alive at r, in that loop's own colour (data from report/examples.replay); the
// explorer also draws the shell of every void alive at r as a translucent surface in that void's own colour.
const RMIN = 0.002, RMAX = 1.5, LN = Math.log(RMAX / RMIN);
const toR = t => RMIN * Math.exp(LN * t / 1000), toT = r => Math.round(1000 * Math.log(Math.max(r, RMIN) / RMIN) / LN);
const aliveAt = (d, r) => d.h1.map(b => b[0] <= r && r < b[1]);                             // alive on [birth, death)
const voidsAliveAt = (d, r) => d.h2.map(b => b[0] <= r && r < b[1]);                        // same rule for voids
const piecesAt = (d, r) => 1 + d.h0_deaths.filter(x => x > r).length;                       // one piece never dies
const crossXY = r => ({x: [r, r, null, RMIN, r], y: [r, RMAX, null, r, r]});
function edgeTrace(d, r) {                                                                   // edges are sorted by entry radius
  const P = d.points, X = [], Y = [], Z = []; let n = 0;
  while (n < d.edge_r.length && d.edge_r[n] <= r) n++;
  for (let k = 0; k < n; k++) { const [i, j] = d.edges[k]; X.push(P[i][0], P[j][0], null); Y.push(P[i][1], P[j][1], null); Z.push(P[i][2], P[j][2], null); }
  return {n, trace: {type: "scatter3d", mode: "lines", x: X, y: Y, z: Z, hoverinfo: "skip", showlegend: false,
    line: {color: "rgba(90,90,90,0.35)", width: 1.5}, name: "alpha edges"}}; }
function loopTraces(d, alive, only = null) {             // one closed cycle per alive loop, or only loop `only` if alive
  const P = d.points, out = [];
  alive.forEach((a, k) => { if (!a || (only !== null && k !== only)) return; const c = d.cycles[k].concat([d.cycles[k][0]]), b = d.h1[k];
    out.push({type: "scatter3d", mode: "lines", x: c.map(i => P[i][0]), y: c.map(i => P[i][1]), z: c.map(i => P[i][2]), showlegend: false,
      line: {color: d.loop_colour[k], width: only === null ? 7 : 12}, hoverinfo: "text", text: "loop born " + b[0].toFixed(4) + ", dies " + b[1].toFixed(4)}); });
  return out; }
function voidTraces(d, alive, only = null) {             // one translucent surface: the shells of the alive voids (or of `only`)
  const P = d.points, I = [], J = [], K = [], C = [];      // mesh3d triangles index into the cloud's points, coloured per face
  alive.forEach((a, k) => { if (!a || (only !== null && k !== only)) return;
    for (const [i, j, l] of d.shells[k]) { I.push(i); J.push(j); K.push(l); C.push(d.void_colour[k]); } });
  return I.length ? [{type: "mesh3d", x: P.map(p => p[0]), y: P.map(p => p[1]), z: P.map(p => p[2]), i: I, j: J, k: K, facecolor: C,
    opacity: only === null ? 0.3 : 0.45, flatshading: true, hoverinfo: "skip", showlegend: false, name: "void shells"}] : []; }
const holeMarker = (colour, alive, sel = null) => ({color: colour, opacity: alive.map((a, k) => (a || k === sel ? 1 : 0.2)),   // solid while alive,
  size: alive.map((a, k) => (k === sel ? 16 : a ? 10 : 5)), line: {color: "#000", width: alive.map((a, k) => (k === sel ? 2.5 : 0))}});   // ringed if picked
const loopMarker = (d, alive, sel = null) => holeMarker(d.loop_colour, alive, sel);
</script>"""

PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Topology of neural geometry - explorer</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
""" + SHARED_CSS + r"""
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
homology (Method B) and travel around the hole.
<a href="#" onclick="term('the-method-in-one-minute'); return false">What am I looking at? The method and all terms</a>
<a href="examples.html">How the six example results were made (animated)</a>
<a href="worked_example.html">Worked example: how the loop and ring test works, step by step</a>
<a href="https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability">GitHub</a></small>
<div id="list"></div></div>
<div id="main"><div class="ctl">colour by: <select id="colour"><option value="concept">concept</option>
<option value="theta">theta_B (cohomology coordinate)</option></select>
<a class="q" href="#" title="Concept / theta_B" onclick="term('theta_a-and-theta_b-hole-coordinates'); return false">?</a>
<label><input type="checkbox" id="showshape" checked> fitted shape</label><a class="q" href="#" title="Fitted shape" onclick="term('fitted-shape-13-families'); return false">?</a>
<label><input type="checkbox" id="showloop" checked> loop B</label><a class="q" href="#" title="Loop B" onclick="term('loop-b'); return false">?</a>
&nbsp;| right: persistence diagram<a class="q" href="#" title="Persistence diagram" onclick="term('persistence-diagram'); return false">?</a>,
red dotted line: null 95th percentile<a class="q" href="#" title="Null 95th percentile" onclick="term('null-95th-percentile-q95'); return false">?</a>
&nbsp;<button class="gl-btn" onclick="openGloss()">Method and terms</button></div>
<div class="ctl">radius r <input type="range" id="rr" min="0" max="1000" step="1" value="500" style="width:240px;vertical-align:middle">
<span id="rv"></span> <label><input type="checkbox" id="showcx" checked> alpha complex, loops and voids at r</label><a class="q" href="#"
title="Alpha complex" onclick="term('alpha-complex'); return false">?</a><a class="q" href="#" title="Representative loop"
onclick="term('representative-loop'); return false">?</a><a class="q" href="#" title="Representative void"
onclick="term('representative-void'); return false">?</a> <span id="rstat" style="color:#555"></span></div>
<div class="ctl">show <select id="onesel" style="max-width:430px"></select> <button class="gl-btn" id="prevl">previous</button>
<button class="gl-btn" id="nextl">next</button> <span style="color:#555">or click a loop's dot or a void's triangle in the persistence diagram.</span>
<span id="selinfo"></span></div>
<div id="plots"><div id="cloud"></div><div id="pd"></div></div><div id="info"></div></div>
""" + DRAWER + SHARED_JS + REPLAY_JS + r"""
<script>
const TERMS = {"Betti (b0,b1,b2)": [["betti-numbers", "Betti numbers"], ["characteristic-scale-r_c", "Characteristic scale r_c"]],
  "Euler characteristic": [["euler-characteristic", "Euler characteristic"]], "genus": [["genus", "Genus"]],
  "homotopy class": [["homotopy-class", "Homotopy class"]],
  "margin ratio rho_A / top H1 pi": [["margin-ratio-rho_a", "Margin ratio rho_A"], ["top-h1-pi", "Top H1 pi"]],
  "resolvable / loop p (MC)": [["resolvable", "Resolvable"], ["monte-carlo-p-value", "Monte Carlo p-value"]]};
let manifest, cur, sel = null, rExact = null, pdBound = false;   // sel: the one hole shown, {kind, k}, or null = all
const bars = (d, kind) => (kind === "loop" ? d.h1 : d.h2), colours = (d, kind) => (kind === "loop" ? d.loop_colour : d.void_colour);
const key = h => (h === null ? "" : h.kind[0] + h.k);               // dropdown value: "l0" = loop #1, "v2" = void #3
const unkey = v => (v === "" ? null : {kind: v[0] === "l" ? "loop" : "void", k: +v.slice(1)});
const holesAlive = (d, r) => [["loop", aliveAt(d, r)], ["void", voidsAliveAt(d, r)]]    // loops, then voids, most persistent first
  .flatMap(([kind, a]) => a.flatMap((x, k) => (x ? [{kind, k}] : [])));
const fmt = v => (v === null || v === undefined) ? "-" : (typeof v === "number" ? (Number.isInteger(v) ? String(v) : (Math.abs(v) < 1e-3 && v !== 0 ? v.toExponential(1) : v.toFixed(3))) : v);
fetch("data/manifest.json").then(r => r.json()).then(m => { manifest = m; const L = document.getElementById("list");
  for (const [g, ids] of Object.entries(m)) { const h = document.createElement("h3"); h.textContent = g; L.appendChild(h);
    for (const it of ids) { const a = document.createElement("a"); a.textContent = it.label; a.onclick = () => load(it.id, a); L.appendChild(a); } }
  load(Object.values(m)[0][0].id, L.querySelector("a")); });
function load(id, el) { document.querySelectorAll("#side a").forEach(a => a.classList.remove("sel")); if (el) el.classList.add("sel");
  fetch("data/" + id + ".json").then(r => r.json()).then(d => { cur = d; sel = null; rExact = null;   // start where the top hole is alive:
    const b = [d.h1[0], d.h2[0]].filter(Boolean).sort((u, v) => v[1] / v[0] - u[1] / u[0])[0];        // the loop or void with the larger pi
    if (b) document.getElementById("rr").value = toT(Math.sqrt(b[0] * b[1])); draw(); }); }
["colour", "showshape", "showloop", "showcx"].forEach(i => document.getElementById(i).onchange = () => draw());
document.getElementById("rr").oninput = () => { rExact = null; draw(); };
const radius = () => (rExact !== null ? rExact : toR(+document.getElementById("rr").value));
document.getElementById("onesel").onchange = e => { sel = unkey(e.target.value); draw(); };
function stepHole(dir) {                                   // previous / next among the loops and voids alive at r
  const on = holesAlive(cur, radius()); if (!on.length) return;
  const i = on.findIndex(h => key(h) === key(sel)); sel = i < 0 ? on[dir > 0 ? 0 : on.length - 1] : on[(i + dir + on.length) % on.length]; draw(); }
document.getElementById("prevl").onclick = () => stepHole(-1);
document.getElementById("nextl").onclick = () => stepHole(1);
function pickFromDiagram(ev) {                             // click a loop's dot or a void's triangle: show it alone, at a radius where it is alive
  const pt = ev.points[0], kind = pt && {[cur.loopCurve]: "loop", [cur.voidCurve]: "void"}[pt.curveNumber]; if (!kind) return;
  sel = {kind, k: pt.pointIndex}; const b = bars(cur, kind)[sel.k], r = radius();
  if (!(b[0] <= r && r < b[1])) { rExact = Math.sqrt(b[0] * b[1]); document.getElementById("rr").value = toT(rExact); }
  draw(); }
function draw() { const d = cur, P = d.points, byTheta = document.getElementById("colour").value === "theta" && d.theta;
  const r = radius(), alive = aliveAt(d, r), valive = voidsAliveAt(d, r);
  const ls = sel && sel.kind === "loop" ? sel.k : null, vs = sel && sel.kind === "void" ? sel.k : null;   // the picked loop / void
  const col = byTheta ? d.theta : d.colour, tr = [{type: "scatter3d", mode: "markers", x: P.map(p => p[0]), y: P.map(p => p[1]), z: P.map(p => p[2]),
    text: d.labels, marker: {size: 3, color: col, colorscale: d.cyclic || byTheta ? "Twilight" : "Viridis",
    opacity: sel === null ? 1 : 0.15}, name: "points"}];                    // a picked hole stays visible inside a dense cloud
  if (document.getElementById("showshape").checked && d.shape) tr.push({type: "scatter3d", mode: "markers", x: d.shape.map(p => p[0]), y: d.shape.map(p => p[1]), z: d.shape.map(p => p[2]), marker: {size: 1.5, color: "#999"}, name: "fitted " + d.family});
  if (document.getElementById("showloop").checked && d.loop) tr.push({type: "scatter3d", mode: "lines", x: d.loop.map(p => p[0]), y: d.loop.map(p => p[1]), z: d.loop.map(p => p[2]), line: {width: 6, color: "#d1495b"}, name: "loop B"});
  let ne = 0;
  if (document.getElementById("showcx").checked) { const ed = edgeTrace(d, r); ne = ed.n; tr.push(ed.trace);   // a picked hole is drawn alone
    if (vs === null) tr.push(...loopTraces(d, alive, ls));
    if (ls === null) tr.push(...voidTraces(d, valive, vs)); }
  Plotly.react("cloud", tr, {margin: {l: 0, r: 0, t: 30, b: 0}, title: {text: d.id, font: {size: 13}}, showlegend: true, uirevision: d.id});
  const ax = t => ({title: t, type: "log", range: [Math.log10(RMIN), Math.log10(RMAX)]}), pd = [];
  pd.push({x: [RMIN, RMAX], y: [RMIN, RMAX], mode: "lines", line: {color: "#999"}, name: "diagonal", hoverinfo: "skip"});
  if (d.q95_pi1) pd.push({x: [RMIN, RMAX / d.q95_pi1], y: [RMIN * d.q95_pi1, RMAX], mode: "lines", line: {color: "red", dash: "dot"}, name: "H1 null q95 (pi)", hoverinfo: "skip"});
  if (d.q95_pi2) pd.push({x: [RMIN, RMAX / d.q95_pi2], y: [RMIN * d.q95_pi2, RMAX], mode: "lines", line: {color: "#7b3294", dash: "dashdot", width: 1}, name: "H2 null q95 (pi)", hoverinfo: "skip"});
  if (d.connect_r) pd.push({x: [RMIN, RMAX], y: [d.connect_r, d.connect_r], mode: "lines", line: {color: "#555", dash: "dot", width: 1}, name: "connect radius", hoverinfo: "skip"});
  cur.loopCurve = pd.length;                                                  // which trace a click must hit to pick a loop
  const tip = b => "born " + b[0].toFixed(4) + ", dies " + b[1].toFixed(4) + ", pi = " + (b[1] / b[0]).toFixed(2);
  pd.push({x: d.h1.map(b => b[0]), y: d.h1.map(b => b[1]), mode: "markers", name: "H1 (loops, own colours)", marker: loopMarker(d, alive, ls), hoverinfo: "text",
    text: d.h1.map(b => "loop " + tip(b))});
  if (d.h1.length) pd.push({x: [d.h1[0][0]], y: [d.h1[0][1]], mode: "markers", marker: {size: 15, color: "rgba(0,0,0,0)", line: {color: "#000", width: 2}}, name: "most persistent loop", hoverinfo: "skip"});
  cur.voidCurve = pd.length;                                                  // which trace a click must hit to pick a void
  pd.push({x: d.h2.map(b => b[0]), y: d.h2.map(b => b[1]), mode: "markers", name: "H2 (voids, own colours)", hoverinfo: "text",
    marker: Object.assign(holeMarker(d.void_colour, valive, vs), {symbol: "triangle-up"}), text: d.h2.map(b => "void " + tip(b))});
  pd.push(Object.assign({mode: "lines", line: {color: "#333", dash: "dot", width: 1}, name: "radius r", hoverinfo: "skip"}, crossXY(r)));
  Plotly.react("pd", pd, {margin: {l: 50, r: 10, t: 30, b: 40}, title: {text: "persistence diagram (log axes)", font: {size: 12}},
    xaxis: ax("birth"), yaxis: ax("death"), legend: {x: 0.98, y: 0.02, xanchor: "right", yanchor: "bottom", font: {size: 10}}, uirevision: d.id})   // below the diagonal: always empty
    .then(gd => { if (!pdBound) { gd.on("plotly_click", pickFromDiagram); pdBound = true; } });
  const S = document.getElementById("onesel"), on = holesAlive(d, r), label = h => { const b = bars(d, h.kind)[h.k];
    return h.kind + " #" + (h.k + 1) + ": pi = " + (b[1] / b[0]).toFixed(2) + " (born " + b[0].toFixed(4) + ", dies " + b[1].toFixed(4) + ")"; };
  const loops = alive.filter(Boolean).length, voids = valive.filter(Boolean).length, isOn = sel !== null && on.some(h => key(h) === key(sel));
  const count = (n, w) => n + " " + w + (n === 1 ? "" : "s");
  S.innerHTML = "";                                                            // all loops, then voids, alive at r, most persistent first
  S.add(new Option("all " + count(loops, "loop") + " and " + count(voids, "void") + " alive at r", ""));
  on.forEach(h => { const o = new Option(label(h), key(h)); o.style.color = colours(d, h.kind)[h.k]; S.add(o); });
  if (sel !== null && !isOn) S.add(new Option(label(sel) + ", not alive at this r", key(sel)));
  S.value = key(sel);
  document.getElementById("selinfo").textContent = sel === null ? "" : "Showing " + sel.kind + " #" + (sel.k + 1) + " of " +
    bars(d, sel.kind).length + " (ranked by persistence ratio pi)" + (isOn ? "." : ": not alive at this radius, so not drawn.");
  const top = d.h1[0], pieces = piecesAt(d, r);
  document.getElementById("rv").textContent = "r = " + r.toFixed(4);
  document.getElementById("rstat").textContent = count(pieces, "piece") + ", " + count(loops, "loop") + " and " + count(voids, "void") +
    " alive, " + ne + " edges" + (top ? "; most persistent loop " + (r < top[0] ? "not born yet" : r < top[1] ? "alive" : "filled in") : "");
  let h = "<table><tr><th></th><th>Method A (fitted " + d.family + ")" + q("method-a-exact-topology-of-the-fitted-shape", "Method A") +
    "</th><th>Method B (persistent homology)" + q("method-b-persistent-homology-of-the-cloud", "Method B") + "</th></tr>";
  for (const [k, a, b] of d.rows) h += "<tr><td>" + k + (TERMS[k] || []).map(t => q(t[0], t[1])).join("") + "</td><td>" + fmt(a) + "</td><td>" + fmt(b) + "</td></tr>";
  h += "</table><p>" + (d.notes ? d.notes + q("alignment-r", "Alignment R") + q("permutation-p-value", "Permutation p-value") +
    q("winding-number", "Winding number") : "") + "</p>"; document.getElementById("info").innerHTML = h; }
</script></body></html>
"""

WORKED = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Worked example - topology of neural geometry</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
""" + SHARED_CSS + r"""
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
<a href="examples.html">How the six example results were made</a>
<button class="gl-btn" onclick="openGloss()">Method and terms</button>
<a href="https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability">GitHub</a></header>
<main id="doc">Loading...</main>
""" + DRAWER + SHARED_JS + r"""
<script>
// The text is docs/worked_example.md (generated by run.py report); numbers and arrays are results/toy/summary.json.
const PAL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"];   // matplotlib tab10, as in fig_toy
const fin = v => (v === "inf" ? Infinity : v);                                                  // JSON stores infinite deaths as "inf"
Promise.all([fetch("worked_example.md").then(r => r.text()), fetch("data/worked_example.json").then(r => r.json())])
  .then(([md, toy]) => { const main = document.getElementById("doc"); main.innerHTML = marked.parse(md); fixLinks(main);
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


EXAMPLES_PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>How the example results were made - topology of neural geometry</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
""" + SHARED_CSS + r"""
<style>
body{font-family:system-ui,sans-serif;margin:0;color:#222;background:#fff;line-height:1.5}
header{padding:8px 16px;border-bottom:1px solid #ddd;font-size:14px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
header a{color:#30638e;text-decoration:none}
main{max-width:1100px;margin:0 auto;padding:8px 20px 60px}
#pick button{font-size:13px;padding:4px 10px;margin:0 6px 6px 0;cursor:pointer;background:#fff;border:1px solid #bbb;border-radius:6px}
#pick button.sel{border-width:3px;font-weight:600}
.row{display:flex;flex-wrap:wrap;gap:8px}.row>div{flex:1 1 460px;height:440px}
.ctl{display:flex;flex-wrap:wrap;align-items:center;gap:10px;font-size:14px;margin:6px 0}
.ctl button{font-size:13px;padding:3px 10px}
.cap{font-size:13px;color:#444;margin:2px 0 14px}
#verdict{font-size:15px;margin:8px 0}#status{font-size:14px;min-height:3em;margin:4px 0}
h2{font-size:17px;margin:22px 0 4px}
</style></head><body>
<header><a href="index.html">&larr; Explorer of the 44 clouds</a><a href="worked_example.html">Worked example on a toy cloud</a>
<button class="gl-btn" onclick="openGloss()">Method and terms</button>
<a href="https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability">GitHub</a></header>
<main>
<h1 style="font-size:22px">How the example results were made</h1>
<p>These are the six clouds of the README's example figure: positive, partial and negative results. Pick one and grow the
radius r. The 3D view shows the alpha complex<a class="q" href="#" title="Alpha complex" onclick="term('alpha-complex'); return false">?</a>
at that radius, and the persistence diagram<a class="q" href="#" title="Persistence diagram" onclick="term('persistence-diagram'); return false">?</a>
records when each loop is born and filled in. Below are the Monte Carlo null that decides whether the most persistent loop is
significant, and the test of whether the concept goes around the hole. Every number is read from the repository's results
files. New to the method? Open <a href="#" onclick="term('the-method-in-one-minute'); return false">Method and terms</a>
or the <a href="worked_example.html">worked example</a>.</p>
<div id="pick"></div><div id="verdict"></div>
<div class="ctl"><label for="r">radius r</label><input type="range" id="r" min="0" max="1000" step="1" value="500" style="flex:1"><span id="rv" style="min-width:6em"></span></div>
<div class="ctl" id="jump"></div><div id="status"></div>
<div class="row"><div id="cloud"></div><div id="pd"></div></div>
<p class="cap">Left: the cloud in its top-3 PCA coordinates<a class="q" href="#" title="Top-3 PCA" onclick="term('top-3-pca-coordinates'); return false">?</a>,
coloured by position in its cycle, with the edges of the alpha complex present at radius r (drag to rotate). Right: the loop
persistence diagram on log axes. Each loop has its own colour: its dot is solid while the loop is alive at r, and one cycle
of it<a class="q" href="#" title="Representative loop" onclick="term('representative-loop'); return false">?</a> is then drawn in
the 3D view in the same colour. The ringed dot is the most
persistent loop<a class="q" href="#" title="Top H1 pi" onclick="term('top-h1-pi'); return false">?</a>. Loops above the red dashed
line beat the null's 95th percentile<a class="q" href="#" title="Null 95th percentile" onclick="term('null-95th-percentile-q95'); return false">?</a>;
loops below the dotted line die before two concepts' clusters touch<a class="q" href="#" title="Connect radius" onclick="term('connect-radius-loop-inside-one-cluster'); return false">?</a>.</p>
<h2>Is the most persistent loop significant?</h2>
<div id="null" style="height:300px"></div>
<p class="cap">The largest persistence ratio π<a class="q" href="#" title="Persistence ratio" onclick="term('persistence-ratio-pi'); return false">?</a>
in each of the null clouds built to match this cloud's design<a class="q" href="#" title="Monte Carlo null" onclick="term('monte-carlo-null'); return false">?</a>,
against this cloud's own; p is the Monte Carlo p-value<a class="q" href="#" title="Monte Carlo p-value" onclick="term('monte-carlo-p-value'); return false">?</a>.</p>
<h2>Does the concept go around the hole once?</h2>
<div class="ctl" id="travtxt"></div>
<div id="circle" style="height:380px"></div>
<p class="cap">Each concept sits at the circular mean<a class="q" href="#" title="Circular mean" onclick="term('circular-mean'); return false">?</a>
of its points' hole angle θ_B<a class="q" href="#" title="theta_B" onclick="term('theta_a-and-theta_b-hole-coordinates'); return false">?</a>,
joined in semantic order. Going around once means alignment p &lt; 0.05<a class="q" href="#" title="Alignment R" onclick="term('alignment-r'); return false">?</a>
and winding number ±1<a class="q" href="#" title="Winding number" onclick="term('winding-number'); return false">?</a>.</p>
</main>
""" + DRAWER + SHARED_JS + REPLAY_JS + r"""
<script>
// Data: docs/data/examples.json, written by run.py site from report/examples.py (results/ and the stored clouds).
const cfg = {displayModeBar: false};                         // RMIN, RMAX, toR, toT, edgeTrace, ...: shared replay script
const fmtp = p => (p < 0.001 ? p.toExponential(1) : p.toFixed(3));
let EX = [], cur = null;
const s = document.getElementById("r");
s.oninput = () => draw(toR(+s.value));
fetch("data/examples.json").then(r => r.json()).then(list => { EX = list; const P = document.getElementById("pick");
  list.forEach((e, i) => { const b = document.createElement("button"); b.textContent = e.name; b.style.color = e.colour;
    b.style.borderColor = e.colour; b.onclick = () => show(i); P.appendChild(b); }); show(0); });
function show(i) {
  const e = cur = EX[i], P = e.points, top = e.h1[e.top];
  document.querySelectorAll("#pick button").forEach((b, j) => b.classList.toggle("sel", i === j));
  document.getElementById("verdict").innerHTML = '<b style="color:' + e.colour + '">' + e.name + ": " + e.verdict.replace(/\n/g, " ") +
    "; goes around once: " + e.goes + "</b>. Most persistent loop: π = " + e.top_pi.toFixed(2) + ", " + e.ratio.toFixed(2) +
    "× the null's 95th percentile (p = " + fmtp(e.p_loop) + ")" +
    (e.within === null ? "." : e.within ? "; it dies inside one concept's cluster." : "; it runs through the concept clusters.");
  e.base = [{type: "scatter3d", mode: "markers", x: P.map(p => p[0]), y: P.map(p => p[1]), z: P.map(p => p[2]), hoverinfo: "skip",
      showlegend: false, marker: {size: P.length > 300 ? 2 : 3.5, color: e.pos, colorscale: e.cyclic ? "Twilight" : "Viridis", cmin: 0, cmax: 1}}];
  e.layout = {margin: {l: 0, r: 0, t: 30, b: 0}, title: {text: "alpha complex and the loops alive at radius r", font: {size: 13}}, showlegend: false,
     uirevision: e.id, scene: {xaxis: {visible: false}, yaxis: {visible: false}, zaxis: {visible: false}, aspectmode: "data"}};
  Plotly.newPlot("cloud", e.base, e.layout, cfg);
  const ax = t => ({title: t, type: "log", range: [Math.log10(RMIN), Math.log10(RMAX)]}), B = [RMIN, RMAX / e.q95];
  const tr = [{x: [RMIN, RMAX], y: [RMIN, RMAX], mode: "lines", line: {color: "#999"}, name: "diagonal (π = 1)", hoverinfo: "skip"},
    {x: B, y: B.map(b => b * e.q95), mode: "lines", line: {color: "#d1495b", dash: "dash"}, name: "null 95th pct. (π = " + e.q95.toFixed(2) + ")", hoverinfo: "skip"}];
  if (e.connect_r) tr.push({x: [RMIN, RMAX], y: [e.connect_r, e.connect_r], mode: "lines", line: {color: "#555", dash: "dot", width: 1}, name: "connect radius", hoverinfo: "skip"});
  e.loopTrace = tr.length;
  tr.push({x: e.h1.map(b => b[0]), y: e.h1.map(b => b[1]), mode: "markers", marker: {size: 5, color: e.loop_colour, opacity: 0.2}, name: "loops (own colours)", hoverinfo: "text",
    text: e.h1.map(b => "born " + b[0].toFixed(4) + ", dies " + b[1].toFixed(4) + ", π = " + (b[1] / b[0]).toFixed(2))});
  tr.push({x: [top[0]], y: [top[1]], mode: "markers", marker: {size: 16, color: "rgba(0,0,0,0)", line: {color: "#000", width: 2}}, name: "most persistent loop", hoverinfo: "skip"});
  tr.push({x: [], y: [], mode: "lines", line: {color: "#333", dash: "dot", width: 1}, name: "radius r", hoverinfo: "skip"});
  Plotly.newPlot("pd", tr, {margin: {l: 55, r: 10, t: 30, b: 45}, title: {text: "loop persistence diagram (log axes)", font: {size: 13}},
    xaxis: ax("birth radius b"), yaxis: ax("death radius d"), legend: {x: 0.98, y: 0.02, xanchor: "right", yanchor: "bottom", font: {size: 11}}}, cfg);
  const J = document.getElementById("jump"); J.textContent = "jump to:";
  [["most persistent loop born", top[0] * 1.0005], ["it is alive", Math.sqrt(top[0] * top[1])], ["it is filled in", top[1] * 1.02]]
    .concat(e.connect_r ? [["clusters touch", e.connect_r * 1.0005]] : []).forEach(([lab, r]) => { const b = document.createElement("button");
      b.textContent = lab + " (r = " + r.toFixed(3) + ")"; b.onclick = () => { s.value = toT(r); draw(r); }; J.appendChild(b); });
  const nm = e.null_max, vline = (x, c, d) => ({type: "line", x0: x, x1: x, yref: "paper", y0: 0, y1: 1, line: {color: c, dash: d, width: 1.5}});
  Plotly.newPlot("null", [{x: nm, type: "histogram", nbinsx: 60, marker: {color: "#bbb"}, hoverinfo: "skip"}],
    {margin: {l: 55, r: 10, t: 10, b: 45}, xaxis: {title: "largest loop π in a null cloud", range: [1, Math.max(...nm, e.top_pi) * 1.06]},
     yaxis: {title: "null clouds (of " + nm.length + ")"}, shapes: [vline(e.q95, "#d1495b", "dash"), vline(e.top_pi, "#222", "solid")],
     annotations: [{x: e.q95, yref: "paper", y: 1, text: " 95th pct. " + e.q95.toFixed(2), showarrow: false, xanchor: "left", yanchor: "top"},
       {x: e.top_pi, yref: "paper", y: 0.82, text: " this cloud " + e.top_pi.toFixed(2) + ", p = " + fmtp(e.p_loop) + " ", showarrow: false,
        xanchor: e.top_pi > e.q95 ? "right" : "left", yanchor: "top"}]}, cfg);
  circle(e);
  const r0 = Math.sqrt(top[0] * top[1]); s.value = toT(r0); draw(r0); }
function draw(r) {
  const e = cur, alive = aliveAt(e, r), ed = edgeTrace(e, r), n = ed.n, m = loopMarker(e, alive);
  document.getElementById("rv").textContent = "r = " + r.toFixed(4);
  Plotly.react("cloud", e.base.concat([ed.trace], loopTraces(e, alive)), e.layout, cfg);
  Plotly.restyle("pd", {"marker.color": [m.color], "marker.opacity": [m.opacity], "marker.size": [m.size]}, [e.loopTrace]);
  Plotly.restyle("pd", {x: [crossXY(r).x], y: [crossXY(r).y]}, [e.loopTrace + 2]);
  const pieces = piecesAt(e, r), loops = alive.filter(Boolean).length, top = e.h1[e.top];
  document.getElementById("status").textContent = pieces + (pieces === 1 ? " piece, " : " pieces, ") + loops + (loops === 1 ? " loop" : " loops") +
    " alive, " + n + " edges in the complex. Most persistent loop (born " + top[0].toFixed(4) + ", dies " + top[1].toFixed(4) + "): " +
    (r < top[0] ? "not born yet." : r < top[1] ? "alive." : "filled in."); }
function circle(e) {
  const t = e.traversal, T = document.getElementById("travtxt");
  if (!t) { T.textContent = "No hole coordinate θ_B could be computed for this cloud."; Plotly.purge("circle"); return; }
  const xs = t.theta.map(Math.cos), ys = t.theta.map(Math.sin), n = xs.length, k = [...Array(101).keys()];
  const tr = [{x: k.map(i => Math.cos(i * Math.PI / 50)), y: k.map(i => Math.sin(i * Math.PI / 50)), mode: "lines", line: {color: "#ccc"}, hoverinfo: "skip"},
    {x: [...xs, xs[0]], y: [...ys, ys[0]], mode: "lines", line: {color: "#555", width: 1}, hoverinfo: "skip"},
    {x: xs, y: ys, mode: "markers", text: t.names, hoverinfo: "text",
     marker: {size: n > 40 ? 6 : 11, color: t.names.map((_, i) => i / n), colorscale: e.cyclic ? "Twilight" : "Viridis", cmin: 0, cmax: 1, line: {width: 0.5, color: "#333"}}}];
  if (n <= 12) tr.push({x: xs.map(v => 1.22 * v), y: ys.map(v => 1.22 * v), mode: "text", text: t.names, hoverinfo: "skip"});
  Plotly.newPlot("circle", tr, {margin: {l: 5, r: 5, t: 5, b: 5}, showlegend: false, xaxis: {range: [-1.6, 1.6], visible: false},
    yaxis: {range: [-1.5, 1.5], scaleanchor: "x", visible: false}}, cfg);
  T.innerHTML = "θ_B: " + t.source + q("preregistered-and-post-hoc", "Preregistered and post hoc") + "; concept variable: " + t.variable +
    ". R = " + t.R.toFixed(3) + ", p = " + fmtp(t.p) + ", winding " + t.w + ": " + (t.passes ? "goes around once." : "does not go around once."); }
</script></body></html>
"""


def examples_page(docs) -> None:
    """docs/examples.html and docs/data/examples.json: the six example clouds (report/examples.py), so the page can
    replay how each result was made (alpha complex growing with r, loops, null, localisation, traversal)."""
    from neurotopo.report.examples import EXAMPLES, example
    rows = []
    for d, _ in EXAMPLES:
        e = example(d)
        e["cycles"] = [c.tolist() for c in e["cycles"]]                 # list of index arrays -> list of lists
        del e["shells"], e["void_colour"], e["void_centres"]                        # this page shows loops only: keep its JSON small
        rows.append({k: (np.round(v, 5).tolist() if isinstance(v, np.ndarray) else v) for k, v in e.items()})
    (docs / "data" / "examples.json").write_text(json.dumps(_clean(rows)), encoding="utf-8", newline=chr(10))
    (docs / "examples.html").write_text(EXAMPLES_PAGE, encoding="utf-8", newline=chr(10))


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
    examples_page(docs)
    res = config.path("results")
    topo = pd.read_csv(res / "exp0" / "real_topology.csv").set_index("id")
    inv = pd.read_csv(res / "exp2" / "invariants.csv").set_index("id") if (res / "exp2" / "invariants.csv").exists() else None
    mb = read_json(res / "exp3" / "method_b.json") if (res / "exp3" / "method_b.json").exists() else {}
    th = np.load(res / "exp3" / "theta_B.npz") if (res / "exp3" / "theta_B.npz").exists() else {}
    loc = read_json(res / "exp7_audit" / "summary.json").get("localisation", {}) if (res / "exp7_audit" / "summary.json").exists() else {}
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
        rp = replay(y)                                    # edges, loops with cycles, voids with shells, colours (slider replay)
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
             "h1": np.round(rp["h1"], 5).tolist(), "h2": np.round(rp["h2"], 5).tolist(), "cycles": [c.tolist() for c in rp["cycles"]],
             "loop_colour": rp["loop_colour"], "shells": [s.tolist() for s in rp["shells"]], "void_colour": rp["void_colour"],
             "edges": rp["edges"].tolist(), "edge_r": np.round(rp["edge_r"], 5).tolist(),
             "h0_deaths": np.round(rp["h0_deaths"], 5).tolist(), "connect_r": loc.get(did, {}).get("connect_radius"),
             "q95_pi1": float(inv.loc[did, "null_q95_pi1"]) if inv is not None else None,
             "q95_pi2": float(inv.loc[did, "null_q95_pi2"]) if inv is not None else None, "rows": rows, "notes": notes}
        (out / f"{did}.json").write_text(json.dumps(_clean(d)), encoding="utf-8", newline=chr(10))
        manifest[names[group_of(did)]].append({"id": did, "label": f"{short(did)} ({t['family']})"})
    (out / "manifest.json").write_text(json.dumps({k: v for k, v in manifest.items() if v}), encoding="utf-8", newline=chr(10))
    (docs / "index.html").write_text(PAGE, encoding="utf-8", newline=chr(10))
