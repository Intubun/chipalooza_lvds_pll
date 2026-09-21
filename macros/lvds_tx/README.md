# `lvds_tx` — LVDS transmitter macro

Pre-driver plus current-steering LVDS output driver for the IHP `sg13cmos5l` PDK,
imported from the `LVDS-PLL_Private` design repository. Schematics, testbenches and
a **placement-stage layout** — every device and sub-block instantiated and legally
placed, nothing routed yet. See `layout/README.md`.

## Cells — `schematic/xschem/`

| Cell | What it is |
|---|---|
| `lvds_tx.sch/.sym` | **Top cell.** Pre-driver and driver wired together; the whole interface between them is the gate-drive pair `In_p`/`In_n`. Two separate `Iref` pins, deliberately. |
| `Driver.sch/.sym` | H-bridge current-steering output stage plus common-mode feedback. 19 HV devices, one tail, **no pre-emphasis**. |
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
| `tb_word`, `tb_prbs`, `tb_alt`, `tb_slow`, `tb_startup` | Mixed-signal link, SerDes → `lvds_tx` → pad → 100 Ω. Each carries its own `meas` commands. | `make sim-link-word`, `make sim-link-prbs` |

The five link benches load `serdes/serdes_dig.so` through `d_cosim`. **That library is
not in this repository yet**, so they will not run until the `serdes/` support directory
is moved across. The three analog benches (`sim-all`) need nothing but the PDK.

## Where it sits in the project

The top level instantiates `lvds_tx` as `xlvds` in
`schematic/xschem/sg13cmos5l_chipalooza_analog_project.sch`:

| macro pin | top level |
|---|---|
| `Out_p` / `Out_n` | `analog_pin[2]` / `analog_pin[3]`, two of the four dedicated pads |
| `Va` / `Vss` | `vdd_3v3` / `vss_3v3` |
| `Iref_pd`, `Iref_drv`, `Vref` | **provisional top-level ports**, because the pin frame in this repository is a copied HeiChips-style template with no bias pins. The real Chipalooza wrapper has `ibias[1:0]` and `vbias` — see the warning in the top-level README — so these three map straight onto them and need no on-chip bias block. |
| `D_p` / `D_n` | driven by `lvds_pattern`, the standard-cell PRBS-7 generator |

With the pattern generator in place the top-level bench runs the whole chain: PRBS-7 at
1 Gb/s into the pre-driver, the driver and a 49.9 + 49.9 Ω termination, giving
|`Vod`| = 358 mV and `Vos` = 1.244 V, both inside TIA/EIA-644-A.

## Running

Inside the IIC-OSIC-TOOLS container:

```bash
make sim-all                  # the three analog benches
make sim-xschem TB=tb_dc      # or any single bench by name
```

## Layout — `layout/`

Generated from the schematic, not drawn: `make layout` rebuilds the leaf device cells
from the PDK gencells and packs them into one magic cell per subcircuit. **Placement
only — nothing is routed**, so there is no LVS yet. 93.8 × 179.4 µm, DRC clean in
magic `drc(full)` and in the KLayout sign-off deck. `layout/README.md` has the
hierarchy table and what comes next.

## Sizing changed for layout

Two devices were resized while the placement was built. Both keep W, L and
every current in the block exactly as they were — they are layout decisions,
not circuit ones, and the schematic is the place they had to be made.

| Device | Was | Now | Why |
|---|---|---|---|
| `iref_x15` `Mn2` | `w=48u ng=15` | `w=48u ng=6` | six fingers of 8 µm is the finger geometry `Mp1`/`Mp2` already had, so the three big devices pack together. Cell 1594 → 1101 µm² |
| `predriver_comp` `Mt` | `w=560u ng=56` | `w=140u ng=14` | the tail was 73 % of the comparator's area at a tenth of the driver tail's current density |
| `predriver` `Mref` | `w=8u` | `w=2u` | holds the 70:1 mirror ratio, so the tail current stays at 2.1 mA |
| `predriver_comp` `Mid`/`Mio` | `w=40u ng=4` | `w=24u ng=2` | the differential pair; skew improves rather than degrades |
| `predriver_comp` `Mld`/`Mlo` | `w=20u ng=2` | `w=12u ng=1` | the pmos load, kept at half the pair — the 2:1 ratio is what matters |

`Mt` is the one that needed evidence rather than judgement, because shrinking
it alone would have cut the tail current with it. Swept over tt/ss/ff at
−40/27/125 °C in `predriver.tb`:

* at constant current (`Mt` and `Mref` together) nothing moves — edges within
  a few ps of the 560 µm reference at every corner, skew ≤ 8 ps, |Vod|
  346–366 mV;
* letting the current fall instead (`Mt` alone) survives 280 µm and breaks at
  140 µm, where the falling edge slips more than 500 ps at ss/125 °C.

`predriver_comp` came down from 1812 to 1141 µm², and `predriver` from 7336
to 6263 µm² — it is now smaller than the `Driver` it feeds. What this costs
is matching: both mirror devices lost a factor of four in gate area, so
σ(Vth) roughly doubles and the tail current spreads more part to part.
**That has not been simulated** — Monte-Carlo over CACE is the open item, and
the only thing that could still sink the change. The sweep scripts are in
`testbenches/xschem/simulations/` (`mt_sweep.py`, `mt_corners.py`,
`mt_edges.py`), which is a build directory and not in git.

## Not imported yet

`compliance/`, `predriver/` and `serdes/` batch benches, `predelay` (verified but out
of the chain), and the findings documents under `docs/`. The routed `Driver` layout in
`LVDS-PLL_Private` was not imported either: the placement here is generated from this
repository's own schematic hierarchy, which puts `Driver` one level down inside
`lvds_tx` rather than at the top.
