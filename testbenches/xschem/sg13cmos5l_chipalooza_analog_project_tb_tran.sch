v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Top-level transient bench.

  analog_pin[0]  250 MHz reference on the dedicated pad
  dig_in[0]      clk_src = 0, the bit clock is the reference
  dig_in[1]      en, low until 3 ns
  dig_in[2]      reset, high until 2 ns
  dig_in[3]      mode, PRBS-7 from 10 ns
  ibias[1:0]     30 uA each, vbias 1.25 V

Load is 49.9 + 49.9 ohm across analog_pin[2] / analog_pin[3] with the
Vos tap.  No pad or ESD model, so the Vos figure is not the compliance
number - the driver was characterised with one.} -1700 -2100 0 0 0.45 0.45 {}
N -1200 -1960 -1200 -1930 {lab=vdd_3v3}
C {lab_pin.sym} -1200 -1960 1 0 {name=ls_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
C {devices/vsource.sym} -1200 -1900 0 0 {name=Vvdd_3v3 value="3.3"}
N -1200 -1870 -1200 -1840 {lab=GND}
C {devices/gnd.sym} -1200 -1840 0 0 {name=lg_vdd_3v3 lab=GND}
T {gated 3.3 V} -1140 -1905 0 0 0.3 0.3 {}
N -1200 -1760 -1200 -1730 {lab=vdd_1v2}
C {lab_pin.sym} -1200 -1760 1 0 {name=ls_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
C {devices/vsource.sym} -1200 -1700 0 0 {name=Vvdd_1v2 value="1.2"}
N -1200 -1670 -1200 -1640 {lab=GND}
C {devices/gnd.sym} -1200 -1640 0 0 {name=lg_vdd_1v2 lab=GND}
T {gated 1.2 V} -1140 -1705 0 0 0.3 0.3 {}
N -1200 -1560 -1200 -1530 {lab=analog_bus[1]}
C {lab_pin.sym} -1200 -1560 1 0 {name=ls_analog_bus_1 sig_type=std_logic lab=analog_bus[1]}
C {devices/vsource.sym} -1200 -1500 0 0 {name=Vanalog_bus_1 value="1.2"}
N -1200 -1470 -1200 -1440 {lab=GND}
C {devices/gnd.sym} -1200 -1440 0 0 {name=lg_analog_bus_1 lab=GND}
T {LVDS common-mode reference, 1.2 V} -1140 -1505 0 0 0.3 0.3 {}
N -1200 -1360 -1200 -1330 {lab=analog_pin[0]}
C {lab_pin.sym} -1200 -1360 1 0 {name=ls_analog_pin_0 sig_type=std_logic lab=analog_pin[0]}
C {devices/vsource.sym} -1200 -1300 0 0 {name=Vanalog_pin_0 value="PULSE(0 1.2 0 50p 50p 1.9n 4n)"}
N -1200 -1270 -1200 -1240 {lab=GND}
C {devices/gnd.sym} -1200 -1240 0 0 {name=lg_analog_pin_0 lab=GND}
T {ref_clk, 250 MHz} -1140 -1305 0 0 0.3 0.3 {}
N -1200 -1160 -1200 -1130 {lab=dig_in[0]}
C {lab_pin.sym} -1200 -1160 1 0 {name=ls_dig_in_0 sig_type=std_logic lab=dig_in[0]}
C {devices/vsource.sym} -1200 -1100 0 0 {name=Vdig_in_0 value="0"}
N -1200 -1070 -1200 -1040 {lab=GND}
C {devices/gnd.sym} -1200 -1040 0 0 {name=lg_dig_in_0 lab=GND}
T {clk_src = 0, take ref_clk} -1140 -1105 0 0 0.3 0.3 {}
N -1200 -960 -1200 -930 {lab=dig_in[1]}
C {lab_pin.sym} -1200 -960 1 0 {name=ls_dig_in_1 sig_type=std_logic lab=dig_in[1]}
C {devices/vsource.sym} -1200 -900 0 0 {name=Vdig_in_1 value="PWL(0 0 3n 0 3.1n 1.2)"}
N -1200 -870 -1200 -840 {lab=GND}
C {devices/gnd.sym} -1200 -840 0 0 {name=lg_dig_in_1 lab=GND}
T {en, low until 3 ns} -1140 -905 0 0 0.3 0.3 {}
N -1200 -760 -1200 -730 {lab=dig_in[2]}
C {lab_pin.sym} -1200 -760 1 0 {name=ls_dig_in_2 sig_type=std_logic lab=dig_in[2]}
C {devices/vsource.sym} -1200 -700 0 0 {name=Vdig_in_2 value="PWL(0 1.2 2n 1.2 2.1n 0)"}
N -1200 -670 -1200 -640 {lab=GND}
C {devices/gnd.sym} -1200 -640 0 0 {name=lg_dig_in_2 lab=GND}
T {reset, high until 2 ns} -1140 -705 0 0 0.3 0.3 {}
N -1200 -560 -1200 -530 {lab=dig_in[3]}
C {lab_pin.sym} -1200 -560 1 0 {name=ls_dig_in_3 sig_type=std_logic lab=dig_in[3]}
C {devices/vsource.sym} -1200 -500 0 0 {name=Vdig_in_3 value="PWL(0 0 10n 0 10.1n 1.2)"}
N -1200 -470 -1200 -440 {lab=GND}
C {devices/gnd.sym} -1200 -440 0 0 {name=lg_dig_in_3 lab=GND}
T {mode -> PRBS-7 at 10 ns} -1140 -505 0 0 0.3 0.3 {}
N -1200 -360 -1200 -330 {lab=ibias[0]}
C {lab_pin.sym} -1200 -360 1 0 {name=ls_ibias_0 sig_type=std_logic lab=ibias[0]}
C {isource.sym} -1200 -300 0 0 {name=Iibias_0 value=-2u}
N -1200 -270 -1200 -240 {lab=GND}
C {devices/gnd.sym} -1200 -240 0 0 {name=lg_ibias_0 lab=GND}
T {pre-driver reference, 2 uA} -1140 -305 0 0 0.3 0.3 {}
N -1200 -160 -1200 -130 {lab=ibias[1]}
C {lab_pin.sym} -1200 -160 1 0 {name=ls_ibias_1 sig_type=std_logic lab=ibias[1]}
C {isource.sym} -1200 -100 0 0 {name=Iibias_1 value=-2u}
N -1200 -70 -1200 -40 {lab=GND}
C {devices/gnd.sym} -1200 -40 0 0 {name=lg_ibias_1 lab=GND}
T {driver reference, 2 uA} -1140 -105 0 0 0.3 0.3 {}
N -280 -350 -220 -350 {lab=vdd_3v3}
C {lab_pin.sym} -280 -350 0 0 {name=lx_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
N -280 -330 -220 -330 {lab=vdd_1v2}
C {lab_pin.sym} -280 -330 0 0 {name=lx_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
N -280 -310 -220 -310 {lab=GND}
C {devices/gnd.sym} -280 -310 1 0 {name=lgg_vss_3v3 lab=GND}
N -280 -290 -220 -290 {lab=GND}
C {devices/gnd.sym} -280 -290 1 0 {name=lgg_vss_1v2 lab=GND}
N -280 -270 -220 -270 {lab=GND}
C {devices/gnd.sym} -280 -270 1 0 {name=lgg_vssio lab=GND}
N -280 -250 -220 -250 {lab=enable}
C {lab_pin.sym} -280 -250 0 0 {name=lx_enable sig_type=std_logic lab=enable}
N -280 -230 -220 -230 {lab=clk}
C {lab_pin.sym} -280 -230 0 0 {name=lx_clk sig_type=std_logic lab=clk}
N -280 -210 -220 -210 {lab=dig_in[23]}
C {lab_pin.sym} -280 -210 0 0 {name=lx_dig_in_23 sig_type=std_logic lab=dig_in[23]}
N -280 -190 -220 -190 {lab=dig_in[22]}
C {lab_pin.sym} -280 -190 0 0 {name=lx_dig_in_22 sig_type=std_logic lab=dig_in[22]}
N -280 -170 -220 -170 {lab=dig_in[21]}
C {lab_pin.sym} -280 -170 0 0 {name=lx_dig_in_21 sig_type=std_logic lab=dig_in[21]}
N -280 -150 -220 -150 {lab=dig_in[20]}
C {lab_pin.sym} -280 -150 0 0 {name=lx_dig_in_20 sig_type=std_logic lab=dig_in[20]}
N -280 -130 -220 -130 {lab=dig_in[19]}
C {lab_pin.sym} -280 -130 0 0 {name=lx_dig_in_19 sig_type=std_logic lab=dig_in[19]}
N -280 -110 -220 -110 {lab=dig_in[18]}
C {lab_pin.sym} -280 -110 0 0 {name=lx_dig_in_18 sig_type=std_logic lab=dig_in[18]}
N -280 -90 -220 -90 {lab=dig_in[17]}
C {lab_pin.sym} -280 -90 0 0 {name=lx_dig_in_17 sig_type=std_logic lab=dig_in[17]}
N -280 -70 -220 -70 {lab=dig_in[16]}
C {lab_pin.sym} -280 -70 0 0 {name=lx_dig_in_16 sig_type=std_logic lab=dig_in[16]}
N -280 -50 -220 -50 {lab=dig_in[15]}
C {lab_pin.sym} -280 -50 0 0 {name=lx_dig_in_15 sig_type=std_logic lab=dig_in[15]}
N -280 -30 -220 -30 {lab=dig_in[14]}
C {lab_pin.sym} -280 -30 0 0 {name=lx_dig_in_14 sig_type=std_logic lab=dig_in[14]}
N -280 -10 -220 -10 {lab=dig_in[13]}
C {lab_pin.sym} -280 -10 0 0 {name=lx_dig_in_13 sig_type=std_logic lab=dig_in[13]}
N -280 10 -220 10 {lab=dig_in[12]}
C {lab_pin.sym} -280 10 0 0 {name=lx_dig_in_12 sig_type=std_logic lab=dig_in[12]}
N -280 30 -220 30 {lab=dig_in[11]}
C {lab_pin.sym} -280 30 0 0 {name=lx_dig_in_11 sig_type=std_logic lab=dig_in[11]}
N -280 50 -220 50 {lab=dig_in[10]}
C {lab_pin.sym} -280 50 0 0 {name=lx_dig_in_10 sig_type=std_logic lab=dig_in[10]}
N -280 70 -220 70 {lab=dig_in[9]}
C {lab_pin.sym} -280 70 0 0 {name=lx_dig_in_9 sig_type=std_logic lab=dig_in[9]}
N -280 90 -220 90 {lab=dig_in[8]}
C {lab_pin.sym} -280 90 0 0 {name=lx_dig_in_8 sig_type=std_logic lab=dig_in[8]}
N -280 110 -220 110 {lab=dig_in[7]}
C {lab_pin.sym} -280 110 0 0 {name=lx_dig_in_7 sig_type=std_logic lab=dig_in[7]}
N -280 130 -220 130 {lab=dig_in[6]}
C {lab_pin.sym} -280 130 0 0 {name=lx_dig_in_6 sig_type=std_logic lab=dig_in[6]}
N -280 150 -220 150 {lab=dig_in[5]}
C {lab_pin.sym} -280 150 0 0 {name=lx_dig_in_5 sig_type=std_logic lab=dig_in[5]}
N -280 170 -220 170 {lab=dig_in[4]}
C {lab_pin.sym} -280 170 0 0 {name=lx_dig_in_4 sig_type=std_logic lab=dig_in[4]}
N -280 190 -220 190 {lab=dig_in[3]}
C {lab_pin.sym} -280 190 0 0 {name=lx_dig_in_3 sig_type=std_logic lab=dig_in[3]}
N -280 210 -220 210 {lab=dig_in[2]}
C {lab_pin.sym} -280 210 0 0 {name=lx_dig_in_2 sig_type=std_logic lab=dig_in[2]}
N -280 230 -220 230 {lab=dig_in[1]}
C {lab_pin.sym} -280 230 0 0 {name=lx_dig_in_1 sig_type=std_logic lab=dig_in[1]}
N -280 250 -220 250 {lab=dig_in[0]}
C {lab_pin.sym} -280 250 0 0 {name=lx_dig_in_0 sig_type=std_logic lab=dig_in[0]}
N -280 270 -220 270 {lab=ibias[1]}
C {lab_pin.sym} -280 270 0 0 {name=lx_ibias_1 sig_type=std_logic lab=ibias[1]}
N -280 290 -220 290 {lab=ibias[0]}
C {lab_pin.sym} -280 290 0 0 {name=lx_ibias_0 sig_type=std_logic lab=ibias[0]}
N -280 310 -220 310 {lab=vbias}
C {lab_pin.sym} -280 310 0 0 {name=lx_vbias sig_type=std_logic lab=vbias}
N 220 -350 280 -350 {lab=dig_out[11]}
C {lab_pin.sym} 280 -350 0 1 {name=lx_dig_out_11 sig_type=std_logic lab=dig_out[11]}
N 220 -330 280 -330 {lab=dig_out[10]}
C {lab_pin.sym} 280 -330 0 1 {name=lx_dig_out_10 sig_type=std_logic lab=dig_out[10]}
N 220 -310 280 -310 {lab=dig_out[9]}
C {lab_pin.sym} 280 -310 0 1 {name=lx_dig_out_9 sig_type=std_logic lab=dig_out[9]}
N 220 -290 280 -290 {lab=dig_out[8]}
C {lab_pin.sym} 280 -290 0 1 {name=lx_dig_out_8 sig_type=std_logic lab=dig_out[8]}
N 220 -270 280 -270 {lab=dig_out[7]}
C {lab_pin.sym} 280 -270 0 1 {name=lx_dig_out_7 sig_type=std_logic lab=dig_out[7]}
N 220 -250 280 -250 {lab=dig_out[6]}
C {lab_pin.sym} 280 -250 0 1 {name=lx_dig_out_6 sig_type=std_logic lab=dig_out[6]}
N 220 -230 280 -230 {lab=dig_out[5]}
C {lab_pin.sym} 280 -230 0 1 {name=lx_dig_out_5 sig_type=std_logic lab=dig_out[5]}
N 220 -210 280 -210 {lab=dig_out[4]}
C {lab_pin.sym} 280 -210 0 1 {name=lx_dig_out_4 sig_type=std_logic lab=dig_out[4]}
N 220 -190 280 -190 {lab=dig_out[3]}
C {lab_pin.sym} 280 -190 0 1 {name=lx_dig_out_3 sig_type=std_logic lab=dig_out[3]}
N 220 -170 280 -170 {lab=dig_out[2]}
C {lab_pin.sym} 280 -170 0 1 {name=lx_dig_out_2 sig_type=std_logic lab=dig_out[2]}
N 220 -150 280 -150 {lab=dig_out[1]}
C {lab_pin.sym} 280 -150 0 1 {name=lx_dig_out_1 sig_type=std_logic lab=dig_out[1]}
N 220 -130 280 -130 {lab=dig_out[0]}
C {lab_pin.sym} 280 -130 0 1 {name=lx_dig_out_0 sig_type=std_logic lab=dig_out[0]}
N 220 -110 280 -110 {lab=analog_pin[3]}
C {lab_pin.sym} 280 -110 0 1 {name=lx_analog_pin_3 sig_type=std_logic lab=analog_pin[3]}
N 220 -90 280 -90 {lab=analog_pin[2]}
C {lab_pin.sym} 280 -90 0 1 {name=lx_analog_pin_2 sig_type=std_logic lab=analog_pin[2]}
N 220 -70 280 -70 {lab=analog_pin[1]}
C {lab_pin.sym} 280 -70 0 1 {name=lx_analog_pin_1 sig_type=std_logic lab=analog_pin[1]}
N 220 -50 280 -50 {lab=analog_pin[0]}
C {lab_pin.sym} 280 -50 0 1 {name=lx_analog_pin_0 sig_type=std_logic lab=analog_pin[0]}
N 220 -30 280 -30 {lab=analog_bus[3]}
C {lab_pin.sym} 280 -30 0 1 {name=lx_analog_bus_3 sig_type=std_logic lab=analog_bus[3]}
N 220 -10 280 -10 {lab=analog_bus[2]}
C {lab_pin.sym} 280 -10 0 1 {name=lx_analog_bus_2 sig_type=std_logic lab=analog_bus[2]}
N 220 10 280 10 {lab=analog_bus[1]}
C {lab_pin.sym} 280 10 0 1 {name=lx_analog_bus_1 sig_type=std_logic lab=analog_bus[1]}
N 220 30 280 30 {lab=analog_bus[0]}
C {lab_pin.sym} 280 30 0 1 {name=lx_analog_bus_0 sig_type=std_logic lab=analog_bus[0]}
C {sg13cmos5l_chipalooza_analog_project.sym} 0 0 0 0 {name=x1}
N 700 -960 700 -930 {lab=analog_pin[3]}
C {lab_pin.sym} 700 -960 1 0 {name=lpad_d_n sig_type=std_logic lab=analog_pin[3]}
C {devices/vsource.sym} 700 -900 0 0 {name=Vd_n value=0}
N 700 -870 700 -840 {lab=d_n}
C {lab_pin.sym} 700 -840 3 0 {name=lmeas_d_n sig_type=std_logic lab=d_n}
N 900 -960 900 -930 {lab=analog_pin[2]}
C {lab_pin.sym} 900 -960 1 0 {name=lpad_d_p sig_type=std_logic lab=analog_pin[2]}
C {devices/vsource.sym} 900 -900 0 0 {name=Vd_p value=0}
N 900 -870 900 -840 {lab=d_p}
C {lab_pin.sym} 900 -840 3 0 {name=lmeas_d_p sig_type=std_logic lab=d_p}
N 800 -840 800 -810 {lab=d_n}
C {lab_pin.sym} 800 -840 1 0 {name=lt1 sig_type=std_logic lab=d_n}
C {res.sym} 800 -810 0 0 {name=Rtp value=49.9}
N 800 -780 800 -750 {lab=vos}
N 800 -780 880 -780 {lab=vos}
C {lab_pin.sym} 880 -780 0 1 {name=lvos sig_type=std_logic lab=vos}
C {res.sym} 800 -720 0 0 {name=Rtn value=49.9}
N 800 -690 800 -660 {lab=d_p}
C {lab_pin.sym} 800 -660 3 0 {name=lt2 sig_type=std_logic lab=d_p}
C {devices/code_shown.sym} -2400 -2100 0 0 {name=NGSPICE
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
.control
save all
op
remzerovec
write @schname\\\\.raw
set appendwrite
tran 5p 40n
write @schname\\\\.raw

let vod = v(d_p)-v(d_n)
meas tran vod_max MAX vod from=20n to=40n
meas tran vod_min MIN vod from=20n to=40n
meas tran vos_avg AVG v(vos) from=20n to=40n
meas tran vos_max MAX v(vos) from=20n to=40n
meas tran vos_min MIN v(vos) from=20n to=40n
let vos_pp = vos_max - vos_min
print vod_max vod_min vos_avg vos_pp

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n)
.endc
"}
