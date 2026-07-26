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

`mower/coil-study/` holds the coil design and efficiency analysis for the
mower's inductive charging system — a Python physics/benchmark suite plus the
generated plots (efficiency vs. gap, frequency vs. efficiency, coil aspect
ratio comparisons, and more). It covers transmitter/receiver coil sizing and
the tradeoffs between coil geometry, air gap, and charging efficiency.

## Simulator

`mower/simulator/` is an early physics simulator for the mower (`mowbot_sim`)
— a C++ implementation that builds natively or to WASM (`build_wasm.sh`,
`shell.html`), plus a Python prototype. It shares mesh assets with the main
mower design rather than duplicating them.

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
