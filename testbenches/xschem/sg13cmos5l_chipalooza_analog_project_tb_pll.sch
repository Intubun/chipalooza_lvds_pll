v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {PLL bench: 250 MHz reference in, PRBS-7 at 500 Mb/s out.

  pll_clk = REF * (DIV_RATIO / 8) / 2, because clock_output_divider.v
  always halves the VCO.  250 MHz and DIV_RATIO = 4.0 (code 32) give
  a 1 GHz VCO and a 500 MHz bit clock. DIV_RATIO[5] is dig_in[12].

  1 ns    PLL RESET_N released
  2 ns    PLL ENABLE
  39 ns   PRBS reset released
  40 ns   pattern generator enabled, running off PLL_CLK

The loop is checked before the transmitter: VCTRL has to move and the VCO
has to oscillate, otherwise the LVDS numbers are meaningless.

KNOWN BLOCKER: the loop filter's two cap_cmomf have no symbol in this PDK,
so the filter is only its resistor and the control node has no capacitance.
Expect no lock until that is resolved.} -2400 -2100 0 0 0.45 0.45 {}
N -1400 -1960 -1400 -1930 {lab=vdd_3v3}
C {devices/lab_wire.sym} -1400 -1960 0 0 {name=ls_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
C {devices/vsource.sym} -1400 -1900 0 0 {name=Vvdd_3v3 value="3.3"}
N -1400 -1870 -1400 -1840 {lab=GND}
C {devices/gnd.sym} -1400 -1840 0 0 {name=lg_vdd_3v3 lab=GND}
T {gated 3.3 V} -1340 -1905 0 0 0.3 0.3 {}
N -1400 -1760 -1400 -1730 {lab=vdd_1v2}
C {devices/lab_wire.sym} -1400 -1760 0 0 {name=ls_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
C {devices/vsource.sym} -1400 -1700 0 0 {name=Vvdd_1v2 value="1.2"}
N -1400 -1670 -1400 -1640 {lab=GND}
C {devices/gnd.sym} -1400 -1640 0 0 {name=lg_vdd_1v2 lab=GND}
T {gated 1.2 V} -1340 -1705 0 0 0.3 0.3 {}
N -1400 -1560 -1400 -1530 {lab=enable}
C {devices/lab_wire.sym} -1400 -1560 0 0 {name=ls_enable sig_type=std_logic lab=enable}
C {devices/vsource.sym} -1400 -1500 0 0 {name=Venable value="1.2"}
N -1400 -1470 -1400 -1440 {lab=GND}
C {devices/gnd.sym} -1400 -1440 0 0 {name=lg_enable lab=GND}
T {project enable} -1340 -1505 0 0 0.3 0.3 {}
N -1400 -1360 -1400 -1330 {lab=dig_in[12]}
C {devices/lab_wire.sym} -1400 -1360 0 0 {name=ls_dig_in_12 sig_type=std_logic lab=dig_in[12]}
C {devices/vsource.sym} -1400 -1300 0 0 {name=Vdig_in_12 value="1.2"}
N -1400 -1270 -1400 -1240 {lab=GND}
C {devices/gnd.sym} -1400 -1240 0 0 {name=lg_dig_in_12 lab=GND}
T {DIV_RATIO[5] -> DIV_RATIO = 4.0} -1340 -1305 0 0 0.3 0.3 {}
N -1400 -1160 -1400 -1130 {lab=dig_in[6]}
C {devices/lab_wire.sym} -1400 -1160 0 0 {name=ls_dig_in_6 sig_type=std_logic lab=dig_in[6]}
C {devices/vsource.sym} -1400 -1100 0 0 {name=Vdig_in_6 value="PWL(0 0 1n 0 1.1n 1.2)"}
N -1400 -1070 -1400 -1040 {lab=GND}
C {devices/gnd.sym} -1400 -1040 0 0 {name=lg_dig_in_6 lab=GND}
T {PLL RESET_N, active low} -1340 -1105 0 0 0.3 0.3 {}
N -1400 -960 -1400 -930 {lab=dig_in[5]}
C {devices/lab_wire.sym} -1400 -960 0 0 {name=ls_dig_in_5 sig_type=std_logic lab=dig_in[5]}
C {devices/vsource.sym} -1400 -900 0 0 {name=Vdig_in_5 value="PWL(0 0 2n 0 2.1n 1.2)"}
N -1400 -870 -1400 -840 {lab=GND}
C {devices/gnd.sym} -1400 -840 0 0 {name=lg_dig_in_5 lab=GND}
T {PLL ENABLE} -1340 -905 0 0 0.3 0.3 {}
N -1400 -760 -1400 -730 {lab=dig_in[3]}
C {devices/lab_wire.sym} -1400 -760 0 0 {name=ls_dig_in_3 sig_type=std_logic lab=dig_in[3]}
C {devices/vsource.sym} -1400 -700 0 0 {name=Vdig_in_3 value="1.2"}
N -1400 -670 -1400 -640 {lab=GND}
C {devices/gnd.sym} -1400 -640 0 0 {name=lg_dig_in_3 lab=GND}
T {mode = 1, PRBS-7} -1340 -705 0 0 0.3 0.3 {}
N -1400 -560 -1400 -530 {lab=dig_in[2]}
C {devices/lab_wire.sym} -1400 -560 0 0 {name=ls_dig_in_2 sig_type=std_logic lab=dig_in[2]}
C {devices/vsource.sym} -1400 -500 0 0 {name=Vdig_in_2 value="PWL(0 1.2 39n 1.2 39.1n 0)"}
N -1400 -470 -1400 -440 {lab=GND}
C {devices/gnd.sym} -1400 -440 0 0 {name=lg_dig_in_2 lab=GND}
T {PRBS reset, released just before en} -1340 -505 0 0 0.3 0.3 {}
N -1400 -360 -1400 -330 {lab=dig_in[1]}
C {devices/lab_wire.sym} -1400 -360 0 0 {name=ls_dig_in_1 sig_type=std_logic lab=dig_in[1]}
C {devices/vsource.sym} -1400 -300 0 0 {name=Vdig_in_1 value="PWL(0 0 40n 0 40.1n 1.2)"}
N -1400 -270 -1400 -240 {lab=GND}
C {devices/gnd.sym} -1400 -240 0 0 {name=lg_dig_in_1 lab=GND}
T {pattern en, held off while the PLL settles} -1340 -305 0 0 0.3 0.3 {}
N -1400 -160 -1400 -130 {lab=dig_in[0]}
C {devices/lab_wire.sym} -1400 -160 0 0 {name=ls_dig_in_0 sig_type=std_logic lab=dig_in[0]}
C {devices/vsource.sym} -1400 -100 0 0 {name=Vdig_in_0 value="1.2"}
N -1400 -70 -1400 -40 {lab=GND}
C {devices/gnd.sym} -1400 -40 0 0 {name=lg_dig_in_0 lab=GND}
T {clk_src = 1, run the pattern generator off the PLL} -1340 -105 0 0 0.3 0.3 {}
N -1400 40 -1400 70 {lab=ibias[1]}
C {devices/lab_wire.sym} -1400 40 0 0 {name=ls_ibias_1 sig_type=std_logic lab=ibias[1]}
C {isource.sym} -1400 100 0 0 {name=Iibias_1 value=-30u}
N -1400 130 -1400 160 {lab=GND}
C {devices/gnd.sym} -1400 160 0 0 {name=lg_ibias_1 lab=GND}
T {driver reference} -1340 95 0 0 0.3 0.3 {}
N -1400 240 -1400 270 {lab=ibias[0]}
C {devices/lab_wire.sym} -1400 240 0 0 {name=ls_ibias_0 sig_type=std_logic lab=ibias[0]}
C {isource.sym} -1400 300 0 0 {name=Iibias_0 value=-30u}
N -1400 330 -1400 360 {lab=GND}
C {devices/gnd.sym} -1400 360 0 0 {name=lg_ibias_0 lab=GND}
T {pre-driver reference} -1340 295 0 0 0.3 0.3 {}
N -1400 440 -1400 470 {lab=vbias}
C {devices/lab_wire.sym} -1400 440 0 0 {name=ls_vbias sig_type=std_logic lab=vbias}
C {devices/vsource.sym} -1400 500 0 0 {name=Vvbias value="1.25"}
N -1400 530 -1400 560 {lab=GND}
C {devices/gnd.sym} -1400 560 0 0 {name=lg_vbias lab=GND}
T {shared voltage bias} -1340 495 0 0 0.3 0.3 {}
N -1400 640 -1400 670 {lab=analog_pin[0]}
C {devices/lab_wire.sym} -1400 640 0 0 {name=ls_analog_pin_0 sig_type=std_logic lab=analog_pin[0]}
C {devices/vsource.sym} -1400 700 0 0 {name=Vanalog_pin_0 value="PULSE(0 1.2 0 50p 50p 1.9n 4n)"}
N -1400 730 -1400 760 {lab=GND}
C {devices/gnd.sym} -1400 760 0 0 {name=lg_analog_pin_0 lab=GND}
T {REF_CLK, 250 MHz} -1340 695 0 0 0.3 0.3 {}
N -1400 840 -1400 870 {lab=analog_bus[0]}
C {devices/lab_wire.sym} -1400 840 0 0 {name=ls_analog_bus_0 sig_type=std_logic lab=analog_bus[0]}
C {isource.sym} -1400 900 0 0 {name=Ianalog_bus_0 value=-30u}
N -1400 930 -1400 960 {lab=GND}
C {devices/gnd.sym} -1400 960 0 0 {name=lg_analog_bus_0 lab=GND}
T {PLL charge-pump reference} -1340 895 0 0 0.3 0.3 {}
N -300 -350 -240 -350 {lab=vdd_3v3}
C {devices/lab_wire.sym} -300 -350 0 0 {name=lx_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
N -300 -330 -240 -330 {lab=vdd_1v2}
C {devices/lab_wire.sym} -300 -330 0 0 {name=lx_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
N -300 -310 -240 -310 {lab=GND}
C {devices/gnd.sym} -300 -310 1 0 {name=lgg_vss_3v3 lab=GND}
N -300 -290 -240 -290 {lab=GND}
C {devices/gnd.sym} -300 -290 1 0 {name=lgg_vss_1v2 lab=GND}
N -300 -270 -240 -270 {lab=GND}
C {devices/gnd.sym} -300 -270 1 0 {name=lgg_vssio lab=GND}
N -300 -250 -240 -250 {lab=enable}
C {devices/lab_wire.sym} -300 -250 0 0 {name=lx_enable sig_type=std_logic lab=enable}
N -300 -230 -240 -230 {lab=clk}
C {devices/lab_wire.sym} -300 -230 0 0 {name=lx_clk sig_type=std_logic lab=clk}
N -300 -210 -240 -210 {lab=dig_in[23]}
C {devices/lab_wire.sym} -300 -210 0 0 {name=lx_dig_in_23 sig_type=std_logic lab=dig_in[23]}
N -300 -190 -240 -190 {lab=dig_in[22]}
C {devices/lab_wire.sym} -300 -190 0 0 {name=lx_dig_in_22 sig_type=std_logic lab=dig_in[22]}
N -300 -170 -240 -170 {lab=dig_in[21]}
C {devices/lab_wire.sym} -300 -170 0 0 {name=lx_dig_in_21 sig_type=std_logic lab=dig_in[21]}
N -300 -150 -240 -150 {lab=dig_in[20]}
C {devices/lab_wire.sym} -300 -150 0 0 {name=lx_dig_in_20 sig_type=std_logic lab=dig_in[20]}
N -300 -130 -240 -130 {lab=dig_in[19]}
C {devices/lab_wire.sym} -300 -130 0 0 {name=lx_dig_in_19 sig_type=std_logic lab=dig_in[19]}
N -300 -110 -240 -110 {lab=dig_in[18]}
C {devices/lab_wire.sym} -300 -110 0 0 {name=lx_dig_in_18 sig_type=std_logic lab=dig_in[18]}
N -300 -90 -240 -90 {lab=dig_in[17]}
C {devices/lab_wire.sym} -300 -90 0 0 {name=lx_dig_in_17 sig_type=std_logic lab=dig_in[17]}
N -300 -70 -240 -70 {lab=dig_in[16]}
C {devices/lab_wire.sym} -300 -70 0 0 {name=lx_dig_in_16 sig_type=std_logic lab=dig_in[16]}
N -300 -50 -240 -50 {lab=dig_in[15]}
C {devices/lab_wire.sym} -300 -50 0 0 {name=lx_dig_in_15 sig_type=std_logic lab=dig_in[15]}
N -300 -30 -240 -30 {lab=dig_in[14]}
C {devices/lab_wire.sym} -300 -30 0 0 {name=lx_dig_in_14 sig_type=std_logic lab=dig_in[14]}
N -300 -10 -240 -10 {lab=dig_in[13]}
C {devices/lab_wire.sym} -300 -10 0 0 {name=lx_dig_in_13 sig_type=std_logic lab=dig_in[13]}
N -300 10 -240 10 {lab=dig_in[12]}
C {devices/lab_wire.sym} -300 10 0 0 {name=lx_dig_in_12 sig_type=std_logic lab=dig_in[12]}
N -300 30 -240 30 {lab=dig_in[11]}
C {devices/lab_wire.sym} -300 30 0 0 {name=lx_dig_in_11 sig_type=std_logic lab=dig_in[11]}
N -300 50 -240 50 {lab=dig_in[10]}
C {devices/lab_wire.sym} -300 50 0 0 {name=lx_dig_in_10 sig_type=std_logic lab=dig_in[10]}
N -300 70 -240 70 {lab=dig_in[9]}
C {devices/lab_wire.sym} -300 70 0 0 {name=lx_dig_in_9 sig_type=std_logic lab=dig_in[9]}
N -300 90 -240 90 {lab=dig_in[8]}
C {devices/lab_wire.sym} -300 90 0 0 {name=lx_dig_in_8 sig_type=std_logic lab=dig_in[8]}
N -300 110 -240 110 {lab=dig_in[7]}
C {devices/lab_wire.sym} -300 110 0 0 {name=lx_dig_in_7 sig_type=std_logic lab=dig_in[7]}
N -300 130 -240 130 {lab=dig_in[6]}
C {devices/lab_wire.sym} -300 130 0 0 {name=lx_dig_in_6 sig_type=std_logic lab=dig_in[6]}
N -300 150 -240 150 {lab=dig_in[5]}
C {devices/lab_wire.sym} -300 150 0 0 {name=lx_dig_in_5 sig_type=std_logic lab=dig_in[5]}
N -300 170 -240 170 {lab=dig_in[4]}
C {devices/lab_wire.sym} -300 170 0 0 {name=lx_dig_in_4 sig_type=std_logic lab=dig_in[4]}
N -300 190 -240 190 {lab=dig_in[3]}
C {devices/lab_wire.sym} -300 190 0 0 {name=lx_dig_in_3 sig_type=std_logic lab=dig_in[3]}
N -300 210 -240 210 {lab=dig_in[2]}
C {devices/lab_wire.sym} -300 210 0 0 {name=lx_dig_in_2 sig_type=std_logic lab=dig_in[2]}
N -300 230 -240 230 {lab=dig_in[1]}
C {devices/lab_wire.sym} -300 230 0 0 {name=lx_dig_in_1 sig_type=std_logic lab=dig_in[1]}
N -300 250 -240 250 {lab=dig_in[0]}
C {devices/lab_wire.sym} -300 250 0 0 {name=lx_dig_in_0 sig_type=std_logic lab=dig_in[0]}
N -300 270 -240 270 {lab=ibias[1]}
C {devices/lab_wire.sym} -300 270 0 0 {name=lx_ibias_1 sig_type=std_logic lab=ibias[1]}
N -300 290 -240 290 {lab=ibias[0]}
C {devices/lab_wire.sym} -300 290 0 0 {name=lx_ibias_0 sig_type=std_logic lab=ibias[0]}
N -300 310 -240 310 {lab=vbias}
C {devices/lab_wire.sym} -300 310 0 0 {name=lx_vbias sig_type=std_logic lab=vbias}
N 240 -350 300 -350 {lab=dig_out[11]}
C {devices/lab_wire.sym} 300 -350 0 0 {name=lx_dig_out_11 sig_type=std_logic lab=dig_out[11]}
N 240 -330 300 -330 {lab=dig_out[10]}
C {devices/lab_wire.sym} 300 -330 0 0 {name=lx_dig_out_10 sig_type=std_logic lab=dig_out[10]}
N 240 -310 300 -310 {lab=dig_out[9]}
C {devices/lab_wire.sym} 300 -310 0 0 {name=lx_dig_out_9 sig_type=std_logic lab=dig_out[9]}
N 240 -290 300 -290 {lab=dig_out[8]}
C {devices/lab_wire.sym} 300 -290 0 0 {name=lx_dig_out_8 sig_type=std_logic lab=dig_out[8]}
N 240 -270 300 -270 {lab=dig_out[7]}
C {devices/lab_wire.sym} 300 -270 0 0 {name=lx_dig_out_7 sig_type=std_logic lab=dig_out[7]}
N 240 -250 300 -250 {lab=dig_out[6]}
C {devices/lab_wire.sym} 300 -250 0 0 {name=lx_dig_out_6 sig_type=std_logic lab=dig_out[6]}
N 240 -230 300 -230 {lab=dig_out[5]}
C {devices/lab_wire.sym} 300 -230 0 0 {name=lx_dig_out_5 sig_type=std_logic lab=dig_out[5]}
N 240 -210 300 -210 {lab=dig_out[4]}
C {devices/lab_wire.sym} 300 -210 0 0 {name=lx_dig_out_4 sig_type=std_logic lab=dig_out[4]}
N 240 -190 300 -190 {lab=dig_out[3]}
C {devices/lab_wire.sym} 300 -190 0 0 {name=lx_dig_out_3 sig_type=std_logic lab=dig_out[3]}
N 240 -170 300 -170 {lab=dig_out[2]}
C {devices/lab_wire.sym} 300 -170 0 0 {name=lx_dig_out_2 sig_type=std_logic lab=dig_out[2]}
N 240 -150 300 -150 {lab=dig_out[1]}
C {devices/lab_wire.sym} 300 -150 0 0 {name=lx_dig_out_1 sig_type=std_logic lab=dig_out[1]}
N 240 -130 300 -130 {lab=dig_out[0]}
C {devices/lab_wire.sym} 300 -130 0 0 {name=lx_dig_out_0 sig_type=std_logic lab=dig_out[0]}
N 240 -110 300 -110 {lab=analog_pin[3]}
C {devices/lab_wire.sym} 300 -110 0 0 {name=lx_analog_pin_3 sig_type=std_logic lab=analog_pin[3]}
N 240 -90 300 -90 {lab=analog_pin[2]}
C {devices/lab_wire.sym} 300 -90 0 0 {name=lx_analog_pin_2 sig_type=std_logic lab=analog_pin[2]}
N 240 -70 300 -70 {lab=analog_pin[1]}
C {devices/lab_wire.sym} 300 -70 0 0 {name=lx_analog_pin_1 sig_type=std_logic lab=analog_pin[1]}
N 240 -50 300 -50 {lab=analog_pin[0]}
C {devices/lab_wire.sym} 300 -50 0 0 {name=lx_analog_pin_0 sig_type=std_logic lab=analog_pin[0]}
N 240 -30 300 -30 {lab=analog_bus[3]}
C {devices/lab_wire.sym} 300 -30 0 0 {name=lx_analog_bus_3 sig_type=std_logic lab=analog_bus[3]}
N 240 -10 300 -10 {lab=analog_bus[2]}
C {devices/lab_wire.sym} 300 -10 0 0 {name=lx_analog_bus_2 sig_type=std_logic lab=analog_bus[2]}
N 240 10 300 10 {lab=analog_bus[1]}
C {devices/lab_wire.sym} 300 10 0 0 {name=lx_analog_bus_1 sig_type=std_logic lab=analog_bus[1]}
N 240 30 300 30 {lab=analog_bus[0]}
C {devices/lab_wire.sym} 300 30 0 0 {name=lx_analog_bus_0 sig_type=std_logic lab=analog_bus[0]}
C {sg13cmos5l_chipalooza_analog_project.sym} 0 0 0 0 {name=x1}
N 700 -960 700 -930 {lab=analog_pin[3]}
C {devices/lab_wire.sym} 700 -960 0 0 {name=lpad_d_n sig_type=std_logic lab=analog_pin[3]}
C {devices/vsource.sym} 700 -900 0 0 {name=Vd_n value=0}
N 700 -870 700 -840 {lab=d_n}
C {devices/lab_wire.sym} 700 -840 0 0 {name=lmeas_d_n sig_type=std_logic lab=d_n}
N 900 -960 900 -930 {lab=analog_pin[2]}
C {devices/lab_wire.sym} 900 -960 0 0 {name=lpad_d_p sig_type=std_logic lab=analog_pin[2]}
C {devices/vsource.sym} 900 -900 0 0 {name=Vd_p value=0}
N 900 -870 900 -840 {lab=d_p}
C {devices/lab_wire.sym} 900 -840 0 0 {name=lmeas_d_p sig_type=std_logic lab=d_p}
N 800 -840 800 -810 {lab=d_n}
C {devices/lab_wire.sym} 800 -840 0 0 {name=lt1 sig_type=std_logic lab=d_n}
C {res.sym} 800 -810 0 0 {name=Rtp value=49.9}
N 800 -780 800 -750 {lab=vos}
N 800 -780 880 -780 {lab=vos}
C {devices/lab_wire.sym} 880 -780 0 0 {name=lvos sig_type=std_logic lab=vos}
C {res.sym} 800 -720 0 0 {name=Rtn value=49.9}
N 800 -690 800 -660 {lab=d_p}
C {devices/lab_wire.sym} 800 -660 0 0 {name=lt2 sig_type=std_logic lab=d_p}
B 2 1500 -1240 3100 -940 {flags=graph
y1=0
y2=1.3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=1e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.xpll.VCTRL"
color="8"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 1500 -920 3100 -620 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=5e-07
x2=5.1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.pll_clk
x1.core_p"
color="4 7"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 1500 -600 3100 -300 {flags=graph
y1=0.9
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=5e-07
x2=5.1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="d_p
d_n
vos"
color="4 5 8"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
C {launcher.sym} 1500 -1320 0 0 {name=h_sim
descr="Simulate"
tclcommand="
set_sim_defaults
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save
xschem netlist
simulate
"}
C {launcher.sym} 1500 -1280 0 0 {name=h_waves
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/sg13cmos5l_chipalooza_analog_project_tb_pll.raw tran"
}
C {launcher.sym} 1500 -1240 0 0 {name=h_check
descr="Check PRBS + timing"
tclcommand="exec python3 [file dirname [xschem get current_dirname]]/../../scripts/check_timing.py &"
}
C {devices/code_shown.sym} -2400 -1300 0 0 {name=NGSPICE
only_toplevel=true
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_mfringe.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.options savecurrents klu method=gear reltol=1e-3 abstol=1e-12 gmin=1e-12
.control
save d_p d_n vos x1.core_p x1.core_n x1.pll_clk x1.xpll.VCTRL x1.xpll.VCO_CLK
tran 5p 1u 0 5p
write @schname\\\\.raw

* First question: does the loop do anything at all?  VCTRL has to move and the
* VCO has to oscillate before any of the numbers below mean anything.
meas tran vctrl_min MIN v(x1.xpll.VCTRL) from=50n to=990n
meas tran vctrl_max MAX v(x1.xpll.VCTRL) from=50n to=990n
meas tran vctrl_end AVG v(x1.xpll.VCTRL) from=900n to=990n
meas tran vco_pp PP v(x1.xpll.VCO_CLK) from=900n to=990n
print vctrl_min vctrl_max vctrl_end vco_pp

* Second: is pll_clk at 500 MHz?  Two consecutive rising edges give the period.
meas tran t1 WHEN v(x1.pll_clk)=0.6 RISE=200
meas tran t2 WHEN v(x1.pll_clk)=0.6 RISE=201
let f_pll = 1/(t2-t1)
print f_pll

* Third: what comes out of the transmitter, once the pattern generator runs
let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=200n to=990n
meas tran vod_min MIN vod from=200n to=990n
meas tran vos_avg AVG v(vos) from=200n to=990n
meas tran vos_max MAX v(vos) from=200n to=990n
meas tran vos_min MIN v(vos) from=200n to=990n
let vos_pp = vos_max - vos_min
meas tran core_pp PP v(x1.core_p) from=200n to=990n
print vod_max vod_min vos_avg vos_pp core_pp

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.pll_clk) v(x1.xpll.VCTRL)
.endc
"}
