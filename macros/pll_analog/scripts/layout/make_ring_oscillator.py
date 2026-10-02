#!/usr/bin/env python3
"""Generate layout/mag/ring_oscillator.mag: bias, three inverter stages, buffer.

Units are Magic internal units (5 nm). Run make_inverter.py first.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "layout/mag/ring_oscillator.mag"
L={}
def rect(l,a,b,c,d): L.setdefault(l,[]).append((a,b,c,d))
def wire(l,x1,y1,x2,y2,w=58):
 h=w//2
 if x1==x2: rect(l,x1-h,min(y1,y2)-h,x1+h,max(y1,y2)+h)
 elif y1==y2: rect(l,min(x1,x2)-h,y1-h,max(x1,x2)+h,y1+h)
 else: raise ValueError

# Intermediate M2/M3 landings are 0.29 x 0.50 um so that a pad that is not
# joined to a wire on its layer still meets the 0.144 um^2 minimum area.
def tall(l,x,y): rect(l,x-29,y-50,x+29,y+50)
def sq(l,x,y): rect(l,x-29,y-29,x+29,y+29)
def via1(x,y,t2=True): sq("metal1",x,y);rect("via1",x-20,y-20,x+20,y+20);(tall if t2 else sq)("metal2",x,y)
def via2(x,y,t3=False): sq("metal2",x,y);rect("via2",x-20,y-20,x+20,y+20);(tall if t3 else sq)("metal3",x,y)
def via3(x,y,t3=False): (tall if t3 else sq)("metal3",x,y);rect("via3",x-20,y-20,x+20,y+20);sq("metal4",x,y)
def via4(x,y): rect("metal4",x-40,y-40,x+40,y+40);rect("via4",x-21,y-21,x+21,y+21);rect("metal5",x-40,y-40,x+40,y+40)
def stack13(x,y): via1(x,y);via2(x,y,True)
uses=[("vco_bias","_bias",-1500,0),("inverter","1",0,1500),("inverter","2",1000,1500),("inverter","3",500,-1000),("vco_buffer","_buffer",1800,-1500)]
# Join the adjacent top-stage N-wells.
rect("nwell",350,1900,650,2850)
# Clock 1 -> 2 on M4.
via3(430,1800); wire("metal4",430,1800,570,1800)
# Clock 2 -> 3 on M4, outside the right edge.
via3(1430,1800); wire("metal4",1430,1800,1600,1800); wire("metal4",1600,1800,1600,-700); wire("metal4",1600,-700,50,-700)
# Clock 3 -> 1 on M3, around the left edge; transition only at stage-1 input.
wire("metal3",950,-700,-600,-700); wire("metal3",-600,-700,-600,1800); wire("metal3",-600,1800,-430,1800); via3(-430,1800)
# Buffer taps the stage-3 output without loading the ring through another layer transition.
wire("metal3",950,-700,1720,-700); wire("metal3",1720,-700,1720,-740); via2(1720,-740)
# VBP on M4, above/outside the inverter cells, avoiding their internal M3 supply wiring.
via2(-820,664,True); via3(-820,664); wire("metal4",-820,664,-820,2900); wire("metal4",-820,2900,1430,2900)
wire("metal4",430,2634,430,2900); wire("metal4",1430,2634,1430,2900)
wire("metal4",-820,134,-820,2900); wire("metal4",-820,134,930,134)
# VCTRL escapes the M2-only bias on M4, then returns to M2 clear of the bias cell.
via2(-1580,1116,True); via3(-1580,1116); wire("metal4",-1580,1116,-2100,1116); wire("metal4",-2100,1116,-2100,500); wire("metal4",-2100,500,-950,500); via3(-950,500); wire("metal3",-950,500,-700,500); via2(-700,500)
wire("metal2",-700,500,2000,500)
# VCTRL drives each stage's NMOS starve gate (VBN). The feeds run in the free
# M2 channel at inverter-local y=-230 and end on the inverter's own VBN M2
# landing at local x=360, so no second via stack sits beside it.
wire("metal2",-500,500,-500,700); via2(-500,700); wire("metal3",-500,700,-500,940); via2(-500,940); wire("metal2",-500,940,-500,1270); wire("metal2",-500,1270,360,1270)
wire("metal2",1500,500,1500,1270); wire("metal2",1360,1270,1500,1270)
wire("metal2",1000,500,1000,-1230); wire("metal2",860,-1230,1000,-1230)
# VDD on M3, with short M2 bridges where it must cross M3 signal wiring.
for x,y in [(-1580,130),(-430,2780),(570,2780),(70,280),(1720,-1370)]: stack13(x,y)
wire("metal3",-1700,130,-1700,2780); wire("metal3",-1700,130,-1580,130); wire("metal3",-1700,2780,1530,2780)
wire("metal3",-1700,280,-700,280); via2(-700,280); wire("metal2",-700,280,-500,280); via2(-500,280); wire("metal3",-500,280,1530,280)
wire("metal3",1500,280,1500,-600); via2(1500,-600); wire("metal2",1500,-600,1500,-800); via2(1500,-800); wire("metal3",1500,-800,1500,-1370); wire("metal3",1500,-1370,1720,-1370)
wire("metal3",1530,280,1530,2780)
# VSS on M2; escape the bias on M3 and route the buffer branch below the core.
for x,y in [(-1580,790),(-430,820),(570,820),(70,-1680),(1720,-230)]: via1(x,y,x in (-1580,1720))
via2(-1580,790,True); via3(-1580,790); wire("metal4",-1580,790,-1900,790); wire("metal4",-1900,790,-1900,820); via3(-1900,820,True); via2(-1900,820); wire("metal4",-1900,820,-930,820); via3(-930,820); wire("metal3",-930,820,-700,820); via2(-700,820)
wire("metal2",-700,820,370,820); via2(370,820); wire("metal3",370,820,510,820); via2(510,820); wire("metal2",510,820,570,820); wire("metal2",-1900,820,-1900,-1900)
wire("metal2",-1900,-1680,70,-1680); wire("metal2",70,-1680,70,-1900)
wire("metal2",-1900,-1900,1620,-1900); wire("metal2",1620,-1900,1620,-230); wire("metal2",1620,-230,1720,-230)
# External pins: VCTRL left, buffered output right, and supply stubs.
wire("metal2",-1800,1116,-1600,1116)
wire("metal2",3900,-832,4100,-832)
wire("metal3",-1900,2780,-1700,2780)
wire("metal2",-2100,820,-1900,820)
labels=[("metal2",-1800,1087,-1760,1145,"VCTRL",1),("metal2",4060,-861,4100,-803,"VCO_OUT",2),("metal3",-1900,2751,-1860,2809,"VDD",3),("metal2",-2100,791,-2060,849,"VSS",4)]
lines=["magic","tech ihp-sg13cmos5l","magscale 1 2","timestamp 0"]
for cell,name,x,y in uses: lines += [f"use {cell}  {name}","timestamp 0",f"transform 1 0 {x} 0 1 {y}","box 0 0 1 1"]
for lay in ["nwell","metal1","via1","metal2","via2","metal3","via3","metal4"]:
 if lay in L:
  lines.append(f"<< {lay} >>"); lines += ["rect %d %d %d %d"%r for r in L[lay]]
lines.append("<< labels >>")
for lay,a,b,c,d,n,p in labels: lines += [f"rlabel {lay} {a} {b} {c} {d} 0 {n}",f"port {p} nsew"]
lines += ["<< end >>",""]
OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
