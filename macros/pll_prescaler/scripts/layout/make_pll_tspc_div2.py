#!/usr/bin/env python3
"""Build a compact fixed divide-by-two from one inverting TSPC stage."""
from pathlib import Path


OUT = Path(__file__).resolve().parents[2] / "layout/mag/pll_tspc_div2.mag"
L = {}


def rect(layer, x0, y0, x1, y1):
    L.setdefault(layer, []).append(
        (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))


RAIL_X = {"VSS": 200, "VDD": 900, "RESET_B": 1600,
          "CLK": 2300, "RST": 3000, "Q": 3700}
TM_HALF = 164


def tv1_post(x, y):
    rect("metal4", x - 62, y - 62, x + 62, y + 62)
    rect("via4", x - 62, y - 62, x + 62, y + 62)


def m4_to_rail(net, pin_x, pin_y):
    rx = RAIL_X[net]
    rect("metal4", min(rx, pin_x), pin_y - 29,
         max(rx, pin_x), pin_y + 29)
    tv1_post(rx, pin_y)


def promote_m1(net, x, y):
    rect("metal1", x - 62, y - 62, x + 62, y + 62)
    rect("via1", x - 20, y - 20, x + 20, y + 20)
    rect("metal2", x - 50, y - 50, x + 50, y + 50)
    rect("via2", x - 20, y - 20, x + 20, y + 20)
    rect("metal3", x - 50, y - 50, x + 50, y + 50)
    rect("via3", x - 20, y - 20, x + 20, y + 20)
    rect("metal4", x - 62, y - 62, x + 62, y + 62)
    m4_to_rail(net, x, y)


def promote_m3(net, x, y, track_y):
    rect("via3", x - 20, y - 20, x + 20, y + 20)
    rect("metal4", x - 62, y - 62, x + 62, y + 62)
    rect("metal3", x - 29, min(y, track_y) - 29,
         x + 29, max(y, track_y) + 29)
    rect("via3", x - 20, track_y - 20, x + 20, track_y + 20)
    rect("metal4", x - 62, track_y - 62, x + 62, track_y + 62)
    m4_to_rail(net, x, track_y)


for x in RAIL_X.values():
    rect("m5", x - TM_HALF, 0, x + TM_HALF, 9600)

# The inverting TSPC stage toggles when D is tied to Q.
FF_X, FF_Y = 5000, 1500
PIN_X = FF_X - 700
# D and Q share the child's M4 pin column, which also contains the supply pins.
# Join only D and Q on M3 so the feedback cannot cross-short those M4 escapes.
for y in (FF_Y - 100, FF_Y + 500):
    rect("via3", PIN_X - 20, y - 20, PIN_X + 20, y + 20)
    rect("metal3", PIN_X - 50, y - 50, PIN_X + 50, y + 50)
    rect("metal4", PIN_X - 62, y - 62, PIN_X + 62, y + 62)
rect("metal3", PIN_X - 29, FF_Y - 100,
     PIN_X + 29, FF_Y + 500)
m4_to_rail("Q", PIN_X, FF_Y - 100)
m4_to_rail("CLK", PIN_X, FF_Y + 700)
m4_to_rail("RST", PIN_X, FF_Y + 900)
m4_to_rail("RESET_B", PIN_X, FF_Y + 1100)
m4_to_rail("VDD", PIN_X, FF_Y + 300)
m4_to_rail("VSS", PIN_X, FF_Y - 900)

# Active-high reset is generated locally from RESET_B.
INV_X, INV_Y = 5000, 5000
m4_to_rail("RESET_B", INV_X - 450, INV_Y + 134)
promote_m3("RST", INV_X + 450, INV_Y + 110, 7000)
promote_m1("VDD", INV_X - 450, INV_Y + 1280)
promote_m1("VSS", INV_X - 450, INV_Y - 680)

# Foundry-recognized antenna diodes share one abutted supply row.
ANT_X, ANT_Y = 7000, 6500
antenna_nets = ["CLK", "RESET_B", "Q", "RST"]
for i, net in enumerate(antenna_nets):
    x0 = ANT_X + 288 * i
    pin_x, pin_y = x0 + 100, ANT_Y + 300
    rect("metal1", pin_x - 29, pin_y - 29, pin_x + 29, pin_y + 29)
    rect("via1", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal2", pin_x - 50, pin_y - 50, pin_x + 50, pin_y + 50)
    rect("via2", pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20)
    rect("metal3", pin_x - 50, pin_y - 50, pin_x + 50, pin_y + 50)
    track_y = 7500 + 180 * i
    rect("metal3", pin_x - 29, pin_y, pin_x + 29, track_y + 29)
    rect("via3", pin_x - 20, track_y - 20, pin_x + 20, track_y + 20)
    rect("metal4", pin_x - 62, track_y - 62, pin_x + 62, track_y + 62)
    m4_to_rail(net, pin_x, track_y)
rect("metal1", ANT_X - 200, ANT_Y - 44,
     ANT_X + 288 * len(antenna_nets), ANT_Y + 44)
rect("metal1", ANT_X - 200, ANT_Y + 712,
     ANT_X + 288 * len(antenna_nets), ANT_Y + 800)
promote_m1("VSS", ANT_X - 200, ANT_Y)
promote_m1("VDD", ANT_X - 200, ANT_Y + 756)

# M4 boundary stubs allow parent routing to remain below TopMetal1.
for net, y in (("Q", 8600), ("RESET_B", 9000), ("CLK", 9400)):
    m4_to_rail(net, 13000, y)
    # Cover the complete LEF access rectangle so any selected router track
    # physically overlaps the macro M4 rather than merely touching its port.
    rect("metal4", 13000 - 124, y - 62, 13000, y + 62)

uses = [
    ("tspc_invff_r0", "XFF", 1, 0, FF_X, 0, 1, FF_Y),
    ("prescaler_inv", "XRESET", 1, 0, INV_X, 0, 1, INV_Y),
]
uses += [("prescaler_antenna", f"XANT_{net}", 1, 0,
          ANT_X + 288 * i, 0, 1, ANT_Y)
         for i, net in enumerate(antenna_nets)]

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
label_rects = {
    "Q": (13000 - 62, 8600 - 62, 13000, 8600 + 62),
    "RESET_B": (13000 - 62, 9000 - 62, 13000, 9000 + 62),
    "CLK": (13000 - 62, 9400 - 62, 13000, 9400 + 62),
    "VDD": (RAIL_X["VDD"] - 62, FF_Y + 300 - 62,
            RAIL_X["VDD"] + 62, FF_Y + 300 + 62),
    "VSS": (RAIL_X["VSS"] - 62, FF_Y - 900 - 62,
            RAIL_X["VSS"] + 62, FF_Y - 900 + 62),
}
for name, port in (("CLK", 0), ("RESET_B", 1), ("Q", 2),
                   ("VDD", 3), ("VSS", 4)):
    x0, y0, x1, y1 = label_rects[name]
    lines += [f"rlabel metal4 {x0} {y0} {x1} {y1} 0 {name}",
              f"port {port} nsew"]
lines += ["<< properties >>", "string FIXED_BBOX 0 0 13000 9600",
          "<< end >>", ""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
