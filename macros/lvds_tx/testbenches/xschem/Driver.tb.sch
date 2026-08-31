v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 920 -1220 1720 -820 {flags=graph
y1=0.8
y2=1.6
ypos1=0
ypos2=2
divy=8
subdivy=1
unity=1
x1=4e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="out_p
out_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
x2=6e-09
hilight_wave=-1}
B 2 920 -800 1720 -400 {flags=graph
y1=-0.5
y2=0.5
ypos1=-0.5
ypos2=0.5
divy=5
subdivy=1
unity=1
x1=4e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Vod;out_p out_n -"
color=4
dataset=-1
unitx=1
logx=0
logy=0
x2=6e-09
hilight_wave=0
rawfile=$netlist_dir/Driver.tb.raw}
B 2 920 -380 1720 -60 {flags=graph
y1=1.1
y2=1.3
ypos1=1.1
ypos2=1.3
divy=4
subdivy=1
unity=1
x1=4e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Vos"
color=6
dataset=-1
unitx=1
logx=0
logy=0
x2=6e-09
hilight_wave=-1}
T {Driver transient testbench - clauses 4.1.4 and 4.1.5.

Load is the 49.9 + 49.9 ohm pair that 4.1.2 / 4.1.5 prescribe: 99.8 ohm total, which is
also the 4.1.4 test load, and the centre tap gives Vos directly.

Stimulus is 3.125 Gb/s (320 ps bit), 100 ps edges, alternating 1,0,1,0.

ONE TRAP, easy to get wrong and it does not error: ngspice PULSE holds v2 for pw
EXCLUDING the edges, so a 50 % duty cycle needs pw = bit - tedge = 220p, not 320p.
Getting it wrong skews the mark/space ratio and makes |Vt| and |Vt*| differ by
~17 mV for no physical reason.

The driver takes In_p / In_n and nothing else. It used to carry a second, delayed
input pair driving an auxiliary H-bridge -- the second tap of a 2-tap FIR
pre-emphasis -- and this testbench faked that tap with a second pulse pair.
Both are gone.

Xpadp / Xpadn are the ESD clamp and pad capacitance. They are not decoration: clause
4.1.5 sets a floor on the total output node capacitance and 4.1.4 Vring sets a ceiling.
See docs/pad-esd-budget.md.

For the full clause-by-clause verdict, corner sweeps, mismatch and the PRBS eye, run
compliance/run.sh - this schematic is the one to look at, that is the one to trust.} -460 -1180 0 0 0.4 0.4 {}
N 520 -200 540 -200 {lab=VDD}
N 540 -220 540 -200 {lab=VDD}
N 520 -140 540 -140 {lab=0}
N 540 -140 540 -120 {lab=0}
N 80 -160 220 -160 {lab=Iref}
N 160 -60 360 -60 {lab=0}
N 360 -60 360 -40 {lab=0}
N -460 -160 -460 -140 {lab=VDD}
N -460 -80 -460 -60 {lab=0}
N -160 -60 80 -60 {lab=0}
N -160 -80 -160 -60 {lab=0}
N -400 -80 -400 -60 {lab=0}
N -460 -60 -400 -60 {lab=0}
N -160 -180 -160 -140 {lab=#net1}
N -160 -180 220 -180 {lab=#net1}
N -400 -200 -400 -140 {lab=#net2}
N 160 -140 220 -140 {lab=Vref}
N 160 -80 160 -60 {lab=0}
N 80 -160 80 -140 {lab=Iref}
N 80 -80 80 -60 {lab=0}
N 80 -60 160 -60 {lab=0}
N -400 -60 -160 -60 {lab=0}
N -400 -200 220 -200 {lab=#net2}
N 820 -180 1500 -180 {lab=Out_p}
N 520 -160 580 -160 {lab=Out_n}
N 580 -160 580 -60 {lab=Out_n}
N 1120 -60 1500 -60 {lab=Out_n}
N 820 -290 820 -180 {lab=Out_p}
N 980 -310 980 -290 {lab=VDD}
N 980 -250 980 -230 {lab=0}
N 1120 -60 1120 30 {lab=Out_n}
N 1280 10 1280 30 {lab=VDD}
N 1280 70 1280 90 {lab=0}
N 520 -180 820 -180 {lab=Out_p}
N 580 -60 1120 -60 {lab=Out_n}
C {Driver.sym} 370 -170 0 0 {name=x1}
C {esdpad.sym} 900 -280 0 0 {name=Xpadp}
C {esdpad.sym} 1200 40 0 0 {name=Xpadn}
C {vdd.sym} 540 -220 0 0 {name=l1 lab=VDD}
C {gnd.sym} 540 -120 0 0 {name=l2 lab=0}
C {vdd.sym} 980 -310 0 0 {name=l6 lab=VDD}
C {gnd.sym} 980 -230 0 0 {name=l7 lab=0}
C {vdd.sym} 1280 10 0 0 {name=l8 lab=VDD}
C {gnd.sym} 1280 90 0 0 {name=l9 lab=0}
C {gnd.sym} 360 -40 0 0 {name=l10 lab=0}
C {res.sym} 1400 -150 0 0 {name=R1
value=49.9
footprint=1206
device=resistor
m=1}
C {res.sym} 1400 -90 0 0 {name=R2
value=49.9
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 1400 -120 0 0 {name=pv sig_type=std_logic lab=Vos}
C {isource.sym} 80 -110 0 0 {name=I0 value=-30u}
C {vdd.sym} -460 -160 0 0 {name=l3 lab=VDD}
C {vsource.sym} -160 -110 0 0 {name=V1 value="PULSE(0 3.3 0 100p 100p 220p 640p)" savecurrent=false}
C {vsource.sym} -400 -110 0 0 {name=V2 value="PULSE(3.3 0 0 100p 100p 220p 640p)" savecurrent=false}
C {vsource.sym} -460 -110 0 0 {name=V3 value=3.3 savecurrent=false}
C {vsource.sym} 160 -110 0 0 {name=V4 value=1.25 savecurrent=false}
C {lab_pin.sym} 160 -140 0 0 {name=p4 sig_type=std_logic lab=Vref}
C {lab_pin.sym} 700 -180 0 0 {name=p1 sig_type=std_logic lab=Out_p}
C {lab_pin.sym} 700 -60 0 0 {name=p2 sig_type=std_logic lab=Out_n}
C {lab_pin.sym} 80 -160 0 0 {name=p3 sig_type=std_logic lab=Iref}
C {simulator_commands_shown.sym} 20 -530 0 0 {
name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_mfringe.lib
"
      }
C {simulator_commands_shown.sym} 20 -390 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.control
save all
tran 0.5p 8n 0 0.5p
write Driver.tb.raw
.endc
"}
C {launcher.sym} 500 -640 0 0 {name=h4
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
C {launcher.sym} 500 -600 0 0 {name=h5
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/Driver.tb.raw tran"
}
