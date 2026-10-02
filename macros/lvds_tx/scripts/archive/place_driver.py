#!/usr/bin/env python3
"""Place the Driver anew in lvds_tx.gds from plan_driver, and nothing else.

    python3 place_driver.py [--gds <file>] [--out <file>] [--write]

The generator in this directory built the whole placement once; since then
lvds_tx.gds is edited by hand.  This runs the one plan again, plan_driver in
make_floorplan.py, with today's leaf cells (build/pcells/cells/, left there
by make layout-pcells), and puts the result into the file:

* every device instance of `Driver` is replaced by the planned one, with
  its schematic name as property 61.  The device cells must be in the file
  already -- `make layout-pcells ONLY=Driver` adds new ones;
* the Driver's own shapes above the switches move with the stack they sit
  in (Cc, Ctn1/Ctn2, M13/M2/M14 all rise or sink together); shapes further
  down stay where they are and are listed;
* the pre-driver instance `pd` in `lvds_tx` moves up or down by as much as
  Cc does, so that the stage keeps its NWell 0.85 um inside Cc's.  The
  `predriver` cell itself is not touched, nor is any cell below it.

Without --write the result goes to --out (build/driver_regen/lvds_tx.gds)
for DRC and a look; --write replaces --gds, after a copy to layout/backups/.
floorplan.json is updated only with --write.
"""
import argparse
import datetime
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MACRO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(MACRO, "scripts", "pcells"))

import build_placement  # noqa: E402

build_placement.CELLDIR = os.path.join(MACRO, "build", "pcells", "cells")

import klayout.db as kdb  # noqa: E402

from build_placement import (leaf_bbox, leaf_shape, load_floorplan,  # noqa: E402
                             save_floorplan)
from devices import parse  # noqa: E402
from magfile import UPUM, orient_box  # noqa: E402
from make_floorplan import Plan, plan_driver  # noqa: E402
from spacing import violations  # noqa: E402

GDS = os.path.join(MACRO, "layout", "lvds_tx.gds")
OUT = os.path.join(MACRO, "build", "driver_regen", "lvds_tx.gds")
NAME = 61
# magfile's orientation names are KLayout's: (rotation, mirror) of a Trans
ORIENT = {"r0": (0, False), "r90": (1, False), "r180": (2, False),
          "r270": (3, False), "m0": (0, True), "m45": (1, True),
          "m90": (2, True), "m135": (3, True)}


def plan():
    """The Driver as plan_driver lays it out: (Plan, {inst: cellname})."""
    sub = parse()["Driver"]
    boxes, shapes, cells = {}, {}, {}
    for dev in sub.devices:
        boxes[dev.name] = leaf_bbox(dev.cellname)
        shapes[dev.name] = [leaf_shape(dev)]
        cells[dev.name] = dev.cellname
    p = Plan("Driver", boxes, shapes)
    plan_driver(p)
    missing = set(boxes) - set(p.at)
    if missing:
        raise SystemExit("nicht platziert: %s" % ", ".join(sorted(missing)))
    p.normalise()
    bad = violations({i: p.shapes_of(i, o, x, y)
                      for i, (x, y, o) in p.at.items()})
    if bad:
        raise SystemExit("zu dicht: %s" % bad)
    return p, cells


def trans(p, inst, scale):
    """Where magic would put the instance -- the lower-left of the turned
    .mag box on the planned point -- as a GDS transformation."""
    x, y, o = p.at[inst]
    llx, lly, _, _ = orient_box(p.boxes[inst], o)
    rot, mirror = ORIENT[o]
    return kdb.Trans(rot, mirror, int(round((x - llx) * scale)),
                     int(round((y - lly) * scale)))


def by_name(cell):
    return {inst.property(NAME): inst for inst in cell.each_inst()}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gds", default=GDS)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--write", action="store_true",
                    help="--gds selbst ersetzen (Kopie in layout/backups/)")
    args = ap.parse_args()

    p, cells = plan()
    mtime = os.stat(args.gds).st_mtime
    layout = kdb.Layout(True)
    layout.read(args.gds)
    scale = 1.0 / UPUM / layout.dbu     # internal units -> dbu
    missing = sorted(c for c in set(cells.values()) if layout.cell(c) is None)
    if missing:
        raise SystemExit("nicht in %s: %s -- erst make layout-pcells "
                         "ONLY=Driver" % (os.path.basename(args.gds),
                                          ", ".join(missing)))
    top, drv = layout.cell("lvds_tx"), layout.cell("Driver")
    old = by_name(drv)
    old_boxes = {n: i.dbbox() for n, i in old.items()}
    switches = min(old_boxes[n].bottom for n in ("M5", "M4"))

    for inst in list(drv.each_inst()):
        inst.delete()
    for inst, cellname in sorted(cells.items()):
        drv.insert(kdb.CellInstArray(layout.cell(cellname).cell_index(),
                                     trans(p, inst, scale)),
                   layout.properties_id([[NAME, inst]]))
    new_boxes = {n: i.dbbox() for n, i in by_name(drv).items()}
    rise = new_boxes["Cc"].bottom - old_boxes["Cc"].bottom
    drise = int(round(rise / layout.dbu))

    # the Driver's own shapes: those in the stack above the switches move
    # with it, anything lower is left and reported
    moved, kept = 0, []
    for li in layout.layer_indexes():
        for shape in list(drv.shapes(li).each()):
            if shape.dbbox().bottom >= switches:
                shape.transform(kdb.Trans(0, drise))
                moved += 1
            else:
                kept.append("%s %s" % (layout.get_info(li), shape.dbbox()))

    pd = by_name(top).get("pd")
    if pd is None:
        raise SystemExit("keine Instanz pd in lvds_tx")
    pd.transform(kdb.Trans(0, drise))
    layout.update()

    print("Driver: %.2f x %.2f um (vorher %.2f x %.2f)" % (
        drv.dbbox().width(), drv.dbbox().height(),
        max(b.right for b in old_boxes.values()) -
        min(b.left for b in old_boxes.values()),
        max(b.top for b in old_boxes.values()) -
        min(b.bottom for b in old_boxes.values())))
    for name in sorted(new_boxes, key=lambda n: (-new_boxes[n].bottom,
                                                 new_boxes[n].left)):
        b = new_boxes[name]
        o = old_boxes.get(name)
        shift = ("neu" if o is None else "dx %+6.2f dy %+6.2f"
                 % (b.left - o.left, b.bottom - o.bottom))
        print("  %-6s x %6.2f..%6.2f  y %6.2f..%6.2f   %s"
              % (name, b.left, b.right, b.bottom, b.top, shift))
    gone = sorted(set(old_boxes) - set(new_boxes))
    if gone:
        print("entfernt: %s" % ", ".join(gone))
    print("Cc und alles darueber: dy %+.2f um; eigene Formen des Driver "
          "mitverschoben: %d" % (rise, moved))
    for k in kept:
        print("  nicht verschoben (unter den Schaltern): %s" % k)
    print("pd in lvds_tx: dy %+.2f um, jetzt bei %s; lvds_tx %.2f x %.2f um"
          % (rise, pd.dcplx_trans.disp, top.dbbox().width(),
             top.dbbox().height()))

    target = args.gds if args.write else args.out
    if args.write:
        if os.stat(args.gds).st_mtime != mtime:
            raise SystemExit("%s wurde waehrend des Laufs gespeichert -- "
                             "nichts geschrieben" % args.gds)
        backups = os.path.join(os.path.dirname(os.path.abspath(args.gds)),
                               "backups")
        os.makedirs(backups, exist_ok=True)
        stem = os.path.splitext(os.path.basename(args.gds))[0]
        backup = os.path.join(backups, "%s_VOR_driver_%s.gds" % (
            stem, datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")))
        shutil.copy2(args.gds, backup)
        print("Kopie: %s" % os.path.relpath(backup, MACRO))
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    tmp = target + ".tmp.gds"
    layout.write(tmp)
    os.replace(tmp, target)
    print("geschrieben: %s" % os.path.relpath(target, MACRO))
    if args.write:
        floorplan = load_floorplan()
        floorplan["Driver"] = p.floorplan()
        pd_at = floorplan.get("lvds_tx", {}).get("pd")
        if pd_at:
            pd_at[1] += int(round(rise * UPUM))
        save_floorplan(floorplan)
        print("floorplan.json nachgefuehrt. In KLayout: File > Reload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
