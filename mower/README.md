# Mower

Open-hardware design for an autonomous **robot mower** — the first Zana device.

Originally prototyped as "mowbot"; preserved here as the reference design.

## What's in here

- **`mowbot.FCStd`, `mowbot2.FCStd`** — main body / chassis (FreeCAD)
- **`shaft*.FCStd/.3mf`, `coupler*.FCStd`, `gt2-pulley.FCStd`** — drivetrain: shafts, couplers, pulley
- **`alimunum_coupler*`** — aluminium coupler variant (STL + FreeCAD)
- **`socket.FCStd`** — connector/socket part
- **`TRANSMITTER.kicad_*`** — RF transmitter PCB (KiCad)
- **`PCB/RAIN/RAIN.step`** — rain sensor board
- **`coilwinder*`, `pcbmachine*`, `pcbuvbox*`** — supporting fabrication rigs (coil winder, PCB mill, UV exposure box) used to build the mower's electronics
- **`*.txt`** — fastener/passive reference tables (bolts, screws, common passives)
- **`old/`** — earlier body/wheel/coupler iterations, kept for history

## Formats

- `.FCStd` — FreeCAD source (edit these)
- `.3mf` / `.stl` — printable/sliced meshes
- `.step` — neutral CAD interchange
- `.kicad_*` — KiCad electronics

FreeCAD auto-backups (`.FCBak`) are gitignored — edit the `.FCStd` sources.

## Status

Prototype-stage reference design. Not yet a finished, documented build.
