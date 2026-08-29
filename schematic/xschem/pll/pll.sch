v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Integer/fractional-N charge-pump PLL top level.
The XSPICE feedback model is fixed at N=20 for analog loop simulation.
rtl/pll_digital.v replaces the behavioral divider for programmable implementation.} -500 -330 0 0 0.3 0.3 {}
C {pfd.sym} -300 -100 0 0 {name=x_pfd}
C {lab_pin.sym} -380 -120 0 0 {name=p_pfd_ref sig_type=std_logic lab=REF_CLK}
C {lab_pin.sym} -380 -80 0 0 {name=p_pfd_fb sig_type=std_logic lab=FB_CLK}
C {lab_pin.sym} -220 -120 0 1 {name=p_pfd_up sig_type=std_logic lab=UP}
C {lab_pin.sym} -220 -80 0 1 {name=p_pfd_down sig_type=std_logic lab=DOWN}
C {lab_pin.sym} -320 -170 1 0 {name=p_pfd_vdd sig_type=std_logic lab=VDD}
C {lab_pin.sym} -280 -30 3 0 {name=p_pfd_vss sig_type=std_logic lab=VSS}
C {charge_pump.sym} -100 -100 0 0 {name=x_charge_pump}
C {lab_pin.sym} -180 -130 0 0 {name=p_cp_up sig_type=std_logic lab=UP}
C {lab_pin.sym} -180 -90 0 0 {name=p_cp_down sig_type=std_logic lab=DOWN}
C {lab_pin.sym} -180 -60 0 0 {name=p_cp_iref sig_type=std_logic lab=IREF}
C {lab_pin.sym} -20 -100 0 1 {name=p_cp_vctrl sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} -120 -180 1 0 {name=p_cp_vdd sig_type=std_logic lab=VDD}
C {lab_pin.sym} -80 -20 3 0 {name=p_cp_vss sig_type=std_logic lab=VSS}
C {loop_filter.sym} 100 -100 0 0 {name=x_loop_filter}
C {lab_pin.sym} 30 -100 0 0 {name=p_filter_vctrl sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} 100 -30 3 0 {name=p_filter_vss sig_type=std_logic lab=VSS}
C {ring_oscillator.sym} 300 -100 0 0 {name=x_vco}
C {lab_pin.sym} 180 -130 0 0 {name=p_vco_ctrl sig_type=std_logic lab=VCTRL}
C {lab_pin.sym} 420 -130 0 1 {name=p_vco_out sig_type=std_logic lab=VCO_CLK}
C {lab_pin.sym} 420 -110 0 1 {name=p_vco_vdd sig_type=std_logic lab=VDD}
C {lab_pin.sym} 420 -50 0 1 {name=p_vco_vss sig_type=std_logic lab=VSS}
C {feedback_divider.sym} 300 70 0 0 {name=x_feedback_divider}
C {lab_pin.sym} 230 70 0 0 {name=p_fb_vco sig_type=std_logic lab=VCO_CLK}
C {lab_pin.sym} 370 70 0 1 {name=p_fb_out sig_type=std_logic lab=FB_CLK}
C {output_divider.sym} 520 -100 0 0 {name=x_output_divider}
C {lab_pin.sym} 450 -100 0 0 {name=p_out_vco sig_type=std_logic lab=VCO_CLK}
C {lab_pin.sym} 590 -120 0 1 {name=p_pll_clk sig_type=std_logic lab=PLL_CLK}
C {lab_pin.sym} 590 -80 0 1 {name=p_test_clk sig_type=std_logic lab=TEST_CLK}
C {ipin.sym} -500 -120 0 0 {name=p_REF_CLK lab=REF_CLK}
C {iopin.sym} -500 -60 2 0 {name=p_IREF lab=IREF}
C {ipin.sym} -500 20 0 0 {name=p_ENABLE lab=ENABLE}
C {ipin.sym} -500 50 0 0 {name=p_RESET_N lab=RESET_N}
C {ipin.sym} -500 80 0 0 {name=p_DIV_INT lab=DIV_INT[6:0]}
C {ipin.sym} -500 110 0 0 {name=p_DIV_FRAC lab=DIV_FRAC[15:0]}
C {ipin.sym} -500 140 0 0 {name=p_TEST_DIV lab=TEST_DIV[1:0]}
C {opin.sym} 700 -120 0 0 {name=p_PLL_CLK lab=PLL_CLK}
C {opin.sym} 700 -80 0 0 {name=p_TEST_CLK lab=TEST_CLK}
C {iopin.sym} 0 -260 3 0 {name=p_VDD lab=VDD}
C {iopin.sym} 0 180 1 0 {name=p_VSS lab=VSS}
