#!/usr/bin/env python3
"""Generate the TSPC FF with its AO21 input decision folded into stage one."""
import importlib.util
from pathlib import Path


BASE = Path(__file__).with_name("make_tspc_invff.py")
SPEC = importlib.util.spec_from_file_location("tspc_layout_base", BASE)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
m.layers.clear()

OUT = Path(__file__).resolve().parents[2] / "layout/mag/tspc_ao21_invff_r0.mag"
YP, YN = 1600, 0
PX = [700, 2500, 4300, 6100, 7900, 9700]
NX = [0, 1200, 2400, 3600, 5000, 6400, 7600, 8800]

uses = [
    ("dev_p_w0p6_l0p13_ng4_noguard_m1", "XMP_Q2", PX[0], YP),
    ("dev_p_w0p6_l0p13_ng4_noguard_m1", "XMP_Q1", PX[1], YP),
    ("dev_p_w0p6_l0p13_ng4_noguard_m1", "XMP_NMC", PX[2], YP),
    ("dev_p_w0p6_l0p13_ng2_noguard_m1", "XM4", PX[3], YP),
    ("dev_p_w0p6_l0p13_ng4_noguard_m1", "XM6", PX[4], YP),
    ("dev_p_w0p6_l0p13_ng1_noguard_m1", "XRB", PX[5], YP),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "XM3", NX[0], YN),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "XMN_Q2", NX[1], YN),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "XMN_Q1", NX[2], YN),
    ("dev_n_w0p6_l0p13_ng2_noguard_m1", "XMN_NMC", NX[3], YN),
    ("dev_n_w0p6_l0p13_ng6_noguard_m1", "XM5", NX[4], YN),
    ("dev_n_w0p6_l0p13_ng8_noguard_m1", "XM7", NX[5], YN),
    ("dev_n_w0p6_l0p13_ng1_noguard_m1", "XRA", NX[6], YN),
    ("dev_n_w0p6_l0p13_ng1_noguard_m1", "XRQ", NX[7], YN),
]

m.BUS = {
    "VSS": -1100, "P": -900, "N1": -700, "NS": -500,
    "A": -300, "B": -100, "Q": 100, "VDD": 300,
    "Q2": 500, "Q1": 700, "NMC": 900, "CLK": 1100,
    "RST": 1300, "RESET_B": 1500,
}
for y in m.BUS.values():
    m.rect("metal4", -700, y - 29, 10800, y + 29)

m.pmos4(PX[0], "P", "Q2", "VDD", (100, 1050, 1250))
m.pmos4(PX[1], "A", "Q1", "P", (2050, 2850, 3050))
m.pmos4(PX[2], "A", "NMC", "P", (3850, 4650, 4850))
m.pmos2(PX[3], "B", "A", "VDD", (5650, 6350, 7000))
m.pmos4(PX[4], "Q", "CLK", "VDD", (7450, 8250, 8450))
m.pmos1(PX[5], "B", "RESET_B", "VDD", (8650, 10400, 10600))

m.nmos(NX[0], 2, "A", "CLK", "N1", (-500, 300, 500))
m.nmos(NX[1], 2, "N1", "Q2", "VSS", (900, 1500, 1700))
m.nmos(NX[2], 2, "N1", "Q1", "NS", (1900, 2700, 3200))
m.nmos(NX[3], 2, "NS", "NMC", "VSS", (3300, 4000, 4200))
m.nmos(NX[4], 6, "B", "CLK", "VSS", (4500, 5500, 5800))
m.nmos(NX[5], 8, "Q", "B", "VSS", (6000, 6700, 7200))
m.nmos(NX[6], 1, "A", "RST", "VSS", (7300, 7700, 7900))
m.nmos(NX[7], 1, "Q", "RST", "VSS", (8050, 9100, 9300))

m.rect("nwell", -600, 1300, 10900, 2700)
m.rect("nsubdiff", -500, 2550, 10800, 2610)
m.rect("psubdiff", -600, -1410, 10900, -1350)
for layer, y0 in (("nsubdiffcont", 2564), ("psubdiffcont", -1396)):
    for x in range(-456, 10760, 72):
        m.rect(layer, x, y0, x + 32, y0 + 32)
m.rect("metal1", -600, 2550, 10900, 2610)
m.rect("metal1", -600, -1410, 10900, -1350)
for tap_y, bus_y in ((2580, m.BUS["VDD"]), (-1380, m.BUS["VSS"])):
    m.via12(10700, tap_y)
    m.via23(10700, tap_y)
    m.rect("metal3", 10671, min(tap_y, bus_y) - 29,
           10729, max(tap_y, bus_y) + 29)
    m.via34(10700, bus_y)

labels = [
    ("Q2", 0), ("Q1", 1), ("NMC", 2), ("CLK", 3), ("Q", 4),
    ("RST", 5), ("RESET_B", 6), ("VDD", 7), ("VSS", 8),
]
lines = ["magic", "tech ihp-sg13cmos5l", "magscale 1 2", "timestamp 0"]
for cell, name, x, y in uses:
    lines += [f"use {cell}  {name}", "timestamp 0",
              f"transform 1 0 {x} 0 1 {y}", "box 0 0 1 1"]
order = ["nwell", "nsubdiff", "nsubdiffcont", "psubdiff", "psubdiffcont",
         "metal1", "via1", "metal2", "via2", "metal3", "via3", "metal4"]
for layer in order:
    if layer in m.layers:
        lines.append(f"<< {layer} >>")
        lines += ["rect %d %d %d %d" % r for r in m.layers[layer]]
lines.append("<< labels >>")
for name, port in labels:
    y = m.BUS[name]
    lines += [f"rlabel metal4 -700 {y - 29} -640 {y + 29} 0 {name}",
              f"port {port} nsew"]
lines += ["<< end >>", ""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
