v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {devices/lab_pin.sym} -700 -440 0 0 {name=l_Va sig_type=std_logic lab=Va}
N -700 -440 -700 -420 {lab=Va}
C {devices/vsource.sym} -700 -400 0 0 {name=VA value="CACE\{vdd\}" savecurrent=true}
N -700 -380 -700 -360 {lab=GND}
C {devices/gnd.sym} -700 -360 0 0 {name=g_VA lab=GND}
C {devices/lab_pin.sym} -700 -280 0 0 {name=l_Vref sig_type=std_logic lab=Vref}
N -700 -280 -700 -260 {lab=Vref}
C {devices/vsource.sym} -700 -240 0 0 {name=Vrf value="CACE\{vref\}" savecurrent=false}
N -700 -220 -700 -200 {lab=GND}
C {devices/gnd.sym} -700 -200 0 0 {name=g_Vrf lab=GND}
C {devices/lab_pin.sym} -700 -120 0 0 {name=l_Iref_pd sig_type=std_logic lab=Iref_pd}
N -700 -120 -700 -100 {lab=Iref_pd}
C {devices/isource.sym} -700 -80 0 0 {name=Ipd value=-CACE\{iref\}}
N -700 -60 -700 -40 {lab=GND}
C {devices/gnd.sym} -700 -40 0 0 {name=g_Ipd lab=GND}
C {devices/lab_pin.sym} -700 40 0 0 {name=l_Iref_drv sig_type=std_logic lab=Iref_drv}
N -700 40 -700 60 {lab=Iref_drv}
C {devices/isource.sym} -700 80 0 0 {name=Idrv value=-CACE\{iref\}}
N -700 100 -700 120 {lab=GND}
C {devices/gnd.sym} -700 120 0 0 {name=g_Idrv lab=GND}
C {devices/lab_pin.sym} -700 200 0 0 {name=l_D_p sig_type=std_logic lab=D_p}
N -700 200 -700 220 {lab=D_p}
C {devices/vsource.sym} -700 240 0 0 {name=VDp value="PULSE(0 CACE\{vddc\} 0 CACE\{tedge\} CACE\{tedge\} 'CACE\{period\}/2-CACE\{tedge\}' CACE\{period\})" savecurrent=false}
N -700 260 -700 280 {lab=GND}
C {devices/gnd.sym} -700 280 0 0 {name=g_VDp lab=GND}
C {devices/lab_pin.sym} -700 360 0 0 {name=l_D_n sig_type=std_logic lab=D_n}
N -700 360 -700 380 {lab=D_n}
C {devices/vsource.sym} -700 400 0 0 {name=VDn value="PULSE(0 CACE\{vddc\} 'CACE\{period\}/2' CACE\{tedge\} CACE\{tedge\} 'CACE\{period\}/2-CACE\{tedge\}' CACE\{period\})" savecurrent=false}
N -700 420 -700 440 {lab=GND}
C {devices/gnd.sym} -700 440 0 0 {name=g_VDn lab=GND}
C {lvds_tx.sym} 0 0 0 0 {name=x1}
N -210 -50 -150 -50 {lab=D_p}
C {devices/lab_pin.sym} -210 -50 0 0 {name=l_D_p sig_type=std_logic lab=D_p}
N -210 -30 -150 -30 {lab=D_n}
C {devices/lab_pin.sym} -210 -30 0 0 {name=l_D_n sig_type=std_logic lab=D_n}
N -210 -10 -150 -10 {lab=Iref_pd}
C {devices/lab_pin.sym} -210 -10 0 0 {name=l_Iref_pd sig_type=std_logic lab=Iref_pd}
N -210 10 -150 10 {lab=Iref_drv}
C {devices/lab_pin.sym} -210 10 0 0 {name=l_Iref_drv sig_type=std_logic lab=Iref_drv}
N -210 30 -150 30 {lab=Vref}
C {devices/lab_pin.sym} -210 30 0 0 {name=l_Vref sig_type=std_logic lab=Vref}
N 150 60 210 60 {lab=Va}
C {devices/lab_pin.sym} 210 60 0 1 {name=l_Va sig_type=std_logic lab=Va}
N 150 80 210 80 {lab=GND}
C {devices/gnd.sym} 210 80 1 0 {name=g_dut lab=GND}
N 150 -30 300 -30 {lab=Out_p}
C {devices/lab_pin.sym} 300 -30 0 1 {name=l_Out_p sig_type=std_logic lab=Out_p}
N 150 -10 300 -10 {lab=Out_n}
C {devices/lab_pin.sym} 300 -10 0 1 {name=l_Out_n sig_type=std_logic lab=Out_n}
N 420 -120 420 -90 {lab=Out_p}
C {devices/lab_pin.sym} 420 -120 0 0 {name=l_Out_p sig_type=std_logic lab=Out_p}
C {devices/res.sym} 420 -60 0 0 {name=Rp value=49.9}
N 420 -30 420 0 {lab=Vos}
N 420 0 420 30 {lab=Vos}
C {devices/res.sym} 420 60 0 0 {name=Rn value=49.9}
N 420 90 420 120 {lab=Out_n}
C {devices/lab_pin.sym} 420 120 0 0 {name=l_Out_n sig_type=std_logic lab=Out_n}
N 420 0 500 0 {lab=Vos}
C {devices/lab_pin.sym} 500 0 0 1 {name=l_Vos sig_type=std_logic lab=Vos}
C {devices/code_shown.sym} 700 -400 0 0 {name=SETUP
simulator=ngspice
only_toplevel=false
value="
* Corner and temperature are conditions, so one template covers the whole grid.
.lib cornerMOSlv.lib mos_CACE\{corner\}
.lib cornerMOShv.lib mos_CACE\{corner\}
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib

* The DUT netlist: schematic, extracted layout or R-C extracted, whichever
* CACE was asked for. This one line is what makes the three columns possible.
.include CACE\{DUT_path\}

.temp CACE\{temperature\}
.option warn=1

* The common-mode loop starts far from its operating point, so the bench gives
* it a hint and then measures only well after it has settled. Measuring across
* the cold start is how a driver that is not compliant comes out looking
* compliant.
.ic v(x1.xdrv.cmfb)=CACE\{cmfb_ic\}
"}
C {devices/code_shown.sym} 700 0 0 0 {name=CONTROL
simulator=ngspice
only_toplevel=false
value="
.control

    * The analysis window and the measurement window are conditions in their
    * own right rather than expressions over the bit period. ngspice's control
    * language takes plain numbers here - a quoted expression is accepted in a
    * netlist line but silently skips the analysis in a .control block, which
    * leaves every meas reporting it is limited to tran, dc, sp or ac.
    * savecurrent on the supply emits a .save line into the netlist, and a
    * single .save makes ngspice keep only what is listed - every node
    * voltage is dropped. So name everything this bench measures.
    save v(Out_p) v(Out_n) v(Vos) i(VA)

    tran CACE\{tstep\} CACE\{tstop\}

    let vod = v(Out_p)-v(Out_n)

    meas tran vod_max MAX vod    from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vod_min MIN vod    from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vos_max MAX v(Vos) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vos_min MIN v(Vos) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vos_avg AVG v(Vos) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran i_va    AVG i(VA)  from=CACE\{tmeas\} to=CACE\{tstop\}

    * Clause 4.1.1 is written on the magnitude, and an unbalanced driver has
    * two different magnitudes. Report the worse one, not the average.
    let vod_mag  = min(vod_max, -vod_min)
    let vos_pp   = vos_max - vos_min
    let i_supply = -i_va

    echo $&vod_mag $&vos_avg $&vos_pp $&i_supply > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc
"}
