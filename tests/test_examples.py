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


def test_headlines_match_the_readme_figure():
    want = {"R7_llama_colors": "ring: yes, but the RGB\nstimuli have it too", "R2_grokking_WE": "ring: yes",
            "R5b_llama_months": "loop: yes; ring: suggestive", "R5a_llama_weekdays": "ring: no",
            "R5c_llama_days_time": "ring: no (a small loop inside\none cluster)", "R6_llama_years": "ring: no (as expected)"}
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


def test_days_time_traversal_uses_the_day_variable():
    # The concept variable of days + times of day is the day ("day of week"), not the time of day.
    t = examples.traversal("R5c_llama_days_time")
    assert t["variable"] == "day of week" and len(t["names"]) == 7
