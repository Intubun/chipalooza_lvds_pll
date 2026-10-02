#!/usr/bin/env python3
"""Repair the DRC errors the PDK gencells leave behind.

rhigh, rppd: magic's own generator stops the metal1 cap 0.025 um past the
poly ContBar where rule CntB.h1 wants 0.05 um.  Extend it.

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
    sign = -1 if side == "s" else 1

    # A full-width bar spans the ring itself.  Measured against the ring's
    # own width, not the cell's: the well and ThickGateOx margin around it
    # is the same 0.3 um on every cell, and on a one-finger 0.8 um device
    # (M10) that alone puts the bar at 78 % of the cell width.
    taps = [r for layer in TAP_LAYERS for r in cell.layers.get(layer, [])]
    if not taps:
        return 0
    width = max(r[2] for r in taps) - min(r[0] for r in taps)

    middle = (lly + ury) / 2.0
    edges = []
    for layer in TAP_LAYERS:
        for (rllx, rlly, rurx, rury) in cell.layers.get(layer, []):
            if rurx - rllx < 0.95 * width:       # not the full-width bar
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
    # instance that moves: the cell could not be swapped into lvds_tx.gds
    # (swap_pcells.py) without shifting the device.  Putting the origin back
    # costs nothing and keeps the cell interchangeable with the one the
    # generator made before.
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


M2_GATE_RAIL = u(0.5)          # height of the metal2 rail m2_gate_rail draws


def m2_gate_rail(path):
    """Join the single gate contacts of a `conn_gates 0` device on metal2.

    `conn_gates 0 polycov 50` leaves one short poly contact per finger, with
    a wide metal1 gap between them through which source and drain reach the
    guard ring.  The generator's own `viagate` would lengthen every contact
    to the whole finger and close those gaps, and joins nothing on metal2.
    So the via1 are drawn here, the way the generator draws them over a
    `viagate 100` rail: a via1 area 4 units beyond the contact at either
    side, metal1 grown 1 unit more; metal1 stays one rectangle per contact.
    The metal2 rail is one plain rectangle of M2_GATE_RAIL over all of them,
    centred on the vias -- wider than the generator's 0.29/0.2 um rail, and
    with no notches to fill before connecting to it.  The cell has no other
    metal2.  All contacts must sit in one row (`topc 0` or `botc 0`).
    """
    cell = MagCell.read(path)
    pads = sorted(cell.layers.get("polycont", []))
    rows = {(p[1], p[3]) for p in pads}
    if len(pads) < 2 or len(rows) != 1:
        raise SystemExit("%s: _m2rail needs one row of single gate contacts, "
                         "found %d in %d rows" % (path, len(pads), len(rows)))
    y0, y1 = rows.pop()
    vy0, vy1 = y0 - 4, y1 + 4
    for (x0, _a, x1, _b) in pads:
        cell.paint("via1", x0, vy0, x1, vy1)
        cell.paint("metal1", x0 - 10, vy0 - 1, x1 + 10, vy1 + 1)
    centre = (vy0 + vy1) // 2
    cell.paint("metal2", pads[0][0], centre - M2_GATE_RAIL // 2,
               pads[-1][2], centre + M2_GATE_RAIL // 2)
    cell.write(path)
    return len(pads)


M2_SPACE = u(0.21)              # M2.b


def clip_gate_rail(path):
    """Cut the metal2 gate rail back from the source/drain straps.

    With `viasrc`/`viadrn 100` on a short finger the strap over the stripe
    runs to within 0.15 um of the `viagate 100` rail (M2.b wants 0.21) --
    the reason the straps are off by default.  Here every metal2 piece of
    the rail that comes nearer than M2.b to a strap is cut back, or dropped
    when nothing of it would be left; the via1 over the gate contacts is
    never touched, so the rail still reaches the gate.  Distances are
    euclidean, as in magic's `drc euclidean on` and the sign-off deck.
    """
    cell = MagCell.read(path)
    contacts = cell.layers.get("polycont", [])
    if not contacts:
        return 0
    band = (min(r[1] for r in contacts) - 20, max(r[3] for r in contacts) + 20)

    def in_band(r):
        return r[1] < band[1] and r[3] > band[0]

    straps = [r for lay in ("metal2", "via1") for r in cell.layers.get(lay, [])
              if not in_band(r)]
    vias = [r for r in cell.layers.get("via1", []) if in_band(r)]

    def gap(a, b):
        dx = max(b[0] - a[2], a[0] - b[2], 0)
        dy = max(b[1] - a[3], a[1] - b[3], 0)
        return (dx * dx + dy * dy) ** 0.5

    out, cut = [], 0
    for r in cell.layers.get("metal2", []):
        if not in_band(r) or all(gap(r, s) >= M2_SPACE for s in straps):
            out.append(r)
            continue
        x0, y0, x1, y1 = r
        for s in straps:
            if gap((x0, y0, x1, y1), s) >= M2_SPACE:
                continue
            if x1 <= s[0]:                       # rail piece left of the strap
                x1 = min(x1, s[0] - M2_SPACE)
            elif x0 >= s[2]:
                x0 = max(x0, s[2] + M2_SPACE)
            else:
                x1 = x0                          # straight under it: drop
        cut += 1
        if x1 > x0 and gap((x0, y0, x1, y1), min(straps, key=lambda s: gap((x0, y0, x1, y1), s))) >= M2_SPACE:
            out.append((x0, y0, x1, y1))
    if any(gap(v, s) < M2_SPACE for v in vias for s in straps):
        raise SystemExit("%s: a gate via1 sits nearer than M2.b to a strap; "
                         "cutting the rail cannot fix that" % path)
    # What is left of the rail can fall under M2.d (0.144 um2) on a short
    # finger.  Fill it out to its bounding box -- that grows it away from
    # the strap only, and leaves no notches -- if the box keeps M2.b.
    rail = [r for r in out if in_band(r)] + vias
    box = (min(r[0] for r in rail), min(r[1] for r in rail),
           max(r[2] for r in rail), max(r[3] for r in rail))
    if all(gap(box, s) >= M2_SPACE for s in straps):
        out = [r for r in out if not in_band(r)] + [box]
    cell.layers["metal2"] = out
    cell.write(path)
    return cut


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
    for path in sorted(glob.glob(os.path.join(celldir, "dev_rhigh_*.mag"))
                       + glob.glob(os.path.join(celldir, "dev_rppd_*.mag"))):
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
        # in by that row's height; push it back out (a cell without a ring
        # has nothing to push: the cell above keeps its taps away)
        for key, side in (("botc", "s"), ("topc", "n")):
            if dev.opts.get(key) == 0 and dev.opts.get("guard", 1) != 0:
                n = pad_guard_ring(path, side)
                print("patched %s: guard ring pushed %s by 0.19 um (%d shapes)"
                      % (cellname, side, n))
        if dev.opts.get("_cliprail"):
            n = clip_gate_rail(path)
            print("patched %s: %d metal2 gate-rail pieces cut back from the "
                  "straps" % (cellname, n))
        if dev.opts.get("_m2rail"):
            n = m2_gate_rail(path)
            print("patched %s: %d gate contacts joined on metal2"
                  % (cellname, n))
        if dev.opts.get("_open"):
            side = dev.opts["_open"]
            n = open_guard_ring(path, side)
            print("patched %s: guard ring opened to the %s (%d shapes removed)"
                  % (cellname, side, n))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cells")
