#!/usr/bin/env python3
"""Generate the CACE testbench template for the PLL's ring oscillator.

The tuning curve is the number the whole loop is designed around: it fixes
which reference and divide ratio combinations can lock at all, and it is the
first thing that moves over PVT. info/ring_oscillator_buffered_pvt.csv holds an
earlier hand-run sweep of it; this puts the same measurement under CACE so it
regenerates with the circuit.

Two things this template has to do that the others do not:

  - Start the oscillator. A ring sits at an unstable DC operating point, and
    ngspice will happily solve for it and then sit there. The existing benches
    kick it with .ic on three ring nodes and so does this one.
  - Measure a frequency without knowing it in advance. The measurement counts
    a fixed number of crossings and divides, rather than taking one period,
    so it is an average over many cycles and survives a factor of ten in
    frequency across the VCTRL sweep.

The format traps are the same as in the other two generators: braces escaped as
CACE\\{corner\\}, and no double quote anywhere in a code block - main() refuses
to write one that carries either.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "templates", "vco_tuning.sch")

HEADER = """v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}"""


def lab(name, x, y, rot=0, flip=0):
    return ("C {devices/lab_pin.sym} %d %d %d %d "
            "{name=l%s_%d_%d sig_type=std_logic lab=%s}"
            % (x, y, rot, flip, name, x, y, name))


def vsource(name, node, value, x, y, savecurrent=False):
    return [lab(node, x, y - 40),
            "N %d %d %d %d {lab=%s}" % (x, y - 40, x, y - 20, node),
            'C {devices/vsource.sym} %d %d 0 0 {name=%s value="%s" '
            "savecurrent=%s}" % (x, y, name, value,
                                 "true" if savecurrent else "false"),
            "N %d %d %d %d {lab=GND}" % (x, y + 20, x, y + 40),
            "C {devices/gnd.sym} %d %d 0 0 {name=g%s lab=GND}" % (x, y + 40, name)]


def code(name, x, y, body):
    return ('C {devices/code_shown.sym} %d %d 0 0 {name=%s\n'
            "simulator=ngspice\n"
            "only_toplevel=false\n"
            'value="\n%s\n"}' % (x, y, name, body))


SETUP = r"""* Corner and temperature are conditions, so one template covers the grid.
.lib cornerMOSlv.lib mos_CACE\{corner\}

* schematic, extracted layout or R-C extracted, whichever CACE was asked for
.include CACE\{DUT_path\}

.temp CACE\{temperature\}
.option warn=1

* A ring oscillator has a perfectly good unstable DC operating point, and
* ngspice will solve for it and then stay there. These three nodes break the
* symmetry so it starts, the same way the block's own benches do it.
.ic v(x1.VCO_CORE)=0 v(x1.net1)=CACE\{vdd\} v(x1.net2)=0"""

CONTROL = r""".control

    save v(VCO_OUT) i(VDD)

    tran CACE\{tstep\} CACE\{tstop\}

    * Count a fixed number of crossings and divide, rather than taking one
    * period. The frequency changes by an order of magnitude across the VCTRL
    * sweep, so a single period is both noisy and, at the fast end, shorter
    * than the timestep resolution deserves.
    meas tran t_a WHEN v(VCO_OUT)=CACE\{vhalf\} RISE=CACE\{edge_a\}
    meas tran t_b WHEN v(VCO_OUT)=CACE\{vhalf\} RISE=CACE\{edge_b\}
    let f_vco = (CACE\{edge_b\}-CACE\{edge_a\})/(t_b-t_a)

    * Amplitude tells you whether it is really oscillating rail to rail or
    * just ringing - a frequency measured on a 100 mV wiggle is not a clock.
    meas tran v_max MAX v(VCO_OUT) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran v_min MIN v(VCO_OUT) from=CACE\{tmeas\} to=CACE\{tstop\}
    let v_swing = v_max - v_min

    meas tran i_vdd AVG i(VDD) from=CACE\{tmeas\} to=CACE\{tstop\}
    * In amps. CACE takes the number as SI base units and uses the unit
    * field only to scale the display, so declaring uA in the datasheet
    * is what makes this read as tens of microamps rather than 0.000 A.
    * Scaling here as well multiplies it in twice.
    let i_vco = -i_vdd

    echo $&f_vco $&v_swing $&i_vco > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc"""


def main():
    out = [HEADER]

    out += vsource("VDD", "VDD", r"CACE\{vdd\}", -600, -300, savecurrent=True)
    out += vsource("VCT", "VCTRL", r"CACE\{vctrl\}", -600, -100)

    out.append("C {ring_oscillator.sym} 0 0 0 0 {name=x1}")
    out.append("N -180 -30 -120 -30 {lab=VCTRL}")
    out.append(lab("VCTRL", -180, -30))
    out.append("N 120 -30 240 -30 {lab=VCO_OUT}")
    out.append(lab("VCO_OUT", 240, -30, 0, 1))
    out.append("N 120 -10 200 -10 {lab=VDD}")
    out.append(lab("VDD", 200, -10, 0, 1))
    out.append("N 120 50 200 50 {lab=GND}")
    out.append("C {devices/gnd.sym} 200 50 1 0 {name=gdut lab=GND}")

    out.append(code("SETUP", 600, -300, SETUP))
    out.append(code("CONTROL", 600, 100, CONTROL))

    for name, body in (("SETUP", SETUP), ("CONTROL", CONTROL)):
        assert '"' not in body, "%s carries a double quote" % name
        assert "{" not in body.replace("\\{", "").replace("\\}", ""), \
            "%s carries an unescaped brace" % name

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("wrote", os.path.relpath(OUT, HERE))


if __name__ == "__main__":
    main()
