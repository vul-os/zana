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
  <a href="#ecosystem">Ecosystem</a>
</p>

<p align="center"><sub>Open hardware · FreeCAD · KiCad · 3D-printable · <a href="https://github.com/vul-os/aql">runs on Aql</a></sub></p>

## What is Zana?

**Zana** (Swahili — *"tools / gear"*) is an open-hardware line for the physical world: reference designs for the devices a smart home or business actually runs on — robot mowers, sensor nodes, security and cleaning bots, cameras. Download a design, build it, or run a finished unit.

Zana is the **body** to [**Aql**](https://github.com/vul-os/aql)'s brain: every device is meant to drop straight into Aql, the open-source command center — but the designs are open and vendor-neutral, so they work with any compatible control plane.

> [!NOTE]
> **Status: prototype-stage reference designs.** The first device — an autonomous **mower** — is here as CAD, PCB, and firmware-adjacent work recovered from active prototyping. It is not yet a finished, documented, buy-the-parts build.

## What's here

| Area | Contents |
|---|---|
| **Chassis & body** | FreeCAD bodies across iterations (`mower/mowbot*.FCStd`), wheels, molds, motor supports |
| **Drivetrain** | Shafts, couplers (incl. aluminium variant), GT2 pulley, castor fitting |
| **Electronics (KiCad)** | `TRANSMITTER` (thru-hole + SMD), `MAINBOARD`, `EMF_SENSOR`, `RAIN` sensor, shared `IMRANS_LIBRARY` symbols |
| **Wireless power** | `mower/coil-study/` — coil design & efficiency study (Python physics + plots) for inductive charging |
| **Simulator** | `mower/simulator/` — a mowbot physics simulator (C++ native/WASM + Python) |
| **Fabrication rigs** | Coil winder, PCB mill, and UV exposure box used to build the electronics |

## The mower

The flagship Zana device — an autonomous robot mower with inductive charging. See [`mower/README.md`](mower/README.md) for the full parts breakdown.

**Formats:** `.FCStd` (FreeCAD source — edit these) · `.3mf` / `.stl` (print) · `.step` (neutral CAD) · `.kicad_*` (electronics). FreeCAD/KiCad auto-backups are gitignored — edit the source files.

## Build it

You'll want [FreeCAD](https://www.freecad.org/) for the mechanical design, [KiCad](https://www.kicad.org/) for the boards, and a 3D printer for the printable parts. Open the `.FCStd` files in `mower/`, the KiCad projects in `mower/PCB/`, and slice the `.3mf`/`.stl` meshes for your printer.

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
