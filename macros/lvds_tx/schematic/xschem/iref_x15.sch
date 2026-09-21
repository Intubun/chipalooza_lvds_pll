v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {1:15 reference-current pre-mirror.

The harness current DACs deliver 50 nA to 10 uA, so the 30 uA that the driver
and the pre-driver were characterised at cannot come off a pin at all.  This
block takes 2 uA in and hands 30 uA to the block behind it, which therefore
stays exactly as it was measured.

  Mn1  the 2 uA diode, one 0.8 um unit
  Mn2  fifteen of the same unit, so it sinks 30 uA
  Mp1  the 30 uA PMOS diode
  Mp2  its 1:1 partner, sourcing 30 uA into IREF_OUT

Mn1 and Mn2 are the same unit device at the same current density -- 2 uA over
0.8 um and 30 uA over 12 um are both 2.5 uA/um -- so the pair sees one Vgs and
the ratio is set by finger count alone.  That density is well below the 37.5
uA/um that M9 in the driver runs at; the pair sits at a lower overdrive, which
costs matching but keeps both devices in the same region.

The PMOS pair carries the whole 30 uA between Va and the reference node.  Mp2
needs Va - V(IREF_OUT) - |Vdsat| of headroom to stay saturated; V(IREF_OUT) is
the Vgs of the diode it feeds, so on 3.3 V there is room to spare.

SIZING HISTORY.  At L = 0.5 um the first build measured |Vod| = 526 mV against
a 359 mV target, a factor 1.47.  Both stages put their diode at Vds = Vgs and
their output device at Vds = 2.6 V, and at that length the channel-length
modulation is worth about 18 % per stage.  L is now 2 um with W scaled by the
same factor, so W/L and the operating point are unchanged while lambda drops
roughly fourfold.} 20 -720 0 0 0.4 0.4 {}
N 310 210 310 230 {lab=IREF_IN}
N 310 290 310 330 {lab=Vss}
N 250 260 310 260 {lab=Vss}
N 550 290 550 330 {lab=Vss}
N 550 260 610 260 {lab=Vss}
N 630 120 670 120 {lab=CASC}
N 550 50 550 90 {lab=Va}
N 550 190 550 230 {lab=CASC}
N 490 120 550 120 {lab=Va}
N 710 50 710 90 {lab=Va}
N 710 150 710 190 {lab=IREF_OUT}
N 710 120 770 120 {lab=Va}
N 710 190 950 190 {lab=IREF_OUT}
N 50 240 110 240 {lab=Va}
N 50 280 110 280 {lab=Vss}
N 550 190 630 190 {lab=CASC}
N 550 150 550 190 {lab=CASC}
N 630 120 630 190 {lab=CASC}
N 590 120 630 120 {lab=CASC}
N 370 260 510 260 {lab=IREF_IN}
N 310 210 370 210 {lab=IREF_IN}
N 310 190 310 210 {lab=IREF_IN}
N 370 210 370 260 {lab=IREF_IN}
N 350 260 370 260 {lab=IREF_IN}
N 250 190 310 190 {lab=IREF_IN}
C {lab_wire.sym} 500 260 0 0 {name=wg2 sig_type=std_logic lab=IREF_IN}
C {lab_wire.sym} 650 120 0 0 {name=wg4 sig_type=std_logic lab=CASC}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 330 260 0 1 {name=Mn1
l=2u
w=3.2u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} 530 260 0 0 {name=Mn2
l=2u
w=48u
 ng=6
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 570 120 0 1 {name=Mp1
l=2u
w=48u
 ng=6
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/sg13_hv_pmos.sym} 690 120 0 0 {name=Mp2
l=2u
w=48u
 ng=6
 m=1
  mm_ok=1
 model=sg13_hv_pmos
spiceprefix=X
}
C {lab_wire.sym} 330 210 0 1 {name=wd1 sig_type=std_logic lab=IREF_IN}
C {lab_wire.sym} 250 260 0 1 {name=wb1 sig_type=std_logic lab=Vss}
C {lab_wire.sym} 310 330 0 1 {name=ws1 sig_type=std_logic lab=Vss}
C {lab_wire.sym} 610 260 0 0 {name=wb2 sig_type=std_logic lab=Vss}
C {lab_wire.sym} 550 330 0 0 {name=ws2 sig_type=std_logic lab=Vss}
C {lab_wire.sym} 550 50 0 1 {name=ws3 sig_type=std_logic lab=Va}
C {lab_wire.sym} 490 120 0 1 {name=wb3 sig_type=std_logic lab=Va}
C {lab_wire.sym} 710 50 0 0 {name=ws4 sig_type=std_logic lab=Va}
C {lab_wire.sym} 770 120 0 0 {name=wb4 sig_type=std_logic lab=Va}
C {ipin.sym} 250 190 0 0 {name=p_iref_in lab=IREF_IN}
C {opin.sym} 950 190 0 0 {name=p_iref_out lab=IREF_OUT}
C {iopin.sym} 50 240 0 0 {name=p_va lab=Va}
C {iopin.sym} 50 280 0 0 {name=p_vss lab=Vss}
C {lab_wire.sym} 110 240 0 0 {name=wva sig_type=std_logic lab=Va}
C {lab_wire.sym} 110 280 0 0 {name=wvss sig_type=std_logic lab=Vss}
