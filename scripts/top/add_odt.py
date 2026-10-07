#!/usr/bin/env python3
"""Place the ref_clk termination (macros/ref_odt) in the top layout and wire it (2026-10-07).

Step 4 of the top-level layout, after route_pads.py: ref_clk is on pad 2
(s14_an_2_esd), and the termination goes on pad 2 itself (s14_an[2]).  The
block sits in the free corner below the LVDS group, beside pad 2, at
(440, 12); its pins and where they go:

  PAD   TopMetal1 pad on top <- s14_an[2] (metal3 at the right edge): a metal3
        tail, via3 + TopVia1 up, TopMetal1 west at y 42.9..48.5 - some 50 um.
        24 mA flow here with the termination on.
  VSS   metal4 along the bottom -> west at y 12..14.5, up at x 352..358 and
        through TopVia1 into the foot of the vss_3v3 strap (y 75..78)
  VDDH  metal4 on the left -> west at y 28.6..29.4, up at x 364..370 and
        through TopVia1 into the foot of the vdd_3v3 strap (y 78.3..81.3)
  VDD   metal4 on the right <- vdd_1v2: TopVia1 off the vdd12 strap at
        x 340..342, y 45, down to y 5, east under the block to x 506, up
  EN    metal3 from below <- dig_in[0]: off the pin 0.2 um wide, onto a 0.6 um
        track at y 77.2 (the one below en's, route_top.py) to x 95, 1 um of
        metal2 down, 0.6 um metal3 east at y 8.2 and up at x 498.3 into the
        block's EN line; 2 x 2 via2 at both ends of the metal2

    python3 scripts/top/add_odt.py --in <gds> --out <gds>
"""
import math, os, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "build/top/3_pads.gds")
OUT = arg("--out", "build/top/4_odt.gds")
MACRO = "macros/ref_odt/layout/ref_odt.gds"
OX, OY = 440.0, 12.0

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell("slot_14")
assert ly.cell("ref_odt") is None, "ref_odt is already placed"
M2, V2, M3, V3, M4, TV1, TM1 = (ly.layer(l, 0) for l in (10, 29, 30, 49, 50, 125, 126))
D = lambda v: int(round(v / ly.dbu))


def box(li, x0, y0, x1, y1):
    top.shapes(li).insert(kdb.DBox(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))


def via(li, x, y, a=0.19):
    box(li, x - a / 2, y - a / 2, x + a / 2, y + a / 2)


def array(li, x0, y0, x1, y1, a, space, inset):
    pitch = a + space
    nx = int(math.floor((x1 - x0 - 2 * inset - a) / pitch + 1e-9)) + 1
    ny = int(math.floor((y1 - y0 - 2 * inset - a) / pitch + 1e-9)) + 1
    sx = x0 + (x1 - x0 - (nx - 1) * pitch - a) / 2
    sy = y0 + (y1 - y0 - (ny - 1) * pitch - a) / 2
    for i in range(nx):
        for j in range(ny):
            box(li, sx + i * pitch, sy + j * pitch, sx + i * pitch + a, sy + j * pitch + a)


# ---------------------------------------------------------------- the block
m = kdb.Layout(); m.read(MACRO)
cell = ly.create_cell("ref_odt")
cell.copy_tree(m.cell("ref_odt"))
assert ly.cell("ref_odt_lvlup") is not None
top.insert(kdb.CellInstArray(cell.cell_index(), kdb.Trans(kdb.Point(D(OX), D(OY)))))
# the block's own prBoundary stays inside it; the top cell's is the frame's

# ---------------------------------------------------------------- VSS -> the vss_3v3 landing
box(M4, 352.0, OY, OX + 1.0, OY + 2.5)
box(M4, 352.0, OY, 358.0, 78.0)
array(TV1, 352.0, 75.0, 358.0, 78.0, 0.42, 0.42, 0.1)    # under vss33_v (TopMetal1, from y 74.6)
# ---------------------------------------------------------------- VDDH -> the vdd_3v3 landing
box(M4, 364.0, OY + 16.6, OX + 1.0, OY + 17.4)
box(M4, 364.0, OY + 16.6, 370.0, 81.3)
array(TV1, 364.0, 78.3, 370.0, 81.3, 0.42, 0.42, 0.1)    # under vdd33_v (TopMetal1, from y 77.88)
# ---------------------------------------------------------------- VDD (1.2 V) <- the vdd12 strap
box(M4, 340.0, 5.0, 342.0, 46.2)
array(TV1, 340.0, 44.8, 342.0, 46.2, 0.42, 0.42, 0.1)   # under vdd12_h / vdd12_v (TopMetal1)
box(M4, 340.0, 5.0, 506.0, 6.0)
box(M4, 505.0, 5.0, 506.0, OY + 19.3)
box(M4, OX + 63.0, OY + 18.7, 506.0, OY + 19.3)
# ---------------------------------------------------------------- EN <- dig_in[0]
EN_X = OX + 58.275                               # the block's EN line: metal3, 0.3 um, from y OY+16.8 up
box(M3, 1.9, 78.36, 2.9, 78.56)                  # off the frame pin, 0.2 um (pin pitch 0.44)
box(M3, 2.6, 76.9, 3.2, 78.56)                   # down onto the track
box(M3, 2.6, 76.9, 95.5, 77.5)                   # y 77.2, 0.6 um
box(M3, 94.5, 76.7, 95.5, 77.7)
array(V2, 94.5, 76.7, 95.5, 77.7, 0.19, 0.29, 0.06)
box(M2, 94.5, 7.7, 95.5, 77.7)
box(M3, 94.5, 7.7, 95.5, 8.7)
array(V2, 94.5, 7.7, 95.5, 8.7, 0.19, 0.29, 0.06)
box(M3, 94.5, 7.9, EN_X + 0.3, 8.5)              # y 8.2, 0.6 um
box(M3, EN_X - 0.3, 7.9, EN_X + 0.3, OY + 16.5)
box(M3, EN_X - 0.15, OY + 16.4, EN_X + 0.15, OY + 16.9)  # joins the block's EN line
# ---------------------------------------------------------------- PAD <- s14_an[2]
box(M3, 528.0, 27.0, 535.6, 48.0)                # tail off the pin (metal3, x 535.05..536.44)
array(V3, 528.0, 27.0, 534.2, 48.0, 0.19, 0.29, 0.06)
box(M4, 528.0, 27.0, 534.2, 48.0)
array(TV1, 528.0, 27.0, 534.2, 48.0, 0.42, 0.42, 0.1)
box(TM1, 527.5, 26.5, 534.7, 48.5)
box(TM1, 470.0, OY + 30.9, 534.7, 48.5)          # onto the block's PAD (TopMetal1, y 42.9..45.4)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
ly.write(OUT)
print("geschrieben:", OUT)
