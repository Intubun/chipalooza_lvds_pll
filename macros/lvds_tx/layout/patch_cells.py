#!/usr/bin/env python3
"""Repair the DRC errors the PDK gencells leave behind.

rhigh: magic's own generator stops the metal1 cap 0.025 um past the poly
ContBar where rule CntB.h1 wants 0.05 um.  Extend it.

narrow MOSFETs: on a 0.8 um finger the source/drain metal2 strap is
0.2 x 0.61 um = 0.122 um^2, under the 0.144 um^2 minimum-area rule M2.d.
The strap cannot grow taller without falling foul of the M2.b spacing to
the gate rail, so widen it instead -- the finger pitch leaves room.
"""
import glob
import os
import sys
from magfile import MagCell, bbox, u

ENC = 10        # 0.05 um in internal units
M2_MIN_AREA = 5760      # 0.144 um^2 in internal units^2
M2_HALF = 30            # widened half-width of a source/drain strap

# Height of the poly contact row `topc`/`botc` draws on a gate.  Drop the row
# and the generator pulls the guard ring in by exactly this much, which is
# what breaks the 0.43 um FET-to-tap spacing (pSD.i1/pSD.d1, pSD.j1/pSD.c1).
GATE_CONTACT_ROW = u(0.19)

# Layers that make up a guard ring, either flavour.
TAP_LAYERS = ("hvnsubdiff", "hvnsubdiffcont", "hvpsubdiff", "hvpsubdiffcont")


def patch_rhigh(path):
    c = MagCell.read(path)
    conts = c.layers.get("polycont", [])
    if not conts:
        return 0
    added = 0
    for (llx, lly, urx, ury) in list(conts):
        m1 = c.layers.get("metal1", [])
        # how far does metal1 reach above / below this contact bar?
        top = max([r[3] for r in m1 if r[0] < urx and r[2] > llx] or [ury])
        bot = min([r[1] for r in m1 if r[0] < urx and r[2] > llx] or [lly])
        if top < ury + ENC:
            c.paint("metal1", llx - ENC, top, urx + ENC, ury + ENC)
            added += 1
        if bot > lly - ENC:
            c.paint("metal1", llx - ENC, lly - ENC, urx + ENC, bot)
            added += 1
    if added:
        c.write(path)
    return added


def sd_columns(cell):
    """x centres of every source/drain diffusion column, including the
    unlabelled last one the generator leaves off."""
    xs = sorted({llx for lay, llx, lly, urx, ury, o, t, p in cell.labels
                 if t[0] in "DS" and "diffc" in lay})
    if len(xs) < 2:
        return xs
    pitch = xs[1] - xs[0]
    return xs + [xs[-1] + pitch]


def patch_narrow_straps(path):
    c = MagCell.read(path)
    cols = sd_columns(c)
    if not cols:
        return 0
    # Only the metal2 grows.  The via1 underneath keeps its width: it is
    # ringed by 0.005 um metal1 collars that the generator sized for it, and
    # widening the contact without them trips V1.c.
    changed = 0
    for x in cols:
        rects = [r for r in c.layers.get("metal2", [])
                 if abs((r[0] + r[2]) // 2 - x) <= 2 and (r[2] - r[0]) <= 48]
        via = [r for r in c.layers.get("via1", [])
               if abs((r[0] + r[2]) // 2 - x) <= 20 and (r[2] - r[0]) <= 48]
        if not rects:
            continue
        lo = min([r[1] for r in rects] + [r[1] for r in via])
        hi = max([r[3] for r in rects] + [r[3] for r in via])
        w = max(r[2] for r in rects) - min(r[0] for r in rects)
        if w * (hi - lo) >= M2_MIN_AREA:
            continue
        for r in rects:
            c.layers["metal2"].remove(r)
            c.layers["metal2"].append((x - M2_HALF, r[1], x + M2_HALF, r[3]))
        # cover the via1 body so the strap is one 0.30 um wide shape
        c.paint("metal2", x - M2_HALF, lo, x + M2_HALF, hi)
        changed += 1
    if changed:
        c.write(path)
    return changed


def pad_guard_ring(path, side, delta=GATE_CONTACT_ROW):
    """Push one side of the guard ring back out by `delta`.

    A true stretch: everything beyond the cut line moves, everything crossing
    it grows, everything inside stays put.  magic stores the ring as a stack
    of horizontal strips, so moving "the ring" rect by rect would tear the
    vertical bars apart; stretching keeps them whole.

    The cut goes just outside the full-width bar of the ring, which is the
    one band that holds nothing but the well and the two vertical bars -- the
    poly tips of the gate fingers reach further out than the bar does, and
    they belong to the FET, not to the ring.
    """
    cell = MagCell.read(path)
    _llx, lly, _urx, ury = bbox(cell)
    width = _urx - _llx
    sign = -1 if side == "s" else 1

    middle = (lly + ury) / 2.0
    edges = []
    for layer in TAP_LAYERS:
        for (rllx, rlly, rurx, rury) in cell.layers.get(layer, []):
            if rurx - rllx < 0.8 * width:        # not the full-width bar
                continue
            if sign < 0 and rury < middle:
                edges.append(rury)               # top edge of the bottom bar
            elif sign > 0 and rlly > middle:
                edges.append(rlly)               # bottom edge of the top bar
    if not edges:
        return 0
    # one unit outside the bar, so the bar itself counts as "beyond the
    # cut" and moves, rather than being stretched in place
    cut = (max(edges) + 1) if sign < 0 else (min(edges) - 1)

    moved = 0
    for layer, rects in cell.layers.items():
        out = []
        for (rllx, rlly, rurx, rury) in rects:
            if sign < 0:
                if rury <= cut:
                    rlly, rury = rlly - delta, rury - delta
                    moved += 1
                elif rlly < cut:
                    rlly -= delta
            else:
                if rlly >= cut:
                    rlly, rury = rlly + delta, rury + delta
                    moved += 1
                elif rury > cut:
                    rury += delta
            out.append((rllx, rlly, rurx, rury))
        cell.layers[layer] = out

    for label in cell.labels:
        if sign < 0 and label[4] <= cut:
            label[2] -= delta
            label[4] -= delta
        elif sign > 0 and label[2] >= cut:
            label[2] += delta
            label[4] += delta

    # Re-centre.  Padding one side leaves the cell the size it was but with
    # its origin off by half the padding, and an origin that moves is an
    # instance that moves: every .mag above would have to be rewritten, and
    # the same cell could not be swapped into a GDS without shifting the
    # block.  Putting the origin back costs nothing and keeps the cell
    # interchangeable with the one the generator made before.
    box = bbox(cell)
    shift = -((box[1] + box[3]) // 2)
    if shift:
        for layer, rects in cell.layers.items():
            cell.layers[layer] = [(a, b + shift, c, d + shift)
                                  for (a, b, c, d) in rects]
        for label in cell.labels:
            label[2] += shift
            label[4] += shift

    cell.write(path)
    return moved


def open_guard_ring(path, side):
    """Cut the guard ring open along one side, leaving a U.

    The generator draws the ring as a whole or not at all, so the only way
    to get an opening is to take the geometry away afterwards: the tap bar
    on that side and its metal go, the two vertical bars are clipped back to
    where the bar was, and the well stays as it is -- it has to keep
    enclosing the FET, and it is not what blocks a wire.

    The cut sits on the ring's inner edge, so everything belonging to the
    FET, the gate rail's metal1 included, is inside it and survives.
    """
    cell = MagCell.read(path)
    _llx, lly, _urx, ury = bbox(cell)
    width = _urx - _llx
    middle = (lly + ury) / 2.0
    sign = 1 if side == "n" else -1

    edges = []
    for layer in TAP_LAYERS:
        for (rllx, rlly, rurx, rury) in cell.layers.get(layer, []):
            if rurx - rllx < 0.8 * width:
                continue
            if sign > 0 and rlly > middle:
                edges.append(rlly)
            elif sign < 0 and rury < middle:
                edges.append(rury)
    if not edges:
        return 0
    cut = min(edges) if sign > 0 else max(edges)

    removed = 0
    for layer in TAP_LAYERS + ("metal1",):
        kept = []
        for (rllx, rlly, rurx, rury) in cell.layers.get(layer, []):
            if sign > 0:
                if rlly >= cut:
                    removed += 1
                    continue
                if rury > cut:
                    rury = cut
            else:
                if rury <= cut:
                    removed += 1
                    continue
                if rlly < cut:
                    rlly = cut
            kept.append((rllx, rlly, rurx, rury))
        if layer in cell.layers:
            cell.layers[layer] = kept

    # the bulk port lived on the bar that just went; put it back on what is
    # left of the ring, otherwise the cell has no B terminal to connect to
    if not any(l[6] == "B" and l[0] in TAP_LAYERS for l in cell.labels):
        pass
    cell.labels = [l for l in cell.labels
                   if not (l[6] == "B" and (l[3] >= cut if sign > 0
                                            else l[1] <= cut))]
    if not any(l[6] == "B" for l in cell.labels):
        conts = cell.layers.get("hvnsubdiffcont") or             cell.layers.get("hvpsubdiffcont") or []
        if conts:
            layer = ("hvnsubdiffcont" if cell.layers.get("hvnsubdiffcont")
                     else "hvpsubdiffcont")
            r = max(conts, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
            cell.label(layer, r[0], r[1], r[2], r[3], "B", port=0)

    cell.write(path)
    return removed


def main(celldir):
    for path in sorted(glob.glob(os.path.join(celldir, "dev_rhigh_*.mag"))):
        n = patch_rhigh(path)
        print("patched %s: %d metal1 caps" % (os.path.basename(path), n))
    for path in sorted(glob.glob(os.path.join(celldir, "dev_[np]_*.mag"))):
        n = patch_narrow_straps(path)
        if n:
            print("patched %s: %d widened metal2 straps"
                  % (os.path.basename(path), n))
    # Cells built with a gate contact left off: put the guard ring back where
    # a two-contact cell would have it.
    # Which cell needs which repair comes from the device table, not from
    # its file name.  The name used to carry the options, so globbing for
    # them worked -- until `_keepname` took them out of it, at which point a
    # cell would quietly miss its repair and come out 0.19 um short.
    from devices import parse, unique_devices

    for cellname, dev in unique_devices(parse()).items():
        path = os.path.join(celldir, cellname + ".mag")
        if not os.path.exists(path):
            continue
        # dropping a gate contact row lets the generator pull the guard ring
        # in by that row's height; push it back out
        for key, side in (("botc", "s"), ("topc", "n")):
            if dev.opts.get(key) == 0:
                n = pad_guard_ring(path, side)
                print("patched %s: guard ring pushed %s by 0.19 um (%d shapes)"
                      % (cellname, side, n))
        if dev.opts.get("_open"):
            side = dev.opts["_open"]
            n = open_guard_ring(path, side)
            print("patched %s: guard ring opened to the %s (%d shapes removed)"
                  % (cellname, side, n))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cells")
