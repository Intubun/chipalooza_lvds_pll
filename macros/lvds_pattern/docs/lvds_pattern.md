# lvds_pattern

- Description: PRBS-7 pattern generator and clock multiplexer for the Chipalooza 2026 LVDS transmitter, built only from IHP standard cells. Selects between the reference and the PLL clock, generates x^7 + x^6 + 1 or passes the clock through, and hands the transmitter a complementary pair that is registered after the inversion so both edges leave on the same clock.
- PDK: ihp-sg13cmos5l

## Authorship

- Designer: Enno Schnackenberg
- License: Apache 2.0
- Company: None
- Created: None
- Last modified: None

## Pins

- ref_clk
  + Description: Reference clock from the pad
  + Type: signal
  + Direction: input
- pll_clk
  + Description: Bit clock from the PLL
  + Type: signal
  + Direction: input
- clk_src
  + Description: Clock select. 0 takes ref_clk, 1 takes pll_clk.
  + Type: signal
  + Direction: input
- en
  + Description: Enables the pattern clock. Latch-based gate, so the clock stops low and en may change at any point in the cycle without a runt pulse. It does not reach the two output flops - those run on an ungated copy.
  + Type: signal
  + Direction: input
- reset
  + Description: Active high, asynchronous, seeds the PRBS shift register. Like en it does not reach the output flops, whose RESET_B is tied high, so the output pair is complementary from the first clock edge after power-up rather than from the first enable.
  + Type: signal
  + Direction: input
- mode
  + Description: 0 passes the gated clock to the pair, 1 generates PRBS-7
  + Type: signal
  + Direction: input
- D_p
  + Description: Data output, true, into the transmitter's pre-driver
  + Type: signal
  + Direction: output
- D_n
  + Description: Data output, complement
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
- vhalf
  + Description: Threshold the edge measurements cross. Held at 0.6 V across the supply sweep rather than tracking vdd/2, so a skew number at 1.08 V and one at 1.32 V are measured on the same threshold and can be compared.
  + Display: Vmid
  + Unit: V
  + Typical: 0.6
- period
  + Description: Reference clock period. One clock period carries one bit.
  + Display: Period
  + Unit: ns
  + Typical: 2
- tedge
  + Description: Edge rate of the stimulus
  + Display: Tedge
  + Unit: ps
  + Typical: 50
- cload
  + Description: Load per output. The transmitter's pre-driver presents about 170 fF, two 40u/0.45u HV gates, and the skew figure is meaningless without it.
  + Display: Cload
  + Unit: fF
  + Typical: 170
- t_rst
  + Description: When reset is released
  + Display: Treset
  + Unit: ns
  + Typical: 2
- t_en
  + Description: When the pattern is enabled
  + Display: Ten
  + Unit: ns
  + Typical: 3
- tstep
  + Description: Transient timestep
  + Display: Tstep
  + Unit: ps
  + Typical: 2
- tstop
  + Description: Length of the transient run
  + Display: Tstop
  + Unit: ns
  + Typical: 200
- tmeas
  + Description: Start of the measurement window, past the enable
  + Display: Tmeas
  + Unit: ns
  + Typical: 20
- edge
  + Description: Index of the output edge the skew is measured on. With PRBS-7 the output only has a rising edge on a 0-to-1 bit, so an index counts transitions and not bits - the bit rate is an input condition here, not something this block determines.
  + Display: Edge
  + Typical: 12
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

![Symbol of lvds_pattern](lvds_pattern_symbol.svg)

## Schematic

![Schematic of lvds_pattern](lvds_pattern_schematic.svg)
