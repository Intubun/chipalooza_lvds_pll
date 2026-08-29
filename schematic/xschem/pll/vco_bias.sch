v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Replica bias generator for the current-starved VCO.
VCTRL directly controls the NMOS starvers; the replica branch generates VBP.} -190 -210 0 0 0.3 0.3 {}
N -120 60 -20 60 {lab=VCTRL}
N 20 0 20 30 {lab=VBP}
N -40 -60 -20 -60 {lab=VBP}
N -40 -60 -40 0 {lab=VBP}
N -40 0 20 0 {lab=VBP}
N 20 0 120 0 {lab=VBP}
N 20 -120 20 -90 {lab=VDD}
N 20 90 20 120 {lab=VSS}
N 20 -120 80 -120 {lab=VDD}
N 80 -120 80 -60 {lab=VDD}
N 20 -60 80 -60 {lab=VDD}
N 20 120 80 120 {lab=VSS}
N 80 60 80 120 {lab=VSS}
N 20 60 80 60 {lab=VSS}
N 20 -30 20 0 {lab=VBP}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 0 -60 0 0 {name=M1
l=0.13u
w=0.15u
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
C {ipin.sym} -120 60 0 0 {name=p_VCTRL lab=VCTRL}
C {opin.sym} 120 0 0 0 {name=p_VBP lab=VBP}
C {iopin.sym} 20 -120 3 0 {name=p_VDD lab=VDD}
C {iopin.sym} 20 120 1 0 {name=p_VSS lab=VSS}
