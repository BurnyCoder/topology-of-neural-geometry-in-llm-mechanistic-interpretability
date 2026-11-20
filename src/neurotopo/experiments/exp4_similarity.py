"""Exp4: topological similarity between the 44 real clouds and ideal shape templates (exploratory).

Global context (reports/preregistration.md, section 7): a p-Wasserstein distance sums over every matched bar,
including the near-diagonal noise bars whose number grows with N (true by its definition, e.g. Cohen-Steiner et al.
2010, doi:10.1007/s10208-010-9060-6), so clouds of N = 5..1496 are compared with the bottleneck distance on
*significant* bars only (H0 components from the b0 rule, H1/H2 bars significant under the design-matched MC null),
summed over dimensions. gudhi.bottleneck_distance with e = 0 computes it exactly (GUDHI's CGAL-based implementation
by F. Godi, after Efrat, Itai & Katz 2001, Algorithmica 31:1-28, doi:10.1007/s00453-001-0016-8; not the Hera
implementation, gudhi.hera.bottleneck_distance; https://gudhi.inria.fr/python/latest/bottleneck_distance_user.html).
Discarding bars by a threshold gives up the bottleneck stability theorem (Cohen-Steiner, Edelsbrunner & Harer
2007, doi:10.1007/s00454-006-1276-5): a bar just above the threshold in one cloud and just below it in a nearly
identical cloud changes the distance by about half its length, so this similarity is exploratory only. The
distance matrix gives an MDS map, an average-linkage dendrogram, the nearest ideal template per cloud
(compared with the fitted family), and a permutation test of whether the cyclic group is topologically cohesive.
"""

from __future__ import annotations

import itertools
import logging

import gudhi
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
from sklearn.manifold import MDS

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.geometry.pca import rms_normalise
from neurotopo.tda import diagrams, invariants, nulls

log = logging.getLogger(__name__)


def significant_diagrams(y: np.ndarray, sig1: np.ndarray, sig2: np.ndarray, t: dict) -> list[np.ndarray]:
    """[H0, H1, H2] diagrams restricted to significant bars; H0 keeps finite bars longer than the b0 cut."""
    d = diagrams.alpha_diagrams(y)
    _, thr = invariants.b0_single_linkage(y, t["b0_tau"], t["b0_minfrac"])
    h0 = d[0][np.isfinite(d[0][:, 1]) & (2 * d[0][:, 1] > thr)]
    return [h0, d[1][sig1], d[2][sig2]]


def templates(seed: int) -> dict[str, np.ndarray]:
    """Ideal noisy clouds (RMS-normalised): circle, 7-gon and 12-gon of clusters, helix, sphere, torus, line, blob."""
    rng = np.random.default_rng(seed)
    n = 300
    t = rng.uniform(0, 2 * np.pi, n)
    out = {"circle": np.c_[np.cos(t), np.sin(t), 0 * t]}
    for k, m in ((7, 7), (12, 12)):
        ph = 2 * np.pi * np.repeat(np.arange(k), m) / k
        out[f"{k}-gon of clusters"] = np.c_[np.cos(ph), np.sin(ph), 0 * ph]
    s = rng.uniform(-3 * np.pi, 3 * np.pi, n)
    out["helix"] = np.c_[np.cos(s), np.sin(s), 0.25 * s]
    v = rng.normal(size=(600, 3))
    out["sphere"] = v / np.linalg.norm(v, axis=1, keepdims=True)
    u, w = rng.uniform(0, 2 * np.pi, (2, 1500))
    out["torus"] = np.c_[(1 + 0.4 * np.cos(w)) * np.cos(u), (1 + 0.4 * np.cos(w)) * np.sin(u), 0.4 * np.sin(w)]
    out["line"] = np.c_[rng.uniform(-1, 1, n), 0 * t, 0 * t]
    out["gaussian blob"] = rng.normal(size=(n, 3))
    return {k: rms_normalise(x + 0.03 * rng.normal(size=x.shape)) for k, x in out.items()}


def template_significance(x: np.ndarray, seed: int, m: int = 199):
    """MC significance of a template's H1/H2 bars against a matched Gaussian (here D = 3)."""
    nm = nulls.null_max_ratios(x, "gaussian", None, m=m, seed=seed, maxdim=2)
    d = diagrams.alpha_diagrams(x)
    return [nulls.mc_pvalues(diagrams.ratios(d[k]), nm[:, k - 1]) < 0.05 for k in (1, 2)]


def distance_matrix(dgms: list[list[np.ndarray]]) -> np.ndarray:
    """Sum over dimensions of the bottleneck distance between significant-bar diagrams (gudhi, exact: e=0)."""
    n = len(dgms)
    out = np.zeros((n, n))
    for i, j in itertools.combinations(range(n), 2):
        out[i, j] = out[j, i] = sum(gudhi.bottleneck_distance(dgms[i][k], dgms[j][k], 0.0) for k in range(3))
    return out


def run() -> None:
    cfg = config.load()
    out = out_dir("exp4")
    env_record("exp4")
    t = read_json(config.path("results") / "power" / "val_tuning.json")
    names, dgms, kinds = [], [], []
    for did in source.dataset_ids():
        mc = realdata.mc_significance(did, cfg["seed"])
        dgms.append(significant_diagrams(realdata.cloud(did)["y"], mc["sig"][1], mc["sig"][2], t))
        names.append(did)
        kinds.append(source.real_results()[did]["family"])
    for k, (name, x) in enumerate(templates(cfg["seed"]).items()):
        s1, s2 = template_significance(x, seed=cfg["seed"] + 100 + k)
        dgms.append(significant_diagrams(x, s1, s2, t))
        names.append(f"template: {name}")
        kinds.append("template")
    dm = distance_matrix(dgms)
    emb = MDS(n_components=2, dissimilarity="precomputed", random_state=0, n_init=8).fit_transform(dm)
    link = linkage(squareform(dm, checks=False), method="average")
    nt = len(names) - 44
    # Nearest template(s): every template within 1e-9 of the minimum (clouds without significant features are
    # equidistant from all topologically trivial templates, so ties are reported, not broken by list order).
    def nearest_of(i):
        row = dm[i, 44:]
        tied = np.flatnonzero(row <= row.min() + 1e-9)
        return " / ".join(names[44 + j].replace("template: ", "") for j in tied)
    nearest = {names[i]: nearest_of(i) for i in range(44)}
    # Cohesion of the cyclic group among the 10 cyclic + ordinal datasets (exact over all 4-subsets).
    g = cfg["groups"]
    pool = g["cyclic_primary"] + g["cyclic_secondary"] + g["ordinal"]
    ix = [names.index(p) for p in pool]
    def mean_pair(sub):
        return np.mean([dm[a, b] for a, b in itertools.combinations(sub, 2)])
    obs = mean_pair(ix[:4])
    allm = [mean_pair(s) for s in itertools.combinations(ix, 4)]
    p_coh = float(np.mean(np.array(allm) <= obs + 1e-12))
    pd.DataFrame(dm, index=names, columns=names).to_csv(out / "bottleneck_matrix.csv")
    write_json(out / "summary.json", {"names": names, "kinds": kinds, "mds": emb.tolist(), "linkage": link.tolist(),
                                      "nearest_template": nearest, "n_templates": nt,
                                      "cyclic_cohesion": {"mean_within": obs, "p_exact": p_coh,
                                                          "n_subsets": len(allm)}})
    log.info("cyclic cohesion: mean within %.3f, exact p = %.3f", obs, p_coh)
