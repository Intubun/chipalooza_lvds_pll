v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {LVDS bench for the top cell - the schematic, and the ODT switched on and off.

ref_clk comes from a 50 ohm generator onto pad 2 (s14_an[2]), through the pad's
IO cell and its secondary protection to s14_an_2_esd.  xodt hangs on pad 2.
The run has three phases:

  A    0 - 300 ns   ODT off, EMF 1.2 V   pad 1.2 V, no current into the pad
  B  300 - 400 ns   ODT on,  EMF 1.2 V   pad halved to 0.6 V: 50 ohm into 50 ohm
                                        (too small for the clock - the pattern stalls)
  C  400 - 700 ns   ODT on,  EMF 2.4 V   pad 1.2 V again, 24 mA while high;
                                        reset at 400 ns, PRBS-7 runs again;
                                        the output back-termination on (dig_in[4])
                                        and ibias1 3 uA

PRBS-7 at 500 Mb/s through the pre-driver and the driver into 49.9 + 49.9 ohm
across pads 1 and 0 with the Vos tap.  The log prints each phase: the clock at
the pad and behind the protection, the pad current, Vod / Vos, the supplies.

Only pad 2 is modelled (its IO cell is what joins s14_an[2] to s14_an_2_esd);
the outputs see an ideal 100 ohm.  Pads, bond wires, package and line on all
three: slot_14_tb_lvds_pads (layout wiring) and slot_14_tb_lvds_pex.} -3600 -2400 0 0 0.45 0.45 {}
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
N -2000 -1360 -2000 -1330 {lab=iovdd}
C {devices/lab_wire.sym} -2000 -1360 0 0 {name=ls_iovdd sig_type=std_logic lab=iovdd}
C {devices/vsource.sym} -2000 -1300 0 0 {name=Viovdd value="3.3"}
N -2000 -1270 -2000 -1240 {lab=GND}
C {devices/gnd.sym} -2000 -1240 0 0 {name=lg_iovdd lab=GND}
T {pad ring, 3.3 V - pad 2's IO cell} -1920 -1305 0 0 0.3 0.3 {}
L 3 -2260 -1820 -1340 -1820 {}
L 3 -1340 -1820 -1340 -1180 {}
L 3 -2260 -1180 -1340 -1180 {}
L 3 -2260 -1820 -2260 -1180 {}
T {supplies} -2260 -1875 0 0 0.4 0.4 {}
N -2000 -1040 -2000 -1010 {lab=vbias}
C {devices/lab_wire.sym} -2000 -1040 0 0 {name=ls_vbias sig_type=std_logic lab=vbias}
C {devices/vsource.sym} -2000 -980 0 0 {name=Vvbias value="1.2"}
N -2000 -950 -2000 -920 {lab=GND}
C {devices/gnd.sym} -2000 -920 0 0 {name=lg_vbias lab=GND}
T {LVDS common-mode reference, 1.2 V from the harness voltage reference} -1920 -985 0 0 0.3 0.3 {}
N -2000 -840 -2000 -810 {lab=ibias0}
C {devices/lab_wire.sym} -2000 -840 0 0 {name=ls_ibias0 sig_type=std_logic lab=ibias0}
C {isource.sym} -2000 -780 0 0 {name=Iibias0 value="-1.935u"}
N -2000 -750 -2000 -720 {lab=GND}
C {devices/gnd.sym} -2000 -720 0 0 {name=lg_ibias0 lab=GND}
T {pre-driver reference, IDAC code 6 = 1.935uA into the 1:15 mirror} -1920 -785 0 0 0.3 0.3 {}
N -2000 -640 -2000 -610 {lab=ibias1}
C {devices/lab_wire.sym} -2000 -640 0 0 {name=ls_ibias1 sig_type=std_logic lab=ibias1}
C {isource.sym} -2000 -580 0 0 {name=Iibias1 value="PWL(0 -1.935u 400n -1.935u 400.1n -2.903u)"}
N -2000 -550 -2000 -520 {lab=GND}
C {devices/gnd.sym} -2000 -520 0 0 {name=lg_ibias1 lab=GND}
T {driver reference, code 6; code 9 = 2.903uA from 400 ns} -1920 -585 0 0 0.3 0.3 {}
L 3 -2260 -1100 -1340 -1100 {}
L 3 -1340 -1100 -1340 -460 {}
L 3 -2260 -460 -1340 -460 {}
L 3 -2260 -1100 -2260 -460 {}
T {bias} -2260 -1155 0 0 0.4 0.4 {}
N -2000 -320 -2000 -290 {lab=dig_in[0]}
C {devices/lab_wire.sym} -2000 -320 0 0 {name=ls_dig_in_0 sig_type=std_logic lab=dig_in[0]}
C {devices/vsource.sym} -2000 -260 0 0 {name=Vdig_in_0 value="PWL(0 0 300n 0 300.1n 1.2)"}
N -2000 -230 -2000 -200 {lab=GND}
C {devices/gnd.sym} -2000 -200 0 0 {name=lg_dig_in_0 lab=GND}
T {ODT: off, on from 300 ns} -1920 -265 0 0 0.3 0.3 {}
N -2000 -120 -2000 -90 {lab=dig_in[1]}
C {devices/lab_wire.sym} -2000 -120 0 0 {name=ls_dig_in_1 sig_type=std_logic lab=dig_in[1]}
C {devices/vsource.sym} -2000 -60 0 0 {name=Vdig_in_1 value="PWL(0 0 3n 0 3.1n 1.2)"}
N -2000 -30 -2000 0 {lab=GND}
C {devices/gnd.sym} -2000 0 0 0 {name=lg_dig_in_1 lab=GND}
T {en, low until 3 ns} -1920 -65 0 0 0.3 0.3 {}
N -2000 80 -2000 110 {lab=dig_in[2]}
C {devices/lab_wire.sym} -2000 80 0 0 {name=ls_dig_in_2 sig_type=std_logic lab=dig_in[2]}
C {devices/vsource.sym} -2000 140 0 0 {name=Vdig_in_2 value="PWL(0 1.2 2n 1.2 2.1n 0 400n 0 400.1n 1.2 402n 1.2 402.1n 0)"}
N -2000 170 -2000 200 {lab=GND}
C {devices/gnd.sym} -2000 200 0 0 {name=lg_dig_in_2 lab=GND}
T {reset until 2 ns, again at 400 ns} -1920 135 0 0 0.3 0.3 {}
N -2000 280 -2000 310 {lab=dig_in[3]}
C {devices/lab_wire.sym} -2000 280 0 0 {name=ls_dig_in_3 sig_type=std_logic lab=dig_in[3]}
C {devices/vsource.sym} -2000 340 0 0 {name=Vdig_in_3 value="1.2"}
N -2000 370 -2000 400 {lab=GND}
C {devices/gnd.sym} -2000 400 0 0 {name=lg_dig_in_3 lab=GND}
T {mode = 1, PRBS-7 throughout} -1920 335 0 0 0.3 0.3 {}
N -2000 480 -2000 510 {lab=dig_in[4]}
C {devices/lab_wire.sym} -2000 480 0 0 {name=ls_dig_in_4 sig_type=std_logic lab=dig_in[4]}
C {devices/vsource.sym} -2000 540 0 0 {name=Vdig_in_4 value="PWL(0 0 400n 0 400.1n 1.2)"}
N -2000 570 -2000 600 {lab=GND}
C {devices/gnd.sym} -2000 600 0 0 {name=lg_dig_in_4 lab=GND}
T {back-termination: off, on from 400 ns} -1920 535 0 0 0.3 0.3 {}
L 3 -2260 -380 -1340 -380 {}
L 3 -1340 -380 -1340 660 {}
L 3 -2260 660 -1340 660 {}
L 3 -2260 -380 -2260 660 {}
T {pattern control} -2260 -435 0 0 0.4 0.4 {}
N -300 -350 -240 -350 {lab=vdd_3v3}
C {devices/lab_wire.sym} -300 -350 0 0 {name=lx_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
N -300 -330 -240 -330 {lab=vdd_1v2}
C {devices/lab_wire.sym} -300 -330 0 0 {name=lx_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
N -300 -310 -240 -310 {lab=GND}
C {devices/gnd.sym} -300 -310 1 0 {name=lgg_vss_3v3 lab=GND}
N -300 -290 -240 -290 {lab=GND}
C {devices/gnd.sym} -300 -290 1 0 {name=lgg_vss_1v2 lab=GND}
N -300 -270 -240 -270 {lab=enable}
C {devices/lab_wire.sym} -300 -270 0 0 {name=lx_enable sig_type=std_logic lab=enable}
N -300 -250 -240 -250 {lab=clk}
C {devices/lab_wire.sym} -300 -250 0 0 {name=lx_clk sig_type=std_logic lab=clk}
N -300 -230 -240 -230 {lab=reset}
C {devices/lab_wire.sym} -300 -230 0 0 {name=lx_reset sig_type=std_logic lab=reset}
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
N -300 270 -240 270 {lab=ibias0}
C {devices/lab_wire.sym} -300 270 0 0 {name=lx_ibias0 sig_type=std_logic lab=ibias0}
N -300 290 -240 290 {lab=ibias1}
C {devices/lab_wire.sym} -300 290 0 0 {name=lx_ibias1 sig_type=std_logic lab=ibias1}
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
N 240 -110 300 -110 {lab=s14_an[2]}
C {devices/lab_wire.sym} 300 -110 0 0 {name=lx_s14_an_2 sig_type=std_logic lab=s14_an[2]}
N 240 -50 300 -50 {lab=s14_an_2_esd}
C {devices/lab_wire.sym} 300 -50 0 0 {name=lx_s14_an_2_esd sig_type=std_logic lab=s14_an_2_esd}
N 240 -30 300 -30 {lab=s14_an_1_esd}
C {devices/lab_wire.sym} 300 -30 0 0 {name=lx_s14_an_1_esd sig_type=std_logic lab=s14_an_1_esd}
N 240 -10 300 -10 {lab=s14_an_0_esd}
C {devices/lab_wire.sym} 300 -10 0 0 {name=lx_s14_an_0_esd sig_type=std_logic lab=s14_an_0_esd}
N 240 10 300 10 {lab=analog_bus0}
C {devices/lab_wire.sym} 300 10 0 0 {name=lx_analog_bus0 sig_type=std_logic lab=analog_bus0}
N 240 30 300 30 {lab=analog_bus1}
C {devices/lab_wire.sym} 300 30 0 0 {name=lx_analog_bus1 sig_type=std_logic lab=analog_bus1}
N 240 50 300 50 {lab=analog_bus2}
C {devices/lab_wire.sym} 300 50 0 0 {name=lx_analog_bus2 sig_type=std_logic lab=analog_bus2}
N 240 70 300 70 {lab=analog_bus3}
C {devices/lab_wire.sym} 300 70 0 0 {name=lx_analog_bus3 sig_type=std_logic lab=analog_bus3}
C {slot_14.sym} 0 0 0 0 {name=x1}
N 240 -90 1000 -90 {lab=s14_an[1]}
N 1000 -295 1000 -90 {lab=s14_an[1]}
C {devices/lab_wire.sym} 1000 -193 0 0 {name=lpad_d_p sig_type=std_logic lab=s14_an[1]}
C {devices/vsource.sym} 1000 -325 0 0 {name=Vd_p value=0}
N 1000 -560 1000 -355 {lab=d_p}
C {devices/lab_wire.sym} 1000 -458 0 0 {name=lmeas_d_p sig_type=std_logic lab=d_p}
N 1000 -560 1560 -560 {lab=d_p}
N 240 -70 1120 -70 {lab=s14_an[0]}
N 1120 -70 1120 165 {lab=s14_an[0]}
C {devices/lab_wire.sym} 1120 47 0 0 {name=lpad_d_n sig_type=std_logic lab=s14_an[0]}
C {devices/vsource.sym} 1120 195 0 0 {name=Vd_n value=0}
N 1120 225 1120 460 {lab=d_n}
C {devices/lab_wire.sym} 1120 342 0 0 {name=lmeas_d_n sig_type=std_logic lab=d_n}
N 1120 460 1560 460 {lab=d_n}
N 1560 -560 1560 -335 {lab=d_p}
C {res.sym} 1560 -305 0 0 {name=Rtd_p value=49.9}
N 1560 -275 1560 -50 {lab=vos}
N 1560 -50 1560 175 {lab=vos}
C {res.sym} 1560 205 0 0 {name=Rtd_n value=49.9}
N 1560 235 1560 460 {lab=d_n}
N 1560 -50 1700 -50 {lab=vos}
C {devices/lab_wire.sym} 1700 -50 0 0 {name=lvos sig_type=std_logic lab=vos}
C {devices/vsource.sym} 500 1000 0 0 {name=Vclk_a value="PULSE(0 1.2 0 50p 50p 0.9n 2n)"}
C {lab_pin.sym} 500 970 0 0 {name=lr_Vclk_a_t sig_type=std_logic lab=clk_mid}
C {devices/gnd.sym} 500 1030 0 0 {name=lgr_Vclk_a_b lab=GND}
C {devices/vsource.sym} 500 800 0 0 {name=Vclk_b value="PULSE(0 1.2 400n 50p 50p 0.9n 2n)"}
C {lab_pin.sym} 500 770 0 0 {name=lr_Vclk_b_t sig_type=std_logic lab=clk_gen}
C {lab_pin.sym} 500 830 0 0 {name=lr_Vclk_b_b sig_type=std_logic lab=clk_mid}
C {res.sym} 800 800 0 0 {name=Rgen value="50"}
C {lab_pin.sym} 800 770 0 0 {name=lr_Rgen_t sig_type=std_logic lab=clk_gen}
C {lab_pin.sym} 800 830 0 0 {name=lr_Rgen_b sig_type=std_logic lab=clk_pad}
C {devices/vsource.sym} 1000 800 0 0 {name=Vpad2 value="0"}
C {lab_pin.sym} 1000 770 0 0 {name=lr_Vpad2_t sig_type=std_logic lab=clk_pad}
C {lab_pin.sym} 1000 830 0 0 {name=lr_Vpad2_b sig_type=std_logic lab=s14_an[2]}
C {sg13cmos5l_io/sg13cmos5l_IOPadAnalog.sym} 1300 1250 0 0 {name=xpad2}
C {devices/gnd.sym} 1307.5 910 0 0 {name=lgr_pad2_vss lab=GND}
C {lab_pin.sym} 1317.5 920 0 0 {name=lr_pad2_vdd sig_type=std_logic lab=vdd_1v2}
C {devices/gnd.sym} 1327.5 930 0 0 {name=lgr_pad2_iovss lab=GND}
C {lab_pin.sym} 1340 940 0 0 {name=lr_pad2_iovdd sig_type=std_logic lab=iovdd}
C {lab_pin.sym} 1400 900 0 0 {name=lr_pad2_pad sig_type=std_logic lab=s14_an[2]}
C {lab_pin.sym} 1500 900 0 0 {name=lr_pad2_padres sig_type=std_logic lab=s14_an_2_esd}
C {lab_pin.sym} 1410 1150 0 0 {name=lr_pad2_bond sig_type=std_logic lab=s14_an[2]}
T {ref_clk: 50 ohm generator onto pad 2.  Vclk_b joins at 400 ns:
EMF 1.2 V before, 2.4 V after (1.2 V into 50 ohm).
Vpad2 is the ammeter: the current into the pad, i.e. into xodt.} 400 580 0 0 0.35 0.35 {}
T {pad 2: IOPadAnalog (PDK model) - pad = s14_an[2] with xodt,
padres = s14_an_2_esd, the ref_clk input of lvds_pattern} 1200 1310 0 0 0.3 0.3 {}
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
tclcommand="xschem raw_read $netlist_dir/slot_14_tb_lvds.raw tran"
}
C {launcher.sym} 2050 -2070 0 0 {name=h_check
descr="Check PRBS + timing"
tclcommand="exec python3 [file dirname [xschem get current_dirname]]/../../scripts/check_timing.py &"
}
B 2 2050 -1950 3850 -1550 {flags=graph
y1=-0.2
y2=3.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=7e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="dig_in_0_
x1.xodt.enh"
color="8 10"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 -1450 3850 -1050 {flags=graph
y1=-0.2
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=7e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="clk_pad
x1.xodt.x
s14_an_2_esd"
color="4 12 7"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 -950 3850 -550 {flags=graph
y1=-0.01
y2=0.03
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=7e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="i(vpad2)"
color="4"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 -450 3850 -50 {flags=graph
y1=0.9
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=7e-07
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
B 2 2050 50 3850 450 {flags=graph,unlocked
y1=-0.2
y2=3.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2.94e-07
x2=3.08e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="dig_in_0_
x1.xodt.enh
clk_pad
x1.xodt.x"
color="8 10 4 12"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 550 3850 950 {flags=graph,unlocked
y1=-0.01
y2=0.03
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2.94e-07
x2=3.08e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="i(vpad2)"
color="4"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 1050 3850 1450 {flags=graph,unlocked
y1=-0.01
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=3.96e-07
x2=4.08e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="clk_pad
i(vpad2)"
color="4"
dataset=-1
unitx=1
logx=0
logy=0
autoload=0
hilight_wave=-1}
B 2 2050 1550 3850 1950 {flags=graph,unlocked
y1=-0.5
y2=1.6
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=6.5e-07
x2=6.6e-07
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="d_p
d_n
\\"vod;d_p d_n -\\""
color="4 5 7"
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
.include ../../../models/diodes_tt0.lib
.include sg13g2_esd.lib
.include cap_cmomf.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_io/spice/sg13cmos5l_io.spi
* the substrate terminal of the pad cell's poly resistor
.global sub!
Vsub sub! 0 0
.temp 27
.options savecurrents klu method=trap reltol=1e-3 abstol=1e-12 gmin=1e-12
* Without this the H-bridge cannot balance at t=0, cmfb runs to the rail and the
* pair spends ~60 ns climbing back (tb_startup measures 61.3 ns).  The driver's
* own benches place cmfb the same way and run no operating point.
.ic v(x1.xlvds.xdrv.cmfb)=1.54
.control
* save all over 700 ns at 5 ps writes a rawfile of several 100 MB; name what the
* measurements, the wrdata and the graph panels actually need.  In_p / In_n are
* the pre-driver pair inside xlvds, where a common-mode problem shows up first.
save d_p d_n vos clk_pad s14_an_2_esd dig_in_0_ i(Vpad2) x1.core_p x1.core_n
+ x1.xodt.enh x1.xodt.x i(Vvdd_3v3) i(Vvdd_1v2) i(Viovdd) x1.xlvds.In_p x1.xlvds.In_n
tran 5p 700n 0 5p
write @schname\\\\.raw

let vod = v(d_p)-v(d_n)
meas tran enh_a AVG v(x1.xodt.enh) from=150n to=295n
meas tran x_max_a MAX v(x1.xodt.x) from=150n to=295n
meas tran pad_max_a MAX v(clk_pad) from=150n to=295n
meas tran pad_min_a MIN v(clk_pad) from=150n to=295n
meas tran ck_max_a MAX v(s14_an_2_esd) from=150n to=295n
meas tran ck_min_a MIN v(s14_an_2_esd) from=150n to=295n
meas tran ipad_max_a MAX i(Vpad2) from=150n to=295n
meas tran ipad_avg_a AVG i(Vpad2) from=150n to=295n
meas tran core_pp_a PP v(x1.core_p) from=150n to=295n
meas tran vod_max_a MAX vod from=150n to=295n
meas tran vod_min_a MIN vod from=150n to=295n
meas tran vos_avg_a AVG v(vos) from=150n to=295n
meas tran vos_pp_a PP v(vos) from=150n to=295n
meas tran i_3v3_a AVG i(Vvdd_3v3) from=150n to=295n
meas tran i_1v2_a AVG i(Vvdd_1v2) from=150n to=295n
meas tran enh_b AVG v(x1.xodt.enh) from=320n to=395n
meas tran x_max_b MAX v(x1.xodt.x) from=320n to=395n
meas tran pad_max_b MAX v(clk_pad) from=320n to=395n
meas tran pad_min_b MIN v(clk_pad) from=320n to=395n
meas tran ck_max_b MAX v(s14_an_2_esd) from=320n to=395n
meas tran ck_min_b MIN v(s14_an_2_esd) from=320n to=395n
meas tran ipad_max_b MAX i(Vpad2) from=320n to=395n
meas tran ipad_avg_b AVG i(Vpad2) from=320n to=395n
meas tran core_pp_b PP v(x1.core_p) from=320n to=395n
meas tran vod_max_b MAX vod from=320n to=395n
meas tran vod_min_b MIN vod from=320n to=395n
meas tran vos_avg_b AVG v(vos) from=320n to=395n
meas tran vos_pp_b PP v(vos) from=320n to=395n
meas tran i_3v3_b AVG i(Vvdd_3v3) from=320n to=395n
meas tran i_1v2_b AVG i(Vvdd_1v2) from=320n to=395n
meas tran enh_c AVG v(x1.xodt.enh) from=500n to=695n
meas tran x_max_c MAX v(x1.xodt.x) from=500n to=695n
meas tran pad_max_c MAX v(clk_pad) from=500n to=695n
meas tran pad_min_c MIN v(clk_pad) from=500n to=695n
meas tran ck_max_c MAX v(s14_an_2_esd) from=500n to=695n
meas tran ck_min_c MIN v(s14_an_2_esd) from=500n to=695n
meas tran ipad_max_c MAX i(Vpad2) from=500n to=695n
meas tran ipad_avg_c AVG i(Vpad2) from=500n to=695n
meas tran core_pp_c PP v(x1.core_p) from=500n to=695n
meas tran vod_max_c MAX vod from=500n to=695n
meas tran vod_min_c MIN vod from=500n to=695n
meas tran vos_avg_c AVG v(vos) from=500n to=695n
meas tran vos_pp_c PP v(vos) from=500n to=695n
meas tran i_3v3_c AVG i(Vvdd_3v3) from=500n to=695n
meas tran i_1v2_c AVG i(Vvdd_1v2) from=500n to=695n
echo === phase A - ODT off, EMF 1.2 V: pad 1.2 V, no pad current (150-295 ns)
print enh_a x_max_a pad_max_a pad_min_a ck_max_a ck_min_a ipad_max_a ipad_avg_a
print core_pp_a vod_max_a vod_min_a vos_avg_a vos_pp_a i_3v3_a i_1v2_a
echo === phase B - ODT on, EMF 1.2 V: pad halved to 0.6 V if the ODT is 50 ohm (320-395 ns)
print enh_b x_max_b pad_max_b pad_min_b ck_max_b ck_min_b ipad_max_b ipad_avg_b
print core_pp_b vod_max_b vod_min_b vos_avg_b vos_pp_b i_3v3_b i_1v2_b
echo === phase C - ODT on, EMF 2.4 V: pad 1.2 V, 24 mA while high; back-termination on, ibias1 3 uA (500-695 ns)
print enh_c x_max_c pad_max_c pad_min_c ck_max_c ck_min_c ipad_max_c ipad_avg_c
print core_pp_c vod_max_c vod_min_c vos_avg_c vos_pp_c i_3v3_c i_1v2_c
let r_odt = 50 * pad_max_b / (1.2 - pad_max_b)
echo === ODT resistance from phase B, 50 * Vpad / (1.2 V - Vpad):
print r_odt

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n) v(clk_pad) v(s14_an_2_esd) i(Vpad2)
.endc
"}
