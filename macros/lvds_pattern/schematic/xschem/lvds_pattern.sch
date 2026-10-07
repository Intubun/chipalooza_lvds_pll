v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {lvds_pattern - data source for the LVDS transmitter, sg13cmos5l standard cells only

  ref_clk   the bit clock, one bit per period
  en        1 = clock runs, 0 = clock stopped low (latch-based gate, no runt pulse)
  reset     active high, asynchronous, seeds the PRBS - shift register only
  mode      0 = gated clock straight to the pair, 1 = PRBS-7

D_p / D_n drive the pre-driver of macros/lvds_tx.} 90 -1280 0 0 0.6 0.6 {}
T {The PDK's latch-based clock gate.  GCLK is held low while en is 0, so
en may change at any point in the cycle without producing a runt pulse.
(The clock source select, ref_clk or pll_clk, went with the PLL, 2026-10-07.)} 200 -720 0 0 0.35 0.35 {}
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
T {reset trunk - shift register only} 1150 48 0 0 0.3 0.3 {}
T {The output pair is free of both en and reset by construction.  Their clock is
the ungated copy and their RESET_B is tied high.  xffp loads s6, xffn loads s6
through xinvd, so the two always load opposite values - in reset too, where s6
is 0: the pair then holds D_p = 1, D_n = 0, the state the set/reset flops gave
it, from the first clock edge on and through any reset.  It is never two equal
levels, so the common-mode loop of the LVDS driver settles once, at t=0, and
not again after a reset or an enable.

dfrbp_2 and not sg13cmos5l_sdfbbp_1 with asynchronous set/reset: that comes in
drive 1 only, its Q rises ~50 ps slower than it falls, and D_p/D_n came out
15 ps apart (28 ps extracted, with unequal Q loads) - enough to dent Vos of the
driver (lvds_tx README).  The inverter is in the D path only, not between clock
and output.} 2400 40 0 0 0.35 0.35 {}
N 200 -620 440 -620 {lab=ref_clk}
N 440 -620 440 -600 {lab=ref_clk}
N 200 -500 600 -500 {lab=en}
N 600 -590 600 -500 {lab=en}
N 600 -590 660 -590 {lab=en}
N 440 -600 620 -600 {lab=ref_clk}
N 620 -610 620 -600 {lab=ref_clk}
N 620 -610 660 -610 {lab=ref_clk}
N 840 -610 1010 -610 {lab=gclk}
N 1090 -320 1090 -220 {lab=gclk_b}
N 2110 -220 2760 -220 {lab=gclk_b}
N 310 -220 310 -120 {lab=gclk_b}
N 610 -220 610 -120 {lab=gclk_b}
N 910 -220 910 -120 {lab=gclk_b}
N 1210 -220 1210 -120 {lab=gclk_b}
N 1510 -220 1510 -120 {lab=gclk_b}
N 1810 -220 1810 -120 {lab=gclk_b}
N 2110 -220 2110 -120 {lab=gclk_b}
N 620 -790 660 -790 {lab=ref_clk}
N 600 -770 660 -770 {lab=VDD}
N 840 -790 1010 -790 {lab=gclk_free}
N 1090 -790 1150 -790 {lab=gclk_free_b}
N 2460 -170 2460 -120 {lab=gclk_free_b}
N 2760 -170 2760 -120 {lab=gclk_free_b}
N 0 -450 110 -450 {lab=reset}
N 190 -450 190 60 {lab=reset_b}
N 1810 60 2110 60 {lab=reset_b}
N 310 -80 310 60 {lab=reset_b}
N 610 -80 610 60 {lab=reset_b}
N 910 -80 910 60 {lab=reset_b}
N 1210 -80 1210 60 {lab=reset_b}
N 1510 -80 1510 60 {lab=reset_b}
N 1810 -80 1810 60 {lab=reset_b}
N 2110 20 2110 60 {lab=reset_b}
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
N 2350 -100 2350 200 {lab=s6}
N 2140 200 2350 200 {lab=s6}
N 2140 200 2140 230 {lab=s6}
N 2350 -100 2460 -100 {lab=s6}
N 2640 -580 2640 -120 {lab=fp}
N 2640 -580 3110 -580 {lab=fp}
N 2940 -280 2940 -120 {lab=fn}
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
N 3060 -620 3110 -620 {lab=gclk_bn}
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
N 910 -220 1090 -220 {lab=gclk_b}
N 310 -220 610 -220 {lab=gclk_b}
N 610 -220 910 -220 {lab=gclk_b}
N 1090 -220 1210 -220 {lab=gclk_b}
N 1210 -220 1510 -220 {lab=gclk_b}
N 1510 -220 1810 -220 {lab=gclk_b}
N 1810 -220 2110 -220 {lab=gclk_b}
N 190 60 310 60 {lab=reset_b}
N 310 60 610 60 {lab=reset_b}
N 610 60 910 60 {lab=reset_b}
N 910 60 1210 60 {lab=reset_b}
N 1210 60 1510 60 {lab=reset_b}
N 1510 60 1810 60 {lab=reset_b}
N 2350 -120 2350 -100 {lab=s6}
N 1090 -610 1090 -500 {lab=gclk_b}
N 1090 -500 1090 -320 {lab=gclk_b}
N 2290 -100 2320 -100 {lab=s6_n}
N 2320 -140 2320 -100 {lab=s6_n}
N 2320 -140 2400 -140 {lab=s6_n}
N 2700 -80 2760 -80 {lab=VDD}
N 2110 -80 2110 20 {lab=reset_b}
N 1090 -320 3110 -320 {lab=gclk_b}
N 3060 -620 3060 -500 {lab=gclk_bn}
C {devices/lab_wire.sym} 530 -600 0 0 {name=lw0 sig_type=std_logic lab=ref_clk}
C {devices/lab_wire.sym} 930 -610 0 0 {name=lw1 sig_type=std_logic lab=gclk}
C {devices/lab_wire.sym} 1090 -400 0 0 {name=lw2 sig_type=std_logic lab=gclk_b}
C {devices/lab_wire.sym} 620 -790 0 0 {name=lw3 sig_type=std_logic lab=ref_clk}
C {devices/lab_wire.sym} 600 -770 0 0 {name=lw4 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 930 -790 0 0 {name=lw5 sig_type=std_logic lab=gclk_free}
C {devices/lab_wire.sym} 1150 -790 0 0 {name=lw6 sig_type=std_logic lab=gclk_free_b}
C {devices/lab_wire.sym} 2460 -170 0 0 {name=lw7 sig_type=std_logic lab=gclk_free_b}
C {devices/lab_wire.sym} 2760 -170 0 0 {name=lw8 sig_type=std_logic lab=gclk_free_b}
C {devices/lab_wire.sym} 190 -200 0 0 {name=lw9 sig_type=std_logic lab=reset_b}
C {devices/lab_wire.sym} 2730 -80 0 0 {name=lw11 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 550 -112 0 0 {name=lw12 sig_type=std_logic lab=s0}
C {devices/lab_wire.sym} 850 -112 0 0 {name=lw13 sig_type=std_logic lab=s1}
C {devices/lab_wire.sym} 1150 -112 0 0 {name=lw14 sig_type=std_logic lab=s2}
C {devices/lab_wire.sym} 1450 -112 0 0 {name=lw15 sig_type=std_logic lab=s3}
C {devices/lab_wire.sym} 1750 -112 0 0 {name=lw16 sig_type=std_logic lab=s4}
C {devices/lab_wire.sym} 2050 -112 0 0 {name=lw17 sig_type=std_logic lab=s5}
C {devices/lab_wire.sym} 2350 100 0 0 {name=lw18 sig_type=std_logic lab=s6}
C {devices/lab_wire.sym} 2400 -140 0 0 {name=lw19 sig_type=std_logic lab=s6_n}
C {devices/lab_wire.sym} 2640 -350 0 0 {name=lw20 sig_type=std_logic lab=fp}
C {devices/lab_wire.sym} 2940 -200 0 0 {name=lw21 sig_type=std_logic lab=fn}
C {devices/lab_wire.sym} 2680 -60 0 0 {name=lw22 sig_type=std_logic lab=fp_n}
C {devices/lab_wire.sym} 2980 -60 0 0 {name=lw23 sig_type=std_logic lab=fn_n}
C {devices/lab_wire.sym} 2340 250 0 0 {name=lw24 sig_type=std_logic lab=fb}
C {devices/lab_wire.sym} 250 -100 0 0 {name=lw25 sig_type=std_logic lab=fb}
C {devices/lab_wire.sym} 530 -60 0 0 {name=lw26 sig_type=std_logic lab=s0_n}
C {devices/lab_wire.sym} 830 -60 0 0 {name=lw27 sig_type=std_logic lab=s1_n}
C {devices/lab_wire.sym} 1130 -60 0 0 {name=lw28 sig_type=std_logic lab=s2_n}
C {devices/lab_wire.sym} 1430 -60 0 0 {name=lw29 sig_type=std_logic lab=s3_n}
C {devices/lab_wire.sym} 1730 -60 0 0 {name=lw30 sig_type=std_logic lab=s4_n}
C {devices/lab_wire.sym} 2030 -60 0 0 {name=lw31 sig_type=std_logic lab=s5_n}
C {devices/lab_wire.sym} 1600 -500 0 0 {name=lw32 sig_type=std_logic lab=gclk_bn}
C {devices/lab_wire.sym} 1600 -320 0 0 {name=lw33 sig_type=std_logic lab=gclk_b}
C {devices/lab_wire.sym} 3080 -420 0 0 {name=lw34 sig_type=std_logic lab=mode}
C {devices/lab_wire.sym} 3270 -600 0 0 {name=lw35 sig_type=std_logic lab=dp0}
C {devices/lab_wire.sym} 3520 -600 0 0 {name=lw36 sig_type=std_logic lab=dp1}
C {devices/lab_wire.sym} 3770 -600 0 0 {name=lw37 sig_type=std_logic lab=dp2}
C {devices/lab_wire.sym} 3270 -300 0 0 {name=lw38 sig_type=std_logic lab=dn0}
C {devices/lab_wire.sym} 3520 -300 0 0 {name=lw39 sig_type=std_logic lab=dn1}
C {devices/lab_wire.sym} 3770 -300 0 0 {name=lw40 sig_type=std_logic lab=dn2}
C {devices/lab_wire.sym} 1320 -900 0 0 {name=lw41 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 1320 400 0 0 {name=lw42 sig_type=std_logic lab=VSS}
C {devices/ipin.sym} 200 -620 2 1 {name=p_ref_clk lab=ref_clk}
C {devices/ipin.sym} 200 -500 2 1 {name=p_en lab=en}
C {devices/ipin.sym} 0 -450 2 1 {name=p_reset lab=reset}
C {devices/ipin.sym} 2900 -700 2 1 {name=p_mode lab=mode}
C {devices/opin.sym} 4100 -600 2 0 {name=p_D_p lab=D_p}
C {devices/opin.sym} 4100 -300 2 0 {name=p_D_n lab=D_n}
C {devices/iopin.sym} 1200 -900 2 0 {name=p_VDD lab=VDD}
C {devices/iopin.sym} 1200 400 2 0 {name=p_VSS lab=VSS}
C {sg13cmos5l_stdcells/sg13cmos5l_lgcp_1.sym} 750 -600 0 0 {name=xicg}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_4.sym} 1050 -610 0 0 {name=xclkb}
C {sg13cmos5l_stdcells/sg13cmos5l_lgcp_1.sym} 750 -780 0 0 {name=xicg2}
C {sg13cmos5l_stdcells/sg13cmos5l_buf_4.sym} 1050 -790 0 0 {name=xclkb2}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 150 -450 0 0 {name=xrstb}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 400 -100 0 0 {name=xs0}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 700 -100 0 0 {name=xs1}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 1000 -100 0 0 {name=xs2}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 1300 -100 0 0 {name=xs3}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 1600 -100 0 0 {name=xs4}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 1900 -100 0 0 {name=xs5}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 2200 -100 0 0 {name=xs6}
C {sg13cmos5l_stdcells/sg13cmos5l_xnor2_1.sym} 2200 250 0 0 {name=xfb}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 1300 -500 0 0 {name=xclkn}
C {sg13cmos5l_stdcells/sg13cmos5l_mux2_2.sym} 3150 -600 0 0 {name=xmodep}
C {sg13cmos5l_stdcells/sg13cmos5l_mux2_2.sym} 3150 -300 0 0 {name=xmoden}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 3400 -600 0 0 {name=xp1}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_8.sym} 3650 -600 0 0 {name=xp2}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_16.sym} 3900 -600 0 0 {name=xbp}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_2.sym} 3400 -300 0 0 {name=xn1}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_8.sym} 3650 -300 0 0 {name=xn2}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_16.sym} 3900 -300 0 0 {name=xbn}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 2850 -100 0 0 {name=xffn}
C {sg13cmos5l_stdcells/sg13cmos5l_dfrbp_2.sym} 2550 -100 0 0 {name=xffp}
C {sg13cmos5l_stdcells/sg13cmos5l_decap_4.sym} -130 180 0 0 {name=x1 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_4.sym} -130 200 0 0 {name=x2 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_4.sym} -130 220 0 0 {name=x3 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_4.sym} -130 240 0 0 {name=x4 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_4.sym} -130 260 0 0 {name=x5 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_4.sym} -130 280 0 0 {name=x6 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 180 0 0 {name=x7 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 200 0 0 {name=x8 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 220 0 0 {name=x9 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 240 0 0 {name=x10 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 260 0 0 {name=x11 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 280 0 0 {name=x12 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 300 0 0 {name=x13 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 320 0 0 {name=x14 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 340 0 0 {name=x15 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -310 360 0 0 {name=x16 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 180 0 0 {name=x17 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 200 0 0 {name=x18 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 220 0 0 {name=x19 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 240 0 0 {name=x20 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 260 0 0 {name=x21 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 280 0 0 {name=x22 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 300 0 0 {name=x23 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 320 0 0 {name=x24 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 340 0 0 {name=x25 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -520 360 0 0 {name=x26 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 180 0 0 {name=x27 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 200 0 0 {name=x28 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 220 0 0 {name=x29 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 240 0 0 {name=x30 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 260 0 0 {name=x31 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 280 0 0 {name=x32 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 300 0 0 {name=x33 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 320 0 0 {name=x34 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 340 0 0 {name=x35 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -730 360 0 0 {name=x36 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -960 180 0 0 {name=x37 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -960 200 0 0 {name=x38 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -960 220 0 0 {name=x39 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -960 240 0 0 {name=x40 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} -960 260 0 0 {name=x41 VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
N 2420 -80 2460 -80 {lab=VDD}
N 2740 -170 2740 -100 {lab=s6_i}
N 2740 -100 2760 -100 {lab=s6_i}
C {devices/lab_wire.sym} 2440 -80 0 0 {name=lw48 sig_type=std_logic lab=VDD}
C {devices/lab_wire.sym} 2740 -130 1 0 {name=lw49 sig_type=std_logic lab=s6_i}
C {devices/lab_pin.sym} 2660 -170 0 0 {name=p40 sig_type=std_logic lab=s6}
C {sg13cmos5l_stdcells/sg13cmos5l_inv_1.sym} 2700 -170 0 0 {name=xinvd}
T {Antenna diodes: at the top level en and mode run ~360 um of metal3 from
dig_in onto one or two gates (Ant.b, ratio over 200).  One antennanp each,
inside the block, lifts the limit to 20000 (Ant.e).} -400 420 0 0 0.3 0.3 {}
C {sg13cmos5l_stdcells/sg13cmos5l_antennanp.sym} -130 520 0 0 {name=xant_en VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
N -260 520 -220 520 {lab=en}
C {devices/lab_pin.sym} -260 520 0 0 {name=p_ant_en sig_type=std_logic lab=en}
C {sg13cmos5l_stdcells/sg13cmos5l_antennanp.sym} -130 580 0 0 {name=xant_mode VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
N -260 580 -220 580 {lab=mode}
C {devices/lab_pin.sym} -260 580 0 0 {name=p_ant_mode sig_type=std_logic lab=mode}
T {ref_clk too: ~450 um of metal4 from pad 2, and its pad clamps to the 3.3 V
ring only - this pair clamps the clock gates' input to the block's own rails.} -400 620 0 0 0.3 0.3 {}
C {sg13cmos5l_stdcells/sg13cmos5l_antennanp.sym} -130 700 0 0 {name=xant_ref VDD=VDD VSS=VSS prefix=sg13cmos5l_ }
N -260 700 -220 700 {lab=ref_clk}
C {devices/lab_pin.sym} -260 700 0 0 {name=p_ant_ref sig_type=std_logic lab=ref_clk}
