v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Chipalooza 2026, slot 14 - LVDS transmitter with PRBS-7 generator} 800 -1900 0 0 1 1 {}
T {Port list is the slot-14 frame (slot14_wrapper of
RTimothyEdwards/sg13cmos5l_ocd_chipalooza), pin for pin, so this cell and
layout/slot_14.gds compare by name in LVS.  Slot 14 has three dedicated
analog pads, each an sg13cmos5l_IOPadAnalog with two core terminals:
s14_an[i] is the pad itself (primary clamps only), s14_an_i_esd goes through
its secondary protection (series resistor and diodes), the one for gates.

  s14_an[0]      d_n       LVDS out -   (Out_n is the upper one of the pair)
  s14_an[1]      d_p       LVDS out +
  s14_an_2_esd   ref_clk   reference in, feeds lvds_pattern - a gate input
  s14_an[2]      odt       pad 2 itself: the switchable 50 ohm termination
  s14_an_0_esd, s14_an_1_esd   not connected

Not connected: dig_out[11:0], dig_in[23:4], analog_bus0/2/3, vbias, clk,
enable and reset - the reference arrives on its own pad.  The harness masks
dig_in to zero for an unselected project (proj_dig_in is dig_in ANDed with
select & dig_ena in user_project_control.v), so dig_in[1] alone stops the
pattern clock.} 300 -1820 0 0 0.4 0.4 {}
T {dig_in map.  The housekeeping SPI routes every bit individually to a
pin, a constant or the sequencer, so a configuration bit costs a register
write and no pin.  Unselected holds every dig_in at zero, and all-zero
leaves the clock stopped and the output pair static - a legal idle.

  dig_in[0]     odt        1 = 50 ohm termination of ref_clk on (xodt); 0 = off
  dig_in[1]     en        gates the pattern clock, not the output pair
  dig_in[2]     reset      active high, seeds the PRBS shift register
                           Neither reaches the two output flops: they run on an
                           ungated clock with RESET_B tied high, so D_p and D_n
                           are complementary from the first edge after power-up
                           and the LVDS driver settles once, not at every enable.
  dig_in[3]     mode       0 = clock passthrough, 1 = PRBS-7
  dig_in[23:4]  unused

The PLL that clocked lvds_pattern through pll_clk left the project on
2026-10-07, and the pattern's clock source select (pll_clk, clk_src) with
it; the PLL goes on as a project of its own.} 300 -1400 0 0 0.4 0.4 {}
T {Two supply domains, one ground.  core_p / core_n cross from vss_1v2 into
the pre-driver on vss_3v3.  The harness ties the two grounds
(chipalooza_frame.v: assign vss3v3 = vss1v2), and every tap of either sits in
the same substrate, so the layout extraction merges them as well; the LVS
joins them in this schematic too (scripts/verify/check_lvs.sh).

The output pads carry the primary clamps only: a series resistor in an
LVDS output would eat the swing.} 1450 -560 0 0 0.35 0.35 {}
T {Decoupling Capacitors} 2860 -990 0 0 0.25 0.25 {}
T {DRST: antenna diode
on the long reset line} 1180 -860 0 0 0.25 0.25 {}
N 1760 -1060 1800 -1060 {lab=core_n}
C {lab_pin.sym} 1800 -1060 0 1 {name=l_xpat_d_n sig_type=std_logic lab=core_n}
N 1760 -1080 1800 -1080 {lab=core_p}
C {lab_pin.sym} 1800 -1080 0 1 {name=l_xpat_d_p sig_type=std_logic lab=core_p}
N 1760 -900 1800 -900 {lab=vdd_1v2}
C {lab_pin.sym} 1800 -900 0 1 {name=l_xpat_vdd sig_type=std_logic lab=vdd_1v2}
N 1760 -880 1800 -880 {lab=vss_1v2}
C {lab_pin.sym} 1800 -880 0 1 {name=l_xpat_vss sig_type=std_logic lab=vss_1v2}
N 1460 -1020 1500 -1020 {lab=dig_in[1]}
C {lab_pin.sym} 1460 -1020 0 0 {name=l_xpat_en sig_type=std_logic lab=dig_in[1]}
N 1460 -980 1500 -980 {lab=dig_in[3]}
C {lab_pin.sym} 1460 -980 0 0 {name=l_xpat_mode sig_type=std_logic lab=dig_in[3]}
N 1460 -1080 1500 -1080 {lab=s14_an_2_esd}
C {lab_pin.sym} 1460 -1080 0 0 {name=l_xpat_ref_clk sig_type=std_logic lab=s14_an_2_esd}
N 1460 -1000 1500 -1000 {lab=dig_in[2]}
C {lab_pin.sym} 1460 -1000 0 0 {name=l_xpat_reset sig_type=std_logic lab=dig_in[2]}
C {lvds_pattern.sym} 1630 -980 0 0 {name=xpat}
N 1850 -1060 1890 -1060 {lab=core_n}
C {lab_pin.sym} 1850 -1060 0 0 {name=l_xlvds_d_n sig_type=std_logic lab=core_n}
N 1850 -1080 1890 -1080 {lab=core_p}
C {lab_pin.sym} 1850 -1080 0 0 {name=l_xlvds_d_p sig_type=std_logic lab=core_p}
N 1850 -1020 1890 -1020 {lab=iref_drv_30u}
C {lab_pin.sym} 1850 -1020 0 0 {name=l_xlvds_iref_drv sig_type=std_logic lab=iref_drv_30u}
N 1850 -1040 1890 -1040 {lab=iref_pd_30u}
C {lab_pin.sym} 1850 -1040 0 0 {name=l_xlvds_iref_pd sig_type=std_logic lab=iref_pd_30u}
N 2190 -1040 2230 -1040 {lab=s14_an[0]}
C {lab_pin.sym} 2230 -1040 0 1 {name=l_xlvds_out_n sig_type=std_logic lab=s14_an[0]}
N 2190 -1060 2230 -1060 {lab=s14_an[1]}
C {lab_pin.sym} 2230 -1060 0 1 {name=l_xlvds_out_p sig_type=std_logic lab=s14_an[1]}
N 2190 -970 2230 -970 {lab=vdd_3v3}
C {lab_pin.sym} 2230 -970 0 1 {name=l_xlvds_va sig_type=std_logic lab=vdd_3v3}
N 1850 -1000 1890 -1000 {lab=analog_bus1}
C {lab_pin.sym} 1850 -1000 0 0 {name=l_xlvds_vref sig_type=std_logic lab=analog_bus1}
N 2190 -950 2230 -950 {lab=vss_3v3}
C {lab_pin.sym} 2230 -950 0 1 {name=l_xlvds_vss sig_type=std_logic lab=vss_3v3}
C {lvds_tx.sym} 2040 -1030 0 0 {name=xlvds}
N 1780 -800 1820 -800 {lab=ibias0}
C {lab_pin.sym} 1780 -800 0 0 {name=l_xiref_pd_iref_in sig_type=std_logic lab=ibias0}
N 1980 -800 2020 -800 {lab=iref_pd_30u}
C {lab_pin.sym} 2020 -800 0 1 {name=l_xiref_pd_iref_out sig_type=std_logic lab=iref_pd_30u}
N 1880 -920 1880 -880 {lab=vdd_3v3}
C {lab_pin.sym} 1880 -920 1 0 {name=l_xiref_pd_va sig_type=std_logic lab=vdd_3v3}
N 1920 -720 1920 -680 {lab=vss_3v3}
C {lab_pin.sym} 1920 -680 3 0 {name=l_xiref_pd_vss sig_type=std_logic lab=vss_3v3}
C {iref_x15.sym} 1900 -800 0 0 {name=xiref_pd}
N 2130 -800 2170 -800 {lab=ibias1}
C {lab_pin.sym} 2130 -800 0 0 {name=l_xiref_drv_iref_in sig_type=std_logic lab=ibias1}
N 2330 -800 2370 -800 {lab=iref_drv_30u}
C {lab_pin.sym} 2370 -800 0 1 {name=l_xiref_drv_iref_out sig_type=std_logic lab=iref_drv_30u}
N 2230 -920 2230 -880 {lab=vdd_3v3}
C {lab_pin.sym} 2230 -920 1 0 {name=l_xiref_drv_va sig_type=std_logic lab=vdd_3v3}
N 2270 -720 2270 -680 {lab=vss_3v3}
C {lab_pin.sym} 2270 -680 3 0 {name=l_xiref_drv_vss sig_type=std_logic lab=vss_3v3}
C {iref_x15.sym} 2250 -800 0 0 {name=xiref_drv}
N 1470 -1290 1510 -1290 {lab=dig_in[0]}
C {lab_pin.sym} 1470 -1290 0 0 {name=l_xodt_en sig_type=std_logic lab=dig_in[0]}
N 1470 -1250 1510 -1250 {lab=s14_an[2]}
C {lab_pin.sym} 1470 -1250 0 0 {name=l_xodt_pad sig_type=std_logic lab=s14_an[2]}
N 1750 -1290 1790 -1290 {lab=vdd_1v2}
C {lab_pin.sym} 1790 -1290 0 1 {name=l_xodt_vdd sig_type=std_logic lab=vdd_1v2}
N 1750 -1250 1790 -1250 {lab=vdd_3v3}
C {lab_pin.sym} 1790 -1250 0 1 {name=l_xodt_vddh sig_type=std_logic lab=vdd_3v3}
N 1750 -1210 1790 -1210 {lab=vss_3v3}
C {lab_pin.sym} 1790 -1210 0 1 {name=l_xodt_vss sig_type=std_logic lab=vss_3v3}
C {ref_odt.sym} 1630 -1250 0 0 {name=xodt}
N 1300 -930 1300 -890 {lab=vss_1v2}
C {lab_pin.sym} 1300 -890 3 0 {name=l_DRST_d0 sig_type=std_logic lab=vss_1v2}
N 1300 -1030 1300 -990 {lab=dig_in[2]}
C {lab_pin.sym} 1300 -1030 1 0 {name=l_DRST_d1 sig_type=std_logic lab=dig_in[2]}
C {sg13cmos5l_pr/dantenna.sym} 1300 -960 0 0 {name=DRST
model=dantenna l=0.78u w=0.78u spiceprefix=X}
C {sg13cmos5l_stdcells/sg13cmos5l_decap_8.sym} 2900 -840 0 0 {name=xdc12[82:0]
VDD=vdd_1v2 VSS=vss_1v2 prefix=sg13cmos5l_}
C {sg13g2_hv_decap_8.sym} 2900 -730 0 0 {name=xdc33[94:0]
VDD=vdd_3v3 VSS=vss_3v3 prefix=sg13g2_hv_}
N 0 -1300 40 -1300 {lab=vdd_3v3}
C {devices/iopin.sym} 0 -1300 2 0 {name=p_vdd_3v3 lab=vdd_3v3}
C {lab_pin.sym} 40 -1300 0 1 {name=lp_vdd_3v3 sig_type=std_logic lab=vdd_3v3}
T {vdd_3v3  ->  xlvds.Va, xiref_pd.Va, xiref_drv.Va, xdc33 decap row} -180 -1308 0 1 0.25 0.25 {}
N 0 -1280 40 -1280 {lab=vdd_1v2}
C {devices/iopin.sym} 0 -1280 2 0 {name=p_vdd_1v2 lab=vdd_1v2}
C {lab_pin.sym} 40 -1280 0 1 {name=lp_vdd_1v2 sig_type=std_logic lab=vdd_1v2}
T {vdd_1v2  ->  xpat.VDD, xdc12 decap row} -180 -1288 0 1 0.25 0.25 {}
N 0 -1260 40 -1260 {lab=vss_3v3}
C {devices/iopin.sym} 0 -1260 2 0 {name=p_vss_3v3 lab=vss_3v3}
C {lab_pin.sym} 40 -1260 0 1 {name=lp_vss_3v3 sig_type=std_logic lab=vss_3v3}
T {vss_3v3  ->  xlvds.Vss, xiref_pd.Vss, xiref_drv.Vss, xdc33 decap row} -180 -1268 0 1 0.25 0.25 {}
N 0 -1240 40 -1240 {lab=vss_1v2}
C {devices/iopin.sym} 0 -1240 2 0 {name=p_vss_1v2 lab=vss_1v2}
C {lab_pin.sym} 40 -1240 0 1 {name=lp_vss_1v2 sig_type=std_logic lab=vss_1v2}
T {vss_1v2  ->  xpat.VSS, xdc12 decap row} -180 -1248 0 1 0.25 0.25 {}
N 0 -1220 40 -1220 {lab=enable}
C {devices/ipin.sym} 0 -1220 2 1 {name=p_enable lab=enable}
C {lab_pin.sym} 40 -1220 0 1 {name=lp_enable sig_type=std_logic lab=enable}
T {enable  not connected} -180 -1228 0 1 0.25 0.25 {}
N 0 -1200 40 -1200 {lab=clk}
C {devices/ipin.sym} 0 -1200 2 1 {name=p_clk lab=clk}
C {lab_pin.sym} 40 -1200 0 1 {name=lp_clk sig_type=std_logic lab=clk}
T {clk  not connected - the reference comes in on s14_an_2_esd} -180 -1208 0 1 0.25 0.25 {}
N 0 -1180 40 -1180 {lab=reset}
C {devices/ipin.sym} 0 -1180 2 1 {name=p_reset lab=reset}
C {lab_pin.sym} 40 -1180 0 1 {name=lp_reset sig_type=std_logic lab=reset}
T {reset  not connected - the PRBS reset is dig_in[2]} -180 -1188 0 1 0.25 0.25 {}
N 0 -1160 40 -1160 {lab=dig_in[23]}
C {devices/ipin.sym} 0 -1160 2 1 {name=p_dig_in_23 lab=dig_in[23]}
C {lab_pin.sym} 40 -1160 0 1 {name=lp_dig_in_23 sig_type=std_logic lab=dig_in[23]}
T {dig_in[23]  not connected} -180 -1168 0 1 0.25 0.25 {}
N 0 -1140 40 -1140 {lab=dig_in[22]}
C {devices/ipin.sym} 0 -1140 2 1 {name=p_dig_in_22 lab=dig_in[22]}
C {lab_pin.sym} 40 -1140 0 1 {name=lp_dig_in_22 sig_type=std_logic lab=dig_in[22]}
T {dig_in[22]  not connected} -180 -1148 0 1 0.25 0.25 {}
N 0 -1120 40 -1120 {lab=dig_in[21]}
C {devices/ipin.sym} 0 -1120 2 1 {name=p_dig_in_21 lab=dig_in[21]}
C {lab_pin.sym} 40 -1120 0 1 {name=lp_dig_in_21 sig_type=std_logic lab=dig_in[21]}
T {dig_in[21]  not connected} -180 -1128 0 1 0.25 0.25 {}
N 0 -1100 40 -1100 {lab=dig_in[20]}
C {devices/ipin.sym} 0 -1100 2 1 {name=p_dig_in_20 lab=dig_in[20]}
C {lab_pin.sym} 40 -1100 0 1 {name=lp_dig_in_20 sig_type=std_logic lab=dig_in[20]}
T {dig_in[20]  not connected} -180 -1108 0 1 0.25 0.25 {}
N 0 -1080 40 -1080 {lab=dig_in[19]}
C {devices/ipin.sym} 0 -1080 2 1 {name=p_dig_in_19 lab=dig_in[19]}
C {lab_pin.sym} 40 -1080 0 1 {name=lp_dig_in_19 sig_type=std_logic lab=dig_in[19]}
T {dig_in[19]  not connected} -180 -1088 0 1 0.25 0.25 {}
N 0 -1060 40 -1060 {lab=dig_in[18]}
C {devices/ipin.sym} 0 -1060 2 1 {name=p_dig_in_18 lab=dig_in[18]}
C {lab_pin.sym} 40 -1060 0 1 {name=lp_dig_in_18 sig_type=std_logic lab=dig_in[18]}
T {dig_in[18]  not connected} -180 -1068 0 1 0.25 0.25 {}
N 0 -1040 40 -1040 {lab=dig_in[17]}
C {devices/ipin.sym} 0 -1040 2 1 {name=p_dig_in_17 lab=dig_in[17]}
C {lab_pin.sym} 40 -1040 0 1 {name=lp_dig_in_17 sig_type=std_logic lab=dig_in[17]}
T {dig_in[17]  not connected} -180 -1048 0 1 0.25 0.25 {}
N 0 -1020 40 -1020 {lab=dig_in[16]}
C {devices/ipin.sym} 0 -1020 2 1 {name=p_dig_in_16 lab=dig_in[16]}
C {lab_pin.sym} 40 -1020 0 1 {name=lp_dig_in_16 sig_type=std_logic lab=dig_in[16]}
T {dig_in[16]  not connected} -180 -1028 0 1 0.25 0.25 {}
N 0 -1000 40 -1000 {lab=dig_in[15]}
C {devices/ipin.sym} 0 -1000 2 1 {name=p_dig_in_15 lab=dig_in[15]}
C {lab_pin.sym} 40 -1000 0 1 {name=lp_dig_in_15 sig_type=std_logic lab=dig_in[15]}
T {dig_in[15]  not connected} -180 -1008 0 1 0.25 0.25 {}
N 0 -980 40 -980 {lab=dig_in[14]}
C {devices/ipin.sym} 0 -980 2 1 {name=p_dig_in_14 lab=dig_in[14]}
C {lab_pin.sym} 40 -980 0 1 {name=lp_dig_in_14 sig_type=std_logic lab=dig_in[14]}
T {dig_in[14]  not connected} -180 -988 0 1 0.25 0.25 {}
N 0 -960 40 -960 {lab=dig_in[13]}
C {devices/ipin.sym} 0 -960 2 1 {name=p_dig_in_13 lab=dig_in[13]}
C {lab_pin.sym} 40 -960 0 1 {name=lp_dig_in_13 sig_type=std_logic lab=dig_in[13]}
T {dig_in[13]  not connected} -180 -968 0 1 0.25 0.25 {}
N 0 -940 40 -940 {lab=dig_in[12]}
C {devices/ipin.sym} 0 -940 2 1 {name=p_dig_in_12 lab=dig_in[12]}
C {lab_pin.sym} 40 -940 0 1 {name=lp_dig_in_12 sig_type=std_logic lab=dig_in[12]}
T {dig_in[12]  not connected} -180 -948 0 1 0.25 0.25 {}
N 0 -920 40 -920 {lab=dig_in[11]}
C {devices/ipin.sym} 0 -920 2 1 {name=p_dig_in_11 lab=dig_in[11]}
C {lab_pin.sym} 40 -920 0 1 {name=lp_dig_in_11 sig_type=std_logic lab=dig_in[11]}
T {dig_in[11]  not connected} -180 -928 0 1 0.25 0.25 {}
N 0 -900 40 -900 {lab=dig_in[10]}
C {devices/ipin.sym} 0 -900 2 1 {name=p_dig_in_10 lab=dig_in[10]}
C {lab_pin.sym} 40 -900 0 1 {name=lp_dig_in_10 sig_type=std_logic lab=dig_in[10]}
T {dig_in[10]  not connected} -180 -908 0 1 0.25 0.25 {}
N 0 -880 40 -880 {lab=dig_in[9]}
C {devices/ipin.sym} 0 -880 2 1 {name=p_dig_in_9 lab=dig_in[9]}
C {lab_pin.sym} 40 -880 0 1 {name=lp_dig_in_9 sig_type=std_logic lab=dig_in[9]}
T {dig_in[9]  not connected} -180 -888 0 1 0.25 0.25 {}
N 0 -860 40 -860 {lab=dig_in[8]}
C {devices/ipin.sym} 0 -860 2 1 {name=p_dig_in_8 lab=dig_in[8]}
C {lab_pin.sym} 40 -860 0 1 {name=lp_dig_in_8 sig_type=std_logic lab=dig_in[8]}
T {dig_in[8]  not connected} -180 -868 0 1 0.25 0.25 {}
N 0 -840 40 -840 {lab=dig_in[7]}
C {devices/ipin.sym} 0 -840 2 1 {name=p_dig_in_7 lab=dig_in[7]}
C {lab_pin.sym} 40 -840 0 1 {name=lp_dig_in_7 sig_type=std_logic lab=dig_in[7]}
T {dig_in[7]  not connected} -180 -848 0 1 0.25 0.25 {}
N 0 -820 40 -820 {lab=dig_in[6]}
C {devices/ipin.sym} 0 -820 2 1 {name=p_dig_in_6 lab=dig_in[6]}
C {lab_pin.sym} 40 -820 0 1 {name=lp_dig_in_6 sig_type=std_logic lab=dig_in[6]}
T {dig_in[6]  not connected} -180 -828 0 1 0.25 0.25 {}
N 0 -800 40 -800 {lab=dig_in[5]}
C {devices/ipin.sym} 0 -800 2 1 {name=p_dig_in_5 lab=dig_in[5]}
C {lab_pin.sym} 40 -800 0 1 {name=lp_dig_in_5 sig_type=std_logic lab=dig_in[5]}
T {dig_in[5]  not connected} -180 -808 0 1 0.25 0.25 {}
N 0 -780 40 -780 {lab=dig_in[4]}
C {devices/ipin.sym} 0 -780 2 1 {name=p_dig_in_4 lab=dig_in[4]}
C {lab_pin.sym} 40 -780 0 1 {name=lp_dig_in_4 sig_type=std_logic lab=dig_in[4]}
T {dig_in[4]  not connected} -180 -788 0 1 0.25 0.25 {}
N 0 -760 40 -760 {lab=dig_in[3]}
C {devices/ipin.sym} 0 -760 2 1 {name=p_dig_in_3 lab=dig_in[3]}
C {lab_pin.sym} 40 -760 0 1 {name=lp_dig_in_3 sig_type=std_logic lab=dig_in[3]}
T {dig_in[3]  ->  xpat.mode - 0 = clock passthrough, 1 = PRBS-7} -180 -768 0 1 0.25 0.25 {}
N 0 -740 40 -740 {lab=dig_in[2]}
C {devices/ipin.sym} 0 -740 2 1 {name=p_dig_in_2 lab=dig_in[2]}
C {lab_pin.sym} 40 -740 0 1 {name=lp_dig_in_2 sig_type=std_logic lab=dig_in[2]}
T {dig_in[2]  ->  xpat.reset - active high, seeds the PRBS shift register; DRST antenna diode} -180 -748 0 1 0.25 0.25 {}
N 0 -720 40 -720 {lab=dig_in[1]}
C {devices/ipin.sym} 0 -720 2 1 {name=p_dig_in_1 lab=dig_in[1]}
C {lab_pin.sym} 40 -720 0 1 {name=lp_dig_in_1 sig_type=std_logic lab=dig_in[1]}
T {dig_in[1]  ->  xpat.en - gates the pattern clock, not the output pair} -180 -728 0 1 0.25 0.25 {}
N 0 -700 40 -700 {lab=dig_in[0]}
C {devices/ipin.sym} 0 -700 2 1 {name=p_dig_in_0 lab=dig_in[0]}
C {lab_pin.sym} 40 -700 0 1 {name=lp_dig_in_0 sig_type=std_logic lab=dig_in[0]}
T {dig_in[0]  ->  xodt.EN - 1 = 50 ohm termination of ref_clk on} -180 -708 0 1 0.25 0.25 {}
N 0 -680 40 -680 {lab=ibias0}
C {devices/ipin.sym} 0 -680 2 1 {name=p_ibias0 lab=ibias0}
C {lab_pin.sym} 40 -680 0 1 {name=lp_ibias0 sig_type=std_logic lab=ibias0}
T {ibias0  ->  xiref_pd (1:15) -> xlvds.Iref_pd - 2 uA in, 30 uA out} -180 -688 0 1 0.25 0.25 {}
N 0 -660 40 -660 {lab=ibias1}
C {devices/ipin.sym} 0 -660 2 1 {name=p_ibias1 lab=ibias1}
C {lab_pin.sym} 40 -660 0 1 {name=lp_ibias1 sig_type=std_logic lab=ibias1}
T {ibias1  ->  xiref_drv (1:15) -> xlvds.Iref_drv - 2 uA in, 30 uA out} -180 -668 0 1 0.25 0.25 {}
N 0 -640 40 -640 {lab=vbias}
C {devices/ipin.sym} 0 -640 2 1 {name=p_vbias lab=vbias}
C {lab_pin.sym} 40 -640 0 1 {name=lp_vbias sig_type=std_logic lab=vbias}
T {vbias  not connected} -180 -648 0 1 0.25 0.25 {}
N 0 -620 40 -620 {lab=dig_out[11]}
C {devices/opin.sym} 0 -620 2 0 {name=p_dig_out_11 lab=dig_out[11]}
C {lab_pin.sym} 40 -620 0 1 {name=lp_dig_out_11 sig_type=std_logic lab=dig_out[11]}
T {dig_out[11]  not connected} -180 -628 0 1 0.25 0.25 {}
N 0 -600 40 -600 {lab=dig_out[10]}
C {devices/opin.sym} 0 -600 2 0 {name=p_dig_out_10 lab=dig_out[10]}
C {lab_pin.sym} 40 -600 0 1 {name=lp_dig_out_10 sig_type=std_logic lab=dig_out[10]}
T {dig_out[10]  not connected} -180 -608 0 1 0.25 0.25 {}
N 0 -580 40 -580 {lab=dig_out[9]}
C {devices/opin.sym} 0 -580 2 0 {name=p_dig_out_9 lab=dig_out[9]}
C {lab_pin.sym} 40 -580 0 1 {name=lp_dig_out_9 sig_type=std_logic lab=dig_out[9]}
T {dig_out[9]  not connected} -180 -588 0 1 0.25 0.25 {}
N 0 -560 40 -560 {lab=dig_out[8]}
C {devices/opin.sym} 0 -560 2 0 {name=p_dig_out_8 lab=dig_out[8]}
C {lab_pin.sym} 40 -560 0 1 {name=lp_dig_out_8 sig_type=std_logic lab=dig_out[8]}
T {dig_out[8]  not connected} -180 -568 0 1 0.25 0.25 {}
N 0 -540 40 -540 {lab=dig_out[7]}
C {devices/opin.sym} 0 -540 2 0 {name=p_dig_out_7 lab=dig_out[7]}
C {lab_pin.sym} 40 -540 0 1 {name=lp_dig_out_7 sig_type=std_logic lab=dig_out[7]}
T {dig_out[7]  not connected} -180 -548 0 1 0.25 0.25 {}
N 0 -520 40 -520 {lab=dig_out[6]}
C {devices/opin.sym} 0 -520 2 0 {name=p_dig_out_6 lab=dig_out[6]}
C {lab_pin.sym} 40 -520 0 1 {name=lp_dig_out_6 sig_type=std_logic lab=dig_out[6]}
T {dig_out[6]  not connected} -180 -528 0 1 0.25 0.25 {}
N 0 -500 40 -500 {lab=dig_out[5]}
C {devices/opin.sym} 0 -500 2 0 {name=p_dig_out_5 lab=dig_out[5]}
C {lab_pin.sym} 40 -500 0 1 {name=lp_dig_out_5 sig_type=std_logic lab=dig_out[5]}
T {dig_out[5]  not connected} -180 -508 0 1 0.25 0.25 {}
N 0 -480 40 -480 {lab=dig_out[4]}
C {devices/opin.sym} 0 -480 2 0 {name=p_dig_out_4 lab=dig_out[4]}
C {lab_pin.sym} 40 -480 0 1 {name=lp_dig_out_4 sig_type=std_logic lab=dig_out[4]}
T {dig_out[4]  not connected} -180 -488 0 1 0.25 0.25 {}
N 0 -460 40 -460 {lab=dig_out[3]}
C {devices/opin.sym} 0 -460 2 0 {name=p_dig_out_3 lab=dig_out[3]}
C {lab_pin.sym} 40 -460 0 1 {name=lp_dig_out_3 sig_type=std_logic lab=dig_out[3]}
T {dig_out[3]  not connected} -180 -468 0 1 0.25 0.25 {}
N 0 -440 40 -440 {lab=dig_out[2]}
C {devices/opin.sym} 0 -440 2 0 {name=p_dig_out_2 lab=dig_out[2]}
C {lab_pin.sym} 40 -440 0 1 {name=lp_dig_out_2 sig_type=std_logic lab=dig_out[2]}
T {dig_out[2]  not connected} -180 -448 0 1 0.25 0.25 {}
N 0 -420 40 -420 {lab=dig_out[1]}
C {devices/opin.sym} 0 -420 2 0 {name=p_dig_out_1 lab=dig_out[1]}
C {lab_pin.sym} 40 -420 0 1 {name=lp_dig_out_1 sig_type=std_logic lab=dig_out[1]}
T {dig_out[1]  not connected} -180 -428 0 1 0.25 0.25 {}
N 0 -400 40 -400 {lab=dig_out[0]}
C {devices/opin.sym} 0 -400 2 0 {name=p_dig_out_0 lab=dig_out[0]}
C {lab_pin.sym} 40 -400 0 1 {name=lp_dig_out_0 sig_type=std_logic lab=dig_out[0]}
T {dig_out[0]  not connected} -180 -408 0 1 0.25 0.25 {}
N 0 -380 40 -380 {lab=s14_an[2]}
C {devices/iopin.sym} 0 -380 2 0 {name=p_s14_an_2 lab=s14_an[2]}
C {lab_pin.sym} 40 -380 0 1 {name=lp_s14_an_2 sig_type=std_logic lab=s14_an[2]}
T {ref_clk termination - pad 2 direct} 100 -388 0 0 0.25 0.25 {}
T {s14_an[2]  ->  xodt.PAD - the termination, on pad 2 itself} -180 -388 0 1 0.25 0.25 {}
N 0 -360 40 -360 {lab=s14_an[1]}
C {devices/iopin.sym} 0 -360 2 0 {name=p_s14_an_1 lab=s14_an[1]}
C {lab_pin.sym} 40 -360 0 1 {name=lp_s14_an_1 sig_type=std_logic lab=s14_an[1]}
T {LVDS out +, pad 1 direct} 100 -368 0 0 0.25 0.25 {}
T {s14_an[1]  ->  xlvds.Out_p} -180 -368 0 1 0.25 0.25 {}
N 0 -340 40 -340 {lab=s14_an[0]}
C {devices/iopin.sym} 0 -340 2 0 {name=p_s14_an_0 lab=s14_an[0]}
C {lab_pin.sym} 40 -340 0 1 {name=lp_s14_an_0 sig_type=std_logic lab=s14_an[0]}
T {LVDS out -, pad 0 direct} 100 -348 0 0 0.25 0.25 {}
T {s14_an[0]  ->  xlvds.Out_n} -180 -348 0 1 0.25 0.25 {}
N 0 -320 40 -320 {lab=s14_an_2_esd}
C {devices/iopin.sym} 0 -320 2 0 {name=p_s14_an_2_esd lab=s14_an_2_esd}
C {lab_pin.sym} 40 -320 0 1 {name=lp_s14_an_2_esd sig_type=std_logic lab=s14_an_2_esd}
T {ref_clk in - pad 2 through its secondary protection} 100 -328 0 0 0.25 0.25 {}
T {s14_an_2_esd  ->  xpat.ref_clk} -180 -328 0 1 0.25 0.25 {}
N 0 -300 40 -300 {lab=s14_an_1_esd}
C {devices/iopin.sym} 0 -300 2 0 {name=p_s14_an_1_esd lab=s14_an_1_esd}
C {lab_pin.sym} 40 -300 0 1 {name=lp_s14_an_1_esd sig_type=std_logic lab=s14_an_1_esd}
T {s14_an_1_esd  not connected} -180 -308 0 1 0.25 0.25 {}
N 0 -280 40 -280 {lab=s14_an_0_esd}
C {devices/iopin.sym} 0 -280 2 0 {name=p_s14_an_0_esd lab=s14_an_0_esd}
C {lab_pin.sym} 40 -280 0 1 {name=lp_s14_an_0_esd sig_type=std_logic lab=s14_an_0_esd}
T {s14_an_0_esd  not connected} -180 -288 0 1 0.25 0.25 {}
N 0 -260 40 -260 {lab=analog_bus0}
C {devices/iopin.sym} 0 -260 2 0 {name=p_analog_bus0 lab=analog_bus0}
C {lab_pin.sym} 40 -260 0 1 {name=lp_analog_bus0 sig_type=std_logic lab=analog_bus0}
T {analog_bus0  not connected} -180 -268 0 1 0.25 0.25 {}
N 0 -240 40 -240 {lab=analog_bus1}
C {devices/iopin.sym} 0 -240 2 0 {name=p_analog_bus1 lab=analog_bus1}
C {lab_pin.sym} 40 -240 0 1 {name=lp_analog_bus1 sig_type=std_logic lab=analog_bus1}
T {analog_bus1  ->  xlvds.Vref - 1.2 V common-mode reference} -180 -248 0 1 0.25 0.25 {}
N 0 -220 40 -220 {lab=analog_bus2}
C {devices/iopin.sym} 0 -220 2 0 {name=p_analog_bus2 lab=analog_bus2}
C {lab_pin.sym} 40 -220 0 1 {name=lp_analog_bus2 sig_type=std_logic lab=analog_bus2}
T {analog_bus2  not connected} -180 -228 0 1 0.25 0.25 {}
N 0 -200 40 -200 {lab=analog_bus3}
C {devices/iopin.sym} 0 -200 2 0 {name=p_analog_bus3 lab=analog_bus3}
C {lab_pin.sym} 40 -200 0 1 {name=lp_analog_bus3 sig_type=std_logic lab=analog_bus3}
T {analog_bus3  not connected} -180 -208 0 1 0.25 0.25 {}
