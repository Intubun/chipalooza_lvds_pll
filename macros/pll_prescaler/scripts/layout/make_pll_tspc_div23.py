#!/usr/bin/env python3
"""Assemble and route the complete TSPC /2-/3 prescaler.

Global nets are vertical TopMetal1 rails. Child pins leave their cell on M4,
then meet the selected rail through a TopVia1 post. This keeps all global
routing above the primitives' M1-M4 local interconnect and makes the macro
hierarchical and replaceable in the digital P&R flow.
"""
from pathlib import Path


OUT = Path(__file__).resolve().parents[2] / "layout/mag/pll_tspc_div23.mag"
L = {}


def rect(layer, x0, y0, x1, y1):
    L.setdefault(layer, []).append(
        (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))


RAIL_X = {
    "VSS": 0, "VDD": 700, "RESET_B": 1400, "RST": 2100,
    "CLK": 2800, "MODULUS_REQUEST": 3500, "Q2": 4200,
    "NMC": 4900, "NQ2": 5600, "Q1": 6300, "D2": 7000,
}
TM_HALF = 164             # 1.64 um TopMetal1 width


def tv1_post(net, x, y):
    """M4 landing + 0.42 um TopVia1 cut into the net's TM1 rail."""
    rect("metal4", x - 62, y - 62, x + 62, y + 62)
    # Magic's via4 paint is the cut plus its mandatory M4 enclosure, hence
    # the full 0.62 um composite width rather than the raw 0.42 um cut.
    rect("via4", x - 62, y - 62, x + 62, y + 62)


def m4_to_rail(net, pin_x, pin_y):
    rx = RAIL_X[net]
    rect("metal4", min(rx, pin_x), pin_y - 29,
         max(rx, pin_x), pin_y + 29)
    tv1_post(net, rx, pin_y)


def m3_pin_to_rail(net, pin_x, pin_y, track_y):
    """Escape a pin vertically on M3, then use M4 to its TM1 rail."""
    rect("via3", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal4", pin_x - 62, pin_y - 62, pin_x + 62, pin_y + 62)
    rect("metal3", pin_x - 29, min(pin_y, track_y) - 29,
         pin_x + 29, max(pin_y, track_y) + 29)
    rect("via3", pin_x - 20, track_y - 20, pin_x + 20, track_y + 20)
    rect("metal4", pin_x - 62, track_y - 62, pin_x + 62, track_y + 62)
    m4_to_rail(net, pin_x, track_y)


def supply_m1_to_rail(net, pin_x, pin_y):
    """Full stack immediately outside an inverter's M1 supply pin."""
    rect("metal1", pin_x - 62, pin_y - 62, pin_x + 62, pin_y + 62)
    rect("via1", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal2", pin_x - 50, pin_y - 50, pin_x + 50, pin_y + 50)
    rect("via2", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal3", pin_x - 50, pin_y - 50, pin_x + 50, pin_y + 50)
    rect("via3", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal4", pin_x - 62, pin_y - 62, pin_x + 62, pin_y + 62)
    m4_to_rail(net, pin_x, pin_y)


def antenna_m1_to_rail(net, pin_x, pin_y, track_y):
    """Promote an antenna-cell M1 pin and escape on a unique M4 track."""
    # The A pin already has ample M1; keep this landing inside its irregular
    # outline rather than widening toward the diode's adjacent diffusion ties.
    rect("metal1", pin_x - 29, pin_y - 29, pin_x + 29, pin_y + 29)
    rect("via1", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal2", pin_x - 50, pin_y - 50, pin_x + 50, pin_y + 50)
    rect("via2", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal3", pin_x - 50, pin_y - 50, pin_x + 50, pin_y + 50)
    rect("metal3", pin_x - 29, pin_y, pin_x + 29, track_y + 29)
    rect("via3", pin_x - 20, track_y - 20, pin_x + 20, track_y + 20)
    rect("metal4", pin_x - 62, track_y - 62, pin_x + 62, track_y + 62)
    m4_to_rail(net, pin_x, track_y)


# TM1 rails are widely spaced to satisfy its 1.64 um width/spacing rules.
for net, x in RAIL_X.items():
    rect("m5", x - TM_HALF, -1500, x + TM_HALF, 33000)

# Three TSPC FFs, stacked with all ports on their left edge.
FF_X = 9000
ff_rows = {
    "XMCFF": (0, {"D": "MODULUS_REQUEST", "CLK": "Q2", "Q": "NMC"}),
    "XFF1": (4500, {"D": "NQ2", "CLK": "CLK", "Q": "Q1"}),
    "XFF2": (9000, {"D": "D2", "CLK": "CLK", "Q": "Q2"}),
}
ff_pin_y = {"D": 500, "CLK": 700, "Q": -100,
            "RST": 900, "RESET_B": 1100, "VDD": 300, "VSS": -900}
for _, (y0, signals) in ff_rows.items():
    for pin, net in signals.items():
        m4_to_rail(net, FF_X - 700, y0 + ff_pin_y[pin])
    for pin, net in (("RST", "RST"), ("RESET_B", "RESET_B"),
                     ("VDD", "VDD"), ("VSS", "VSS")):
        m4_to_rail(net, FF_X - 700, y0 + ff_pin_y[pin])

# AO21 is mirrored so its Y output faces the rail corridor. Inputs escape
# upward on M3 to independent M4 tracks.
AO_MIRROR_X, AO_Y = 15000, 13500
m3_pin_to_rail("Q2", AO_MIRROR_X - 470, AO_Y + 1830, 16000)
m3_pin_to_rail("Q1", AO_MIRROR_X - 2270, AO_Y + 1830, 16200)
m3_pin_to_rail("NMC", AO_MIRROR_X - 4070, AO_Y + 1830, 16400)
m4_to_rail("D2", AO_MIRROR_X - 5520, AO_Y + 300)
m4_to_rail("VDD", AO_MIRROR_X + 300, AO_Y + 900)
m4_to_rail("VSS", AO_MIRROR_X + 300, AO_Y - 500)

# Two local inverters. Their M3 outputs rise outside the cell before moving
# left on M4; M1 supplies are promoted through a complete local stack. Keep
# the cells on separate rows so their long M4 rail escapes cannot interact.
for x0, y0, ain, yout, track_y in (
        (9000, 17500, "RESET_B", "RST", 19800),
        (9000, 22000, "Q2", "NQ2", 24300)):
    m4_to_rail(ain, x0 - 450, y0 + 134)
    m3_pin_to_rail(yout, x0 + 450, y0 + 70, track_y)
    supply_m1_to_rail("VDD", x0 - 450, y0 + 1280)
    supply_m1_to_rail("VSS", x0 - 450, y0 - 680)

# Protect every signal rail with the foundry-recognized dual antenna diode.
# The cells abut in one row with shared M1 supplies; unique M4 tracks avoid
# introducing shorts while each signal reaches its own TopMetal1 rail.
ANT_Y = 25000
antenna_nets = ["CLK", "RESET_B", "MODULUS_REQUEST", "Q2", "NMC",
                "NQ2", "Q1", "D2", "RST"]
for i, net in enumerate(antenna_nets):
    x0 = 11000 + 288 * i
    antenna_m1_to_rail(net, x0 + 100, ANT_Y + 300, 26600 + 700 * i)
rect("metal1", 10800, ANT_Y - 44, 11000 + 288 * len(antenna_nets), ANT_Y + 44)
rect("metal1", 10800, ANT_Y + 712,
     11000 + 288 * len(antenna_nets), ANT_Y + 800)
supply_m1_to_rail("VSS", 10800, ANT_Y)
supply_m1_to_rail("VDD", 10800, ANT_Y + 756)

uses = [
    ("tspc_invff_r0", "XMCFF", 1, 0, FF_X, 0, 1, 0),
    ("tspc_invff_r0", "XFF1", 1, 0, FF_X, 0, 1, 4500),
    ("tspc_invff_r0", "XFF2", 1, 0, FF_X, 0, 1, 9000),
    ("prescaler_ao21", "XNEXT", -1, 0, AO_MIRROR_X, 0, 1, AO_Y),
    ("prescaler_inv", "XRESET", 1, 0, 9000, 0, 1, 17500),
    ("prescaler_inv", "XQ2B", 1, 0, 9000, 0, 1, 22000),
]
uses += [("prescaler_antenna", f"XANT_{net}", 1, 0,
          11000 + 288 * i, 0, 1, ANT_Y)
         for i, net in enumerate(antenna_nets)]

labels = [
    ("CLK", 0), ("RESET_B", 1), ("MODULUS_REQUEST", 2),
    ("Q2", 3), ("VDD", 4), ("VSS", 5),
]
lines = ["magic", "tech ihp-sg13cmos5l", "magscale 1 2", "timestamp 0"]
for cell, name, a, b, c, d, e, f in uses:
    lines += [f"use {cell}  {name}", "timestamp 0",
              f"transform {a} {b} {c} {d} {e} {f}", "box 0 0 1 1"]
for layer in ("metal1", "via1", "metal2", "via2", "metal3", "via3",
              "metal4", "via4", "m5"):
    if layer in L:
        lines.append(f"<< {layer} >>")
        lines += ["rect %d %d %d %d" % r for r in L[layer]]
lines.append("<< labels >>")
for name, port in labels:
    x = RAIL_X[name]
    lines += [f"rlabel m5 {x - TM_HALF} -1500 {x + TM_HALF} -1200 0 {name}",
              f"port {port} nsew"]
lines += ["<< end >>", ""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
