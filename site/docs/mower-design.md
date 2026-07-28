# The mower design

The flagship Zana device — an autonomous robot mower with inductive
charging. Originally prototyped as "mowbot"; preserved here as the reference
design.

> **Status: prototype-stage reference design.** Not yet a finished,
> documented build.

## What's in `mower/`

- **`mowbot.FCStd`, `mowbot2.FCStd`, `mowbot3*`, `mowbot4*`** — main body /
  chassis iterations (FreeCAD). `mowbot4` is the latest.
- **`shaft*.FCStd` / `.3mf`, `coupler*.FCStd`, `gt2-pulley.FCStd`** —
  drivetrain: shafts, couplers, pulley.
- **`alimunum_coupler*`** — an aluminium coupler variant (STL + FreeCAD).
- **`socket.FCStd`** — a connector/socket part.
- **`TRANSMITTER.kicad_*`** — the RF transmitter PCB (KiCad), with thru-hole
  and SMD variants (`PCB/TRANSMITTER_DIP`, `PCB/TRANSMITTER_SMD`).
- **`PCB/MAINBOARD`, `PCB/EMF_SENSOR`, `PCB/RAIN`** — the mainboard, an EMF
  sensor board, and a rain sensor board.
- **`coilwinder*`, `pcbmachine*`, `pcbuvbox*`** — supporting fabrication rigs
  (a coil winder, a PCB mill, and a UV exposure box) used to build the
  mower's own electronics.
- **`*.txt`** — fastener/passive reference tables (bolts, screws, common
  passives).
- **`old/`** — earlier body, wheel, and coupler iterations, kept for history.

## Wireless charging

`mower/coil-study/` holds the model behind the mower's inductive charging
dock, and it is the one part of `mower/` that is executable code rather than
CAD. `physics.py` computes mutual inductance between coaxial loops from
complete elliptic integrals, sums self-inductance segment by segment for
planar and stacked coils, adds AC resistance with skin and proximity effects,
and solves link efficiency from `k·Q`. `benchmark.py` sweeps that model over
gap, frequency, voltage and coil aspect ratio and emits printable A3/A4
winding templates.

`coil-study/DESIGN_SUMMARY.md` writes up three candidate coils for a 200 mm-ID,
40 kHz, 40 mm-air-gap link — the recommendation is two stacked layers of 8
turns, 91.5 % link efficiency at 223.8 mm outer diameter. Those figures are
not decoration: the repo's test suite parses the comparison table back out of
that markdown and re-derives every cell from `physics.py`, so the write-up and
the model cannot drift apart silently.

Two plots are tracked (`Single_Layer_8Turns_A3.png`,
`Efficiency_vs_AirGap_Comparison.png`); the rest of the sweeps are regenerable
output and are deliberately not committed.

## Simulator

`mower/simulator/` holds sources for a driving-over-grass simulation, written
twice: C++ on raylib + Bullet with an Emscripten/WASM target (`cpp/`), and an
earlier PyBullet prototype (`python/`).

> **It is source only.** Nothing builds it, nothing tests it, and CI does not
> compile it. It also loads a mesh called `mowbot.stl` that is not checked in
> anywhere — the chassis meshes are named `mowbot4-Body.stl` and so on — and
> the WASM build script still has `path/to/raylib` placeholders. Treat it as a
> sketch to pick up, not a tool to use. `simulator/README.md` lists exactly
> what it would take to get it running.

## Electronics

The KiCad projects under `mower/PCB/` cover the boards the mower actually
needs:

| Board | Role |
|---|---|
| `TRANSMITTER` (DIP / SMD) | RF transmitter, thru-hole and SMD variants |
| `MAINBOARD` | Main control board |
| `EMF_SENSOR` (+ DIP variant) | EMF sensing |
| `RAIN` | Rain sensor |

All boards share the `IMRANS_LIBRARY.kicad_sym` symbol library.

## File formats

- `.FCStd` — FreeCAD source (edit these).
- `.3mf` / `.stl` — printable/sliced meshes.
- `.step` — neutral CAD interchange.
- `.kicad_*` — KiCad electronics.

FreeCAD auto-backups (`.FCBak`) are gitignored — edit the `.FCStd` sources
directly.

## Related documents

- [Getting started](#getting-started) — the tools and general build workflow.
- [Overview](#overview) — where the mower fits in the wider Zana line.
