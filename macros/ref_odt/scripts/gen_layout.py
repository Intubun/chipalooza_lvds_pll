#!/usr/bin/env python3
"""layout/ref_odt.gds - the switchable 50 ohm termination of ref_clk.

Runs inside KLayout (it needs the IHP PCell library):

    klayout -b -r macros/ref_odt/scripts/gen_layout.py

    PAD --- R1 rppd 40 x 6.65 um (45 ohm) --- X --- MSW nmosHV 300/0.45, 30 fingers --- VSS
                                              |-- DN dantenna 20 x 1.26 to the substrate (VSS)
                                              '-- DP dpantenna 20 x 1.26 to VDDH (3.3 V)
    EN --- level shifter (the layout of sg13cmos5l_LevelUp) --- gate of MSW at VDDH
     '---- DEN dantenna 0.78 x 0.78 (antenna)

Floor plan, block coordinates in um (origin bottom left):

    y 28.4..33.4  PAD: R1's top terminal, stacked up to a TopMetal1 pad
    y 22  ..28.65 R1, x 1..41
    y 16.6..17.4  VDDH on metal4, enters on the left, to the diode tap and the shifter
    y 5.2 ..20    MSW in a p+ guard ring, gate bar below it; X on metal3 straps up to R1
    x 33  ..53    DP (y 12) with its n-well tap (y 14.6), DN (y 7)
    x 57  ..60.5  the level shifter: iovdd rail y 0.5, vss y 9, vdd y 19
    y 0   ..2.5   VSS on metal3 and metal4, x 0..56

The level shifter is the IO library's own, copied as the cell ref_odt_lvlup
without its ptap1 marker (Substrate + "sub!"), so its tap is a plain tap like
everyone else's; the schematic carries its eight transistors.
"""
import os, sys
import pya

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "layout", "ref_odt.gds")
PDK = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"])
K = os.path.join(PDK, "libs.tech/klayout")
sys.path.append(os.path.join(K, "python"))
sys.path.append(os.path.join(K, "python/pycell4klayout-api/source/python"))
import sg13cmos5l_pycell_lib  # noqa: E402  registers SG13_dev

ly = pya.Layout(); ly.dbu = 0.001; ly.technology_name = "sg13cmos5l"
LIB = pya.Library.library_by_name("SG13_dev", "sg13cmos5l")
top = ly.create_cell("ref_odt")
L = {n: ly.layer(l, d) for n, (l, d) in {
    "activ": (1, 0), "gatpoly": (5, 0), "cont": (6, 0), "psd": (14, 0), "nwell": (31, 0),
    "tgo": (44, 0), "m1": (8, 0), "v1": (19, 0), "m2": (10, 0), "v2": (29, 0), "m3": (30, 0),
    "v3": (49, 0), "m4": (50, 0), "tv1": (125, 0), "tm1": (126, 0),
    "m3pin": (30, 2), "m3txt": (30, 25), "m4pin": (50, 2), "m4txt": (50, 25),
    "tm1pin": (126, 2), "tm1txt": (126, 25), "prb": (189, 4)}.items()}


def box(n, x0, y0, x1, y1):
    top.shapes(L[n]).insert(pya.DBox(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))


def cut(n, x, y, a):
    box(n, x - a / 2, y - a / 2, x + a / 2, y + a / 2)


def row(n, x0, x1, y, a, pitch):
    """cuts of size a along x from x0 to x1 (centres), at y"""
    k = int((x1 - x0) / pitch + 1e-9)
    for i in range(k + 1):
        cut(n, x0 + i * pitch, y, a)


def col(n, x, y0, y1, a, pitch):
    k = int((y1 - y0) / pitch + 1e-9)
    for i in range(k + 1):
        cut(n, x, y0 + i * pitch, a)


def pcell(name, x, y, **p):
    ci = ly.add_pcell_variant(LIB, LIB.layout().pcell_id(name), {k: str(v) for k, v in p.items()})
    top.insert(pya.CellInstArray(ci, pya.Trans(pya.Point(round(x / ly.dbu), round(y / ly.dbu)))))
    return ly.cell(ci)


def label(layer, pin, txt, name, x0, y0, x1, y1):
    box(layer, x0, y0, x1, y1); box(pin, x0, y0, x1, y1)
    top.shapes(L[txt]).insert(pya.DText(name, pya.DTrans(pya.DVector((x0 + x1) / 2, (y0 + y1) / 2))))


def stack_m1_m4(x, y, top_layer="m4"):
    """via1 .. via3 at (x, y) with 0.38 x 0.38 landing pads (Mn.d 0.144 um2)"""
    for v in ("v1", "v2", "v3"):
        cut(v, x, y, 0.19)
        if top_layer == "m2" and v == "v1": break
        if top_layer == "m3" and v == "v2": break
    for m in ("m2", "m3", "m4"):
        box(m, x - 0.19, y - 0.19, x + 0.19, y + 0.19)
        if m == top_layer: break


# ------------------------------------------------------------------ the switch
SX, SY = 3.0, 6.0
sw = pcell("nmosHV", SX, SY, w="300u", ws="10u", l="0.45u", ng=30)
stripes = sorted([p.bbox().to_dtype(ly.dbu) for p in pya.Region(sw.begin_shapes_rec(L["m1"])).merged().each()],
                 key=lambda b: b.left)
gates = sorted([p.bbox().to_dtype(ly.dbu) for p in pya.Region(sw.begin_shapes_rec(L["gatpoly"])).merged().each()],
               key=lambda b: b.left)
assert len(stripes) == 31 and len(gates) == 30, (len(stripes), len(gates))
xs = [SX + (b.left + b.right) / 2 for b in stripes]
gx = [SX + (b.left + b.right) / 2 for b in gates]
X_L, X_R = SX + stripes[0].left, SX + stripes[-1].right

# gate bar below the active: poly, a contact per finger, metal1
box("gatpoly", SX + gates[0].left, SY - 0.78, SX + gates[-1].right, SY - 0.18)
for x in gx:
    cut("cont", x, SY - 0.48, 0.16)
box("m1", gx[0] - 0.13, SY - 0.63, gx[-1] + 0.13, SY - 0.33)
box("tgo", SX - 0.27, SY - 1.3, SX + 25.47, SY + 10.52)
# the gate leaves on metal2 to the right, then metal4 to the shifter's output
for x in gx[::5]:
    cut("v1", x, SY - 0.48, 0.19)
box("m2", gx[0] - 0.15, SY - 0.63, 31.5, SY - 0.33)

# source and drain: metal2 buses across the stripes, via1 where the stripe is widened
SRC_Y, DRN_Y = (SY + 1.0, SY + 4.0), (SY + 6.0, SY + 9.0)
box("m2", X_L - 0.3, SRC_Y[0], X_R + 0.3, SRC_Y[1])     # 0.3 past the outer vias (M2.c1)
box("m2", X_L - 0.3, DRN_Y[0], 53.0, DRN_Y[0] + 1.3)    # the drain bus runs on over DP
box("m2", X_L - 0.3, DRN_Y[0], X_R + 0.3, DRN_Y[1])
for k, x in enumerate(xs):
    y0, y1 = (SRC_Y if k % 2 == 0 else DRN_Y)
    box("m1", x - 0.125, y0, x + 0.125, y1)
    col("v1", x, y0 + 0.25, y1 - 0.25, 0.19, 0.41)

# p+ guard ring around switch and gate bar, tied to VSS
GR = (SX - 1.6, SY - 2.6, SX + 25.2 + 1.6, SY + 10.0 + 1.6)   # outer edge
W = 0.8
for (x0, y0, x1, y1) in ((GR[0], GR[1], GR[2], GR[1] + W), (GR[0], GR[3] - W, GR[2], GR[3]),
                         (GR[0], GR[1], GR[0] + W, GR[3]), (GR[2] - W, GR[1], GR[2], GR[3])):
    box("activ", x0, y0, x1, y1); box("m1", x0, y0, x1, y1)
    box("psd", x0 - 0.03, y0 - 0.03, x1 + 0.03, y1 + 0.03)
    if x1 - x0 > y1 - y0:
        row("cont", x0 + 0.4, x1 - 0.4, (y0 + y1) / 2, 0.16, 0.36)
    else:
        col("cont", (x0 + x1) / 2, y0 + 1.2, y1 - 1.2, 0.16, 0.36)    # clear of the corners (Cnt.b)
box("tgo", GR[0] - 0.4, GR[1] - 0.4, GR[2] + 0.4, GR[3] + 0.4)

# VSS: metal3 + metal4 along the bottom, straps up to the source bus and the ring
box("m3", 0.0, 0.0, 56.0, 2.5); box("m4", 0.0, 0.0, 56.0, 2.5)
row("v3", 0.4, 55.6, 1.25, 0.19, 0.48)
for x in xs[2:-1:6]:
    box("m3", x - 0.2, 0.0, x + 0.2, SRC_Y[1])
    col("v2", x, SRC_Y[0] + 0.25, SRC_Y[1] - 0.25, 0.19, 0.41)
    # and where the strap crosses the ring's bottom bar, down onto it
    ry = GR[1] + W / 2
    cut("v1", x, ry, 0.19); cut("v2", x, ry, 0.19)
    box("m2", x - 0.19, ry - 0.19, x + 0.19, ry + 0.19)

# ------------------------------------------------------------------ the diodes on X
DP_X, DP_Y, DN_Y = 33.0, SY + 6.0, SY + 1.0
VH_Y = (16.6, 17.4)              # the VDDH line on metal4
pcell("dpantenna", DP_X, DP_Y, w="20u", l="1.26u")
pcell("dantenna", DP_X, DN_Y, w="20u", l="1.26u")
# the diode PCells draw their metal1 flush with the contact array: 0.05 more all round (M1.c1)
for y in (DP_Y, DN_Y):
    box("m1", DP_X + 0.18, y + 0.16, DP_X + 19.82, y + 1.10)
# DP anode (its metal1, y +0.21..1.05) onto the drain bus extension
row("v1", DP_X + 0.5, DP_X + 19.5, DP_Y + 0.63, 0.19, 0.41)
# DN cathode: a metal2 strip over it, tied to the drain bus at both ends
box("m2", DP_X, DN_Y, DP_X + 20.0, DN_Y + 1.26)
row("v1", DP_X + 0.5, DP_X + 19.5, DN_Y + 0.63, 0.19, 0.41)
for x in (DP_X + 0.3, DP_X + 19.7):
    box("m2", x - 0.3, DN_Y, x + 0.3, DRN_Y[0] + 1.3)
# n-well tap of DP, to VDDH
NT_Y = DP_Y + 2.3
box("nwell", DP_X - 0.31, DP_Y - 0.31, DP_X + 20.31, NT_Y + 1.0)
box("activ", DP_X, NT_Y, DP_X + 20.0, NT_Y + 0.6)
box("m1", DP_X, NT_Y, DP_X + 20.0, NT_Y + 0.6)
row("cont", DP_X + 0.3, DP_X + 19.7, NT_Y + 0.3, 0.16, 0.36)
for x in (DP_X + 10.0,):
    stack_m1_m4(x, NT_Y + 0.3)
    box("m4", x - 0.3, NT_Y + 0.3, x + 0.3, VH_Y[1])

# ------------------------------------------------------------------ R1 and the X straps
RX, RY = 1.0, 22.0
pcell("rppd", RX, RY, w="40u", l="6.65u", R="45")
# X: R1's bottom terminal (y -0.43..-0.13) - metal2, metal3 straps down to the drain bus
row("v1", RX + 0.4, RX + 39.6, RY - 0.28, 0.19, 0.41)
box("m2", RX, RY - 0.9, RX + 40.0, RY - 0.13)
box("m3", RX, RY - 0.9, RX + 40.0, RY - 0.13)
row("v2", RX + 0.4, RX + 39.6, RY - 0.6, 0.19, 0.41)
for x in (6.0, 14.0, 22.0):
    box("m3", x - 0.5, DRN_Y[0], x + 0.5, RY - 0.13)
    col("v2", x, DRN_Y[0] + 0.25, DRN_Y[1] - 0.25, 0.19, 0.41)
# PAD: R1's top terminal (y 6.78..7.08) up through metal4 to a TopMetal1 pad
PT = RY + 6.93
row("v1", RX + 0.4, RX + 39.6, PT, 0.19, 0.41)
for m in ("m2", "m3"):
    box(m, RX, RY + 6.78, RX + 40.0, RY + 8.5)
row("v2", RX + 0.4, RX + 39.6, RY + 7.6, 0.19, 0.41)
box("m4", RX, RY + 6.78, RX + 40.0, RY + 11.0)
row("v3", RX + 0.4, RX + 39.6, RY + 7.6, 0.19, 0.41)
for x in [RX + 1.0 + 0.84 * i for i in range(46)]:
    cut("tv1", x + 0.21, RY + 9.9, 0.42)
label("tm1", "tm1pin", "tm1txt", "PAD", RX - 0.5, RY + 8.9, RX + 40.5, RY + 11.4)

# ------------------------------------------------------------------ the level shifter
io = pya.Layout(); io.read(os.path.join(PDK, "libs.ref/sg13cmos5l_io/gds/sg13cmos5l_io.gds"))
src = io.cell("sg13cmos5l_LevelUp")
lv = ly.create_cell("ref_odt_lvlup")
for li in io.layer_indexes():
    info = io.get_info(li)
    if (info.layer, info.datatype) in ((40, 0), (63, 0)):     # ptap1 marker and its "sub!"
        continue
    lv.shapes(ly.layer(info)).insert(src.shapes(li))
LX, LY = 57.0, 0.5
top.insert(pya.CellInstArray(lv.cell_index(), pya.Trans(pya.Point(round(LX / ly.dbu), round(LY / ly.dbu)))))
# output o (metal2 x 3.18..3.38, y 1.02..7.46) <- the gate, over metal4
O_X, O_Y = LX + 3.28, LY + 3.5
box("m3", 31.0, SY - 0.75, 31.6, SY - 0.21)
cut("v2", 31.3, SY - 0.48, 0.19); cut("v3", 31.3, SY - 0.48, 0.19)
box("m4", 31.0, O_Y - 0.3, 31.6, SY - 0.21)
box("m4", 31.0, O_Y - 0.3, O_X + 0.3, O_Y + 0.3)
cut("v3", O_X, O_Y, 0.19); cut("v2", O_X, O_Y, 0.19)
box("m3", O_X - 0.19, O_Y - 0.19, O_X + 0.19, O_Y + 0.19)
# rails: iovdd (y 0) and vdd (y 18.5) extended right, vss (y 8.5) extended left
for y, x0, x1 in ((LY + 0.0, LX + 3.51, 63.5), (LY + 18.5, LX + 3.51, 63.5), (LY + 8.5, 55.0, LX)):
    box("m1", x0, y - 0.105, x1, y + 0.105)
# vss: via stack at x 55.3 down to the VSS bus
stack_m1_m4(55.3, LY + 8.5, "m3")
box("m3", 55.1, 0.0, 55.5, LY + 8.5)
# iovdd = VDDH: metal4 from the VDDH line (y 18..19) down the right side to the rail
VH_X = 62.9
stack_m1_m4(VH_X, LY + 0.0)
box("m4", VH_X - 0.3, LY - 0.19, VH_X + 0.3, VH_Y[1])
box("m4", 0.0, VH_Y[0], VH_X + 0.3, VH_Y[1])
label("m4", "m4pin", "m4txt", "VDDH", 0.0, VH_Y[0], 1.0, VH_Y[1])
# vdd: the 1.2 V rail on top, out to the right edge on metal4
VD_X = 61.9
stack_m1_m4(VD_X, LY + 18.5)
box("m4", VD_X - 0.3, LY + 18.5 - 0.3, 64.0, LY + 18.5 + 0.3)
label("m4", "m4pin", "m4txt", "VDD", 63.0, LY + 18.2, 64.0, LY + 18.8)
# input i (metal2 x 1.175..1.375, y 9.265..17.755): metal3 up to the EN pin at the top
I_X = LX + 1.275
cut("v2", I_X, LY + 16.5, 0.19)
box("m3", I_X - 0.15, LY + 16.3, I_X + 0.15, 33.4)
DEN_X, DEN_Y = 58.6, 27.0        # the antenna diode on EN
pcell("dantenna", DEN_X, DEN_Y, w="0.78u", l="0.78u")
box("m1", DEN_X + 0.09, DEN_Y + 0.09, DEN_X + 0.69, DEN_Y + 0.69)
cut("v1", DEN_X + 0.39, DEN_Y + 0.39, 0.19); cut("v2", DEN_X + 0.39, DEN_Y + 0.39, 0.19)
box("m2", DEN_X + 0.2, DEN_Y + 0.2, DEN_X + 0.58, DEN_Y + 0.58)
box("m3", I_X - 0.15, DEN_Y + 0.2, DEN_X + 0.58, DEN_Y + 0.58)
label("m3", "m3pin", "m3txt", "EN", I_X - 0.15, 32.4, I_X + 0.15, 33.4)
label("m4", "m4pin", "m4txt", "VSS", 0.0, 0.0, 1.0, 2.5)

# ------------------------------------------------------------------ flatten the PCells
for inst in list(top.each_inst()):
    if inst.cell.is_pcell_variant():
        inst.flatten()
ly.cleanup()
box("prb", 0.0, 0.0, 64.0, 33.4)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
ly.write(OUT)
print("geschrieben:", OUT, top.dbbox())
