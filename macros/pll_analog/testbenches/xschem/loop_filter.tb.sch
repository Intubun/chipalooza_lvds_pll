v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Loop-filter AC impedance and transient charge testbench.} -260 -240 0 0 0.3 0.3 {}
B 2 220 -190 820 170 {flags=graph
y1=0
y2=0.04
ypos1=0
ypos2=2
divy=4
subdivy=1
unity=1
x1=0
x2=5e-07
divx=5
subdivx=1
node="VCTRL"
color="4"
dataset=-1
unitx=1
logx=0
logy=0}
C {loop_filter.sym} 0 0 0 0 {name=x_filter}
C {lab_pin.sym} -70 0 0 0 {name=p_vctrl sig_type=std_logic lab=VCTRL}
C {gnd.sym} 0 70 0 0 {name=l_vss lab=0}
C {isource.sym} -150 50 0 0 {name=IPULSE value="PULSE(0 -2.5u 100n 1n 1n 100n 1u)"}
C {lab_pin.sym} -150 20 1 0 {name=p_isrc sig_type=std_logic lab=VCTRL}
C {gnd.sym} -150 80 0 0 {name=l_isrc lab=0}
C {res.sym} -80 100 0 0 {name=RLEAK
value=1G
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} -80 70 1 0 {name=p_rleak sig_type=std_logic lab=VCTRL}
C {gnd.sym} -80 130 0 0 {name=l_rleak lab=0}
C {simulator_commands_shown.sym} -260 140 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.control
save all
tran 20p 500n
meas tran vctrl_before avg v(VCTRL) from=80n to=90n
meas tran vctrl_peak max v(VCTRL) from=100n to=220n
write loop_filter.tb.raw
.endc
"}
C {launcher.sym} -40 180 0 0 {name=h_simulate
descr=SimulateNGSPICE
tclcommand="
set_sim_defaults
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}
set sim(spice,default) 0
file mkdir $netlist_dir
xschem netlist
simulate
"}
C {launcher.sym} -40 220 0 0 {name=h_waves
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/loop_filter.tb.raw tran"
}
