#!/usr/bin/env python3
"""Generate a conservative, LVS-readable layout for prescaler_ao21.

The four PMOS devices occupy the upper row and the four NMOS devices the
lower row. Device terminals rise on separate Metal3 drops to horizontal
Metal4 net buses. Gate pairs share dedicated Metal3 columns. This is larger
than a compact standard cell, but avoids hidden crossings in this custom
dynamic-clock macro and gives PEX predictable, short local branches.

Magic coordinates are 5 nm internal units.
"""
from pathlib import Path


OUT = Path(__file__).resolve().parents[2] / "layout/mag/prescaler_ao21.mag"
layers = {}


def rect(layer, x0, y0, x1, y1):
    layers.setdefault(layer, []).append(
        (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))


def pad(layer, x, y):
    rect(layer, x - 29, y - 50, x + 29, y + 50)


def via12(x, y):
    rect("metal1", x - 29, y - 29, x + 29, y + 29)
    rect("via1", x - 20, y - 20, x + 20, y + 20)
    rect("metal2", x - 29, y - 29, x + 29, y + 29)


def via23(x, y):
    pad("metal2", x, y)
    rect("via2", x - 20, y - 20, x + 20, y + 20)
    pad("metal3", x, y)


def via34(x, y):
    pad("metal3", x, y)
    rect("via3", x - 20, y - 20, x + 20, y + 20)
    rect("metal4", x - 29, y - 29, x + 29, y + 29)


def terminal_rail(xs, device_y, offset, drop_x, bus_y, connect_bus=True):
    """Join diffusion stripes on M2 and take one M3 drop to an M4 bus."""
    rail_y = device_y + offset
    contact_y = device_y + (20 if offset > 0 else -20)
    for x in xs:
        via12(x, contact_y)
        rect("metal2", x - 29, min(contact_y, rail_y) - 29,
             x + 29, max(contact_y, rail_y) + 29)
    rect("metal2", min(xs) - 29, rail_y - 29,
         max(xs) + 29, rail_y + 29)
    rect("metal2", min(drop_x, min(xs)) - 29, rail_y - 29,
         max(drop_x, max(xs)) + 29, rail_y + 29)
    via23(drop_x, rail_y)
    rect("metal3", drop_x - 29, min(rail_y, bus_y) - 29,
         drop_x + 29, max(rail_y, bus_y) + 29)
    if connect_bus:
        via34(drop_x, bus_y)


def gate_pair(xc, half_p, half_n, gate_x, yp, yn, port=False):
    """Join aligned PMOS/NMOS gates on an isolated M3 column."""
    p_y = yp + 134
    n_y = yn + 134
    for y, half in ((p_y, half_p), (n_y, half_n)):
        rect("metal1", min(xc - half, gate_x - 29), y - 20,
             max(xc + half, gate_x + 29), y + 22)
        via12(gate_x, y)
        via23(gate_x, y)
    top = 1600 if port else p_y
    rect("metal3", gate_x - 29, n_y - 29, gate_x + 29, top + 29)
    if port:
        via34(gate_x, 1600)
        rect("metal4", gate_x - 29, 1571, gate_x + 29, 1860)


# Four widely spaced columns. PMOS and NMOS in each column are aligned so a
# gate is one straight M3 drop. Device widths/fingers match the schematic.
YP, YN = 1000, 0
X = [0, 1800, 3600, 5400]
uses = [
    ("dev_p_w0p6_l0p13_ng4_noguard_m1", "XP_A", X[0], YP),
    ("dev_p_w0p6_l0p13_ng4_noguard_m1", "XP_B", X[1], YP),
    ("dev_p_w0p6_l0p13_ng4_noguard_m1", "XP_C", X[2], YP),
    ("dev_p_w0p6_l0p13_ng2_noguard_m1", "XP_I", X[3], YP),
    ("dev_n_w0p6_l0p13_ng1_noguard_m1", "XN_A", X[0], YN),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "XN_B", X[1], YN),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "XN_C", X[2], YN),
    ("dev_n_w0p6_l0p13_ng1_noguard_m1", "XN_I", X[3], YN),
]

# One M4 track per electrical net. Tracks are 0.5 um apart, comfortably over
# M4 spacing. Their x extents include all drops belonging to that net.
BUS = {"VSS": -500, "N": -300, "Y": 300,
       "NY": 500, "P": 700, "VDD": 900}
bus_extent = {
    "VSS": (-300, 6000), "N": (1700, 3700), "Y": (5100, 5700),
    "NY": (-300, 6000), "P": (-300, 3900), "VDD": (-300, 6000),
}
for net, y in BUS.items():
    x0, x1 = bus_extent[net]
    rect("metal4", x0, y - 29, x1, y + 29)

# PMOS terminal rails: ng4 outer stripes are D, inner stripes S; ng2 outer
# stripes are D and the centre stripe S.
terminal_rail([X[0] - 204, X[0], X[0] + 204], YP, 80,
              X[0] - 204, BUS["VDD"])
terminal_rail([X[0] - 102, X[0] + 102], YP, -90,
              X[0] + 102, BUS["P"])
terminal_rail([X[1] - 204, X[1], X[1] + 204], YP, 80,
              X[1] - 204, BUS["P"])
terminal_rail([X[1] - 102, X[1] + 102], YP, -90,
              X[1] + 102, BUS["NY"])
terminal_rail([X[2] - 204, X[2], X[2] + 204], YP, 80,
              X[2] - 204, BUS["P"])
terminal_rail([X[2] - 102, X[2] + 102], YP, -90,
              X[2] + 102, BUS["NY"])
terminal_rail([X[3] - 102, X[3] + 102], YP, 80,
              X[3] - 102, BUS["VDD"])
terminal_rail([X[3]], YP, -90, 5100, BUS["Y"])

# NMOS terminal rails. For ng1, D is -51 and S is +51. For ng2, the outer
# stripes are D and the centre stripe is S.
terminal_rail([X[0] - 51], YN, 90, X[0] - 51, BUS["NY"])
terminal_rail([X[0] + 51], YN, -80, X[0] + 51, BUS["VSS"])
terminal_rail([X[1] - 102, X[1] + 102], YN, 90,
              X[1] - 102, BUS["NY"])
terminal_rail([X[1]], YN, -80, X[1], BUS["N"])
terminal_rail([X[2] - 102, X[2] + 102], YN, 90,
              X[2] - 102, BUS["N"])
terminal_rail([X[2]], YN, -80, X[2], BUS["VSS"])
terminal_rail([X[3] - 51], YN, 90, 5100, BUS["Y"], connect_bus=False)
terminal_rail([X[3] + 51], YN, -80, X[3] + 51, BUS["VSS"])

# Input gates A/B/C become top-edge M4 pins. The output-inverter gate pair is
# tied to the NY M4 bus instead.
for xc, name in zip(X[:3], ("A", "B", "C")):
    gate_pair(xc, 204, 51 if name == "A" else 102,
              xc + 500, YP, YN, port=True)
gate_pair(X[3], 102, 51, X[3] + 350, YP, YN)
via34(X[3] + 350, BUS["NY"])

# The unused bottom gate rails of the two single-finger NMOS devices need
# enough Metal1 area even though only their common top gate ports are used.
for xc in (X[0], X[3]):
    rect("metal1", xc - 60, YN - 150, xc + 60, YN - 118)

# Well/substrate taps. Their M1 rails are connected to the corresponding M4
# bus by stacks at the far right, away from all signal drops.
rect("nwell", -500, 700, 6100, 2100)
rect("nsubdiff", -400, 1950, 6000, 2010)
rect("psubdiff", -500, -810, 6100, -750)
for layer, y0 in (("nsubdiffcont", 1964), ("psubdiffcont", -796)):
    for x in range(-356, 5980, 72):
        rect(layer, x, y0, x + 32, y0 + 32)
rect("metal1", -500, 1950, 6100, 2010)
rect("metal1", -500, -810, 6100, -750)
for tap_y, bus_y in ((1980, BUS["VDD"]), (-780, BUS["VSS"])):
    via12(5900, tap_y)
    via23(5900, tap_y)
    rect("metal3", 5871, min(tap_y, bus_y) - 29,
         5929, max(tap_y, bus_y) + 29)
    via34(5900, bus_y)

# Ports use the buses directly. A/B/C are the three top gate columns.
labels = [
    ("metal4", 470, 1800, 530, 1860, "A", 0),
    ("metal4", 2270, 1800, 2330, 1860, "B", 1),
    ("metal4", 4070, 1800, 4130, 1860, "C", 2),
    ("metal4", 5520, 271, 5700, 329, "Y", 3),
    ("metal4", -300, 871, -240, 929, "VDD", 4),
    ("metal4", -300, -529, -240, -471, "VSS", 5),
]

lines = ["magic", "tech ihp-sg13cmos5l", "magscale 1 2", "timestamp 0"]
for cell, name, x, y in uses:
    lines += [f"use {cell}  {name}", "timestamp 0",
              f"transform 1 0 {x} 0 1 {y}", "box 0 0 1 1"]
order = ["nwell", "nsubdiff", "nsubdiffcont", "psubdiff", "psubdiffcont",
         "metal1", "via1", "metal2", "via2", "metal3", "via3", "metal4"]
for layer in order:
    if layer in layers:
        lines.append(f"<< {layer} >>")
        lines += ["rect %d %d %d %d" % r for r in layers[layer]]
lines.append("<< labels >>")
for layer, x0, y0, x1, y1, name, port in labels:
    lines += [f"rlabel {layer} {x0} {y0} {x1} {y1} 0 {name}",
              f"port {port} nsew"]
lines += ["<< end >>", ""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
