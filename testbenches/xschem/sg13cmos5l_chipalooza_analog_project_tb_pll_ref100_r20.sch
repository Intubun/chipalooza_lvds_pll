v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {PLL bench ref100_r20: 100 MHz reference in, PRBS-7 at 1 Gb/s out.

  2 GHz VCO, the fast end - the other characterised row

  VCO      = REF * DIV_RATIO   = 2 GHz
  pll_clk  = VCO / 2           = 1 GHz   <- the line rate
  test_clk = VCO / 8           = 250 MHz   <- on analog_pin[1]

  DIV_RATIO = 20, code 160 = 0010100000
              integer part 20 in div_ratio[9:3], 0/8 in div_ratio[2:0]

  1 ns       PLL RESET_N released
  2 ns       PLL ENABLE
  4.50 us    PRBS reset released, then the pattern generator enabled

The run is 6 us because the loop needs it: pll_integer_characterization.csv
measures lock at 2.75 us typical and 4.50 us slow, so the earlier 1 us bench was
reading a frequency the loop had not settled to yet.

f_pll is averaged over ~1200 cycles late in the run rather than across two
adjacent edges.  fractional_divider.v is a plain N/N+1 accumulator with no
delta-sigma, so at a fractional ratio the instantaneous period alternates and
only the average over a whole accumulator cycle is the number worth reading.

Every DIV_RATIO and TEST_DIV bit carries its own source, including the zeros.

No pad or ESD model, so the Vos figure here is not the compliance number.} -3600 -2400 0 0 0.45 0.45 {}
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
T {LVDS common-mode reference, 1.2 V} -1920 -1185 0 0 0.3 0.3 {}
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
N -2000 -640 -2000 -610 {lab=analog_bus[0]}
C {devices/lab_wire.sym} -2000 -640 0 0 {name=ls_analog_bus_0 sig_type=std_logic lab=analog_bus[0]}
C {isource.sym} -2000 -580 0 0 {name=Ianalog_bus_0 value=-2u}
N -2000 -550 -2000 -520 {lab=GND}
C {devices/gnd.sym} -2000 -520 0 0 {name=lg_analog_bus_0 lab=GND}
T {PLL charge-pump reference - 2 uA, not the transmitter's 30 uA} -1920 -585 0 0 0.3 0.3 {}
L 3 -2260 -1300 -1340 -1300 {}
L 3 -1340 -1300 -1340 -460 {}
L 3 -2260 -460 -1340 -460 {}
L 3 -2260 -1300 -2260 -460 {}
T {bias} -2260 -1355 0 0 0.4 0.4 {}
N -2000 -320 -2000 -290 {lab=dig_in[6]}
C {devices/lab_wire.sym} -2000 -320 0 0 {name=ls_dig_in_6 sig_type=std_logic lab=dig_in[6]}
C {devices/vsource.sym} -2000 -260 0 0 {name=Vdig_in_6 value="PWL(0 0 1n 0 1.1n 1.2)"}
N -2000 -230 -2000 -200 {lab=GND}
C {devices/gnd.sym} -2000 -200 0 0 {name=lg_dig_in_6 lab=GND}
T {PLL RESET_N, active low} -1920 -265 0 0 0.3 0.3 {}
N -2000 -120 -2000 -90 {lab=dig_in[5]}
C {devices/lab_wire.sym} -2000 -120 0 0 {name=ls_dig_in_5 sig_type=std_logic lab=dig_in[5]}
C {devices/vsource.sym} -2000 -60 0 0 {name=Vdig_in_5 value="PWL(0 0 2n 0 2.1n 1.2)"}
N -2000 -30 -2000 0 {lab=GND}
C {devices/gnd.sym} -2000 0 0 0 {name=lg_dig_in_5 lab=GND}
T {PLL ENABLE} -1920 -65 0 0 0.3 0.3 {}
L 3 -2260 -380 -1340 -380 {}
L 3 -1340 -380 -1340 60 {}
L 3 -2260 60 -1340 60 {}
L 3 -2260 -380 -2260 60 {}
T {PLL control} -2260 -435 0 0 0.4 0.4 {}
N -2000 200 -2000 230 {lab=dig_in[16]}
C {devices/lab_wire.sym} -2000 200 0 0 {name=ls_dig_in_16 sig_type=std_logic lab=dig_in[16]}
C {devices/vsource.sym} -2000 260 0 0 {name=Vdig_in_16 value="0"}
N -2000 290 -2000 320 {lab=GND}
C {devices/gnd.sym} -2000 320 0 0 {name=lg_dig_in_16 lab=GND}
T {DIV_RATIO[9] = 0   weight integer 64} -1920 255 0 0 0.3 0.3 {}
N -2000 400 -2000 430 {lab=dig_in[15]}
C {devices/lab_wire.sym} -2000 400 0 0 {name=ls_dig_in_15 sig_type=std_logic lab=dig_in[15]}
C {devices/vsource.sym} -2000 460 0 0 {name=Vdig_in_15 value="0"}
N -2000 490 -2000 520 {lab=GND}
C {devices/gnd.sym} -2000 520 0 0 {name=lg_dig_in_15 lab=GND}
T {DIV_RATIO[8] = 0   weight integer 32} -1920 455 0 0 0.3 0.3 {}
N -2000 600 -2000 630 {lab=dig_in[14]}
C {devices/lab_wire.sym} -2000 600 0 0 {name=ls_dig_in_14 sig_type=std_logic lab=dig_in[14]}
C {devices/vsource.sym} -2000 660 0 0 {name=Vdig_in_14 value="1.2"}
N -2000 690 -2000 720 {lab=GND}
C {devices/gnd.sym} -2000 720 0 0 {name=lg_dig_in_14 lab=GND}
T {DIV_RATIO[7] = 1   weight integer 16} -1920 655 0 0 0.3 0.3 {}
N -2000 800 -2000 830 {lab=dig_in[13]}
C {devices/lab_wire.sym} -2000 800 0 0 {name=ls_dig_in_13 sig_type=std_logic lab=dig_in[13]}
C {devices/vsource.sym} -2000 860 0 0 {name=Vdig_in_13 value="0"}
N -2000 890 -2000 920 {lab=GND}
C {devices/gnd.sym} -2000 920 0 0 {name=lg_dig_in_13 lab=GND}
T {DIV_RATIO[6] = 0   weight integer 8} -1920 855 0 0 0.3 0.3 {}
N -2000 1000 -2000 1030 {lab=dig_in[12]}
C {devices/lab_wire.sym} -2000 1000 0 0 {name=ls_dig_in_12 sig_type=std_logic lab=dig_in[12]}
C {devices/vsource.sym} -2000 1060 0 0 {name=Vdig_in_12 value="1.2"}
N -2000 1090 -2000 1120 {lab=GND}
C {devices/gnd.sym} -2000 1120 0 0 {name=lg_dig_in_12 lab=GND}
T {DIV_RATIO[5] = 1   weight integer 4} -1920 1055 0 0 0.3 0.3 {}
N -2000 1200 -2000 1230 {lab=dig_in[11]}
C {devices/lab_wire.sym} -2000 1200 0 0 {name=ls_dig_in_11 sig_type=std_logic lab=dig_in[11]}
C {devices/vsource.sym} -2000 1260 0 0 {name=Vdig_in_11 value="0"}
N -2000 1290 -2000 1320 {lab=GND}
C {devices/gnd.sym} -2000 1320 0 0 {name=lg_dig_in_11 lab=GND}
T {DIV_RATIO[4] = 0   weight integer 2} -1920 1255 0 0 0.3 0.3 {}
N -2000 1400 -2000 1430 {lab=dig_in[10]}
C {devices/lab_wire.sym} -2000 1400 0 0 {name=ls_dig_in_10 sig_type=std_logic lab=dig_in[10]}
C {devices/vsource.sym} -2000 1460 0 0 {name=Vdig_in_10 value="0"}
N -2000 1490 -2000 1520 {lab=GND}
C {devices/gnd.sym} -2000 1520 0 0 {name=lg_dig_in_10 lab=GND}
T {DIV_RATIO[3] = 0   weight integer 1} -1920 1455 0 0 0.3 0.3 {}
N -2000 1600 -2000 1630 {lab=dig_in[9]}
C {devices/lab_wire.sym} -2000 1600 0 0 {name=ls_dig_in_9 sig_type=std_logic lab=dig_in[9]}
C {devices/vsource.sym} -2000 1660 0 0 {name=Vdig_in_9 value="0"}
N -2000 1690 -2000 1720 {lab=GND}
C {devices/gnd.sym} -2000 1720 0 0 {name=lg_dig_in_9 lab=GND}
T {DIV_RATIO[2] = 0   weight 1/2} -1920 1655 0 0 0.3 0.3 {}
N -2000 1800 -2000 1830 {lab=dig_in[8]}
C {devices/lab_wire.sym} -2000 1800 0 0 {name=ls_dig_in_8 sig_type=std_logic lab=dig_in[8]}
C {devices/vsource.sym} -2000 1860 0 0 {name=Vdig_in_8 value="0"}
N -2000 1890 -2000 1920 {lab=GND}
C {devices/gnd.sym} -2000 1920 0 0 {name=lg_dig_in_8 lab=GND}
T {DIV_RATIO[1] = 0   weight 1/4} -1920 1855 0 0 0.3 0.3 {}
N -2000 2000 -2000 2030 {lab=dig_in[7]}
C {devices/lab_wire.sym} -2000 2000 0 0 {name=ls_dig_in_7 sig_type=std_logic lab=dig_in[7]}
C {devices/vsource.sym} -2000 2060 0 0 {name=Vdig_in_7 value="0"}
N -2000 2090 -2000 2120 {lab=GND}
C {devices/gnd.sym} -2000 2120 0 0 {name=lg_dig_in_7 lab=GND}
T {DIV_RATIO[0] = 0   weight 1/8} -1920 2055 0 0 0.3 0.3 {}
L 3 -2260 140 -1340 140 {}
L 3 -1340 140 -1340 2180 {}
L 3 -2260 2180 -1340 2180 {}
L 3 -2260 140 -2260 2180 {}
T {DIV_RATIO = 20   code 160 = 0010100000} -2260 85 0 0 0.4 0.4 {}
N -2000 2320 -2000 2350 {lab=dig_in[18]}
C {devices/lab_wire.sym} -2000 2320 0 0 {name=ls_dig_in_18 sig_type=std_logic lab=dig_in[18]}
C {devices/vsource.sym} -2000 2380 0 0 {name=Vdig_in_18 value="1.2"}
N -2000 2410 -2000 2440 {lab=GND}
C {devices/gnd.sym} -2000 2440 0 0 {name=lg_dig_in_18 lab=GND}
T {TEST_DIV[1] = 1} -1920 2375 0 0 0.3 0.3 {}
N -2000 2520 -2000 2550 {lab=dig_in[17]}
C {devices/lab_wire.sym} -2000 2520 0 0 {name=ls_dig_in_17 sig_type=std_logic lab=dig_in[17]}
C {devices/vsource.sym} -2000 2580 0 0 {name=Vdig_in_17 value="0"}
N -2000 2610 -2000 2640 {lab=GND}
C {devices/gnd.sym} -2000 2640 0 0 {name=lg_dig_in_17 lab=GND}
T {TEST_DIV[0] = 0} -1920 2575 0 0 0.3 0.3 {}
L 3 -2260 2260 -1340 2260 {}
L 3 -1340 2260 -1340 2700 {}
L 3 -2260 2700 -1340 2700 {}
L 3 -2260 2260 -2260 2700 {}
T {TEST_DIV = 2   TEST_CLK = VCO/8} -2260 2205 0 0 0.4 0.4 {}
N -2000 2840 -2000 2870 {lab=dig_in[0]}
C {devices/lab_wire.sym} -2000 2840 0 0 {name=ls_dig_in_0 sig_type=std_logic lab=dig_in[0]}
C {devices/vsource.sym} -2000 2900 0 0 {name=Vdig_in_0 value="1.2"}
N -2000 2930 -2000 2960 {lab=GND}
C {devices/gnd.sym} -2000 2960 0 0 {name=lg_dig_in_0 lab=GND}
T {clk_src = 1, pattern generator off the PLL} -1920 2895 0 0 0.3 0.3 {}
N -2000 3040 -2000 3070 {lab=dig_in[1]}
C {devices/lab_wire.sym} -2000 3040 0 0 {name=ls_dig_in_1 sig_type=std_logic lab=dig_in[1]}
C {devices/vsource.sym} -2000 3100 0 0 {name=Vdig_in_1 value="PWL(0 0 4.500u 0 4.501u 1.2)"}
N -2000 3130 -2000 3160 {lab=GND}
C {devices/gnd.sym} -2000 3160 0 0 {name=lg_dig_in_1 lab=GND}
T {pattern en, held off until the loop has locked} -1920 3095 0 0 0.3 0.3 {}
N -2000 3240 -2000 3270 {lab=dig_in[2]}
C {devices/lab_wire.sym} -2000 3240 0 0 {name=ls_dig_in_2 sig_type=std_logic lab=dig_in[2]}
C {devices/vsource.sym} -2000 3300 0 0 {name=Vdig_in_2 value="PWL(0 1.2 4.490u 1.2 4.491u 0)"}
N -2000 3330 -2000 3360 {lab=GND}
C {devices/gnd.sym} -2000 3360 0 0 {name=lg_dig_in_2 lab=GND}
T {PRBS reset, released just before en} -1920 3295 0 0 0.3 0.3 {}
N -2000 3440 -2000 3470 {lab=dig_in[3]}
C {devices/lab_wire.sym} -2000 3440 0 0 {name=ls_dig_in_3 sig_type=std_logic lab=dig_in[3]}
C {devices/vsource.sym} -2000 3500 0 0 {name=Vdig_in_3 value="1.2"}
N -2000 3530 -2000 3560 {lab=GND}
C {devices/gnd.sym} -2000 3560 0 0 {name=lg_dig_in_3 lab=GND}
T {mode = 1, PRBS-7} -1920 3495 0 0 0.3 0.3 {}
L 3 -2260 2780 -1340 2780 {}
L 3 -1340 2780 -1340 3620 {}
L 3 -2260 3620 -1340 3620 {}
L 3 -2260 2780 -2260 3620 {}
T {pattern control} -2260 2725 0 0 0.4 0.4 {}
N -2000 3760 -2000 3790 {lab=analog_pin[0]}
C {devices/lab_wire.sym} -2000 3760 0 0 {name=ls_analog_pin_0 sig_type=std_logic lab=analog_pin[0]}
C {devices/vsource.sym} -2000 3820 0 0 {name=Vanalog_pin_0 value="PULSE(0 1.2 0 50p 50p 4.9500n 10.0000n)"}
N -2000 3850 -2000 3880 {lab=GND}
C {devices/gnd.sym} -2000 3880 0 0 {name=lg_analog_pin_0 lab=GND}
T {REF_CLK, 100 MHz} -1920 3815 0 0 0.3 0.3 {}
L 3 -2260 3700 -1340 3700 {}
L 3 -1340 3700 -1340 3940 {}
L 3 -2260 3940 -1340 3940 {}
L 3 -2260 3700 -2260 3940 {}
T {reference clock} -2260 3645 0 0 0.4 0.4 {}
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
tclcommand="xschem raw_read $netlist_dir/sg13cmos5l_chipalooza_analog_project_tb_pll_ref100_r20.raw tran"
}
C {launcher.sym} 2050 -2070 0 0 {name=h_check
descr="Check PRBS + timing"
tclcommand="exec python3 [file dirname [xschem get current_dirname]]/../../scripts/check_timing.py &"
}
B 2 2050 -1950 3850 -1550 {flags=graph,unlocked
y1=0
y2=1.3
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=6e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="x1.xpll.x_analog.VCTRL"
color="8"
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
x1=4.8e-06
x2=4.81e-06
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
B 2 2050 -950 3850 -550 {flags=graph
y1=0.9
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=4.8e-06
x2=4.81e-06
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
B 2 2050 -450 3850 -50 {flags=graph
y1=-0.2
y2=3.5
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=4.8e-06
x2=4.81e-06
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
.ic v(x1.xlvds.xdrv.cmfb)=1.54
* gear2 collapses the timestep once the PLL XSPICE bridges are in the netlist,
* and the run then stops early whatever tstop says.  trap gets through.
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
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
save d_p d_n vos x1.core_p x1.core_n x1.pll_clk
+ x1.xpll.x_analog.VCTRL x1.xpll.VCO_CLK x1.xpll.FB_CLK x1.xpll.UP x1.xpll.DOWN
+ x1.xlvds.In_p x1.xlvds.In_n
tran 1.25e-11 6e-06 0 1.25e-11
write @schname\\\\.raw

* First: does the loop do anything at all?  VCTRL has to move and the VCO has
* to oscillate before any number below means anything.
meas tran vctrl_min MIN v(x1.xpll.x_analog.VCTRL) from=50n to=5.95e-06
meas tran vctrl_max MAX v(x1.xpll.x_analog.VCTRL) from=50n to=5.95e-06
meas tran vctrl_end AVG v(x1.xpll.x_analog.VCTRL) from=5.45e-06 to=5.95e-06
meas tran vco_pp PP v(x1.xpll.VCO_CLK) from=5.45e-06 to=5.95e-06
* FB_CLK used to be measurable because the XSPICE divider drove it through a
* dac_bridge.  Under d_cosim it is a digital output that no analog node
* consumes, so it carries no voltage waveform - and f_pll answers the question
* it was there to answer.
print vctrl_min vctrl_max vctrl_end vco_pp

* Second: is pll_clk on target?  Averaged over 1200 cycles, because the
* N/N+1 divider makes any single period the wrong thing to measure.
meas tran t1 WHEN v(x1.pll_clk)=0.6 RISE=4500
meas tran t2 WHEN v(x1.pll_clk)=0.6 RISE=5700
let f_pll = 1200/(t2-t1)
let f_pll_target = 1e+09
let f_pll_err_ppm = 1e6*(f_pll-f_pll_target)/f_pll_target
print f_pll f_pll_target f_pll_err_ppm

* Third: what leaves the transmitter once the pattern generator runs
let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=4.6e-06 to=5.95e-06
meas tran vod_min MIN vod from=4.6e-06 to=5.95e-06
meas tran vos_avg AVG v(vos) from=4.6e-06 to=5.95e-06
meas tran vos_max MAX v(vos) from=4.6e-06 to=5.95e-06
meas tran vos_min MIN v(vos) from=4.6e-06 to=5.95e-06
let vos_pp = vos_max - vos_min
meas tran core_pp PP v(x1.core_p) from=4.6e-06 to=5.95e-06
print vod_max vod_min vos_avg vos_pp core_pp

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.pll_clk) v(x1.xpll.x_analog.VCTRL)
.endc
"}
