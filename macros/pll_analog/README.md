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

## Layout

The editable layout source is the Magic hierarchy in `layout/mag/`, with one
cell per schematic subcircuit. `layout/pll_analog.gds` is its exported view for
KLayout sign-off and integration.

```bash
make layout-view       # open layout/mag/pll_analog.mag in Magic
make layout-export     # write layout/pll_analog.gds from the Magic hierarchy
make klayout-drc       # sign-off DRC of the exported GDS
```

The initial SPICE import is an unrouted placement: seven subcircuits and 13
distinct PDK-generated device cells in a 138.51 x 134.65 um bounding box. The
large loop-filter capacitor dominates the area. It is a legal 100 x 100 um
Metal2-Metal4 `cap_cmomf`, giving 9.15 pF in the PDK's nominal low-frequency
model.

KLayout macro-level DRC is clean on the unrouted placement. Magic `drc(full)`
reports minimum-area markers in the PDK-generated short-channel MOS device
cells, so the Magic result is not clean even though the sign-off deck accepts
the same geometry.

## Views

- Use `schematic/xschem/pll_analog.sym` for the physical analog macro.
- Use `schematic/xschem/pll_cosim.sym` only for configurable RTL/transistor simulation.
- `schematic/xschem/pll.sym` is a fixed-ratio XSPICE characterization view;
  it is not a layout view.
