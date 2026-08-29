v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {PFD transient testbench.
The upper case checks REF leading FB by 2 ns; the lower case checks FB leading REF by 2 ns.} -340 -300 0 0 0.3 0.3 {}
B 2 260 -250 960 250 {flags=graph
y1=-0.1
y2=1.3
ypos1=0
ypos2=2
divy=7
subdivy=1
unity=1
x1=0
x2=4e-08
divx=8
subdivx=1
node="REF_EARLY
FB_LATE
UP_LEAD
DOWN_LEAD
REF_LATE
FB_EARLY
UP_LAG
DOWN_LAG"
color="4 5 6 7 8 9 10 11"
dataset=-1
unitx=1
logx=0
logy=0}
C {pfd.sym} 0 -90 0 0 {name=x_up_case}
C {lab_pin.sym} -80 -110 0 0 {name=p_ref_early sig_type=std_logic lab=REF_EARLY}
C {lab_pin.sym} -80 -70 0 0 {name=p_fb_late sig_type=std_logic lab=FB_LATE}
C {lab_pin.sym} 80 -110 0 1 {name=p_up_lead sig_type=std_logic lab=UP_LEAD}
C {lab_pin.sym} 80 -70 0 1 {name=p_down_lead sig_type=std_logic lab=DOWN_LEAD}
C {lab_pin.sym} -20 -160 1 0 {name=p_vdd_up sig_type=std_logic lab=VDD}
C {gnd.sym} 20 -20 0 0 {name=l_vss_up lab=0}
C {pfd.sym} 0 100 0 0 {name=x_down_case}
C {lab_pin.sym} -80 80 0 0 {name=p_ref_late sig_type=std_logic lab=REF_LATE}
C {lab_pin.sym} -80 120 0 0 {name=p_fb_early sig_type=std_logic lab=FB_EARLY}
C {lab_pin.sym} 80 80 0 1 {name=p_up_lag sig_type=std_logic lab=UP_LAG}
C {lab_pin.sym} 80 120 0 1 {name=p_down_lag sig_type=std_logic lab=DOWN_LAG}
C {lab_pin.sym} -20 30 1 0 {name=p_vdd_down sig_type=std_logic lab=VDD}
C {gnd.sym} 20 170 0 0 {name=l_vss_down lab=0}
C {vsource.sym} -280 -110 0 0 {name=VREF_EARLY value="PULSE(0 1.2 1n 20p 20p 4n 10n)" savecurrent=false}
C {lab_pin.sym} -280 -140 1 0 {name=p_src_ref_early sig_type=std_logic lab=REF_EARLY}
C {gnd.sym} -280 -80 0 0 {name=l_src_ref_early lab=0}
C {vsource.sym} -190 -110 0 0 {name=VFB_LATE value="PULSE(0 1.2 3n 20p 20p 4n 10n)" savecurrent=false}
C {lab_pin.sym} -190 -140 1 0 {name=p_src_fb_late sig_type=std_logic lab=FB_LATE}
C {gnd.sym} -190 -80 0 0 {name=l_src_fb_late lab=0}
C {vsource.sym} -280 100 0 0 {name=VREF_LATE value="PULSE(0 1.2 3n 20p 20p 4n 10n)" savecurrent=false}
C {lab_pin.sym} -280 70 1 0 {name=p_src_ref_late sig_type=std_logic lab=REF_LATE}
C {gnd.sym} -280 130 0 0 {name=l_src_ref_late lab=0}
C {vsource.sym} -190 100 0 0 {name=VFB_EARLY value="PULSE(0 1.2 1n 20p 20p 4n 10n)" savecurrent=false}
C {lab_pin.sym} -190 70 1 0 {name=p_src_fb_early sig_type=std_logic lab=FB_EARLY}
C {gnd.sym} -190 130 0 0 {name=l_src_fb_early lab=0}
C {vsource.sym} -100 -240 0 0 {name=VDD_SRC value=1.2 savecurrent=false}
C {lab_pin.sym} -100 -270 1 0 {name=p_vdd_src sig_type=std_logic lab=VDD}
C {gnd.sym} -100 -210 0 0 {name=l_vdd_src lab=0}
C {simulator_commands_shown.sym} -340 200 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.control
save all
tran 1p 40n
meas tran up_width trig v(UP_LEAD) val=0.6 rise=3 targ v(UP_LEAD) val=0.6 fall=3
meas tran down_width trig v(DOWN_LAG) val=0.6 rise=3 targ v(DOWN_LAG) val=0.6 fall=3
meas tran reset_up_width trig v(DOWN_LEAD) val=0.6 rise=3 targ v(DOWN_LEAD) val=0.6 fall=3
meas tran reset_down_width trig v(UP_LAG) val=0.6 rise=3 targ v(UP_LAG) val=0.6 fall=3
write pfd.tb.raw
if up_width < 1.9n
  echo ERROR: UP pulse width outside expected range
end
if up_width > 2.2n
  echo ERROR: UP pulse width outside expected range
end
if down_width < 1.9n
  echo ERROR: DOWN pulse width outside expected range
end
if down_width > 2.2n
  echo ERROR: DOWN pulse width outside expected range
end
.endc
"}
C {launcher.sym} -20 250 0 0 {name=h_simulate
descr=SimulateNGSPICE
tclcommand="
set_sim_defaults
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}
set sim(spice,default) 0
file mkdir $netlist_dir
xschem netlist
simulate
"}
C {launcher.sym} -20 290 0 0 {name=h_waves
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/pfd.tb.raw tran"
}
