#!/usr/bin/env python3
"""Reference netlist and layout copy for the top-level LVS.

    prepare_lvs.py <run_dir> <schematic.cdl> <layout.gds> <stdcell.cdl>

Writes <run_dir>/reference.cdl and <run_dir>/layout.gds.

The reference is the xschem CDL of the top cell with the PDK's standard-cell
CDL in front of it (lvds_pattern is built from standard cells), keeping only
the subcircuits the top actually uses and none of the simulator lines (.lib,
.include, .model, .option, XSPICE A-elements) - an LVS reader takes none of
those.  The layout is copied as it is, so the run never reads a file KLayout
might be saving at the same moment.

Until 2026-10-07 this also took Rahul's PLL out of both sides (xpll, a d_cosim
model, and the cell `pll`); the PLL has left the project since.
"""
import shutil
import sys

TOP = "slot_14"

run, cdl, gds, std = sys.argv[1:5]

joined = []
for l in open(cdl).read().split("\n"):
    if l.startswith("+") and joined:
        joined[-1] += " " + l[1:].strip()
    else:
        joined.append(l)
blocks, cur = {}, None
for l in joined:
    low = l.strip().lower()
    if low.startswith(".subckt"):
        cur = l.split()[1]; blocks[cur] = [l]
        continue
    if cur is not None:
        blocks[cur].append(l)
        if low.startswith(".ends"):
            cur = None
assert TOP in blocks, "no .subckt %s in %s" % (TOP, cdl)


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
    f.write("* top-level LVS reference (prepare_lvs.py)\n")
    if dropped:
        f.write("* unused, left out: %s\n" % " ".join(dropped))
    f.write(open(std).read() + "\n")
    for n, b in blocks.items():
        if n in keep:
            f.write("\n".join(l for l in b if not is_sim_line(l)) + "\n\n")
print("  Schaltplan: %d Subcircuits%s" % (len(keep), (", unbenutzt weggelassen: " + ", ".join(dropped)) if dropped else ""))
shutil.copy2(gds, "%s/layout.gds" % run)
