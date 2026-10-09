#!/usr/bin/env python3
"""Two simulation netlists of slot_14 from one hierarchical magic extraction.

    python3 scripts/sim/pex_top.py <raw.spice> <schematic.spice> <symbol.sym> <outdir>

<raw.spice> is magic's ext2spice output of layout/slot_14.gds, hierarchical, with
coupling capacitance (scripts/sim/extract_top.sh); <schematic.spice> xschem's
netlist of schematic/xschem/slot_14.sch with every subcircuit below it.  Writes

  slot_14_pex.spice    everything as laid out: every block from its own
                       extraction, the top-level wiring with its capacitance
                       (.subckt slot_14_pex)
  slot_14_wires.spice  the top-level wiring as laid out, the blocks from their
                       schematics (.subckt slot_14_wires) - what the wiring
                       between the pads and the blocks adds, on its own

Both take the 56 pins in the order of <symbol.sym>, so the primitive symbols
slot_14_pex.sym / slot_14_wires.sym drop into a bench in place of slot_14.sym.

What changes on the way:
* vss_1v2 and vss_3v3 come out of the extraction as one net (every tap sits in
  the same substrate; the harness ties them too): the missing one is a port
  again, joined to the other by 1 mohm.
* names a bench can use: the instances as in the schematic (xpat, xlvds,
  xiref_pd, xiref_drv, xodt, xbt, XDRST), the pattern pair core_p / core_n, the
  mirror outputs iref_pd_30u / iref_drv_30u; inside lvds_tx (pex only) the
  pre-driver pair In_p / In_n and the CMFB node xdrv.cmfb - the paths
  x1.xlvds.In_p and x1.xlvds.xdrv.cmfb then read as in the schematic.
* pex: magic leaves the n-diode of ref_odt (DN) and of every antennanp open -
  joined to X / A again, the nets the KLayout LVS connects them to (below);
  ref_odt's switch gate and the node behind R1 are enh and x, as in the
  schematic, so x1.xodt.enh / x1.xodt.x read the same in every bench.
* both: capacitors onto nodes that touch no device anywhere are dropped -
  magic's hierarchical corrections on child nets it did not pass out as ports
  (below); held only by capacitors, many negative, they made the run unstable.
* pex: every extracted cell gets a pex_ prefix, so the standard cells as laid
  out cannot clash with the library's own definitions a bench includes.
* wires: a block is called by its schematic port order, matched by name; a
  coupling capacitance from a top-level net to a node inside a block (which
  the schematic block does not have) goes to ground instead, so every
  top-level net keeps its total capacitance.
"""
import io, os, re, sys

RAW, SCH, SYM, OUTDIR = sys.argv[1:5]
TOP = "slot_14"
GROUNDS = ("vss_1v2", "vss_3v3")
BLOCKS = {"xpat": "lvds_pattern", "xlvds": "lvds_tx", "xiref_pd": "iref_x15",
          "xiref_drv": "iref_x15", "xodt": "ref_odt", "xbt": "lvds_bt"}
TOP_NETS = {"xpat/D_p": "core_p", "xpat/D_n": "core_n",
            "xlvds/Iref_pd": "iref_pd_30u", "xlvds/Iref_drv": "iref_drv_30u"}
TX_NETS = {"pd/In_p": "In_p", "pd/In_n": "In_n", "drv/x_cmfb/cmfb": "xdrv.cmfb"}


def logical(text):
    return text.replace("\r", "").replace("\n+", " ").split("\n")


def blocks(lines):
    """[(name, ports, body lines)] for every .subckt, in file order"""
    out, cur = [], None
    for l in lines:
        t = l.split()
        if not t:
            continue
        if t[0].lower() == ".subckt":
            cur = (t[1], t[2:], [])
        elif t[0].lower() == ".ends":
            out.append(cur); cur = None
        elif cur is not None and not l.startswith("*"):
            cur[2].append(t)
    return out


def card_nodes(t, subckts):
    """(nodes, rest) of one element card: C/R/D/V take two nodes, X its nodes up to the
    subcircuit or model name (the last token before the first name=value)"""
    if t[0][0] in "CcRrDdVv":
        return t[1:3], t[3:]
    k = next((i for i, x in enumerate(t) if "=" in x), len(t))
    return t[1:k - 1], t[k - 1:]


def clean(n):
    return n.replace("[", "_").replace("]", "_")


raw = blocks(logical(io.open(RAW, encoding="utf-8").read()))
cells = {b[0]: b for b in raw}
assert TOP in cells, "no .subckt %s in %s" % (TOP, RAW)
pins = [m.group(1) for m in re.finditer(r"^B 5 \S+ \S+ \S+ \S+ \{name=([^ }]+)",
                                        io.open(SYM, encoding="utf-8").read(), re.M)]
assert len(pins) == 56, len(pins)

# ------------------------------------------------------------------ the top cell
name, ports, body = cells[TOP]
missing = [p for p in pins if p not in ports]
assert all(p in GROUNDS for p in missing), "pins the extraction lost: %s" % missing
assert not set(ports) - set(pins), "ports the symbol lacks: %s" % (set(ports) - set(pins))
ground = next(g for g in GROUNDS if g in ports)
net = lambda n: clean(TOP_NETS.get(n, n))


def rename_inst(inst, sub):
    if sub == "ref_odt":
        return "xodt"
    if sub == "lvds_bt":
        return "xbt"
    if sub == "dantenna":
        return "XDRST"
    return inst[1:] if inst[:2] in ("Xx", "XX") else inst


top_cards = []                       # (kind, name, nodes, rest) with the new names
for t in body:
    nodes, rest = card_nodes(t, cells)
    kind = t[0][0].upper()
    inst = rename_inst(t[0], rest[0]) if kind == "X" else t[0]
    top_cards.append((kind, inst, [net(n) for n in nodes], rest))
found = set(i for k, i, n, r in top_cards if k == "X")
assert set(BLOCKS) <= found and "XDRST" in found, sorted(found)[:12]
# the ODT switch's gate is a port of the extracted ref_odt (the top level couples
# to it), so its node carries the parent's name: call it xodt.enh there, which
# flattens to x1.xodt.enh - the name the schematic gives it
odt = next(c for c in top_cards if c[1] == "xodt")
gate = odt[2][cells["ref_odt"][1].index("ref_odt_lvlup_0/o")]
top_cards = [(k, i, ["xodt.enh" if v == gate else v for v in nn], r) for k, i, nn, r in top_cards]


def header(title):
    return ["* %s - %s" % (TOP, title),
            "* written by scripts/sim/pex_top.py from a magic extraction of layout/slot_14.gds",
            "* metal islands that only coupling capacitance reaches would leave the operating",
            "* point singular",
            ".option rshunt=1e12", ""]


def top_lines(subname, cards):
    out = [".subckt %s %s" % (subname, " ".join(clean(p) for p in pins))]
    for g in missing:
        out.append("Rjoin_%s %s %s 1m" % (g, g, ground))
    for kind, inst, nodes, rest in cards:
        out.append(" ".join([inst] + nodes + rest))
    out.append(".ends")
    return out


# ------------------------------------------------------------------ magic's open n-diodes
# Magic reads the contacts of some n+ diodes (dantenna) as not touching their
# metal1: the diode's diffusion comes out as a node of its own that only a
# coupling capacitance reaches - DN of ref_odt, the n-diode of every
# sg13cmos5l_antennanp.  The layout has the contacts (the same as on the
# dpantenna next to them, which magic does connect) and the KLayout LVS sees the
# connection, so the node is joined to the net it couples to most: X and A.
EXPECT = {"ref_odt": lambda ports, body: next(
              n for t in body if card_nodes(t, cells)[1][0] == "rppd"
              for n in card_nodes(t, cells)[0][:2] if n != "PAD"),
          "sg13cmos5l_antennanp": lambda ports, body: "A"}
JOIN = {}                            # cell -> {open diode node: the net it belongs to}
for cname, cports, cbody in raw:
    use = {}
    for t in cbody:
        if t[0][0] not in "Cc":
            for n in card_nodes(t, cells)[0]:
                use[n] = use.get(n, 0) + 1
    for t in cbody:
        nodes, rest = card_nodes(t, cells)
        if rest[0] != "dantenna" or use[nodes[1]] > 1 or nodes[1] in cports:
            continue
        caps = [(float(re.sub(r"[a-z]+$", "", c[3]) or 0) * {"f": 1, "a": 1e-3, "p": 1e3}.get(c[3][-1], 1),
                 c[2] if c[1] == nodes[1] else c[1])
                for c in cbody if c[0][0] in "Cc" and nodes[1] in c[1:3]]
        net = max(caps)[1]
        assert cname in EXPECT, "%s: open n-diode %s, nearest net %s - check it" % (cname, nodes[1], net)
        assert net == EXPECT[cname](cports, cbody), (cname, nodes[1], net)
        JOIN.setdefault(cname, {})[nodes[1]] = net
# ref_odt: the gate of the switch and the node behind R1, by their schematic names
x_odt = EXPECT["ref_odt"](cells["ref_odt"][1], cells["ref_odt"][2])
ODT_NETS = {x_odt: "x", "ref_odt_lvlup_0/o": "enh"}
for k, v in list(JOIN.get("ref_odt", {}).items()):
    JOIN["ref_odt"][k] = ODT_NETS.get(v, v)

# ------------------------------------------------------------------ magic's floating correction nodes
# The hierarchical extraction puts capacitance - much of it negative, the
# corrections for what a parent's metal shields in a child - on nodes named
# after a child's internal net (x_hbridge/M6/S9 in Driver, and up through
# lvds_tx to the top) without passing that net out of the child as a port.
# The node then touches no device anywhere: an island held only by
# capacitors, many of them with a negative total - which makes the transient
# unstable (timestep too small at ~0.5 us).  Their capacitors are dropped:
# they load nothing as extracted.  A node counts as connected when a device
# touches it in its cell or below, or, for a port, when the net it is given
# is connected in the cell above.
DEV = {}
for cname, cports, cbody in raw:
    dev, calls = set(), []
    for t in cbody:
        if t[0][0] in "Cc":
            continue
        nodes, rest = card_nodes(t, cells)
        if t[0][0] in "Xx" and rest[0] in cells:
            calls.append((nodes, rest[0]))
        else:
            dev |= set(nodes)
    DEV[cname] = (dev, calls)
CONN = {}


def conn(cname, node):
    key = (cname, node)
    if key not in CONN:
        dev, calls = DEV[cname]
        CONN[key] = node in dev or any(
            n == node and conn(sub, cells[sub][1][i]) for nodes, sub in calls for i, n in enumerate(nodes))
    return CONN[key]


sys.setrecursionlimit(10000)
topo, seen = [], set()


def visit(c):
    if c in seen:
        return
    seen.add(c)
    for nodes, sub in DEV[c][1]:
        visit(sub)
    topo.append(c)


visit(TOP)
topo.reverse()                                           # every parent before its children
port_live = {c: set() for c in cells}
FLOAT = {}
for c in topo:
    allnodes = set(cells[c][1]) | set(n for t in cells[c][2] for n in card_nodes(t, cells)[0])
    FLOAT[c] = set(n for n in allnodes if not conn(c, n)
                   and (c == TOP or n not in cells[c][1] or n not in port_live[c]))
    for nodes, sub in DEV[c][1]:
        for i, n in enumerate(nodes):
            if n not in FLOAT[c]:
                port_live[sub].add(cells[sub][1][i])
float_caps = sum(1 for c in cells for t in cells[c][2] if t[0][0] in "Cc"
                 and set(card_nodes(t, cells)[0]) & FLOAT.get(c, set()))
FLOAT_TOP = set(clean(TOP_NETS.get(n, n)) for n in FLOAT[TOP])          # the top level's names, as in top_cards
top_cards = [(k, i, nn, r) for k, i, nn, r in top_cards if not (k == "C" and set(nn) & FLOAT_TOP)]

# ------------------------------------------------------------------ pex: everything extracted
pfx = lambda s: "pex_" + s if s in cells and s != TOP else s
pex = header("everything as laid out, every block from its own extraction")
for cname, cports, cbody in raw:
    if cname == TOP:
        continue
    ren = dict(TX_NETS if cname == "lvds_tx" else ODT_NETS if cname == "ref_odt" else {})
    ren.update(JOIN.get(cname, {}))
    pex.append(".subckt %s %s" % (pfx(cname), " ".join(ren.get(p, p) for p in cports)))
    for t in cbody:
        nodes, rest = card_nodes(t, cells)
        if t[0][0] in "Cc" and set(nodes) & FLOAT.get(cname, set()):
            continue                 # onto an island magic left unconnected (above)
        if t[0][0] in "Xx":
            rest = [pfx(rest[0])] + rest[1:]
        nodes = [ren.get(n, n) for n in nodes]
        if t[0][0] in "Cc" and nodes[0] == nodes[1]:
            continue                 # the coupling of a joined diode to its own net
        pex.append(" ".join([t[0]] + nodes + rest))
    pex.append(".ends")
pex += top_lines(TOP + "_pex", [(k, i, n, [pfx(r[0])] + r[1:] if k == "X" else r)
                                for k, i, n, r in top_cards])
io.open(OUTDIR + "/slot_14_pex.spice", "w", encoding="utf-8", newline="\n").write("\n".join(pex) + "\n")

# ------------------------------------------------------------------ wires: the blocks from their schematics
sch_lines = logical(io.open(SCH, encoding="utf-8").read())
sch = blocks(sch_lines)
sch_ports = {b[0]: b[1] for b in sch}
real = set(clean(p) for p in pins) | set(GROUNDS)       # nets a schematic block can see
wired = []
for kind, inst, nodes, rest in top_cards:
    if kind == "X" and rest[0] in sch_ports or kind == "X" and rest[0].startswith("sg13cmos5l_"):
        sub = rest[0]
        by_name = dict(zip(cells[sub][1], nodes))
        order = sch_ports.get(sub) or cells[sub][1]      # library cells: the extracted order is theirs
        lost = [p for p in order if p not in by_name]
        assert not lost, "%s (%s): no %s in the extraction" % (inst, sub, lost)
        wired.append((kind, inst, [by_name[p] for p in order], rest))
        real |= set(by_name[p] for p in order)
    else:
        wired.append((kind, inst, nodes, rest))
        if kind != "C":
            real |= set(nodes)
caps_moved = caps_dropped = 0
cards = []
for kind, inst, nodes, rest in wired:
    if kind == "C":
        inside = [n not in real for n in nodes]
        if all(inside):
            caps_dropped += 1
            continue
        if any(inside):
            nodes = [ground if i else n for n, i in zip(nodes, inside)]
            caps_moved += 1
    cards.append((kind, inst, nodes, rest))
wires = header("the top-level wiring as laid out, the blocks from their schematics")
wires += top_lines(TOP + "_wires", cards)
wires += ["", "* the blocks, as xschem netlists schematic/xschem/slot_14.sch"]
keep, skip = [], False
for l in io.open(SCH, encoding="utf-8").read().replace("\r", "").split("\n"):
    low = l.strip().lower()
    if low.startswith(".subckt %s " % TOP):
        skip = True
    if not skip and low not in (".end",):
        keep.append(l)
    if skip and low.startswith(".ends"):
        skip = False
wires += keep
io.open(OUTDIR + "/slot_14_wires.spice", "w", encoding="utf-8", newline="\n").write("\n".join(wires) + "\n")

nc = lambda lines: sum(1 for l in lines if l[:1] == "C")
print("  slot_14_pex.spice    %5d C, %d cells" % (nc(pex), len(raw)))
print("  slot_14_wires.spice  %5d C on the top-level wiring (%d to block internals now to ground, %d inside blocks dropped)"
      % (nc(wires), caps_moved, caps_dropped))
print("  %s joined to %s" % (", ".join(missing) or "nothing", ground))
print("  %d capacitors onto floating islands dropped (%s)" % (float_caps, ", ".join(
    "%s %d" % (c, len(FLOAT[c])) for c in topo if FLOAT.get(c))))
for cname, j in sorted(JOIN.items()):
    print("  %s: open n-diode joined to %s (magic, see above)" % (cname, ", ".join(sorted(set(j.values())))))
if os.environ.get("PEX_DEBUG"):
    for c in topo:
        if FLOAT.get(c):
            print("FLOAT", c, len(FLOAT[c]), sorted(FLOAT[c])[:6])
