## 10× Single-Stage Pulse Amplifier (MC33272, +12 V single-supply)

**Goal**: Amplify ~20 mV coil pulses by 10× in one stage, cleanly and stably, no schematic drawing required.

### Topology
- **Type**: Non-inverting, single stage, gain = 10
- **Reference**: Mid-supply virtual ground (VREF ≈ 6 V)
- **Protection**: Series input damping + Schottky clamps to VREF
- **Bandwidth** (approx):
  - MC33272: GBW ≈ 8 MHz → BW ≈ 800 kHz at G=10
  - TL072: GBW ≈ 3 MHz → BW ≈ 300 kHz at G=10 (use larger Cf for stability)

### Connections (step-by-step, schematic-free)
1. Create VREF (mid-rail):
   - `+12 V → 10 kΩ → VREF → 10 kΩ → GND`
   - Bypass VREF to GND with `10 µF || 0.1 µF` (close to op-amp).
2. Input conditioning from the 150 µH coil:
   - `COIL_OUT → Rs (220 Ω) → Cin (100 nF) → IN_NODE`
   - Bias: `IN_NODE → 100 kΩ → VREF`
   - Clamp (BAT54S or two Schottkys):
     - D1: `IN_NODE →|→ VREF`
     - D2: `VREF →|→ IN_NODE`
3. Amplifier (MC33272, non-inverting):
   - `+IN = IN_NODE`
   - `-IN ↔ Rg (1.00 kΩ) ↔ VREF`
   - `OUT ↔ Rf (9.09 kΩ) ↔ -IN` (gain ≈ 1 + 9.09/1.00 = 10.09)
   - Add `Cf` across Rf for HF stability: `Rf || Cf (33–68 pF)`
4. Output:
   - `VOUT = OUT` (centered at VREF ≈ 6 V)
   - Optional AC-coupled, ground-referenced output: `VOUT → 10 µF → VOUT_AC`, and `VOUT_AC → 100 kΩ → GND`.
5. Decoupling (mandatory):
   - Place `0.1 µF` + `1–10 µF` at op-amp supply pins; shortest possible paths.

### Recommended component values
| Function | Component | Value | Notes |
|---|---|---|---|
| Mid-rail | Divider | 10 kΩ / 10 kΩ | +12 V → 10 kΩ → VREF → 10 kΩ → GND |
| Mid-rail | Bypass | 10 µF || 0.1 µF | From VREF to GND |
| Input | Rs | 220 Ω | Damps source inductance, protects input |
| Input | Cin | 100 nF | With 100 kΩ → fc ≈ 1/(2π·100 kΩ·100 nF) ≈ 16 Hz |
| Input bias | Rbias | 100 kΩ | From IN_NODE to VREF |
| Clamp | D1, D2 | BAT54S | Back-to-back to VREF |
| Gain set | Rg | 1.00 kΩ (0.1%) | To VREF |
| Gain set | Rf | 9.09 kΩ (0.1%) | Gain ≈ 10.09 |
| HF trim | Cf | 33–68 pF (C0G) | Across Rf; start 47 pF |
| Output AC couple (opt.) | Cout | 10 µF | To create ground-referenced VOUT_AC |
| Output load (opt.) | Rout | 100 kΩ | From VOUT_AC to GND |
| Supply decoupling | Bypass | 0.1 µF + 1–10 µF | Close to supply pins |

### Expected behavior
- Gain ≈ 10 (±1% with 0.1% resistors)
- Output centered at VREF ≈ 6 V (for single-supply operation)
- With MC33272: ~800 kHz small-signal bandwidth at G=10. Suitable for fast coil pulses.

### TL072 option (if MC33272 unavailable)
- Same netlist and values work; for stability with capacitive/inductive sources:
  - Prefer `Cf = 56–100 pF` across Rf.
  - Keep input series `Rs ≥ 220 Ω`.
  - Expect ≈ 300 kHz bandwidth at G=10.

### Layout tips (critical)
- Keep feedback loop (OUT → Rf → -IN) extremely short.
- Place Rs and clamp diodes at the op-amp input pin.
- Star the VREF return to the op-amp ground; avoid sharing with load currents.
- Decouple both supply and VREF locally with short, wide traces. 