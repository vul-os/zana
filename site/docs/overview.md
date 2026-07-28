# Overview

**Zana** (Swahili — *"tools / gear"*) is an open-hardware line for the
physical world: reference designs for the devices a smart home or business
actually runs on — robot mowers, sensor nodes, security and cleaning bots,
cameras. Download a design, build it, or run a finished unit.

Zana is the **body** to [Aql](https://github.com/vul-os/aql)'s brain: every
device is meant to drop straight into Aql, the open-source command centre —
but the designs are open and vendor-neutral, so they work with any compatible
control plane.

> **Status: prototype-stage reference designs.** The first device — an
> autonomous **mower** — is here as CAD and PCB work recovered from active
> prototyping, plus one executable engineering study. There is **no firmware
> in this repo**, no bill of materials and no assembly guide. It is not yet a
> finished, documented, buy-the-parts build.

## What's here

| Area | Contents | State |
|---|---|---|
| **Chassis & body** | FreeCAD bodies across four iterations (`mower/mowbot*.FCStd`), wheels, moulds, motor supports | design files |
| **Drivetrain** | Shafts, couplers (including an aluminium variant), GT2 pulley, castor fitting | design files |
| **Electronics (KiCad)** | `TRANSMITTER` (thru-hole + SMD), `MAINBOARD`, `EMF_SENSOR`, `RAIN` sensor, shared `IMRANS_LIBRARY` symbols | design files |
| **Wireless power** | `mower/coil-study/` — an inductance/efficiency model for the inductive charging link, in Python | runs; covered by tests |
| **Simulator** | `mower/simulator/` — C++ (raylib + Bullet, native and WASM) and PyBullet sources for a driving-over-grass sim | source only — not built, not tested |
| **Fabrication rigs** | Coil winder, PCB mill, and UV exposure box used to build the electronics | design files |

## What is checked

Most of a hardware repo is binaries no build server can meaningfully verify.
What *is* checkable is checked on every push, by three gates that each assert
their own coverage count so none of them can pass by doing nothing:

- the numbers in the coil study's design write-up are re-derived from the model;
- every path named in a README or doc exists, no tracked file is empty, every
  script parses;
- this site carries the Vulos token block, badge, band and footer, every local
  link resolves, and no page fetches anything off-box.

## What Zana is not

Zana is a set of open reference designs, not a finished consumer product with
a buy button. There's no serial number, no cloud activation, and no vendor
lock — you build it, or you run a unit somebody else already built, on
hardware you own outright.

## The line

The devices a real space runs on, as open designs you can build and command
yourself:

- **Mower** — an autonomous robot mower. The first device, and the only one
  with real CAD and PCB work today.
- **Sensor nodes** — environment, motion, and presence, over open protocols.
  Planned.
- **Security & cleaning bots** — patrol and cleaning units you own outright.
  Planned.
- **Cameras** — local-first cameras where footage stays on your box. Planned.

## Ecosystem

Zana is one half of a pair:

- **[Aql](https://github.com/vul-os/aql)** — the brain: the open-source
  command centre that discovers and controls your devices.
- **Zana** — the body (this repo): the open hardware Aql commands.

Zana devices work with any compatible control plane, and run best on Aql. See
[Runs on Aql](#aql) for how the two halves fit together.

## License

MIT — © VulOS. Zana is a VulOS project; source and issues at
[github.com/vul-os/zana](https://github.com/vul-os/zana).

## Related documents

- [Getting started](#getting-started) — tools you need and how to build a device.
- [The mower design](#mower) — the flagship device, in depth.
- [Runs on Aql](#aql) — how Zana devices pair with the command centre.
