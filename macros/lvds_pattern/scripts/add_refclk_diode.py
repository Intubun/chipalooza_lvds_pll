#!/usr/bin/env python3
"""lvds_pattern.gds: a third antennanp, on ref_clk (2026-10-07).

Since ref_clk comes from pad 2 it reaches the two clock gates over ~450 um of
metal4 (scripts/top/swap_pads.py): Ant.b on metal4 and TopMetal1.  The diode pair
of an antennanp also does a second job here: ref_clk arrives from the pad's
secondary protection, whose diodes clamp to the IO ring (iovss / iovdd at
3.3 V), not to the 1.2 V rails the clock gates sit on - this one clamps the
gate node to VSS / VDD of the block itself.

It takes the place of fill_2 + the left half of the remaining fills in the slot
xcsel left (add_antenna_diodes.py):

    antennanp (en) | antennanp (mode) | antennanp (ref_clk) | fill_2
    4.32             5.76               7.20                  8.64 .. 9.60

A (via1 at 7.705, 5.33) goes straight up on metal2 into the ref_clk line at
y 6.69..6.99, which runs right over it.

    python3 scripts/add_refclk_diode.py [--out <file>]     (default: layout/lvds_pattern.gds)
"""
import datetime, os, shutil, sys
import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
GDS = os.path.join(HERE, "..", "layout", "lvds_pattern.gds")
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else GDS
ly = kdb.Layout(); ly.read(GDS); top = ly.cell("lvds_pattern")
V1, M2 = ly.layer(19, 0), ly.layer(10, 0)
D = lambda v: int(round(v / ly.dbu))
ROW_Y = 3.78

ant = ly.cell("sg13cmos5l_antennanp")
assert ant is not None, "run add_antenna_diodes.py first"
assert sum(1 for i in top.each_inst() if i.cell.name == "sg13cmos5l_antennanp") == 2, "already done"
fills = [i for i in top.each_inst() if i.cell.name.startswith("sg13cmos5l_fill_")
         and abs(i.dcplx_trans.disp.y - ROW_Y) < 1e-3 and 7.1 < i.dcplx_trans.disp.x < 9.2
         and str(i.trans).startswith("r0 ")]
assert sorted((round(i.dcplx_trans.disp.x, 2), i.cell.name) for i in fills) == \
    [(7.2, "sg13cmos5l_fill_2"), (8.16, "sg13cmos5l_fill_2"), (9.12, "sg13cmos5l_fill_1")], fills
for i in fills:
    i.delete()
top.insert(kdb.CellInstArray(ant.cell_index(), kdb.Trans(kdb.Trans.R0, D(7.20), D(ROW_Y))))
top.insert(kdb.CellInstArray(ly.cell("sg13cmos5l_fill_2").cell_index(), kdb.Trans(kdb.Trans.R0, D(8.64), D(ROW_Y))))

x, y = 7.20 + 0.505, ROW_Y + 1.55
top.shapes(V1).insert(kdb.DBox(x - 0.095, y - 0.095, x + 0.095, y + 0.095))
top.shapes(M2).insert(kdb.DBox(x - 0.1, y - 0.145, x + 0.1, 6.99))          # up into ref_clk (y 6.69..6.99)
r = kdb.Region(top.shapes(M2)).merged(); top.shapes(M2).clear(); top.shapes(M2).insert(r)

if out == GDS:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(GDS, os.path.join(HERE, "..", "layout", "backups", "lvds_pattern_VOR_refclkdiode_%s.gds" % ts))
ly.write(out)
print("geschrieben:", out)
