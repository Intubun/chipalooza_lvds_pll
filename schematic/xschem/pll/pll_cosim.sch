v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Configurable RTL/transistor PLL co-simulation hierarchy.
pll_digital.v is loaded through ngspice d_cosim; pll_analog.sch remains hierarchical.} -430 -300 0 0 0.3 0.3 {}
C {pll_digital_cosim.sym} -120 -40 0 0 {name=a_digital model=pll_digital_cosim
device_model=".model pll_digital_cosim d_cosim simulation=\"./pll_digital_cosim.so\" delay=0"}
C {lab_pin.sym} -230 -120 0 0 {name=p_d_ref sig_type=std_logic lab=REF_CLK}
C {lab_pin.sym} -230 -100 0 0 {name=p_d_vco sig_type=std_logic lab=VCO_CLK}
C {lab_pin.sym} -230 -80 0 0 {name=p_d_reset sig_type=std_logic lab=RESET_N}
C {lab_pin.sym} -230 -60 0 0 {name=p_d_enable sig_type=std_logic lab=ENABLE}
C {lab_pin.sym} -230 -40 0 0 {name=p_d_int sig_type=std_logic lab=DIV_INT[6..0]}
C {lab_pin.sym} -230 -20 0 0 {name=p_d_frac sig_type=std_logic lab=DIV_FRAC[15..0]}
C {lab_pin.sym} -230 0 0 0 {name=p_d_test_div sig_type=std_logic lab=TEST_DIV[1..0]}
C {lab_pin.sym} -10 -120 0 1 {name=p_d_fb sig_type=std_logic lab=FB_CLK}
C {lab_pin.sym} -10 -80 0 1 {name=p_d_pll sig_type=std_logic lab=PLL_CLK}
C {lab_pin.sym} -10 -40 0 1 {name=p_d_test sig_type=std_logic lab=TEST_CLK}
C {lab_pin.sym} -10 0 0 1 {name=p_d_up sig_type=std_logic lab=UP}
C {lab_pin.sym} -10 40 0 1 {name=p_d_down sig_type=std_logic lab=DOWN}
C {pll_analog.sym} 180 -40 0 0 {name=x_analog}
C {lab_pin.sym} 80 -80 0 0 {name=p_a_up sig_type=std_logic lab=UP}
C {lab_pin.sym} 80 -40 0 0 {name=p_a_down sig_type=std_logic lab=DOWN}
C {lab_pin.sym} 80 0 0 0 {name=p_a_iref sig_type=std_logic lab=IREF}
C {lab_pin.sym} 280 -80 0 1 {name=p_a_vco sig_type=std_logic lab=VCO_CLK}
C {lab_pin.sym} 160 -120 1 0 {name=p_a_vdd sig_type=std_logic lab=VDD}
C {lab_pin.sym} 200 40 3 0 {name=p_a_vss sig_type=std_logic lab=VSS}
C {ipin.sym} -430 -120 0 0 {name=p_REF_CLK lab=REF_CLK}
C {iopin.sym} -430 -80 2 0 {name=p_IREF lab=IREF}
C {ipin.sym} -430 -40 0 0 {name=p_ENABLE lab=ENABLE}
C {ipin.sym} -430 -10 0 0 {name=p_RESET_N lab=RESET_N}
C {ipin.sym} -430 20 0 0 {name=p_DIV_INT lab=DIV_INT[6..0]}
C {ipin.sym} -430 50 0 0 {name=p_DIV_FRAC lab=DIV_FRAC[15..0]}
C {ipin.sym} -430 80 0 0 {name=p_TEST_DIV lab=TEST_DIV[1..0]}
C {opin.sym} 420 -80 0 0 {name=p_PLL_CLK lab=PLL_CLK}
C {opin.sym} 420 -40 0 0 {name=p_TEST_CLK lab=TEST_CLK}
C {iopin.sym} 0 -220 3 0 {name=p_VDD lab=VDD}
C {iopin.sym} 0 140 1 0 {name=p_VSS lab=VSS}
