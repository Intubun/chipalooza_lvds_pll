#!/usr/bin/env python3
"""Rebuild predriver_stage as two rows of ring-less devices with tap strips.
Run once, 2026-09-29, from macros/lvds_tx inside the container:

    python3 scripts/archive/rebuild_stage.py

The 16 devices are gencells without a guard ring (devices.py:
SUBCKT_OVERRIDES).  This places them and draws what the rings used to be:

    y  ptap strip (Vss)       Activ + pSD + Cont + Metal1, pin "Vss"
       NMOS row               top-flush under the strip
       -- 0.62 um --          NW.d1: N+Activ in ThickGateOx to NWell
       PMOS row  } one NWell  bottom-flush over the strip
       ntap strip (Va)        Activ + Cont + Metal1, pin "Va"
    0  NWell bottom edge      where it always was: it merges with Cc's NWell
                              below, 0.85 um into it, as before

Each column is one inverter, PMOS under NMOS on one centre line, the right
half the mirror image (m90) of the left about the pre-driver's axis.  One
ThickGateOx covers the whole stage.  The strips are the old ring bar
rebuilt: 0.30 um Activ, 0.62 um inside the NWell (NW.e1), 0.44 um from the
device Activ, pSD 0.03 um over the ptap Activ and 0.41 um from the NFET gate
(pSD.j1 wants 0.40).  Every gate is contacted on the inner side only
(devices.py: MODEL_OVERRIDES), so the source stripes can run straight into
the strips in metal1.

Nothing but predriver_stage changes; the old file goes to layout/backups/.
Run again, it replaces what it drew itself and refuses anything else.
"""
import datetime
import os
import shutil

import klayout.db as kdb

GDS = "layout/lvds_tx.gds"
AXIS = 19400                    # nm, the pre-driver's axis
GAP = -300                      # between PMOS cell boxes: Activ 0.94 um apart,
                                # pSD 0.58, metal1 0.98 -- room for two wires
TAP_IN, TAP_H, TAP_GAP = 620, 300, 440
# The NWell, and with it both strips and the ThickGateOx, reach this far past
# the outer PMOS on either side: as far as Cop/Con in the Driver allow.  The
# NWell stops 0.51 um short of them (0.5 um between a PMOS and an NMOS cell
# is clean), which puts the ThickGateOx exactly TGO.e's 0.86 um from theirs.
EXTEND = 3380
NW_NPLUS = 620                  # NW.d1
TGO_OVER = 270                  # TGO.a
PSD_OVER, CONT, CONT_SPACE, CONT_IN = 30, 160, 200, 70
LEFT = [("Mpp2", "Mnp2"), ("Mpp1", "Mnp1"), ("Mpp0", "Mnp0"), ("Mpxn", "Mnxn")]
RIGHT = [("Mpn2", "Mnn2"), ("Mpn1", "Mnn1"), ("Mpn0", "Mnn0"), ("Mpxp", "Mnxp")]

mtime = os.stat(GDS).st_mtime
ly = kdb.Layout(True)
ly.read(GDS)
L = {n: ly.layer(*n) for n in ((1, 0), (6, 0), (8, 0), (8, 2), (8, 25), (14, 0),
                               (31, 0), (44, 0))}
stage = ly.cell("predriver_stage")
inst = {i.property(61): i for i in stage.each_inst()}
before = {i.property(61): (ly.cell(i.cell_index).name, str(i.trans))
          for i in stage.each_inst()}


def activ(name):
    """The device's Activ box, in the orientation of its instance."""
    i = inst[name]
    cell = ly.cell(i.cell_index)
    box = kdb.Region(cell.shapes(L[(1, 0)])).bbox()
    t = kdb.Trans(i.trans.rot, i.trans.is_mirror(), 0, 0)
    return (t * box), (t * cell.bbox())


def place(name, xc, y_ref, top):
    """Centre the cell box on xc; put its Activ bottom (or top) on y_ref."""
    act, box = activ(name)
    dx = xc - (box.left + box.right) // 2
    dy = y_ref - (act.top if top else act.bottom)
    t = inst[name].trans
    inst[name].trans = kdb.Trans(t.rot, t.is_mirror(), dx, dy)


# own shapes: the ThickGateOx patch the old ringed cells needed, or what an
# earlier run of this script drew -- nothing on a routing layer, and no
# metal1 beyond the two strips
own = {li: stage.shapes(li).size() for li in ly.layer_indexes()
       if stage.shapes(li).size()}
mine = {L[n] for n in ((1, 0), (6, 0), (8, 0), (8, 2), (8, 25), (14, 0),
                       (31, 0), (44, 0))}
assert set(own) <= mine and own.get(L[(8, 0)], 0) <= 2, \
    "predriver_stage hat eigene Shapes, die nicht von hier sind: %s" % own
stage.clear_shapes()

# columns: PMOS cell widths set the pitch, packed outward from the axis
centres = {}
edge = AXIS - GAP // 2          # right edge of the innermost left column
for p, n in LEFT[::-1]:         # innermost first
    w = activ(p)[1].width()
    centres[(p, n)] = edge - w // 2
    edge = edge - w - GAP
for (p, n), (pm, nm) in zip(LEFT, RIGHT):
    centres[(pm, nm)] = 2 * AXIS - centres[(p, n)]

# PMOS row: Activ bottom-flush over the ntap strip
p_act_bottom = TAP_IN + TAP_H + TAP_GAP
for (p, n), xc in centres.items():
    place(p, xc, p_act_bottom, top=False)
pmos = [activ(p)[0].moved(inst[p].trans.disp) for p, _n in centres]
pcell = [activ(p)[1].moved(inst[p].trans.disp) for p, _n in centres]
nw = kdb.Box(min(b.left for b in pcell) - EXTEND, 0,
             max(b.right for b in pcell) + EXTEND,
             max(a.top for a in pmos) + NW_NPLUS)

# NMOS row: Activ top-flush under the ptap strip, the tallest NW_NPLUS off
tallest = max(activ(n)[0].height() for _p, n in centres)
n_act_top = nw.top + NW_NPLUS + tallest
for (p, n), xc in centres.items():
    place(n, xc, n_act_top, top=True)
nmos = [activ(n)[0].moved(inst[n].trans.disp) for _p, n in centres]


def strip(y0, label, psd):
    act = kdb.Box(nw.left + TAP_IN, y0, nw.right - TAP_IN, y0 + TAP_H)
    stage.shapes(L[(1, 0)]).insert(act)
    if psd:
        stage.shapes(L[(14, 0)]).insert(act.enlarged(PSD_OVER, PSD_OVER))
    n = (act.width() - 2 * CONT_IN + CONT_SPACE) // (CONT + CONT_SPACE)
    span = n * CONT + (n - 1) * CONT_SPACE
    x = act.left + ((act.width() - span) // 2) // 5 * 5
    y = act.bottom + (TAP_H - CONT) // 2
    for k in range(n):
        x0 = x + k * (CONT + CONT_SPACE)
        stage.shapes(L[(6, 0)]).insert(kdb.Box(x0, y, x0 + CONT, y + CONT))
    # Metal1 over the whole strip.  Possible because the devices have no
    # gate rail on the strip's side (devices.py: MODEL_OVERRIDES); with one
    # it came within 0.115 um of that rail's metal1 (M1.b wants 0.18)
    m1 = act
    for layer in ((8, 0), (8, 2)):
        stage.shapes(L[layer]).insert(m1)
    c = m1.center()
    stage.shapes(L[(8, 25)]).insert(kdb.Text(label, kdb.Trans(c.x, c.y)))
    return act


ntap = strip(TAP_IN, "Va", psd=False)
ptap = strip(n_act_top + TAP_GAP, "Vss", psd=True)
stage.shapes(L[(31, 0)]).insert(nw)
every = pmos + nmos + [ntap, ptap]
stage.shapes(L[(44, 0)]).insert(kdb.Box(
    min(b.left for b in every) - TGO_OVER, ntap.bottom - TGO_OVER,
    max(b.right for b in every) + TGO_OVER, ptap.top + TGO_OVER))

after = {i.property(61): ly.cell(i.cell_index).name for i in stage.each_inst()}
assert after == {k: v[0] for k, v in before.items()}, "Instanzen veraendert"
for (p, n), xc in sorted(centres.items(), key=lambda kv: kv[1]):
    print("Spalte x %6.3f  %-5s %-5s" % (xc / 1e3, p, n))
print("NWell   ", nw.to_dtype(ly.dbu))
print("ntap    ", ntap.to_dtype(ly.dbu), " ptap ", ptap.to_dtype(ly.dbu))
print("Stufe   ", stage.dbbox())
assert os.stat(GDS).st_mtime == mtime, "GDS waehrend des Laufs gespeichert"
backup = "layout/backups/lvds_tx_VOR_stage_taps_%s.gds" % (
    datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss"))
shutil.copy2(GDS, backup)
os.makedirs("build", exist_ok=True)
ly.write("build/stage.tmp.gds")
os.replace("build/stage.tmp.gds", GDS)
print("geschrieben:", GDS, "(vorher:", backup + ")")
