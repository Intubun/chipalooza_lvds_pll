v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {serdes  --  pattern generator and serializer in front of the LVDS transmitter

WHAT IS IN HERE: nothing but the mixed-signal boundary.  adc_bridge on the way
in, one d_cosim instance in the middle, dac_bridge on the way out.  All the
behaviour is Verilog, in serdes/serdes_dig.v, compiled by Verilator into
serdes/serdes_dig.so and loaded by ngspice through the XSPICE d_cosim code
model.  It runs inside the same transient analysis as the analog transmitter.

BUILD IT BEFORE SIMULATING, and again after every edit to the Verilog:

  docker exec iic-osic-tools_xserver bash -lc     /foss/designs/chipalooza_lvds_pll/macros/lvds_tx/serdes/build_dig.sh

ngspice loads the .so, never the .v, and an out-of-date .so simulates happily.

THE PIN LIST IS THE CHIPALOOZA #2 HARNESS SLOT: Clk, Ena, 24 digital inputs,
12 digital outputs, all 1.2 V.  Not a convenient set of signals -- the interface
the project has to fit when it is dropped into the harness.  Every DI bit is
routed there by the housekeeping SPI to a package pin, to a constant, or to the
harness sequencer, so a configuration bit costs a register write and nothing
else.  docs/harness-mapping.md is the map:

   DI7..DI0    parallel word, DI7 out first
   DI9,DI8     pattern: 0 word, 1 PRBS, 2 alternating, 3 static low
   DI11,DI10   PRBS length: 0 PRBS7, 1 PRBS9, 2 PRBS15, 3 PRBS31
   DI12        reset, synchronous, active high
   DI13        invert the output pair
   DI23..DI14  reserved, and zero is a working setting

   DO0         byte strobe, high for the bit carrying DI7
   DO1         byte clock, bit clock divided by eight
   DO11..DO2   zero

D_p / D_n are the serial data pair in the core domain, and they are the whole
analog interface: data and no timing.  No clock channel, and nothing derived
from the bit period -- the transmitter downstream is a plain differential
driver with no pre-emphasis and therefore nothing to time.

The dac_bridge model in the testbench sets the core-domain swing and edge rate
the pre-driver sees: out_low / out_high are the 1.2 V rails, t_rise and t_fall
the slew.  Those two numbers are the whole analog content of this block -- get
them wrong and every pre-driver measurement downstream is wrong.

THE d_cosim PORT LIST IS POSITIONAL.  The A-device net order below has to match
the Verilog port declaration order exactly, all inputs then all outputs, and a
vector port expands MSB first.  Nothing checks it at run time;
serdes/check_ports.py does, from build_dig.sh.} -1700 -1700 0 0 0.4 0.4 {}
N -1700 -400 -1660 -400 {lab=Clk}
C {ipin.sym} -1700 -400 0 0 {name=p1 lab=Clk}
N -1700 -300 -1660 -300 {lab=Ena}
C {ipin.sym} -1700 -300 0 0 {name=p2 lab=Ena}
N -1700 -200 -1660 -200 {lab=DI23}
C {ipin.sym} -1700 -200 0 0 {name=p3 lab=DI23}
N -1700 -100 -1660 -100 {lab=DI22}
C {ipin.sym} -1700 -100 0 0 {name=p4 lab=DI22}
N -1700 0 -1660 0 {lab=DI21}
C {ipin.sym} -1700 0 0 0 {name=p5 lab=DI21}
N -1700 100 -1660 100 {lab=DI20}
C {ipin.sym} -1700 100 0 0 {name=p6 lab=DI20}
N -1700 200 -1660 200 {lab=DI19}
C {ipin.sym} -1700 200 0 0 {name=p7 lab=DI19}
N -1700 300 -1660 300 {lab=DI18}
C {ipin.sym} -1700 300 0 0 {name=p8 lab=DI18}
N -1700 400 -1660 400 {lab=DI17}
C {ipin.sym} -1700 400 0 0 {name=p9 lab=DI17}
N -1700 500 -1660 500 {lab=DI16}
C {ipin.sym} -1700 500 0 0 {name=p10 lab=DI16}
N -1700 600 -1660 600 {lab=DI15}
C {ipin.sym} -1700 600 0 0 {name=p11 lab=DI15}
N -1700 700 -1660 700 {lab=DI14}
C {ipin.sym} -1700 700 0 0 {name=p12 lab=DI14}
N -1700 800 -1660 800 {lab=DI13}
C {ipin.sym} -1700 800 0 0 {name=p13 lab=DI13}
N -1700 900 -1660 900 {lab=DI12}
C {ipin.sym} -1700 900 0 0 {name=p14 lab=DI12}
N -1700 1000 -1660 1000 {lab=DI11}
C {ipin.sym} -1700 1000 0 0 {name=p15 lab=DI11}
N -1700 1100 -1660 1100 {lab=DI10}
C {ipin.sym} -1700 1100 0 0 {name=p16 lab=DI10}
N -1700 1200 -1660 1200 {lab=DI9}
C {ipin.sym} -1700 1200 0 0 {name=p17 lab=DI9}
N -1700 1300 -1660 1300 {lab=DI8}
C {ipin.sym} -1700 1300 0 0 {name=p18 lab=DI8}
N -1700 1400 -1660 1400 {lab=DI7}
C {ipin.sym} -1700 1400 0 0 {name=p19 lab=DI7}
N -1700 1500 -1660 1500 {lab=DI6}
C {ipin.sym} -1700 1500 0 0 {name=p20 lab=DI6}
N -1700 1600 -1660 1600 {lab=DI5}
C {ipin.sym} -1700 1600 0 0 {name=p21 lab=DI5}
N -1700 1700 -1660 1700 {lab=DI4}
C {ipin.sym} -1700 1700 0 0 {name=p22 lab=DI4}
N -1700 1800 -1660 1800 {lab=DI3}
C {ipin.sym} -1700 1800 0 0 {name=p23 lab=DI3}
N -1700 1900 -1660 1900 {lab=DI2}
C {ipin.sym} -1700 1900 0 0 {name=p24 lab=DI2}
N -1700 2000 -1660 2000 {lab=DI1}
C {ipin.sym} -1700 2000 0 0 {name=p25 lab=DI1}
N -1700 2100 -1660 2100 {lab=DI0}
C {ipin.sym} -1700 2100 0 0 {name=p26 lab=DI0}
N 1700 -300 1660 -300 {lab=D_p}
C {opin.sym} 1700 -300 0 0 {name=p27 lab=D_p}
N 1700 -200 1660 -200 {lab=D_n}
C {opin.sym} 1700 -200 0 0 {name=p28 lab=D_n}
N 1700 -100 1660 -100 {lab=DO11}
C {opin.sym} 1700 -100 0 0 {name=p29 lab=DO11}
N 1700 0 1660 0 {lab=DO10}
C {opin.sym} 1700 0 0 0 {name=p30 lab=DO10}
N 1700 100 1660 100 {lab=DO9}
C {opin.sym} 1700 100 0 0 {name=p31 lab=DO9}
N 1700 200 1660 200 {lab=DO8}
C {opin.sym} 1700 200 0 0 {name=p32 lab=DO8}
N 1700 300 1660 300 {lab=DO7}
C {opin.sym} 1700 300 0 0 {name=p33 lab=DO7}
N 1700 400 1660 400 {lab=DO6}
C {opin.sym} 1700 400 0 0 {name=p34 lab=DO6}
N 1700 500 1660 500 {lab=DO5}
C {opin.sym} 1700 500 0 0 {name=p35 lab=DO5}
N 1700 600 1660 600 {lab=DO4}
C {opin.sym} 1700 600 0 0 {name=p36 lab=DO4}
N 1700 700 1660 700 {lab=DO3}
C {opin.sym} 1700 700 0 0 {name=p37 lab=DO3}
N 1700 800 1660 800 {lab=DO2}
C {opin.sym} 1700 800 0 0 {name=p38 lab=DO2}
N 1700 900 1660 900 {lab=DO1}
C {opin.sym} 1700 900 0 0 {name=p39 lab=DO1}
N 1700 1000 1660 1000 {lab=DO0}
C {opin.sym} 1700 1000 0 0 {name=p40 lab=DO0}
C {adc_bridge.sym} -1200 -400 0 0 {name=A100 adc_bridge_model=adc_1}
N -1230 -400 -1270 -400 {lab=Clk}
C {lab_pin.sym} -1270 -400 0 1 {name=l41 lab=Clk}
N -1170 -400 -1130 -400 {lab=dclk}
C {lab_pin.sym} -1130 -400 0 0 {name=l42 lab=dclk}
C {adc_bridge.sym} -1200 -300 0 0 {name=A101 adc_bridge_model=adc_1}
N -1230 -300 -1270 -300 {lab=Ena}
C {lab_pin.sym} -1270 -300 0 1 {name=l43 lab=Ena}
N -1170 -300 -1130 -300 {lab=dena}
C {lab_pin.sym} -1130 -300 0 0 {name=l44 lab=dena}
C {adc_bridge.sym} -1200 -200 0 0 {name=A102 adc_bridge_model=adc_1}
N -1230 -200 -1270 -200 {lab=DI23}
C {lab_pin.sym} -1270 -200 0 1 {name=l45 lab=DI23}
N -1170 -200 -1130 -200 {lab=ddi23}
C {lab_pin.sym} -1130 -200 0 0 {name=l46 lab=ddi23}
C {adc_bridge.sym} -1200 -100 0 0 {name=A103 adc_bridge_model=adc_1}
N -1230 -100 -1270 -100 {lab=DI22}
C {lab_pin.sym} -1270 -100 0 1 {name=l47 lab=DI22}
N -1170 -100 -1130 -100 {lab=ddi22}
C {lab_pin.sym} -1130 -100 0 0 {name=l48 lab=ddi22}
C {adc_bridge.sym} -1200 0 0 0 {name=A104 adc_bridge_model=adc_1}
N -1230 0 -1270 0 {lab=DI21}
C {lab_pin.sym} -1270 0 0 1 {name=l49 lab=DI21}
N -1170 0 -1130 0 {lab=ddi21}
C {lab_pin.sym} -1130 0 0 0 {name=l50 lab=ddi21}
C {adc_bridge.sym} -1200 100 0 0 {name=A105 adc_bridge_model=adc_1}
N -1230 100 -1270 100 {lab=DI20}
C {lab_pin.sym} -1270 100 0 1 {name=l51 lab=DI20}
N -1170 100 -1130 100 {lab=ddi20}
C {lab_pin.sym} -1130 100 0 0 {name=l52 lab=ddi20}
C {adc_bridge.sym} -1200 200 0 0 {name=A106 adc_bridge_model=adc_1}
N -1230 200 -1270 200 {lab=DI19}
C {lab_pin.sym} -1270 200 0 1 {name=l53 lab=DI19}
N -1170 200 -1130 200 {lab=ddi19}
C {lab_pin.sym} -1130 200 0 0 {name=l54 lab=ddi19}
C {adc_bridge.sym} -1200 300 0 0 {name=A107 adc_bridge_model=adc_1}
N -1230 300 -1270 300 {lab=DI18}
C {lab_pin.sym} -1270 300 0 1 {name=l55 lab=DI18}
N -1170 300 -1130 300 {lab=ddi18}
C {lab_pin.sym} -1130 300 0 0 {name=l56 lab=ddi18}
C {adc_bridge.sym} -1200 400 0 0 {name=A108 adc_bridge_model=adc_1}
N -1230 400 -1270 400 {lab=DI17}
C {lab_pin.sym} -1270 400 0 1 {name=l57 lab=DI17}
N -1170 400 -1130 400 {lab=ddi17}
C {lab_pin.sym} -1130 400 0 0 {name=l58 lab=ddi17}
C {adc_bridge.sym} -1200 500 0 0 {name=A109 adc_bridge_model=adc_1}
N -1230 500 -1270 500 {lab=DI16}
C {lab_pin.sym} -1270 500 0 1 {name=l59 lab=DI16}
N -1170 500 -1130 500 {lab=ddi16}
C {lab_pin.sym} -1130 500 0 0 {name=l60 lab=ddi16}
C {adc_bridge.sym} -1200 600 0 0 {name=A110 adc_bridge_model=adc_1}
N -1230 600 -1270 600 {lab=DI15}
C {lab_pin.sym} -1270 600 0 1 {name=l61 lab=DI15}
N -1170 600 -1130 600 {lab=ddi15}
C {lab_pin.sym} -1130 600 0 0 {name=l62 lab=ddi15}
C {adc_bridge.sym} -1200 700 0 0 {name=A111 adc_bridge_model=adc_1}
N -1230 700 -1270 700 {lab=DI14}
C {lab_pin.sym} -1270 700 0 1 {name=l63 lab=DI14}
N -1170 700 -1130 700 {lab=ddi14}
C {lab_pin.sym} -1130 700 0 0 {name=l64 lab=ddi14}
C {adc_bridge.sym} -1200 800 0 0 {name=A112 adc_bridge_model=adc_1}
N -1230 800 -1270 800 {lab=DI13}
C {lab_pin.sym} -1270 800 0 1 {name=l65 lab=DI13}
N -1170 800 -1130 800 {lab=ddi13}
C {lab_pin.sym} -1130 800 0 0 {name=l66 lab=ddi13}
C {adc_bridge.sym} -1200 900 0 0 {name=A113 adc_bridge_model=adc_1}
N -1230 900 -1270 900 {lab=DI12}
C {lab_pin.sym} -1270 900 0 1 {name=l67 lab=DI12}
N -1170 900 -1130 900 {lab=ddi12}
C {lab_pin.sym} -1130 900 0 0 {name=l68 lab=ddi12}
C {adc_bridge.sym} -1200 1000 0 0 {name=A114 adc_bridge_model=adc_1}
N -1230 1000 -1270 1000 {lab=DI11}
C {lab_pin.sym} -1270 1000 0 1 {name=l69 lab=DI11}
N -1170 1000 -1130 1000 {lab=ddi11}
C {lab_pin.sym} -1130 1000 0 0 {name=l70 lab=ddi11}
C {adc_bridge.sym} -1200 1100 0 0 {name=A115 adc_bridge_model=adc_1}
N -1230 1100 -1270 1100 {lab=DI10}
C {lab_pin.sym} -1270 1100 0 1 {name=l71 lab=DI10}
N -1170 1100 -1130 1100 {lab=ddi10}
C {lab_pin.sym} -1130 1100 0 0 {name=l72 lab=ddi10}
C {adc_bridge.sym} -1200 1200 0 0 {name=A116 adc_bridge_model=adc_1}
N -1230 1200 -1270 1200 {lab=DI9}
C {lab_pin.sym} -1270 1200 0 1 {name=l73 lab=DI9}
N -1170 1200 -1130 1200 {lab=ddi9}
C {lab_pin.sym} -1130 1200 0 0 {name=l74 lab=ddi9}
C {adc_bridge.sym} -1200 1300 0 0 {name=A117 adc_bridge_model=adc_1}
N -1230 1300 -1270 1300 {lab=DI8}
C {lab_pin.sym} -1270 1300 0 1 {name=l75 lab=DI8}
N -1170 1300 -1130 1300 {lab=ddi8}
C {lab_pin.sym} -1130 1300 0 0 {name=l76 lab=ddi8}
C {adc_bridge.sym} -1200 1400 0 0 {name=A118 adc_bridge_model=adc_1}
N -1230 1400 -1270 1400 {lab=DI7}
C {lab_pin.sym} -1270 1400 0 1 {name=l77 lab=DI7}
N -1170 1400 -1130 1400 {lab=ddi7}
C {lab_pin.sym} -1130 1400 0 0 {name=l78 lab=ddi7}
C {adc_bridge.sym} -1200 1500 0 0 {name=A119 adc_bridge_model=adc_1}
N -1230 1500 -1270 1500 {lab=DI6}
C {lab_pin.sym} -1270 1500 0 1 {name=l79 lab=DI6}
N -1170 1500 -1130 1500 {lab=ddi6}
C {lab_pin.sym} -1130 1500 0 0 {name=l80 lab=ddi6}
C {adc_bridge.sym} -1200 1600 0 0 {name=A120 adc_bridge_model=adc_1}
N -1230 1600 -1270 1600 {lab=DI5}
C {lab_pin.sym} -1270 1600 0 1 {name=l81 lab=DI5}
N -1170 1600 -1130 1600 {lab=ddi5}
C {lab_pin.sym} -1130 1600 0 0 {name=l82 lab=ddi5}
C {adc_bridge.sym} -1200 1700 0 0 {name=A121 adc_bridge_model=adc_1}
N -1230 1700 -1270 1700 {lab=DI4}
C {lab_pin.sym} -1270 1700 0 1 {name=l83 lab=DI4}
N -1170 1700 -1130 1700 {lab=ddi4}
C {lab_pin.sym} -1130 1700 0 0 {name=l84 lab=ddi4}
C {adc_bridge.sym} -1200 1800 0 0 {name=A122 adc_bridge_model=adc_1}
N -1230 1800 -1270 1800 {lab=DI3}
C {lab_pin.sym} -1270 1800 0 1 {name=l85 lab=DI3}
N -1170 1800 -1130 1800 {lab=ddi3}
C {lab_pin.sym} -1130 1800 0 0 {name=l86 lab=ddi3}
C {adc_bridge.sym} -1200 1900 0 0 {name=A123 adc_bridge_model=adc_1}
N -1230 1900 -1270 1900 {lab=DI2}
C {lab_pin.sym} -1270 1900 0 1 {name=l87 lab=DI2}
N -1170 1900 -1130 1900 {lab=ddi2}
C {lab_pin.sym} -1130 1900 0 0 {name=l88 lab=ddi2}
C {adc_bridge.sym} -1200 2000 0 0 {name=A124 adc_bridge_model=adc_1}
N -1230 2000 -1270 2000 {lab=DI1}
C {lab_pin.sym} -1270 2000 0 1 {name=l89 lab=DI1}
N -1170 2000 -1130 2000 {lab=ddi1}
C {lab_pin.sym} -1130 2000 0 0 {name=l90 lab=ddi1}
C {adc_bridge.sym} -1200 2100 0 0 {name=A125 adc_bridge_model=adc_1}
N -1230 2100 -1270 2100 {lab=DI0}
C {lab_pin.sym} -1270 2100 0 1 {name=l91 lab=DI0}
N -1170 2100 -1130 2100 {lab=ddi0}
C {lab_pin.sym} -1130 2100 0 0 {name=l92 lab=ddi0}
T {adc_bridge: 1.2 V core levels in, XSPICE digital out} -1400 -520 0 0 0.3 0.3 {}
C {serdes/serdes_dig.sym} 0 0 0 0 {name=Adig model=serdes_dig_1}
N -130 -250 -170 -250 {lab=dclk}
C {lab_pin.sym} -170 -250 0 1 {name=l93 lab=dclk}
N -130 -230 -170 -230 {lab=dena}
C {lab_pin.sym} -170 -230 0 1 {name=l94 lab=dena}
N -130 -210 -170 -210 {lab=ddi23}
C {lab_pin.sym} -170 -210 0 1 {name=l95 lab=ddi23}
N -130 -190 -170 -190 {lab=ddi22}
C {lab_pin.sym} -170 -190 0 1 {name=l96 lab=ddi22}
N -130 -170 -170 -170 {lab=ddi21}
C {lab_pin.sym} -170 -170 0 1 {name=l97 lab=ddi21}
N -130 -150 -170 -150 {lab=ddi20}
C {lab_pin.sym} -170 -150 0 1 {name=l98 lab=ddi20}
N -130 -130 -170 -130 {lab=ddi19}
C {lab_pin.sym} -170 -130 0 1 {name=l99 lab=ddi19}
N -130 -110 -170 -110 {lab=ddi18}
C {lab_pin.sym} -170 -110 0 1 {name=l100 lab=ddi18}
N -130 -90 -170 -90 {lab=ddi17}
C {lab_pin.sym} -170 -90 0 1 {name=l101 lab=ddi17}
N -130 -70 -170 -70 {lab=ddi16}
C {lab_pin.sym} -170 -70 0 1 {name=l102 lab=ddi16}
N -130 -50 -170 -50 {lab=ddi15}
C {lab_pin.sym} -170 -50 0 1 {name=l103 lab=ddi15}
N -130 -30 -170 -30 {lab=ddi14}
C {lab_pin.sym} -170 -30 0 1 {name=l104 lab=ddi14}
N -130 -10 -170 -10 {lab=ddi13}
C {lab_pin.sym} -170 -10 0 1 {name=l105 lab=ddi13}
N -130 10 -170 10 {lab=ddi12}
C {lab_pin.sym} -170 10 0 1 {name=l106 lab=ddi12}
N -130 30 -170 30 {lab=ddi11}
C {lab_pin.sym} -170 30 0 1 {name=l107 lab=ddi11}
N -130 50 -170 50 {lab=ddi10}
C {lab_pin.sym} -170 50 0 1 {name=l108 lab=ddi10}
N -130 70 -170 70 {lab=ddi9}
C {lab_pin.sym} -170 70 0 1 {name=l109 lab=ddi9}
N -130 90 -170 90 {lab=ddi8}
C {lab_pin.sym} -170 90 0 1 {name=l110 lab=ddi8}
N -130 110 -170 110 {lab=ddi7}
C {lab_pin.sym} -170 110 0 1 {name=l111 lab=ddi7}
N -130 130 -170 130 {lab=ddi6}
C {lab_pin.sym} -170 130 0 1 {name=l112 lab=ddi6}
N -130 150 -170 150 {lab=ddi5}
C {lab_pin.sym} -170 150 0 1 {name=l113 lab=ddi5}
N -130 170 -170 170 {lab=ddi4}
C {lab_pin.sym} -170 170 0 1 {name=l114 lab=ddi4}
N -130 190 -170 190 {lab=ddi3}
C {lab_pin.sym} -170 190 0 1 {name=l115 lab=ddi3}
N -130 210 -170 210 {lab=ddi2}
C {lab_pin.sym} -170 210 0 1 {name=l116 lab=ddi2}
N -130 230 -170 230 {lab=ddi1}
C {lab_pin.sym} -170 230 0 1 {name=l117 lab=ddi1}
N -130 250 -170 250 {lab=ddi0}
C {lab_pin.sym} -170 250 0 1 {name=l118 lab=ddi0}
N 130 -130 170 -130 {lab=ddp}
C {lab_pin.sym} 170 -130 0 0 {name=l119 lab=ddp}
N 130 -110 170 -110 {lab=ddn}
C {lab_pin.sym} 170 -110 0 0 {name=l120 lab=ddn}
N 130 -90 170 -90 {lab=ddo11}
C {lab_pin.sym} 170 -90 0 0 {name=l121 lab=ddo11}
N 130 -70 170 -70 {lab=ddo10}
C {lab_pin.sym} 170 -70 0 0 {name=l122 lab=ddo10}
N 130 -50 170 -50 {lab=ddo9}
C {lab_pin.sym} 170 -50 0 0 {name=l123 lab=ddo9}
N 130 -30 170 -30 {lab=ddo8}
C {lab_pin.sym} 170 -30 0 0 {name=l124 lab=ddo8}
N 130 -10 170 -10 {lab=ddo7}
C {lab_pin.sym} 170 -10 0 0 {name=l125 lab=ddo7}
N 130 10 170 10 {lab=ddo6}
C {lab_pin.sym} 170 10 0 0 {name=l126 lab=ddo6}
N 130 30 170 30 {lab=ddo5}
C {lab_pin.sym} 170 30 0 0 {name=l127 lab=ddo5}
N 130 50 170 50 {lab=ddo4}
C {lab_pin.sym} 170 50 0 0 {name=l128 lab=ddo4}
N 130 70 170 70 {lab=ddo3}
C {lab_pin.sym} 170 70 0 0 {name=l129 lab=ddo3}
N 130 90 170 90 {lab=ddo2}
C {lab_pin.sym} 170 90 0 0 {name=l130 lab=ddo2}
N 130 110 170 110 {lab=ddo1}
C {lab_pin.sym} 170 110 0 0 {name=l131 lab=ddo1}
N 130 130 170 130 {lab=ddo0}
C {lab_pin.sym} 170 130 0 0 {name=l132 lab=ddo0}
T {serdes/serdes_dig.v, through d_cosim} -160 -180 0 0 0.3 0.3 {}
C {dac_bridge.sym} 1200 -300 0 0 {name=A200 dac_bridge_model=dac_1}
N 1170 -300 1130 -300 {lab=ddp}
C {lab_pin.sym} 1130 -300 0 1 {name=l133 lab=ddp}
N 1230 -300 1270 -300 {lab=D_p}
C {lab_pin.sym} 1270 -300 0 0 {name=l134 lab=D_p}
C {dac_bridge.sym} 1200 -200 0 0 {name=A201 dac_bridge_model=dac_1}
N 1170 -200 1130 -200 {lab=ddn}
C {lab_pin.sym} 1130 -200 0 1 {name=l135 lab=ddn}
N 1230 -200 1270 -200 {lab=D_n}
C {lab_pin.sym} 1270 -200 0 0 {name=l136 lab=D_n}
C {dac_bridge.sym} 1200 -100 0 0 {name=A202 dac_bridge_model=dac_1}
N 1170 -100 1130 -100 {lab=ddo11}
C {lab_pin.sym} 1130 -100 0 1 {name=l137 lab=ddo11}
N 1230 -100 1270 -100 {lab=DO11}
C {lab_pin.sym} 1270 -100 0 0 {name=l138 lab=DO11}
C {dac_bridge.sym} 1200 0 0 0 {name=A203 dac_bridge_model=dac_1}
N 1170 0 1130 0 {lab=ddo10}
C {lab_pin.sym} 1130 0 0 1 {name=l139 lab=ddo10}
N 1230 0 1270 0 {lab=DO10}
C {lab_pin.sym} 1270 0 0 0 {name=l140 lab=DO10}
C {dac_bridge.sym} 1200 100 0 0 {name=A204 dac_bridge_model=dac_1}
N 1170 100 1130 100 {lab=ddo9}
C {lab_pin.sym} 1130 100 0 1 {name=l141 lab=ddo9}
N 1230 100 1270 100 {lab=DO9}
C {lab_pin.sym} 1270 100 0 0 {name=l142 lab=DO9}
C {dac_bridge.sym} 1200 200 0 0 {name=A205 dac_bridge_model=dac_1}
N 1170 200 1130 200 {lab=ddo8}
C {lab_pin.sym} 1130 200 0 1 {name=l143 lab=ddo8}
N 1230 200 1270 200 {lab=DO8}
C {lab_pin.sym} 1270 200 0 0 {name=l144 lab=DO8}
C {dac_bridge.sym} 1200 300 0 0 {name=A206 dac_bridge_model=dac_1}
N 1170 300 1130 300 {lab=ddo7}
C {lab_pin.sym} 1130 300 0 1 {name=l145 lab=ddo7}
N 1230 300 1270 300 {lab=DO7}
C {lab_pin.sym} 1270 300 0 0 {name=l146 lab=DO7}
C {dac_bridge.sym} 1200 400 0 0 {name=A207 dac_bridge_model=dac_1}
N 1170 400 1130 400 {lab=ddo6}
C {lab_pin.sym} 1130 400 0 1 {name=l147 lab=ddo6}
N 1230 400 1270 400 {lab=DO6}
C {lab_pin.sym} 1270 400 0 0 {name=l148 lab=DO6}
C {dac_bridge.sym} 1200 500 0 0 {name=A208 dac_bridge_model=dac_1}
N 1170 500 1130 500 {lab=ddo5}
C {lab_pin.sym} 1130 500 0 1 {name=l149 lab=ddo5}
N 1230 500 1270 500 {lab=DO5}
C {lab_pin.sym} 1270 500 0 0 {name=l150 lab=DO5}
C {dac_bridge.sym} 1200 600 0 0 {name=A209 dac_bridge_model=dac_1}
N 1170 600 1130 600 {lab=ddo4}
C {lab_pin.sym} 1130 600 0 1 {name=l151 lab=ddo4}
N 1230 600 1270 600 {lab=DO4}
C {lab_pin.sym} 1270 600 0 0 {name=l152 lab=DO4}
C {dac_bridge.sym} 1200 700 0 0 {name=A210 dac_bridge_model=dac_1}
N 1170 700 1130 700 {lab=ddo3}
C {lab_pin.sym} 1130 700 0 1 {name=l153 lab=ddo3}
N 1230 700 1270 700 {lab=DO3}
C {lab_pin.sym} 1270 700 0 0 {name=l154 lab=DO3}
C {dac_bridge.sym} 1200 800 0 0 {name=A211 dac_bridge_model=dac_1}
N 1170 800 1130 800 {lab=ddo2}
C {lab_pin.sym} 1130 800 0 1 {name=l155 lab=ddo2}
N 1230 800 1270 800 {lab=DO2}
C {lab_pin.sym} 1270 800 0 0 {name=l156 lab=DO2}
C {dac_bridge.sym} 1200 900 0 0 {name=A212 dac_bridge_model=dac_1}
N 1170 900 1130 900 {lab=ddo1}
C {lab_pin.sym} 1130 900 0 1 {name=l157 lab=ddo1}
N 1230 900 1270 900 {lab=DO1}
C {lab_pin.sym} 1270 900 0 0 {name=l158 lab=DO1}
C {dac_bridge.sym} 1200 1000 0 0 {name=A213 dac_bridge_model=dac_1}
N 1170 1000 1130 1000 {lab=ddo0}
C {lab_pin.sym} 1130 1000 0 1 {name=l159 lab=ddo0}
N 1230 1000 1270 1000 {lab=DO0}
C {lab_pin.sym} 1270 1000 0 0 {name=l160 lab=DO0}
T {dac_bridge: 0..1.2 V out, t_rise/t_fall set the core edge rate} 950 -420 0 0 0.3 0.3 {}
