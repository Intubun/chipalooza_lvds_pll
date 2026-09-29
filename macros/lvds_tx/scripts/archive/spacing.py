"""How close two device cells may sit, measured by the sign-off deck.

Every leaf cell carries its own guard ring, and what decides how near two of
them can come is not the ring but the layers around it.  The numbers below
were not read from the rule manual but measured: every pair of kinds, side
by side and on top of each other, at gaps from -1.4 to +2.0 um in 0.05 um
steps, through KLayout's sign-off DRC (`run_drc.py --no_density`).  Gaps are
between the .mag bounding boxes, which is what the placer works with.

    pmos  the nwell is the bounding box; ThickGateOx sits 0.35 um inside it,
          the n+ tap ring 0.62 um.  Two separate nwells need 1.8 um (NW.b1:
          the deck cannot tell that both are Va), and every gap below that is
          dirty -- until the cells overlap by 0.70 to 1.00 um: then nwell and
          ThickGateOx have merged (TGO.e) and the tap rings are still 0.24 to
          0.54 um apart.
    nmos  ThickGateOx is 0.04 um inside the box, pSD 0.28, the p+ ring 0.31.
          0.8 um apart, or overlapping by 0.10 to 0.25 um, where ThickGateOx
          has merged and pSD has not yet run into the other ring.
    pmos-nmos  0.5 um (NW.f1, TGO.e).  They cannot merge.
    rhigh, cap_cmomf  0 um to anything, except two MOM caps: 0.25 um.

Merging is right electrically too: every pmos bulk in lvds_tx is Va and
every nmos bulk Vss.  The rings themselves never touch.

Merging needs the two cells to face each other along a real length: with
only a corner overlapping, the ThickGateOx of the two would end up close
without merging.  MERGE_FACE asks for enough common edge that the joint in
ThickGateOx is itself as wide as TGO.f (0.86 um): 0.86 + 2 x 0.35 for pmos,
0.86 + 2 x 0.04 for nmos, rounded up.

Once merged, two pmos are one nwell, and so is anything merged to either of
them: between two parts of the same nwell the rule is NW.b, 0.62 um (space
or notch, same net), not NW.b1's 1.8.  That is what lets a narrow pmos sit
between two others that both merge into it -- they are 1.64 um apart above
it, and legal.  ThickGateOx is 0.35 um inside the nwell on either side, so
its own notch (0.86) is met from 0.16 um on.  An nmos gains nothing from
this: its ThickGateOx notch is what sets the 0.8.

Two cells of the same kind can also share their guard ring: overlapped by
exactly 1.54 um (pmos) or 0.92 um (nmos), the contact bar of one ring lies
on the contact bar of the other -- 0.69..0.85 um inside the box for pmos,
0.38..0.54 um for nmos -- and so do the tap diffusions around them.  Measured
the same way, for every pair of equal cells in the layout, side by side and
stacked, turned and mirrored: clean at exactly that overlap, dirty 5 nm
either side of it.  So it is only allowed where the placer can hit it
exactly, between two cells that are equally long along the shared edge and
flush at both ends; otherwise the contact cuts of the two rings would not
coincide.
"""
from collections import namedtuple

from magfile import u

# model -> kind
KIND = {"sg13_hv_pmos": "p", "sg13_lv_pmos": "p",
        "sg13_hv_nmos": "n", "sg13_lv_nmos": "n",
        "rhigh": "r", "rsil": "r", "rppd": "r",
        "cap_cmomf": "c"}

# Least gap that is clean without merging, in internal units.
_PLAIN = {("p", "p"): 1.80, ("n", "n"): 0.80, ("n", "p"): 0.50,
          ("p", "r"): 0.0, ("n", "r"): 0.0, ("r", "r"): 0.0,
          ("c", "p"): 0.0, ("c", "n"): 0.0, ("c", "r"): 0.0,
          ("c", "c"): 0.25}
PLAIN = {k: u(v) for k, v in _PLAIN.items()}

# Overlap at which two cells of the same kind merge cleanly: (window, used).
# The window is the measured one shrunk by 0.05 um at either end; `used` is
# the value the placer aims for, its middle.
MERGE = {"p": ((u(-0.95), u(-0.75)), u(-0.85)),
         "n": ((u(-0.20), u(-0.15)), u(-0.175))}
MERGE_FACE = {"p": u(1.8), "n": u(1.0)}

# Least gap between two shapes that are part of the same merged region.
CONNECTED = {"p": u(0.62)}

# Overlap at which two equal edges share one guard ring, exactly.
SHARE = {"p": u(1.54), "n": u(0.92)}

# Overlap at which two cells whose guard rings are open towards each other
# (patch_cells.py: _open) meet, the lower one open to the north, the upper
# one to the south, equally wide and flush at both ends: their rings' side
# bars run into each other and become one ring round both, with nothing
# between the two FETs.  Measured like SHARE, on the comparator's tail
# under its input pair (same l, same fingers): clean at exactly 1.56 um
# between the .mag boxes (1.17 um between the GDS boxes, which sit inside
# them differently at the open side) and dirty 5 nm either side -- one step
# less and the ThickGateOx the two open sides leave notched does not close
# (TGO.e), one step more and the gate poly tips of the two rows, finger
# above finger, come closer than 0.18 um (Gat.b) -- and at 0.18 um more,
# they would short.  Only measured for that pair: other cells need their
# own measurement (the sign-off DRC will say so).
JOIN = {"n": u(1.56)}

# The deepest any block may be pushed into another.
MAX_OVERLAP = u(1.6)

# `opens`: the sides ("n", "s", "e", "w") on which the cell's guard ring is
# open, in the frame the shape is in.
Shape = namedtuple("Shape", "x0 y0 x1 y1 kind merge opens", defaults=("",))

# Where each side of a cell ends up when it is placed turned or mirrored,
# by KLayout's orientation names.
_TURN = {"r0": "nsew", "r90": "wens", "r180": "snwe", "r270": "ewsn",
         "m0": "snew", "m90": "nswe", "m45": "ewns", "m135": "wesn"}


def turned(opens, orient):
    """The open sides of a cell once placed with `orient`."""
    return "".join(sorted(_TURN[orient]["nsew".index(c)] for c in opens))


def plain(a, b):
    return PLAIN[tuple(sorted((a, b)))]


def _d(a, b):
    """Gap along x and along y: > 0 apart, < 0 overlapping."""
    return (max(b.x0 - a.x1, a.x0 - b.x1), max(b.y0 - a.y1, a.y0 - b.y1))


def shared(a, b):
    """True if a and b sit on one common guard ring."""
    if not (a.kind == b.kind and a.kind in SHARE and a.merge and b.merge):
        return False
    dx, dy = _d(a, b)
    if dx == -SHARE[a.kind] and a.y0 == b.y0 and a.y1 == b.y1:
        return True
    return dy == -SHARE[a.kind] and a.x0 == b.x0 and a.x1 == b.x1


def joined(a, b):
    """True if a and b meet on their open ring sides (JOIN)."""
    if not (a.kind == b.kind and a.kind in JOIN and a.merge and b.merge):
        return False
    if a.x0 != b.x0 or a.x1 != b.x1:
        return False
    low, high = (a, b) if a.y0 < b.y0 else (b, a)
    return ("n" in low.opens and "s" in high.opens
            and high.y0 - low.y1 == -JOIN[a.kind])


def merged(a, b):
    """True if a and b overlap the way that makes them one region."""
    if not (a.kind == b.kind and a.kind in MERGE and a.merge and b.merge):
        return False
    if shared(a, b) or joined(a, b):
        return True
    dx, dy = _d(a, b)
    (lo, hi), _ = MERGE[a.kind]
    face = MERGE_FACE[a.kind]
    if -dy >= face and lo <= dx <= hi:
        return True
    if -dx >= face and lo <= dy <= hi:
        return True
    # corner on corner, both overlaps in the window: what happens between
    # M6_0 and M10 when both merge into M11 and M9
    return lo <= dx <= hi and lo <= dy <= hi


def ok(a, b, connected=False):
    """True if shapes a and b may sit where they are.  `connected` says
    they belong to one merged region already, through other shapes."""
    dx, dy = _d(a, b)
    need = plain(a.kind, b.kind)
    if connected and a.kind == b.kind and a.kind in CONNECTED \
            and a.merge and b.merge:
        need = min(need, CONNECTED[a.kind])
    return dx >= need or dy >= need or merged(a, b)


def regions(shapes):
    """Index of the merged region each shape belongs to."""
    parent = list(range(len(shapes)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            if merged(shapes[i], shapes[j]):
                parent[root(i)] = root(j)
    return [root(i) for i in range(len(shapes))]


def gaps_to_try(a, b):
    """The gaps worth trying between a and b: plain, merged, a shared
    guard ring, and the one that holds when they are merged through
    something else."""
    out = [plain(a.kind, b.kind)]
    if a.kind == b.kind and a.kind in MERGE and a.merge and b.merge:
        out.append(MERGE[a.kind][1])
        out.append(-SHARE[a.kind])
        if a.kind in CONNECTED:
            out.append(CONNECTED[a.kind])
        if a.kind in JOIN and a.opens and b.opens:
            out.append(-JOIN[a.kind])
    return out


def moved(shapes, dx, dy):
    return [s._replace(x0=s.x0 + dx, y0=s.y0 + dy, x1=s.x1 + dx, y1=s.y1 + dy)
            for s in shapes]


def combine(shapes):
    """Shapes on a common guard ring, as the one rectangle they form.

    To a neighbour, two cells that share a ring are one block: where four of
    them meet on the axis -- M1|M3 on M6_0|M6_1 -- M1 overlaps M6_1 only
    along the 0.92 um of the shared ring, too short a joint on its own, but
    that strip lies inside the shared ring below and is the same geometry as
    M1 on M6_0.  Returns [(shape, members)], members being the originals."""
    parent = list(range(len(shapes)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            if shared(shapes[i], shapes[j]):
                parent[root(i)] = root(j)
    groups = {}
    for i, s in enumerate(shapes):
        groups.setdefault(root(i), []).append(s)
    out = []
    for members in groups.values():
        if len(members) == 1:
            out.append((members[0], members))
            continue
        # open on a side only if every member is: then the block can join
        opens = set(members[0].opens)
        for m in members[1:]:
            opens &= set(m.opens)
        out.append((Shape(min(m.x0 for m in members), min(m.y0 for m in members),
                          max(m.x1 for m in members), max(m.y1 for m in members),
                          kind=members[0].kind, merge=True,
                          opens="".join(sorted(opens))), members))
    return out


def _pairs_ok(pairs, everything):
    """All (a, b) legal, allowing the NW.b gap inside one merged region."""
    bad = [(a, b) for a, b in pairs if not ok(a, b)]
    if not bad:
        return True
    if any(a.kind != b.kind or a.kind not in CONNECTED for a, b in bad):
        return False
    region = dict(zip(map(id, everything), regions(everything)))
    return all(region[id(a)] == region[id(b)] and ok(a, b, connected=True)
               for a, b in bad)


def legal(fixed, moving):
    f = [s for s, _ in combine(list(fixed))]
    m = [s for s, _ in combine(list(moving))]
    pairs = [(a, b) for a in f for b in m]
    # a moving cell that shares its ring with a fixed one is checked as it is
    direct = set()
    for a in fixed:
        for b in moving:
            if shared(a, b):
                direct.add(id(a))
                direct.add(id(b))
    if direct:
        f = [s for s, mem in combine(list(fixed))
             if not any(id(x) in direct for x in mem)] +             [a for a in fixed if id(a) in direct]
        m = [s for s, mem in combine(list(moving))
             if not any(id(x) in direct for x in mem)] +             [b for b in moving if id(b) in direct]
        pairs = [(a, b) for a in f for b in m]
    return _pairs_ok(pairs, f + m)


def slide(fixed, moving, axis):
    """Least offset along `axis` ("x" or "y") at which `moving` may sit
    after `fixed`: every pair legal, and nothing pushed deeper than
    MAX_OVERLAP into what it faces.  `moving` is given at offset 0."""
    lo_i, hi_i = (0, 2) if axis == "x" else (1, 3)
    other = (1, 3) if axis == "x" else (0, 2)

    def facing(a, b):
        return min(a[other[1]], b[other[1]]) > max(a[other[0]], b[other[0]])

    floor = None
    candidates = set()
    for a in fixed:
        for b in moving:
            if facing(a, b):
                bound = a[hi_i] - MAX_OVERLAP - b[lo_i]
                floor = bound if floor is None else max(floor, bound)
            for g in gaps_to_try(a, b):
                candidates.add(a[hi_i] + g - b[lo_i])
    if floor is None:
        floor = min(candidates) if candidates else 0
    candidates.add(floor)
    for t in sorted(c for c in candidates if c >= floor):
        shifted = moved(moving, t, 0) if axis == "x" else moved(moving, 0, t)
        if legal(fixed, shifted):
            return t
    raise SystemExit("no legal position found")   # pragma: no cover


def violations(groups):
    """Pairs of groups whose shapes sit too close.

    `groups` is {name: [Shape]}; shapes within one group were checked when
    that group was built.  Cells on a common guard ring count as one block.
    """
    owner = {}
    shapes = []
    for n in sorted(groups):
        for s in groups[n]:
            owner[id(s)] = n
            shapes.append(s)
    blocks = combine(shapes)
    names = [sorted({owner[id(m)] for m in mem}) for _, mem in blocks]
    everything = [b for b, _ in blocks]
    bad = []
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            if len(names[i]) == 1 and names[i] == names[j]:
                continue            # inside one group, checked already
            if not _pairs_ok([(blocks[i][0], blocks[j][0])], everything):
                bad.append(("+".join(names[i]), "+".join(names[j])))
    return bad
