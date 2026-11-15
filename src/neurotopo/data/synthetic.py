"""Synthetic clouds of the source project: points, dense ground truth, ground-truth parameters, predictions.

Global context: Exp0 and Exp1 need, for each of the 39,000 test clouds (and 1,560 validation clouds), the
normalised points, the dense noise-free ground truth, the exact ground-truth parameters (regenerated
bit-exactly by scripts/export_source_artifacts.py) and the source fitter's predicted family. All of them are
fetched from the Hugging Face dataset (`run.py fetch`) into data/hf/inputs/synth/.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from neurotopo import config

FAMILIES = ["blob", "clusters", "polytope", "line", "arc", "ellipse", "helix", "ringing", "disc", "sphere",
            "paraboloid", "cone", "torus"]                 # source registry order (neurogeom/shapes/registry.py)
CHUNK = 25                                                  # source testsets.CHUNK: clouds generated per call


@dataclass
class SynthSet:
    """Ragged synthetic clouds; cloud i has points[offsets[i]:offsets[i+1]] and gt_points[gt_offsets[i]:...]."""
    points: np.ndarray
    offsets: np.ndarray
    gt_points: np.ndarray
    gt_offsets: np.ndarray
    meta: pd.DataFrame          # family, sigma, n, embed_dim, n_bin, noise_bin, idx, sample_id, chunk, family_name
    params: list                # describe() dicts of the ground-truth shapes

    def cloud(self, i: int) -> np.ndarray:
        return self.points[self.offsets[i]:self.offsets[i + 1]].astype(np.float64)

    def gt(self, i: int) -> np.ndarray:
        return self.gt_points[self.gt_offsets[i]:self.gt_offsets[i + 1]].astype(np.float64)

    def __len__(self) -> int:
        return len(self.meta)


@lru_cache(maxsize=2)
def load(name: str = "test") -> SynthSet:
    """Load the test (39,000) or val (1,560) set with ground-truth parameters, in the source's cell order."""
    d = config.path("inputs") / "synth"
    z = np.load(d / f"{name}_cells.npz")
    meta = pd.DataFrame({k: z[k] for k in ("family", "sigma", "n", "embed_dim", "n_bin", "noise_bin", "idx")})
    meta["family_name"] = [FAMILIES[f] for f in meta["family"]]
    meta["sample_id"] = [f"{b}-{s}-{i}" for b, s, i in zip(meta["n_bin"], meta["noise_bin"], meta["idx"])]
    per_family = int((meta.groupby(["n_bin", "noise_bin"]).size() // len(FAMILIES)).iloc[0])
    chunk = min(CHUNK, per_family)                           # val set: 10 per family -> one chunk of 10
    # Generator chunk id (clouds of one chunk share N and the embedding draw): (cell, family, index // chunk).
    meta["chunk"] = [f"{b}-{s}-{f}-{(i % per_family) // chunk}" for b, s, f, i in
                     zip(meta["n_bin"], meta["noise_bin"], meta["family"], meta["idx"])]
    with open(d / f"{name}_gt_params.jsonl", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    assert [r["family"] for r in rows] == list(meta["family_name"]), "parameter rows out of order"
    return SynthSet(z["points"], z["offsets"], z["gt_points"], z["gt_offsets"], meta, [r["describe"] for r in rows])


@lru_cache(maxsize=1)
def predictions() -> pd.DataFrame:
    """Source fitter predictions per test cloud and system (per_sample.csv: method, A3, A5, B1-B3, B1_fixed)."""
    return pd.read_csv(config.path("inputs") / "synth" / "per_sample.csv", low_memory=False)


def baseline_subset(meta: pd.DataFrame) -> np.ndarray:
    """Boolean mask of the source's 3,120-cloud baseline subset: first 20 per family in every cell
    (source configs/base.yaml eval.baseline_per_cell = 20)."""
    per_family = int((meta.groupby(["n_bin", "noise_bin"]).size() // len(FAMILIES)).iloc[0])
    return (meta["idx"] % per_family).to_numpy() < 20
