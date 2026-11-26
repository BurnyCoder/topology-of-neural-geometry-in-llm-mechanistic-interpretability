"""Replay alpha nulls from original activations and calibrate the fitted-null test (Dufour 2006)."""

import logging

import gudhi
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.linalg import eigh
from scipy.stats import binomtest
from threadpoolctl import threadpool_limits

from neurotopo import config
from neurotopo.data import hub, source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import out_dir, write_json
from neurotopo.tda import nulls

log = logging.getLogger(__name__)


def scores(x, k):
    """An independent PCA implementation, using the smaller scatter matrix and unit RMS radius."""
    x = x - x.mean(axis=0)
    n, d = x.shape
    dim = min(n, d)
    span = [max(0, dim - k), dim - 1]
    if n <= d:
        val, vec = eigh(x @ x.T, subset_by_index=span)
        y = vec[:, ::-1] * np.sqrt(np.maximum(val[::-1], 0))
    else:
        _, vec = eigh(x.T @ x, subset_by_index=span)
        y = x @ vec[:, ::-1]
    return y / max(np.sqrt((y * y).sum(axis=1).mean()), 1e-12)


def observed_max(y):
    """GUDHI can return radii directly. Independently check the pipeline's squared-radius conversion."""
    tree = gudhi.AlphaComplex(points=y, precision="safe").create_simplex_tree(output_squared_values=False)
    tree.compute_persistence(homology_coeff_field=2, persistence_dim_max=True)
    stats = []
    for dim in (1, 2):
        bars = tree.persistence_intervals_in_dimension(dim)
        keep = (bars[:, 0] > 0) & np.isfinite(bars[:, 1])
        bars = bars[keep]
        stats.append(np.max(bars[:, 1] / bars[:, 0], initial=1.))
    return np.array(stats)


def replay():
    """Generate every seed-zero array and primary robustness seed before reading its deposited counterpart."""
    inputs = config.path("inputs")
    count = hub.verify(inputs)
    out = out_dir("science")
    ref = pd.read_csv(config.path("results") / "exp2/invariants.csv").set_index("id")
    rows = []
    with threadpool_limits(1):
        for did in source.dataset_ids():
            x, labels, _ = source.load_raw(did)
            obs = observed_max(scores(x, 3))
            seeds = [0, 1, 2] if did in config.load()["groups"]["cyclic_primary"] else [0]
            for seed in seeds:
                fresh = nulls.null_max_ratios(x, realdata.design(did), realdata.groups(did, labels),
                                              config.load()["tda"]["mc_draws"], nulls.dataset_seed(did, seed))
                archive = np.load(config.path("results") / "nulls" / f"{did}_seed{seed}.npy")
                if fresh.shape != archive.shape:
                    raise ValueError(f"{did}: null draw shape differs")
                # Rank counts carry the actual hypothesis decision. Small numerical draw differences are recorded.
                for j, name in enumerate(("loop", "void")):
                    ref_pi = ref.loc[did, f"top_pi{j + 1}"]
                    rank = int(np.sum(fresh[:, j] >= obs[j]))
                    p = (1 + rank) / (1 + len(fresh))
                    old = (1 + np.sum(archive[:, j] >= ref_pi)) / (1 + len(archive))
                    rows.append(dict(id=did, seed=seed, dimension=j+1, draws=len(fresh), observed=obs[j],
                                     reference_observed=ref_pi, exceedances=rank, p=p, deposited_p=old,
                                     max_draw_difference=np.max(np.abs(fresh[:, j] - archive[:, j])),
                                     registered_p=ref.loc[did, f"p_top_{name}"] if seed == 0 else None,
                                     same_decision=(p < .05) == (old < .05)))
            log.info("Fresh nulls checked for %s", did)
            pd.DataFrame(rows).to_csv(out / "null_replay.csv", index=False)
    write_json(out / "inputs.json", {"verified_files": count, "hf_revision": config.load()["hf"]["revision"],
                                    "source_commit": config.load()["source_commit"]})


def simulate_one(n_groups, copies, fixed_residual, seed):
    """Draw from a known population, fit its nuisance covariance anew, and obtain Monte Carlo ranks."""
    rng = np.random.default_rng(seed)
    means = rng.normal(size=(n_groups, 6)) * np.array([1., .85, .7, .55, .4, .25])
    groups = np.repeat(np.arange(n_groups), copies)
    x = means[groups] + fixed_residual
    kind = "gaussian" if copies == 1 else "cluster"
    maxima = nulls.null_max_ratios(x, kind, groups, 99, int(rng.integers(2**32)), n_jobs=1)
    return (1 + np.sum(maxima >= observed_max(scores(x, 3)), axis=0)) / (1 + len(maxima))


def calibration():
    """Marginal binomial intervals for independent outer datasets, conditional on one residual template."""
    out = out_dir("science")
    draws, rates = [], []
    for design, c, m in [("weekdays", 7, 7), ("months", 12, 12), ("residues", 113, 1)]:
        template_seed, *seeds = np.random.SeedSequence([20261126, c]).spawn(129)
        residual = np.random.default_rng(template_seed).normal(0, .12, (c, m, 6))
        residual -= residual.mean(axis=1, keepdims=True)
        pv = Parallel(n_jobs=-1)(delayed(simulate_one)(c, m, residual.reshape(-1, 6), seed) for seed in seeds)
        for rep, v in enumerate(pv):
            draws.append(dict(design=design, replicate=rep, p_loop=v[0], p_void=v[1]))
        for k in (0, 1):
            hits = int((np.array(pv)[:, k] < .05).sum())
            ci = binomtest(hits, len(pv)).proportion_ci(method="exact")
            rates.append(dict(design=design, n=c*m, dimension=k+1, hits=hits, replicates=len(pv),
                              rate=hits/len(pv), low=ci.low, high=ci.high, exchangeable_rank_rate=.04))
        log.info("Completed fitted-null calibration for %s", design)
    pd.DataFrame(draws).to_csv(out / "calibration_draws.csv", index=False)
    pd.DataFrame(rates).to_csv(out / "calibration.csv", index=False)
