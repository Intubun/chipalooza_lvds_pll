v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {lvds_tx  --  the analog transmitter: pre-driver and driver in one schematic

WIRED GEOMETRICALLY, like Driver.sch: every connection here is a drawn wire.
xschem connects a device pin anywhere along a wire, and a wire ENDPOINT that
touches another wire, but two wires that merely CROSS connect nothing -- so the
supply and bias nets can be routed through each other in a channel the way they
would be on paper.  Read the crossings as crossings; they are deliberate.

The two labels sitting on the wires between the blocks only NAME them, so they
can be probed as xtx.In_p instead of xtx.net3.  The wire is the connection:
delete a label and the circuit is unchanged.

WHAT THE TWO WIRES BETWEEN THE BLOCKS ARE:

  In_p / In_n      the data pair, rail-to-rail 3.3 V gate drive.  That is the
                   whole interface.  There used to be four: In_p_d / In_n_d
                   carried the same pair one bit period later and fed the
                   driver's auxiliary H-bridge, the second tap of a 2-tap FIR
                   pre-emphasis.  The pre-emphasis is gone -- it put an 11 mV
                   settling tail on every de-emphasised bit and bought nothing
                   measurable on a bench-length channel -- and with it went the
                   auxiliary bridge, the pre-driver's second slice, and the
                   analog delay line that made the tap.

TWO SEPARATE REFERENCE CURRENTS, Iref_pd and Iref_drv, and they must stay
separate.  Tie them together and feed twice one pin's current and neither block
gets its share: the two reference diodes sit in parallel and split the current
by width -- M9 in the driver is 0.8 um, Mref in the pre-driver is 8 um -- so the
driver would run at about a tenth of its bias while every waveform still looked
plausible and |Vod| quietly landed at 110 mV.  That is the reason they are two
pins on this symbol and not one.

BOTH PINS NOW TAKE 2 uA, NOT 30 uA.  The harness current DACs deliver 50 nA to
10 uA, so the 30 uA the driver and the pre-driver were characterised at cannot
come off a pin at all.  Xm_pd and Xm_drv are 1:15 pre-mirrors (iref_x15.sch):
each takes 2 uA from its pin and hands 30 uA to the block behind it on
Iref_pd_30u / Iref_drv_30u, so Driver.sch and predriver.sch are untouched and
still see exactly the bias they were measured at.

The macro's own Driver.tb, predriver.tb and tb_dc drive those blocks directly,
below the pre-mirror, and therefore still use 30 uA.  tb_alt, tb_prbs, tb_slow,
tb_startup and tb_word drive this symbol's pins and use 2 uA.

Va is 3.3 V and runs along the top; Vss along the bottom.  The 1.2 V core rail
does not appear here at all -- the pre-driver's input stage takes core-level
data on a 3.3 V differential pair, which is its entire job.

WHAT IS NOT IN HERE: the pads.  esdpad.sym belongs to whatever hangs on the
output, and the clause 4.1.4 and 4.1.5 numbers depend on that capacitance, so
it stays visible in the testbench rather than being buried in a block.} -1480 -590 0 0 0.4 0.4 {}
N -400 -50 -150 -50 {lab=D_p}
N -400 -30 -150 -30 {lab=D_n}
N -400 30 -340 30 {lab=Iref_pd}
C {lab_wire.sym} -340 30 0 0 {name=wpin_pd sig_type=std_logic lab=Iref_pd}
N -210 30 -150 30 {lab=Iref_pd_30u}
C {lab_wire.sym} -210 30 0 0 {name=wblk_pd sig_type=std_logic lab=Iref_pd_30u}
N -400 120 -340 120 {lab=Iref_drv}
C {lab_wire.sym} -340 120 0 0 {name=wpin_dv sig_type=std_logic lab=Iref_drv}
N -210 120 400 120 {lab=Iref_drv_30u}
C {lab_wire.sym} -210 120 0 0 {name=wblk_dv sig_type=std_logic lab=Iref_drv_30u}
N 400 10 400 120 {lab=Iref_drv_30u}
N 400 10 550 10 {lab=Iref_drv_30u}
N -400 160 460 160 {lab=Vref}
N 460 30 460 160 {lab=Vref}
N 460 30 550 30 {lab=Vref}
N 150 -50 300 -50 {lab=In_p}
N 300 -50 300 -30 {lab=In_p}
N 300 -30 550 -30 {lab=In_p}
N 150 -30 250 -30 {lab=In_n}
N 250 -30 250 -10 {lab=In_n}
N 250 -10 550 -10 {lab=In_n}
N 150 -70 320 -70 {lab=Va}
N 320 -250 320 -70 {lab=Va}
N 600 -250 950 -250 {lab=Va}
N 950 -250 950 -30 {lab=Va}
N 850 -30 950 -30 {lab=Va}
N 600 -300 600 -250 {lab=Va}
N 150 30 260 30 {lab=Vss}
N 260 30 260 250 {lab=Vss}
N 600 250 950 250 {lab=Vss}
N 950 30 950 250 {lab=Vss}
N 850 30 950 30 {lab=Vss}
N 600 250 600 300 {lab=Vss}
N 850 -10 1100 -10 {lab=Out_p}
N 850 10 1100 10 {lab=Out_n}
N 320 -250 600 -250 {lab=Va}
N 260 250 600 250 {lab=Vss}
N -180 400 -220 400 {lab=Iref_pd}
C {lab_wire.sym} -220 400 0 0 {name=wm_pd_in sig_type=std_logic lab=Iref_pd}
N -20 400 20 400 {lab=Iref_pd_30u}
C {lab_wire.sym} 20 400 0 0 {name=wm_pd_out sig_type=std_logic lab=Iref_pd_30u}
N -120 320 -120 280 {lab=Va}
C {lab_wire.sym} -120 280 0 0 {name=wm_pd_va sig_type=std_logic lab=Va}
N -80 480 -80 520 {lab=Vss}
C {lab_wire.sym} -80 520 0 0 {name=wm_pd_vss sig_type=std_logic lab=Vss}
C {iref_x15.sym} -100 400 0 0 {name=Xm_pd}
N -180 650 -220 650 {lab=Iref_drv}
C {lab_wire.sym} -220 650 0 0 {name=wm_drv_in sig_type=std_logic lab=Iref_drv}
N -20 650 20 650 {lab=Iref_drv_30u}
C {lab_wire.sym} 20 650 0 0 {name=wm_drv_out sig_type=std_logic lab=Iref_drv_30u}
N -120 570 -120 530 {lab=Va}
C {lab_wire.sym} -120 530 0 0 {name=wm_drv_va sig_type=std_logic lab=Va}
N -80 730 -80 770 {lab=Vss}
C {lab_wire.sym} -80 770 0 0 {name=wm_drv_vss sig_type=std_logic lab=Vss}
C {iref_x15.sym} -100 650 0 0 {name=Xm_drv}
C {predriver.sym} 0 0 0 0 {name=Xpd}
C {Driver.sym} 700 0 0 0 {name=Xdrv}
C {lab_wire.sym} 450 -30 0 0 {name=w1 sig_type=std_logic lab=In_p}
C {lab_wire.sym} 450 -10 0 0 {name=w2 sig_type=std_logic lab=In_n}
C {ipin.sym} -400 -50 0 0 {name=p1 lab=D_p}
C {ipin.sym} -400 -30 0 0 {name=p2 lab=D_n}
C {ipin.sym} -400 30 0 0 {name=p3 lab=Iref_pd}
C {ipin.sym} -400 120 0 0 {name=p4 lab=Iref_drv}
C {ipin.sym} -400 160 0 0 {name=p5 lab=Vref}
C {iopin.sym} 600 -300 3 0 {name=p6 lab=Va}
C {iopin.sym} 600 300 1 0 {name=p7 lab=Vss}
C {opin.sym} 1100 -10 0 0 {name=p8 lab=Out_p}
C {opin.sym} 1100 10 0 0 {name=p9 lab=Out_n}
