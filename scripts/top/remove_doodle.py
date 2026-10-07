#!/usr/bin/env python3
"""Take the silicon doodle (cell flags_doodle, top left) out of the top layout (2026-10-07).

    python3 scripts/top/remove_doodle.py [--in <gds>] [--out <gds>]

The cell was floating metal on metal1..4 (scripts/gen_doodle.py drew it); the
LVS purged it anyway, so nothing else changes.
"""
import datetime, os, shutil, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "layout/slot_14.gds")
OUT = arg("--out", "layout/slot_14.gds")

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell("slot_14")
c = ly.cell("flags_doodle")
assert c is not None, "no flags_doodle in %s" % SRC
assert [ly.cell(p).name for p in c.each_parent_cell()] == ["slot_14"]
c.prune_cell()                      # the instance, the cell and anything only it used
assert ly.cell("flags_doodle") is None

if OUT == SRC:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(SRC, "layout/backups/slot_14_VOR_doodle_%s.gds" % ts)
ly.write(OUT)
if OUT == "layout/slot_14.gds":
    shutil.copy2(OUT, "layout/slot_14.klay.gds")
print("geschrieben:", OUT)
