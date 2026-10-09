#!/usr/bin/env python3
"""Generate the top cell, its symbol and its benches.

The port list is the Chipalooza slot-14 frame (slot14_wrapper in
RTimothyEdwards/sg13cmos5l_ocd_chipalooza), pin for pin, so this cell and
layout/slot_14.gds compare by name in LVS.  Slot 14 has three dedicated analog
pads, each an sg13cmos5l_IOPadAnalog with two core terminals: s14_an[i] is its
`pad`, straight onto the pad, and s14_an_i_esd its `padres`, through the
secondary protection (series resistor and diodes) - the one for gate inputs.

Nets are joined by label rather than by drawn wire: every pin gets a stub and a
lab_pin carrying the net name. That is what keeps a fifty-port frame generatable.
"""
import io
import os
import re

TOP = "slot_14"
HERE = os.path.dirname(os.path.abspath(__file__))


def bus(name, hi, lo=0):
    """MSB first, the way the Verilog declaration reads"""
    return ["%s[%d]" % (name, i) for i in range(hi, lo - 1, -1)]


# (net, xschem pin symbol, side).  The names are the frame's pin labels.
PORTS = (
    [(n, "iopin", "L") for n in ("vdd_3v3", "vdd_1v2", "vss_3v3", "vss_1v2")]
    + [("enable", "ipin", "L"), ("clk", "ipin", "L"), ("reset", "ipin", "L")]
    + [(n, "ipin", "L") for n in bus("dig_in", 23)]
    + [(n, "ipin", "L") for n in ("ibias0", "ibias1", "vbias")]
    + [(n, "opin", "R") for n in bus("dig_out", 11)]
    + [(n, "iopin", "R") for n in bus("s14_an", 2)]
    + [(n, "iopin", "R") for n in ("s14_an_2_esd", "s14_an_1_esd", "s14_an_0_esd")]
    + [(n, "iopin", "R") for n in ("analog_bus0", "analog_bus1", "analog_bus2", "analog_bus3")]
)

# what the three dedicated pads carry
PAD_USE = [("s14_an[0]", "LVDS out -, pad 0 direct"),
           ("s14_an[1]", "LVDS out +, pad 1 direct"),
           ("s14_an_2_esd", "ref_clk in - pad 2 through its secondary protection"),
           ("s14_an[2]", "ref_clk termination - pad 2 direct")]

# Where every port actually goes, so the sheet answers "what is this pin wired
# to" without tracing a label across the drawing.  Read off the netlist of the
# top cell; keep it in step when the wiring changes.
NC = "not connected"
PIN_USE = dict(
    [("vdd_3v3", "xlvds.Va, xiref_pd.Va, xiref_drv.Va, xdc33 decap row"),
     ("vdd_1v2", "xpat.VDD, xdc12 decap row"),
     ("vss_3v3", "xlvds.Vss, xiref_pd.Vss, xiref_drv.Vss, xdc33 decap row"),
     ("vss_1v2", "xpat.VSS, xdc12 decap row"),
     ("enable", NC),
     ("clk", NC + " - the reference comes in on s14_an_2_esd"),
     ("reset", NC + " - the PRBS reset is dig_in[2]"),
     ("dig_in[3]", "xpat.mode - 0 = clock passthrough, 1 = PRBS-7"),
     ("dig_in[2]", "xpat.reset - active high, seeds the PRBS shift register; DRST antenna diode"),
     ("dig_in[1]", "xpat.en - gates the pattern clock, not the output pair"),
     ("dig_in[0]", "xodt.EN - 1 = 50 ohm termination of ref_clk on"),
     ("dig_in[4]", "xbt.EN - 1 = ~200 ohm back-termination of the LVDS pair on (with ibias1 3 uA)"),
     ("ibias0", "xiref_pd (1:15) -> xlvds.Iref_pd - IDAC code 6 (1.94 uA in, 29 uA out)"),
     ("ibias1", "xiref_drv (1:15) -> xlvds.Iref_drv - code 6; code 9 (2.90 uA) with dig_in[4]"),
     ("vbias", "xlvds.Vref - 1.2 V common-mode reference, the harness voltage reference"),
     ("analog_bus0", "tap on ibias0 through RT0 (1.1 kohm): measure it, or force it from outside"),
     ("analog_bus1", "tap on vbias = Vref through RT1 (1.1 kohm)"),
     ("analog_bus2", "tap on ibias1 through RT2 (1.1 kohm)"),
     ("s14_an_2_esd", "xpat.ref_clk"),
     ("s14_an[0]", "xlvds.Out_n, xbt.OUTN"),
     ("s14_an[1]", "xlvds.Out_p, xbt.OUTP")]
    + [("dig_in[%d]" % b, NC) for b in range(23, 4, -1)]
    + [("dig_out[%d]" % b, NC) for b in range(12)]
    + [(n, NC) for n in ("analog_bus3", "s14_an_0_esd", "s14_an_1_esd")]
    + [("s14_an[2]", "xodt.PAD - the termination, on pad 2 itself")])

# The port name that ipin.sym draws is 0.33 high and grows left from x = -18.75;
# the widest one, s14_an_0_esd, reaches about x = -140.  Anchoring the pinout
# at -180 leaves 40 units of air between the two columns.
PINOUT_X = -180


def pin_label(net, y):
    """one right-aligned pinout line, vertically centred on the pin at y"""
    dest = PIN_USE[net]
    # rot 0 flip 1 makes xschem right-align the string on the anchor and grow it
    # leftwards, the way ipin.sym places its own @lab, so the column stays flush
    # against the pin row however long a line gets
    joiner = "  " if dest.startswith(NC) else "  ->  "
    return "T {%s%s%s} %d %d 0 1 0.25 0.25 {}" % (net, joiner, dest, PINOUT_X, y - 8)


def sym_offsets(path):
    """pin name -> (x, y) of its centre, read off a symbol file"""
    s = io.open(path, encoding="utf-8").read()
    return dict((m.group(5), (int(round((float(m.group(1)) + float(m.group(3))) / 2)),
                              int(round((float(m.group(2)) + float(m.group(4))) / 2))))
                for m in re.finditer(r"^B 5 (\S+) (\S+) (\S+) (\S+) \{name=([^ }]+)", s, re.M))


# pin offsets read off each macro's own symbol, so a moved pin cannot leave a
# stub hanging in the air
PINS = dict((cell, sym_offsets(os.path.join(HERE, "..", "macros", cell, "schematic",
                                            "xschem", cell + ".sym")))
            for cell in ("lvds_pattern", "lvds_tx", "iref_x15", "ref_odt", "lvds_bt"))
PINS["mos"] = {"D": (20, 30), "G": (-20, 0), "S": (20, -30), "B": (20, 0)}
PINS["dio"] = {"d1": (0, -30), "d0": (0, 30)}          # sg13cmos5l_pr/dantenna.sym: d1 cathode, d0 anode
PINS["res"] = {"P": (0, -30), "M": (0, 30)}            # sg13cmos5l_pr/rppd.sym
# rppd's value as the PDK symbol computes it - xschem shows it, the LVS ignores it
RPPD_VALUE = ('value=\\"expr_eng(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) '
              '+ 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )\\"')
# decap rows in the layout - keep in step with N_LV / N_HV in scripts/top/route_top.py
DECAP_LV, DECAP_HV = 83, 95

CELLS = [
    # the reference from pad 2 through its secondary protection is the bit
    # clock; the control from dig_in bits, which the housekeeping SPI routes
    # individually to a pin, a constant or the sequencer.
    ("xpat", "lvds_pattern.sym", "lvds_pattern", 1630, -980, {
        "ref_clk": "s14_an_2_esd",
        "en": "dig_in[1]", "reset": "dig_in[2]", "mode": "dig_in[3]",
        "D_p": "core_p", "D_n": "core_n", "VDD": "vdd_1v2", "VSS": "vss_1v2"}, ""),
    # the output pair straight onto pads 1 and 0, the bias through two 1:15 mirrors
    ("xlvds", "lvds_tx.sym", "lvds_tx", 2040, -1030, {
        "D_p": "core_p", "D_n": "core_n", "Iref_pd": "iref_pd_30u",
        "Iref_drv": "iref_drv_30u", "Vref": "vbias", "Va": "vdd_3v3",
        "Out_p": "s14_an[1]", "Out_n": "s14_an[0]", "Vss": "vss_3v3"}, ""),
    # the IDAC grid stops at 10 uA; the transmitter wants 30 uA per reference
    ("xiref_pd", "iref_x15.sym", "iref_x15", 1900, -800, {
        "IREF_IN": "ibias0", "IREF_OUT": "iref_pd_30u", "Va": "vdd_3v3", "Vss": "vss_3v3"}, ""),
    ("xiref_drv", "iref_x15.sym", "iref_x15", 2250, -800, {
        "IREF_IN": "ibias1", "IREF_OUT": "iref_drv_30u", "Va": "vdd_3v3", "Vss": "vss_3v3"}, ""),
    # the switchable 50 ohm termination of ref_clk, on pad 2 itself (s14_an[2]):
    # behind the secondary protection the ~520 ohm there would make it a divider
    ("xodt", "ref_odt.sym", "ref_odt", 1630, -1250, {
        "EN": "dig_in[0]", "PAD": "s14_an[2]", "VDD": "vdd_1v2", "VDDH": "vdd_3v3", "VSS": "vss_3v3"}, ""),
    # the switchable ~200 ohm back-termination across the output pair: a wave
    # coming back from the receiver is absorbed instead of thrown back by the
    # current-source driver; ibias1 3 uA instead of 2 uA keeps |Vod|
    # taps on the bias nodes for measuring - or forcing from outside, should the
    # IDAC or the voltage reference not work: 1.1 kohm of rppd each, at the frame
    # edge in the layout (scripts/top/route_top.py)
    ("RT0", "sg13cmos5l_pr/rppd.sym", "res", 2450, -1300, {"P": "analog_bus0", "M": "ibias0"},
     "w=1u l=4u model=rppd body=vss_1v2 spiceprefix=X b=0 m=1 mm_ok=1 " + RPPD_VALUE),
    ("RT1", "sg13cmos5l_pr/rppd.sym", "res", 2560, -1300, {"P": "analog_bus1", "M": "vbias"},
     "w=1u l=4u model=rppd body=vss_1v2 spiceprefix=X b=0 m=1 mm_ok=1 " + RPPD_VALUE),
    ("RT2", "sg13cmos5l_pr/rppd.sym", "res", 2670, -1300, {"P": "analog_bus2", "M": "ibias1"},
     "w=1u l=4u model=rppd body=vss_1v2 spiceprefix=X b=0 m=1 mm_ok=1 " + RPPD_VALUE),
    ("xbt", "lvds_bt.sym", "lvds_bt", 2040, -1300, {
        "EN": "dig_in[4]", "OUTP": "s14_an[1]", "OUTN": "s14_an[0]",
        "VDD": "vdd_1v2", "VDDH": "vdd_3v3", "VSS": "vss_3v3"}, ""),
    # reset is ~470 um of metal3 from dig_in[2] to a small gate and has no antenna
    # diode inside lvds_pattern (en, mode and ref_clk do): this one sits under the
    # line in the layout, 9 um before the pin (scripts/top/route_top.py)
    ("DRST", "sg13cmos5l_pr/dantenna.sym", "dio", 1300, -960, {
        "d1": "dig_in[2]", "d0": "vss_1v2"}, "model=dantenna l=0.78u w=0.78u spiceprefix=X"),
    # decoupling, one row of decap cells per supply domain, laid under the edges
    # of the TopMetal1 supply straps (scripts/top/route_top.py, which places
    # exactly DECAP_LV / DECAP_HV of them).  The 3.3 V row has to be HV cells.
    ("xdc12[%d:0]" % (DECAP_LV - 1), "sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym", "decap",
     2900, -840, {}, "VDD=vdd_1v2 VSS=vss_1v2 prefix=sg13cmos5l_"),
    ("xdc33[%d:0]" % (DECAP_HV - 1), "sg13g2_hv_decap_8.sym", "decap",
     2900, -730, {}, "VDD=vdd_3v3 VSS=vss_3v3 prefix=sg13g2_hv_"),
]

HEADER = """v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}"""

NOTES = """T {Chipalooza 2026, slot 14 - LVDS transmitter with PRBS-7 generator} 800 -1900 0 0 1 1 {}
T {Port list is the slot-14 frame (slot14_wrapper of
RTimothyEdwards/sg13cmos5l_ocd_chipalooza), pin for pin, so this cell and
layout/slot_14.gds compare by name in LVS.  Slot 14 has three dedicated
analog pads, each an sg13cmos5l_IOPadAnalog with two core terminals:
s14_an[i] is the pad itself (primary clamps only), s14_an_i_esd goes through
its secondary protection (series resistor and diodes), the one for gates.

  s14_an[0]      d_n       LVDS out -   (Out_n is the upper one of the pair)
  s14_an[1]      d_p       LVDS out +
  s14_an_2_esd   ref_clk   reference in, feeds lvds_pattern - a gate input
  s14_an[2]      odt       pad 2 itself: the switchable 50 ohm termination
  s14_an_0_esd, s14_an_1_esd   not connected

Not connected: dig_out[11:0], dig_in[23:5], analog_bus3, clk,
enable and reset - the reference arrives on its own pad.  The harness masks
dig_in to zero for an unselected project (proj_dig_in is dig_in ANDed with
select & dig_ena in user_project_control.v), so dig_in[1] alone stops the
pattern clock.} 300 -1820 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit individually to a
pin, a constant or the sequencer, so a configuration bit costs a register
write and no pin.  Unselected holds every dig_in at zero, and all-zero
leaves the clock stopped and the output pair static - a legal idle.

  dig_in[0]     odt        1 = 50 ohm termination of ref_clk on (xodt); 0 = off
  dig_in[1]     en        gates the pattern clock, not the output pair
  dig_in[2]     reset      active high, seeds the PRBS shift register
                           Neither reaches the two output flops: they run on an
                           ungated clock with RESET_B tied high, so D_p and D_n
                           are complementary from the first edge after power-up
                           and the LVDS driver settles once, not at every enable.
  dig_in[3]     mode       0 = clock passthrough, 1 = PRBS-7
  dig_in[4]     bt         1 = ~200 ohm across the LVDS pair (xbt) - set ibias1
                           to 3 uA with it, or |Vod| drops by a third; 0 = off
  dig_in[23:5]  unused

The PLL that clocked lvds_pattern through pll_clk left the project on
2026-10-07, and the pattern's clock source select (pll_clk, clk_src) with
it; the PLL goes on as a project of its own.} 300 -1400 0 0 0.4 0.4 {}
T {Two supply domains, one ground.  core_p / core_n cross from vss_1v2 into
the pre-driver on vss_3v3.  The harness ties the two grounds
(chipalooza_frame.v: assign vss3v3 = vss1v2), and every tap of either sits in
the same substrate, so the layout extraction merges them as well; the LVS
joins them in this schematic too (scripts/verify/check_lvs.sh).

The output pads carry the primary clamps only: a series resistor in an
LVDS output would eat the swing.} 1450 -560 0 0 0.35 0.35 {}
T {Decoupling Capacitors} 2860 -990 0 0 0.25 0.25 {}
T {DRST: antenna diode
on the long reset line} 1180 -860 0 0 0.25 0.25 {}"""


def gen_sch(path):
    out = [HEADER, NOTES]
    for inst, sym, fam, x, y, conn, extra in CELLS:
        for pin in sorted(conn):
            dx, dy = PINS[fam][pin]
            px, py = x + dx, y + dy
            tag = pin.lower().replace("[", "").replace("]", "")
            if fam != "mos" and abs(dy) > abs(dx):   # a macro pin on the top or bottom edge
                s = -1 if dy < 0 else 1
                ey = py + s * 40
                out.append("N %d %d %d %d {lab=%s}"
                           % (px, min(py, ey), px, max(py, ey), conn[pin]))
                out.append("C {lab_pin.sym} %d %d %d 0 "
                           "{name=l_%s_%s sig_type=std_logic lab=%s}"
                           % (px, ey, 1 if s < 0 else 3, inst, tag, conn[pin]))
            else:
                s = -1 if dx < 0 else 1
                ex = px + s * 40
                out.append("N %d %d %d %d {lab=%s}"
                           % (min(px, ex), py, max(px, ex), py, conn[pin]))
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
        # ngspice has to run from the netlist directory: the deck reaches the
        # PDK through relative .lib / .include lines, writes its raw beside
        # itself and its wrdata output to ../plot_simulations/data.  Started
        # anywhere else it dies on Cannot compute substitute, and the d_cosim
        # shared object would not resolve either.  make sim-xschem cds there;
        # the launcher does the same and puts the directory back after.
        'xschem netlist\n'
        'set _cwd [pwd]\n'
        'cd $netlist_dir\n'
        'simulate\n'
        'cd $_cwd\n'
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
    "iovdd": ("v", "3.3", "pad ring, 3.3 V - pad 2's IO cell"),
    "vbias": ("v", "1.2", "LVDS common-mode reference, 1.2 V from the harness voltage reference"),
    "ibias0": ("i", "-1.935u", "pre-driver reference, IDAC code 6 = 1.935uA into the 1:15 mirror"),
    "ibias1": ("i", "PWL(0 -1.935u 400n -1.935u 400.1n -2.903u)", "driver reference, code 6; code 9 = 2.903uA from 400 ns"),
    "dig_in[0]": ("v", "PWL(0 0 300n 0 300.1n 1.2)", "ODT: off, on from 300 ns"),
    "dig_in[4]": ("v", "PWL(0 0 400n 0 400.1n 1.2)", "back-termination: off, on from 400 ns"),
    "dig_in[1]": ("v", "PWL(0 0 3n 0 3.1n 1.2)", "en, low until 3 ns"),
    "dig_in[2]": ("v", "PWL(0 1.2 2n 1.2 2.1n 0 400n 0 400.1n 1.2 402n 1.2 402.1n 0)",
                  "reset until 2 ns, again at 400 ns"),
    "dig_in[3]": ("v", "1.2", "mode = 1, PRBS-7 throughout"),
}
TB_LVDS_GROUND = ("vss_3v3", "vss_1v2")
TB_LVDS_PADS = ("s14_an[1]", "s14_an[0]")     # the differential pair: d_p, d_n

# the three phases of the run (see LVDS_TITLE) and the windows each is measured in
TB_LVDS_PHASES = [
    ("a", 150, 295, "phase A - ODT off, EMF 1.2 V: pad 1.2 V, no pad current"),
    ("b", 320, 395, "phase B - ODT on, EMF 1.2 V: pad halved to 0.6 V if the ODT is 50 ohm"),
    ("c", 500, 695, "phase C - ODT on, EMF 2.4 V: pad 1.2 V, 24 mA while high; back-termination on, ibias1 3 uA"),
]


def tb_lvds_measures():
    out = []
    for k, t0, t1, what in TB_LVDS_PHASES:
        w = "from=%dn to=%dn" % (t0, t1)
        for name, fn, vec in (("enh", "AVG", "v(x1.xodt.enh)"), ("x_max", "MAX", "v(x1.xodt.x)"),
                              ("pad_max", "MAX", "v(clk_pad)"), ("pad_min", "MIN", "v(clk_pad)"),
                              ("ck_max", "MAX", "v(s14_an_2_esd)"), ("ck_min", "MIN", "v(s14_an_2_esd)"),
                              ("ipad_max", "MAX", "i(Vpad2)"), ("ipad_avg", "AVG", "i(Vpad2)"),
                              ("core_pp", "PP", "v(x1.core_p)"),
                              ("vod_max", "MAX", "vod"), ("vod_min", "MIN", "vod"),
                              ("vos_avg", "AVG", "v(vos)"), ("vos_pp", "PP", "v(vos)"),
                              ("i_3v3", "AVG", "i(Vvdd_3v3)"), ("i_1v2", "AVG", "i(Vvdd_1v2)")):
            out.append("meas tran %s_%s %s %s %s" % (name, k, fn, vec, w))
    for k, t0, t1, what in TB_LVDS_PHASES:
        out.append("echo === %s (%d-%d ns)" % (what, t0, t1))
        out.append("print enh_%s x_max_%s pad_max_%s pad_min_%s ck_max_%s ck_min_%s ipad_max_%s ipad_avg_%s"
                   % ((k,) * 8))
        out.append("print core_pp_%s vod_max_%s vod_min_%s vos_avg_%s vos_pp_%s i_3v3_%s i_1v2_%s"
                   % ((k,) * 7))
    # phase B: the same generator into the termination - the pad divides 1.2 V EMF
    # between the generator's 50 ohm and the ODT
    out.append("let r_odt = 50 * pad_max_b / (1.2 - pad_max_b)")
    out.append("echo === ODT resistance from phase B, 50 * Vpad / (1.2 V - Vpad):")
    out.append("print r_odt")
    return "\n".join(out)


TB_LVDS_CONTROL = r"""
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.include ../../../models/diodes_tt0.lib
.include sg13g2_esd.lib
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_io/spice/sg13cmos5l_io.spi
* the substrate terminal of the pad cell's poly resistor
.global sub!
Vsub sub! 0 0
.temp 27
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
* Without this the H-bridge cannot balance at t=0, cmfb runs to the rail and the
* pair spends ~60 ns climbing back (tb_startup measures 61.3 ns).  The driver's
* own benches place cmfb the same way and run no operating point.
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.control
* save all over 700 ns at 5 ps writes a rawfile of several 100 MB; name what the
* measurements, the wrdata and the graph panels actually need.  In_p / In_n are
* the pre-driver pair inside xlvds, where a common-mode problem shows up first.
save d_p d_n vos clk_pad s14_an_2_esd dig_in_0_ i(Vpad2) x1.core_p x1.core_n
+ x1.xodt.enh x1.xodt.x i(Vvdd_3v3) i(Vvdd_1v2) i(Viovdd) x1.xlvds.In_p x1.xlvds.In_n
tran 5p 700n 0 5p
write @schname\\\\.raw

let vod = v(d_p)-v(d_n)
%s

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n) v(clk_pad) v(s14_an_2_esd) i(Vpad2)
.endc
""" % tb_lvds_measures()


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
    """the stacked waveform panels, with the launchers above them

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
                       'C {isource.sym} %d %d 0 0 {name=I%s value="%s"}'
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


# ref_clk comes in the way it does on the chip: a 50 ohm generator onto pad 2
# itself (s14_an[2], where xodt hangs), through the pad's IO cell and its
# secondary protection to s14_an_2_esd.  Two pulse sources in series make the
# generator: the second one joins at 400 ns, which doubles the EMF - a generator
# set to 1.2 V into 50 ohm.  Placed below the output termination, connected by
# net labels only.
REFCLK_X, REFCLK_Y = 500, 1000
# the pad pin is there twice: core side (100, -350) and bond pad (110, -100), one net
PAD2_PINS = {"vss": (7.5, -340), "vdd": (17.5, -330), "iovss": (27.5, -320), "bond": (110, -100),
             "iovdd": (40, -310), "pad": (100, -350), "padres": (200, -350)}


def refclk_path():
    x, y = REFCLK_X, REFCLK_Y
    out = []

    def lab(px, py, net, name):
        if net == "GND":
            out.append("C {devices/gnd.sym} %g %g 0 0 {name=lgr_%s lab=GND}" % (px, py, name))
        else:
            out.append("C {lab_pin.sym} %g %g 0 0 {name=lr_%s sig_type=std_logic lab=%s}"
                       % (px, py, name, net))

    def vert(sym, cx, cy, name, value, top, bot):
        out.append('C {%s} %d %d 0 0 {name=%s value="%s"}' % (sym, cx, cy, name, value))
        lab(cx, cy - 30, top, name + "_t")
        lab(cx, cy + 30, bot, name + "_b")

    vert("devices/vsource.sym", x, y, "Vclk_a", "PULSE(0 1.2 0 50p 50p 0.9n 2n)", "clk_mid", "GND")
    vert("devices/vsource.sym", x, y - 200, "Vclk_b", "PULSE(0 1.2 400n 50p 50p 0.9n 2n)",
         "clk_gen", "clk_mid")
    vert("res.sym", x + 300, y - 200, "Rgen", "50", "clk_gen", "clk_pad")
    vert("devices/vsource.sym", x + 500, y - 200, "Vpad2", "0", "clk_pad", "s14_an[2]")
    px, py = x + 800, y + 250
    out.append("C {sg13cmos5l_io/sg13cmos5l_IOPadAnalog.sym} %d %d 0 0 {name=xpad2}" % (px, py))
    for pin, net in (("vss", "GND"), ("vdd", "vdd_1v2"), ("iovss", "GND"),
                     ("iovdd", "iovdd"), ("pad", "s14_an[2]"), ("padres", "s14_an_2_esd"), ("bond", "s14_an[2]")):
        dx, dy = PAD2_PINS[pin]
        lab(px + dx, py + dy, net, "pad2_" + pin)
    out.append("T {ref_clk: 50 ohm generator onto pad 2.  Vclk_b joins at 400 ns:\n"
               "EMF 1.2 V before, 2.4 V after (1.2 V into 50 ohm).\n"
               "Vpad2 is the ammeter: the current into the pad, i.e. into xodt.} "
               "%d %d 0 0 0.35 0.35 {}" % (x - 100, y - 420))
    out.append("T {pad 2: IOPadAnalog (PDK model) - pad = s14_an[2] with xodt,\n"
               "padres = s14_an_2_esd, the ref_clk input of lvds_pattern} "
               "%d %d 0 0 0.3 0.3 {}" % (px - 100, py + 60))
    return out


# the sources, split by what they are actually for
TB_LVDS_GROUPS = [
    ("supplies", ["vdd_3v3", "vdd_1v2", "iovdd"]),
    ("bias", ["vbias", "ibias0", "ibias1"]),
    ("pattern control", ["dig_in[0]", "dig_in[1]", "dig_in[2]", "dig_in[3]", "dig_in[4]"]),
]

LVDS_TITLE = """LVDS bench for the top cell - the schematic, and the ODT switched on and off.

ref_clk comes from a 50 ohm generator onto pad 2 (s14_an[2]), through the pad's
IO cell and its secondary protection to s14_an_2_esd.  xodt hangs on pad 2.
The run has three phases:

  A    0 - 300 ns   ODT off, EMF 1.2 V   pad 1.2 V, no current into the pad
  B  300 - 400 ns   ODT on,  EMF 1.2 V   pad halved to 0.6 V: 50 ohm into 50 ohm
                                        (too small for the clock - the pattern stalls)
  C  400 - 700 ns   ODT on,  EMF 2.4 V   pad 1.2 V again, 24 mA while high;
                                        reset at 400 ns, PRBS-7 runs again;
                                        the output back-termination on (dig_in[4])
                                        and ibias1 3 uA

PRBS-7 at 500 Mb/s through the pre-driver and the driver into 49.9 + 49.9 ohm
across pads 1 and 0 with the Vos tap.  The log prints each phase: the clock at
the pad and behind the protection, the pad current, Vod / Vos, the supplies.

Only pad 2 is modelled (its IO cell is what joins s14_an[2] to s14_an_2_esd);
the outputs see an ideal 100 ohm.  Pads, bond wires, package and line on all
three: slot_14_tb_lvds_pads (layout wiring) and slot_14_tb_lvds_pex."""


def gen_tb_lvds(path, symbol):
    pins = sym_pins(symbol)
    covered = [n for _, names in TB_LVDS_GROUPS for n in names]
    assert sorted(covered) == sorted(TB_LVDS_DRIVE), "groups and drive disagree"
    out = [HEADER, title_block(DOC_X, DOC_TITLE_Y, LVDS_TITLE)]
    out += stim_groups(TB_LVDS_GROUPS, TB_LVDS_DRIVE)
    out += dut_stubs(pins, TB_LVDS_GROUND, skip=TB_LVDS_PADS)
    out.append("C {%s.sym} 0 0 0 0 {name=x1}" % TOP)
    out += pad_network(pins, TB_LVDS_PADS)
    out += refclk_path()
    # the four full-run panels share their window and stay locked together:
    #   the switch - dig_in[0] and the gate of the ODT switch, level-shifted to 3.3 V
    #   the pad - its envelope halves at 300 ns and is back at 1.2 V from 400 ns;
    #     x1.xodt.x, behind R1, drops to ~0 once the switch is on
    #   the current into the pad - edge spikes only with the ODT off, 12 mA and
    #     then 24 mA while the clock is high with it on
    #   the output pair
    # below them the switch-on at 300 ns close up, and a few settled bits of phase C
    out += view_panels(
        [(["dig_in_0_", "x1.xodt.enh"], [8, 10], -0.2, 3.6, 0.0, 7.0e-7),
         (["clk_pad", "x1.xodt.x", "s14_an_2_esd"], [4, 12, 7], -0.2, 1.6, 0.0, 7.0e-7),
         (["i(vpad2)"], [4], -0.01, 0.03, 0.0, 7.0e-7),
         (["d_p", "d_n", "vos"], [4, 5, 8], 0.9, 1.6, 0.0, 7.0e-7),
         (["dig_in_0_", "x1.xodt.enh", "clk_pad", "x1.xodt.x"], [8, 10, 4, 12],
          -0.2, 3.6, 2.94e-7, 3.08e-7),
         (["i(vpad2)"], [4], -0.01, 0.03, 2.94e-7, 3.08e-7),
         (["clk_pad", "i(vpad2)"], [4], -0.01, 1.6, 3.96e-7, 4.08e-7),
         # vod is a let vector, written after the rawfile: the panel computes it
         (["d_p", "d_n", '\\\\"vod;d_p d_n -\\\\"'], [4, 5, 7], -0.5, 1.6, 6.50e-7, 6.60e-7)],
        TOP + "_tb_lvds")
    out.append(code_block(DOC_X, DOC_CODE_Y, TB_LVDS_CONTROL))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ------------------------------------------------------------------ testbench
TB_SOURCES = [
    ("vdd_3v3", "v", "3.3", "gated 3.3 V"),
    ("vdd_1v2", "v", "1.2", "gated 1.2 V"),
    ("vbias", "v", "1.2", "LVDS common-mode reference, 1.2 V"),
    ("s14_an_2_esd", "v", "PULSE(0 1.2 0 50p 50p 1.9n 4n)", "ref_clk, 250 MHz"),
    ("dig_in[0]", "v", "0", "ODT off"),
    ("dig_in[4]", "v", "0", "back-termination off"),
    ("dig_in[1]", "v", "PWL(0 0 3n 0 3.1n 1.2)", "en, low until 3 ns"),
    ("dig_in[2]", "v", "PWL(0 1.2 2n 1.2 2.1n 0)", "reset, high until 2 ns"),
    ("dig_in[3]", "v", "PWL(0 0 10n 0 10.1n 1.2)", "mode -> PRBS-7 at 10 ns"),
    ("ibias0", "i", "-1.935u", "pre-driver reference, IDAC code 6"),
    ("ibias1", "i", "-1.935u", "driver reference, IDAC code 6"),
]

TB_CONTROL = r"""
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.include ../../../models/diodes_tt0.lib
.include sg13g2_esd.lib
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
.ic v(x1.xlvds.xdrv.cmfb)=1.54
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
"""


def gen_tb(path):
    out = [HEADER]
    out.append("T {Top-level transient bench.\n\n"
               "  s14_an_2_esd   250 MHz reference on pad 2, the bit clock\n"
               "  dig_in[1]      en, low until 3 ns\n"
               "  dig_in[2]      reset, high until 2 ns\n"
               "  dig_in[3]      mode, PRBS-7 from 10 ns\n"
               "  ibias0/1       2 uA each into the two 1:15 mirrors\n\n"
               "Load is 49.9 + 49.9 ohm across s14_an[1] / s14_an[0] with the\n"
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
    grounded = {"vss_3v3", "vss_1v2"}
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

    # ngspice's frontend reads [ ] as vector indexing, so v(s14_an[1]) will not
    # parse.  A 0 V source per pad gives the net a plain name to measure on, and
    # its branch current is the pad current for free.
    for x, pad, name in ((700, "s14_an[0]", "d_n"), (900, "s14_an[1]", "d_p")):
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
    import sys
    sch = os.path.join(HERE, "..", "schematic", "xschem")
    tb = os.path.join(HERE, "..", "testbenches", "xschem")
    sym = os.path.join(sch, TOP + ".sym")
    # The top cell may be edited by hand in xschem, so regenerating it would throw
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
    print("wrote %s_tb_lvds.sch from the %d pins of %s.sym"
          % (TOP, len(sym_pins(sym)), TOP))
