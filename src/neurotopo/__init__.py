"""neurotopo: topology of top-3-PCA neural activation clouds.

Global context: the sibling project (git submodule `external/shape-fitting`) fitted one of 13 uniquely
parametrised geometric shape families to each top-3-PCA activation cloud. This package (a) reads off the
exact topology of every fitted shape from its parameters (Method A, `neurotopo.analytic`), (b) measures the
topology of the point clouds themselves with persistent homology (Method B, `neurotopo.tda`), and (c) tests
whether semantically cyclic concepts (weekdays, months, residues mod 113) "travel around" a hole
(`neurotopo.stats.circular`). `run.py` at the repository root calls the experiment phases in order.
"""

__version__ = "0.1.0"
