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
