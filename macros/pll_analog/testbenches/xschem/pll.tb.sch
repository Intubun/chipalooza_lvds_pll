v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Nominal closed-loop PLL testbench.
100 MHz reference, N=20 feedback model, 2 GHz VCO target, and 1 GHz PLL output.} -360 -330 0 0 0.3 0.3 {}
B 2 260 -250 940 250 {flags=graph
y1=-0.1
y2=1.3
ypos1=0
ypos2=2
divy=7
subdivy=1
unity=1
x1=8e-06
x2=8.1e-06
divx=5
subdivx=1
node="REF_CLK
PLL_CLK
TEST_CLK
x_pll.VCTRL"
color="4 5 6 7"
dataset=-1
unitx=1
logx=0
logy=0}
C {pll.sym} 0 0 0 0 {name=x_pll}
C {lab_pin.sym} -100 -60 0 0 {name=p_ref sig_type=std_logic lab=REF_CLK}
C {lab_pin.sym} -100 -40 0 0 {name=p_iref sig_type=std_logic lab=IREF}
C {lab_pin.sym} -100 -20 0 0 {name=p_enable sig_type=std_logic lab=ENABLE}
C {lab_pin.sym} -100 0 0 0 {name=p_reset sig_type=std_logic lab=RESET_N}
C {lab_pin.sym} -100 20 0 0 {name=p_div_ratio sig_type=std_logic lab=DIV_RATIO[9:0]}
C {lab_pin.sym} -100 60 0 0 {name=p_test_div sig_type=std_logic lab=TEST_DIV[1:0]}
C {lab_pin.sym} 100 -20 0 1 {name=p_pll_clk sig_type=std_logic lab=PLL_CLK}
C {lab_pin.sym} 100 20 0 1 {name=p_test_clk sig_type=std_logic lab=TEST_CLK}
C {lab_pin.sym} -20 -100 1 0 {name=p_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 20 100 0 0 {name=l_vss lab=0}
C {vsource.sym} -280 -80 0 0 {name=VREF value="PULSE(0 1.2 1n 20p 20p 4.98n 10n)" savecurrent=false}
C {lab_pin.sym} -280 -110 1 0 {name=p_ref_src sig_type=std_logic lab=REF_CLK}
C {gnd.sym} -280 -50 0 0 {name=l_ref_src lab=0}
C {isource.sym} -190 -80 0 0 {name=IREF_SRC value=-2u}
C {lab_pin.sym} -190 -110 1 0 {name=p_iref_src sig_type=std_logic lab=IREF}
C {gnd.sym} -190 -50 0 0 {name=l_iref_src lab=0}
C {vsource.sym} -280 60 0 0 {name=VDD_SRC value=1.2 savecurrent=true}
C {lab_pin.sym} -280 30 1 0 {name=p_vdd_src sig_type=std_logic lab=VDD}
C {gnd.sym} -280 90 0 0 {name=l_vdd_src lab=0}
C {vsource.sym} -190 60 0 0 {name=VENABLE value=1.2 savecurrent=false}
C {lab_pin.sym} -190 30 1 0 {name=p_enable_src sig_type=std_logic lab=ENABLE}
C {gnd.sym} -190 90 0 0 {name=l_enable_src lab=0}
C {vsource.sym} -100 160 0 0 {name=VRESET value=1.2 savecurrent=false}
C {lab_pin.sym} -100 130 1 0 {name=p_reset_src sig_type=std_logic lab=RESET_N}
C {gnd.sym} -100 190 0 0 {name=l_reset_src lab=0}
C {capa.sym} 160 -20 0 0 {name=CPLL
m=1
value=5f
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} 160 -50 1 0 {name=p_pll_load sig_type=std_logic lab=PLL_CLK}
C {gnd.sym} 160 10 0 0 {name=l_pll_load lab=0}
C {capa.sym} 210 20 0 0 {name=CTEST
m=1
value=5f
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} 210 -10 1 0 {name=p_test_load sig_type=std_logic lab=TEST_CLK}
C {gnd.sym} 210 50 0 0 {name=l_test_load lab=0}
C {simulator_commands_shown.sym} -360 150 0 0 {name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOSlv.lib mos_tt
"}
C {simulator_commands_shown.sym} -360 260 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.ic v(x_pll.x_vco.VCO_CORE)=0 v(x_pll.x_vco.net1)=1.2 v(x_pll.x_vco.net2)=0
.control
save v(REF_CLK) v(PLL_CLK) v(TEST_CLK) v(x_pll.VCO_CLK) v(x_pll.FB_CLK) v(x_pll.VCTRL) i(VDD_SRC)
tran 5p 10u uic
meas tran pll_t1 when v(PLL_CLK)=0.6 rise=1 TD=8u
meas tran pll_t2 when v(PLL_CLK)=0.6 rise=2 TD=8u
meas tran vco_t1 when v(x_pll.VCO_CLK)=0.6 rise=1 TD=8u
meas tran vco_t2 when v(x_pll.VCO_CLK)=0.6 rise=2 TD=8u
meas tran vctrl_avg avg v(x_pll.VCTRL) from=8u to=10u
meas tran idd_avg avg i(VDD_SRC) from=8u to=10u
let pll_frequency=1/(pll_t2-pll_t1)
let vco_frequency=1/(vco_t2-vco_t1)
print pll_frequency vco_frequency vctrl_avg idd_avg
write pll.tb.raw
.endc
"}
C {launcher.sym} -60 240 0 0 {name=h_simulate
descr=SimulateNGSPICE
tclcommand="
set_sim_defaults
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}
set sim(spice,default) 0
file mkdir $netlist_dir
xschem netlist
simulate
"}
C {launcher.sym} -60 280 0 0 {name=h_waves
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/pll.tb.raw tran"
}
