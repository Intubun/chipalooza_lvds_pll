#!/usr/bin/env python3
"""Replace the copy of a macro in the top layout with the macro's own layout.

    python3 scripts/top/refresh_macro.py <cell> [--in <gds>] [--out <gds>]

The top GDS carries a copy of every macro cell.  When a macro's layout changes
(macros/<cell>/layout/<cell>.gds), this swaps the copy: the cell's own shapes
and its instances; child cells the top does not have yet are copied in, those
it has (standard cells) are taken as they are.  It then checks that the copy
is the macro, shape for shape, on every layer.
"""
import datetime, os, shutil, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
CELL = sys.argv[1]
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "layout/slot_14.gds")
OUT = arg("--out", "layout/slot_14.gds")

ly = kdb.Layout(); ly.read(SRC)
m = kdb.Layout(); m.read("macros/%s/layout/%s.gds" % (CELL, CELL))
src, dst = m.cell(CELL), ly.cell(CELL)
assert dst is not None, "%s is not in %s" % (CELL, SRC)


def copy_leaf(name):
    """a child cell the top does not have yet: shapes only (library cells are leaves)"""
    c = ly.create_cell(name)
    mc = m.cell(name)
    assert mc.child_cells() == 0, "%s has children - extend refresh_macro.py" % name
    for li in m.layer_indexes():
        c.shapes(ly.layer(m.get_info(li))).insert(mc.shapes(li))
    return c


dst.clear()
for li in m.layer_indexes():
    dst.shapes(ly.layer(m.get_info(li))).insert(src.shapes(li))
for inst in src.each_inst():
    child = ly.cell(inst.cell.name) or copy_leaf(inst.cell.name)
    dst.insert(kdb.CellInstArray(child.cell_index(), inst.cplx_trans))
for li in m.layer_indexes():
    a = kdb.Region(dst.begin_shapes_rec(ly.layer(m.get_info(li))))
    assert (a ^ kdb.Region(src.begin_shapes_rec(li))).is_empty(), m.get_info(li)

if OUT == SRC:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(SRC, "layout/backups/slot_14_VOR_refresh_%s_%s.gds" % (CELL, ts))
ly.write(OUT)
if OUT == "layout/slot_14.gds":
    shutil.copy2(OUT, "layout/slot_14.klay.gds")
print("geschrieben: %s (%s aus macros/%s)" % (OUT, CELL, CELL))
