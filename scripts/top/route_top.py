#!/usr/bin/env python3
"""Step 2 of the top-level layout: control lines, supplies, bias, decoupling (2026-10-07).

Runs on the output of floorplan_shift.py, where the LVDS group sits DY higher
than in the hand-drawn floor plan.  The blocks' supply and bias lines end in
metal3 stubs at x = 340; this adds:

* lvds_pattern from the macro again, with its three antenna diodes (en, mode,
  ref_clk: macros/lvds_pattern/scripts/add_*_diode*.py);
* the control lines dig_in[1..3] -> en, reset, mode on 0.6 um metal3, fanned
  out from the 0.44 um pin pitch of the frame; mode crosses the other two on a
  metal4 bridge; 2 x 2 via2 onto each pin of lvds_pattern; the dangling line of
  dig_in[0] (it went to clk_src) goes;
* reset: an antenna diode (dantenna, DRST in the schematic) under the line;
* ibias0, ibias1 and vbias (Vref) on 1 um metal4, over the metal3 control lines:
  from the frame pin a metal3 tail and a via3 array, along metal4 to x 336 /
  334 / 332, up, and a via3 array onto the stub of xiref_pd.IREF_IN,
  xiref_drv.IREF_IN and xlvds.Vref - vbias first up the frame edge on metal2 to
  y 115, so all three climb, the lowest pin and stub in the rightmost column;
* taps: analog_bus0 / 2 / 1 to ibias0 / ibias1 / Vref through 1.1 kohm each, to
  measure the bias nodes or force them from outside;
* the four supplies on TopMetal1, crossing-free - left edge, bottom to top
  vdd_1v2, vss_1v2, vss_3v3, vdd_3v3, and at the stubs vdd_1v2 lowest and
  vss_1v2 highest of the 1.2 V pair, vss_3v3 left of vdd_3v3 - each landing
  through TopVia1 onto a metal4 riser that climbs to its stub (via3):

      vdd_1v2   y 44..52.2 to x 347, up at x 339.6..347 to y 96, riser x 341.6..344 to xpat.VDD
      vss_1v2   y 66.5..74.5 to x 308, up, y 114..120, riser x 344.6..346.6 to xpat.VSS
      vss_3v3   y 124..132.2 to x 358.5, riser x 352..358 to the Vss stub of xlvds and the mirrors
      vdd_3v3   y 138/150.5..158.5 to x 370.5, riser x 364..370 to their Va stub

* decoupling as standard-cell rows laid under the edges of those straps, so
  each rail is reached by a via stack (via1..TopVia1, two cuts per level) every ~20 um:
  N_LV sg13cmos5l_decap_8 between vdd_1v2 and a vss_1v2 branch (y 51.5..55.28),
  N_HV sg13g2_hv_decap_8 between vss_3v3 and vdd_3v3 (y 131.5..138.64).

    python3 scripts/top/route_top.py --in <gds> --out <gds>

N_LV and N_HV have to match the decap arrays in scripts/gen_top.py.  The
whole chain: scripts/top/build_layout.sh.
"""
import math, os, sys
import klayout.db as kdb

N_LV, N_HV = 83, 95
DY = 92.25                 # the LVDS group's shift - the same as in floorplan_shift.py

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "build/top/1_shift.gds")
OUT = arg("--out", "build/top/2_route.gds")
MACRO = "macros/lvds_pattern/layout/lvds_pattern.gds"
LIB = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.ref")

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell("slot_14")
M1, V1, M2, V2, M3, V3, M4, TV1, TM1 = (ly.layer(l, 0) for l in (8, 19, 10, 29, 30, 49, 50, 125, 126))
D = lambda v: int(round(v / ly.dbu))
assert kdb.Region(top.shapes(TM1)).bbox().right <= D(2.0) + 1, "TopMetal1 beyond the frame - already routed?"
pat = [i for i in top.each_inst() if i.cell.name == "lvds_pattern"]
assert len(pat) == 1 and abs(pat[0].dcplx_trans.disp.y - (97.215 + DY)) < 1e-3, "run floorplan_shift.py first"


def box(li, x0, y0, x1, y1):
    top.shapes(li).insert(kdb.DBox(x0, y0, x1, y1))


def via(li, x, y, a=0.19):
    box(li, x - a / 2, y - a / 2, x + a / 2, y + a / 2)


def array(li, x0, y0, x1, y1, a, space, inset):
    """as many a x a cuts as fit into the box minus inset, centred"""
    pitch = a + space
    nx = int(math.floor((x1 - x0 - 2 * inset - a) / pitch + 1e-9)) + 1
    ny = int(math.floor((y1 - y0 - 2 * inset - a) / pitch + 1e-9)) + 1
    assert nx > 0 and ny > 0, (x0, y0, x1, y1)
    sx = x0 + (x1 - x0 - (nx - 1) * pitch - a) / 2
    sy = y0 + (y1 - y0 - (ny - 1) * pitch - a) / 2
    for i in range(nx):
        for j in range(ny):
            box(li, sx + i * pitch, sy + j * pitch, sx + i * pitch + a, sy + j * pitch + a)
    return (sx, sy, sx + (nx - 1) * pitch + a, sy + (ny - 1) * pitch + a)


def land(x0, y0, x1, y1):
    """TopMetal1 onto a metal3 stub: metal4 pad on the stub, via3 and TopVia1 arrays.
    Returns the TopVia1 extent; the TopMetal1 has to cover it by 0.42."""
    box(M4, x0, y0, x1, y1)
    array(V3, x0, y0, x1, y1, 0.19, 0.29, 0.06)          # V3.b1: 0.29 in arrays over 3 x 3
    return array(TV1, x0, y0, x1, y1, 0.42, 0.42, 0.1)


def covered(tv, tm):
    """the TopVia1 extent tv lies inside the TopMetal1 box tm with 0.42 to spare"""
    return tm[0] <= tv[0] - 0.42 + 1e-6 and tm[1] <= tv[1] - 0.42 + 1e-6 and \
        tm[2] >= tv[2] + 0.42 - 1e-6 and tm[3] >= tv[3] + 0.42 - 1e-6


def rail_stack(x, y):
    """via1 .. TopVia1 straight up from a standard-cell rail at (x, y), two of each side by side"""
    for li in (V1, V2, V3):
        via(li, x - 0.205, y); via(li, x + 0.205, y)
    for li in (M2, M3, M4):
        box(li, x - 0.73, y - 0.31, x + 0.73, y + 0.31)
    via(TV1, x - 0.42, y, 0.42); via(TV1, x + 0.42, y, 0.42)


# ---------------------------------------------------------------- lvds_pattern
m = kdb.Layout(); m.read(MACRO)
src, dst = m.cell("lvds_pattern"), ly.cell("lvds_pattern")
assert m.cell("sg13cmos5l_antennanp") is not None, "run add_antenna_diodes.py on the macro first"
for name in ("sg13cmos5l_antennanp",):
    if ly.cell(name) is None:
        c = ly.create_cell(name)
        for li in m.layer_indexes():
            c.shapes(ly.layer(m.get_info(li))).insert(m.cell(name).shapes(li))
dst.clear()
for li in m.layer_indexes():
    dst.shapes(ly.layer(m.get_info(li))).insert(src.shapes(li))
for inst in src.each_inst():
    dst.insert(kdb.CellInstArray(ly.cell(inst.cell.name).cell_index(), inst.cplx_trans))
for li in m.layer_indexes():
    a = kdb.Region(dst.begin_shapes_rec(ly.layer(m.get_info(li))))
    assert (a ^ kdb.Region(src.begin_shapes_rec(li))).is_empty(), m.get_info(li)

# ---------------------------------------------------------------- dig_in[0]: the dangling line
# it went to clk_src; add_odt.py routes dig_in[0] to the termination's EN
pin0 = kdb.DBox(0, 78.35, 2, 78.57)                      # dig_in[0], the frame pin itself
hit = [s for s in top.shapes(M3).each() if not s.is_text()
       and s.dbbox() == kdb.DBox(0, 78.35, 117.11, 98.675)]
assert len(hit) == 1, len(hit)
top.shapes(M3).erase(hit[0]); box(M3, *[pin0.left, pin0.bottom, pin0.right, pin0.top])
for s in list(top.shapes(M2).each()):
    if s.dbbox() == kdb.DBox(116.76, 98.675, 117.26, 107.915):
        top.shapes(M2).erase(s)

# ---------------------------------------------------------------- control lines, 0.6 um metal3
# dig_in[1..3] -> en, reset, mode of lvds_pattern.  The frame pins sit at a 0.44 um
# pitch, so each line leaves its pin 0.2 um wide and fans out within 4 um onto its
# own 0.6 um track (pitch 1.4; dig_in[0] takes the one below - add_odt.py - and
# dig_in[4] the one above mode's - add_bt.py).  Up at
# x 104.5 / 109 / 112.3, east to the pins; mode crosses over the other two on a
# metal4 bridge.  Every change of layer and every pin gets a via array.
W = 0.6
Y_PIN = {"en": 78.90, "reset": 79.34, "mode": 79.78}           # the frame pins dig_in[1..3]
Y_TRK = {"en": 78.60, "reset": 80.00, "mode": 81.40}           # their tracks after the fan-out
# where they leave the pin's height; the outermost go first: dig_in[0] (down, add_odt.py) and
# dig_in[4] (up, add_bt.py) at x 2.9, mode at 4.1, en and reset at 5.3
X_JOG = {"en": 5.3, "reset": 5.3, "mode": 4.1}
X_UP = {"en": 112.255, "reset": 108.955, "mode": 104.515}      # the climb
Y_END = {"en": 103.915 + DY, "reset": 111.915 + DY, "mode": 101.915 + DY}  # lvds_pattern's pins
X_PIN = (338.78, 339.78)                                        # the pins: metal2, 1 x 1 um


def path(li, pts, w):
    """square-cornered path: each leg widened to w, extended by w/2 at inner corners only"""
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        e0 = w / 2 if i > 0 else 0.0
        e1 = w / 2 if i < len(pts) - 2 else 0.0
        if y0 == y1:
            box(li, min(x0, x1) - (e0 if x0 < x1 else e1), y0 - w / 2,
                max(x0, x1) + (e1 if x0 < x1 else e0), y0 + w / 2)
        else:
            assert x0 == x1, (pts[i], pts[i + 1])
            box(li, x0 - w / 2, min(y0, y1) - (e0 if y0 < y1 else e1),
                x0 + w / 2, max(y0, y1) + (e1 if y0 < y1 else e0))


def pin_vias(y):
    """metal3 pad and a 2 x 2 via2 array onto one of lvds_pattern's metal2 pins"""
    old = [s for s in top.shapes(V2).each() if s.dbbox().center() == kdb.DPoint(339.28, y)]
    assert len(old) == 1, (y, len(old))                         # the single via of the floor plan
    top.shapes(V2).erase(old[0])
    box(M3, X_PIN[0], y - 0.5, X_PIN[1], y + 0.5)
    array(V2, X_PIN[0], y - 0.5, X_PIN[1], y + 0.5, 0.19, 0.29, 0.06)


for net in ("en", "reset", "mode"):
    y0, yt, xj, xu, ye = Y_PIN[net], Y_TRK[net], X_JOG[net], X_UP[net], Y_END[net]
    box(M3, 1.9, y0 - 0.1, xj, y0 + 0.1)                       # off the pin, 0.2 um
    edge = y0 + 0.1 if yt < y0 else y0 - 0.1                    # the jog starts flush with it
    if net == "mode":                                           # up, east to the bridge
        path(M3, [(xj, edge), (xj, yt), (xu, yt), (xu, ye), (108.2, ye)], W)
    else:
        path(M3, [(xj, edge), (xj, yt), (xu, yt), (xu, ye), (X_PIN[1], ye)], W)
    pin_vias(ye)
# the mode bridge: over the reset and en climbs (x 108.7..109.3, 112.0..112.6)
YM = Y_END["mode"]
for x0, x1 in ((106.6, 108.2), (112.8, 114.4)):
    box(M3, x0, YM - 0.4, x1, YM + 0.4)
    array(V3, x0, YM - 0.4, x1, YM + 0.4, 0.19, 0.29, 0.06)
box(M4, 106.6, YM - 0.4, 114.4, YM + 0.4)
path(M3, [(112.8, YM), (X_PIN[1], YM)], W)

# ---------------------------------------------------------------- reset: an antenna diode
# reset is ~470 um of metal3 to a small gate, and unlike en, mode and ref_clk it
# has no antenna diode inside lvds_pattern: a dantenna 0.78 x 0.78 (the PDK
# PCell, flattened) right under the line 9 um before the pin, stacked up to it
# with 2 x 2 arrays.  The schematic carries it as DRST (scripts/gen_top.py).
K = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.tech/klayout")
sys.path += [os.path.join(K, "python"), os.path.join(K, "python/pycell4klayout-api/source/python")]
import sg13cmos5l_pycell_lib  # noqa: E402,F401  registers SG13_dev
PCL = kdb.Library.library_by_name("SG13_dev", "sg13cmos5l")
pl = kdb.Layout(); pl.dbu = ly.dbu; pl.technology_name = "sg13cmos5l"
dio = pl.cell(pl.add_pcell_variant(PCL, PCL.layout().pcell_id("dantenna"), {"w": "0.78u", "l": "0.78u"}))
XD, YD = 330.0, Y_END["reset"]                                  # the diode's centre
t = kdb.Trans(D(XD - 0.39), D(YD - 0.39))
for li in pl.layer_indexes():
    r = kdb.Region(dio.begin_shapes_rec(li))
    if not r.is_empty():
        info = pl.get_info(li)
        top.shapes(ly.layer(info.layer, info.datatype)).insert(r.transformed(t))
for m in (M1, M2, M3):
    box(m, XD - 0.4, YD - 0.4, XD + 0.4, YD + 0.4)
for v in (V1, V2):
    array(v, XD - 0.4, YD - 0.4, XD + 0.4, YD + 0.4, 0.19, 0.29, 0.06)

# ---------------------------------------------------------------- bias on metal4, 1 um
for y_pin, x_down, y_stub in ((98.155, 336.0, 61.5 + DY),     # ibias0 -> xiref_pd.IREF_IN
                              (101.095, 334.0, 64.0 + DY)):   # ibias1 -> xiref_drv.IREF_IN
    box(M3, 1.9, y_pin - 1.0, 5.2, y_pin + 1.0)                 # the frame pin is 2 um high
    box(M4, 3.0, y_pin - 1.0, 5.2, y_pin + 1.0)
    array(V3, 3.0, y_pin - 1.0, 5.2, y_pin + 1.0, 0.19, 0.29, 0.06)
    path(M4, [(3.0, y_pin), (x_down, y_pin), (x_down, y_stub), (341.0, y_stub)], 1.0)
    array(V3, 340.0, y_stub - 0.5, 341.0, y_stub + 0.5, 0.19, 0.29, 0.06)   # onto the 1 um metal3 stub

# Vref from vbias, the harness's voltage reference at 1.2 V.  Its frame pin is the
# lowest of the bias pins and Vref's stub the highest, so it climbs at the frame
# first - metal2 at x 6.5..7.5, under the other bias lines, up to y 115 above all
# of them - and then runs like them: east on metal4, up at x 332, onto the stub.
Y_VB, Y_VR, Y_VS = 95.215, 115.0, 92.5 + DY
box(M3, 1.9, Y_VB - 1.0, 7.5, Y_VB + 1.0)
array(V2, 6.5, Y_VB - 1.0, 7.5, Y_VB + 1.0, 0.19, 0.29, 0.06)
box(M2, 6.5, Y_VB - 1.0, 7.5, Y_VR + 0.5)
box(M3, 6.5, Y_VR - 0.5, 7.5, Y_VR + 0.5)
array(V2, 6.5, Y_VR - 0.5, 7.5, Y_VR + 0.5, 0.19, 0.29, 0.06)
array(V3, 6.5, Y_VR - 0.5, 7.5, Y_VR + 0.5, 0.19, 0.29, 0.06)
path(M4, [(6.5, Y_VR), (332.0, Y_VR), (332.0, Y_VS), (341.0, Y_VS)], 1.0)
array(V3, 340.0, Y_VS - 0.5, 341.0, Y_VS + 0.5, 0.19, 0.29, 0.06)

# ---------------------------------------------------------------- taps for measuring
# analog_bus0 -> ibias0, analog_bus2 -> ibias1, analog_bus1 -> Vref, each through
# 1.1 kohm of rppd (w 1 um, l 4 um) right at the frame edge: through the harness's
# analog bus switches the node can be measured, or forced from outside if the IDAC
# or the voltage reference do not work.  2 uA drop 2 mV; the resistor keeps the bus
# capacitance and what is coupled onto the bus off the bias nodes.  The schematic
# carries them as RT0..RT2.


def flat_pcell(name, x, y, **p):
    """a PDK PCell, flattened into the top cell at (x, y); returns its metal1 boxes, bottom first"""
    c = pl.cell(pl.add_pcell_variant(PCL, PCL.layout().pcell_id(name), {k: str(v) for k, v in p.items()}))
    t = kdb.Trans(D(x), D(y))
    m1 = []
    for li in pl.layer_indexes():
        r = kdb.Region(c.begin_shapes_rec(li))
        if r.is_empty():
            continue
        info = pl.get_info(li)
        top.shapes(ly.layer(info.layer, info.datatype)).insert(r.transformed(t))
        if (info.layer, info.datatype) == (8, 0):
            m1 = sorted([q.bbox().to_dtype(ly.dbu).moved(kdb.DVector(x, y)) for q in r.merged().each()],
                        key=lambda b: b.bottom)
    assert len(m1) == 2, (name, m1)
    return m1


def term_stack(b, upto):
    """via1 .. up to metal2 / metal3 / metal4 on the centre of a resistor terminal"""
    cx, cy = b.center().x, b.center().y
    via(V1, cx, cy)
    box(M2, cx - 0.19, cy - 0.19, cx + 0.19, cy + 0.19)
    if upto >= 3:
        via(V2, cx, cy)
        box(M3, cx - 0.19, cy - 0.19, cx + 0.19, cy + 0.19)
    if upto >= 4:
        via(V3, cx, cy)
        box(M4, cx - 0.19, cy - 0.19, cx + 0.19, cy + 0.19)
    return cx, cy


TAP = dict(w="1u", l="4u", R="1110")
for pin_y, x_tail in ((109.915, 11.0), (112.855, 14.0), (106.975, 17.0)):   # analog_bus1, 0, 2
    box(M3, 1.9, pin_y - 1.0, x_tail, pin_y + 1.0)                          # the bus pin's tail
# RT1: analog_bus1 (bottom) -> Vref (top, metal4 at y 115)
bot, tp = flat_pcell("rppd", 10.0, 110.6, **TAP)
term_stack(bot, 3)
term_stack(tp, 4)
# RT0: ibias0 (bottom, metal4 at y 98.2) -> analog_bus0 (top, metal2 up to its tail at y 112.9)
bot, tp = flat_pcell("rppd", 13.0, 99.2, **TAP)
cx, cy = term_stack(bot, 4)
box(M4, cx - 0.5, 97.655, cx + 0.5, cy + 0.19)
cx, cy = term_stack(tp, 2)
box(M2, cx - 0.25, cy - 0.19, cx + 0.25, 113.1)
via(V2, cx, 112.855)
box(M2, cx - 0.19, 112.855 - 0.19, cx + 0.19, 113.1)
# RT2: ibias1 (bottom, metal4 at y 101.1) -> analog_bus2 (top, its tail at y 107)
bot, tp = flat_pcell("rppd", 16.0, 101.75, **TAP)
cx, cy = term_stack(bot, 4)
box(M4, cx - 0.5, 100.595, cx + 0.5, cy + 0.19)
cx, cy = term_stack(tp, 3)
box(M3, cx - 0.5, cy - 0.3, cx + 0.5, 106.975)

# ---------------------------------------------------------------- supplies on TopMetal1
TM = {
    "vdd12_h": (1.0, 44.0, 347.12, 52.2),
    "vdd12_v": (339.6, 44.0, 347.12, 96.81),
    "vss12_a": (1.0, 66.5, 308.0, 74.5),
    "vss12_b": (290.0, 54.46, 298.0, 74.5),
    "vss12_lv": (5.0, 54.46, 298.0, 56.1),
    "vss12_c": (300.0, 66.5, 308.0, 120.0),
    "vss12_d": (300.0, 114.0, 347.12, 120.0),
    "vss12_land": (339.6, 112.745, 347.12, 120.0),
    "vss33_h": (1.0, 124.0, 358.5, 132.2),
    "vss33_v": (351.5, 74.6, 358.5, 132.2),
    "vdd33_h": (1.0, 150.5, 370.5, 158.5),
    "vdd33_hv": (5.0, 138.0, 370.5, 150.5),
    "vdd33_v": (363.5, 77.88, 370.5, 158.5),
}
for b in TM.values():
    box(TM1, *b)
# Each supply leaves its TopMetal1 through TopVia1 onto a metal4 riser and lands
# on its stub with via3: (riser x0, x1), TopVia1 window (y0, y1), stub (y0, y1)
RISERS = (
    ("vdd12_v",    (341.6, 344.0), (94.7, 96.3),   (94.385 + DY, 96.385 + DY)),    # xpat.VDD
    ("vss12_land", (344.6, 346.6), (113.3, 119.6), (113.165 + DY, 115.165 + DY)),  # xpat.VSS
    ("vss33_v",    (352.0, 358.0), (126.0, 131.7), (75.0 + DY, 78.0 + DY)),        # Vss of xlvds and the mirrors
    ("vdd33_v",    (364.0, 370.0), (152.0, 158.0), (78.3 + DY, 81.3 + DY)),        # their Va
)
for tm, (x0, x1), (t0, t1), (s0, s1) in RISERS:
    box(M4, x0, t0, x1, s1)
    tv = array(TV1, x0, t0, x1, t1, 0.42, 0.42, 0.1)
    assert covered(tv, TM[tm]), (tm, tv)
    array(V3, x0, s0, x1, s1, 0.19, 0.29, 0.06)

# ---------------------------------------------------------------- decoupling rows
hv = kdb.Layout(); hv.read(os.path.join(LIB, "sg13cmos5l_stdcell_hv/gds/sg13cmos5l_stdcell_hv.gds"))
if ly.cell("sg13g2_hv_decap_8") is None:
    c = ly.create_cell("sg13g2_hv_decap_8")
    for li in hv.layer_indexes():
        c.shapes(ly.layer(hv.get_info(li))).insert(hv.cell("sg13g2_hv_decap_8").shapes(li))
LV, HV = ly.cell("sg13cmos5l_decap_8"), ly.cell("sg13g2_hv_decap_8")
X0, W = 10.0, 3.36
# 1.2 V: mirrored, so VDD (cell y 3.78) is at the bottom, on the edge of vdd12_h
Y_VSS_LV, Y_VDD_LV = 55.28, 55.28 - 3.78
for i in range(N_LV):
    top.insert(kdb.CellInstArray(LV.cell_index(), kdb.Trans(kdb.Trans.M0, D(X0 + i * W), D(Y_VSS_LV))))
# 3.3 V: upright, VSS at the bottom on the edge of vss33_h, VDD (cell y 7.14) under vdd33_hv
Y_VSS_HV, Y_VDD_HV = 131.5, 131.5 + 7.14
for i in range(N_HV):
    top.insert(kdb.CellInstArray(HV.cell_index(), kdb.Trans(kdb.Trans.R0, D(X0 + i * W), D(Y_VSS_HV))))
# The HV cells carry DigiBnd (16/0), which ends on the middle of each rail, while
# the rail contacts reach 0.08 past it: Cnt.c.Digi (0.05 Activ enclosure inside
# DigiBnd) sees the clipped tap.  In a block the mirrored neighbour row covers
# the other half; this row has none, so DigiBnd is drawn 0.2 past both rails.
DIGIBND = ly.layer(16, 0)
box(DIGIBND, X0, Y_VSS_HV - 0.2, X0 + N_HV * W, Y_VSS_HV)
box(DIGIBND, X0, Y_VDD_HV, X0 + N_HV * W, Y_VDD_HV + 0.2)
for n, y_lo, y_hi in ((N_LV, Y_VDD_LV, Y_VSS_LV), (N_HV, Y_VSS_HV, Y_VDD_HV)):
    x_end = X0 + n * W
    for x in [X0 + 1.68 + k * 20.16 for k in range(int((x_end - X0 - 1.68) / 20.16) + 1)]:
        # not under the three control lines, which climb at x 104.5 .. 112.3 through the HV row
        if x < x_end - 1.0 and not (n == N_HV and 100.0 < x < 118.0):
            rail_stack(x, y_lo); rail_stack(x, y_hi)

# ---------------------------------------------------------------- write
os.makedirs(os.path.dirname(OUT), exist_ok=True)
ly.write(OUT)
print("geschrieben:", OUT)
