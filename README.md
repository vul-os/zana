# Zana

**Zana** (Swahili — "tools / gear") is an open-hardware line for the physical world:
reference designs for the devices a smart home or business actually runs on.

Mowers, security bots, cleaning bots, sensor nodes, cameras — download the
design, build it, or run a finished unit. Every device speaks the same protocol
so it drops straight into a control plane.

## What's here

- **Reference designs** — blueprints, BOMs, firmware for each device
- **Device classes** — sensor node, camera, mower, security bot, cleaning bot
- **One protocol** — every Zana device is discoverable and controllable out of the box

## Ecosystem

- **[Aql](../aql)** — the brain: the open-source command center that runs your devices.
- **Zana** — the body (this repo): the hardware Aql controls.

Zana devices work with any compatible control plane, and shine when driven by Aql.

## Legacy

`legacy/opengro` is an early watering/irrigation + light-controller device
(MicroPython + Arduino firmware), folded in for history only — not actively
developed. Hardcoded WiFi credentials were scrubbed to placeholders.

## Status

Early. First device class and hardware/software seam in design.
