"""Per-dataset verdicts read from results/, shared by the README role table and the plain-language example figure.

Global context: "goes around" means the alignment of a hole coordinate with the concept's semantic cycle has
p < 0.05 (unadjusted) and winding number +-1 (experiments.alignment.passes), for the concept variable only
(ordinal sets: 7 or 12 value bins; days_time: day; the exploratory mod-10/100 variables are excluded).
"""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from neurotopo import config
from neurotopo.experiments.alignment import passes
from neurotopo.experiments.common import read_json


@lru_cache(maxsize=1)
def _data() -> dict:
    r = config.path("results")
    return {"inv": pd.read_csv(r / "exp2" / "invariants.csv").set_index("id"),
            "topo": pd.read_csv(r / "exp0" / "real_topology.csv").set_index("id"),
            "a0": read_json(r / "exp0" / "real_alignment.json"),
            "mb": read_json(r / "exp3" / "method_b.json"),
            "ph": read_json(r / "exp3" / "posthoc_relaxed_range.json")}


def concept_record(d: str, r: dict) -> bool:
    """True for an alignment record of the dataset's concept variable: no mod-10/100 variable, and for days + times
    of day the day ("day of week", the label source.concepts gives it), not the time of day."""
    return "mod" not in r["variable"] and (d != "R5c_llama_days_time" or r["variable"] == "day of week")


def _around(d: str, recs: list) -> bool:
    return any(passes(r) for r in recs if concept_record(d, r))


def loop(d: str) -> bool:
    """Significant top-3 loop under the design-matched Monte Carlo null (Exp2)."""
    return bool(_data()["inv"].loc[d, "p_top_loop"] < 0.05)


def method_a(d: str) -> bool:
    """Resolvable hole of the fitted shape (rho_A >= 1) that the concept goes around in theta_A (Exp0)."""
    t, a0 = _data()["topo"], _data()["a0"]
    return bool(t.loc[d, "hole"] and t.loc[d, "resolvable"]
                and _around(d, [r for r in a0 if r["id"] == d and r["kind"] == "hole"]))


def method_b(d: str) -> bool:
    """Significant loop that the concept goes around in the preregistered theta_B, 3D (Exp3)."""
    m = _data()["mb"][d]
    return bool(m["loop"] and _around(d, m["records3"]))


def method_b10(d: str) -> bool:
    """method_b plus the preregistered top-10-PC check (d): the full H1-B rule."""
    return method_b(d) and _around(d, _data()["mb"][d].get("records10", []))


def posthoc(d: str) -> bool:
    """Goes around once in 3D with DREiMac standard_range=False (post hoc, deviation D5)."""
    return _around(d, _data()["ph"].get(d, {}).get("3d", {}).get("records", []))
