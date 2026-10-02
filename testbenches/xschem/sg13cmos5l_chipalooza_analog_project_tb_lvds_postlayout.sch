v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {LVDS path after layout - lvds_pattern and lvds_tx as laid out.

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
no pad or ESD model.} -1700 -1350 0 0 0.4 0.4 {}
T {supplies and bias} -1700 -560 0 0 0.4 0.4 {}
C {devices/vsource.sym} -1600 -420 0 0 {name=Vvdd_3v3 value="3.3"}
C {devices/lab_pin.sym} -1600 -450 0 0 {name=p1 sig_type=std_logic lab=vdd_3v3}
C {devices/gnd.sym} -1600 -390 0 0 {name=g2 lab=GND}
T {3.3 V, lvds_tx} -1450 -430 0 0 0.3 0.3 {}
C {devices/vsource.sym} -1600 -240 0 0 {name=Vvdd_1v2 value="1.2"}
C {devices/lab_pin.sym} -1600 -270 0 0 {name=p3 sig_type=std_logic lab=vdd_1v2}
C {devices/gnd.sym} -1600 -210 0 0 {name=g4 lab=GND}
T {1.2 V, lvds_pattern} -1450 -250 0 0 0.3 0.3 {}
C {devices/vsource.sym} -1600 -60 0 0 {name=Vvref value="1.2"}
C {devices/lab_pin.sym} -1600 -90 0 0 {name=p5 sig_type=std_logic lab=vref}
C {devices/gnd.sym} -1600 -30 0 0 {name=g6 lab=GND}
T {common-mode reference} -1450 -70 0 0 0.3 0.3 {}
C {isource.sym} -1600 120 0 0 {name=Iiref_pd value="-30u"}
C {devices/lab_pin.sym} -1600 90 0 0 {name=p7 sig_type=std_logic lab=iref_pd}
C {devices/gnd.sym} -1600 150 0 0 {name=g8 lab=GND}
T {pre-driver bias, 30 uA} -1450 110 0 0 0.3 0.3 {}
C {isource.sym} -1600 300 0 0 {name=Iiref_drv value="-30u"}
C {devices/lab_pin.sym} -1600 270 0 0 {name=p9 sig_type=std_logic lab=iref_drv}
C {devices/gnd.sym} -1600 330 0 0 {name=g10 lab=GND}
T {driver bias, 30 uA} -1450 290 0 0 0.3 0.3 {}
T {pattern control} -1000 -560 0 0 0.4 0.4 {}
C {devices/vsource.sym} -900 -420 0 0 {name=Vref_clk value="PULSE(0 1.2 0 25p 25p 1n 2n)"}
C {devices/lab_pin.sym} -900 -450 0 0 {name=p11 sig_type=std_logic lab=ref_clk}
C {devices/gnd.sym} -900 -390 0 0 {name=g12 lab=GND}
T {ref_clk, 500 MHz} -750 -430 0 0 0.3 0.3 {}
C {devices/vsource.sym} -900 -240 0 0 {name=Vpll_clk value="0"}
C {devices/lab_pin.sym} -900 -270 0 0 {name=p13 sig_type=std_logic lab=pll_clk}
C {devices/gnd.sym} -900 -210 0 0 {name=g14 lab=GND}
T {pll_clk unused} -750 -250 0 0 0.3 0.3 {}
C {devices/vsource.sym} -900 -60 0 0 {name=Vclk_src value="0"}
C {devices/lab_pin.sym} -900 -90 0 0 {name=p15 sig_type=std_logic lab=clk_src}
C {devices/gnd.sym} -900 -30 0 0 {name=g16 lab=GND}
T {clk_src = 0: take ref_clk} -750 -70 0 0 0.3 0.3 {}
C {devices/vsource.sym} -900 120 0 0 {name=Ven value="1.2"}
C {devices/lab_pin.sym} -900 90 0 0 {name=p17 sig_type=std_logic lab=en}
C {devices/gnd.sym} -900 150 0 0 {name=g18 lab=GND}
T {en = 1: clock runs} -750 110 0 0 0.3 0.3 {}
C {devices/vsource.sym} -900 300 0 0 {name=Vreset value="PWL(0 1.2 2n 1.2 2.1n 0)"}
C {devices/lab_pin.sym} -900 270 0 0 {name=p19 sig_type=std_logic lab=reset}
C {devices/gnd.sym} -900 330 0 0 {name=g20 lab=GND}
T {reset until 2 ns} -750 290 0 0 0.3 0.3 {}
C {devices/vsource.sym} -900 480 0 0 {name=Vmode value="1.2"}
C {devices/lab_pin.sym} -900 450 0 0 {name=p21 sig_type=std_logic lab=mode}
C {devices/gnd.sym} -900 510 0 0 {name=g22 lab=GND}
T {mode = 1: PRBS-7} -750 470 0 0 0.3 0.3 {}
C {lvds_pattern_pex.sym} 0 -200 0 0 {name=xpat}
C {devices/lab_pin.sym} -130 -300 0 0 {name=p23 sig_type=std_logic lab=ref_clk}
C {devices/lab_pin.sym} -130 -280 0 0 {name=p24 sig_type=std_logic lab=pll_clk}
C {devices/lab_pin.sym} -130 -260 0 0 {name=p25 sig_type=std_logic lab=clk_src}
C {devices/lab_pin.sym} -130 -240 0 0 {name=p26 sig_type=std_logic lab=en}
C {devices/lab_pin.sym} -130 -220 0 0 {name=p27 sig_type=std_logic lab=reset}
C {devices/lab_pin.sym} -130 -200 0 0 {name=p28 sig_type=std_logic lab=mode}
C {devices/lab_pin.sym} 130 -120 0 1 {name=p29 sig_type=std_logic lab=vdd_1v2}
C {devices/lab_pin.sym} 130 -100 0 1 {name=p30 sig_type=std_logic lab=GND}
C {lvds_tx_pex.sym} 600 -250 0 0 {name=xlvds}
N 130 -300 450 -300 {lab=core_p}
C {devices/lab_wire.sym} 290 -300 0 0 {name=w31 sig_type=std_logic lab=core_p}
N 130 -280 450 -280 {lab=core_n}
C {devices/lab_wire.sym} 290 -280 0 0 {name=w32 sig_type=std_logic lab=core_n}
C {devices/lab_pin.sym} 450 -260 0 0 {name=p33 sig_type=std_logic lab=iref_pd}
C {devices/lab_pin.sym} 450 -240 0 0 {name=p34 sig_type=std_logic lab=iref_drv}
C {devices/lab_pin.sym} 450 -220 0 0 {name=p35 sig_type=std_logic lab=vref}
C {devices/lab_pin.sym} 750 -190 0 1 {name=p36 sig_type=std_logic lab=vdd_3v3}
C {devices/lab_pin.sym} 750 -170 0 1 {name=p37 sig_type=std_logic lab=GND}
C {res.sym} 1000 -250 0 0 {name=Rload_p value=49.9}
C {res.sym} 1000 -160 0 0 {name=Rload_n value=49.9}
N 750 -280 1000 -280 {lab=out_p}
C {devices/lab_wire.sym} 850 -280 0 0 {name=w38 sig_type=std_logic lab=out_p}
N 1000 -220 1000 -190 {lab=vos}
N 1000 -205 1080 -205 {lab=vos}
C {devices/lab_wire.sym} 1080 -205 0 0 {name=w39 sig_type=std_logic lab=vos}
N 750 -260 900 -260 {lab=out_n}
N 900 -260 900 -130 {lab=out_n}
N 900 -130 1000 -130 {lab=out_n}
C {devices/lab_wire.sym} 900 -180 0 0 {name=w40 sig_type=std_logic lab=out_n}
T {100 ohm termination,
mid-point = Vos} 1040 -110 0 0 0.3 0.3 {}
B 2 1400 -1350 3200 -980 {flags=graph
y1=0.9
y2=1.6
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
node="out_p
out_n
vos"
color="4 5 8"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 1400 -920 3200 -550 {flags=graph
y1=-0.5
y2=0.5
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
node="vod"
color="7"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 1400 -490 3200 -120 {flags=graph
y1=-0.2
y2=1.4
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
node="core_p
core_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 1400 -60 3200 310 {flags=graph
y1=-0.2
y2=3.5
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
node="xlvds.in_p
xlvds.in_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
T {LVDS outputs and Vos} 3250 -1200 0 0 0.3 0.3 {}
T {Vod = out_p - out_n} 3250 -770 0 0 0.3 0.3 {}
T {pattern -> driver (1.2 V)} 3250 -340 0 0 0.3 0.3 {}
T {pre-driver -> H-bridge (3.3 V)} 3250 90 0 0 0.3 0.3 {}
C {launcher.sym} 1400 -1480 0 0 {name=h_sim
descr="Simulate"
tclcommand="
set_sim_defaults
file mkdir $netlist_dir
xschem netlist
set _cwd [pwd]
cd $netlist_dir
simulate
cd $_cwd
"}
C {launcher.sym} 1400 -1440 0 0 {name=h_waves
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/sg13cmos5l_chipalooza_analog_project_tb_lvds_postlayout.raw tran"
}
C {devices/code_shown.sym} -1700 750 0 0 {name=NGSPICE
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
write sg13cmos5l_chipalooza_analog_project_tb_lvds_postlayout.raw
.endc
"}
