#!/usr/bin/env python3
"""Die Verbindungen von lvds_tx als Text -- das Gegenstueck zu
layout_ascii.txt, das die Platzierung zeigt.

    python3 ascii_routing.py > routing_ascii.txt                 # alles
    python3 ascii_routing.py predriver > routing_predriver.txt   # nur der Predriver
    (im Container: braucht klayout.db)

Drei Teile:

1. lvds_tx: die Signale zwischen den Bloecken, wie Abschnitt 2 von
   ROUTING.md sie plant.
2. predriver: die Verdrahtung, die route_predriver.py zeichnet.  Sie wird
   hier im Speicher auf lvds_tx_gen.gds gerechnet (das Skript ist zur Zeit
   aus dem Flow genommen, keine Datei wird geschrieben), die Netze werden aus
   der Geometrie extrahiert und ueber die Transistor-Anschluesse nach dem
   Schaltplan benannt -- die Karte zeigt, was wirklich verbunden ist.
3. Driver: die geplante Verdrahtung aus ROUTING.md Abschnitt 3.  Noch nicht
   gezeichnet, nur der Plan, von Hand eingetragen.
"""
import os
import re
import sys

import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ascii_layout  # noqa: E402
import route_predriver as rp  # noqa: E402
from devices import parse  # noqa: E402

GDS = os.path.join(HERE, "lvds_tx_gen.gds")


class Grid:
    """A character grid over a cell, x to the right, y up (um)."""

    def __init__(self, w, h, sx, sy):
        self.sx, self.sy = sx, sy
        self.W, self.H = int(w / sx) + 1, int(h / sy) + 1
        self.g = [[" "] * self.W for _ in range(self.H)]
        self.owner = [[None] * self.W for _ in range(self.H)]

    def span(self, x0, y0, x1, y1):
        """Grid cells a box overlaps."""
        c0, c1 = int(x0 / self.sx + 1e-6), int(x1 / self.sx - 1e-6)
        r0, r1 = int(y0 / self.sy + 1e-6), int(y1 / self.sy - 1e-6)
        for r in range(max(r0, 0), min(r1, self.H - 1) + 1):
            for c in range(max(c0, 0), min(c1, self.W - 1) + 1):
                yield self.H - 1 - r, c

    def _frame(self, x0, y0, x1, y1):
        c0, c1 = int(x0 / self.sx + 0.5), int(x1 / self.sx - 0.5)
        rb, rt = self.H - 1 - int(y0 / self.sy + 0.5), self.H - 1 - int(y1 / self.sy - 0.5)
        return c0, c1, rt, rb

    def outline(self, x0, y0, x1, y1):
        """A light device frame."""
        c0, c1, rt, rb = self._frame(x0, y0, x1, y1)
        for c in range(c0, c1 + 1):
            for r in (rt, rb):
                if 0 <= r < self.H and 0 <= c < self.W:
                    self.g[r][c] = "."
        for r in range(rt, rb + 1):
            for c in (c0, c1):
                if 0 <= r < self.H and 0 <= c < self.W:
                    self.g[r][c] = ":"

    def label(self, x0, y0, x1, y1, text):
        """The device name inside its frame, on the row nearest the middle
        where it fits on empty cells -- never over a wire.  Left out if
        there is no such row."""
        c0, c1, rt, rb = self._frame(x0, y0, x1, y1)
        mid = (rt + rb) // 2
        for r in sorted(range(rt + 1, rb), key=lambda r: abs(r - mid)):
            for c in sorted(range(c0 + 1, c1 - len(text) + 1),
                            key=lambda c: abs(c - (c0 + c1 - len(text)) // 2)):
                if all(self.g[r][c + j] == " " for j in range(len(text))):
                    for j, ch in enumerate(text):
                        self.g[r][c + j] = ch
                    return

    def polyline(self, pts):
        """The cells a zero-width wire through `pts` (um) runs along, one
        cell wide: each point rounded to its nearest cell."""
        out = []
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            ca, cb = int(round(xa / self.sx)), int(round(xb / self.sx))
            ra, rb = int(round(ya / self.sy)), int(round(yb / self.sy))
            if ra == rb:
                cells = [(ra, c) for c in range(min(ca, cb), max(ca, cb) + 1)]
            else:
                cells = [(r, ca) for r in range(min(ra, rb), max(ra, rb) + 1)]
            out += [(self.H - 1 - r, c) for r, c in cells
                    if 0 <= r < self.H and 0 <= c < self.W]
        return out

    def paint(self, cells, ch, upper):
        """Mark cells for a net: `ch` on the lower layer, `ch.upper()` on
        the upper ones.  Two different nets on the upper layers in one
        cell show as '+' (they cross on different layers)."""
        mark = ch.upper() if upper else ch
        for r, c in cells:
            old = self.owner[r][c]
            if old is None or old[1] < upper or (old[0] == ch and old[1] == upper):
                self.g[r][c], self.owner[r][c] = mark, (ch, upper)
            elif upper and old[1] and old[0] != ch:
                self.g[r][c] = "+"

    def text(self, title):
        out = [title]
        rl = [" "] * (self.W + 8)
        for i in range(0, int(self.W * self.sx) + 1, 5):
            for j, d in enumerate(str(i)):
                c = int(round(i / self.sx)) + j
                if c < len(rl):
                    rl[c] = d
        out.append("      " + "".join(rl).rstrip() + "  x/um")
        for r in range(self.H):
            y = (self.H - 1 - r) * self.sy
            near = round(y / 5) * 5
            tag = "%5.0f " % near if abs(y - near) < self.sy / 2 else "      "
            out.append(tag + "".join(self.g[r]).rstrip())
        return "\n".join(out)


# ======================================================================
# 1. lvds_tx: between the blocks -- the plan in ROUTING.md section 2
# ======================================================================
def part_top():
    text = open(os.path.join(HERE, "ROUTING.md"), encoding="utf-8").read()
    sec = text.split("## 2.", 1)[1].split("\n## ", 1)[0]
    drawing = re.search(r"```\n(.*?)```", sec, re.S).group(1).rstrip()
    return "\n".join([
        "=" * 100,
        "1. lvds_tx -- Verbindungen zwischen den Bloecken (Plan, ROUTING.md Abschnitt 2)",
        "=" * 100,
        "",
        drawing,
        "",
        "o = Anschluss, + = Abzweig/Ecke; Linien, die sich nur kreuzen, liegen auf",
        "verschiedenen Lagen.  Nichts davon ist gezeichnet."])


# ======================================================================
# 2. predriver: the wiring route_predriver.py draws, extracted
# ======================================================================
EXTRACT = [("poly", (5, 0)), ("cont", (6, 0)), ("M1", (8, 0)), ("V1", (19, 0)),
           ("M2", (10, 0)), ("V2", (29, 0)), ("M3", (30, 0)), ("V3", (49, 0)),
           ("M4", (50, 0)), ("TV1", (125, 0)), ("TM1", (126, 0))]

# net (named after the schematic, as seen from `predriver`) -> map letter,
# and what it is.  Lower case on metal2, upper case on metal3/metal4.
PD_NETS = [
    ("D_n", "n", "Pin D_n"),
    ("D_p", "p", "Pin D_p"),
    ("Iref", "r", "Pin Iref (Iref_pd)"),
    ("net1", "i", "kpm.Out = Eingang In_p der Stage"),
    ("net2", "j", "knm.Out = Eingang In_n der Stage"),
    ("In_p", "o", "Stage Out_p = Pin In_p (zum Driver)"),
    ("In_n", "q", "Stage Out_n = Pin In_n (zum Driver)"),
    ("kpm.net1", "a", "kpm intern: Last-Diode / Mid Drain"),
    ("kpm.net2", "b", "kpm intern: Tail-Drain / Paar-Sources"),
    ("knm.net1", "c", "knm intern: Last-Diode / Mid Drain"),
    ("knm.net2", "d", "knm intern: Tail-Drain / Paar-Sources"),
    ("stm.net1", "e", "Stage: Spalte 3 D -> Spalte 2 G"),
    ("stm.net2", "f", "Stage: Spalte 2 D, Spalte 4 D -> Spalte 1 G, Spalte 5 G"),
    ("stm.net3", "g", "Stage: Spalte 6 D -> Spalte 7 G"),
    ("stm.net4", "h", "Stage: Spalte 7 D, Spalte 5 D -> Spalte 8 G, Spalte 4 G"),
]
SUPPLY = ("Va", "Vss")


def leaf_devices(ly):
    """[(path, Dev in the predriver frame)] for every transistor below
    `predriver`; path is () for its own devices, ("kpm",) etc. below."""
    pd = rp.Cell(ly, "predriver")
    out = []
    for name, inst in pd.insts.items():
        child = ly.cell(inst.cell_index)
        if child.name.startswith("dev_"):
            out.append(((), pd.dev(name)))
            continue
        sub = rp.Cell(ly, child.name)
        t = inst.dcplx_trans
        for dname in sub.insts:
            d = sub.dev(dname)
            d.stripes = {k: [t * b for b in v] for k, v in d.stripes.items()}
            # (bottom, top), None where a side has no rail; the sub-blocks
            # are placed unturned or mirrored in x, so the order holds
            d.rails = tuple(t * b if b is not None else None for b in d.rails)
            d.box = t * d.box
            out.append(((name,), d))
    return out


def terminals(subs, path, dev):
    """[(layer, point, schematic net, label)] to probe on one transistor.
    The net is named as `predriver` sees it: a port of a sub-block becomes
    the net it is wired to.  A MERGED cell (devices.py) has its shared
    source on the even stripes and each member's drain on its own odd
    ones."""
    cell = "predriver" if not path else \
        next(i.cell for i in subs["predriver"].instances if i.name == path[0])
    sd = next(d for d in subs[cell].devices if d.name == dev.name)
    prefix = "".join(q + "." for q in path)

    def resolve(net):
        if not path:
            return net
        inst = next(i for i in subs["predriver"].instances if i.name == path[0])
        ports = subs[cell].ports
        if net in ports:
            return inst.nets[ports.index(net)]
        return "%s.%s" % (path[0], net)

    def centre(b):
        return kdb.DPoint((b.left + b.right) / 2, (b.bottom + b.top) / 2)

    members = getattr(sd, "members", None)
    who = "/".join(m for m, _ in members) if members else dev.name
    rail = dev.rails[1] or dev.rails[0]     # one-sided cells have only one
    out = [("M2", centre(rail), resolve(sd.nets[1]), "%s%s G" % (prefix, who))]
    if members:                               # MOS nets: D G S B
        out.append(("M1", centre(dev.stripes["D"][0]), resolve(sd.nets[2]),
                    "%s%s S" % (prefix, who)))
        drain = dict(members)
        for stripe, m in zip(dev.stripes["S"], sd.drains):
            out.append(("M1", centre(stripe), resolve(drain[m]), "%s%s D" % (prefix, m)))
    else:
        d_st, s_st = "DS" if dev.name not in rp.SOURCE_ON_D else "SD"
        out.append(("M1", centre(dev.stripes[d_st][0]), resolve(sd.nets[0]),
                    "%s%s D" % (prefix, dev.name)))
        out.append(("M1", centre(dev.stripes[s_st][0]), resolve(sd.nets[2]),
                    "%s%s S" % (prefix, dev.name)))
    return out


def part_predriver(heading="2. predriver -- Verdrahtung (route_predriver.py)"):
    ly = kdb.Layout()
    ly.read(GDS)
    rp.route_predriver(ly)                    # in memory only
    devs = leaf_devices(ly)
    pins = []                                 # the block's own, before flattening
    for lay in ((30, 25), (126, 25)):
        li = ly.find_layer(*lay)
        for s in ly.cell("predriver").shapes(li).each() if li is not None else []:
            p = s.text.trans.disp
            pins.append("%s (%.2f, %.2f)" % (s.text.string, p.x * ly.dbu, p.y * ly.dbu))
    # Flat, so that kpm's and knm's internal nets are two nets, each in the
    # predriver's frame -- extracted hierarchically they are one net of
    # predriver_comp, in its own frame.
    top = ly.cell("predriver")
    top.flatten(True)
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
    R = {name: l2n.make_layer(ly.layer(*ld), name) for name, ld in EXTRACT}
    chain = [name for name, _ in EXTRACT]
    for name in chain:
        l2n.connect(R[name])
    for a, b in zip(chain, chain[1:]):
        l2n.connect(R[a], R[b])
    l2n.extract_netlist()

    # name every extracted net by the transistor terminals it reaches
    subs = parse()
    names, terms, nets = {}, {}, {}
    for path, d in devs:
        for layer, p, sname, label in terminals(subs, path, d):
            net = l2n.probe_net(R[layer], p)
            key = net.cluster_id
            nets[key] = net
            names.setdefault(key, set()).add(sname)
            terms.setdefault(key, []).append(label)
    problems = ["  Kurzschluss? ein Netz traegt %s" % ", ".join(sorted(v))
                for v in names.values() if len(v) > 1]
    by_name = {}
    for key, v in names.items():
        for n in v:
            by_name.setdefault(n, []).append(key)
    # Va is two rails on purpose: the supply comb of lvds_tx joins them
    problems += ["  Offen? %s ist %d Netze" % (n, len(k)) for n, k in by_name.items()
                 if len(k) > 1 and n != "Va"]

    # which layers each net uses, and what it reaches
    SX, SY = 0.3, 0.5
    bb = top.dbbox()

    def cells_of(g, net, layer):
        region = l2n.shapes_of_net(net, R[layer], True)
        for poly in region.each():
            for trap in poly.decompose_trapezoids():
                box = trap.bbox().to_dtype(ly.dbu)
                yield from g.span(box.left, box.bottom, box.right, box.top)

    def render(layers, upper, title):
        g = Grid(bb.right, bb.top, SX, SY)
        for path, d in devs:
            b = d.box
            g.outline(b.left + 0.4, b.bottom + 0.4, b.right - 0.4, b.top - 0.4)
        for name, ch, what in PD_NETS:
            for k in by_name.get(name, []):
                for layer in layers:
                    g.paint(list(cells_of(g, nets[k], layer)), ch, upper)
        for path, d in devs:
            b = d.box
            g.label(b.left + 0.4, b.bottom + 0.4, b.right - 0.4, b.top - 0.4, d.name)
        return g.text("%s   (%.1f x %.1f um; 1 Zeichen = %.2f um, 1 Zeile = %.1f um)"
                      % (title, bb.right, bb.top, SX, SY))

    legend = []
    for name, ch, what in PD_NETS:
        keys = by_name.get(name, [])
        if not keys:
            legend.append("  %s  %-9s  -- nicht gefunden" % (ch, name))
            continue
        used = [layer for layer in ("M2", "M3", "M4")
                if any(l2n.shapes_of_net(nets[k], R[layer], True).count() for k in keys)]
        ts = sorted(set(t for k in keys for t in terms[k]))
        legend.append("  %s/%s  %-9s %-44s  %s" % (ch, ch.upper(), name, what, "+".join(used)))
        legend.append("             an: " + ", ".join(ts))

    supply = []
    for name in SUPPLY:
        keys = by_name.get(name, [])
        tm = [p.bbox().to_dtype(ly.dbu) for k in keys
              for p in l2n.shapes_of_net(nets[k], R["TM1"], True).merged().each()]
        posts = sum(l2n.shapes_of_net(nets[k], R["TV1"], True).count() for k in keys)
        rails = ", ".join("y %.1f-%.1f" % (b.bottom, b.top) for b in sorted(tm, key=lambda b: -b.top))
        supply.append("  %-4s TopMetal1 %s, %d TopVia1-Posts%s" % (
            name, rails, posts,
            "  (zwei Schienen, erst der Kamm in lvds_tx verbindet sie)"
            if len(keys) > 1 else ""))

    head = [
        "=" * 100,
        heading,
        "=" * 100,
        "",
        "Die Verdrahtung, die route_predriver.py zeichnet (zur Zeit nicht im Flow; hier im",
        "Speicher gerechnet).  Aus der Geometrie extrahiert (Metal1-TopMetal1 und Poly, keine",
        "Diffusion) und ueber die Transistor-Anschluesse nach dem Schaltplan benannt.  Ein",
        "Buchstabe je Netz (Liste unten), ':' '.' = Umriss eines Transistors.  Va/Vss sind nicht",
        "eingezeichnet.  Koordinaten im predriver-Rahmen; in lvds_tx x + 9.36, y + 33.02.",
        ""]
    maps = [
        "Karte 1: Metal3 (senkrecht) und Metal4 (waagerecht) -- die Verbindungen zwischen den",
        "Transistoren und zu den Pins.  '+' = zwei Netze kreuzen sich (Metal3 unter Metal4).",
        "",
        render(("M3", "M4"), True, "predriver, Metal3/Metal4"),
        "",
        "",
        "Karte 2: Metal2 -- Straps ueber den Fingern (Drain/Source), Gate-Schienen und",
        "Gate-Balken; dort landen die Leitungen aus Karte 1.",
        "",
        render(("M2",), False, "predriver, Metal2")]
    tail = ["", "Netze:"] + legend + ["", "Versorgung (nicht eingezeichnet):"] + supply \
        + ["", "Pins: " + ", ".join(pins)]
    tail += ["", "Pruefung: jedes Netz genau einmal, keine zwei Namen auf einem Netz."] \
        if not problems else ["", "Auffaelligkeiten:"] + problems
    return "\n".join(head + maps + tail)


# ======================================================================
# 3. Driver: the plan in ROUTING.md section 3
# ======================================================================
M = 57.52                                   # driver width, axis at M/2


def mirror(pts):
    return [(M - x, y) for x, y in pts]


# net letter -> polylines in um (driver frame = lvds_tx frame)
DRV = {
    "#": [  # Out_p
        [(11.75, 0), (11.75, 17.2)], [(11.75, 13.3), (28.0, 13.3)], [(11.75, 11.4), (28.0, 11.4)],
        [(22.0, 11.4), (22.0, 13.3)], [(25.5, 11.4), (25.5, 13.3)], [(9.0, 11.1), (11.75, 11.1)],
        [(11.75, 17.2), (1.5, 17.2)], [(3.0, 17.2), (3.0, 46.4)], [(3.0, 35.2), (5.5, 35.2)],
        [(3.0, 46.4), (5.5, 46.4)],
    ],
    "P": [  # tail_p
        [(19.5, 21.0), (38.0, 21.0)], [(15.0, 18.5), (42.5, 18.5)],
        [(23.0, 18.5), (23.0, 21.0)], [(25.5, 18.5), (25.5, 21.0)], [(32.0, 18.5), (32.0, 21.0)],
        [(34.5, 18.5), (34.5, 21.0)],
    ],
    "N": [  # tail_n
        [(15.5, 8.6), (42.0, 8.6)], [(1.0, 7.2), (56.5, 7.2)],
        [(18.0, 7.2), (18.0, 8.6)], [(39.5, 7.2), (39.5, 8.6)],
        [(14.1, 8.6), (14.1, 18.9), (11.0, 18.9)], [(43.4, 8.6), (43.4, 21.9), (46.0, 21.9)],
    ],
    "i": [  # In_p
        [(17.5, 34.0), (17.5, 19.1)], [(16.0, 11.2), (16.0, 13.7)], [(16.0, 14.3), (51.5, 14.3)],
    ],
    "j": [  # In_n
        [(40.0, 34.0), (40.0, 19.1)], [(41.5, 11.2), (41.5, 13.7)], [(41.5, 15.0), (6.0, 15.0)],
    ],
    "c": [[(1.5, 9.3), (1.5, 3.8), (4.0, 3.8)], [(1.5, 7.5), (56.0, 7.5), (56.0, 9.3)]],   # cm
    "d": [[(4.0, 3.4), (25.5, 3.4)], [(19.0, 3.4), (19.0, 23.0)], [(17.5, 23.0), (40.0, 23.0)]],  # pd
    "f": [[(32.0, 3.4), (53.5, 3.4)], [(38.5, 3.4), (38.5, 24.0)],                        # cmfb
          [(38.5, 24.0), (49.8, 24.0), (49.8, 19.9)], [(38.5, 25.9), (36.0, 25.9)]],
    "g": [[(56.4, 19.9), (56.4, 27.3), (54.0, 27.3)]],                                    # cc_g
    "r": [[(28.4, 57.6), (28.4, 3.2)], [(26.8, 3.2), (30.0, 3.2)], [(28.4, 4.9), (27.0, 4.9)]],  # Iref
    "v": [[(29.1, 57.6), (29.1, 3.8), (32.0, 3.8)]],                                      # Vref
    "t": [[(3.0, 1.2), (54.0, 1.2)]],                                                     # otail
}
DRV["@"] = [mirror(p) for p in DRV["#"]]
DRV_LEGEND = [
    ("#", "Out_p", "Stamm x ~12 bis zur Suedkante, Straps von M5/M1, Rp, Cxp, hinauf zu Cop"),
    ("@", "Out_n", "Spiegelbild, hinauf zu Con"),
    ("P", "tail_p", "M2-Drain auf die Sources von M5/M4"),
    ("N", "tail_n", "Sources von M1/M3 auf die Drains von M6, Aeste zu Ctn1/Ctn2"),
    ("i", "In_p", "vom Predriver auf die Gates von M5/M1, weiter zu Cxn"),
    ("j", "In_n", "Spiegelbild, zu Cxp"),
    ("c", "cm", "Rp/Rn -> Gate M11, unter Cxp/Cxn durch"),
    ("d", "pd", "M11 D -> M13 D+G -> M14 G"),
    ("f", "cmfb", "M12 D -> M14 D -> M2 G, Rc R1"),
    ("g", "cc_g", "Rc R2 -> Gate-Schiene von Cc"),
    ("r", "Iref", "Iref_drv auf der Achse hinunter zu M9 (Gates M6, M10)"),
    ("v", "Vref", "auf der Achse hinunter zum Gate von M12"),
    ("t", "otail", "M10 D -> Sources von M11/M12"),
]


def part_driver():
    SX, SY = 0.5, 1.0
    boxes = ascii_layout.flat("Driver")
    w = max(b[4] for b in boxes)
    h = max(b[5] for b in boxes)
    g = Grid(w, h, SX, SY)
    for lab, kind, x0, y0, x1, y1 in boxes:
        g.outline(x0 + 0.3, y0 + 0.3, x1 - 0.3, y1 - 0.3)
    for ch, polys in DRV.items():
        for pts in polys:
            g.paint(g.polyline(pts), ch.lower() if ch.isalpha() else ch, True)
    for lab, kind, x0, y0, x1, y1 in boxes:
        g.label(x0 + 0.3, y0 + 0.3, x1 - 0.3, y1 - 0.3,
                lab.replace("_0", "0").replace("_1", "1"))
    legend = ["  %s  %-7s %s" % (ch.upper() if ch.isalpha() else ch, n, what)
              for ch, n, what in DRV_LEGEND]
    return "\n".join([
        "=" * 100,
        "3. Driver -- geplante Verdrahtung (ROUTING.md Abschnitt 3), noch nicht gezeichnet",
        "=" * 100,
        "",
        "Von Hand eingetragen, nicht extrahiert.  '+' = zwei Netze kreuzen sich auf",
        "verschiedenen Lagen.  Va/Vss nicht eingezeichnet.",
        "",
        g.text("Driver   (%.1f x %.1f um; 1 Zeichen = %.2f um, 1 Zeile = %.1f um)"
               % (w, h, SX, SY)),
        "",
        "Netze:"] + legend)


def main(args):
    if args == ["predriver"]:
        print(part_predriver("predriver -- Verdrahtung (route_predriver.py)"))
        return
    print("\n\n\n".join([part_top(), part_predriver(), part_driver()]))


if __name__ == "__main__":
    main(sys.argv[1:])
