# Progress

Last updated: 2026-11-20. The step-by-step status table is in [plan.md](plan.md#status); this page says where things stand.

**Done.** Every preregistered topology analysis (Exp0–Exp5), three independent audits (deviations D6, D8, D9), two math fact-checks (D12, D13), the post hoc void and loop searches (D10, D11), the worked example, the paper, the explorer, and the results on Hugging Face. All of it uses stored activations; no model was run.

**Latest step (2026-11-20).** An independent math fact-check, done without relying on the earlier audits: [reviews/math-fact-check-2.md](reviews/math-fact-check-2.md), deviation [D13](deviations.md).
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
