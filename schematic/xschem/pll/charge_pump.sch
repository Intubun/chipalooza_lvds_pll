v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Approximately 2.84 uA charge pump with mirrored NMOS/PMOS currents.
IREF is a 2 uA current-input bias node. UP and DOWN are active high.} -260 -270 0 0 0.3 0.3 {}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} -160 -140 0 0 {name=M_UP_INV_P
l=0.13u
w=0.30u
ng=1
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} -160 -80 0 0 {name=M_UP_INV_N
l=0.13u
w=0.15u
ng=1
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} -160 100 0 0 {name=M_IREF
l=0.50u
w=4.0u
ng=4
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} -40 20 0 0 {name=M_PBIAS
l=0.50u
w=8.0u
ng=8
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} -40 100 0 0 {name=M_PBIAS_SINK
l=0.50u
w=4.0u
ng=4
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 80 20 0 0 {name=M_UP_SOURCE
l=0.50u
w=7.0u
ng=8
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 80 80 0 0 {name=M_UP_SWITCH
l=0.13u
w=1.0u
ng=1
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} 80 140 0 0 {name=M_DOWN_SWITCH
l=0.13u
w=1.5u
ng=1
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_lv_nmos.sym} 80 200 0 0 {name=M_DOWN_SINK
l=0.50u
w=4.0u
ng=4
m=1
mm_ok=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} -140 -170 1 0 {name=p_inv_p_s sig_type=std_logic lab=VDD}
C {lab_pin.sym} -140 -140 0 1 {name=p_inv_p_b sig_type=std_logic lab=VDD}
C {lab_pin.sym} -140 -110 0 1 {name=p_inv_p_d sig_type=std_logic lab=UP_B}
C {lab_pin.sym} -180 -140 0 0 {name=p_inv_p_g sig_type=std_logic lab=UP}
C {lab_pin.sym} -140 -80 0 1 {name=p_inv_n_b sig_type=std_logic lab=VSS}
C {lab_pin.sym} -140 -50 3 0 {name=p_inv_n_s sig_type=std_logic lab=VSS}
C {lab_pin.sym} -180 -80 0 0 {name=p_inv_n_g sig_type=std_logic lab=UP}
C {lab_pin.sym} -140 70 1 0 {name=p_iref_d sig_type=std_logic lab=IREF}
C {lab_pin.sym} -180 100 0 0 {name=p_iref_g sig_type=std_logic lab=IREF}
C {lab_pin.sym} -140 100 0 1 {name=p_iref_b sig_type=std_logic lab=VSS}
C {lab_pin.sym} -140 130 3 0 {name=p_iref_s sig_type=std_logic lab=VSS}
C {lab_pin.sym} -20 -10 1 0 {name=p_pbias_p_s sig_type=std_logic lab=VDD}
C {lab_pin.sym} -20 20 0 1 {name=p_pbias_p_b sig_type=std_logic lab=VDD}
C {lab_pin.sym} -20 50 3 0 {name=p_pbias_p_d sig_type=std_logic lab=PBIAS}
C {lab_pin.sym} -60 20 0 0 {name=p_pbias_p_g sig_type=std_logic lab=PBIAS}
C {lab_pin.sym} -20 70 1 0 {name=p_pbias_n_d sig_type=std_logic lab=PBIAS}
C {lab_pin.sym} -60 100 0 0 {name=p_pbias_n_g sig_type=std_logic lab=IREF}
C {lab_pin.sym} -20 100 0 1 {name=p_pbias_n_b sig_type=std_logic lab=VSS}
C {lab_pin.sym} -20 130 3 0 {name=p_pbias_n_s sig_type=std_logic lab=VSS}
C {lab_pin.sym} 100 -10 1 0 {name=p_up_src_s sig_type=std_logic lab=VDD}
C {lab_pin.sym} 100 20 0 1 {name=p_up_src_b sig_type=std_logic lab=VDD}
C {lab_pin.sym} 100 50 3 0 {name=p_up_src_d sig_type=std_logic lab=P_UP}
C {lab_pin.sym} 60 20 0 0 {name=p_up_src_g sig_type=std_logic lab=PBIAS}
C {lab_pin.sym} 100 80 0 1 {name=p_up_sw_b sig_type=std_logic lab=VDD}
C {lab_pin.sym} 100 110 3 0 {name=p_up_sw_d sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} 60 80 0 0 {name=p_up_sw_g sig_type=std_logic lab=UP_B}
C {lab_pin.sym} 100 140 0 1 {name=p_down_sw_b sig_type=std_logic lab=VSS}
C {lab_pin.sym} 100 170 3 0 {name=p_down_sw_s sig_type=std_logic lab=N_DOWN}
C {lab_pin.sym} 60 140 0 0 {name=p_down_sw_g sig_type=std_logic lab=DOWN}
C {lab_pin.sym} 100 200 0 1 {name=p_down_sink_b sig_type=std_logic lab=VSS}
C {lab_pin.sym} 100 230 3 0 {name=p_down_sink_s sig_type=std_logic lab=VSS}
C {lab_pin.sym} 60 200 0 0 {name=p_down_sink_g sig_type=std_logic lab=IREF}
C {ipin.sym} -260 -140 0 0 {name=p_UP lab=UP}
C {ipin.sym} -260 -80 0 0 {name=p_DOWN lab=DOWN}
C {iopin.sym} -260 100 2 0 {name=p_IREF lab=IREF}
C {opin.sym} 200 110 0 0 {name=p_VCTRL lab=VCTRL}
C {iopin.sym} 0 -180 3 0 {name=p_VDD lab=VDD}
C {iopin.sym} 0 240 1 0 {name=p_VSS lab=VSS}
