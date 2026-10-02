#!/usr/bin/env python3
"""Generate layout/mag/prescaler_inv.mag from PDK gencells + routing.

prescaler_inv: XP PMOS w1.2 ng2 + XN NMOS w0.6 ng1.
  XP Y A VDD VDD  -> dev_p_w0p6_ng2 (0.6x2=1.2u)
  XN Y A VSS VSS  -> dev_n_w0p6_ng1 (0.6x1)

Pattern follows macros/pll_analog/scripts/layout/make_inverter.py:
M2 buses on D/S stripes with offset via1s (M2.b safe), gate() landings,
via23 to M3, wells/taps with NW.e/Cnt.c margins. Units: Magic internal (5nm).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "layout/mag/prescaler_inv.mag"
L = {}


def rect(layer, a, b, c, d):
    L.setdefault(layer, []).append((a, b, c, d))


def rail(cols, center, offset):
    # w0p6 straps are y +/-46 (vs +/-76 for w0p9): vias must sit at
    # center+/-20 so the 40-wide via stays inside the straps (V1.c).
    # Parent M1 pads give the 0.045um V1.c1 enclosure (gencell straps
    # alone are only 10 wide vs the 40 via).
    y = center + offset
    vy = center + (20 if offset > 0 else -20)
    for x in cols:
        rect("metal1", x - 29, vy - 29, x + 29, vy + 29)
        rect("via1", x - 20, vy - 20, x + 20, vy + 20)
        rect("metal2", x - 29, min(vy, y) - 29, x + 29, max(vy, y) + 29)
    rect("metal2", min(cols) - 29, y - 29, max(cols) + 29, y + 29)
    if len(cols) == 1:
        x = cols[0]
        if offset > 0:
            rect("metal2", x - 29, y, x + 29, y + 60)
        else:
            rect("metal2", x - 29, y - 60, x + 29, y)


def pad(layer, x, y):
    rect(layer, x - 29, y - 50, x + 29, y + 50)


def gate(y, halfwidth, xout):
    rect("metal1", min(-halfwidth, xout - 29), y - 20, max(halfwidth, xout + 29), y + 22)
    rect("metal1", xout - 29, y - 29, xout + 29, y + 29)
    rect("via1", xout - 20, y - 20, xout + 20, y + 20)
    pad("metal2", xout, y)


def via23(x, y, landing=False):
    rect("via2", x - 20, y - 20, x + 20, y + 20)
    if landing:
        pad("metal2", x, y)
        pad("metal3", x, y)
    else:
        rect("metal2", x - 29, y - 29, x + 29, y + 29)
        rect("metal3", x - 29, y - 29, x + 29, y + 29)


def m3wire(a, b, c, d):
    rect("metal3", a, b, c, d)


# Placement: PMOS top, NMOS bottom (like inverter M2/M3).
YP, YN = 600, 0
uses = [
    ("dev_p_w0p6_l0p13_ng2_noguard_m1", "XP", 0, YP),
    ("dev_n_w0p6_l0p13_ng1_noguard_m1", "XN", 0, YN),
]

# D/S stripes (M1 coords, from gencell measurement):
#  ng2: diffusions -102,0,+102 -> outers strapped, middle alone.
#  ng1: D -51, S +51.
# PMOS: outers=VDD (2 stripes to supply), middle=Y.
# NMOS: D=Y at -51, S=VSS at +51.
# Supply buses at +/-80 (vs +/-70 signal) for M2.b/M3.b clearance.
rail([-102, 102], YP, 80)   # VDD (PMOS sources)
rail([0], YP, -70)          # Y (PMOS drain, middle)
rail([-51], YN, 70)         # Y (NMOS drain)
rail([51], YN, -80)         # VSS (NMOS source)

# NOTE: no min-area widening rects on the PMOS bottom gate rail (its 3-pad
# row passes M1.d alone). The NMOS single-finger bottom rail needs one;
# it is gate net (touches only the bottom gate pads at the same y).
rect("metal1", -60, YN - 150, 60, YN - 118)

# Gates to A on M4 (like inverter VIN/VBP/VBN): M2 landing -> M3 -> M4,
# so the horizontal A bus never shares M3 with the Y wire.
GATE_X = 300
gate(YP + 134, 102, GATE_X)   # PMOS gate rail (poly ends +/-134)
gate(YN + 134, 51, -250)      # NMOS gate rail
for p in [(GATE_X, YP + 134), (-250, YN + 134)]:
    via23(*p, landing=True)
    from pathlib import Path as _P  # noqa
rect("via3", GATE_X - 20, YP + 134 - 20, GATE_X + 20, YP + 134 + 20)
pad("metal3", GATE_X, YP + 134)
rect("metal4", GATE_X - 29, YP + 134 - 29, GATE_X + 29, YP + 134 + 29)
rect("via3", -250 - 20, YN + 134 - 20, -250 + 20, YN + 134 + 20)
pad("metal3", -250, YN + 134)
rect("metal4", -250 - 29, YN + 134 - 29, -250 + 29, YN + 134 + 29)
rect("metal4", -279, YN + 134 - 29, GATE_X + 29, YN + 134 + 29)
# PMOS gate M4 riser down to the A bus (joins area, like inverter m4wire).
rect("metal4", GATE_X - 29, YN + 134, GATE_X + 29, YP + 134 + 29)
# A port on M4 left edge.
rect("metal4", -450, YN + 134 - 29, -279, YN + 134 + 29)

# Output Y: PMOS middle drain to NMOS drain. Use landing pads so the
# M3 meets the 0.144um^2 minimum area.
for p in [(0, YP - 70), (-51, YN + 70)]:
    via23(*p, landing=True)
m3wire(-80, YN + 70, 80, YP - 70)
pad("metal3", 0, YP - 70)
pad("metal3", -51, YN + 70)

# Supplies to tap rails (right-edge trunk like inverter), with landings.
# VDD via on outer stripe (102) to clear the Y stub at x=0 (M2.b).
for p in [(102, YP + 80), (51, YN - 80)]:
    via23(*p, landing=True)
via23(255, 1280 - 21, landing=True)
via23(255, -680 + 21, landing=True)
for x, y in [(255, 1280), (255, -680)]:
    rect("via1", x - 20, y - 20, x + 20, y + 20)
    rect("metal1", x - 29, y - 29, x + 29, y + 29)
# VSS trunk bottom needs via2 to reach the M3 trunk (else source floats).
rect("via2", 255 - 20, -680 - 20, 255 + 20, -680 + 20)
rect("metal2", 255 - 29, -680 - 29, 255 + 29, -680 + 29)
m3wire(226, YP + 80, 284, 1280)
m3wire(226, YN - 80, 284, -680)
# VDD trunk jogs to the outer-stripe via at x=102.
m3wire(73, YP + 51, 284, YP + 109)
# VSS trunk jog to the single-stripe via at x=51 (else source floats).
m3wire(22, YN - 109, 284, YN - 51)

# Wells/taps.
rect("nwell", -350, YP - 200, 350, YP + 758)
rect("nsubdiff", -302, YP + 650, 302, YP + 710)
rect("psubdiff", -350, YN - 710, 350, YN - 650)
for layer, y0 in [("nsubdiffcont", YP + 664), ("psubdiffcont", YN - 696)]:
    for x in range(-258, 247, 72):
        rect(layer, x, y0, x + 32, y0 + 32)
rect("metal1", -450, YP + 650, 450, YP + 710)
rect("metal1", -450, YN - 710, 450, YN - 650)

# Ports.
m3wire(-22, YN + 41, 450, 99)              # Y out (M3 right edge)
# A in on metal4 left, Y out metal3 right, supplies on metal1 taps.
labels = [
    ("metal1", -450, YP + 650, -410, YP + 710, "VDD", 2),
    ("metal1", -450, YN - 710, -410, YN - 650, "VSS", 3),
    ("metal4", -450, 105, -410, 163, "A", 0),
    ("metal3", 410, 41, 450, 99, "Y", 1),
]
# A riser: M3 A bus to M4.
rect("via3", -270, YN + 114, -230, YN + 154)
pad("metal3", -250, YN + 134)
rect("metal4", -279, YN + 105, -221, YN + 163)
rect("metal4", -450, YN + 105, -221, YN + 163)

lines = ["magic", "tech ihp-sg13cmos5l", "magscale 1 2", "timestamp 0"]
for cell, name, x, y in uses:
    lines += [f"use {cell}  {name}", "timestamp 0",
              f"transform 1 0 {x} 0 1 {y}", "box 0 0 1 1"]
order = ["nwell", "nsubdiff", "nsubdiffcont", "psubdiff", "psubdiffcont",
         "metal1", "via1", "metal2", "via2", "metal3", "via3", "metal4"]
for layer in order:
    if layer in L:
        lines.append(f"<< {layer} >>")
        lines += ["rect %d %d %d %d" % r for r in L[layer]]
lines.append("<< labels >>")
for layer, a, b, c, d, name, port in labels:
    lines += [f"rlabel {layer} {a} {b} {c} {d} 0 {name}", f"port {port} nsew"]
lines += ["<< end >>", ""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
