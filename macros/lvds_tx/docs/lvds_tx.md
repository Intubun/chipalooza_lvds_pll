# lvds_tx

- Description: LVDS output driver with pre-driver and common-mode feedback, for the Chipalooza 2026 LVDS transmitter. Takes a complementary CMOS pair on the 1.2 V core domain and drives a 100 ohm differential line from the 3.3 V domain, to TIA/EIA-644-A.
- PDK: ihp-sg13cmos5l

## Authorship

- Designer: Enno Schnackenberg
- License: Apache 2.0
- Company: None
- Created: None
- Last modified: None

## Pins

- D_p
  + Description: Data input, true. Core domain, full swing on vddc.
  + Type: signal
  + Direction: input
- D_n
  + Description: Data input, complement. Must be the complement of D_p at every instant.
  + Type: signal
  + Direction: input
- Iref_pd
  + Description: Pre-driver bias reference. Mirrored 1:15 inside the block, so the pin takes 2 uA and the pre-driver sees the 30 uA it was characterised at. The 1:15 step exists because the harness current DACs stop at 10 uA.
  + Type: signal
  + Direction: input
- Iref_drv
  + Description: Output driver bias reference, 2 uA, mirrored 1:15 as above.
  + Type: signal
  + Direction: input
- Vref
  + Description: Output common-mode reference. The CMFB loop drives Vos to this voltage. Clause 4.1.2 centres on 1.25 V; the harness supplies 1.2 V.
  + Type: signal
  + Direction: input
- Va
  + Description: Analog supply, 3.3 V
  + Type: power
  + Direction: inout
  + Vmin: 2.97
  + Vmax: 3.63
- Out_p
  + Description: LVDS output, true
  + Type: signal
  + Direction: output
- Out_n
  + Description: LVDS output, complement
  + Type: signal
  + Direction: output
- Vss
  + Description: Analog ground
  + Type: ground
  + Direction: inout

## Default Conditions

- vdd
  + Description: Analog supply voltage
  + Display: Va
  + Unit: V
  + Typical: 3.3
- vddc
  + Description: Core-domain swing of the input pair
  + Display: Vddc
  + Unit: V
  + Typical: 1.2
- vref
  + Description: Common-mode reference into the CMFB loop
  + Display: Vref
  + Unit: V
  + Typical: 1.2
- iref
  + Description: Bias reference current per pin, mirrored 1:15 inside
  + Display: Iref
  + Unit: uA
  + Typical: 2
- period
  + Description: Bit period times two - one PULSE period carries two bits
  + Display: Period
  + Unit: ns
  + Typical: 4
- tedge
  + Description: Input edge rate
  + Display: Tedge
  + Unit: ps
  + Typical: 50
- tstep
  + Description: Transient timestep
  + Display: Tstep
  + Unit: ps
  + Typical: 10
- tstop
  + Description: Length of the transient run
  + Display: Tstop
  + Unit: ns
  + Typical: 600
- tmeas
  + Description: Start of the measurement window. Everything before it is the common-mode loop settling from the DC operating point, and measuring across that is how a driver that is not compliant looks compliant.
  + Display: Tmeas
  + Unit: ns
  + Typical: 160
- cmfb_ic
  + Description: Initial condition on the CMFB node, near its settled value
  + Display: CMFB ic
  + Unit: V
  + Typical: 1.54
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

![Symbol of lvds_tx](lvds_tx_symbol.svg)

## Schematic

![Schematic of lvds_tx](lvds_tx_schematic.svg)
