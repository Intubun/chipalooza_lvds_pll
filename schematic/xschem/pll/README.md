# Integer/fractional-N PLL

## Interface

| Port | Direction | Purpose |
|---|---|---|
| `REF_CLK` | input | 25-250 MHz reference clock |
| `IREF` | analog input | 2 uA charge-pump current reference |
| `ENABLE` | input | PLL enable; low resets digital state |
| `RESET_N` | input | active-low reset |
| `DIV_INT[6:0]` | input | integer feedback divisor, 4-80 |
| `DIV_FRAC[15:0]` | input | fractional numerator over 65536; use zero for integer-N |
| `TEST_DIV[1:0]` | input | selects VCO/2, /4, /8 or /16 test output |
| `PLL_CLK` | output | 500 MHz-1 GHz clock for the SerDes clock mux |
| `TEST_CLK` | output | divided test/observability clock |
| `VDD`, `VSS` | power | 1.2 V supply and ground |

`PLL_CLK = REF_CLK * (DIV_INT + DIV_FRAC / 65536) / 2`.

## Which top-level view to use

1. Add `pll_cosim.sym` to an Xschem top for configurable RTL/transistor simulation.
2. Add `pll_analog.sym` to the physical analog top; it is the custom-layout/LVS macro.
3. Harden `rtl/pll_digital.v` separately and connect its `up/down` and `vco_clk` to `pll_analog`.
4. Use `pll.sym` only for fixed-ratio XSPICE characterization; do not lay it out.
5. Use `rtl/pll_behavioral.v` instead of a `.sym` for fast full-chip/SerDes RTL simulation.
