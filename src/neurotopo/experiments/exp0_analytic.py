"""Exp0: exact topology of the fitted shapes (Method A) and the travel-around-the-hole test on them.

Global context (reports/preregistration.md, sections 3, 5, 6): every source fit is a uniquely parametrised
shape, so its Betti numbers, chi, genus and boundary components are exact. This phase
1. computes them for the 44 real fits, with the margin ratio rho_A = m / (2 nu) that says whether the fitted
   topology is resolvable at the cloud's noise scale;
2. reads off the hole coordinate theta_A of every point on fits that have a hole (closed arc, ellipse,
   frustum, torus) and, descriptively, the axial winding of helix fits, and runs the alignment test
   (H1-A for weekdays/months/grokking, H2-A for ordinal sets and controls);
3. computes the exact ground-truth topology and rho_A of all 40,560 synthetic clouds (primary ground truth of
   Exp1);
4. checks the analytic rules numerically: persistent homology of dense noise-free samples of the shapes.
"""

from __future__ import annotations

import logging
import os

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from neurotopo import config
from neurotopo.analytic import coords
from neurotopo.analytic.topology import shape_topology
from neurotopo.data import source, synthetic
from neurotopo.experiments import alignment
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.tda import diagrams
from neurotopo.tda.ground_truth import margin_ratio, noise_scale

log = logging.getLogger(__name__)
PARAMETRISED = {"line", "arc", "ellipse", "helix", "ringing", "disc", "paraboloid", "sphere", "cone", "torus"}
HOLE_FAMILIES = {"arc", "ellipse", "cone", "torus"}          # families that can have b1 >= 1
DENSE_N, DENSE_N_CURVE, DENSE_PI = 10000, 2000, 4.0          # dense check sizes; bars with pi > 4 count


def shape_noise(family: str, params: dict, points: np.ndarray, gt_points: np.ndarray | None = None) -> dict:
    """nu of a cloud w.r.t. a shape (reports/deviations.md D2): exact point-to-shape distances on a fine
    parameter grid and 2,000 area-uniform shape samples for the coverage term (point sets: their points)."""
    if family in PARAMETRISED:
        d_ps = coords.intrinsic_coords(family, params, points, curve_n=4096, surface_n=256)["dist"]
        shp = coords.random_samples(family, params, 2000, seed=0)
        return noise_scale(points, shp, d_ps)
    if family == "clusters":
        return noise_scale(points, np.asarray(params["centroids"]))
    if family == "polytope":
        return noise_scale(points, np.asarray(params["vertices"]))
    return noise_scale(points, gt_points if gt_points is not None else points.mean(0, keepdims=True))


def real_fit(dataset_id: str, seed: int) -> tuple[dict, list[dict]]:
    """Method A invariants, margin ratio and alignment records of one real fit."""
    rr = source.real_results()[dataset_id]
    fam, params = rr["family"], rr["params"]
    viz = source.load_viz(dataset_id)
    pts, labels = viz["points"], viz["labels"]
    topo = shape_topology(fam, params)
    ns = shape_noise(fam, params, pts)
    rho = margin_ratio(topo["margin"], ns["nu"])
    row = {"id": dataset_id, "family": fam, "N": len(pts), **{k: topo[k] for k in
           ("b0", "b1", "b2", "chi", "genus", "n_boundary", "dim", "homotopy", "margin")},
           **ns, "rho_A": rho, "resolvable": bool(rho >= config.load()["analytic"]["resolvable_ratio"]),
           "hole": bool(topo["b1"] >= 1)}
    recs = []
    if fam in HOLE_FAMILIES and topo["b1"] >= 1:
        ic = coords.intrinsic_coords(fam, params, pts)
        angles = {"theta": ic["theta"]} if fam != "torus" else {"longitude": ic["theta"], "meridian": ic["theta2"]}
        for name, th in angles.items():
            for r in alignment.records(dataset_id, th, labels, seed):
                recs.append({"id": dataset_id, "coordinate": name, "kind": "hole", **r})
    elif fam == "helix":
        ic = coords.intrinsic_coords(fam, params, pts)
        for v, nb in alignment.variables(dataset_id):
            r = alignment.record(dataset_id, ic["theta"], labels, v, nb, seed)
            rec = {"id": dataset_id, "coordinate": "azimuth", "kind": "axial winding (descriptive)", **r}
            if dataset_id not in alignment.GROK:
                rec.update(helix_closure(dataset_id, labels, ic, params, v, nb))
            recs.append(rec)
    return row, recs


def helix_closure(dataset_id: str, labels: list[str], ic: dict, params: dict, variable, n_bins: int) -> dict:
    """Closure gap of a helix fit: axial distance between the first and last concept means divided by the
    radius (0 for a closed circle), and the mean axial drift per concept step (descriptive, prereg section 3)."""
    con = source.concepts(dataset_id, labels, variable=None if variable == "bins" else variable, n_bins=n_bins or 7)
    n = len(con.phase)
    z = np.array([ic["axial"][con.index == c].mean() if np.any(con.index == c) else np.nan for c in range(n)])
    r = float(params["radius"])
    return {"closure_gap": float(abs(z[-1] - z[0]) / r), "axial_step": float(np.nanmean(np.diff(z)) / r)}


def synth_row(sset: synthetic.SynthSet, i: int) -> dict:
    """Exact ground-truth invariants and rho_A of synthetic cloud i (normalised frame)."""
    fam = sset.meta["family_name"].iat[i]
    p = sset.params[i]
    topo = shape_topology(fam, p)
    ns = shape_noise(fam, p, sset.cloud(i), sset.gt(i))
    rho = margin_ratio(topo["margin"], ns["nu"])
    return {"b0": topo["b0"], "b1": topo["b1"], "b2": topo["b2"], "chi": topo["chi"], "margin": topo["margin"],
            "nu": ns["nu"], "noise": ns["noise"], "coverage": ns["coverage"], "rho_A": rho}


def synth_table(name: str) -> pd.DataFrame:
    """Ground-truth topology table of the test or val set (parallel over clouds)."""
    sset = synthetic.load(name)
    rows = Parallel(n_jobs=-1, batch_size=64)(delayed(synth_row)(sset, i) for i in range(len(sset)))
    df = pd.concat([sset.meta.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    df["resolvable"] = df["rho_A"] >= config.load()["analytic"]["resolvable_ratio"]
    return df


def dense_points(family: str, params: dict) -> np.ndarray:
    """The dense noise-free sample of a shape used by the dense check (also reused by the D9 audit's torus check)."""
    curve = family not in coords.SURFACES
    pts = coords.random_samples(family, params, DENSE_N_CURVE if curve else DENSE_N, seed=0)
    # Noise-free samples on a space curve can have a Delaunay triangulation of superlinear size (Erickson 2003,
    # doi:10.1007/s00454-003-2927-4: Omega(n^{3/2}) for a helix with about sqrt(n) points per turn, Thm 2.3; every
    # point is joined to every point less than a full turn away, Lemma 2.1, so about n^2 / T edges for T turns;
    # here 10,000 helix points exhausted 10 GB), and flat / co-circular samples are degenerate inputs where CGAL's
    # exact predicates become very slow. A small jitter (1e-3 of the RMS radius for curves, 1e-6 for surfaces)
    # makes the input generic; it is far below every feature scale that is counted (pi > 4).
    rms = float(np.sqrt(((pts - pts.mean(0)) ** 2).sum(1).mean()))
    return pts + (1e-3 if curve else 1e-6) * rms * np.random.default_rng(1).normal(size=pts.shape)


def dense_check(family: str, params: dict) -> dict:
    """Persistent homology of 10,000 dense noise-free samples: bars with pi > 4 vs the analytic b1, b2."""
    t = shape_topology(family, params)
    pts = dense_points(family, params)
    d = diagrams.alpha_diagrams(pts)
    # The exact topology holds at scales below the topological margin m: a feature born at ~m/2 is a
    # near-closure (e.g. the two ends of a helix whose gap m is small), which rho_A already quantifies.
    # Count only persistent features (pi > 4) born below m / 4.
    cut = t["margin"] / 4 if np.isfinite(t["margin"]) else np.inf
    b1, b2 = (int(((diagrams.ratios(d[k]) > DENSE_PI) & (d[k][:, 0] < cut)).sum()) for k in (1, 2))
    near = int(((diagrams.ratios(d[1]) > DENSE_PI) & (d[1][:, 0] >= cut)).sum())
    d0 = diagrams.alpha_diagrams(pts[:2000], maxdim=0)[0][:, 1]
    h = 2 * float(np.median(d0[np.isfinite(d0)]))         # typical sample spacing (H0 death = half the MST edge)
    return {"family": family, "b1_exact": t["b1"], "b2_exact": t["b2"], "b1_dense": b1, "b2_dense": b2,
            "near_closure_loops": near,
            "margin_over_spacing": t["margin"] / h if h > 0 else np.inf,
            "agree": (b1, b2) == (t["b1"], t["b2"])}


def _real_check(dataset_id: str, family: str) -> dict:
    return {"source": "real", "id": dataset_id, **dense_check(family, source.real_results()[dataset_id]["params"])}


def _synth_check(family: str, sample_id: str, params: dict) -> dict:
    return {"source": "synthetic", "id": sample_id, **dense_check(family, params)}


def _reuse(path) -> bool:
    """NEUROTOPO_REUSE=1 skips parts whose output exists (development only; `run.py all` recomputes)."""
    return os.environ.get("NEUROTOPO_REUSE") == "1" and path.exists()


def run() -> None:
    cfg = config.load()
    out = out_dir("exp0")
    env_record("exp0")
    seed = cfg["seed"]
    # 1-2. Real fits.
    rows, recs = [], []
    for did in source.dataset_ids():
        row, rr = real_fit(did, seed)
        rows.append(row)
        recs.extend(rr)
        log.info("%-28s %-9s b=(%d,%d,%d) chi=%d rho_A=%.2f records=%d", did, row["family"], row["b0"], row["b1"],
                 row["b2"], row["chi"], row["rho_A"], len(rr))
    real = pd.DataFrame(rows)
    real.to_csv(out / "real_topology.csv", index=False)
    write_json(out / "real_alignment.json", recs)
    # 3. Synthetic ground truth (test + val).
    for name in ("test", "val"):
        if _reuse(out / f"synth_{name}_topology.csv.gz"):
            continue
        df = synth_table(name)
        df.to_csv(out / f"synth_{name}_topology.csv.gz", index=False)
        log.info("synthetic %s: %d clouds, %.1f%% resolvable", name, len(df), 100 * df["resolvable"].mean())
    # 4. Dense numeric check: every parametrised real fit + 20 ground-truth shapes per parametrised family.
    checks = Parallel(n_jobs=4)(delayed(_real_check)(r["id"], r["family"]) for r in rows if r["family"] in PARAMETRISED)
    sset = synthetic.load("test")
    for fam in sorted(PARAMETRISED):
        idx = np.flatnonzero(sset.meta["family_name"].to_numpy() == fam)[::150][:20]
        checks += Parallel(n_jobs=4)(delayed(_synth_check)(fam, sset.meta["sample_id"].iat[i], sset.params[i])
                                      for i in idx)
    dc = pd.DataFrame(checks)
    dc.to_csv(out / "dense_check.csv", index=False)
    resolved = dc["margin_over_spacing"] >= 4
    write_json(out / "summary.json", {
        "dense_check_agreement_all": float(dc["agree"].mean()),
        "dense_check_agreement_margin_ge_4_spacings": float(dc.loc[resolved, "agree"].mean()),
        "dense_check_n": int(len(dc)), "dense_check_n_resolved": int(resolved.sum())})
    log.info("dense check: %.1f%% agree (%.1f%% where margin >= 4 spacings, n=%d)", 100 * dc["agree"].mean(),
             100 * dc.loc[resolved, "agree"].mean(), resolved.sum())
