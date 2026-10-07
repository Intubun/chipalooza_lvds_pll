#!/usr/bin/env python3
"""lvds_pattern.gds: antenna diodes on en and mode (2026-10-07).

At the top level en and mode arrive on ~360 um of metal3 from dig_in[1] and
dig_in[3] and end on the gate of one lgcp_1 (en) and of the two mode muxes:
Ant.b (cumulative metal area / gate area, no diode) is over 200 on metal3, 4
and TopMetal1.  A diode on the net lifts the limit to 20000 (Ant.e), so each
input gets a sg13cmos5l_antennanp - n+ and p+ diode, A to VSS and to VDD -
inside the block, where every user of the macro gets them.

They go into the slot xcsel left (row y 3.78..7.56, x 4.32..9.6, filled since
drop_clk_select.py):

    antennanp (en) | antennanp (mode) | fill_2 | fill_2 | fill_1
    4.32             5.76               7.20     8.16     9.12 .. 9.60

* en:   via1 on A, metal2 straight down to the en line at y 2.85..3.15;
* mode: via1 + via2 on A, metal3 down across en to the mode line at
        y 0.595..0.895 and via2 onto it - metal2 would short to en.

    python3 scripts/add_antenna_diodes.py [--out <file>]     (default: layout/lvds_pattern.gds)
"""
import datetime, os, shutil, sys
import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
GDS = os.path.join(HERE, "..", "layout", "lvds_pattern.gds")
STD = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"],
                   "libs.ref/sg13cmos5l_stdcell/gds/sg13cmos5l_stdcell.gds")
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else GDS
ly = kdb.Layout(); ly.read(GDS); top = ly.cell("lvds_pattern")
V1, M2, V2, M3 = (ly.layer(l, 0) for l in (19, 10, 29, 30))
D = lambda v: int(round(v / ly.dbu))
VIA = 0.19

assert ly.cell("sg13cmos5l_antennanp") is None, "already has antenna cells"
std = kdb.Layout(); std.read(STD)
src = std.cell("sg13cmos5l_antennanp")
ant = ly.create_cell("sg13cmos5l_antennanp")
ant.copy_tree(src)          # a leaf cell: shapes only

# ---------------------------------------------------------------- the slot
ROW_Y = 3.78
fills = [i for i in top.each_inst() if i.cell.name.startswith("sg13cmos5l_fill_")
         and abs(i.dcplx_trans.disp.y - ROW_Y) < 1e-3 and 4.3 < i.dcplx_trans.disp.x < 9.2
         and str(i.trans).startswith("r0 ")]
assert len(fills) == 6, [(i.cell.name, i.dcplx_trans) for i in fills]
for i in fills:
    i.delete()
for x, cell in ((4.32, ant), (5.76, ant), (7.20, ly.cell("sg13cmos5l_fill_2")),
                (8.16, ly.cell("sg13cmos5l_fill_2")), (9.12, ly.cell("sg13cmos5l_fill_1"))):
    top.insert(kdb.CellInstArray(cell.cell_index(), kdb.Trans(kdb.Trans.R0, D(x), D(ROW_Y))))


def box(li, x0, y0, x1, y1):
    top.shapes(li).insert(kdb.DBox(x0, y0, x1, y1))


def via(li, x, y):
    box(li, x - VIA / 2, y - VIA / 2, x + VIA / 2, y + VIA / 2)


# A pin of antennanp: metal1 x 0.38..0.63, y 1.13..2.41; the via1 sits at (0.505, 1.55)
AY = ROW_Y + 1.55
# en
x = 4.32 + 0.505
via(V1, x, AY)
box(M2, x - 0.1, 2.85, x + 0.1, AY + VIA / 2 + 0.05)
# mode
x = 5.76 + 0.505
via(V1, x, AY); via(V2, x, AY)
box(M2, x - 0.15, AY - 0.25, x + 0.15, AY + 0.25)                 # 0.15 um2 (Mn.d)
box(M3, x - 0.1, 0.745 - VIA / 2 - 0.05, x + 0.1, AY + VIA / 2 + 0.05)
via(V2, x, 0.745)                                               # onto the mode line
for li in (M2, M3):
    r = kdb.Region(top.shapes(li)).merged(); top.shapes(li).clear(); top.shapes(li).insert(r)

if out == GDS:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(GDS, os.path.join(HERE, "..", "layout", "backups",
                                   "lvds_pattern_VOR_antenna_%s.gds" % ts))
ly.write(out)
print("geschrieben:", out)
