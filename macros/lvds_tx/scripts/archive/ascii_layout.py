#!/usr/bin/env python3
"""Every cell of lvds_tx as ASCII, drawn from floorplan.json and the leaf
cell boxes -- the placement as it is, to scale.

    python3 ascii_layout.py > layout_ascii.txt

Each device is its .mag box, drawn inside by half the overlap at which two
cells of its kind share a guard ring (spacing.py): a pair on a shared ring
then shows as two boxes with one common edge, a merged pair as two boxes a
little apart, instead of frames inside each other.  The scale is set
per cell so that nothing is wider than about 125 characters.
"""
import json
import os
import sys

LAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LAY)
from build_placement import leaf_bbox  # noqa: E402
from devices import parse  # noqa: E402
from magfile import orient_box  # noqa: E402
from spacing import KIND  # noqa: E402

fp = json.load(open(LAY + "/floorplan.json"))
subs = parse()
BORDER = {"p": ("=", "|"), "n": ("-", "|"), "r": ("~", ":"), "c": ("#", "#")}
TAG = {"p": "P", "n": "N", "r": "R", "c": "C"}


def flat(name):
    """[(label, kind, x0, y0, x1, y1)] in um, every leaf device of `name`."""
    out = []
    sub = subs[name]
    kids = [(d.name, d.cellname, KIND[d.model]) for d in sub.devices] + \
           [(i.name, i.cell, None) for i in sub.instances]
    for inst, child, kind in kids:
        e = fp[name][inst]
        o = e[2] if len(e) > 2 else "r0"
        if kind:
            a, b, c, d = orient_box(leaf_bbox(child), o)
            x0, y0 = e[0] / 200.0, e[1] / 200.0
            out.append((inst, kind, x0, y0, x0 + (c - a) / 200.0, y0 + (d - b) / 200.0))
        else:
            inner = flat(child)
            # box of the child in its own frame, in 5 nm units, for the turn
            cx1 = max(v[4] for v in inner) * 200
            cy1 = max(v[5] for v in inner) * 200
            llx, lly, _, _ = orient_box((0, 0, cx1, cy1), o)
            for lab, k, a0, b0, a1, b1 in inner:
                a, b, c, d = orient_box((a0 * 200, b0 * 200, a1 * 200, b1 * 200), o)
                out.append((lab, k, (a - llx + e[0]) / 200.0, (b - lly + e[1]) / 200.0,
                            (c - llx + e[0]) / 200.0, (d - lly + e[1]) / 200.0))
    return out


# um drawn inside each box on every side: half the shared-ring overlap
SHRINK = {"p": 0.77, "n": 0.46, "r": 0.45, "c": 0.45}


def render(name, title, label_of=lambda s: s, SX=0.5, SY=1.0):
    boxes = [(l, k, x0 + SHRINK[k], y0 + SHRINK[k], x1 - SHRINK[k], y1 - SHRINK[k])
             for l, k, x0, y0, x1, y1 in flat(name)]
    W = int(round(max(b[4] for b in boxes) / SX)) + 1
    H = int(round(max(b[5] for b in boxes) / SY)) + 1
    g = [[" "] * W for _ in range(H)]

    def cell(x, y):                      # um -> (row, col), row 0 at the top
        return H - 1 - int(round(y / SY)), int(round(x / SX))

    # big boxes first, small ones drawn over them
    order = sorted(boxes, key=lambda b: -(b[4] - b[2]) * (b[5] - b[3]))
    for lab, k, x0, y0, x1, y1 in order:
        rt, c0 = cell(x0, y1)
        rb, c1 = cell(x1, y0)
        hch, vch = BORDER[k]
        for c in range(c0, c1 + 1):
            g[rt][c] = hch
            g[rb][c] = hch
        for r in range(rt, rb + 1):
            g[r][c0] = vch
            g[r][c1] = vch
        for r, c in ((rt, c0), (rt, c1), (rb, c0), (rb, c1)):
            g[r][c] = "+"
    for lab, k, x0, y0, x1, y1 in order:
        rt, c0 = cell(x0, y1)
        rb, c1 = cell(x1, y0)
        inner_w, inner_h = c1 - c0 - 1, rb - rt - 1
        text = label_of(lab)
        if inner_h < 1 or inner_w < 1:
            continue
        if len(text) > inner_w and len(text) - 1 <= inner_w:
            text = text[1:]              # M10 -> 10, never a misleading M1
        if len(text) > inner_w:
            continue
        lines = [text] + ([TAG[k]] if inner_h >= 3 else [])

        def free(r, t):
            c = c0 + 1 + (inner_w - len(t)) // 2
            return all(g[r][c + j] == " " for j in range(len(t))), c

        # middle of the box first, then any row where the label fits
        mid = rt + 1 + max(0, (inner_h - len(lines)) // 2)
        rows = sorted(range(rt + 1, rb - len(lines) + 2), key=lambda r: abs(r - mid))
        for r0 in rows:
            if all(free(r0 + i, t)[0] for i, t in enumerate(lines)):
                for i, t in enumerate(lines):
                    _, c = free(r0 + i, t)
                    for j, ch in enumerate(t):
                        g[r0 + i][c + j] = ch
                break
        else:
            for r0 in rows:                       # at least the name
                ok, c = free(r0, text)
                if ok:
                    for j, ch in enumerate(text):
                        g[r0][c + j] = ch
                    break
    rl = [" "] * (W + 8)
    for i in range(0, int(W * SX) + 1, 5):
        for j, ch in enumerate(str(i)):
            rl[int(round(i / SX)) + j] = ch
    ruler = "".join(rl).rstrip()
    out = ["%s   (%.1f x %.1f um; 1 Zeichen = %.2f um, 1 Zeile = %.1f um)"
           % (title, max(b[4] + SHRINK[b[1]] for b in boxes),
              max(b[5] + SHRINK[b[1]] for b in boxes), SX, SY),
           "      " + ruler + "  x/um"]
    for r in range(H):
        y = (H - 1 - r) * SY
        tag = "%5.0f " % round(y / 5) * 5 if False else ("%5.0f " % (round(y / 5) * 5) if abs(y - round(y / 5) * 5) < SY / 2 else "      ")
        out.append(tag + "".join(g[r]).rstrip())
    return "\n".join(out)


def main():
    legend = "\n".join([
        "Rahmen: '=' PMOS, '-' NMOS, '~' rhigh, '#' MOM-Kondensator; P/N/R/C im Kasten = Typ.",
        "Kaesten eingerueckt (PMOS 0.77 um, NMOS 0.46 um, sonst 0.45 um): Nachbarn mit gemeinsamem",
        "Guard-Ring stossen mit einer Kante aneinander; verschmolzene Nachbarn (PMOS 0.85 um,",
        "NMOS 0.175 um Ueberlappung) erscheinen mit kleinem Abstand.",
        "In der Gesamtansicht sind kleine Devices abgekuerzt (Mre = Mref, Mn.. = Stage-NMOS);",
        "ausgeschrieben stehen sie in den Einzelansichten darunter.",
        "Die Verbindungen stehen in routing_ascii.txt (ascii_routing.py)."])
    parts = [legend,
             render("lvds_tx", "lvds_tx (gesamt)"),
             render("Driver", "Driver"),
             render("predriver", "predriver", SX=0.35, SY=0.7),
             render("predriver_comp", "predriver_comp (kpm; knm gespiegelt)", SX=0.25, SY=0.5),
             render("predriver_stage", "predriver_stage", SX=0.35, SY=0.7)]
    print("\n\n".join(parts))


if __name__ == "__main__":
    main()
