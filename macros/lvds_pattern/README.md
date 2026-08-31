# `lvds_pattern` — data source for the LVDS transmitter

Nineteen `sg13cmos5l` standard cells and nothing else: a clock source select, a
clock gate, a PRBS-7 generator and a complementary output pair. `D_p` / `D_n`
drive the pre-driver of [`macros/lvds_tx/`](../lvds_tx/README.md).

## Interface

| pin | dir | meaning |
|---|---|---|
| `ref_clk` | in | reference clock |
| `pll_clk` | in | clock from the PLL |
| `clk_src` | in | `0` = `ref_clk`, `1` = `pll_clk` |
| `en` | in | `1` = clock runs, `0` = clock stopped **low** |
| `reset` | in | active high, asynchronous, seeds the PRBS |
| `mode` | in | `0` = gated clock straight to the pair, `1` = PRBS-7 |
| `D_p`, `D_n` | out | complementary data pair to the pre-driver |
| `VDD`, `VSS` | inout | 1.2 V core supply |

**All-zero is a working setting**, which the harness requires: `clk_src` = 0
selects the reference, `en` = 0 stops the clock, `reset` = 0 is *not* reset,
`mode` = 0 is passthrough. The block then sits with `D_p` low and `D_n` high —
a static, legal state for the driver, not a broken one.

## How it is built

```
ref_clk ─┐
         ├─ mux2_2 ─ lgcp_1 ─ buf_4 ─┬────────────────────────── gclk_b ─┐
pll_clk ─┘  (clk_src)   (en)          │                                  │
                                      └─ 7 × dfrbp ─ xnor2 feedback       ├─ mux2_2 ─┬─ inv_2 ─ inv_8 ─ buf_16 ─ D_p
reset ─ inv_2 ─ reset_b ──────────────── to every flop         s6_n ──────┘  (mode)  └─ inv_2 ─ inv_8 ─ inv_16 ─ D_n
```

**Clock gating** uses the PDK's own latch-based gate `sg13cmos5l_lgcp_1`, not an
AND. `en` may therefore change at any point in the cycle without producing a
runt pulse, and `GCLK` parks low rather than high.

**PRBS-7** is `x⁷ + x⁶ + 1`, and the stream is *bit-identical* to the one
`serdes_dig.v` puts on the line in PRBS7 mode — so `serdes/check_link.py` on the
analog side works against this block unchanged. Getting there needs one trick:
`dfrbp` resets `Q` to 0, but the reference LFSR seeds to all ones. The seven
flops therefore hold the **complement** of the LFSR word. An all-zero complement
*is* the all-ones seed, the feedback becomes `XNOR(s6, s5)` instead of XOR, and
the bit that goes to the line is `s6_n`. No set-capable flop, no seed logic.

**The output pair** is where the design effort went. `D_p` and `D_n` each drive
two 40 µm/0.45 µm HV gates inside `predriver_comp`, about 170 fF, and
`docs/predriver-findings.md` in the LVDS design repo puts the pre-driver's skew
budget at roughly 40 ps. A single-ended source cannot produce a zero-skew
complement in static CMOS — the two paths differ by one inversion — so the
pairing was chosen by measurement into that load:

| output stage | measured `D_p`/`D_n` skew |
|---|---|
| `buf_4` / `inv_8` | 53 ps |
| `xor2` / `xnor2` against `VSS`, then `buf_4` | 48 ps |
| `dfrbp` `Q`/`Q_N` through a mirrored `mux2` pair | 39 ps |
| **`inv_2`→`inv_8`→`buf_16` against `inv_2`→`inv_8`→`inv_16`** | **23 ps** |

`buf_16` is two internal stages, so the true side sees four inversions against
the complement side's three; the sizes make the two totals nearly equal. The
`xor2`/`xnor2` pair looks like the textbook answer and is the *worst* of the
symmetric options here, because the two cells are not built alike.

## Files

| path | what |
|---|---|
| `schematic/xschem/lvds_pattern.sch`, `.sym` | the block, **generated** |
| `testbenches/xschem/lvds_pattern_tb_tran.sch` | transient bench, **generated** |
| `scripts/gen_schematic.py` | the cell table the three files come from |
| `scripts/check_prbs.py` | replays the polynomial over the simulation output |

The schematic is written out from a table rather than drawn, so the drawing and
the net list cannot drift: every pin of every cell is named exactly once in
`CELLS`. Edit the table, run `make gen`, do not hand-edit the `.sch`.

## Running

```bash
make sim-all        # transient bench, then the PRBS check
make gen            # regenerate the schematic after editing the cell table
```

The bench walks the whole interface: reset high, clock stopped, then
passthrough of `pll_clk` at 1 GHz, then PRBS-7 at 1 Gb/s for a full 127-bit
period, then `en` low to show the clock gate, then `clk_src` low to hand over to
the 250 MHz reference. Current result at tt/27 °C, 1.2 V, 170 fF load:

```
bit rate            1.000 Gb/s
PRBS-7 mismatches   0 of 128 checked
non-complementary   0 samples
worst D_p/D_n skew  23.0 ps
```

## Not done yet

No layout, no LibreLane run, no STA. The flop chain closes timing at 1 GHz in
simulation at the typical corner with no wire load; whether it still does over
PVT with real routing is a question for the hardening flow, not for this
schematic.

The top level instantiates this macro as `xpat` and wires `D_p`/`D_n` straight
into `lvds_tx`. `pll_clk` is tied to `ui_in[7]` there as a **placeholder**: a
shared harness gpio cannot really carry 500 MHz…1 GHz, and that input becomes
`pll_analog`'s output as soon as the PLL is placed at the top level.
