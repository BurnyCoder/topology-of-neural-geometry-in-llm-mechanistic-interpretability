"""Check the displayed chains in F2 homology at their paired death simplices.

A shortest path closed by a birth edge can differ from a death-specific representative by an older class.
Test membership in the span of earlier boundaries, then in the enlarged span at death (Edelsbrunner et al.,
https://doi.org/10.1007/s00454-002-2885-2). Integers encode sparse binary simplex chains.
"""
from itertools import combinations
import logging

import gudhi
import numpy as np
import pandas as pd

from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import out_dir
from neurotopo.tda import diagrams

log = logging.getLogger(__name__)


class BoundaryBasis:
    """Echelon basis over F2. A zero remainder certifies that a chain bounds."""
    def __init__(self):
        self.pivots = {}

    def reduce(self, chain):
        while chain:
            pivot = chain.bit_length() - 1
            if pivot not in self.pivots:
                break
            chain ^= self.pivots[pivot]
        return chain

    def insert(self, chain):
        remainder = self.reduce(chain)
        if remainder:
            self.pivots[remainder.bit_length()-1] = remainder


def chain_bits(faces, index):
    """Sum the simplex indicators over the coefficient field used by the alpha analysis."""
    chain = 0
    for f in faces:
        chain ^= 1 << index[tuple(sorted(f))]
    return chain


def certify(y, dim):
    """Check all displayed paths or shells against the filtration and the library's own simplex pairing."""
    tree = gudhi.AlphaComplex(points=y).create_simplex_tree()
    tree.compute_persistence(homology_coeff_field=2, min_persistence=0.)
    ordered = [tuple(sorted(sx)) for sx, _ in tree.get_filtration()]
    rank = {sx: i for i, sx in enumerate(ordered)}
    index = {sx: i for i, sx in enumerate(s for s in ordered if len(s) == dim+1)}
    if dim == 1:
        bars, reps = diagrams.alpha_h1_cycles(y)
    else:
        bars, reps, _ = diagrams.alpha_h2_voids(y)
    by_death, records = {}, []
    for birth, death in tree.persistence_pairs():
        if len(birth) != dim+1 or len(death) != dim+2:
            continue
        b, d = (np.sqrt(max(0.,tree.filtration(sx))) for sx in (birth, death))
        if d-b <= 1e-12*max(1.,b):
            continue
        j = len(records)
        if not np.allclose(bars[j], [b, d], atol=1e-12, rtol=1e-10):
            raise ValueError("Representative and persistence-pair order differ")
        v = reps[j]
        cells = list(zip(v, np.roll(v,-1))) if dim == 1 else v
        cells = [tuple(sorted(sx)) for sx in cells]
        boundary = set()
        for sx in cells:
            boundary.symmetric_difference_update(combinations(sx, dim))
        born = tuple(sorted(birth))
        by_death[tuple(sorted(death))] = (j, chain_bits(cells, index))
        records.append(dict(birth=b, death=d, ratio=d/b, cycle_closed=not boundary,
                            supported_at_birth=born in cells and all(rank[s] <= rank[born] for s in cells)))
    if len(records) != len(bars):
        raise ValueError("Unpaired representatives")
    basis = BoundaryBasis()
    for sx in ordered:
        if len(sx) != dim+2:
            continue
        face_chain = chain_bits(combinations(sx, dim+1), index)
        if sx in by_death:
            j, chain = by_death[sx]
            before = basis.reduce(chain)
            records[j]["nonboundary_before_death"] = bool(before)
            # If before != 0, adding this boundary kills it exactly when chain + boundary was already in span.
            records[j]["bounds_at_death"] = before == 0 or basis.reduce(chain ^ face_chain) == 0
        basis.insert(face_chain)
    records = sorted(records, key=lambda r: -r["ratio"])
    return [dict(k=k, certified=all(r[s] for s in ("cycle_closed","supported_at_birth",
                          "nonboundary_before_death","bounds_at_death")), **r) for k,r in enumerate(records,1)]


def run():
    """Cover every H1/H2 entry, including every example drawn in any gallery or interactive explorer."""
    out = out_dir("science")
    rows = []
    for did in source.dataset_ids():
        y = realdata.cloud(did)["y"]
        for dim in (1, 2):
            rows.extend(dict(id=did, dimension=dim, **r) for r in certify(y, dim))
        log.info("Certified chains for %s", did)
    pd.DataFrame(rows).to_csv(out / "representatives.csv.gz", index=False,
                              compression={"method": "gzip", "mtime": 0})


def analytic_controls():
    """At a stated radius, test unfiltered Betti numbers for four designs with known ideal domains."""
    t = np.linspace(0, 2*np.pi, 96, endpoint=False)
    n = 400
    z = 1 - 2*(np.arange(n)+.5)/n
    phi = np.pi*(3-np.sqrt(5))*np.arange(n)
    sphere = np.column_stack((np.sqrt(1-z*z)*np.cos(phi), np.sqrt(1-z*z)*np.sin(phi), z))
    circle = np.c_[np.cos(t), np.sin(t), np.zeros_like(t)]
    cases = [("circle", circle, (1,1,0)), ("open arc, 120-degree gap", circle[t <= 4*np.pi/3], (1,0,0)),
             ("sphere", sphere, (1,0,1)), ("spherical cap, z >= -0.5", sphere[z >= -.5], (1,0,0))]
    rows = []
    for name, points, target in cases:
        tree = gudhi.AlphaComplex(points=points).create_simplex_tree(output_squared_values=False)
        tree.compute_persistence(homology_coeff_field=2, persistence_dim_max=True)
        betti = tree.persistent_betti_numbers(.30, .30)
        vector = tuple((list(betti)+[0,0,0])[:3])
        rows.append(dict(shape=name, n=len(points), radius=.30, expected=str(target), observed=str(vector),
                         agrees=vector==target))
    pd.DataFrame(rows).to_csv(out_dir("science") / "analytic_controls.csv", index=False)
