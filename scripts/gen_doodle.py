#!/usr/bin/env python3
"""Silicon doodle: the flags of the three people behind slot 14 - Germany
(Enno, with the federal eagle), India (Rahul) and the USA (Tim, harness).

Colours are metal levels, which look different under the microscope:
black/navy metal1, red metal2, gold/saffron metal3, green metal4, and the
eagle on metal4 over the German stripes.  Everything obeys the sg13cmos5l
metal rules: edges at 0/45/90 degrees only, no acute corners, 5 nm grid,
widths and spaces above M1.a/b and Mn.a/b.  Pixel art is cleaned so no two
pixels touch at a corner only.

usage: gen_doodle.py <out.gds>      (cell flags_doodle, 12 um high)"""
import sys
import klayout.db as kdb

G = 0.005                                   # drawing grid
def g(v): return round(v / G) * G
H = 12.0                                    # flag height

ly = kdb.Layout(); ly.dbu = 0.001
cell = ly.create_cell("flags_doodle")
M1, M2, M3, M4 = (ly.layer(l, 0) for l in (8, 10, 30, 50))
def box(li, x0, y0, x1, y1, reg=None):
    b = kdb.DBox(g(x0), g(y0), g(x1), g(y1))
    (reg.insert(b.to_itype(ly.dbu)) if reg is not None else cell.shapes(li).insert(b))
def poly(pts): return kdb.DPolygon([kdb.DPoint(g(x), g(y)) for x, y in pts]).to_itype(ly.dbu)

def bitmap(rows, x0, y0, p):
    """'#' pixels -> merged region; corner-only contacts get a fill pixel."""
    m = [list(r) for r in rows]
    h, w = len(m), max(len(r) for r in m)
    for r in m: r += ["."] * (w - len(r))
    changed = True
    while changed:
        changed = False
        for i in range(h - 1):
            for j in range(w - 1):
                a, b, c, d = m[i][j], m[i][j + 1], m[i + 1][j], m[i + 1][j + 1]
                if a == d == "#" and b == c == "." : m[i][j + 1] = "#"; changed = True
                if b == c == "#" and a == d == "." : m[i][j] = "#"; changed = True
    reg = kdb.Region()
    for i in range(h):
        for j in range(w):
            if m[i][j] == "#":
                reg.insert(kdb.DBox(g(x0 + j * p), g(y0 + (h - 1 - i) * p), g(x0 + (j + 1) * p), g(y0 + (h - i) * p)).to_itype(ly.dbu))
    return reg.merged()

def octagon(cx, cy, a):
    """regular-ish octagon of inradius a, facets normal to 0/45/90 deg, exact 45 deg edges"""
    c = g(a * (2 - 2 ** 0.5) / 2 * 2 ** 0.5 * 0.7071 * 2)    # corner cut, ~0.586 a
    c = g(a * 0.5858)
    return poly([(cx + a, cy - a + c), (cx + a, cy + a - c), (cx + a - c, cy + a), (cx - a + c, cy + a),
                 (cx - a, cy + a - c), (cx - a, cy - a + c), (cx - a + c, cy - a), (cx + a - c, cy - a)])

# ---------------- Germany: 5:3, black / red / gold, federal eagle on metal4
W_DE = H * 5 / 3; x = 0.0
box(M1, x, 2 * H / 3, x + W_DE, H); box(M2, x, H / 3, x + W_DE, 2 * H / 3); box(M3, x, 0, x + W_DE, H / 3)
def eagle_rows():
    """federal eagle, 27 x 24 pixels: head with eye and hooked beak to the
    viewer's left, wings rising to the tips with five pinions each, legs with
    talons, a tail fan.  Staircases step orthogonally, no corner contacts."""
    W = 27
    rows = [set() for _ in range(24)]
    def run(r, c0, c1): rows[r].update(range(c0, c1 + 1))
    run(0, 12, 15); run(1, 11, 16); run(2, 10, 11); run(2, 13, 16); run(3, 8, 16)
    run(4, 7, 10); run(4, 12, 16); run(5, 7, 8); run(5, 12, 15)
    for k in range(5):                                   # wing tips rising outward, shoulders widening
        r = 6 + k
        run(r, 0, k); run(r, 26 - k, 26); run(r, 11 - k, 15 + k)
    run(11, 0, 26); run(12, 0, 26)
    for c, last in ((0, 20), (2, 19), (4, 18), (6, 17), (8, 16)):   # pinions
        for r in range(13, last + 1): rows[r].add(c); rows[r].add(26 - c)
    for r in range(13, 18): run(r, 10, 16)               # body
    run(18, 11, 15); run(19, 11, 15); run(20, 11, 15); run(21, 10, 16)   # tail
    for r in (22, 23):
        for c in (10, 12, 14, 16): rows[r].add(c)
    for r, (c0, c1) in zip((18, 19, 20, 21), ((9, 10), (8, 9), (7, 8), (6, 8))):   # legs
        run(r, c0, c1); run(r, 26 - c1, 26 - c0)
    for c in (6, 8): rows[22].add(c); rows[22].add(26 - c)  # talons
    return ["".join("#" if c in rr else "." for c in range(W)) for rr in rows]
EAGLE = eagle_rows()
p = 0.32
ew, eh = len(EAGLE[0]) * p, len(EAGLE) * p
cell.shapes(M4).insert(bitmap(EAGLE, x + (W_DE - ew) / 2, (H - eh) / 2, p))

# ---------------- India: 3:2, saffron / white / green, chakra on metal1
x = W_DE + 2.0; W_IN = H * 3 / 2
box(M3, x, 2 * H / 3, x + W_IN, H); box(M4, x, 0, x + W_IN, H / 3)
cx, cy = g(x + W_IN / 2), g(H / 2)
R_OUT, R_IN, R_HUB, SH = 1.8, 1.55, 0.55, 0.12          # ring, hub inradius, spoke half-width (45 deg: SH*sqrt2/2*2)
ring = kdb.Region(octagon(cx, cy, R_OUT)) - kdb.Region(octagon(cx, cy, R_IN))
chakra = ring + kdb.Region(octagon(cx, cy, R_HUB))
for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):              # orthogonal spokes
    if sx: chakra.insert(kdb.DBox(g(cx + sx * (R_HUB - 0.05)), g(cy - 0.085), g(cx + sx * (R_IN + 0.05)), g(cy + 0.085)).to_itype(ly.dbu))
    else:  chakra.insert(kdb.DBox(g(cx - 0.085), g(cy + sy * (R_HUB - 0.05)), g(cx + 0.085), g(cy + sy * (R_IN + 0.05))).to_itype(ly.dbu))
for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):            # 45 deg spokes, exact 45 deg edges
    r0, r1 = (R_HUB - 0.05) * 0.7071, (R_IN + 0.05) * 0.7071   # along the diagonal, per axis
    a, b = (g(cx + sx * r0), g(cy + sy * r0)), (g(cx + sx * r1), g(cy + sy * r1))
    h = SH * 0.7071
    nx, ny = -sy * h, sx * h                                   # perpendicular, per axis
    chakra.insert(poly([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]))
cell.shapes(M1).insert(chakra.merged())

# ---------------- USA: 19:10, 13 stripes, canton with 50 stars (diamond holes)
x = W_DE + 2.0 + W_IN + 2.0; W_US = H * 1.9; s = H / 13
for k in range(13):
    if k % 2 == 0: box(M2, x + (0.76 * H if k < 7 else 0) - 0.0, H - (k + 1) * s, x + W_US, H - k * s)
cw, ch = 0.76 * H, 7 * s
canton = kdb.Region(kdb.DBox(g(x), g(H - ch), g(x + cw), g(H)).to_itype(ly.dbu))
d = 0.25
for row in range(9):
    for col in range(11):
        if (row + col) % 2: continue
        sx_, sy_ = g(x + cw * (col + 1) / 12), g(H - ch * (row + 1) / 10)
        canton -= kdb.Region(poly([(sx_ + d, sy_), (sx_, sy_ + d), (sx_ - d, sy_), (sx_, sy_ - d)]))
cell.shapes(M1).insert(canton)
n_stars = sum(1 for row in range(9) for col in range(11) if not (row + col) % 2)
print("flags_doodle %s (%.1f x %.1f um), %d Sterne" % (cell.dbbox(), cell.dbbox().width(), cell.dbbox().height(), n_stars))
ly.write(sys.argv[1] if len(sys.argv) > 1 else "flags_doodle.gds")
