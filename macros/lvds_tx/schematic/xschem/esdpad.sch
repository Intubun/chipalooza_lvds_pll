v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Everything that hangs on one LVDS output pad.

Clause 4.1.5 sets a FLOOR on the total capacitance of this node and clause 4.1.4 Vring
sets a CEILING - see docs/pad-esd-budget.md before changing anything here.
Usable window 300 fF ... 1.0 pF per output; as built the total is ~814 fF, of which
~681 fF is Cop/Con inside Driver.sch and the rest is here.

Cpad is a geometric estimate, not a PDK number: sg13g2_bondpad.lib is an empty
placeholder. 90 fF is an 80 um pad on the default stack (bottomMetal=3, 3.03 um up).
The 4 kV clamp is used rather than the 2 kV one because it costs nothing in speed
(87 fF vs 43 fF) and both sit far below the ceiling.} -200 -560 0 0 0.4 0.4 {}
T {VA} -260 -245 0 0 0.3 0.3 {}
T {VSS} -270 255 0 0 0.3 0.3 {}
N 60 -250 400 -250 {lab=VA}
N 300 250 400 250 {lab=VSS}
N 150 0 300 0 {lab=PAD}
N 0 -250 0 -130 {lab=VA}
N 0 -70 0 0 {lab=PAD}
N -200 -100 -30 -100 {lab=VSS}
N -200 -100 -200 250 {lab=VSS}
N 150 0 150 70 {lab=PAD}
N 150 130 150 250 {lab=VSS}
N 60 100 120 100 {lab=VA}
N 60 -250 60 100 {lab=VA}
N 300 -30 300 0 {lab=PAD}
N 300 30 300 250 {lab=VSS}
N -200 -250 0 -250 {lab=VA}
N -100 0 0 0 {lab=PAD}
N 0 0 150 0 {lab=PAD}
N -200 250 150 250 {lab=VSS}
N 0 -250 60 -250 {lab=VA}
N 150 250 300 250 {lab=VSS}
C {sg13cmos5l_pr/diodevdd_4kv.sym} 0 -100 0 0 {name=Ddvdd
model=diodevdd_4kv
m=1
spiceprefix=X
}
C {sg13cmos5l_pr/diodevss_4kv.sym} 150 100 0 0 {name=Ddvss
model=diodevss_4kv
m=1
spiceprefix=X
}
C {capa.sym} 300 0 0 0 {name=Cpad
m=1
value=90f
footprint=1206
device="ceramic capacitor"}
C {iopin.sym} -100 0 0 1 {name=p1 lab=PAD}
C {iopin.sym} -200 -250 0 0 {name=p2 lab=VA}
C {iopin.sym} -200 250 0 0 {name=p3 lab=VSS}
