#!/usr/bin/env python3
"""Generate the top cell, its symbol and its transient bench from the tables below.

The port list is the Chipalooza project interface, `verilog/rtl/user_project_wrapper_4a.v`
in RTimothyEdwards/sg13cmos5l_ocd_chipalooza — four dedicated analog pads, which means
slot s1 or s16, the only two that have four.

Nets are joined by label rather than by drawn wire: every pin gets a stub and a lab_pin
carrying the net name. That is what keeps a 50-port frame generatable and diffable.
"""
import io
import os

TOP = "sg13cmos5l_chipalooza_analog_project"

# ---------------------------------------------------------------- the interface
# (net, xschem pin symbol, side, comment).  Order is the .subckt port order.
PORTS = [
    # the four dedicated analog pads.  config.txt in the harness repo names them;
    # analog_pin[0..3] there are ref_clk, pll_out, d_p, d_n here.
    ("ref_clk",        "ipin",  "L", "analog_pin[0] - PLL reference in"),
    ("pll_out",        "opin",  "R", "analog_pin[1] - PLL clock out, reserved"),
    ("d_p",            "opin",  "R", "analog_pin[2] - LVDS out +"),
    ("d_n",            "opin",  "R", "analog_pin[3] - LVDS out -"),
    # shared digital
    ("enable",         "ipin",  "L", "project enable"),
    ("clk",            "ipin",  "L", "shared external clock"),
    ("dig_in[23:0]",   "ipin",  "L", "24 shared digital inputs"),
    ("dig_out[11:0]",  "opin",  "R", "12 shared digital outputs"),
    # shared analog
    ("ibias[1:0]",     "iopin", "L", "shared current biases"),
    ("vbias",          "iopin", "L", "shared voltage bias"),
    ("analog_bus[3:0]", "iopin", "R", "shared analog buses"),
    # supplies
    ("vdd_3v3",        "iopin", "L", "gated 3.3 V"),
    ("vdd_1v2",        "iopin", "L", "gated 1.2 V"),
    ("vss_3v3",        "iopin", "L", ""),
    ("vss_1v2",        "iopin", "L", ""),
    ("vssio",          "iopin", "L", "substrate ground"),
]

# ---------------------------------------------------------------- the contents
# pin offsets read off each symbol
PINS = {
    "lvds_pattern": {"ref_clk": (-130, -100), "pll_clk": (-130, -80),
                     "clk_src": (-130, -60), "en": (-130, -40),
                     "reset": (-130, -20), "mode": (-130, 0),
                     "D_p": (130, -100), "D_n": (130, -80),
                     "VDD": (130, 80), "VSS": (130, 100)},
    "lvds_tx": {"D_p": (-150, -50), "D_n": (-150, -30), "Iref_pd": (-150, -10),
                "Iref_drv": (-150, 10), "Vref": (-150, 30),
                "Va": (150, -50), "Out_p": (150, -30), "Out_n": (150, -10),
                "Vss": (150, 10)},
    "and2": {"A": (-60, -20), "B": (-60, 20), "X": (60, 0)},
    "mos": {"D": (20, 30), "G": (-20, 0), "S": (20, -30), "B": (20, 0)},
}

CELLS = [
    # the pattern generator: reference from the dedicated pad, the PLL clock from a
    # dig_in bit until the PLL is placed, the rest of the control from dig_in bits.
    ("xpat", "lvds_pattern.sym", "lvds_pattern", 900, -500, {
        "ref_clk": "ref_clk", "pll_clk": "dig_in[4]", "clk_src": "dig_in[0]",
        "en": "en_gated", "reset": "dig_in[2]", "mode": "dig_in[3]",
        "D_p": "core_p", "D_n": "core_n", "VDD": "vdd_1v2", "VSS": "vss_1v2"}, ""),
    # the transmitter: bias straight off the harness, pair onto two dedicated pads
    ("xlvds", "lvds_tx.sym", "lvds_tx", 1700, -500, {
        "D_p": "core_p", "D_n": "core_n", "Iref_pd": "ibias[0]",
        "Iref_drv": "ibias[1]", "Vref": "vbias", "Va": "vdd_3v3",
        "Out_p": "d_p", "Out_n": "d_n", "Vss": "vss_3v3"}, ""),
    # project enable gates the pattern clock, so an unselected project is idle by
    # construction and all-zero on dig_in is a legal state
    ("xeng", "sg13cmos5l_stdcells/sg13cmos5l_and2_1.sym", "and2", 500, -300, {
        "A": "enable", "B": "dig_in[1]", "X": "en_gated"},
     "VDD=vdd_1v2 VSS=vss_1v2"),
    # decoupling, one per supply domain.  The 3.3 V one must be an HV device.
    ("Cd12", "sg13cmos5l_pr/sg13_lv_pmos.sym", "mos", 2400, -800, {
        "G": "vdd_1v2", "D": "vss_1v2", "S": "vss_1v2", "B": "vss_1v2"},
     "l=10.0u w=10.0u ng=1 m=1 mm_ok=1 model=sg13_lv_pmos spiceprefix=X"),
    ("Cd33", "sg13cmos5l_pr/sg13_hv_pmos.sym", "mos", 2400, -500, {
        "G": "vdd_3v3", "D": "vss_3v3", "S": "vss_3v3", "B": "vss_3v3"},
     "l=10.0u w=10.0u ng=1 m=1 mm_ok=1 model=sg13_hv_pmos spiceprefix=X"),
]

HEADER = """v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}"""

NOTES = """T {Chipalooza 2026 - LVDS transmitter with PRBS-7 generator} 700 -1500 0 0 1 1 {}
T {Port list is verilog/rtl/user_project_wrapper_4a.v from
RTimothyEdwards/sg13cmos5l_ocd_chipalooza.  Four dedicated analog
pads means slot s1 or s16 - the only two that have four.

  analog_pin[0]  ref_clk   PLL reference in
  analog_pin[1]  pll_out   PLL clock out, RESERVED - nothing drives it
                           until the PLL is placed
  analog_pin[2]  d_p       LVDS out +
  analog_pin[3]  d_n       LVDS out -

All four are sg13cmos5l_IOPadAnalog in config.txt, so the core signal
name is the pad name and there is one signal per pad.  Changing a pad
type changes the core-facing signals - an InOut pad becomes five.} 60 -1420 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit
individually to a pin, a constant or the sequencer, so a
configuration bit costs a register write and no pin.

  dig_in[0]   clk_src   0 = ref_clk, 1 = pll_clk
  dig_in[1]   en        gated with the project enable
  dig_in[2]   reset     active high, seeds the PRBS
  dig_in[3]   mode      0 = clock passthrough, 1 = PRBS-7
  dig_in[4]   PROVISIONAL pll_clk, until the PLL is placed
  dig_in[23:5] unused, read as zero, and zero works

dig_out[11:0], analog_bus[3:0] and vssio are not connected
yet.  clk, the shared external clock, is unused: the
reference comes in on its own dedicated pad.} 60 -1000 0 0 0.4 0.4 {}
T {Two supply domains with separate grounds.  The core pair
core_p / core_n crosses from vss_1v2 to vss_3v3 - the two
have to be tied together in the frame, check before tapeout.} 1450 -760 0 0 0.35 0.35 {}"""


def emit_pin(out, inst, pin, net, x, y, dx, dy):
    px, py = x + dx, y + dy
    s = -1 if dx < 0 else 1
    ex = px + s * 40
    out.append("N %d %d %d %d {lab=%s}" % (min(px, ex), py, max(px, ex), py, net))
    out.append("C {lab_pin.sym} %d %d 0 %d {name=l_%s_%s sig_type=std_logic lab=%s}"
               % (ex, py, 0 if s < 0 else 1, inst, pin.lower().replace("[", "").replace("]", ""), net))


def gen_sch(path):
    out = [HEADER, NOTES]
    for inst, sym, fam, x, y, conn, extra in CELLS:
        for pin in sorted(conn):
            dx, dy = PINS[fam][pin]
            emit_pin(out, inst, pin, conn[pin], x, y, dx, dy)
        props = "name=%s" % inst + (("\n" + extra) if extra else "")
        out.append("C {%s} %d %d 0 0 {%s}" % (sym, x, y, props))
    y = -1300
    for net, sym, side, comment in PORTS:
        out.append("N 0 %d 40 %d {lab=%s}" % (y, y, net))
        out.append("C {devices/%s.sym} 0 %d 2 %d {name=p_%s lab=%s}"
                   % (sym, y, 1 if sym == "ipin" else 0,
                      net.replace("[", "").replace("]", "").replace(":", "_"), net))
        out.append("C {lab_pin.sym} 40 %d 0 1 {name=lp_%s sig_type=std_logic lab=%s}"
                   % (y, net.replace("[", "").replace("]", "").replace(":", "_"), net))
        if comment:
            out.append("T {%s} 90 %d 0 0 0.25 0.25 {}" % (comment, y - 8))
        y += 40
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


def gen_sym(path, pex=False):
    out = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}",
           "K {type=%s" % ("primitive" if pex else "subcircuit"),
           'format="@name @pinlist @symname"',
           'spectre_format="@name ( @pinlist ) @symname"',
           'template="name=x1"', "}", "V {}", "S {}", "F {}", "E {}"]
    left = [p for p in PORTS if p[2] == "L"]
    right = [p for p in PORTS if p[2] == "R"]
    w = 200
    n = max(len(left), len(right))
    top, bot = -20 * n - 40, 20 * n + 40
    out.append("P 4 5 %d %d %d %d %d %d %d %d %d %d {}"
               % (-w, top, w, top, w, bot, -w, bot, -w, top))
    out.append("T {@symname} -120 -6 0 0 0.3 0.3 {}")
    out.append("T {@name} %d %d 0 0 0.25 0.25 {}" % (w + 5, top - 14))

    def emit(name, sym, x, y):
        sgn = -1 if x < 0 else 1
        d = {"ipin": "in", "opin": "out", "iopin": "inout"}[sym]
        out.append("B 5 %s %s %s %s {name=%s dir=%s}"
                   % (x + sgn * 17.5, y - 2.5, x + sgn * 22.5, y + 2.5, name, d))
        out.append("L %d %d %d %d %d {}"
                   % (7 if d == "inout" else 4, x, y, x + sgn * 20, y))
        out.append("T {%s} %d %d 0 %d 0.2 0.2 {}"
                   % (name, x - sgn * 6, y - 4, 0 if x < 0 else 1))

    for i, (net, sym, side, c) in enumerate(left):
        emit(net, sym, -w, top + 30 + i * 20)
    for i, (net, sym, side, c) in enumerate(right):
        emit(net, sym, w, top + 30 + i * 20)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ---------------------------------------------------------------- testbench
TB_SOURCES = [
    ("vdd_3v3", "3.3"),
    ("vdd_1v2", "1.2"),
    ("vbias", "1.25"),
    ("ref_clk", "PULSE(0 1.2 0 50p 50p 1.9n 4n)"),
    ("dig_in[4]", "PULSE(0 1.2 0 30p 30p 470p 1n)"),   # provisional pll_clk, 1 GHz
    ("dig_in[0]", "1.2"),                              # clk_src = pll
    ("enable", "1.2"),
    ("dig_in[1]", "PWL(0 0 3n 0 3.1n 1.2)"),           # en
    ("dig_in[2]", "PWL(0 1.2 2n 1.2 2.1n 0)"),         # reset
    ("dig_in[3]", "PWL(0 0 10n 0 10.1n 1.2)"),         # mode -> PRBS-7
]
TB_IREF = [("ibias[0]", "-30u"), ("ibias[1]", "-30u")]

TB_CONTROL = r'''
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_mfringe.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
.options savecurrents klu method=gear reltol=1e-3 abstol=1e-12 gmin=1e-12
.control
save all
op
remzerovec
write @schname\\\\.raw
set appendwrite
tran 5p 40n
write @schname\\\\.raw

let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=20n to=40n
meas tran vod_min MIN vod from=20n to=40n
meas tran vos_avg AVG v(vos) from=20n to=40n
meas tran vos_max MAX v(vos) from=20n to=40n
meas tran vos_min MIN v(vos) from=20n to=40n
let vos_pp = vos_max - vos_min
print vod_max vod_min vos_avg vos_pp
print i(Vvdd_3v3) i(Vvdd_1v2)

unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n)
.endc
'''


def gen_tb(path):
    out = [HEADER]
    out.append("T {Top-level transient bench on the real project interface.\n\n"
               "  ref_clk       250 MHz on the dedicated pad\n"
               "  dig_in[4]     1 GHz, standing in for the PLL\n"
               "  dig_in[0]     clk_src = 1, take the fast clock\n"
               "  dig_in[1]     en, low until 3 ns\n"
               "  dig_in[2]     reset, high until 2 ns\n"
               "  dig_in[3]     mode, PRBS-7 from 10 ns\n"
               "  ibias[1:0]    30 uA each, straight from the harness\n"
               "  vbias         1.25 V\n\n"
               "Load is 49.9 + 49.9 ohm across d_p / d_n with the Vos tap.} "
               "-900 -1700 0 0 0.45 0.45 {}")
    y = -1500
    for net, val in TB_SOURCES:
        tag = net.replace("[", "").replace("]", "")
        out.append("N -600 %d -600 %d {lab=%s}" % (y - 60, y - 30, net))
        out.append("C {lab_pin.sym} -600 %d 1 0 {name=lv_%s sig_type=std_logic lab=%s}"
                   % (y - 60, tag, net))
        out.append('C {devices/vsource.sym} -600 %d 0 0 {name=V%s value="%s"}'
                   % (y, tag, val))
        out.append("N -600 %d -600 %d {lab=GND}" % (y + 30, y + 60))
        out.append("C {devices/gnd.sym} -600 %d 0 0 {name=lg_%s lab=GND}" % (y + 60, tag))
        y += 200
    for net, val in TB_IREF:
        tag = net.replace("[", "").replace("]", "")
        out.append("N -600 %d -600 %d {lab=%s}" % (y - 60, y - 30, net))
        out.append("C {lab_pin.sym} -600 %d 1 0 {name=lv_%s sig_type=std_logic lab=%s}"
                   % (y - 60, tag, net))
        out.append("C {isource.sym} -600 %d 0 0 {name=I%s value=%s}" % (y, tag, val))
        out.append("N -600 %d -600 %d {lab=GND}" % (y + 30, y + 60))
        out.append("C {devices/gnd.sym} -600 %d 0 0 {name=lg_%s lab=GND}" % (y + 60, tag))
        y += 200

    # the block under test
    left = [p for p in PORTS if p[2] == "L"]
    right = [p for p in PORTS if p[2] == "R"]
    n = max(len(left), len(right))
    w, top = 200, -20 * n - 40
    ix, iy = 400, 0
    grounded = {"vss_3v3": "GND", "vss_1v2": "GND", "vssio": "GND"}
    for i, (net, sym, side, c) in enumerate(left):
        py = iy + top + 30 + i * 20
        lab = grounded.get(net, net)
        out.append("N %d %d %d %d {lab=%s}" % (ix - w - 60, py, ix - w, py, lab))
        if net in grounded:
            out.append("C {devices/gnd.sym} %d %d 1 0 {name=lgg_%s lab=GND}"
                       % (ix - w - 60, py, net))
        else:
            out.append("C {lab_pin.sym} %d %d 0 0 {name=lx_%s sig_type=std_logic lab=%s}"
                       % (ix - w - 60, py, net.replace("[", "").replace("]", "").replace(":", "_"), net))
    for i, (net, sym, side, c) in enumerate(right):
        py = iy + top + 30 + i * 20
        out.append("N %d %d %d %d {lab=%s}" % (ix + w, py, ix + w + 60, py, net))
        out.append("C {lab_pin.sym} %d %d 0 1 {name=lx_%s sig_type=std_logic lab=%s}"
                   % (ix + w + 60, py, net.replace("[", "").replace("]", "").replace(":", "_"), net))
    out.append("C {%s.sym} %d %d 0 0 {name=x1}" % (TOP, ix, iy))

    # 49.9 + 49.9 termination with the Vos tap
    out.append("N 1200 -840 1200 -810 {lab=d_n}")
    out.append("C {lab_pin.sym} 1200 -840 1 0 {name=lt1 sig_type=std_logic lab=d_n}")
    out.append("C {res.sym} 1200 -810 0 0 {name=Rtp value=49.9 m=1}")
    out.append("N 1200 -780 1200 -750 {lab=vos}")
    out.append("N 1200 -780 1280 -780 {lab=vos}")
    out.append("C {lab_pin.sym} 1280 -780 0 1 {name=lvos sig_type=std_logic lab=vos}")
    out.append("C {res.sym} 1200 -720 0 0 {name=Rtn value=49.9 m=1}")
    out.append("N 1200 -690 1200 -660 {lab=d_p}")
    out.append("C {lab_pin.sym} 1200 -660 3 0 {name=lt2 sig_type=std_logic lab=d_p}")

    out.append('C {devices/code_shown.sym} -1500 -1500 0 0 {name=NGSPICE\n'
               'only_toplevel=true\nvalue="%s"}' % TB_CONTROL)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sch = os.path.join(here, "..", "schematic", "xschem")
    tb = os.path.join(here, "..", "testbenches", "xschem")
    gen_sch(os.path.join(sch, TOP + ".sch"))
    gen_sym(os.path.join(sch, TOP + ".sym"))
    gen_sym(os.path.join(sch, TOP + "_pex.sym"), pex=True)
    gen_tb(os.path.join(tb, TOP + "_tb_tran.sch"))
    print("wrote %s.sch/.sym/_pex.sym and %s_tb_tran.sch" % (TOP, TOP))
