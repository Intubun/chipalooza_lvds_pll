#!/usr/bin/env python3
"""Pin labels Va, Vss and IREF_IN on iref_x15 (2026-10-02; IREF_OUT had one).

Without them a top-level LVS cannot tell the cell's ports apart: the
extracted subcircuit gets $-numbered pins and the comparison of iref_x15
fails.  Each net is found by extraction from a device terminal (as in
build/top/pack_mine.py): Va from the stripe D0 of Mp1 (a source), Vss from the source of
Mn1, IREF_IN from the drain of Mn1 (the diode).  The pin goes where IREF_OUT's
is, a box on metal2 pin (10/2) with the text on 10/25, at the point of the
net's widest metal2 piece furthest inside it.

    python3 scripts/add_pins.py [--dry-run]
"""
import datetime, os, shutil, sys
import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
GDS = os.path.join(HERE, "..", "layout", "iref_x15.gds")
ly = kdb.Layout(); ly.read(GDS); t = ly.cell("iref_x15")
M1, V1, M2 = ly.layer(8, 0), ly.layer(19, 0), ly.layer(10, 0)
PIN, TXT = ly.layer(10, 2), ly.layer(10, 25)
have = [s.text_string for s in t.shapes(TXT).each() if s.is_text()]

terms = {}
for i in t.each_inst():
    for s in ly.cell(i.cell_index).shapes(ly.layer(8, 25)).each():
        if s.is_text():
            terms.setdefault((i.property(61), s.text_string), i.dcplx_trans * s.dtext.trans.disp.to_p())
l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, t, []))
L = {n: l2n.make_layer(li, n) for n, li in (("m1", M1), ("v1", V1), ("m2", M2))}
l2n.connect(L["m1"], L["v1"]); l2n.connect(L["v1"], L["m2"])
for x in L.values(): l2n.connect(x)
l2n.extract_netlist()
H = 0.15                                   # half size of the pin box
# Va from the stripe "D0" of Mp1 (D0, D2, D4 of Mp1 and Mp2 are the sources on Va);
# its "S1" is the drain, CASC - which build/top/pack_mine.py took for Va on 2026-10-02
for net, key in (("Va", ("Mp1", "D0")), ("Vss", ("Mn1", "S")), ("IREF_IN", ("Mn1", "D"))):
    if net in have:
        print(net, "hat schon ein Label"); continue
    n = l2n.probe_net(L["m1"], terms[key])
    m2 = l2n.shapes_of_net(n, L["m2"], True).merged()
    assert not m2.is_empty(), net
    piece = max(m2.each(), key=lambda p: p.area())
    core = kdb.Region(piece).sized(-int(H / ly.dbu) - 10)      # 10 nm margin to the edge
    assert not core.is_empty(), net
    # centre of the largest rectangle of the shrunk piece (the layout is Manhattan)
    rect = max((q.bbox() for q in core.decompose_trapezoids_to_region().each()), key=lambda r: r.area())
    c = rect.center()
    p = c.to_dtype(ly.dbu)
    t.shapes(PIN).insert(kdb.DBox(p.x - H, p.y - H, p.x + H, p.y + H))
    t.shapes(TXT).insert(kdb.DText(net, kdb.DTrans(p.x, p.y)))
    print("%-8s Pin bei (%.3f, %.3f) auf dem metal2-Stueck %s" % (net, p.x, p.y, piece.bbox().to_dtype(ly.dbu)))
if "--dry-run" in sys.argv:
    sys.exit()
ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
os.makedirs(os.path.join(HERE, "..", "layout", "backups"), exist_ok=True)
shutil.copy2(GDS, os.path.join(HERE, "..", "layout", "backups", "iref_x15_VOR_pins_%s.gds" % ts))
ly.write(GDS); print("geschrieben:", GDS)
