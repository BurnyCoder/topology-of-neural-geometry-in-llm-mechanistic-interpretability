"""Tests for the void search (`run.py voids`, experiments/void_search.py; post hoc, D10).

Global context: the README's void figures show the voids that three fixed rules pick (significant, large, shape and
meaning). These tests pin the rules on a small hand-made table, check that each cloud's most persistent void gets
exactly Exp2's p, and check the life of the toy model's octahedral void (examples.void_life).
"""

import pandas as pd

from neurotopo import config
from neurotopo.experiments import void_search as vs
from neurotopo.report import examples


def toy_table() -> pd.DataFrame:
    base = {"N": 10, "birth": 0.5, "death": 0.6, "faces": 8, "corners": 6, "n_concepts": 4}
    rows = [{"id": "R3_tms_a", "k": 1, "p": 0.001, "empty": 0.30, "extent": 1.0, "shell_concepts": 4},   # sig + large
            {"id": "C1_gp_x", "k": 1, "p": 0.90, "empty": 0.20, "extent": 1.0, "shell_concepts": 4},    # large only
            {"id": "R5_days", "k": 2, "p": 0.30, "empty": 0.01, "extent": 0.8, "shell_concepts": 3},    # shape+meaning
            {"id": "R5_days", "k": 1, "p": 0.40, "empty": 0.02, "extent": 0.9, "shell_concepts": 4},    # same cloud, worse p
            {"id": "R6_years", "k": 1, "p": 0.60, "empty": 0.01, "extent": 0.9, "shell_concepts": 4},   # p >= 0.5: out
            {"id": "R7_hues", "k": 1, "p": 0.04, "empty": 0.001, "extent": 0.1, "shell_concepts": 1}]   # sig only
    return pd.DataFrame([{**base, **r, "pi": 1.1} for r in rows])


def test_interesting_rules(monkeypatch):
    monkeypatch.setattr(vs, "LARGE_N", 2)
    out = vs.interesting(toy_table()).set_index(["id", "k"])["reasons"].to_dict()
    assert out == {("R3_tms_a", 1): "significant, large", ("R7_hues", 1): "significant", ("R5_days", 2): "shape and meaning",
                   ("C1_gp_x", 1): "large"}


def test_top_void_p_equals_exp2():
    s = pd.read_json(config.path("results") / "voids" / "summary.json", typ="series")
    assert s["max_abs_p_gap_vs_exp2"] == 0 and s["n_voids"] > 0


def test_octahedron_void_life():
    # Toy model, 6 features: 12 edges make 7 loops; 8 faces kill them and close one void; tetrahedra fill it.
    life = examples.void_life("R3_tms_n6")
    s1, s2, s3, s4 = life["stages"]
    assert (s1["edges"], s1["triangles"], s1["loops"], s1["voids"]) == (12, 0, 7, 0)
    assert (s2["triangles"], s2["loops"], s2["voids"]) == (8, 0, 1) and s2["pocket"] > s3["pocket"] > 0
    assert s4["voids"] == 0 and s4["tetrahedra"] > 0 and s4["pocket"] == 0
    assert life["loops_born"] == life["loops_dead_by_birth"] == 7
    assert len(life["y"]) - s2["edges"] + s2["triangles"] == 2                      # Euler characteristic 1 - 0 + 1
