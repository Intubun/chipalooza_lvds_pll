v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Mixed-signal output-divider model.
PLL_CLK is VCO/2; TEST_CLK defaults to VCO/4 for pad-safe simulation.} -250 -190 0 0 0.3 0.3 {}
N -220 0 -150 0 {lab=VCO_IN}
N 170 -40 240 -40 {lab=PLL_CLK}
N 170 40 240 40 {lab=TEST_CLK}
C {adc_bridge.sym} -120 0 0 0 {name=A_ADC adc_bridge_model=pll_out_adc}
C {lab_pin.sym} -90 0 0 1 {name=p_dvco sig_type=std_logic lab=dvco_out}
C {d_fdiv.sym} 0 -40 0 0 {name=A_PLL_DIV divider_model=pll_out_div2}
C {lab_pin.sym} -60 -40 0 0 {name=p_pll_in sig_type=std_logic lab=dvco_out}
C {lab_pin.sym} 60 -40 0 1 {name=p_dpll sig_type=std_logic lab=dpll}
C {dac_bridge.sym} 140 -40 0 0 {name=A_PLL_DAC dac_bridge_model=pll_out_dac}
C {lab_pin.sym} 110 -40 0 0 {name=p_pll_dac sig_type=std_logic lab=dpll}
C {d_fdiv.sym} 0 40 0 0 {name=A_TEST_DIV divider_model=pll_out_div4}
C {lab_pin.sym} -60 40 0 0 {name=p_test_in sig_type=std_logic lab=dvco_out}
C {lab_pin.sym} 60 40 0 1 {name=p_dtest sig_type=std_logic lab=dtest}
C {dac_bridge.sym} 140 40 0 0 {name=A_TEST_DAC dac_bridge_model=pll_out_dac}
C {lab_pin.sym} 110 40 0 0 {name=p_test_dac sig_type=std_logic lab=dtest}
C {ipin.sym} -220 0 0 0 {name=p_VCO_IN lab=VCO_IN}
C {opin.sym} 240 -40 0 0 {name=p_PLL_CLK lab=PLL_CLK}
C {opin.sym} 240 40 0 0 {name=p_TEST_CLK lab=TEST_CLK}
C {simulator_commands_shown.sym} -250 110 0 0 {name=MODELS
simulator=ngspice
only_toplevel=false
value="
.model pll_out_adc adc_bridge(in_low=0.3 in_high=0.9 rise_delay=5p fall_delay=5p)
.model pll_out_dac dac_bridge(out_low=0 out_high=1.2 out_undef=0.6 input_load=1p t_rise=20p t_fall=20p)
.model pll_out_div2 d_fdiv(div_factor=2 high_cycles=1 i_count=0 rise_delay=5p fall_delay=5p freq_in_load=1p)
.model pll_out_div4 d_fdiv(div_factor=4 high_cycles=2 i_count=0 rise_delay=5p fall_delay=5p freq_in_load=1p)
"}
