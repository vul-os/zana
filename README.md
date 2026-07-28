<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-wordmark-dark.svg">
    <img src="assets/brand/logo-wordmark.svg" alt="Zana" width="220">
  </picture>
</p>

<p align="center"><strong>Open hardware for the physical world — the devices your hub commands.</strong></p>

<p align="center">
  <a href="#what-is-zana">What</a> ·
  <a href="#whats-here">What's here</a> ·
  <a href="#the-mower">The mower</a> ·
  <a href="#build-it">Build it</a> ·
  <a href="#checks">Checks</a> ·
  <a href="#ecosystem">Ecosystem</a>
</p>

<p align="center"><sub>Open hardware · FreeCAD · KiCad · 3D-printable · <a href="https://github.com/vul-os/aql">runs on Aql</a></sub></p>

## What is Zana?

**Zana** (Swahili — *"tools / gear"*) is an open-hardware line for the physical world: reference designs for the devices a smart home or business actually runs on — robot mowers, sensor nodes, security and cleaning bots, cameras. Download a design, build it, or run a finished unit.

Zana is the **body** to [**Aql**](https://github.com/vul-os/aql)'s brain: every device is meant to drop straight into Aql, the open-source command center — but the designs are open and vendor-neutral, so they work with any compatible control plane.

> [!NOTE]
> **Status: prototype-stage reference designs.** The first device — an autonomous **mower** — is here as CAD and PCB work recovered from active prototyping, plus one executable engineering study. There is **no firmware in this repo**, no bill of materials and no assembly guide. It is not yet a finished, documented, buy-the-parts build.

## What's here

| Area | Contents | State |
|---|---|---|
| **Chassis & body** | FreeCAD bodies across four iterations (`mower/mowbot*.FCStd`), wheels, moulds, motor supports | design files |
| **Drivetrain** | Shafts, couplers (incl. an aluminium variant), GT2 pulley, castor fitting | design files |
| **Electronics (KiCad)** | `TRANSMITTER` (thru-hole + SMD), `MAINBOARD`, `EMF_SENSOR`, `RAIN` sensor, shared `IMRANS_LIBRARY` symbols | design files |
| **Wireless power** | [`mower/coil-study/`](mower/coil-study/README.md) — an inductance/efficiency model for the charging link, in Python | **runs; covered by tests** |
| **Simulator** | [`mower/simulator/`](mower/simulator/README.md) — C++ (raylib + Bullet, native and WASM) and PyBullet sources for a driving-over-grass sim | **source only — not built, not tested, needs a mesh that isn't checked in** |
| **Fabrication rigs** | Coil winder, PCB mill, and UV exposure box used to build the electronics | design files |

## The mower

The flagship Zana device — an autonomous robot mower with inductive charging. See [`mower/README.md`](mower/README.md) for the full parts breakdown.

**Formats:** `.FCStd` (FreeCAD source — edit these) · `.3mf` / `.stl` (print) · `.step` (neutral CAD) · `.dxf` / `.svg` (2D profiles) · `.kicad_*` (electronics). FreeCAD/KiCad auto-backups are gitignored — edit the source files.

## Build it

You'll want [FreeCAD](https://www.freecad.org/) for the mechanical design, [KiCad](https://www.kicad.org/) for the boards, and a 3D printer for the printable parts. Open the `.FCStd` files in `mower/`, the KiCad projects in `mower/PCB/`, and slice the `.3mf`/`.stl` meshes for your printer.

## Checks

Most of this repo is CAD and PCB binaries that no CI can meaningfully verify. What *is* checkable is checked, and [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs it on every push:

```sh
pip install -r requirements-dev.txt
python3 -m pytest -q
```

Three gates, each asserting its own coverage count so it cannot pass by doing nothing:

- **`tests/test_coil_physics.py`** — re-derives every number in `mower/coil-study/DESIGN_SUMMARY.md` from `physics.py`, and checks the model's own invariants (reciprocity, monotonicity, efficiency bounds).
- **`tests/test_repo_integrity.py`** — every path named in a README or doc exists; no tracked file is zero bytes; every shell script parses; every Python file compiles.
- **`tests/test_site.py`** — `site/` carries the Vulos product-site token block, badge, band and footer, every local link resolves, and no page fetches anything off-box.

## Ecosystem

Zana is one half of a pair:

- **[Aql](https://github.com/vul-os/aql)** — the brain: the open-source command center that discovers and controls your devices.
- **Zana** — the body (this repo): the open hardware Aql commands.

Zana devices work with any compatible control plane, and run best on Aql.

## License

[MIT](LICENSE) — © VulOS. Zana is a VulOS project; source and issues at
[github.com/vul-os/zana](https://github.com/vul-os/zana).

---

<p align="center">
  <a href="https://vulos.org"><img src="assets/vulos-logo.png" alt="vulos" height="20"></a><br>
  <sub><a href="https://vulos.org"><b>vulos</b></a> — open by design</sub>
</p>
