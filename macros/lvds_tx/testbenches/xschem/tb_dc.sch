v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Static generator clauses - 4.1.1 full load, 4.1.2 offset and balance, 4.1.3 short circuit.

Each clause compares one generator in BOTH binary states, so every test appears twice: an
ON cell (In_p low -> Out_p positive, binary 0) and an OFF cell. Reading a pair of cells off
one operating point is what makes |VT|-|VT*| and |VOS-VOS*| meaningful.

  X1 / X2   4.1.1  100 ohm across the outputs plus 3.74 k from each to VTEST, swept 0..2.4 V.
                   The 3.74 k pair models 32 receivers biasing the bus - this is the test
                   that actually stresses the common-mode loop, and Vos should barely move.
  X3 / X4   4.1.2  two matched 49.9 ohm, Vos at the centre tap.
  X5 / X6   4.1.3  both outputs shorted to circuit common through 0 V ammeters (Isa, Isb).
  X7 / X8   4.1.3  outputs shorted to each other (Isab).

The inputs are tied to fixed levels because all three clauses are steady-state, and the
delayed pair carries the same data as the undelayed one in steady state.

CAUTION: the two states are separate driver instances here. That is correct for a matched
run, but it makes the balance limits meaningless under mismatch, where the two copies would
draw independent random values and measure the spread between two chips instead of the
asymmetry within one. For mismatch use compliance/run.sh with MC=<n>, which toggles a single
instance instead.} -500 -1560 0 0 0.4 0.4 {}
T {X1  ON (binary 0)  full} 120 -260 0 0 0.3 0.3 {}
T {X2  OFF (binary 1)  full} 120 140 0 0 0.3 0.3 {}
T {X3  ON (binary 0)  off} 120 540 0 0 0.3 0.3 {}
T {X4  OFF (binary 1)  off} 120 940 0 0 0.3 0.3 {}
T {X5  ON (binary 0)  shortc} 120 1340 0 0 0.3 0.3 {}
T {X6  OFF (binary 1)  shortc} 120 1740 0 0 0.3 0.3 {}
T {X7  ON (binary 0)  shortab} 120 2140 0 0 0.3 0.3 {}
T {X8  OFF (binary 1)  shortab} 120 2540 0 0 0.3 0.3 {}
N -900 -1200 -900 -1170 {lab=HI}
N -900 -1110 -900 -1080 {lab=0}
N -700 -1200 -700 -1170 {lab=VREF}
N -700 -1110 -700 -1080 {lab=0}
N -500 -1200 -500 -1170 {lab=VTEST}
N -500 -1110 -500 -1080 {lab=0}
N -1100 -1140 -1100 -1080 {lab=LO}
N -1300 -1200 -1300 -1170 {lab=VDD}
N -1300 -1110 -1300 -1080 {lab=0}
N 520 -200 540 -200 {lab=VDD}
N 540 -220 540 -200 {lab=VDD}
N 520 -140 540 -140 {lab=0}
N 540 -140 540 -120 {lab=0}
N 180 -200 220 -200 {lab=LO}
N 180 -180 220 -180 {lab=HI}
N 180 -120 220 -120 {lab=LO}
N 180 -100 220 -100 {lab=HI}
N 80 -160 220 -160 {lab=Iref1}
N 80 -160 80 -140 {lab=Iref1}
N 80 -80 80 -60 {lab=0}
N 160 -140 220 -140 {lab=VREF}
N 820 -180 1700 -180 {lab=Op1}
N 520 -160 580 -160 {lab=On1}
N 580 -160 580 -60 {lab=On1}
N 1120 -60 1700 -60 {lab=On1}
N 820 -290 820 -180 {lab=Op1}
N 980 -310 980 -290 {lab=VDD}
N 980 -250 980 -230 {lab=0}
N 1120 -60 1120 30 {lab=On1}
N 1280 10 1280 30 {lab=VDD}
N 1280 70 1280 90 {lab=0}
N 1700 -180 1700 -150 {lab=Op1}
N 1700 -90 1700 -60 {lab=On1}
N 1900 -210 1900 -180 {lab=Op1}
N 1700 -180 1900 -180 {lab=Op1}
N 1900 -300 1900 -270 {lab=VTEST}
N 2100 -90 2100 -60 {lab=On1}
N 1700 -60 2100 -60 {lab=On1}
N 2100 -300 2100 -150 {lab=VTEST}
N 520 200 540 200 {lab=VDD}
N 540 180 540 200 {lab=VDD}
N 520 260 540 260 {lab=0}
N 540 260 540 280 {lab=0}
N 180 200 220 200 {lab=HI}
N 180 220 220 220 {lab=LO}
N 180 280 220 280 {lab=HI}
N 180 300 220 300 {lab=LO}
N 80 240 220 240 {lab=Iref2}
N 80 240 80 260 {lab=Iref2}
N 80 320 80 340 {lab=0}
N 160 260 220 260 {lab=VREF}
N 820 220 1700 220 {lab=Op2}
N 520 240 580 240 {lab=On2}
N 580 240 580 340 {lab=On2}
N 1120 340 1700 340 {lab=On2}
N 820 110 820 220 {lab=Op2}
N 980 90 980 110 {lab=VDD}
N 980 150 980 170 {lab=0}
N 1120 340 1120 430 {lab=On2}
N 1280 410 1280 430 {lab=VDD}
N 1280 470 1280 490 {lab=0}
N 1700 220 1700 250 {lab=Op2}
N 1700 310 1700 340 {lab=On2}
N 1900 190 1900 220 {lab=Op2}
N 1700 220 1900 220 {lab=Op2}
N 1900 100 1900 130 {lab=VTEST}
N 2100 310 2100 340 {lab=On2}
N 1700 340 2100 340 {lab=On2}
N 2100 100 2100 250 {lab=VTEST}
N 520 600 540 600 {lab=VDD}
N 540 580 540 600 {lab=VDD}
N 520 660 540 660 {lab=0}
N 540 660 540 680 {lab=0}
N 180 600 220 600 {lab=LO}
N 180 620 220 620 {lab=HI}
N 180 680 220 680 {lab=LO}
N 180 700 220 700 {lab=HI}
N 80 640 220 640 {lab=Iref3}
N 80 640 80 660 {lab=Iref3}
N 80 720 80 740 {lab=0}
N 160 660 220 660 {lab=VREF}
N 820 620 1700 620 {lab=Op3}
N 520 640 580 640 {lab=On3}
N 580 640 580 740 {lab=On3}
N 1120 740 1700 740 {lab=On3}
N 820 510 820 620 {lab=Op3}
N 980 490 980 510 {lab=VDD}
N 980 550 980 570 {lab=0}
N 1120 740 1120 830 {lab=On3}
N 1280 810 1280 830 {lab=VDD}
N 1280 870 1280 890 {lab=0}
N 520 1000 540 1000 {lab=VDD}
N 540 980 540 1000 {lab=VDD}
N 520 1060 540 1060 {lab=0}
N 540 1060 540 1080 {lab=0}
N 180 1000 220 1000 {lab=HI}
N 180 1020 220 1020 {lab=LO}
N 180 1080 220 1080 {lab=HI}
N 180 1100 220 1100 {lab=LO}
N 80 1040 220 1040 {lab=Iref4}
N 80 1040 80 1060 {lab=Iref4}
N 80 1120 80 1140 {lab=0}
N 160 1060 220 1060 {lab=VREF}
N 820 1020 1700 1020 {lab=Op4}
N 520 1040 580 1040 {lab=On4}
N 580 1040 580 1140 {lab=On4}
N 1120 1140 1700 1140 {lab=On4}
N 820 910 820 1020 {lab=Op4}
N 980 890 980 910 {lab=VDD}
N 980 950 980 970 {lab=0}
N 1120 1140 1120 1230 {lab=On4}
N 1280 1210 1280 1230 {lab=VDD}
N 1280 1270 1280 1290 {lab=0}
N 520 1400 540 1400 {lab=VDD}
N 540 1380 540 1400 {lab=VDD}
N 520 1460 540 1460 {lab=0}
N 540 1460 540 1480 {lab=0}
N 180 1400 220 1400 {lab=LO}
N 180 1420 220 1420 {lab=HI}
N 180 1480 220 1480 {lab=LO}
N 180 1500 220 1500 {lab=HI}
N 80 1440 220 1440 {lab=Iref5}
N 80 1440 80 1460 {lab=Iref5}
N 80 1520 80 1540 {lab=0}
N 160 1460 220 1460 {lab=VREF}
N 820 1420 1700 1420 {lab=Op5}
N 520 1440 580 1440 {lab=On5}
N 580 1440 580 1540 {lab=On5}
N 1120 1540 1900 1540 {lab=On5}
N 820 1310 820 1420 {lab=Op5}
N 980 1290 980 1310 {lab=VDD}
N 980 1350 980 1370 {lab=0}
N 1120 1540 1120 1630 {lab=On5}
N 1280 1610 1280 1630 {lab=VDD}
N 1280 1670 1280 1690 {lab=0}
N 1700 1480 1700 1500 {lab=0}
N 1900 1600 1900 1620 {lab=0}
N 520 1800 540 1800 {lab=VDD}
N 540 1780 540 1800 {lab=VDD}
N 520 1860 540 1860 {lab=0}
N 540 1860 540 1880 {lab=0}
N 180 1800 220 1800 {lab=HI}
N 180 1820 220 1820 {lab=LO}
N 180 1880 220 1880 {lab=HI}
N 180 1900 220 1900 {lab=LO}
N 80 1840 220 1840 {lab=Iref6}
N 80 1840 80 1860 {lab=Iref6}
N 80 1920 80 1940 {lab=0}
N 160 1860 220 1860 {lab=VREF}
N 820 1820 1700 1820 {lab=Op6}
N 520 1840 580 1840 {lab=On6}
N 580 1840 580 1940 {lab=On6}
N 1120 1940 1900 1940 {lab=On6}
N 820 1710 820 1820 {lab=Op6}
N 980 1690 980 1710 {lab=VDD}
N 980 1750 980 1770 {lab=0}
N 1120 1940 1120 2030 {lab=On6}
N 1280 2010 1280 2030 {lab=VDD}
N 1280 2070 1280 2090 {lab=0}
N 1700 1880 1700 1900 {lab=0}
N 1900 2000 1900 2020 {lab=0}
N 520 2200 540 2200 {lab=VDD}
N 540 2180 540 2200 {lab=VDD}
N 520 2260 540 2260 {lab=0}
N 540 2260 540 2280 {lab=0}
N 180 2200 220 2200 {lab=LO}
N 180 2220 220 2220 {lab=HI}
N 180 2280 220 2280 {lab=LO}
N 180 2300 220 2300 {lab=HI}
N 80 2240 220 2240 {lab=Iref7}
N 80 2240 80 2260 {lab=Iref7}
N 80 2320 80 2340 {lab=0}
N 160 2260 220 2260 {lab=VREF}
N 820 2220 1700 2220 {lab=Op7}
N 520 2240 580 2240 {lab=On7}
N 580 2240 580 2340 {lab=On7}
N 1120 2340 1700 2340 {lab=On7}
N 820 2110 820 2220 {lab=Op7}
N 980 2090 980 2110 {lab=VDD}
N 980 2150 980 2170 {lab=0}
N 1120 2340 1120 2430 {lab=On7}
N 1280 2410 1280 2430 {lab=VDD}
N 1280 2470 1280 2490 {lab=0}
N 1700 2220 1700 2250 {lab=Op7}
N 1700 2310 1700 2340 {lab=On7}
N 520 2600 540 2600 {lab=VDD}
N 540 2580 540 2600 {lab=VDD}
N 520 2660 540 2660 {lab=0}
N 540 2660 540 2680 {lab=0}
N 180 2600 220 2600 {lab=HI}
N 180 2620 220 2620 {lab=LO}
N 180 2680 220 2680 {lab=HI}
N 180 2700 220 2700 {lab=LO}
N 80 2640 220 2640 {lab=Iref8}
N 80 2640 80 2660 {lab=Iref8}
N 80 2720 80 2740 {lab=0}
N 160 2660 220 2660 {lab=VREF}
N 820 2620 1700 2620 {lab=Op8}
N 520 2640 580 2640 {lab=On8}
N 580 2640 580 2740 {lab=On8}
N 1120 2740 1700 2740 {lab=On8}
N 820 2510 820 2620 {lab=Op8}
N 980 2490 980 2510 {lab=VDD}
N 980 2550 980 2570 {lab=0}
N 1120 2740 1120 2830 {lab=On8}
N 1280 2810 1280 2830 {lab=VDD}
N 1280 2870 1280 2890 {lab=0}
N 1700 2620 1700 2650 {lab=Op8}
N 1700 2710 1700 2740 {lab=On8}
N 520 -180 820 -180 {lab=Op1}
N 580 -60 1120 -60 {lab=On1}
N 520 220 820 220 {lab=Op2}
N 580 340 1120 340 {lab=On2}
N 520 620 820 620 {lab=Op3}
N 580 740 1120 740 {lab=On3}
N 520 1020 820 1020 {lab=Op4}
N 580 1140 1120 1140 {lab=On4}
N 520 1420 820 1420 {lab=Op5}
N 580 1540 1120 1540 {lab=On5}
N 520 1820 820 1820 {lab=Op6}
N 580 1940 1120 1940 {lab=On6}
N 520 2220 820 2220 {lab=Op7}
N 580 2340 1120 2340 {lab=On7}
N 520 2620 820 2620 {lab=Op8}
N 580 2740 1120 2740 {lab=On8}
C {vsource.sym} -1300 -1140 0 0 {name=Vdd value=3.3 savecurrent=false}
C {vdd.sym} -1300 -1200 0 0 {name=pz lab=VDD}
C {gnd.sym} -1300 -1080 0 0 {name=gz lab=0}
C {vsource.sym} -900 -1140 0 0 {name=Vhi value=3.3 savecurrent=false}
C {vsource.sym} -700 -1140 0 0 {name=Vrf value=1.2 savecurrent=false}
C {vsource.sym} -500 -1140 0 0 {name=Vtst value=1.2 savecurrent=false}
C {lab_pin.sym} -900 -1200 0 0 {name=pa lab=HI}
C {lab_pin.sym} -700 -1200 0 0 {name=pb lab=VREF}
C {lab_pin.sym} -500 -1200 0 0 {name=pc lab=VTEST}
C {lab_pin.sym} -1100 -1140 0 0 {name=pd lab=LO}
C {gnd.sym} -900 -1080 0 0 {name=ga lab=0}
C {gnd.sym} -700 -1080 0 0 {name=gb lab=0}
C {gnd.sym} -500 -1080 0 0 {name=gc lab=0}
C {gnd.sym} -1100 -1080 0 0 {name=gd lab=0}
C {Driver.sym} 370 -170 0 0 {name=X1}
C {vdd.sym} 540 -220 0 0 {name=lv1 lab=VDD}
C {gnd.sym} 540 -120 0 0 {name=lg1 lab=0}
C {lab_pin.sym} 180 -200 0 0 {name=pi1a lab=LO}
C {lab_pin.sym} 180 -180 0 0 {name=pi1b lab=HI}
C {lab_pin.sym} 180 -120 0 0 {name=pi1c lab=LO}
C {lab_pin.sym} 180 -100 0 0 {name=pi1d lab=HI}
C {isource.sym} 80 -110 0 0 {name=I1 value=-30u}
C {gnd.sym} 80 -60 0 0 {name=lb1 lab=0}
C {lab_pin.sym} 160 -140 0 0 {name=pr1 lab=VREF}
C {lab_pin.sym} 700 -180 0 0 {name=po1 lab=Op1}
C {lab_pin.sym} 700 -60 0 0 {name=pq1 lab=On1}
C {esdpad.sym} 900 -280 0 0 {name=Xp1}
C {vdd.sym} 980 -310 0 0 {name=lw1 lab=VDD}
C {gnd.sym} 980 -230 0 0 {name=lh1 lab=0}
C {esdpad.sym} 1200 40 0 0 {name=Xn1}
C {vdd.sym} 1280 10 0 0 {name=lx1 lab=VDD}
C {gnd.sym} 1280 90 0 0 {name=li1 lab=0}
C {res.sym} 1700 -120 0 0 {name=RL1
value=100
footprint=1206
device=resistor
m=1}
C {res.sym} 1900 -240 0 0 {name=Ra1
value=3.74k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 1900 -300 0 0 {name=pt1 lab=VTEST}
C {res.sym} 2100 -120 0 0 {name=Rb1
value=3.74k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 2100 -300 0 0 {name=tu1 lab=VTEST}
C {Driver.sym} 370 230 0 0 {name=X2}
C {vdd.sym} 540 180 0 0 {name=lv2 lab=VDD}
C {gnd.sym} 540 280 0 0 {name=lg2 lab=0}
C {lab_pin.sym} 180 200 0 0 {name=pi2a lab=HI}
C {lab_pin.sym} 180 220 0 0 {name=pi2b lab=LO}
C {lab_pin.sym} 180 280 0 0 {name=pi2c lab=HI}
C {lab_pin.sym} 180 300 0 0 {name=pi2d lab=LO}
C {isource.sym} 80 290 0 0 {name=I2 value=-30u}
C {gnd.sym} 80 340 0 0 {name=lb2 lab=0}
C {lab_pin.sym} 160 260 0 0 {name=pr2 lab=VREF}
C {lab_pin.sym} 700 220 0 0 {name=po2 lab=Op2}
C {lab_pin.sym} 700 340 0 0 {name=pq2 lab=On2}
C {esdpad.sym} 900 120 0 0 {name=Xp2}
C {vdd.sym} 980 90 0 0 {name=lw2 lab=VDD}
C {gnd.sym} 980 170 0 0 {name=lh2 lab=0}
C {esdpad.sym} 1200 440 0 0 {name=Xn2}
C {vdd.sym} 1280 410 0 0 {name=lx2 lab=VDD}
C {gnd.sym} 1280 490 0 0 {name=li2 lab=0}
C {res.sym} 1700 280 0 0 {name=RL2
value=100
footprint=1206
device=resistor
m=1}
C {res.sym} 1900 160 0 0 {name=Ra2
value=3.74k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 1900 100 0 0 {name=pt2 lab=VTEST}
C {res.sym} 2100 280 0 0 {name=Rb2
value=3.74k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 2100 100 0 0 {name=tu2 lab=VTEST}
C {Driver.sym} 370 630 0 0 {name=X3}
C {vdd.sym} 540 580 0 0 {name=lv3 lab=VDD}
C {gnd.sym} 540 680 0 0 {name=lg3 lab=0}
C {lab_pin.sym} 180 600 0 0 {name=pi3a lab=LO}
C {lab_pin.sym} 180 620 0 0 {name=pi3b lab=HI}
C {lab_pin.sym} 180 680 0 0 {name=pi3c lab=LO}
C {lab_pin.sym} 180 700 0 0 {name=pi3d lab=HI}
C {isource.sym} 80 690 0 0 {name=I3 value=-30u}
C {gnd.sym} 80 740 0 0 {name=lb3 lab=0}
C {lab_pin.sym} 160 660 0 0 {name=pr3 lab=VREF}
C {lab_pin.sym} 700 620 0 0 {name=po3 lab=Op3}
C {lab_pin.sym} 700 740 0 0 {name=pq3 lab=On3}
C {esdpad.sym} 900 520 0 0 {name=Xp3}
C {vdd.sym} 980 490 0 0 {name=lw3 lab=VDD}
C {gnd.sym} 980 570 0 0 {name=lh3 lab=0}
C {esdpad.sym} 1200 840 0 0 {name=Xn3}
C {vdd.sym} 1280 810 0 0 {name=lx3 lab=VDD}
C {gnd.sym} 1280 890 0 0 {name=li3 lab=0}
C {res.sym} 1700 650 0 0 {name=Rp3
value=49.9
footprint=1206
device=resistor
m=1}
C {res.sym} 1700 710 0 0 {name=Rn3
value=49.9
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 1700 680 0 0 {name=pv3 lab=Vos3}
C {Driver.sym} 370 1030 0 0 {name=X4}
C {vdd.sym} 540 980 0 0 {name=lv4 lab=VDD}
C {gnd.sym} 540 1080 0 0 {name=lg4 lab=0}
C {lab_pin.sym} 180 1000 0 0 {name=pi4a lab=HI}
C {lab_pin.sym} 180 1020 0 0 {name=pi4b lab=LO}
C {lab_pin.sym} 180 1080 0 0 {name=pi4c lab=HI}
C {lab_pin.sym} 180 1100 0 0 {name=pi4d lab=LO}
C {isource.sym} 80 1090 0 0 {name=I4 value=-30u}
C {gnd.sym} 80 1140 0 0 {name=lb4 lab=0}
C {lab_pin.sym} 160 1060 0 0 {name=pr4 lab=VREF}
C {lab_pin.sym} 700 1020 0 0 {name=po4 lab=Op4}
C {lab_pin.sym} 700 1140 0 0 {name=pq4 lab=On4}
C {esdpad.sym} 900 920 0 0 {name=Xp4}
C {vdd.sym} 980 890 0 0 {name=lw4 lab=VDD}
C {gnd.sym} 980 970 0 0 {name=lh4 lab=0}
C {esdpad.sym} 1200 1240 0 0 {name=Xn4}
C {vdd.sym} 1280 1210 0 0 {name=lx4 lab=VDD}
C {gnd.sym} 1280 1290 0 0 {name=li4 lab=0}
C {res.sym} 1700 1050 0 0 {name=Rp4
value=49.9
footprint=1206
device=resistor
m=1}
C {res.sym} 1700 1110 0 0 {name=Rn4
value=49.9
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 1700 1080 0 0 {name=pv4 lab=Vos4}
C {Driver.sym} 370 1430 0 0 {name=X5}
C {vdd.sym} 540 1380 0 0 {name=lv5 lab=VDD}
C {gnd.sym} 540 1480 0 0 {name=lg5 lab=0}
C {lab_pin.sym} 180 1400 0 0 {name=pi5a lab=LO}
C {lab_pin.sym} 180 1420 0 0 {name=pi5b lab=HI}
C {lab_pin.sym} 180 1480 0 0 {name=pi5c lab=LO}
C {lab_pin.sym} 180 1500 0 0 {name=pi5d lab=HI}
C {isource.sym} 80 1490 0 0 {name=I5 value=-30u}
C {gnd.sym} 80 1540 0 0 {name=lb5 lab=0}
C {lab_pin.sym} 160 1460 0 0 {name=pr5 lab=VREF}
C {lab_pin.sym} 700 1420 0 0 {name=po5 lab=Op5}
C {lab_pin.sym} 700 1540 0 0 {name=pq5 lab=On5}
C {esdpad.sym} 900 1320 0 0 {name=Xp5}
C {vdd.sym} 980 1290 0 0 {name=lw5 lab=VDD}
C {gnd.sym} 980 1370 0 0 {name=lh5 lab=0}
C {esdpad.sym} 1200 1640 0 0 {name=Xn5}
C {vdd.sym} 1280 1610 0 0 {name=lx5 lab=VDD}
C {gnd.sym} 1280 1690 0 0 {name=li5 lab=0}
C {vsource.sym} 1700 1450 0 0 {name=Vsa5 value=0 savecurrent=true}
C {gnd.sym} 1700 1500 0 0 {name=ls5 lab=0}
C {vsource.sym} 1900 1570 0 0 {name=Vsb5 value=0 savecurrent=true}
C {gnd.sym} 1900 1620 0 0 {name=lt5 lab=0}
C {Driver.sym} 370 1830 0 0 {name=X6}
C {vdd.sym} 540 1780 0 0 {name=lv6 lab=VDD}
C {gnd.sym} 540 1880 0 0 {name=lg6 lab=0}
C {lab_pin.sym} 180 1800 0 0 {name=pi6a lab=HI}
C {lab_pin.sym} 180 1820 0 0 {name=pi6b lab=LO}
C {lab_pin.sym} 180 1880 0 0 {name=pi6c lab=HI}
C {lab_pin.sym} 180 1900 0 0 {name=pi6d lab=LO}
C {isource.sym} 80 1890 0 0 {name=I6 value=-30u}
C {gnd.sym} 80 1940 0 0 {name=lb6 lab=0}
C {lab_pin.sym} 160 1860 0 0 {name=pr6 lab=VREF}
C {lab_pin.sym} 700 1820 0 0 {name=po6 lab=Op6}
C {lab_pin.sym} 700 1940 0 0 {name=pq6 lab=On6}
C {esdpad.sym} 900 1720 0 0 {name=Xp6}
C {vdd.sym} 980 1690 0 0 {name=lw6 lab=VDD}
C {gnd.sym} 980 1770 0 0 {name=lh6 lab=0}
C {esdpad.sym} 1200 2040 0 0 {name=Xn6}
C {vdd.sym} 1280 2010 0 0 {name=lx6 lab=VDD}
C {gnd.sym} 1280 2090 0 0 {name=li6 lab=0}
C {vsource.sym} 1700 1850 0 0 {name=Vsa6 value=0 savecurrent=true}
C {gnd.sym} 1700 1900 0 0 {name=ls6 lab=0}
C {vsource.sym} 1900 1970 0 0 {name=Vsb6 value=0 savecurrent=true}
C {gnd.sym} 1900 2020 0 0 {name=lt6 lab=0}
C {Driver.sym} 370 2230 0 0 {name=X7}
C {vdd.sym} 540 2180 0 0 {name=lv7 lab=VDD}
C {gnd.sym} 540 2280 0 0 {name=lg7 lab=0}
C {lab_pin.sym} 180 2200 0 0 {name=pi7a lab=LO}
C {lab_pin.sym} 180 2220 0 0 {name=pi7b lab=HI}
C {lab_pin.sym} 180 2280 0 0 {name=pi7c lab=LO}
C {lab_pin.sym} 180 2300 0 0 {name=pi7d lab=HI}
C {isource.sym} 80 2290 0 0 {name=I7 value=-30u}
C {gnd.sym} 80 2340 0 0 {name=lb7 lab=0}
C {lab_pin.sym} 160 2260 0 0 {name=pr7 lab=VREF}
C {lab_pin.sym} 700 2220 0 0 {name=po7 lab=Op7}
C {lab_pin.sym} 700 2340 0 0 {name=pq7 lab=On7}
C {esdpad.sym} 900 2120 0 0 {name=Xp7}
C {vdd.sym} 980 2090 0 0 {name=lw7 lab=VDD}
C {gnd.sym} 980 2170 0 0 {name=lh7 lab=0}
C {esdpad.sym} 1200 2440 0 0 {name=Xn7}
C {vdd.sym} 1280 2410 0 0 {name=lx7 lab=VDD}
C {gnd.sym} 1280 2490 0 0 {name=li7 lab=0}
C {vsource.sym} 1700 2280 0 0 {name=Vsab7 value=0 savecurrent=true}
C {Driver.sym} 370 2630 0 0 {name=X8}
C {vdd.sym} 540 2580 0 0 {name=lv8 lab=VDD}
C {gnd.sym} 540 2680 0 0 {name=lg8 lab=0}
C {lab_pin.sym} 180 2600 0 0 {name=pi8a lab=HI}
C {lab_pin.sym} 180 2620 0 0 {name=pi8b lab=LO}
C {lab_pin.sym} 180 2680 0 0 {name=pi8c lab=HI}
C {lab_pin.sym} 180 2700 0 0 {name=pi8d lab=LO}
C {isource.sym} 80 2690 0 0 {name=I8 value=-30u}
C {gnd.sym} 80 2740 0 0 {name=lb8 lab=0}
C {lab_pin.sym} 160 2660 0 0 {name=pr8 lab=VREF}
C {lab_pin.sym} 700 2620 0 0 {name=po8 lab=Op8}
C {lab_pin.sym} 700 2740 0 0 {name=pq8 lab=On8}
C {esdpad.sym} 900 2520 0 0 {name=Xp8}
C {vdd.sym} 980 2490 0 0 {name=lw8 lab=VDD}
C {gnd.sym} 980 2570 0 0 {name=lh8 lab=0}
C {esdpad.sym} 1200 2840 0 0 {name=Xn8}
C {vdd.sym} 1280 2810 0 0 {name=lx8 lab=VDD}
C {gnd.sym} 1280 2890 0 0 {name=li8 lab=0}
C {vsource.sym} 1700 2680 0 0 {name=Vsab8 value=0 savecurrent=true}
C {simulator_commands_shown.sym} -1100 -900 0 0 {
name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib
"
      }
C {simulator_commands_shown.sym} -1100 -700 0 0 {name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.control
save all
dc Vtst 0 2.4 0.1
echo 4.1.1 full load VT VTstar and the difference, limits 247..454 mV and 50 mV
let vta = v(Op1)-v(On1)
let vtb = v(Op2)-v(On2)
let dvt = abs(abs(vta)-abs(vtb))
print vta vtb dvt
echo 4.1.2 offset Vos Vosstar and the difference, limits 1.125..1.375 V and 50 mV
let dvos = abs(v(Vos3)-v(Vos4))
print v(Vos3) v(Vos4) dvos
echo 4.1.3 short to common Isa Isb limit 24 mA
let isa  = abs(i(Vsa5))
let isb  = abs(i(Vsb5))
let isas = abs(i(Vsa6))
let isbs = abs(i(Vsb6))
print isa isb isas isbs
echo 4.1.3 outputs shorted together Isab limit 12 mA
let isab  = abs(i(Vsab7))
let isabs = abs(i(Vsab8))
print isab isabs
.endc
"}
