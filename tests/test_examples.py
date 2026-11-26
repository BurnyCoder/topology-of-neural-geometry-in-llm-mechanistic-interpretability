"""Tests for the data behind the six plain-language examples (report/examples.py).

Global context: the README's example figure (fig_examples), its animation (anim_examples) and the interactive page
docs/examples.html all read one function, examples.example(d). These tests pin the verdict headlines to the titles
the README figure shows, and check that the per-example data (alpha-complex edges, loops, null, localisation,
traversal) is internally consistent.
"""

import math

import numpy as np

from neurotopo.experiments import toy_example as toy
from neurotopo.report import examples
from neurotopo.tda import diagrams


def test_alpha_edges_toy():
    # The toy's 21 triangle sides enter at half their length s/2; the edge list is sorted by entry radius.
    p, _ = toy.toy_points(7, 0.1)
    ij, r = diagrams.alpha_edges(p)
    assert ij.shape[1] == 2 and np.all(np.diff(r) >= 0)
    assert int(np.isclose(r, 0.05).sum()) == 21
    assert math.isclose(r.max(), math.hypot(1 - 0.1 / (2 * math.sqrt(3)), 0.05), rel_tol=1e-9)


def test_loop_representatives_toy():
    # Each loop comes with a closed cycle made of edges present when the loop is born. On the toy, the 7 tiny loops
    # are the triangles of single concepts and the ring passes through all 7 concepts.
    p, idx = toy.toy_points(7, 0.1)
    bars, cycles = diagrams.alpha_h1_cycles(p)
    ref = diagrams.alpha_diagrams(p)[1]
    assert np.allclose(np.sort(bars, axis=0), np.sort(ref, axis=0))                 # same loops as the diagram
    ij, r = diagrams.alpha_edges(p)
    entry = {tuple(sorted(e)): x for e, x in zip(ij.tolist(), r)}
    for (b, _), cyc in zip(bars, cycles):
        ring = list(cyc) + [cyc[0]]
        assert len(set(cyc)) == len(cyc) >= 3                                       # a simple closed cycle
        assert all(entry[tuple(sorted(e))] <= b + 1e-12 for e in zip(ring[:-1], ring[1:]))
    sizes = sorted(len(set(idx[c])) for c in cycles)
    assert sizes == [1] * 7 + [7]


def test_headlines_match_the_readme_figure():
    want = {"R7_llama_colors": "3D hue alignment\nalso in RGB", "R2_grokking_WE": "3D alignment and winding",
            "R5b_llama_months": "3D loop; alignment\nonly post hoc", "R5a_llama_weekdays": "3D loop test below threshold",
            "R5c_llama_days_time": "3D loop within one cluster", "R6_llama_years": "3D loop test below threshold"}
    for d, v in want.items():
        assert examples.headline(d)["verdict"] == v, d


def test_example_weekdays_is_consistent():
    e = examples.example("R5a_llama_weekdays")
    n = len(e["points"])
    assert e["edges"].max() < n and np.all(np.diff(e["edge_r"]) >= 0)
    top = e["h1"][e["top"]]
    assert e["within"] is True and top[1] <= e["connect_r"]          # the top loop dies inside one day's cluster
    assert len(e["h0_deaths"]) == n - 1                              # all but one piece merge
    t = e["traversal"]
    assert t["source"].startswith("post hoc") and t["names"][0] == "Monday" and len(t["theta"]) == 7


def test_colours_largest_void_and_stimulus_colours():
    # The README's colours void is the one with the largest empty middle; the hue ring winds around it once; the
    # points are painted in their prompts' RGB (36 hues x 5 saturations x 5 lightnesses = 900 prompts).
    from neurotopo.experiments import realdata
    lv = examples.largest_void("R7_llama_colors")
    h2 = lv["rp"]["h2"]
    assert lv["k"] == int(np.argmax(h2[:, 1] - h2[:, 0])) and abs(lv["winding"]) == 1
    assert 0 < lv["p"] <= 1 and 0 < lv["shell_concepts"] <= lv["n_concepts"] == 36
    rgb = examples.stimulus_rgb("R7_llama_colors", realdata.cloud("R7_llama_colors")["labels"])
    assert rgb.shape == (900, 3) and rgb.min() >= 0 and rgb.max() <= 1
    assert examples.stimulus_rgb("R6_llama_years", []) is None


def test_highlights_are_the_bh_significant_rings_and_voids():
    # The README's first figure: top loops surviving BH whose concepts go around once, and top voids surviving BH.
    loops, voids = examples.highlights()
    assert [r["id"] for r in loops] == ["R7_llama_colors", "R2_grokking_WE", "R5b_llama_months", "R5b_llama_months_means"]
    assert all(r["k"] == 1 and abs(r["winding"]) == 1 for r in loops)
    assert [r["id"] for r in voids] == ["R3_tms_n20", "R3_tms_n6", "R3_tms_n8"] and all(r["k"] == 1 for r in voids)


def test_days_time_traversal_uses_the_day_variable():
    # The concept variable of days + times of day is the day ("day of week"), not the time of day.
    t = examples.traversal("R5c_llama_days_time")
    assert t["variable"] == "day of week" and len(t["names"]) == 7
