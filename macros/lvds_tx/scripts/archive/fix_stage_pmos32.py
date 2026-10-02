#!/usr/bin/env python3
"""predriver_stage after Mpp2/Mpn2 went from 10 x 4 um to 10 x 3.2 um fingers
(2026-10-02, against the common-mode dip: the last stage pulled up faster
than down, so In_p and In_n were both high at every edge).

swap_pcells.py puts the new, 0.8 um shorter cell at the old origin, and the
gencell draws a device about its centre.  This:

* moves both instances up so that their gate rail (top, metal2) is where it
  was -- the gate net arrives there;
* runs the Va metal1 tabs of the stage (one per Va stripe of the device,
  from the Va strip at the bottom) up to the now shorter stripes;
* deletes the via1 of the Out_p columns that no longer land on a stripe.

    python3 scripts/archive/fix_stage_pmos32.py [--dry-run]
"""
import datetime, os, shutil, sys
import klayout.db as kdb
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
GDS = "layout/lvds_tx.gds"
NEW = "dev_p_w3p2_l0p4_ng10_botc0_guard0"
OLD_RAIL_TOP = 2.27          # metal2 gate rail of dev_p_w4_l0p4_ng10, local
TAB_Y0, TAB_Y1 = 0.92, 1.43  # the stage's Va tabs (metal1), above the strip
ly = kdb.Layout(); ly.read(GDS)
st = ly.cell("predriver_stage"); dev = ly.cell(NEW)
M1, V1, M2 = ly.layer(8, 0), ly.layer(19, 0), ly.layer(10, 0)
um = lambda v: int(round(v / ly.dbu))
rail_top = kdb.Region(dev.shapes(M2)).bbox().top * ly.dbu
dy = round(OLD_RAIL_TOP - rail_top, 3)
print("Gate-Schiene neu bei %.3f, Verschiebung %+.3f um" % (rail_top, dy))
assert abs(dy - 0.4) < 1e-6, dy
pins = {s.text_string: s.dtext.trans.disp for s in dev.shapes(ly.layer(8, 25)).each() if s.is_text()}
stripes = [p for p in kdb.Region(dev.shapes(M1)).merged().each() if p.bbox().height() > p.bbox().width()]
tabs = [s for s in st.shapes(M1).each() if s.is_box() and abs(s.box.bottom - um(TAB_Y0)) <= 1 and abs(s.box.top - um(TAB_Y1)) <= 1]
added, removed = 0, []
for inst in list(st.each_inst()):
    if inst.property(61) not in ("Mpp2", "Mpn2"): continue
    assert ly.cell(inst.cell_index).name == NEW, ly.cell(inst.cell_index).name
    t = inst.dcplx_trans
    assert abs(t.disp.y - 3.455) < 1e-6, ("schon verschoben?", str(t))
    inst.dcplx_trans = kdb.DCplxTrans(kdb.DVector(0, dy)) * t
    t = kdb.ICplxTrans(inst.dcplx_trans, ly.dbu)
    S = kdb.Region([p.transformed(t) for p in stripes])
    bb = S.bbox()
    # Va tabs under this device: lengthen each to overlap its stripe
    for s in tabs:
        b = s.box
        if not (bb.left <= b.left and b.right <= bb.right): continue
        hit = [p for p in S.each() if p.bbox().left <= b.left and b.right <= p.bbox().right]
        assert len(hit) == 1, (inst.property(61), str(b))
        st.shapes(M1).insert(kdb.Box(b.left, b.top - 1, b.right, hit[0].bbox().bottom + um(0.1))); added += 1
    # via1 of the Out_p columns: keep those a stripe still encloses by 0.05 um top and bottom
    for s in list(st.shapes(V1).each()):
        b = s.box if s.is_box() else s.bbox
        if not kdb.Box(bb.left, um(TAB_Y1), bb.right, bb.top).contains(b.center()): continue
        if not any(p.bbox().left <= b.left and b.right <= p.bbox().right and p.bbox().bottom + um(0.05) <= b.bottom and b.top <= p.bbox().top - um(0.05) for p in S.each()):
            removed.append((inst.property(61), str(b.to_dtype(ly.dbu)))); st.shapes(V1).erase(s)
    print(inst.property(61), "neu:", str(inst.dcplx_trans))
print("Va-Laschen verlaengert:", added, "| Via1 entfernt:", len(removed), sorted(set(r[1].split(",")[1].split(";")[0] for r in removed)))
if "--dry-run" in sys.argv: sys.exit()
ts = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
shutil.copy2(GDS, "layout/backups/lvds_tx_VOR_pmos32_%s.gds" % ts)
ly.write(GDS); print("geschrieben:", GDS)
