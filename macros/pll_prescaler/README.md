# PLL TSPC dual-modulus prescaler

This macro is the custom high-speed front end for `macros/pll_digital`. It
implements a synchronous `/2-/3` prescaler using ratioed true-single-phase-
clock (TSPC) flip-flops based on Razavi, *Design of CMOS Phase-Locked Loops*,
Chapter 15.

Only this macro sees the full VCO rate. The portable RTL pulse-swallow counter
and fractional accumulator run from `Q2`, at no more than half that rate.

## Interface

| Pin | Direction | Function |
| --- | --- | --- |
| `CLK` | input | Full-rate VCO clock |
| `RESET_B` | input | Asynchronous active-low reset |
| `MODULUS_REQUEST` | input | `1` selects `/2`; `0` selects `/3` |
| `Q2` | output | Prescaled clock and safe modulus-sampling boundary |
| `VDD`, `VSS` | power | 1.2 V nominal core supply |

`MODULUS_REQUEST` is prepared one `Q2` cycle early and captured inside the
macro on the next rising `Q2` edge. This removes the impossible standard-cell
clock-to-Q path between the modulus controller and the next 2 GHz VCO edge.

## Characterization

From the repository root, in the IIC-OSIC container:

```sh
python3 macros/pll_prescaler/scripts/characterize_prescaler.py
```

The sweep tests `/2` and `/3` at the maximum measured buffered-VCO frequency
for SS, TT, FF, SF, and FS. Results are written to
`info/pll_tspc_div23_pvt.csv`.

After physical signoff, repeat the same sweep against the full-RC extracted
netlist:

```sh
python3 macros/pll_prescaler/scripts/characterize_prescaler.py --pex
```

Extracted results are written to `info/pll_tspc_div23_pex_pvt.csv`.
