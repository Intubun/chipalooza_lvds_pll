v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Ctn holds tail_n through the switching edge: without it the
bottom switches pull harder than the top ones while the gates pass mid-rail,
the common mode dips and Out_p/Out_n cross ~14 % below the middle.} 200 20 0 0 0.2 0.2 {}
N 1260 -320 1400 -320 {lab=Out_p}
N 1260 -320 1260 -150 {lab=Out_p}
N 1040 -320 1260 -320 {lab=Out_p}
N 1360 -300 1400 -300 {lab=Out_n}
N 1360 -300 1360 -150 {lab=Out_n}
N 1040 -300 1360 -300 {lab=Out_n}
N 940 -480 940 -360 {lab=Va}
N 680 -260 840 -260 {lab=cmfb}
N 580 -480 580 -330 {lab=Va}
N 1040 -280 1060 -280 {lab=cm}
N 1060 -280 1060 -120 {lab=cm}
N 400 -280 480 -280 {lab=cm}
N 400 -280 400 -120 {lab=cm}
N 400 -120 1060 -120 {lab=cm}
N 360 -260 480 -260 {lab=Vref}
N 360 -400 820 -400 {lab=In_p}
N 820 -400 820 -320 {lab=In_p}
N 820 -320 840 -320 {lab=In_p}
N 360 -360 780 -360 {lab=In_n}
N 780 -360 780 -300 {lab=In_n}
N 780 -300 840 -300 {lab=In_n}
N 940 -480 1400 -480 {lab=Va}
N 580 -480 940 -480 {lab=Va}
N 1300 -60 1400 -60 {lab=Vss}
N 1300 -180 1300 -60 {lab=Vss}
N 1400 -180 1400 -60 {lab=Vss}
N 940 -60 1300 -60 {lab=Vss}
N 940 -220 940 -60 {lab=Vss}
N 580 -60 940 -60 {lab=Vss}
N 580 -190 580 -60 {lab=Vss}
N 220 -190 260 -190 {lab=Iref}
N 260 -190 260 -160 {lab=Iref}
N 220 -60 580 -60 {lab=Vss}
N 160 -240 220 -240 {lab=Iref}
N 220 -240 220 -190 {lab=Iref}
N 460 -160 800 -160 {lab=Iref}
N 800 -280 800 -160 {lab=Iref}
N 800 -280 840 -280 {lab=Iref}
N 460 -240 480 -240 {lab=Iref}
N 460 -240 460 -160 {lab=Iref}
N 260 -160 460 -160 {lab=Iref}
N 220 -160 220 -60 {lab=Vss}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 240 -160 0 1 {name=M9
l=0.5u
w=0.8u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 1280 -150 0 0 {name=Cop
l=5u
w=20u
 ng=2
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 1380 -150 0 0 {name=Con
l=5u
w=20u
 ng=2
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {iopin.sym} 1400 -480 0 0 {name=p1 lab=Va}
C {opin.sym} 1400 -320 0 0 {name=p4 lab=Out_p}
C {opin.sym} 1400 -300 0 0 {name=p5 lab=Out_n}
C {cmfb_amp.sym} 580 -260 0 0 {name=x_cmfb}
C {lab_wire.sym} 520 -120 0 0 {name=n20 sig_type=std_logic lab=cm}
C {lab_wire.sym} 320 -160 0 0 {name=n22 sig_type=std_logic lab=Iref}
C {lab_wire.sym} 720 -260 0 1 {name=p23 sig_type=std_logic lab=cmfb}
C {hbridge.sym} 940 -290 0 0 {name=x_hbridge}
C {ipin.sym} 360 -260 0 0 {name=p3 lab=Vref}
C {ipin.sym} 360 -400 0 0 {name=p6 lab=In_p}
C {ipin.sym} 360 -360 0 0 {name=p7 lab=In_n}
C {iopin.sym} 1400 -60 0 0 {name=p2 lab=Vss}
C {ipin.sym} 160 -240 0 0 {name=p8 lab=Iref}
