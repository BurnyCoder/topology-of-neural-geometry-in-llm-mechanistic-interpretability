"""Exp3 post hoc (not preregistered): theta_B with DREiMac standard_range=False.

Global context: the preregistered DREiMac setting standard_range=True builds a circular coordinate only for a
Rips class whose death is at least twice its birth (DREiMac EMCoords.get_cover_radius), which guarantees the
class is non-trivial in the Cech complex. The weekday, month and days_time loops are weaker than that (Rips
death/birth 1.3-1.9), so H1-B failed there before the alignment could be tested. This post hoc sensitivity
analysis (reports/deviations.md D5) recomputes theta_B with standard_range=False (class guaranteed only in the
Rips complex, as DREiMac's error message suggests) in 3D and in the top-10 PCs, and repeats the alignment
test. It does not change any preregistered verdict.
"""

from __future__ import annotations

import logging

from neurotopo import config
from neurotopo.experiments import alignment, realdata
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.experiments.exp3_cyclic import EXPLORATORY
from neurotopo.geometry.pca import fit_frame
from neurotopo.tda import circular

log = logging.getLogger(__name__)


def run() -> None:
    cfg = config.load()
    g = cfg["groups"]
    out = out_dir("exp3")
    env_record("exp3_posthoc")
    ids = g["cyclic_primary"] + g["cyclic_secondary"] + g["ordinal"] + g["init_controls"] + \
        [f"C1_{k}_{i}" for k in ("gp", "walk") for i in range(10)] + EXPLORATORY
    res = {}
    for did in ids:
        c = realdata.cloud(did)
        y10, _ = fit_frame(c["x"], k=cfg["circular"]["topk_check"])
        r = {}
        for name, pts in (("3d", c["y"]), ("top10", y10)):
            cc = circular.circular_coordinates(pts, standard_range=False)
            recs = alignment.records(did, cc["theta"], c["labels"], cfg["seed"]) if cc["theta"] is not None else []
            r[name] = {"error": cc["error"], "rips_bar": cc["bar"], "records": recs}
        res[did] = r
        first = lambda k: (r[k]["records"] or [{}])[0]
        log.info("%-26s 3D: R=%s p=%s w=%s | top10: R=%s p=%s w=%s", did, first("3d").get("R"), first("3d").get("p"),
                 first("3d").get("winding"), first("top10").get("R"), first("top10").get("p"), first("top10").get("winding"))
    write_json(out / "posthoc_relaxed_range.json", res)
