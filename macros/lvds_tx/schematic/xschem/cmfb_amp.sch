v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {CMFB amplifier of the driver: M11/M12 compare cm (from Rp/Rn) with Vref, M13/M14 the load, M10 the tail (mirrors Iref), Cc and Rc compensate cmfb, the gate of the driver's top tail M2. Split out of Driver on 2026-10-01 for layout and LVS on its own.} -1500 -1060 0 0 0.3 0.3 {}
N -1180 -440 -1140 -440 {lab=Vss}
N -980 -440 -920 -440 {lab=Vss}
N -980 -560 -980 -470 {lab=cmfb}
N -1180 -560 -1180 -470 {lab=pd}
N -1180 -570 -1180 -560 {lab=pd}
N -1140 -600 -1140 -560 {lab=pd}
N -1180 -560 -1140 -560 {lab=pd}
N -1180 -410 -1180 -380 {lab=otail}
N -980 -410 -980 -380 {lab=otail}
N -1080 -380 -980 -380 {lab=otail}
N -1300 -310 -1120 -310 {lab=Iref}
N -1080 -310 -1080 -240 {lab=Vss}
N -1080 -380 -1080 -340 {lab=otail}
N -1180 -380 -1080 -380 {lab=otail}
N -1100 -440 -1020 -440 {lab=Vref}
N -1100 -440 -1100 -340 {lab=Vref}
N -1300 -340 -1100 -340 {lab=Vref}
N -920 -440 -920 -240 {lab=Vss}
N -840 -240 -620 -240 {lab=Vss}
N -1080 -240 -920 -240 {lab=Vss}
N -1140 -440 -1140 -240 {lab=Vss}
N -1140 -240 -1080 -240 {lab=Vss}
N -840 -360 -750 -360 {lab=Vss}
N -780 -460 -780 -400 {lab=cc_g}
N -1140 -600 -1020 -600 {lab=pd}
N -1300 -440 -1220 -440 {lab=cm}
N -780 -560 -620 -560 {lab=cmfb}
N -980 -570 -980 -560 {lab=cmfb}
N -780 -560 -780 -520 {lab=cmfb}
N -980 -560 -780 -560 {lab=cmfb}
N -840 -360 -840 -240 {lab=Vss}
N -920 -240 -840 -240 {lab=Vss}
N -1180 -680 -980 -680 {lab=Va}
N -980 -680 -980 -600 {lab=Va}
N -1180 -680 -1180 -600 {lab=Va}
N -1280 -680 -1180 -680 {lab=Va}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} -1160 -600 0 1 {name=M13
l=1u
w=5u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} -1000 -600 0 0 {name=M14
l=1u
w=5u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -1200 -440 0 0 {name=M11
l=1u
w=20u
 ng=4
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -1000 -440 0 0 {name=M12
l=1u
w=20u
 ng=4
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -1100 -310 0 0 {name=M10
l=0.5u
w=0.8u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -780 -380 1 0 {name=Cc
l=5u
w=50u
 ng=5
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/rppd.sym} -780 -490 0 0 {name=Rc
w=1u
l=6u
model=rppd
body=Vss
spiceprefix=X
b=0
 m=1
  mm_ok=1
}
C {lab_pin.sym} -780 -430 2 0 {name=n9 sig_type=std_logic lab=cc_g}
C {lab_wire.sym} -1070 -600 0 0 {name=n7 sig_type=std_logic lab=pd}
C {lab_pin.sym} -1160 -380 0 0 {name=n8 sig_type=std_logic lab=otail}
C {iopin.sym} -1280 -680 0 1 {name=p1 lab=Va}
C {iopin.sym} -620 -240 0 0 {name=p2 lab=Vss}
C {ipin.sym} -1300 -440 0 0 {name=p3 lab=cm}
C {ipin.sym} -1300 -310 0 0 {name=p4 lab=Iref}
C {ipin.sym} -1300 -340 0 0 {name=p5 lab=Vref}
C {opin.sym} -620 -560 0 0 {name=p6 lab=cmfb}
