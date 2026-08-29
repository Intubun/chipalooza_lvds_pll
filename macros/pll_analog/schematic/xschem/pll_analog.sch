v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Custom-layout analog portion of the PLL.
Digital PFD/divider logic drives UP and DOWN and consumes VCO_CLK.} -300 -250 0 0 0.3 0.3 {}
C {charge_pump.sym} -120 -60 0 0 {name=x_charge_pump}
C {lab_pin.sym} -200 -90 0 0 {name=p_cp_up sig_type=std_logic lab=UP}
C {lab_pin.sym} -200 -50 0 0 {name=p_cp_down sig_type=std_logic lab=DOWN}
C {lab_pin.sym} -200 -20 0 0 {name=p_cp_iref sig_type=std_logic lab=IREF}
C {lab_pin.sym} -40 -60 0 1 {name=p_cp_vctrl sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} -140 -140 1 0 {name=p_cp_vdd sig_type=std_logic lab=VDD}
C {lab_pin.sym} -100 20 3 0 {name=p_cp_vss sig_type=std_logic lab=VSS}
C {loop_filter.sym} 80 -60 0 0 {name=x_loop_filter}
C {lab_pin.sym} 10 -60 0 0 {name=p_filter_vctrl sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} 80 10 3 0 {name=p_filter_vss sig_type=std_logic lab=VSS}
C {ring_oscillator.sym} 280 -60 0 0 {name=x_vco}
C {lab_pin.sym} 160 -90 0 0 {name=p_vco_ctrl sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} 400 -90 0 1 {name=p_vco_out sig_type=std_logic lab=VCO_CLK}
C {lab_pin.sym} 400 -70 0 1 {name=p_vco_vdd sig_type=std_logic lab=VDD}
C {lab_pin.sym} 400 -10 0 1 {name=p_vco_vss sig_type=std_logic lab=VSS}
C {ipin.sym} -300 -90 0 0 {name=p_UP lab=UP}
C {ipin.sym} -300 -50 0 0 {name=p_DOWN lab=DOWN}
C {iopin.sym} -300 -10 2 0 {name=p_IREF lab=IREF}
C {opin.sym} 500 -90 0 0 {name=p_VCO_CLK lab=VCO_CLK}
C {iopin.sym} 0 -180 3 0 {name=p_VDD lab=VDD}
C {iopin.sym} 0 100 1 0 {name=p_VSS lab=VSS}
