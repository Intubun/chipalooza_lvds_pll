# lvds_bt - switchable back-termination of the LVDS pair

~200 ohm across `Out_p` / `Out_n` of [`lvds_tx`](../lvds_tx/README.md), switched
by `dig_in[4]` at the top level (`xbt`).

```
OUTP --- R1 rppd 10 x 3.3 um (93 ohm) --- A --- MSW nmosHV 300/0.45, 30 fingers --- B --- R2 (93 ohm) --- OUTN
EN --- level shifter (ref_odt_lvlup = sg13cmos5l_LevelUp) --- gate of MSW at 3.3 V
 '---- DEN dantenna 0.78 x 0.78 (antenna diode on the long EN line)
```

## Why

`lvds_tx` is a current-steering driver: its output impedance is high, so
whatever the line sends back is reflected again whole. With the IHP pad, a
2 nH bond wire, a 0.5 pF package and a receiver of 1 pF per side, the edge
that reaches the receiver partly comes back, reaches the pads 400 ps later
(dips of up to 0.18 V there) and arrives at the receiver a second time 800 ps
after the edge. `slot_14_tb_lvds_pads`, 500 Mb/s, tt:

| | reflection at the pads | at the receiver | Vos p-p | 3.3 V supply |
|---|---|---|---|---|
| no termination, `ibias1` 2 uA | 0.18 V | ±0.40 V, ringing | 46 mV | 5.2 mA |
| 200 ohm, `ibias1` 3 uA | ~0.1 V | ±0.38 V, nearly flat | 38 mV | 7.0 mA |
| 100 ohm, `ibias1` 4 uA (not built) | ~0.05 V | ±0.37 V, flat | 43 mV | 8.4 mA |
| gate resistors 3 kOhm, slower edges (not built) | small | ±0.41 V | 160 mV | 5.2 mA |

200 ohm takes most of the benefit for half the extra current of 100 ohm.
Slowing the edges instead pushes Vos p-p past 150 mV: the H-bridge spends longer
half-switched and its tail sources lose headroom (`lvds_tx` README, *Output
crossing point*).

## Use

`dig_in[4]` = 1 and `ibias1` at IDAC code 9 (2.90 uA) instead of 6 (1.94 uA).
The pair works into 100 || 200 = 67 ohm, so the driver needs 1.5 times the
current for the same |Vod|; through the 1:15 mirror that is 43.5 uA on
`Iref_drv` instead of 29 uA. Without the
`ibias1` step |Vod| drops by a third. `dig_in[4]` = 0 (the default): MSW off,
the pair sees R1 / R2 and MSW's junctions, a few 10 fF each, and the chip
behaves as without the block.

## Results

- **Resistance**, schematic, tt, 27 C, outputs at 1.4 / 1.0 V: 193 ohm on,
  264 Gohm off.
- **`lvds_tx` with it**, 2 x 49.9 ohm, over the CACE grid (ss/tt/ff,
  -40/27/125 C, 2.97/3.3/3.63 V, 500 Mb/s, 110 ps input edges), with the IDAC
  codes taken as linear to 10 uA:

  | | off, code 6 (29.0 uA) | on, code 9 (43.5 uA) | TIA/EIA-644-A |
  |---|---|---|---|
  | \|Vod\| | 345-394 mV | 304-364 mV | 247-454 mV |
  | Vos | 1.191-1.195 V | 1.174-1.194 V | 1.125-1.375 V |
  | Vos p-p | <= 78 mV | <= 83 mV | <= 150 mV |
  | 3.3 V supply | 4.5-5.6 mA | 5.6-7.3 mA | |
  | 20-80 % edge | 46-73 ps | 38-75 ps | |

  The worst case is ss, 125 C, 2.97 V (304 mV): at 1.5 times the current the
  driver's tail sources run short of headroom there. rppd at its `res_wcs` /
  `res_bcs` corners moves |Vod| by +-3 % (tt).
- DRC clean (KLayout, IHP deck, antenna rules included), LVS clean, the level
  shifter hierarchically (`bash scripts/check.sh`); at the top level `make check`.

## Protection

No clamp diodes on A and B, unlike `ref_odt`'s X: R1 / R2 (93 ohm, 10 um wide)
sit between the pads and MSW, MSW is a thick-oxide device with its gate behind
the level shifter, and its drain and source junctions clamp negative excursions
to the substrate. The driver's own transistors are on the pads with no resistor
at all.

## Files

| file | |
|---|---|
| `scripts/gen_schematic.py` | writes `schematic/xschem/lvds_bt.sch` / `.sym` |
| `scripts/gen_layout.py` | writes `layout/lvds_bt.gds` from the IHP PCells - run inside KLayout: `klayout -b -r macros/lvds_bt/scripts/gen_layout.py` |
| `scripts/check.sh` | DRC and LVS of the block, results in `build/lvds_bt/` |
| `layout/lvds_bt.gds` | 64 x 28 um; the switch, gate bar, guard ring and level shifter are `ref_odt`'s |
| `schematic/xschem/xschemrc` | adds `macros/ref_odt/schematic/xschem` for the shared level shifter |

At the top level: `scripts/top/add_bt.py` places and wires it (step 5 of
`scripts/top/build_layout.sh`).
