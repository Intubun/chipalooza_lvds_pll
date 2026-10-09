#!/usr/bin/env python3
"""Write testbenches/xschem/slot_14_tb_lvds_pads.sch and slot_14_tb_lvds_pex.sch

The slot as laid out, with what lies outside it: the three IHP pads of slot 14
(sg13cmos5l_IOPadAnalog, the PDK's spice model - clamps, diodes and the
secondary protection), a bond wire and the package, a 50 ohm board line and
the receiver.  The question it answers is what the transmitter looks like at
the far end of a real link, and what the on-die termination of ref_clk does:

  ref_clk   generator, 50 ohm series -> 50 ohm line, 200 ps -> 0.5 pF package
            -> 2 nH bond wire -> Vpad2 (the ammeter) -> pad 2 -> padres
            (secondary protection) -> s14_an_2_esd
  d_p, d_n  s14_an[1] / s14_an[0] = the pad itself -> 2 nH -> 0.5 pF -> 50 ohm
            line, 200 ps -> receiver: 1 pF per side, 49.9 + 49.9 ohm, Vos tap
  ODT       on the ref_clk input only: xodt (macros/ref_odt) inside the top
            cell, on pad 2 itself (s14_an[2]), switched by dig_in[0].  The
            outputs are never terminated on chip.

One run, the same three phases as slot_14_tb_lvds:

  A    0 - 300 ns   ODT off, EMF 1.2 V   series terminated: the open end doubles 0.6 V
  B  300 - 400 ns   ODT on,  EMF 1.2 V   the pad halves to 0.6 V - 50 ohm into 50 ohm
  C  400 - 700 ns   ODT on,  EMF 2.4 V   a generator set to 1.2 V into 50 ohm; reset
                                        at 400 ns, PRBS-7 runs again; the output
                                        back-termination on (dig_in[4], xbt) with
                                        ibias1 at 3 uA - the reflections of A, absorbed

The pad ring is iovdd = 3.3 V / iovss = 0; vdd / vss of the pad cell (its 1.2 V
core pins) at 1.2 V / 0.  Package and line values are typical guesses for a
QFN on FR4, not a measured channel - change them in PKG below.

Two benches, the same surroundings, two views of the slot (scripts/sim/extract_top.sh
writes both netlists from one extraction of layout/slot_14.gds):

  slot_14_tb_lvds_pads  slot_14_wires.sym: the top-level wiring as laid out, with
                        its capacitance, and the blocks from their schematics -
                        the pads and the connections between them and the blocks
  slot_14_tb_lvds_pex   slot_14_pex.sym: everything as laid out, every block
                        from its own extraction

The schematic itself, without the output pads: slot_14_tb_lvds (scripts/gen_top.py).

    python3 scripts/sim/gen_tb_lvds_pads.py
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gen_top  # noqa: E402  graph(), launchers() - the panels look like slot_14_tb_lvds's

TOP = "slot_14"
TB = os.path.join(ROOT, "testbenches", "xschem")
SYM = os.path.join(ROOT, "schematic", "xschem", TOP + ".sym")

# bench -> (DUT symbol, its netlist, what the DUT is)
VARIANTS = {
    "pads": ("slot_14_wires", "slot_14_wires.spice",
             "the top-level wiring as laid out (with its capacitance), the blocks from their schematics"),
    "pex": ("slot_14_pex", "slot_14_pex.spice",
            "everything as laid out: the wiring and every block from the extraction"),
}

PKG = {"lbond": "2n", "cpkg": "0.5p", "z0": "50", "td": "200p", "crx": "1p"}

# the phases of the run and the windows each is measured in (ns)
PHASES = [
    ("a", 150, 295, "phase A - ODT off, EMF 1.2 V: pad 1.2 V, no pad current"),
    ("b", 320, 395, "phase B - ODT on, EMF 1.2 V: pad halved to 0.6 V if the ODT is 50 ohm"),
    ("c", 500, 695, "phase C - ODT on, EMF 2.4 V: pad 1.2 V, 24 mA while high; back-termination on, ibias1 3 uA"),
]


def measures():
    out = []
    for k, t0, t1, what in PHASES:
        w = "from=%dn to=%dn" % (t0, t1)
        for name, fn, vec in (("enh", "AVG", "v(x1.xodt.enh)"), ("x_max", "MAX", "v(x1.xodt.x)"),
                              ("pad_max", "MAX", "v(clk_pad)"), ("pad_min", "MIN", "v(clk_pad)"),
                              ("ck_max", "MAX", "v(refclk_core)"), ("ck_min", "MIN", "v(refclk_core)"),
                              ("ipad_max", "MAX", "i(Vpad2)"), ("ipad_avg", "AVG", "i(Vpad2)"),
                              ("core_pp", "PP", "v(x1.core_p)"),
                              ("vod_max", "MAX", "vd"), ("vod_min", "MIN", "vd"),
                              ("vodpad_max", "MAX", "vdpad"), ("vodpad_min", "MIN", "vdpad"),
                              ("vos_avg", "AVG", "v(vos)"), ("vos_pp", "PP", "v(vos)"),
                              ("i_3v3", "AVG", "i(Vvdd_3v3)"), ("i_1v2", "AVG", "i(Vvdd_1v2)")):
            out.append("meas tran %s_%s %s %s %s" % (name, k, fn, vec, w))
    # the 20-80 % rise time at the receiver, on settled bits of phases A and C
    for k, t0, t1, what in (PHASES[0], PHASES[2]):
        out.append("let th20_%s = vod_min_%s + 0.2*(vod_max_%s - vod_min_%s)" % ((k,) * 4))
        out.append("let th80_%s = vod_min_%s + 0.8*(vod_max_%s - vod_min_%s)" % ((k,) * 4))
        out.append("meas tran t20_%s WHEN vd=$&th20_%s RISE=5 FROM=%dn" % (k, k, t0))
        out.append("meas tran t80_%s WHEN vd=$&th80_%s RISE=5 FROM=%dn" % (k, k, t0))
        out.append("let trise_%s = t80_%s - t20_%s" % ((k,) * 3))
    for k, t0, t1, what in PHASES:
        out.append("echo === %s (%d-%d ns)" % (what, t0, t1))
        out.append("print enh_%s x_max_%s pad_max_%s pad_min_%s ck_max_%s ck_min_%s ipad_max_%s ipad_avg_%s"
                   % ((k,) * 8))
        out.append("print core_pp_%s vod_max_%s vod_min_%s vodpad_max_%s vodpad_min_%s vos_avg_%s vos_pp_%s"
                   % ((k,) * 7))
        out.append("print i_3v3_%s i_1v2_%s" % ((k,) * 2))
    out.append("print trise_a trise_c")
    # phase B: the generator's 1.2 V EMF divided between its 50 ohm and the ODT -
    # the line is matched, so the pad sees the division once it has settled
    out.append("let r_odt = 50 * pad_max_b / (1.2 - pad_max_b)")
    out.append("echo === ODT resistance from phase B, 50 * Vpad / (1.2 V - Vpad):")
    out.append("print r_odt")
    return "\n".join(out)


# the waveform panels, right of the receiver: the four full-run panels share their
# window and stay locked together, the zooms below sit on the switch-on at 300 ns,
# the EMF step at 400 ns and a few settled bits of phase C
VD = '\\\\"vd;rx_p rx_n -\\\\"'
VDPAD = '\\\\"vdpad;chip_p chip_n -\\\\"'
PANELS = [
    (["odt_en", "x1.xodt.enh"], [8, 10], -0.2, 3.6, 0.0, 7.0e-7),
    (["clk_pad", "x1.xodt.x", "refclk_core"], [4, 12, 7], -0.2, 1.6, 0.0, 7.0e-7),
    (["i(vpad2)"], [4], -0.01, 0.03, 0.0, 7.0e-7),
    (["rx_p", "rx_n", "vos"], [4, 5, 8], 0.9, 1.6, 0.0, 7.0e-7),
    (["odt_en", "x1.xodt.enh", "clk_pad", "x1.xodt.x"], [8, 10, 4, 12], -0.2, 3.6, 2.94e-7, 3.08e-7),
    (["i(vpad2)"], [4], -0.01, 0.03, 2.94e-7, 3.08e-7),
    (["clk_pad", "refclk_core"], [4, 7], -0.2, 1.6, 3.96e-7, 4.08e-7),
    (["rx_p", "rx_n", VD], [4, 5, 7], -0.5, 1.6, 6.50e-7, 6.60e-7),
    (["chip_p", "chip_n", VDPAD], [4, 5, 7], -0.5, 1.6, 6.50e-7, 6.60e-7),
]
VIEW_X, VIEW_W, VIEW_TOP = 2700, 1800, -2150
DIG_IN = ("odt_en", "en", "rst", "mode", "bt_en")


def bench(variant):
    global L, n
    DUT, NETLIST, WHAT = VARIANTS[variant]
    NAME = TOP + "_tb_lvds_" + variant
    OUT = os.path.join(TB, NAME + ".sch")
    L = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}", "V {}", "S {}", "F {}", "E {}"]
    n = [0]

    def nm(p):
        n[0] += 1
        return "%s%d" % (p, n[0])

    seen = {}

    def pin(x, y, net, right=False):
        # a label joins whatever else sits on its point: two nets on one point would be
        # shorted without a word (Vbt and Vclk_b were, before the clock path moved left)
        assert seen.setdefault((x, y), net) == net, ((x, y), seen[(x, y)], net)
        L.append("C {devices/lab_pin.sym} %g %g 0 %d {name=%s sig_type=std_logic lab=%s}"
                 % (x, y, 1 if right else 0, nm("p"), net))

    def two(sym, x, y, name, value, top_net, bot_net):
        """a vertical two-terminal element, pins at y -/+ 30, a label on each"""
        L.append('C {%s} %g %g 0 0 {name=%s value="%s"}' % (sym, x, y, name, value))
        pin(x, y - 30, top_net)
        if bot_net == "GND":
            L.append("C {devices/gnd.sym} %g %g 0 0 {name=%s lab=GND}" % (x, y + 30, nm("g")))
        else:
            pin(x, y + 30, bot_net)

    def text(x, y, s, size=0.3):
        L.append("T {%s} %g %g 0 0 %s %s {}" % (s, x, y, size, size))

    # ---- the top cell, every frame pin labelled -----------------------------------
    NETS = {"vdd_3v3": "vdd_3v3", "vdd_1v2": "vdd_1v2", "vss_3v3": "GND", "vss_1v2": "GND",
            "ibias0": "ib0", "ibias1": "ib1", "vbias": "vcm_ref",
            "dig_in[0]": "odt_en", "dig_in[1]": "en", "dig_in[2]": "rst", "dig_in[3]": "mode",
            "dig_in[4]": "bt_en",
            "s14_an_2_esd": "refclk_core", "s14_an[2]": "clk_pad",
            "s14_an[1]": "chip_p", "s14_an[0]": "chip_n"}
    pins = [(m.group(5), (float(m.group(1)) + float(m.group(3))) / 2, (float(m.group(2)) + float(m.group(4))) / 2)
            for m in re.finditer(r"^B 5 (\S+) (\S+) (\S+) (\S+) \{name=([^ }]+)", io.open(SYM).read(), re.M)]
    assert len(pins) == 56, len(pins)
    L.append("C {%s.sym} 0 0 0 0 {name=x1}" % DUT)
    for name, px, py in pins:
        net = NETS.get(name, "nc_" + name.replace("[", "_").replace("]", ""))
        if net == "GND":
            L.append("C {devices/gnd.sym} %g %g %d 0 {name=%s lab=GND}" % (px, py, 1 if px < 0 else 3, nm("g")))
        else:
            pin(px, py, net, right=px > 0)

    # ---- stimulus -------------------------------------------------------------------
    X = -1500
    text(X - 150, -1050, "supplies, bias, control", 0.4)
    for i, (sym, name, val, net, note) in enumerate([
            ("devices/vsource.sym", "Vvdd_3v3", "3.3", "vdd_3v3", "3.3 V"),
            ("devices/vsource.sym", "Vvdd_1v2", "1.2", "vdd_1v2", "1.2 V"),
            ("devices/vsource.sym", "Viovdd", "3.3", "iovdd", "pad ring, 3.3 V"),
            ("devices/vsource.sym", "Vvcm", "1.2", "vcm_ref", "vbias = Vref, 1.2 V"),
            ("isource.sym", "Iib0", "-1.935u", "ib0", "ibias0, IDAC code 6 = 1.935uA"),
            ("isource.sym", "Iib1", "PWL(0 -1.935u 400n -1.935u 400.1n -2.903u)", "ib1", "ibias1, code 6; code 9 = 2.903uA from 400 ns"),
            ("devices/vsource.sym", "Vodt", "PWL(0 0 300n 0 300.1n 1.2)", "odt_en",
             "dig_in[0] ODT: off, on from 300 ns"),
            ("devices/vsource.sym", "Ven", "PWL(0 0 3n 0 3.1n 1.2)", "en", "dig_in[1] en"),
            ("devices/vsource.sym", "Vrst", "PWL(0 1.2 2n 1.2 2.1n 0 400n 0 400.1n 1.2 402n 1.2 402.1n 0)",
             "rst", "dig_in[2] reset until 2 ns, again at 400 ns"),
            ("devices/vsource.sym", "Vmode", "1.2", "mode", "dig_in[3] mode = PRBS-7"),
            ("devices/vsource.sym", "Vbt", "PWL(0 0 400n 0 400.1n 1.2)", "bt_en",
             "dig_in[4] back-termination: off, on from 400 ns")]):
        y = -900 + 160 * i
        if net in DIG_IN:
            # dig_in comes from the harness's logic, not from an ideal source: 100 ohm
            # behind each.  Ideal sources on these long lines stalled the PEX run
            # (timestep too small on vmode#branch at 513 ns).
            two(sym, X, y, name, val, net + "_drv", "GND")
            two("res.sym", X + 420, y, "R" + net, "100", net + "_drv", net)
        else:
            two(sym, X, y, name, val, net, "GND")
        text(X + 40, y - 10, note)

    # ---- the three pads -------------------------------------------------------------
    # IOPadAnalog has its pad pin twice: on the core side (100, -350), where the slot
    # pin joins, and on the bond pad (110, -100), where the bond wire lands - one net
    PADPINS = {"vss": (7.5, -340), "vdd": (17.5, -330), "iovss": (27.5, -320), "bond": (110, -100),
               "iovdd": (40, -310), "pad": (100, -350), "padres": (200, -350)}

    def pad(x, y, inst, pad_net, padres_net):
        L.append("C {sg13cmos5l_io/sg13cmos5l_IOPadAnalog.sym} %g %g 0 0 {name=%s}" % (x, y, inst))
        for p, net in (("vss", "GND"), ("vdd", "vdd_1v2"), ("iovss", "GND"), ("iovdd", "iovdd"),
                       ("pad", pad_net), ("padres", padres_net), ("bond", pad_net)):
            dx, dy = PADPINS[p]
            if net == "GND":
                L.append("C {devices/gnd.sym} %g %g 0 0 {name=%s lab=GND}" % (x + dx, y + dy, nm("g")))
            else:
                pin(x + dx, y + dy, net)

    pad(-1000, 900, "xpad2", "clk_pad", "refclk_core")
    pad(900, -300, "xpad1", "chip_p", "nc_pad1_res")
    pad(900, 300, "xpad0", "chip_n", "nc_pad0_res")
    text(-1000, 960, "pad 2: ref_clk in through padres (secondary protection), termination on the pad itself")
    text(900, -240, "pad 1: d_p, the pad direct")
    text(900, 360, "pad 0: d_n, the pad direct")

    # ---- ref_clk: generator, line, package, bond wire, ammeter ----------------------
    XC = -2300                           # left of the stimulus column, which reaches y 730
    text(XC - 150, 500, "ref_clk: 50 ohm generator, 50 ohm line, package, bond wire", 0.35)
    two("devices/vsource.sym", XC, 800, "Vclk_a", "PULSE(0 1.2 0 100p 100p 0.9n 2n)", "clk_mid", "GND")
    two("devices/vsource.sym", XC, 640, "Vclk_b", "PULSE(0 1.2 400n 100p 100p 0.9n 2n)", "clk_src", "clk_mid")
    two("res.sym", XC + 160, 700, "Rclk", "50", "clk_src", "clk_line")
    two("capa.sym", XC + 320, 700, "Cpkg_clk", PKG["cpkg"], "clk_pkg", "GND")
    two("ind.sym", XC + 480, 700, "Lclk", PKG["lbond"], "clk_pkg", "clk_bw")
    two("devices/vsource.sym", XC + 640, 700, "Vpad2", "0", "clk_bw", "clk_pad")
    text(XC - 150, 560, "Vclk_b joins at 400 ns: EMF 1.2 V before, 2.4 V after.  Vpad2 is the ammeter:\n"
                        "the current into pad 2, i.e. into xodt (s14_an[2]) and the pad cell", 0.3)

    # ---- outputs: bond wire, package, (line in the code block), receiver ------------
    XO = 1500
    text(XO - 100, -760, "d_p / d_n: bond wire, package, 50 ohm line, receiver", 0.35)
    for k, (s, chip) in enumerate((("p", "chip_p"), ("n", "chip_n"))):
        y = -600 + 400 * k
        two("ind.sym", XO, y, "Lb" + s, PKG["lbond"], chip, "pkg_" + s)
        two("capa.sym", XO + 160, y, "Cpkg_" + s, PKG["cpkg"], "pkg_" + s, "GND")
        two("capa.sym", XO + 480, y, "Crx_" + s, PKG["crx"], "rx_" + s, "GND")
    two("res.sym", XO + 640, -500, "Rt_p", "49.9", "rx_p", "vos")
    two("res.sym", XO + 640, -300, "Rt_n", "49.9", "vos", "rx_n")
    text(XO + 700, -420, "100 ohm at the receiver, mid-point = Vos")

    # ---- title -----------------------------------------------------------------------
    text(-1700, -1700, """LVDS link with the IHP pads - slot_14 with its three sg13cmos5l_IOPadAnalog,
bond wire %(lbond)sH, package %(cpkg)sF, a %(z0)s ohm line of %(td)ss, the receiver %(crx)sF + 100 ohm.

One run, three phases - the same as slot_14_tb_lvds:
  A    0 - 300 ns   ODT off, EMF 1.2 V   pad 1.2 V (the open end doubles 0.6 V)
  B  300 - 400 ns   ODT on,  EMF 1.2 V   pad halved to 0.6 V: 50 ohm into 50 ohm
  C  400 - 700 ns   ODT on,  EMF 2.4 V   pad 1.2 V, 24 mA while high; reset at 400 ns;
                                        the output back-termination on (dig_in[4]), ibias1 3 uA
The outputs are never terminated on chip.  The log prints each phase: the ODT
switch, the clock at pad 2 and behind the protection, the pad current, Vod / Vos
at the receiver and at the pads, the supplies; the rise time in A and C.

The slot: %(what)s
(%(net)s, from scripts/sim/extract_top.sh - run make extract-top after a layout change).
The pad cells are the PDK's spice model.""" % dict(PKG, what=WHAT, net=NETLIST), 0.45)

    CONTROL = r"""
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.include ../../../models/diodes_tt0.lib
.include sg13g2_esd.lib
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_io/spice/sg13cmos5l_io.spi
* the slot: %(what)s
.include ../../../netlist/pex/%(net)s
* the substrate terminal of the pads' poly resistors
.global sub!
Vsub sub! 0 0
* the board: one uncoupled 50 ohm line per leg
Tclk clk_line 0 clk_pkg 0 Z0=%(z0)s TD=%(td)s
Tp pkg_p 0 rx_p 0 Z0=%(z0)s TD=%(td)s
Tn pkg_n 0 rx_n 0 Z0=%(z0)s TD=%(td)s
.temp 27
* no savecurrents: with the PEX netlist it writes thousands of device currents
.options klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.control
save rx_p rx_n vos chip_p chip_n refclk_core clk_pad odt_en i(Vpad2) x1.xodt.enh x1.xodt.x
+ x1.core_p x1.core_n i(Vvdd_3v3) i(Vvdd_1v2) i(Viovdd)
tran 5p 700n 0 5p
write @schname\\\\.raw

let vd = v(rx_p)-v(rx_n)
let vdpad = v(chip_p)-v(chip_n)
%(measures)s

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ vd vdpad v(vos) v(refclk_core) v(clk_pad) i(Vpad2) v(odt_en)
.endc
""" % dict(PKG, what=WHAT, net=NETLIST, measures=measures())
    assert '"' not in CONTROL, "a double quote ends the value property"
    L.append('C {devices/code_shown.sym} -1700 -2600 0 0 {name=NGSPICE\nonly_toplevel=true\nvalue="%s"}' % CONTROL)

    # ---- the waveform panels and the Simulate / Load waves launchers ----------------
    L.extend(gen_top.launchers(VIEW_X, VIEW_TOP, NAME))
    y = VIEW_TOP + 200
    full = (0.0, 7.0e-7)
    for nodes, colors, ymin, ymax, t0, t1 in PANELS:
        L.append(gen_top.graph((VIEW_X, y, VIEW_X + VIEW_W, y + 400), nodes, colors,
                               ymin, ymax, t0, t1, unlocked=(t0, t1) != full))
        y += 500
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("geschrieben:", OUT)


# the DUT symbols: slot_14.sym with type=primitive, so the bench calls the
# subcircuit of the included netlist instead of descending into the schematic.
# slot_14_pex.sym comes with the top cell (scripts/gen_top.py --schematic).
prim = io.open(os.path.join(ROOT, "schematic", "xschem", TOP + "_pex.sym"), encoding="utf-8").read()
assert "type=primitive" in prim and "@symname" in prim
io.open(os.path.join(TB, TOP + "_wires.sym"), "w", encoding="utf-8", newline="\n").write(prim)
for v in VARIANTS:
    bench(v)
