v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Pre-driver: 1.2 V core data in, rail-to-rail 3.3 V driver gate drive out.

THREE SUB-BLOCKS, and the split is the circuit, not a drawing convenience:

  predriver_comp   the level shifter.  NMOS pair on a tail, PMOS current-
                   mirror load to Va.  The gates only ever see 1.2 V; the
                   drains hang off 3.3 V, so the shift is complete at its
                   output.  Instantiated TWICE with the inputs swapped, so
                   the two delays match by construction, not by trimming.

  predriver_stage  both tapered inverter chains AND the skew corrector.
                   The corrector belongs to neither side -- it exists only
                   because there are two chains, and it forces them to stay
                   complements -- so the block is the pair, not one chain.

The comparator decides on D_p - D_n crossing zero rather than on either
input crossing an absolute trip point, which is what keeps the two
polarities aligned over corners.  docs/predriver-findings.md 4 records the
three load topologies tried before this one and how each failed.

The corrector must stay well below the strength of the stage driving it.
Measured: at ratio 1.0 it stops correcting and latches.  It sits at 0.35.

SIZING: pn[0] is 1.65, not the 1.2 it was.  In_p and In_n run ANTIPHASE
through the same chain, so each stage rise/fall asymmetry adds up as
differential delay.  Balancing the first stage took skew from 31..64 ps to
1.6..16 ps over PVT and Vos p-p from 137..197 mV to 42..70 mV, at the same
current.  docs/predriver-findings.md 5c.} -170 -1780 0 0 0.4 0.4 {}
N 1400 -1000 3000 -1000 {lab=Va}
N 200 340 3000 340 {lab=Vss}
N -20 440 500 440 {lab=Iref}
N 60 500 500 500 {lab=D_p}
N 20 560 500 560 {lab=D_n}
N 200 -1000 200 -70 {lab=Va}
N 200 70 200 340 {lab=Vss}
N 60 -20 100 -20 {lab=D_p}
N 60 -20 60 500 {lab=D_p}
N 20 0 100 0 {lab=D_n}
N 20 0 20 560 {lab=D_n}
N -20 20 100 20 {lab=Iref}
N -20 20 -20 440 {lab=Iref}
N 300 0 1280 0 {lab=#net1}
N -80 60 -40 60 {lab=Vss}
N -40 60 -40 340 {lab=Vss}
N -120 20 -120 440 {lab=Iref}
N -120 20 -80 20 {lab=Iref}
N -80 20 -80 30 {lab=Iref}
N -80 90 -80 340 {lab=Vss}
N 200 700 3000 700 {lab=Va}
N 1400 2040 3000 2040 {lab=Vss}
N -20 2140 500 2140 {lab=Iref}
N 20 2200 500 2200 {lab=D_p}
N 60 2260 500 2260 {lab=D_n}
N 200 700 200 1630 {lab=Va}
N 200 1770 200 2040 {lab=Vss}
N 60 1680 100 1680 {lab=D_n}
N 60 1680 60 2260 {lab=D_n}
N 20 1700 100 1700 {lab=D_p}
N 20 1700 20 2200 {lab=D_p}
N -20 1720 100 1720 {lab=Iref}
N -20 1720 -20 2140 {lab=Iref}
N 300 1700 1280 1700 {lab=#net2}
N 1280 0 1280 830 {lab=#net1}
N 1280 870 1280 1700 {lab=#net2}
N 1520 830 3000 830 {lab=In_p}
N 1520 870 3000 870 {lab=In_n}
N 1400 -1000 1400 780 {lab=Va}
N 1400 920 1400 2040 {lab=Vss}
N -560 -1000 -560 700 {lab=Va}
N -500 340 -500 2040 {lab=Vss}
N -440 440 -440 2140 {lab=Iref}
N -380 500 -380 2200 {lab=D_p}
N -320 560 -320 2260 {lab=D_n}
N -560 -1000 200 -1000 {lab=Va}
N -40 340 200 340 {lab=Vss}
N -380 500 60 500 {lab=D_p}
N -320 560 20 560 {lab=D_n}
N -120 440 -20 440 {lab=Iref}
N -80 340 -40 340 {lab=Vss}
N -440 440 -120 440 {lab=Iref}
N -500 340 -80 340 {lab=Vss}
N -560 700 200 700 {lab=Va}
N -500 2040 200 2040 {lab=Vss}
N -320 2260 60 2260 {lab=D_n}
N -380 2200 20 2200 {lab=D_p}
N -440 2140 -20 2140 {lab=Iref}
N 200 -1000 1400 -1000 {lab=Va}
N 200 2040 1400 2040 {lab=Vss}
C {predriver_comp.sym} 200 0 0 0 {name=Xkpm}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -100 60 0 0 {name=Mref
l=0.5u
w=8u
 ng=1
 m=1
  mm_ok=1
 model=sg13_hv_nmos
spiceprefix=X
}
C {predriver_comp.sym} 200 1700 0 0 {name=Xknm}
C {predriver_stage.sym} 1400 850 0 0 {name=Xstm}
C {iopin.sym} -560 -1000 0 0 {name=p_Va lab=Va}
C {iopin.sym} -500 2040 0 0 {name=p_Vss lab=Vss}
C {ipin.sym} -440 440 0 0 {name=p_Iref lab=Iref}
C {ipin.sym} -380 500 0 0 {name=p_D_p lab=D_p}
C {ipin.sym} -320 560 0 0 {name=p_D_n lab=D_n}
C {opin.sym} 3000 830 0 0 {name=p_In_p lab=In_p}
C {opin.sym} 3000 870 0 0 {name=p_In_n lab=In_n}
