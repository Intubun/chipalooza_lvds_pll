#!/usr/bin/env python3
"""Route the pre-driver: `predriver_comp`, `predriver_stage`, `predriver`.

    python3 route_predriver.py                  # into lvds_tx_gen.gds, in place
    python3 route_predriver.py in.gds out.gds   # a copy, for trying things

magic writes lvds_tx_gen.gds with every device placed and nothing
connected.  This draws the pre-driver's wiring into it, cell by cell, as
plain KLayout geometry.  It is a scripted hand-routing, not a router: every
wire is written down below, net by net, the way ROUTING.md (sections 4-6)
plans it.  What is computed is only *where* -- straps, vias and tracks are
put relative to the stripes, gate rails and guard rings the device cells
really have, so a device that moves a little takes its wiring along.  A new
floorplan can still break it; the sign-off DRC and the LVS of `predriver`
(`check_lvs.sh predriver`) are what say so.

Layers, as ROUTING.md has them:

    metal1     only in the devices, plus patches that widen a guard ring
               where a via lands on it, and bridges from ring to ring
    metal2     horizontal straps over the fingers of every device; the gate
               rails the generator already puts there (`viagate`, see
               gen_devices.py); short vertical gate bars
    metal3     vertical: device to device, the block's in- and outputs
    metal4     horizontal: the stage's two cross tracks, the D_p/D_n bus,
               landing pads under TopMetal1
    TopMetal1  three supply rails: Va over the comparator loads (top),
               Vss over the comparator tails and the stage's NMOS row,
               Va under the stage's PMOS row (bottom)

Supply current reaches a transistor through "posts": a stack of vias from
its source strap straight up to the TopMetal1 rail above it.  Guard rings
are bridged ring to ring with metal1, and tied to the posts or to their own
source strap, so each ring group reaches its supply without a wire of its
own.

Nothing here writes lvds_tx.gds.
"""
import os
import sys

import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from devices import MERGED  # noqa: E402
GDS = os.path.join(HERE, "lvds_tx_gen.gds")

LAYERS = {"M1": (8, 0), "V1": (19, 0), "M2": (10, 0), "V2": (29, 0),
          "M3": (30, 0), "V3": (49, 0), "M4": (50, 0), "TV1": (125, 0),
          "TM1": (126, 0)}
PIN = {"M3": (30, 2), "TM1": (126, 2)}
TEXT = {"M3": (30, 25), "TM1": (126, 25)}

# cut size and spacing (V1.a/b, Vn.a/b, TV1.a/b)
CUT = {"V1": (0.19, 0.22), "V2": (0.19, 0.22), "V3": (0.19, 0.22),
       "TV1": (0.42, 0.42)}
STACK = ["M1", "V1", "M2", "V2", "M3", "V3", "M4", "TV1", "TM1"]

# Transistors whose sources sit on the generator's "D" stripes (the even
# ones), and their drains on its "S": the comparator's tail halves, whose
# drains have to line up under the input pair's sources.  Source and drain
# are the same to the device; only the routing decides.
SOURCE_ON_D = {"Mt_0", "Mt_1"}

# Metal2 straps keep this far from the generator's metal2 gate rails.  0.24
# is Mn.e (a wire over 0.39 um wide running more than 1 um alongside); 0.25
# keeps a grid step in hand.
RAIL_GAP = 0.25
STRAP_GAP = 0.25        # between the two straps over one device
GRID = 0.005


def snap(v):
    return round(round(v / GRID) * GRID, 3)


class Dev:
    """One transistor as the router sees it, in its parent's frame (um).

    stripes["D"] / ["S"]  the metal1 source/drain stripes, left to right
    rails                 (bottom, top) metal2 gate rails
    ring                  outer box of the metal1 guard ring (0.16 um bars)
    """

    def __init__(self, layout, inst, name):
        self.name = name
        leaf = layout.cell(inst.cell_index)
        t = inst.dcplx_trans
        # the generator draws a rail or a ring as several overlapping pieces
        def merged(layer):
            region = kdb.Region(leaf.shapes(layout.layer(*LAYERS[layer])))
            return [p.bbox().to_dtype(layout.dbu) for p in region.merged().each()]
        m1, m2 = merged("M1"), merged("M2")
        # a stripe is a 0.26 um wide vertical bar; the generator numbers
        # them D0 S1 D2 ... from the left of the unturned cell
        bars = sorted((b for b in m1 if abs(b.width() - 0.26) < 0.011
                       and b.height() > 0.5), key=lambda b: b.left)
        self.stripes = {"D": [], "S": []}
        for k, b in enumerate(bars):
            self.stripes["D" if k % 2 == 0 else "S"].append(t * b)
        for key in self.stripes:
            self.stripes[key].sort(key=lambda b: b.left)
        # (bottom, top); None where the cell is contacted on one side only
        # (topc 0 / botc 0 -- the comparator's tail and pair)
        if not 1 <= len(m2) <= 2:
            raise SystemExit("%s: expected one or two metal2 gate rails, "
                             "found %d (viagate off?)" % (name, len(m2)))
        ys = [s.center().y for s in self.stripes["D"] + self.stripes["S"]]
        centre = (min(ys) + max(ys)) / 2
        placed = [t * b for b in m2]
        below = [r for r in placed if r.center().y < centre]
        above = [r for r in placed if r.center().y > centre]
        self.rails = (below[0] if below else None, above[0] if above else None)
        ring = kdb.DBox()
        for b in m1:
            ring += b
        self.ring = t * ring
        self.box = t * leaf.dbbox()

    @property
    def band(self):
        """The height between the two gate rails a strap may use -- up to
        the stripes' end on a side without a rail."""
        ys = [s for s in self.stripes["D"] + self.stripes["S"]]
        lo = (self.rails[0].top + RAIL_GAP if self.rails[0]
              else min(s.bottom for s in ys))
        hi = (self.rails[1].bottom - RAIL_GAP if self.rails[1]
              else max(s.top for s in ys))
        return (lo, hi)

    def halves(self, lower_from_rail=False):
        """(lower, upper) strap heights.  With `lower_from_rail` the lower
        one reaches down onto the bottom gate rail (a diode's drain)."""
        y0, y1 = self.band
        mid = (y0 + y1) / 2
        lo0 = self.rails[0].bottom if lower_from_rail else y0
        return ((snap(lo0), snap(mid - STRAP_GAP / 2)),
                (snap(mid + STRAP_GAP / 2), snap(y1)))


class Cell:
    """Drawing into one cell, optionally mirrored about x = w/2."""

    def __init__(self, layout, name, mirror_w=None):
        self.ly = layout
        self.cell = layout.cell(name)
        self.name = name
        self.mirror_w = mirror_w
        self.insts = {i.property(61): i for i in self.cell.each_inst()}

    def mirrored(self):
        c = Cell.__new__(Cell)
        c.__dict__.update(self.__dict__)
        c.mirror_w = self.width()
        return c

    def width(self):
        return self.cell.dbbox().right

    def dev(self, name):
        return Dev(self.ly, self.insts[name], name)

    def child(self, name):
        return self.insts[name]

    # --- drawing -----------------------------------------------------
    def _x(self, x0, x1):
        if self.mirror_w is None:
            return x0, x1
        return self.mirror_w - x1, self.mirror_w - x0

    def rect(self, layer, x0, y0, x1, y1):
        """Draw a box; returns it in the caller's frame (unmirrored)."""
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        mx0, mx1 = self._x(x0, x1)
        self.cell.shapes(self.ly.layer(*LAYERS[layer])).insert(
            kdb.DBox(snap(mx0), snap(y0), snap(mx1), snap(y1)))
        return kdb.DBox(snap(x0), snap(y0), snap(x1), snap(y1))

    def cuts(self, via, x0, y0, x1, y1):
        """As many cuts as fit in the box, centred."""
        size, space = CUT[via]

        def count(a, b, sp):
            return max(1, int((b - a + sp + 1e-6) // (size + sp)))
        nx, ny = count(x0, x1, space), count(y0, y1, space)
        if nx >= 3 and ny >= 3:         # V1.b1 / Vn.b1: arrays space wider
            space = 0.29
            nx, ny = count(x0, x1, space), count(y0, y1, space)
        pitch = size + space
        sx = snap((x0 + x1) / 2 - (nx * size + (nx - 1) * space) / 2)
        sy = snap((y0 + y1) / 2 - (ny * size + (ny - 1) * space) / 2)
        for i in range(nx):
            for j in range(ny):
                a, b = sx + i * pitch, sy + j * pitch
                self.rect(via, a, b, a + size, b + size)

    def cut(self, via, x, y, n=1):
        """`n` cuts side by side (in x) centred on (x, y)."""
        size, space = CUT[via]
        w = n * size + (n - 1) * space
        self.cuts(via, x - w / 2, y - size / 2, x + w / 2, y + size / 2)

    def post(self, x, y, lo, hi, n=1):
        """A via stack at (x, y) from metal `lo` up to metal `hi`, with
        landing pads on the metals in between (not on `lo` or `hi`)."""
        a, b = STACK.index(lo), STACK.index(hi)
        for k in range(a + 1, b, 2):
            self.cut(STACK[k], x, y, 1 if STACK[k] == "TV1" else n)
        cuts = n * 0.19 + (n - 1) * 0.22
        for k in range(a + 2, b, 2):
            metal = STACK[k]
            if STACK[k + 1] == "TV1":       # TV1.c: 0.1 um of metal4
                w, h = max(0.62, cuts + 0.1), 0.62
            else:                           # 0.39 square: Mn.d area
                w, h = max(0.39, cuts + 0.1), 0.39
            self.rect(metal, x - w / 2, y - h / 2, x + w / 2, y + h / 2)

    def label(self, layer, text, x0, y0, x1, y1):
        x0, x1 = self._x(min(x0, x1), max(x0, x1))
        box = kdb.DBox(snap(x0), snap(y0), snap(x1), snap(y1))
        self.cell.shapes(self.ly.layer(*PIN[layer])).insert(box)
        self.cell.shapes(self.ly.layer(*TEXT[layer])).insert(
            kdb.DText(text, box.center().x, box.center().y))

    # --- device wiring -----------------------------------------------
    def strap(self, dev, term, heights, extend=()):
        """Metal2 strap over every `term` stripe of `dev`, at `heights`,
        with via1 into each stripe.  `extend` widens it to more x."""
        return self.strap_over(dev.stripes[term], heights, extend)

    def strap_over(self, stripes, heights, extend=()):
        """Metal2 strap over the given stripes, via1 into each."""
        y0, y1 = heights
        xs = [s.left - 0.02 for s in stripes] + [s.right + 0.02 for s in stripes]
        xs += list(extend)
        box = self.rect("M2", min(xs), y0, max(xs), y1)
        for s in stripes:
            lo, hi = max(y0, s.bottom) + 0.05, min(y1, s.top) - 0.05
            self.cuts("V1", s.left + 0.035, lo, s.right - 0.035, hi)
        return box

    def fill_rails(self):
        """Square off every gate rail in the cell.  The generator's rail is
        a 0.2 um core with a 0.29 um bump over each via1; anything joined
        onto it next to a bump leaves a notch (M2.b).  Filled out to its
        bounding box it is a plain 0.29 um bar -- no wider than the bumps
        already made it."""
        for name, inst in self.insts.items():
            if self.ly.cell(inst.cell_index).name.startswith(("dev_n_", "dev_p_")):
                for r in Dev(self.ly, inst, name).rails:
                    if r is not None:
                        self.rect("M2", r.left, r.bottom, r.right, r.top)

    def vline(self, layer, x, y0, y1, w=0.3):
        return self.rect(layer, x - w / 2, y0, x + w / 2, y1)

    def hline(self, layer, y, x0, x1, w=0.3):
        return self.rect(layer, x0, y - w / 2, x1, y + w / 2)


def mid(a, b):
    return snap((a + b) / 2)


# ======================================================================
# predriver_comp  (kpm; knm is its mirror image in `predriver`)
# ======================================================================
def route_comp(c, out_x):
    """`out_x`: where the comparator output leaves the cell downwards, in
    the cell's own frame.  Decided by the stage below (its input column)."""
    T0, T1, Mid, Mio, L = (c.dev(n) for n in ("Mt_0", "Mt_1", "Mid", "Mio", "Mldo"))
    c.fill_rails()

    # --- tail and pair, finger on finger (make_floorplan.py) ---------------
    # Mt_0 stands under Mid, Mt_1 under Mio, in one guard ring with nothing
    # between the rows.  Each tail drain (net2, the odd stripes) runs
    # straight up in metal1 into the pair source above it: net2 needs no
    # metal2 and no metal3.  The tail's sources (Vss) are its even stripes,
    # under the pair's drains, and stop short of them.
    for T, P in ((T0, Mid), (T1, Mio)):
        for td, ps in zip(T.stripes["S"], P.stripes["S"]):
            if abs(td.left - ps.left) > 1e-3:
                raise SystemExit("%s and %s are no longer finger on finger"
                                 % (T.name, P.name))
            c.rect("M1", td.left, td.top - 0.05, td.right, ps.bottom + 0.05)
    # ... and the columns of each half joined by a metal1 bar in the gap
    # between the rows, 0.19 um clear of the tail's sources below and the
    # pair's drains above.  Only the ring bar between the two halves (Vss)
    # has to be crossed on metal2.
    g0 = snap(max(s.top for s in T0.stripes["D"]) + 0.19)
    g1 = snap(min(s.bottom for s in Mid.stripes["D"]) - 0.19)
    if g1 - g0 < 0.28:
        raise SystemExit("the gap between tail and pair no longer takes a "
                         "metal1 bar (%.3f um)" % (g1 - g0))
    for T in (T0, T1):
        ss = T.stripes["S"]
        c.rect("M1", ss[0].left, g0, ss[-1].right, g1)
    ym = mid(g0, g1)
    xa = mid(T0.stripes["S"][-1].left, T0.stripes["S"][-1].right)
    xb = mid(T1.stripes["S"][0].left, T1.stripes["S"][0].right)
    c.cut("V1", xa, ym)
    c.cut("V1", xb, ym)
    c.rect("M2", xa - 0.15, ym - 0.15, xb + 0.15, ym + 0.15)

    # --- tail gates (Iref): the two halves' bottom rails joined, so that
    # the cell has one Iref of its own -------------------------------------
    r0, r1 = T0.rails[0], T1.rails[0]
    c.rect("M2", min(r0.right, r1.right) - 0.1, r0.bottom,
           max(r0.left, r1.left) + 0.1, r0.top)

    # --- tail sources (Vss): one strap over both halves ---------------------
    t_band = T0.band
    h_vss = (snap(t_band[0]), snap(t_band[1] - 0.1))
    v0 = c.strap(T0, "D", h_vss)
    v1 = c.strap(T1, "D", h_vss)
    c.rect("M2", v0.right, h_vss[0], v1.left, h_vss[1])
    # ... and on out over the ring's outer side bars, to a via on each: the
    # sources and the ring (the p-substrate) are one Vss inside this cell.
    # The side, not the bottom bar: under that one the stage's metal1
    # bridges come up.
    y = mid(*h_vss)
    for x_bar, out, strap in ((T0.ring.left, -1, v0), (T1.ring.right, 1, v1)):
        x_via = snap(x_bar + out * 0.14)      # just outside the bar
        c.rect("M1", x_via - 0.16, y - 0.2, x_via + 0.16, y + 0.2)
        c.cut("V1", x_via, y)
        end = strap.left if out < 0 else strap.right
        c.rect("M2", min(x_via, end) - 0.15, y - 0.15, max(x_via, end) + 0.15,
               y + 0.15)

    # --- pair drains: net1 over Mid, Out over Mio -------------------------
    # (starting 0.1 um up, clear of the net2 bridge in metal2 below)
    p_band = (snap(Mid.band[0] + 0.1), snap(Mid.band[1]))
    c.strap(Mid, "D", p_band)
    c.strap(Mio, "D", p_band, extend=(out_x + 0.2,))

    # --- load Mld|Mlo, one cell (devices.py: MERGED) -----------------------
    # Its gate rail runs through all eight fingers in metal1, at the bottom
    # only.  The sources sit on the even stripes, the drains of Mld and Mlo
    # on the odd ones (`drains`).  The diode is closed in metal1: each of
    # Mld's drain stripes runs on down into the gate rail below it -- net1
    # needs no strap.  The sources run on up into the guard ring (Va) in
    # metal1: with no gate rail on top nothing is in the way.  Out (Mlo's
    # drains) and Va get the two metal2 straps; the Va strap carries the
    # posts.
    ab = MERGED[("predriver_comp", "Mldo")]["drains"]
    drain = {k: [s for s, a in zip(L.stripes["S"], ab) if a == k] for k in "AB"}
    rail = L.rails[0]
    for st in drain["A"]:
        c.rect("M1", st.left, mid(rail.bottom, rail.top), st.right, st.bottom + 0.05)
    if L.rails[1] is not None:
        raise SystemExit("Mldo has a top gate rail again -- its sources "
                         "cannot reach the ring in metal1")
    for st in L.stripes["D"]:
        c.rect("M1", st.left, st.top - 0.05, st.right, L.ring.top - 0.08)
    h_out, h_va = L.halves()
    x_mid = (L.box.left + L.box.right) / 2
    x_n1, x_out = snap(x_mid - 2.07), snap(x_mid + 2.07)   # the two links
    c.strap_over(drain["B"], h_out, extend=(x_out + 0.25,))
    c.strap(L, "D", h_va)

    # --- net1: from the load's gate rail down to the Mid drains ----------
    ya, yb = mid(rail.bottom, rail.top), mid(*p_band)
    c.vline("M3", x_n1, yb - 0.2, ya + 0.2)
    c.cut("V2", x_n1, ya)
    c.cut("V2", x_n1, yb)

    # --- Out: Mlo drains down to the Mio drains, and on down out of the
    # cell towards the stage input below ---------------------------------
    ya = mid(*h_out)
    c.vline("M3", x_out, yb - 0.2, ya + 0.2)
    c.cut("V2", x_out, ya)
    c.cut("V2", x_out, yb)
    c.vline("M3", out_x, 0, yb + 0.2)
    c.cut("V2", out_x, yb)

    # --- Vss: posts from the tail sources to the TopMetal1 rail, two per
    # half, off the output line --------------------------------------------
    y = mid(*h_vss)
    xs = [snap(v.left + f * (v.right - v.left)) for v in (v0, v1) for f in (0.25, 0.75)]
    for x in xs:
        if abs(x - out_x) > 0.8:
            c.post(x, y, "M2", "TM1", n=2)

    # --- Va: posts from the load sources to the TopMetal1 rail (the ring
    # is on the sources already, in metal1) ---------------------------------
    y = mid(*h_va)
    for x in (x_n1, x_out):
        c.post(x, y, "M2", "TM1", n=2)

    return {"gate_din": Mid.rails[1], "gate_gin": Mio.rails[1],
            "tail_rails": (T0.rails[0], T1.rails[0]),
            "y_vss_post": mid(*h_vss), "y_va_post": mid(*h_va)}


# ======================================================================
# predriver_stage
# ======================================================================
# The two metal4 cross tracks in the gap between the PMOS row (below) and
# the NMOS row (above).  Net2 and net4 both cross the axis, so they cannot
# be mirror images on one track: the left half puts net2 on A and net1 on
# B, the mirrored right half puts their twins net4 on B and net3 on A.
Y_TRACK = {"A": 6.4, "B": 7.2}

# Where the stage output Out_p leaves the cell downwards: on the driver's
# In_p line (ROUTING.md: x ~ 17.5 um in lvds_tx, the stage sits at 9.36).
X_OUT = 8.14

# Posts sit on the source straps at these heights, under the TopMetal1
# rails of `predriver`.
Y_POST_P = 2.1
Y_POST_N = 9.875

PAIRS = (("Mpp2", "Mpn2"), ("Mnp2", "Mnn2"), ("Mpp1", "Mpn1"),
         ("Mnp1", "Mnn1"), ("Mpp0", "Mpn0"), ("Mnp0", "Mnn0"),
         ("Mpxn", "Mpxp"), ("Mnxn", "Mnxp"))


def route_stage(c, in_x, ring_above):
    """`in_x`: x of the stage input In_p (on column 3's gate).
    `ring_above`: top of the guard ring bar right above the NMOS row (the
    comparator tails'), which the NMOS rings are bridged up to."""
    w = c.width()
    for a, b in PAIRS:
        ba, bb = c.dev(a).box, c.dev(b).box
        if abs(ba.left - (w - bb.right)) > 1e-3 or abs(ba.bottom - bb.bottom) > 1e-3:
            raise SystemExit("%s/%s are no longer mirror images -- the stage "
                             "routing draws the right half as the mirror of "
                             "the left" % (a, b))
    c.fill_rails()
    tracks = {}
    route_stage_half(c, {"A": "A", "B": "B"}, in_x, ring_above, tracks,
                     {"in": "In_p", "out": "Out_p"})
    route_stage_half(c.mirrored(), {"A": "B", "B": "A"}, in_x, ring_above,
                     tracks, {"in": "In_n", "out": "Out_n"})
    for net, (x0, x1, t) in sorted(tracks.items()):
        c.hline("M4", Y_TRACK[t], x0 - 0.15, x1 + 0.15)

    # guard rings: the PMOS rings' bottom bars and the NMOS rings' top bars
    # (each row is flush on that side) bridged into one line per row
    for row, side in (("Mp", "bottom"), ("Mn", "top")):
        devs = sorted((c.dev(n) for n in c.insts if n.startswith(row)),
                      key=lambda d: d.ring.left)
        for a, b in zip(devs, devs[1:]):
            if b.ring.left <= a.ring.right:
                continue                    # a shared ring
            y = a.ring.bottom if side == "bottom" else a.ring.top - 0.16
            c.rect("M1", a.ring.right, y, b.ring.left, y + 0.16)


def route_stage_half(c, track, in_x, ring_above, tracks, names):
    """The left half of the stage, or -- drawn through a mirrored `c` --
    the right half.  `track` maps the left half's track names onto the
    ones this half uses."""
    w = c.width()
    flip = c.mirror_w is not None
    P2, N2, P1, N1, P0, N0, PX, NX = (c.dev(n) for n in (
        "Mpp2", "Mnp2", "Mpp1", "Mnp1", "Mpp0", "Mnp0", "Mpxn", "Mnxn"))

    def on_track(key, x, t):
        """Note a via on track `t` for the track segment `key`."""
        xx = w - x if flip else x
        x0, x1, _ = tracks.get(key, (xx, xx, None))
        tracks[key] = (min(x0, xx), max(x1, xx), track[t])

    # net names of this half, and of the other half's twin of net2
    me, other = ("'", "") if flip else ("", "'")

    # --- straps: PMOS sources (Va) below and drains above, NMOS drains
    # below and sources (Vss) above -- sources face their supply rail -----
    S, D = {}, {}
    for dev in (P2, P1, P0, PX):
        S[dev.name], D[dev.name] = dev.halves()
    for dev in (N2, N1, N0, NX):
        D[dev.name], S[dev.name] = dev.halves()

    x_d3 = snap(in_x - 0.56)            # column 3's drain line, left of In
    d_p2 = c.strap(P2, "D", D["Mpp2"])
    d_n2 = c.strap(N2, "D", D["Mnp2"])
    c.strap(P1, "D", D["Mpp1"])
    d_n1 = c.strap(N1, "D", D["Mnp1"])
    c.strap(P0, "D", D["Mpp0"], extend=(x_d3 - 0.2,))
    c.strap(N0, "D", D["Mnp0"], extend=(x_d3 - 0.2,))
    c.strap(PX, "D", D["Mpxn"])
    c.strap(NX, "D", D["Mnxn"])

    s_p2 = c.strap(P2, "S", S["Mpp2"])
    s_n2 = c.strap(N2, "S", S["Mnp2"])
    s_p1 = c.strap(P1, "S", S["Mpp1"])
    sn1 = N1.stripes["S"][0]
    s_n1 = c.strap(N1, "S", S["Mnp1"], extend=(sn1.left - 0.25, sn1.right + 0.25))
    sp0 = P0.stripes["S"][0]
    s_p0 = c.strap(P0, "S", S["Mpp0"], extend=(sp0.left - 0.2, sp0.right + 0.2))

    # Mnp0's source: the input line comes down right over it, so no post --
    # its strap goes to the ring bar beside it instead (the bar widened
    # inwards to take a via)
    lo, hi = S["Mnp0"]
    bar = N0.ring.right - 0.16
    c.strap(N0, "S", (lo, hi), extend=(bar + 0.16,))
    c.rect("M1", N0.stripes["S"][0].right + 0.18, lo, bar + 0.16, hi)
    c.cuts("V1", bar - 0.075, lo + 0.05, bar + 0.115, hi - 0.05)

    # Mpxn|Mpxp and Mnxn|Mnxp: the sources face each other across the
    # shared ring bar on the axis.  One strap over both, the bar widened to
    # take vias -- the axis stays free of metal3 for the bias lines
    axis = w / 2
    for dev in (PX, NX):
        lo, hi = S[dev.name]
        c.strap(dev, "S", (lo, hi), extend=(axis,))
        c.rect("M1", axis - 0.14, lo, axis, hi)
        if not flip:
            c.cuts("V1", axis - 0.095, lo + 0.05, axis + 0.095, hi - 0.05)

    # --- gate bars: each column's PMOS top rail to its NMOS bottom rail --
    def gate_bar(p, n, x):
        lo = max(p.rails[1].left, n.rails[0].left)
        hi = min(p.rails[1].right, n.rails[0].right)
        if not lo + 0.15 <= x <= hi - 0.15:
            raise SystemExit("gate bar of %s/%s at %.3f is off the rails "
                             "(%.3f..%.3f)" % (p.name, n.name, x, lo, hi))
        c.vline("M2", x, p.rails[1].bottom, n.rails[0].top)

    def overlap_mid(p, n):
        return mid(max(p.rails[1].left, n.rails[0].left),
                   min(p.rails[1].right, n.rails[0].right))

    x_g1 = overlap_mid(P2, N2)
    x_g2 = snap(min(P1.rails[1].right, N1.rails[0].right) - 0.35)
    x_g4 = snap(max(PX.rails[1].left, NX.rails[0].left) + 0.34)
    gate_bar(P2, N2, x_g1)
    gate_bar(P1, N1, x_g2)
    gate_bar(P0, N0, in_x)
    gate_bar(PX, NX, x_g4)

    # --- column 1: two Out lines between the drain straps; one carries on
    # down out of the cell ------------------------------------------------
    x_o2 = snap(d_n2.left + 0.4)
    for x in (X_OUT, x_o2):
        if not (d_p2.left + 0.25 <= x <= d_p2.right - 0.25
                and d_n2.left + 0.25 <= x <= d_n2.right - 0.25):
            raise SystemExit("Out line at %.3f misses a drain strap" % x)
    yp, yn = mid(*D["Mpp2"]), mid(*D["Mnp2"])
    c.vline("M3", X_OUT, 0.0, yn + 0.2, w=0.4)
    c.vline("M3", x_o2, yp - 0.2, yn + 0.2, w=0.4)
    for x in (X_OUT, x_o2):
        c.cut("V2", x, yp)
        c.cut("V2", x, yn)
    c.label("M3", names["out"], X_OUT - 0.2, 0.0, X_OUT + 0.2, 0.5)

    # --- drain lines of columns 2 to 4 ------------------------------------
    def drain_line(p, n, x):
        yp, yn = mid(*D[p.name]), mid(*D[n.name])
        c.vline("M3", x, yp - 0.195, yn + 0.195)
        c.cut("V2", x, yp)
        c.cut("V2", x, yn)

    x_d2 = snap(d_n1.left + 0.2)
    x_d4 = snap(NX.stripes["D"][0].left + 0.15)
    drain_line(P1, N1, x_d2)
    drain_line(P0, N0, x_d3)
    drain_line(PX, NX, x_d4)

    # --- onto the tracks: a via3 on a drain line; via2, a metal3 pad and a
    # via3 on a gate bar ------------------------------------------------------
    def drop(x, t, gate, y2=None):
        """`y2`: where the via2 goes if not on the track itself."""
        y = Y_TRACK[track[t]]
        if gate:
            y2 = y if y2 is None else y2
            c.cut("V2", x, y2)
            c.rect("M3", x - 0.195, min(y, y2) - 0.195, x + 0.195,
                   max(y, y2) + 0.195)
        c.cut("V3", x, y)

    for net, x, t, gate in (("net2", x_g1, "A", True), ("net2", x_d2, "A", False),
                            ("net2", x_d4, "A", False), ("net1", x_g2, "B", True),
                            ("net1", x_d3, "B", False)):
        drop(x, t, gate)
        on_track(net + me, x, t)
    # column 4's gate (net4) leaves its bar on a metal2 stub outwards, clear
    # of the drain line and of the axis, and joins the other half's net2
    # track -- net4 is the mirror image of net2
    # The stub stays at track B's height in both halves: at track A's it
    # would come within 0.15 um of the PMOS gate rail it starts from.
    x_p4 = snap(x_d4 - 0.89)
    y_stub = Y_TRACK["B"]
    c.hline("M2", y_stub, x_p4 - 0.2, x_g4 + 0.15)
    drop(x_p4, "B", True, y2=y_stub)
    on_track("net2" + other, x_p4, "B")

    # --- the stage input: from the comparator above onto column 3's bar.
    # Up to the ring above, which lies inside the comparator: its output
    # line starts at its bottom edge (and the cell's own top edge is no
    # measure -- the bridges drawn below move it) ----------------------
    top = ring_above
    y_in = snap(N0.rails[0].bottom - 0.3)
    c.vline("M3", in_x, y_in - 0.2, top)
    c.cut("V2", in_x, y_in)
    c.label("M3", names["in"], in_x - 0.15, top - 0.5, in_x + 0.15, top)

    # --- Va posts on the PMOS sources, each tied to the ring line below --
    ring_y = P2.ring.bottom + 0.08          # centre of the bottom bar line
    yr = snap(ring_y - 0.14)
    a, b = s_p2.left + 0.7, X_OUT - 1.0
    for x in (snap(a), mid(a, b), snap(b), mid(s_p1.left, s_p1.right),
              mid(s_p0.left, s_p0.right)):
        c.post(x, Y_POST_P, "M2", "TM1", n=2)
        c.rect("M1", x - 0.14, yr - 0.22, x + 0.14, ring_y + 0.08)
        c.cut("V1", x, yr)
        c.rect("M2", x - 0.25, yr - 0.15, x + 0.25, yr + 0.15)
        c.cut("V2", x, yr)
        c.vline("M3", x, yr - 0.15, Y_POST_P)

    # --- Vss: posts on the NMOS sources, and metal1 bridges from every
    # NMOS ring up to the ring above ---------------------------------------
    # Each post carries on up in metal3 to a via on a bridge, so sources and
    # rings are one Vss inside the cell.  Mnp0 and Mnxn, whose sources are
    # on their rings already, get a bridge with a post of its own.
    top = N2.ring.top
    yb = mid(top, ring_above)
    a, b = s_n2.left + 0.9, s_n2.right - 0.8
    on_source = [snap(a), mid(a, b), snap(b), mid(s_n1.left, s_n1.right)]
    on_ring = [snap(N0.ring.left + 0.45), snap(NX.ring.left + 0.45)]
    for x in on_source + on_ring:
        c.rect("M1", x - 0.14, top - 0.16, x + 0.14, ring_above)
        c.cut("V1", x, yb)
        c.rect("M2", x - 0.25, yb - 0.15, x + 0.25, yb + 0.15)
    for x in on_source:
        c.post(x, Y_POST_N, "M2", "TM1", n=2)
        c.cut("V2", x, yb)
        c.vline("M3", x, Y_POST_N, yb + 0.195, w=0.39)
    for x in on_ring:
        c.post(x, yb, "M2", "TM1")


# ======================================================================
# predriver
# ======================================================================
# TopMetal1 rails.  Each has to cover the posts under it with the 0.42 um
# TV1.d wants around a TopVia1 (0.63 um from a post's centre to the rail's
# edge); this is what they are given.  The top Va rail runs from its posts
# to the top edge, Vss from the stage's NMOS posts to the tails' posts, the
# bottom Va rail from the bottom edge over the stage's PMOS posts.
TM1_MARGIN = 0.8

# Metal3 is kept clear this far either side of the axis: Iref_drv and Vref
# pass down it to the driver (0.3 um wide at axis -/+ 0.36), plus Mn.b.
AXIS_KEEP = 0.36 + 0.15 + 0.21
TM1_VA_BOT = (0.0, 3.0)         # the stage's PMOS sources (posts at y 2.1)


def route_predriver(ly):
    pd = Cell(ly, "predriver")
    stm = pd.child("stm")
    kpm, knm = pd.child("kpm"), pd.child("knm")
    if stm.dcplx_trans.disp != kdb.DVector(0, 0):
        raise SystemExit("predriver_stage is expected at the origin")
    kx = kpm.dcplx_trans.disp.x
    w = pd.width()
    top = pd.cell.dbbox().top

    # the stage decides where its input is: over column 3's gate rails
    stage = Cell(ly, "predriver_stage")
    P0, N0 = stage.dev("Mpp0"), stage.dev("Mnp0")
    lo = max(P0.rails[1].left, N0.rails[0].left)
    hi = min(P0.rails[1].right, N0.rails[0].right)
    In_x = mid(lo, hi)
    comp = Cell(ly, "predriver_comp")
    Mt_k = Dev(ly, comp.child("Mt_0"), "Mt_0")
    route_stage(stage, In_x, (kpm.dcplx_trans * Mt_k.ring).bottom + 0.16)
    gates = route_comp(comp, snap(In_x - kx))
    pd.fill_rails()

    # --- supply rails ----------------------------------------------------
    ky = kpm.dcplx_trans.disp.y
    va_top = (snap(ky + gates["y_va_post"] - TM1_MARGIN), top)
    vss = (snap(Y_POST_N - TM1_MARGIN), snap(ky + gates["y_vss_post"] + TM1_MARGIN))
    for (a0, a1), (b0, b1) in ((TM1_VA_BOT, vss), (vss, va_top)):
        if b0 - a1 < 1.64:                  # TM1.b
            raise SystemExit("TopMetal1 rails %.2f-%.2f and %.2f-%.2f are "
                             "closer than 1.64 um" % (a0, a1, b0, b1))
    for (y0, y1), net in ((va_top, "Va"), (vss, "Vss"), (TM1_VA_BOT, "Va")):
        pd.rect("TM1", 0, y0, w, y1)
        pd.label("TM1", net, 1.0, y0 + 0.5, 2.0, y1 - 0.5)

    # --- D_p / D_n: pins on top, a metal4 bus, drops onto the pair gates -
    kt = kpm.dcplx_trans
    nt = knm.dcplx_trans
    din_k = kt * gates["gate_din"]
    gin_k = kt * gates["gate_gin"]
    din_n = nt * gates["gate_din"]
    gin_n = nt * gates["gate_gin"]
    # kpm: Din = D_n, Gin = D_p;  knm: Din = D_p, Gin = D_n.  Each net:
    # (bus height, x of its two drops, x of its pin).  The three pins sit
    # side by side left of the axis, Iref nearest to it: as far right as
    # the bias lines that pass down the axis (Iref_drv, Vref) allow, D_p and
    # D_n 0.7 um apart to its left.
    x_iref = snap(w / 2 - AXIS_KEEP - 0.15)
    y_rail = mid(din_k.bottom, din_k.top)
    bus = {"D_n": (snap(y_rail + 0.83), [din_k.left + 0.47, gin_n.right - 0.47],
                   snap(x_iref - 1.4)),
           "D_p": (snap(y_rail + 1.43), [gin_k.left + 0.47, din_n.right - 0.47],
                   snap(x_iref - 0.7))}
    for net, (y, drops, x_pin) in bus.items():
        xs = [snap(x) for x in drops]
        pd.hline("M4", y, min(xs + [x_pin]) - 0.15, max(xs + [x_pin]) + 0.15)
        for x in xs:
            pd.cut("V2", x, y_rail)
            pd.vline("M3", x, y_rail - 0.195, y + 0.195, w=0.39)
            pd.cut("V3", x, y)
        pd.vline("M3", x_pin, y - 0.195, top)
        pd.cut("V3", x_pin, y)
        pd.label("M3", net, x_pin - 0.15, top - 0.5, x_pin + 0.15, top)

    # --- Iref: Mref sits between the two comparators, level with their
    # tails.  The four tail halves are contacted at the bottom only, and
    # their bottom gate rails and Mref's are at one height: one metal2 bar
    # through all five.  Mref's drain is its gate, and the pin comes down
    # just left of the axis onto its top rail ---------------------------
    Mref = pd.dev("Mref")
    rb, rt = Mref.rails
    tails = [t * r for t in (kt, nt) for r in gates["tail_rails"]]
    if any(abs(r.bottom - rb.bottom) > 1e-3 or abs(r.top - rb.top) > 1e-3
           for r in tails):
        raise SystemExit("the tails' gate rails and Mref's are no longer at "
                         "one height -- the Iref bar assumes they are")
    pd.rect("M2", min(r.left for r in tails), rb.bottom,
            max(r.right for r in tails), rb.top)
    d = Mref.stripes["D"][0]
    yd = d.bottom + 0.3
    pd.cut("V1", mid(d.left, d.right), yd)
    pd.rect("M2", d.left - 0.02, rb.top - 0.05, d.right + 0.02, yd + 0.3)
    # the pin lands on Mref's top gate rail, lengthened towards it if short
    pd.rect("M2", min(rt.left, x_iref - 0.24), rt.bottom, rt.right, rt.top)
    pd.cut("V2", x_iref, mid(rt.bottom, rt.top))
    pd.vline("M3", x_iref, mid(rt.bottom, rt.top) - 0.195, top)
    pd.label("M3", "Iref", x_iref - 0.15, top - 0.5, x_iref + 0.15, top)
    # Mref's source to its own ring (Vss); the ring reaches Vss through the
    # stage's metal1 bridges below, which land on its bottom bar
    s = Mref.stripes["S"][0]
    ys = mid(s.bottom, s.top)
    pd.cut("V1", mid(s.left, s.right), ys)
    xr = Mref.ring.right - 0.16
    pd.rect("M1", xr, ys - 0.2, Mref.ring.right + 0.32, ys + 0.2)
    pd.cut("V1", Mref.ring.right + 0.13, ys)
    pd.rect("M2", s.left - 0.02, ys - 0.15, Mref.ring.right + 0.29, ys + 0.15)

    # --- pins at the bottom: the stage's outputs are the block's In_p/In_n
    pd.label("M3", "In_p", X_OUT - 0.2, 0.0, X_OUT + 0.2, 0.5)
    pd.label("M3", "In_n", w - X_OUT - 0.2, 0.0, w - X_OUT + 0.2, 0.5)


def main(src=GDS, dst=None):
    dst = dst or src
    ly = kdb.Layout()
    ly.read(src)
    for name in ("predriver", "predriver_comp", "predriver_stage"):
        if ly.cell(name) is None:
            raise SystemExit("%s fehlt in %s" % (name, src))
    if os.path.samefile(os.path.dirname(os.path.abspath(dst)), HERE) \
            and os.path.basename(dst) == "lvds_tx.gds":
        raise SystemExit("lvds_tx.gds gehoert dem Benutzer -- nicht schreiben")
    route_predriver(ly)
    ly.write(dst)
    print("predriver geroutet: %s" % os.path.basename(dst))


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
