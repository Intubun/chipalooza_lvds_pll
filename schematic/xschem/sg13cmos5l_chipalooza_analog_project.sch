v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
L 4 2680 -600 3180 -600 {}
L 4 2680 -1030 2680 -600 {}
L 4 2680 -1030 3180 -1030 {}
L 4 3180 -1030 3180 -600 {}
T {Chipalooza 2026 - LVDS transmitter with PRBS-7 generator} 870 -2230 0 0 1 1 {}
T {Port list is verilog/rtl/user_project_wrapper_4a.v from
RTimothyEdwards/sg13cmos5l_ocd_chipalooza, every bus expanded into
individual pins.  Four dedicated analog pads means slot s1 or s16 -
per config.txt the only two that have four.

  analog_pin[0]  ref_clk   PLL reference in, feeds lvds_pattern and the PLL
  analog_pin[1]  pll_out   the PLL's TEST_CLK, brought off chip
  analog_pin[2]  d_p       LVDS out +
  analog_pin[3]  d_n       LVDS out -

All four are sg13cmos5l_IOPadAnalog in config.txt, so each pad is one core
signal carrying the pad name.  A different pad type changes that: an InOut
pad becomes five core signals (_in, _out, _ena, _one, _zero).

Not connected: dig_out[11:0], analog_bus[3:2], vssio, clk - the reference
arrives on its own dedicated pad instead of the shared clock pin - and enable.
The harness already masks dig_in to zero for an unselected project
(proj_dig_in is dig_in ANDed with 24 copies of select & dig_ena, in
user_project_control.v), so
dig_in[1] alone stops the pattern clock.  Note this drops the one case the
gate used to cover: select and dig_ena high with enable low leaves dig_in[1]
live, and the block then runs with the project enable deasserted.} -70 -2310 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit individually to a
pin, a constant or the sequencer, so a configuration bit costs a register
write and no pin.  Unselected holds every dig_in at zero, and all-zero
leaves the clock stopped and the output pair static - a legal idle.

  dig_in[0]     clk_src    0 = ref_clk, 1 = pll_clk
  dig_in[1]     en         gates the pattern clock
  dig_in[2]     reset      active high, seeds the PRBS
  dig_in[3]     mode       0 = clock passthrough, 1 = PRBS-7
  dig_in[4]     unused     carried the provisional pll_clk before the PLL was placed
  dig_in[5]     PLL ENABLE
  dig_in[6]     PLL RESET_N, active low
  dig_in[16:7]  PLL DIV_RATIO[9:0], unsigned Q7.3
  dig_in[18:17] PLL TEST_DIV[1:0]
  dig_in[23:19] unused

The Q7.3 ratio costs 10 bits where the earlier split DIV_INT + DIV_FRAC cost
23, so the PLL and the LVDS controls together now fit in 18 of the 24 bits
and DIV_FRAC no longer has to be tied off.} 300 -1400 0 0 0.4 0.4 {}
T {LVDS out -} 2420 -1048 0 0 0.25 0.25 {}
T {LVDS out +} 2420 -1068 0 0 0.25 0.25 {}
T {PLL clock out - the PLL's TEST_CLK} 2460 -388 0 0 0.25 0.25 {}
T {Reference Clock Input 1-500 MHz} 370 -728 0 0 0.25 0.25 {}
T {Decoupling Capacitors} 2860 -990 0 0 0.25 0.25 {}
T {PLL - macros/pll_analog/schematic/xschem/pll.sch, the assembled top.

The whole loop is inside: PFD, charge pump, loop filter, ring oscillator,
feedback divider and output divider.  Nothing of VCO_CLK, UP/DOWN or
FB_CLK leaves the block.

  REF_CLK   analog_pin[0]   same dedicated pad as the pattern generator
  PLL_CLK   -> pll_clk      this is what clocks lvds_pattern now
  TEST_CLK  analog_pin[1]   the reserved pad
  IREF      analog_bus[0]   NOT ibias - the transmitter uses both, and
                            the references cannot be shared
  DIV_RATIO dig_in[16:7]    unsigned Q7.3 divider ratio
  TEST_DIV  dig_in[18:17]   ENABLE dig_in[5], RESET_N dig_in[6]

The Q7.3 ratio supports integer-N when bits [2:0] are zero and fractional-N
in eighth steps. The complete PLL and LVDS controls use 18 of 24 dig_in bits.

NOT tapeout-ready: PFD and both dividers are XSPICE behavioural models
(d_dff, d_and2, d_fdiv with adc/dac bridges).  The synthesisable version
is the RTL in macros/pll_digital.

And the DIV_RATIO / TEST_DIV pins above do nothing here: inside pll.sch they
are ipin declarations that connect to nothing, feedback_divider.sym carries
only VCO_IN and FB_OUT, and the divide comes from a model card,
.model pll_feedback_div d_fdiv(div_factor=20 ...).  TEST_CLK is likewise
always VCO/4.  Measured 2026-09-01 at 250 MHz with DIV_RATIO = 4.0: the loop
asks for 5 GHz, the ring stops at 4.05 GHz, VCTRL rails and pll_clk comes out
at 1.997 GHz.  Only macros/pll_digital decodes DIV_RATIO, via
scripts/pll/run_pll_cosim.sh.

The loop filter is complete again: the container update of 2026-08-30 brought
cap_cmomf, and the netlist now carries XR1 plus XC1A and XC2.} 800 -2740 0 0 0.4 0.4 {}
T {PLL Clock out} 2430 -648 0 0 0.25 0.25 {}
T {vdd_3v3  ->  xlvds.Va, Cd33 decoupling} -180 -1308 0 1 0.25 0.25 {}
T {vdd_1v2  ->  xpat.VDD, xpll.VDD, Cd12 decoupling} -180 -1288 0 1 0.25 0.25 {}
T {vss_3v3  ->  xlvds.Vss, Cd33 decoupling} -180 -1268 0 1 0.25 0.25 {}
T {vss_1v2  ->  xpat.VSS, xpll.VSS, Cd12 decoupling} -180 -1248 0 1 0.25 0.25 {}
T {vssio  not connected} -180 -1228 0 1 0.25 0.25 {}
T {enable  not connected} -180 -1208 0 1 0.25 0.25 {}
T {clk  not connected - the reference comes in on analog_pin[0]} -180 -1188 0 1 0.25 0.25 {}
T {dig_in[23]  not connected} -180 -1168 0 1 0.25 0.25 {}
T {dig_in[22]  not connected} -180 -1148 0 1 0.25 0.25 {}
T {dig_in[21]  not connected} -180 -1128 0 1 0.25 0.25 {}
T {dig_in[20]  not connected} -180 -1108 0 1 0.25 0.25 {}
T {dig_in[19]  not connected} -180 -1088 0 1 0.25 0.25 {}
T {dig_in[18]  ->  xpll.TEST_DIV[1]} -180 -1068 0 1 0.25 0.25 {}
T {dig_in[17]  ->  xpll.TEST_DIV[0]} -180 -1048 0 1 0.25 0.25 {}
T {dig_in[16]  ->  xpll.DIV_RATIO[9] - weight 64} -180 -1028 0 1 0.25 0.25 {}
T {dig_in[15]  ->  xpll.DIV_RATIO[8] - weight 32} -180 -1008 0 1 0.25 0.25 {}
T {dig_in[14]  ->  xpll.DIV_RATIO[7] - weight 16} -180 -988 0 1 0.25 0.25 {}
T {dig_in[13]  ->  xpll.DIV_RATIO[6] - weight 8} -180 -968 0 1 0.25 0.25 {}
T {dig_in[12]  ->  xpll.DIV_RATIO[5] - weight 4} -180 -948 0 1 0.25 0.25 {}
T {dig_in[11]  ->  xpll.DIV_RATIO[4] - weight 2} -180 -928 0 1 0.25 0.25 {}
T {dig_in[10]  ->  xpll.DIV_RATIO[3] - weight 1} -180 -908 0 1 0.25 0.25 {}
T {dig_in[9]  ->  xpll.DIV_RATIO[2] - weight 1/2} -180 -888 0 1 0.25 0.25 {}
T {dig_in[8]  ->  xpll.DIV_RATIO[1] - weight 1/4} -180 -868 0 1 0.25 0.25 {}
T {dig_in[7]  ->  xpll.DIV_RATIO[0] - weight 1/8} -180 -848 0 1 0.25 0.25 {}
T {dig_in[6]  ->  xpll.RESET_N - active low} -180 -828 0 1 0.25 0.25 {}
T {dig_in[5]  ->  xpll.ENABLE} -180 -808 0 1 0.25 0.25 {}
T {dig_in[4]  not connected - was the provisional pll_clk} -180 -788 0 1 0.25 0.25 {}
T {dig_in[3]  ->  xpat.mode - 0 = clock passthrough, 1 = PRBS-7} -180 -768 0 1 0.25 0.25 {}
T {dig_in[2]  ->  xpat.reset - active high, seeds the PRBS} -180 -748 0 1 0.25 0.25 {}
T {dig_in[1]  ->  xpat.en - gates the pattern clock} -180 -728 0 1 0.25 0.25 {}
T {dig_in[0]  ->  xpat.clk_src - 0 = ref_clk, 1 = pll_clk} -180 -708 0 1 0.25 0.25 {}
T {dig_out[11]  not connected} -180 -688 0 1 0.25 0.25 {}
T {dig_out[10]  not connected} -180 -668 0 1 0.25 0.25 {}
T {dig_out[9]  not connected} -180 -648 0 1 0.25 0.25 {}
T {dig_out[8]  not connected} -180 -628 0 1 0.25 0.25 {}
T {dig_out[7]  not connected} -180 -608 0 1 0.25 0.25 {}
T {dig_out[6]  not connected} -180 -588 0 1 0.25 0.25 {}
T {dig_out[5]  not connected} -180 -568 0 1 0.25 0.25 {}
T {dig_out[4]  not connected} -180 -548 0 1 0.25 0.25 {}
T {dig_out[3]  not connected} -180 -528 0 1 0.25 0.25 {}
T {dig_out[2]  not connected} -180 -508 0 1 0.25 0.25 {}
T {dig_out[1]  not connected} -180 -488 0 1 0.25 0.25 {}
T {dig_out[0]  not connected} -180 -468 0 1 0.25 0.25 {}
T {ibias[1]  ->  xlvds.Iref_drv - 2 uA, mirrored 1:15 to the driver's 30 uA} -180 -448 0 1 0.25 0.25 {}
T {ibias[0]  ->  xlvds.Iref_pd - 2 uA, mirrored 1:15 to the pre-driver's 30 uA} -180 -428 0 1 0.25 0.25 {}
T {vbias  not connected} -180 -408 0 1 0.25 0.25 {}
T {analog_bus[3]  not connected} -180 -388 0 1 0.25 0.25 {}
T {analog_bus[2]  not connected} -180 -368 0 1 0.25 0.25 {}
T {analog_bus[1]  ->  xlvds.Vref - 1.2 V common-mode reference} -180 -348 0 1 0.25 0.25 {}
T {analog_bus[0]  ->  xpll.IREF - 2 uA charge-pump reference} -180 -328 0 1 0.25 0.25 {}
N 1760 -900 1800 -900 {lab=vdd_1v2}
N 1760 -880 1800 -880 {lab=vss_1v2}
N 1460 -1040 1500 -1040 {lab=dig_in[0]}
N 1460 -1020 1500 -1020 {lab=dig_in[1]}
N 1460 -980 1500 -980 {lab=dig_in[3]}
N 1460 -1000 1500 -1000 {lab=dig_in[2]}
N 1850 -1020 1890 -1020 {lab=ibias[1]}
N 1850 -1040 1890 -1040 {lab=ibias[0]}
N 2190 -1040 2270 -1040 {lab=analog_pin[3]}
N 2190 -1060 2270 -1060 {lab=analog_pin[2]}
N 2190 -970 2230 -970 {lab=vdd_3v3}
N 1850 -1000 1890 -1000 {lab=analog_bus[1]}
N 2190 -950 2230 -950 {lab=vss_3v3}
N 2920 -840 2960 -840 {lab=vss_1v2}
N 2920 -810 2960 -810 {lab=vss_1v2}
N 2840 -840 2880 -840 {lab=vdd_1v2}
N 2920 -870 2960 -870 {lab=vss_1v2}
N 2920 -730 2960 -730 {lab=vss_3v3}
N 2920 -700 2960 -700 {lab=vss_3v3}
N 2840 -730 2880 -730 {lab=vdd_3v3}
N 2920 -760 2960 -760 {lab=vss_3v3}
N 0 -1300 40 -1300 {lab=vdd_3v3}
N 0 -1280 40 -1280 {lab=vdd_1v2}
N 0 -1260 40 -1260 {lab=vss_3v3}
N 0 -1240 40 -1240 {lab=vss_1v2}
N 0 -1220 40 -1220 {lab=vssio}
N 0 -1200 40 -1200 {lab=enable}
N 0 -1180 40 -1180 {lab=clk}
N 0 -1160 40 -1160 {lab=dig_in[23]}
N 0 -1140 40 -1140 {lab=dig_in[22]}
N 0 -1120 40 -1120 {lab=dig_in[21]}
N 0 -1100 40 -1100 {lab=dig_in[20]}
N 0 -1080 40 -1080 {lab=dig_in[19]}
N 0 -1060 40 -1060 {lab=dig_in[18]}
N 0 -1040 40 -1040 {lab=dig_in[17]}
N 0 -1020 40 -1020 {lab=dig_in[16]}
N 0 -1000 40 -1000 {lab=dig_in[15]}
N 0 -980 40 -980 {lab=dig_in[14]}
N 0 -960 40 -960 {lab=dig_in[13]}
N 0 -940 40 -940 {lab=dig_in[12]}
N 0 -920 40 -920 {lab=dig_in[11]}
N 0 -900 40 -900 {lab=dig_in[10]}
N 0 -880 40 -880 {lab=dig_in[9]}
N 0 -860 40 -860 {lab=dig_in[8]}
N 0 -840 40 -840 {lab=dig_in[7]}
N 0 -820 40 -820 {lab=dig_in[6]}
N 0 -800 40 -800 {lab=dig_in[5]}
N 0 -780 40 -780 {lab=dig_in[4]}
N 0 -760 40 -760 {lab=dig_in[3]}
N 0 -740 40 -740 {lab=dig_in[2]}
N 0 -720 40 -720 {lab=dig_in[1]}
N 0 -700 40 -700 {lab=dig_in[0]}
N 0 -680 40 -680 {lab=dig_out[11]}
N 0 -660 40 -660 {lab=dig_out[10]}
N 0 -640 40 -640 {lab=dig_out[9]}
N 0 -620 40 -620 {lab=dig_out[8]}
N 0 -600 40 -600 {lab=dig_out[7]}
N 0 -580 40 -580 {lab=dig_out[6]}
N 0 -560 40 -560 {lab=dig_out[5]}
N 0 -540 40 -540 {lab=dig_out[4]}
N 0 -520 40 -520 {lab=dig_out[3]}
N 0 -500 40 -500 {lab=dig_out[2]}
N 0 -480 40 -480 {lab=dig_out[1]}
N 0 -460 40 -460 {lab=dig_out[0]}
N 1000 -720 1120 -720 {lab=analog_pin[0]}
N 0 -440 40 -440 {lab=ibias[1]}
N 0 -420 40 -420 {lab=ibias[0]}
N 0 -400 40 -400 {lab=vbias}
N 0 -380 40 -380 {lab=analog_bus[3]}
N 0 -360 40 -360 {lab=analog_bus[2]}
N 0 -340 40 -340 {lab=analog_bus[1]}
N 0 -320 40 -320 {lab=analog_bus[0]}
N 1760 -1080 1890 -1080 {lab=core_p}
N 1760 -1060 1890 -1060 {lab=core_n}
N 1080 -700 1120 -700 {lab=analog_bus[0]}
N 1080 -680 1120 -680 {lab=dig_in[5]}
N 1080 -660 1120 -660 {lab=dig_in[6]}
N 1080 -640 1120 -640 {lab=dig_in[16:7]}
N 1080 -600 1120 -600 {lab=dig_in[18:17]}
N 1320 -640 2270 -640 {lab=analog_pin[1]}
N 1200 -800 1200 -760 {lab=vdd_1v2}
N 1240 -560 1240 -520 {lab=vss_1v2}
N 1000 -1080 1500 -1080 {lab=analog_pin[0]}
N 1000 -1080 1000 -720 {lab=analog_pin[0]}
N 1340 -1060 1500 -1060 {lab=pll_clk}
N 1340 -1060 1340 -680 {lab=pll_clk}
N 1320 -680 1340 -680 {lab=pll_clk}
N 740 -720 1000 -720 {lab=analog_pin[0]}
C {lab_pin.sym} 1800 -900 0 1 {name=l_xpat_vdd sig_type=std_logic lab=vdd_1v2}
C {lab_pin.sym} 1800 -880 0 1 {name=l_xpat_vss sig_type=std_logic lab=vss_1v2}
C {lab_pin.sym} 1460 -1040 0 0 {name=l_xpat_clk_src sig_type=std_logic lab=dig_in[0]}
C {lab_pin.sym} 1460 -1020 0 0 {name=l_xpat_en sig_type=std_logic lab=dig_in[1]}
C {lab_pin.sym} 1460 -980 0 0 {name=l_xpat_mode sig_type=std_logic lab=dig_in[3]}
C {lab_pin.sym} 1460 -1000 0 0 {name=l_xpat_reset sig_type=std_logic lab=dig_in[2]}
C {lab_wire.sym} 1420 -1060 0 0 {name=p_pll_clk sig_type=std_logic lab=pll_clk}
C {lvds_pattern.sym} 1630 -980 0 0 {name=xpat}
C {lab_pin.sym} 1850 -1020 0 0 {name=l_xlvds_iref_drv sig_type=std_logic lab=ibias[1]}
C {lab_pin.sym} 1850 -1040 0 0 {name=l_xlvds_iref_pd sig_type=std_logic lab=ibias[0]}
C {lab_pin.sym} 2230 -970 0 1 {name=l_xlvds_va sig_type=std_logic lab=vdd_3v3}
C {lab_pin.sym} 1850 -1000 0 0 {name=l_xlvds_vref sig_type=std_logic lab=analog_bus[1]}
C {lab_pin.sym} 2230 -950 0 1 {name=l_xlvds_vss sig_type=std_logic lab=vss_3v3}
C {lvds_tx.sym} 2040 -1030 0 0 {name=xlvds}
C {lab_pin.sym} 2960 -840 0 1 {name=l_Cd12_b sig_type=std_logic lab=vss_1v2}
C {lab_pin.sym} 2960 -810 0 1 {name=l_Cd12_d sig_type=std_logic lab=vss_1v2}
C {lab_pin.sym} 2840 -840 0 0 {name=l_Cd12_g sig_type=std_logic lab=vdd_1v2}
C {lab_pin.sym} 2960 -870 0 1 {name=l_Cd12_s sig_type=std_logic lab=vss_1v2}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 2900 -840 0 0 {name=Cd12
l=10.0u w=10.0u ng=1 m=1 mm_ok=1 model=sg13_lv_pmos spiceprefix=X}
C {lab_pin.sym} 2960 -730 0 1 {name=l_Cd33_b sig_type=std_logic lab=vss_3v3}
C {lab_pin.sym} 2960 -700 0 1 {name=l_Cd33_d sig_type=std_logic lab=vss_3v3}
C {lab_pin.sym} 2840 -730 0 0 {name=l_Cd33_g sig_type=std_logic lab=vdd_3v3}
C {lab_pin.sym} 2960 -760 0 1 {name=l_Cd33_s sig_type=std_logic lab=vss_3v3}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 2900 -730 0 0 {name=Cd33
l=10.0u w=10.0u ng=1 m=1 mm_ok=1 model=sg13_hv_pmos spiceprefix=X}
C {devices/iopin.sym} 0 -1300 2 0 {name=p_vdd_3v3 lab=vdd_3v3}
C {lab_pin.sym} 40 -1300 0 1 {name=lp_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
C {devices/iopin.sym} 0 -1280 2 0 {name=p_vdd_1v2 lab=vdd_1v2}
C {lab_pin.sym} 40 -1280 0 1 {name=lp_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
C {devices/iopin.sym} 0 -1260 2 0 {name=p_vss_3v3 lab=vss_3v3}
C {lab_pin.sym} 40 -1260 0 1 {name=lp_vss_3v3 sig_type=std_logic lab=vss_3v3}
C {devices/iopin.sym} 0 -1240 2 0 {name=p_vss_1v2 lab=vss_1v2}
C {lab_pin.sym} 40 -1240 0 1 {name=lp_vss_1v2 sig_type=std_logic lab=vss_1v2}
C {devices/iopin.sym} 0 -1220 2 0 {name=p_vssio lab=vssio}
C {lab_pin.sym} 40 -1220 0 1 {name=lp_vssio sig_type=std_logic lab=vssio}
C {devices/ipin.sym} 0 -1200 2 1 {name=p_enable lab=enable}
C {lab_pin.sym} 40 -1200 0 1 {name=lp_enable sig_type=std_logic lab=enable}
C {devices/ipin.sym} 0 -1180 2 1 {name=p_clk lab=clk}
C {lab_pin.sym} 40 -1180 0 1 {name=lp_clk sig_type=std_logic lab=clk}
C {devices/ipin.sym} 0 -1160 2 1 {name=p_dig_in_23 lab=dig_in[23]}
C {lab_pin.sym} 40 -1160 0 1 {name=lp_dig_in_23 sig_type=std_logic lab=dig_in[23]}
C {devices/ipin.sym} 0 -1140 2 1 {name=p_dig_in_22 lab=dig_in[22]}
C {lab_pin.sym} 40 -1140 0 1 {name=lp_dig_in_22 sig_type=std_logic lab=dig_in[22]}
C {devices/ipin.sym} 0 -1120 2 1 {name=p_dig_in_21 lab=dig_in[21]}
C {lab_pin.sym} 40 -1120 0 1 {name=lp_dig_in_21 sig_type=std_logic lab=dig_in[21]}
C {devices/ipin.sym} 0 -1100 2 1 {name=p_dig_in_20 lab=dig_in[20]}
C {lab_pin.sym} 40 -1100 0 1 {name=lp_dig_in_20 sig_type=std_logic lab=dig_in[20]}
C {devices/ipin.sym} 0 -1080 2 1 {name=p_dig_in_19 lab=dig_in[19]}
C {lab_pin.sym} 40 -1080 0 1 {name=lp_dig_in_19 sig_type=std_logic lab=dig_in[19]}
C {devices/ipin.sym} 0 -1060 2 1 {name=p_dig_in_18 lab=dig_in[18]}
C {lab_pin.sym} 40 -1060 0 1 {name=lp_dig_in_18 sig_type=std_logic lab=dig_in[18]}
C {devices/ipin.sym} 0 -1040 2 1 {name=p_dig_in_17 lab=dig_in[17]}
C {lab_pin.sym} 40 -1040 0 1 {name=lp_dig_in_17 sig_type=std_logic lab=dig_in[17]}
C {devices/ipin.sym} 0 -1020 2 1 {name=p_dig_in_16 lab=dig_in[16]}
C {lab_pin.sym} 40 -1020 0 1 {name=lp_dig_in_16 sig_type=std_logic lab=dig_in[16]}
C {devices/ipin.sym} 0 -1000 2 1 {name=p_dig_in_15 lab=dig_in[15]}
C {lab_pin.sym} 40 -1000 0 1 {name=lp_dig_in_15 sig_type=std_logic lab=dig_in[15]}
C {devices/ipin.sym} 0 -980 2 1 {name=p_dig_in_14 lab=dig_in[14]}
C {lab_pin.sym} 40 -980 0 1 {name=lp_dig_in_14 sig_type=std_logic lab=dig_in[14]}
C {devices/ipin.sym} 0 -960 2 1 {name=p_dig_in_13 lab=dig_in[13]}
C {lab_pin.sym} 40 -960 0 1 {name=lp_dig_in_13 sig_type=std_logic lab=dig_in[13]}
C {devices/ipin.sym} 0 -940 2 1 {name=p_dig_in_12 lab=dig_in[12]}
C {lab_pin.sym} 40 -940 0 1 {name=lp_dig_in_12 sig_type=std_logic lab=dig_in[12]}
C {devices/ipin.sym} 0 -920 2 1 {name=p_dig_in_11 lab=dig_in[11]}
C {lab_pin.sym} 40 -920 0 1 {name=lp_dig_in_11 sig_type=std_logic lab=dig_in[11]}
C {devices/ipin.sym} 0 -900 2 1 {name=p_dig_in_10 lab=dig_in[10]}
C {lab_pin.sym} 40 -900 0 1 {name=lp_dig_in_10 sig_type=std_logic lab=dig_in[10]}
C {devices/ipin.sym} 0 -880 2 1 {name=p_dig_in_9 lab=dig_in[9]}
C {lab_pin.sym} 40 -880 0 1 {name=lp_dig_in_9 sig_type=std_logic lab=dig_in[9]}
C {devices/ipin.sym} 0 -860 2 1 {name=p_dig_in_8 lab=dig_in[8]}
C {lab_pin.sym} 40 -860 0 1 {name=lp_dig_in_8 sig_type=std_logic lab=dig_in[8]}
C {devices/ipin.sym} 0 -840 2 1 {name=p_dig_in_7 lab=dig_in[7]}
C {lab_pin.sym} 40 -840 0 1 {name=lp_dig_in_7 sig_type=std_logic lab=dig_in[7]}
C {devices/ipin.sym} 0 -820 2 1 {name=p_dig_in_6 lab=dig_in[6]}
C {lab_pin.sym} 40 -820 0 1 {name=lp_dig_in_6 sig_type=std_logic lab=dig_in[6]}
C {devices/ipin.sym} 0 -800 2 1 {name=p_dig_in_5 lab=dig_in[5]}
C {lab_pin.sym} 40 -800 0 1 {name=lp_dig_in_5 sig_type=std_logic lab=dig_in[5]}
C {devices/ipin.sym} 0 -780 2 1 {name=p_dig_in_4 lab=dig_in[4]}
C {lab_pin.sym} 40 -780 0 1 {name=lp_dig_in_4 sig_type=std_logic lab=dig_in[4]}
C {devices/ipin.sym} 0 -760 2 1 {name=p_dig_in_3 lab=dig_in[3]}
C {lab_pin.sym} 40 -760 0 1 {name=lp_dig_in_3 sig_type=std_logic lab=dig_in[3]}
C {devices/ipin.sym} 0 -740 2 1 {name=p_dig_in_2 lab=dig_in[2]}
C {lab_pin.sym} 40 -740 0 1 {name=lp_dig_in_2 sig_type=std_logic lab=dig_in[2]}
C {devices/ipin.sym} 0 -720 2 1 {name=p_dig_in_1 lab=dig_in[1]}
C {lab_pin.sym} 40 -720 0 1 {name=lp_dig_in_1 sig_type=std_logic lab=dig_in[1]}
C {devices/ipin.sym} 0 -700 2 1 {name=p_dig_in_0 lab=dig_in[0]}
C {lab_pin.sym} 40 -700 0 1 {name=lp_dig_in_0 sig_type=std_logic lab=dig_in[0]}
C {devices/opin.sym} 0 -680 2 0 {name=p_dig_out_11 lab=dig_out[11]}
C {lab_pin.sym} 40 -680 0 1 {name=lp_dig_out_11 sig_type=std_logic lab=dig_out[11]}
C {devices/opin.sym} 0 -660 2 0 {name=p_dig_out_10 lab=dig_out[10]}
C {lab_pin.sym} 40 -660 0 1 {name=lp_dig_out_10 sig_type=std_logic lab=dig_out[10]}
C {devices/opin.sym} 0 -640 2 0 {name=p_dig_out_9 lab=dig_out[9]}
C {lab_pin.sym} 40 -640 0 1 {name=lp_dig_out_9 sig_type=std_logic lab=dig_out[9]}
C {devices/opin.sym} 0 -620 2 0 {name=p_dig_out_8 lab=dig_out[8]}
C {lab_pin.sym} 40 -620 0 1 {name=lp_dig_out_8 sig_type=std_logic lab=dig_out[8]}
C {devices/opin.sym} 0 -600 2 0 {name=p_dig_out_7 lab=dig_out[7]}
C {lab_pin.sym} 40 -600 0 1 {name=lp_dig_out_7 sig_type=std_logic lab=dig_out[7]}
C {devices/opin.sym} 0 -580 2 0 {name=p_dig_out_6 lab=dig_out[6]}
C {lab_pin.sym} 40 -580 0 1 {name=lp_dig_out_6 sig_type=std_logic lab=dig_out[6]}
C {devices/opin.sym} 0 -560 2 0 {name=p_dig_out_5 lab=dig_out[5]}
C {lab_pin.sym} 40 -560 0 1 {name=lp_dig_out_5 sig_type=std_logic lab=dig_out[5]}
C {devices/opin.sym} 0 -540 2 0 {name=p_dig_out_4 lab=dig_out[4]}
C {lab_pin.sym} 40 -540 0 1 {name=lp_dig_out_4 sig_type=std_logic lab=dig_out[4]}
C {devices/opin.sym} 0 -520 2 0 {name=p_dig_out_3 lab=dig_out[3]}
C {lab_pin.sym} 40 -520 0 1 {name=lp_dig_out_3 sig_type=std_logic lab=dig_out[3]}
C {devices/opin.sym} 0 -500 2 0 {name=p_dig_out_2 lab=dig_out[2]}
C {lab_pin.sym} 40 -500 0 1 {name=lp_dig_out_2 sig_type=std_logic lab=dig_out[2]}
C {devices/opin.sym} 0 -480 2 0 {name=p_dig_out_1 lab=dig_out[1]}
C {lab_pin.sym} 40 -480 0 1 {name=lp_dig_out_1 sig_type=std_logic lab=dig_out[1]}
C {devices/opin.sym} 0 -460 2 0 {name=p_dig_out_0 lab=dig_out[0]}
C {lab_pin.sym} 40 -460 0 1 {name=lp_dig_out_0 sig_type=std_logic lab=dig_out[0]}
C {devices/iopin.sym} 2270 -1040 0 0 {name=p_analog_pin_3 lab=analog_pin[3]}
C {devices/iopin.sym} 2270 -1060 0 0 {name=p_analog_pin_2 lab=analog_pin[2]}
C {devices/iopin.sym} 2270 -640 2 1 {name=p_analog_pin_1 lab=analog_pin[1]}
C {devices/iopin.sym} 740 -720 2 0 {name=p_analog_pin_0 lab=analog_pin[0]}
C {devices/ipin.sym} 0 -440 2 1 {name=p_ibias_1 lab=ibias[1]}
C {lab_pin.sym} 40 -440 0 1 {name=lp_ibias_1 sig_type=std_logic lab=ibias[1]}
C {devices/ipin.sym} 0 -420 2 1 {name=p_ibias_0 lab=ibias[0]}
C {lab_pin.sym} 40 -420 0 1 {name=lp_ibias_0 sig_type=std_logic lab=ibias[0]}
C {devices/ipin.sym} 0 -400 2 1 {name=p_vbias lab=vbias}
C {lab_pin.sym} 40 -400 0 1 {name=lp_vbias sig_type=std_logic lab=vbias}
C {devices/iopin.sym} 0 -380 2 0 {name=p_analog_bus_3 lab=analog_bus[3]}
C {lab_pin.sym} 40 -380 0 1 {name=lp_analog_bus_3 sig_type=std_logic lab=analog_bus[3]}
C {devices/iopin.sym} 0 -360 2 0 {name=p_analog_bus_2 lab=analog_bus[2]}
C {lab_pin.sym} 40 -360 0 1 {name=lp_analog_bus_2 sig_type=std_logic lab=analog_bus[2]}
C {devices/iopin.sym} 0 -340 2 0 {name=p_analog_bus_1 lab=analog_bus[1]}
C {lab_pin.sym} 40 -340 0 1 {name=lp_analog_bus_1 sig_type=std_logic lab=analog_bus[1]}
C {devices/iopin.sym} 0 -320 2 0 {name=p_analog_bus_0 lab=analog_bus[0]}
C {lab_pin.sym} 40 -320 0 1 {name=lp_analog_bus_0 sig_type=std_logic lab=analog_bus[0]}
C {lab_wire.sym} 1830 -1080 0 0 {name=p1 sig_type=std_logic lab=core_p
}
C {lab_wire.sym} 1830 -1060 0 0 {name=p2 sig_type=std_logic lab=core_n}
C {lab_pin.sym} 1080 -700 0 0 {name=l_xpll_iref sig_type=std_logic lab=analog_bus[0]}
C {lab_pin.sym} 1080 -680 0 0 {name=l_xpll_enable sig_type=std_logic lab=dig_in[5]}
C {lab_pin.sym} 1080 -660 0 0 {name=l_xpll_reset_n sig_type=std_logic lab=dig_in[6]}
C {lab_pin.sym} 1080 -640 0 0 {name=l_xpll_div_ratio90 sig_type=std_logic lab=dig_in[16:7]}
C {lab_pin.sym} 1080 -600 0 0 {name=l_xpll_test_div10 sig_type=std_logic lab=dig_in[18:17]}
C {lab_pin.sym} 1200 -800 1 0 {name=l_xpll_vdd sig_type=std_logic lab=vdd_1v2}
C {lab_pin.sym} 1240 -520 3 0 {name=l_xpll_vss sig_type=std_logic lab=vss_1v2}
C {pll_cosim.sym} 1220 -660 0 0 {name=xpll}
