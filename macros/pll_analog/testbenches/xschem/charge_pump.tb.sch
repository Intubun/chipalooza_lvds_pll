v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Charge-pump current and matching testbench.
UP is asserted from 10-20 ns, DOWN from 30-40 ns, and both from 50-60 ns.} -330 -290 0 0 0.3 0.3 {}
B 2 260 -220 900 220 {flags=graph
y1=-1.2e-05
y2=1.2e-05
ypos1=0
ypos2=2
divy=6
subdivy=1
unity=1
x1=0
x2=7e-08
divx=7
subdivx=1
node="i(VCTRL_CLAMP)"
color="4"
dataset=-1
unitx=1
logx=0
logy=0}
C {charge_pump.sym} 0 0 0 0 {name=x_cp}
C {lab_pin.sym} -80 -30 0 0 {name=p_up sig_type=std_logic lab=UP}
C {lab_pin.sym} -80 10 0 0 {name=p_down sig_type=std_logic lab=DOWN}
C {lab_pin.sym} -80 40 0 0 {name=p_iref sig_type=std_logic lab=IREF}
C {lab_pin.sym} 80 0 0 1 {name=p_vctrl sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} -20 -80 1 0 {name=p_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 20 80 0 0 {name=l_vss lab=0}
C {vsource.sym} -260 -20 0 0 {name=VUP value="PWL(0 0 9.9n 0 10n 1.2 20n 1.2 20.1n 0 49.9n 0 50n 1.2 60n 1.2 60.1n 0)" savecurrent=false}
C {lab_pin.sym} -260 -50 1 0 {name=p_up_src sig_type=std_logic lab=UP}
C {gnd.sym} -260 10 0 0 {name=l_up_src lab=0}
C {vsource.sym} -170 -20 0 0 {name=VDOWN value="PWL(0 0 29.9n 0 30n 1.2 40n 1.2 40.1n 0 49.9n 0 50n 1.2 60n 1.2 60.1n 0)" savecurrent=false}
C {lab_pin.sym} -170 -50 1 0 {name=p_down_src sig_type=std_logic lab=DOWN}
C {gnd.sym} -170 10 0 0 {name=l_down_src lab=0}
C {isource.sym} -170 120 0 0 {name=IREF_SRC value=-2u}
C {lab_pin.sym} -170 90 1 0 {name=p_iref_src sig_type=std_logic lab=IREF}
C {gnd.sym} -170 150 0 0 {name=l_iref_src lab=0}
C {vsource.sym} -260 120 0 0 {name=VDD_SRC value=1.2 savecurrent=false}
C {lab_pin.sym} -260 90 1 0 {name=p_vdd_src sig_type=std_logic lab=VDD}
C {gnd.sym} -260 150 0 0 {name=l_vdd_src lab=0}
C {vsource.sym} 150 50 0 0 {name=VCTRL_CLAMP value=0.7 savecurrent=true}
C {lab_pin.sym} 150 20 1 0 {name=p_vctrl_clamp sig_type=std_logic lab=VCTRL}
C {gnd.sym} 150 80 0 0 {name=l_vctrl_clamp lab=0}
C {simulator_commands_shown.sym} -330 200 0 0 {name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOSlv.lib mos_tt
"}
C {simulator_commands_shown.sym} -330 300 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.control
save all
tran 2p 70n
meas tran i_up avg i(VCTRL_CLAMP) from=12n to=18n
meas tran i_down avg i(VCTRL_CLAMP) from=32n to=38n
meas tran i_both avg i(VCTRL_CLAMP) from=52n to=58n
write charge_pump.tb.raw
.endc
"}
C {launcher.sym} -20 230 0 0 {name=h_simulate
descr=SimulateNGSPICE
tclcommand="
set_sim_defaults
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}
set sim(spice,default) 0
file mkdir $netlist_dir
xschem netlist
simulate
"}
C {launcher.sym} -20 270 0 0 {name=h_waves
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/charge_pump.tb.raw tran"
}
