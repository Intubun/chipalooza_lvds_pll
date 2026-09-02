v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {LVDS bench for the top cell.

Reset, then clock passthrough of the 500 MHz reference on the dedicated
pad, then PRBS-7 from 10 ns, through the pre-driver and the driver into
49.9 + 49.9 ohm across the two output pads with the Vos tap.

clk_src is 0 here on purpose: this bench characterises the transmitter,
so the bit clock comes straight off analog_pin[0] and the PLL is left
out of the measurement.  tb_pll is the one that runs through the loop.

The port list is read out of the symbol when this bench is generated,
so it survives rewiring of the top cell.  Any harness pin without a
source in the stimulus column is left open on purpose - except the
PLL's, which are driven even though the loop is unused here.  They
land on an XSPICE adc_bridge, where an open node has no defined logic
value, so ENABLE and RESET_N hold the loop off and every ratio bit
carries its own source.

clk_pp and core_pp are checked first: if the gated clock inside the
pattern generator is not moving, the control path is broken and the
LVDS numbers below it mean nothing.

No pad or ESD model - the driver was characterised with one, so the
Vos figure here is not the compliance number.} -3600 -2400 0 0 0.45 0.45 {}
N -2000 -1760 -2000 -1730 {lab=vdd_3v3}
C {devices/lab_wire.sym} -2000 -1760 0 0 {name=ls_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
C {devices/vsource.sym} -2000 -1700 0 0 {name=Vvdd_3v3 value="3.3"}
N -2000 -1670 -2000 -1640 {lab=GND}
C {devices/gnd.sym} -2000 -1640 0 0 {name=lg_vdd_3v3 lab=GND}
T {gated 3.3 V} -1920 -1705 0 0 0.3 0.3 {}
N -2000 -1560 -2000 -1530 {lab=vdd_1v2}
C {devices/lab_wire.sym} -2000 -1560 0 0 {name=ls_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
C {devices/vsource.sym} -2000 -1500 0 0 {name=Vvdd_1v2 value="1.2"}
N -2000 -1470 -2000 -1440 {lab=GND}
C {devices/gnd.sym} -2000 -1440 0 0 {name=lg_vdd_1v2 lab=GND}
T {gated 1.2 V} -1920 -1505 0 0 0.3 0.3 {}
L 3 -2260 -1820 -1340 -1820 {}
L 3 -1340 -1820 -1340 -1380 {}
L 3 -2260 -1380 -1340 -1380 {}
L 3 -2260 -1820 -2260 -1380 {}
T {supplies} -2260 -1875 0 0 0.4 0.4 {}
N -2000 -1240 -2000 -1210 {lab=analog_bus[1]}
C {devices/lab_wire.sym} -2000 -1240 0 0 {name=ls_analog_bus_1 sig_type=std_logic lab=analog_bus[1]}
C {devices/vsource.sym} -2000 -1180 0 0 {name=Vanalog_bus_1 value="1.2"}
N -2000 -1150 -2000 -1120 {lab=GND}
C {devices/gnd.sym} -2000 -1120 0 0 {name=lg_analog_bus_1 lab=GND}
T {LVDS common-mode reference, 1.2 V (the IDAC grid has no 1.25 V)} -1920 -1185 0 0 0.3 0.3 {}
N -2000 -1040 -2000 -1010 {lab=ibias[0]}
C {devices/lab_wire.sym} -2000 -1040 0 0 {name=ls_ibias_0 sig_type=std_logic lab=ibias[0]}
C {isource.sym} -2000 -980 0 0 {name=Iibias_0 value=-2u}
N -2000 -950 -2000 -920 {lab=GND}
C {devices/gnd.sym} -2000 -920 0 0 {name=lg_ibias_0 lab=GND}
T {pre-driver reference, 2 uA} -1920 -985 0 0 0.3 0.3 {}
N -2000 -840 -2000 -810 {lab=ibias[1]}
C {devices/lab_wire.sym} -2000 -840 0 0 {name=ls_ibias_1 sig_type=std_logic lab=ibias[1]}
C {isource.sym} -2000 -780 0 0 {name=Iibias_1 value=-2u}
N -2000 -750 -2000 -720 {lab=GND}
C {devices/gnd.sym} -2000 -720 0 0 {name=lg_ibias_1 lab=GND}
T {driver reference, 2 uA} -1920 -785 0 0 0.3 0.3 {}
L 3 -2260 -1300 -1340 -1300 {}
L 3 -1340 -1300 -1340 -660 {}
L 3 -2260 -660 -1340 -660 {}
L 3 -2260 -1300 -2260 -660 {}
T {bias} -2260 -1355 0 0 0.4 0.4 {}
N -2000 -520 -2000 -490 {lab=dig_in[0]}
C {devices/lab_wire.sym} -2000 -520 0 0 {name=ls_dig_in_0 sig_type=std_logic lab=dig_in[0]}
C {devices/vsource.sym} -2000 -460 0 0 {name=Vdig_in_0 value="0"}
N -2000 -430 -2000 -400 {lab=GND}
C {devices/gnd.sym} -2000 -400 0 0 {name=lg_dig_in_0 lab=GND}
T {clk_src = 0, take ref_clk} -1920 -465 0 0 0.3 0.3 {}
N -2000 -320 -2000 -290 {lab=dig_in[1]}
C {devices/lab_wire.sym} -2000 -320 0 0 {name=ls_dig_in_1 sig_type=std_logic lab=dig_in[1]}
C {devices/vsource.sym} -2000 -260 0 0 {name=Vdig_in_1 value="PWL(0 0 3n 0 3.1n 1.2)"}
N -2000 -230 -2000 -200 {lab=GND}
C {devices/gnd.sym} -2000 -200 0 0 {name=lg_dig_in_1 lab=GND}
T {en, low until 3 ns} -1920 -265 0 0 0.3 0.3 {}
N -2000 -120 -2000 -90 {lab=dig_in[2]}
C {devices/lab_wire.sym} -2000 -120 0 0 {name=ls_dig_in_2 sig_type=std_logic lab=dig_in[2]}
C {devices/vsource.sym} -2000 -60 0 0 {name=Vdig_in_2 value="PWL(0 1.2 2n 1.2 2.1n 0)"}
N -2000 -30 -2000 0 {lab=GND}
C {devices/gnd.sym} -2000 0 0 0 {name=lg_dig_in_2 lab=GND}
T {reset, high until 2 ns} -1920 -65 0 0 0.3 0.3 {}
N -2000 80 -2000 110 {lab=dig_in[3]}
C {devices/lab_wire.sym} -2000 80 0 0 {name=ls_dig_in_3 sig_type=std_logic lab=dig_in[3]}
C {devices/vsource.sym} -2000 140 0 0 {name=Vdig_in_3 value="1.2"}
N -2000 170 -2000 200 {lab=GND}
C {devices/gnd.sym} -2000 200 0 0 {name=lg_dig_in_3 lab=GND}
T {mode = 1, PRBS-7 throughout} -1920 135 0 0 0.3 0.3 {}
L 3 -2260 -580 -1340 -580 {}
L 3 -1340 -580 -1340 260 {}
L 3 -2260 260 -1340 260 {}
L 3 -2260 -580 -2260 260 {}
T {pattern control} -2260 -635 0 0 0.4 0.4 {}
N -2000 400 -2000 430 {lab=analog_pin[0]}
C {devices/lab_wire.sym} -2000 400 0 0 {name=ls_analog_pin_0 sig_type=std_logic lab=analog_pin[0]}
C {devices/vsource.sym} -2000 460 0 0 {name=Vanalog_pin_0 value="PULSE(0 1.2 0 50p 50p 0.9n 2n)"}
N -2000 490 -2000 520 {lab=GND}
C {devices/gnd.sym} -2000 520 0 0 {name=lg_analog_pin_0 lab=GND}
T {ref_clk, 500 MHz} -1920 455 0 0 0.3 0.3 {}
L 3 -2260 340 -1340 340 {}
L 3 -1340 340 -1340 580 {}
L 3 -2260 580 -1340 580 {}
L 3 -2260 340 -2260 580 {}
T {clocks} -2260 285 0 0 0.4 0.4 {}
N -2000 720 -2000 750 {lab=dig_in[6]}
C {devices/lab_wire.sym} -2000 720 0 0 {name=ls_dig_in_6 sig_type=std_logic lab=dig_in[6]}
C {devices/vsource.sym} -2000 780 0 0 {name=Vdig_in_6 value="0"}
N -2000 810 -2000 840 {lab=GND}
C {devices/gnd.sym} -2000 840 0 0 {name=lg_dig_in_6 lab=GND}
T {PLL RESET_N = 0, held in reset} -1920 775 0 0 0.3 0.3 {}
N -2000 920 -2000 950 {lab=dig_in[5]}
C {devices/lab_wire.sym} -2000 920 0 0 {name=ls_dig_in_5 sig_type=std_logic lab=dig_in[5]}
C {devices/vsource.sym} -2000 980 0 0 {name=Vdig_in_5 value="0"}
N -2000 1010 -2000 1040 {lab=GND}
C {devices/gnd.sym} -2000 1040 0 0 {name=lg_dig_in_5 lab=GND}
T {PLL ENABLE = 0, the loop is not used here} -1920 975 0 0 0.3 0.3 {}
N -2000 1120 -2000 1150 {lab=dig_in[16]}
C {devices/lab_wire.sym} -2000 1120 0 0 {name=ls_dig_in_16 sig_type=std_logic lab=dig_in[16]}
C {devices/vsource.sym} -2000 1180 0 0 {name=Vdig_in_16 value="0"}
N -2000 1210 -2000 1240 {lab=GND}
C {devices/gnd.sym} -2000 1240 0 0 {name=lg_dig_in_16 lab=GND}
T {DIV_RATIO[9] = 0} -1920 1175 0 0 0.3 0.3 {}
N -2000 1320 -2000 1350 {lab=dig_in[15]}
C {devices/lab_wire.sym} -2000 1320 0 0 {name=ls_dig_in_15 sig_type=std_logic lab=dig_in[15]}
C {devices/vsource.sym} -2000 1380 0 0 {name=Vdig_in_15 value="0"}
N -2000 1410 -2000 1440 {lab=GND}
C {devices/gnd.sym} -2000 1440 0 0 {name=lg_dig_in_15 lab=GND}
T {DIV_RATIO[8] = 0} -1920 1375 0 0 0.3 0.3 {}
N -2000 1520 -2000 1550 {lab=dig_in[14]}
C {devices/lab_wire.sym} -2000 1520 0 0 {name=ls_dig_in_14 sig_type=std_logic lab=dig_in[14]}
C {devices/vsource.sym} -2000 1580 0 0 {name=Vdig_in_14 value="0"}
N -2000 1610 -2000 1640 {lab=GND}
C {devices/gnd.sym} -2000 1640 0 0 {name=lg_dig_in_14 lab=GND}
T {DIV_RATIO[7] = 0} -1920 1575 0 0 0.3 0.3 {}
N -2000 1720 -2000 1750 {lab=dig_in[13]}
C {devices/lab_wire.sym} -2000 1720 0 0 {name=ls_dig_in_13 sig_type=std_logic lab=dig_in[13]}
C {devices/vsource.sym} -2000 1780 0 0 {name=Vdig_in_13 value="0"}
N -2000 1810 -2000 1840 {lab=GND}
C {devices/gnd.sym} -2000 1840 0 0 {name=lg_dig_in_13 lab=GND}
T {DIV_RATIO[6] = 0} -1920 1775 0 0 0.3 0.3 {}
N -2000 1920 -2000 1950 {lab=dig_in[12]}
C {devices/lab_wire.sym} -2000 1920 0 0 {name=ls_dig_in_12 sig_type=std_logic lab=dig_in[12]}
C {devices/vsource.sym} -2000 1980 0 0 {name=Vdig_in_12 value="0"}
N -2000 2010 -2000 2040 {lab=GND}
C {devices/gnd.sym} -2000 2040 0 0 {name=lg_dig_in_12 lab=GND}
T {DIV_RATIO[5] = 0} -1920 1975 0 0 0.3 0.3 {}
N -2000 2120 -2000 2150 {lab=dig_in[11]}
C {devices/lab_wire.sym} -2000 2120 0 0 {name=ls_dig_in_11 sig_type=std_logic lab=dig_in[11]}
C {devices/vsource.sym} -2000 2180 0 0 {name=Vdig_in_11 value="0"}
N -2000 2210 -2000 2240 {lab=GND}
C {devices/gnd.sym} -2000 2240 0 0 {name=lg_dig_in_11 lab=GND}
T {DIV_RATIO[4] = 0} -1920 2175 0 0 0.3 0.3 {}
N -2000 2320 -2000 2350 {lab=dig_in[10]}
C {devices/lab_wire.sym} -2000 2320 0 0 {name=ls_dig_in_10 sig_type=std_logic lab=dig_in[10]}
C {devices/vsource.sym} -2000 2380 0 0 {name=Vdig_in_10 value="0"}
N -2000 2410 -2000 2440 {lab=GND}
C {devices/gnd.sym} -2000 2440 0 0 {name=lg_dig_in_10 lab=GND}
T {DIV_RATIO[3] = 0} -1920 2375 0 0 0.3 0.3 {}
N -2000 2520 -2000 2550 {lab=dig_in[9]}
C {devices/lab_wire.sym} -2000 2520 0 0 {name=ls_dig_in_9 sig_type=std_logic lab=dig_in[9]}
C {devices/vsource.sym} -2000 2580 0 0 {name=Vdig_in_9 value="0"}
N -2000 2610 -2000 2640 {lab=GND}
C {devices/gnd.sym} -2000 2640 0 0 {name=lg_dig_in_9 lab=GND}
T {DIV_RATIO[2] = 0} -1920 2575 0 0 0.3 0.3 {}
N -2000 2720 -2000 2750 {lab=dig_in[8]}
C {devices/lab_wire.sym} -2000 2720 0 0 {name=ls_dig_in_8 sig_type=std_logic lab=dig_in[8]}
C {devices/vsource.sym} -2000 2780 0 0 {name=Vdig_in_8 value="0"}
N -2000 2810 -2000 2840 {lab=GND}
C {devices/gnd.sym} -2000 2840 0 0 {name=lg_dig_in_8 lab=GND}
T {DIV_RATIO[1] = 0} -1920 2775 0 0 0.3 0.3 {}
N -2000 2920 -2000 2950 {lab=dig_in[7]}
C {devices/lab_wire.sym} -2000 2920 0 0 {name=ls_dig_in_7 sig_type=std_logic lab=dig_in[7]}
C {devices/vsource.sym} -2000 2980 0 0 {name=Vdig_in_7 value="0"}
N -2000 3010 -2000 3040 {lab=GND}
C {devices/gnd.sym} -2000 3040 0 0 {name=lg_dig_in_7 lab=GND}
T {DIV_RATIO[0] = 0} -1920 2975 0 0 0.3 0.3 {}
N -2000 3120 -2000 3150 {lab=dig_in[18]}
C {devices/lab_wire.sym} -2000 3120 0 0 {name=ls_dig_in_18 sig_type=std_logic lab=dig_in[18]}
C {devices/vsource.sym} -2000 3180 0 0 {name=Vdig_in_18 value="0"}
N -2000 3210 -2000 3240 {lab=GND}
C {devices/gnd.sym} -2000 3240 0 0 {name=lg_dig_in_18 lab=GND}
T {TEST_DIV[1] = 0} -1920 3175 0 0 0.3 0.3 {}
N -2000 3320 -2000 3350 {lab=dig_in[17]}
C {devices/lab_wire.sym} -2000 3320 0 0 {name=ls_dig_in_17 sig_type=std_logic lab=dig_in[17]}
C {devices/vsource.sym} -2000 3380 0 0 {name=Vdig_in_17 value="0"}
N -2000 3410 -2000 3440 {lab=GND}
C {devices/gnd.sym} -2000 3440 0 0 {name=lg_dig_in_17 lab=GND}
T {TEST_DIV[0] = 0} -1920 3375 0 0 0.3 0.3 {}
L 3 -2260 660 -1340 660 {}
L 3 -1340 660 -1340 3500 {}
L 3 -2260 3500 -1340 3500 {}
L 3 -2260 660 -2260 3500 {}
T {PLL held off - see TB_LVDS_DRIVE} -2260 605 0 0 0.4 0.4 {}
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
N 240 -110 1000 -110 {lab=analog_pin[3]}
N 1000 -305 1000 -110 {lab=analog_pin[3]}
C {devices/lab_wire.sym} 1000 -208 0 0 {name=lpad_d_n sig_type=std_logic lab=analog_pin[3]}
C {devices/vsource.sym} 1000 -335 0 0 {name=Vd_n value=0}
N 1000 -560 1000 -365 {lab=d_n}
C {devices/lab_wire.sym} 1000 -463 0 0 {name=lmeas_d_n sig_type=std_logic lab=d_n}
N 1000 -560 1560 -560 {lab=d_n}
N 240 -90 1120 -90 {lab=analog_pin[2]}
N 1120 -90 1120 155 {lab=analog_pin[2]}
C {devices/lab_wire.sym} 1120 32 0 0 {name=lpad_d_p sig_type=std_logic lab=analog_pin[2]}
C {devices/vsource.sym} 1120 185 0 0 {name=Vd_p value=0}
N 1120 215 1120 460 {lab=d_p}
C {devices/lab_wire.sym} 1120 337 0 0 {name=lmeas_d_p sig_type=std_logic lab=d_p}
N 1120 460 1560 460 {lab=d_p}
N 1560 -560 1560 -335 {lab=d_n}
C {res.sym} 1560 -305 0 0 {name=Rtd_n value=49.9}
N 1560 -275 1560 -50 {lab=vos}
N 1560 -50 1560 175 {lab=vos}
C {res.sym} 1560 205 0 0 {name=Rtd_p value=49.9}
N 1560 235 1560 460 {lab=d_p}
N 1560 -50 1700 -50 {lab=vos}
C {devices/lab_wire.sym} 1700 -50 0 0 {name=lvos sig_type=std_logic lab=vos}
C {launcher.sym} 2050 -2150 0 0 {name=h_sim
descr="Simulate"
tclcommand="
set_sim_defaults
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save
xschem netlist
set _cwd [pwd]
cd $netlist_dir
simulate
cd $_cwd
"}
C {launcher.sym} 2050 -2110 0 0 {name=h_waves
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/sg13cmos5l_chipalooza_analog_project_tb_lvds.raw tran"
}
C {launcher.sym} 2050 -2070 0 0 {name=h_check
descr="Check PRBS + timing"
tclcommand="exec python3 [file dirname [xschem get current_dirname]]/../../scripts/check_timing.py &"
}
B 2 2050 -1950 3850 -1550 {flags=graph,unlocked
y1=0.9
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=6e-07
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
B 2 2050 -1450 3850 -1050 {flags=graph
y1=-0.2
y2=1.4
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=3e-07
x2=3.1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.xpat.gclk_b
x1.core_p
x1.core_n"
color="4 7 5"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 -950 3850 -550 {flags=graph
y1=-0.5
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=3e-07
x2=3.1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="d_p
d_n
vod"
color="4 5 7"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 -450 3850 -50 {flags=graph
y1=-0.2
y2=3.5
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=3e-07
x2=3.1e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.xlvds.In_p
x1.xlvds.In_n"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
C {devices/code_shown.sym} -3600 -1650 0 0 {name=NGSPICE
only_toplevel=true
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
* gear2 collapses the timestep to 6e-24 s at 414 ns on vvdd_1v2#branch
* once the PLL's XSPICE bridges are in the netlist, and the run stops
* there whatever tstop says.  trap gets through the full span.
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
* Without this the H-bridge cannot balance at t=0, cmfb runs to the rail and the
* pair spends ~60 ns climbing back (tb_startup measures 61.3 ns).  The driver's
* own benches place cmfb the same way and run no operating point.
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.control
* The top cell carries pll_cosim, whose RTL half only couples to the analog
* loop once ngspice holds the auto-bridge templates.  Those are injected into
* the netlist after xschem writes it, by scripts/pll/inject_cosim_bridges.py,
* because the quotes their syntax needs would end xschem's value=... property
* and silently take .endc with them.
*
* make sim-xschem netlists, injects, then simulates.  The Simulate arrow in
* xschem does not netlist - it runs ngspice on whatever netlist is already
* there, so it works after a make run and fails after xschem has written a
* fresh one.  Without the bridges nothing couples and every waveform comes
* out flat, so stop here rather than produce a plausible-looking lie.
if $?auto_bridge_d_in = 0
  echo
  echo ERROR: d_cosim auto-bridges are not set, so the PLL is disconnected.
  echo Fix: run make sim-xschem with the TB= name of this bench.
  echo The Simulate arrow reuses that netlist afterwards and will work.
  echo
* quit 1 rather than quit: xschem runs ngspice in a terminal that falls back
* to a shell only on a non-zero exit.  Quitting with zero closes the window
* before the message above can be read.
  quit 1
end
* xpll is pll_cosim: the PFD and both dividers are the RTL of
* macros/pll_digital, through d_cosim.  The analog/digital bridges are
* inserted into the netlist by scripts/pll/inject_cosim_bridges.py - they
* cannot live here: xschem ends the value property at the first quote.
* Build the shared object first: make pll-cosim-so.
* save all over 120 ns at 5 ps writes a 292 MB rawfile; name what the
* measurements, the wrdata and the four graph panels actually need.
* In_p / In_n are the pre-driver pair inside xlvds - the last node before
* the output stage, and where a common-mode problem shows up first.
save d_p d_n vos x1.core_p x1.core_n x1.xpat.gclk_b i(Vvdd_3v3) i(Vvdd_1v2)
+ x1.xlvds.In_p x1.xlvds.In_n
* 500 Mb/s means 2 ns a bit, so a full PRBS-7 period is 254 ns.  600 ns gives
* one settling stretch plus about 225 bits of settled data to measure on.
tran 5p 600n 0 5p
write @schname\\\\.raw

* did the pattern generator actually get a clock?  A static pair means the
* control path is broken, not the driver.
meas tran clk_pp PP v(x1.xpat.gclk_b) from=150n to=595n
meas tran core_pp PP v(x1.core_p) from=150n to=595n
print clk_pp core_pp

* TIA/EIA-644-A 4.1.1 and 4.1.2 on the settled pattern
let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=150n to=595n
meas tran vod_min MIN vod from=150n to=595n
meas tran vos_avg AVG v(vos) from=150n to=595n
meas tran vos_max MAX v(vos) from=150n to=595n
meas tran vos_min MIN v(vos) from=150n to=595n
let vos_pp = vos_max - vos_min
* the cold start, kept in the log so the settled number is not mistaken for it
meas tran vos_pp_early PP v(vos) from=20n to=100n
meas tran vos_pp_mid PP v(vos) from=100n to=150n
print vod_max vod_min vos_avg vos_pp
print vos_pp_early vos_pp_mid
* print on a transient vector dumps every timepoint - measure instead
meas tran i_3v3 AVG i(Vvdd_3v3) from=150n to=595n
meas tran i_1v2 AVG i(Vvdd_1v2) from=150n to=595n
print i_3v3 i_1v2

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n)
.endc
"}
