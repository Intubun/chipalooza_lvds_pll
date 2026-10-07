v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {ref_odt_lvlup - 1.2 V -> 3.3 V level shifter, non-inverting
= sg13cmos5l_LevelUp of the IHP IO library, transistor for transistor.
Input inverter on vdd (LV), cross-coupled pair and output inverter on iovdd (HV).} -150 -420 0 0 0.4 0.4 {}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 0 -100 0 0 {name=MP_I
l=0.13u
w=4.75u
ng=1
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X}
N 20 -130 20 -160 {}
C {devices/lab_pin.sym} 20 -160 0 0 {name=l1 sig_type=std_logic lab=vdd}
N 20 -100 50 -100 {}
C {devices/lab_pin.sym} 50 -100 0 1 {name=l2 sig_type=std_logic lab=vdd}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} 0 50 0 0 {name=MN_I
l=0.13u
w=2.75u
ng=1
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X}
N 20 80 20 110 {}
C {devices/lab_pin.sym} 20 110 0 0 {name=l3 sig_type=std_logic lab=vss}
N 20 50 50 50 {}
C {devices/lab_pin.sym} 50 50 0 1 {name=l4 sig_type=std_logic lab=vss}
N 20 -70 20 20 {lab=IN_N}
C {devices/lab_wire.sym} 20 -25 0 0 {name=w5 sig_type=std_logic lab=IN_N}
N -20 -100 -60 -100 {lab=i}
N -60 -100 -60 50 {lab=i}
N -60 50 -20 50 {lab=i}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 300 -100 0 0 {name=MP_LN
l=0.45u
w=0.3u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 320 -130 320 -160 {}
C {devices/lab_pin.sym} 320 -160 0 0 {name=l6 sig_type=std_logic lab=iovdd}
N 320 -100 350 -100 {}
C {devices/lab_pin.sym} 350 -100 0 1 {name=l7 sig_type=std_logic lab=iovdd}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 300 50 0 0 {name=MN_LN
l=0.45u
w=1.9u
ng=1
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
N 320 80 320 110 {}
C {devices/lab_pin.sym} 320 110 0 0 {name=l8 sig_type=std_logic lab=vss}
N 320 50 350 50 {}
C {devices/lab_pin.sym} 350 50 0 1 {name=l9 sig_type=std_logic lab=vss}
N 320 -70 320 20 {lab=LVLD_N}
C {devices/lab_wire.sym} 320 -25 0 0 {name=w10 sig_type=std_logic lab=LVLD_N}
C {devices/lab_pin.sym} 280 -100 0 0 {name=l11 sig_type=std_logic lab=LVLD}
C {devices/lab_pin.sym} 280 50 0 0 {name=l12 sig_type=std_logic lab=i}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 550 -100 0 0 {name=MP_L
l=0.45u
w=0.3u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 570 -130 570 -160 {}
C {devices/lab_pin.sym} 570 -160 0 0 {name=l13 sig_type=std_logic lab=iovdd}
N 570 -100 600 -100 {}
C {devices/lab_pin.sym} 600 -100 0 1 {name=l14 sig_type=std_logic lab=iovdd}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 550 50 0 0 {name=MN_L
l=0.45u
w=1.9u
ng=1
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
N 570 80 570 110 {}
C {devices/lab_pin.sym} 570 110 0 0 {name=l15 sig_type=std_logic lab=vss}
N 570 50 600 50 {}
C {devices/lab_pin.sym} 600 50 0 1 {name=l16 sig_type=std_logic lab=vss}
N 570 -70 570 20 {lab=LVLD}
C {devices/lab_wire.sym} 570 -25 0 0 {name=w17 sig_type=std_logic lab=LVLD}
C {devices/lab_pin.sym} 530 -100 0 0 {name=l18 sig_type=std_logic lab=LVLD_N}
C {devices/lab_pin.sym} 530 50 0 0 {name=l19 sig_type=std_logic lab=IN_N}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 800 -100 0 0 {name=MP_O
l=0.45u
w=3.9u
ng=1
m=1
mm_ok=1
model=sg13_hv_pmos
spiceprefix=X}
N 820 -130 820 -160 {}
C {devices/lab_pin.sym} 820 -160 0 0 {name=l20 sig_type=std_logic lab=iovdd}
N 820 -100 850 -100 {}
C {devices/lab_pin.sym} 850 -100 0 1 {name=l21 sig_type=std_logic lab=iovdd}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 800 50 0 0 {name=MN_O
l=0.45u
w=1.9u
ng=1
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
N 820 80 820 110 {}
C {devices/lab_pin.sym} 820 110 0 0 {name=l22 sig_type=std_logic lab=vss}
N 820 50 850 50 {}
C {devices/lab_pin.sym} 850 50 0 1 {name=l23 sig_type=std_logic lab=vss}
N 820 -70 820 20 {lab=o}
C {devices/lab_wire.sym} 820 -25 0 0 {name=w24 sig_type=std_logic lab=o}
N 780 -100 740 -100 {lab=LVLD_N}
N 740 -100 740 50 {lab=LVLD_N}
N 740 50 780 50 {lab=LVLD_N}
C {devices/ipin.sym} -150 -25 2 1 {name=p_i lab=i}
N -150 -25 -60 -25 {lab=i}
C {devices/lab_pin.sym} 740 -25 0 0 {name=l25 sig_type=std_logic lab=LVLD_N}
C {devices/opin.sym} 950 -25 0 0 {name=p_o lab=o}
N 820 -25 950 -25 {lab=o}
C {devices/iopin.sym} -150 200 2 0 {name=p_vdd lab=vdd}
N -150 200 -110 200 {lab=vdd}
C {devices/lab_pin.sym} -110 200 0 1 {name=l26 sig_type=std_logic lab=vdd}
C {devices/iopin.sym} -150 240 2 0 {name=p_iovdd lab=iovdd}
N -150 240 -110 240 {lab=iovdd}
C {devices/lab_pin.sym} -110 240 0 1 {name=l27 sig_type=std_logic lab=iovdd}
C {devices/iopin.sym} -150 280 2 0 {name=p_vss lab=vss}
N -150 280 -110 280 {lab=vss}
C {devices/lab_pin.sym} -110 280 0 1 {name=l28 sig_type=std_logic lab=vss}
