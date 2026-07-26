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
> autonomous **mower** — is here as CAD, PCB, and firmware-adjacent work
> recovered from active prototyping. It is not yet a finished, documented,
> buy-the-parts build.

## What's here

| Area | Contents |
|---|---|
| **Chassis & body** | FreeCAD bodies across iterations (`mower/mowbot*.FCStd`), wheels, moulds, motor supports |
| **Drivetrain** | Shafts, couplers (including an aluminium variant), GT2 pulley, castor fitting |
| **Electronics (KiCad)** | `TRANSMITTER` (thru-hole + SMD), `MAINBOARD`, `EMF_SENSOR`, `RAIN` sensor, shared `IMRANS_LIBRARY` symbols |
| **Wireless power** | `mower/coil-study/` — coil design and efficiency study (Python physics + plots) for inductive charging |
| **Simulator** | `mower/simulator/` — a mowbot physics simulator (C++ native/WASM + Python) |
| **Fabrication rigs** | Coil winder, PCB mill, and UV exposure box used to build the electronics |

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
