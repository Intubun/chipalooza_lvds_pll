v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Divide-by-20 mixed-signal feedback-divider testbench.} -230 -190 0 0 0.3 0.3 {}
B 2 190 -150 760 160 {flags=graph
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
node="VCO_IN
FB_OUT"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0}
C {feedback_divider.sym} 0 0 0 0 {name=x_div}
C {lab_pin.sym} -70 0 0 0 {name=p_vco sig_type=std_logic lab=VCO_IN}
C {lab_pin.sym} 70 0 0 1 {name=p_fb sig_type=std_logic lab=FB_OUT}
C {vsource.sym} -150 30 0 0 {name=VVCO value="PULSE(0 1.2 1n 20p 20p 230p 500p)" savecurrent=false}
C {lab_pin.sym} -150 0 1 0 {name=p_vco_src sig_type=std_logic lab=VCO_IN}
C {gnd.sym} -150 60 0 0 {name=l_vco_src lab=0}
C {simulator_commands_shown.sym} -230 100 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.control
save all
tran 1p 40n
meas tran fb_t1 when v(FB_OUT)=0.6 rise=2
meas tran fb_t2 when v(FB_OUT)=0.6 rise=3
let fb_period=fb_t2-fb_t1
print fb_period
write feedback_divider.tb.raw
.endc
"}
