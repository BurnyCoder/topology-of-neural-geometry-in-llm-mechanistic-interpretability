# Progress

Last updated: 2026-11-20. The step-by-step status table is in [plan.md](plan.md#status); this page says where things stand.

**Done.** Every preregistered topology analysis (Exp0–Exp5), three independent audits (deviations D6, D8, D9), the post hoc void and loop searches (D10, D11), the worked example, the paper, the explorer, and the results on Hugging Face. All of it uses stored activations; no model was run.

**Latest step (2026-11-20).** A fact-check of the math against the persistent-homology and interpretability literature: [reviews/math-fact-check.md](reviews/math-fact-check.md), deviation [D12](deviations.md).
- Fixed in code: Method B now reads all three Betti numbers at the same scale r_c and uses a Betti label instead of "homotopy class"; the spindle-torus Betti numbers.
- Overstated or mis-cited sentences corrected with sources; 8 new tests.
- Exp2, reports, README, paper and explorer regenerated. No preregistered verdict changed.

**In progress.** Nothing is running.

**Not done (postponed by the author or future work).** These are listed in [plan.md](plan.md#status) and the README to-do:
- steering (simulated and Llama-3.1-8B, preregistered as H6);
- colour controls with model inference;
- the optional Exp0b refit;
- a hole-specific loop test.

Llama steering, the colour controls and Exp0b need model inference, which waits for the author's go-ahead. Simulated steering and the hole-specific test need none; simulated steering is postponed by the author.
