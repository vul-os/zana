"""Gates on mower/coil-study — the one executable part of this hardware repo.

The centrepiece is `test_design_summary_*`: DESIGN_SUMMARY.md is the document a
reader trusts when they wind a coil, and every number in it is recomputed here
from physics.py. Both the inputs (inner diameter, frequency, air gap, wire
diameter, pitch, layer gap, turn counts) and the expected outputs are PARSED
OUT OF THE MARKDOWN, so editing the write-up without re-running the model is a
test failure rather than a silent lie.

The rest are invariants of the model itself: reciprocity, known values of the
elliptic integrals, monotonicity in air gap and frequency, and the bounds the
efficiency expressions must respect.
"""

import math
import re
from pathlib import Path

import numpy as np
import pytest

import physics

REPO = Path(__file__).resolve().parent.parent
SUMMARY = REPO / "mower" / "coil-study" / "DESIGN_SUMMARY.md"

# ── Parsing DESIGN_SUMMARY.md ───────────────────────────────────────────────

# Rows of the comparison table this gate re-derives, and how to read each cell.
CHECKED_ROWS = {
    "Total Turns": ("total_turns", r"([\d.]+)", 0),
    "Outer Diameter": ("outer_diameter_mm", r"([\d.]+)mm", 1),
    "Wire Length": ("wire_length_m", r"([\d.]+)m", 2),
    "Inductance": ("L_tx_uH", r"([\d.]+)µH", 2),
    "Efficiency @ 40mm": ("eff_pct", r"([\d.]+)%", 1),
    "Capacitor": ("C_resonant_nF", r"([\d.]+)nF", 1),
}


def _text() -> str:
    assert SUMMARY.is_file(), f"{SUMMARY} is missing — nothing to verify"
    return SUMMARY.read_text(encoding="utf-8")


def _requirements(text: str) -> dict:
    """The fixed inputs, read out of the '## Design Requirements' list."""
    wanted = {
        "inner_diameter_mm": r"^- Inner Diameter:\s*([\d.]+)\s*mm",
        "freq_khz": r"^- Operating Frequency:\s*([\d.]+)\s*kHz",
        "air_gap_mm": r"^- Target Air Gap:\s*([\d.]+)\s*mm",
        "wire_dia_mm": r"^- Wire Diameter:\s*([\d.]+)\s*mm",
        "pitch_mm": r"^- Pitch:\s*([\d.]+)\s*mm",
    }
    out = {}
    for key, pattern in wanted.items():
        m = re.search(pattern, text, re.MULTILINE)
        assert m, f"DESIGN_SUMMARY.md no longer states '{key}' — cannot verify it"
        out[key] = float(m.group(1))
    assert len(out) == len(wanted) == 5
    return out


def _options(text: str) -> list[dict]:
    """Column headers of the comparison table: layers x turns per layer."""
    m = re.search(r"^\| Parameter\s*\|(.+)\|\s*$", text, re.MULTILINE)
    assert m, "comparison table header not found in DESIGN_SUMMARY.md"
    cells = [c.strip() for c in m.group(1).split("|") if c.strip()]

    opts = []
    for cell in cells:
        spec = re.search(r"\((?:(\d+)[x×])?(\d+)T\)", cell)
        assert spec, f"cannot read a layers/turns spec out of column {cell!r}"
        opts.append(
            {
                "label": cell,
                "layers": int(spec.group(1) or 1),
                "turns_per_layer": int(spec.group(2)),
            }
        )
    return opts


def _layer_gaps(text: str) -> list[float]:
    """Layer gap per stacked option, in document order. Single layer -> 0."""
    return [float(v) for v in re.findall(r"^- Layer Gap:\s*([\d.]+)\s*mm", text, re.MULTILINE)]


def _table_cells(text: str) -> dict:
    """{row label: [cell, cell, cell]} for the rows this gate checks."""
    rows = {}
    for label, (_, cell_re, _) in CHECKED_ROWS.items():
        m = re.search(r"^\|\s*\*\*" + re.escape(label) + r"\*\*\s*\|(.+)\|\s*$", text, re.MULTILINE)
        assert m, f"row '{label}' is no longer in the comparison table"
        cells = [c.strip() for c in m.group(1).split("|") if c.strip()]
        values = []
        for c in cells:
            hit = re.search(cell_re, c)
            assert hit, f"cannot parse {c!r} in row '{label}' with {cell_re}"
            values.append(float(hit.group(1)))
        rows[label] = values
    return rows


@pytest.fixture(scope="module")
def summary():
    text = _text()
    reqs = _requirements(text)
    opts = _options(text)
    gaps = _layer_gaps(text)

    # Give each option its layer gap: the single-layer option has none stated.
    stacked = [o for o in opts if o["layers"] > 1]
    assert len(gaps) == len(stacked), (
        f"DESIGN_SUMMARY.md states {len(gaps)} layer gaps for {len(stacked)} "
        "stacked options — the document and the table disagree"
    )
    it = iter(gaps)
    for o in opts:
        o["layer_gap_mm"] = next(it) if o["layers"] > 1 else 0.0

    return {"reqs": reqs, "options": opts, "cells": _table_cells(text)}


# ── The golden gate ─────────────────────────────────────────────────────────


def test_design_summary_is_parseable(summary):
    """Coverage assertion: the parse found a real table, not nothing."""
    assert len(summary["options"]) == 3, (
        f"expected 3 design options, parsed {len(summary['options'])} — this gate "
        "only means anything if it covers every column of the table"
    )
    assert set(summary["cells"]) == set(CHECKED_ROWS), "checked rows went missing"
    for label, values in summary["cells"].items():
        assert len(values) == 3, f"row '{label}' has {len(values)} cells, expected 3"
    assert [o["turns_per_layer"] for o in summary["options"]] == [8, 8, 29]
    assert [o["layers"] for o in summary["options"]] == [1, 2, 2]


def test_design_summary_numbers_are_reproduced_by_the_model(summary):
    """Every checked cell of the comparison table, recomputed from physics.py."""
    reqs = summary["reqs"]
    compared = 0
    failures = []

    for col, opt in enumerate(summary["options"]):
        res = physics.simulate_stacked_system(
            inner_radius_mm=reqs["inner_diameter_mm"] / 2,
            turns_per_layer=opt["turns_per_layer"],
            pitch_mm=reqs["pitch_mm"],
            wire_dia_mm=reqs["wire_dia_mm"],
            num_layers=opt["layers"],
            layer_gap_mm=opt["layer_gap_mm"],
            air_gap_mm=reqs["air_gap_mm"],
            freq=reqs["freq_khz"] * 1000,
        )
        res["eff_pct"] = res["eff"] * 100

        for label, (key, _, places) in CHECKED_ROWS.items():
            documented = summary["cells"][label][col]
            computed = round(float(res[key]), places)
            compared += 1
            if computed != round(documented, places):
                failures.append(
                    f"{opt['label']} / {label}: DESIGN_SUMMARY.md says {documented}, "
                    f"physics.py gives {computed}"
                )

    assert compared == 3 * len(CHECKED_ROWS) == 18, (
        f"only {compared} cells compared; this gate must cover all 18 or it is "
        "passing by doing nothing"
    )
    assert not failures, "the design write-up no longer matches the model:\n  " + "\n  ".join(failures)


# ── Model invariants ────────────────────────────────────────────────────────


def test_elliptic_integrals_match_known_values():
    # K(0) = E(0) = pi/2; K(1/2) = 1.6857503548, E(1/2) = 1.4674622093.
    assert physics.ellipk(0.0) == pytest.approx(math.pi / 2, rel=1e-9)
    assert physics.ellipe(0.0) == pytest.approx(math.pi / 2, rel=1e-6)
    assert physics.ellipk(0.5) == pytest.approx(1.6857503548, rel=1e-8)
    assert physics.ellipe(0.5) == pytest.approx(1.4674622093, rel=1e-6)


def test_mutual_inductance_between_loops_is_reciprocal_and_decays():
    m_ab = physics.mutual_loops(0.10, 0.06, 0.03)
    m_ba = physics.mutual_loops(0.06, 0.10, 0.03)
    assert m_ab == pytest.approx(m_ba, rel=1e-12), "M(r1,r2,z) must equal M(r2,r1,z)"

    zs = [0.01, 0.02, 0.04, 0.08, 0.16]
    ms = [physics.mutual_loops(0.10, 0.10, z) for z in zs]
    assert all(a > b > 0 for a, b in zip(ms, ms[1:])), f"M must fall with distance, got {ms}"

    # Degenerate radii short-circuit rather than blow up.
    assert physics.mutual_loops(0.0, 0.1, 0.01) == 0
    assert physics.mutual_loops(0.1, -1.0, 0.01) == 0


def test_mutual_loops_approaches_the_dipole_limit():
    """Small loop on the axis of a large one: M -> mu0*pi*r1^2*r2^2 / 2(r2^2+z^2)^1.5."""
    mu0 = 4 * np.pi * 1e-7
    r_small, r_big, z = 0.002, 0.10, 0.05
    analytic = mu0 * np.pi * r_small**2 * r_big**2 / (2 * (r_big**2 + z**2) ** 1.5)
    assert physics.mutual_loops(r_small, r_big, z) == pytest.approx(analytic, rel=2e-3)


@pytest.mark.parametrize(
    "width,height,pitch,shape,expected",
    [
        (100, 100, 5, "square", 10),
        (100, 60, 5, "square", 6),
        (120, 120, 2, "circle", 30),
    ],
)
def test_coil_geometry_turn_counts(width, height, pitch, shape, expected):
    turns = physics.get_coil_geometry(width, height, pitch, shape)
    assert len(turns) == expected
    if shape == "circle":
        assert all(r > 0 for r in turns)
        assert turns == sorted(turns, reverse=True), "circular turns spiral inward"
    else:
        assert all(w > 0 and h > 0 for w, h in turns)


def test_ac_resistance_rises_with_frequency():
    turns = physics.get_coil_geometry(120, 120, 2.0, "circle")
    rs = [physics.calculate_ac_resistance(turns, 1.0, 2.0, f, "circle") for f in (1e3, 1e4, 1e5, 1e6)]
    assert all(a < b for a, b in zip(rs, rs[1:])), f"skin+proximity must raise R_ac, got {rs}"
    assert all(r > 0 for r in rs)


def test_litz_wire_lowers_ac_resistance():
    turns = physics.get_coil_geometry(120, 120, 2.0, "circle")
    solid = physics.calculate_ac_resistance(turns, 1.0, 2.0, 4e4, "circle", litz_factor=1.0)
    litz = physics.calculate_ac_resistance(turns, 1.0, 2.0, 4e4, "circle", litz_factor=0.3)
    assert litz == pytest.approx(0.3 * solid, rel=1e-12)


def test_system_efficiency_is_bounded_by_the_link_and_by_one():
    for link in (0.6, 0.8, 0.95, 0.999):
        total = physics.calculate_total_system_efficiency(link, v_in=12.0, p_load=25.0)
        assert 0 < total < link < 1, f"link={link} gave total={total}"
    assert physics.calculate_total_system_efficiency(0.0, 12.0) == 0
    assert physics.calculate_total_system_efficiency(-0.1, 12.0) == 0


def test_stacked_link_efficiency_falls_as_the_air_gap_opens():
    effs = [
        physics.simulate_stacked_system(100, 8, 1.7, 0.7, 2, 1.5, gap, 40000)["eff"]
        for gap in (20, 40, 60, 80)
    ]
    assert all(a > b for a, b in zip(effs, effs[1:])), f"efficiency must fall with gap, got {effs}"
    assert all(0 < e < 1 for e in effs)


def test_stacking_a_second_layer_raises_inductance_and_efficiency():
    one = physics.simulate_stacked_system(100, 8, 1.7, 0.7, 1, 0.0, 40, 40000)
    two = physics.simulate_stacked_system(100, 8, 1.7, 0.7, 2, 1.5, 40, 40000)
    assert two["total_turns"] == 2 * one["total_turns"] == 16
    assert two["L_tx_uH"] > 3 * one["L_tx_uH"], "two coupled layers ~ 4x the inductance"
    assert two["eff"] > one["eff"]
    assert two["outer_diameter_mm"] == pytest.approx(one["outer_diameter_mm"])


def test_resonant_capacitance_actually_resonates():
    res = physics.simulate_stacked_system(100, 8, 1.7, 0.7, 2, 1.5, 40, 40000)
    L = res["L_tx_uH"] * 1e-6
    C = res["C_resonant_nF"] * 1e-9
    f0 = 1 / (2 * np.pi * np.sqrt(L * C))
    assert f0 == pytest.approx(res["freq_Hz"], rel=1e-9)


def test_planar_square_simulation_is_self_consistent():
    res = physics.simulate_system(120, 120, 2.0, 1.0, gap_mm=35, freq=40000)
    assert res is not None
    assert res["n_turns"] == 30
    assert 0 < res["k"] < 1, "coupling coefficient must be a fraction"
    assert 0 < res["eff"] < 1
    assert res["U"] == pytest.approx(res["k"] * res["Q"], rel=1e-12)
    # A coil too small for even one turn yields nothing rather than a fake answer.
    assert physics.simulate_system(1.0, 1.0, 5.0, 1.0, gap_mm=35) is None
