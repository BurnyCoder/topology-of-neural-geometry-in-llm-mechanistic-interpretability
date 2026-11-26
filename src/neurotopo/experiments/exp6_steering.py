"""Exp6 (primary after amendment A2): semantically meaningful manifold steering around topologically detected holes.

Global context: the user's primary hypothesis is that whenever topology finds a hole in a concept's activation
cloud, moving the concept token's activation around the loop that encircles the hole makes the model's answer
go around the concept cycle (Monday -> Tuesday -> ... -> Monday), as in manifold steering (Wurgaft et al. 2026,
arXiv:2605.05115), and that topology finds such holes more easily than geometric shape fitting. For each task
(reports/preregistration.md, amendment A2):
- loops: B (fit-free: theta_B-binned periodic spline), A (the fitted shape's circle around its axis), the
  linear chord path through ordered concept centroids, and M = 20 random loops (same centre and radius, random
  plane in the top-10 PC space);
- steering: h(Delta) = h + (gamma(phi + Delta) - gamma(phi)) @ basis^T in un-normalised top-k PCA coordinates,
  at hidden_states[layer] of the steered token, Delta = 2 pi j / K, K = 4 n;
- readout: next-token distribution over the concept words; per prompt R, winding, in-vocabulary mass;
- decision: T(loop B) > random loops (p < 0.05), |winding| = 1 for >= 50% of prompts, mean mass >= 0.5.
Requires `uv sync --extra steer`, a CUDA GPU and access to the gated meta-llama/Llama-3.1-8B.
"""

from __future__ import annotations

import logging

import numpy as np
import torch

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.geometry.pca import fit_frame
from neurotopo.stats import circular as cs
from neurotopo.tda.nulls import dataset_seed
from neurotopo.steering import loops, metrics, models, tasks
from neurotopo.tda import circular

log = logging.getLogger(__name__)
M_RANDOM = 20


def task_rows(task: tasks.Task) -> np.ndarray:
    """Row of the source cloud for each task prompt (same template, same order as the source's builders)."""
    if task.dataset_id in ("R5a_llama_weekdays", "R5b_llama_months"):
        return np.arange(len(task.prompts))
    if task.dataset_id == "R5c_llama_days_time":
        # source order: row = day * 48 + t, t over [h:mm AM/PM for ap in (AM, PM) for h in 1..12 for m in (0, 30)]
        t_index = {"1:00 AM": 0, "7:30 AM": 13, "1:00 PM": 24, "7:30 PM": 37}
        return np.array([p.concept * 48 + t_index[p.steer_text.split("It's ")[1].split(" on")[0]] for p in task.prompts])
    if task.dataset_id == "R7_llama_colors":
        return np.array([p.concept * 25 + 3 * 5 + 2 for p in task.prompts])   # saturation 0.85 (idx 3), lightness 0.5 (idx 2)
    raise ValueError(task.dataset_id)


def steer_positions(tok, task: tasks.Task) -> list[int]:
    """Index of the last token of steer_text inside the tokenised full prompt (asserting the prefix matches)."""
    pos = []
    for p in task.prompts:
        full = tok(p.text).input_ids
        pre = tok(p.steer_text).input_ids
        assert full[:len(pre)] == pre, f"prefix tokenisation differs: {p.text!r}"
        pos.append(len(pre) - 1)
    return pos


def run_loop(model, tok, task, loop: loops.Loop, z: np.ndarray, basis: np.ndarray, pos: list[int], idx: np.ndarray,
             word_ids: list[int], k_steps: int) -> list[dict]:
    """Steer prompts idx around one loop (coordinates z, basis D x k) and return per-prompt traversal metrics."""
    deltas = 2 * np.pi * np.arange(k_steps) / k_steps
    texts, spos, dh = [], [], []
    for i in idx:
        for d in deltas:
            texts.append(task.prompts[i].text)
            spos.append(pos[i])
            dh.append(loop.displacement(z[i:i + 1], d)[0] @ basis.T)
    probs, mass = models.readout_probs(model, tok, texts, spos, np.array(dh), task.layer, word_ids)
    out = []
    for a, i in enumerate(idx):
        sl = slice(a * k_steps, (a + 1) * k_steps)
        psi = metrics.decode_phase(probs[sl], task.phases, task.decode)
        tr = metrics.traversal(psi, deltas)
        out.append({"prompt": int(i), **tr, "vocab_mass": float(mass[sl].mean()),
                    "answers": [task.words[j] for j in probs[sl].argmax(1)]})
    return out


def llama_task(model, tok, task: tasks.Task, seed: int) -> dict:
    x, labels, _ = source.load_raw(task.dataset_id)
    y, fr = fit_frame(x)
    z = y * fr["scale"]                                                   # un-normalised top-3 PCA coordinates
    rows = task_rows(task)
    pos = steer_positions(tok, task)
    word_ids = models.word_token_ids(tok, task.words)
    # Check: the model's hidden state at the steered token equals the analysed cloud (same weights / template).
    h = models.hidden_at(model, tok, [p.steer_text for p in task.prompts], task.layer)
    rel_err = float(np.max(np.linalg.norm(h - x[rows], axis=1) / np.linalg.norm(x[rows], axis=1)))
    zt = (x[rows] - fr["mean"]) @ fr["basis"]                             # prompts' coordinates (exact cloud rows)
    k_steps = 4 * task.n if task.n <= 12 else 72
    con = source.concepts(task.dataset_id, [str(s) for s in labels])
    # Loop B (fit-free) from the persistent-cohomology coordinate of the whole cloud.
    cc = circular.circular_coordinates(y)
    res = {"dataset": task.dataset_id, "hidden_rel_err": rel_err, "k_steps": k_steps, "n_prompts": len(task.prompts)}
    loop_set = {}
    if cc["theta"] is not None:
        loop_set["B_cohomology"] = loops.loop_from_coordinate(z, cc["theta"], n_bins=loops.steering_bins(task.n))
    rr = source.real_results()[task.dataset_id]
    if rr["family"] in ("helix", "cone"):
        loop_set["A_fitted_axis_circle"] = None                           # built per prompt (height-dependent)
    cen = np.stack([z[con.index == c].mean(0) for c in range(len(con.phase))])
    loop_set["chord_centroids"] = loops.chord_path(cen)
    all_idx = np.arange(len(task.prompts))
    for name, lp in loop_set.items():
        if name == "A_fitted_axis_circle":
            res[name] = fitted_axis_loop(model, tok, task, rr, zt, fr, pos, all_idx, word_ids, k_steps)
        else:
            per = run_loop(model, tok, task, lp, zt, fr["basis"], pos, all_idx, word_ids, k_steps)
            res[name] = {"per_prompt": per, **metrics.dataset_statistic(per)}
        log.info("%s %s: %s", task.dataset_id, name, {k: v for k, v in res[name].items() if k != "per_prompt"})
    # Random-loop null on a fixed prompt subset (one prompt per concept: the first offset), same centre/radius.
    sub = np.array([np.flatnonzero(np.array([p.concept for p in task.prompts]) == c)[0] for c in range(task.n)
                    if np.any(np.array([p.concept for p in task.prompts]) == c)])
    if "B_cohomology" in loop_set:
        y10, fr10 = fit_frame(x, k=10)
        z10 = ((x[rows] - fr10["mean"]) @ fr10["basis"])
        lb = loop_set["B_cohomology"]
        centre10 = ((lb.pts.mean(0) @ fr["basis"].T + fr["mean"]) - fr10["mean"]) @ fr10["basis"]
        rng = np.random.default_rng(seed)
        t_null = []
        for _ in range(M_RANDOM):
            rl, _ = loops.random_loop(centre10, lb.radius, np.eye(10), rng)
            per = run_loop(model, tok, task, rl, z10, fr10["basis"], pos, sub, word_ids, k_steps)
            t_null.append(metrics.dataset_statistic(per)["T"])
        per_b = [p for p in res["B_cohomology"]["per_prompt"] if p["prompt"] in set(sub.tolist())]
        t_obs = metrics.dataset_statistic(per_b)["T"]
        res["random_null"] = {"T_subset_B": t_obs, "T_random": t_null, "p": metrics.null_pvalue(t_obs, np.array(t_null))}
        b = res["B_cohomology"]
        res["H6_pass"] = bool(res["random_null"]["p"] < 0.05 and b["frac_wind1"] >= 0.5 and b["vocab_mass"] >= 0.5)
    else:
        res.update(H6_pass=None, missing_endpoint="coordinate unavailable")
    return res


def fitted_axis_loop(model, tok, task, rr, zt, fr, pos, idx, word_ids, k_steps) -> dict:
    """Loop A for helix / cone fits: the circle around the fitted axis at each prompt's own axial height
    (helix radius; cone radius r_bot + dr * s at that height). Parameters are in un-normalised PCA coordinates."""
    p = rr["params"]
    c, ax = np.asarray(p["center"]), np.asarray(p["axes"])
    per = []
    for i in idx:
        hgt = float((zt[i] - c) @ ax[2])
        if rr["family"] == "helix":
            rad = lambda _h: float(p["radius"])
        else:
            rad = lambda h: float(p["r_bot"]) + float(p["dr"]) * np.clip((h / float(p["half_height"]) + 1) / 2, 0, 1)
        lp = loops.azimuth_loop(c, ax, rad, hgt)
        per += run_loop(model, tok, task, lp, zt, fr["basis"], pos, np.array([i]), word_ids, k_steps)
    return {"per_prompt": per, **metrics.dataset_statistic(per)}


@torch.no_grad()
def grok_readout(model, steer_vecs: np.ndarray, a_idx: np.ndarray, b_vals: list[int], p: int = 113) -> np.ndarray:
    """Decoded steered residue a_hat = (argmax logits - b) mod p for every (steer vector, a, b); shape (n, len(b))."""
    dev = next(model.parameters()).device
    out = np.zeros((len(a_idx), len(b_vals)), int)
    for j, b in enumerate(b_vals):
        toks = torch.stack([torch.as_tensor(a_idx), torch.full((len(a_idx),), b), torch.full((len(a_idx),), p)], 1).to(dev)
        logits = model(toks, steer=torch.as_tensor(steer_vecs, dtype=torch.float32, device=dev))
        if logits.shape[-1] != p:
            raise ValueError("The full output vocabulary must consist of the residue classes for mass one")
        out[:, j] = (logits.argmax(-1).cpu().numpy() - b) % p
    return out


def grok_steer(model, w: np.ndarray, label: str, seed: int, b_vals=(0, 14, 28, 42, 56, 70, 84, 98)) -> dict:
    """Steer W_E[a] (position-0 residual) around loops of the model's own W_E cloud; decode a_hat on the
    k*-circle (k* = Fourier frequency best aligned with theta_B, max over k as in Exp3)."""
    p = w.shape[0]
    y, fr = fit_frame(w)
    z = y * fr["scale"]
    cc = circular.circular_coordinates(y)
    res = {"model": label}
    if cc["theta"] is None:
        res.update(theta_B=None, H6_pass=None, missing_endpoint="coordinate unavailable")
        return res
    a = np.arange(p)
    r, k, s = cs.max_over_frequency(cc["theta"], a, p, 56)
    res.update({"k_star": k, "R_alignment": r})
    k_steps = 2 * p
    deltas = 2 * np.pi * np.arange(k_steps) / k_steps
    order = np.argsort((k * a) % p)                                       # residues in k*-circle order
    cen = z[order]
    loop_set = {"B_cohomology": loops.loop_from_coordinate(z, cc["theta"], n_bins=loops.steering_bins(p)),
                "chord_centroids": loops.chord_path(cen)}
    def evaluate(lp, coords, basis, idx, offsets=b_vals):
        per = []
        for i in idx:
            dh = np.stack([lp.displacement(coords[i:i + 1], d)[0] @ basis.T for d in deltas])
            ahat = grok_readout(model, dh, np.full(k_steps, i), list(offsets))
            for j in range(len(offsets)):
                psi = 2 * np.pi * k * ahat[:, j] / p
                per.append({"a": int(i), "b": int(offsets[j]), **metrics.traversal(psi, deltas), "vocab_mass": 1.0})
        return per
    for name, lp in loop_set.items():
        per = evaluate(lp, z, fr["basis"], a)
        res[name] = {**metrics.dataset_statistic(per), "per_prompt": per}
        log.info("grokking %s %s: %s", label, name, {kk: v for kk, v in res[name].items() if kk != "per_prompt"})
    y10, fr10 = fit_frame(w, k=10)
    z10 = y10 * fr10["scale"]
    lb = loop_set["B_cohomology"]
    centre10 = ((lb.pts.mean(0) @ fr["basis"].T + fr["mean"]) - fr10["mean"]) @ fr10["basis"]
    rng = np.random.default_rng(dataset_seed("grok" + label, seed))
    # One fixed prompt per residue for the matched B-versus-random comparison (amendment A2).
    first_offset = b_vals[0]
    t_null = [metrics.dataset_statistic(evaluate(loops.random_loop(centre10, lb.radius, np.eye(10), rng)[0], z10,
                                                 fr10["basis"], a, (first_offset,)))["T"] for _ in range(M_RANDOM)]
    t_obs = metrics.dataset_statistic([q for q in res["B_cohomology"]["per_prompt"] if q["b"] == first_offset])["T"]
    res["random_null"] = {"T_subset_B": t_obs, "T_random": t_null, "p": metrics.null_pvalue(t_obs, np.array(t_null))}
    b = res["B_cohomology"]
    res["H6_pass"] = bool(res["random_null"]["p"] < 0.05 and b["frac_wind1"] >= 0.5 and b["vocab_mass"] >= 0.5)
    return res


def grokking(seed: int) -> dict:
    """Retrain the source's grokked model (identical recipe and seed), compare its W_E with the analysed cloud,
    and steer the trained model and its initial / memorised checkpoints (controls)."""
    out = out_dir("exp6")
    model, snaps = models.train_grokking(seed=seed)
    src = source.load_raw("R2_grokking_WE")[0]
    res = {"test_acc": snaps["test_acc"], "max_abs_diff_vs_source_W_E": float(np.abs(snaps["final"] - src).max())}
    torch.save({"final": model.state_dict(), "memorised": snaps["memorised_state"], "init": snaps["init_state"]},
               out / "grokking_model.pt")
    model.eval()
    res["trained"] = grok_steer(model, snaps["final"], "trained", seed)
    for name in ("memorised", "init"):
        ctl = models.OneLayerTransformer().to(next(model.parameters()).device)
        ctl.load_state_dict(snaps[f"{name}_state"])
        ctl.eval()
        res[name] = grok_steer(ctl, snaps[name], name, seed)
    return res


def run() -> None:
    cfg = config.load()
    out = out_dir("exp6")
    env_record("exp6")
    models.env_hf_home()
    torch.manual_seed(cfg["seed"])
    write_json(out / "grokking_steering.json", grokking(cfg["seed"]))
    model, tok = models.load_llama()
    results = {}
    for did, make in tasks.TASKS.items():
        results[did] = llama_task(model, tok, make(), cfg["seed"])
        write_json(out / "llama_steering.json", results)
    del model
    torch.cuda.empty_cache()
