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
  xiref_pd, xiref_drv, xodt, XDRST), the pattern pair core_p / core_n, the
  mirror outputs iref_pd_30u / iref_drv_30u; inside lvds_tx (pex only) the
  pre-driver pair In_p / In_n and the CMFB node xdrv.cmfb - the paths
  x1.xlvds.In_p and x1.xlvds.xdrv.cmfb then read as in the schematic.
* pex: every extracted cell gets a pex_ prefix, so the standard cells as laid
  out cannot clash with the library's own definitions a bench includes.
* wires: a block is called by its schematic port order, matched by name; a
  coupling capacitance from a top-level net to a node inside a block (which
  the schematic block does not have) goes to ground instead, so every
  top-level net keeps its total capacitance.
"""
import io, re, sys

RAW, SCH, SYM, OUTDIR = sys.argv[1:5]
TOP = "slot_14"
GROUNDS = ("vss_1v2", "vss_3v3")
BLOCKS = {"xpat": "lvds_pattern", "xlvds": "lvds_tx", "xiref_pd": "iref_x15",
          "xiref_drv": "iref_x15", "xodt": "ref_odt"}
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


# ------------------------------------------------------------------ pex: everything extracted
pfx = lambda s: "pex_" + s if s in cells and s != TOP else s
pex = header("everything as laid out, every block from its own extraction")
for cname, cports, cbody in raw:
    if cname == TOP:
        continue
    ren = TX_NETS if cname == "lvds_tx" else {}
    pex.append(".subckt %s %s" % (pfx(cname), " ".join(ren.get(p, p) for p in cports)))
    for t in cbody:
        nodes, rest = card_nodes(t, cells)
        if t[0][0] in "Xx":
            rest = [pfx(rest[0])] + rest[1:]
        pex.append(" ".join([t[0]] + [ren.get(n, n) for n in nodes] + rest))
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
