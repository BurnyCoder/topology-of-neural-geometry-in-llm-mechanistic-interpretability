"""Tests for turning the source's labels and row order into concepts and semantic phases.

Global context: the alignment test needs the concept of every point and its phase on the semantic cycle.
Some factors are only implicit in the source's prompt order (external/shape-fitting/src/neurogeom/realdata/
llm_sets.py: calendar_prompts, bhalla_prompts), so the parsing must reproduce those templates exactly.
"""

import numpy as np

from neurotopo.data import source


def test_chronological_half_hour_matches_source_time_list():
    # Source order: [f"{h}:{m:02d} {ap}" for ap in (AM, PM) for h in 1..12 for m in (0, 30)].
    times = [f"{h}:{m:02d} {ap}" for ap in ("AM", "PM") for h in range(1, 13) for m in (0, 30)]
    chron = source.chronological_half_hour(np.arange(48))
    def minutes(s):
        hm, ap = s.split()
        h, m = map(int, hm.split(":"))
        return ((h % 12) + 12 * (ap == "PM")) * 60 + m
    assert np.array_equal(chron, np.array([minutes(t) // 30 for t in times]))
    assert chron[times.index("12:00 AM")] == 0 and chron[times.index("12:00 PM")] == 24
    assert sorted(chron) == list(range(48))


def test_calendar_concepts_follow_prompt_order():
    # Weekdays: row i = day i // 7 (source: for d in DAYS for k in 1..7); months: row i = month i // 12.
    days = [d for d in source.DAYS for _ in range(7)]
    c = source.concepts("R5a_llama_weekdays", days)
    assert np.array_equal(c.index, np.arange(49) // 7) and c.cyclic and len(c.phase) == 7
    months = [m for m in source.MONTHS for _ in range(12)]
    assert np.array_equal(source.concepts("R5b_llama_months", months).index, np.arange(144) // 12)
    t = source.concepts("R5c_llama_days_time", [d for d in source.DAYS for _ in range(48)], variable="time")
    assert t.index[22] == 0                                # row 22 of each day is "12:00 AM"


def test_colour_hue_and_ordinal_bins():
    c = source.concepts("R7_llama_colors", ["0|0.4|0.25", "350|1.0|0.75", "180|0.7|0.5"])
    assert list(c.index) == [0, 35, 18] and len(c.phase) == 36
    o = source.concepts("R8b_llama_age", [str(v) for v in range(1, 8)], n_bins=7)
    assert list(o.index) == list(range(7)) and not o.cyclic
    m = source.concepts("R6_llama_years", ["1801", "1810", "1999"], variable="mod10")
    assert list(m.index) == [1, 0, 9]
