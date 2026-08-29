v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Configurable Verilator/ngspice co-simulation testbench.
Default: 100 MHz reference, integer N=20, 1 GHz PLL output.} -390 -350 0 0 0.3 0.3 {}
C {pll_cosim.sym} 0 0 0 0 {name=x_pll}
C {lab_pin.sym} -100 -60 0 0 {name=p_ref sig_type=std_logic lab=REF_CLK}
C {lab_pin.sym} -100 -40 0 0 {name=p_iref sig_type=std_logic lab=IREF}
C {lab_pin.sym} -100 -20 0 0 {name=p_enable sig_type=std_logic lab=ENABLE}
C {lab_pin.sym} -100 0 0 0 {name=p_reset sig_type=std_logic lab=RESET_N}
C {lab_pin.sym} -100 20 0 0 {name=p_div_int sig_type=std_logic lab=DIV_INT[6..0]}
C {lab_pin.sym} -100 40 0 0 {name=p_div_frac sig_type=std_logic lab=DIV_FRAC[15..0]}
C {lab_pin.sym} -100 60 0 0 {name=p_test_div sig_type=std_logic lab=TEST_DIV[1..0]}
C {lab_pin.sym} 100 -20 0 1 {name=p_pll_clk sig_type=std_logic lab=PLL_CLK}
C {lab_pin.sym} 100 20 0 1 {name=p_test_clk sig_type=std_logic lab=TEST_CLK}
C {lab_pin.sym} -20 -100 1 0 {name=p_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 20 100 0 0 {name=l_vss lab=0}
C {vsource.sym} -300 -90 0 0 {name=VREF value="PULSE(0 1.2 1n 20p 20p 4.98n 10n)" savecurrent=false}
C {lab_pin.sym} -300 -120 1 0 {name=p_ref_src sig_type=std_logic lab=REF_CLK}
C {gnd.sym} -300 -60 0 0 {name=l_ref_src lab=0}
C {isource.sym} -210 -90 0 0 {name=IREF_SRC value=-2u}
C {lab_pin.sym} -210 -120 1 0 {name=p_iref_src sig_type=std_logic lab=IREF}
C {gnd.sym} -210 -60 0 0 {name=l_iref_src lab=0}
C {vsource.sym} -300 50 0 0 {name=VDD_SRC value=1.2 savecurrent=true}
C {lab_pin.sym} -300 20 1 0 {name=p_vdd_src sig_type=std_logic lab=VDD}
C {gnd.sym} -300 80 0 0 {name=l_vdd_src lab=0}
C {vsource.sym} -210 50 0 0 {name=VENABLE value=1.2 savecurrent=false}
C {lab_pin.sym} -210 20 1 0 {name=p_enable_src sig_type=std_logic lab=ENABLE}
C {gnd.sym} -210 80 0 0 {name=l_enable_src lab=0}
C {vsource.sym} -120 150 0 0 {name=VRESET value="PULSE(0 1.2 2n 20p 20p 20u 40u)" savecurrent=false}
C {lab_pin.sym} -120 120 1 0 {name=p_reset_src sig_type=std_logic lab=RESET_N}
C {gnd.sym} -120 180 0 0 {name=l_reset_src lab=0}
C {capa.sym} 150 -20 0 0 {name=CPLL m=1 value=5f footprint=1206 device="ceramic capacitor"}
C {lab_pin.sym} 150 -50 1 0 {name=p_pll_load sig_type=std_logic lab=PLL_CLK}
C {gnd.sym} 150 10 0 0 {name=l_pll_load lab=0}
C {capa.sym} 210 20 0 0 {name=CTEST m=1 value=5f footprint=1206 device="ceramic capacitor"}
C {lab_pin.sym} 210 -10 1 0 {name=p_test_load sig_type=std_logic lab=TEST_CLK}
C {gnd.sym} 210 50 0 0 {name=l_test_load lab=0}
C {simulator_commands_shown.sym} -390 150 0 0 {name=Libs_Ngspice simulator=ngspice only_toplevel=false value="
.lib cornerMOSlv.lib mos_tt
VDIV_INT6 DIV_INT6 0 0
VDIV_INT5 DIV_INT5 0 0
VDIV_INT4 DIV_INT4 0 1.2
VDIV_INT3 DIV_INT3 0 0
VDIV_INT2 DIV_INT2 0 1.2
VDIV_INT1 DIV_INT1 0 0
VDIV_INT0 DIV_INT0 0 0
VDIV_FRAC15 DIV_FRAC15 0 0
VDIV_FRAC14 DIV_FRAC14 0 0
VDIV_FRAC13 DIV_FRAC13 0 0
VDIV_FRAC12 DIV_FRAC12 0 0
VDIV_FRAC11 DIV_FRAC11 0 0
VDIV_FRAC10 DIV_FRAC10 0 0
VDIV_FRAC9 DIV_FRAC9 0 0
VDIV_FRAC8 DIV_FRAC8 0 0
VDIV_FRAC7 DIV_FRAC7 0 0
VDIV_FRAC6 DIV_FRAC6 0 0
VDIV_FRAC5 DIV_FRAC5 0 0
VDIV_FRAC4 DIV_FRAC4 0 0
VDIV_FRAC3 DIV_FRAC3 0 0
VDIV_FRAC2 DIV_FRAC2 0 0
VDIV_FRAC1 DIV_FRAC1 0 0
VDIV_FRAC0 DIV_FRAC0 0 0
VTEST_DIV1 TEST_DIV1 0 0
VTEST_DIV0 TEST_DIV0 0 1.2
"}
C {simulator_commands_shown.sym} 270 100 0 0 {name=SimulatorNGSPICE simulator=ngspice only_toplevel=false value="
.options temp=27
.ic v(x_pll.x_analog.x_vco.VCO_CORE)=0 v(x_pll.x_analog.x_vco.net1)=1.2 v(x_pll.x_analog.x_vco.net2)=0
.control
pre_set auto_bridge_d_in =
+ ( \\".model auto_adc adc_bridge(
+   in_low=0.3 in_high=0.9 rise_delay=5p fall_delay=5p )\\"
+ \\"auto_bridge%d [ %s ] [ %s ] auto_adc\\" )
pre_set auto_bridge_d_out =
+ ( \\".model auto_dac dac_bridge(
+   out_low=0 out_high=1.2 t_rise=20p t_fall=20p )\\"
+ \\"auto_bridge%d [ %s ] [ %s ] auto_dac\\" )
save v(REF_CLK) v(PLL_CLK) v(TEST_CLK) v(x_pll.VCO_CLK) v(x_pll.x_analog.VCTRL) i(VDD_SRC)
tran 5p 10u uic
meas tran pll_t1 when v(PLL_CLK)=0.6 rise=1 TD=8u
meas tran pll_t101 when v(PLL_CLK)=0.6 rise=101 TD=8u
meas tran vctrl_avg avg v(x_pll.x_analog.VCTRL) from=8u to=10u
let pll_frequency=100/(pll_t101-pll_t1)
print pll_frequency vctrl_avg
.endc
"}
