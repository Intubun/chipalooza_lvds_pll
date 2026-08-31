v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {lvds_pattern transient bench.

  0...2 ns     reset high, clock stopped
  3 ns         en high, clock passthrough of pll_clk at 1 GHz
  12 ns        mode high, PRBS-7 at 1 Gb/s
  150...155 ns en low, the clock gate stops the pattern
  160 ns       clk_src low, the 250 MHz reference takes over

scripts/check_prbs.py re-runs the polynomial over the exported
data and counts the bits that do not match.} 100 -1200 0 0 0.45 0.45 {}
N 150 -1060 150 -1030 {lab=VDD}
C {lab_pin.sym} 150 -1060 1 0 {name=lv_VDD sig_type=std_logic lab=VDD}
C {devices/vsource.sym} 150 -1000 0 0 {name=VVDD value="1.2"}
N 150 -970 150 -940 {lab=GND}
C {devices/gnd.sym} 150 -940 0 0 {name=lg_VDD lab=GND}
N 150 -860 150 -830 {lab=ref_clk}
C {lab_pin.sym} 150 -860 1 0 {name=lv_ref_clk sig_type=std_logic lab=ref_clk}
C {devices/vsource.sym} 150 -800 0 0 {name=Vref_clk value="PULSE(0 1.2 0 50p 50p 1.9n 4n)"}
N 150 -770 150 -740 {lab=GND}
C {devices/gnd.sym} 150 -740 0 0 {name=lg_ref_clk lab=GND}
N 150 -660 150 -630 {lab=pll_clk}
C {lab_pin.sym} 150 -660 1 0 {name=lv_pll_clk sig_type=std_logic lab=pll_clk}
C {devices/vsource.sym} 150 -600 0 0 {name=Vpll_clk value="PULSE(0 1.2 0 30p 30p 470p 1n)"}
N 150 -570 150 -540 {lab=GND}
C {devices/gnd.sym} 150 -540 0 0 {name=lg_pll_clk lab=GND}
N 150 -460 150 -430 {lab=clk_src}
C {lab_pin.sym} 150 -460 1 0 {name=lv_clk_src sig_type=std_logic lab=clk_src}
C {devices/vsource.sym} 150 -400 0 0 {name=Vclk_src value="PWL(0 1.2 160n 1.2 160.1n 0)"}
N 150 -370 150 -340 {lab=GND}
C {devices/gnd.sym} 150 -340 0 0 {name=lg_clk_src lab=GND}
N 150 -260 150 -230 {lab=en}
C {lab_pin.sym} 150 -260 1 0 {name=lv_en sig_type=std_logic lab=en}
C {devices/vsource.sym} 150 -200 0 0 {name=Ven value="PWL(0 0 3n 0 3.1n 1.2 150n 1.2 150.1n 0 155n 0 155.1n 1.2)"}
N 150 -170 150 -140 {lab=GND}
C {devices/gnd.sym} 150 -140 0 0 {name=lg_en lab=GND}
N 150 -60 150 -30 {lab=reset}
C {lab_pin.sym} 150 -60 1 0 {name=lv_reset sig_type=std_logic lab=reset}
C {devices/vsource.sym} 150 0 0 0 {name=Vreset value="PWL(0 1.2 2n 1.2 2.1n 0)"}
N 150 30 150 60 {lab=GND}
C {devices/gnd.sym} 150 60 0 0 {name=lg_reset lab=GND}
N 150 140 150 170 {lab=mode}
C {lab_pin.sym} 150 140 1 0 {name=lv_mode sig_type=std_logic lab=mode}
C {devices/vsource.sym} 150 200 0 0 {name=Vmode value="PWL(0 0 12n 0 12.1n 1.2)"}
N 150 230 150 260 {lab=GND}
C {devices/gnd.sym} 150 260 0 0 {name=lg_mode lab=GND}
N 530 -100 590 -100 {lab=ref_clk}
C {lab_pin.sym} 530 -100 0 0 {name=lx_ref_clk sig_type=std_logic lab=ref_clk}
N 530 -80 590 -80 {lab=pll_clk}
C {lab_pin.sym} 530 -80 0 0 {name=lx_pll_clk sig_type=std_logic lab=pll_clk}
N 530 -60 590 -60 {lab=clk_src}
C {lab_pin.sym} 530 -60 0 0 {name=lx_clk_src sig_type=std_logic lab=clk_src}
N 530 -40 590 -40 {lab=en}
C {lab_pin.sym} 530 -40 0 0 {name=lx_en sig_type=std_logic lab=en}
N 530 -20 590 -20 {lab=reset}
C {lab_pin.sym} 530 -20 0 0 {name=lx_reset sig_type=std_logic lab=reset}
N 530 0 590 0 {lab=mode}
C {lab_pin.sym} 530 0 0 0 {name=lx_mode sig_type=std_logic lab=mode}
N 810 -100 870 -100 {lab=D_p}
C {lab_pin.sym} 870 -100 0 1 {name=lx_D_p sig_type=std_logic lab=D_p}
N 810 -80 870 -80 {lab=D_n}
C {lab_pin.sym} 870 -80 0 1 {name=lx_D_n sig_type=std_logic lab=D_n}
N 810 80 870 80 {lab=VDD}
C {lab_pin.sym} 870 80 0 1 {name=lx_VDD sig_type=std_logic lab=VDD}
N 810 100 870 100 {lab=0}
C {devices/gnd.sym} 870 100 3 0 {name=lg_vss lab=GND}
C {lvds_pattern.sym} 700 0 0 0 {name=x1}
N 1000 -360 1000 -330 {lab=D_p}
C {lab_pin.sym} 1000 -360 1 0 {name=lc_D_p sig_type=std_logic lab=D_p}
C {capa.sym} 1000 -300 0 0 {name=CD_p m=1 value=170f}
N 1000 -270 1000 -240 {lab=GND}
C {devices/gnd.sym} 1000 -240 0 0 {name=lgc_D_p lab=GND}
N 1000 -160 1000 -130 {lab=D_n}
C {lab_pin.sym} 1000 -160 1 0 {name=lc_D_n sig_type=std_logic lab=D_n}
C {capa.sym} 1000 -100 0 0 {name=CD_n m=1 value=170f}
N 1000 -70 1000 -40 {lab=GND}
C {devices/gnd.sym} 1000 -40 0 0 {name=lgc_D_n lab=GND}
C {devices/code_shown.sym} 1200 -1000 0 0 {name=NGSPICE
only_toplevel=true
value="
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.lib cornerMOSlv.lib mos_tt
.temp 27
.options savecurrents klu reltol=1e-3
.control
save all
tran 5p 200n
write @schname\\\\.raw

* the pair has to be complementary at every instant
let dsum = v(D_p)+v(D_n)
meas tran dsum_min MIN dsum from=20n to=140n
meas tran dsum_max MAX dsum from=20n to=140n

* D_p rising against D_n falling on the same bit: this is the skew the
* pre-driver sees, budget about 40 ps (docs/predriver-findings.md)
meas tran tp_r WHEN v(D_p)=0.6 RISE=5
meas tran tn_f WHEN v(D_n)=0.6 FALL=5
let skew = tn_f - tp_r
print skew

* clock passthrough period, measured before mode goes high
meas tran t1 WHEN v(D_p)=0.6 RISE=4
meas tran t2 WHEN v(D_p)=0.6 RISE=5
let tpass = t2 - t1
print tpass

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(D_p) v(D_n) v(x1.gclk_b) v(mode) v(en)
.endc
"}
