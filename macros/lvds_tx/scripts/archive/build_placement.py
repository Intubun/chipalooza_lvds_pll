#!/usr/bin/env python3
"""Place the devices and sub-blocks of `lvds_tx`, one magic cell per subcircuit.

This is the placement stage only: every subcircuit of the schematic becomes a
`.mag` cell that instantiates its children, and **nothing is routed**.  The
cells are therefore a frame to route into, not a working block -- an extract
of them finds each device on its own island with no nets between them.

The hierarchy mirrors the schematic exactly, so the cell a person opens in
magic is the cell they are looking at in xschem:

    lvds_tx
    +-- predriver
    |   +-- predriver_comp   (x2)
    |   +-- predriver_stage
    +-- Driver

Where each block goes is decided by make_floorplan.py and kept in
floorplan.json; this script builds the cells from it and checks every pair
of neighbours against spacing.py.  A block the floorplan does not know yet
is shelf-packed on top, with a gap that is legal between anything.
"""
import json
import math
import os
import sys

from devices import build_order, parse
from magfile import MagCell, bbox, orient_box, u
from spacing import KIND, Shape, turned, violations

HERE = os.path.dirname(os.path.abspath(__file__))
CELLDIR = os.path.join(HERE, "cells")

# Where the positions live once they have been decided.  Without this the
# packer re-derives every position from scratch on every run, so changing one
# device moves the whole block -- and there is no way to touch a device
# without redoing the layout.  With it, a rebuild keeps what is already
# placed and only finds room for what is new.
FLOORPLAN = os.path.join(HERE, "floorplan.json")

# Gap the shelf packer leaves between blocks it has to place on its own --
# a new block that floorplan.json does not know yet.  2 um is legal between
# any two kinds (spacing.py), so a fresh shelf never needs checking.
#
# The floorplan itself is not bound to it: make_floorplan.py pushes every
# block as close to its neighbours as spacing.py allows, and the check here
# holds it to the same rules.
GAP = u(2.0)

# Nothing around the edge of a cell.  It used to be 2 um, and with the gap
# between two cells on top that made 6 um between devices that are 0.5 um
# apart in the same cell; spacing between cells is now the parent's problem,
# decided from the devices that actually face each other.
MARGIN = 0

# Cells routed by hand in lvds_tx.gds.  Their arrangement is the one in that
# file (make_floorplan.py reads it back), and how close two of their devices
# sit is a decision taken there -- not something to flag here.  Empty since
# iref_x15, the one cell routed so far, became its own macro (macros/iref_x15)
# and left this hierarchy.
ROUTED = ()

# Preferred width/height of a packed cell, used only to break a tie, and the
# ratio past which a packing counts as unusable however small it is.  Blocks
# here differ in size by two orders of magnitude, so neither is a constraint
# on an individual block: one wider than the shelf simply gets a shelf of its
# own.
ASPECT = 1.4
EXTREME = 3.0


def _pack_at(items, target, gap):
    """First-fit shelves at a given target width, in the items' own order."""
    shelves, shelf, shelf_w = [], [], 0
    for item in items:
        w = item[1]
        if shelf and shelf_w + gap + w > target:
            shelves.append(shelf)
            shelf, shelf_w = [], 0
        shelf_w += (gap if shelf else 0) + w
        shelf.append(item)
    if shelf:
        shelves.append(shelf)

    placed, y, extent_x = {}, MARGIN, 0
    for shelf in shelves:
        x = MARGIN
        for key, w, h in shelf:
            placed[key] = (x, y)
            x += w + gap
        extent_x = max(extent_x, x - gap)
        y += max(h for _, _, h in shelf) + gap
    return placed, (extent_x + MARGIN, y - gap + MARGIN)


def shelf_pack(items, gap=GAP, aspect=ASPECT):
    """Pack (key, w, h) into shelves; return {key: (x, y)} and the extent.

    Items keep their given order, so the arrangement can be read against the
    schematic.  Only the width the shelves break at is searched for: every
    prefix of the item list is a candidate, which is the complete set of
    widths that produce a different set of shelves in a fixed order, and the
    smallest bounding box that is not absurdly long and thin wins.

    Picking a single target from the total area instead -- the obvious thing
    -- makes the cell jump in size whenever one block changes, because a
    block that no longer fits pushes a whole shelf down.
    """
    if not items:
        return {}, (0, 0)
    widest = max(w for _, w, h in items)

    candidates, cumulative = set(), 0
    for i, (_, w, _h) in enumerate(items):
        cumulative += w + (gap if i else 0)
        candidates.add(max(cumulative, widest))

    # Area decides, shape only rules candidates out.  Weighing the two
    # against each other does not work: a shape term strong enough to reject
    # the single column is also strong enough to accept a packing half again
    # as large, which is the opposite of what the search is for.
    def measure(target):
        _placed, (width, height) = _pack_at(items, target, gap)
        return width * height, width / float(height)

    usable = [t for t in candidates
              if EXTREME > measure(t)[1] > 1.0 / EXTREME]
    if usable:
        return _pack_at(items, min(usable, key=lambda t: measure(t)[0]), gap)
    # nothing in the band: take whatever comes closest to the target shape
    return _pack_at(items, min(candidates,
                               key=lambda t: abs(math.log(measure(t)[1]
                                                          / aspect))), gap)


def load_floorplan():
    if not os.path.exists(FLOORPLAN):
        return {}
    with open(FLOORPLAN) as fh:
        return json.load(fh)


def save_floorplan(data):
    with open(FLOORPLAN, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        print(file=fh)


def placed_shapes(base, box, orient, x, y):
    """A child's shapes in the parent: turned, then moved so that the
    lower-left of the turned box lands on (x, y) -- how `place` puts it."""
    llx, lly, _, _ = orient_box(box, orient)
    out = []
    for s in base:
        a, b, c, d = orient_box((s.x0, s.y0, s.x1, s.y1), orient)
        out.append(s._replace(x0=a - llx + x, y0=b - lly + y,
                              x1=c - llx + x, y1=d - lly + y,
                              opens=turned(s.opens, orient)))
    return out


def leaf_shape(dev):
    """The one Shape a leaf device cell is to the placer: its box, its kind,
    and the sides its guard ring is open on (patch_cells.py: _open)."""
    return Shape(*leaf_bbox(dev.cellname), kind=KIND[dev.model], merge=True,
                 opens=dev.opts.get("_open", ""))


def routed_shapes(shapes, envelope):
    """A hand-routed cell as its neighbours see it: its devices, never
    merged with anything (the cell is not ours to lean into), and the
    extent of its wiring as metal."""
    out = [s._replace(merge=False) for s in shapes]
    if envelope:
        out.append(Shape(*envelope, kind="c", merge=False))
    return out


def orientation(entry):
    """The orientation a floorplan entry asks for: [x, y] or [x, y, "m90"]."""
    return entry[2] if len(entry) > 2 else "r0"


def reuse(items, saved):
    """Keep the positions we already had; shelf-pack the rest on top.

    Anything already in the floorplan stays exactly where it is, so a device
    that only changed on the inside does not move a single instance.  New
    blocks go on a fresh shelf above everything, which is never the prettiest
    answer but is always a legal one, and is easy to see and fix by hand.

    `items` carry the size each block has in the orientation it is placed
    in, so a block turned by 90 degrees is checked with its width and height
    swapped.
    """
    sizes = {inst: (w, h) for inst, w, h in items}
    placed = {inst: tuple(saved[inst][:2]) for inst, _w, _h in items
              if inst in saved}
    fresh = [it for it in items if it[0] not in placed]

    if fresh:
        top = max((y + sizes[i][1] for i, (x, y) in placed.items()),
                  default=MARGIN - GAP)
        more, _extent = shelf_pack(fresh)
        for inst, (x, y) in more.items():
            placed[inst] = (x, y + top + GAP - MARGIN)

    width = max(x + sizes[i][0] for i, (x, y) in placed.items()) + MARGIN
    height = max(y + sizes[i][1] for i, (x, y) in placed.items()) + MARGIN
    return placed, (width, height), sizes


def leaf_bbox(cellname):
    """Bounding box of a generated leaf cell, in internal units."""
    path = os.path.join(CELLDIR, cellname + ".mag")
    if not os.path.exists(path):
        raise SystemExit("missing leaf cell %s -- run build_cells.sh first"
                         % path)
    box = bbox(MagCell.read(path))
    if box[0] is None:
        raise SystemExit("leaf cell %s paints nothing" % cellname)
    return box


def build(top="lvds_tx", check=False, replace=False):
    """Write one .mag per subcircuit, or with `check` only say whether the
    ones on disk still match what the leaf cells now imply.

    The check exists because regenerating the leaf cells alone is the cheap
    move -- it leaves the placement, and anything drawn into the GDS by
    hand, alone -- but it is only safe while the cells still have the same
    names and the same sizes.  Change either and the cells above are stale:
    an instance points at a name that is gone, or two blocks that used to
    clear each other now overlap.
    """
    subckts = parse()
    boxes = {}          # cell name -> (llx, lly, urx, ury)
    shapes = {}         # cell name -> [Shape], for the spacing check
    report = []
    stale = []
    floorplan = {} if replace else load_floorplan()
    clashes = []

    for name in build_order(subckts, top):
        sub = subckts[name]
        children = ([(d.name, d.cellname) for d in sub.devices]
                    + [(i.name, i.cell) for i in sub.instances])
        for d in sub.devices:
            if d.cellname not in shapes:
                shapes[d.cellname] = [leaf_shape(d)]

        saved = {} if replace else floorplan.get(name, {})
        orients = {inst: orientation(saved[inst]) if inst in saved else "r0"
                   for inst, _child in children}

        items = []
        for inst, child in children:
            if child not in boxes:
                boxes[child] = leaf_bbox(child)
            llx, lly, urx, ury = orient_box(boxes[child], orients[inst])
            items.append((inst, urx - llx, ury - lly))

        if saved:
            placed, (width, height), sizes = reuse(items, saved)
        else:
            placed, (width, height) = shelf_pack(items)
        groups = {inst: placed_shapes(shapes[child], boxes[child],
                                      orients[inst], *placed[inst])
                  for inst, child in children}
        if name not in ROUTED:
            for pair in violations(groups):
                clashes.append((name,) + pair)
        own = [s for g in groups.values() for s in g]
        if name in ROUTED:
            own = routed_shapes(own, saved.get("_envelope"))
        shapes[name] = own
        # keys starting with "_" are notes for this script, not instances
        floorplan[name] = dict(
            [(k, v) for k, v in saved.items() if k.startswith("_")]
            + [(i, list(p) + ([orients[i]] if orients[i] != "r0" else []))
               for i, p in placed.items()])

        cell = MagCell(name)
        for inst, child in children:
            llx, lly, _, _ = orient_box(boxes[child], orients[inst])
            x, y = placed[inst]
            # turn the child first, then translate so its lower-left --
            # the lower-left of the turned box -- lands on (x, y)
            cell.place(child, inst, x - llx, y - lly, orients[inst])

        path = os.path.join(HERE, name + ".mag")
        if check:
            reason = _differs(path, cell)
            if reason:
                stale.append((name, reason))
        else:
            cell.write(path)

        boxes[name] = (0, 0, width, height)
        report.append((name, len(children), width, height))

    if clashes:
        print("Blöcke liegen zu dicht beieinander (Regeln: spacing.py):")
        for cell, a, b in clashes:
            print("  %-18s %s <-> %s" % (cell, a, b))
        print("")
        print("Neu anordnen mit: make layout-floorplan")
        return clashes

    if not check:
        save_floorplan(floorplan)

    if check:
        if stale:
            print("Die Zellen oberhalb passen NICHT mehr:")
            for name, reason in stale:
                print("  %-18s %s" % (name, reason))
            print("")
            print("Die Platzierung muss neu gebaut werden: run_all.sh")
            return stale
        print("Die Zellen oberhalb passen unveraendert - "
              "%d Zellen geprueft, kein Neubau noetig." % len(report))
        return []

    print("%-18s %8s %12s %12s %12s"
          % ("cell", "blocks", "width/um", "height/um", "area/um2"))
    for name, n, width, height in report:
        w_um, h_um = width / 200.0, height / 200.0
        print("%-18s %8d %12.2f %12.2f %12.1f"
              % (name, n, w_um, h_um, w_um * h_um))
    return report


def _differs(path, wanted):
    """Why the .mag on disk is not what `wanted` would write, or None."""
    if not os.path.exists(path):
        return "fehlt"
    on_disk = MagCell.read(path)
    have = sorted(tuple(use) for use in on_disk.uses)
    want = sorted(tuple(use) for use in wanted.uses)
    if [u[0] for u in have] != [u[0] for u in want]:
        gone = set(u[0] for u in have) - set(u[0] for u in want)
        new = set(u[0] for u in want) - set(u[0] for u in have)
        bits = []
        if gone:
            bits.append("verweist noch auf " + ", ".join(sorted(gone)))
        if new:
            bits.append("braucht jetzt " + ", ".join(sorted(new)))
        return "; ".join(bits)
    if have != want:
        moved = sum(1 for a, b in zip(have, want) if a != b)
        return "%d Instanzen muessten sich verschieben" % moved
    return None


if __name__ == "__main__":
    flags = ("--check", "--replace")
    args = [a for a in sys.argv[1:] if a not in flags]
    build(args[0] if args else "lvds_tx",
          check="--check" in sys.argv, replace="--replace" in sys.argv)
