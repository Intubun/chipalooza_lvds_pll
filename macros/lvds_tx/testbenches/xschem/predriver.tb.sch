v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1700 -1500 2500 -1160 {flags=graph
y1=-0.2
y2=3.5
ypos1=0
ypos2=2
divy=6
subdivy=1
unity=1
x1=3e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="In_p
In_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
x2=4e-09
hilight_wave=-1}
B 2 1700 -1140 2500 -800 {flags=graph
y1=0.8
y2=1.6
ypos1=0
ypos2=2
divy=8
subdivy=1
unity=1
x1=3e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Out_p
Out_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
x2=4e-09
hilight_wave=-1
rawfile=$netlist_dir/predriver.tb.raw}
B 2 1700 -780 2500 -440 {flags=graph
y1=-0.5
y2=0.5
ypos1=-0.5
ypos2=0.5
divy=5
subdivy=1
unity=1
x1=3e-09
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Vod;Out_p Out_n -"
color=4
dataset=-1
unitx=1
logx=0
logy=0
x2=4e-09
hilight_wave=0}
B 2 1700 -420 2500 -100 {flags=graph
y1=1.1
y2=1.3
ypos1=1.1
ypos2=1.3
divy=4
subdivy=1
unity=1
x1=3e-09
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
x2=4e-09
hilight_wave=-1}
T {Pre-driver testbench - the whole gate-drive path, core data in to LVDS out.

The stimulus is the CORE domain: 0..1.2 V, not 0..3.3 V.  Bridging those is the
pre-driver's entire job, so any testbench that starts at 3.3 V is testing nothing.

The load is the real Driver.sym, not a lumped capacitor.  Two reasons: the driver's
gate capacitance is nonlinear over the swing, and while the driver switches it pushes
charge back into In_p / In_n through Cgd.  Both are first-order here.

WHAT TO LOOK AT, in order:

 1. In_p vs In_n (top graph).  The number that matters is not the edge rate, it is the
    SKEW between them.  Measured on the driver: Vos p-p is 81 mV at zero skew and
    166 mV at 20 ps, so clause 4.1.5's 150 mV limit lands at about +-7 ps.  Vos is
    flat from 10 to 100 ps of edge rate, so slew is NOT the binding spec - which is
    what docs/compliance-plan.md section 5 assumed.  See docs/predriver-findings.md.
 2. Vos (bottom graph) against 150 mV peak-to-peak.
 3. Out_p / Out_n and Vod, to confirm the driver still does what the compliance
    suite says it does when a real pre-driver drives it.

D_p / D_n is the whole core-domain interface.  There used to be a second pair,
D_p_d / D_n_d, the previous bit one period late, which the pre-driver carried on a
scaled second slice and the driver turned into a 2-tap FIR pre-emphasis.  All of it
is gone: the tap put an 11 mV settling tail on every de-emphasised bit and bought
nothing measurable on a bench-length channel.

ngspice PULSE holds v2 for pw EXCLUDING the edges, so a 50 % duty cycle needs
pw = bit - tedge = 290p, not 320p.

Iref and Iref_pd are SEPARATE nodes with one 30 uA source each.  Tying them
together and feeding 60 uA does not give each block 30 uA - the two reference
diodes sit in parallel and split by width (M9 is 0.8 um, Mref is 8 um), so the
driver would get about a tenth of its bias and |Vod| would land at 110 mV while
every pre-driver waveform still looked perfect.

STATUS: clean PRBS7 eye over the full PVT set at 1 Gb/s and 2 Gb/s - 597..651 mV
high, >=0.934 UI wide, worst-case |Vod| 292..321 mV against the 247 mV floor.
It runs out between 2 and 3.125 Gb/s: at 3.125 Gb/s the hot corners fail, and not
through skew but through bandwidth - at ss/125C the output only reaches 2.1 V of
3.3 V.  Enlarging the output chain makes that WORSE; the level shifter is the
bottleneck.  Vos p-p is 288..464 mV, over 4.1.5's 150 mV, which is a declared
deviation - see the skew note above and docs/predriver-findings.md section 1.

This schematic is set up for 3.125 Gb/s, i.e. the failing case.  For the rates
the PLL can actually feed, set the four sources to 500p or 1000p bits.

Sweep before believing anything here:
  docker exec iic-osic-tools_xserver bash -lc \\
    /foss/designs/chipalooza_lvds_pll/macros/lvds_tx/predriver/matrix.sh} -900 -1500 0 0 0.4 0.4 {}
N -900 -180 -900 -130 {lab=VDD}
N -900 -70 -900 -20 {lab=0}
N -700 -180 -700 -130 {lab=D_p}
N -700 -70 -700 -20 {lab=0}
N -600 -180 -600 -130 {lab=D_n}
N -600 -70 -600 -20 {lab=0}
N -350 120 -350 170 {lab=Iref}
N -350 230 -350 270 {lab=0}
N -450 120 -450 170 {lab=Iref_pd}
N -450 230 -450 270 {lab=0}
N -250 120 -250 170 {lab=Vref}
N -250 230 -250 270 {lab=0}
N -200 -50 -150 -50 {lab=D_p}
N -200 -30 -150 -30 {lab=D_n}
N -200 30 -150 30 {lab=Iref_pd}
N 150 -70 250 -70 {lab=VDD}
N 150 30 300 30 {lab=0}
N 300 30 300 120 {lab=0}
N 150 -50 200 -50 {lab=In_p}
N 150 -30 200 -30 {lab=In_n}
N 400 -30 450 -30 {lab=In_p}
N 400 -10 450 -10 {lab=In_n}
N 400 10 450 10 {lab=Iref}
N 400 30 450 30 {lab=Vref}
N 750 -30 800 -30 {lab=VDD}
N 750 30 810 30 {lab=0}
N 810 30 810 120 {lab=0}
N 750 -10 900 -10 {lab=Out_p}
N 900 -210 900 -10 {lab=Out_p}
N 900 -210 1020 -210 {lab=Out_p}
N 900 -260 1500 -260 {lab=Out_p}
N 1500 -260 1500 -130 {lab=Out_p}
N 750 10 860 10 {lab=Out_n}
N 860 190 860 300 {lab=Out_n}
N 860 190 1020 190 {lab=Out_n}
N 860 300 1500 300 {lab=Out_n}
N 1500 30 1500 300 {lab=Out_n}
N 1500 -70 1500 -30 {lab=Vos}
N 1180 -210 1240 -210 {lab=VDD}
N 1180 -170 1240 -170 {lab=0}
N 1240 -170 1240 -120 {lab=0}
N 1180 190 1240 190 {lab=VDD}
N 1180 230 1240 230 {lab=0}
N 1240 230 1240 280 {lab=0}
N 900 -260 900 -210 {lab=Out_p}
N 860 10 860 190 {lab=Out_n}
C {predriver.sym} 0 0 0 0 {name=Xpd}
C {Driver.sym} 600 0 0 0 {name=Xdrv}
C {esdpad.sym} 1100 -200 0 0 {name=Xpadp}
C {esdpad.sym} 1100 200 0 0 {name=Xpadn}
C {vsource.sym} -900 -100 0 0 {name=V0 value=3.3 savecurrent=false}
C {vsource.sym} -700 -100 0 0 {name=V1 value="PULSE(0 1.2 0 30p 30p 290p 640p)" savecurrent=false}
C {vsource.sym} -600 -100 0 0 {name=V2 value="PULSE(1.2 0 0 30p 30p 290p 640p)" savecurrent=false}
C {vsource.sym} -250 200 0 0 {name=V5 value=1.2 savecurrent=false}
C {isource.sym} -350 200 0 0 {name=I0 value=-30u}
C {isource.sym} -450 200 0 0 {name=I1 value=-30u}
C {lab_pin.sym} -450 120 0 0 {name=s25 sig_type=std_logic lab=Iref_pd}
C {gnd.sym} -450 270 0 0 {name=l16 lab=0}
C {res.sym} 1500 -100 0 0 {name=Rp
value=49.9
footprint=1206
device=resistor
m=1}
C {res.sym} 1500 0 0 0 {name=Rn
value=49.9
footprint=1206
device=resistor
m=1}
C {vdd.sym} -900 -180 0 0 {name=l0 lab=VDD}
C {gnd.sym} -900 -20 0 0 {name=l1 lab=0}
C {lab_pin.sym} -700 -180 0 0 {name=s1 sig_type=std_logic lab=D_p}
C {gnd.sym} -700 -20 0 0 {name=l2 lab=0}
C {lab_pin.sym} -600 -180 0 0 {name=s2 sig_type=std_logic lab=D_n}
C {gnd.sym} -600 -20 0 0 {name=l3 lab=0}
C {lab_pin.sym} -350 120 0 0 {name=s5 sig_type=std_logic lab=Iref}
C {gnd.sym} -350 270 0 0 {name=l6 lab=0}
C {lab_pin.sym} -250 120 0 0 {name=s6 sig_type=std_logic lab=Vref}
C {gnd.sym} -250 270 0 0 {name=l7 lab=0}
C {lab_pin.sym} -200 -50 0 0 {name=s7 sig_type=std_logic lab=D_p}
C {lab_pin.sym} -200 -30 0 0 {name=s8 sig_type=std_logic lab=D_n}
C {lab_pin.sym} -200 30 0 0 {name=s11 sig_type=std_logic lab=Iref_pd}
C {vdd.sym} 250 -70 0 0 {name=l8 lab=VDD}
C {gnd.sym} 300 120 0 0 {name=l9 lab=0}
C {lab_pin.sym} 200 -50 0 0 {name=s12 sig_type=std_logic lab=In_p}
C {lab_pin.sym} 200 -30 0 0 {name=s13 sig_type=std_logic lab=In_n}
C {lab_pin.sym} 400 -30 0 0 {name=s16 sig_type=std_logic lab=In_p}
C {lab_pin.sym} 400 -10 0 0 {name=s17 sig_type=std_logic lab=In_n}
C {lab_pin.sym} 400 10 0 0 {name=s18 sig_type=std_logic lab=Iref}
C {lab_pin.sym} 400 30 0 0 {name=s19 sig_type=std_logic lab=Vref}
C {vdd.sym} 800 -30 0 0 {name=l10 lab=VDD}
C {gnd.sym} 810 120 0 0 {name=l11 lab=0}
C {vdd.sym} 1240 -210 0 0 {name=l12 lab=VDD}
C {gnd.sym} 1240 -120 0 0 {name=l13 lab=0}
C {vdd.sym} 1240 190 0 0 {name=l14 lab=VDD}
C {gnd.sym} 1240 280 0 0 {name=l15 lab=0}
C {lab_pin.sym} 1500 -50 0 0 {name=s22 sig_type=std_logic lab=Vos}
C {lab_pin.sym} 1000 -260 0 0 {name=s23 sig_type=std_logic lab=Out_p}
C {lab_pin.sym} 1000 300 0 0 {name=s24 sig_type=std_logic lab=Out_n}
C {simulator_commands_shown.sym} -900 -700 0 0 {
name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
"
      }
C {simulator_commands_shown.sym} -900 -540 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.control
save all
tran 0.2p 4.5n 0 0.2p
write predriver.tb.raw
.endc
"}
C {launcher.sym} -400 -700 0 0 {name=h1
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
C {launcher.sym} -400 -660 0 0 {name=h2
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/predriver.tb.raw tran"
}
