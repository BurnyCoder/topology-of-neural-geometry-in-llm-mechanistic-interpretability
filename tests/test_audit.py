"""Tests for the post hoc audit checks (experiments/exp7_audit.py, deviation D8).

Global context: the audit asks (1) whether the colour stimulus set itself already has the hue loop, and (2) whether
the most persistent loop of a prompt-template cloud lies inside a concept cluster or runs through the clusters.
These tests pin the stimulus builder to the source's prompt grid and check the localisation rule on clouds whose
answer is known by construction.
"""

import numpy as np

from neurotopo.data import source
from neurotopo.experiments.exp7_audit import bar_scale, colour_stimuli
from neurotopo.geometry.pca import rms_normalise
from neurotopo.tda import diagrams


def test_colour_stimuli_match_source_grid():
    # 36 hues x 5 saturations x 5 lightnesses, labels "hue|sat|lum" parsed into 36 hue concepts of 25 prompts each.
    rgb, labels = colour_stimuli()
    assert rgb.shape == (900, 3) and len(labels) == 900
    assert labels[0] == "0|0.4|0.25" and labels[-1] == "350|1.0|0.75"
    con = source.concepts("R7_llama_colors", labels)
    assert np.bincount(con.index).tolist() == [25] * 36
    assert rgb.min() >= 0 and rgb.max() <= 255
    # Pure red at full saturation and mid lightness is #ff0000.
    assert rgb[labels.index("0|1.0|0.5")].tolist() == [255.0, 0.0, 0.0]


def _clusters(centres, m, spread, rng, micro=False):
    """m points per centre; with micro=True each cluster is a small circle (a loop inside the cluster)."""
    pts, idx = [], []
    for c, mu in enumerate(centres):
        if micro:
            t = 2 * np.pi * np.arange(m) / m
            p = mu + spread * np.c_[np.cos(t), np.sin(t), np.zeros(m)]
        else:
            p = mu + spread * rng.normal(size=(m, 3))
        pts.append(p)
        idx += [c] * m
    return rms_normalise(np.concatenate(pts)), np.array(idx)


def test_bar_scale_ring_of_clusters_is_not_within_concept():
    # 7 tight clusters on a ring: the top loop runs through the clusters (dies far beyond the cluster radius).
    rng = np.random.default_rng(0)
    t = 2 * np.pi * np.arange(7) / 7
    y, idx = _clusters(np.c_[np.cos(t), np.sin(t), np.zeros(7)], 7, 0.02, rng)
    r = bar_scale(y, idx, diagrams.alpha_diagrams(y)[1])
    assert not r["within_concept_loop"]
    assert r["means_top_pi1"] > 2.0          # a regular 7-gon has pi = 1 / sin(pi / 7) ~ 2.3


def test_bar_scale_flags_loop_inside_clusters_on_an_arc():
    # 7 clusters on an open 180-degree arc, each cluster a small circle: the only loops are inside clusters.
    rng = np.random.default_rng(0)
    t = np.pi * np.arange(7) / 6
    y, idx = _clusters(np.c_[np.cos(t), np.sin(t), np.zeros(7)], 12, 0.08, rng, micro=True)
    r = bar_scale(y, idx, diagrams.alpha_diagrams(y)[1])
    assert r["within_concept_loop"]
    assert r["means_top_pi1"] < 1.2          # the arc of cluster means has no persistent loop
