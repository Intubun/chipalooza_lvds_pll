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
           ("analog_pin[1]", "PLL clock out - the PLL's TEST_CLK"),
           ("analog_pin[2]", "LVDS out +"),
           ("analog_pin[3]", "LVDS out -")]

# Where every port in the left-hand column actually goes, so the sheet answers
# "what is this pin wired to" without tracing a label across the drawing.  Read
# off the netlist of the top cell; keep it in step when the wiring changes.
NC = "not connected"
PIN_USE = dict(
    [("vdd_3v3", "xlvds.Va, Cd33 decoupling"),
     ("vdd_1v2", "xpat.VDD, xpll.VDD, Cd12 decoupling"),
     ("vss_3v3", "xlvds.Vss, Cd33 decoupling"),
     ("vss_1v2", "xpat.VSS, xpll.VSS, Cd12 decoupling"),
     ("vssio", NC),
     ("enable", NC),
     ("clk", NC + " - the reference comes in on analog_pin[0]"),
     ("dig_in[18]", "xpll.TEST_DIV[1]"),
     ("dig_in[17]", "xpll.TEST_DIV[0]"),
     ("dig_in[6]", "xpll.RESET_N - active low"),
     ("dig_in[5]", "xpll.ENABLE"),
     ("dig_in[4]", NC + " - was the provisional pll_clk"),
     ("dig_in[3]", "xpat.mode - 0 = clock passthrough, 1 = PRBS-7"),
     ("dig_in[2]", "xpat.reset - active high, seeds the PRBS"),
     ("dig_in[1]", "xpat.en - gates the pattern clock"),
     ("dig_in[0]", "xpat.clk_src - 0 = ref_clk, 1 = pll_clk"),
     ("ibias[1]", "xlvds.Iref_drv - 2 uA, mirrored 1:15 to the driver's 30 uA"),
     ("ibias[0]", "xlvds.Iref_pd - 2 uA, mirrored 1:15 to the pre-driver's 30 uA"),
     ("vbias", NC),
     ("analog_bus[0]", "xpll.IREF - 2 uA charge-pump reference"),
     ("analog_bus[1]", "xlvds.Vref - 1.25 V common-mode reference")]
    # DIV_RATIO is unsigned Q7.3, so bit 3 is the ones digit and bits 2..0 the eighths
    + [("dig_in[%d]" % (b + 7), "xpll.DIV_RATIO[%d] - weight %s" % (b, w))
       for b, w in ((9, "64"), (8, "32"), (7, "16"), (6, "8"), (5, "4"),
                    (4, "2"), (3, "1"), (2, "1/2"), (1, "1/4"), (0, "1/8"))]
    + [("dig_in[%d]" % b, NC) for b in range(23, 18, -1)]
    + [("dig_out[%d]" % b, NC) for b in range(12)]
    + [("analog_bus[%d]" % b, NC) for b in (2, 3)])

# The port name that ipin.sym draws is 0.33 high and grows left from x = -18.75;
# the widest one, analog_bus[0], measures 121 units, so it reaches x = -140.
# Anchoring the pinout at -180 leaves 40 units of air between the two columns.
PINOUT_X = -180


def pin_label(net, y):
    """one right-aligned pinout line, vertically centred on the pin at y"""
    dest = PIN_USE[net]
    # rot 0 flip 1 makes xschem right-align the string on the anchor and grow it
    # leftwards, the way ipin.sym places its own @lab, so the column stays flush
    # against the pin row however long a line gets
    joiner = "  " if dest.startswith(NC) else "  ->  "
    return "T {%s%s%s} %d %d 0 1 0.25 0.25 {}" % (net, joiner, dest, PINOUT_X, y - 8)

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
    "mos": {"D": (20, 30), "G": (-20, 0), "S": (20, -30), "B": (20, 0)},
}

CELLS = [
    # reference from the dedicated pad; the PLL clock from a dig_in bit until the
    # PLL is placed; the rest of the control from dig_in bits, which the
    # housekeeping SPI routes individually to a pin, a constant or the sequencer.
    ("xpat", "lvds_pattern.sym", "lvds_pattern", 900, -500, {
        "ref_clk": "analog_pin[0]", "pll_clk": "dig_in[4]", "clk_src": "dig_in[0]",
        "en": "dig_in[1]", "reset": "dig_in[2]", "mode": "dig_in[3]",
        "D_p": "core_p", "D_n": "core_n", "VDD": "vdd_1v2", "VSS": "vss_1v2"}, ""),
    # bias straight off the harness, output pair onto two dedicated pads
    ("xlvds", "lvds_tx.sym", "lvds_tx", 1700, -500, {
        "D_p": "core_p", "D_n": "core_n", "Iref_pd": "ibias[0]",
        "Iref_drv": "ibias[1]", "Vref": "analog_bus[1]", "Va": "vdd_3v3",
        "Out_p": "analog_pin[2]", "Out_n": "analog_pin[3]", "Vss": "vss_3v3"}, ""),
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
  analog_pin[1]  pll_out   the PLL's TEST_CLK, brought off chip
  analog_pin[2]  d_p       LVDS out +
  analog_pin[3]  d_n       LVDS out -

All four are sg13cmos5l_IOPadAnalog in config.txt, so each pad is one core
signal carrying the pad name.  A different pad type changes that: an InOut
pad becomes five core signals (_in, _out, _ena, _one, _zero).

Not connected: dig_out[11:0], analog_bus[3:0], vssio, clk - the reference
arrives on its own dedicated pad instead of the shared clock pin - and enable.
The harness already masks dig_in to zero for an unselected project
(proj_dig_in = {24{select & dig_ena}} & dig_in in user_project_control.v), so
dig_in[1] alone stops the pattern clock.  Note this drops the one case the
gate used to cover: select and dig_ena high with enable low leaves dig_in[1]
live, and the block then runs with the project enable deasserted.} 300 -1820 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit individually to a
pin, a constant or the sequencer, so a configuration bit costs a register
write and no pin.  Unselected holds every dig_in at zero, and all-zero
leaves the clock stopped and the output pair static - a legal idle.

  dig_in[0]     clk_src    0 = ref_clk, 1 = pll_clk
  dig_in[1]     en         gates the pattern clock
  dig_in[2]     reset      active high, seeds the PRBS
  dig_in[3]     mode       0 = clock passthrough, 1 = PRBS-7
  dig_in[4]     unused     carried the provisional pll_clk before the PLL was placed
  dig_in[5]     PLL ENABLE
  dig_in[6]     PLL RESET_N, active low
  dig_in[16:7]  PLL DIV_RATIO[9:0], unsigned Q7.3
  dig_in[18:17] PLL TEST_DIV[1:0]
  dig_in[23:19] unused

The Q7.3 ratio costs 10 bits where the earlier split DIV_INT + DIV_FRAC cost
23, so the PLL and the LVDS controls together now fit in 18 of the 24 bits
and DIV_FRAC no longer has to be tied off.} 300 -1400 0 0 0.4 0.4 {}
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
        if net in PIN_USE:
            out.append(pin_label(net, y))
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


def graph(box, nodes, colors, ymin, ymax, tmin, tmax, divy=5, unlocked=False):
    """one waveform panel; box is (x1, y1, x2, y2) in schematic coordinates

    xschem locks every graph on a sheet to one shared x axis unless the graph
    carries the `unlocked` flag - the "Unlock. X axis" checkbox in its property
    dialog.  Locked panels showing different time windows fight each other:
    scrolling any one of them drags the rest onto its window.
    """
    x1, y1, x2, y2 = box
    return ("B 2 %d %d %d %d {flags=graph%s\n"
            "y1=%g\ny2=%g\nypos1=0\nypos2=2\ndivy=%d\nsubdivy=1\nunity=1\n"
            "x1=%g\nx2=%g\ndivx=5\nsubdivx=1\n"
            "xlabmag=1.0\nylabmag=1.0\nlegendmag=1.0\n"
            'node="%s"\ncolor="%s"\n'
            "dataset=-1\nunitx=1\nlogx=0\nlogy=0\nautoload=0\nhilight_wave=-1}"
            % (x1, y1, x2, y2, ",unlocked" if unlocked else "",
               ymin, ymax, divy, tmin, tmax,
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
    "analog_bus[1]": ("v", "1.2", "LVDS common-mode reference, 1.2 V (the IDAC grid has no 1.25 V)"),
    "ibias[0]": ("i", "-2u", "pre-driver reference, 2 uA"),
    "ibias[1]": ("i", "-2u", "driver reference, 2 uA"),
    "analog_pin[0]": ("v", "PULSE(0 1.2 0 50p 50p 0.9n 2n)", "ref_clk, 500 MHz"),
    "dig_in[0]": ("v", "0", "clk_src = 0, take ref_clk"),
    "dig_in[1]": ("v", "PWL(0 0 3n 0 3.1n 1.2)", "en, low until 3 ns"),
    "dig_in[2]": ("v", "PWL(0 1.2 2n 1.2 2.1n 0)", "reset, high until 2 ns"),
    "dig_in[3]": ("v", "1.2", "mode = 1, PRBS-7 throughout"),
}
TB_LVDS_GROUND = ("vss_3v3", "vss_1v2", "vssio")
TB_LVDS_PADS = ("analog_pin[2]", "analog_pin[3]")     # the differential pair

TB_LVDS_CONTROL = r'''
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
* gear2 collapses the timestep to 6e-24 s at 414 ns on vvdd_1v2#branch
* once the PLL's XSPICE bridges are in the netlist, and the run stops
* there whatever tstop says.  trap gets through the full span.
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
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
* print on a transient vector dumps every timepoint - measure instead
meas tran i_3v3 AVG i(Vvdd_3v3) from=150n to=595n
meas tran i_1v2 AVG i(Vvdd_1v2) from=150n to=595n
print i_3v3 i_1v2

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


# ---------------------------------------------------------------- layout zones
# Every bench in this file is drawn in the same bands, left to right in signal
# order, and nothing is placed outside its own band, so two zones cannot end up
# on top of each other however many pins or sources a bench has:
#
#   DOC    the title and the ngspice control block
#   STIM   the sources, one framed group per purpose
#   DUT    the block under test, one labelled stub per pin
#   LOAD   the two pads, their ammeters and the 49.9 + 49.9 termination
#   VIEW   the launchers and the waveform panels
#
# Every pin stub is the same length, so the net labels line up on one x per
# side.  The symbol has a 20 unit pin pitch and a net label is taller than
# that, so neighbouring labels do touch; widening the symbol pin pitch is the
# only way around it and that would rewrite the top cell.
DOC_X = -3600
DOC_TITLE_Y = -2400
DOC_CODE_Y = -1650

STIM_X = -2000
STIM_TEXT_X = STIM_X + 80
STIM_TOP = -1700
STIM_PITCH = 200
STIM_GROUP_GAP = 200
STIM_FRAME_L = STIM_X - 260
STIM_FRAME_R = STIM_X + 660

STUB = 60                 # every pin stub is this long

PAD_X = (1000, 1120)      # the two pad escapes, at different x so they cannot cross
RAIL_Y = (-560, 460)      # the upper pad leaves upwards, the lower one downwards
TERM_X = 1560

VIEW_X = 2050
VIEW_W = 1800
VIEW_TOP = -2150


def title_block(x, y, text, scale=0.45):
    return "T {%s} %d %d 0 0 %g %g {}" % (text, x, y, scale, scale)


def code_block(x, y, control):
    return '''C {devices/code_shown.sym} %d %d 0 0 {name=NGSPICE
only_toplevel=true
value="%s"}''' % (x, y, control)


def view_panels(specs, tb):
    """three stacked waveform panels with the launchers above them

    Panels that share a time window stay locked to each other, so scrolling one
    scrolls its partners and the traces stay comparable.  A panel on a window of
    its own is unlocked, so the overview keeps showing the whole run however far
    the detail panels are scrolled.
    """
    windows = [(t0, t1) for _, _, _, _, t0, t1 in specs]
    keep = max(set(windows), key=windows.count) if windows else None
    out = launchers(VIEW_X, VIEW_TOP, tb)
    y = VIEW_TOP + 200
    for nodes, colors, ymin, ymax, t0, t1 in specs:
        out.append(graph((VIEW_X, y, VIEW_X + VIEW_W, y + 400),
                         nodes, colors, ymin, ymax, t0, t1,
                         unlocked=(t0, t1) != keep))
        y += 500
    return out


def stim_groups(groups, drive):
    """the source column, one framed and captioned group at a time"""
    out, y = [], STIM_TOP
    for caption, names in groups:
        top = y - 120
        for name in names:
            kind, val, why = drive[name]
            tag = name.replace("[", "_").replace("]", "")
            out.append("N %d %d %d %d {lab=%s}"
                       % (STIM_X, y - 60, STIM_X, y - 30, name))
            out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                       "{name=ls_%s sig_type=std_logic lab=%s}"
                       % (STIM_X, y - 60, tag, name))
            out.append('C {devices/vsource.sym} %d %d 0 0 {name=V%s value="%s"}'
                       % (STIM_X, y, tag, val) if kind == "v" else
                       "C {isource.sym} %d %d 0 0 {name=I%s value=%s}"
                       % (STIM_X, y, tag, val))
            out.append("N %d %d %d %d {lab=GND}"
                       % (STIM_X, y + 30, STIM_X, y + 60))
            out.append("C {devices/gnd.sym} %d %d 0 0 {name=lg_%s lab=GND}"
                       % (STIM_X, y + 60, tag))
            out.append("T {%s} %d %d 0 0 0.3 0.3 {}" % (why, STIM_TEXT_X, y - 5))
            y += STIM_PITCH
        bottom = y - STIM_PITCH + 120
        for a, b, c, d in ((STIM_FRAME_L, top, STIM_FRAME_R, top),
                           (STIM_FRAME_R, top, STIM_FRAME_R, bottom),
                           (STIM_FRAME_L, bottom, STIM_FRAME_R, bottom),
                           (STIM_FRAME_L, top, STIM_FRAME_L, bottom)):
            out.append("L 3 %d %d %d %d {}" % (a, b, c, d))
        out.append("T {%s} %d %d 0 0 0.4 0.4 {}" % (caption, STIM_FRAME_L, top - 55))
        y = bottom + STIM_GROUP_GAP
    return out


def dut_stubs(pins, ground, skip=()):
    """one labelled stub per pin, every stub on the same x per side"""
    out = []
    for name, d, cx, cy in pins:
        if name in skip:
            continue
        s = -1 if cx < 0 else 1
        px, py = int(cx), int(cy)
        # the stub has to start on the pin itself; offsetting it here leaves
        # every port on an unconnected auto-net and the netlist still looks fine
        ex = px + s * STUB
        tag = name.replace("[", "_").replace("]", "")
        out.append("N %d %d %d %d {lab=%s}"
                   % (min(px, ex), py, max(px, ex), py,
                      "GND" if name in ground else name))
        if name in ground:
            out.append("C {devices/gnd.sym} %d %d %d 0 {name=lgg_%s lab=GND}"
                       % (ex, py, 1 if s < 0 else 3, tag))
        else:
            out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                       "{name=lx_%s sig_type=std_logic lab=%s}"
                       % (ex, py, tag, name))
    return out


def pad_network(pins, pads):
    """the differential pads, each through its own ammeter, into 49.9 + 49.9

    The pad that sits higher on the symbol leaves upwards and the other one
    downwards, and the two escapes use different x, so the two nets reach the
    termination without a single crossing.  The ammeters are real 0 V sources:
    they give the pad currents, and they put a plain d_p / d_n name on the part
    of the net the measurements refer to.
    """
    pos = dict((n, (int(cx), int(cy))) for n, d, cx, cy in pins)
    legs = [(pads[0], "d_p"), (pads[1], "d_n")]
    legs.sort(key=lambda leg: pos[leg[0]][1])          # topmost pad first
    out = []
    for (pad, sig), esc_x, rail_y in zip(legs, PAD_X, RAIL_Y):
        px, py = pos[pad]
        mid = (py + rail_y) // 2
        near, far = (mid - 30, mid + 30) if rail_y > py else (mid + 30, mid - 30)
        out.append("N %d %d %d %d {lab=%s}" % (px, py, esc_x, py, pad))
        out.append("N %d %d %d %d {lab=%s}"
                   % (esc_x, min(py, near), esc_x, max(py, near), pad))
        out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                   "{name=lpad_%s sig_type=std_logic lab=%s}"
                   % (esc_x, (py + near) // 2, sig, pad))
        out.append('C {devices/vsource.sym} %d %d 0 0 {name=V%s value=0}'
                   % (esc_x, mid, sig))
        out.append("N %d %d %d %d {lab=%s}"
                   % (esc_x, min(far, rail_y), esc_x, max(far, rail_y), sig))
        out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                   "{name=lmeas_%s sig_type=std_logic lab=%s}"
                   % (esc_x, (far + rail_y) // 2, sig, sig))
        out.append("N %d %d %d %d {lab=%s}" % (esc_x, rail_y, TERM_X, rail_y, sig))

    top_sig, bot_sig = legs[0][1], legs[1][1]
    vos_y = (RAIL_Y[0] + RAIL_Y[1]) // 2
    r_top = (RAIL_Y[0] + vos_y) // 2
    r_bot = (vos_y + RAIL_Y[1]) // 2
    out += ["N %d %d %d %d {lab=%s}" % (TERM_X, RAIL_Y[0], TERM_X, r_top - 30, top_sig),
            "C {res.sym} %d %d 0 0 {name=Rt%s value=49.9}" % (TERM_X, r_top, top_sig),
            "N %d %d %d %d {lab=vos}" % (TERM_X, r_top + 30, TERM_X, vos_y),
            "N %d %d %d %d {lab=vos}" % (TERM_X, vos_y, TERM_X, r_bot - 30),
            "C {res.sym} %d %d 0 0 {name=Rt%s value=49.9}" % (TERM_X, r_bot, bot_sig),
            "N %d %d %d %d {lab=%s}" % (TERM_X, r_bot + 30, TERM_X, RAIL_Y[1], bot_sig),
            "N %d %d %d %d {lab=vos}" % (TERM_X, vos_y, TERM_X + 140, vos_y),
            "C {devices/lab_wire.sym} %d %d 0 0 "
            "{name=lvos sig_type=std_logic lab=vos}" % (TERM_X + 140, vos_y)]
    return out


# the sources, split by what they are actually for
TB_LVDS_GROUPS = [
    ("supplies", ["vdd_3v3", "vdd_1v2"]),
    ("bias", ["analog_bus[1]", "ibias[0]", "ibias[1]"]),
    ("pattern control", ["dig_in[0]", "dig_in[1]",
                         "dig_in[2]", "dig_in[3]"]),
    ("clocks", ["analog_pin[0]"]),
]

LVDS_TITLE = """LVDS bench for the top cell.

Reset, then clock passthrough of the 500 MHz reference on the dedicated
pad, then PRBS-7 from 10 ns, through the pre-driver and the driver into
49.9 + 49.9 ohm across the two output pads with the Vos tap.

clk_src is 0 here on purpose: this bench characterises the transmitter,
so the bit clock comes straight off analog_pin[0] and the PLL is left
out of the measurement.  tb_pll is the one that runs through the loop.

The port list is read out of the symbol when this bench is generated,
so it survives rewiring of the top cell.  Any harness pin without a
source in the stimulus column is left open on purpose.

clk_pp and core_pp are checked first: if the gated clock inside the
pattern generator is not moving, the control path is broken and the
LVDS numbers below it mean nothing.

No pad or ESD model - the driver was characterised with one, so the
Vos figure here is not the compliance number."""


def gen_tb_lvds(path, symbol):
    pins = sym_pins(symbol)
    covered = [n for _, names in TB_LVDS_GROUPS for n in names]
    assert sorted(covered) == sorted(TB_LVDS_DRIVE), "groups and drive disagree"
    out = [HEADER, title_block(DOC_X, DOC_TITLE_Y, LVDS_TITLE)]
    out += stim_groups(TB_LVDS_GROUPS, TB_LVDS_DRIVE)
    out += dut_stubs(pins, TB_LVDS_GROUND, skip=TB_LVDS_PADS)
    out.append("C {%s.sym} 0 0 0 0 {name=x1}" % TOP)
    out += pad_network(pins, TB_LVDS_PADS)
    # the top panel spans the whole run so the cold start stays visible, the two
    # below it are zoomed onto a few settled bits
    out += view_panels(
        [(["d_p", "d_n", "vos"], [4, 5, 8], 0.9, 1.6, 0.0, 6.0e-7),
         (["x1.xpat.gclk_b", "x1.core_p", "x1.core_n"], [4, 7, 5],
          -0.2, 1.4, 3.00e-7, 3.10e-7),
         (["d_p", "d_n", "vod"], [4, 5, 7], -0.5, 1.6, 3.00e-7, 3.10e-7)],
        TOP + "_tb_lvds")
    out.append(code_block(DOC_X, DOC_CODE_Y, TB_LVDS_CONTROL))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ------------------------------------------------------------------ testbench
TB_SOURCES = [
    ("vdd_3v3", "v", "3.3", "gated 3.3 V"),
    ("vdd_1v2", "v", "1.2", "gated 1.2 V"),
    ("analog_bus[1]", "v", "1.2", "LVDS common-mode reference, 1.2 V"),
    ("analog_pin[0]", "v", "PULSE(0 1.2 0 50p 50p 1.9n 4n)", "ref_clk, 250 MHz"),
    ("dig_in[0]", "v", "0", "clk_src = 0, take ref_clk"),
    ("dig_in[1]", "v", "PWL(0 0 3n 0 3.1n 1.2)", "en, low until 3 ns"),
    ("dig_in[2]", "v", "PWL(0 1.2 2n 1.2 2.1n 0)", "reset, high until 2 ns"),
    ("dig_in[3]", "v", "PWL(0 0 10n 0 10.1n 1.2)", "mode -> PRBS-7 at 10 ns"),
    ("ibias[0]", "i", "-2u", "pre-driver reference, 2 uA"),
    ("ibias[1]", "i", "-2u", "driver reference, 2 uA"),
]

TB_CONTROL = r'''
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
* gear2 collapses the timestep to 6e-24 s at 414 ns on vvdd_1v2#branch
* once the PLL's XSPICE bridges are in the netlist, and the run stops
* there whatever tstop says.  trap gets through the full span.
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
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
               "  dig_in[0]      clk_src = 0, the bit clock is the reference\n"
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


# ---------------------------------------------------- the PLL bench family
# VCO = REF * DIV_RATIO and pll_clk = VCO / 2 (clock_output_divider.v always
# halves), so the line rate is REF * DIV_RATIO / 2.  DIV_RATIO is an unsigned
# Q7.3 word: div_ratio[9:3] is the integer part, div_ratio[2:0] the eighths
# (pll_digital.v), and fractional_divider.v requires the integer part >= 4.
#
# The ring oscillator runs from 322 MHz (vctrl 0.50) to 4.05 GHz (vctrl 0.95)
# at tt/1.2 V/27 C and does not start below 0.50 V, per
# info/ring_oscillator_buffered_pvt.csv, so every combination below lands
# between 0.7 and 2.1 GHz - clear of both ends of the tuning curve.
#
# info/pll_integer_characterization.csv measures lock at 2.75 us typical,
# 2.25 us fast and 4.50 us slow.  A bench therefore has to run well past 1 us
# before it asks what the output frequency is.
# CAVEAT, measured 2026-09-01: the transistor-level PLL ignores DIV_RATIO.
# In macros/pll_analog/schematic/xschem/pll.sch the DIV_RATIO[9:0] and
# TEST_DIV[1:0] pins are ipin declarations that connect to nothing;
# feedback_divider.sym carries only VCO_IN and FB_OUT and the divide comes from
# a model card, .model pll_feedback_div d_fdiv(div_factor=20 ...).  The table
# below therefore describes what each bench asks for, not what the schematic
# does: only ref100_r20 matches the hard-wired 20 and can lock, and the rest
# drive VCTRL to a rail.  DIV_RATIO is decoded only by the RTL in
# macros/pll_digital, through scripts/pll/run_pll_cosim.sh.
PLL_TSTOP = 6.0e-6
PLL_VCO_MIN, PLL_VCO_MAX = 0.7e9, 2.1e9

PLL_COMBOS = [
    # name, ref_hz, ratio, test_div, why this combination is in the set
    ("ref250_r4", 250e6, 4.0, 0,
     "baseline - the operating point the rest of the project assumes"),
    ("ref125_r8", 125e6, 8.0, 1,
     "same 1 GHz VCO as the baseline at half the compare frequency"),
    ("ref25_r40", 25e6, 40.0, 3,
     "same 1 GHz VCO again at a tenth of the compare frequency - a row of "
     "pll_integer_characterization.csv"),
    ("ref100_r20", 100e6, 20.0, 2,
     "2 GHz VCO, the fast end - the other characterised row"),
    ("ref250_r4p5", 250e6, 4.5, 0,
     "fractional-N, code 36: one eighth bit, N/N+1 alternates every other cycle"),
    ("ref200_r4p375", 200e6, 4.375, 1,
     "fractional-N, code 35: three eighth bits, and the slow end at 875 MHz"),
]


def pll_combo(name, ref_hz, ratio, test_div, why):
    """everything a bench needs, derived once so deck and prose cannot disagree"""
    code = int(round(ratio * 8))
    assert abs(code / 8.0 - ratio) < 1e-9, "%s: ratio is not a whole eighth" % name
    assert code >> 3 >= 4, "%s: fractional_divider.v wants integer_div >= 4" % name
    assert code < 1024, "%s: DIV_RATIO is 10 bits" % name
    vco = ref_hz * ratio
    assert PLL_VCO_MIN <= vco <= PLL_VCO_MAX, \
        "%s: %.3f GHz is outside the characterised VCO band" % (name, vco / 1e9)
    return dict(
        name=name, ref=ref_hz, ratio=ratio, code=code, why=why,
        integer=code >> 3, frac=code & 7,
        vco=vco, pll_clk=vco / 2.0, test_div=test_div,
        test_clk=vco / 2.0 ** (1 + test_div),
        # 40 points per VCO period is plenty for an edge-triggered loop, and it
        # keeps a 6 us run near the point count of the old 1 us / 5 ps deck
        maxstep=1.0 / (40.0 * vco),
        # the pattern generator stays off until the loop has locked
        pattern_on=0.75 * PLL_TSTOP)


def eng(x, unit=""):
    for scale, suffix in ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1.0, "")):
        if abs(x) >= scale:
            return ("%.6g %s%s" % (x / scale, suffix, unit)).strip()
    return ("%.6g %s" % (x, unit)).strip()


def pll_drive(c):
    """every source, with all ten DIV_RATIO bits driven to a real level"""
    ref_ns = 1e9 / c["ref"]
    on = c["pattern_on"] * 1e6
    d = {
        "vdd_3v3": ("v", "3.3", "gated 3.3 V"),
        "vdd_1v2": ("v", "1.2", "gated 1.2 V"),
        "analog_bus[1]": ("v", "1.2", "LVDS common-mode reference, 1.2 V"),
        "ibias[0]": ("i", "-2u", "pre-driver reference, 2 uA"),
        "ibias[1]": ("i", "-2u", "driver reference, 2 uA"),
        "analog_bus[0]": ("i", "-2u",
                          "PLL charge-pump reference - 2 uA, not the "
                          "transmitter's 30 uA"),
        "analog_pin[0]": ("v", "PULSE(0 1.2 0 50p 50p %.4fn %.4fn)"
                          % (ref_ns / 2 - 0.05, ref_ns),
                          "REF_CLK, %s" % eng(c["ref"], "Hz")),
        "dig_in[0]": ("v", "1.2", "clk_src = 1, pattern generator off the PLL"),
        "dig_in[1]": ("v", "PWL(0 0 %.3fu 0 %.3fu 1.2)" % (on, on + 0.001),
                      "pattern en, held off until the loop has locked"),
        "dig_in[2]": ("v", "PWL(0 1.2 %.3fu 1.2 %.3fu 0)" % (on - 0.01, on - 0.009),
                      "PRBS reset, released just before en"),
        "dig_in[3]": ("v", "1.2", "mode = 1, PRBS-7"),
        "dig_in[5]": ("v", "PWL(0 0 2n 0 2.1n 1.2)", "PLL ENABLE"),
        "dig_in[6]": ("v", "PWL(0 0 1n 0 1.1n 1.2)", "PLL RESET_N, active low"),
    }
    # DIV_RATIO[9:0] on dig_in[16:7].  Every bit gets a source: an undriven bit
    # floats into the XSPICE adc_bridge and the divide ratio becomes a guess.
    for b in range(10):
        weight = "integer %d" % (2 ** (b - 3)) if b >= 3 else "1/%d" % (2 ** (3 - b))
        d["dig_in[%d]" % (b + 7)] = (
            "v", "1.2" if c["code"] >> b & 1 else "0",
            "DIV_RATIO[%d] = %d   weight %s" % (b, c["code"] >> b & 1, weight))
    # TEST_DIV[1:0] on dig_in[18:17]
    for b in range(2):
        d["dig_in[%d]" % (b + 17)] = (
            "v", "1.2" if c["test_div"] >> b & 1 else "0",
            "TEST_DIV[%d] = %d" % (b, c["test_div"] >> b & 1))
    return d


def pll_groups(c):
    return [
        ("supplies", ["vdd_3v3", "vdd_1v2"]),
        ("bias", ["analog_bus[1]", "ibias[0]", "ibias[1]", "analog_bus[0]"]),
        ("PLL control", ["dig_in[6]", "dig_in[5]"]),
        ("DIV_RATIO = %g   code %d = %s"
         % (c["ratio"], c["code"], format(c["code"], "010b")),
         ["dig_in[%d]" % (b + 7) for b in range(9, -1, -1)]),
        ("TEST_DIV = %d   TEST_CLK = VCO/%d"
         % (c["test_div"], 2 ** (1 + c["test_div"])),
         ["dig_in[18]", "dig_in[17]"]),
        ("pattern control", ["dig_in[0]", "dig_in[1]", "dig_in[2]", "dig_in[3]"]),
        ("reference clock", ["analog_pin[0]"]),
    ]


PLL_TITLE_FMT = """PLL bench %(name)s: %(ref)s reference in, PRBS-7 at %(rate)s out.

  %(why)s

  VCO      = REF * DIV_RATIO   = %(vco)s
  pll_clk  = VCO / 2           = %(fpll)s   <- the line rate
  test_clk = VCO / %(td)-2d          = %(ftest)s   <- on analog_pin[1]

  DIV_RATIO = %(ratio)g, code %(code)d = %(bits)s
              integer part %(int)d in div_ratio[9:3], %(frac)d/8 in div_ratio[2:0]

  1 ns       PLL RESET_N released
  2 ns       PLL ENABLE
  %(on).2f us    PRBS reset released, then the pattern generator enabled

The run is %(tstop).0f us because the loop needs it: pll_integer_characterization.csv
measures lock at 2.75 us typical and 4.50 us slow, so the earlier 1 us bench was
reading a frequency the loop had not settled to yet.

f_pll is averaged over ~%(ncyc)d cycles late in the run rather than across two
adjacent edges.  fractional_divider.v is a plain N/N+1 accumulator with no
delta-sigma, so at a fractional ratio the instantaneous period alternates and
only the average over a whole accumulator cycle is the number worth reading.

Every DIV_RATIO and TEST_DIV bit carries its own source, including the zeros.

No pad or ESD model, so the Vos figure here is not the compliance number."""


def pll_title(c):
    return PLL_TITLE_FMT % dict(
        name=c["name"], ref=eng(c["ref"], "Hz"), rate=eng(c["pll_clk"], "b/s"),
        why=c["why"], vco=eng(c["vco"], "Hz"), fpll=eng(c["pll_clk"], "Hz"),
        td=2 ** (1 + c["test_div"]), ftest=eng(c["test_clk"], "Hz"),
        ratio=c["ratio"], code=c["code"], bits=format(c["code"], "010b"),
        int=c["integer"], frac=c["frac"],
        on=c["pattern_on"] * 1e6, tstop=PLL_TSTOP * 1e6,
        ncyc=int(0.20 * PLL_TSTOP * c["pll_clk"]))


PLL_CONTROL_FMT = r'''
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
.ic v(x1.xlvds.xdrv.cmfb)=1.54
* gear2 collapses the timestep once the PLL XSPICE bridges are in the netlist,
* and the run then stops early whatever tstop says.  trap gets through.
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
.control
save d_p d_n vos x1.core_p x1.core_n x1.pll_clk
+ x1.xpll.VCTRL x1.xpll.VCO_CLK x1.xpll.FB_CLK x1.xpll.UP x1.xpll.DOWN
tran %(step).4g %(tstop).4g 0 %(step).4g
write @schname\\\\.raw

* First: does the loop do anything at all?  VCTRL has to move and the VCO has
* to oscillate before any number below means anything.
meas tran vctrl_min MIN v(x1.xpll.VCTRL) from=50n to=%(tend).4g
meas tran vctrl_max MAX v(x1.xpll.VCTRL) from=50n to=%(tend).4g
meas tran vctrl_end AVG v(x1.xpll.VCTRL) from=%(tsettle).4g to=%(tend).4g
meas tran vco_pp PP v(x1.xpll.VCO_CLK) from=%(tsettle).4g to=%(tend).4g
meas tran fb_pp PP v(x1.xpll.FB_CLK) from=%(tsettle).4g to=%(tend).4g
print vctrl_min vctrl_max vctrl_end vco_pp fb_pp

* Second: is pll_clk on target?  Averaged over %(ncyc)d cycles, because the
* N/N+1 divider makes any single period the wrong thing to measure.
meas tran t1 WHEN v(x1.pll_clk)=0.6 RISE=%(k1)d
meas tran t2 WHEN v(x1.pll_clk)=0.6 RISE=%(k2)d
let f_pll = %(ncyc)d/(t2-t1)
let f_pll_target = %(fpll).8g
let f_pll_err_ppm = 1e6*(f_pll-f_pll_target)/f_pll_target
print f_pll f_pll_target f_pll_err_ppm

* Third: what leaves the transmitter once the pattern generator runs
let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=%(tpat).4g to=%(tend).4g
meas tran vod_min MIN vod from=%(tpat).4g to=%(tend).4g
meas tran vos_avg AVG v(vos) from=%(tpat).4g to=%(tend).4g
meas tran vos_max MAX v(vos) from=%(tpat).4g to=%(tend).4g
meas tran vos_min MIN v(vos) from=%(tpat).4g to=%(tend).4g
let vos_pp = vos_max - vos_min
meas tran core_pp PP v(x1.core_p) from=%(tpat).4g to=%(tend).4g
print vod_max vod_min vos_avg vos_pp core_pp

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.pll_clk) v(x1.xpll.VCTRL)
.endc
'''


def pll_control(c):
    t = PLL_TSTOP
    k1, k2 = int(0.75 * t * c["pll_clk"]), int(0.95 * t * c["pll_clk"])
    return PLL_CONTROL_FMT % dict(
        step=c["maxstep"], tstop=t, tend=t - 50e-9, tsettle=t - 550e-9,
        tpat=c["pattern_on"] + 100e-9, k1=k1, k2=k2, ncyc=k2 - k1,
        fpll=c["pll_clk"])


def gen_tb_pll(path, symbol, c):
    pins = sym_pins(symbol)
    drive, groups = pll_drive(c), pll_groups(c)
    covered = [n for _, names in groups for n in names]
    assert sorted(covered) == sorted(drive), "groups and drive disagree"
    out = [HEADER, title_block(DOC_X, DOC_TITLE_Y, pll_title(c))]
    out += stim_groups(groups, drive)
    out += dut_stubs(pins, TB_LVDS_GROUND, skip=TB_LVDS_PADS)
    out.append("C {%s.sym} 0 0 0 0 {name=x1}" % TOP)
    out += pad_network(pins, TB_LVDS_PADS)
    # the loop first, the bit clock second, the transmitter last - reading the
    # panels top to bottom is reading the signal path
    zoom = c["pattern_on"] + 300e-9
    out += view_panels(
        [(["x1.xpll.VCTRL"], [8], 0.0, 1.3, 0.0, PLL_TSTOP),
         (["x1.pll_clk", "x1.core_p"], [4, 7], -0.2, 1.4, zoom, zoom + 10e-9),
         (["d_p", "d_n", "vos"], [4, 5, 8], 0.9, 1.6, zoom, zoom + 10e-9)],
        os.path.basename(path)[:-4])
    out.append(code_block(DOC_X, DOC_CODE_Y, pll_control(c)))
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
    # The first combination keeps the historical name so make sim-xschem
    # TB=<top>_tb_pll and everything that cites it still resolve; the rest of
    # the family is <top>_tb_pll_<name>.sch.
    for i, spec in enumerate(PLL_COMBOS):
        c = pll_combo(*spec)
        leaf = TOP + "_tb_pll.sch" if i == 0 else TOP + "_tb_pll_%s.sch" % c["name"]
        gen_tb_pll(os.path.join(tb, leaf), sym, c)
        print("  %-34s REF %-9s ratio %-7g VCO %-9s line %s"
              % (leaf, eng(c["ref"], "Hz"), c["ratio"],
                 eng(c["vco"], "Hz"), eng(c["pll_clk"], "b/s")))
    print("wrote %s_tb_lvds.sch and %d PLL benches from the %d pins of %s.sym"
          % (TOP, len(PLL_COMBOS), len(sym_pins(sym)), TOP))
