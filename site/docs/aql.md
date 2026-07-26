# Runs on Aql

Zana is one half of a pair:

- **[Aql](https://github.com/vul-os/aql)** — the brain: a self-hosted command
  centre that discovers and controls your devices from one console,
  local-first, with no cloud in the middle.
- **Zana** (this repo) — the body: the open hardware Aql commands.

## Brain and body, each usable alone

Every Zana device is designed to drop straight into Aql — but the designs
themselves are open and vendor-neutral. Nothing here requires Aql to be
useful: a Zana device works with any compatible control plane you already
run, and Aql is a project you can adopt independently of Zana's hardware.
The two are built to pair well together, not to lock you into either one.

## Why the split

Splitting the "brain" (control software) from the "body" (the physical
device) keeps each half honest about what it is:

- **Zana** stays a hardware project — FreeCAD, KiCad, fabrication notes — and
  doesn't grow into a bespoke app platform per device.
- **Aql** stays a general command centre — it doesn't need to know the
  internals of every device's electronics, only how to discover and talk to
  it.

## Where to go next

- [github.com/vul-os/aql](https://github.com/vul-os/aql) — Aql's own source
  and documentation.
- [The mower design](#mower) — the one Zana device built today, and what it
  takes to build one yourself.
- [Overview](#overview) — the wider Zana line and its current status.
