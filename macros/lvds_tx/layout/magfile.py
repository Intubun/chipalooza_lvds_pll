#!/usr/bin/env python3
"""Minimal reader/writer for magic .mag files.

Coordinates are normalised on the way in to a grid of 5 nm per unit -- the
`magscale 1 2` this technology uses when a cell holds sub-grid geometry, and
what `write` always emits.

A file's own grid is not fixed, and magic picks the coarsest one the cell
needs: drop the vias out of a device and it writes the cell with no
`magscale` line at all, meaning 10 nm per unit.  Read such a file as if it
were 5 nm and every coordinate comes out at half its true value, which is
silent and looks exactly like a layout that fits.
"""
from fractions import Fraction

UPUM = 200          # units per micron, after normalisation
_NATIVE = Fraction(1, 2)        # the magscale `write` emits


def u(x_um):
    """Microns -> internal units (rounded to the grid)."""
    return int(round(x_um * UPUM))


class MagCell:
    def __init__(self, name):
        self.name = name
        self.layers = {}        # layer -> list of (llx, lly, urx, ury)
        self.uses = []          # (childcell, instname, dx, dy)
        self.labels = []        # (layer, llx, lly, urx, ury, orient, text, port)
        self.props = {}

    # ---------------------------------------------------------------- read
    @classmethod
    def read(cls, path):
        cell = cls(None)
        section = None
        pending_use = None
        pending_label = None
        # no magscale line means 1 1, the coarse grid
        scale = _NATIVE.denominator // Fraction(1, 1).denominator
        with open(path) as fh:
            head = fh.read(4096)
        for line in head.splitlines():
            if line.startswith("magscale"):
                tok = line.split()
                given = Fraction(int(tok[1]), int(tok[2]))
                factor = given / _NATIVE
                if factor.denominator != 1:
                    raise ValueError("%s: magscale %s is finer than 5 nm"
                                     % (path, given))
                scale = int(factor)
                break

        def s(value):
            return int(value) * scale

        with open(path) as fh:
            for raw in fh:
                line = raw.rstrip("\n")
                if not line.strip():
                    continue
                tok = line.split()
                if line.startswith("<<"):
                    section = line.strip("<> \t")
                    continue
                if tok[0] == "magic" or tok[0] == "tech" or tok[0] == "magscale":
                    continue
                if tok[0] == "timestamp":
                    continue
                if tok[0] == "use":
                    pending_use = [tok[1], tok[2] if len(tok) > 2 else tok[1], 0, 0]
                    cell.uses.append(pending_use)
                    continue
                if tok[0] == "transform" and pending_use is not None:
                    pending_use[2] = s(tok[3])
                    pending_use[3] = s(tok[6])
                    continue
                if tok[0] == "box":
                    continue
                if tok[0] == "rect" and section not in (None, "end", "checkpaint"):
                    cell.layers.setdefault(section, []).append(
                        tuple(s(v) for v in tok[1:5]))
                    continue
                if tok[0] in ("rlabel", "flabel"):
                    # rlabel <layer> llx lly urx ury orient text
                    pending_label = [tok[1], s(tok[2]), s(tok[3]),
                                     s(tok[4]), s(tok[5]), int(tok[6]),
                                     " ".join(tok[7:]), None]
                    cell.labels.append(pending_label)
                    continue
                if tok[0] == "port" and pending_label is not None:
                    pending_label[7] = int(tok[1])
                    continue
                if tok[0] == "string":
                    cell.props[tok[1]] = " ".join(tok[2:])
                    continue
        return cell

    # --------------------------------------------------------------- write
    def paint(self, layer, llx, lly, urx, ury):
        if urx < llx:
            llx, urx = urx, llx
        if ury < lly:
            lly, ury = ury, lly
        self.layers.setdefault(layer, []).append((llx, lly, urx, ury))

    def place(self, child, inst, dx, dy):
        self.uses.append([child, inst, dx, dy])

    def label(self, layer, llx, lly, urx, ury, text, port=None):
        self.labels.append([layer, llx, lly, urx, ury, 0, text, port])

    def write(self, path):
        out = ["magic", "tech ihp-sg13cmos5l", "magscale 1 2", "timestamp 0"]
        for layer in sorted(self.layers):
            out.append("<< %s >>" % layer)
            for r in self.layers[layer]:
                out.append("rect %d %d %d %d" % r)
        for child, inst, dx, dy in self.uses:
            out.append("use %s  %s" % (child, inst))
            out.append("timestamp 0")
            out.append("transform 1 0 %d 0 1 %d" % (dx, dy))
            out.append("box 0 0 1 1")
        if self.labels:
            out.append("<< labels >>")
            for lay, llx, lly, urx, ury, orient, text, port in self.labels:
                out.append("rlabel %s %d %d %d %d %d %s"
                           % (lay, llx, lly, urx, ury, orient, text))
                if port is not None:
                    out.append("port %d nsew" % port)
        out.append("<< end >>")
        with open(path, "w") as fh:
            fh.write("\n".join(out) + "\n")


def bbox(cell, layers=None):
    """Bounding box over the given layers (all painted layers by default)."""
    xs, ys, xe, ye = None, None, None, None
    for lay, rects in cell.layers.items():
        if layers is not None and lay not in layers:
            continue
        for (a, b, c, d) in rects:
            xs = a if xs is None else min(xs, a)
            ys = b if ys is None else min(ys, b)
            xe = c if xe is None else max(xe, c)
            ye = d if ye is None else max(ye, d)
    return xs, ys, xe, ye
