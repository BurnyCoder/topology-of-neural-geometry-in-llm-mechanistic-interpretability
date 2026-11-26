# Progress

**26 November 2026.** The independent replay recovered the registered H1 decision. The [audit report](reviews/2026-11-26-scientific-audit.md) records the changes to H4 agreement, H5 eligibility, near-closure scoring, path certificates and calibration. The [study result tables](../results/science/) contain the current observations. Both steering phases remain untested.


The full synthetic replay completed in the working checkout. A Ripser worker aborted during the independent checkout's first attempt. The replay now writes complete batches atomically and caps simultaneous native workers. The [replication record](../results/science/reproduction.json) reports the numerical comparisons for the completed replay. [Batch implementation](../src/neurotopo/experiments/exp1_batches.py)

## Archived progress on 22 November 2026

The table in [plan.md](plan.md#status) records the status at that date.

**Done.** Every preregistered topology analysis (Exp0–Exp5), four independent audits (deviations D6, D8, D9, D14), two math fact-checks (D12, D13), the post hoc void and loop searches (D10, D11), the worked example, the paper, the explorer, and the results on Hugging Face. All of it uses stored activations; no model was run.

**Latest step (2026-11-22).** An independent audit of soundness, hypothesis evaluation, methods and citations, done without relying on the earlier audits: [reviews/independent-audit.md](reviews/independent-audit.md), deviation [D14](deviations.md).
- No preregistered verdict is wrong, and every document regenerates from `results/` without drift.
- **Negative result for a documented explanation:**
  - The claim: the ordinal concepts' top-10 loops are consistent with PCA artefacts of smooth or random-walk curves.
  - The test: a new post hoc control, with its decision rule committed before the run (`run.py audit4`).
  - The result: none of the 20 smooth-curve controls has such a loop, so that explanation is not supported. The source of those loops stays open.
- Corrected: the helix margin is the pitch (adjacent turns), not the end gap; the months' saddle-loop claim is hedged; Engels et al. did intervene on the circle angle; missing related work, attributions, the GUDHI licence scope and the persim role. 1 new test.

**Before that (2026-11-20).** An independent math fact-check: [reviews/math-fact-check-2.md](reviews/math-fact-check-2.md), deviation [D13](deviations.md).
- Every definition, theorem, statistic and citation was checked against its primary source. The core mathematics holds.
- Fixed: mis-citations (bottleneck implementation, Hatcher numbering, universal-null sample sizes, the assumptions of Bobrowski, Kahle & Skraba, helix Delaunay size, PCA horseshoes) and imprecise wording (the margin, the cyclic-order p, the DREiMac guarantee, general position); 1 new test.
- Reports, README and paper regenerated. No code path, number or preregistered verdict changed.
- Before that, the first fact-check ([reviews/math-fact-check.md](reviews/math-fact-check.md), [D12](deviations.md)) fixed the Method B invariants and the spindle-torus Betti numbers.

**In progress.** Nothing is running.

**Not done (postponed by the author or future work).** These are listed in [plan.md](plan.md#status) and the README to-do:
- steering (simulated and Llama-3.1-8B, preregistered as H6);
- colour controls with model inference;
- the optional Exp0b refit;
- a hole-specific loop test.

Llama steering, the colour controls and Exp0b need model inference, which waits for the author's go-ahead. Simulated steering and the hole-specific test need none; simulated steering is postponed by the author.
