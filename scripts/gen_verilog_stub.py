#!/usr/bin/env python3
"""Verilog stub of the top cell from its xschem symbol.

    python3 scripts/gen_verilog_stub.py <cell.sym> <module> <out.vh>

The template took the pin list from a PEX netlist of the layout.  That stopped
working here: vss_1v2 and vss_3v3 share the substrate, so Magic's extraction
reports them shorted and keeps one port - the stub lost vss_1v2.  The symbol
carries the slot-14 frame pin for pin, with directions, and the top-level LVS
compares exactly those pin names against the layout, so it is the better
source anyway.  Supplies go under USE_POWER_PINS; buses are folded back.
"""
import io, re, sys

sym, module, out = sys.argv[1:4]
POWER = re.compile(r"^(vdd|vss)_")
DIRS = {"in": "input", "out": "output", "inout": "inout"}
pins = [(m.group(1), m.group(2)) for m in
        re.finditer(r"^B 5 \S+ \S+ \S+ \S+ \{name=([^ }]+) dir=(\w+)", io.open(sym).read(), re.M)]
assert pins, "no pins in %s" % sym

order, bus = [], {}
for name, d in pins:
    m = re.match(r"^(.*)\[(\d+)\]$", name)
    base, idx = (m.group(1), int(m.group(2))) if m else (name, None)
    if base not in bus:
        order.append(base); bus[base] = (DIRS[d], [])
    if idx is not None:
        bus[base][1].append(idx)

power = [b for b in order if POWER.match(b)]
signal = [b for b in order if not POWER.match(b)]
lines = ["module %s (" % module]
if power:
    lines.append("`ifdef USE_POWER_PINS")
    lines += ["    inout %s," % b for b in power]
    lines.append("`endif")
for i, b in enumerate(signal):
    d, idx = bus[b]
    rng = " [%d:%d]" % (max(idx), min(idx)) if idx else ""
    lines.append("    %s%s %s%s" % (d, rng, b, "," if i < len(signal) - 1 else ""))
lines += [");", "endmodule", ""]
io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("wrote %s: %d pins (%d power)" % (out, len(pins), len(power)))
