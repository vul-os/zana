# Mower

Open-hardware design for an autonomous **robot mower** with inductive
charging — the first Zana device.

Originally prototyped as "mowbot"; preserved here as the reference design.

> **Status: prototype-stage reference design.** CAD and PCB work recovered
> from active prototyping, plus one executable study (`coil-study/`) and one
> unbuilt simulator sketch (`simulator/`). There is no firmware in this
> directory, no bill of materials, and no assembly guide. It is not yet a
> finished, documented, buy-the-parts build.

## Mechanical (FreeCAD + meshes, this directory)

- **`mowbot.FCStd` … `mowbot4.FCStd`** — main body / chassis, four iterations.
  `mowbot4` is the latest; build from that one.
- **`shaft*.FCStd` / `.3mf`, `coupler*.FCStd`, `gt2-pulley.FCStd`** —
  drivetrain: shafts, couplers, pulley.
- **`alimunum_coupler*`** — aluminium coupler variant (STL + FreeCAD).
  `al_coup.dxf` / `.svg` / `.pdf` are its 2D cutting profiles.
- **`castor_fitting*`, `socket.FCStd`, `plate.dxf`** — castor mount, a
  connector/socket part, and the base-plate profile.
- **`mowbot4-CoilTX.3mf` / `mowbot4-CoilRX.3mf`** — the charging-coil formers.
- **`*.txt`** — fastener and passive reference tables (hex bolts, countersunk
  and wafer-head M3–M4 screws, common passives).
- **`old/`** — earlier body, wheel and coupler iterations plus their sliced
  gcode, kept for history. Nothing in `old/` is current.

## Electronics (`PCB/`)

| Project | Role |
|---|---|
| `PCB/TRANSMITTER` | Charging-coil transmitter |
| `PCB/TRANSMITTER_DIP` | Thru-hole variant, with a 4×4 KiKit panel and Gerbers |
| `PCB/TRANSMITTER_SMD` | SMD variant |
| `PCB/MAINBOARD` | Main control board |
| `PCB/EMF_SENSOR` | EMF sensing (used for boundary/coil alignment) |
| `PCB/EMF_SENSOR_DIP` | Thru-hole variant, with a 4×6 KiKit panel |
| `PCB/RAIN` | Rain sensor |

All boards draw on the shared `PCB/IMRANS_LIBRARY.kicad_sym` symbol library.

A second, older `TRANSMITTER.kicad_pro` / `.kicad_sch` / `.kicad_prl` also sits
at the top of this directory. It is **not** a copy of `PCB/TRANSMITTER/` — the
schematic is a different, smaller revision (42 KB vs 65 KB) and there is no
board file beside it. `PCB/TRANSMITTER/` is the one to open; the top-level pair
is kept only as history.

`PCB/*_DIP/create_panel.sh` panelises a board for home fabrication; both need
[KiKit](https://github.com/yaqwsx/KiKit) on `PATH`.

`pulse_amp_10x.md` is a build-it-on-veroboard note for a 10× single-stage
pulse amplifier for the coil pickup — component values and connections, no
schematic.

## Wireless power (`coil-study/`)

Executable Python: an inductance/efficiency model plus the sweeps and printable
winding templates built on it. `coil-study/DESIGN_SUMMARY.md` writes up three
candidate coils, and the repo's test suite re-derives every number in it from
the model. See [`coil-study/README.md`](coil-study/README.md).

## Simulator (`simulator/`)

C++ (raylib + Bullet, native and WASM) and PyBullet sources for a driving-over-
grass simulation. **Not built, not packaged, not tested, and not run by CI** —
it also loads a `mowbot.stl` that is not checked in. See
[`simulator/README.md`](simulator/README.md) for what it would take to run it.

## Fabrication rigs

`coilwinder*`, `pcbmachine*`, `pcbuvbox*` — a coil winder, a PCB mill and a UV
exposure box, designed to build the mower's own electronics. They are tools for
the build, not parts of the mower.

## Formats

- `.FCStd` — FreeCAD source (edit these)
- `.3mf` / `.stl` — printable/sliced meshes
- `.step` — neutral CAD interchange
- `.dxf` / `.svg` — 2D profiles for laser/waterjet
- `.kicad_*` — KiCad electronics

FreeCAD and KiCad auto-backups (`.FCBak`, `*-backups/`, `fp-info-cache`) are
gitignored — edit the checked-in sources.
