v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 360 -700 600 -700 {lab=Va}
N 460 640 600 640 {lab=Vss}
N 120 -400 160 -400 {}
N 160 -700 160 -400 {lab=Va}
N 320 -400 360 -400 {}
N 360 -700 360 -400 {lab=Va}
N 220 0 260 0 {}
N 260 0 260 640 {lab=Vss}
N 420 0 460 0 {}
N 460 0 460 640 {lab=Vss}
N 320 360 360 360 {}
N 360 360 360 640 {lab=Vss}
N 120 -700 120 -430 {lab=Va}
N 320 -700 320 -430 {lab=Va}
N 220 -260 280 -260 {lab=dg}
N 80 -400 80 -260 {}
N 120 -370 120 -260 {}
N 280 -400 280 -260 {}
N 220 -260 220 -30 {}
N 320 -370 320 -240 {}
N 320 -240 420 -240 {lab=Out}
N 420 -240 420 -30 {}
N 420 -240 600 -240 {lab=Out}
N 220 30 220 60 {}
N 320 60 420 60 {lab=tl}
N 420 30 420 60 {}
N 320 60 320 330 {}
N 320 390 320 640 {lab=Vss}
N -100 200 180 200 {lab=Din}
N 180 0 180 200 {}
N -100 260 380 260 {lab=Gin}
N 380 0 380 260 {}
N -100 320 280 320 {lab=Iref}
N 280 320 280 360 {}
N 120 -700 160 -700 {lab=Va}
N 320 -700 360 -700 {lab=Va}
N -100 640 260 640 {lab=Vss}
N 360 640 460 640 {lab=Vss}
N 320 640 360 640 {lab=Vss}
N -100 -700 120 -700 {lab=Va}
N 160 -700 320 -700 {lab=Va}
N 80 -260 120 -260 {lab=dg}
N 120 -260 220 -260 {lab=dg}
N 220 60 320 60 {lab=tl}
N 260 640 320 640 {lab=Vss}
C {iopin.sym} -100 -700 0 0 {name=p_Va lab=Va}
C {iopin.sym} -100 640 0 0 {name=p_Vss lab=Vss}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 100 -400 0 0 {name=Mld
l=0.4u
w=12u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 300 -400 0 0 {name=Mlo
l=0.4u
w=12u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 200 0 0 0 {name=Mid
l=0.45u
w=24u
 ng=2
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 400 0 0 0 {name=Mio
l=0.45u
w=24u
 ng=2
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 300 360 0 0 {name=Mt
l=0.5u
w=140u
 ng=14
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {opin.sym} 600 -240 0 0 {name=p_Out lab=Out}
C {ipin.sym} -100 200 0 0 {name=p_Din lab=Din}
C {ipin.sym} -100 260 0 0 {name=p_Gin lab=Gin}
C {ipin.sym} -100 320 0 0 {name=p_Iref lab=Iref}
