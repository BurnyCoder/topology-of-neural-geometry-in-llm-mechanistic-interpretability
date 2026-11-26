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
    """Summarise the measured 3D loop and alignment separately from the top-ten or steering endpoints."""
    a = _audit()
    small = v.loop(d) and a.get("localisation", {}).get(d, {}).get("within_concept_loop", False)
    ring = v.loop(d) and not small
    goes = "yes" if (v.method_b(d) or v.method_a(d)) else ("only post hoc" if v.posthoc(d) else "no")
    control = d == CONTROL
    inherited = d == "R7_llama_colors" and ring and bool(a and a["colour_baseline"]["rgb"]["p_loop"] < 0.05)
    ok = (ring and goes == "yes" and not inherited) or (control and not ring)
    if small:
        verdict = "3D loop within one cluster"
    elif inherited:
        verdict = "3D hue alignment\nalso in RGB"
    elif ring and goes == "yes":
        verdict = "3D alignment and winding"
    elif ring:
        verdict = "3D loop; alignment\n" + ("only post hoc" if goes == "only post hoc" else "unavailable")
    else:
        verdict = "3D loop test below threshold"

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
    the H0 deaths (pieces merging), and the loops and the voids, each sorted from the most persistent down, with a
    representative cycle (diagrams.alpha_h1_cycles) or shell and centre (diagrams.alpha_h2_voids) and its own colour;
    voids continue the loops' colour sequence, so no void shares a colour with a loop. Index 0 is the most persistent."""
    ij, er = diagrams.alpha_edges(y)
    h0 = diagrams.alpha_diagrams(y, maxdim=0)[0][:, 1]
    bars, cycles = diagrams.alpha_h1_cycles(y)
    vbars, shells, centres = diagrams.alpha_h2_voids(y)
    by_pi = lambda b: np.argsort(-(b[:, 1] / b[:, 0]), kind="stable")   # most persistent first; empty -> empty
    order, vorder = by_pi(bars), by_pi(vbars)
    colours = loop_colours(len(order) + len(vorder))
    return {"edges": ij, "edge_r": er, "h0_deaths": np.sort(h0[np.isfinite(h0)]), "h1": bars[order],
            "cycles": [cycles[i] for i in order], "loop_colour": colours[:len(order)], "h2": vbars[vorder],
            "shells": [shells[i] for i in vorder], "void_centres": centres[vorder], "void_colour": colours[len(order):],
            "top": 0}


@lru_cache(maxsize=1)
def _certificates():
    path = config.path("results")/"science/representatives.csv.gz"
    return pd.read_csv(path).query("dimension == 1").sort_values("k").groupby("id").certified.agg(list).to_dict()


def loop_certificates(d, count):
    flags = _certificates()[d]
    if len(flags) != count:
        raise ValueError(f"{d}: loop certificates and persistence intervals differ in length")
    return flags


def example(d: str) -> dict:
    """Everything needed to replay how dataset d's result was made (arrays as numpy, see site.py for JSON)."""
    seed = config.load()["seed"]
    c = realdata.cloud(d)
    rp = replay(c["y"])
    top_pi = float(rp["h1"][0, 1] / rp["h1"][0, 0])
    inv = _inv().loc[d]
    loc = _audit().get("localisation", {}).get(d)
    return {"id": d, "name": dict(EXAMPLES).get(d, d).replace("\n", " "), **headline(d), "points": c["y"],
            "pos": concept_positions(d, c["labels"]), "cyclic": d != CONTROL, **rp, "cycle_certified": loop_certificates(d, len(rp["h1"])), "top_pi": top_pi,
            "q95": float(inv["null_q95_pi1"]), "p_loop": float(inv["p_top_loop"]),
            "ratio": top_pi / float(inv["null_q95_pi1"]), "null_max": realdata.null(d, seed)[:, 0],
            "connect_r": float(loc["connect_radius"]) if loc else None,
            "within": bool(loc["within_concept_loop"]) if loc else None, "traversal": traversal(d)}


@lru_cache(maxsize=None)
def largest_void(d: str) -> dict:
    """Cloud d's void with the largest empty middle (largest death - birth, the blue ball of figures.fig_detected_voids),
    chosen for the README after browsing the explorer (post hoc). Also its rank by pi, the radius at which the most
    persistent loop is filled in, that loop's winding number around the void's centre, measured in the loop's best-fit
    plane (SVD of its representative cycle), and the void's Monte Carlo p-value against the cloud's design-matched
    null of the largest void pi (realdata.null, as Exp2 tests the top void), and how many of the cloud's concepts
    (source.concepts; 36 hues for colours) have a point among the shell's corners. The dict holds the replay data
    `rp`; treat it as read-only."""
    c = realdata.cloud(d)
    y, con = c["y"], source.concepts(d, c["labels"])
    rp = replay(y)
    h2, k = rp["h2"], int(np.argmax(rp["h2"][:, 1] - rp["h2"][:, 0]))
    null = realdata.null(d, config.load()["seed"])[:, 1]               # max void pi in each null cloud
    ring = y[np.r_[rp["cycles"][0], rp["cycles"][0][:1]]]              # most persistent loop, closed
    m = ring.mean(0)
    plane = np.linalg.svd(ring - m)[2][:2]                              # its best-fit plane's two axes
    p, c = (ring - m) @ plane.T, (rp["void_centres"][k] - m) @ plane.T
    turn = np.unwrap(np.arctan2(p[:, 1] - c[1], p[:, 0] - c[0]))        # angle of the loop seen from the void's centre
    return {"rp": rp, "k": k, "rank": k + 1, "n": len(h2), "birth": float(h2[k, 0]), "death": float(h2[k, 1]),
            "pi": float(h2[k, 1] / h2[k, 0]), "loop_death": float(rp["h1"][0, 1]),
            "p": float((1 + np.sum(null >= h2[k, 1] / h2[k, 0])) / (len(null) + 1)),   # (1 + #null >= obs) / (M + 1)
            "shell_concepts": len(np.unique(con.index[np.unique(rp["shells"][k])])), "n_concepts": len(con.names),
            "winding": int(round((turn[-1] - turn[0]) / (2 * np.pi)))}


@lru_cache(maxsize=None)
def void_life(d: str) -> dict:
    """The life of cloud d's most persistent void, in four stages of the alpha complex (figures.fig_void_life):
    (1) after the loops are born but before the void closes (halfway between the last loop birth below the void's
    birth b and b), (2) just after it closes (b + 0.2 (d - b)), (3) shortly before it fills (b + 0.8 (d - b)) and
    (4) just after it fills (1.03 d). At each stage: the simplices present (alpha radius <= r), the loops and voids
    alive (birth <= r < death) and the radius d - r of the ball around the void's centre still uncovered (no point
    is closer to the centre than d). Read-only dict."""
    y = realdata.cloud(d)["y"]
    vbars, shells, centres = diagrams.alpha_h2_voids(y)
    t = int(np.argmax(vbars[:, 1] / vbars[:, 0]))
    b, dd = vbars[t]
    h1 = diagrams.alpha_diagrams(y)[1]
    cx = diagrams.alpha_filtration(y, maxdim=3)                         # every simplex with its entry radius
    radii = [0.5 * (b + h1[h1[:, 0] < b, 0].max()), b + 0.2 * (dd - b), b + 0.8 * (dd - b), 1.03 * dd]
    stages = [{"r": r, **{name: sum(1 for sx, x in cx if len(sx) == m and x <= r)
                          for name, m in (("edges", 2), ("triangles", 3), ("tetrahedra", 4))},
               "loops": int(np.sum((h1[:, 0] <= r) & (r < h1[:, 1]))),
               "voids": int(np.sum((vbars[:, 0] <= r) & (r < vbars[:, 1]))),
               "pocket": float(dd - r) if b <= r < dd else 0.0} for r in radii]
    return {"y": y, "complex": cx, "birth": float(b), "death": float(dd), "pi": float(dd / b), "shell": shells[t],
            "centre": centres[t], "h1": h1, "h2": vbars, "stages": stages,
            "loops_born": int(np.sum(h1[:, 0] < b)), "loops_dead_by_birth": int(np.sum(h1[:, 1] <= b * (1 + 1e-9))),
            "edge_r": float(h1[h1[:, 0] < b, 0].max()), "faces_r": float(h1[h1[:, 0] < b, 1].min())}


def highlights() -> tuple[list[dict], list[dict]]:
    """The README's first figure (figures.fig_highlights): the strongest loops and voids, by rule (post hoc).
    Loops: a cloud's most persistent loop that survives Benjamini-Hochberg over Exp2's 44 loop tests and whose
    concepts wind once along its representative cycle (results/loops, run.py loops). This does not make it a "ring":
    the figure titles each loop with its original verdict (headline). Voids: a cloud's most persistent
    void that survives Benjamini-Hochberg over the 44 void tests (results/voids, run.py voids). Each list is ordered
    by persistence ratio, largest first; rows are the search phases' records (with the cycle for loops)."""
    inv = _inv()
    loops = [r for r in _json("loops", "summary.json")["interesting"]
             if r["k"] == 1 and inv.loc[r["id"], "q_top_loop"] < 0.05 and r["cyclic"] and abs(r["winding"]) == 1]
    voids = [r for r in _json("voids", "summary.json")["interesting"]
             if r["k"] == 1 and inv.loc[r["id"], "q_top_void"] < 0.05]
    by_pi = lambda rows: sorted(rows, key=lambda r: -r["pi"])
    return by_pi(loops), by_pi(voids)


def stimulus_rgb(d: str, labels: list[str]) -> np.ndarray | None:
    """(N, 3) RGB in [0, 1] of each colour prompt (labels "hue|sat|lum", as exp7_audit.colour_stimuli builds them
    from the source's prompt builder), so the colours cloud can be painted in its own colours; None for other sets."""
    if d != "R7_llama_colors":
        return None
    from neurotopo.experiments.exp7_audit import colour_stimuli
    rgb, lab = colour_stimuli()
    return rgb[[lab.index(s) for s in labels]] / 255.0

