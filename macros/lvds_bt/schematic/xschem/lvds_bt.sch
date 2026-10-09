v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {lvds_bt - switchable back-termination of the LVDS pair, ~200 ohm differential

  EN = 1   R1 + MSW + R2 ~ 200 ohm from OUTP to OUTN (MSW's gate at 3.3 V through xls)
  EN = 0   off: the pair sees R1 / R2 and MSW's junctions, no current

The driver is a current source: without this, a wave coming back from the receiver
is thrown back whole.  With it, two thirds are absorbed.  The pair then sees
100 || 200 = 67 ohm - ibias1 3 uA instead of 2 uA keeps |Vod|.} -520 -980 0 0 0.4 0.4 {}
C {devices/iopin.sym} -200 -620 2 0 {name=p_OUTP lab=OUTP}
N -200 -620 0 -620 {lab=OUTP}
N 0 -620 0 -550 {lab=OUTP}
C {sg13cmos5l_pr/rppd.sym} 0 -520 0 0 {name=R1
w=10u
l=3.3u
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
mm_ok=1
value=\"expr_eng(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )\"}
T {93 ohm, 10 um wide} 30 -550 0 0 0.35 0.35 {}
N 0 -490 0 -300 {lab=A}
C {devices/lab_wire.sym} 0 -400 0 0 {name=w1 sig_type=std_logic lab=A}
C {sg13cmos5l_pr/sg13_hv_nmos.sym} -20 -270 0 0 {name=MSW
l=0.45u
w=300u
ng=30
m=1
mm_ok=1
model=sg13_hv_nmos
spiceprefix=X}
N 0 -270 40 -270 {}
C {devices/lab_pin.sym} 40 -270 0 1 {name=l2 sig_type=std_logic lab=VSS}
T {300/0.45 HV, 30 fingers:
~11 ohm with S/D at 1.2 V} 40 -330 0 0 0.35 0.35 {}
N 0 -240 0 -170 {lab=B}
C {devices/lab_wire.sym} 0 -200 0 0 {name=w3 sig_type=std_logic lab=B}
C {sg13cmos5l_pr/rppd.sym} 0 -140 0 0 {name=R2
w=10u
l=3.3u
model=rppd
body=VSS
spiceprefix=X
b=0
m=1
mm_ok=1
value=\"expr_eng(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )\"}
N 0 -110 0 -60 {lab=OUTN}
N 0 -60 -200 -60 {lab=OUTN}
C {devices/iopin.sym} -200 -60 2 0 {name=p_OUTN lab=OUTN}
C {devices/ipin.sym} -520 -270 2 1 {name=p_EN lab=EN}
N -520 -270 -330 -270 {lab=EN}
C {ref_odt_lvlup.sym} -250 -270 0 0 {name=xls}
N -170 -270 -40 -270 {lab=ENH}
C {devices/lab_wire.sym} -110 -270 0 0 {name=w4 sig_type=std_logic lab=ENH}
N -290 -330 -290 -360 {}
C {devices/lab_pin.sym} -290 -360 0 0 {name=l5 sig_type=std_logic lab=VDD}
N -210 -330 -210 -360 {}
C {devices/lab_pin.sym} -210 -360 0 0 {name=l6 sig_type=std_logic lab=VDDH}
N -250 -210 -250 -180 {}
C {devices/lab_pin.sym} -250 -180 0 0 {name=l7 sig_type=std_logic lab=VSS}
C {sg13cmos5l_pr/dantenna.sym} -420 -210 0 0 {name=DEN
model=dantenna
l=0.78u
w=0.78u
spiceprefix=X}
N -420 -240 -420 -270 {lab=EN}
C {devices/lab_pin.sym} -420 -180 0 0 {name=l8 sig_type=std_logic lab=VSS}
T {DEN: antenna diode
on the long EN line} -470 -150 0 0 0.35 0.35 {}
C {devices/iopin.sym} -520 40 2 0 {name=p_VDD lab=VDD}
N -520 40 -480 40 {lab=VDD}
C {devices/lab_pin.sym} -480 40 0 1 {name=l9 sig_type=std_logic lab=VDD}
C {devices/iopin.sym} -520 80 2 0 {name=p_VDDH lab=VDDH}
N -520 80 -480 80 {lab=VDDH}
C {devices/lab_pin.sym} -480 80 0 1 {name=l10 sig_type=std_logic lab=VDDH}
C {devices/iopin.sym} -520 120 2 0 {name=p_VSS lab=VSS}
N -520 120 -480 120 {lab=VSS}
C {devices/lab_pin.sym} -480 120 0 1 {name=l11 sig_type=std_logic lab=VSS}
