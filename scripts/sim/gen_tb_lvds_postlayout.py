#!/usr/bin/env python3
"""Write testbenches/xschem/sg13cmos5l_chipalooza_analog_project_tb_lvds_postlayout.sch

The LVDS path after layout: lvds_pattern and lvds_tx from their magic
extraction with coupling C (scripts/sim/extract_lvds.sh, symbols
testbenches/xschem/*_pex.sym), PRBS-7 at 500 Mb/s into 49.9 + 49.9 ohm.
No PLL - the bit clock is an ideal 500 MHz source on ref_clk - so it runs
from the xschem Simulate button without the d_cosim set-up.

    python3 scripts/sim/gen_tb_lvds_postlayout.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "sg13cmos5l_chipalooza_analog_project_tb_lvds_postlayout"
OUT = os.path.join(HERE, "..", "..", "testbenches", "xschem", NAME + ".sch")

L = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}", "V {}", "S {}", "F {}", "E {}"]
n = [0]


def nm(p):
    n[0] += 1
    return "%s%d" % (p, n[0])


def pin(x, y, net, right=False):
    L.append("C {devices/lab_pin.sym} %g %g 0 %d {name=%s sig_type=std_logic lab=%s}" % (x, y, 1 if right else 0, nm("p"), net))


def source(x, y, name, value, net, kind="vsource"):
    """a source with its + pin on `net` and its - pin on GND (pins at y -/+ 30)"""
    sym = "devices/vsource.sym" if kind == "vsource" else "isource.sym"
    L.append('C {%s} %g %g 0 0 {name=%s value="%s"}' % (sym, x, y, name, value))
    pin(x, y - 30, net)
    L.append("C {devices/gnd.sym} %g %g 0 0 {name=%s lab=GND}" % (x, y + 30, nm("g")))


def text(x, y, s, size=0.3):
    L.append("T {%s} %g %g 0 0 %s %s {}" % (s, x, y, size, size))


# ---- title ------------------------------------------------------------------
text(-1700, -1350, """LVDS path after layout - lvds_pattern and lvds_tx as laid out.

Both blocks come from a magic extraction of their GDS with coupling
capacitance (the pex column of CACE): every wire and its coupling to
its neighbours is in the netlist, not just the transistors.
lvds_pattern sends PRBS-7 at 500 Mb/s, lvds_tx drives it into
49.9 + 49.9 ohm with the mid-point tapped for Vos (TIA/EIA-644-A).

Extract first (in the container):  make extract-lvds
  -> netlist/pex/lvds_tx_pex.spice, netlist/pex/lvds_pattern_pex.spice
then Simulate, then Load waves.  ~5 min for 160 ns.

No PLL here: ref_clk is an ideal 500 MHz source, so the bench needs
none of the d_cosim set-up of tb_lvds.  Bias currents are ideal 30 uA,
no pad or ESD model.""", 0.4)

# ---- stimulus ---------------------------------------------------------------
text(-1700, -560, "supplies and bias", 0.4)
for i, (name, val, net, kind, note) in enumerate([
        ("Vvdd_3v3", "3.3", "vdd_3v3", "vsource", "3.3 V, lvds_tx"),
        ("Vvdd_1v2", "1.2", "vdd_1v2", "vsource", "1.2 V, lvds_pattern"),
        ("Vvref", "1.2", "vref", "vsource", "common-mode reference"),
        ("Iiref_pd", "-30u", "iref_pd", "isource", "pre-driver bias, 30 uA"),
        ("Iiref_drv", "-30u", "iref_drv", "isource", "driver bias, 30 uA")]):
    y = -420 + 180 * i
    source(-1600, y, name, val, net, kind)
    text(-1450, y - 10, note)
text(-1000, -560, "pattern control", 0.4)
for i, (name, val, net, note) in enumerate([
        ("Vref_clk", "PULSE(0 1.2 0 25p 25p 1n 2n)", "ref_clk", "ref_clk, 500 MHz"),
        ("Vpll_clk", "0", "pll_clk", "pll_clk unused"),
        ("Vclk_src", "0", "clk_src", "clk_src = 0: take ref_clk"),
        ("Ven", "1.2", "en", "en = 1: clock runs"),
        ("Vreset", "PWL(0 1.2 2n 1.2 2.1n 0)", "reset", "reset until 2 ns"),
        ("Vmode", "1.2", "mode", "mode = 1: PRBS-7")]):
    y = -420 + 180 * i
    source(-900, y, name, val, net)
    text(-750, y - 10, note)

# ---- DUT ----------------------------------------------------------------------
XP, YP = 0, -200          # lvds_pattern_pex
L.append("C {lvds_pattern_pex.sym} %g %g 0 0 {name=xpat}" % (XP, YP))
for net, dy in (("ref_clk", -100), ("pll_clk", -80), ("clk_src", -60), ("en", -40), ("reset", -20), ("mode", 0)):
    pin(XP - 130, YP + dy, net)
for net, dy in (("vdd_1v2", 80), ("GND", 100)):
    pin(XP + 130, YP + dy, net, right=True)
XT, YT = 600, -250        # lvds_tx_pex, its D_p / D_n level with the pattern outputs
L.append("C {lvds_tx_pex.sym} %g %g 0 0 {name=xlvds}" % (XT, YT))


def wire(x0, y0, x1, y1, net):
    L.append("N %g %g %g %g {lab=%s}" % (x0, y0, x1, y1, net))


def wlabel(x, y, net):
    L.append("C {devices/lab_wire.sym} %g %g 0 0 {name=%s sig_type=std_logic lab=%s}" % (x, y, nm("w"), net))


# the pair, drawn: pattern -> driver
for net, y in (("core_p", YP - 100), ("core_n", YP - 80)):
    wire(XP + 130, y, XT - 150, y, net); wlabel(290, y, net)
for net, dy in (("iref_pd", -10), ("iref_drv", 10), ("vref", 30)):
    pin(XT - 150, YT + dy, net)
for net, dy in (("vdd_3v3", 60), ("GND", 80)):
    pin(XT + 150, YT + dy, net, right=True)
# 49.9 + 49.9 ohm in series across the pair, mid-point Vos - drawn
XR = 1000
L.append("C {res.sym} %g -250 0 0 {name=Rload_p value=49.9}" % XR)
L.append("C {res.sym} %g -160 0 0 {name=Rload_n value=49.9}" % XR)
wire(XT + 150, -280, XR, -280, "out_p"); wlabel(850, -280, "out_p")
wire(XR, -220, XR, -190, "vos"); wire(XR, -205, XR + 80, -205, "vos"); wlabel(XR + 80, -205, "vos")
wire(XT + 150, -260, 900, -260, "out_n"); wire(900, -260, 900, -130, "out_n"); wire(900, -130, XR, -130, "out_n")
wlabel(900, -180, "out_n")
text(XR + 40, -110, "100 ohm termination,\nmid-point = Vos")


# ---- graphs -------------------------------------------------------------------
def graph(x0, y0, x1, y1, nodes, colors, ymin, ymax):
    L.append("""B 2 %g %g %g %g {flags=graph
y1=%s
y2=%s
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1.2e-07
x2=1.4e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="%s"
color="%s"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}""" % (x0, y0, x1, y1, ymin, ymax, "\n".join(nodes), colors))


graph(1400, -1350, 3200, -980, ["out_p", "out_n", "vos"], "4 5 8", 0.9, 1.6)
graph(1400, -920, 3200, -550, ["vod"], "7", -0.5, 0.5)
graph(1400, -490, 3200, -120, ["core_p", "core_n"], "4 5", -0.2, 1.4)
graph(1400, -60, 3200, 310, ["xlvds.in_p", "xlvds.in_n"], "4 5", -0.2, 3.5)
text(3250, -1200, "LVDS outputs and Vos")
text(3250, -770, "Vod = out_p - out_n")
text(3250, -340, "pattern -> driver (1.2 V)")
text(3250, 90, "pre-driver -> H-bridge (3.3 V)")

# ---- launchers ----------------------------------------------------------------
L.append('''C {launcher.sym} 1400 -1480 0 0 {name=h_sim
descr="Simulate"
tclcommand="
set_sim_defaults
file mkdir $netlist_dir
xschem netlist
set _cwd [pwd]
cd $netlist_dir
simulate
cd $_cwd
"}''')
L.append('''C {launcher.sym} 1400 -1440 0 0 {name=h_waves
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/%s.raw tran"
}''' % NAME)

# ---- simulator commands -------------------------------------------------------------
L.append('''C {devices/code_shown.sym} -1700 750 0 0 {name=NGSPICE
only_toplevel=true
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
* the two extracted blocks (make extract-lvds); the paths are relative to
* testbenches/xschem/simulations, where xschem runs ngspice
.include ../../../netlist/pex/lvds_tx_pex.spice
.include ../../../netlist/pex/lvds_pattern_pex.spice
.temp 27
.options klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
* the common-mode loop starts near its operating point instead of
* climbing out of the rail for ~60 ns
.ic v(xlvds.xdrv.cmfb)=1.54
.control
save out_p out_n vos core_p core_n ref_clk xlvds.in_p xlvds.in_n
tran 10p 160n 0 10p
let vod = v(out_p) - v(out_n)
* TIA/EIA-644-A on the settled part: |Vod| 247..454 mV, Vos 1.125..1.375 V,
* Vos peak-to-peak <= 150 mV
meas tran vod_max MAX vod from=60n to=160n
meas tran vod_min MIN vod from=60n to=160n
meas tran vos_avg AVG v(vos) from=60n to=160n
meas tran vos_max MAX v(vos) from=60n to=160n
meas tran vos_min MIN v(vos) from=60n to=160n
let vos_pp = vos_max - vos_min
print vod_max vod_min vos_avg vos_pp
write %s.raw
.endc
"}''' % NAME)

open(OUT, "w").write("\n".join(L) + "\n")
print("geschrieben:", os.path.normpath(OUT))
