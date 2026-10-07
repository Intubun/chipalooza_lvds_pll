#!/usr/bin/env python3
"""The top layout with lvds_pattern without its clock source select (2026-10-07).

lvds_pattern lost pll_clk and clk_src (macros/lvds_pattern/scripts/
drop_clk_select.py); ref_clk now clocks the gate directly.  In the top:

* the copy of lvds_pattern is replaced by the macro's new layout - its own
  shapes and its instances, the standard cells themselves are unchanged;
* the bridge split_pll.py drew from pll_clk to the pattern's VDD goes: the
  stack at y 105.915, the M4 down to y 95.23, the via3 there and the M3 that
  lengthened the VDD strap to x 339 - the strap is back at x 340..346.7;
* the M3 line of clk_src (y 107.915, x 117.01..339.43) and its via2 go: the
  pin is gone, and the line never reached dig_in.

    python3 scripts/top/drop_clk_select.py [--in <gds>] [--out <gds>]

Default in and out: layout/slot_14.gds; the .klay.gds becomes a copy of it.
"""
import datetime, os, shutil, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "layout/slot_14.gds")
OUT = arg("--out", "layout/slot_14.gds")
MACRO = "macros/lvds_pattern/layout/lvds_pattern.gds"

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell("slot_14")
V2, M3, V3, M4 = (ly.layer(l, 0) for l in (29, 30, 49, 50))

# ---------------------------------------------------------------- lvds_pattern
m = kdb.Layout(); m.read(MACRO)
src, dst = m.cell("lvds_pattern"), ly.cell("lvds_pattern")
assert "pll_clk" not in [s.text_string for s in src.shapes(m.layer(10, 25)).each()], \
    "the macro still has pll_clk - run macros/lvds_pattern/scripts/drop_clk_select.py first"
dst.clear()
for li in m.layer_indexes():
    dst.shapes(ly.layer(m.get_info(li))).insert(src.shapes(li))
for inst in src.each_inst():
    child = ly.cell(inst.cell.name)
    assert child is not None, inst.cell.name
    dst.insert(kdb.CellInstArray(child.cell_index(), inst.cplx_trans))
for li in m.layer_indexes():          # the copy has to be the macro, shape for shape
    a = kdb.Region(dst.begin_shapes_rec(ly.layer(m.get_info(li))))
    assert (a ^ kdb.Region(src.begin_shapes_rec(li))).is_empty(), m.get_info(li)


# ---------------------------------------------------------------- top-level rip-up
def kill(li, x0, y0, x1, y1):
    """erase the one shape whose bounding box is this"""
    b = kdb.DBox(x0, y0, x1, y1)
    hit = [s for s in top.shapes(li).each() if not s.is_text() and s.dbbox() == b]
    assert len(hit) == 1, (ly.get_info(li), b, len(hit))
    top.shapes(li).erase(hit[0])


def via(li, x, y):
    kill(li, x - 0.095, y - 0.095, x + 0.095, y + 0.095)


X = 339.28
# pll_clk -> VDD
via(V2, X, 105.915); via(V3, X, 105.915)
kill(M3, X - 0.15, 105.665, X + 0.15, 106.165)
kill(M4, X - 0.15, 95.23, X + 0.15, 106.07)
via(V3, X, 95.385)
kill(M3, 339.0, 94.385, 346.7, 96.385)
top.shapes(M3).insert(kdb.DBox(340.0, 94.385, 346.7, 96.385))
# clk_src
via(V2, X, 107.915)
kill(M3, 117.01, 107.815, X + 0.15, 108.015)

if OUT == SRC:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(SRC, "layout/backups/slot_14_VOR_clksel_%s.gds" % ts)
ly.write(OUT)
if OUT == "layout/slot_14.gds":
    shutil.copy2(OUT, "layout/slot_14.klay.gds")
print("geschrieben:", OUT)
