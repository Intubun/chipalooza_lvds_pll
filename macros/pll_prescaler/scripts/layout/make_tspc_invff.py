#!/usr/bin/env python3
"""Generate the ratioed TSPC inverting flip-flop layout.

The implementation follows tspc_invff_r0 in pll_tspc_div23.spice. Every
electrical net has a separate Metal4 track; transistor terminals and gates
reach those tracks through short Metal3 drops. The regular topology is
intentionally conservative for first-pass PEX and can be compacted after the
post-layout PVT sweep establishes margin.
"""
from pathlib import Path


OUT = Path(__file__).resolve().parents[2] / "layout/mag/tspc_invff_r0.mag"
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


def diffusion_rail(xs, device_y, offset, drop_x, bus_y):
    rail_y = device_y + offset
    contact_y = device_y + (20 if offset > 0 else -20)
    for x in xs:
        via12(x, contact_y)
        rect("metal2", x - 29, min(contact_y, rail_y) - 29,
             x + 29, max(contact_y, rail_y) + 29)
    rect("metal2", min(xs + [drop_x]) - 29, rail_y - 29,
         max(xs + [drop_x]) + 29, rail_y + 29)
    via23(drop_x, rail_y)
    rect("metal3", drop_x - 29, min(rail_y, bus_y) - 29,
         drop_x + 29, max(rail_y, bus_y) + 29)
    via34(drop_x, bus_y)


def gate_to_bus(xc, halfwidth, device_y, gate_x, bus_y):
    gate_y = device_y + 134
    rect("metal1", min(xc - halfwidth, gate_x - 29), gate_y - 20,
         max(xc + halfwidth, gate_x + 29), gate_y + 22)
    via12(gate_x, gate_y)
    via23(gate_x, gate_y)
    rect("metal3", gate_x - 29, min(gate_y, bus_y) - 29,
         gate_x + 29, max(gate_y, bus_y) + 29)
    via34(gate_x, bus_y)


YP, YN = 1600, 0
PX = [700, 2500, 4300, 6100]
NX = [0, 1200, 2400, 3600, 4800, 6000]
uses = [
    ("dev_p_w0p6_l0p13_ng2_noguard_m1", "M1", PX[0], YP),
    ("dev_p_w0p6_l0p13_ng2_noguard_m1", "M4", PX[1], YP),
    ("dev_p_w0p6_l0p13_ng2_noguard_m1", "M6", PX[2], YP),
    ("dev_p_w0p6_l0p13_ng1_noguard_m1", "XRB", PX[3], YP),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "M3", NX[0], YN),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "M2", NX[1], YN),
    ("dev_n_w0p6_l0p13_ng6_noguard_m1", "M5", NX[2], YN),
    ("dev_n_w0p6_l0p13_ng4_noguard_m1", "M7", NX[3], YN),
    ("dev_n_w0p6_l0p13_ng1_noguard_m1", "XRA", NX[4], YN),
    ("dev_n_w0p6_l0p13_ng1_noguard_m1", "XRQ", NX[5], YN),
]

BUS = {
    "VSS": -900, "N1": -700, "A": -500, "B": -300, "Q": -100,
    "VDD": 300, "D": 500, "CLK": 700, "RST": 900, "RESET_B": 1100,
}
for y in BUS.values():
    rect("metal4", -700, y - 29, 7600, y + 29)


def pmos2(x, drain, gate, source, drops):
    diffusion_rail([x - 102, x + 102], YP, 80, drops[0], BUS[drain])
    diffusion_rail([x], YP, -90, drops[1], BUS[source])
    gate_to_bus(x, 102, YP, drops[2], BUS[gate])


def pmos1(x, drain, gate, source, drops):
    diffusion_rail([x - 51], YP, 80, drops[0], BUS[drain])
    diffusion_rail([x + 51], YP, -90, drops[1], BUS[source])
    gate_to_bus(x, 51, YP, drops[2], BUS[gate])
    rect("metal1", x - 60, YP - 150, x + 60, YP - 118)


def nmos(x, fingers, drain, gate, source, drops):
    if fingers == 1:
        ds, ss, half = [x - 51], [x + 51], 51
    else:
        half = 51 * fingers
        stripes = [x + 51 * (2 * i - fingers) for i in range(fingers + 1)]
        ds, ss = stripes[0::2], stripes[1::2]
    diffusion_rail(ds, YN, 90, drops[0], BUS[drain])
    diffusion_rail(ss, YN, -80, drops[1], BUS[source])
    gate_to_bus(x, half, YN, drops[2], BUS[gate])
    if fingers == 1:
        rect("metal1", x - 60, YN - 150, x + 60, YN - 118)


pmos2(PX[0], "A", "D", "VDD", (100, 1050, 1250))
pmos2(PX[1], "B", "A", "VDD", (2050, 2750, 3400))
pmos2(PX[2], "Q", "CLK", "VDD", (3850, 4650, 4850))
pmos1(PX[3], "B", "RESET_B", "VDD", (5500, 6800, 7000))
nmos(NX[0], 2, "A", "CLK", "N1", (-500, 300, 500))
nmos(NX[1], 2, "N1", "D", "VSS", (900, 1500, 1700))
nmos(NX[2], 6, "B", "CLK", "VSS", (1900, 2900, 3100))
nmos(NX[3], 4, "Q", "B", "VSS", (3250, 4000, 4200))
nmos(NX[4], 1, "A", "RST", "VSS", (4500, 5100, 5300))
nmos(NX[5], 1, "Q", "RST", "VSS", (5700, 6300, 6500))

# Body ties and wide tap rails.
rect("nwell", -600, 1300, 7700, 2700)
rect("nsubdiff", -500, 2550, 7600, 2610)
rect("psubdiff", -600, -1210, 7700, -1150)
for layer, y0 in (("nsubdiffcont", 2564), ("psubdiffcont", -1196)):
    for x in range(-456, 7560, 72):
        rect(layer, x, y0, x + 32, y0 + 32)
rect("metal1", -600, 2550, 7700, 2610)
rect("metal1", -600, -1210, 7700, -1150)
for tap_y, bus_y in ((2580, BUS["VDD"]), (-1180, BUS["VSS"])):
    via12(7500, tap_y)
    via23(7500, tap_y)
    rect("metal3", 7471, min(tap_y, bus_y) - 29,
         7529, max(tap_y, bus_y) + 29)
    via34(7500, bus_y)

labels = [
    ("D", 0), ("CLK", 1), ("Q", 2), ("RST", 3),
    ("RESET_B", 4), ("VDD", 5), ("VSS", 6),
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
for name, port in labels:
    y = BUS[name]
    lines += [f"rlabel metal4 -700 {y - 29} -640 {y + 29} 0 {name}",
              f"port {port} nsew"]
lines += ["<< end >>", ""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
