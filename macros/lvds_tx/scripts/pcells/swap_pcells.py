#!/usr/bin/env python3
"""Put freshly generated device cells into lvds_tx.gds, and change nothing else.

    python3 swap_pcells.py [--dry-run] [--gds <file>]

layout/lvds_tx.gds is the layout, placed and routed by hand in KLayout.  Its
device cells -- every cell whose name starts with `dev_` -- are the one
exception: they come from the PDK's magic gencells, and update_pcells.sh
leaves one GDS per cell in build/pcells/gds/.  This takes them into the file:

* a device cell the file already has gets the new geometry in place.  Its
  instances do not move.  The gencell draws a device around its origin, so a
  cell that grew grows about its centre, and may now reach a neighbour;
* an instance whose device now needs a *different* cell -- the schematic
  changed w, l or ng, or devices.py its gencell options, and with them the
  cell name -- is pointed at the new cell, at the same position and in the
  same orientation.  Instances are matched to the schematic by their name
  (GDS property 61: magic wrote it, and KLayout keeps it on a copy) within
  the cell of their subcircuit;
* a device cell nothing uses any more is deleted.  One the schematic has but
  the layout does not place yet stays behind as a top cell, to be placed by
  hand.

Every other cell -- its shapes, texts and instances -- is compared before
and after, and the file is written only if nothing but the device cells and
the re-pointed instances changed.  The old file goes to layout/backups/
first.

That makes two rules for editing lvds_tx.gds: never draw inside a dev_*
cell (the next update puts the generator's geometry back), and never give a
cell of your own a name starting with dev_.
"""
import argparse
import datetime
import glob
import os
import shutil
import sys

import klayout.db as kdb

from devices import parse

HERE = os.path.dirname(os.path.abspath(__file__))
MACRO = os.path.dirname(os.path.dirname(HERE))
GDS = os.path.join(MACRO, "layout", "lvds_tx.gds")
BUILD = os.path.join(MACRO, "build", "pcells")
CELLS = os.path.join(BUILD, "gds")

PREFIX = "dev_"
NAME = 61           # the GDS property an instance's name is kept in


def is_device(name):
    return name.startswith(PREFIX)


def size(box):
    return "%.2f x %.2f" % (box.width(), box.height())


def content(layout, cell):
    """A cell's own shapes, {(layer, datatype): (Region, [texts])}."""
    out = {}
    for li in layout.layer_indexes():
        shapes = cell.shapes(li)
        if shapes.is_empty():
            continue
        info = layout.get_info(li)
        texts = sorted("%s %s" % (s.text_string, s.text_trans)
                       for s in shapes.each(kdb.Shapes.STexts))
        out[(info.layer, info.datatype)] = (kdb.Region(shapes), texts)
    return out


def differences(old, new, dbu):
    """The layers two contents differ on, as '8/0 0.120 um2' or '8/0 Texte'."""
    out = []
    for key in sorted(set(old) | set(new)):
        region_a, texts_a = old.get(key, (kdb.Region(), []))
        region_b, texts_b = new.get(key, (kdb.Region(), []))
        area = (region_a ^ region_b).area() * dbu * dbu
        if area or texts_a != texts_b:
            out.append("%d/%d %s" % (key[0], key[1], "%.3f um2" % area
                                     if area else "Texte"))
    return out


def frame(layout):
    """Every cell that is not a device cell: its shapes, and its instances
    by name, placement and cell."""
    out = {}
    for cell in layout.each_cell():
        if is_device(cell.name):
            continue
        insts = sorted((str(i.property(NAME)), str(i.dcplx_trans), i.na, i.nb,
                        str(i.a), str(i.b), layout.cell(i.cell_index).name)
                       for i in cell.each_inst())
        out[cell.name] = (content(layout, cell), insts)
    return out


def changed_cells(before, after, repointed, dbu):
    """Cells that are not what they were, the re-pointed instances aside."""
    out = []
    for name in sorted(set(before) | set(after)):
        if name not in before or name not in after:
            out.append(name)
            continue
        (shapes_a, insts_a), (shapes_b, insts_b) = before[name], after[name]
        expected = []
        for inst in insts_a:
            old_new = repointed.get((name, inst[0]))
            if old_new and inst[-1] == old_new[0]:
                inst = inst[:-1] + (old_new[1],)
            expected.append(inst)
        if sorted(expected) != insts_b or differences(shapes_a, shapes_b, dbu):
            out.append(name)
    return out


def load_generated():
    """The cells update_pcells.sh wrote, {name: (Layout, Cell)}."""
    cells = {}
    for path in sorted(glob.glob(os.path.join(CELLS, PREFIX + "*.gds"))):
        name = os.path.splitext(os.path.basename(path))[0]
        layout = kdb.Layout()
        layout.read(path)
        cell = layout.cell(name)
        # a device cell is flat; anything below it would need copying too
        if cell is None or cell.child_cells():
            raise SystemExit("%s: keine flache Zelle %s darin" % (path, name))
        cells[name] = (layout, cell)
    if not cells:
        raise SystemExit("keine Zellen in %s -- die erzeugt update_pcells.sh"
                         % CELLS)
    return cells


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="nur berichten, nichts schreiben")
    ap.add_argument("--gds", default=GDS,
                    help="die Layoutdatei (Standard: lvds_tx.gds)")
    args = ap.parse_args()

    generated = load_generated()
    # Which cell every device of the schematic is, by (subcircuit, name).
    wanted = {(sub.name, dev.name): dev.cellname
              for sub in parse().values() for dev in sub.devices}
    missing = sorted(set(wanted.values()) - set(generated))
    if missing:
        raise SystemExit("nicht erzeugt: %s" % ", ".join(missing))

    mtime = os.stat(args.gds).st_mtime
    layout = kdb.Layout(True)
    layout.read(args.gds)
    dbu = layout.dbu
    for name, (lib, _cell) in generated.items():
        if abs(lib.dbu - dbu) > 1e-12:
            raise SystemExit("%s: dbu %g, lvds_tx.gds hat %g"
                             % (name, lib.dbu, dbu))
    before = frame(layout)

    # 1. the geometry of every device cell
    replaced, same = [], 0
    for name, (lib, source) in sorted(generated.items()):
        cell = layout.cell(name)
        if cell is None:
            layout.create_cell(name).copy_shapes(source)
            replaced.append((name, "neu"))
            continue
        diffs = differences(content(layout, cell), content(lib, source), dbu)
        if not diffs:
            same += 1
            continue
        old = cell.dbbox()
        cell.clear_shapes()
        cell.copy_shapes(source)
        note = "ersetzt: " + ", ".join(diffs)
        if cell.dbbox() != old:
            note += "; GROESSE %s -> %s um" % (size(old), size(cell.dbbox()))
        replaced.append((name, note))

    # 2. every device instance, against the schematic
    placed, strangers, repoint = set(), [], []
    for parent in layout.each_cell():
        if is_device(parent.name):
            continue
        for inst in parent.each_inst():
            child = layout.cell(inst.cell_index).name
            if not is_device(child):
                continue
            key = (parent.name, inst.property(NAME))
            if key not in wanted:
                strangers.append((key, child))
                continue
            placed.add(key)
            if wanted[key] != child:
                repoint.append((inst, key, child))
    repointed, resized = {}, set()
    for inst, key, child in repoint:
        new = layout.cell(wanted[key])
        if new.dbbox() != layout.cell(child).dbbox():
            resized.add(key)
        inst.cell_index = new.cell_index()
        repointed[key] = (child, wanted[key])
    unplaced = sorted(k for k in wanted if k not in placed)

    # 3. device cells nothing uses any more, and that are not current
    dropped = sorted(c.name for c in layout.each_cell()
                     if is_device(c.name) and c.name not in generated
                     and c.parent_cells() == 0)
    for name in dropped:
        layout.delete_cell(layout.cell(name).cell_index())
    stale = sorted(c.name for c in layout.each_cell()
                   if is_device(c.name) and c.name not in generated)

    print("Zellen: %d unveraendert, %d neu oder ersetzt"
          % (same, len(replaced)))
    for name, note in replaced:
        print("  %-36s %s" % (name, note))
    if repointed:
        print("Instanzen auf eine neue Zelle umgehaengt (Lage und "
              "Orientierung bleiben):")
        for key, (old, new) in sorted(repointed.items()):
            note = ("; GROESSE jetzt %s um" % size(layout.cell(new).dbbox())
                    if key in resized else "")
            print("  %s/%s: %s -> %s%s" % (key + (old, new, note)))
    if unplaced:
        print("Im Schaltplan, aber nicht platziert (die Zelle liegt als "
              "Top-Zelle bereit):")
        for parent, inst in unplaced:
            print("  %s/%s: %s" % (parent, inst, wanted[(parent, inst)]))
    if strangers:
        print("Nicht im Schaltplan -- von Hand loeschen oder umbenennen:")
        for (parent, inst), child in sorted(strangers, key=str):
            print("  %s/%s: %s" % (parent, inst, child))
    if dropped:
        print("Geloescht, weil unbenutzt: %s" % ", ".join(dropped))
    if stale:
        print("Veraltet, aber noch verwendet: %s" % ", ".join(stale))
    if resized or any("GROESSE" in note for _n, note in replaced):
        print("Ein Device hat seine Groesse geaendert: Abstand zu den "
              "Nachbarn pruefen (make klayout-drc).")

    broken = changed_cells(before, frame(layout), repointed, dbu)
    if broken:
        raise SystemExit("ABBRUCH, nichts geschrieben -- ausser Devices "
                         "haette sich auch geaendert: %s" % ", ".join(broken))
    print("Alles andere unveraendert: %d Zellen geprueft." % len(before))

    if not (replaced or repointed or dropped):
        print("%s ist aktuell, nichts geschrieben."
              % os.path.basename(args.gds))
        return 0
    if args.dry_run:
        print("Probelauf, nichts geschrieben.")
        return 0
    if os.stat(args.gds).st_mtime != mtime:
        raise SystemExit("%s wurde waehrend des Laufs gespeichert -- nichts "
                         "geschrieben, bitte noch einmal" % args.gds)
    backups = os.path.join(os.path.dirname(os.path.abspath(args.gds)),
                           "backups")
    os.makedirs(backups, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.gds))[0]
    backup = os.path.join(backups, "%s_VOR_pcells_%s.gds" % (
        stem, datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")))
    shutil.copy2(args.gds, backup)
    # written aside and renamed, so nobody ever sees half a file
    os.makedirs(BUILD, exist_ok=True)
    tmp = os.path.join(BUILD, "swap.tmp.gds")
    layout.write(tmp)
    os.replace(tmp, args.gds)
    print("geschrieben: %s (vorher: %s)"
          % (os.path.relpath(args.gds, MACRO), os.path.relpath(backup, MACRO)))
    print("In KLayout: File > Reload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
