#!/usr/bin/env python3
"""The top layout without the PLL, renamed slot_14 (2026-10-07).

Rahul's PLL leaves this project.  From the top layout:

* the instance of `pll` goes, with every cell only it used;
* every top-level shape of a net that touched the PLL goes - the lines from
  dig_in[5..18] to its inputs, pll_clk from its output to lvds_pattern - and the
  old ref_clk line that ran from lvds_pattern towards the PLL's REF_CLK.  The
  frame's own pins stay: they lie entirely inside the 2 um edge strips.
* lvds_pattern's pll_clk, now an unused mux input, is held at VDD (1.2 V): an M4
  bridge from the pin onto the pattern's VDD rail.  Towards VSS the lines of
  mode / en / clk_src / reset are in the way.  (drop_clk_select.py took the
  bridge out again the same day, with the pin and the mux behind it);
* ref_clk comes from s14_an_0_esd - the pad's `padres`, through its secondary
  protection, since it drives a gate - along M4 at y 238.45 across where the PLL
  was, then down to the pin;
* Out_n to s14_an[1], Out_p to s14_an[2], the direct `pad` (no series resistor
  in an LVDS output).  Out_n leaves lvds_tx above Out_p and the two pads lie in
  that order too, so the lines do not cross; 3.27 um of metal3, the pin's height;
* the top cell is renamed slot_14.

    python3 scripts/top/split_pll.py [--in <gds>] [--out <gds>]

Default in and out: layout/slot_14.gds (git mv the old file there first);
the .klay.gds becomes a copy of the result.
"""
import datetime, os, shutil, sys
import klayout.db as kdb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
os.chdir(ROOT)
OLD_TOP, NEW_TOP = "sg13cmos5l_chipalooza_analog_project", "slot_14"
arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
SRC = arg("--in", "layout/slot_14.gds")
OUT = arg("--out", "layout/slot_14.gds")
VIA = 0.19

ly = kdb.Layout(); ly.read(SRC)
top = ly.cell(OLD_TOP) or ly.cell(NEW_TOP)
assert top is not None and ly.cell("pll") is not None, "no top cell with a pll in %s" % SRC
names = [("m1", 8), ("v1", 19), ("m2", 10), ("v2", 29), ("m3", 30), ("v3", 49), ("m4", 50), ("tv1", 125), ("tm1", 126)]
LI = {n: ly.layer(l, 0) for n, l in names}
W, H = top.dbbox().width(), top.dbbox().height()


def frame_shape(s):
    """a pin of the slot frame: entirely inside the left or right 2 um strip"""
    b = s.dbbox()
    return b.right <= 2.0 + 1e-6 or b.left >= W - 2.1 - 1e-6


# ---------------------------------------------------------------- nets of the PLL
l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
L = {n: l2n.make_layer(LI[n], n) for n, _ in names}
seq = [n for n, _ in names]
for a, b in zip(seq, seq[1:]): l2n.connect(L[a], L[b])
for x in L.values(): l2n.connect(x)
for l, n in ((8, "m1"), (10, "m2"), (30, "m3"), (50, "m4"), (126, "tm1")):
    t = l2n.make_text_layer(ly.layer(l, 25), "t%d" % l); l2n.connect(L[n], t)
l2n.extract_netlist()
circ = l2n.netlist().circuit_by_name(top.name)
doomed = []
for net in circ.each_net():
    users = set((sp.subcircuit().circuit_ref().name, sp.pin().name()) for sp in net.each_subcircuit_pin())
    if not any(c == "pll" for c, _ in users):
        continue
    others = sorted("%s.%s" % u for u in users if u[0] != "pll")
    # the only other block a PLL net may reach is lvds_pattern's pll_clk
    assert all(o == "lvds_pattern.pll_clk" for o in others), (net.expanded_name(), others)
    doomed.append((net, net.expanded_name(), others))
ref = l2n.probe_net(L["m2"], kdb.DPoint(330.0, 109.915))     # the old ref_clk line
assert ref is not None
doomed.append((ref, "ref_clk (Leitung zur PLL)", []))
gone = 0
for net, name, others in doomed:
    region = {n: l2n.shapes_of_net(net, L[n], False) for n, _ in names}
    k = 0
    for n, _ in names:
        for s in list(top.shapes(LI[n]).each()):
            if not s.is_text() and not frame_shape(s) and (kdb.Region(s.polygon) - region[n]).is_empty():
                top.shapes(LI[n]).erase(s); k += 1
    gone += k
    print("  %-26s %3d Formen entfernt%s" % (name, k, ("  (auch an " + ", ".join(others) + ")") if others else ""))
ly.cell("pll").prune_cell()
print("  PLL-Instanz und ihre Zellen entfernt; Zellen jetzt:", ly.cells())

# ---------------------------------------------------------------- new wiring
M2, V2, M3, V3, M4 = (ly.layer(l, 0) for l in (10, 29, 30, 49, 50))
def box(li, x0, y0, x1, y1): top.shapes(li).insert(kdb.DBox(x0, y0, x1, y1))
def via(li, x, y): box(li, x - VIA / 2, y - VIA / 2, x + VIA / 2, y + VIA / 2)


def stack(x, y):
    """via2 + via3 on a metal2 pin of lvds_pattern; metal3 pad 0.3 x 0.5 (M3.d: 0.144 um2)"""
    via(V2, x, y); via(V3, x, y); box(M3, x - 0.15, y - 0.25, x + 0.15, y + 0.25)


X = 339.28                 # the via column the pattern's inputs already use
# the metal3 of mode / en / clk_src / reset ended flush with their via2 (M3.c1): 0.05 um more
for y in (101.915, 103.915, 107.915, 111.915):
    box(M3, X - 0.15, y - 0.1, X + 0.15, y + 0.1)
# pll_clk (pin at y 105.915) -> VDD rail of lvds_pattern (metal3, y 94.385..96.385, here from x 340)
stack(X, 105.915)
box(M4, X - 0.15, 95.23, X + 0.15, 106.07)
box(M3, 339.0, 94.385, 340.1, 96.385); via(V3, X, 95.385)
# ref_clk: s14_an_0_esd (metal3 at x 535.15..537.15, y 238.2..238.7) -> pin at y 109.915
stack(X, 109.915)
box(M4, X - 0.15, 109.76, X + 0.15, 238.65)
box(M4, X - 0.15, 238.25, 534.35, 238.65)
via(V3, 534.15, 238.45); box(M3, 533.95, 238.2, 535.6, 238.7)
# Out_n -> s14_an[1] (metal3 pin x 535.05..536.44, y 135.18..159.95)
box(M3, 514.2, 118.145, 531.2, 121.41)
box(M3, 527.93, 118.145, 531.2, 139.77)
box(M3, 527.93, 136.5, 535.6, 139.77)
# Out_p -> s14_an[2] (y 25.18..49.95)
box(M3, 514.2, 99.19, 531.2, 102.455)
box(M3, 527.93, 45.5, 531.2, 102.455)
box(M3, 527.93, 45.5, 535.6, 48.77)
for li in (M3, M4):
    r = kdb.Region(top.shapes(li)).merged(); top.shapes(li).clear(); top.shapes(li).insert(r)

top.name = NEW_TOP
print("  entfernt insgesamt %d Formen; Topzelle heisst jetzt %s" % (gone, NEW_TOP))
if OUT == SRC:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(SRC, "layout/backups/%s_VOR_split_%s.gds" % (NEW_TOP, ts))
ly.write(OUT)
if OUT == "layout/slot_14.gds":
    shutil.copy2(OUT, "layout/slot_14.klay.gds")
print("geschrieben:", OUT)
