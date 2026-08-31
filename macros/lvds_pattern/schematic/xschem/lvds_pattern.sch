v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {lvds_pattern - data source for the LVDS transmitter, sg13cmos5l standard cells only.

  clk_src   0 = ref_clk, 1 = pll_clk
  en        1 = clock runs, 0 = clock stopped low (latch-based gate, no runt pulse)
  reset     active high, asynchronous, seeds the PRBS
  mode      0 = gated clock straight to the pair, 1 = PRBS-7

D_p / D_n drive the pre-driver of macros/lvds_tx.} 200 -1150 0 0 0.5 0.5 {}
T {Clock source select, then the latch-based clock gate. GCLK is held low
while en is 0, so en may change at any time without a runt pulse.} 300 -720 0 0 0.35 0.35 {}
T {PRBS-7, x^7 + x^6 + 1. The flops hold the COMPLEMENT of the LFSR word:
dfrbp resets Q to 0, and an all-zero complement is the all-ones seed that
serdes_dig.v uses. The feedback is XNOR for the same reason, and the line
bit is s6_n. The stream is bit-identical to serdes_dig.v in PRBS7 mode.} 300 300 0 0 0.35 0.35 {}
T {Complementary output pair, sized for ~170 fF: D_p and D_n each drive two
40u/0.45u HV gates in the pre-driver. Matched inv_2 -> inv_8 front ends, then
buf_16 (two internal stages, four inversions) against inv_16 (three), which is
the pairing that measured the least D_p/D_n skew into that load: 23 ps, against
the pre-driver's ~40 ps budget. XOR/XNOR against VSS measured 48 ps.} 2700 -900 0 0 0.35 0.35 {}
N 320 -620 360 -620 {lab=ref_clk}
C {lab_pin.sym} 320 -620 0 0 {name=l_xcsel_a0 sig_type=std_logic lab=ref_clk}
N 320 -580 360 -580 {lab=pll_clk}
C {lab_pin.sym} 320 -580 0 0 {name=l_xcsel_a1 sig_type=std_logic lab=pll_clk}
N 320 -540 360 -540 {lab=clk_src}
C {lab_pin.sym} 320 -540 0 0 {name=l_xcsel_s sig_type=std_logic lab=clk_src}
N 440 -600 480 -600 {lab=clk_sel}
C {lab_pin.sym} 480 -600 0 1 {name=l_xcsel_x sig_type=std_logic lab=clk_sel}
C {sg13cmos5l_stdcells/sg13cmos5l_mux2_2.sym} 400 -600 0 0 {name=xcsel}
N 620 -610 660 -610 {lab=clk_sel}
C {lab_pin.sym} 620 -610 0 0 {name=l_xicg_clk sig_type=std_logic lab=clk_sel}
N 620 -590 660 -590 {lab=en}
C {lab_pin.sym} 620 -590 0 0 {name=l_xicg_gate sig_type=std_logic lab=en}
N 840 -610 880 -610 {lab=gclk}
C {lab_pin.sym} 880 -610 0 1 {name=l_xicg_gclk sig_type=std_logic lab=gclk}
C {sg13cmos5l_stdcells/sg13cmos5l_lgcp_1.sym} 750 -600 0 0 {name=xicg}
N 970 -610 1010 -610 {lab=gclk}
C {lab_pin.sym} 970 -610 0 0 {name=l_xclkb_a sig_type=std_logic lab=gclk}
N 1090 -610 1130 -610 {lab=gclk_b}
C {lab_pin.sym} 1130 -610 0 1 {name=l_xclkb_x sig_type=std_logic lab=gclk_b}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_4.sym} 1050 -610 0 0 {name=xclkb}
N 320 -450 360 -450 {lab=reset}
C {lab_pin.sym} 320 -450 0 0 {name=l_xrstb_a sig_type=std_logic lab=reset}
N 440 -450 480 -450 {lab=reset_b}
C {lab_pin.sym} 480 -450 0 1 {name=l_xrstb_y sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 400 -450 0 0 {name=xrstb}
N 270 -120 310 -120 {lab=gclk_b}
C {lab_pin.sym} 270 -120 0 0 {name=l_xs0_clk sig_type=std_logic lab=gclk_b}
N 270 -100 310 -100 {lab=fb}
C {lab_pin.sym} 270 -100 0 0 {name=l_xs0_d sig_type=std_logic lab=fb}
N 490 -120 530 -120 {lab=s0}
C {lab_pin.sym} 530 -120 0 1 {name=l_xs0_q sig_type=std_logic lab=s0}
N 490 -100 530 -100 {lab=s0_n}
C {lab_pin.sym} 530 -100 0 1 {name=l_xs0_q_n sig_type=std_logic lab=s0_n}
N 270 -80 310 -80 {lab=reset_b}
C {lab_pin.sym} 270 -80 0 0 {name=l_xs0_reset_b sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 400 -100 0 0 {name=xs0}
N 570 -120 610 -120 {lab=gclk_b}
C {lab_pin.sym} 570 -120 0 0 {name=l_xs1_clk sig_type=std_logic lab=gclk_b}
N 570 -100 610 -100 {lab=s0}
C {lab_pin.sym} 570 -100 0 0 {name=l_xs1_d sig_type=std_logic lab=s0}
N 790 -120 830 -120 {lab=s1}
C {lab_pin.sym} 830 -120 0 1 {name=l_xs1_q sig_type=std_logic lab=s1}
N 790 -100 830 -100 {lab=s1_n}
C {lab_pin.sym} 830 -100 0 1 {name=l_xs1_q_n sig_type=std_logic lab=s1_n}
N 570 -80 610 -80 {lab=reset_b}
C {lab_pin.sym} 570 -80 0 0 {name=l_xs1_reset_b sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 700 -100 0 0 {name=xs1}
N 870 -120 910 -120 {lab=gclk_b}
C {lab_pin.sym} 870 -120 0 0 {name=l_xs2_clk sig_type=std_logic lab=gclk_b}
N 870 -100 910 -100 {lab=s1}
C {lab_pin.sym} 870 -100 0 0 {name=l_xs2_d sig_type=std_logic lab=s1}
N 1090 -120 1130 -120 {lab=s2}
C {lab_pin.sym} 1130 -120 0 1 {name=l_xs2_q sig_type=std_logic lab=s2}
N 1090 -100 1130 -100 {lab=s2_n}
C {lab_pin.sym} 1130 -100 0 1 {name=l_xs2_q_n sig_type=std_logic lab=s2_n}
N 870 -80 910 -80 {lab=reset_b}
C {lab_pin.sym} 870 -80 0 0 {name=l_xs2_reset_b sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 1000 -100 0 0 {name=xs2}
N 1170 -120 1210 -120 {lab=gclk_b}
C {lab_pin.sym} 1170 -120 0 0 {name=l_xs3_clk sig_type=std_logic lab=gclk_b}
N 1170 -100 1210 -100 {lab=s2}
C {lab_pin.sym} 1170 -100 0 0 {name=l_xs3_d sig_type=std_logic lab=s2}
N 1390 -120 1430 -120 {lab=s3}
C {lab_pin.sym} 1430 -120 0 1 {name=l_xs3_q sig_type=std_logic lab=s3}
N 1390 -100 1430 -100 {lab=s3_n}
C {lab_pin.sym} 1430 -100 0 1 {name=l_xs3_q_n sig_type=std_logic lab=s3_n}
N 1170 -80 1210 -80 {lab=reset_b}
C {lab_pin.sym} 1170 -80 0 0 {name=l_xs3_reset_b sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 1300 -100 0 0 {name=xs3}
N 1470 -120 1510 -120 {lab=gclk_b}
C {lab_pin.sym} 1470 -120 0 0 {name=l_xs4_clk sig_type=std_logic lab=gclk_b}
N 1470 -100 1510 -100 {lab=s3}
C {lab_pin.sym} 1470 -100 0 0 {name=l_xs4_d sig_type=std_logic lab=s3}
N 1690 -120 1730 -120 {lab=s4}
C {lab_pin.sym} 1730 -120 0 1 {name=l_xs4_q sig_type=std_logic lab=s4}
N 1690 -100 1730 -100 {lab=s4_n}
C {lab_pin.sym} 1730 -100 0 1 {name=l_xs4_q_n sig_type=std_logic lab=s4_n}
N 1470 -80 1510 -80 {lab=reset_b}
C {lab_pin.sym} 1470 -80 0 0 {name=l_xs4_reset_b sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 1600 -100 0 0 {name=xs4}
N 1770 -120 1810 -120 {lab=gclk_b}
C {lab_pin.sym} 1770 -120 0 0 {name=l_xs5_clk sig_type=std_logic lab=gclk_b}
N 1770 -100 1810 -100 {lab=s4}
C {lab_pin.sym} 1770 -100 0 0 {name=l_xs5_d sig_type=std_logic lab=s4}
N 1990 -120 2030 -120 {lab=s5}
C {lab_pin.sym} 2030 -120 0 1 {name=l_xs5_q sig_type=std_logic lab=s5}
N 1990 -100 2030 -100 {lab=s5_n}
C {lab_pin.sym} 2030 -100 0 1 {name=l_xs5_q_n sig_type=std_logic lab=s5_n}
N 1770 -80 1810 -80 {lab=reset_b}
C {lab_pin.sym} 1770 -80 0 0 {name=l_xs5_reset_b sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 1900 -100 0 0 {name=xs5}
N 2070 -120 2110 -120 {lab=gclk_b}
C {lab_pin.sym} 2070 -120 0 0 {name=l_xs6_clk sig_type=std_logic lab=gclk_b}
N 2070 -100 2110 -100 {lab=s5}
C {lab_pin.sym} 2070 -100 0 0 {name=l_xs6_d sig_type=std_logic lab=s5}
N 2290 -120 2330 -120 {lab=s6}
C {lab_pin.sym} 2330 -120 0 1 {name=l_xs6_q sig_type=std_logic lab=s6}
N 2290 -100 2330 -100 {lab=s6_n}
C {lab_pin.sym} 2330 -100 0 1 {name=l_xs6_q_n sig_type=std_logic lab=s6_n}
N 2070 -80 2110 -80 {lab=reset_b}
C {lab_pin.sym} 2070 -80 0 0 {name=l_xs6_reset_b sig_type=std_logic lab=reset_b}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 2200 -100 0 0 {name=xs6}
N 2100 180 2140 180 {lab=s6}
C {lab_pin.sym} 2100 180 0 0 {name=l_xfb_a sig_type=std_logic lab=s6}
N 2100 220 2140 220 {lab=s5}
C {lab_pin.sym} 2100 220 0 0 {name=l_xfb_b sig_type=std_logic lab=s5}
N 2260 200 2300 200 {lab=fb}
C {lab_pin.sym} 2300 200 0 1 {name=l_xfb_y sig_type=std_logic lab=fb}
C {sg13cmos5l_stdcells/sg13cmos5l_xnor2_1.sym} 2200 200 0 0 {name=xfb}
N 2470 -620 2510 -620 {lab=gclk_b}
C {lab_pin.sym} 2470 -620 0 0 {name=l_xmode_a0 sig_type=std_logic lab=gclk_b}
N 2470 -580 2510 -580 {lab=s6_n}
C {lab_pin.sym} 2470 -580 0 0 {name=l_xmode_a1 sig_type=std_logic lab=s6_n}
N 2470 -540 2510 -540 {lab=mode}
C {lab_pin.sym} 2470 -540 0 0 {name=l_xmode_s sig_type=std_logic lab=mode}
N 2590 -600 2630 -600 {lab=d}
C {lab_pin.sym} 2630 -600 0 1 {name=l_xmode_x sig_type=std_logic lab=d}
C {sg13cmos5l_stdcells/sg13cmos5l_mux2_2.sym} 2550 -600 0 0 {name=xmode}
N 2820 -740 2860 -740 {lab=d}
C {lab_pin.sym} 2820 -740 0 0 {name=l_xp1_a sig_type=std_logic lab=d}
N 2940 -740 2980 -740 {lab=dp1}
C {lab_pin.sym} 2980 -740 0 1 {name=l_xp1_y sig_type=std_logic lab=dp1}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 2900 -740 0 0 {name=xp1}
N 3070 -740 3110 -740 {lab=dp1}
C {lab_pin.sym} 3070 -740 0 0 {name=l_xp2_a sig_type=std_logic lab=dp1}
N 3190 -740 3230 -740 {lab=dp2}
C {lab_pin.sym} 3230 -740 0 1 {name=l_xp2_y sig_type=std_logic lab=dp2}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_8.sym} 3150 -740 0 0 {name=xp2}
N 3320 -740 3360 -740 {lab=dp2}
C {lab_pin.sym} 3320 -740 0 0 {name=l_xbp_a sig_type=std_logic lab=dp2}
N 3440 -740 3480 -740 {lab=D_p}
C {lab_pin.sym} 3480 -740 0 1 {name=l_xbp_x sig_type=std_logic lab=D_p}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_16.sym} 3400 -740 0 0 {name=xbp}
N 2820 -480 2860 -480 {lab=d}
C {lab_pin.sym} 2820 -480 0 0 {name=l_xn1_a sig_type=std_logic lab=d}
N 2940 -480 2980 -480 {lab=dn1}
C {lab_pin.sym} 2980 -480 0 1 {name=l_xn1_y sig_type=std_logic lab=dn1}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 2900 -480 0 0 {name=xn1}
N 3070 -480 3110 -480 {lab=dn1}
C {lab_pin.sym} 3070 -480 0 0 {name=l_xn2_a sig_type=std_logic lab=dn1}
N 3190 -480 3230 -480 {lab=dn2}
C {lab_pin.sym} 3230 -480 0 1 {name=l_xn2_y sig_type=std_logic lab=dn2}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_8.sym} 3150 -480 0 0 {name=xn2}
N 3320 -480 3360 -480 {lab=dn2}
C {lab_pin.sym} 3320 -480 0 0 {name=l_xbn_a sig_type=std_logic lab=dn2}
N 3440 -480 3480 -480 {lab=D_n}
C {lab_pin.sym} 3480 -480 0 1 {name=l_xbn_y sig_type=std_logic lab=D_n}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_16.sym} 3400 -480 0 0 {name=xbn}
N 0 -900 40 -900 {lab=ref_clk}
C {devices/ipin.sym} 0 -900 2 1 {name=p_ref_clk lab=ref_clk}
C {lab_pin.sym} 40 -900 0 1 {name=lp_ref_clk sig_type=std_logic lab=ref_clk}
N 0 -880 40 -880 {lab=pll_clk}
C {devices/ipin.sym} 0 -880 2 1 {name=p_pll_clk lab=pll_clk}
C {lab_pin.sym} 40 -880 0 1 {name=lp_pll_clk sig_type=std_logic lab=pll_clk}
N 0 -860 40 -860 {lab=clk_src}
C {devices/ipin.sym} 0 -860 2 1 {name=p_clk_src lab=clk_src}
C {lab_pin.sym} 40 -860 0 1 {name=lp_clk_src sig_type=std_logic lab=clk_src}
N 0 -840 40 -840 {lab=en}
C {devices/ipin.sym} 0 -840 2 1 {name=p_en lab=en}
C {lab_pin.sym} 40 -840 0 1 {name=lp_en sig_type=std_logic lab=en}
N 0 -820 40 -820 {lab=reset}
C {devices/ipin.sym} 0 -820 2 1 {name=p_reset lab=reset}
C {lab_pin.sym} 40 -820 0 1 {name=lp_reset sig_type=std_logic lab=reset}
N 0 -800 40 -800 {lab=mode}
C {devices/ipin.sym} 0 -800 2 1 {name=p_mode lab=mode}
C {lab_pin.sym} 40 -800 0 1 {name=lp_mode sig_type=std_logic lab=mode}
N 0 -760 40 -760 {lab=D_p}
C {devices/opin.sym} 0 -760 2 0 {name=p_D_p lab=D_p}
C {lab_pin.sym} 40 -760 0 1 {name=lp_D_p sig_type=std_logic lab=D_p}
N 0 -740 40 -740 {lab=D_n}
C {devices/opin.sym} 0 -740 2 0 {name=p_D_n lab=D_n}
C {lab_pin.sym} 40 -740 0 1 {name=lp_D_n sig_type=std_logic lab=D_n}
N 0 -700 40 -700 {lab=VDD}
C {devices/iopin.sym} 0 -700 2 0 {name=p_VDD lab=VDD}
C {lab_pin.sym} 40 -700 0 1 {name=lp_VDD sig_type=std_logic lab=VDD}
N 0 -680 40 -680 {lab=VSS}
C {devices/iopin.sym} 0 -680 2 0 {name=p_VSS lab=VSS}
C {lab_pin.sym} 40 -680 0 1 {name=lp_VSS sig_type=std_logic lab=VSS}
