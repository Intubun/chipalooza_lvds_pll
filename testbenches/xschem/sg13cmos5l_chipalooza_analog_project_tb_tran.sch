v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Top-level transient bench on the real project interface.

  ref_clk       250 MHz on the dedicated pad
  dig_in[4]     1 GHz, standing in for the PLL
  dig_in[0]     clk_src = 1, take the fast clock
  dig_in[1]     en, low until 3 ns
  dig_in[2]     reset, high until 2 ns
  dig_in[3]     mode, PRBS-7 from 10 ns
  ibias[1:0]    30 uA each, straight from the harness
  vbias         1.25 V

Load is 49.9 + 49.9 ohm across d_p / d_n with the Vos tap.} -900 -1700 0 0 0.45 0.45 {}
N -600 -1560 -600 -1530 {lab=vdd_3v3}
C {lab_pin.sym} -600 -1560 1 0 {name=lv_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
C {devices/vsource.sym} -600 -1500 0 0 {name=Vvdd_3v3 value="3.3"}
N -600 -1470 -600 -1440 {lab=GND}
C {devices/gnd.sym} -600 -1440 0 0 {name=lg_vdd_3v3 lab=GND}
N -600 -1360 -600 -1330 {lab=vdd_1v2}
C {lab_pin.sym} -600 -1360 1 0 {name=lv_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
C {devices/vsource.sym} -600 -1300 0 0 {name=Vvdd_1v2 value="1.2"}
N -600 -1270 -600 -1240 {lab=GND}
C {devices/gnd.sym} -600 -1240 0 0 {name=lg_vdd_1v2 lab=GND}
N -600 -1160 -600 -1130 {lab=vbias}
C {lab_pin.sym} -600 -1160 1 0 {name=lv_vbias sig_type=std_logic lab=vbias}
C {devices/vsource.sym} -600 -1100 0 0 {name=Vvbias value="1.25"}
N -600 -1070 -600 -1040 {lab=GND}
C {devices/gnd.sym} -600 -1040 0 0 {name=lg_vbias lab=GND}
N -600 -960 -600 -930 {lab=ref_clk}
C {lab_pin.sym} -600 -960 1 0 {name=lv_ref_clk sig_type=std_logic lab=ref_clk}
C {devices/vsource.sym} -600 -900 0 0 {name=Vref_clk value="PULSE(0 1.2 0 50p 50p 1.9n 4n)"}
N -600 -870 -600 -840 {lab=GND}
C {devices/gnd.sym} -600 -840 0 0 {name=lg_ref_clk lab=GND}
N -600 -760 -600 -730 {lab=dig_in[4]}
C {lab_pin.sym} -600 -760 1 0 {name=lv_dig_in4 sig_type=std_logic lab=dig_in[4]}
C {devices/vsource.sym} -600 -700 0 0 {name=Vdig_in4 value="PULSE(0 1.2 0 30p 30p 470p 1n)"}
N -600 -670 -600 -640 {lab=GND}
C {devices/gnd.sym} -600 -640 0 0 {name=lg_dig_in4 lab=GND}
N -600 -560 -600 -530 {lab=dig_in[0]}
C {lab_pin.sym} -600 -560 1 0 {name=lv_dig_in0 sig_type=std_logic lab=dig_in[0]}
C {devices/vsource.sym} -600 -500 0 0 {name=Vdig_in0 value="1.2"}
N -600 -470 -600 -440 {lab=GND}
C {devices/gnd.sym} -600 -440 0 0 {name=lg_dig_in0 lab=GND}
N -600 -360 -600 -330 {lab=enable}
C {lab_pin.sym} -600 -360 1 0 {name=lv_enable sig_type=std_logic lab=enable}
C {devices/vsource.sym} -600 -300 0 0 {name=Venable value="1.2"}
N -600 -270 -600 -240 {lab=GND}
C {devices/gnd.sym} -600 -240 0 0 {name=lg_enable lab=GND}
N -600 -160 -600 -130 {lab=dig_in[1]}
C {lab_pin.sym} -600 -160 1 0 {name=lv_dig_in1 sig_type=std_logic lab=dig_in[1]}
C {devices/vsource.sym} -600 -100 0 0 {name=Vdig_in1 value="PWL(0 0 3n 0 3.1n 1.2)"}
N -600 -70 -600 -40 {lab=GND}
C {devices/gnd.sym} -600 -40 0 0 {name=lg_dig_in1 lab=GND}
N -600 40 -600 70 {lab=dig_in[2]}
C {lab_pin.sym} -600 40 1 0 {name=lv_dig_in2 sig_type=std_logic lab=dig_in[2]}
C {devices/vsource.sym} -600 100 0 0 {name=Vdig_in2 value="PWL(0 1.2 2n 1.2 2.1n 0)"}
N -600 130 -600 160 {lab=GND}
C {devices/gnd.sym} -600 160 0 0 {name=lg_dig_in2 lab=GND}
N -600 240 -600 270 {lab=dig_in[3]}
C {lab_pin.sym} -600 240 1 0 {name=lv_dig_in3 sig_type=std_logic lab=dig_in[3]}
C {devices/vsource.sym} -600 300 0 0 {name=Vdig_in3 value="PWL(0 0 10n 0 10.1n 1.2)"}
N -600 330 -600 360 {lab=GND}
C {devices/gnd.sym} -600 360 0 0 {name=lg_dig_in3 lab=GND}
N -600 440 -600 470 {lab=ibias[0]}
C {lab_pin.sym} -600 440 1 0 {name=lv_ibias0 sig_type=std_logic lab=ibias[0]}
C {isource.sym} -600 500 0 0 {name=Iibias0 value=-30u}
N -600 530 -600 560 {lab=GND}
C {devices/gnd.sym} -600 560 0 0 {name=lg_ibias0 lab=GND}
N -600 640 -600 670 {lab=ibias[1]}
C {lab_pin.sym} -600 640 1 0 {name=lv_ibias1 sig_type=std_logic lab=ibias[1]}
C {isource.sym} -600 700 0 0 {name=Iibias1 value=-30u}
N -600 730 -600 760 {lab=GND}
C {devices/gnd.sym} -600 760 0 0 {name=lg_ibias1 lab=GND}
N 140 -230 200 -230 {lab=ref_clk}
C {lab_pin.sym} 140 -230 0 0 {name=lx_ref_clk sig_type=std_logic lab=ref_clk}
N 140 -210 200 -210 {lab=enable}
C {lab_pin.sym} 140 -210 0 0 {name=lx_enable sig_type=std_logic lab=enable}
N 140 -190 200 -190 {lab=clk}
C {lab_pin.sym} 140 -190 0 0 {name=lx_clk sig_type=std_logic lab=clk}
N 140 -170 200 -170 {lab=dig_in[23:0]}
C {lab_pin.sym} 140 -170 0 0 {name=lx_dig_in23_0 sig_type=std_logic lab=dig_in[23:0]}
N 140 -150 200 -150 {lab=ibias[1:0]}
C {lab_pin.sym} 140 -150 0 0 {name=lx_ibias1_0 sig_type=std_logic lab=ibias[1:0]}
N 140 -130 200 -130 {lab=vbias}
C {lab_pin.sym} 140 -130 0 0 {name=lx_vbias sig_type=std_logic lab=vbias}
N 140 -110 200 -110 {lab=vdd_3v3}
C {lab_pin.sym} 140 -110 0 0 {name=lx_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
N 140 -90 200 -90 {lab=vdd_1v2}
C {lab_pin.sym} 140 -90 0 0 {name=lx_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
N 140 -70 200 -70 {lab=GND}
C {devices/gnd.sym} 140 -70 1 0 {name=lgg_vss_3v3 lab=GND}
N 140 -50 200 -50 {lab=GND}
C {devices/gnd.sym} 140 -50 1 0 {name=lgg_vss_1v2 lab=GND}
N 140 -30 200 -30 {lab=GND}
C {devices/gnd.sym} 140 -30 1 0 {name=lgg_vssio lab=GND}
N 600 -230 660 -230 {lab=pll_out}
C {lab_pin.sym} 660 -230 0 1 {name=lx_pll_out sig_type=std_logic lab=pll_out}
N 600 -210 660 -210 {lab=d_p}
C {lab_pin.sym} 660 -210 0 1 {name=lx_d_p sig_type=std_logic lab=d_p}
N 600 -190 660 -190 {lab=d_n}
C {lab_pin.sym} 660 -190 0 1 {name=lx_d_n sig_type=std_logic lab=d_n}
N 600 -170 660 -170 {lab=dig_out[11:0]}
C {lab_pin.sym} 660 -170 0 1 {name=lx_dig_out11_0 sig_type=std_logic lab=dig_out[11:0]}
N 600 -150 660 -150 {lab=analog_bus[3:0]}
C {lab_pin.sym} 660 -150 0 1 {name=lx_analog_bus3_0 sig_type=std_logic lab=analog_bus[3:0]}
C {sg13cmos5l_chipalooza_analog_project.sym} 400 0 0 0 {name=x1}
N 1200 -840 1200 -810 {lab=d_n}
C {lab_pin.sym} 1200 -840 1 0 {name=lt1 sig_type=std_logic lab=d_n}
C {res.sym} 1200 -810 0 0 {name=Rtp value=49.9 m=1}
N 1200 -780 1200 -750 {lab=vos}
N 1200 -780 1280 -780 {lab=vos}
C {lab_pin.sym} 1280 -780 0 1 {name=lvos sig_type=std_logic lab=vos}
C {res.sym} 1200 -720 0 0 {name=Rtn value=49.9 m=1}
N 1200 -690 1200 -660 {lab=d_p}
C {lab_pin.sym} 1200 -660 3 0 {name=lt2 sig_type=std_logic lab=d_p}
C {devices/code_shown.sym} -1500 -1500 0 0 {name=NGSPICE
only_toplevel=true
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_mfringe.lib
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.temp 27
.options savecurrents klu method=gear reltol=1e-3 abstol=1e-12 gmin=1e-12
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
print i(Vvdd_3v3) i(Vvdd_1v2)

unset appendwrite
set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(d_p) v(d_n) v(vos) vod v(x1.core_p) v(x1.core_n)
.endc
"}
