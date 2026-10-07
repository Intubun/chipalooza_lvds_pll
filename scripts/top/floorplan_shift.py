#!/usr/bin/env python3
"""Step 1 of the top-level layout: the LVDS group moves up, the old pad lines go.

    python3 scripts/top/floorplan_shift.py --in layout/slot_14_base.gds --out <gds>

layout/slot_14_base.gds is the hand-drawn floor plan before any routing script:
the blocks, the lines between them, their stubs, the three control lines from
dig_in - with the one-off edits split_pll.py, drop_clk_select.py and
remove_doodle.py applied.  The chain: scripts/top/build_layout.sh.  This script

* takes out the pad lines of the old assignment (Out_p -> pad 2, Out_n -> pad 1,
  ref_clk from pad 0) and restores the frame pins they had merged into;
* moves the LVDS group - lvds_pattern, lvds_tx, both iref_x15 and every shape
  between them and their stubs (box GROUP) - up by DY, so that the middle of
  lvds_tx's two outputs sits level with the middle of pads 0 and 1 (y 202.6):
  the pair now reaches its pads in ~60 and ~80 um instead of ~40 and ~180;
* takes out the three control lines from dig_in[1..3] (0.2 um metal3, the
  mode line with a metal2 bridge): route_top.py draws them anew, wider, to the
  pins where the group now sits.

The termination (ref_odt) and the decap rows stay where they are.
"""
import os, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "layout/slot_14_base.gds")
OUT = arg("--out", "build/top/1_shift.gds")
DY = 92.25                 # middle of Out_p / Out_n stubs (110.3) -> middle of pads 0 / 1 (202.57)
GROUP = kdb.DBox(338.5, 55.0, 446.0, 127.0)      # everything inside moves with the blocks
BLOCKS = ("lvds_pattern", "lvds_tx", "iref_x15")

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell("slot_14")
V2, M2, M3, V3, M4 = (ly.layer(l, 0) for l in (29, 10, 30, 49, 50))
D = lambda v: int(round(v / ly.dbu))
assert ly.cell("ref_odt") is None, "%s is past the routing steps" % SRC


def take(li, bbox):
    hit = [s for s in top.shapes(li).each() if not s.is_text() and s.dbbox() == kdb.DBox(*bbox)]
    assert len(hit) == 1, (ly.get_info(li), bbox, len(hit))
    p = hit[0].polygon
    top.shapes(li).erase(hit[0])
    return p


# ---------------------------------------------------------------- old pad lines
take(M3, (514.2, 25.18, 536.44, 102.455)); top.shapes(M3).insert(kdb.DBox(535.05, 25.18, 536.44, 49.95))
take(M3, (514.2, 118.145, 536.44, 159.95)); top.shapes(M3).insert(kdb.DBox(535.05, 135.18, 536.44, 159.95))
p = take(M3, (533.95, 238.2, 537.15, 238.7))
top.shapes(M3).insert(kdb.Region(p) - kdb.Region(kdb.DBox(533.9, 238.1, 535.15, 238.8).to_itype(ly.dbu)))
take(V3, (534.055, 238.355, 534.245, 238.545))
take(M4, (339.13, 109.76, 534.35, 238.65))

# ---------------------------------------------------------------- the group
t = kdb.Trans(0, D(DY))
n_inst = 0
for inst in list(top.each_inst()):
    if inst.cell.name in BLOCKS:
        inst.transform(t); n_inst += 1
assert n_inst == 4, n_inst
g = GROUP.to_itype(ly.dbu)
n_shapes = 0
for li in ly.layer_indexes():
    for s in list(top.shapes(li).each()):
        if s.bbox().inside(g):
            s.transform(t); n_shapes += 1

# ---------------------------------------------------------------- the control lines
for pin, bbox in (((0, 78.79, 2, 79.01), (0, 78.79, 339.43, 104.015)),     # dig_in[1] -> en
                  ((0, 79.23, 2, 79.45), (0, 79.23, 339.43, 112.015)),     # dig_in[2] -> reset
                  ((0, 79.67, 2, 79.89), (0, 79.67, 107.115, 102.015))):   # dig_in[3] -> the bridge
    take(M3, bbox)
    top.shapes(M3).insert(kdb.DBox(*pin))                                  # the frame pin stays
take(M3, (114.3, 101.815, 339.43, 102.015))       # the bridge -> mode
take(M2, (107.115, 101.665, 114.3, 102.165))      # the bridge itself

os.makedirs(os.path.dirname(OUT), exist_ok=True)
ly.write(OUT)
print("geschrieben: %s (4 Bloecke und %d Formen um %.2f um nach oben)" % (OUT, n_shapes, DY))
