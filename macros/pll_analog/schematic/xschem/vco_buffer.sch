v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Two-stage tapered CMOS buffer for isolating the VCO core.
Stage 1: WP/WN=0.30/0.15 um. Stage 2: WP/WN=0.90/0.45 um.} -170 -210 0 0 0.3 0.3 {}
N -120 0 -60 0 {lab=VIN}
N -60 -60 -20 -60 {lab=VIN}
N -60 0 -60 60 {lab=VIN}
N -60 60 -20 60 {lab=VIN}
N 20 0 20 30 {lab=#net1}
N 20 0 100 0 {lab=#net1}
N 100 -60 140 -60 {lab=#net1}
N 100 0 100 60 {lab=#net1}
N 100 60 140 60 {lab=#net1}
N 180 0 180 30 {lab=VOUT}
N 180 0 280 0 {lab=VOUT}
N 80 -120 180 -120 {lab=VDD}
N 20 -120 20 -90 {lab=VDD}
N 180 -120 180 -90 {lab=VDD}
N 20 90 20 120 {lab=VSS}
N 180 90 180 120 {lab=VSS}
N 80 120 180 120 {lab=VSS}
N 20 -60 80 -60 {lab=VDD}
N 80 -120 80 -60 {lab=VDD}
N 20 60 80 60 {lab=VSS}
N 80 60 80 120 {lab=VSS}
N 180 -60 240 -60 {lab=VDD}
N 240 -120 240 -60 {lab=VDD}
N 180 -120 240 -120 {lab=VDD}
N 180 60 240 60 {lab=VSS}
N 240 60 240 120 {lab=VSS}
N 180 120 240 120 {lab=VSS}
N -60 -60 -60 0 {lab=VIN}
N 20 -30 20 0 {lab=#net1}
N 100 -60 100 0 {lab=#net1}
N 180 -30 180 0 {lab=VOUT}
N 20 -120 80 -120 {lab=VDD}
N 20 120 80 120 {lab=VSS}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 0 -60 0 0 {name=M1
l=0.13u
w=0.30u
ng=1
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} 0 60 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 160 -60 0 0 {name=M3
l=0.13u
w=0.90u
ng=3
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} 160 60 0 0 {name=M4
l=0.13u
w=0.45u
ng=3
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ipin.sym} -120 0 0 0 {name=p_VIN lab=VIN}
C {opin.sym} 280 0 0 0 {name=p_VOUT lab=VOUT}
C {iopin.sym} 20 -120 3 0 {name=p_VDD lab=VDD}
C {iopin.sym} 20 120 1 0 {name=p_VSS lab=VSS}
