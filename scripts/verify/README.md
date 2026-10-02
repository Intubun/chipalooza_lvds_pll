# Top-level DRC and LVS

Run inside the IIC-OSIC-TOOLS container, from anywhere:

```bash
make check              # both, from the repository root
make check-drc          # DRC only      (ARGS="--with-pll --no-antenna --density")
make check-lvs          # LVS only      (ARGS=--strict-ports)

bash scripts/verify/check_drc.sh [--with-pll] [--no-antenna] [--density] [<gds>]
bash scripts/verify/check_lvs.sh [--strict-ports] [<gds>]
bash scripts/verify/check_all.sh [any of the above]
```

Both check `layout/sg13cmos5l_chipalooza_analog_project.gds` unless another
copy is given, print a summary, and exit with 0 only when they are clean.
Save in KLayout first: they read the file on disk.

| | results in | open in KLayout |
|---|---|---|
| DRC | `build/verify/drc/` | `*_full.lyrdb` - Tools > Marker Browser |
| LVS | `build/verify/lvs/` | `layout.lvsdb` - Tools > Netlist Browser |

## What they leave out, and why

**Rahul's PLL** is not finished yet.

* DRC runs over everything, but errors in cells that only the PLL uses are
  listed in one line and not counted. Errors in the top cell itself are
  counted; those lying on the PLL are marked, because they are the top level's
  own wiring to it - antenna on the PLL inputs, for instance. `--with-pll`
  counts the PLL cells as well.
* LVS removes the PLL on both sides (`prepare_lvs.py`): the instance `xpll`
  and the subcircuits only it uses from the schematic - it is the `pll_cosim`
  XSPICE model there, which no LVS reads - and the instance of the cell `pll`
  from a copy of the layout. Wires the top level runs to the PLL stay and end
  open; they belong to their nets either way. To bring the PLL in, the
  schematic needs a structural PLL (the hardened `pll_digital` netlist plus
  `pll_analog`) instead of `pll_cosim`.

**Top-level pin names** are not compared by default
(`--ignore_top_ports_mismatch`): the slot-14 frame names them `s14_an[0..2]`,
`ibias0`, `analog_bus1`, ..., while the schematic still has the template's
`analog_pin[0..3]`, `ibias[0]`, `analog_bus[1]`, ... The circuit behind the
pins is compared regardless. `--strict-ports` compares the names too, once the
schematic follows the frame.

**Density** is off by default: the slot gets its fill, and its density check,
at chip level. **Taps** are not extracted as devices and **floating metal**
(the flags doodle) is purged, as in the macro LVS runs.
