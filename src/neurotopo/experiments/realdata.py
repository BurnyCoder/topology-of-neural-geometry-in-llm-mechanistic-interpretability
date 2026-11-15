"""Shared Method B machinery for the 44 real clouds: normalised cloud, alpha diagrams, cached MC nulls.

Global context: Exp2 (invariants) and Exp3 (cyclic hypotheses) both need, per dataset, the source-identical
top-3 PCA cloud, its alpha diagrams, and the design-matched Monte Carlo null distribution of the maximum pi
in H1/H2 (reports/preregistration.md, section 4.3: cluster-centre null for prompt-template designs, full-D
matched Gaussian otherwise; M = 999; seed = crc32(id) + seed). Nulls are expensive, so they are computed once
per (dataset, seed) and cached in results/nulls/<id>_seed<k>.npy.
"""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments.common import out_dir
from neurotopo.geometry.pca import fit_frame
from neurotopo.tda import diagrams, nulls

log = logging.getLogger(__name__)


def design(dataset_id: str) -> str:
    """'cluster' for prompt-template designs (prereg list), else 'gaussian'."""
    return "cluster" if dataset_id in config.load()["groups"]["cluster_designs"] else "gaussian"


def groups(dataset_id: str, labels) -> np.ndarray | None:
    """Concept ids used by the cluster-centre null (concept = day / month / hue)."""
    if design(dataset_id) != "cluster":
        return None
    return source.concepts(dataset_id, [str(s) for s in labels]).index


@lru_cache(maxsize=None)
def cloud(dataset_id: str) -> dict:
    """Raw X, labels, normalised top-3 cloud y and its frame; checks y * scale equals the source's stored points."""
    x, labels, meta = source.load_raw(dataset_id)
    y, fr = fit_frame(x)
    dev = float(np.abs(y * fr["scale"] - source.load_viz(dataset_id)["points"]).max())
    if dev > 1e-3 * fr["scale"]:
        raise RuntimeError(f"{dataset_id}: recomputed cloud deviates from the source by {dev}")
    return {"x": x, "labels": [str(s) for s in labels], "meta": meta, "y": y, "frame": fr, "dev": dev}


@lru_cache(maxsize=None)
def alpha(dataset_id: str) -> list[np.ndarray]:
    return diagrams.alpha_diagrams(cloud(dataset_id)["y"])


def null(dataset_id: str, seed: int) -> np.ndarray:
    """(M, 2) null distribution of max pi in H1, H2 for the dataset's design; cached on disk."""
    path = out_dir("nulls") / f"{dataset_id}_seed{seed}.npy"
    if path.exists():
        return np.load(path)
    c = cloud(dataset_id)
    m = config.load()["tda"]["mc_draws"]
    nm = nulls.null_max_ratios(c["x"], design(dataset_id), groups(dataset_id, c["labels"]), m=m,
                               seed=nulls.dataset_seed(dataset_id, seed), maxdim=2)
    np.save(path, nm)
    log.info("null %s seed %d (%s, M=%d): q95 max pi H1 = %.3f, H2 = %.3f", dataset_id, seed, design(dataset_id),
             m, *np.quantile(nm, 0.95, axis=0))
    return nm


def mc_significance(dataset_id: str, seed: int) -> dict:
    """Per-bar MC p-values (H1, H2) against the max-pi null, and the significance masks (p < alpha)."""
    a = config.load()["tda"]["alpha_level"]
    d = alpha(dataset_id)
    nm = null(dataset_id, seed)
    p = {k: nulls.mc_pvalues(diagrams.ratios(d[k]), nm[:, k - 1]) for k in (1, 2)}
    return {"p": p, "sig": {k: np.nan_to_num(p[k], nan=1.0) < a for k in (1, 2)}, "null_q95": np.quantile(nm, 0.95, axis=0)}
