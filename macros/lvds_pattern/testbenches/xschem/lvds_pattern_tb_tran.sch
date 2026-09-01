v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {lvds_pattern transient bench.

  0...2 ns     reset high, clock stopped
  3 ns         en high, clock passthrough of pll_clk at 1 GHz
  12 ns        mode high, PRBS-7 at 1 Gb/s
  150...155 ns en low, the clock gate stops the pattern
  160 ns       clk_src low, the 250 MHz reference takes over

scripts/check_timing.py re-runs the polynomial over the exported
data and counts the bits that do not match.} -1500 -1500 0 0 0.45 0.45 {}
N 150 -1060 150 -1030 {lab=VDD}
C {devices/lab_wire.sym} 150 -1060 0 0 {name=lv_VDD sig_type=std_logic lab=VDD}
C {devices/vsource.sym} 150 -1000 0 0 {name=VVDD value="1.2"}
N 150 -970 150 -940 {lab=GND}
C {devices/gnd.sym} 150 -940 0 0 {name=lg_VDD lab=GND}
L 3 -30 -1120 330 -1120 {}
L 3 330 -1120 330 -880 {}
L 3 -30 -880 330 -880 {}
L 3 -30 -1120 -30 -880 {}
T {supply} -30 -1175 0 0 0.4 0.4 {}
N 150 -740 150 -710 {lab=ref_clk}
C {devices/lab_wire.sym} 150 -740 0 0 {name=lv_ref_clk sig_type=std_logic lab=ref_clk}
C {devices/vsource.sym} 150 -680 0 0 {name=Vref_clk value="PULSE(0 1.2 0 50p 50p 1.9n 4n)"}
N 150 -650 150 -620 {lab=GND}
C {devices/gnd.sym} 150 -620 0 0 {name=lg_ref_clk lab=GND}
N 150 -540 150 -510 {lab=pll_clk}
C {devices/lab_wire.sym} 150 -540 0 0 {name=lv_pll_clk sig_type=std_logic lab=pll_clk}
C {devices/vsource.sym} 150 -480 0 0 {name=Vpll_clk value="PULSE(0 1.2 0 30p 30p 470p 1n)"}
N 150 -450 150 -420 {lab=GND}
C {devices/gnd.sym} 150 -420 0 0 {name=lg_pll_clk lab=GND}
L 3 -30 -800 330 -800 {}
L 3 330 -800 330 -360 {}
L 3 -30 -360 330 -360 {}
L 3 -30 -800 -30 -360 {}
T {clocks} -30 -855 0 0 0.4 0.4 {}
N 150 -220 150 -190 {lab=clk_src}
C {devices/lab_wire.sym} 150 -220 0 0 {name=lv_clk_src sig_type=std_logic lab=clk_src}
C {devices/vsource.sym} 150 -160 0 0 {name=Vclk_src value="PWL(0 1.2 160n 1.2 160.1n 0)"}
N 150 -130 150 -100 {lab=GND}
C {devices/gnd.sym} 150 -100 0 0 {name=lg_clk_src lab=GND}
N 150 -20 150 10 {lab=en}
C {devices/lab_wire.sym} 150 -20 0 0 {name=lv_en sig_type=std_logic lab=en}
C {devices/vsource.sym} 150 40 0 0 {name=Ven value="PWL(0 0 3n 0 3.1n 1.2 150n 1.2 150.1n 0 155n 0 155.1n 1.2)"}
N 150 70 150 100 {lab=GND}
C {devices/gnd.sym} 150 100 0 0 {name=lg_en lab=GND}
N 150 180 150 210 {lab=reset}
C {devices/lab_wire.sym} 150 180 0 0 {name=lv_reset sig_type=std_logic lab=reset}
C {devices/vsource.sym} 150 240 0 0 {name=Vreset value="PWL(0 1.2 2n 1.2 2.1n 0)"}
N 150 270 150 300 {lab=GND}
C {devices/gnd.sym} 150 300 0 0 {name=lg_reset lab=GND}
N 150 380 150 410 {lab=mode}
C {devices/lab_wire.sym} 150 380 0 0 {name=lv_mode sig_type=std_logic lab=mode}
C {devices/vsource.sym} 150 440 0 0 {name=Vmode value="PWL(0 0 12n 0 12.1n 1.2)"}
N 150 470 150 500 {lab=GND}
C {devices/gnd.sym} 150 500 0 0 {name=lg_mode lab=GND}
L 3 -30 -280 330 -280 {}
L 3 330 -280 330 560 {}
L 3 -30 560 330 560 {}
L 3 -30 -280 -30 560 {}
T {control} -30 -335 0 0 0.4 0.4 {}
N 530 -100 590 -100 {lab=ref_clk}
C {devices/lab_wire.sym} 530 -100 0 0 {name=lx_ref_clk sig_type=std_logic lab=ref_clk}
N 530 -80 590 -80 {lab=pll_clk}
C {devices/lab_wire.sym} 530 -80 0 0 {name=lx_pll_clk sig_type=std_logic lab=pll_clk}
N 530 -60 590 -60 {lab=clk_src}
C {devices/lab_wire.sym} 530 -60 0 0 {name=lx_clk_src sig_type=std_logic lab=clk_src}
N 530 -40 590 -40 {lab=en}
C {devices/lab_wire.sym} 530 -40 0 0 {name=lx_en sig_type=std_logic lab=en}
N 530 -20 590 -20 {lab=reset}
C {devices/lab_wire.sym} 530 -20 0 0 {name=lx_reset sig_type=std_logic lab=reset}
N 530 0 590 0 {lab=mode}
C {devices/lab_wire.sym} 530 0 0 0 {name=lx_mode sig_type=std_logic lab=mode}
N 810 -100 870 -100 {lab=D_p}
C {devices/lab_wire.sym} 870 -100 0 0 {name=lx_D_p sig_type=std_logic lab=D_p}
N 810 -80 870 -80 {lab=D_n}
C {devices/lab_wire.sym} 870 -80 0 0 {name=lx_D_n sig_type=std_logic lab=D_n}
N 810 80 870 80 {lab=VDD}
C {devices/lab_wire.sym} 870 80 0 0 {name=lx_VDD sig_type=std_logic lab=VDD}
N 810 100 870 100 {lab=0}
C {devices/gnd.sym} 870 100 3 0 {name=lg_vss lab=GND}
C {lvds_pattern.sym} 700 0 0 0 {name=x1}
N 1150 -360 1150 -330 {lab=D_p}
C {devices/lab_wire.sym} 1150 -360 0 0 {name=lc_D_p sig_type=std_logic lab=D_p}
C {capa.sym} 1150 -300 0 0 {name=CD_p m=1 value=170f}
N 1150 -270 1150 -240 {lab=GND}
C {devices/gnd.sym} 1150 -240 0 0 {name=lgc_D_p lab=GND}
N 1150 -160 1150 -130 {lab=D_n}
C {devices/lab_wire.sym} 1150 -160 0 0 {name=lc_D_n sig_type=std_logic lab=D_n}
C {capa.sym} 1150 -100 0 0 {name=CD_n m=1 value=170f}
N 1150 -70 1150 -40 {lab=GND}
C {devices/gnd.sym} 1150 -40 0 0 {name=lgc_D_n lab=GND}
C {launcher.sym} 1700 -1750 0 0 {name=h_sim
descr="Simulate"
tclcommand="
set_sim_defaults
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save
xschem netlist
simulate
"}
C {launcher.sym} 1700 -1710 0 0 {name=h_waves
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/lvds_pattern_tb_tran.raw tran"
}
C {launcher.sym} 1700 -1670 0 0 {name=h_check
descr="Check PRBS + timing"
tclcommand="exec python3 [file dirname [xschem get current_dirname]]/../../scripts/check_timing.py &"
}
B 2 1700 -1550 3300 -1150 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2e-08
x2=2.6e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.gclk_b"
color="4"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 1700 -1050 3300 -650 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2e-08
x2=2.6e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="D_p
D_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 1700 -550 3300 -150 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2e-08
x2=2.6e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.s6
x1.fp
x1.fn"
color="7 4 5"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
C {devices/code_shown.sym} -1500 -800 0 0 {name=NGSPICE
only_toplevel=true
value="
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.lib cornerMOSlv.lib mos_tt
.temp 27
.options savecurrents klu reltol=1e-3
.control
save D_p D_n x1.gclk_b x1.s6 x1.s6_n x1.fp x1.fn mode en reset
tran 5p 200n
write @schname\\\\.raw

* the pair has to be complementary at every instant
let dsum = v(D_p)+v(D_n)
meas tran dsum_min MIN dsum from=20n to=140n
meas tran dsum_max MAX dsum from=20n to=140n

* D_p rising against D_n falling on the same bit: the skew the pre-driver sees,
* budget about 40 ps (docs/predriver-findings.md)
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
"}
