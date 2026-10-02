#!/usr/bin/env python3
"""The floorplan of `lvds_tx`, written out as floorplan.json.

`build_placement.py` only knows how to keep positions and shelf-pack what is
new; it has no idea what a differential pair is.  This is where the
arrangement is actually decided, cell by cell, in rows -- and where it can
be read:

    Driver           H-bridge on a vertical axis: Out_p devices left, Out_n
                     devices right, every right-hand device the mirror image
                     of its left-hand twin.  Va on top, Vss at the bottom,
                     the tail current flowing straight down the middle.
    predriver_comp   5-transistor OTA: load, pair, tail stacked Va -> Vss.
    predriver_stage  two inverter chains facing away from each other, inputs
                     in the middle, outputs at the two ends, the latch pair
                     between them.  NMOS row on top, PMOS row below.
    predriver        the two comparators side by side (knm mirrored), Mref
                     between their tails, the stage underneath.
    lvds_tx          signal flow top to bottom: bias and data in at the top,
                     outputs at the bottom edge, where the pads are.  The
                     bias pre-mirrors are not in here: macros/iref_x15.

The arrangement is fixed here; how close things sit is not.  Every row is
pushed together, and every row pushed down onto what is below it, as far as
`spacing.py` allows -- which is as far as the sign-off deck allows: two pmos
share their nwell and ThickGateOx, two nmos their ThickGateOx, and a pmos
keeps 0.5 um from an nmos.  Where two cells meet, the devices that actually
face each other decide, not the cells' boxes.

Cells named in ROUTED are routed by hand in lvds_tx.gds.  Their arrangement
is not decided here but read back from that file, so the generator's copy
has the footprint of the real thing and the cells above are planned around
it.  Nothing is pushed into them.  The file is only read.

Run it after the leaf cells exist (build_cells.sh), then build_placement.py:

    python3 make_floorplan.py && python3 build_placement.py
"""
import os

from build_placement import (MARGIN, ROUTED, leaf_bbox, leaf_shape,
                             load_floorplan, placed_shapes, routed_shapes,
                             save_floorplan)
from devices import build_order, parse
from magfile import orient_box
from spacing import KIND, MERGE, Shape, moved, slide, violations

HERE = os.path.dirname(os.path.abspath(__file__))
USER_GDS = os.path.join(HERE, "lvds_tx.gds")

# The driver's outer edges, where Rp, Ctn1 and Cop stand on the left and
# their twins on the right.  The pre-driver fits between Cop and Con with
# its NWell and ThickGateOx exactly TGO.e from theirs (docs/layout.md, *The
# stage*), so the width is fixed by that, not by the rows.  M6_0|M6_1 used
# to set it; M6 is one block of half that width now.
DRIVER_WIDTH = 11504            # 57.52 um


class Block:
    """Instances at fixed positions relative to each other, and the shapes
    they occupy.  `members` are (inst, orient, x, y), with (x, y) where the
    lower-left of the turned child lands, relative to the block's own
    lower-left, which is (0, 0)."""

    def __init__(self, plan, members):
        self.members = members
        self.shapes = [s for inst, o, x, y in members
                       for s in plan.shapes_of(inst, o, x, y)]
        boxes = [plan.box_of(inst, o, x, y) for inst, o, x, y in members]
        llx = min(b[0] for b in boxes)
        lly = min(b[1] for b in boxes)
        if llx or lly:
            self.members = [(i, o, x - llx, y - lly)
                            for i, o, x, y in members]
            self.shapes = moved(self.shapes, -llx, -lly)
        self.w = max(b[2] for b in boxes) - llx
        self.h = max(b[3] for b in boxes) - lly


class Plan:
    """The placement of one cell.

    Coordinates are internal units (5 nm), rows centred on x = 0; the
    finished plan is shifted so that it starts at MARGIN, which is what
    build_placement.py assumes of every cell.
    """

    def __init__(self, name, boxes, child_shapes):
        self.name = name
        self.boxes = boxes              # instance -> bbox of its child cell
        self.child_shapes = child_shapes    # instance -> [Shape], child frame
        self.at = {}                    # instance -> [x, y, orient]
        self.shapes = []                # everything placed so far

    # -- geometry of one instance
    def box_of(self, inst, orient, x, y):
        llx, lly, urx, ury = orient_box(self.boxes[inst], orient)
        return (x, y, x + urx - llx, y + ury - lly)

    def shapes_of(self, inst, orient, x, y):
        return placed_shapes(self.child_shapes[inst], self.boxes[inst],
                             orient, x, y)

    def dim(self, inst, orient="r0"):
        x0, y0, x1, y1 = self.box_of(inst, orient, 0, 0)
        return x1 - x0, y1 - y0

    # -- building blocks
    def one(self, inst, orient="r0"):
        return Block(self, [(inst, orient, 0, 0)])

    def row(self, items, valign=0.0):
        """Blocks left to right, each pushed against the ones before it.

        `items` are instance names, (name, orient), Blocks, or any of those
        paired with an explicit height offset as (item, dy).  Shorter
        blocks sit at the bottom (valign 0), middle (0.5) or top (1)."""
        blocks = []
        for item in items:
            dy = None
            if isinstance(item, tuple) and len(item) == 2 \
                    and isinstance(item[1], int):
                item, dy = item
            if isinstance(item, str):
                item = self.one(item)
            elif isinstance(item, tuple):
                item = self.one(*item)
            blocks.append((item, dy))
        height = max(b.h for b, _ in blocks)
        members, shapes = [], []
        for block, dy in blocks:
            if dy is None:
                dy = int(round((height - block.h) * valign))
            here = moved(block.shapes, 0, dy)
            x = slide(shapes, here, "x") if shapes else 0
            shapes += moved(here, x, 0)
            members += [(i, o, bx + x, by + dy)
                        for i, o, bx, by in block.members]
        return Block(self, members)

    # -- putting blocks into the cell
    def put(self, block, x, y):
        for inst, o, bx, by in block.members:
            if inst in self.at:
                raise SystemExit("%s: %s placed twice" % (self.name, inst))
            self.at[inst] = [int(x + bx), int(y + by), o]
        self.shapes += moved(block.shapes, x, y)

    def drop(self, block, x):
        """Put a block at x, as low as the rules let it sink onto what is
        placed already.  Returns its y."""
        here = moved(block.shapes, x, 0)
        y = slide(self.shapes, here, "y") if self.shapes else 0
        self.put(block, x, y)
        return y

    def centred(self, block):
        return -block.w // 2

    def extent(self, insts=None):
        """(llx, lly, urx, ury) over the given (default: all) instances."""
        boxes = [self.box_of(i, o, x, y)
                 for i, (x, y, o) in self.at.items()
                 if insts is None or i in insts]
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes))

    def normalise(self):
        llx, lly, _, _ = self.extent()
        for entry in self.at.values():
            entry[0] += MARGIN - llx
            entry[1] += MARGIN - lly
        self.shapes = moved(self.shapes, MARGIN - llx, MARGIN - lly)

    def size(self):
        """The cell's extent as build_placement.py computes it."""
        _, _, urx, ury = self.extent()
        return (0, 0, urx + MARGIN, ury + MARGIN)

    def floorplan(self):
        return {inst: [x, y] + ([o] if o != "r0" else [])
                for inst, (x, y, o) in self.at.items()}


# ------------------------------------------------------------------- cells

def plan_predriver_comp(p):
    """Load, pair, tail from Va down to Vss.  The pair's right half (Mio,
    the output) is the mirror of its left (Mid, the diode side), so the two
    halves see the same surroundings.  The tail Mt is two halves, Mt_0
    under Mid and Mt_1 (mirrored) under Mio, finger on finger, their rings
    open towards the pair's (spacing.py: JOIN) -- each drain of Mt runs
    straight up in metal1 into the pair source above it.  The load Mld|Mlo
    is one cell (Mldo, devices.py: MERGED): one guard ring, one gate rail
    through all eight fingers, the two halves on a common centroid."""
    for spec in (["Mt_0", ("Mt_1", "m90")],
                 ["Mid", ("Mio", "m90")],
                 ["Mldo"]):
        b = p.row(spec, valign=0.5)
        p.drop(b, p.centred(b))


def plan_predriver_stage(p):
    """Columns left to right: the In_p chain running outwards (stage 2 at the
    left edge, where Out_p leaves), the latch pair, the In_n chain mirrored.

    The PMOS row and the NMOS row are pushed together each on its own, so
    that neighbours share their well: an NMOS is not exactly above its PMOS
    any more, but within a couple of um.  The PMOS row is flush at the
    bottom, where it meets the driver's Cc; the NMOS row flush at the top,
    where it meets the comparator tails -- a flush edge is what lets the
    rows above and below merge into it."""
    left = ["Mpp2", "Mpp1", "Mpp0", "Mpxn"]
    right = ["Mpxp", "Mpn0", "Mpn1", "Mpn2"]
    pmos = p.row(left + [(n, "m90") for n in right], valign=0.0)
    nmos = p.row([n.replace("Mp", "Mn", 1) for n in left]
                 + [(n.replace("Mp", "Mn", 1), "m90") for n in right],
                 valign=1.0)
    p.drop(pmos, p.centred(pmos))
    p.drop(nmos, p.centred(nmos))


def plan_driver(p):
    """The H-bridge on a vertical axis, Vss at the bottom, Va on top:

        Cop                        Con  load caps, standing up at the outer
        |                            |  corners, next to the pre-driver
        Cc                              (Va - cc_g, under the Va rail)
        Ctn1  M13   M2   M14  Ctn2      CMFB load either side of the tail;
                                        tail_n caps in the corners
        M5 | M4       Rc                switches, Out_p left, Out_n right;
                                        Rc (cmfb - cc_g) on Rn, right edge
        M1 | M3
        Rp       M6       Rn        tail, 31 fingers of 3.2 um
                M11 M9 M10 M12          CMFB pair (8 fingers each), the two
                                        references between, all under M6;
                                        the flanks down to the bottom edge

    M6 is one block on the axis, under both halves of the bridge.  M9, its
    reference, and M10 are single 0.8 um fingers, much lower than M6: in the
    M6 row that step would face a row above or below that can then no
    longer share its ThickGateOx with the row.  In the bottom row there is
    nothing below, so they sit there, flush with the top of M11/M12 and
    right under the middle of M6 -- M9 under the device it is the reference
    for, M10 next to the sources of M11/M12 it feeds.

    Cop/Con are gate capacitors, where only W*L counts: at 2 x 10 x 5 um,
    two halves on one shared ring, they are 7.3 um wide and 23.3 um tall,
    and stand in the corners above Cc,
    where the pre-driver -- 17 um narrower than the driver -- leaves room
    on either side of it.  The cell reaches up past Cc there; the parent
    fits the pre-driver in between."""
    a1 = p.row(["M11", "M9", "M10", ("M12", "m90")], valign=1.0)
    p.drop(a1, p.centred(a1))
    m6 = p.one("M6")
    p.drop(m6, p.centred(m6))

    # The sense resistor of each output, at the outer edge, beside M6 and
    # the CMFB row (which is no wider than M6 since M11/M12 have eight
    # fingers), down on the bottom edge.  The gap between it and M6 and the
    # switches is where the Out trunk runs.  (The cross caps Cxp/Cxn that
    # stood next to it were taken out of the schematic on 2026-09-30.)
    left = -DRIVER_WIDTH // 2
    right = left + DRIVER_WIDTH
    lf = p.one("Rp")
    rf = p.one("Rn", "m90")
    # Put, not dropped: with nothing under them, drop stops on the first
    # edge a neighbour offers (the top of M11), not on the floor.
    floor = p.extent(["M11"])[1]
    p.put(lf, left, floor)
    p.put(rf, right - rf.w, floor)

    for spec, valign in ((["M1", ("M3", "m90")], 0.0),
                         (["M5", ("M4", "m90")], 0.0),
                         # M2 is fingered to the height of M13/M14 (ng=20),
                         # so that both the switches below and Cc above
                         # can share their well with all three
                         (["M13", "M2", ("M14", "m90")], 0.5)):
        b = p.row(spec, valign=valign)
        p.drop(b, p.centred(b))

    # Rc, the resistor in series with Cc, lying down on top of Rn at the
    # right edge, in the free corner between M4/M14 and the edge, under Cc.
    # Not further left: the gap next to M4 below y 17 is where the Out_n
    # trunk and the drain straps of M4 run.  R1 (cmfb, left end) is reached
    # from the drain of M14, R2 (cc_g, right end) goes straight up into Cc.
    rc = p.one("Rc", "r90")
    p.drop(rc, right - rc.w)
    cc = p.one("Cc")
    cc_y = p.drop(cc, p.centred(cc))

    # Ctn1/Ctn2, the tail_n caps, in the two corners under Cc, hanging from
    # it: merged into Cc above (0.85 um) and keeping NW.b's 0.62 um from
    # M5/M13 and M14 beside them, which holds because all of them are one
    # nwell through Cc.  Below them the corners are free down to Rp and
    # Rc.  Put, not dropped: dropped they would stack on top of Cc.
    ctn1, ctn2 = p.one("Ctn1"), p.one("Ctn2")
    p.put(ctn1, left, cc_y - MERGE["p"][1] - ctn1.h)
    p.put(ctn2, right - ctn2.w, cc_y - MERGE["p"][1] - ctn2.h)

    # Cop/Con are two 10 um halves each (the PDK allows 10 um per finger),
    # stacked on one shared guard ring
    for half in ("Cop_0", "Cop_1"):
        p.drop(p.one(half), left)
    for half in ("Con_0", "Con_1"):
        b = p.one(half, "m90")
        p.drop(b, right - b.w)


def plan_predriver(p, comp):
    """The comparators left and right of the axis, knm the mirror of kpm, so
    both outputs arrive at the middle, right above the stage inputs.  Mref,
    the device that biases the two tails, sits between them on the axis, at
    the bottom of the row: level with the tails, whose gates are contacted
    at the bottom only (they stand finger on finger under their input pairs,
    see plan_predriver_comp)."""
    stage = p.one("stm")
    p.drop(stage, p.centred(stage))
    comps = p.row(["kpm", "Mref", ("knm", "m90")])
    p.drop(comps, p.centred(comps))


def plan_lvds_tx(p):
    """Signal flow top to bottom: data and bias in at the top edge, then the
    pre-driver, then the driver, whose outputs leave at the bottom edge
    towards the pads.  Iref_pd comes in on the axis straight into Mref,
    Iref_drv runs down the axis to M9.  The 1:15 pre-mirrors that feed both
    pins sit at the top level now (macros/iref_x15)."""
    for spec in (["drv"], ["pd"]):
        b = p.row(spec)
        p.drop(b, p.centred(b))


# ------------------------------------------------------------ routed cells

def adopt(cell, boxes):
    """The arrangement of a hand-routed cell, read from lvds_tx.gds, and
    the extent of its wiring in the same frame.

    Instances are matched by name (magic writes it into GDS property 61 and
    KLayout keeps it).  A leaf cell in that file need not have the origin
    the generator gives it today -- patch_cells.py re-centres cells -- so
    the match is on the centre of each device, not on its origin.
    """
    import klayout.db as kdb

    layout = kdb.Layout()
    layout.read(USER_GDS)
    top = layout.cell(cell)
    if top is None:
        raise SystemExit("%s not found in %s" % (cell, USER_GDS))
    unit = layout.dbu * 200                 # GDS units -> internal units
    plan = {}
    for inst in top.each_inst():
        name = inst.property(61)
        orient = str(inst.trans).split()[0]
        box = inst.bbox()                   # geometry, in `cell` coordinates
        cxx = (box.left + box.right) / 2.0 * unit
        cyy = (box.bottom + box.top) / 2.0 * unit
        llx, lly, urx, ury = orient_box(boxes[name], orient)
        plan[name] = [int(round(cxx - (urx - llx) / 2.0)),
                      int(round(cyy - (ury - lly) / 2.0)), orient]
    b = top.bbox()
    envelope = [int(round(v * unit)) for v in (b.left, b.bottom,
                                               b.right, b.top)]
    return plan, envelope


# -------------------------------------------------------------------- main

PLANS = {
    "predriver_comp": plan_predriver_comp,
    "predriver_stage": plan_predriver_stage,
    "Driver": plan_driver,
    "lvds_tx": plan_lvds_tx,
}


def main(top="lvds_tx"):
    subckts = parse()
    floorplan = load_floorplan()
    sizes = {}                  # cell name -> bbox, leaf or planned
    shapes = {}                 # cell name -> [Shape] in its own frame
    plans = {}
    for name in build_order(subckts, top):
        sub = subckts[name]
        boxes, child_shapes = {}, {}
        for dev in sub.devices:
            if dev.cellname not in sizes:
                sizes[dev.cellname] = leaf_bbox(dev.cellname)
                shapes[dev.cellname] = [leaf_shape(dev)]
            boxes[dev.name] = sizes[dev.cellname]
            child_shapes[dev.name] = shapes[dev.cellname]
        for inst in sub.instances:
            boxes[inst.name] = sizes[inst.cell]
            child_shapes[inst.name] = shapes[inst.cell]

        p = Plan(name, boxes, child_shapes)
        envelope = None
        if name in ROUTED:
            p.at, envelope = adopt(name, boxes)
            p.shapes = [s for i, (x, y, o) in p.at.items()
                        for s in p.shapes_of(i, o, x, y)]
        elif name == "predriver":
            plan_predriver(p, plans["predriver_comp"])
        else:
            PLANS[name](p)
        missing = set(boxes) - set(p.at)
        if missing:
            raise SystemExit("%s: not placed: %s"
                             % (name, ", ".join(sorted(missing))))
        llx, lly, _, _ = p.extent()
        p.normalise()
        if name not in ROUTED:
            groups = {i: p.shapes_of(i, o, x, y)
                      for i, (x, y, o) in p.at.items()}
            bad = violations(groups)
            if bad:
                raise SystemExit("%s: too close: %s" % (name, bad))
        plans[name] = p
        sizes[name] = p.size()
        entry = p.floorplan()
        own = p.shapes
        if envelope:
            envelope = [envelope[0] + MARGIN - llx, envelope[1] + MARGIN - lly,
                        envelope[2] + MARGIN - llx, envelope[3] + MARGIN - lly]
            entry["_envelope"] = envelope
            own = routed_shapes(own, envelope)
        shapes[name] = own
        floorplan[name] = entry
        _, _, w, h = sizes[name]
        print("%-16s %7.2f x %7.2f um  %8.1f um2%s"
              % (name, w / 200.0, h / 200.0, w * h / 40000.0,
                 "   (aus lvds_tx.gds)" if name in ROUTED else ""))
    # cells that left the hierarchy leave the floorplan too
    for gone in set(floorplan) - set(plans):
        del floorplan[gone]
    save_floorplan(floorplan)


if __name__ == "__main__":
    main()
