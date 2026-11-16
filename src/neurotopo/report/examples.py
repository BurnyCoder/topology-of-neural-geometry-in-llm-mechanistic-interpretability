"""Data behind the six plain-language examples: verdict headlines, cycle positions and everything needed to replay
how each result was made (alpha complex growing with r, loops, null, localisation, travel around the hole).

Global context: the README's example figure (figures.fig_examples), its animation (figures.anim_examples) and the
interactive page docs/examples.html (report/site.py) all read this module, so their titles and numbers agree. It
only reads results/ and the stored clouds; the alpha complexes are recomputed with GUDHI (seconds per cloud).
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.alignment import passes
from neurotopo.experiments.common import read_json
from neurotopo.report import verdicts as v
from neurotopo.stats import circular as cs
from neurotopo.tda import diagrams

EXAMPLES = [("R7_llama_colors", "Colours"), ("R2_grokking_WE", "Residues mod 113\n(toy network)"),
            ("R5b_llama_months", "Months"), ("R5a_llama_weekdays", "Weekdays"),
            ("R5c_llama_days_time", "Days + times of day"), ("R6_llama_years", "Years (control)")]
CONTROL = "R6_llama_years"                       # an ordinal concept: "no ring" is the expected outcome


@lru_cache(maxsize=None)
def _json(*parts: str):
    return read_json(config.path("results").joinpath(*parts))


@lru_cache(maxsize=1)
def _inv() -> pd.DataFrame:
    """results/exp2/invariants.csv: per cloud the top H1 pi, its null 95th percentile and p-value."""
    return pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")


def _audit() -> dict:
    p = config.path("results") / "exp7_audit" / "summary.json"
    return _json("exp7_audit", "summary.json") if p.exists() else {}


def grok_k() -> int:
    """Fourier frequency k found by theta_B for the residues (they are ordered by k * r mod 113)."""
    return int(_json("exp3", "method_b.json")["R2_grokking_WE"]["records3"][0]["k"])


def concept_positions(d: str, labels: list[str], n_bins: int = 12) -> np.ndarray:
    """Position of every point in its semantic cycle, in [0, 1): concept index / number of concepts (years: value
    bin), residues by k * r mod 113. Used to colour the clouds."""
    if d == "R2_grokking_WE":
        return (grok_k() * np.array([int(s) for s in labels])) % 113 / 113
    con = source.concepts(d, labels, n_bins=n_bins)
    return con.index / len(con.phase)


def headline(d: str) -> dict:
    """The example figure's two verdicts. A top-3 loop beyond the design-matched Gaussian null is not enough for
    "ring": that null also rejects many hole-free shapes (audit D9), and a significant loop inside one concept's
    cluster is not a ring of concepts (audit D8). So "ring: yes" needs a loop through the clusters that the concept
    goes around once in the preregistered analysis; with only post hoc traversal it is "suggestive"."""
    a = _audit()
    small = v.loop(d) and a.get("localisation", {}).get(d, {}).get("within_concept_loop", False)
    ring = v.loop(d) and not small
    goes = "yes" if (v.method_b(d) or v.method_a(d)) else ("only post hoc" if v.posthoc(d) else "no")
    control = d == CONTROL
    inherited = d == "R7_llama_colors" and ring and bool(a and a["colour_baseline"]["rgb"]["p_loop"] < 0.05)
    ok = (ring and goes == "yes" and not inherited) or (control and not ring)
    verdict = "ring: no (a small loop inside\none cluster)" if small else \
        "ring: yes, but the RGB\nstimuli have it too" if inherited else \
        "ring: yes" if ring and goes == "yes" else \
        f"loop: yes; ring: {'suggestive' if goes == 'only post hoc' else 'not shown'}" if ring else \
        "ring: no" + (" (as expected)" if control else "")
    return {"ring": bool(ring), "small": bool(small), "goes": goes, "ok": bool(ok), "verdict": verdict,
            "colour": "#1b7837" if ok else ("#b35806" if ring else "#333333")}


def _concepts_for(d: str, labels: list[str], variable: str):
    """source.concepts for an alignment record's variable name (e.g. "value in 7 bins", "time of day")."""
    if "bins" in variable:
        return source.concepts(d, labels, n_bins=int(variable.split()[2]))
    return source.concepts(d, labels, variable="time" if variable == "time of day" else None)


def traversal(d: str) -> dict | None:
    """Concept mean angles of theta_B in semantic order with the record's R, p and winding: the preregistered
    record if theta_B exists, else the post hoc one (DREiMac standard_range=False, deviation D5); None if neither."""
    labels = realdata.cloud(d)["labels"]
    recs, src = [r for r in _json("exp3", "method_b.json")[d]["records3"] if v.concept_record(d, r)], "preregistered"
    if not recs:
        ph = _json("exp3", "posthoc_relaxed_range.json").get(d, {}).get("3d", {}).get("records", [])
        recs, src = [r for r in ph if v.concept_record(d, r)], "post hoc (standard_range=False)"
    if not recs:
        return None
    r = recs[0]
    if d == "R2_grokking_WE":                    # one point per residue; the record keeps only the frequency k
        theta = np.load(config.path("results") / "exp3" / "theta_B.npz")[d]
        tc = cs.concept_means(theta, np.array([int(s) for s in labels]), 113)
        order = np.argsort((r["k"] * np.arange(113)) % 113)
        names = [str(i) for i in order]
    else:
        con = _concepts_for(d, labels, r["variable"])
        tc = np.asarray(r["concept_theta"], dtype=np.float64)
        order = np.argsort(np.mod(con.phase, 2 * np.pi), kind="stable")
        names = [con.names[i] for i in order]
    return {"source": src, "variable": r["variable"], "names": names, "theta": tc[order].tolist(),
            "R": float(r["R"]), "p": float(r["p"]), "w": int(r["winding"]), "passes": bool(passes(r))}


def loop_colours(n: int) -> list[str]:
    """n distinct colours, one per loop: hues spaced by the golden angle (consecutive loops never look alike)."""
    from matplotlib.colors import hsv_to_rgb, to_hex
    return [to_hex(hsv_to_rgb(((0.6180339887 * i) % 1.0, 0.8, 0.85))) for i in range(n)]


def replay(y: np.ndarray) -> dict:
    """What it takes to replay persistent homology on a cloud y: the alpha complex's edges with their entry radii,
    the H0 deaths (pieces merging), the voids, and the loops sorted from the most persistent down, each with a
    representative cycle (diagrams.alpha_h1_cycles) and its own colour. Index 0 is the most persistent loop."""
    ij, er = diagrams.alpha_edges(y)
    dg = diagrams.alpha_diagrams(y)
    bars, cycles = diagrams.alpha_h1_cycles(y)
    order = np.argsort(-(bars[:, 1] / bars[:, 0]), kind="stable") if len(bars) else np.zeros(0, dtype=int)
    h0 = dg[0][:, 1]
    return {"edges": ij, "edge_r": er, "h0_deaths": np.sort(h0[np.isfinite(h0)]), "h1": bars[order],
            "cycles": [cycles[i] for i in order], "loop_colour": loop_colours(len(order)), "h2": dg[2], "top": 0}


def example(d: str) -> dict:
    """Everything needed to replay how dataset d's result was made (arrays as numpy, see site.py for JSON)."""
    seed = config.load()["seed"]
    c = realdata.cloud(d)
    rp = replay(c["y"])
    top_pi = float(rp["h1"][0, 1] / rp["h1"][0, 0])
    inv = _inv().loc[d]
    loc = _audit().get("localisation", {}).get(d)
    return {"id": d, "name": dict(EXAMPLES).get(d, d).replace("\n", " "), **headline(d), "points": c["y"],
            "pos": concept_positions(d, c["labels"]), "cyclic": d != CONTROL, **rp, "top_pi": top_pi,
            "q95": float(inv["null_q95_pi1"]), "p_loop": float(inv["p_top_loop"]),
            "ratio": top_pi / float(inv["null_q95_pi1"]), "null_max": realdata.null(d, seed)[:, 0],
            "connect_r": float(loc["connect_radius"]) if loc else None,
            "within": bool(loc["within_concept_loop"]) if loc else None, "traversal": traversal(d)}

