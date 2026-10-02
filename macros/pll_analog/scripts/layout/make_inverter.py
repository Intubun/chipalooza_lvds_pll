#!/usr/bin/env python3
"""Generate layout/mag/inverter.mag, the current-starved VCO stage.

Device cells (dev_*_noguard_m1) come from the PDK gencell; this script places
them and draws the routing. Units are Magic internal units (5 nm).

Stack, top to bottom: M1 PMOS starve (ng5), M2 PMOS switch (ng1),
M3 NMOS switch (ng1), M4 NMOS starve (ng5).

Each device has two M2 buses: drain (D) 0.35 um above the device centre and
source (S) 0.35 um below it. The via1 on a D stripe sits in the upper half of
the stripe and the via1 on an S stripe in the lower half, so a via pad on one
net never faces the other net's bus (M2.b).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "layout/mag/inverter.mag"
L = {}


def rect(layer, a, b, c, d):
    L.setdefault(layer, []).append((a, b, c, d))


def rail(cols, center, offset):
    """M2 bus at center+offset joining via1s on the given stripes."""
    y = center + offset
    vy = center + (35 if offset > 0 else -35)
    for x in cols:
        rect("via1", x - 20, vy - 20, x + 20, vy + 20)
        rect("metal2", x - 29, min(vy, y) - 29, x + 29, max(vy, y) + 29)
    rect("metal2", min(cols) - 29, y - 29, max(cols) + 29, y + 29)
    if len(cols) == 1:
        # A one-stripe bus is only 0.29 x 0.53 um; extend it away from the
        # device centre to the 0.144 um^2 M2 minimum area.
        x = cols[0]
        if offset > 0:
            rect("metal2", x - 29, y, x + 29, y + 60)
        else:
            rect("metal2", x - 29, y - 60, x + 29, y)


def pad(layer, x, y):
    """0.29 x 0.50 um landing pad: meets the 0.144 um^2 M2/M3 minimum area."""
    rect(layer, x - 29, y - 50, x + 29, y + 50)


def gate(y, halfwidth, xout):
    """Extend a generated M1 gate rail to a via1 landing at xout."""
    rect("metal1", min(-halfwidth, xout - 29), y - 20, max(halfwidth, xout + 29), y + 22)
    rect("metal1", xout - 29, y - 29, xout + 29, y + 29)  # V1 enclosure
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


def via34(x, y):
    rect("via3", x - 20, y - 20, x + 20, y + 20)
    pad("metal3", x, y)
    rect("metal4", x - 29, y - 29, x + 29, y + 29)


def m3wire(a, b, c, d):
    rect("metal3", a, b, c, d)


def m4wire(a, b, c, d):
    rect("metal4", a, b, c, d)


uses = [("dev_p_w0p9_l0p13_ng5_noguard_m1", "M1", 0, 1000),
        ("dev_p_w0p9_l0p13_ng1_noguard_m1", "M2", 0, 600),
        ("dev_n_w0p9_l0p13_ng1_noguard_m1", "M3", 0, 0),
        ("dev_n_w0p9_l0p13_ng5_noguard_m1", "M4", 0, -400)]

for y, ds, ss in [(1000, [-255, -51, 153], [-153, 51, 255]),
                  (600, [-51], [51]),
                  (0, [-51], [51]),
                  (-400, [-255, -51, 153], [-153, 51, 255])]:
    rail(ds, y, 70)
    rail(ss, y, -70)

# The single-finger switches use only their top gate rail; widen the unused
# bottom rail to the 0.09 um^2 M1 minimum area.
for y in (600, 0):
    rect("metal1", -60, y - 150, 60, y - 118)

# Gate landings. VBP/VBN land 0.21 um clear of the supply trunk (M3.b).
GATE_X = 360
gate(1134, 255, GATE_X)   # M1 VBP
gate(734, 51, -250)       # M2 VIN
gate(134, 51, -250)       # M3 VIN
gate(-266, 255, GATE_X)   # M4 VBN

# PMOS internal node: M1.D to M2.S.
for p in [(153, 1070), (51, 530)]:
    via23(*p)
m3wire(71, 530, 129, 1070)
m3wire(100, 1041, 182, 1099)
m3wire(22, 501, 100, 559)
# Output: M2.D to M3.D.
for p in [(-51, 670), (-51, 70)]:
    via23(*p)
m3wire(-80, 70, -22, 670)
# NMOS internal node: M3.S to M4.D.
for p in [(51, -70), (153, -330)]:
    via23(*p)
m3wire(71, -330, 129, -70)
m3wire(22, -99, 100, -41)
m3wire(100, -359, 182, -301)

# Starve-device sources to the tap rails on an M3 trunk at the right edge.
for p in [(255, 930), (255, -470)]:
    via23(*p)
via23(255, 1280 - 21, landing=True)
via23(255, -680 + 21, landing=True)
for x, y in [(255, 1280), (255, -680)]:
    rect("via1", x - 20, y - 20, x + 20, y + 20)
    rect("metal1", x - 29, y - 29, x + 29, y + 29)
m3wire(226, 930, 284, 1280)
m3wire(226, -680, 284, -470)

# Gates move from their M2/M3 landings to M4 for clean crossings.
for p in [(GATE_X, 1134), (GATE_X, -266), (-250, 734), (-250, 134)]:
    via23(*p, landing=True)
    via34(*p)
m4wire(-279, 134, -221, 734)

# N-well and taps. Tap diffusion stays 0.24 um inside the well (NW.e) and the
# contacts 0.07 um inside the diffusion (Cnt.c).
rect("nwell", -350, 400, 350, 1358)
rect("nsubdiff", -302, 1250, 302, 1310)
rect("psubdiff", -350, -710, 350, -650)
for layer, y0 in [("nsubdiffcont", 1264), ("psubdiffcont", -696)]:
    for x in range(-258, 247, 72):
        rect(layer, x, y0, x + 32, y0 + 32)
rect("metal1", -450, 1250, 450, 1310)
rect("metal1", -450, -710, 450, -650)

# Port stubs.
m3wire(-22, 271, 450, 329)            # VOUT
m4wire(GATE_X - 29, 1105, 450, 1163)  # VBP
m4wire(GATE_X - 29, -295, 450, -237)  # VBN
m4wire(-450, 271, -221, 329)          # VIN

labels = [("metal1", -450, 1250, -410, 1310, "VDD", 4),
          ("metal1", -450, -710, -410, -650, "VSS", 6),
          ("metal4", 410, 1105, 450, 1163, "VBP", 3),
          ("metal4", -450, 271, -410, 329, "VIN", 1),
          ("metal3", 410, 271, 450, 329, "VOUT", 2),
          ("metal4", 410, -295, 450, -237, "VBN", 5)]

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
