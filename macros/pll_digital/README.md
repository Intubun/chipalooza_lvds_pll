# PLL digital macro

`pll_digital` is the synthesizable standard-cell portion of the fractional-N
PLL: PFD, N/N+1 fractional feedback divider, fixed divide-by-two SerDes output,
and programmable test divider.

The macro receives `REF_CLK` (25-250 MHz) and the analog macro's `VCO_CLK`.
Its external configuration inputs are `RESET_N`, `ENABLE`, `DIV_RATIO[9:0]`,
and `TEST_DIV[1:0]`. `DIV_RATIO` is unsigned Q7.3 fixed point: bits `[9:3]`
are the integer divider and bits `[2:0]` select eighths. It returns `PLL_CLK`, `TEST_CLK`, `UP`,
and `DOWN`; `FB_CLK` is exposed only for debug and may be left unconnected.

For the physical Xschem top, instantiate `schematic/xschem/pll_digital.sym`
beside `../pll_analog/schematic/xschem/pll_analog.sym`. Connect `UP`, `DOWN`,
and `VCO_CLK` between the macros. The top-level layout must place the matching
`pll_digital` and `pll_analog` GDS macros.

The output relation is:

`PLL_CLK = REF_CLK * (DIV_RATIO / 8) / 2`.

## Physical implementation checkpoint (WIP)

The current implementation uses the fixed TSPC `/2` macro and a half-rate
fractional divider. All 992 legal Q7.3 settings and nine behavioral closed-loop
cases pass. Odd integer ratios alternate adjacent even VCO-cycle intervals;
this preserves the average ratio, not the original N/N+1 edge sequence.

Timing is not closed. The current RTL's routed run
`RUN_2026-10-11_01-28-19` has setup slack of -0.6037 ns at 1.08 V/125 C,
-0.0153 ns typical, and -0.0084 ns at the 1.35 V slow corner. Hold, slew and
capacitance checks pass. Earlier experiments passed five timing corners but
still failed 1.08 V. A successful flow exit is not all-corner signoff.

Local `final/`, `netlist/`, `render/`, and `verification/` exports predate this
RTL and are not published as matching integration artifacts in this checkpoint.
In particular, earlier green STA reports omitted unclocked registers and must
not be used as timing evidence. Rebuild matching views after timing closure.
The prescaler is PEX-verified separately; STA starts at its buffered half-rate
output because the macro has no Liberty model. Integrated analog/digital
editable-MAG DRC, LVS, antenna and full mixed-signal PEX verification remain.
