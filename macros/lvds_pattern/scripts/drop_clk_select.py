#!/usr/bin/env python3
"""lvds_pattern.gds without the clock source select (2026-10-07).

The PLL left the project, so pll_clk has nothing to come from and clk_src
nothing to choose.  From the layout:

* xcsel (mux2_2, r0 at x 4.32 in the middle row, 11 sites) goes; five fill_2
  and a fill_1 take its sites.  Fill, not decap, as in rework_outflops.py: no
  devices, so the device count LVS sees is the schematic's.
* pll_clk and clk_src go as whole nets - their lines from the pins at the left
  edge to the mux, the pins and their labels.
* ref_clk, which ended on the mux's A0, runs on along its M2 at y 6.69..6.99 to
  x 8.92 and up the 0.2 um column of the old mux output (X, via1 at 8.82 / 6.31),
  which carries on as before to CLK of both lgcp_1.  The two via1 onto the mux's
  M1 go with the mux; nothing else of another net is on M2 there - the VSS strap
  above it is on M3.

    python3 scripts/drop_clk_select.py [--out <file>]     (default: layout/lvds_pattern.gds)
"""
import datetime, os, shutil, sys
import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
GDS = os.path.join(HERE, "..", "layout", "lvds_pattern.gds")
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else GDS
ly = kdb.Layout(); ly.read(GDS); top = ly.cell("lvds_pattern")
M1, V1, M2, V2, M3 = (ly.layer(l, 0) for l in (8, 19, 10, 29, 30))
M2PIN, M2TXT = ly.layer(10, 2), ly.layer(10, 25)
D = lambda v: int(round(v / ly.dbu))

# ---------------------------------------------------------------- nets
l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
L = {n: l2n.make_layer(li, n) for n, li in (("m1", M1), ("v1", V1), ("m2", M2), ("v2", V2), ("m3", M3))}
for a, b in (("m1", "v1"), ("v1", "m2"), ("m2", "v2"), ("v2", "m3")): l2n.connect(L[a], L[b])
for x in L.values(): l2n.connect(x)
t = l2n.make_text_layer(M2TXT, "t2"); l2n.connect(L["m2"], t)
t = l2n.make_text_layer(ly.layer(8, 25), "t1"); l2n.connect(L["m1"], t)     # the cells' pin names
l2n.extract_netlist()
circ = l2n.netlist().circuit_by_name("lvds_pattern")
mux = [sc for sc in circ.each_subcircuit()
       if sc.circuit_ref().name == "sg13cmos5l_mux2_2"
       and (sc.trans.disp - kdb.DVector(4.32, 3.78)).length() < 1e-3]
assert len(mux) == 1, "xcsel not where it was"
pins = {p.name(): mux[0].net_for_pin(p.id()).expanded_name() for p in mux[0].circuit_ref().each_pin()}
assert (pins["A0"], pins["A1"], pins["S"]) == ("ref_clk", "pll_clk", "clk_src"), pins

# ---------------------------------------------------------------- rip-up
gone = {}
for name in ("pll_clk", "clk_src"):
    net = circ.net_by_name(name)
    gone[name] = 0
    for n, li in (("v1", V1), ("m2", M2), ("v2", V2), ("m3", M3)):
        region = l2n.shapes_of_net(net, L[n], False)
        for s in list(top.shapes(li).each()):
            if not s.is_text() and (kdb.Region(s.polygon) - region).is_empty():
                top.shapes(li).erase(s); gone[name] += 1
    for li in (M2PIN, M2TXT):
        for s in list(top.shapes(li).each()):
            if (s.is_text() and s.text_string == name) or \
               (not s.is_text() and (kdb.Region(s.polygon) - l2n.shapes_of_net(net, L["m2"], False)).is_empty()):
                top.shapes(li).erase(s); gone[name] += 1


def kill(li, b):
    """erase the one shape whose bounding box is b"""
    hit = [s for s in top.shapes(li).each() if not s.is_text() and s.dbbox() == b]
    assert len(hit) == 1, (ly.get_info(li), b, len(hit))
    top.shapes(li).erase(hit[0])


kill(V1, kdb.DBox(6.58, 5.33, 6.77, 5.52))         # ref_clk onto A0
kill(V1, kdb.DBox(8.725, 6.215, 8.915, 6.405))     # X onto the old output column
# ref_clk's stub down to A0 (x 6.495..6.855) is part of the line's polygon: cut below y 6.69
STUB = kdb.DBox(6.495, 5.18, 6.855, 6.69)

inst = [i for i in top.each_inst() if i.cell.name == "sg13cmos5l_mux2_2"
        and i.trans.disp == kdb.Point(D(4.32), D(3.78))]
assert len(inst) == 1
inst[0].delete()
for x, cell in ((4.32, "fill_2"), (5.28, "fill_2"), (6.24, "fill_2"), (7.20, "fill_2"),
                (8.16, "fill_2"), (9.12, "fill_1")):
    c = ly.cell("sg13cmos5l_" + cell)
    top.insert(kdb.CellInstArray(c.cell_index(), kdb.Trans(kdb.Trans.R0, D(x), D(3.78))))

# ---------------------------------------------------------------- ref_clk on
r = kdb.Region(top.shapes(M2)) - kdb.Region(STUB.to_itype(ly.dbu))
for b in (kdb.DBox(6.495, 6.69, 8.92, 6.99), kdb.DBox(8.72, 6.165, 8.92, 6.99)):
    r.insert(b.to_itype(ly.dbu))
top.shapes(M2).clear(); top.shapes(M2).insert(r.merged())

print("  entfernt: xcsel, %s" % ", ".join("%s (%d Formen)" % kv for kv in gone.items()))
if out == GDS:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    shutil.copy2(GDS, os.path.join(HERE, "..", "layout", "backups",
                                   "lvds_pattern_VOR_clksel_%s.gds" % ts))
ly.write(out)
print("geschrieben:", out)
