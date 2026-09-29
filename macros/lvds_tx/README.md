# `lvds_tx` — LVDS transmitter macro

Pre-driver plus current-steering LVDS output driver for the IHP `sg13cmos5l` PDK,
imported from the `LVDS-PLL_Private` design repository. Schematics, testbenches and
a **layout in progress**: every device placed, routing by hand just started. See
`docs/layout.md`.

## Cells — `schematic/xschem/`

| Cell | What it is |
|---|---|
| `lvds_tx.sch/.sym` | **Top cell.** Pre-driver and driver wired together; the whole interface between them is the gate-drive pair `In_p`/`In_n`. Two separate `Iref` pins, deliberately. |
| `Driver.sch/.sym` | H-bridge current-steering output stage plus common-mode feedback. 22 devices, one tail, **no pre-emphasis**. |
| `predriver.sch/.sym` | 1.2 V core data in, rail-to-rail 3.3 V gate drive out. Built from `predriver_stage` and `predriver_comp`. |
| `predriver_stage.sch/.sym`, `predriver_comp.sch/.sym` | Pre-driver sub-cells. |
| `esdpad.sch/.sym` | 4 kV ESD clamp plus pad capacitance as one block. Instantiate on every output pad. |
| `serdes.sch/.sym` | Mixed-signal boundary around the Verilog serializer: `adc_bridge` in, one `d_cosim` instance, `dac_bridge` out. |
| `serdes/serdes_dig.sym` | Symbol of the Verilog pattern generator + 8-bit serializer. The `.v` and the Verilated `.so` are **not** here yet. |

The HV device flavour (`sg13_hv_*`) is mandatory: the 1.25 V LVDS output common mode
sits above the entire 1.2 V LV supply.

## Testbenches — `testbenches/xschem/`

| Bench | Question it asks | `make` target |
|---|---|---|
| `tb_dc.sch` | TIA/EIA-644-A clauses 4.1.1/4.1.2/4.1.3. Eight driver cells off one DC sweep of `VTEST`. | `make sim-dc` |
| `Driver.tb.sch` | Clauses 4.1.4/4.1.5 at 3.125 Gb/s into 49.9 + 49.9 Ω with the `Vos` tap. | `make sim-driver` |
| `predriver.tb.sch` | Core-domain stimulus → pre-driver → driver → pad/ESD/100 Ω. | `make sim-predriver` |
| `tb_cmfb.sch` | Is the common-mode loop stable? `Vref` step and closed-loop `Vos`/`Vref` (ac), set to the corner with the least margin (ff, −40 °C, 3.63 V, res_wcs). | `make sim-cmfb` |
| `tb_word`, `tb_prbs`, `tb_alt`, `tb_slow`, `tb_startup` | Mixed-signal link, SerDes → `lvds_tx` → pad → 100 Ω. Each carries its own `meas` commands. | `make sim-link-word`, `make sim-link-prbs` |

The five link benches load `serdes/serdes_dig.so` through `d_cosim`. **That library is
not in this repository yet**, so they will not run until the `serdes/` support directory
is moved across. The four analog benches (`sim-all`) need nothing but the PDK.

## Where it sits in the project

The top level instantiates `lvds_tx` as `xlvds` in
`schematic/xschem/sg13cmos5l_chipalooza_analog_project.sch`:

| macro pin | top level |
|---|---|
| `Out_p` / `Out_n` | `analog_pin[2]` / `analog_pin[3]`, two of the four dedicated pads |
| `Va` / `Vss` | `vdd_3v3` / `vss_3v3` |
| `Iref_pd`, `Iref_drv` | 30 uA each, from `xiref_pd` / `xiref_drv`: two instances of [`macros/iref_x15`](../iref_x15/README.md), the 1:15 pre-mirror that turns the 2 uA of `ibias[0]` / `ibias[1]` into 30 uA. It used to sit inside this macro. |
| `Vref` | `analog_bus[1]`, the 1.2 V common-mode reference |
| `D_p` / `D_n` | driven by `lvds_pattern`, the standard-cell PRBS-7 generator |

With the pattern generator in place the top-level bench runs the whole chain: PRBS-7 at
1 Gb/s into the pre-driver, the driver and a 49.9 + 49.9 Ω termination, giving
|`Vod`| = 358 mV and `Vos` = 1.244 V, both inside TIA/EIA-644-A.

## Running

Inside the IIC-OSIC-TOOLS container:

```bash
make sim-all                  # the four analog benches
make sim-xschem TB=tb_dc      # or any single bench by name
```

## Layout — `layout/`

`layout/lvds_tx.gds` is the layout, edited by hand in KLayout. Only its device cells
(`dev_*`) are generated: `make layout-pcells` rebuilds them from the schematic with the
PDK's magic gencells and swaps them into the file, leaving everything else as it is.
57.5 × 61.1 µm, every device at the least spacing the sign-off deck allows, mirror pairs
on shared guard rings, `make klayout-drc` clean. Routing by hand has just started, so
there is no LVS yet. `docs/layout.md` has the rules for editing the file and what an
update does. `docs/routing.md` has the planned wiring net by net, and
`scripts/archive/` the generator that made the placement.

## Sizing changed for layout

Two devices were resized while the placement was built. Both keep W, L and
every current in the block exactly as they were — they are layout decisions,
not circuit ones, and the schematic is the place they had to be made.

| Device | Was | Now | Why |
|---|---|---|---|
| `iref_x15` `Mn2` | `w=48u ng=15` | `w=48u ng=6` | six fingers of 8 µm is the finger geometry `Mp1`/`Mp2` already had, so the three big devices pack together. Cell 1594 → 1101 µm². (`iref_x15` is its own macro now, `macros/iref_x15`.) |
| `predriver_comp` `Mt` | `w=560u ng=56 l=0.5u` | `w=17.52u ng=6 m=2 l=0.45u` | the tail was 73 % of the comparator's area; first to 140u, then to 35u with the longer `Mref`, then onto the input pair's length and finger count so that it stands finger on finger under it (below) |
| `predriver` `Mref` | `w=8u l=0.5u` | `w=2u l=2u` | first narrowed with `Mt`; then lengthened, which raises `Mt`'s gate so a quarter of its width conducts as well (below) |
| `predriver_comp` `Mid`/`Mio` | `w=40u ng=4` | `w=24u ng=2` | the differential pair; skew improves rather than degrades |
| `predriver_comp` `Mld`/`Mlo` | `w=20u ng=2` | `w=12u ng=1` | the pmos load, kept at half the pair — the 2:1 ratio is what matters |
| `predriver_stage` `Mpp1`/`Mpn1` | `w=12.5u` | `w=12.52u` | what the layout has: the gencell draws a finger on the 10 nm grid, 3.125 µm comes out 3.13 µm. LVS compares widths exactly (+0.16 %) |
| `predriver_stage` `Mpxn`/`Mpxp` | `w=4.375u` | `w=4.38u` | the same rounding (+0.11 %) |

The floorplan changed finger counts once more, W and L untouched: `M5`/`M4`
40 → 16, `M2` 12 → 20, `M11`/`M12` 20 → 16, `Mt` 14 → 20, `Mid`/`Mio` 2 → 6,
`Mld`/`Mlo` 1 → 4 (and drawn as one eight-finger cell in one guard ring,
so their gate runs through in metal1 — `docs/layout.md`, *One cell for two
transistors*) and four pairs in `predriver_stage`; `M6` went from four
blocks of 31 fingers à 0.8 µm to two à 1.6 µm, which raises |Vod| by 2–6 %
(the reference `M9` keeps its 0.8 µm finger). `Cop`/`Con` went from 10 × 10 µm to
two 10 × 5 µm halves each (`m=2`), same gate area, so they stand upright beside the pre-driver;
two halves because the PDK allows at most 10 µm per finger. The table and the corner comparison are in
`scripts/archive/README.md`, *Finger counts changed for the floorplan*.

In `predriver_stage` every NMOS now has as many gates as the PMOS in its column. Only
the NMOS moved, W and L unchanged:

| Device | Before | Now |
|---|---|---|
| `Mnp1`/`Mnn1` | 2 × 2.5 µm | 4 × 1.25 µm |
| `Mnp2`/`Mnn2` | 8 × 2.0 µm | 10 × 1.6 µm |

Going the other way, with the PMOS at 2 and 8 fingers, would have made their fingers
6.26 and 5.0 µm long and the stage about 1.5 µm taller. `predriver.tb` over tt 27 / ss 125 /
ss −40 / ff −40 / ff 125 °C (`testbenches/xschem/simulations/stage_ng.py`):

| | Largest change, any corner |
|---|---|
| Delay D → In | 2.3 ps |
| 20–80 % edges at `In_p` | 1.3 ps |
| \|Vod\| | 1 mV |
| Rising/falling delay difference | 0.1–5.9 ps, was 2.0–4.2 ps |

The stage has since been rebuilt without guard rings, as two rows with tap strips
(`docs/layout.md`, *The stage: rows and tap strips*). It is now 41.9 × 9.7 µm, of which
the tap strips alone take 3.4 µm on either side.

`Mt` is the one that needed evidence rather than judgement, because shrinking
it alone would have cut the tail current with it. Swept over tt/ss/ff at
−40/27/125 °C in `predriver.tb`:

* at constant current (`Mt` and `Mref` together) nothing moves — edges within
  a few ps of the 560 µm reference at every corner, skew ≤ 8 ps, |Vod|
  346–366 mV;
* letting the current fall instead (`Mt` alone) survives 280 µm and breaks at
  140 µm, where the falling edge slips more than 500 ps at ss/125 °C.

`predriver_comp` came down from 1812 to 1141 µm², and `predriver` from 7336
to 6263 µm² — it is now smaller than the `Driver` it feeds.

**`Mt` is not a current source.** Measured in `predriver.tb` (kpm, five
corners): its drain, the tail node, sits at only 50–100 mV — the inputs are
1.2 V logic, and the pair's Vgs leaves nothing above the tail — so `Mt` is a
switch deep in its linear region. The tail current is 0.5–0.8 mA, set by the
pair and the loads; the 2.1 mA the 70:1 ratio suggests never flows. What
`Mt` has to be is a low resistance, and that depends on its gate voltage as
much as on its width. A longer `Mref` raises that gate: at `l=2u` it is at
1.37 V instead of 0.94 V (tt 27 °C), and 35 µm of `Mt` do what 140 µm did:

| `Mref` / `Mt` | tail current tt / ss 125 °C | In_p edges ss 125 °C | \|Vod\| min, 5 corners |
|---|---|---|---|
| 2u × 0.5u / 140u | 0.63 / 0.50 mA | 103 / 102 ps | 369 mV |
| 2u × 1u / 70u | 0.63 / 0.48 mA | 104 / 102 ps | 369 mV |
| **2u × 2u / 35u** | 0.59 / 0.46 mA | 104 / 102 ps | 369 mV |

Edges within 1 ps and |Vod| within 2 mV in every corner. CACE over the full
PVT grid afterwards: all pass, |Vod| 361 / 384 / 406 mV (min / typ / max,
was 361 / 385 / 406), Vos p-p 50 / 105 mV (was 47 / 103), edges 52.6 /
83.2 ps (was 52.8 / 83.5), supply 6.17 / 7.09 mA (was 6.23 / 6.86 — the
higher gate lets a little more tail current through at ff). A mirror of two
lengths would hold its ratio poorly over corners, but nothing is mirrored
here. What the small `Mt` costs is matching — less gate area, more σ(Vth) —
and it matters less for a switch than it would for a current source; **it
has not been simulated**: Monte-Carlo over CACE is the open item. The sweep
scripts are in `testbenches/xschem/simulations/` (`mt_sweep.py`,
`mt_corners.py`, `mt_edges.py`, `mt_lref.py`, `mt_l045.py`), a build
directory, not in git.

For the layout `Mt` then took the input pair's gate length and finger count
— `l=0.45u`, two halves of six fingers (`w=17.52u ng=6 m=2`, 35.04 µm in
all) — so that each half stands finger on finger under one half of the pair
and every tail drain runs straight up in metal1 into the pair source above
it (`docs/layout.md`, *Tail under the pair*). Over the same five corners: edges
within 0.4 ps, |Vod| unchanged, tail current +3 % (it conducts a little
better at the shorter length). CACE afterwards: all pass, |Vod| 362 / 385 /
405 mV, Vos p-p 50 / 103 mV, edges 52.6 / 83.6 ps, supply 6.21 / 7.17 mA.

## CMFB compensation

The common-mode loop — `Rp`/`Rn` sense `cm`, `M11`/`M12` compare it with `Vref`,
`cmfb` drives the gate of `M2` — used to be compensated by `Cc` alone, 40u × 5u
straight on `cmfb`. With the loop broken at the gate of `M2` (loop gain by double
injection) and swept over the 27 CACE conditions times the resistor corners
bcs/typ/wcs, that left 11° of phase margin at tt and none at ff / −40 °C / 3.63 V /
res_wcs: −1.3°, gain margin −0.5 dB. The loop oscillated there, growing to 150 mV pp
on `Vos`. CACE did not see it because it runs res_typ only, where the same corner
still has 1.6°.

A larger `Cc` alone hardly helps — six times the area gives 23° — because the
non-dominant poles sit close to the crossover. A resistor in series with `Cc`
puts a zero next to it; 1–2 kΩ is the sweet spot, above ~3 kΩ it stops helping:

| | Was | Now |
|---|---|---|
| `Cc` | `w=40u l=5u ng=8`, gate on `cmfb` | `w=50u l=5u ng=10`, gate on `cc_g` |
| `Rc` | — | `rppd w=1u l=6u` (1.6 kΩ), `cmfb` → `cc_g` |
| phase margin tt / worst | 11° / −1.3° | 44° / 32° |
| gain margin worst | −0.5 dB | 8.3 dB |
| 50 mV `Vref` step, worst: overshoot / settled to ±2 mV | 155 % / never | 54 % / 17 ns |
| `Vos` pp in `Driver.tb`, tt / worst | 94 / 170 mV | 57 / 95 mV |

|`Vod`| does not move (≥ 351 mV everywhere). rppd rather than rhigh because rhigh
spreads by a factor of two over corner and temperature, and at its high end the
zero no longer helps; rppd stays within 1.42–1.86 kΩ. The area did not change:
ten fingers make `Cc` 56.4 µm wide, which the driver row has room for, and `Rc`
fits in a free corner (`scripts/archive/README.md`). More margin costs area — `Cc` 80u
(ten fingers of 8 µm) with `rppd l=4u` gives 45° worst case for 3 µm more height.
`tb_cmfb.sch` shows the worst corner, and what the old compensation did there.

## Output crossing point

`Out_p` and `Out_n` used to cross well below the middle of their swing — 9 to 14 %
of it, at every edge and in every corner — and `Vos` dipped by the same amount.
The cause is in the H-bridge, not the pre-driver (it does it with ideal input
edges too): while the switch gates pass mid-rail, the PMOS switches need
`tail_p` to rise by ~0.7 V and the NMOS switches `tail_n` to fall by ~0.3 V
before they carry the current. Both tail sources lose headroom for those
~60 ps — `M2` drops from 3.9 to 2.1 mA, `M6` from 3.8 to 2.7 mA — and since the
top one loses more, the bottom pulls the common mode down.

`Ctn1` and `Ctn2`, PMOS caps from `tail_n` to Va (95 µm² of gate together), hold
`tail_n` through the edge, so the bottom slows down as much as the top does.
`predriver.tb` (pre-driver + driver + ESD pad + 100 Ω), over tt, ss/ff at
−40/125 °C and the skewed corners sf/fs:

| | Was | Now |
|---|---|---|
| crossing, from the middle, in % of the swing | −14.0 … −9.2 | −5.1 … −0.6 |
| `Vos` pp, tt / worst | 72 / 83 mV | 33 / 51 mV |
| \|`Vod`\| | 370–418 mV | 368–405 mV |
| 20–80 % edges / delay at tt | 53 / 128 ps | 52 / 128 ps |

`Driver.tb` over the 81 CMFB conditions: `Vos` pp 54 / 85 → 25 / 66 mV; the loop
keeps 32° and 8.8 dB. What does not work: moving the pre-driver's crossing
point (a weaker `Mpp2` or stronger `Mnp2`) centres the outputs too, but trebles
`Vos` pp; weaker NMOS switches the same; a wider `M2` does nothing; a cap on
`tail_p` makes it worse. The gate area is what counts — L hardly matters,
PMOS and NMOS about the same — and the two caps are what fits into the free
corners under `Cc`, so the area did not change. In the top-level bench (PRBS-7 at
500 Mb/s, no pad model, so less capacitance on the outputs) the crossing moves
from −23 % to −9 % of the swing and `Vos` pp from 119 to 72 mV.

## Not imported yet

`compliance/`, `predriver/` and `serdes/` batch benches, `predelay` (verified but out
of the chain), and the findings documents under `docs/`. The routed `Driver` layout in
`LVDS-PLL_Private` was not imported either: the placement here was generated from this
repository's own schematic hierarchy, which puts `Driver` one level down inside
`lvds_tx` rather than at the top.
