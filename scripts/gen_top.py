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


# ------------------------------------------------- graphs and launchers
# xschem draws waveforms straight into the schematic from the rawfile the deck
# writes.  The launchers run the simulation and load that rawfile, so the whole
# loop stays inside the drawing.


def graph(box, nodes, colors, ymin, ymax, tmin, tmax, divy=5):
    """one waveform panel; box is (x1, y1, x2, y2) in schematic coordinates"""
    x1, y1, x2, y2 = box
    return ("B 2 %d %d %d %d {flags=graph\n"
            "y1=%g\ny2=%g\nypos1=0\nypos2=2\ndivy=%d\nsubdivy=1\nunity=1\n"
            "x1=%g\nx2=%g\ndivx=5\nsubdivx=1\n"
            "xlabmag=1.0\nylabmag=1.0\nlegendmag=1.0\n"
            'node="%s"\ncolor="%s"\n'
            "dataset=-1\nunitx=1\nlogx=0\nlogy=0\nautoload=0\nhilight_wave=-1}"
            % (x1, y1, x2, y2, ymin, ymax, divy, tmin, tmax,
               "\n".join(nodes), " ".join(str(c) for c in colors)))


def launchers(x, y, tb):
    """Simulate and load-waves arrows for testbench `tb`"""
    return [
        'C {launcher.sym} %d %d 0 0 {name=h_sim\n'
        'descr="Simulate"\n'
        'tclcommand="\n'
        'set_sim_defaults\n'
        'file mkdir $netlist_dir\n'
        'write_data [save_params] $netlist_dir/[file rootname '
        '[file tail [xschem get current_name]]].save\n'
        'xschem netlist\n'
        'simulate\n'
        '"}' % (x, y),
        'C {launcher.sym} %d %d 0 0 {name=h_waves\n'
        'descr="Load waves"\n'
        'tclcommand="xschem raw_read $netlist_dir/%s.raw tran"\n'
        '}' % (x, y + 40, tb),
        'C {launcher.sym} %d %d 0 0 {name=h_check\n'
        'descr="Check PRBS + timing"\n'
        'tclcommand="exec python3 [file dirname [xschem get current_dirname]]'
        '/../../scripts/check_timing.py &"\n'
        '}' % (x, y + 80),
    ]


# ------------------------------------------------- LVDS bench for the top cell
# The port list is read out of the symbol rather than taken from PORTS above, so
# this bench keeps working when the top cell is rewired by hand in xschem.

# what each harness pin is driven with; anything not listed is left open
TB_LVDS_DRIVE = {
    "vdd_3v3": ("v", "3.3", "gated 3.3 V"),
    "vdd_1v2": ("v", "1.2", "gated 1.2 V"),
    "vbias": ("v", "1.25", "shared voltage bias, the driver wants 1.25 V"),
    "ibias[0]": ("i", "-30u", "pre-driver reference, 30 uA"),
    "ibias[1]": ("i", "-30u", "driver reference, 30 uA"),
    "enable": ("v", "1.2", "project enable"),
    "analog_pin[0]": ("v", "PULSE(0 1.2 0 50p 50p 0.9n 2n)", "ref_clk, 500 MHz"),
    "dig_in[0]": ("v", "0", "clk_src = 0, take ref_clk"),
    "dig_in[1]": ("v", "PWL(0 0 3n 0 3.1n 1.2)", "en, low until 3 ns"),
    "dig_in[2]": ("v", "PWL(0 1.2 2n 1.2 2.1n 0)", "reset, high until 2 ns"),
    "dig_in[3]": ("v", "1.2", "mode = 1, PRBS-7 throughout"),
    "dig_in[4]": ("v", "PULSE(0 1.2 0 30p 30p 470p 1n)", "provisional pll_clk, 1 GHz"),
}
TB_LVDS_GROUND = ("vss_3v3", "vss_1v2", "vssio")
TB_LVDS_PADS = ("analog_pin[2]", "analog_pin[3]")     # the differential pair

TB_LVDS_CONTROL = r'''
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_mfringe.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
.options savecurrents klu method=gear reltol=1e-3 abstol=1e-12 gmin=1e-12
* Without this the H-bridge cannot balance at t=0, cmfb runs to the rail and the
* pair spends ~60 ns climbing back (tb_startup measures 61.3 ns).  The driver's
* own benches place cmfb the same way and run no operating point.
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.control
* save all over 120 ns at 5 ps writes a 292 MB rawfile; name what the
* measurements, the wrdata and the three graph panels actually need
save d_p d_n vos x1.core_p x1.core_n x1.xpat.gclk_b i(Vvdd_3v3) i(Vvdd_1v2)
* 500 Mb/s means 2 ns a bit, so a full PRBS-7 period is 254 ns.  600 ns gives
* one settling stretch plus about 225 bits of settled data to measure on.
tran 5p 600n 0 5p
write @schname\\\\.raw

* did the pattern generator actually get a clock?  A static pair means the
* control path is broken, not the driver.
meas tran clk_pp PP v(x1.xpat.gclk_b) from=150n to=595n
meas tran core_pp PP v(x1.core_p) from=150n to=595n
print clk_pp core_pp

* TIA/EIA-644-A 4.1.1 and 4.1.2 on the settled pattern
let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=150n to=595n
meas tran vod_min MIN vod from=150n to=595n
meas tran vos_avg AVG v(vos) from=150n to=595n
meas tran vos_max MAX v(vos) from=150n to=595n
meas tran vos_min MIN v(vos) from=150n to=595n
let vos_pp = vos_max - vos_min
* the cold start, kept in the log so the settled number is not mistaken for it
meas tran vos_pp_early PP v(vos) from=20n to=100n
meas tran vos_pp_mid PP v(vos) from=100n to=150n
print vod_max vod_min vos_avg vos_pp
print vos_pp_early vos_pp_mid
print i(Vvdd_3v3) i(Vvdd_1v2)

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n)
.endc
'''


def sym_pins(path):
    """(name, dir, cx, cy) for every pin of a symbol, in file order"""
    import re
    s = io.open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^B 5 (\S+) (\S+) (\S+) (\S+) \{name=([^ }]+) dir=(\w+)",
                         s, re.M):
        x1, y1, x2, y2, name, d = m.groups()
        out.append((name, d, (float(x1) + float(x2)) / 2,
                    (float(y1) + float(y2)) / 2))
    return out


def gen_tb_lvds(path, symbol):
    pins = sym_pins(symbol)
    out = [HEADER]
    out.append("T {LVDS bench for the top cell.\n"
               "\n"
               "Reset, then clock passthrough of the provisional 1 GHz on dig_in[4],\n"
               "then PRBS-7 from 10 ns, through the pre-driver and the driver into\n"
               "49.9 + 49.9 ohm across the two output pads with the Vos tap.\n"
               "\n"
               "The port list is read out of the symbol when this bench is generated,\n"
               "so it survives rewiring of the top cell.  Any harness pin without a\n"
               "source below is left open on purpose.\n"
               "\n"
               "clk_pp and core_pp are checked first: if the gated clock inside the\n"
               "pattern generator is not moving, the control path is broken and the\n"
               "LVDS numbers below it mean nothing.\n"
               "\n"
               "No pad or ESD model - the driver was characterised with one, so the\n"
               "Vos figure here is not the compliance number.} -2200 -1700 0 0 0.45 0.45 {}")

    # stimulus column
    y = -1500
    for name, kind_val in [(n, TB_LVDS_DRIVE[n]) for n, d, cx, cy in pins
                           if n in TB_LVDS_DRIVE]:
        kind, val, why = kind_val
        tag = name.replace("[", "_").replace("]", "")
        out.append("N -1400 %d -1400 %d {lab=%s}" % (y - 60, y - 30, name))
        out.append("C {devices/lab_wire.sym} -1400 %d 0 0 "
                   "{name=ls_%s sig_type=std_logic lab=%s}" % (y - 60, tag, name))
        out.append(('C {devices/vsource.sym} -1400 %d 0 0 {name=V%s value="%s"}'
                    % (y, tag, val)) if kind == "v" else
                   ("C {isource.sym} -1400 %d 0 0 {name=I%s value=%s}" % (y, tag, val)))
        out.append("N -1400 %d -1400 %d {lab=GND}" % (y + 30, y + 60))
        out.append("C {devices/gnd.sym} -1400 %d 0 0 {name=lg_%s lab=GND}" % (y + 60, tag))
        out.append("T {%s} -1340 %d 0 0 0.3 0.3 {}" % (why, y - 5))
        y += 200

    # the block under test, wired by label at every pin
    for name, d, cx, cy in pins:
        # cx is the pin itself.  Offsetting the stub away from it leaves every
        # port on an unconnected auto-net, and the netlist still looks plausible.
        s = -1 if cx < 0 else 1
        px, py = int(cx), int(cy)
        ex = px + s * 60
        tag = name.replace("[", "_").replace("]", "")
        lab = "GND" if name in TB_LVDS_GROUND else name
        out.append("N %d %d %d %d {lab=%s}" % (min(px, ex), py, max(px, ex), py, lab))
        if name in TB_LVDS_GROUND:
            out.append("C {devices/gnd.sym} %d %d %d 0 {name=lgg_%s lab=GND}"
                       % (ex, py, 1 if s < 0 else 3, tag))
        else:
            out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                       "{name=lx_%s sig_type=std_logic lab=%s}" % (ex, py, tag, name))
    out.append("C {%s.sym} 0 0 0 0 {name=x1}" % TOP)

    # ngspice reads [ ] as vector indexing, so v(analog_pin[2]) will not parse.
    # A 0 V source per pad gives the net a plain name and its branch current.
    for x, pad, name in ((700, TB_LVDS_PADS[1], "d_n"), (900, TB_LVDS_PADS[0], "d_p")):
        out.append("N %d -960 %d -930 {lab=%s}" % (x, x, pad))
        out.append("C {devices/lab_wire.sym} %d -960 0 0 "
                   "{name=lpad_%s sig_type=std_logic lab=%s}" % (x, name, pad))
        out.append('C {devices/vsource.sym} %d -900 0 0 {name=V%s value=0}' % (x, name))
        out.append("N %d -870 %d -840 {lab=%s}" % (x, x, name))
        out.append("C {devices/lab_wire.sym} %d -840 0 0 "
                   "{name=lmeas_%s sig_type=std_logic lab=%s}" % (x, name, name))

    # 49.9 + 49.9 across the pair with the Vos tap
    out += ["N 800 -840 800 -810 {lab=d_n}",
            "C {devices/lab_wire.sym} 800 -840 0 0 {name=lt1 sig_type=std_logic lab=d_n}",
            "C {res.sym} 800 -810 0 0 {name=Rtp value=49.9}",
            "N 800 -780 800 -750 {lab=vos}",
            "N 800 -780 880 -780 {lab=vos}",
            "C {devices/lab_wire.sym} 880 -780 0 0 {name=lvos sig_type=std_logic lab=vos}",
            "C {res.sym} 800 -720 0 0 {name=Rtn value=49.9}",
            "N 800 -690 800 -660 {lab=d_p}",
            "C {devices/lab_wire.sym} 800 -660 0 0 {name=lt2 sig_type=std_logic lab=d_p}"]

    # top panel spans the whole run so the cold start is visible; the two below
    # are zoomed onto a few settled bits
    panels = [((1500, -1240, 3100, -940), ["d_p", "d_n", "vos"], [4, 5, 8],
               0.9, 1.6, 0.0, 6.0e-7),
              ((1500, -920, 3100, -620), ["x1.xpat.gclk_b", "x1.core_p", "x1.core_n"],
               [4, 7, 5], -0.2, 1.4, 3.00e-7, 3.10e-7),
              ((1500, -600, 3100, -300), ["d_p", "d_n", "vod"], [4, 5, 7],
               -0.5, 1.6, 3.00e-7, 3.10e-7)]
    for box, nodes, colors, ymin, ymax, t0, t1 in panels:
        out.append(graph(box, nodes, colors, ymin, ymax, t0, t1))
    out += launchers(1500, -1320, TOP + "_tb_lvds")

    out.append('C {devices/code_shown.sym} -2200 -1300 0 0 {name=NGSPICE\n'
               'only_toplevel=true\nvalue="%s"}' % TB_LVDS_CONTROL)
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
meas tran vod_max MAX vod from=150n to=595n
meas tran vod_min MIN vod from=150n to=595n
meas tran vos_avg AVG v(vos) from=150n to=595n
meas tran vos_max MAX v(vos) from=150n to=595n
meas tran vos_min MIN v(vos) from=150n to=595n
let vos_pp = vos_max - vos_min
print vod_max vod_min vos_avg vos_pp

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


# --------------------------------------------- PLL bench: 250 MHz in, PRBS out
# The reference goes in on the dedicated pad, the PLL multiplies it, and the
# pattern generator runs off PLL_CLK instead of the reference.
#
# pll_clk is always VCO/2 (clock_output_divider.v), and the feedback divider
# divides the VCO by DIV_RATIO / 8, so
#
#     pll_clk = REF * (DIV_RATIO / 8) / 2
#
# 250 MHz in and 500 Mb/s out therefore wants DIV_RATIO = 4.0 (code 32),
# i.e. a 1 GHz VCO. DIV_RATIO[9:0] sits on dig_in[16:7], so bit 5 is dig_in[12].
TB_PLL_DRIVE = {
    "vdd_3v3": ("v", "3.3", "gated 3.3 V"),
    "vdd_1v2": ("v", "1.2", "gated 1.2 V"),
    "vbias": ("v", "1.25", "shared voltage bias"),
    "ibias[0]": ("i", "-30u", "pre-driver reference"),
    "ibias[1]": ("i", "-30u", "driver reference"),
    "analog_bus[0]": ("i", "-30u", "PLL charge-pump reference"),
    "enable": ("v", "1.2", "project enable"),
    "analog_pin[0]": ("v", "PULSE(0 1.2 0 50p 50p 1.9n 4n)", "REF_CLK, 250 MHz"),
    "dig_in[0]": ("v", "1.2", "clk_src = 1, run the pattern generator off the PLL"),
    "dig_in[1]": ("v", "PWL(0 0 40n 0 40.1n 1.2)", "pattern en, held off while the PLL settles"),
    "dig_in[2]": ("v", "PWL(0 1.2 39n 1.2 39.1n 0)", "PRBS reset, released just before en"),
    "dig_in[3]": ("v", "1.2", "mode = 1, PRBS-7"),
    "dig_in[5]": ("v", "PWL(0 0 2n 0 2.1n 1.2)", "PLL ENABLE"),
    "dig_in[6]": ("v", "PWL(0 0 1n 0 1.1n 1.2)", "PLL RESET_N, active low"),
    "dig_in[12]": ("v", "1.2", "DIV_RATIO[5] -> DIV_RATIO = 4.0"),
}

TB_PLL_CONTROL = r'''
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_mfringe.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.options savecurrents klu method=gear reltol=1e-3 abstol=1e-12 gmin=1e-12
.control
save d_p d_n vos x1.core_p x1.core_n x1.pll_clk x1.xpll.VCTRL x1.xpll.VCO_CLK
tran 5p 1u 0 5p
write @schname\\\\.raw

* First question: does the loop do anything at all?  VCTRL has to move and the
* VCO has to oscillate before any of the numbers below mean anything.
meas tran vctrl_min MIN v(x1.xpll.VCTRL) from=50n to=990n
meas tran vctrl_max MAX v(x1.xpll.VCTRL) from=50n to=990n
meas tran vctrl_end AVG v(x1.xpll.VCTRL) from=900n to=990n
meas tran vco_pp PP v(x1.xpll.VCO_CLK) from=900n to=990n
print vctrl_min vctrl_max vctrl_end vco_pp

* Second: is pll_clk at 500 MHz?  Two consecutive rising edges give the period.
meas tran t1 WHEN v(x1.pll_clk)=0.6 RISE=200
meas tran t2 WHEN v(x1.pll_clk)=0.6 RISE=201
let f_pll = 1/(t2-t1)
print f_pll

* Third: what comes out of the transmitter, once the pattern generator runs
let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=200n to=990n
meas tran vod_min MIN vod from=200n to=990n
meas tran vos_avg AVG v(vos) from=200n to=990n
meas tran vos_max MAX v(vos) from=200n to=990n
meas tran vos_min MIN v(vos) from=200n to=990n
let vos_pp = vos_max - vos_min
meas tran core_pp PP v(x1.core_p) from=200n to=990n
print vod_max vod_min vos_avg vos_pp core_pp

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.pll_clk) v(x1.xpll.VCTRL)
.endc
'''

TB_PLL_TITLE = (
    "T {PLL bench: 250 MHz reference in, PRBS-7 at 500 Mb/s out.\n"
    "\n"
    "  pll_clk = REF * (DIV_RATIO / 8) / 2, because clock_output_divider.v\n"
    "  always halves the VCO.  250 MHz and DIV_RATIO = 4.0 (code 32) give\n"
    "  a 1 GHz VCO and a 500 MHz bit clock. DIV_RATIO[5] is dig_in[12].\n"
    "\n"
    "  1 ns    PLL RESET_N released\n"
    "  2 ns    PLL ENABLE\n"
    "  39 ns   PRBS reset released\n"
    "  40 ns   pattern generator enabled, running off PLL_CLK\n"
    "\n"
    "The loop is checked before the transmitter: VCTRL has to move and the VCO\n"
    "has to oscillate, otherwise the LVDS numbers are meaningless.\n"
    "\n"
    "KNOWN BLOCKER: the loop filter's two cap_cmomf have no symbol in this PDK,\n"
    "so the filter is only its resistor and the control node has no capacitance.\n"
    "Expect no lock until that is resolved.} -2400 -2100 0 0 0.45 0.45 {}")


def gen_tb_pll(path, symbol):
    pins = sym_pins(symbol)
    out = [HEADER, TB_PLL_TITLE]
    y = -1900
    for name, d, cx, cy in pins:
        if name not in TB_PLL_DRIVE:
            continue
        kind, val, why = TB_PLL_DRIVE[name]
        tag = name.replace("[", "_").replace("]", "")
        out.append("N -1400 %d -1400 %d {lab=%s}" % (y - 60, y - 30, name))
        out.append("C {devices/lab_wire.sym} -1400 %d 0 0 "
                   "{name=ls_%s sig_type=std_logic lab=%s}" % (y - 60, tag, name))
        out.append(('C {devices/vsource.sym} -1400 %d 0 0 {name=V%s value="%s"}'
                    % (y, tag, val)) if kind == "v" else
                   ("C {isource.sym} -1400 %d 0 0 {name=I%s value=%s}" % (y, tag, val)))
        out.append("N -1400 %d -1400 %d {lab=GND}" % (y + 30, y + 60))
        out.append("C {devices/gnd.sym} -1400 %d 0 0 {name=lg_%s lab=GND}" % (y + 60, tag))
        out.append("T {%s} -1340 %d 0 0 0.3 0.3 {}" % (why, y - 5))
        y += 200

    for name, d, cx, cy in pins:
        s = -1 if cx < 0 else 1
        px, py = int(cx), int(cy)
        ex = px + s * 60
        tag = name.replace("[", "_").replace("]", "")
        lab = "GND" if name in TB_LVDS_GROUND else name
        out.append("N %d %d %d %d {lab=%s}" % (min(px, ex), py, max(px, ex), py, lab))
        if name in TB_LVDS_GROUND:
            out.append("C {devices/gnd.sym} %d %d %d 0 {name=lgg_%s lab=GND}"
                       % (ex, py, 1 if s < 0 else 3, tag))
        else:
            out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                       "{name=lx_%s sig_type=std_logic lab=%s}" % (ex, py, tag, name))
    out.append("C {%s.sym} 0 0 0 0 {name=x1}" % TOP)

    for x, pad, name in ((700, TB_LVDS_PADS[1], "d_n"), (900, TB_LVDS_PADS[0], "d_p")):
        out.append("N %d -960 %d -930 {lab=%s}" % (x, x, pad))
        out.append("C {devices/lab_wire.sym} %d -960 0 0 "
                   "{name=lpad_%s sig_type=std_logic lab=%s}" % (x, name, pad))
        out.append('C {devices/vsource.sym} %d -900 0 0 {name=V%s value=0}' % (x, name))
        out.append("N %d -870 %d -840 {lab=%s}" % (x, x, name))
        out.append("C {devices/lab_wire.sym} %d -840 0 0 "
                   "{name=lmeas_%s sig_type=std_logic lab=%s}" % (x, name, name))

    out += ["N 800 -840 800 -810 {lab=d_n}",
            "C {devices/lab_wire.sym} 800 -840 0 0 {name=lt1 sig_type=std_logic lab=d_n}",
            "C {res.sym} 800 -810 0 0 {name=Rtp value=49.9}",
            "N 800 -780 800 -750 {lab=vos}",
            "N 800 -780 880 -780 {lab=vos}",
            "C {devices/lab_wire.sym} 880 -780 0 0 {name=lvos sig_type=std_logic lab=vos}",
            "C {res.sym} 800 -720 0 0 {name=Rtn value=49.9}",
            "N 800 -690 800 -660 {lab=d_p}",
            "C {devices/lab_wire.sym} 800 -660 0 0 {name=lt2 sig_type=std_logic lab=d_p}"]

    panels = [((1500, -1240, 3100, -940), ["x1.xpll.VCTRL"], [8], 0.0, 1.3, 0.0, 1.0e-6),
              ((1500, -920, 3100, -620), ["x1.pll_clk", "x1.core_p"], [4, 7],
               -0.2, 1.4, 5.00e-7, 5.10e-7),
              ((1500, -600, 3100, -300), ["d_p", "d_n", "vos"], [4, 5, 8],
               0.9, 1.6, 5.00e-7, 5.10e-7)]
    for box, nodes, colors, ymin, ymax, t0, t1 in panels:
        out.append(graph(box, nodes, colors, ymin, ymax, t0, t1))
    out += launchers(1500, -1320, TOP + "_tb_pll")

    out.append('C {devices/code_shown.sym} -2400 -1300 0 0 {name=NGSPICE\n'
               'only_toplevel=true\nvalue="%s"}' % TB_PLL_CONTROL)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    sch = os.path.join(here, "..", "schematic", "xschem")
    tb = os.path.join(here, "..", "testbenches", "xschem")
    sym = os.path.join(sch, TOP + ".sym")
    # The top cell is edited by hand in xschem, so regenerating it would throw
    # that work away.  It only happens when asked for explicitly.
    if "--schematic" in sys.argv:
        gen_sch(os.path.join(sch, TOP + ".sch"))
        gen_sym(sym)
        gen_sym(os.path.join(sch, TOP + "_pex.sym"), pex=True)
        gen_tb(os.path.join(tb, TOP + "_tb_tran.sch"))
        print("regenerated the top cell, its symbols and the tran bench")
    else:
        print("top cell left alone - pass --schematic to regenerate it")
    gen_tb_lvds(os.path.join(tb, TOP + "_tb_lvds.sch"), sym)
    gen_tb_pll(os.path.join(tb, TOP + "_tb_pll.sch"), sym)
    print("wrote %s_tb_lvds.sch from the %d pins of %s.sym"
          % (TOP, len(sym_pins(sym)), TOP))
