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

def test_steering_matrix_includes_both_model_checkpoints():
    p = config.path("results")/"science/h6_datasets.csv"
    if not p.exists():
        pytest.skip("audit tables have not been generated")
    h6 = pd.read_csv(p).set_index("id")
    assert len(h6)==44
    for name in ("C3_grokking_WE_init","C3_grokking_WE_memorised"):
        assert h6.at[name,"model_role"]=="checkpoint control"
        assert h6.at[name,"model"]=="untested"
    assert h6["random_loop_p"].isna().all()

def test_blob_calibration_covers_every_degree_size_and_noise_cell():
    p = config.path("results")/"science/blob_score_strata.csv"
    if not (p.parent/"false_positives.csv").exists():
        pytest.skip("audit tables have not been generated")
    d = pd.read_csv(p).set_index(["dimension","n_bin","noise_bin"])
    expected = {(h,n,k) for h in (1,2) for n in range(4) for k in range(3)}
    assert set(d.index)==expected and (d.n_clouds==250).all()
    assert d.hits.sum()==round((d.rate*d.n_clouds).sum())
    assert d.loc[d.valid_bars>0,"pooled_bar_KS_D"].between(0,1).all()

def test_matched_gaussian_comparison_uses_registered_subset():
    p = config.path("results")/"science"
    if not (p/"benchmark.csv").exists():
        pytest.skip("audit tables have not been generated")
    selection = pd.read_csv(p/"mc_selection.csv")
    assert selection.measured_chunks.eq(1).all() and selection.total_chunks.eq(10).all()
    assert selection.measured_clouds.sum()==3120 and selection.eligible_measured_clouds.sum()==2427
    subset = pd.read_csv(p/"mc_subset.csv").query("target=='catalog' and group=='macro'").set_index("method")
    delta = subset.loc["P_alpha_universal","accuracy"] - subset.loc["MC_gaussian3d","accuracy"]
    assert subset.loc["MC_gaussian3d","P_minus_method"] == pytest.approx(delta)
