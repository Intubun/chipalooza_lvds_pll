#!/usr/bin/env python3
"""Place the devices and sub-blocks of `lvds_tx`, one magic cell per subcircuit.

This is the placement stage only: every subcircuit of the schematic becomes a
`.mag` cell that instantiates its children, and **nothing is routed**.  The
cells are therefore a frame to route into, not a working block -- an extract
of them finds each device on its own island with no nets between them.

The hierarchy mirrors the schematic exactly, so the cell a person opens in
magic is the cell they are looking at in xschem:

    lvds_tx
    +-- iref_x15        (x2)
    +-- predriver
    |   +-- predriver_comp   (x2)
    |   +-- predriver_stage
    +-- Driver

Blocks are shelf-packed in netlist order at a target aspect ratio, with a
uniform gap left between neighbours for the routing that comes next.  Netlist
order keeps the arrangement readable against the schematic; it is not a
floorplan, and any device can be moved later without touching this script's
callers.
"""
import json
import math
import os
import sys

from devices import build_order, parse
from magfile import MagCell, bbox, u

HERE = os.path.dirname(os.path.abspath(__file__))
CELLDIR = os.path.join(HERE, "cells")

# Where the positions live once they have been decided.  Without this the
# packer re-derives every position from scratch on every run, so changing one
# device moves the whole block -- and there is no way to touch a device
# without redoing the layout.  With it, a rebuild keeps what is already
# placed and only finds room for what is new.
FLOORPLAN = os.path.join(HERE, "floorplan.json")

# Gap left between neighbouring blocks, and around the edge of a cell.  Wide
# enough for the nwell and tap spacing between two guard rings, plus a few
# tracks, so the placement stays DRC clean before anything is routed.
#
# It was 4 um, which on a leaf cell of five devices turned out to be the
# single largest term in the cell's area -- predriver_comp was 35% device
# and 65% gap.  Raise it again if the routing turns out to need the room;
# nothing else depends on the value.
GAP = u(2.0)
MARGIN = u(2.0)

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


def collisions(placed, sizes, gap=GAP):
    """Pairs of blocks closer than `gap`, after keeping old positions."""
    boxes = []
    for inst, (x, y) in placed.items():
        w, h = sizes[inst]
        boxes.append((inst, x - gap // 2, y - gap // 2,
                      x + w + gap // 2, y + h + gap // 2))
    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
                hits.append((a[0], b[0]))
    return hits


def reuse(items, saved):
    """Keep the positions we already had; shelf-pack the rest on top.

    Anything already in the floorplan stays exactly where it is, so a device
    that only changed on the inside does not move a single instance.  New
    blocks go on a fresh shelf above everything, which is never the prettiest
    answer but is always a legal one, and is easy to see and fix by hand.
    """
    sizes = {inst: (w, h) for inst, w, h in items}
    placed = {inst: tuple(saved[inst]) for inst, _w, _h in items
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
    report = []
    stale = []
    floorplan = {} if replace else load_floorplan()
    clashes = []

    for name in build_order(subckts, top):
        sub = subckts[name]
        children = ([(d.name, d.cellname) for d in sub.devices]
                    + [(i.name, i.cell) for i in sub.instances])

        items = []
        for inst, child in children:
            if child not in boxes:
                boxes[child] = leaf_bbox(child)
            llx, lly, urx, ury = boxes[child]
            items.append((inst, urx - llx, ury - lly))

        saved = floorplan.get(name, {})
        if saved and not replace:
            placed, (width, height), sizes = reuse(items, saved)
            for pair in collisions(placed, sizes):
                clashes.append((name,) + pair)
        else:
            placed, (width, height) = shelf_pack(items)
        floorplan[name] = {i: list(p) for i, p in placed.items()}

        cell = MagCell(name)
        for inst, child in children:
            llx, lly, _, _ = boxes[child]
            x, y = placed[inst]
            # translate so the child's own lower-left lands on (x, y)
            cell.place(child, inst, x - llx, y - lly)

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
        print("Blöcke liegen zu dicht beieinander, weil eine Zelle gewachsen ist:")
        for cell, a, b in clashes:
            print("  %-18s %s <-> %s" % (cell, a, b))
        print("")
        print("Neu anordnen mit: make layout-replace")
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
    have = sorted((c, i, dx, dy) for c, i, dx, dy in on_disk.uses)
    want = sorted((c, i, dx, dy) for c, i, dx, dy in wanted.uses)
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
