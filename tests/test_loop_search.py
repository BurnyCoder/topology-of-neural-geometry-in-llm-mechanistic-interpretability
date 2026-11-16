"""Tests for the loop search (`run.py loops`, experiments/loop_search.py; post hoc, D11).

Global context: the README's loop gallery shows the loops that three fixed rules pick (significant, large, goes around
once). These tests pin the concept winding on known sequences, the rules on a small hand-made table, and check that
each cloud's most persistent loop gets exactly Exp2's p.
"""

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.experiments import loop_search as ls


def test_winding_counts_turns():
    t = 2 * np.pi * np.arange(12) / 12                                    # 12 months in order
    assert ls.winding(t) == 1 and ls.winding(t[::-1]) == -1               # once around, either direction
    assert ls.winding(2 * t) == 2                                         # around twice
    assert ls.winding(np.array([0.0, 0.5, 1.0, 0.5])) == 0                # out and back: no turn
    assert ls.winding(t[[0, 1, 2, 3, 5, 4, 6, 7, 8, 9, 10, 11]]) == 1     # one swap does not change the winding


def toy_table() -> pd.DataFrame:
    base = {"N": 10, "birth": 0.1, "death": 0.2, "length": 6, "loop_concepts": 6, "n_concepts": 7, "pi": 2.0}
    rows = [{"id": "R7_hues", "k": 1, "p": 0.001, "size": 0.40, "extent": 0.4, "cyclic": True, "winding": 1},   # sig+large
            {"id": "R5_months", "k": 2, "p": 0.20, "size": 0.01, "extent": 0.8, "cyclic": True, "winding": -1},  # around
            {"id": "R5_months", "k": 3, "p": 0.30, "size": 0.01, "extent": 0.9, "cyclic": True, "winding": 1},   # worse p
            {"id": "R6_years", "k": 1, "p": 0.10, "size": 0.01, "extent": 0.9, "cyclic": False, "winding": 0},   # not cyclic
            {"id": "C1_gp", "k": 1, "p": 0.90, "size": 0.30, "extent": 0.9, "cyclic": False, "winding": 0}]      # large only
    return pd.DataFrame([{**base, **r} for r in rows])


def test_interesting_rules(monkeypatch):
    monkeypatch.setattr(ls, "LARGE_N", 2)
    out = ls.interesting(toy_table()).set_index(["id", "k"])["reasons"].to_dict()
    assert out == {("R7_hues", 1): "significant, large", ("R5_months", 2): "goes around once", ("C1_gp", 1): "large"}


def test_top_loop_p_equals_exp2():
    s = pd.read_json(config.path("results") / "loops" / "summary.json", typ="series")
    assert s["max_abs_p_gap_vs_exp2"] == 0 and s["n_loops"] > 0
