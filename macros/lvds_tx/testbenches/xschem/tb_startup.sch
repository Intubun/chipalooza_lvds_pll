v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {tb_startup  --  the cold start, without the .ic the others use

Every other testbench here begins with .ic v(xtx.xdrv.cmfb)=1.54, which puts
the common-mode loop at its operating point on the first timepoint.  This one
does not, so it shows what the transmitter does from a standing start.

WHY IT MATTERS: at t=0 both SerDes outputs are 0 V -- the digital solver has not
produced an event yet -- and two low inputs are a state the H-bridge cannot
balance.  The loop drives cmfb to the rail, the tail current shuts off, and both
outputs collapse to ground.  It recovers, but only at the 43 mV/ns the OTA can
slew into Cc, so a cold start costs about 60 ns before anything is worth
measuring.

That is real behaviour and not a simulation artefact: any power-up sequence that
presents both inputs low does the same thing on silicon.  On the harness the
per-project supply gates are what start this block, so this is the waveform that
follows a project being selected.

WHAT TO LOOK AT: Vos in the third graph, from zero.  t_cm in the log is when it
first reaches 1.15 V; vosend and cmfbend are where both have settled.

THE CHAIN, left to right:

  serdes.sch          the mixed-signal boundary: adc_bridge, one d_cosim
                      instance running serdes/serdes_dig.v, dac_bridge
  lvds_tx.sch         pre-driver and driver, wired to each other with drawn
                      wires inside.  D_p / D_n is the whole analog interface:
                      the serializer supplies data and no timing at all.
  esdpad.sym          ESD clamp plus pad capacitance, on both outputs
  2 x 49.9 ohm        the clause 4.1.2 test load, with the Vos tap

BUILD THE VERILOG FIRST, and again after every edit to serdes_dig.v.  ngspice
loads the compiled .so, never the .v, and an out-of-date .so simulates happily
and silently:

  docker exec iic-osic-tools_xserver bash -lc \\
    /foss/designs/chipalooza_lvds_pll/macros/lvds_tx/serdes/build_dig.sh

THE PIN LIST OF THE SERDES IS THE CHIPALOOZA #2 HARNESS SLOT, not a set of
convenient signals: Clk, Ena, DI23..DI0, DO11..DO0, all 1.2 V.  DI9 DI8 select
the pattern (00 word, 01 PRBS, 10 alternating, 11 static low), DI11 DI10 the
PRBS length (7 / 9 / 15 / 31), DI12 is the reset and DI13 swaps the output
pair.  DI23..DI14 are reserved and tied low, which is where the harness holds
them anyway.  Every DI source here is a plain DC source because on the real
part each of those bits is an SPI register field routed to a constant.
docs/harness-mapping.md is the map.

THREE THINGS THAT DO NOT ANNOUNCE THEMSELVES:

 *  d_cosim has a DEFAULT OUTPUT DELAY OF 1 ns.  The model card sets delay=1p.
    Without it every output of the Verilog arrives a nanosecond late -- one to
    three bits at these rates -- and the first nanosecond is lost outright.
 *  The reset is a PULSE that starts LOW and rises two bits in.  A level that
    is already high at t=0 never reaches the Verilog: input events around the
    start of the transient are missed, so the block comes up believing rst is
    asserted and sits in reset forever, emitting a flat line.
 *  Iref is a SEPARATE source per block, three in total.  Tying them together
    and feeding the sum does not give each block its share: the reference
    diodes sit in parallel and split by width, so a block ends up at a fraction
    of its bias while every digital waveform still looks perfect.

For corners, bit-error counts and recovered-clock sampling, use the headless
bench instead:
  docker exec iic-osic-tools_xserver bash -lc \\
    /foss/designs/chipalooza_lvds_pll/macros/lvds_tx/serdes/run.sh} -2600 -2600 0 0 0.4 0.4 {}
C {vsource.sym} -2500 -1300 0 0 {name=V0 value="3.3" savecurrent=false}
N -2500 -1330 -2440 -1330 {lab=VDD}
C {vdd.sym} -2440 -1330 0 0 {name=v1 lab=VDD}
N -2500 -1270 -2560 -1270 {lab=0}
C {gnd.sym} -2560 -1270 0 0 {name=g2 lab=0}
C {vsource.sym} -2300 -1300 0 0 {name=V1 value="PULSE(0 1.2 0 10p 10p 490p 1000p)" savecurrent=false}
N -2300 -1330 -2240 -1330 {lab=Clk}
C {lab_pin.sym} -2240 -1330 0 0 {name=l3 lab=Clk}
N -2300 -1270 -2360 -1270 {lab=0}
C {gnd.sym} -2360 -1270 0 0 {name=g4 lab=0}
T {bit clock: 1000 ps period = 1.00 Gb/s} -2400 -1420 0 0 0.3 0.3 {}
C {vsource.sym} -2100 -1300 0 0 {name=V2 value="PULSE(0 1.2 2000p 5p 5p 2000p 1u)" savecurrent=false}
N -2100 -1330 -2040 -1330 {lab=DI12}
C {lab_pin.sym} -2040 -1330 0 0 {name=l5 lab=DI12}
N -2100 -1270 -2160 -1270 {lab=0}
C {gnd.sym} -2160 -1270 0 0 {name=g6 lab=0}
T {DI12 reset: pulse at 2000..4000 ps, deliberately not at t=0} -2200 -1460 0 0 0.3 0.3 {}
C {vsource.sym} -1900 -1300 0 0 {name=V3 value="0.0" savecurrent=false}
N -1900 -1330 -1840 -1330 {lab=DI8}
C {lab_pin.sym} -1840 -1330 0 0 {name=l7 lab=DI8}
N -1900 -1270 -1960 -1270 {lab=0}
C {gnd.sym} -1960 -1270 0 0 {name=g8 lab=0}
C {vsource.sym} -1700 -1300 0 0 {name=V4 value="0.0" savecurrent=false}
N -1700 -1330 -1640 -1330 {lab=DI9}
C {lab_pin.sym} -1640 -1330 0 0 {name=l9 lab=DI9}
N -1700 -1270 -1760 -1270 {lab=0}
C {gnd.sym} -1760 -1270 0 0 {name=g10 lab=0}
T {DI9 DI8 = 00  parallel word} -1900 -1420 0 0 0.3 0.3 {}
C {vsource.sym} -1500 -1300 0 0 {name=V7 value="0.0" savecurrent=false}
N -1500 -1330 -1440 -1330 {lab=DI10}
C {lab_pin.sym} -1440 -1330 0 0 {name=l11 lab=DI10}
N -1500 -1270 -1560 -1270 {lab=0}
C {gnd.sym} -1560 -1270 0 0 {name=g12 lab=0}
C {vsource.sym} -1300 -1300 0 0 {name=V8 value="0.0" savecurrent=false}
N -1300 -1330 -1240 -1330 {lab=DI11}
C {lab_pin.sym} -1240 -1330 0 0 {name=l13 lab=DI11}
N -1300 -1270 -1360 -1270 {lab=0}
C {gnd.sym} -1360 -1270 0 0 {name=g14 lab=0}
T {DI11 DI10 = 00  PRBS length} -1500 -1380 0 0 0.3 0.3 {}
C {vsource.sym} -1100 -1300 0 0 {name=V9 value="0.0" savecurrent=false}
N -1100 -1330 -1040 -1330 {lab=DI13}
C {lab_pin.sym} -1040 -1330 0 0 {name=l15 lab=DI13}
N -1100 -1270 -1160 -1270 {lab=0}
C {gnd.sym} -1160 -1270 0 0 {name=g16 lab=0}
T {DI13 = 0  invert the pair} -1100 -1420 0 0 0.3 0.3 {}
C {vsource.sym} -2500 -1000 0 0 {name=VD7 value="1.2" savecurrent=false}
N -2500 -1030 -2440 -1030 {lab=DI7}
C {lab_pin.sym} -2440 -1030 0 0 {name=l17 lab=DI7}
N -2500 -970 -2560 -970 {lab=0}
C {gnd.sym} -2560 -970 0 0 {name=g18 lab=0}
C {vsource.sym} -2300 -1000 0 0 {name=VD6 value="0.0" savecurrent=false}
N -2300 -1030 -2240 -1030 {lab=DI6}
C {lab_pin.sym} -2240 -1030 0 0 {name=l19 lab=DI6}
N -2300 -970 -2360 -970 {lab=0}
C {gnd.sym} -2360 -970 0 0 {name=g20 lab=0}
C {vsource.sym} -2100 -1000 0 0 {name=VD5 value="1.2" savecurrent=false}
N -2100 -1030 -2040 -1030 {lab=DI5}
C {lab_pin.sym} -2040 -1030 0 0 {name=l21 lab=DI5}
N -2100 -970 -2160 -970 {lab=0}
C {gnd.sym} -2160 -970 0 0 {name=g22 lab=0}
C {vsource.sym} -1900 -1000 0 0 {name=VD4 value="1.2" savecurrent=false}
N -1900 -1030 -1840 -1030 {lab=DI4}
C {lab_pin.sym} -1840 -1030 0 0 {name=l23 lab=DI4}
N -1900 -970 -1960 -970 {lab=0}
C {gnd.sym} -1960 -970 0 0 {name=g24 lab=0}
C {vsource.sym} -1700 -1000 0 0 {name=VD3 value="0.0" savecurrent=false}
N -1700 -1030 -1640 -1030 {lab=DI3}
C {lab_pin.sym} -1640 -1030 0 0 {name=l25 lab=DI3}
N -1700 -970 -1760 -970 {lab=0}
C {gnd.sym} -1760 -970 0 0 {name=g26 lab=0}
C {vsource.sym} -1500 -1000 0 0 {name=VD2 value="1.2" savecurrent=false}
N -1500 -1030 -1440 -1030 {lab=DI2}
C {lab_pin.sym} -1440 -1030 0 0 {name=l27 lab=DI2}
N -1500 -970 -1560 -970 {lab=0}
C {gnd.sym} -1560 -970 0 0 {name=g28 lab=0}
C {vsource.sym} -1300 -1000 0 0 {name=VD1 value="0.0" savecurrent=false}
N -1300 -1030 -1240 -1030 {lab=DI1}
C {lab_pin.sym} -1240 -1030 0 0 {name=l29 lab=DI1}
N -1300 -970 -1360 -970 {lab=0}
C {gnd.sym} -1360 -970 0 0 {name=g30 lab=0}
C {vsource.sym} -1100 -1000 0 0 {name=VD0 value="0.0" savecurrent=false}
N -1100 -1030 -1040 -1030 {lab=DI0}
C {lab_pin.sym} -1040 -1030 0 0 {name=l31 lab=DI0}
N -1100 -970 -1160 -970 {lab=0}
C {gnd.sym} -1160 -970 0 0 {name=g32 lab=0}
T {parallel word DI7..DI0 = 0xB4} -2500 -1120 0 0 0.3 0.3 {}
C {vsource.sym} -700 -1300 0 0 {name=V5 value="1.25" savecurrent=false}
N -700 -1330 -640 -1330 {lab=Vref}
C {lab_pin.sym} -640 -1330 0 0 {name=l33 lab=Vref}
N -700 -1270 -760 -1270 {lab=0}
C {gnd.sym} -760 -1270 0 0 {name=g34 lab=0}
C {vsource.sym} -500 -1300 0 0 {name=V6 value="1.2" savecurrent=false}
N -500 -1330 -440 -1330 {lab=VDDC}
C {lab_pin.sym} -440 -1330 0 0 {name=l35 lab=VDDC}
N -500 -1270 -560 -1270 {lab=0}
C {gnd.sym} -560 -1270 0 0 {name=g36 lab=0}
T {1.2 V core rail: the digital bus levels} -700 -1420 0 0 0.3 0.3 {}
C {isource.sym} -300 -1300 0 0 {name=I0 value=-2u}
N -300 -1330 -240 -1330 {lab=Irf_pdd}
C {lab_pin.sym} -240 -1330 0 0 {name=l37 lab=Irf_pdd}
N -300 -1270 -360 -1270 {lab=0}
C {gnd.sym} -360 -1270 0 0 {name=g38 lab=0}
C {isource.sym} -100 -1300 0 0 {name=I1 value=-2u}
N -100 -1330 -40 -1330 {lab=Irf_drvd}
C {lab_pin.sym} -40 -1330 0 0 {name=l39 lab=Irf_drvd}
N -100 -1270 -160 -1270 {lab=0}
C {gnd.sym} -160 -1270 0 0 {name=g40 lab=0}
T {one 30 uA reference per block, on separate nodes} -300 -1420 0 0 0.3 0.3 {}
C {serdes.sym} -2000 0 0 0 {name=Xsd}
N -2140 -250 -2180 -250 {lab=Clk}
C {lab_pin.sym} -2180 -250 0 1 {name=l41 lab=Clk}
N -2140 -230 -2180 -230 {lab=VDDC}
C {lab_pin.sym} -2180 -230 0 1 {name=l42 lab=VDDC}
N -2140 -30 -2180 -30 {lab=0}
C {gnd.sym} -2180 -30 0 0 {name=g43 lab=0}
N -2140 -50 -2180 -50 {lab=0}
C {gnd.sym} -2180 -50 0 0 {name=g44 lab=0}
N -2140 -70 -2180 -70 {lab=0}
C {gnd.sym} -2180 -70 0 0 {name=g45 lab=0}
N -2140 -90 -2180 -90 {lab=0}
C {gnd.sym} -2180 -90 0 0 {name=g46 lab=0}
N -2140 -110 -2180 -110 {lab=0}
C {gnd.sym} -2180 -110 0 0 {name=g47 lab=0}
N -2140 -130 -2180 -130 {lab=0}
C {gnd.sym} -2180 -130 0 0 {name=g48 lab=0}
N -2140 -150 -2180 -150 {lab=0}
C {gnd.sym} -2180 -150 0 0 {name=g49 lab=0}
N -2140 -170 -2180 -170 {lab=0}
C {gnd.sym} -2180 -170 0 0 {name=g50 lab=0}
N -2140 -190 -2180 -190 {lab=0}
C {gnd.sym} -2180 -190 0 0 {name=g51 lab=0}
N -2140 -210 -2180 -210 {lab=0}
C {gnd.sym} -2180 -210 0 0 {name=g52 lab=0}
N -2140 250 -2180 250 {lab=DI0}
C {lab_pin.sym} -2180 250 0 1 {name=l53 lab=DI0}
N -2140 230 -2180 230 {lab=DI1}
C {lab_pin.sym} -2180 230 0 1 {name=l54 lab=DI1}
N -2140 210 -2180 210 {lab=DI2}
C {lab_pin.sym} -2180 210 0 1 {name=l55 lab=DI2}
N -2140 190 -2180 190 {lab=DI3}
C {lab_pin.sym} -2180 190 0 1 {name=l56 lab=DI3}
N -2140 170 -2180 170 {lab=DI4}
C {lab_pin.sym} -2180 170 0 1 {name=l57 lab=DI4}
N -2140 150 -2180 150 {lab=DI5}
C {lab_pin.sym} -2180 150 0 1 {name=l58 lab=DI5}
N -2140 130 -2180 130 {lab=DI6}
C {lab_pin.sym} -2180 130 0 1 {name=l59 lab=DI6}
N -2140 110 -2180 110 {lab=DI7}
C {lab_pin.sym} -2180 110 0 1 {name=l60 lab=DI7}
N -2140 90 -2180 90 {lab=DI8}
C {lab_pin.sym} -2180 90 0 1 {name=l61 lab=DI8}
N -2140 70 -2180 70 {lab=DI9}
C {lab_pin.sym} -2180 70 0 1 {name=l62 lab=DI9}
N -2140 50 -2180 50 {lab=DI10}
C {lab_pin.sym} -2180 50 0 1 {name=l63 lab=DI10}
N -2140 30 -2180 30 {lab=DI11}
C {lab_pin.sym} -2180 30 0 1 {name=l64 lab=DI11}
N -2140 10 -2180 10 {lab=DI12}
C {lab_pin.sym} -2180 10 0 1 {name=l65 lab=DI12}
N -2140 -10 -2180 -10 {lab=DI13}
C {lab_pin.sym} -2180 -10 0 1 {name=l66 lab=DI13}
N -1860 -130 -1820 -130 {lab=Dp}
C {lab_pin.sym} -1820 -130 0 0 {name=l67 lab=Dp}
N -1860 -110 -1820 -110 {lab=Dn}
C {lab_pin.sym} -1820 -110 0 0 {name=l68 lab=Dn}
N -1860 130 -1820 130 {lab=DO0}
C {lab_pin.sym} -1820 130 0 0 {name=l69 lab=DO0}
N -1860 110 -1820 110 {lab=DO1}
C {lab_pin.sym} -1820 110 0 0 {name=l70 lab=DO1}
N -1860 90 -1820 90 {lab=DO2}
C {lab_pin.sym} -1820 90 0 0 {name=l71 lab=DO2}
N -1860 70 -1820 70 {lab=DO3}
C {lab_pin.sym} -1820 70 0 0 {name=l72 lab=DO3}
N -1860 50 -1820 50 {lab=DO4}
C {lab_pin.sym} -1820 50 0 0 {name=l73 lab=DO4}
N -1860 30 -1820 30 {lab=DO5}
C {lab_pin.sym} -1820 30 0 0 {name=l74 lab=DO5}
N -1860 10 -1820 10 {lab=DO6}
C {lab_pin.sym} -1820 10 0 0 {name=l75 lab=DO6}
N -1860 -10 -1820 -10 {lab=DO7}
C {lab_pin.sym} -1820 -10 0 0 {name=l76 lab=DO7}
N -1860 -30 -1820 -30 {lab=DO8}
C {lab_pin.sym} -1820 -30 0 0 {name=l77 lab=DO8}
N -1860 -50 -1820 -50 {lab=DO9}
C {lab_pin.sym} -1820 -50 0 0 {name=l78 lab=DO9}
N -1860 -70 -1820 -70 {lab=DO10}
C {lab_pin.sym} -1820 -70 0 0 {name=l79 lab=DO10}
N -1860 -90 -1820 -90 {lab=DO11}
C {lab_pin.sym} -1820 -90 0 0 {name=l80 lab=DO11}
C {lvds_tx.sym} -700 0 0 0 {name=Xtx}
N -850 -50 -890 -50 {lab=Dp}
C {lab_pin.sym} -890 -50 0 1 {name=l81 lab=Dp}
N -850 -30 -890 -30 {lab=Dn}
C {lab_pin.sym} -890 -30 0 1 {name=l82 lab=Dn}
N -850 -10 -890 -10 {lab=Irf_pdd}
C {lab_pin.sym} -890 -10 0 1 {name=l83 lab=Irf_pdd}
N -850 10 -890 10 {lab=Irf_drvd}
C {lab_pin.sym} -890 10 0 1 {name=l84 lab=Irf_drvd}
N -850 30 -890 30 {lab=Vref}
C {lab_pin.sym} -890 30 0 1 {name=l85 lab=Vref}
N -550 -50 -510 -50 {lab=VDD}
C {vdd.sym} -510 -50 0 0 {name=v86 lab=VDD}
N -550 10 -510 10 {lab=0}
C {gnd.sym} -510 10 0 0 {name=g87 lab=0}
N -550 -30 -510 -30 {lab=Od_p}
C {lab_pin.sym} -510 -30 0 0 {name=l88 lab=Od_p}
N -550 -10 -510 -10 {lab=Od_n}
C {lab_pin.sym} -510 -10 0 0 {name=l89 lab=Od_n}
T {lvds_tx: pre-driver and driver, wired to each other inside} -900 -180 0 0 0.3 0.3 {}
C {esdpad.sym} 100 -200 0 0 {name=Xpadp_d}
N 20 -210 -20 -210 {lab=Od_p}
C {lab_pin.sym} -20 -210 0 1 {name=l90 lab=Od_p}
N 180 -210 220 -210 {lab=VDD}
C {vdd.sym} 220 -210 0 0 {name=v91 lab=VDD}
N 180 -170 220 -170 {lab=0}
C {gnd.sym} 220 -170 0 0 {name=g92 lab=0}
C {esdpad.sym} 100 200 0 0 {name=Xpadn_d}
N 20 190 -20 190 {lab=Od_n}
C {lab_pin.sym} -20 190 0 1 {name=l93 lab=Od_n}
N 180 190 220 190 {lab=VDD}
C {vdd.sym} 220 190 0 0 {name=v94 lab=VDD}
N 180 230 220 230 {lab=0}
C {gnd.sym} 220 230 0 0 {name=g95 lab=0}
C {res.sym} 600 -100 0 0 {name=Rp_d
value=49.9
footprint=1206
device=resistor
m=1}
N 600 -130 650 -130 {lab=Od_p}
C {lab_pin.sym} 650 -130 0 0 {name=l96 lab=Od_p}
N 600 -70 550 -70 {lab=Vos_d}
C {lab_pin.sym} 550 -70 0 1 {name=l97 lab=Vos_d}
C {res.sym} 600 100 0 0 {name=Rn_d
value=49.9
footprint=1206
device=resistor
m=1}
N 600 70 650 70 {lab=Vos_d}
C {lab_pin.sym} 650 70 0 0 {name=l98 lab=Vos_d}
N 600 130 550 130 {lab=Od_n}
C {lab_pin.sym} 550 130 0 1 {name=l99 lab=Od_n}
T {2 x 49.9 ohm with the Vos tap -- the clause 4.1.2 test load} 480 -200 0 0 0.3 0.3 {}
B 2 1200 -1300 2600 -900 {flags=graph
y1=-0.2
y2=1.5
ypos1=-0.2
ypos2=1.5
divy=5
subdivy=1
unity=1
x1=0
x2=9e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Clk
DO0
D_p"
color="4 6 7"
dataset=-1
unitx=1e-9
logx=0
logy=0
hilight_wave=-1}
B 2 1200 -850 2600 -450 {flags=graph
y1=0
y2=3.3
ypos1=0
ypos2=3.3
divy=7
subdivy=1
unity=1
x1=0
x2=9e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Od_p
Od_n"
color="4 5"
dataset=-1
unitx=1e-9
logx=0
logy=0
hilight_wave=-1}
B 2 1200 -400 2600 0 {flags=graph
y1=-0.5
y2=0.5
ypos1=-0.5
ypos2=0.5
divy=5
subdivy=1
unity=1
x1=0
x2=9e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Vod;Od_p Od_n -"
color="4"
dataset=-1
unitx=1e-9
logx=0
logy=0
hilight_wave=-1}
B 2 1200 50 2600 450 {flags=graph
y1=0
y2=2.5
ypos1=0
ypos2=2.5
divy=4
subdivy=1
unity=1
x1=0
x2=9e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Vos_d"
color="6"
dataset=-1
unitx=1e-9
logx=0
logy=0
hilight_wave=-1}
B 2 1200 500 2600 900 {flags=graph
y1=-0.2
y2=1.4
ypos1=-0.2
ypos2=1.4
divy=4
subdivy=1
unity=1
x1=0
x2=9e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
legendmag=1.0
node="Dp
Dn"
color="4 5"
dataset=-1
unitx=1e-9
logx=0
logy=0
hilight_wave=-1
rawfile=$netlist_dir/tb_startup.raw}
C {simulator_commands_shown.sym} -2600 -2000 0 0 {
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
C {simulator_commands_shown.sym} -2600 -1800 0 0 {
name=DigitalModels
simulator=ngspice
only_toplevel=false
value="
.model adc_1 adc_bridge(in_low=0.4 in_high=0.8 rise_delay=1p fall_delay=1p)
.model dac_1 dac_bridge(out_low=0 out_high=1.2 out_undef=0.6 input_load=1f t_rise=30p t_fall=30p)
.model serdes_dig_1 d_cosim(simulation=\\"/foss/designs/chipalooza_lvds_pll/macros/lvds_tx/serdes/serdes_dig.so\\" delay=1p)
"
}
C {simulator_commands_shown.sym} -2600 -1600 0 0 {
name=SimulatorNGSPICE
simulator=ngspice
only_toplevel=false
value="
.options temp=27
.control
save all
tran 1p 90n 0 1p
let vod = v(od_p)-v(od_n)
meas tran t_cm WHEN v(vos_d)=1.15 RISE=1
meas tran vosend FIND v(vos_d) AT=89.0000n
meas tran cmfbend FIND v(xtx.xdrv.cmfb) AT=89.0000n
write tb_startup.raw
.endc
"
}
C {launcher.sym} -1600 -2000 0 0 {name=h1
descr=SimulateNGSPICE
tclcommand="
set_sim_defaults
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}
set sim(spice,default) 0
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save
xschem netlist
simulate
"}
C {launcher.sym} -1600 -1960 0 0 {name=h2
descr="load waves"
tclcommand="xschem raw_read $netlist_dir/tb_startup.raw tran"
}
