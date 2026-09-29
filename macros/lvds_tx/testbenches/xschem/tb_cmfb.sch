v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1600 -1220 2500 -860 {flags=graph
y1=1.24
y2=1.34
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2.5e-08
x2=1.5e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="vos
vref"
color="6 4"
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
rawfile=$netlist_dir/tb_cmfb.raw
sim_type=tran
autoload=1}
B 2 1600 -840 2500 -480 {flags=graph
y1=-30
y2=30
ypos1=0
ypos2=2
divy=6
subdivy=1
unity=1
x1=5
x2=10
divx=5
subdivx=8
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="\\"Vos/Vref dB; vos db20()\\""
color=6
dataset=-1
unitx=1
logx=1
logy=0
hilight_wave=-1
rawfile=$netlist_dir/tb_cmfb.raw
sim_type=ac
autoload=1}
B 2 1600 -460 2500 -100 {flags=graph
y1=2.00
y2=2.05
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2.5e-08
x2=1.5e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.cmfb
x1.cc_g"
color="4 7"
dataset=-1
unitx=1
logx=0
logy=0
hilight_wave=-1
rawfile=$netlist_dir/tb_cmfb.raw
sim_type=tran
autoload=1}
T {CMFB loop bench - the common-mode loop of the driver, on its own.

The inputs stand still (In_p low, In_n high).  Vref steps from 1.25 to 1.30 V at
30 ns (top graph) and carries AC 1, so the ac run gives the closed-loop response
Vos/Vref (middle).  Bottom: cmfb, the error amplifier output, and cc_g, the gate of
Cc behind Rc.  Both runs go into tb_cmfb.raw, the ac one appended.

Set to the corner where the loop has the least margin: ff, -40 C, Va 3.63 V, res_wcs.
For another one change .param vdd, the .lib sections and temp below; the graph
y ranges are set for this corner.

Compensation: Cc 50u x 5u (10 fingers) from cc_g to Va, Rc rppd 1u x 6u (1.6 kOhm)
in series between cmfb and cc_g.  Rc puts a zero next to the unity-gain frequency;
rppd rather than rhigh because rhigh drifts by 2x over corners and temperature, and
above ~3 kOhm the zero stops helping.

Expected here: overshoot 54 %, settled to +-2 mV 10 ns after the step, then flat;
Vos/Vref peaks at +5.8 dB near 140 MHz.  Loop gain (broken at the gate of M2, not
measurable from this bench): 32 deg phase margin in this corner, 32 deg worst over
all 81 conditions (27 CACE x res bcs/typ/wcs).
The previous compensation (Cc 40u x 5u straight on cmfb, no Rc) oscillates in this
corner: the ringing grows to 150 mV pp by 150 ns and Vos/Vref peaks at +28 dB
near 105 MHz.} -460 -1300 0 0 0.4 0.4 {}
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
C {vsource.sym} -160 -110 0 0 {name=V1 value=\{vdd\} savecurrent=false}
C {vsource.sym} -400 -110 0 0 {name=V2 value=0 savecurrent=false}
C {vsource.sym} -460 -110 0 0 {name=V3 value=\{vdd\} savecurrent=false}
C {vsource.sym} 160 -110 0 0 {name=V4 value="DC 1.25 AC 1 PULSE(1.25 1.30 30n 50p 50p 1u 2u)" savecurrent=false}
C {lab_pin.sym} 160 -140 0 0 {name=p4 sig_type=std_logic lab=Vref}
C {lab_pin.sym} 700 -180 0 0 {name=p1 sig_type=std_logic lab=Out_p}
C {lab_pin.sym} 700 -60 0 0 {name=p2 sig_type=std_logic lab=Out_n}
C {lab_pin.sym} 80 -160 0 0 {name=p3 sig_type=std_logic lab=Iref}
C {simulator_commands_shown.sym} -460 180 0 0 {
name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.param vdd=3.63
.lib cornerMOSlv.lib mos_ff
.lib cornerMOShv.lib mos_ff
.lib cornerRES.lib res_wcs
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
"
      }
C {simulator_commands_shown.sym} 0 180 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=-40
.control
save all
tran 20p 150n 0 20p
meas tran vos_before AVG v(Vos) from=25n to=30n
meas tran vos_after AVG v(Vos) from=140n to=150n
meas tran vos_max MAX v(Vos) from=30n to=150n
meas tran vos_pp_late PP v(Vos) from=100n to=150n
write tb_cmfb.raw
set appendwrite
ac dec 50 100k 10g
meas ac peak_db MAX vdb(Vos)
write tb_cmfb.raw
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
tclcommand="xschem raw_clear; xschem raw_read $netlist_dir/tb_cmfb.raw tran; xschem raw_read $netlist_dir/tb_cmfb.raw ac; xschem redraw"
}
