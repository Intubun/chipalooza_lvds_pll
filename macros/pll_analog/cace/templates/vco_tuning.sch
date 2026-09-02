v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {devices/lab_pin.sym} -600 -340 0 0 {name=lVDD_-600_-340 sig_type=std_logic lab=VDD}
N -600 -340 -600 -320 {lab=VDD}
C {devices/vsource.sym} -600 -300 0 0 {name=VDD value="CACE\{vdd\}" savecurrent=true}
N -600 -280 -600 -260 {lab=GND}
C {devices/gnd.sym} -600 -260 0 0 {name=gVDD lab=GND}
C {devices/lab_pin.sym} -600 -140 0 0 {name=lVCTRL_-600_-140 sig_type=std_logic lab=VCTRL}
N -600 -140 -600 -120 {lab=VCTRL}
C {devices/vsource.sym} -600 -100 0 0 {name=VCT value="CACE\{vctrl\}" savecurrent=false}
N -600 -80 -600 -60 {lab=GND}
C {devices/gnd.sym} -600 -60 0 0 {name=gVCT lab=GND}
C {ring_oscillator.sym} 0 0 0 0 {name=x1}
N -180 -30 -120 -30 {lab=VCTRL}
C {devices/lab_pin.sym} -180 -30 0 0 {name=lVCTRL_-180_-30 sig_type=std_logic lab=VCTRL}
N 120 -30 240 -30 {lab=VCO_OUT}
C {devices/lab_pin.sym} 240 -30 0 1 {name=lVCO_OUT_240_-30 sig_type=std_logic lab=VCO_OUT}
N 120 -10 200 -10 {lab=VDD}
C {devices/lab_pin.sym} 200 -10 0 1 {name=lVDD_200_-10 sig_type=std_logic lab=VDD}
N 120 50 200 50 {lab=GND}
C {devices/gnd.sym} 200 50 1 0 {name=gdut lab=GND}
C {devices/code_shown.sym} 600 -300 0 0 {name=SETUP
simulator=ngspice
only_toplevel=false
value="
* Corner and temperature are conditions, so one template covers the grid.
.lib cornerMOSlv.lib mos_CACE\{corner\}

* schematic, extracted layout or R-C extracted, whichever CACE was asked for
.include CACE\{DUT_path\}

.temp CACE\{temperature\}
.option warn=1

* A ring oscillator has a perfectly good unstable DC operating point, and
* ngspice will solve for it and then stay there. These three nodes break the
* symmetry so it starts, the same way the block's own benches do it.
.ic v(x1.VCO_CORE)=0 v(x1.net1)=CACE\{vdd\} v(x1.net2)=0
"}
C {devices/code_shown.sym} 600 100 0 0 {name=CONTROL
simulator=ngspice
only_toplevel=false
value="
.control

    save v(VCO_OUT) i(VDD)

    tran CACE\{tstep\} CACE\{tstop\}

    * Count a fixed number of crossings and divide, rather than taking one
    * period. The frequency changes by an order of magnitude across the VCTRL
    * sweep, so a single period is both noisy and, at the fast end, shorter
    * than the timestep resolution deserves.
    meas tran t_a WHEN v(VCO_OUT)=CACE\{vhalf\} RISE=CACE\{edge_a\}
    meas tran t_b WHEN v(VCO_OUT)=CACE\{vhalf\} RISE=CACE\{edge_b\}
    let f_vco = (CACE\{edge_b\}-CACE\{edge_a\})/(t_b-t_a)

    * Amplitude tells you whether it is really oscillating rail to rail or
    * just ringing - a frequency measured on a 100 mV wiggle is not a clock.
    meas tran v_max MAX v(VCO_OUT) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran v_min MIN v(VCO_OUT) from=CACE\{tmeas\} to=CACE\{tstop\}
    let v_swing = v_max - v_min

    meas tran i_vdd AVG i(VDD) from=CACE\{tmeas\} to=CACE\{tstop\}
    * In amps. CACE takes the number as SI base units and uses the unit
    * field only to scale the display, so declaring uA in the datasheet
    * is what makes this read as tens of microamps rather than 0.000 A.
    * Scaling here as well multiplies it in twice.
    let i_vco = -i_vdd

    echo $&f_vco $&v_swing $&i_vco > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc
"}
