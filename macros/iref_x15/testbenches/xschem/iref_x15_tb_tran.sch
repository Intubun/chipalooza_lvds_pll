v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 400 -500 1200 -100 {flags=graph
y1=0
y2=4e-05
ypos1=0
ypos2=2
divy=4
subdivy=1
unity=1
x1=0
x2=3.3
divx=6
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="\\"I(IREF_OUT); i(vload)\\""
color=4
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
rawfile=$netlist_dir/iref_x15_tb_tran.raw
sim_type=dc
autoload=1}
T {iref_x15 bench - the 1:15 bias pre-mirror on its own.

2 uA is pushed into IREF_IN, as the chip's ibias pin delivers it.  IREF_OUT
sources into Vload, a 0 V-drop ammeter held at a fixed voltage: 0.8 V is about
where the diode it feeds in lvds_tx sits (Mref in the pre-driver, M9 in the
driver), and the dc sweep of Vload from 0 to 3.3 V is the output characteristic,
i.e. how far the output may rise before the current falls off.

Printed: iout (at 0.8 V), ratio = iout / 2 uA, and vcomp, the highest output
voltage at which the current is still within 2 % of its value at 0.8 V.
Corner and temperature are in the two blocks below.} -560 -880 0 0 0.35 0.35 {}
N -200 30 -200 0 {lab=in}
N -200 0 -80 0 {lab=in}
N 80 0 200 0 {lab=out}
N 200 0 200 30 {lab=out}
N -20 -100 -20 -80 {lab=VDD}
N 20 80 20 110 {lab=0}
N -200 90 -200 110 {lab=0}
N 200 90 200 110 {lab=0}
N -320 10 -320 30 {lab=VDD}
N -320 90 -320 110 {lab=0}
C {iref_x15.sym} 0 0 0 0 {name=x1}
C {isource.sym} -200 60 0 0 {name=Iin value=-2u}
C {vsource.sym} 200 60 0 0 {name=Vload value=0.8 savecurrent=true}
C {vsource.sym} -320 60 0 0 {name=Vsup value=3.3 savecurrent=false}
C {vdd.sym} -20 -100 0 0 {name=l1 lab=VDD}
C {vdd.sym} -320 10 0 0 {name=l2 lab=VDD}
C {gnd.sym} 20 110 0 0 {name=l3 lab=0}
C {gnd.sym} -200 110 0 0 {name=l4 lab=0}
C {gnd.sym} 200 110 0 0 {name=l5 lab=0}
C {gnd.sym} -320 110 0 0 {name=l6 lab=0}
C {lab_pin.sym} -140 0 0 0 {name=p1 sig_type=std_logic lab=in}
C {lab_pin.sym} 140 0 0 1 {name=p2 sig_type=std_logic lab=out}
C {simulator_commands_shown.sym} -560 200 0 0 {
name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOShv.lib mos_tt
"
      }
C {simulator_commands_shown.sym} -160 200 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.control
save all
op
let iout = i(vload)
let ratio = iout / 2e-6
print iout ratio
dc Vload 0 3.3 0.01
meas dc iout08 FIND i(vload) AT=0.8
let lim = 0.98 * iout08
meas dc vcomp WHEN i(vload)=$&lim FALL=LAST
write iref_x15_tb_tran.raw
.endc
"}
C {launcher.sym} 460 -620 0 0 {name=h1
descr=SimulateNGSPICE
tclcommand="
set_sim_defaults
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}
set sim(spice,default) 0
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save
xschem netlist
simulate
"}
C {launcher.sym} 460 -580 0 0 {name=h2
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/iref_x15_tb_tran.raw dc"
}
