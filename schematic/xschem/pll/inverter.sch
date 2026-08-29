v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Current-starved inverter for the PLL VCO.
VBP and VBN set the pull-up and pull-down currents.} -180 -250 0 0 0.3 0.3 {}
N -120 -120 -20 -120 {lab=VBP}
N -120 120 -20 120 {lab=VBN}
N -120 0 -60 0 {lab=VIN}
N -60 0 -60 60 {lab=VIN}
N -60 -60 -20 -60 {lab=VIN}
N -60 60 -20 60 {lab=VIN}
N 20 -30 60 -30 {lab=VOUT}
N 20 30 60 30 {lab=VOUT}
N 60 0 60 30 {lab=VOUT}
N 60 0 120 0 {lab=VOUT}
N 20 -180 80 -180 {lab=VDD}
N 20 -180 20 -150 {lab=VDD}
N 20 -120 80 -120 {lab=VDD}
N 80 -120 80 -60 {lab=VDD}
N 20 -60 80 -60 {lab=VDD}
N 20 150 20 180 {lab=VSS}
N 20 120 80 120 {lab=VSS}
N 80 120 80 180 {lab=VSS}
N 20 60 80 60 {lab=VSS}
N 20 180 80 180 {lab=VSS}
N -60 -60 -60 0 {lab=VIN}
N 60 -30 60 0 {lab=VOUT}
N 80 -180 80 -120 {lab=VDD}
N 80 60 80 120 {lab=VSS}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 0 -120 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 0 -60 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} 0 60 0 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} 0 120 0 0 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ipin.sym} -120 0 0 0 {name=p_VIN lab=VIN}
C {ipin.sym} -120 -120 0 0 {name=p_VBP lab=VBP}
C {ipin.sym} -120 120 0 0 {name=p_VBN lab=VBN}
C {opin.sym} 120 0 0 0 {name=p_VOUT lab=VOUT}
C {iopin.sym} 80 -180 3 0 {name=p_VDD lab=VDD}
C {iopin.sym} 80 180 1 0 {name=p_VSS lab=VSS}
