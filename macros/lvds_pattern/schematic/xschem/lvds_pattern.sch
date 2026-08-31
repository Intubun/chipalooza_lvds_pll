v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {lvds_pattern - data source for the LVDS transmitter, sg13cmos5l standard cells only

  clk_src   0 = ref_clk, 1 = pll_clk
  en        1 = clock runs, 0 = clock stopped low (latch-based gate, no runt pulse)
  reset     active high, asynchronous, seeds the PRBS
  mode      0 = gated clock straight to the pair, 1 = PRBS-7

D_p / D_n drive the pre-driver of macros/lvds_tx.} 150 -1000 0 0 0.6 0.6 {}
T {Clock source select, then the PDK's latch-based clock gate.  GCLK is
held low while en is 0, so en may change at any point in the cycle
without producing a runt pulse.} 200 -700 0 0 0.35 0.35 {}
T {PRBS-7, x^7 + x^6 + 1.  The seven flops hold the COMPLEMENT of the LFSR word:
dfrbp resets Q to 0, and an all-zero complement is the all-ones seed that
serdes_dig.v uses.  That is why the feedback gate is an XNOR and not an XOR, and
why the bit that goes to the line is s6_n rather than s6.  The stream is
bit-identical to serdes_dig.v in PRBS7 mode, so serdes/check_link.py works
against this block unchanged.

xsout re-registers the line bit on the same clock, so what leaves the block is a
flop output and not a combinational path through the shift register's fanout: both
mux inputs are then synchronous edges.  It costs one bit of latency and does not
change the sequence - b[k] = b[k-7] xor b[k-6] is shift invariant.

The feedback net fb is the one connection drawn as a label at each end instead of
a wire - it returns from the XNOR at the right to the first flop at the left.} 250 400 0 0 0.4 0.4 {}
T {Complementary output pair, sized for the ~170 fF the pre-driver presents
(two 40u/0.45u HV gates per side).  Matched inv_2 -> inv_8 front ends, then
buf_16 - two internal stages, so four inversions - against inv_16, three.
That pairing measured the least D_p/D_n skew into that load: 23 ps, against
the pre-driver's ~40 ps budget.  XOR/XNOR against VSS measured 48 ps.} 2800 -900 0 0 0.35 0.35 {}
T {clock trunk} 1150 -232 0 0 0.3 0.3 {}
T {reset trunk} 1150 48 0 0 0.3 0.3 {}
N 200 -620 360 -620 {lab=ref_clk}
N 200 -580 360 -580 {lab=pll_clk}
N 200 -540 360 -540 {lab=clk_src}
N 200 -500 600 -500 {lab=en}
N 600 -500 600 -590 {lab=en}
N 600 -590 660 -590 {lab=en}
N 440 -600 620 -600 {lab=clk_sel}
N 620 -600 620 -610 {lab=clk_sel}
N 620 -610 660 -610 {lab=clk_sel}
N 840 -610 1010 -610 {lab=gclk}
N 1090 -610 1090 -220 {lab=gclk_b}
N 310 -220 2760 -220 {lab=gclk_b}
N 310 -220 310 -120 {lab=gclk_b}
N 610 -220 610 -120 {lab=gclk_b}
N 910 -220 910 -120 {lab=gclk_b}
N 1210 -220 1210 -120 {lab=gclk_b}
N 1510 -220 1510 -120 {lab=gclk_b}
N 1810 -220 1810 -120 {lab=gclk_b}
N 2110 -220 2110 -120 {lab=gclk_b}
N 2460 -220 2460 -120 {lab=gclk_b}
N 2760 -220 2760 -120 {lab=gclk_b}
N 1090 -610 2520 -610 {lab=gclk_b}
N 2520 -610 2520 -620 {lab=gclk_b}
N 2520 -620 2560 -620 {lab=gclk_b}
N 0 -450 110 -450 {lab=reset}
N 190 -450 190 60 {lab=reset_b}
N 190 60 2760 60 {lab=reset_b}
N 310 60 310 -80 {lab=reset_b}
N 610 60 610 -80 {lab=reset_b}
N 910 60 910 -80 {lab=reset_b}
N 1210 60 1210 -80 {lab=reset_b}
N 1510 60 1510 -80 {lab=reset_b}
N 1810 60 1810 -80 {lab=reset_b}
N 2110 60 2110 -80 {lab=reset_b}
N 2460 60 2460 -80 {lab=reset_b}
N 2760 60 2760 -80 {lab=reset_b}
N 490 -120 550 -120 {lab=s0}
N 550 -120 550 -100 {lab=s0}
N 550 -100 610 -100 {lab=s0}
N 790 -120 850 -120 {lab=s1}
N 850 -120 850 -100 {lab=s1}
N 850 -100 910 -100 {lab=s1}
N 1090 -120 1150 -120 {lab=s2}
N 1150 -120 1150 -100 {lab=s2}
N 1150 -100 1210 -100 {lab=s2}
N 1390 -120 1450 -120 {lab=s3}
N 1450 -120 1450 -100 {lab=s3}
N 1450 -100 1510 -100 {lab=s3}
N 1690 -120 1750 -120 {lab=s4}
N 1750 -120 1750 -100 {lab=s4}
N 1750 -100 1810 -100 {lab=s4}
N 1990 -120 2050 -120 {lab=s5}
N 2050 -120 2050 -100 {lab=s5}
N 2050 -100 2110 -100 {lab=s5}
N 2050 -100 2050 270 {lab=s5}
N 2050 270 2140 270 {lab=s5}
N 2290 -120 2350 -120 {lab=s6}
N 2350 -120 2350 200 {lab=s6}
N 2350 200 2140 200 {lab=s6}
N 2140 200 2140 230 {lab=s6}
N 2350 -100 2460 -100 {lab=s6}
N 2290 -100 2290 -40 {lab=s6_n}
N 2290 -40 2700 -40 {lab=s6_n}
N 2700 -40 2700 -100 {lab=s6_n}
N 2700 -100 2760 -100 {lab=s6_n}
N 2640 -120 2640 -580 {lab=fp}
N 2640 -580 3110 -580 {lab=fp}
N 2940 -120 2940 -280 {lab=fn}
N 2940 -280 3110 -280 {lab=fn}
N 2640 -100 2680 -100 {lab=fp_n}
N 2680 -100 2680 -60 {lab=fp_n}
N 2940 -100 2980 -100 {lab=fn_n}
N 2980 -100 2980 -60 {lab=fn_n}
N 2260 250 2340 250 {lab=fb}
N 250 -100 310 -100 {lab=fb}
N 490 -100 530 -100 {lab=s0_n}
N 530 -100 530 -60 {lab=s0_n}
N 790 -100 830 -100 {lab=s1_n}
N 830 -100 830 -60 {lab=s1_n}
N 1090 -100 1130 -100 {lab=s2_n}
N 1130 -100 1130 -60 {lab=s2_n}
N 1390 -100 1430 -100 {lab=s3_n}
N 1430 -100 1430 -60 {lab=s3_n}
N 1690 -100 1730 -100 {lab=s4_n}
N 1730 -100 1730 -60 {lab=s4_n}
N 1990 -100 2030 -100 {lab=s5_n}
N 2030 -100 2030 -60 {lab=s5_n}
N 1090 -500 1260 -500 {lab=gclk_b}
N 1340 -500 3060 -500 {lab=gclk_bn}
N 3060 -500 3060 -620 {lab=gclk_bn}
N 3060 -620 3110 -620 {lab=gclk_bn}
N 1090 -320 3110 -320 {lab=gclk_b}
N 2900 -700 3080 -700 {lab=mode}
N 3080 -700 3080 -540 {lab=mode}
N 3080 -540 3110 -540 {lab=mode}
N 3080 -540 3080 -240 {lab=mode}
N 3080 -240 3110 -240 {lab=mode}
N 3190 -600 3360 -600 {lab=dp0}
N 3440 -600 3610 -600 {lab=dp1}
N 3690 -600 3860 -600 {lab=dp2}
N 3940 -600 4100 -600 {lab=D_p}
N 3190 -300 3360 -300 {lab=dn0}
N 3440 -300 3610 -300 {lab=dn1}
N 3690 -300 3860 -300 {lab=dn2}
N 3940 -300 4100 -300 {lab=D_n}
N 1200 -900 1320 -900 {lab=VDD}
N 1200 400 1320 400 {lab=VSS}
C {devices/lab_wire.sym} 530 -600 0 0 {name=lw0 sig_type=std_logic lab=clk_sel}
C {devices/lab_wire.sym} 930 -610 0 0 {name=lw1 sig_type=std_logic lab=gclk}
C {devices/lab_wire.sym} 1090 -400 0 0 {name=lw2 sig_type=std_logic lab=gclk_b}
C {devices/lab_wire.sym} 190 -200 0 0 {name=lw3 sig_type=std_logic lab=reset_b}
C {devices/lab_wire.sym} 550 -112 0 0 {name=lw4 sig_type=std_logic lab=s0}
C {devices/lab_wire.sym} 850 -112 0 0 {name=lw5 sig_type=std_logic lab=s1}
C {devices/lab_wire.sym} 1150 -112 0 0 {name=lw6 sig_type=std_logic lab=s2}
C {devices/lab_wire.sym} 1450 -112 0 0 {name=lw7 sig_type=std_logic lab=s3}
C {devices/lab_wire.sym} 1750 -112 0 0 {name=lw8 sig_type=std_logic lab=s4}
C {devices/lab_wire.sym} 2050 -112 0 0 {name=lw9 sig_type=std_logic lab=s5}
C {devices/lab_wire.sym} 2350 100 0 0 {name=lw10 sig_type=std_logic lab=s6}
C {devices/lab_wire.sym} 2500 -40 0 0 {name=lw11 sig_type=std_logic lab=s6_n}
C {devices/lab_wire.sym} 2640 -350 0 0 {name=lw12 sig_type=std_logic lab=fp}
C {devices/lab_wire.sym} 2940 -200 0 0 {name=lw13 sig_type=std_logic lab=fn}
C {devices/lab_wire.sym} 2680 -60 0 0 {name=lw14 sig_type=std_logic lab=fp_n}
C {devices/lab_wire.sym} 2980 -60 0 0 {name=lw15 sig_type=std_logic lab=fn_n}
C {devices/lab_wire.sym} 2340 250 0 0 {name=lw16 sig_type=std_logic lab=fb}
C {devices/lab_wire.sym} 250 -100 0 0 {name=lw17 sig_type=std_logic lab=fb}
C {devices/lab_wire.sym} 530 -60 0 0 {name=lw18 sig_type=std_logic lab=s0_n}
C {devices/lab_wire.sym} 830 -60 0 0 {name=lw19 sig_type=std_logic lab=s1_n}
C {devices/lab_wire.sym} 1130 -60 0 0 {name=lw20 sig_type=std_logic lab=s2_n}
C {devices/lab_wire.sym} 1430 -60 0 0 {name=lw21 sig_type=std_logic lab=s3_n}
C {devices/lab_wire.sym} 1730 -60 0 0 {name=lw22 sig_type=std_logic lab=s4_n}
C {devices/lab_wire.sym} 2030 -60 0 0 {name=lw23 sig_type=std_logic lab=s5_n}
C {devices/lab_wire.sym} 1600 -500 0 0 {name=lw24 sig_type=std_logic lab=gclk_bn}
C {devices/lab_wire.sym} 1600 -320 0 0 {name=lw25 sig_type=std_logic lab=gclk_b}
C {devices/lab_wire.sym} 3080 -420 0 0 {name=lw26 sig_type=std_logic lab=mode}
C {devices/lab_wire.sym} 3270 -600 0 0 {name=lw27 sig_type=std_logic lab=dp0}
C {devices/lab_wire.sym} 3520 -600 0 0 {name=lw28 sig_type=std_logic lab=dp1}
C {devices/lab_wire.sym} 3770 -600 0 0 {name=lw29 sig_type=std_logic lab=dp2}
C {devices/lab_wire.sym} 3270 -300 0 0 {name=lw30 sig_type=std_logic lab=dn0}
C {devices/lab_wire.sym} 3520 -300 0 0 {name=lw31 sig_type=std_logic lab=dn1}
C {devices/lab_wire.sym} 3770 -300 0 0 {name=lw32 sig_type=std_logic lab=dn2}
C {devices/lab_wire.sym} 1320 -900 0 0 {name=lw33 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 1320 400 0 0 {name=lw34 sig_type=std_logic lab=VSS}
C {devices/ipin.sym} 200 -620 2 1 {name=p_ref_clk lab=ref_clk}
C {devices/ipin.sym} 200 -580 2 1 {name=p_pll_clk lab=pll_clk}
C {devices/ipin.sym} 200 -540 2 1 {name=p_clk_src lab=clk_src}
C {devices/ipin.sym} 200 -500 2 1 {name=p_en lab=en}
C {devices/ipin.sym} 0 -450 2 1 {name=p_reset lab=reset}
C {devices/ipin.sym} 2900 -700 2 1 {name=p_mode lab=mode}
C {devices/opin.sym} 4100 -600 2 0 {name=p_D_p lab=D_p}
C {devices/opin.sym} 4100 -300 2 0 {name=p_D_n lab=D_n}
C {devices/iopin.sym} 1200 -900 2 0 {name=p_VDD lab=VDD}
C {devices/iopin.sym} 1200 400 2 0 {name=p_VSS lab=VSS}
C {sg13cmos5l_stdcells/sg13cmos5l_mux2_2.sym} 400 -600 0 0 {name=xcsel}
C {sg13cmos5l_stdcells/sg13cmos5l_lgcp_1.sym} 750 -600 0 0 {name=xicg}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_4.sym} 1050 -610 0 0 {name=xclkb}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 150 -450 0 0 {name=xrstb}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 400 -100 0 0 {name=xs0}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 700 -100 0 0 {name=xs1}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 1000 -100 0 0 {name=xs2}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 1300 -100 0 0 {name=xs3}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_1.sym} 1600 -100 0 0 {name=xs4}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 1900 -100 0 0 {name=xs5}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 2200 -100 0 0 {name=xs6}
C {sg13cmos5l_stdcells/sg13cmos5l_xnor2_1.sym} 2200 250 0 0 {name=xfb}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 2550 -100 0 0 {name=xffp}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 2850 -100 0 0 {name=xffn}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 1300 -500 0 0 {name=xclkn}
C {sg13cmos5l_stdcells/sg13cmos5l_mux2_2.sym} 3150 -600 0 0 {name=xmodep}
C {sg13cmos5l_stdcells/sg13cmos5l_mux2_2.sym} 3150 -300 0 0 {name=xmoden}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 3400 -600 0 0 {name=xp1}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_8.sym} 3650 -600 0 0 {name=xp2}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_16.sym} 3900 -600 0 0 {name=xbp}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 3400 -300 0 0 {name=xn1}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_8.sym} 3650 -300 0 0 {name=xn2}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_16.sym} 3900 -300 0 0 {name=xbn}
