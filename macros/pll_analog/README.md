# PLL analog macro

This macro contains the charge pump, passive loop filter, and current-starved
ring VCO. The separately hardened `macros/pll_digital` macro provides the PFD,
fractional feedback divider, and output dividers.

## Physical interface

| Port | Direction | Purpose |
|---|---|---|
| `IREF` | analog input | 2 uA charge-pump current reference |
| `UP`, `DOWN` | input | charge-pump controls from `pll_digital` |
| `VCO_CLK` | output | VCO clock to `pll_digital` |
| `VDD`, `VSS` | power | 1.2 V supply and ground |

The layout source of truth will be `layout/pll_analog.klay.gds`; export it to
`layout/pll_analog.gds` before running DRC, LVS, or PEX.

## Views

- Use `schematic/xschem/pll_analog.sym` for the physical analog macro.
- Use `schematic/xschem/pll_cosim.sym` only for configurable RTL/transistor simulation.
- `schematic/xschem/pll.sym` is a fixed-ratio XSPICE characterization view;
  it is not a layout view.
