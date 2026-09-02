v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {devices/lab_pin.sym} -700 -440 0 0 {name=lVDD_-700_-440 sig_type=std_logic lab=VDD}
N -700 -440 -700 -420 {lab=VDD}
C {devices/vsource.sym} -700 -400 0 0 {name=VDD value="CACE\{vdd\}" savecurrent=true}
N -700 -380 -700 -360 {lab=GND}
C {devices/gnd.sym} -700 -360 0 0 {name=gVDD lab=GND}
C {devices/lab_pin.sym} -700 -280 0 0 {name=lref_clk_-700_-280 sig_type=std_logic lab=ref_clk}
N -700 -280 -700 -260 {lab=ref_clk}
C {devices/vsource.sym} -700 -240 0 0 {name=VREF value="PULSE(0 CACE\{vdd\} 0 CACE\{tedge\} CACE\{tedge\} 'CACE\{period\}/2-CACE\{tedge\}' CACE\{period\})" savecurrent=false}
N -700 -220 -700 -200 {lab=GND}
C {devices/gnd.sym} -700 -200 0 0 {name=gVREF lab=GND}
C {devices/lab_pin.sym} -700 -120 0 0 {name=lpll_clk_-700_-120 sig_type=std_logic lab=pll_clk}
N -700 -120 -700 -100 {lab=pll_clk}
C {devices/vsource.sym} -700 -80 0 0 {name=VPLL value="0" savecurrent=false}
N -700 -60 -700 -40 {lab=GND}
C {devices/gnd.sym} -700 -40 0 0 {name=gVPLL lab=GND}
C {devices/lab_pin.sym} -700 40 0 0 {name=lclk_src_-700_40 sig_type=std_logic lab=clk_src}
N -700 40 -700 60 {lab=clk_src}
C {devices/vsource.sym} -700 80 0 0 {name=VSRC value="0" savecurrent=false}
N -700 100 -700 120 {lab=GND}
C {devices/gnd.sym} -700 120 0 0 {name=gVSRC lab=GND}
C {devices/lab_pin.sym} -700 200 0 0 {name=len_-700_200 sig_type=std_logic lab=en}
N -700 200 -700 220 {lab=en}
C {devices/vsource.sym} -700 240 0 0 {name=VEN value="PWL(0 0 CACE\{t_en\} 0 'CACE\{t_en\}+CACE\{tedge\}' CACE\{vdd\})" savecurrent=false}
N -700 260 -700 280 {lab=GND}
C {devices/gnd.sym} -700 280 0 0 {name=gVEN lab=GND}
C {devices/lab_pin.sym} -700 360 0 0 {name=lreset_-700_360 sig_type=std_logic lab=reset}
N -700 360 -700 380 {lab=reset}
C {devices/vsource.sym} -700 400 0 0 {name=VRST value="PWL(0 CACE\{vdd\} CACE\{t_rst\} CACE\{vdd\} 'CACE\{t_rst\}+CACE\{tedge\}' 0)" savecurrent=false}
N -700 420 -700 440 {lab=GND}
C {devices/gnd.sym} -700 440 0 0 {name=gVRST lab=GND}
C {devices/lab_pin.sym} -700 520 0 0 {name=lmode_-700_520 sig_type=std_logic lab=mode}
N -700 520 -700 540 {lab=mode}
C {devices/vsource.sym} -700 560 0 0 {name=VMODE value="CACE\{vdd\}" savecurrent=false}
N -700 580 -700 600 {lab=GND}
C {devices/gnd.sym} -700 600 0 0 {name=gVMODE lab=GND}
C {lvds_pattern.sym} 0 0 0 0 {name=x1}
N -190 -100 -130 -100 {lab=ref_clk}
C {devices/lab_pin.sym} -190 -100 0 0 {name=lref_clk_-190_-100 sig_type=std_logic lab=ref_clk}
N -190 -80 -130 -80 {lab=pll_clk}
C {devices/lab_pin.sym} -190 -80 0 0 {name=lpll_clk_-190_-80 sig_type=std_logic lab=pll_clk}
N -190 -60 -130 -60 {lab=clk_src}
C {devices/lab_pin.sym} -190 -60 0 0 {name=lclk_src_-190_-60 sig_type=std_logic lab=clk_src}
N -190 -40 -130 -40 {lab=en}
C {devices/lab_pin.sym} -190 -40 0 0 {name=len_-190_-40 sig_type=std_logic lab=en}
N -190 -20 -130 -20 {lab=reset}
C {devices/lab_pin.sym} -190 -20 0 0 {name=lreset_-190_-20 sig_type=std_logic lab=reset}
N -190 0 -130 0 {lab=mode}
C {devices/lab_pin.sym} -190 0 0 0 {name=lmode_-190_0 sig_type=std_logic lab=mode}
N 130 80 190 80 {lab=VDD}
C {devices/lab_pin.sym} 190 80 0 1 {name=lVDD_190_80 sig_type=std_logic lab=VDD}
N 130 100 190 100 {lab=GND}
C {devices/gnd.sym} 190 100 1 0 {name=gdut lab=GND}
N 130 -100 260 -100 {lab=D_p}
C {devices/lab_pin.sym} 260 -100 0 1 {name=lD_p_260_-100 sig_type=std_logic lab=D_p}
N 400 -300 400 -270 {lab=D_p}
C {devices/lab_pin.sym} 400 -300 0 0 {name=lD_p_400_-300 sig_type=std_logic lab=D_p}
C {devices/capa.sym} 400 -240 0 0 {name=CD_p m=1 value=CACE\{cload\}}
N 400 -210 400 -180 {lab=GND}
C {devices/gnd.sym} 400 -180 0 0 {name=gD_p lab=GND}
N 130 -80 260 -80 {lab=D_n}
C {devices/lab_pin.sym} 260 -80 0 1 {name=lD_n_260_-80 sig_type=std_logic lab=D_n}
N 400 -160 400 -130 {lab=D_n}
C {devices/lab_pin.sym} 400 -160 0 0 {name=lD_n_400_-160 sig_type=std_logic lab=D_n}
C {devices/capa.sym} 400 -100 0 0 {name=CD_n m=1 value=CACE\{cload\}}
N 400 -70 400 -40 {lab=GND}
C {devices/gnd.sym} 400 -40 0 0 {name=gD_n lab=GND}
C {devices/code_shown.sym} 700 -400 0 0 {name=SETUP
simulator=ngspice
only_toplevel=false
value="
* Corner and temperature are conditions, so one template covers the grid.
.lib cornerMOSlv.lib mos_CACE\{corner\}
.include CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice

* schematic, extracted layout or R-C extracted, whichever CACE was asked for
.include CACE\{DUT_path\}

.temp CACE\{temperature\}
.option warn=1
"}
C {devices/code_shown.sym} 700 0 0 0 {name=CONTROL
simulator=ngspice
only_toplevel=false
value="
.control

    * A single .save in the netlist makes ngspice drop every node voltage that
    * is not named, and savecurrent on the supply emits one. So list them.
    save v(D_p) v(D_n) i(VDD)

    tran CACE\{tstep\} CACE\{tstop\}

    * Is the pair complementary at every instant? dsum is twice the common mode
    * of the two outputs, so a pair that ever sits at the same level shows up
    * here as an excursion, whatever the data is doing.
    let dsum = v(D_p)+v(D_n)
    meas tran dsum_min MIN dsum from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran dsum_max MAX dsum from=CACE\{tmeas\} to=CACE\{tstop\}
    let dsum_dev = maximum(abs(dsum_max-CACE\{vdd\}), abs(CACE\{vdd\}-dsum_min))

    * Output skew: D_p rising against D_n falling on the same bit. This is what
    * the pre-driver sees, and its budget is about 40 ps.
    * Both counts start at tmeas, not at t=0. During power-up one side can
    * emit a transition the other does not, and from then on the two edge
    * indices refer to different bits - which showed up as a skew of three
    * whole bit periods in some corners and 25 ps in others.
    meas tran tp_r WHEN v(D_p)=CACE\{vhalf\} RISE=CACE\{edge\} TD=CACE\{tmeas\}
    meas tran tn_f WHEN v(D_n)=CACE\{vhalf\} FALL=CACE\{edge\} TD=CACE\{tmeas\}
    let skew = abs(tn_f - tp_r)

    meas tran i_vdd AVG i(VDD) from=CACE\{tmeas\} to=CACE\{tstop\}
    let i_core = -i_vdd

    echo $&dsum_dev $&skew $&i_core > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc
"}
