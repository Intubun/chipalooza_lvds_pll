# Top-level DRC and LVS

Run inside the IIC-OSIC-TOOLS container, from anywhere:

```bash
make check              # both, from the repository root
make check-drc          # DRC only      (ARGS="--no-antenna --density")
make check-lvs          # LVS only      (ARGS=--ignore-ports)

bash scripts/verify/check_drc.sh [--no-antenna] [--density] [<gds>]
bash scripts/verify/check_lvs.sh [--ignore-ports] [<gds>]
bash scripts/verify/check_all.sh [any of the above]
```

Both check `layout/slot_14.gds` unless another copy is given, print a
summary, and exit with 0 only when they are clean. Save in KLayout first:
they read the file on disk.

| | results in | open in KLayout |
|---|---|---|
| DRC | `build/verify/drc/` | `*_full.lyrdb` - Tools > Marker Browser |
| LVS | `build/verify/lvs/` | `layout.lvsdb` - Tools > Netlist Browser |

## What they compare

**LVS** takes the top schematic `schematic/xschem/slot_14.sch` (exported as
CDL by xschem, with the PDK's standard-cell CDL in front of it for
`lvds_pattern`) against a copy of the layout. The schematic carries the
slot-14 frame pin for pin (`scripts/gen_top.py`), so the top-level pin names
are compared as well; `--ignore-ports` leaves them out and compares the
circuit behind the pins only.

**One ground.** `vss_1v2` and `vss_3v3` come out of the extraction as one net:
every substrate tap of either sits in the same p-substrate, and the IHP deck
connects taps straight to it. That is also what the chip does - the harness
ties them (`chipalooza_frame.v`: `assign vss3v3 = vss1v2`). The schematic keeps
both frame pins, so `check_lvs.sh` runs a copy of the deck
(`build/verify/lvs_deck/`) that joins the two nets in the reference right after
reading it (`LVS_JOIN_NETS`). Both remain pins, so the strict port check still
sees both names.

**DRC** runs the IHP deck over the whole layout, with the antenna rules, and
sorts what it finds by the top-level instance it sits in, so a macro's own
errors and the top level's wiring do not mix.

## What they leave out, and why

**Density** is off by default: the slot gets its fill, and its density check,
at chip level. **Taps** are not extracted as devices and **floating metal**
is purged, as in the macro LVS runs.

**The PLL** left the project on 2026-10-07. Until then the LVS took it out of
both sides (it was an XSPICE `d_cosim` model in the schematic) and the DRC
listed the errors in its cells without counting them; the DRC summary still
does that for any cell named `pll`, with `--with-pll` to count them.
