#!/usr/bin/env python3
"""Generate lvds_pattern.sch and lvds_pattern.sym from the cell table below.

The block is pure sg13cmos5l standard cells. Writing it out from a table rather
than drawing it keeps the drawing and the net list in step: every pin of every
cell is named here exactly once, and a pin left out of the table simply does not
appear in the schematic.

Nets are joined by label, not by drawn wire. Each pin gets a 40-unit stub and a
lab_pin carrying the net name, which is what makes an 18-cell block readable
without a router.
"""
import io
import os

# ---------------------------------------------------------------- cell library
# pin name -> (dx, dy) offset from the instance origin, read off the PDK symbols
PINS = {
    "mux2":  {"A0": (-40, -20), "A1": (-40, 20), "S": (-40, 60), "X": (40, 0)},
    "lgcp":  {"CLK": (-90, -10), "GATE": (-90, 10), "GCLK": (90, -10)},
    "buf":   {"A": (-40, 0), "X": (40, 0)},
    "inv":   {"A": (-40, 0), "Y": (40, 0)},
    "dfrbp": {"CLK": (-90, -20), "D": (-90, 0), "RESET_B": (-90, 20),
              "Q": (90, -20), "Q_N": (90, 0)},
    "xnor2": {"A": (-60, -20), "B": (-60, 20), "Y": (60, 0)},
    "xor2":  {"A": (-60, -20), "B": (-60, 20), "X": (60, 0)},
}

FLOP_X = [400, 700, 1000, 1300, 1600, 1900, 2200]

# (instance, standard cell, family, x, y, {pin: net})
CELLS = [
    # clock source select, then the latch-based clock gate
    ("xcsel", "mux2_2", "mux2", 400, -600,
     {"A0": "ref_clk", "A1": "pll_clk", "S": "clk_src", "X": "clk_sel"}),
    ("xicg", "lgcp_1", "lgcp", 750, -600,
     {"CLK": "clk_sel", "GATE": "en", "GCLK": "gclk"}),
    ("xclkb", "buf_4", "buf", 1050, -610,
     {"A": "gclk", "X": "gclk_b"}),
    # reset is active high on the port and active low on the flops
    ("xrstb", "inv_2", "inv", 400, -450,
     {"A": "reset", "Y": "reset_b"}),
]

# PRBS-7 shift register. The flops hold the COMPLEMENT of the LFSR word - see
# README: that is what lets a reset-to-zero flop produce the all-ones seed.
for _i, _x in enumerate(FLOP_X):
    _drive = "_2" if _i >= 5 else "_1"        # s5 and s6 carry the extra fanout
    _d = "fb" if _i == 0 else "s%d" % (_i - 1)
    CELLS.append(("xs%d" % _i, "dfrbp" + _drive, "dfrbp", _x, -100,
                  {"CLK": "gclk_b", "D": _d, "RESET_B": "reset_b",
                   "Q": "s%d" % _i, "Q_N": "s%d_n" % _i}))

CELLS += [
    # feedback: s0 <- XNOR(s6, s5), the complement of lfsr[6] ^ lfsr[5]
    ("xfb", "xnor2_1", "xnor2", 2200, 200,
     {"A": "s6", "B": "s5", "Y": "fb"}),
    # mode: 0 = gated clock straight through, 1 = PRBS-7.
    # A1 is s6_n, which is lfsr[6] - the same bit serdes_dig.v puts on the line.
    ("xmode", "mux2_2", "mux2", 2550, -600,
     {"A0": "gclk_b", "A1": "s6_n", "S": "mode", "X": "d"}),
    # Complementary output pair, sized for the real load: D_p and D_n each drive
    # two 40u/0.45u HV gates in the pre-driver, about 170 fF. Two identical
    # inv_2 -> inv_8 front ends, then buf_16 on the true side (a buf is two
    # internal stages, so four inversions in all) against inv_16 on the
    # complement side (three). The parity of a single-ended source cannot be
    # matched exactly; this pairing measured 23 ps of D_p/D_n skew at 170 fF,
    # against the pre-driver's ~40 ps budget in docs/predriver-findings.md.
    # An XOR/XNOR pair against VSS was tried first and measured 48 ps.
    ("xp1", "inv_2", "inv", 2900, -740, {"A": "d", "Y": "dp1"}),
    ("xp2", "inv_8", "inv", 3150, -740, {"A": "dp1", "Y": "dp2"}),
    ("xbp", "buf_16", "buf", 3400, -740, {"A": "dp2", "X": "D_p"}),
    ("xn1", "inv_2", "inv", 2900, -480, {"A": "d", "Y": "dn1"}),
    ("xn2", "inv_8", "inv", 3150, -480, {"A": "dn1", "Y": "dn2"}),
    ("xbn", "inv_16", "inv", 3400, -480, {"A": "dn2", "Y": "D_n"}),
]

# port column: (net, xschem pin symbol, y)
PORTS = [
    ("ref_clk", "ipin", -900),
    ("pll_clk", "ipin", -880),
    ("clk_src", "ipin", -860),
    ("en", "ipin", -840),
    ("reset", "ipin", -820),
    ("mode", "ipin", -800),
    ("D_p", "opin", -760),
    ("D_n", "opin", -740),
    ("VDD", "iopin", -700),
    ("VSS", "iopin", -680),
]

HEADER = """v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}"""

NOTES = """T {lvds_pattern - data source for the LVDS transmitter, sg13cmos5l standard cells only.

  clk_src   0 = ref_clk, 1 = pll_clk
  en        1 = clock runs, 0 = clock stopped low (latch-based gate, no runt pulse)
  reset     active high, asynchronous, seeds the PRBS
  mode      0 = gated clock straight to the pair, 1 = PRBS-7

D_p / D_n drive the pre-driver of macros/lvds_tx.} 200 -1150 0 0 0.5 0.5 {}
T {Clock source select, then the latch-based clock gate. GCLK is held low
while en is 0, so en may change at any time without a runt pulse.} 300 -720 0 0 0.35 0.35 {}
T {PRBS-7, x^7 + x^6 + 1. The flops hold the COMPLEMENT of the LFSR word:
dfrbp resets Q to 0, and an all-zero complement is the all-ones seed that
serdes_dig.v uses. The feedback is XNOR for the same reason, and the line
bit is s6_n. The stream is bit-identical to serdes_dig.v in PRBS7 mode.} 300 300 0 0 0.35 0.35 {}
T {Complementary output pair, sized for ~170 fF: D_p and D_n each drive two
40u/0.45u HV gates in the pre-driver. Matched inv_2 -> inv_8 front ends, then
buf_16 (two internal stages, four inversions) against inv_16 (three), which is
the pairing that measured the least D_p/D_n skew into that load: 23 ps, against
the pre-driver's ~40 ps budget. XOR/XNOR against VSS measured 48 ps.} 2700 -900 0 0 0.35 0.35 {}"""


def gen_sch(path):
    out = [HEADER, NOTES]
    for inst, cell, fam, x, y, conn in CELLS:
        for pin in sorted(conn):
            net = conn[pin]
            dx, dy = PINS[fam][pin]
            px, py = x + dx, y + dy
            s = -1 if dx < 0 else 1
            ex = px + s * 40
            out.append("N %d %d %d %d {lab=%s}"
                       % (min(px, ex), py, max(px, ex), py, net))
            out.append("C {lab_pin.sym} %d %d 0 %d "
                       "{name=l_%s_%s sig_type=std_logic lab=%s}"
                       % (ex, py, 0 if s < 0 else 1, inst, pin.lower(), net))
        out.append("C {sg13cmos5l_stdcells/sg13cmos5l_%s.sym} %d %d 0 0 {name=%s}"
                   % (cell, x, y, inst))
    for net, sym, y in PORTS:
        out.append("N 0 %d 40 %d {lab=%s}" % (y, y, net))
        out.append("C {devices/%s.sym} 0 %d 2 %d {name=p_%s lab=%s}"
                   % (sym, y, 1 if sym == "ipin" else 0, net, net))
        out.append("C {lab_pin.sym} 40 %d 0 1 "
                   "{name=lp_%s sig_type=std_logic lab=%s}" % (y, net, net))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


SYM_PINS = [("ref_clk", "in"), ("pll_clk", "in"), ("clk_src", "in"),
            ("en", "in"), ("reset", "in"), ("mode", "in"),
            ("D_p", "out"), ("D_n", "out"),
            ("VDD", "inout"), ("VSS", "inout")]


def gen_sym(path):
    out = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}",
           "K {type=subcircuit", 'format="@name @pinlist @symname"',
           'template="name=x1"', "}", "V {}", "S {}", "E {}"]
    w, top, bot = 110, -120, 120
    out.append("P 4 5 %d %d %d %d %d %d %d %d %d %d {}"
               % (-w, top, w, top, w, bot, -w, bot, -w, top))
    out.append("T {@symname} -60 -6 0 0 0.3 0.3 {}")
    out.append("T {@name} %d %d 0 0 0.2 0.2 {}" % (w + 5, top - 12))

    def emit(name, direction, x, y):
        sgn = -1 if x < 0 else 1
        out.append("B 5 %s %s %s %s {name=%s dir=%s}"
                   % (x + sgn * 17.5, y - 2.5, x + sgn * 22.5, y + 2.5,
                      name, direction))
        out.append("L %d %d %d %d %d {}"
                   % (7 if direction == "inout" else 4, x, y, x + sgn * 20, y))
        out.append("T {%s} %d %d 0 %d 0.2 0.2 {}"
                   % (name, x - sgn * 5, y - 4, 0 if x < 0 else 1))

    for i, (name, d) in enumerate([p for p in SYM_PINS if p[1] == "in"]):
        emit(name, d, -w, top + 20 + i * 20)
    for i, (name, d) in enumerate([p for p in SYM_PINS if p[1] == "out"]):
        emit(name, d, w, top + 20 + i * 20)
    for i, (name, d) in enumerate([p for p in SYM_PINS if p[1] == "inout"]):
        emit(name, d, w, bot - 40 + i * 20)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ---------------------------------------------------------------- testbench
# (net, source value).  One stimulus per control line, so the sequence the bench
# walks through is readable in one place.
TB_SOURCES = [
    ("VDD", "1.2"),
    ("ref_clk", "PULSE(0 1.2 0 50p 50p 1.9n 4n)"),
    ("pll_clk", "PULSE(0 1.2 0 30p 30p 470p 1n)"),
    # pll until 160 ns, then the reference, to show the source select
    ("clk_src", "PWL(0 1.2 160n 1.2 160.1n 0)"),
    # clock off until 3 ns, off again over 150...155 ns to show the clock gate
    ("en", "PWL(0 0 3n 0 3.1n 1.2 150n 1.2 150.1n 0 155n 0 155.1n 1.2)"),
    # asynchronous seed of the PRBS
    ("reset", "PWL(0 1.2 2n 1.2 2.1n 0)"),
    # clock passthrough until 12 ns, PRBS-7 after
    ("mode", "PWL(0 0 12n 0 12.1n 1.2)"),
]

TB_CONTROL = r'''
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.lib cornerMOSlv.lib mos_tt
.temp 27
.options savecurrents klu reltol=1e-3
.control
save all
tran 5p 200n
write @schname\\\\.raw

* the pair has to be complementary at every instant
let dsum = v(D_p)+v(D_n)
meas tran dsum_min MIN dsum from=20n to=140n
meas tran dsum_max MAX dsum from=20n to=140n

* D_p rising against D_n falling on the same bit: this is the skew the
* pre-driver sees, budget about 40 ps (docs/predriver-findings.md)
meas tran tp_r WHEN v(D_p)=0.6 RISE=5
meas tran tn_f WHEN v(D_n)=0.6 FALL=5
let skew = tn_f - tp_r
print skew

* clock passthrough period, measured before mode goes high
meas tran t1 WHEN v(D_p)=0.6 RISE=4
meas tran t2 WHEN v(D_p)=0.6 RISE=5
let tpass = t2 - t1
print tpass

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(D_p) v(D_n) v(x1.gclk_b) v(mode) v(en)
.endc
'''


def gen_tb(path):
    out = [HEADER]
    out.append("T {lvds_pattern transient bench.\n\n"
               "  0...2 ns     reset high, clock stopped\n"
               "  3 ns         en high, clock passthrough of pll_clk at 1 GHz\n"
               "  12 ns        mode high, PRBS-7 at 1 Gb/s\n"
               "  150...155 ns en low, the clock gate stops the pattern\n"
               "  160 ns       clk_src low, the 250 MHz reference takes over\n\n"
               "scripts/check_prbs.py re-runs the polynomial over the exported\n"
               "data and counts the bits that do not match.} "
               "100 -1200 0 0 0.45 0.45 {}")
    y = -1000
    for net, val in TB_SOURCES:
        out.append("N 150 %d 150 %d {lab=%s}" % (y - 60, y - 30, net))
        out.append("C {lab_pin.sym} 150 %d 1 0 "
                   "{name=lv_%s sig_type=std_logic lab=%s}" % (y - 60, net, net))
        out.append('C {devices/vsource.sym} 150 %d 0 0 {name=V%s value="%s"}'
                   % (y, net, val))
        out.append("N 150 %d 150 %d {lab=GND}" % (y + 30, y + 60))
        out.append("C {devices/gnd.sym} 150 %d 0 0 {name=lg_%s lab=GND}" % (y + 60, net))
        y += 200
    # the block under test
    ports = [("ref_clk", -110, -100), ("pll_clk", -110, -80), ("clk_src", -110, -60),
             ("en", -110, -40), ("reset", -110, -20), ("mode", -110, 0),
             ("D_p", 110, -100), ("D_n", 110, -80),
             ("VDD", 110, 80), ("VSS", 110, 100)]
    ix, iy = 700, 0
    for net, dx, dy in ports:
        px, py = ix + dx, iy + dy
        s = -1 if dx < 0 else 1
        ex = px + s * 60
        out.append("N %d %d %d %d {lab=%s}"
                   % (min(px, ex), py, max(px, ex), py, "0" if net == "VSS" else net))
        if net == "VSS":
            out.append("C {devices/gnd.sym} %d %d 3 0 {name=lg_vss lab=GND}" % (ex, py))
        else:
            out.append("C {lab_pin.sym} %d %d 0 %d "
                       "{name=lx_%s sig_type=std_logic lab=%s}"
                       % (ex, py, 0 if s < 0 else 1, net, net))
    out.append("C {lvds_pattern.sym} %d %d 0 0 {name=x1}" % (ix, iy))
    # the load the pre-driver actually presents: two 40u/0.45u HV gates per side
    for net, cy in (("D_p", -300), ("D_n", -100)):
        out.append("N 1000 %d 1000 %d {lab=%s}" % (cy - 60, cy - 30, net))
        out.append("C {lab_pin.sym} 1000 %d 1 0 "
                   "{name=lc_%s sig_type=std_logic lab=%s}" % (cy - 60, net, net))
        out.append("C {capa.sym} 1000 %d 0 0 {name=C%s m=1 value=170f}" % (cy, net))
        out.append("N 1000 %d 1000 %d {lab=GND}" % (cy + 30, cy + 60))
        out.append("C {devices/gnd.sym} 1000 %d 0 0 {name=lgc_%s lab=GND}" % (cy + 60, net))
    out.append('C {devices/code_shown.sym} 1200 -1000 0 0 {name=NGSPICE\n'
               'only_toplevel=true\n'
               'value="%s"}' % TB_CONTROL)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sch = os.path.join(here, "..", "schematic", "xschem")
    tb = os.path.join(here, "..", "testbenches", "xschem")
    gen_sch(os.path.join(sch, "lvds_pattern.sch"))
    gen_sym(os.path.join(sch, "lvds_pattern.sym"))
    gen_tb(os.path.join(tb, "lvds_pattern_tb_tran.sch"))
    print("wrote lvds_pattern.sch (%d cells), lvds_pattern.sym, "
          "lvds_pattern_tb_tran.sch" % len(CELLS))
