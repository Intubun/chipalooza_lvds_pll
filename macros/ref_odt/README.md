# `ref_odt` — switchable 50 Ω termination of `ref_clk`

`ref_clk` comes in on pad 2 of slot 14, an `sg13cmos5l_IOPadAnalog`. Without a
termination, the chip end of the clock line is high-impedance: a 50 Ω generator
then doubles its open-circuit swing at the pad, and a low-impedance driver rings
(simulated: −0.6 … 1.85 V at the clock gates from a 10 Ω driver). `ref_odt` puts a
50 Ω termination on the pad, switched by `dig_in[0]`.

```
PAD ── R1 rppd 40 × 6.65 µm (45 Ω) ── X ── MSW sg13_hv_nmos 300/0.45, 30 fingers ── VSS
                                       ├── DN dantenna 20 × 1.26  (X → substrate / VSS)
                                       └── DP dpantenna 20 × 1.26 (X → VDDH)
EN ── xls ref_odt_lvlup (1.2 V → 3.3 V) ── ENH = gate of MSW
 └─── DEN dantenna 0.78 × 0.78 (antenna diode on the long EN line)
```

| pin | at the top level | |
|---|---|---|
| `PAD` | `s14_an[2]` | pad 2 itself — not `s14_an_2_esd`, where the ~520 Ω of the secondary protection would make the termination a divider |
| `EN` | `dig_in[0]` | 1 = termination on, 0 = off (the harness default: unselected, every `dig_in` is 0) |
| `VDD` | `vdd_1v2` | the level shifter's input stage |
| `VDDH` | `vdd_3v3` | the level shifter's output, the gate drive of MSW, DP's cathode |
| `VSS` | `vss_3v3` | one net with `vss_1v2` (the harness ties them) |

## Why it is built like this

**At the pad itself.** The analog pad has two core terminals: `s14_an[2]` is the
bond pad, `s14_an_2_esd` its output through the secondary protection (≈ 520 Ω
`rppd` and two small diodes). The clock gates sit on the protected terminal; the
termination has to sit on the bond pad, or 50 Ω against 520 Ω in series would just
divide the clock down.

**Resistor first.** R1 is the first thing behind the pad: 45 Ω of `rppd`, 40 µm
wide for the 24 mA the termination carries with 1.2 V on the pad, and for what an
ESD event pushes into this path. DN and DP clamp the switch's drain X to VSS and
to the 3.3 V rail, the way the pad's own secondary protection does — extra ESD
protection for the switch.

**An HV switch, driven at 3.3 V.** With the termination off, X follows the pad,
which a mis-driven clock can push to ~2 V: MSW is a 3.3 V device. Driven straight
from `dig_in[0]` at 1.2 V, an HV NMOS needs ~1 mm of width for 5 Ω and is not
linear (simulated at ss / 125 °C / 1.08 V: 74 Ω and 1.47 V at the gates). With
its gate at 3.3 V, 300 µm give ~5 Ω, linear: R1 + MSW = 50 Ω. The level shifter
is `sg13cmos5l_LevelUp` of the IHP IO library, transistor for transistor
(`ref_odt_lvlup`); its layout is the library's, copied without the `ptap1`
marker so its tap is a plain tap.

## Verified

- DRC clean (KLayout, IHP deck, antenna rules included); LVS clean, hierarchical
  (`ref_odt` and `ref_odt_lvlup`). At the top level, `make check`.
- Simulated on the input path — source, 50 Ω line, 0.5 pF package, 2 nH bond
  wire, the pad's own model, the two clock gates as load (500 MHz):

  | case | at the clock gates | ringing | source current |
  |---|---|---|---|
  | 50 Ω generator, termination off | 0 … 1.20 V | 0.07 V | 0 |
  | 50 Ω generator, termination on | 0 … 1.20 V | 0.09 V | 12 mA mean |
  | 10 Ω driver, termination off | **−0.62 … 1.85 V** | 0.65 V | |
  | 10 Ω driver, termination on | −0.03 … 1.23 V | 0.10 V | |
  | termination on, ss / 125 °C | 0 … 1.28 V (57 Ω) | | |
  | termination on, ff / −40 °C | 0 … 1.12 V (44 Ω) | | |

- In the full top cell with the pads (`make sim-lvds-pads`): `dig_in[0]` = 1 draws
  12.1 mA mean from a source at 2.4 V open circuit (1.2 V into 50 Ω): 50 Ω; the
  LVDS output is unchanged.

## Using it

Set `dig_in[0]` = 1 **before** the clock source is switched on. With the
termination still off, a generator set for a 50 Ω load doubles its swing at the
open pad: 2.4 V on 1.2 V gates. Termination on, set the generator to 0 … 1.2 V
into 50 Ω; it then has to deliver 24 mA while high.

## Files

| path | what |
|---|---|
| `scripts/gen_schematic.py` | writes `ref_odt.sch/.sym` and `ref_odt_lvlup.sch/.sym` |
| `scripts/gen_layout.py` | writes `layout/ref_odt.gds` from the IHP PCells — run inside KLayout: `klayout -b -r macros/ref_odt/scripts/gen_layout.py` |
| `layout/ref_odt.gds` | 64 × 33.4 µm |
