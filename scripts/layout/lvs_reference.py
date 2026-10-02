#!/usr/bin/env python3
"""Build the Netgen reference netlist for a Magic LVS run.

    lvs_reference.py <schematic.spice> <layout.spice> <out.spice>

Magic extracts PDK resistor and MOM-capacitor gencells as their own
subcircuits (dev_rhigh_w1_l22p08, dev_cap_cmomf_w100_l100, ...) holding a
plain R or C, while Xschem writes `rhigh` / `cap_cmomf` primitives. Each such
schematic instance is rewritten to the layout cell whose name encodes the same
w and l, and those cell definitions are copied in from the layout netlist.
Pin order follows the layout cells: rhigh (B R1 R2), cap_cmomf (c1 c2).

If no layout cell has the instance's w/l, the instance is left untouched, so
a sizing difference still makes LVS fail.
"""
import re
import sys

schematic, layout, out = sys.argv[1:4]


def tag(value):
    um = float(re.sub(r"u$", "", value))
    return ("%g" % um).replace(".", "p")


layout_text = open(layout).read()
cells = {}
for m in re.finditer(r"^\.subckt (dev_(rhigh|cap_cmomf)_\S+).*?^\.ends.*?$",
                     layout_text, re.M | re.S):
    cells[m.group(1)] = m.group(0)

used = []
lines = []
for line in open(schematic).read().splitlines():
    tok = line.split()
    if tok and tok[0].upper().startswith("X") and len(tok) > 3:
        params = dict(t.split("=", 1) for t in tok if "=" in t)
        nodes = [t for t in tok[1:] if "=" not in t]
        model = nodes[-1] if nodes else ""
        if model in ("rhigh", "cap_cmomf") and "w" in params and "l" in params:
            name = f"dev_{model}_w{tag(params['w'])}_l{tag(params['l'])}"
            if name in cells:
                if model == "rhigh":       # schematic: R1 R2 B
                    r1, r2, b = nodes[:3]
                    pins = [b, r1, r2]
                else:                      # schematic: c1 c2
                    pins = nodes[:2]
                line = " ".join([tok[0]] + pins + [name])
                used.append(name)
    lines.append(line)

text = "\n".join(lines) + "\n"
defs = "\n".join(cells[n] for n in dict.fromkeys(used))
if defs:
    # Definitions must precede the first .subckt that instantiates them.
    first = re.search(r"^\.subckt ", text, re.M)
    pos = first.start() if first else 0
    text = text[:pos] + defs + "\n" + text[pos:]
open(out, "w").write(text)
