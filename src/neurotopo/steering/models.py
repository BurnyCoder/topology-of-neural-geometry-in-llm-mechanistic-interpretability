"""Models for steering: Llama-3.1-8B with a residual-stream steering hook, and the grokked modular-addition model.

Global context (preregistration amendment A2): the analysed clouds are hidden states of
meta-llama/Llama-3.1-8B in bf16 (source: hidden_states[layer] at the concept token; external/shape-fitting/src/
neurogeom/realdata/common.py, load_truncated / token_acts), and the embedding matrix W_E of a 1-layer
transformer grokked on (a + b) mod 113 with the Nanda et al. (2023, arXiv:2301.05217) recipe (source
realdata/weights_sets.py: OneLayerTransformer, grokking). The source did not keep the grokked model, so it is
retrained here with the identical code and seed and published on Hugging Face.
Steering adds a displacement to hidden_states[layer] at one token position: hidden_states[layer] is the output
of decoder block layer - 1 (HF convention: hidden_states[0] = embeddings), so a forward hook on
model.model.layers[layer - 1] that edits its output implements it.
Requires the optional dependency group `steer` (torch, transformers, accelerate): uv sync --extra steer.
"""

from __future__ import annotations

import contextlib
import logging
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

log = logging.getLogger(__name__)
LLAMA = "meta-llama/Llama-3.1-8B"


# ----------------------------------------------------------------------------- Llama
def load_llama(max_gpu_gib: float = 6.5):
    """Full Llama-3.1-8B in bf16 (the precision of the analysed clouds); layers that do not fit on the 8 GB GPU
    are offloaded to CPU by accelerate (big-model inference), as in the source's load_truncated."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(LLAMA)
    model = AutoModelForCausalLM.from_pretrained(LLAMA, torch_dtype=torch.bfloat16, device_map="auto",
                                                 max_memory={0: f"{max_gpu_gib}GiB", "cpu": "28GiB"})
    model.eval()
    return model, tok


@contextlib.contextmanager
def steer_hook(model, layer: int, positions: torch.Tensor, delta: torch.Tensor):
    """Add delta[b] (D) to the output of decoder block layer - 1 at token position positions[b] of batch row b."""
    block = model.model.layers[layer - 1]

    def hook(_module, _inp, out):
        hs = out[0] if isinstance(out, tuple) else out
        rows = torch.arange(hs.shape[0], device=hs.device)
        hs[rows, positions.to(hs.device)] += delta.to(hs.device, hs.dtype)
        return out

    h = block.register_forward_hook(hook)
    try:
        yield
    finally:
        h.remove()


@torch.no_grad()
def hidden_at(model, tok, texts: list[str], layer: int, batch: int = 16) -> np.ndarray:
    """hidden_states[layer] at the last token of each text (right padding), float32 (N, D)."""
    tok.padding_side = "right"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    out = []
    for s in range(0, len(texts), batch):
        enc = tok(texts[s:s + batch], return_tensors="pt", padding=True).to("cuda")
        hs = model(**enc, output_hidden_states=True).hidden_states[layer]
        last = enc["attention_mask"].sum(-1) - 1
        out.append(hs[torch.arange(hs.shape[0], device=hs.device), last].float().cpu().numpy())
    return np.concatenate(out)


def word_token_ids(tok, words: list[str]) -> list[int]:
    """First token id of ' word' for each readout word (Llama-3 tokens carry the leading space)."""
    return [tok.encode(" " + w, add_special_tokens=False)[0] for w in words]


@torch.no_grad()
def readout_probs(model, tok, texts: list[str], steer_pos: list[int], deltas: np.ndarray, layer: int,
                  word_ids: list[int], batch: int = 16) -> tuple[np.ndarray, np.ndarray]:
    """Next-token probabilities at the last position with a steering displacement at steer_pos.

    Returns (probabilities over word_ids renormalised within the vocabulary subset, total probability mass on
    word_ids) for every text."""
    tok.padding_side = "right"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    probs, mass = [], []
    ids = torch.tensor(word_ids, device="cuda")
    for s in range(0, len(texts), batch):
        enc = tok(texts[s:s + batch], return_tensors="pt", padding=True).to("cuda")
        last = enc["attention_mask"].sum(-1) - 1
        pos = torch.tensor(steer_pos[s:s + batch])
        dl = torch.tensor(deltas[s:s + batch], dtype=torch.float32)
        with steer_hook(model, layer, pos, dl):
            logits = model(**enc).logits
        p = torch.softmax(logits[torch.arange(logits.shape[0], device=logits.device), last].float(), -1)
        sub = p[:, ids]
        mass.append(sub.sum(-1).cpu().numpy())
        probs.append((sub / sub.sum(-1, keepdim=True)).cpu().numpy())
    return np.concatenate(probs), np.concatenate(mass)


# ----------------------------------------------------------------------------- grokked modular addition
class OneLayerTransformer(nn.Module):
    """Copied from the source (external/shape-fitting/src/neurogeom/realdata/weights_sets.py, MIT): Nanda et al.
    2023 architecture, embed + learned pos-embed, 1 attention layer, 1 ReLU MLP, unembed, no LayerNorm.
    Input [a, b, =]; the logits at '=' predict (a + b) mod p. `steer` adds a displacement to the residual
    stream at position 0 (the embedding of a), the analogue of steering W_E[a]."""

    def __init__(self, p: int = 113, d: int = 128, heads: int = 4, d_mlp: int = 512):
        super().__init__()
        self.W_E = nn.Parameter(torch.randn(p + 1, d) / d ** 0.5)
        self.W_pos = nn.Parameter(torch.randn(3, d) / d ** 0.5)
        self.attn = nn.MultiheadAttention(d, heads, bias=False, batch_first=True)
        self.mlp_in, self.mlp_out = nn.Linear(d, d_mlp), nn.Linear(d_mlp, d)
        self.W_U = nn.Parameter(torch.randn(d, p) / d ** 0.5)

    def forward(self, tokens: torch.Tensor, steer: torch.Tensor | None = None) -> torch.Tensor:
        h = self.W_E[tokens] + self.W_pos
        if steer is not None:
            h = h.clone()
            h[:, 0] = h[:, 0] + steer
        mask = torch.triu(torch.ones(3, 3, dtype=torch.bool, device=h.device), 1)
        h = h + self.attn(h, h, h, attn_mask=mask, need_weights=False)[0]
        h = h + self.mlp_out(F.relu(self.mlp_in(h)))
        return h[:, -1] @ self.W_U


def train_grokking(p: int = 113, epochs: int = 25000, seed: int = 0, device: str = "cuda") -> tuple[OneLayerTransformer, dict]:
    """The source's grokking() recipe verbatim (30% train split from torch.Generator seed 0, AdamW lr 1e-3,
    weight decay 1.0, betas (0.9, 0.98), full batch, 25,000 epochs), returning the model and W_E snapshots."""
    g = torch.Generator().manual_seed(seed)
    a, b = torch.meshgrid(torch.arange(p), torch.arange(p), indexing="ij")
    data = torch.stack([a.flatten(), b.flatten(), torch.full((p * p,), p)], 1)
    labels = (data[:, 0] + data[:, 1]) % p
    perm = torch.randperm(p * p, generator=g)
    n_train = int(0.3 * p * p)
    tr, te = perm[:n_train], perm[n_train:]
    torch.manual_seed(seed)
    model = OneLayerTransformer(p).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1.0, betas=(0.9, 0.98))
    xtr, ytr, xte, yte = data[tr].to(device), labels[tr].to(device), data[te].to(device), labels[te].to(device)
    snaps = {"init": model.W_E.detach()[:p].cpu().numpy().copy(),
             "init_state": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}}
    for ep in range(epochs):
        loss = F.cross_entropy(model(xtr), ytr)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if ep == 1000:
            snaps["memorised"] = model.W_E.detach()[:p].cpu().numpy().copy()
            snaps["memorised_state"] = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        if ep % 2500 == 0 or ep == epochs - 1:
            with torch.no_grad():
                acc = float((model(xte).argmax(-1) == yte).float().mean())
            log.info("grokking epoch %d: train loss %.4f, test acc %.3f", ep, float(loss), acc)
    with torch.no_grad():
        snaps["test_acc"] = float((model(xte).argmax(-1) == yte).float().mean())
    snaps["final"] = model.W_E.detach()[:p].cpu().numpy().copy()
    return model, snaps


def env_hf_home() -> None:
    """Point the HF cache at HF_HOME from .env (e.g. D:/AI/hf_cache, where Llama-3.1-8B is cached)."""
    from dotenv import load_dotenv
    from neurotopo.config import ROOT
    load_dotenv(ROOT / ".env")
    if os.environ.get("HF_HOME"):
        log.info("HF_HOME = %s", os.environ["HF_HOME"])
