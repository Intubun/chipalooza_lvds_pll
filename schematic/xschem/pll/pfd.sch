v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Resettable dual-DFF phase-frequency detector.
XSPICE digital core with analog 1.2 V interfaces.} -210 -250 0 0 0.3 0.3 {}
N -220 -80 -150 -80 {lab=REF}
N -220 80 -150 80 {lab=FB}
N -220 -160 -150 -160 {lab=VDD}
N -220 160 -150 160 {lab=VSS}
N 290 -80 350 -80 {lab=UP}
N 290 80 350 80 {lab=DOWN}
C {adc_bridge.sym} -120 -80 0 0 {name=A_REF adc_bridge_model=pll_adc}
C {adc_bridge.sym} -120 80 0 0 {name=A_FB adc_bridge_model=pll_adc}
C {adc_bridge.sym} -120 -160 0 0 {name=A_ONE adc_bridge_model=pll_adc}
C {adc_bridge.sym} -120 160 0 0 {name=A_ZERO adc_bridge_model=pll_adc}
C {d_dff.sym} 0 -80 0 0 {name=A_UP dff_model=pll_dff}
C {d_dff.sym} 0 80 0 0 {name=A_DOWN dff_model=pll_dff}
C {d_and2.sym} 120 0 0 0 {name=A_RESET and_model=pll_and}
C {dac_bridge.sym} 260 -80 0 0 {name=A_UP_DAC dac_bridge_model=pll_dac}
C {dac_bridge.sym} 260 80 0 0 {name=A_DOWN_DAC dac_bridge_model=pll_dac}
C {lab_pin.sym} -90 -80 0 1 {name=p_dref sig_type=std_logic lab=dref}
C {lab_pin.sym} -90 80 0 1 {name=p_dfb sig_type=std_logic lab=dfb}
C {lab_pin.sym} -90 -160 0 1 {name=p_done sig_type=std_logic lab=done}
C {lab_pin.sym} -90 160 0 1 {name=p_dzero sig_type=std_logic lab=dzero}
C {lab_pin.sym} -70 -110 0 0 {name=p_up_d sig_type=std_logic lab=done}
C {lab_pin.sym} -70 -90 0 0 {name=p_up_clk sig_type=std_logic lab=dref}
C {lab_pin.sym} -70 -70 0 0 {name=p_up_set sig_type=std_logic lab=dzero}
C {lab_pin.sym} -70 -50 0 0 {name=p_up_reset sig_type=std_logic lab=drst}
C {lab_pin.sym} 70 -100 0 1 {name=p_dup sig_type=std_logic lab=dup}
C {lab_pin.sym} -70 50 0 0 {name=p_down_d sig_type=std_logic lab=done}
C {lab_pin.sym} -70 70 0 0 {name=p_down_clk sig_type=std_logic lab=dfb}
C {lab_pin.sym} -70 90 0 0 {name=p_down_set sig_type=std_logic lab=dzero}
C {lab_pin.sym} -70 110 0 0 {name=p_down_reset sig_type=std_logic lab=drst}
C {lab_pin.sym} 70 60 0 1 {name=p_ddn sig_type=std_logic lab=ddn}
C {lab_pin.sym} 50 -10 0 0 {name=p_and_a sig_type=std_logic lab=dup}
C {lab_pin.sym} 50 10 0 0 {name=p_and_b sig_type=std_logic lab=ddn}
C {lab_pin.sym} 150 0 0 1 {name=p_drst sig_type=std_logic lab=drst}
C {lab_pin.sym} 230 -80 0 0 {name=p_up_dac sig_type=std_logic lab=dup}
C {lab_pin.sym} 230 80 0 0 {name=p_down_dac sig_type=std_logic lab=ddn}
C {ipin.sym} -220 -80 0 0 {name=p_REF lab=REF}
C {ipin.sym} -220 80 0 0 {name=p_FB lab=FB}
C {opin.sym} 350 -80 0 0 {name=p_UP lab=UP}
C {opin.sym} 350 80 0 0 {name=p_DOWN lab=DOWN}
C {iopin.sym} -220 -160 2 0 {name=p_VDD lab=VDD}
C {iopin.sym} -220 160 2 0 {name=p_VSS lab=VSS}
C {simulator_commands_shown.sym} -210 220 0 0 {name=MODELS
simulator=ngspice
only_toplevel=false
value="
.model pll_adc adc_bridge(in_low=0.3 in_high=0.9 rise_delay=5p fall_delay=5p)
.model pll_dac dac_bridge(out_low=0 out_high=1.2 out_undef=0.6 input_load=1p t_rise=20p t_fall=20p)
.model pll_dff d_dff(clk_delay=10p set_delay=10p reset_delay=20p ic=0 rise_delay=5p fall_delay=5p data_load=1p clk_load=1p set_load=1p reset_load=1p)
.model pll_and d_and(rise_delay=10p fall_delay=10p input_load=1p)
"}
