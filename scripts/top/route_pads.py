#!/usr/bin/env python3
"""Step 3 of the top-level layout: the lines to the three analog pads (2026-10-07).

    pad 0  s14_an[0]     Out_n (LVDS -)
    pad 1  s14_an[1]     Out_p (LVDS +)
    pad 2  s14_an_2_esd  ref_clk;  s14_an[2] gets the termination (add_odt.py)

lvds_tx sits between pads 0 and 1 (floorplan_shift.py): Out_n leaves it above
Out_p and climbs on the inside (x 521.7..525) to pad 0, Out_p drops on the
outside (x 529.7..533) to pad 1 - no crossing, 3.27 um of metal3 as drawn
before, ~60 and ~80 um long.

ref_clk: from s14_an_2_esd a metal3 tail to x 517, 1 um of metal4 up the right
side to y 225, west above the LVDS group, down at x 337.5 and onto
lvds_pattern's ref_clk pin (metal2, 1 x 1 um) - 2 x 2 arrays of via3 and via2
at both ends.

    python3 scripts/top/route_pads.py --in <gds> --out <gds>
"""
import math, os, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "build/top/2_route.gds")
OUT = arg("--out", "build/top/3_pads.gds")
DY = 92.25                 # the LVDS group's shift - the same as in floorplan_shift.py

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell("slot_14")
V2, V3, M3, M4 = (ly.layer(l, 0) for l in (29, 49, 30, 50))
tx = [i for i in top.each_inst() if i.cell.name == "lvds_tx"]
assert len(tx) == 1 and abs(tx[0].dcplx_trans.disp.y - (80.875 + DY)) < 1e-3, "run floorplan_shift.py first"


def box(li, x0, y0, x1, y1):
    top.shapes(li).insert(kdb.DBox(x0, y0, x1, y1))


def array(li, x0, y0, x1, y1, a=0.19, space=0.29, inset=0.06):
    """as many a x a cuts as fit into the box minus inset, centred"""
    pitch = a + space
    nx = int(math.floor((x1 - x0 - 2 * inset - a) / pitch + 1e-9)) + 1
    ny = int(math.floor((y1 - y0 - 2 * inset - a) / pitch + 1e-9)) + 1
    sx = x0 + (x1 - x0 - (nx - 1) * pitch - a) / 2
    sy = y0 + (y1 - y0 - (ny - 1) * pitch - a) / 2
    for i in range(nx):
        for j in range(ny):
            box(li, sx + i * pitch, sy + j * pitch, sx + i * pitch + a, sy + j * pitch + a)


def take(li, bbox):
    hit = [s for s in top.shapes(li).each() if not s.is_text() and s.dbbox() == kdb.DBox(*bbox)]
    assert len(hit) == 1, (ly.get_info(li), bbox, len(hit))
    top.shapes(li).erase(hit[0])


# ---------------------------------------------------------------- LVDS: Out_n -> pad 0, Out_p -> pad 1
N0, N1 = 118.145 + DY, 121.41 + DY        # Out_n leaves lvds_tx here (x 514.2)
P0, P1 = 99.19 + DY, 102.455 + DY         # Out_p
for b in ((514.2, N0, 525.0, N1), (521.73, N0, 525.0, 250.0), (521.73, 246.73, 535.6, 250.0)):
    box(M3, *b)
for b in ((514.2, P0, 533.0, P1), (529.73, 136.5, 533.0, P1), (529.73, 136.5, 535.6, 139.77)):
    box(M3, *b)

# ---------------------------------------------------------------- ref_clk from s14_an_2_esd
RC = 109.915 + DY                         # lvds_pattern's ref_clk pin: metal2, x 338.78..339.78
# the floor plan's single-via stub on it goes
take(M3, (339.13, RC - 0.25, 339.43, RC + 0.25))
take(V3, (339.185, RC - 0.095, 339.375, RC + 0.095))
take(V2, (339.185, RC - 0.095, 339.375, RC + 0.095))
box(M3, 516.6, 17.95, 535.6, 18.95)       # the tail: the pin itself is 0.5 um high (y 18.2..18.7)
array(V3, 516.6, 17.95, 517.6, 18.95)
box(M4, 516.6, 17.95, 517.6, 225.5)
box(M4, 337.0, 224.5, 517.6, 225.5)
box(M4, 337.0, RC - 0.5, 338.0, 225.5)
box(M4, 337.0, RC - 0.5, 339.78, RC + 0.5)
box(M3, 338.78, RC - 0.5, 339.78, RC + 0.5)
array(V3, 338.78, RC - 0.5, 339.78, RC + 0.5)
array(V2, 338.78, RC - 0.5, 339.78, RC + 0.5)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
ly.write(OUT)
print("geschrieben:", OUT)
