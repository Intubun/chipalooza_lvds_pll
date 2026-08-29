v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Buffered three-stage current-starved VCO with single-control replica bias} -210 -230 0 0 0.3 0.3 {}
N -50 0 -30 0 {lab=#net1}
N 110 0 130 0 {lab=#net2}
N 270 0 270 180 {lab=VCO_CORE}
N -190 0 -190 180 {lab=VCO_CORE}
N -190 180 270 180 {lab=VCO_CORE}
N 20 -100 180 -100 {lab=VBP}
N 220 -140 360 -140 {lab=VDD}
N 20 100 180 100 {lab=VCTRL}
N 220 140 360 140 {lab=VSS}
N -140 -100 -140 -70 {lab=VBP}
N -100 -140 -100 -70 {lab=VDD}
N 20 -100 20 -70 {lab=VBP}
N 60 -140 60 -70 {lab=VDD}
N 180 -100 180 -70 {lab=VBP}
N 220 -140 220 -70 {lab=VDD}
N -140 70 -140 100 {lab=VCTRL}
N -100 70 -100 140 {lab=VSS}
N 20 70 20 100 {lab=VCTRL}
N 60 70 60 140 {lab=VSS}
N 180 70 180 100 {lab=VCTRL}
N 220 70 220 140 {lab=VSS}
N -210 -100 -140 -100 {lab=VBP}
N -280 -140 -100 -140 {lab=VDD}
N -140 -100 20 -100 {lab=VBP}
N -100 -140 60 -140 {lab=VDD}
N 60 -140 220 -140 {lab=VDD}
N -350 100 -140 100 {lab=VCTRL}
N -280 140 -100 140 {lab=VSS}
N -140 100 20 100 {lab=VCTRL}
N -100 140 60 140 {lab=VSS}
N 60 140 220 140 {lab=VSS}
N -210 -100 -210 0 {lab=VBP}
N -350 0 -350 100 {lab=VCTRL}
N -280 -140 -280 -70 {lab=VDD}
N -280 70 -280 140 {lab=VSS}
N 270 0 290 0 {lab=VCO_CORE}
N 360 -140 360 -70 {lab=VDD}
N 360 70 360 140 {lab=VSS}
N -390 100 -350 100 {lab=VCTRL}
C {inverter.sym} -120 0 0 0 {name=x1}
C {inverter.sym} 40 0 0 0 {name=x2}
C {inverter.sym} 200 0 0 0 {name=x3}
C {vco_bias.sym} -280 0 0 0 {name=x_bias}
C {vco_buffer.sym} 360 0 0 0 {name=x_buffer}
C {lab_pin.sym} -210 -100 1 0 {name=p_VBP_INTERNAL sig_type=std_logic lab=VBP}
C {lab_pin.sym} 270 0 1 0 {name=p_VCO_CORE_INTERNAL sig_type=std_logic lab=VCO_CORE}
C {ipin.sym} -390 100 0 0 {name=p_VCTRL lab=VCTRL}
C {iopin.sym} 250 -140 0 0 {name=p_VDD lab=VDD}
C {iopin.sym} 250 140 0 0 {name=p_VSS lab=VSS}
C {opin.sym} 430 0 0 0 {name=p_VCO_OUT lab=VCO_OUT}
