# `lvds_pattern` — data source for the LVDS transmitter

`sg13cmos5l` standard cells and nothing else: a clock gate, a PRBS-7 generator
and a complementary output pair. `D_p` / `D_n` drive the pre-driver of
[`macros/lvds_tx/`](../lvds_tx/README.md).

## Interface

| pin | dir | meaning |
|---|---|---|
| `ref_clk` | in | the bit clock, one bit per period |
| `en` | in | `1` = clock runs, `0` = clock stopped **low** |
| `reset` | in | active high, asynchronous, seeds the PRBS |
| `mode` | in | `0` = gated clock straight to the pair, `1` = PRBS-7 |
| `D_p`, `D_n` | out | complementary data pair to the pre-driver |
| `VDD`, `VSS` | inout | 1.2 V core supply |

**All-zero is a working setting**, which the harness requires: `en` = 0 stops
the clock, `reset` = 0 is *not* reset, `mode` = 0 is passthrough. The block then
sits with `D_p` low and `D_n` high — a static, legal state for the driver, not a
broken one.

**No clock source select any more.** Until 2026-10-07 a `mux2_2` (`xcsel`) in
front of the gate chose between `ref_clk` and `pll_clk` on `clk_src`. The PLL left
the project that day, and the mux, both pins and their lines went with it
(`scripts/drop_clk_select.py`); five `fill_2` and a `fill_1` hold its sites, and
`ref_clk` runs on along its M2 onto the old mux output, the line to CLK of both
`lgcp_1`. Every other pin kept its place on the symbol and in the layout.

**Antenna diodes on `en` and `mode`.** At the top level both arrive over ~360 um
of Metal3 from `dig_in` and end on one gate (`en`, the clock gate) or two (`mode`,
the two output muxes): over the antenna ratio of 200 without a diode (`Ant.b`).
Two `sg13cmos5l_antennanp` (`xant_en`, `xant_mode`) sit in the slot `xcsel` left,
next to the fills, and lift the limit to 20000 (`Ant.e`) for every user of the
block (`scripts/add_antenna_diodes.py`). A third (`xant_ref`) went onto `ref_clk`
when the clock moved to pad 2 and its line to ~450 um of Metal4
(`scripts/add_refclk_diode.py`); it also clamps the clock gates' input to the
block's own 1.2 V rails, which the pad's secondary protection - diodes to the
3.3 V IO ring - does not. `reset` stays under the limit without one.

## How it is built

```
ref_clk ─ lgcp_1 ─ buf_4 ─┬────────────────────────── gclk_b ─┐
          (en)            │                                  │
                          └─ 7 × dfrbp ─ xnor2 feedback       ├─ mux2_2 ─┬─ inv_2 ─ inv_8 ─ buf_16 ─ D_p
reset ─ inv_2 ─ reset_b ──── to every flop         s6_n ──────┘  (mode)  └─ inv_2 ─ inv_8 ─ inv_16 ─ D_n
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

**The pair is registered after the inversion.** `s6` goes straight into `xffp` and,
through `xinvd` (`inv_1`), into `xffn` — two identical `dfrbp_2` on the same clock.
What leaves those flops is two edges from the same cell type at the same instant;
the inverter sits in the D path only, so its delay is absorbed by the output flops'
setup margin instead of appearing as output skew. (Until 2026-10-02 `xffn` took
`s6_n`, `Q_N` of `xs6`, with the same effect; the inverter came in with the layout
rework below, where it saved routing `s6_n` across the block.)

**Those two flops answer to neither `en` nor `reset`, by construction.** They are
clocked by `gclk_free_b`, an ungated copy of the clock — a second `lgcp_1` with its
enable tied to VDD, then a second `buf_4`, so the cell types match the gated path —
and their `RESET_B` is tied high. Everything else in the block, the whole shift
register included, still stops on `en` and still seeds on `reset`.

The reason is the transmitter, not this block. `dfrbp` drives **both** `Q` and `Q_N`
to 0 on reset, so a reset output pair is not complementary: it leaves as two equal
levels, and the driver's common-mode loop has no valid operating point to sit at. It
runs to a rail and needs ~60 ns to climb back every time the pattern is enabled.
Hanging the output flops off the gated clock had the same effect for `en = 0` — never
clocked, never reset, both sides drifting to the same level.

`s6` and its inverse are opposite in *every* state the register can hold: held in
reset (`s6` = 0, so the pair loads `D_p` = 1, `D_n` = 0), stopped by `en`, or running.
Clocking the two output flops unconditionally therefore hands the driver a
complementary pair from the first edge after power-up, and `en` still does its job —
the register stops, the output pair just holds its last complementary value instead
of collapsing. A reset in the middle of operation does not disturb the pair either:
simulated (this block from the schematic, the extracted driver as load, a reset
pulse of 10 ns in the middle of PRBS-7), the pair never shows two equal levels and
`Vos` stays within 27 mV pp through the reset.

The library has no reset-less flop: `dfrbp`, `dfrbpq`, `sdfrbp` and `sdfbbp` all carry
`RESET_B`. Tying it high is that flop.

**Not `sdfbbp_1`.** The first layout (2026-10-02, `b6ddedf`) placed two
`sg13cmos5l_sdfbbp_1` instead, `xffp` reset and `xffn` set by `reset_b`, for a
complementary state without a clock edge. That cell comes in drive 1 only, its `Q`
rises ~50 ps slower than it falls, and in the layout `xffn`'s `Q` wire carried 7.0 fF
against 4.3 fF on `xffp`. Extracted, the pair came out one-sided: `D_p` rose 28 ps
before `D_n` fell (39 ps at ss, 125 °C), and the lvds_tx pre-driver turned that into
`Vos` pp of 154 mV at ss, 125 °C, 2.97 V - over the 150 mV of TIA/EIA-644-A
(lvds_tx README, *Output crossing point*). `scripts/rework_outflops.py` put the
`dfrbp_2` back, mirrored against each other so both `Q` pins sit in the middle of
the row and `fp`/`fn` leave together (4.7 / 5.1 fF). `D_p`/`D_n` skew, extracted
(magic, coupling C), with the extracted lvds_tx as load, PRBS-7 at 500 Mb/s,
`D_p` rising / falling:

| | tt, 27 °C | tt, −40 °C, 3.63 V | ss, 125 °C, 2.97 V |
|---|---|---|---|
| `sdfbbp_1` | −28.5 / +2.1 ps | — | −38.9 / +3.5 ps |
| **`dfrbp_2`** | **+13.1 / −17.9 ps** | **+11.1 / −15.1 ps** | **+15.7 / −22.1 ps** |

The rest is symmetric: the falling output now comes ~15 ps early on either side,
which the pre-driver tolerates far better than one rising edge early (`Vos` pp on
that bench 154 → 80 mV at ss, 125 °C).

The capture clock is ~38 ps **earlier** than `gclk_b`, because its buffer drives two
flop clock pins instead of seven. That is skew in the safe direction: the launch flop
`xs6` sits on `gclk_b`, so an early capture edge adds hold margin and costs 38 ps of
the ~500 ps setup slack. The hold table below puts the tolerated skew at ~160 ps at
the hold-critical corner. From there the two sides are symmetric all the way out: one `mux2_2`
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

**Since `b6ddedf` the `.sch` is ahead of the table**: the decap cells and the
output-flop changes (`sdfbbp_1`, then `dfrbp_2` with `xinvd`, 2026-10-02) were
made in the `.sch` itself, so `make gen` would drop them - and the two antenna
diodes (2026-10-07) as well. Bring `CELLS` up to the `.sch` before using it
again. The benches, the symbol and the CACE template are still written by the
scripts (`gen_tb`, `gen_tb_prbs`, `gen_sym`; `cace/gen_template.py`).

The benches include `models/diodes_tt0.lib` from the repository root: the
antenna diodes stall ngspice with the PDK's own diode model, see
`scripts/sim/make_diode_models.py`.

## Running

```bash
make sim-all        # both benches and their checks
make sim-prbs       # the PRBS-7 timing bench on its own
make gen            # regenerate the schematic after editing the cell table
```

The bench walks the whole interface: reset high, clock stopped, then
passthrough of `ref_clk` at 1 GHz, then PRBS-7 at 1 Gb/s for a full 127-bit
period, then `en` low to show the clock gate. Current result at tt/27 °C,
1.2 V, 170 fF load:

```
bit rate             1.000 Gb/s
clock to output      441.1 ... 448.0 ps  (spread 6.9 ps)
data valid window    0.448 ... 1.441 ns after the edge, 99.3% of a UI
PRBS-7 mismatches    0 of 138 checked
non-complementary    0 samples
worst D_p/D_n skew   12.7 ps
```

Clock-to-output is measured against `gclk_b`, the gated clock, while the output flops
now run off the ungated copy — which is the ~38 ps that came off the figure. The two
numbers that describe the eye, the 6.9 ps spread and the 12.7 ps skew, are unchanged.

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

No LibreLane run, no STA. The layout is placed and routed by hand, DRC and LVS
clean; the timing figures above are from simulation, and the extracted block
drives the post-layout LVDS bench at the top level
(`testbenches/xschem/slot_14_tb_lvds_postlayout.sch`).

The top level instantiates this macro as `xpat` and wires `D_p`/`D_n` straight
into `lvds_tx`. `ref_clk` comes from pad 2 through its secondary protection
(`s14_an_2_esd`), `en` / `reset` / `mode` from `dig_in[1]` / `[2]` / `[3]`.
