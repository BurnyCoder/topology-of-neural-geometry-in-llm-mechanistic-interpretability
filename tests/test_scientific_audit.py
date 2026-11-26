"""Regression cases for the registered cohort, catalog targets and persistence representatives."""

import numpy as np
import pandas as pd

from neurotopo.experiments.exp1_synthetic import contractible_cohort
from neurotopo.experiments.exp2_invariants import agreement, save_summary
from neurotopo.science.benchmark import angular_target
from neurotopo.science.cycles import BoundaryBasis
from neurotopo.stats.circular import order_test


def test_false_positive_denominator_uses_the_specific_shape():
    rows = pd.DataFrame(dict(family_name=["arc", "sphere", "arc", "sphere", "line", "clusters"],
                             b0=[1, 1, 1, 1, 1, 3], b1=[0, 0, 1, 0, 0, 0],
                             b2=[0, 0, 0, 1, 0, 0], resolvable=[True, True, True, True, False, True]))
    assert contractible_cohort(rows).tolist() == [True, True, False, False, False, False]


def test_catalog_flag_and_raw_domain_define_distinct_targets():
    for family, key, closed in [("arc", "extent_frac", (1, 1, 0)), ("sphere", "cap_frac", (1, 0, 1))]:
        assert angular_target(family, {key: 0.999}, closed) == (1, 0, 0)
        assert angular_target(family, {key: 1.0}, closed) == closed
    assert angular_target("torus", {}, (1, 2, 1)) == (1, 2, 1)


def test_full_agreement_includes_components():
    df = pd.DataFrame(dict(A_b0=[1, 1], A_b1=[1, 0], A_b2=[0, 0], b0=[2, 1], b1_mc=[1, 0], b2_mc=[0, 0]))
    assert agreement(df).tolist() == [False, True]


def test_historical_and_clean_invariant_tables_have_the_same_schema(tmp_path):
    base = pd.DataFrame([dict(id="sample", A_b0=1, A_b1=0, A_b2=0, b0=2, b1_mc=0, b2_mc=0,
                              p_top_loop=0.25, p_top_void=0.75)])
    save_summary(base, tmp_path)
    expected = (tmp_path/"invariants.csv").read_bytes()
    archived = base.assign(agree_b1b2=False, q_top_loop=0, q_top_void=0)
    save_summary(archived, tmp_path)
    assert (tmp_path/"invariants.csv").read_bytes() == expected


def test_order_test_for_nonmatch_and_adaptive_frequency():
    assert order_test(False, 7)["order_p"] == 1
    assert np.isclose(order_test(True, 7)["order_p"], 1 / 360)
    assert np.isclose(order_test(True, 7, 3)["order_p"], 3 / 360)


def test_cycle_can_survive_a_different_triangles_death():
    basis = BoundaryBasis()
    older, younger = 0b111, 0b111000
    basis.insert(younger)
    assert basis.reduce(younger) == 0
    assert basis.reduce(older ^ younger) != 0

def test_frequency_permutation_repeats_search_with_duplicate_residues():
    from neurotopo.stats.circular import max_over_frequency, max_over_frequency_pvalue

    a = np.array([0, 0, 2, 3, 5, 6, 6, 4])
    theta = np.array([.5, 1.1, -2., 2.2, .4, -.6, 2.8, .9])
    rng = np.random.default_rng(815)
    obs = max_over_frequency(theta, a, 7, 3)[0]
    hits = sum(max_over_frequency(theta, rng.permutation(a), 7, 3)[0] >= obs-1e-12 for _ in range(99))
    assert max_over_frequency_pvalue(theta, a, 7, 3, 99, np.random.default_rng(815)) == (1+hits)/100


def test_certificates_use_the_death_simplex_and_are_closed():
    from neurotopo.science.cycles import certify

    rng = np.random.default_rng(4)
    records = certify(rng.normal(size=(65,3)), 1)
    assert all(r["cycle_closed"] and r["nonboundary_before_death"] for r in records)
    assert any(r["certified"] for r in records)
    assert any(not r["bounds_at_death"] for r in records)
