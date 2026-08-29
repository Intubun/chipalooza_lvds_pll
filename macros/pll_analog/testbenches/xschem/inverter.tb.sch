v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Current-starved inverter transient testbench.

VBP=0.3 V and VBN=0.9 V enable both current-starving devices while
leaving room to adjust their pull-up and pull-down currents independently.} -300 -320 0 0 0.3 0.3 {}
B 2 320 -220 1020 180 {flags=graph
y1=-0.1
y2=1.3
ypos1=0
ypos2=2
divy=7
subdivy=1
unity=1
x1=0
x2=5e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="VIN
VOUT"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1}
N 70 0 140 0 {lab=VOUT}
N 140 0 140 20 {lab=VOUT}
C {inverter.sym} 0 0 0 0 {name=x1}
C {lab_pin.sym} -70 0 0 0 {name=p_VIN sig_type=std_logic lab=VIN}
C {lab_pin.sym} 70 0 2 0 {name=p_VOUT sig_type=std_logic lab=VOUT}
C {lab_pin.sym} -20 -70 1 0 {name=p_VBP sig_type=std_logic lab=VBP}
C {lab_pin.sym} 20 -70 1 0 {name=p_VDD sig_type=std_logic lab=VDD}
C {lab_pin.sym} -20 70 3 0 {name=p_VBN sig_type=std_logic lab=VBN}
C {gnd.sym} 20 70 0 0 {name=l_VSS lab=0}
C {vsource.sym} -240 50 0 0 {name=VIN_SRC value="PULSE(0 1.2 0.5n 20p 20p 1n 2n)" savecurrent=false}
C {lab_pin.sym} -240 20 1 0 {name=p_VIN_SRC sig_type=std_logic lab=VIN}
C {gnd.sym} -240 80 0 0 {name=l_VIN lab=0}
C {vsource.sym} -180 -180 0 0 {name=VDD_SRC value=1.2 savecurrent=false}
C {lab_pin.sym} -180 -210 1 0 {name=p_VDD_SRC sig_type=std_logic lab=VDD}
C {gnd.sym} -180 -150 0 0 {name=l_VDD lab=0}
C {vsource.sym} -60 -180 0 0 {name=VBP_SRC value=0.3 savecurrent=false}
C {lab_pin.sym} -60 -210 1 0 {name=p_VBP_SRC sig_type=std_logic lab=VBP}
C {gnd.sym} -60 -150 0 0 {name=l_VBP lab=0}
C {vsource.sym} 60 -180 0 0 {name=VBN_SRC value=0.9 savecurrent=false}
C {lab_pin.sym} 60 -210 1 0 {name=p_VBN_SRC sig_type=std_logic lab=VBN}
C {gnd.sym} 60 -150 0 0 {name=l_VBN lab=0}
C {capa.sym} 140 50 0 0 {name=CLOAD
m=1
value=1f
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 140 80 0 0 {name=l_CLOAD lab=0}
C {simulator_commands_shown.sym} -300 150 0 0 {name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOSlv.lib mos_tt
"}
C {simulator_commands_shown.sym} -300 280 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.control
save all
tran 0.5p 5n
meas tran vout_low avg v(VOUT) from=1n to=1.4n
meas tran vout_high avg v(VOUT) from=2n to=2.4n
write inverter.tb.raw
.endc
"}
C {launcher.sym} 20 210 0 0 {name=h_simulate
descr=SimulateNGSPICE
tclcommand="
set_sim_defaults
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}
set sim(spice,default) 0
file mkdir $netlist_dir
xschem netlist
simulate
"}
C {launcher.sym} 20 250 0 0 {name=h_waves
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/inverter.tb.raw tran"
}
