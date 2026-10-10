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
    "Q2": -700, "VSS": 0, "VDD": 700, "RESET_B": 1400, "RST": 2100,
    "CLK": 2800, "MODULUS_REQUEST": 3500,
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
    """Extend an inverter's native M3 output, then use M4 to its rail."""
    rect("metal3", pin_x - 29, min(pin_y, track_y) - 29,
         pin_x + 29, max(pin_y, track_y) + 29)
    rect("via3", pin_x - 20, track_y - 20, pin_x + 20, track_y + 20)
    rect("metal4", pin_x - 62, track_y - 62, pin_x + 62, track_y + 62)
    m4_to_rail(net, pin_x, track_y)


def m3_output_to_rail(net, output_x, output_y, track_y, jog_x):
    """Escape a native M3 output on a private jog before reaching its rail."""
    rect("metal3", min(output_x, jog_x) - 29, output_y - 29,
         max(output_x, jog_x) + 29, output_y + 29)
    rect("metal3", jog_x - 29, min(output_y, track_y) - 29,
         jog_x + 29, max(output_y, track_y) + 29)
    rect("via3", jog_x - 20, track_y - 20,
         jog_x + 20, track_y + 20)
    rect("metal4", jog_x - 62, track_y - 62,
         jog_x + 62, track_y + 62)
    m4_to_rail(net, jog_x, track_y)


def local_m4_m3(pin0_x, pin0_y, pin1_x, pin1_y, jog_x):
    """Join two M4 pins through a private M3 jog outside the cells."""
    for pin_x, pin_y in ((pin0_x, pin0_y), (pin1_x, pin1_y)):
        rect("metal4", min(pin_x, jog_x) - 29, pin_y - 29,
             max(pin_x, jog_x) + 29, pin_y + 29)
        rect("via3", jog_x - 20, pin_y - 20,
             jog_x + 20, pin_y + 20)
        rect("metal3", jog_x - 50, pin_y - 50,
             jog_x + 50, pin_y + 50)
    rect("metal3", jog_x - 29, min(pin0_y, pin1_y) - 29,
         jog_x + 29, max(pin0_y, pin1_y) + 29)


def m3_output_to_m4_targets(output_x, output_y, targets, jog_x):
    """Fan a native M3 inverter output to M4 targets without shorting A/Y."""
    rect("metal3", min(output_x, jog_x) - 29, output_y - 29,
         max(output_x, jog_x) + 29, output_y + 29)
    for pin_x, pin_y in targets:
        rect("metal3", jog_x - 29, min(output_y, pin_y) - 29,
             jog_x + 29, max(output_y, pin_y) + 29)
        rect("via3", jog_x - 20, pin_y - 20,
             jog_x + 20, pin_y + 20)
        rect("metal4", min(pin_x, jog_x) - 29, pin_y - 29,
             max(pin_x, jog_x) + 29, pin_y + 29)


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
rail_top = {net: 25600 for net in RAIL_X}
for net, x in RAIL_X.items():
    rect("m5", x - TM_HALF, -1500, x + TM_HALF, rail_top[net])

# Three TSPC FFs, stacked with all ports on their left edge.
FF_X = 9000
MCFF_Y = 8400
FF1_Y = 0
ff_rows = {
    "XMCFF": (MCFF_Y, {"D": "MODULUS_REQUEST"}),
    "XFF1": (FF1_Y, {"CLK": "CLK"}),
}
ff_pin_y = {"D": 500, "CLK": 700, "Q": -100,
            "RST": 900, "RESET_B": 1100, "VDD": 300, "VSS": -900}
for _, (y0, signals) in ff_rows.items():
    for pin, net in signals.items():
        m4_to_rail(net, FF_X - 700, y0 + ff_pin_y[pin])
    for pin, net in (("RST", "RST"), ("RESET_B", "RESET_B"),
                     ("VDD", "VDD"), ("VSS", "VSS")):
        m4_to_rail(net, FF_X - 700, y0 + ff_pin_y[pin])

# FF2 folds Q2_RAW | (Q1 & NMC) into its first dynamic TSPC stage.  Its
# nine M4 pins are on the left edge at the cell's internal bus ordinates.
FF2_Y = 4200
for pin_y, net in ((1100, "CLK"), (1300, "RST"),
                   (1500, "RESET_B"), (300, "VDD"), (-1100, "VSS")):
    m4_to_rail(net, FF_X - 700, FF2_Y + pin_y)

# Keep the four full-rate state nets off the long TopMetal1 buses. Each route
# uses its own M3 jog immediately outside the child pins, with only short M4
# endpoint stubs. This removes the dominant extracted capacitance that stopped
# Q2_RAW from reaching a valid logic level at the slow-corner VCO maximum.
PIN_X = FF_X - 700
local_m4_m3(PIN_X, MCFF_Y + 700, PIN_X, FF2_Y + 100, 8050)  # Q2_RAW
local_m4_m3(PIN_X, FF2_Y + 100, PIN_X, FF2_Y + 500, 8050)  # local feedback
local_m4_m3(PIN_X, FF1_Y - 100, PIN_X, FF2_Y + 700, 7750)  # Q1
local_m4_m3(PIN_X, MCFF_Y - 100, PIN_X, FF2_Y + 900, 7450) # NMC

# Local inverters occupy dedicated rows above the TSPC stack so the global M4
# escapes to the FF pins cannot cross their pins or internal routing.
RESET_X, RESET_Y = 6000, 16800
for x0, y0, ain, yout, output_track_y in (
        (RESET_X, RESET_Y, "RESET_B", "RST", 19000),):
    m4_to_rail(ain, x0 - 450, y0 + 134)
    m3_output_to_rail(yout, x0 + 450, y0 + 110,
                      output_track_y, x0 + 700)
    supply_m1_to_rail("VDD", x0 - 450, y0 + 1280)
    supply_m1_to_rail("VSS", x0 - 450, y0 - 680)

# Restore a static Q2 after the isolating inverter. This output, rather than
# the dynamic TSPC node, drives the modulus controller and macro boundary.
Q2B_X, Q2B_Y = 7000, 11200
Q2R_X, Q2R_Y = 7000, 14000

# Q2_RAW reaches the nearby isolating inverter through a private M3 trunk.
local_m4_m3(PIN_X, FF2_Y + 100,
            Q2B_X - 450, Q2B_Y + 134, 6200)

# NQ2 leaves the native M3 output without placing an M4 landing over the
# inverter's adjacent M4 input pin.
m3_output_to_m4_targets(
    Q2B_X + 450, Q2B_Y + 110,
    ((PIN_X, FF1_Y + 500), (Q2R_X - 450, Q2R_Y + 134)), 7900)

m3_pin_to_rail("Q2", Q2R_X + 450, Q2R_Y + 110, 23000)
supply_m1_to_rail("VDD", Q2R_X - 450, Q2R_Y + 1280)
supply_m1_to_rail("VSS", Q2R_X - 450, Q2R_Y - 680)

for net, pin_x, pin_y in (("VDD", Q2B_X - 450, Q2B_Y + 1280),
                          ("VSS", Q2B_X - 450, Q2B_Y - 680)):
    supply_m1_to_rail(net, pin_x, pin_y)

# Protect every signal rail with the foundry-recognized dual antenna diode.
# The cells abut in one row with shared M1 supplies; unique M4 tracks avoid
# introducing shorts while each signal reaches its own TopMetal1 rail.
ANT_Y = 19500
antenna_nets = ["CLK", "RESET_B", "MODULUS_REQUEST", "Q2", "RST"]
for i, net in enumerate(antenna_nets):
    x0 = 12000 + 600 * i
    antenna_m1_to_rail(net, x0 + 100, ANT_Y + 300, 21000 + 400 * i)
rect("metal1", 11800, ANT_Y - 44, 12000 + 600 * (len(antenna_nets) - 1) + 288,
     ANT_Y + 44)
rect("metal1", 11800, ANT_Y + 712,
     12000 + 600 * (len(antenna_nets) - 1) + 288, ANT_Y + 800)
supply_m1_to_rail("VSS", 11800, ANT_Y)
supply_m1_to_rail("VDD", 11800, ANT_Y + 756)

# Give the block-level router M4 access at the right macro boundary. Keeping
# all external routes at M4 or below prevents a horizontal TopMetal1 route from
# crossing and shorting the vertical global rails.
for net, y in (("Q2", 23600), ("RESET_B", 24200),
               ("CLK", 24800), ("MODULUS_REQUEST", 25400)):
    m4_to_rail(net, 21000, y)
    # Cover the complete LEF access rectangle.  The narrow horizontal route
    # alone leaves legal router access tracks a few nanometers away from the
    # drawn M4, which is electrically connected by the hierarchy port but is
    # a real M4 spacing/min-width violation after stream-out.
    rect("metal4", 21000 - 124, y - 62, 21000, y + 62)

uses = [
    ("tspc_invff_r0", "XMCFF", 1, 0, FF_X, 0, 1, MCFF_Y),
    ("tspc_invff_r0", "XFF1", 1, 0, FF_X, 0, 1, FF1_Y),
    ("tspc_ao21_invff_r0", "XFF2", 1, 0, FF_X, 0, 1, FF2_Y),
    ("prescaler_inv", "XRESET", 1, 0, RESET_X, 0, 1, RESET_Y),
    ("prescaler_inv", "XQ2B", 1, 0, Q2B_X, 0, 1, Q2B_Y),
    ("prescaler_inv", "XQ2R", 1, 0, Q2R_X, 0, 1, Q2R_Y),
]
uses += [("prescaler_antenna", f"XANT_{net}", 1, 0,
          12000 + 600 * i, 0, 1, ANT_Y)
         for i, net in enumerate(antenna_nets)]

labels = [
    ("CLK", 0), ("RESET_B", 1), ("MODULUS_REQUEST", 2),
    ("Q2", 3), ("VDD", 4), ("VSS", 5),
]
# Normalize the generated hierarchy to a zero-based boundary.  The child
# cells and the leftmost Q2 rail extend to (-864, -1500), while LEF/DEF place
# macros relative to (0, 0).  Keeping the GDS/MAG origin identical to the LEF
# origin avoids a physical gap between parent routes and the right-edge pins.
SHIFT_X, SHIFT_Y = 864, 1500
lines = ["magic", "tech ihp-sg13cmos5l", "magscale 1 2", "timestamp 0"]
for cell, name, a, b, c, d, e, f in uses:
    lines += [f"use {cell}  {name}", "timestamp 0",
              f"transform {a} {b} {c + SHIFT_X} {d} {e} {f + SHIFT_Y}",
              "box 0 0 1 1"]
for layer in ("metal1", "via1", "metal2", "via2", "metal3", "via3",
              "metal4", "via4", "m5"):
    if layer in L:
        lines.append(f"<< {layer} >>")
        lines += ["rect %d %d %d %d" %
                  (x0 + SHIFT_X, y0 + SHIFT_Y,
                   x1 + SHIFT_X, y1 + SHIFT_Y)
                  for x0, y0, x1, y1 in L[layer]]
lines.append("<< labels >>")
label_rects = {
    "Q2": (21000 - 62, 23600 - 62, 21000, 23600 + 62),
    "RESET_B": (21000 - 62, 24200 - 62, 21000, 24200 + 62),
    "CLK": (21000 - 62, 24800 - 62, 21000, 24800 + 62),
    "MODULUS_REQUEST": (21000 - 62, 25400 - 62, 21000, 25400 + 62),
    "VDD": (RAIL_X["VDD"] - 62, 300 - 62,
            RAIL_X["VDD"] + 62, 300 + 62),
    "VSS": (RAIL_X["VSS"] - 62, -900 - 62,
            RAIL_X["VSS"] + 62, -900 + 62),
}
for name, port in labels:
    x0, y0, x1, y1 = label_rects[name]
    lines += [f"rlabel metal4 {x0 + SHIFT_X} {y0 + SHIFT_Y} "
              f"{x1 + SHIFT_X} {y1 + SHIFT_Y} 0 {name}",
              f"port {port} nsew"]
lines += ["<< properties >>", "string FIXED_BBOX 0 0 21864 27100",
          "<< end >>", ""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
