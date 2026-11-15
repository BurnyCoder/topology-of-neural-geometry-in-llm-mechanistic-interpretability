"""Tests for the numpy re-implementation of the source project's PCA normalisation (`fit_frame`).

Global context: every topological statistic is computed on clouds produced by exactly the source's
preprocessing (centre -> top-3 PCs -> skewness sign fix -> right-handed if D == 3 -> RMS radius 1).
The null models re-run this preprocessing on every null draw, so it must be exact and fast.
"""

import json

import numpy as np
import pytest

from neurotopo.data import source
from neurotopo.geometry.pca import fit_frame


def test_rms_radius_is_one_and_centred():
    # A random anisotropic cloud in R^10: output must be centred with RMS radius exactly 1.
    rng = np.random.default_rng(0)
    x = rng.normal(size=(200, 10)) * np.arange(1, 11)
    y, fr = fit_frame(x)
    assert y.shape == (200, 3)
    assert np.allclose(y.mean(0), 0, atol=1e-12)
    assert np.isclose(np.sqrt((y ** 2).sum(1).mean()), 1.0)
    # Explained-variance ordering: eigenvalues are descending.
    assert np.all(np.diff(fr["eigvals"]) <= 1e-9)


def test_skewness_sign_rule_and_rotation_invariance():
    # The sign rule makes the output invariant to rotations of the input (the source's design goal).
    rng = np.random.default_rng(1)
    x = rng.gamma(2.0, size=(300, 5)) * np.array([5, 3, 2, 1, 0.5])
    q, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    y1, _ = fit_frame(x)
    y2, _ = fit_frame(x @ q)
    assert np.allclose(y1, y2, atol=1e-8)
    assert np.all((y1 ** 3).sum(0) >= 0)


def test_top_k_generalisation():
    rng = np.random.default_rng(2)
    x = rng.normal(size=(100, 20))
    y, fr = fit_frame(x, k=10)
    assert y.shape == (100, 10)
    assert np.isclose(np.sqrt((y ** 2).sum(1).mean()), 1.0)


@pytest.mark.parametrize("dataset_id", ["R5a_llama_weekdays", "R2_grokking_WE", "R3_tms_n6", "R7_llama_colors"])
def test_reproduces_source_viz_points(dataset_id):
    # The source stores y * scale rounded to 5 decimals in viz/<id>.json; our frame must reproduce it.
    raw = source.raw_path(dataset_id)
    if not raw.exists():
        pytest.skip("raw activations not fetched yet (run.py fetch)")
    x, _, _ = source.load_raw(dataset_id)
    y, fr = fit_frame(x)
    viz = source.load_viz(dataset_id)
    assert np.abs(y * fr["scale"] - viz["points"]).max() < 1e-4
