"""Steering tasks: prompts, the steered token, the readout vocabulary and the expected answer per concept.

Global context (preregistration amendment A2): a steering experiment needs a behavioural readout whose answer
depends on the steered concept. Prompts reproduce the source's templates (external/shape-fitting/src/neurogeom/
realdata/llm_sets.py: calendar_prompts, bhalla_prompts) so the activation at the steered position is exactly
the one in the analysed cloud; readout text is appended after the steered token where the template has no
question (a causal model's activation at that position does not depend on later text).
"""

from __future__ import annotations

import colorsys
from dataclasses import dataclass, field

import numpy as np

from neurotopo.data.source import DAYS, MONTHS

NUM_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine",
             10: "Ten", 11: "Eleven", 12: "Twelve"}       # source llm_sets.NUM_WORDS (number words 1..12)


@dataclass
class Prompt:
    text: str                 # full prompt fed to the model
    steer_text: str           # prefix of `text` whose last token is the steered position
    concept: int              # source concept index of the steered token
    shift: int = 0            # answer = (steered concept + shift) mod n


@dataclass
class Task:
    dataset_id: str
    layer: int                # hidden_states[layer] (output of decoder block layer - 1)
    words: list[str]          # readout vocabulary (concept words, decoded from the first token of " word")
    phases: np.ndarray        # phase of each readout word
    n: int                    # concepts on the cycle
    prompts: list[Prompt] = field(default_factory=list)
    decode: str = "argmax"


def weekdays() -> Task:
    """R5a: "Let's do some days of the week math. {k} day(s) from {d} is" -> day (d + k) mod 7; steer the day token."""
    t = Task("R5a_llama_weekdays", 5, DAYS, 2 * np.pi * np.arange(7) / 7, 7)
    for c, d in enumerate(DAYS):
        for k in range(1, 8):
            pre = f"Let's do some days of the week math. {NUM_WORDS[k]} day{'s' if k != 1 else ''} from {d}"
            t.prompts.append(Prompt(pre + " is", pre, c, k))
    return t


def months() -> Task:
    """R5b: "Let's do some calendar math. {k} month(s) from {m} is" -> month (m + k) mod 12; steer the month token."""
    t = Task("R5b_llama_months", 5, MONTHS, 2 * np.pi * np.arange(12) / 12, 12)
    for c, m in enumerate(MONTHS):
        for k in range(1, 13):
            pre = f"Let's do some calendar math. {NUM_WORDS[k]} month{'s' if k != 1 else ''} from {m}"
            t.prompts.append(Prompt(pre + " is", pre, c, k))
    return t


def days_time() -> Task:
    """R5c: steer the last token of "It's {t} on {d}" (layer 19); readout "... The next day is" -> (d + 1) mod 7.
    Four times of day per day (1:00 AM, 7:30 AM, 1:00 PM, 7:30 PM)."""
    t = Task("R5c_llama_days_time", 19, DAYS, 2 * np.pi * np.arange(7) / 7, 7)
    for c, d in enumerate(DAYS):
        for tm in ("1:00 AM", "7:30 AM", "1:00 PM", "7:30 PM"):
            pre = f"It's {tm} on {d}"
            t.prompts.append(Prompt(pre + ". The next day is", pre, c, 1))
    return t


COLOR_WORDS = {"red": 0, "orange": 30, "yellow": 60, "green": 120, "cyan": 180, "blue": 240, "purple": 280, "pink": 330}


def colors() -> Task:
    """R7: steer the last token of "The hex code {hex} is for the color" (layer 19); the next token is a colour
    word; decoded hue = probability-weighted circular mean of 8 basic colour words' hues. One prompt per hue
    (saturation 0.85, lightness 0.5), hex computed exactly as in the source."""
    words = list(COLOR_WORDS)
    t = Task("R7_llama_colors", 19, words, np.deg2rad(np.array(list(COLOR_WORDS.values()), float)), 36, decode="mean")
    for h in range(36):
        r, g, b = colorsys.hls_to_rgb(h / 36, 0.5, 0.85)
        hexc = f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}"
        pre = f"The hex code {hexc} is for the color"
        t.prompts.append(Prompt(pre, pre, h, 0))
    return t


TASKS = {"R5a_llama_weekdays": weekdays, "R5b_llama_months": months, "R5c_llama_days_time": days_time,
         "R7_llama_colors": colors}
