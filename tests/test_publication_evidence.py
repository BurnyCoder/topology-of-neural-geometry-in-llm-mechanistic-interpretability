"""Release-level regressions against a fixed, independently checked study corpus."""
import pandas as pd
import pytest

from neurotopo import config


def test_published_vector_and_outlier_denominators():
    root = config.path("results")
    if not (root/"science/false_positives.csv").exists():
        pytest.skip("audit tables have not been generated")
    h4 = pd.read_csv(root/"science/h4_datasets.csv")
    fp = pd.read_csv(root/"science/false_positives.csv").set_index(["cohort","comparison"])
    assert (len(h4), int(h4.H4_full_vector.sum()), int(h4.b1_b2_only.sum())) == (44,27,31)
    assert tuple(fp.loc[("catalog","flagged"),["hits","n"]]) == (350,4144)
    assert tuple(fp.loc[("six families","flagged"),["hits","n"]]) == (230,3547)


def test_paired_angular_rank_reversals_and_known_gap_controls():
    root = config.path("results")/"science"
    if not (root/"benchmark.csv").exists():
        pytest.skip("audit tables have not been generated")
    rows = pd.read_csv(root/"benchmark.csv").set_index(["target","group","method"])
    for family in ("arc","sphere"):
        assert rows.at[("catalog",family,"Bb_family_implied"),"P_minus_method"] > 0
        assert rows.at[("angular",family,"Bb_family_implied"),"P_minus_method"] < 0
    controls = pd.read_csv(root/"analytic_controls.csv")
    assert len(controls)==4 and controls.agrees.all()
    assert set(controls.Bc_majority) == {"(1, 0, 0)"}
    for estimator in ("P_alpha_universal", "S_rips_universal", "Ba_fixed_pi"):
        assert controls[estimator].str.fullmatch(r"\(\d+, \d+, \d+\)").all()
    assert controls.Bb_family_implied.isna().all()
    assert (controls.Ba_fixed_pi == controls.expected).all()
    assert (controls.P_alpha_universal == controls.expected).tolist() == [False, True, False, True]
