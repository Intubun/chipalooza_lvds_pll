v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {VCO/2 PLL output and VCO/4 test-output divider testbench.} -240 -200 0 0 0.3 0.3 {}
B 2 200 -160 780 170 {flags=graph
y1=-0.1
y2=1.3
ypos1=0
ypos2=2
divy=7
subdivy=1
unity=1
x1=0
x2=1.5e-08
divx=6
subdivx=1
node="VCO_IN
PLL_CLK
TEST_CLK"
color="4 5 6"
dataset=-1
unitx=1
logx=0
logy=0}
C {output_divider.sym} 0 0 0 0 {name=x_div}
C {lab_pin.sym} -70 0 0 0 {name=p_vco sig_type=std_logic lab=VCO_IN}
C {lab_pin.sym} 70 -20 0 1 {name=p_pll sig_type=std_logic lab=PLL_CLK}
C {lab_pin.sym} 70 20 0 1 {name=p_test sig_type=std_logic lab=TEST_CLK}
C {vsource.sym} -150 30 0 0 {name=VVCO value="PULSE(0 1.2 1n 20p 20p 230p 500p)" savecurrent=false}
C {lab_pin.sym} -150 0 1 0 {name=p_vco_src sig_type=std_logic lab=VCO_IN}
C {gnd.sym} -150 60 0 0 {name=l_vco_src lab=0}
C {simulator_commands_shown.sym} -240 100 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.control
save all
tran 1p 15n
meas tran pll_t1 when v(PLL_CLK)=0.6 rise=3
meas tran pll_t2 when v(PLL_CLK)=0.6 rise=4
meas tran test_t1 when v(TEST_CLK)=0.6 rise=2
meas tran test_t2 when v(TEST_CLK)=0.6 rise=3
let pll_period=pll_t2-pll_t1
let test_period=test_t2-test_t1
print pll_period test_period
write output_divider.tb.raw
.endc
"}
