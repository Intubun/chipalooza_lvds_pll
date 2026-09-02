# ring_oscillator

- Description: Voltage-controlled ring oscillator of the Chipalooza 2026 PLL, by Rahul Bhagwat. Its tuning curve is what decides which reference and DIV_RATIO combinations the loop can lock at all, so it is characterised on its own rather than only inside the loop.
- PDK: ihp-sg13cmos5l

## Authorship

- Designer: Rahul Bhagwat
- License: Apache 2.0
- Company: None
- Created: None
- Last modified: None

## Pins

- VCTRL
  + Description: Control voltage from the loop filter. The oscillator does not start below about 0.50 V, which is the lower end of the usable range rather than a specification limit.
  + Type: signal
  + Direction: input
- VCO_OUT
  + Description: Buffered oscillator output
  + Type: signal
  + Direction: output
- VDD
  + Description: Core supply, 1.2 V
  + Type: power
  + Direction: inout
  + Vmin: 1.08
  + Vmax: 1.32
- VSS
  + Description: Core ground
  + Type: ground
  + Direction: inout

## Default Conditions

- vdd
  + Description: Core supply voltage
  + Display: Vdd
  + Unit: V
  + Typical: 1.2
- vctrl
  + Description: Control voltage
  + Display: Vctrl
  + Unit: V
  + Typical: 0.75
- vhalf
  + Description: Threshold the crossings are counted on. Held at 0.6 V across the supply sweep so frequencies at different supplies are measured alike.
  + Display: Vmid
  + Unit: V
  + Typical: 0.6
- tstep
  + Description: Transient timestep
  + Display: Tstep
  + Unit: ps
  + Typical: 1
- tstop
  + Description: Length of the run. Long enough that the slowest corner still delivers well over edge_b crossings. At the slow corner and the low end of the VCTRL range that is about 300 MHz, so 120 ns carries roughly 36 cycles - which is why edge_b is 30 and not 60.
  + Display: Tstop
  + Unit: ns
  + Typical: 120
- tmeas
  + Description: Start of the measurement window, past the startup transient
  + Display: Tmeas
  + Unit: ns
  + Typical: 20
- edge_a
  + Description: First counted rising edge
  + Display: EdgeA
  + Typical: 5
- edge_b
  + Description: Last counted rising edge. The frequency is taken across the whole span rather than one period, because the range covers more than a decade.
  + Display: EdgeB
  + Typical: 25
- corner
  + Description: Process corner
  + Display: Corner
  + Typical: tt
- temperature
  + Description: Ambient temperature
  + Display: Temp
  + Unit: °C
  + Typical: 27

## Symbol

![Symbol of ring_oscillator](ring_oscillator_symbol.svg)

## Schematic

![Schematic of ring_oscillator](ring_oscillator_schematic.svg)
