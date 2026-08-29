v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Physical third-order passive charge-pump loop filter.
The impedance is scaled 4x to reduce capacitor area while retaining the original loop dynamics.} -230 -220 0 0 0.3 0.3 {}
N -140 0 -60 0 {lab=VCTRL}
N 20 0 100 0 {lab=VCTRL}
N -60 0 -60 40 {lab=VCTRL}
N 20 0 20 40 {lab=VCTRL}
N -60 190 20 190 {lab=VSS}
N -60 160 -60 190 {lab=VSS}
N 20 100 20 190 {lab=VSS}
N -60 0 20 0 {lab=VCTRL}
C {sg13cmos5l_pr/rhigh.sym} -60 70 0 0 {name=R1
w=1.0u
l=22.08u
model=rhigh
body=VSS
spiceprefix=X
b=0
m=1
mm_ok=1}
C {sg13cmos5l_pr/cap_cmomf.sym} -60 130 0 0 {name=C1A
model=cap_cmomf
w=103.2266u
l=103.2266u
mmin=2
mmax=4
subblock=0
m=1
mm_ok=1
spiceprefix=X}
C {sg13cmos5l_pr/cap_cmomf.sym} 20 70 0 0 {name=C2
model=cap_cmomf
w=32.6431u
l=32.6431u
mmin=2
mmax=4
subblock=0
m=1
mm_ok=1
spiceprefix=X}
C {iopin.sym} -140 0 2 0 {name=p_VCTRL lab=VCTRL}
C {iopin.sym} 20 190 1 0 {name=p_VSS lab=VSS}
C {lab_pin.sym} -60 100 0 0 {name=p_zero sig_type=std_logic lab=FILTER_ZERO}
C {simulator_commands_shown.sym} 120 130 0 0 {name=PASSIVE_MODELS
simulator=ngspice
only_toplevel=false
value="
.lib cornerRES.lib res_typ
.include cap_cmomf.lib
"}
