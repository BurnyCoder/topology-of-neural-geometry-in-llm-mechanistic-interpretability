"""Where do the original labelled points sit on their fitted shape? (exploratory, descriptive)

Global context: each real cloud was fitted by one uniquely parametrised shape (helix, ringing curve, cone,
sphere, clusters, ...). Projecting every original point onto its fitted shape gives its intrinsic
coordinates: the curve parameter t / s, the azimuth and height around a cone's or helix's axis, the sphere's
azimuth and polar height, or the nearest cluster centroid / polytope vertex. This phase checks whether the
concept values (weekday, month, residue, hue, year, temperature, ...) are ordered along those coordinates:
- angular coordinates: circular alignment R with the semantic phases, permutation p, winding (shared code);
- linear coordinates (t, s, axial position, height): Spearman rank correlation with the value (ordinal sets,
  per point) or with the concept index (cyclic sets, per concept mean; exact permutation p for n <= 8);
- cluster / vertex assignments: normalised mutual information and adjusted Rand index with the concepts.
It uses only the stored clouds and the source fits; no model is run.
"""

from __future__ import annotations

import itertools
import logging

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

from neurotopo import config
from neurotopo.analytic import coords
from neurotopo.data import source
from neurotopo.experiments import alignment
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.stats import circular as cs

log = logging.getLogger(__name__)
ANGULAR = {"theta", "theta2"}
NAMES = {"helix": {"t": "curve parameter t", "theta": "azimuth", "axial": "axial position"},
         "ringing": {"s": "curve parameter s"}, "line": {"s": "position s"},
         "arc": {"theta": "angle"}, "ellipse": {"theta": "angle"},
         "cone": {"theta": "azimuth", "height": "height s"}, "sphere": {"theta": "azimuth", "height": "polar height z"},
         "torus": {"theta": "longitude", "theta2": "meridian"}}


def spearman_exact(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Spearman rho with an exact two-sided permutation p for n <= 8, else scipy's asymptotic p."""
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    rho = float(stats.spearmanr(x, y).statistic)
    if len(x) <= 8:
        rs = [stats.spearmanr(x, np.asarray(y)[list(p)]).statistic for p in itertools.permutations(range(len(y)))]
        return rho, float(np.mean(np.abs(rs) >= abs(rho) - 1e-12))
    return rho, float(stats.spearmanr(x, y).pvalue)


def numeric_values(labels: list[str]) -> np.ndarray | None:
    try:
        return np.array([float(s) for s in labels])
    except ValueError:
        return None


def extra_variables(dataset_id: str, labels: list[str]) -> dict[str, np.ndarray]:
    """Nuisance / secondary variables stored implicitly in the source's row order or labels:
    the prompt offset k ("k days from") of weekdays and months, and saturation / lightness of colours."""
    n = len(labels)
    if dataset_id in ("R5a_llama_weekdays", "C3_llama_weekdays_init"):
        return {"offset k": (np.arange(n) % 7 + 1).astype(float)}
    if dataset_id in ("R5b_llama_months", "C3_llama_months_init"):
        return {"offset k": (np.arange(n) % 12 + 1).astype(float)}
    if dataset_id == "R7_llama_colors":
        sat = np.array([float(s.split("|")[1]) for s in labels])
        lum = np.array([float(s.split("|")[2]) for s in labels])
        return {"saturation": sat, "lightness": lum}
    return {}


def dataset_records(dataset_id: str, seed: int) -> list[dict]:
    rr = source.real_results()[dataset_id]
    fam, p = rr["family"], rr["params"]
    viz = source.load_viz(dataset_id)
    pts, labels = viz["points"], viz["labels"]
    out = []
    variables = alignment.variables(dataset_id)
    if not variables:
        return out
    if fam in ("clusters", "polytope"):
        assign = cKDTree(np.asarray(p["centroids"] if fam == "clusters" else p["vertices"])).query(pts)[1]
        for v, nb in variables:
            if v in ("mod10", "mod100"):
                continue
            con = source.concepts(dataset_id, labels, variable=None if v == "bins" else v, n_bins=nb or 7)
            out.append({"id": dataset_id, "family": fam, "coordinate": "nearest centroid/vertex", "variable": con.variable,
                        "NMI": float(normalized_mutual_info_score(con.index, assign)),
                        "ARI": float(adjusted_rand_score(con.index, assign)), "k": int(assign.max() + 1)})
        return out
    if fam not in NAMES:
        return out
    ic = coords.intrinsic_coords(fam, p, pts)
    num = numeric_values(labels)
    for key, cname in NAMES[fam].items():
        x = ic[key]
        for vname, vals in extra_variables(dataset_id, labels).items():
            if key in ANGULAR:
                continue
            rho, pv = spearman_exact(x, vals)
            out.append({"id": dataset_id, "family": fam, "coordinate": cname, "statistic": "Spearman (points)",
                        "variable": vname, "n": len(x), "rho": rho, "p": pv})
        if key in ANGULAR:
            for r in alignment.records(dataset_id, x, labels, seed):
                out.append({"id": dataset_id, "family": fam, "coordinate": cname, "statistic": "circular alignment",
                            **{k: r[k] for k in ("variable", "n", "R", "p", "winding", "order_match")}})
        else:
            if num is not None and dataset_id not in alignment.CYCLIC_IDS:
                rho, pv = spearman_exact(x, num)
                out.append({"id": dataset_id, "family": fam, "coordinate": cname, "statistic": "Spearman (points)",
                            "variable": "value", "n": len(x), "rho": rho, "p": pv})
            else:
                for v, nb in variables:
                    if dataset_id in alignment.GROK:
                        a = np.array([int(s) for s in labels])
                        k = alignment.record(dataset_id, ic.get("theta", x), labels, None, 0, seed).get("k", 1) \
                            if "theta" in ic else 1
                        order = (k * a) % 113
                        rho, pv = spearman_exact(x, order.astype(float))
                        out.append({"id": dataset_id, "family": fam, "coordinate": cname, "statistic": "Spearman (points)",
                                    "variable": f"position on the k={k} circle", "n": len(x), "rho": rho, "p": pv})
                        continue
                    con = source.concepts(dataset_id, labels, variable=None if v == "bins" else v, n_bins=nb or 7)
                    m = np.array([x[con.index == c].mean() if np.any(con.index == c) else np.nan for c in range(len(con.phase))])
                    rho, pv = spearman_exact(m, np.arange(len(m), dtype=float))
                    out.append({"id": dataset_id, "family": fam, "coordinate": cname, "statistic": "Spearman (concept means)",
                                "variable": con.variable, "n": len(m), "rho": rho, "p": pv,
                                "concept_means": dict(zip([str(s) for s in con.names], np.round(m, 4).tolist()))})
    return out


def harmonic_r2(values: np.ndarray, max_h: int = 3) -> dict:
    """Post hoc: R^2 of fitting a + b cos(h phi) + c sin(h phi) (phi = 2 pi c / n) to per-concept means, h = 1..3.
    A closed curve (cos phi, sin phi, cos 2 phi) - a saddle / tennis-ball-seam loop - shows up as h = 2."""
    z = np.asarray(values, dtype=float)
    n = len(z)
    phi = 2 * np.pi * np.arange(n) / n
    out = {}
    for h in range(1, max_h + 1):
        a = np.c_[np.ones(n), np.cos(h * phi), np.sin(h * phi)]
        c, *_ = np.linalg.lstsq(a, z, rcond=None)
        out[f"h{h}"] = float(1 - ((z - a @ c) ** 2).sum() / ((z - z.mean()) ** 2).sum())
    return out


def run() -> None:
    cfg = config.load()
    out = out_dir("coords")
    env_record("coords")
    recs = []
    for did in source.dataset_ids():
        r = dataset_records(did, cfg["seed"])
        recs.extend(r)
        for q in r:
            log.info("%-26s %-8s %-24s %-22s %s", did, q["family"], q["coordinate"], q["variable"],
                     {k: round(v, 4) if isinstance(v, float) else v for k, v in q.items()
                      if k in ("rho", "p", "R", "winding", "NMI", "ARI")})
    # Post hoc (not preregistered): harmonic content of the axial position of helix fits of cyclic concepts.
    for q in recs:
        if q.get("concept_means") and "axial" in q["coordinate"]:
            q["post_hoc_axial_harmonic_r2"] = harmonic_r2(list(q["concept_means"].values()))
            log.info("post hoc %s axial harmonic R2: %s", q["id"], q["post_hoc_axial_harmonic_r2"])
    write_json(out / "point_coordinates.json", recs)
    pd.DataFrame([{k: v for k, v in q.items() if k != "concept_means"} for q in recs]).to_csv(out / "point_coordinates.csv", index=False)
