#!/usr/bin/env python3
"""lvds_pattern.gds: the two output flops from sdfbbp_1 to dfrbp_2, plus xinvd
(2026-10-02, schematic: xffp D = s6, xffn D = s6_i = NOT s6, RESET_B on VDD).

The sdfbbp_1 output flops gave D_p/D_n 15 ps of skew (Q rises ~50 ps slower
than it falls) and, extracted, another 13 ps from the longer Q wire of xffn
(7.0 against 4.3 fF on a drive-1 flop) - enough to dent Vos of lvds_tx.

Middle row (y 7.56..11.34), x 0.48..34.08, which the two sdfbbp_1 filled:

    fill_1 | xffn dfrbp_2, m0 | xffp dfrbp_2, r180 | 3 x fill_2 | xinvd inv_1, m0
    0.48     0.96               15.36                29.76        32.64 .. 34.08

xffn mirrored and xffp rotated put both Q pins in the middle, 0.96 um apart,
each on an M2 track (15.06 / 16.02), so fp and fn leave together.  Fill, not
decap, in the gaps: no devices, so the device count LVS sees is the schematic's.

Routing, on the block's own tracks (M2 vertical x = 0.18 + 0.48 k, M3
horizontal y = 0.01 + 0.42 j), M2 hops under the vertical M3 power straps:
  fn     Q -> M2 down to the old fn M3 at y 4.21 -> the old route to the mux
  fp     Q -> M2 down to y 8.41 -> the old fp route (under the VDD strap) to the mux
  s6     the old M3 at y 9.67, on to xffp D (under the VSS strap on M2) and xinvd A
  s6_i   xinvd Y -> M3 y 10.09 west, three hops -> xffn D
  CLK    the old trunk at y 11.35; stubs to both CLK pins; the riser from the
         buffer now crosses under the VSS strap at y 10.51 instead of 9.67
  RESET_B  xffn: the old tie of the sdfbbp_1 RESET_B lands on the new pin as it is;
           xffp: the VDD branch off the strap at y 9.22, extended to the pin
Removed: s6_n (whole net), the scan/set/reset ties, the old pin stubs.

    python3 scripts/rework_outflops.py [--out <file>]     (default: layout/lvds_pattern.gds)
"""
import datetime, glob, os, shutil, sys
import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
GDS = os.path.join(HERE, "..", "layout", "lvds_pattern.gds")
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else GDS
ly = kdb.Layout(); ly.read(GDS); top = ly.cell("lvds_pattern")
M1, V1, M2, V2, M3 = (ly.layer(l, 0) for l in (8, 19, 10, 29, 30))
D = lambda v: int(round(v / ly.dbu))
VIA = 0.19

# ---------------------------------------------------------------- rip-up
# s6_n (xs6 Q_N -> old xffn D) as a whole net, before the cells change
l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
L = {n: l2n.make_layer(li, n) for n, li in (("m1", M1), ("v1", V1), ("m2", M2), ("v2", V2), ("m3", M3))}
for a, b in (("m1", "v1"), ("v1", "m2"), ("m2", "v2"), ("v2", "m3")): l2n.connect(L[a], L[b])
for x in L.values(): l2n.connect(x)
l2n.extract_netlist()
s6n = l2n.probe_net(L["m2"], kdb.DPoint(15.54, 5.0))
assert s6n is not None and s6n.circuit().name == "lvds_pattern", s6n
gone = {"s6_n": 0}
for n, li in (("v1", V1), ("m2", M2), ("v2", V2), ("m3", M3)):
    net = l2n.shapes_of_net(s6n, L[n], False)
    for s in list(top.shapes(li).each()):
        if (kdb.Region(s.polygon) - net).is_empty():
            top.shapes(li).erase(s); gone["s6_n"] += 1


def kill(li, *boxes):
    """erase the top-level shapes with exactly these bounding boxes"""
    for b in boxes:
        x0, y0, x1, y1 = (float(v) for v in b.replace(";", ",").split(","))
        want = kdb.Box(D(x0), D(y0), D(x1), D(y1))
        hit = [s for s in top.shapes(li).each() if s.bbox() == want]
        assert len(hit) == 1, (ly.get_info(li), b, len(hit))
        top.shapes(li).erase(hit[0])


# fn: old Q stub, its M3 at y 8.41 and the M2 down to y 4.21; the M3 at y 4.21 is shortened below
kill(M2, "0.800,7.835;1.000,8.410", "0.795,8.265;1.005,8.555", "7.755,8.265;7.965,8.555",
     "7.760,4.110;10.840,8.510", "10.635,4.065;10.845,4.355")
kill(M3, "0.755,8.310;1.045,8.510", "0.800,8.310;7.960,8.510", "7.715,8.310;8.005,8.510",
     "10.595,4.110;10.885,4.310", "10.640,4.110;17.560,4.310")
kill(V1, "0.805,8.315;0.995,8.505")
kill(V2, "0.805,8.315;0.995,8.505", "7.765,8.315;7.955,8.505", "10.645,4.115;10.835,4.305")
# fp: only the via onto the old Q
kill(V1, "17.605,8.315;17.795,8.505")
# reset_b to the old xffn SET_B (the riser to the top-row flop stays, shortened)
kill(M2, "5.520,8.465;5.720,9.140", "5.475,8.685;5.765,9.240", "2.475,8.685;2.685,8.975", "2.480,8.730;2.680,14.810")
kill(M3, "2.435,8.730;2.725,8.930", "2.480,8.730;5.720,8.930", "5.475,8.730;5.765,8.930")
kill(V1, "5.525,9.000;5.715,9.190")
kill(V2, "2.485,8.735;2.675,8.925", "5.525,8.735;5.715,8.925")
# reset_b to the old xffp RESET_B: the stub off the M2 at y 10.51
kill(M2, "20.045,9.710;20.335,10.025")
kill(V1, "20.095,9.760;20.285,9.950")
rb = [s for s in top.shapes(M2).each() if s.bbox() == kdb.Box(D(16.88), D(9.78), D(21.4), D(14.81))]
assert len(rb) == 1
rbr = kdb.Region(rb[0].polygon) - kdb.Region(kdb.Box(D(20.0), D(9.7), D(20.4), D(10.4)))
top.shapes(M2).erase(rb[0]); top.shapes(M2).insert(rbr)
# scan / set ties of both sdfbbp_1 (VSS, VDD)
kill(M2, "15.920,9.105;16.120,9.395", "15.920,9.150;16.840,11.440", "16.520,9.525;16.885,9.815",
     "16.160,11.195;16.360,11.485", "32.740,9.170;33.550,11.485", "22.250,8.830;22.590,9.350")
kill(V1, "15.925,9.155;16.115,9.345", "16.570,9.575;16.760,9.765", "16.165,11.245;16.355,11.435",
     "32.790,9.220;32.980,9.410", "33.310,9.220;33.500,9.410", "33.310,11.245;33.500,11.435",
     "22.325,9.125;22.515,9.315")
kill(V2, "22.325,9.125;22.515,9.315")
# CLK: vias onto the old pins, and the riser that crossed under the VSS strap at y 9.67
kill(V1, "13.045,9.575;13.235,9.765", "29.845,9.575;30.035,9.765")
kill(M2, "27.440,5.370;31.000,11.450", "29.840,9.525;30.040,9.815")
# s6: the pad on the old (metal2) D pin of xffp
kill(M2, "32.195,9.565;32.485,9.775")
kill(M3, "32.195,9.570;32.485,9.770")
kill(V2, "32.245,9.575;32.435,9.765")

# ---------------------------------------------------------------- cells
old = [i for i in top.each_inst() if ly.cell(i.cell_index).name == "sg13cmos5l_sdfbbp_1"]
assert sorted(round(i.dcplx_trans.disp.x, 3) for i in old) == [17.28, 34.08]
for i in old: i.delete()
if ly.cell("sg13cmos5l_inv_1") is None:
    lib = kdb.Layout(); lib.read(glob.glob(os.environ["PDK_ROOT"] + "/" + os.environ["PDK"] + "/libs.ref/sg13cmos5l_stdcell/gds/*.gds")[0])
    ly.create_cell("sg13cmos5l_inv_1").copy_tree(lib.cell("sg13cmos5l_inv_1"))
Y = 11.34
R180 = lambda x: kdb.DCplxTrans(1, 180, False, kdb.DVector(x, Y))
M0 = lambda x: kdb.DCplxTrans(1, 0, True, kdb.DVector(x, Y))
for name, t in (("sg13cmos5l_fill_1", R180(0.96)), ("sg13cmos5l_dfrbp_2", M0(0.96)), ("sg13cmos5l_dfrbp_2", R180(29.76)),
                ("sg13cmos5l_fill_2", R180(30.72)), ("sg13cmos5l_fill_2", R180(31.68)), ("sg13cmos5l_fill_2", R180(32.64)),
                ("sg13cmos5l_inv_1", M0(32.64))):
    top.insert(kdb.DCellInstArray(ly.cell(name).cell_index(), t))

# ---------------------------------------------------------------- routing
def box(li, x0, y0, x1, y1): top.shapes(li).insert(kdb.DBox(x0, y0, x1, y1))
def via(li, x, y): box(li, x - VIA / 2, y - VIA / 2, x + VIA / 2, y + VIA / 2)
def stack(x, y, horizontal=True):
    """via1 + via2 on one spot, with a metal2 pad that encloses both"""
    via(V1, x, y); via(V2, x, y)
    # 0.29 x 0.5: M2.d wants 0.144 um2 for a pad that leads nowhere
    box(M2, x - 0.145, y - 0.25, x + 0.145, y + 0.25) if horizontal else box(M2, x - 0.25, y - 0.145, x + 0.25, y + 0.145)

# fn: Q (15.06, 10.07) -> M2 down to M3 y 4.21 (shortened to start here) -> old route
via(V1, 15.06, 10.07); box(M2, 14.96, 4.065, 15.16, 10.215); via(V2, 15.06, 4.21); box(M3, 14.915, 4.11, 17.56, 4.31)
# fp: Q (16.02, 10.07) -> M2 down to y 8.41 -> east onto the old hop under the VDD strap
via(V1, 16.02, 10.07); box(M2, 15.92, 8.31, 16.12, 10.215); box(M2, 15.92, 8.31, 17.8, 8.51)
# CLK: riser from the buffer, under the VSS strap at y 10.51, up to the trunk at 11.35
box(M2, 30.8, 5.37, 31.0, 10.61); box(M2, 27.44, 10.41, 31.0, 10.61); box(M2, 27.44, 10.41, 27.64, 11.45)
via(V1, 23.22, 9.67); box(M2, 23.12, 9.525, 23.32, 11.495); via(V2, 23.22, 11.35)      # xffp CLK
via(V1, 7.6, 9.67); box(M2, 7.455, 9.57, 13.24, 9.77)                                  # xffn CLK, onto the old stub at 13.14
# s6: old M3 at y 9.67 west to 30.255, M2 under the VSS strap to xffp D; xinvd A under the M3
box(M3, 30.255, 9.57, 32.3, 9.77); via(V2, 30.4, 9.67); box(M2, 29.185, 9.57, 30.545, 9.77); via(V1, 29.33, 9.67)
stack(33.1, 9.67)
# s6_i: xinvd Y -> M3 y 10.09 west, hops under the three straps, -> xffn D
stack(33.61, 10.09)
box(M3, 30.255, 9.99, 33.755, 10.19); via(V2, 30.4, 10.09); box(M2, 27.82, 9.99, 30.545, 10.19); via(V2, 27.965, 10.09)
box(M3, 20.38, 9.99, 28.11, 10.19); via(V2, 20.525, 10.09); box(M2, 18.0, 9.99, 20.67, 10.19); via(V2, 18.145, 10.09)
box(M3, 10.46, 9.99, 18.29, 10.19); via(V2, 10.605, 10.09); box(M2, 8.08, 9.99, 10.75, 10.19); via(V2, 8.225, 10.09)
box(M3, 1.245, 9.99, 8.37, 10.19); via(V2, 1.39, 10.09); box(M2, 1.29, 9.5, 1.49, 10.26); via(V1, 1.39, 9.67)
# xffp RESET_B -> VDD: the M3 branch off the VDD strap at y 9.22, on to the pin
box(M3, 20.17, 9.07, 27.45, 9.37); via(V2, 27.3, 9.22); box(M2, 27.2, 9.0, 27.4, 9.76); via(V1, 27.3, 9.6)
# (xffn RESET_B -> VDD: the old tie at x 3.39 and its via1 land on the new pin as they are)
# reset_b riser to the top-row flop, shortened to the part it still needs
box(M2, 2.48, 12.885, 2.68, 14.81)

for li in (M2, M3):          # one polygon per touching group, as the rest of the file
    r = kdb.Region(top.shapes(li)).merged(); top.shapes(li).clear(); top.shapes(li).insert(r)
print("entfernt: s6_n", gone["s6_n"], "Formen")
if out == GDS:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(GDS, os.path.join(HERE, "..", "layout", "backups", "lvds_pattern_VOR_outflops_%s.gds" % ts))
ly.write(out); print("geschrieben:", out)
