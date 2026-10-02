v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {H-bridge of the driver: switches M5/M4 (top) and M1/M3 (bottom), tail sources M2 (gate cmfb, from the CMFB amplifier) and M6 (gate Iref), Ctn on tail_n, sense resistors Rp/Rn to cm. Split out of Driver on 2026-10-01.} -400 -1000 0 0 0.3 0.3 {}
N -180 -440 -80 -440 {lab=Va}
N 20 -440 60 -440 {lab=Va}
N 60 -660 60 -440 {lab=Va}
N -180 -200 -80 -200 {lab=Vss}
N 20 -200 60 -200 {lab=Vss}
N 60 -200 60 100 {lab=Vss}
N -80 100 60 100 {lab=Vss}
N -180 -520 -180 -470 {lab=tail_p}
N 20 -520 20 -470 {lab=tail_p}
N -180 -520 20 -520 {lab=tail_p}
N -180 -170 -180 -110 {lab=tail_n}
N 20 -170 20 -110 {lab=tail_n}
N -180 -110 20 -110 {lab=tail_n}
N -180 -350 -180 -230 {lab=Out_p}
N 300 -350 300 -290 {lab=Out_p}
N 20 -310 20 -230 {lab=Out_n}
N 400 -310 400 -290 {lab=Out_n}
N 300 -230 520 -230 {lab=cm}
N -220 -350 -220 -200 {lab=In_p}
N -260 -350 -220 -350 {lab=In_p}
N -220 -440 -220 -350 {lab=In_p}
N -260 -310 -20 -310 {lab=In_n}
N -20 -440 -20 -310 {lab=In_n}
N -20 -310 -20 -200 {lab=In_n}
N 20 -110 200 -110 {lab=tail_n}
N 200 -110 200 -80 {lab=tail_n}
N 140 -40 230 -40 {lab=Vss}
N 140 -40 140 100 {lab=Vss}
N 140 100 260 100 {lab=Vss}
N 60 100 140 100 {lab=Vss}
N 300 -350 520 -350 {lab=Out_p}
N -180 -350 300 -350 {lab=Out_p}
N -180 -410 -180 -350 {lab=Out_p}
N 400 -310 520 -310 {lab=Out_n}
N 20 -310 400 -310 {lab=Out_n}
N 20 -410 20 -310 {lab=Out_n}
N 60 -660 100 -660 {lab=Va}
N -80 -660 60 -660 {lab=Va}
N -180 -570 -180 -520 {lab=tail_p}
N -80 -600 -80 -440 {lab=Va}
N -180 -600 -80 -600 {lab=Va}
N -80 -660 -80 -600 {lab=Va}
N -180 -660 -180 -630 {lab=Va}
N -180 -660 -80 -660 {lab=Va}
N -180 -110 -180 -70 {lab=tail_n}
N -260 -40 -220 -40 {lab=Iref}
N -180 -10 -180 100 {lab=Vss}
N -180 100 -80 100 {lab=Vss}
N -80 -40 -80 100 {lab=Vss}
N -180 -40 -80 -40 {lab=Vss}
N -80 -200 -80 -40 {lab=Vss}
N -260 -600 -220 -600 {lab=cmfb}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 200 -60 1 0 {name=Ctn
l=5u
w=30u
 ng=3
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} -200 -600 0 0 {name=M2
l=0.5u
w=97.2u
 ng=20
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} -200 -440 0 0 {name=M5
l=0.4u
w=80u
 ng=16
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 0 -440 0 0 {name=M4
l=0.4u
w=80u
 ng=16
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -200 -200 0 0 {name=M1
l=0.45u
w=30u
 ng=15
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 0 -200 0 0 {name=M3
l=0.45u
w=30u
 ng=15
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -200 -40 0 0 {name=M6
l=0.5u
w=99.2u
 ng=31
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/rhigh.sym} 300 -260 0 0 {name=Rp
w=1u
l=7.35u
model=rhigh
body=Vss
spiceprefix=X
b=0
 m=1
  mm_ok=1
}
C {sg13cmos5l_pr/rhigh.sym} 400 -260 0 0 {name=Rn
w=1u
l=7.35u
model=rhigh
body=Vss
spiceprefix=X
b=0
 m=1
  mm_ok=1
}
C {lab_wire.sym} 0 -520 0 0 {name=n3 sig_type=std_logic lab=tail_p}
C {lab_wire.sym} -10 -110 0 0 {name=n5 sig_type=std_logic lab=tail_n}
C {iopin.sym} 100 -660 0 0 {name=p1 lab=Va}
C {iopin.sym} 260 100 0 0 {name=p2 lab=Vss}
C {ipin.sym} -260 -350 0 0 {name=p3 lab=In_p}
C {ipin.sym} -260 -310 0 0 {name=p4 lab=In_n}
C {ipin.sym} -260 -40 0 0 {name=p5 lab=Iref}
C {ipin.sym} -260 -600 0 0 {name=p6 lab=cmfb}
C {opin.sym} 520 -350 0 0 {name=p7 lab=Out_p}
C {opin.sym} 520 -310 0 0 {name=p8 lab=Out_n}
C {opin.sym} 520 -230 0 0 {name=p9 lab=cm}
