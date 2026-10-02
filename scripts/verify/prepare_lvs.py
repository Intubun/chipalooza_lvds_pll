#!/usr/bin/env python3
"""Reference netlist and layout for the top-level LVS, without Rahul's PLL.

    prepare_lvs.py <run_dir> <schematic.cdl> <layout.gds> <stdcell.cdl>

Writes <run_dir>/reference.cdl and <run_dir>/layout.gds.

The PLL is left out on both sides until it is finished: the schematic models
it as pll_cosim, an XSPICE d_cosim block that no LVS reads, and its layout is
still changing.  On the schematic side the instance xpll goes, together with
every subcircuit only it used and the simulator lines (.lib, .include, .model,
XSPICE A-elements); on the layout side the instance of the cell `pll` goes.
Whatever the top level routes to the PLL then ends in a dangling wire, which
LVS sees as part of the net it belongs to - the comparison of everything else
is unaffected.  The standard cells (lvds_pattern) come from the PDK's CDL.
"""
import sys
import klayout.db as kdb

TOP = "sg13cmos5l_chipalooza_analog_project"
PLL_INST = "xpll"          # schematic instance
PLL_CELL = "pll"           # layout cell

run, cdl, gds, std = sys.argv[1:5]

# ---- schematic -------------------------------------------------------------
joined = []
for l in open(cdl).read().split("\n"):
    if l.startswith("+") and joined:
        joined[-1] += " " + l[1:].strip()
    else:
        joined.append(l)
blocks, cur, outside = {}, None, []
for l in joined:
    low = l.strip().lower()
    if low.startswith(".subckt"):
        cur = l.split()[1]; blocks[cur] = [l]
        continue
    if cur is not None:
        blocks[cur].append(l)
        if low.startswith(".ends"):
            cur = None
    else:
        outside.append(l)
assert TOP in blocks, "no .subckt %s in %s" % (TOP, cdl)
pll = [l for l in blocks[TOP] if l.split() and l.split()[0].lower() == PLL_INST]
if len(pll) != 1:
    sys.exit("expected one instance %s in %s, found %d" % (PLL_INST, TOP, len(pll)))
blocks[TOP] = [l for l in blocks[TOP] if l not in pll]


def is_sim_line(l):
    t = l.strip().lower()
    return t.startswith((".lib", ".include", ".model", ".option", ".param")) or t[:1] == "a"


def children(name):
    out = []
    for l in blocks[name][1:]:
        p = l.split()
        if p and p[0][:1].lower() == "x":
            cell = [t for t in p[1:] if "=" not in t][-1]
            if cell in blocks:
                out.append(cell)
    return out


keep, todo = set(), [TOP]
while todo:
    n = todo.pop()
    if n not in keep:
        keep.add(n); todo += children(n)
dropped = sorted(n for n in blocks if n not in keep)
with open("%s/reference.cdl" % run, "w") as f:
    f.write("* top-level LVS reference, without %s (prepare_lvs.py)\n" % PLL_INST)
    f.write("* left out: %s\n" % " ".join(dropped))
    f.write(open(std).read() + "\n")
    for n, b in blocks.items():
        if n in keep:
            f.write("\n".join(l for l in b if not is_sim_line(l)) + "\n\n")
print("  Schaltplan: %s und %d nur von ihm benutzte Subcircuits entfernt (%s)" % (PLL_INST, len(dropped), ", ".join(dropped)))

# ---- layout ----------------------------------------------------------------
ly = kdb.Layout(); ly.read(gds)
top = ly.cell(TOP)
gone = [i for i in top.each_inst() if ly.cell(i.cell_index).name == PLL_CELL]
for i in gone:
    i.delete()
ly.write("%s/layout.gds" % run)
print("  Layout: %d Instanz(en) von %s entfernt" % (len(gone), PLL_CELL))
