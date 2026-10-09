#!/usr/bin/env python3
"""Step 5 of the top-level layout: the LVDS back-termination (macros/lvds_bt), placed and wired.

~200 ohm across the output pair, switched by dig_in[4].  The block sits below
lvds_tx, between the termination of ref_clk and pad 1, at (450, 96); its pins
and where they go:

  OUTP  metal3 on top (x 464..474) -> 2 um metal3 east at y 124..126 to x 533,
        up onto the bottom of Out_p's line to pad 1 (x 529.7..533)
  OUTN  metal3 on top (x 451..461) -> up to y 142, 2 um metal3 east to x 523.5,
        metal4 up at x 522..523.5 over Out_p's line to the bottom of Out_n's
        (y 210.4) - via3 arrays at both ends
  VSS   metal4 on the left (y 96..98.5) <- metal4 west to x 352, TopVia1 from
        the vss_3v3 strap (vss33_v, x 351.5..358.5)
  VDDH  metal4 on the left (y 112.6..113.4) <- metal4 west to x 364, TopVia1
        from the vdd_3v3 strap (vdd33_v, x 363.5..370.5)
  VDD   metal4 on the right (y 114.7..115.3) <- metal4 down at x 515.4..516 to
        y 30.7 and west onto the termination's VDD line (x 503..506)
  EN    metal4 at the bottom (x 508.3) <- dig_in[4]: off the frame pin 0.2 um
        wide, onto a 0.6 um metal3 track at y 82.8 (the one above mode's,
        route_top.py), up to metal4 at x 6 and east along y 82.8

    python3 scripts/top/add_bt.py --in <gds> --out <gds>
"""
import math, os, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "build/top/4_odt.gds")
OUT = arg("--out", "build/top/5_bt.gds")
MACRO = "macros/lvds_bt/layout/lvds_bt.gds"
BX, BY = 450.0, 96.0

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell("slot_14")
assert ly.cell("lvds_bt") is None, "lvds_bt is already placed"
assert ly.cell("ref_odt_lvlup") is not None, "run add_odt.py first"
M2, V2, M3, V3, M4, TV1 = (ly.layer(l, 0) for l in (10, 29, 30, 49, 50, 125))
D = lambda v: int(round(v / ly.dbu))


def box(li, x0, y0, x1, y1):
    top.shapes(li).insert(kdb.DBox(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))


def array(li, x0, y0, x1, y1, a=0.19, space=0.29, inset=0.06):
    pitch = a + space
    nx = int(math.floor((x1 - x0 - 2 * inset - a) / pitch + 1e-9)) + 1
    ny = int(math.floor((y1 - y0 - 2 * inset - a) / pitch + 1e-9)) + 1
    g = lambda v: round(v / 0.005) * 0.005                      # the 5 nm manufacturing grid
    sx = g(x0 + (x1 - x0 - (nx - 1) * pitch - a) / 2)
    sy = g(y0 + (y1 - y0 - (ny - 1) * pitch - a) / 2)
    for i in range(nx):
        for j in range(ny):
            box(li, sx + i * pitch, sy + j * pitch, sx + i * pitch + a, sy + j * pitch + a)


# ---------------------------------------------------------------- the block
m = kdb.Layout(); m.read(MACRO)
# its level shifter is ref_odt's cell, already here: the same shapes, so it is shared
mine, theirs = m.cell("ref_odt_lvlup"), ly.cell("ref_odt_lvlup")
for li in m.layer_indexes():
    lj = ly.find_layer(m.get_info(li))
    a = kdb.Region(mine.begin_shapes_rec(li))
    b = kdb.Region(theirs.begin_shapes_rec(lj)) if lj is not None else kdb.Region()
    assert (a ^ b).is_empty(), ("ref_odt_lvlup differs on", m.get_info(li))
cell = ly.create_cell("lvds_bt")
src = m.cell("lvds_bt")
for li in m.layer_indexes():
    cell.shapes(ly.layer(m.get_info(li))).insert(src.shapes(li))
for inst in src.each_inst():
    assert inst.cell.name == "ref_odt_lvlup", inst.cell.name
    cell.insert(kdb.CellInstArray(theirs.cell_index(), inst.cplx_trans))
top.insert(kdb.CellInstArray(cell.cell_index(), kdb.Trans(kdb.Point(D(BX), D(BY)))))
for li in m.layer_indexes():
    a = kdb.Region(cell.begin_shapes_rec(ly.layer(m.get_info(li))))
    assert (a ^ kdb.Region(src.begin_shapes_rec(li))).is_empty(), m.get_info(li)

# ---------------------------------------------------------------- OUTP -> Out_p (pad 1)
box(M3, BX + 14.0, BY + 26.9, BX + 24.0, BY + 30.0)             # up from the pin
box(M3, BX + 14.0, BY + 28.0, 533.0, BY + 30.0)                 # east, 2 um, y 124..126
box(M3, 529.73, BY + 28.0, 533.0, 136.6)                        # onto Out_p's line (from y 136.5)

# ---------------------------------------------------------------- OUTN -> Out_n (pad 0)
box(M3, BX + 1.0, BY + 26.9, BX + 11.0, 142.0)                  # up from the pin
box(M3, BX + 1.0, 140.0, 523.5, 142.0)                          # east, 2 um
box(M4, 522.0, 140.0, 523.5, 213.66)                            # up over Out_p's line
array(V3, 522.0, 140.0, 523.5, 142.0)
array(V3, 522.0, 210.395, 523.5, 213.66)                        # into Out_n's line (x 521.73..525)

# ---------------------------------------------------------------- VSS <- vss_3v3, VDDH <- vdd_3v3
box(M4, 352.0, BY, BX + 1.0, BY + 2.5)
array(TV1, 352.0, BY, 358.0, BY + 2.5, 0.42, 0.42, 0.1)         # under vss33_v (x 351.5..358.5)
box(M4, 364.0, BY + 15.5, 370.0, BY + 18.5)
box(M4, 364.0, BY + 16.6, BX + 1.0, BY + 17.4)
array(TV1, 364.0, BY + 15.5, 370.0, BY + 18.5, 0.42, 0.42, 0.1)  # under vdd33_v (x 363.5..370.5)

# ---------------------------------------------------------------- VDD <- the termination's VDD line
box(M4, 505.0, 30.7, 516.0, 31.3)
box(M4, 515.4, 30.7, 516.0, BY + 19.3)
box(M4, BX + 63.0, BY + 18.7, 516.0, BY + 19.3)

# ---------------------------------------------------------------- EN <- dig_in[4]
Y4 = 82.8                                                       # its track, above mode's (81.4)
EN_X = BX + 58.275
box(M3, 1.9, 80.12, 2.9, 80.32)                                 # off the frame pin, 0.2 um
box(M3, 2.6, 80.12, 3.2, Y4 + 0.3)                              # up onto the track
box(M3, 2.6, Y4 - 0.3, 6.5, Y4 + 0.3)
box(M3, 5.5, Y4 - 0.4, 6.5, Y4 + 0.4)
array(V3, 5.5, Y4 - 0.4, 6.5, Y4 + 0.4)
box(M4, 5.5, Y4 - 0.4, 6.5, Y4 + 0.4)
box(M4, 5.5, Y4 - 0.3, EN_X + 0.3, Y4 + 0.3)                    # east on metal4, over the climbs
box(M4, EN_X - 0.3, Y4 - 0.3, EN_X + 0.3, BY + 1.0)             # up into the pin

os.makedirs(os.path.dirname(OUT), exist_ok=True)
ly.write(OUT)
print("geschrieben:", OUT)
