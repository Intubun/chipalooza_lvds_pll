#!/usr/bin/env python3
"""Write testbenches/xschem/slot_14_tb_lvds_pads.sch and slot_14_tb_lvds_pex.sch

The slot as laid out, with what lies outside it: the three IHP pads of slot 14
(sg13cmos5l_IOPadAnalog, the PDK's spice model - clamps, diodes and the
secondary protection), a bond wire and the package, a 50 ohm board line and
the receiver.  The question it answers is what the transmitter looks like at
the far end of a real link, and whether an on-die termination of the ref_clk input helps:

  ref_clk   source 1.2 V, 50 ohm series -> 50 ohm line, 200 ps -> 0.5 pF
            package -> 2 nH bond wire -> pad 2 -> padres (secondary
            protection) -> s14_an_2_esd
  d_p, d_n  s14_an[1] / s14_an[0] = the pad itself -> 2 nH -> 0.5 pF -> 50 ohm
            line, 200 ps -> receiver: 1 pF per side, 49.9 + 49.9 ohm, Vos tap
  ODT       on the ref_clk input only: xodt (macros/ref_odt) inside the top
            cell, on pad 2 itself (s14_an[2]), switched by dig_in[0].  The
            bench runs twice: dig_in[0] = 0 (off) with the source at 1.2 V EMF
            (series terminated, the open end doubles 0.6 V), then dig_in[0] = 1
            with 2.4 V EMF - a generator set to 1.2 V into 50 ohm.
            The outputs are never terminated on chip.

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

The schematic itself, without pads: slot_14_tb_lvds (scripts/gen_top.py).

    python3 scripts/sim/gen_tb_lvds_pads.py
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
TOP = "slot_14"
TB = os.path.join(ROOT, "testbenches", "xschem")
SYM = os.path.join(ROOT, "schematic", "xschem", TOP + ".sym")

# bench -> (DUT symbol, its netlist, runs, what the DUT is).  runs: 1 = ODT off only,
# 2 = off, then on.  The PEX bench takes a few times as long per run.
VARIANTS = {
    "pads": ("slot_14_wires", "slot_14_wires.spice", 2,
             "the top-level wiring as laid out (with its capacitance), the blocks from their schematics"),
    "pex": ("slot_14_pex", "slot_14_pex.spice", 1,
            "everything as laid out: the wiring and every block from the extraction"),
}

PKG = {"lbond": "2n", "cpkg": "0.5p", "z0": "50", "td": "200p", "crx": "1p"}

RUNS_TEXT = {
    1: """Runs once: ref_clk with the termination off (dig_in[0] = 0, source at 1.2 V
EMF, series terminated).  let runs = 2 in the code block adds the run with it
on (dig_in[0] = 1, xodt puts 50 ohm on pad 2; source at 2.4 V EMF).""",
    2: """Runs twice: ref_clk with the termination off (dig_in[0] = 0, source at 1.2 V
EMF, series terminated), then on (dig_in[0] = 1, xodt puts 50 ohm on pad 2;
source at 2.4 V EMF, i.e. set to 1.2 V into 50 ohm)."""}


def bench(variant):
    global L, n
    DUT, NETLIST, RUNS, WHAT = VARIANTS[variant]
    NAME = TOP + "_tb_lvds_" + variant
    OUT = os.path.join(TB, NAME + ".sch")
    L = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}", "V {}", "S {}", "F {}", "E {}"]
    n = [0]

    def nm(p):
        n[0] += 1
        return "%s%d" % (p, n[0])

    def pin(x, y, net, right=False):
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
            "ibias0": "ib0", "ibias1": "ib1", "analog_bus1": "vcm_ref",
            "dig_in[0]": "odt_en", "dig_in[1]": "en", "dig_in[2]": "rst", "dig_in[3]": "mode",
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
            ("devices/vsource.sym", "Vvcm", "1.2", "vcm_ref", "analog_bus1, 1.2 V"),
            ("isource.sym", "Iib0", "-2u", "ib0", "ibias0, 2 uA"),
            ("isource.sym", "Iib1", "-2u", "ib1", "ibias1, 2 uA"),
            ("devices/vsource.sym", "Vodt", "'odt_en'", "odt_en", "dig_in[0] ODT: 0 / 1.2"),
            ("devices/vsource.sym", "Ven", "PWL(0 0 3n 0 3.1n 1.2)", "en", "dig_in[1] en"),
            ("devices/vsource.sym", "Vrst", "PWL(0 1.2 2n 1.2 2.1n 0)", "rst", "dig_in[2] reset"),
            ("devices/vsource.sym", "Vmode", "1.2", "mode", "dig_in[3] mode = PRBS-7")]):
        y = -900 + 160 * i
        two(sym, X, y, name, val, net, "GND")
        text(X + 40, y - 10, note)

    # ---- the three pads -------------------------------------------------------------
    PADPINS = {"vss": (7.5, -340), "vdd": (17.5, -330), "iovss": (27.5, -320),
               "iovdd": (40, -310), "pad": (100, -350), "padres": (200, -350)}

    def pad(x, y, inst, pad_net, padres_net):
        L.append("C {sg13cmos5l_io/sg13cmos5l_IOPadAnalog.sym} %g %g 0 0 {name=%s}" % (x, y, inst))
        for p, net in (("vss", "GND"), ("vdd", "vdd_1v2"), ("iovss", "GND"), ("iovdd", "iovdd"),
                       ("pad", pad_net), ("padres", padres_net)):
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

    # ---- ref_clk: source, line, package, bond wire ----------------------------------
    XC = -1500
    text(XC - 150, 560, "ref_clk: 50 ohm source, 50 ohm line, package, bond wire", 0.35)
    two("devices/vsource.sym", XC, 700, "Vclk", "PULSE(0 'emf' 0 100p 100p 0.9n 2n)", "clk_src", "GND")
    two("res.sym", XC + 160, 700, "Rclk", "50", "clk_src", "clk_line")
    two("capa.sym", XC + 320, 700, "Cpkg_clk", PKG["cpkg"], "clk_pkg", "GND")
    two("ind.sym", XC + 480, 700, "Lclk", PKG["lbond"], "clk_pkg", "clk_pad")
    text(XC + 640, 680, "the termination itself is xodt inside the top cell, on clk_pad = s14_an[2]")

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

%(runs_text)s
The outputs are never terminated on chip.  The log prints
Vod / Vos at the receiver and at the pads, the 20-80 %% rise time at the
receiver, the clock at pad 2 and behind the secondary protection, and the
currents of the supplies and of the clock source.

The slot: %(what)s
(%(net)s, from scripts/sim/extract_top.sh - run make extract-top after a layout change).
The pad cells are the PDK's spice model.  The schematic without pads: slot_14_tb_lvds.""" % dict(PKG, what=WHAT, net=NETLIST, runs_text=RUNS_TEXT[RUNS]), 0.45)

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
.param odt_en=0 emf=1.2
.temp 27
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.control
save rx_p rx_n vos chip_p chip_n refclk_core clk_pad x1.core_p x1.core_n i(Vvdd_3v3) i(Vvdd_1v2) i(Viovdd) i(Vclk)
* 1 = ODT off only, 2 = then once more with the termination on
let runs = %(runs)d
let run = 0
while run < runs
  if run = 1
    alterparam odt_en=1.2
    alterparam emf=2.4
    reset
  end
  tran 5p 300n 0 5p
  let vd = v(rx_p)-v(rx_n)
  let vdpad = v(chip_p)-v(chip_n)
  meas tran vod_max MAX vd from=120n to=295n
  meas tran vod_min MIN vd from=120n to=295n
  meas tran vos_avg AVG v(vos) from=120n to=295n
  meas tran vos_max MAX v(vos) from=120n to=295n
  meas tran vos_min MIN v(vos) from=120n to=295n
  let vos_pp = vos_max - vos_min
  meas tran vodpad_max MAX vdpad from=120n to=295n
  meas tran vodpad_min MIN vdpad from=120n to=295n
  let th20 = vod_min + 0.2*(vod_max - vod_min)
  let th80 = vod_min + 0.8*(vod_max - vod_min)
  meas tran t20 WHEN vd=$&th20 RISE=5 FROM=150n
  meas tran t80 WHEN vd=$&th80 RISE=5 FROM=150n
  let trise = t80 - t20
  meas tran ck_max MAX v(refclk_core) from=120n to=295n
  meas tran ck_min MIN v(refclk_core) from=120n to=295n
  meas tran pad_max MAX v(clk_pad) from=120n to=295n
  meas tran pad_min MIN v(clk_pad) from=120n to=295n
  meas tran i_clk AVG i(Vclk) from=120n to=295n
* the pattern pair between lvds_pattern and lvds_tx: a static pair means the
* clock or the control never arrived, and the numbers above mean nothing
  meas tran core_pp PP v(x1.core_p) from=120n to=295n
  meas tran i_3v3 AVG i(Vvdd_3v3) from=120n to=295n
  meas tran i_1v2 AVG i(Vvdd_1v2) from=120n to=295n
  meas tran i_io AVG i(Viovdd) from=120n to=295n
  echo === run $&run - 0 dig_in 0 = 0 ODT off, 1 dig_in 0 = 1 ODT on
  print vod_max vod_min vos_avg vos_pp vodpad_max vodpad_min trise
  print ck_max ck_min pad_max pad_min core_pp i_3v3 i_1v2 i_io i_clk
  set wr_vecnames
  set wr_singlescale
  if run = 0
    wrdata ../plot_simulations/data/@schname\\\\_noodt.txt vd vdpad v(vos) v(refclk_core) v(clk_pad)
  else
    wrdata ../plot_simulations/data/@schname\\\\_odt.txt vd vdpad v(vos) v(refclk_core) v(clk_pad)
  end
  let run = run + 1
end
.endc
""" % dict(PKG, what=WHAT, net=NETLIST, runs=RUNS)
    assert '"' not in CONTROL, "a double quote ends the value property"
    L.append('C {devices/code_shown.sym} -1700 -2600 0 0 {name=NGSPICE\nonly_toplevel=true\nvalue="%s"}' % CONTROL)
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
