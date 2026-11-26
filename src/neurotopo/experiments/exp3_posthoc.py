"""Post hoc alignment with DREiMac standard_range=False in three and ten PCs.

The strict method uses a landmark Rips H1 interval with death at least twice birth
to select a range compatible with the Cech construction. A coordinate also needs
coverage of the observed points. Relaxing the interval requirement can produce
angles for shorter classes. See https://dreimac.scikit-tda.org/en/latest/theory.html
and the preregistered and exploratory measurements in results/exp3.
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
            r[name] = {"error": cc["error"], "rips_bar": cc["bar"], "uncovered": cc.get("uncovered"), "cover_radius": cc.get("cover_radius"), "n_landmarks": cc["n_landmarks"], "records": recs}
        res[did] = r
        first = lambda k: (r[k]["records"] or [{}])[0]
        log.info("%-26s 3D: R=%s p=%s w=%s | top10: R=%s p=%s w=%s", did, first("3d").get("R"), first("3d").get("p"),
                 first("3d").get("winding"), first("top10").get("R"), first("top10").get("p"), first("top10").get("winding"))
    write_json(out / "posthoc_relaxed_range.json", res)
