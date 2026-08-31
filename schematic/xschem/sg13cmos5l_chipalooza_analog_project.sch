v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Chipalooza 2026 - LVDS transmitter with PRBS-7 generator} 800 -1900 0 0 1 1 {}
T {Port list is verilog/rtl/user_project_wrapper_4a.v from
RTimothyEdwards/sg13cmos5l_ocd_chipalooza, every bus expanded into
individual pins.  Four dedicated analog pads means slot s1 or s16 -
per config.txt the only two that have four.

  analog_pin[0]  ref_clk   PLL reference in
  analog_pin[1]  pll_out   RESERVED, nothing drives it until the PLL is placed
  analog_pin[2]  d_p       LVDS out +
  analog_pin[3]  d_n       LVDS out -

All four are sg13cmos5l_IOPadAnalog in config.txt, so each pad is one core
signal carrying the pad name.  A different pad type changes that: an InOut
pad becomes five core signals (_in, _out, _ena, _one, _zero).

Not connected yet: dig_out[11:0], analog_bus[3:0], vssio, and clk - the
reference arrives on its own dedicated pad instead of the shared clock pin.} 300 -1820 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit individually to a
pin, a constant or the sequencer, so a configuration bit costs a register
write and no pin.  Unselected holds every dig_in at zero, and all-zero
leaves the clock stopped and the output pair static - a legal idle.

  dig_in[0]    clk_src   0 = ref_clk, 1 = pll_clk
  dig_in[1]    en        ANDed with the project enable
  dig_in[2]    reset     active high, seeds the PRBS
  dig_in[3]    mode      0 = clock passthrough, 1 = PRBS-7
  dig_in[4]    PROVISIONAL pll_clk, until the PLL is placed
  dig_in[23:5] unused} 300 -1400 0 0 0.4 0.4 {}
T {Two supply domains with separate grounds.  core_p / core_n cross from
vss_1v2 into the pre-driver on vss_3v3 - the two grounds have to be tied
together in the frame, check that before tapeout.

No ESD structure on the output pads, and analog_pin[0] runs straight into
a standard-cell input with no receiver.  Both need fixing before tapeout.} 1450 -760 0 0 0.35 0.35 {}
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
N 730 -600 770 -600 {lab=analog_pin[0]}
C {lab_pin.sym} 730 -600 0 0 {name=l_xpat_ref_clk sig_type=std_logic lab=analog_pin[0]}
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
N 1850 -510 1890 -510 {lab=analog_pin[3]}
C {lab_pin.sym} 1890 -510 0 1 {name=l_xlvds_out_n sig_type=std_logic lab=analog_pin[3]}
N 1850 -530 1890 -530 {lab=analog_pin[2]}
C {lab_pin.sym} 1890 -530 0 1 {name=l_xlvds_out_p sig_type=std_logic lab=analog_pin[2]}
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
N 0 -1300 40 -1300 {lab=vdd_3v3}
C {devices/iopin.sym} 0 -1300 2 0 {name=p_vdd_3v3 lab=vdd_3v3}
C {lab_pin.sym} 40 -1300 0 1 {name=lp_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
N 0 -1280 40 -1280 {lab=vdd_1v2}
C {devices/iopin.sym} 0 -1280 2 0 {name=p_vdd_1v2 lab=vdd_1v2}
C {lab_pin.sym} 40 -1280 0 1 {name=lp_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
N 0 -1260 40 -1260 {lab=vss_3v3}
C {devices/iopin.sym} 0 -1260 2 0 {name=p_vss_3v3 lab=vss_3v3}
C {lab_pin.sym} 40 -1260 0 1 {name=lp_vss_3v3 sig_type=std_logic lab=vss_3v3}
N 0 -1240 40 -1240 {lab=vss_1v2}
C {devices/iopin.sym} 0 -1240 2 0 {name=p_vss_1v2 lab=vss_1v2}
C {lab_pin.sym} 40 -1240 0 1 {name=lp_vss_1v2 sig_type=std_logic lab=vss_1v2}
N 0 -1220 40 -1220 {lab=vssio}
C {devices/iopin.sym} 0 -1220 2 0 {name=p_vssio lab=vssio}
C {lab_pin.sym} 40 -1220 0 1 {name=lp_vssio sig_type=std_logic lab=vssio}
N 0 -1200 40 -1200 {lab=enable}
C {devices/ipin.sym} 0 -1200 2 1 {name=p_enable lab=enable}
C {lab_pin.sym} 40 -1200 0 1 {name=lp_enable sig_type=std_logic lab=enable}
N 0 -1180 40 -1180 {lab=clk}
C {devices/ipin.sym} 0 -1180 2 1 {name=p_clk lab=clk}
C {lab_pin.sym} 40 -1180 0 1 {name=lp_clk sig_type=std_logic lab=clk}
N 0 -1160 40 -1160 {lab=dig_in[23]}
C {devices/ipin.sym} 0 -1160 2 1 {name=p_dig_in_23 lab=dig_in[23]}
C {lab_pin.sym} 40 -1160 0 1 {name=lp_dig_in_23 sig_type=std_logic lab=dig_in[23]}
N 0 -1140 40 -1140 {lab=dig_in[22]}
C {devices/ipin.sym} 0 -1140 2 1 {name=p_dig_in_22 lab=dig_in[22]}
C {lab_pin.sym} 40 -1140 0 1 {name=lp_dig_in_22 sig_type=std_logic lab=dig_in[22]}
N 0 -1120 40 -1120 {lab=dig_in[21]}
C {devices/ipin.sym} 0 -1120 2 1 {name=p_dig_in_21 lab=dig_in[21]}
C {lab_pin.sym} 40 -1120 0 1 {name=lp_dig_in_21 sig_type=std_logic lab=dig_in[21]}
N 0 -1100 40 -1100 {lab=dig_in[20]}
C {devices/ipin.sym} 0 -1100 2 1 {name=p_dig_in_20 lab=dig_in[20]}
C {lab_pin.sym} 40 -1100 0 1 {name=lp_dig_in_20 sig_type=std_logic lab=dig_in[20]}
N 0 -1080 40 -1080 {lab=dig_in[19]}
C {devices/ipin.sym} 0 -1080 2 1 {name=p_dig_in_19 lab=dig_in[19]}
C {lab_pin.sym} 40 -1080 0 1 {name=lp_dig_in_19 sig_type=std_logic lab=dig_in[19]}
N 0 -1060 40 -1060 {lab=dig_in[18]}
C {devices/ipin.sym} 0 -1060 2 1 {name=p_dig_in_18 lab=dig_in[18]}
C {lab_pin.sym} 40 -1060 0 1 {name=lp_dig_in_18 sig_type=std_logic lab=dig_in[18]}
N 0 -1040 40 -1040 {lab=dig_in[17]}
C {devices/ipin.sym} 0 -1040 2 1 {name=p_dig_in_17 lab=dig_in[17]}
C {lab_pin.sym} 40 -1040 0 1 {name=lp_dig_in_17 sig_type=std_logic lab=dig_in[17]}
N 0 -1020 40 -1020 {lab=dig_in[16]}
C {devices/ipin.sym} 0 -1020 2 1 {name=p_dig_in_16 lab=dig_in[16]}
C {lab_pin.sym} 40 -1020 0 1 {name=lp_dig_in_16 sig_type=std_logic lab=dig_in[16]}
N 0 -1000 40 -1000 {lab=dig_in[15]}
C {devices/ipin.sym} 0 -1000 2 1 {name=p_dig_in_15 lab=dig_in[15]}
C {lab_pin.sym} 40 -1000 0 1 {name=lp_dig_in_15 sig_type=std_logic lab=dig_in[15]}
N 0 -980 40 -980 {lab=dig_in[14]}
C {devices/ipin.sym} 0 -980 2 1 {name=p_dig_in_14 lab=dig_in[14]}
C {lab_pin.sym} 40 -980 0 1 {name=lp_dig_in_14 sig_type=std_logic lab=dig_in[14]}
N 0 -960 40 -960 {lab=dig_in[13]}
C {devices/ipin.sym} 0 -960 2 1 {name=p_dig_in_13 lab=dig_in[13]}
C {lab_pin.sym} 40 -960 0 1 {name=lp_dig_in_13 sig_type=std_logic lab=dig_in[13]}
N 0 -940 40 -940 {lab=dig_in[12]}
C {devices/ipin.sym} 0 -940 2 1 {name=p_dig_in_12 lab=dig_in[12]}
C {lab_pin.sym} 40 -940 0 1 {name=lp_dig_in_12 sig_type=std_logic lab=dig_in[12]}
N 0 -920 40 -920 {lab=dig_in[11]}
C {devices/ipin.sym} 0 -920 2 1 {name=p_dig_in_11 lab=dig_in[11]}
C {lab_pin.sym} 40 -920 0 1 {name=lp_dig_in_11 sig_type=std_logic lab=dig_in[11]}
N 0 -900 40 -900 {lab=dig_in[10]}
C {devices/ipin.sym} 0 -900 2 1 {name=p_dig_in_10 lab=dig_in[10]}
C {lab_pin.sym} 40 -900 0 1 {name=lp_dig_in_10 sig_type=std_logic lab=dig_in[10]}
N 0 -880 40 -880 {lab=dig_in[9]}
C {devices/ipin.sym} 0 -880 2 1 {name=p_dig_in_9 lab=dig_in[9]}
C {lab_pin.sym} 40 -880 0 1 {name=lp_dig_in_9 sig_type=std_logic lab=dig_in[9]}
N 0 -860 40 -860 {lab=dig_in[8]}
C {devices/ipin.sym} 0 -860 2 1 {name=p_dig_in_8 lab=dig_in[8]}
C {lab_pin.sym} 40 -860 0 1 {name=lp_dig_in_8 sig_type=std_logic lab=dig_in[8]}
N 0 -840 40 -840 {lab=dig_in[7]}
C {devices/ipin.sym} 0 -840 2 1 {name=p_dig_in_7 lab=dig_in[7]}
C {lab_pin.sym} 40 -840 0 1 {name=lp_dig_in_7 sig_type=std_logic lab=dig_in[7]}
N 0 -820 40 -820 {lab=dig_in[6]}
C {devices/ipin.sym} 0 -820 2 1 {name=p_dig_in_6 lab=dig_in[6]}
C {lab_pin.sym} 40 -820 0 1 {name=lp_dig_in_6 sig_type=std_logic lab=dig_in[6]}
N 0 -800 40 -800 {lab=dig_in[5]}
C {devices/ipin.sym} 0 -800 2 1 {name=p_dig_in_5 lab=dig_in[5]}
C {lab_pin.sym} 40 -800 0 1 {name=lp_dig_in_5 sig_type=std_logic lab=dig_in[5]}
N 0 -780 40 -780 {lab=dig_in[4]}
C {devices/ipin.sym} 0 -780 2 1 {name=p_dig_in_4 lab=dig_in[4]}
C {lab_pin.sym} 40 -780 0 1 {name=lp_dig_in_4 sig_type=std_logic lab=dig_in[4]}
N 0 -760 40 -760 {lab=dig_in[3]}
C {devices/ipin.sym} 0 -760 2 1 {name=p_dig_in_3 lab=dig_in[3]}
C {lab_pin.sym} 40 -760 0 1 {name=lp_dig_in_3 sig_type=std_logic lab=dig_in[3]}
N 0 -740 40 -740 {lab=dig_in[2]}
C {devices/ipin.sym} 0 -740 2 1 {name=p_dig_in_2 lab=dig_in[2]}
C {lab_pin.sym} 40 -740 0 1 {name=lp_dig_in_2 sig_type=std_logic lab=dig_in[2]}
N 0 -720 40 -720 {lab=dig_in[1]}
C {devices/ipin.sym} 0 -720 2 1 {name=p_dig_in_1 lab=dig_in[1]}
C {lab_pin.sym} 40 -720 0 1 {name=lp_dig_in_1 sig_type=std_logic lab=dig_in[1]}
N 0 -700 40 -700 {lab=dig_in[0]}
C {devices/ipin.sym} 0 -700 2 1 {name=p_dig_in_0 lab=dig_in[0]}
C {lab_pin.sym} 40 -700 0 1 {name=lp_dig_in_0 sig_type=std_logic lab=dig_in[0]}
N 0 -680 40 -680 {lab=dig_out[11]}
C {devices/opin.sym} 0 -680 2 0 {name=p_dig_out_11 lab=dig_out[11]}
C {lab_pin.sym} 40 -680 0 1 {name=lp_dig_out_11 sig_type=std_logic lab=dig_out[11]}
N 0 -660 40 -660 {lab=dig_out[10]}
C {devices/opin.sym} 0 -660 2 0 {name=p_dig_out_10 lab=dig_out[10]}
C {lab_pin.sym} 40 -660 0 1 {name=lp_dig_out_10 sig_type=std_logic lab=dig_out[10]}
N 0 -640 40 -640 {lab=dig_out[9]}
C {devices/opin.sym} 0 -640 2 0 {name=p_dig_out_9 lab=dig_out[9]}
C {lab_pin.sym} 40 -640 0 1 {name=lp_dig_out_9 sig_type=std_logic lab=dig_out[9]}
N 0 -620 40 -620 {lab=dig_out[8]}
C {devices/opin.sym} 0 -620 2 0 {name=p_dig_out_8 lab=dig_out[8]}
C {lab_pin.sym} 40 -620 0 1 {name=lp_dig_out_8 sig_type=std_logic lab=dig_out[8]}
N 0 -600 40 -600 {lab=dig_out[7]}
C {devices/opin.sym} 0 -600 2 0 {name=p_dig_out_7 lab=dig_out[7]}
C {lab_pin.sym} 40 -600 0 1 {name=lp_dig_out_7 sig_type=std_logic lab=dig_out[7]}
N 0 -580 40 -580 {lab=dig_out[6]}
C {devices/opin.sym} 0 -580 2 0 {name=p_dig_out_6 lab=dig_out[6]}
C {lab_pin.sym} 40 -580 0 1 {name=lp_dig_out_6 sig_type=std_logic lab=dig_out[6]}
N 0 -560 40 -560 {lab=dig_out[5]}
C {devices/opin.sym} 0 -560 2 0 {name=p_dig_out_5 lab=dig_out[5]}
C {lab_pin.sym} 40 -560 0 1 {name=lp_dig_out_5 sig_type=std_logic lab=dig_out[5]}
N 0 -540 40 -540 {lab=dig_out[4]}
C {devices/opin.sym} 0 -540 2 0 {name=p_dig_out_4 lab=dig_out[4]}
C {lab_pin.sym} 40 -540 0 1 {name=lp_dig_out_4 sig_type=std_logic lab=dig_out[4]}
N 0 -520 40 -520 {lab=dig_out[3]}
C {devices/opin.sym} 0 -520 2 0 {name=p_dig_out_3 lab=dig_out[3]}
C {lab_pin.sym} 40 -520 0 1 {name=lp_dig_out_3 sig_type=std_logic lab=dig_out[3]}
N 0 -500 40 -500 {lab=dig_out[2]}
C {devices/opin.sym} 0 -500 2 0 {name=p_dig_out_2 lab=dig_out[2]}
C {lab_pin.sym} 40 -500 0 1 {name=lp_dig_out_2 sig_type=std_logic lab=dig_out[2]}
N 0 -480 40 -480 {lab=dig_out[1]}
C {devices/opin.sym} 0 -480 2 0 {name=p_dig_out_1 lab=dig_out[1]}
C {lab_pin.sym} 40 -480 0 1 {name=lp_dig_out_1 sig_type=std_logic lab=dig_out[1]}
N 0 -460 40 -460 {lab=dig_out[0]}
C {devices/opin.sym} 0 -460 2 0 {name=p_dig_out_0 lab=dig_out[0]}
C {lab_pin.sym} 40 -460 0 1 {name=lp_dig_out_0 sig_type=std_logic lab=dig_out[0]}
N 0 -440 40 -440 {lab=analog_pin[3]}
C {devices/iopin.sym} 0 -440 2 0 {name=p_analog_pin_3 lab=analog_pin[3]}
C {lab_pin.sym} 40 -440 0 1 {name=lp_analog_pin_3 sig_type=std_logic lab=analog_pin[3]}
T {LVDS out -} 100 -448 0 0 0.25 0.25 {}
N 0 -420 40 -420 {lab=analog_pin[2]}
C {devices/iopin.sym} 0 -420 2 0 {name=p_analog_pin_2 lab=analog_pin[2]}
C {lab_pin.sym} 40 -420 0 1 {name=lp_analog_pin_2 sig_type=std_logic lab=analog_pin[2]}
T {LVDS out +} 100 -428 0 0 0.25 0.25 {}
N 0 -400 40 -400 {lab=analog_pin[1]}
C {devices/iopin.sym} 0 -400 2 0 {name=p_analog_pin_1 lab=analog_pin[1]}
C {lab_pin.sym} 40 -400 0 1 {name=lp_analog_pin_1 sig_type=std_logic lab=analog_pin[1]}
T {PLL clock out - RESERVED, nothing drives it yet} 100 -408 0 0 0.25 0.25 {}
N 0 -380 40 -380 {lab=analog_pin[0]}
C {devices/iopin.sym} 0 -380 2 0 {name=p_analog_pin_0 lab=analog_pin[0]}
C {lab_pin.sym} 40 -380 0 1 {name=lp_analog_pin_0 sig_type=std_logic lab=analog_pin[0]}
T {PLL reference in, feeds lvds_pattern} 100 -388 0 0 0.25 0.25 {}
N 0 -360 40 -360 {lab=ibias[1]}
C {devices/ipin.sym} 0 -360 2 1 {name=p_ibias_1 lab=ibias[1]}
C {lab_pin.sym} 40 -360 0 1 {name=lp_ibias_1 sig_type=std_logic lab=ibias[1]}
N 0 -340 40 -340 {lab=ibias[0]}
C {devices/ipin.sym} 0 -340 2 1 {name=p_ibias_0 lab=ibias[0]}
C {lab_pin.sym} 40 -340 0 1 {name=lp_ibias_0 sig_type=std_logic lab=ibias[0]}
N 0 -320 40 -320 {lab=vbias}
C {devices/ipin.sym} 0 -320 2 1 {name=p_vbias lab=vbias}
C {lab_pin.sym} 40 -320 0 1 {name=lp_vbias sig_type=std_logic lab=vbias}
N 0 -300 40 -300 {lab=analog_bus[3]}
C {devices/iopin.sym} 0 -300 2 0 {name=p_analog_bus_3 lab=analog_bus[3]}
C {lab_pin.sym} 40 -300 0 1 {name=lp_analog_bus_3 sig_type=std_logic lab=analog_bus[3]}
N 0 -280 40 -280 {lab=analog_bus[2]}
C {devices/iopin.sym} 0 -280 2 0 {name=p_analog_bus_2 lab=analog_bus[2]}
C {lab_pin.sym} 40 -280 0 1 {name=lp_analog_bus_2 sig_type=std_logic lab=analog_bus[2]}
N 0 -260 40 -260 {lab=analog_bus[1]}
C {devices/iopin.sym} 0 -260 2 0 {name=p_analog_bus_1 lab=analog_bus[1]}
C {lab_pin.sym} 40 -260 0 1 {name=lp_analog_bus_1 sig_type=std_logic lab=analog_bus[1]}
N 0 -240 40 -240 {lab=analog_bus[0]}
C {devices/iopin.sym} 0 -240 2 0 {name=p_analog_bus_0 lab=analog_bus[0]}
C {lab_pin.sym} 40 -240 0 1 {name=lp_analog_bus_0 sig_type=std_logic lab=analog_bus[0]}
