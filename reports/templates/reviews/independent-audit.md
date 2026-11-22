# Independent audit: scientific soundness, hypothesis evaluation, methods and citations

Libor "Burny" Burian, 2026-11-22. Logged as deviation [D14](../deviations.md).

**Question.** Are the results scientifically sound? Are the hypotheses evaluated correctly against the preregistered rules? Are the methods and definitions used the way topological data analysis (TDA), statistics and mechanistic interpretability use them? Is every claim correct and sourced?

Every number below is generated from `results/` by `run.py report` (source: `reports/templates/reviews/independent-audit.md`).

**Independence.** This audit ignored the earlier audits (D6, D8, D9) and fact-checks (D12, D13). It re-read the preregistration, the code, the stored results and every document, and recomputed key quantities. No model was run and nothing was trained.

## Answer in brief

- **No preregistered verdict is wrong.** H1-A {{exp3.H1A}}/3, H1-B {{exp3.H1B}}/3, H2 not falsified, H3 fail (Method A {{exp3.H3.A}}, Method B {{exp3.H3.B}}) and H4 balanced accuracy {{exp3.H4.conj_B:2}} all follow from the rules and the stored results.
- **The core statistics and mathematics are correct and used in the accepted way.** The checked items are listed below.
- **The documentation is in sync with the results.** `run.py report` regenerated every table, number and figure from `results/`, and every committed file came out byte-identical.
- **One claim was refuted by a new control,** run with a decision rule committed before the run:
  - The claim: the ordinal concepts' top-10-PC loops are "consistent with" PCA artefacts of smooth or random-walk curves.
  - The control: the {{audit4.n}} smooth-curve controls in the same test. {{audit4.n_sig}} of {{audit4.n}} have a loop.
- **One mechanism was misdescribed.** The helix fits are unresolvable because their adjacent turns merge into a tube (the margin is the pitch), not because their ends meet.
- **One post hoc claim was overstated.** "The months lie on a closed saddle loop" is now hedged.
- **Smaller wording and citation errors** were also fixed (table below).
- **Missing related work** is now cited: two close precedents and two recent papers.

## Method

- **Read in full:**
  - the preregistration (with A1 and A2), the deviations, the plan, the summary, every report, the README and the paper;
  - `docs/glossary.md`, `docs/methodology.md` and `docs/analytic_topology.md`;
  - `tda/nulls.py`, `tda/diagrams.py`, `tda/circular.py`, `stats/circular.py`, `stats/tests.py`, `analytic/topology.py`, `geometry/pca.py`, `experiments/realdata.py`, `experiments/exp3_cyclic.py`, `experiments/alignment.py` and `experiments/exp0_analytic.py`;
  - the relevant parts of the Exp5, Exp7 and loop-search code.
- **Recomputed from stored data:**
  - the reconstruction of all 44 clouds against the source (maximum absolute deviation {{exp2.source_dev_max:3}}; the run aborts above 10⁻³ of a cloud's scale);
  - Benjamini–Hochberg over the 44 loop tests and over the 44 void tests (two separate families, as documented);
  - the "{{audit3.k12.holefree_pi_ge_real_all}} of {{audit3.k12.holefree_n_all}}" hole-free replicates against the months' loop strength;
  - that the closing step is the largest step for weekdays, months, days_time and colours;
  - the H1–H4 decision logic, from `results/exp3/summary.json` and `results/exp0/real_topology.csv`;
  - the geometry of every helix fit (turns, pitch, end gap, data coverage);
  - the dense-check loops of the helix fits.
- **Regenerated:**
  - `run.py report`: no drift;
  - `pytest`: all tests passed, before and after the changes.
- **Web sources:** three source-checking passes, plus direct checks of every item they flagged. The passes covered the interpretability literature, the TDA and statistics literature, and the tools and documentation. Quotes are short, and statements below are paraphrased.

## What is correct (checked)

| Item | Check |
|---|---|
| Design-(b) null | X* = m̄ + Z X_c/√(N−1) gives rows with covariance X_cᵀX_c/(N−1). The low-rank factor L with LLᵀ = X_cX_cᵀ leaves the null cloud's Gram matrix, and so its PCA scores, unchanged up to rotation. |
| Design-(a) null | Redrawn means Z M_c/√(n−1) have the sample covariance of the means, and within-concept residuals are kept, as preregistered (§4.3). |
| Monte Carlo p | (1 + #{null max ≥ π})/(M + 1) ([Phipson & Smyth 2010](https://doi.org/10.2202/1544-6115.1585)). Testing every bar against the null of the *maximum* is a max-statistic, family-wise test. |
| Universal null | π = d/b; ℓ = A log log π − λ − A L̄ with A = ½ (Čech/alpha) and A = 1 (Rips); p = exp(−e^ℓ); Bonferroni over the diagram. Matches [Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2) and the authors' code (`AVALS = {ALPHA: 0.5, RIPS: 1}`). |
| Alpha complex | GUDHI's squared filtration values are square-rooted. The alpha complex has the persistence of the Čech filtration and the union of balls ([Edelsbrunner 1995](https://doi.org/10.1007/BF02574053) Thm 3.2; [Bauer & Edelsbrunner 2017](https://doi.org/10.1090/tran/6991) Thm 5.10, Cor. 6.1). Rips filtration values are halved to radii. |
| Alignment statistic | R = max_s \|mean e^{i(θ̄_c − sφ_c)}\| is invariant to the origin and orientation of θ. For 7 concepts the exact permutation null has p_min = 14/7! = 1/360 (7 rotations × 2 reflections). For residues, k = 1..56 covers every frequency, because k and 113 − k differ only in orientation. |
| Winding and cyclic order | The winding number is computed on concept means. For residues, the means are taken in the order k·a mod 113. 2/(n−1)! is an upper bound for the implemented criterion. |
| Holm, BH, Clopper–Pearson, exact McNemar, cluster bootstrap | Implemented as defined. |
| H1-B (a) | The minimum p over H1 bars equals the p of the most persistent bar, because p is monotone in π. |
| D8 localisation rule | A bar that dies at or below half the smallest distance between points of different concepts lives inside one concept's union of balls. This is an exact sufficient condition. |
| Method A | Betti numbers, χ, genus, boundary counts and homotopy types for all 13 families, including the frustum (annulus), the horn torus (S² ∨ S¹) and the spindle torus (S² ∨ S² ∨ S¹). The n-gon π = 1/sin(π/n), the octahedron's √(3/2) and the square's √2 are correct. |
| Theorem and page numbers | Hatcher Thm 2.44, Cor. 3.45, Cor. 3.46, Example 0.8, p. 256; de Silva & Ghrist Thm 2.5; Adamaszek & Adams Thm 4.3; Obayashi & Yoshiwaki Cor. 1–2; Bobrowski, Kahle & Skraba Thm 3.1 (homogeneous Poisson process in a cube). |
| Bibliography | Volumes, issues, pages and years agree with Crossref. |
| Tools | GUDHI 3.13.0, ripser 0.6.15, persim 0.4.1 and DREiMac 0.3.2 are installed. DREiMac requires Python < 3.12. Licences are as stated (with the bottleneck addition below). |

## Findings and fixes

| # | Severity | Finding | Evidence | Fix |
|---|---|---|---|---|
| 1 | **Claim refuted** | "The ordinal loops [in the top-10 PCs] are consistent both with Fourier features of numbers and with the PCA artefacts of smooth or random-walk curves; this test cannot tell them apart." The project's 20 smooth-curve controls had never been put through that test. | New phase `audit4` (D14), with its decision rule committed (3a62958) before the run: **{{audit4.n_sig}} of {{audit4.n}}** controls are significant; their largest Rips ratio is {{audit4.pi_max:3}}, against null thresholds of {{audit4.q95_min:2}}–{{audit4.q95_max:2}}. Pre-specified verdict: {{audit4.decision}}. In Antognini & Sohl-Dickstein's formula (PC_k ∝ cos(kπt)), PC1 is monotone, so the projected curve stays open in 3 or 10 dimensions. | README caption, Exp5 report and paper: the ordinal loops need structure the controls lack (periodic number features, clusters, or noise around a curve). The controls contain no independent noise, so noise is not ruled out. |
| 2 | Mechanism misdescribed | "Whether the helices are open or closed is unresolvable": the docs explained ρ_A < 1 as "its two ends are closer than the noise". | All {{exp0.helix_n}} helix fits are tight coils ({{exp0.prim_turns_min:1}}–{{exp0.prim_turns_max:1}} turns for the cyclic sets), and for {{exp0.helix_pitch_margin_n}} of {{exp0.helix_n}} the margin is the **pitch**, not the end gap. In noise-scale units the ends are {{exp0.weekdays.endgap_rho:2}}, {{exp0.months.endgap_rho:2}} and {{exp0.grok.endgap_rho:2}} × 2ν apart for weekdays, months and residues; the residue fit's ends are resolvably apart. The dense check's one persistent loop per helix fit is the tube that adjacent turns form. The conclusion (the fit cannot tell open from closed) stands, because the thickened coil has one loop around its axis. | `analytic.topology.helix_end_gap` (shared by Method A and the report) and a new test. Wording in the README, summary, paper, Exp0 report, glossary and methodology. Generated numbers: `exp0.helix_pitch_margin_n`, `exp0.*.turns`, `exp0.*.endgap_rho`. |
| 3 | Overclaim (post hoc) | "The months lie on a closed saddle loop" (paper; summary). | The harmonic fit z = a + b cos 2φ + c sin 2φ is periodic by construction, so it assumes closure. In 3D the December → January step is the largest of the 12 ({{audit.loc.months.lastfirst:2}}× the median). | Reworded to "the shape of a closed saddle loop, but the periodic fit assumes closure", with the closing step quoted. |
| 4 | Overstated citation | Engels et al. "did not steer along the circles". | They set the circle-subspace projection to a target angle, and in Mistral swept a grid of (r, θ) inside the circle ([§5](https://arxiv.org/html/2405.14860v3)). | They did not steer along a continuous fitted path. |
| 5 | Missing related work | The Gap and novelty statements omitted close precedents. | [Gardinazzi et al. 2025](https://arxiv.org/abs/2410.11042), App. C: zigzag barcodes of the 12 month tokens in Mistral, without a null. The [shouvik-majumder re-implementation](https://github.com/shouvik-majumder/circular-features): weekday and month loops "correctly ordered" and beyond a covariance-matched Gaussian null, with no statistics, not peer reviewed. [Gupta, Fruengel & Heimersheim 2026](https://arxiv.org/abs/2610.37796): weekdays behave like seven discrete states. [Karkada et al. 2026](https://arxiv.org/abs/2602.15029): month circles from translation symmetry. | Added to the literature and state-of-the-art reviews, the README novelty bullet and the paper's Gap paragraph (new bib entry). The "no peer-reviewed null-controlled loop-plus-order test" claim still holds. |
| 6 | Wrong attribution | Methodology attributed PCA horseshoes of Gaussian processes and random walks to Diaconis, Goel & Holmes (2008), whose subject is MDS and kernel projections. | Diaconis et al. abstract; [Novembre & Stephens 2008](https://doi.org/10.1038/ng.139) show sinusoidal PCs from spatial covariance. | Novembre & Stephens for distance-decaying covariance, Antognini & Sohl-Dickstein for random walks, Diaconis et al. for MDS. |
| 7 | Misdescription | Antognini & Sohl-Dickstein: "closed-looking figures in higher pairs". | The paper gives PC_k ∝ cos(kπt); the curves are open. Some 2D pairs cross themselves, but the 3D and 10D curves stay open. | Reworded, with D14 as the empirical check. |
| 8 | Imprecise citation | Erickson 2003: "Ω(n^{3/2}) for evenly spaced points on a helix". | Thm 2.3 is an existence result for a helix with about √n points per turn. Lemma 2.1: every point is joined to every point less than a full turn away, so a fixed helix with T turns has about n²/T edges. | Reworded in the docs and the code comment. |
| 9 | Pointer errors | Niyogi, Smale & Weinberger "sampling theorem (Prop. 3.1)"; Obayashi & Yoshiwaki "Example 1: 1 in 10,000". | Prop. 3.1 is the deterministic covering condition, and the random-sample result is Thm 3.1. Example 1 is the Möbius band; the 1-in-10,000 count is in §8. | Glossary fixed. |
| 10 | Licence scope | NOTICE and README: only GUDHI's alpha complex is GPL-3.0. | `gudhi/bottleneck.py` also declares `__license__ = "GPL v3"`, and Exp4 calls it. | NOTICE, README and literature-review table. |
| 11 | Tool list | persim is listed as used for "diagram distances, plotting". | It is never imported; it is installed as a dependency of ripser.py and DREiMac. Its 0.4.1 wheel is pure Python, not cp311-specific (plan.md). | README, NOTICE, review table and plan. |
| 12 | Wording | README: the random-init loop at p = {{exp2.grokinit.p_top_loop}} is "about what the 5% level predicts". The voids paragraph: "none of the other 14 trained-model clouds". Exp2: "two random-init or toy controls cross the 5% line, consistent with the nominal error rate". | P(at least one of 3 below 0.05) = 0.14. The 14 include the two clouds discussed just before them. The dense toy model's loop survives Benjamini–Hochberg (q = {{exp2.tmsdense.q_loop:3}}) and is a 4-cycle of its polytope, not a chance hit. | Reworded with generated numbers. |
| 13 | Precision | "Comes back in only 1% of subsamples" for a fraction {{exp2.wposinit.void_freq:3}} of 200. The clean-room to-do omitted the phases added or rerun after 2026-11-15. D3 calls a rule "preregistered" that is in `plan.md`. | `results/exp2/invariants.csv`; `results/replication.json` (2026-11-15). Commit b6cc417 pushed `plan.md` with the preregistration. | Fraction quoted; to-do completed; D14 notes the D3 source. |
| 14 | Metadata | Nanda et al.'s venue was listed as unverified; the README wrote "Engels et al. 2024". | The [ICLR 2023 oral page](https://iclr.cc/virtual/2023/oral/12572) lists Nanda et al. Engels et al. was accepted to ICLR 2025. | Removed from "not verified"; "Engels et al. 2025". |

## What a skeptical reviewer would still say

- **The headline evidence is per dataset and mostly post hoc.** The strict preregistered conjunctions pass for nothing ({{exp3.H1A}}/3, {{exp3.H1B}}/3). The positive claims carry the post hoc and audit labels the documents give them:
  - colours, a ring inherited from the stimuli;
  - residues, a ring on the traversal;
  - months, suggestive.
- **The loop test is not hole-specific** (D9). This audit adds that the ordinal top-10 loops are not explained by smooth-curve PCA artefacts either. Their source is unknown.
- **Small numbers of controls** (three random-init networks) give weak calibration, as the documents say.
- **The primary hypothesis since amendment A2, steering (H6), is untested.** It is postponed by the author.

## Not verified

- The paraphrase of Engels et al. §5 and Gardinazzi et al. App. C rests on the source-checking passes' reading of the HTML. The quoted Gardinazzi sentence (§3.2) and the shouvik-majumder README quotes were read verbatim.
- The content of Fasy et al., Robinson & Turner, Vejdemo-Johansson & Mukherjee, Anai et al., Adams et al., Bubenik and Chazal et al. 2015. Only metadata was checked; these are cited for context only.
- The full texts of Gupta et al. 2026 and Karkada et al. 2026. Only their abstracts were read, and they are cited for what the abstracts say.
