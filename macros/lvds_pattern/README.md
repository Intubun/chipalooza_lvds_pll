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

**The pair is registered after the inversion.** `s6` and `s6_n` — the line bit and
its native complement, both straight off the last shift-register flop — go into two
identical `dfrbp_2` on the same clock, `xffp` and `xffn`. What leaves those flops is
two edges from the same cell type at the same instant, so the Q/Q_N mismatch of
`xs6` (~55 ps) is absorbed by the output flops' setup margin instead of appearing as
output skew. From there the two sides are symmetric all the way out: one `mux2_2`
per polarity and two identical `inv_2` → `inv_8` → `inv_16` chains.

That symmetry is what removed the parity problem. The earlier version formed the
complement *after* the mux, so one side saw four inversions and the other three, and
the mismatch had to be traded off by sizing — 23.7 ps at best, 15…36 ps over PVT.
With the pair registered, the chains are identical and there is nothing left to
compensate:

| | skew | clock-to-out spread | data valid window |
|---|---|---|---|
| complement after the mux, sized to match | 23.7 ps | 15.8 ps | 98.4 % UI |
| **registered pair, identical chains** | **12.4 ps** | **6.8 ps** | **99.3 % UI** |

`dsum` — the sum of the two outputs, which is 2 × the common mode — went from
0.81…1.61 V to 0.97…1.22 V, i.e. the crossing barely disturbs the pair any more.

**Clock passthrough keeps one inverter of skew and that is deliberate.** The
passthrough leg feeds `gclk_b` to one mux and `xclkn`'s inverted copy to the other,
so in that mode the pair is one inverter apart (measured −50.9 ps). Registering the
passthrough path is not possible — a flop clocked by the signal it samples produces
a constant — and passthrough is a bring-up and debug mode, not the mode an eye is
measured in.

## Files

| path | what |
|---|---|
| `schematic/xschem/lvds_pattern.sch`, `.sym` | the block, **generated** and **drawn** - every local connection is a real wire |
| `testbenches/xschem/lvds_pattern_tb_tran.sch` | walks the whole interface, **generated** |
| `testbenches/xschem/lvds_pattern_tb_prbs.sch` | PRBS-7 only, for timing, **generated** |
| `scripts/gen_schematic.py` | the cell table all four files come from |
| `scripts/check_timing.py` | measures the sampling phase, then replays the polynomial |

The schematic is written out from a table rather than drawn, so the drawing and
the net list cannot drift: every pin of every cell is named exactly once in
`CELLS`. Edit the table, run `make gen`, do not hand-edit the `.sch`.

## Running

```bash
make sim-all        # both benches and their checks
make sim-prbs       # the PRBS-7 timing bench on its own
make gen            # regenerate the schematic after editing the cell table
```

The bench walks the whole interface: reset high, clock stopped, then
passthrough of `pll_clk` at 1 GHz, then PRBS-7 at 1 Gb/s for a full 127-bit
period, then `en` low to show the clock gate, then `clk_src` low to hand over to
the 250 MHz reference. Current result at tt/27 °C, 1.2 V, 170 fF load:

```
bit rate             1.000 Gb/s
clock to output      479.6 ... 486.3 ps  (spread 6.8 ps)
data valid window    0.486 ... 1.480 ns after the edge, 99.3% of a UI
PRBS-7 mismatches    0 of 138 checked
non-complementary    0 samples
worst D_p/D_n skew   12.4 ps
```

**The checker measures the sampling phase, it does not assume one.** An earlier
version sampled half a bit after the clock edge, which happens to be almost
exactly where this block's data transitions - clock to output is ~515 ps against
a 1000 ps bit - so it was reading the eye at its worst point and reported half
the samples as non-complementary. `check_timing.py` finds the transition each
clock edge causes, closes the window from the spread of those delays, and samples
in the middle of it. The window is 98.4 % of a UI because the clock-to-output
spread is only 16 ps; the absolute delay does not cost eye, only latency.

### Delay cells: measured, and not needed here

Two places were considered.

**In the output pair, to trim the skew.** That question is closed by construction —
the two chains are identical now, so there is no systematic difference to trim. It
was measured first: over 27 PVT points the old asymmetric pair drifted 15.1…36.3 ps,
always the same sign, and the smallest PDK delay gate adds **63 ps** against a plain
`buf_4` (`dlygate4sd2_1` 115 ps, `dlygate4sd3_1` 300 ps). The smallest cell was 2.5×
the ~25 ps that wanted cancelling, so it would have flipped the sign rather than
removed the skew. Symmetry was the cheaper fix.

**In the shift register, against hold violations.** Measured directly: two `dfrbp_2`
in series, artificial clock skew swept until the chain collapses.

| corner | tolerated clock skew |
|---|---|
| ss, 27 °C, 1.2 V | between 300 and 400 ps |
| tt, 27 °C, 1.2 V | between 250 and 300 ps |
| ff, 27 °C, 1.2 V | between 200 and 250 ps |
| **ff, −40 °C, 1.32 V** (hold-critical) | **between 160 and 180 ps** |

Hold is worst at the fast corner, as expected, and the register still tolerates
**~160 ps** of clock skew there. A block of twenty-odd cells will not see anything
close to that from its clock tree, so there is nothing to fix at this level — and
sizing a hold buffer now means guessing at a skew number that does not exist until
after placement and clock tree synthesis. If the macro is hardened by a flow that
does hold fixing, it will insert what it needs with the real numbers. If it is ever
placed by hand, revisit this with the extracted clock skew: one `dlygate4sd1_1` per
data path buys 63 ps of hold margin and costs 63 ps of the ~500 ps setup slack.

## Not done yet

No layout, no LibreLane run, no STA. The flop chain closes timing at 1 GHz in
simulation at the typical corner with no wire load; whether it still does over
PVT with real routing is a question for the hardening flow, not for this
schematic.

The top level instantiates this macro as `xpat` and wires `D_p`/`D_n` straight
into `lvds_tx`. `pll_clk` is tied to `ui_in[7]` there as a **placeholder**: a
shared harness gpio cannot really carry 500 MHz…1 GHz, and that input becomes
`pll_analog`'s output as soon as the PLL is placed at the top level.
