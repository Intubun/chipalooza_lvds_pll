v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {ref_odt - switchable 50 ohm termination of the ref_clk pad

  EN = 1   R1 + MSW = 50 ohm from PAD to VSS (MSW's gate at 3.3 V through xls)
  EN = 0   off: no current, ~0.25 pF on PAD

PAD is pad 2 itself (s14_an[2]) - not its secondary-protection output, where
~520 ohm in series would make the termination a divider.  R1 is the first thing
behind the pad, so it also limits what an ESD event drives into MSW's drain;
DN / DP clamp that node to VSS and VDDH.} -520 -900 0 0 0.4 0.4 {}
C {devices/iopin.sym} -200 -540 2 0 {name=p_PAD lab=PAD}
N -200 -540 0 -540 {lab=PAD}
N 0 -540 0 -470 {lab=PAD}
C {sg13cmos5l_pr/rppd.sym} 0 -440 0 0 {name=R1
w=40u
l=6.65u
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
mm_ok=1
value=\"expr_eng(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )\"}
T {45 ohm, 40 um wide:
24 mA and ESD} 30 -470 0 0 0.35 0.35 {}
N 0 -410 0 -300 {lab=X}
N 0 -380 260 -380 {lab=X}
C {devices/lab_wire.sym} 180 -380 0 0 {name=w1 sig_type=std_logic lab=X}
C {sg13cmos5l_pr/dantenna.sym} 120 -330 0 0 {name=DN
model=dantenna
l=1.26u
w=20u
spiceprefix=X}
N 120 -380 120 -360 {lab=X}
C {devices/lab_pin.sym} 120 -300 0 0 {name=l2 sig_type=std_logic lab=VSS}
C {sg13cmos5l_pr/dpantenna.sym} 260 -410 0 0 {name=DP
model=dpantenna
l=1.26u
w=20u
spiceprefix=X}
C {devices/lab_pin.sym} 260 -440 0 0 {name=l3 sig_type=std_logic lab=VDDH}
T {DN, DP: clamp X
to VSS / VDDH} 290 -360 0 0 0.35 0.35 {}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -20 -270 0 0 {name=MSW
l=0.45u
w=300u
ng=30
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
N 0 -270 40 -270 {}
C {devices/lab_pin.sym} 40 -270 0 1 {name=l4 sig_type=std_logic lab=VSS}
N 0 -240 0 -200 {}
C {devices/lab_pin.sym} 0 -200 0 0 {name=l5 sig_type=std_logic lab=VSS}
T {300/0.45 HV, 30 fingers:
~5 ohm at 3.3 V gate drive} 40 -230 0 0 0.35 0.35 {}
C {devices/ipin.sym} -520 -270 2 1 {name=p_EN lab=EN}
N -520 -270 -330 -270 {lab=EN}
C {ref_odt_lvlup.sym} -250 -270 0 0 {name=xls}
N -170 -270 -40 -270 {lab=ENH}
C {devices/lab_wire.sym} -110 -270 0 0 {name=w6 sig_type=std_logic lab=ENH}
N -290 -330 -290 -360 {}
C {devices/lab_pin.sym} -290 -360 0 0 {name=l7 sig_type=std_logic lab=VDD}
N -210 -330 -210 -360 {}
C {devices/lab_pin.sym} -210 -360 0 0 {name=l8 sig_type=std_logic lab=VDDH}
N -250 -210 -250 -180 {}
C {devices/lab_pin.sym} -250 -180 0 0 {name=l9 sig_type=std_logic lab=VSS}
C {sg13cmos5l_pr/dantenna.sym} -420 -210 0 0 {name=DEN
model=dantenna
l=0.78u
w=0.78u
spiceprefix=X}
N -420 -240 -420 -270 {lab=EN}
C {devices/lab_pin.sym} -420 -180 0 0 {name=l10 sig_type=std_logic lab=VSS}
T {DEN: antenna diode
on the long EN line} -470 -150 0 0 0.35 0.35 {}
C {devices/iopin.sym} -520 -40 2 0 {name=p_VDD lab=VDD}
N -520 -40 -480 -40 {lab=VDD}
C {devices/lab_pin.sym} -480 -40 0 1 {name=l11 sig_type=std_logic lab=VDD}
C {devices/iopin.sym} -520 0 2 0 {name=p_VDDH lab=VDDH}
N -520 0 -480 0 {lab=VDDH}
C {devices/lab_pin.sym} -480 0 0 1 {name=l12 sig_type=std_logic lab=VDDH}
C {devices/iopin.sym} -520 40 2 0 {name=p_VSS lab=VSS}
N -520 40 -480 40 {lab=VSS}
C {devices/lab_pin.sym} -480 40 0 1 {name=l13 sig_type=std_logic lab=VSS}
