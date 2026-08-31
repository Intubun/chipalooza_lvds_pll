v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Chipalooza 2026 - LVDS transmitter with PRBS-7 generator} 700 -1500 0 0 1 1 {}
T {Port list is verilog/rtl/user_project_wrapper_4a.v from
RTimothyEdwards/sg13cmos5l_ocd_chipalooza.  Four dedicated analog
pads means slot s1 or s16 - the only two that have four.

  analog_pin[0]  ref_clk   PLL reference in
  analog_pin[1]  pll_out   PLL clock out, RESERVED - nothing drives it
                           until the PLL is placed
  analog_pin[2]  d_p       LVDS out +
  analog_pin[3]  d_n       LVDS out -

All four are sg13cmos5l_IOPadAnalog in config.txt, so the core signal
name is the pad name and there is one signal per pad.  Changing a pad
type changes the core-facing signals - an InOut pad becomes five.} 60 -1420 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit
individually to a pin, a constant or the sequencer, so a
configuration bit costs a register write and no pin.

  dig_in[0]   clk_src   0 = ref_clk, 1 = pll_clk
  dig_in[1]   en        gated with the project enable
  dig_in[2]   reset     active high, seeds the PRBS
  dig_in[3]   mode      0 = clock passthrough, 1 = PRBS-7
  dig_in[4]   PROVISIONAL pll_clk, until the PLL is placed
  dig_in[23:5] unused, read as zero, and zero works

dig_out[11:0], analog_bus[3:0] and vssio are not connected
yet.  clk, the shared external clock, is unused: the
reference comes in on its own dedicated pad.} 60 -1000 0 0 0.4 0.4 {}
T {Two supply domains with separate grounds.  The core pair
core_p / core_n crosses from vss_1v2 to vss_3v3 - the two
have to be tied together in the frame, check before tapeout.} 1450 -760 0 0 0.35 0.35 {}
N 1030 -580 1070 -580 {lab=core_n}
C {lab_pin.sym} 1070 -580 0 1 {name=l_xpat_d_n sig_type=std_logic lab=core_n}
N 1030 -600 1070 -600 {lab=core_p}
C {lab_pin.sym} 1070 -600 0 1 {name=l_xpat_d_p sig_type=std_logic lab=core_p}
N 1030 -420 1070 -420 {lab=vdd_1v2}
C {lab_pin.sym} 1070 -420 0 1 {name=l_xpat_vdd sig_type=std_logic lab=vdd_1v2}
N 1030 -400 1070 -400 {lab=vss_1v2}
C {lab_pin.sym} 1070 -400 0 1 {name=l_xpat_vss sig_type=std_logic lab=vss_1v2}
N 730 -560 770 -560 {lab=dig_in[0]}
C {lab_pin.sym} 730 -560 0 0 {name=l_xpat_clk_src sig_type=std_logic lab=dig_in[0]}
N 730 -540 770 -540 {lab=en_gated}
C {lab_pin.sym} 730 -540 0 0 {name=l_xpat_en sig_type=std_logic lab=en_gated}
N 730 -500 770 -500 {lab=dig_in[3]}
C {lab_pin.sym} 730 -500 0 0 {name=l_xpat_mode sig_type=std_logic lab=dig_in[3]}
N 730 -580 770 -580 {lab=dig_in[4]}
C {lab_pin.sym} 730 -580 0 0 {name=l_xpat_pll_clk sig_type=std_logic lab=dig_in[4]}
N 730 -600 770 -600 {lab=ref_clk}
C {lab_pin.sym} 730 -600 0 0 {name=l_xpat_ref_clk sig_type=std_logic lab=ref_clk}
N 730 -520 770 -520 {lab=dig_in[2]}
C {lab_pin.sym} 730 -520 0 0 {name=l_xpat_reset sig_type=std_logic lab=dig_in[2]}
C {lvds_pattern.sym} 900 -500 0 0 {name=xpat}
N 1510 -530 1550 -530 {lab=core_n}
C {lab_pin.sym} 1510 -530 0 0 {name=l_xlvds_d_n sig_type=std_logic lab=core_n}
N 1510 -550 1550 -550 {lab=core_p}
C {lab_pin.sym} 1510 -550 0 0 {name=l_xlvds_d_p sig_type=std_logic lab=core_p}
N 1510 -490 1550 -490 {lab=ibias[1]}
C {lab_pin.sym} 1510 -490 0 0 {name=l_xlvds_iref_drv sig_type=std_logic lab=ibias[1]}
N 1510 -510 1550 -510 {lab=ibias[0]}
C {lab_pin.sym} 1510 -510 0 0 {name=l_xlvds_iref_pd sig_type=std_logic lab=ibias[0]}
N 1850 -510 1890 -510 {lab=d_n}
C {lab_pin.sym} 1890 -510 0 1 {name=l_xlvds_out_n sig_type=std_logic lab=d_n}
N 1850 -530 1890 -530 {lab=d_p}
C {lab_pin.sym} 1890 -530 0 1 {name=l_xlvds_out_p sig_type=std_logic lab=d_p}
N 1850 -550 1890 -550 {lab=vdd_3v3}
C {lab_pin.sym} 1890 -550 0 1 {name=l_xlvds_va sig_type=std_logic lab=vdd_3v3}
N 1510 -470 1550 -470 {lab=vbias}
C {lab_pin.sym} 1510 -470 0 0 {name=l_xlvds_vref sig_type=std_logic lab=vbias}
N 1850 -490 1890 -490 {lab=vss_3v3}
C {lab_pin.sym} 1890 -490 0 1 {name=l_xlvds_vss sig_type=std_logic lab=vss_3v3}
C {lvds_tx.sym} 1700 -500 0 0 {name=xlvds}
N 400 -320 440 -320 {lab=enable}
C {lab_pin.sym} 400 -320 0 0 {name=l_xeng_a sig_type=std_logic lab=enable}
N 400 -280 440 -280 {lab=dig_in[1]}
C {lab_pin.sym} 400 -280 0 0 {name=l_xeng_b sig_type=std_logic lab=dig_in[1]}
N 560 -300 600 -300 {lab=en_gated}
C {lab_pin.sym} 600 -300 0 1 {name=l_xeng_x sig_type=std_logic lab=en_gated}
C {sg13cmos5l_stdcells/sg13cmos5l_and2_1.sym} 500 -300 0 0 {name=xeng
VDD=vdd_1v2 VSS=vss_1v2}
N 2420 -800 2460 -800 {lab=vss_1v2}
C {lab_pin.sym} 2460 -800 0 1 {name=l_Cd12_b sig_type=std_logic lab=vss_1v2}
N 2420 -770 2460 -770 {lab=vss_1v2}
C {lab_pin.sym} 2460 -770 0 1 {name=l_Cd12_d sig_type=std_logic lab=vss_1v2}
N 2340 -800 2380 -800 {lab=vdd_1v2}
C {lab_pin.sym} 2340 -800 0 0 {name=l_Cd12_g sig_type=std_logic lab=vdd_1v2}
N 2420 -830 2460 -830 {lab=vss_1v2}
C {lab_pin.sym} 2460 -830 0 1 {name=l_Cd12_s sig_type=std_logic lab=vss_1v2}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 2400 -800 0 0 {name=Cd12
l=10.0u w=10.0u ng=1 m=1 mm_ok=1 model=sg13_lv_pmos spiceprefix=X}
N 2420 -500 2460 -500 {lab=vss_3v3}
C {lab_pin.sym} 2460 -500 0 1 {name=l_Cd33_b sig_type=std_logic lab=vss_3v3}
N 2420 -470 2460 -470 {lab=vss_3v3}
C {lab_pin.sym} 2460 -470 0 1 {name=l_Cd33_d sig_type=std_logic lab=vss_3v3}
N 2340 -500 2380 -500 {lab=vdd_3v3}
C {lab_pin.sym} 2340 -500 0 0 {name=l_Cd33_g sig_type=std_logic lab=vdd_3v3}
N 2420 -530 2460 -530 {lab=vss_3v3}
C {lab_pin.sym} 2460 -530 0 1 {name=l_Cd33_s sig_type=std_logic lab=vss_3v3}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 2400 -500 0 0 {name=Cd33
l=10.0u w=10.0u ng=1 m=1 mm_ok=1 model=sg13_hv_pmos spiceprefix=X}
N 0 -1300 40 -1300 {lab=ref_clk}
C {devices/ipin.sym} 0 -1300 2 1 {name=p_ref_clk lab=ref_clk}
C {lab_pin.sym} 40 -1300 0 1 {name=lp_ref_clk sig_type=std_logic lab=ref_clk}
T {analog_pin[0] - PLL reference in} 90 -1308 0 0 0.25 0.25 {}
N 0 -1260 40 -1260 {lab=pll_out}
C {devices/opin.sym} 0 -1260 2 0 {name=p_pll_out lab=pll_out}
C {lab_pin.sym} 40 -1260 0 1 {name=lp_pll_out sig_type=std_logic lab=pll_out}
T {analog_pin[1] - PLL clock out, reserved} 90 -1268 0 0 0.25 0.25 {}
N 0 -1220 40 -1220 {lab=d_p}
C {devices/opin.sym} 0 -1220 2 0 {name=p_d_p lab=d_p}
C {lab_pin.sym} 40 -1220 0 1 {name=lp_d_p sig_type=std_logic lab=d_p}
T {analog_pin[2] - LVDS out +} 90 -1228 0 0 0.25 0.25 {}
N 0 -1180 40 -1180 {lab=d_n}
C {devices/opin.sym} 0 -1180 2 0 {name=p_d_n lab=d_n}
C {lab_pin.sym} 40 -1180 0 1 {name=lp_d_n sig_type=std_logic lab=d_n}
T {analog_pin[3] - LVDS out -} 90 -1188 0 0 0.25 0.25 {}
N 0 -1140 40 -1140 {lab=enable}
C {devices/ipin.sym} 0 -1140 2 1 {name=p_enable lab=enable}
C {lab_pin.sym} 40 -1140 0 1 {name=lp_enable sig_type=std_logic lab=enable}
T {project enable} 90 -1148 0 0 0.25 0.25 {}
N 0 -1100 40 -1100 {lab=clk}
C {devices/ipin.sym} 0 -1100 2 1 {name=p_clk lab=clk}
C {lab_pin.sym} 40 -1100 0 1 {name=lp_clk sig_type=std_logic lab=clk}
T {shared external clock} 90 -1108 0 0 0.25 0.25 {}
N 0 -1060 40 -1060 {lab=dig_in[23:0]}
C {devices/ipin.sym} 0 -1060 2 1 {name=p_dig_in23_0 lab=dig_in[23:0]}
C {lab_pin.sym} 40 -1060 0 1 {name=lp_dig_in23_0 sig_type=std_logic lab=dig_in[23:0]}
T {24 shared digital inputs} 90 -1068 0 0 0.25 0.25 {}
N 0 -1020 40 -1020 {lab=dig_out[11:0]}
C {devices/opin.sym} 0 -1020 2 0 {name=p_dig_out11_0 lab=dig_out[11:0]}
C {lab_pin.sym} 40 -1020 0 1 {name=lp_dig_out11_0 sig_type=std_logic lab=dig_out[11:0]}
T {12 shared digital outputs} 90 -1028 0 0 0.25 0.25 {}
N 0 -980 40 -980 {lab=ibias[1:0]}
C {devices/iopin.sym} 0 -980 2 0 {name=p_ibias1_0 lab=ibias[1:0]}
C {lab_pin.sym} 40 -980 0 1 {name=lp_ibias1_0 sig_type=std_logic lab=ibias[1:0]}
T {shared current biases} 90 -988 0 0 0.25 0.25 {}
N 0 -940 40 -940 {lab=vbias}
C {devices/iopin.sym} 0 -940 2 0 {name=p_vbias lab=vbias}
C {lab_pin.sym} 40 -940 0 1 {name=lp_vbias sig_type=std_logic lab=vbias}
T {shared voltage bias} 90 -948 0 0 0.25 0.25 {}
N 0 -900 40 -900 {lab=analog_bus[3:0]}
C {devices/iopin.sym} 0 -900 2 0 {name=p_analog_bus3_0 lab=analog_bus[3:0]}
C {lab_pin.sym} 40 -900 0 1 {name=lp_analog_bus3_0 sig_type=std_logic lab=analog_bus[3:0]}
T {shared analog buses} 90 -908 0 0 0.25 0.25 {}
N 0 -860 40 -860 {lab=vdd_3v3}
C {devices/iopin.sym} 0 -860 2 0 {name=p_vdd_3v3 lab=vdd_3v3}
C {lab_pin.sym} 40 -860 0 1 {name=lp_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
T {gated 3.3 V} 90 -868 0 0 0.25 0.25 {}
N 0 -820 40 -820 {lab=vdd_1v2}
C {devices/iopin.sym} 0 -820 2 0 {name=p_vdd_1v2 lab=vdd_1v2}
C {lab_pin.sym} 40 -820 0 1 {name=lp_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
T {gated 1.2 V} 90 -828 0 0 0.25 0.25 {}
N 0 -780 40 -780 {lab=vss_3v3}
C {devices/iopin.sym} 0 -780 2 0 {name=p_vss_3v3 lab=vss_3v3}
C {lab_pin.sym} 40 -780 0 1 {name=lp_vss_3v3 sig_type=std_logic lab=vss_3v3}
N 0 -740 40 -740 {lab=vss_1v2}
C {devices/iopin.sym} 0 -740 2 0 {name=p_vss_1v2 lab=vss_1v2}
C {lab_pin.sym} 40 -740 0 1 {name=lp_vss_1v2 sig_type=std_logic lab=vss_1v2}
N 0 -700 40 -700 {lab=vssio}
C {devices/iopin.sym} 0 -700 2 0 {name=p_vssio lab=vssio}
C {lab_pin.sym} 40 -700 0 1 {name=lp_vssio sig_type=std_logic lab=vssio}
T {substrate ground} 90 -708 0 0 0.25 0.25 {}
