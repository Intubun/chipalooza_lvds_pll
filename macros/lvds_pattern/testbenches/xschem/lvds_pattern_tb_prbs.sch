v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1800 -1240 3400 -940 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=7.1974738e-08
x2=7.737024e-08
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
B 2 1800 -920 3400 -620 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=7.1974738e-08
x2=7.737024e-08
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
B 2 1800 -600 3400 -300 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=7.1974738e-08
x2=7.737024e-08
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
T {lvds_pattern PRBS-7 timing bench.

PRBS-7 from the first clock, 1 Gb/s, 160 ns - a full 127-bit period with
margin.  mode and clk_src are static, so nothing moves the data path timing
during the run.

scripts/check_timing.py reads the export and reports the bit rate, the
clock-to-output spread, the data valid window that follows from it, the
D_p / D_n skew, and it re-runs the polynomial sampling in the middle of that
window rather than at a fixed phase.} 170 -1460 0 0 0.45 0.45 {}
N 150 -1060 150 -1030 {lab=VDD}
N 150 -970 150 -940 {lab=GND}
N 150 -860 150 -830 {lab=ref_clk}
N 150 -770 150 -740 {lab=GND}
N 150 -660 150 -630 {lab=pll_clk}
N 150 -570 150 -540 {lab=GND}
N 150 -460 150 -430 {lab=clk_src}
N 150 -370 150 -340 {lab=GND}
N 150 -260 150 -230 {lab=en}
N 150 -170 150 -140 {lab=GND}
N 150 -60 150 -30 {lab=reset}
N 150 30 150 60 {lab=GND}
N 150 140 150 170 {lab=mode}
N 150 230 150 260 {lab=GND}
N 530 -100 590 -100 {lab=ref_clk}
N 530 -80 590 -80 {lab=pll_clk}
N 530 -60 590 -60 {lab=clk_src}
N 530 -40 590 -40 {lab=en}
N 530 -20 590 -20 {lab=reset}
N 530 0 590 0 {lab=mode}
N 810 -100 870 -100 {lab=D_p}
N 810 -80 870 -80 {lab=D_n}
N 810 80 870 80 {lab=VDD}
N 810 100 870 100 {lab=GND}
N 1000 -360 1000 -330 {lab=D_p}
N 1000 -270 1000 -240 {lab=GND}
N 1000 -160 1000 -130 {lab=D_n}
N 1000 -70 1000 -40 {lab=GND}
C {devices/lab_wire.sym} 150 -1060 0 0 {name=lv_VDD sig_type=std_logic lab=VDD}
C {devices/vsource.sym} 150 -1000 0 0 {name=VVDD value="1.2"}
C {devices/gnd.sym} 150 -940 0 0 {name=lg_VDD lab=GND}
C {devices/lab_wire.sym} 150 -860 0 0 {name=lv_ref_clk sig_type=std_logic lab=ref_clk}
C {devices/vsource.sym} 150 -800 0 0 {name=Vref_clk value="0"}
C {devices/gnd.sym} 150 -740 0 0 {name=lg_ref_clk lab=GND}
C {devices/lab_wire.sym} 150 -660 0 0 {name=lv_pll_clk sig_type=std_logic lab=pll_clk}
C {devices/vsource.sym} 150 -600 0 0 {name=Vpll_clk value="PULSE(0 1.2 0 30p 30p 470p 1n)"}
C {devices/gnd.sym} 150 -540 0 0 {name=lg_pll_clk lab=GND}
C {devices/lab_wire.sym} 150 -460 0 0 {name=lv_clk_src sig_type=std_logic lab=clk_src}
C {devices/vsource.sym} 150 -400 0 0 {name=Vclk_src value="1.2"}
C {devices/gnd.sym} 150 -340 0 0 {name=lg_clk_src lab=GND}
C {devices/lab_wire.sym} 150 -260 0 0 {name=lv_en sig_type=std_logic lab=en}
C {devices/vsource.sym} 150 -200 0 0 {name=Ven value="PWL(0 0 3n 0 3.1n 1.2)"}
C {devices/gnd.sym} 150 -140 0 0 {name=lg_en lab=GND}
C {devices/lab_wire.sym} 150 -60 0 0 {name=lv_reset sig_type=std_logic lab=reset}
C {devices/vsource.sym} 150 0 0 0 {name=Vreset value="PWL(0 1.2 2n 1.2 2.1n 0)"}
C {devices/gnd.sym} 150 60 0 0 {name=lg_reset lab=GND}
C {devices/lab_wire.sym} 150 140 0 0 {name=lv_mode sig_type=std_logic lab=mode}
C {devices/vsource.sym} 150 200 0 0 {name=Vmode value="1.2"}
C {devices/gnd.sym} 150 260 0 0 {name=lg_mode lab=GND}
C {devices/lab_wire.sym} 530 -100 0 0 {name=lx_ref_clk sig_type=std_logic lab=ref_clk}
C {devices/lab_wire.sym} 530 -80 0 0 {name=lx_pll_clk sig_type=std_logic lab=pll_clk}
C {devices/lab_wire.sym} 530 -60 0 0 {name=lx_clk_src sig_type=std_logic lab=clk_src}
C {devices/lab_wire.sym} 530 -40 0 0 {name=lx_en sig_type=std_logic lab=en}
C {devices/lab_wire.sym} 530 -20 0 0 {name=lx_reset sig_type=std_logic lab=reset}
C {devices/lab_wire.sym} 530 0 0 0 {name=lx_mode sig_type=std_logic lab=mode}
C {devices/lab_wire.sym} 870 -100 0 0 {name=lx_D_p sig_type=std_logic lab=D_p}
C {devices/lab_wire.sym} 870 -80 0 0 {name=lx_D_n sig_type=std_logic lab=D_n}
C {devices/lab_wire.sym} 870 80 0 0 {name=lx_VDD sig_type=std_logic lab=VDD}
C {devices/gnd.sym} 870 100 3 0 {name=lg_vss lab=GND}
C {lvds_pattern.sym} 700 0 0 0 {name=x1}
C {devices/lab_wire.sym} 1000 -360 0 0 {name=lc_D_p sig_type=std_logic lab=D_p}
C {capa.sym} 1000 -300 0 0 {name=CD_p m=1 value=170f}
C {devices/gnd.sym} 1000 -240 0 0 {name=lgc_D_p lab=GND}
C {devices/lab_wire.sym} 1000 -160 0 0 {name=lc_D_n sig_type=std_logic lab=D_n}
C {capa.sym} 1000 -100 0 0 {name=CD_n m=1 value=170f}
C {devices/gnd.sym} 1000 -40 0 0 {name=lgc_D_n lab=GND}
C {launcher.sym} 1800 -1320 0 0 {name=h_sim
descr="Simulate"
tclcommand="
set_sim_defaults
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save
xschem netlist
simulate
"}
C {launcher.sym} 1800 -1280 0 0 {name=h_waves
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/lvds_pattern_tb_prbs.raw tran"
}
C {launcher.sym} 1800 -1240 0 0 {name=h_check
descr="Check PRBS + timing"
tclcommand="exec python3 [file dirname [xschem get current_dirname]]/../../scripts/check_timing.py &"
}
C {devices/code_shown.sym} 1400 -1000 0 0 {name=NGSPICE
only_toplevel=true
value="
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.lib cornerMOSlv.lib mos_tt
.temp 27
.options savecurrents klu reltol=1e-3
.control
save D_p D_n x1.gclk_b x1.s6 x1.s6_n x1.fp x1.fn mode en reset
tran 2p 160n
write @schname\\\\.raw

* the pair has to be complementary at every instant
let dsum = v(D_p)+v(D_n)
meas tran dsum_min MIN dsum from=10n to=155n
meas tran dsum_max MAX dsum from=10n to=155n
print dsum_min dsum_max

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(D_p) v(D_n) v(x1.gclk_b)
.endc
"}
