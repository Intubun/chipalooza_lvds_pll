#!/usr/bin/env python3
"""Generate the top cell, its symbol and its transient bench.

The port list is exactly `verilog/rtl/user_project_wrapper_4a.v` from
RTimothyEdwards/sg13cmos5l_ocd_chipalooza, with every bus expanded into
individual pins. Four dedicated analog pads means slot s1 or s16 - per config.txt
in that repository the only two that have four.

Nets are joined by label rather than by drawn wire: every pin gets a stub and a
lab_pin carrying the net name. That is what keeps a fifty-port frame generatable.
"""
import io
import os

TOP = "sg13cmos5l_chipalooza_analog_project"


def bus(name, hi, lo=0):
    """MSB first, the way the Verilog declaration reads"""
    return ["%s[%d]" % (name, i) for i in range(hi, lo - 1, -1)]


# (net, xschem pin symbol, side).  Order follows the wrapper declaration.
PORTS = (
    [(n, "iopin", "L") for n in ("vdd_3v3", "vdd_1v2", "vss_3v3", "vss_1v2", "vssio")]
    + [("enable", "ipin", "L"), ("clk", "ipin", "L")]
    + [(n, "ipin", "L") for n in bus("dig_in", 23)]
    + [(n, "opin", "R") for n in bus("dig_out", 11)]
    + [(n, "iopin", "R") for n in bus("analog_pin", 3)]
    + [(n, "ipin", "L") for n in bus("ibias", 1)]
    + [("vbias", "ipin", "L")]
    + [(n, "iopin", "R") for n in bus("analog_bus", 3)]
)

# what the four dedicated pads carry
PAD_USE = [("analog_pin[0]", "PLL reference in, feeds lvds_pattern"),
           ("analog_pin[1]", "PLL clock out - RESERVED, nothing drives it yet"),
           ("analog_pin[2]", "LVDS out +"),
           ("analog_pin[3]", "LVDS out -")]

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
    # reference from the dedicated pad; the PLL clock from a dig_in bit until the
    # PLL is placed; the rest of the control from dig_in bits, which the
    # housekeeping SPI routes individually to a pin, a constant or the sequencer.
    ("xpat", "lvds_pattern.sym", "lvds_pattern", 900, -500, {
        "ref_clk": "analog_pin[0]", "pll_clk": "dig_in[4]", "clk_src": "dig_in[0]",
        "en": "en_gated", "reset": "dig_in[2]", "mode": "dig_in[3]",
        "D_p": "core_p", "D_n": "core_n", "VDD": "vdd_1v2", "VSS": "vss_1v2"}, ""),
    # bias straight off the harness, output pair onto two dedicated pads
    ("xlvds", "lvds_tx.sym", "lvds_tx", 1700, -500, {
        "D_p": "core_p", "D_n": "core_n", "Iref_pd": "ibias[0]",
        "Iref_drv": "ibias[1]", "Vref": "vbias", "Va": "vdd_3v3",
        "Out_p": "analog_pin[2]", "Out_n": "analog_pin[3]", "Vss": "vss_3v3"}, ""),
    # the project enable gates the pattern clock, so an unselected project is idle
    ("xeng", "sg13cmos5l_stdcells/sg13cmos5l_and2_1.sym", "and2", 500, -300, {
        "A": "enable", "B": "dig_in[1]", "X": "en_gated"},
     "VDD=vdd_1v2 VSS=vss_1v2"),
    # decoupling, one per supply domain.  The 3.3 V one has to be an HV device.
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

NOTES = """T {Chipalooza 2026 - LVDS transmitter with PRBS-7 generator} 800 -1900 0 0 1 1 {}
T {Port list is verilog/rtl/user_project_wrapper_4a.v from
RTimothyEdwards/sg13cmos5l_ocd_chipalooza, every bus expanded into
individual pins.  Four dedicated analog pads means slot s1 or s16 -
per config.txt the only two that have four.

  analog_pin[0]  ref_clk   PLL reference in
  analog_pin[1]  pll_out   RESERVED, nothing drives it until the PLL is placed
  analog_pin[2]  d_p       LVDS out +
  analog_pin[3]  d_n       LVDS out -

All four are sg13cmos5l_IOPadAnalog in config.txt, so each pad is one core
signal carrying the pad name.  A different pad type changes that: an InOut
pad becomes five core signals (_in, _out, _ena, _one, _zero).

Not connected yet: dig_out[11:0], analog_bus[3:0], vssio, and clk - the
reference arrives on its own dedicated pad instead of the shared clock pin.} 300 -1820 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit individually to a
pin, a constant or the sequencer, so a configuration bit costs a register
write and no pin.  Unselected holds every dig_in at zero, and all-zero
leaves the clock stopped and the output pair static - a legal idle.

  dig_in[0]    clk_src   0 = ref_clk, 1 = pll_clk
  dig_in[1]    en        ANDed with the project enable
  dig_in[2]    reset     active high, seeds the PRBS
  dig_in[3]    mode      0 = clock passthrough, 1 = PRBS-7
  dig_in[4]    PROVISIONAL pll_clk, until the PLL is placed
  dig_in[23:5] unused} 300 -1400 0 0 0.4 0.4 {}
T {Two supply domains with separate grounds.  core_p / core_n cross from
vss_1v2 into the pre-driver on vss_3v3 - the two grounds have to be tied
together in the frame, check that before tapeout.

No ESD structure on the output pads, and analog_pin[0] runs straight into
a standard-cell input with no receiver.  Both need fixing before tapeout.} 1450 -760 0 0 0.35 0.35 {}"""


def gen_sch(path):
    out = [HEADER, NOTES]
    for inst, sym, fam, x, y, conn, extra in CELLS:
        for pin in sorted(conn):
            dx, dy = PINS[fam][pin]
            px, py = x + dx, y + dy
            s = -1 if dx < 0 else 1
            ex = px + s * 40
            out.append("N %d %d %d %d {lab=%s}"
                       % (min(px, ex), py, max(px, ex), py, conn[pin]))
            tag = pin.lower().replace("[", "").replace("]", "")
            out.append("C {lab_pin.sym} %d %d 0 %d "
                       "{name=l_%s_%s sig_type=std_logic lab=%s}"
                       % (ex, py, 0 if s < 0 else 1, inst, tag, conn[pin]))
        props = "name=%s" % inst + (("\n" + extra) if extra else "")
        out.append("C {%s} %d %d 0 0 {%s}" % (sym, x, y, props))

    use = dict(PAD_USE)
    y = -1300
    for net, sym, side in PORTS:
        tag = net.replace("[", "_").replace("]", "")
        out.append("N 0 %d 40 %d {lab=%s}" % (y, y, net))
        out.append("C {devices/%s.sym} 0 %d 2 %d {name=p_%s lab=%s}"
                   % (sym, y, 1 if sym == "ipin" else 0, tag, net))
        out.append("C {lab_pin.sym} 40 %d 0 1 {name=lp_%s sig_type=std_logic lab=%s}"
                   % (y, tag, net))
        if net in use:
            out.append("T {%s} 100 %d 0 0 0.25 0.25 {}" % (use[net], y - 8))
        y += 20
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


def gen_sym(path, pex=False):
    out = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}",
           "K {type=%s" % ("primitive" if pex else "subcircuit"),
           'format="@name @pinlist @symname"',
           'spectre_format="@name ( @pinlist ) @symname"',
           'template="name=x1"', "}", "V {}", "S {}", "F {}", "E {}"]
    left = [p for p in PORTS if p[2] == "L"]
    right = [p for p in PORTS if p[2] == "R"]
    w = 220
    n = max(len(left), len(right))
    top, bot = -10 * n - 40, 10 * n + 40
    out.append("P 4 5 %d %d %d %d %d %d %d %d %d %d {}"
               % (-w, top, w, top, w, bot, -w, bot, -w, top))
    out.append("T {@symname} -140 -6 0 0 0.3 0.3 {}")
    out.append("T {@name} %d %d 0 0 0.25 0.25 {}" % (w + 5, top - 14))

    def emit(name, sym, x, y):
        sgn = -1 if x < 0 else 1
        d = {"ipin": "in", "opin": "out", "iopin": "inout"}[sym]
        out.append("B 5 %s %s %s %s {name=%s dir=%s}"
                   % (x + sgn * 17.5, y - 2.5, x + sgn * 22.5, y + 2.5, name, d))
        out.append("L %d %d %d %d %d {}"
                   % (7 if d == "inout" else 4, x, y, x + sgn * 20, y))
        out.append("T {%s} %d %d 0 %d 0.18 0.18 {}"
                   % (name, x - sgn * 6, y - 4, 0 if x < 0 else 1))

    for i, (net, sym, side) in enumerate(left):
        emit(net, sym, -w, top + 30 + i * 20)
    for i, (net, sym, side) in enumerate(right):
        emit(net, sym, w, top + 30 + i * 20)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ------------------------------------------------------------------ testbench
TB_SOURCES = [
    ("vdd_3v3", "v", "3.3", "gated 3.3 V"),
    ("vdd_1v2", "v", "1.2", "gated 1.2 V"),
    ("vbias", "v", "1.25", "shared voltage bias, the driver wants 1.25 V"),
    ("analog_pin[0]", "v", "PULSE(0 1.2 0 50p 50p 1.9n 4n)", "ref_clk, 250 MHz"),
    ("dig_in[4]", "v", "PULSE(0 1.2 0 30p 30p 470p 1n)", "PROVISIONAL pll_clk, 1 GHz"),
    ("dig_in[0]", "v", "1.2", "clk_src = 1, take the fast clock"),
    ("enable", "v", "1.2", "project enable"),
    ("dig_in[1]", "v", "PWL(0 0 3n 0 3.1n 1.2)", "en, low until 3 ns"),
    ("dig_in[2]", "v", "PWL(0 1.2 2n 1.2 2.1n 0)", "reset, high until 2 ns"),
    ("dig_in[3]", "v", "PWL(0 0 10n 0 10.1n 1.2)", "mode -> PRBS-7 at 10 ns"),
    ("ibias[0]", "i", "-30u", "pre-driver reference, 30 uA"),
    ("ibias[1]", "i", "-30u", "driver reference, 30 uA"),
]

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

unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n)
.endc
'''


def gen_tb(path):
    out = [HEADER]
    out.append("T {Top-level transient bench.\n\n"
               "  analog_pin[0]  250 MHz reference on the dedicated pad\n"
               "  dig_in[4]      1 GHz, standing in for the PLL\n"
               "  dig_in[0]      clk_src = 1\n"
               "  dig_in[1]      en, low until 3 ns\n"
               "  dig_in[2]      reset, high until 2 ns\n"
               "  dig_in[3]      mode, PRBS-7 from 10 ns\n"
               "  ibias[1:0]     30 uA each, vbias 1.25 V\n\n"
               "Load is 49.9 + 49.9 ohm across analog_pin[2] / analog_pin[3] with the\n"
               "Vos tap.  No pad or ESD model, so the Vos figure is not the compliance\n"
               "number - the driver was characterised with one.} -1700 -2100 0 0 0.45 0.45 {}")
    y = -1900
    for net, kind, val, why in TB_SOURCES:
        tag = net.replace("[", "_").replace("]", "")
        out.append("N -1200 %d -1200 %d {lab=%s}" % (y - 60, y - 30, net))
        out.append("C {lab_pin.sym} -1200 %d 1 0 {name=ls_%s sig_type=std_logic lab=%s}"
                   % (y - 60, tag, net))
        out.append('C {devices/vsource.sym} -1200 %d 0 0 {name=V%s value="%s"}'
                   % (y, tag, val) if kind == "v" else
                   "C {isource.sym} -1200 %d 0 0 {name=I%s value=%s}" % (y, tag, val))
        out.append("N -1200 %d -1200 %d {lab=GND}" % (y + 30, y + 60))
        out.append("C {devices/gnd.sym} -1200 %d 0 0 {name=lg_%s lab=GND}" % (y + 60, tag))
        out.append("T {%s} -1140 %d 0 0 0.3 0.3 {}" % (why, y - 5))
        y += 200

    left = [p for p in PORTS if p[2] == "L"]
    right = [p for p in PORTS if p[2] == "R"]
    n = max(len(left), len(right))
    w, top = 220, -10 * n - 40
    ix, iy = 0, 0
    grounded = {"vss_3v3", "vss_1v2", "vssio"}
    for i, (net, sym, side) in enumerate(left):
        py = iy + top + 30 + i * 20
        tag = net.replace("[", "_").replace("]", "")
        lab = "GND" if net in grounded else net
        out.append("N %d %d %d %d {lab=%s}" % (ix - w - 60, py, ix - w, py, lab))
        if net in grounded:
            out.append("C {devices/gnd.sym} %d %d 1 0 {name=lgg_%s lab=GND}" % (ix - w - 60, py, tag))
        else:
            out.append("C {lab_pin.sym} %d %d 0 0 {name=lx_%s sig_type=std_logic lab=%s}"
                       % (ix - w - 60, py, tag, net))
    for i, (net, sym, side) in enumerate(right):
        py = iy + top + 30 + i * 20
        tag = net.replace("[", "_").replace("]", "")
        out.append("N %d %d %d %d {lab=%s}" % (ix + w, py, ix + w + 60, py, net))
        out.append("C {lab_pin.sym} %d %d 0 1 {name=lx_%s sig_type=std_logic lab=%s}"
                   % (ix + w + 60, py, tag, net))
    out.append("C {%s.sym} %d %d 0 0 {name=x1}" % (TOP, ix, iy))

    # ngspice's frontend reads [ ] as vector indexing, so v(analog_pin[2]) will not
    # parse.  A 0 V source per pad gives the net a plain name to measure on, and
    # its branch current is the pad current for free.
    for x, pad, name in ((700, "analog_pin[3]", "d_n"), (900, "analog_pin[2]", "d_p")):
        out.append("N %d -960 %d -930 {lab=%s}" % (x, x, pad))
        out.append("C {lab_pin.sym} %d -960 1 0 {name=lpad_%s sig_type=std_logic lab=%s}"
                   % (x, name, pad))
        out.append('C {devices/vsource.sym} %d -900 0 0 {name=V%s value=0}' % (x, name))
        out.append("N %d -870 %d -840 {lab=%s}" % (x, x, name))
        out.append("C {lab_pin.sym} %d -840 3 0 {name=lmeas_%s sig_type=std_logic lab=%s}"
                   % (x, name, name))

    # 49.9 + 49.9 across the pair, with the Vos tap
    out.append("N 800 -840 800 -810 {lab=d_n}")
    out.append("C {lab_pin.sym} 800 -840 1 0 {name=lt1 sig_type=std_logic lab=d_n}")
    out.append("C {res.sym} 800 -810 0 0 {name=Rtp value=49.9}")
    out.append("N 800 -780 800 -750 {lab=vos}")
    out.append("N 800 -780 880 -780 {lab=vos}")
    out.append("C {lab_pin.sym} 880 -780 0 1 {name=lvos sig_type=std_logic lab=vos}")
    out.append("C {res.sym} 800 -720 0 0 {name=Rtn value=49.9}")
    out.append("N 800 -690 800 -660 {lab=d_p}")
    out.append("C {lab_pin.sym} 800 -660 3 0 {name=lt2 sig_type=std_logic lab=d_p}")

    out.append('C {devices/code_shown.sym} -2400 -2100 0 0 {name=NGSPICE\n'
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
    print("wrote %s.sch/.sym/_pex.sym and %s_tb_tran.sch, %d ports"
          % (TOP, TOP, len(PORTS)))
