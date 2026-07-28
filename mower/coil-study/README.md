# Coil study

Wireless-power coil design and efficiency analysis for the mower's inductive
charging dock. This is the one part of `mower/` that is executable code rather
than CAD, and it is the part the test suite covers.

## Modules

| File | What it does |
|---|---|
| `physics.py` | The model. Elliptic integrals, Maxwell mutual inductance between coaxial loops, self/mutual inductance for planar square and circular spirals and for stacked circular coils, AC resistance with skin and proximity effects, and the `k·Q` link-efficiency solve. No side effects, no plotting — import this. |
| `benchmark.py` | Parameter sweeps and printable A3/A4 winding templates, via matplotlib. Every entry point writes a `.png` into the working directory. |
| `main.py` | Reproduces the three designs written up in `DESIGN_SUMMARY.md` and emits the two plots tracked here. |
| `find_minimum_turns.py` | Search for the fewest single-layer turns that reach 85 % link efficiency at a 40 mm gap. **Runs on import** — it has no `__main__` guard, so execute it, never import it. |

Requires `numpy`; everything except `physics.py` also requires `matplotlib`.

## The design that came out of it

`DESIGN_SUMMARY.md` records three candidate coils for a 200 mm-ID, 40 kHz,
40 mm-air-gap link. Its numbers are not decoration: `tests/test_coil_physics.py`
parses the comparison table out of that markdown and re-derives every cell from
`physics.py`, so the write-up and the model cannot drift apart silently.

```
$ python3 -m pytest tests/test_coil_physics.py -q     # from the repo root
```

## Regenerating the plots

Two plots are tracked, both produced by `main.py`:

- `Single_Layer_8Turns_A3.png` — printable winding template for the 8-turn coil.
- `Efficiency_vs_AirGap_Comparison.png` — efficiency against air gap for the
  three candidates.

```sh
pip install numpy matplotlib
cd mower/coil-study && python3 main.py
```

`benchmark.py`'s sweeps write a further ~20 plots. Those are regenerable
output, not source, and are deliberately not tracked — run the sweep you want
rather than reading a stale `.png`.
