# Getting started — build a device

Zana ships **designs**, not assembled products. Building a device means
opening the CAD/PCB sources, sourcing parts, and printing or fabricating the
rest yourself. This page covers the tools you need and the general workflow;
see [The mower design](#mower) for the parts breakdown of the one device that
exists today.

## Tools you'll need

- **[FreeCAD](https://www.freecad.org/)** — for the mechanical design. Every
  chassis, drivetrain, and fixture in this repo is a `.FCStd` source file;
  open these to inspect or modify a design.
- **[KiCad](https://www.kicad.org/)** — for the electronics. PCB projects
  live under `mower/PCB/` as `.kicad_*` files.
- **A 3D printer** — for the printable parts (wheels, moulds, motor supports,
  couplers). Slice the `.3mf` / `.stl` meshes for your printer.
- **Basic PCB fabrication or an assembly house** — to turn the KiCad projects
  into populated boards, whichever route you prefer.

## File formats in this repo

| Format | What it's for |
|---|---|
| `.FCStd` | FreeCAD source — **edit these**, not the exported meshes |
| `.3mf` / `.stl` | Printable/sliced meshes, ready to slice |
| `.step` | Neutral CAD interchange, for tools that don't read FreeCAD natively |
| `.kicad_*` | KiCad electronics — schematics, PCB layout, symbol libraries |

FreeCAD and KiCad auto-backup files are gitignored — always edit the checked-in
source files, not a local `.FCBak`.

## General workflow

1. **Clone the repo.**

   ```bash
   git clone https://github.com/vul-os/zana.git
   cd zana
   ```

2. **Open the mechanical design in FreeCAD.** Start with the device's main
   body/chassis file (for the mower, `mower/mowbot4.FCStd` is the latest
   iteration — see [The mower design](#mower)). Earlier iterations are kept
   under `old/` for history; the newest numbered file is the one to build
   from.

3. **Open the electronics in KiCad.** Each board lives in its own directory
   under `mower/PCB/` with its own `.kicad_pro` project file. The shared
   `IMRANS_LIBRARY.kicad_sym` holds common symbols used across boards.

4. **Export and print/fabricate.** Export STEP/STL from FreeCAD for parts you
   need to print or machine, and generate Gerbers from KiCad for parts you
   need to fabricate as PCBs.

5. **Pair it with a control plane.** Zana devices are built to drop into
   [Aql](https://github.com/vul-os/aql), the open-source command centre — but
   nothing here is locked to it. See [Runs on Aql](#aql).

## Running the checks

Nothing in this repo needs building, but the parts that *can* be verified are,
and you can run the same gates CI runs:

```bash
pip install -r requirements-dev.txt
python3 -m pytest -q
```

That re-derives the charging-coil design from its model, checks that every
path named in a README or doc exists and that no tracked file is empty, and
checks this site's markup. Roughly four seconds; no network access.

To regenerate the coil-study plots you also need matplotlib:

```bash
cd mower/coil-study && python3 main.py
```

## Honest status

This is prototype-stage reference material recovered from active
prototyping, not a polished "buy the parts, follow the numbered steps" kit
yet. Expect to do real engineering work — verifying fits, sourcing
equivalent parts, adapting the electronics to what you can source locally.
The [mower design](#mower) page lists exactly what's included today.
