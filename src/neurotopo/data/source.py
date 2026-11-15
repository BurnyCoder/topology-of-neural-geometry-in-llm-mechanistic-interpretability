"""Access to the source project's real clouds, fitted shapes and raw activations; concept labels and phases.

Global context: the sibling project (git submodule `external/shape-fitting`, commit 4c5f3b6) stores, per
dataset, the preprocessed top-3 PCA cloud with labels and dense samples of the fitted shape
(`results/main_s0/real/viz/<id>.json`), the fitter's output (`real_results.json`), and, locally only, the raw
activation matrix (`data_cache/real/<id>.npz`), which this project republishes on Hugging Face and fetches to
`data/source/real/`. This module also turns the stored labels into *concepts* (which points belong to the
same day, month, residue, ...) and their *semantic phases* phi_c, the inputs of the travel-around-the-hole
test (reports/preregistration.md, sections 2 and 5).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from neurotopo import config

# Concept orders, copied from the source's prompt builders (external/shape-fitting/src/neurogeom/realdata/llm_sets.py:34-35).
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def viz_path(dataset_id: str) -> Path:
    """Preprocessed cloud + labels + fitted-shape samples of one dataset (tracked in the submodule)."""
    return config.source_run_dir() / "real" / "viz" / f"{dataset_id}.json"


def raw_path(dataset_id: str) -> Path:
    """Raw activation matrix fetched from Hugging Face (`run.py fetch`)."""
    return config.path("inputs") / "real" / f"{dataset_id}.npz"


@lru_cache(maxsize=None)
def load_viz(dataset_id: str) -> dict:
    """Return {points (N,3) un-normalised top-3 PCA coordinates, labels list[str], shape (M,3) fitted-shape samples}."""
    with open(viz_path(dataset_id), encoding="utf-8") as f:
        d = json.load(f)
    return {"points": np.asarray(d["points"], dtype=np.float64), "labels": [str(s) for s in d["labels"]],
            "shape": np.asarray(d["shape"], dtype=np.float64).reshape(-1, 3)}


def load_raw(dataset_id: str) -> tuple[np.ndarray, np.ndarray, dict]:
    """Raw activations X (N, D) float64, labels (N,) object array, meta dict (source `save_cloud` format)."""
    z = np.load(raw_path(dataset_id), allow_pickle=True)   # labels are a pickled object array (source format)
    return z["X"].astype(np.float64), z["labels"], json.loads(str(z["meta"]))


@lru_cache(maxsize=1)
def real_results() -> dict:
    """The source fitter's output per dataset: family, probabilities, canonical params, diagnostics."""
    with open(config.source_run_dir() / "real" / "real_results.json", encoding="utf-8") as f:
        return {d["id"]: d for d in json.load(f)}


def dataset_ids() -> list[str]:
    """All 44 real dataset ids, in the source's order."""
    return list(real_results().keys())


@dataclass
class Concepts:
    """Concept structure of a cloud for the alignment test.

    index: (N,) concept id of every point (0..n-1); phase: (n,) semantic phase phi_c in radians;
    names: concept names; cyclic: True if the concept variable is semantically cyclic (prereg groups).
    """
    index: np.ndarray
    phase: np.ndarray
    names: list
    cyclic: bool
    variable: str


def _equal_bins(values: np.ndarray, n: int) -> Concepts:
    """Ordinal variable -> n equal-width bins of its range; bin b gets phase 2*pi*b/n (prereg, section 5)."""
    v = values.astype(np.float64)
    edges = np.linspace(v.min(), v.max(), n + 1)
    idx = np.clip(np.searchsorted(edges, v, side="right") - 1, 0, n - 1)   # max value falls in the last bin
    names = [f"[{edges[b]:.4g}, {edges[b + 1]:.4g}]" for b in range(n)]
    return Concepts(idx, 2 * np.pi * np.arange(n) / n, names, False, f"value in {n} bins")


def chronological_half_hour(t: np.ndarray) -> np.ndarray:
    """Source time index t in 0..47 -> chronological half-hour 0..47 with 12:00 AM = 0.

    Source order (llm_sets.py:58): [f"{h}:{m:02d} {ap}" for ap in (AM, PM) for h in 1..12 for m in (0, 30)],
    so t -> ap = t // 24, h = (t % 24) // 2 + 1, m = 30 * (t % 2), and hour24 = h % 12 + 12 * (ap == PM).
    """
    ap, h, m = t // 24, (t % 24) // 2 + 1, 30 * (t % 2)
    return ((h % 12) + 12 * ap) * 2 + m // 30


def concepts(dataset_id: str, labels: list[str], variable: str | None = None, n_bins: int = 7) -> Concepts:
    """Concepts and semantic phases for a dataset (reports/preregistration.md, section 2).

    variable: for R5c, "day" (default) or "time"; for numeric sets, "bins" (default) or "mod10"/"mod100"
    (exploratory base-10 periodicity); n_bins: number of equal-width bins for ordinal sets.
    """
    lab = list(labels)
    n_pts = len(lab)
    if dataset_id in ("R5a_llama_weekdays", "C3_llama_weekdays_init", "R5a_llama_weekdays_means") or \
            (dataset_id == "R5c_llama_days_time" and variable in (None, "day")):
        idx = np.array([DAYS.index(s) for s in lab])
        return Concepts(idx, 2 * np.pi * np.arange(7) / 7, DAYS, True, "day of week")
    if dataset_id == "R5c_llama_days_time" and variable == "time":
        t = chronological_half_hour(np.arange(n_pts) % 48)          # row i: day i // 48, time i % 48
        return Concepts(t, 2 * np.pi * np.arange(48) / 48, [f"{(k // 2):02d}:{30 * (k % 2):02d}" for k in range(48)],
                        True, "time of day")
    if dataset_id in ("R5b_llama_months", "C3_llama_months_init", "R5b_llama_months_means"):
        idx = np.array([MONTHS.index(s) for s in lab])
        return Concepts(idx, 2 * np.pi * np.arange(12) / 12, MONTHS, True, "month")
    if dataset_id in ("R2_grokking_WE", "C3_grokking_WE_init", "C3_grokking_WE_memorised"):
        a = np.array([int(s) for s in lab])
        # Base phase 2*pi*a/113; the alignment test multiplies it by the Fourier frequency k (max over k).
        return Concepts(a, 2 * np.pi * np.arange(113) / 113, [str(i) for i in range(113)], True, "residue mod 113")
    if dataset_id == "R7_llama_colors":
        hue = np.array([int(s.split("|")[0]) for s in lab])          # labels "hue|sat|lum", hue in degrees
        idx = hue // 10                                               # 36 hues, 10 degrees apart
        return Concepts(idx, 2 * np.pi * np.arange(36) / 36, [f"{10 * i} deg" for i in range(36)], True, "hue")
    # Numeric ordinal sets (positions, counts, years, temperatures, ages, ordinal-process indices).
    try:
        values = np.array([float(s) for s in lab])
    except ValueError as exc:
        raise ValueError(f"{dataset_id}: no concept structure defined") from exc
    if variable in ("mod10", "mod100"):
        p = 10 if variable == "mod10" else 100
        idx = (values.astype(int) % p)
        return Concepts(idx, 2 * np.pi * np.arange(p) / p, [str(i) for i in range(p)], True, f"value mod {p}")
    return _equal_bins(values, n_bins)
