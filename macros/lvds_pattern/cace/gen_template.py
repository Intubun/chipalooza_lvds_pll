#!/usr/bin/env python3
"""Generate the CACE testbench template for lvds_pattern.

Same shape as macros/lvds_tx/cace/gen_template.py, and for the same reasons:
the template is generated rather than drawn so that the two silent traps of the
format cannot creep back in. Inside a .sch the braces must be escaped as
CACE\\{corner\\}, because xschem uses bare braces to delimit properties; and a
double quote anywhere in a code block ends the value property, taking .endc and
the rest of the control block with it. main() refuses to write a block that
contains either.

What is characterised: the block hands the transmitter a complementary pair,
and everything that matters about it is a timing property of that pair. The
polynomial itself is not checked here - scripts/check_timing.py re-runs the
recurrence on an exported waveform and is the right tool for it. This template
answers the questions a user of the block asks before that: does the pair stay
complementary at every instant, how much skew is there between the two edges,
and what does it cost on the core supply.

The load is the real one: the pre-driver of macros/lvds_tx presents about
170 fF per side, two 40u/0.45u HV gates, and the skew figure is meaningless
without it.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "templates", "pattern_timing.sch")

HEADER = """v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}"""


def lab(name, x, y, rot=0, flip=0):
    return ("C {devices/lab_pin.sym} %d %d %d %d "
            "{name=l%s_%d_%d sig_type=std_logic lab=%s}"
            % (x, y, rot, flip, name.replace("[", "_").replace("]", ""), x, y, name))


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
.include CACE\{PDK_ROOT\}/CACE\{PDK\}/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice

* schematic, extracted layout or R-C extracted, whichever CACE was asked for
.include CACE\{DUT_path\}

.temp CACE\{temperature\}
.option warn=1"""

CONTROL = r""".control

    * A single .save in the netlist makes ngspice drop every node voltage that
    * is not named, and savecurrent on the supply emits one. So list them.
    save v(D_p) v(D_n) i(VDD)

    tran CACE\{tstep\} CACE\{tstop\}

    * Is the pair complementary at every instant? dsum is twice the common mode
    * of the two outputs, so a pair that ever sits at the same level shows up
    * here as an excursion, whatever the data is doing.
    let dsum = v(D_p)+v(D_n)
    meas tran dsum_min MIN dsum from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran dsum_max MAX dsum from=CACE\{tmeas\} to=CACE\{tstop\}
    let dsum_dev = maximum(abs(dsum_max-CACE\{vdd\}), abs(CACE\{vdd\}-dsum_min))

    * Output skew: D_p rising against D_n falling on the same bit. This is what
    * the pre-driver sees, and its budget is about 40 ps.
    * Both counts start at tmeas, not at t=0. During power-up one side can
    * emit a transition the other does not, and from then on the two edge
    * indices refer to different bits - which showed up as a skew of three
    * whole bit periods in some corners and 25 ps in others.
    meas tran tp_r WHEN v(D_p)=CACE\{vhalf\} RISE=CACE\{edge\} TD=CACE\{tmeas\}
    meas tran tn_f WHEN v(D_n)=CACE\{vhalf\} FALL=CACE\{edge\} TD=CACE\{tmeas\}
    let skew = abs(tn_f - tp_r)

    meas tran i_vdd AVG i(VDD) from=CACE\{tmeas\} to=CACE\{tstop\}
    let i_core = -i_vdd

    echo $&dsum_dev $&skew $&i_core > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc"""


def main():
    out = [HEADER]

    out += vsource("VDD", "VDD", r"CACE\{vdd\}", -700, -400, savecurrent=True)
    out += vsource("VREF", "ref_clk",
                   r"PULSE(0 CACE\{vdd\} 0 CACE\{tedge\} CACE\{tedge\} "
                   r"'CACE\{period\}/2-CACE\{tedge\}' CACE\{period\})",
                   -700, -240)
    out += vsource("VPLL", "pll_clk", "0", -700, -80)
    out += vsource("VSRC", "clk_src", "0", -700, 80)
    out += vsource("VEN", "en",
                   r"PWL(0 0 CACE\{t_en\} 0 'CACE\{t_en\}+CACE\{tedge\}' CACE\{vdd\})",
                   -700, 240)
    out += vsource("VRST", "reset",
                   r"PWL(0 CACE\{vdd\} CACE\{t_rst\} CACE\{vdd\} "
                   r"'CACE\{t_rst\}+CACE\{tedge\}' 0)",
                   -700, 400)
    out += vsource("VMODE", "mode", r"CACE\{vdd\}", -700, 560)

    out.append("C {lvds_pattern.sym} 0 0 0 0 {name=x1}")
    for pin, py in (("ref_clk", -100), ("pll_clk", -80), ("clk_src", -60),
                    ("en", -40), ("reset", -20), ("mode", 0)):
        out.append("N -190 %d -130 %d {lab=%s}" % (py, py, pin))
        out.append(lab(pin, -190, py))
    out.append("N 130 80 190 80 {lab=VDD}")
    out.append(lab("VDD", 190, 80, 0, 1))
    out.append("N 130 100 190 100 {lab=GND}")
    out.append("C {devices/gnd.sym} 190 100 1 0 {name=gdut lab=GND}")

    # the pre-driver load, one per side: without it the skew figure is fiction
    for sig, py, cy in (("D_p", -100, -300), ("D_n", -80, -160)):
        out.append("N 130 %d 260 %d {lab=%s}" % (py, py, sig))
        out.append(lab(sig, 260, py, 0, 1))
        out.append("N 400 %d 400 %d {lab=%s}" % (cy, cy + 30, sig))
        out.append(lab(sig, 400, cy))
        out.append("C {devices/capa.sym} 400 %d 0 0 {name=C%s m=1 "
                   "value=CACE\\{cload\\}}" % (cy + 60, sig))
        # capa.sym has its pins at +/-30 and gnd.sym sits on its own
        # origin, so the bottom plate needs a wire down to the ground
        # symbol. Without it the plate floats, the operating point
        # cannot be solved, and the run dies in -Transient op failed,
        # timestep too small-.
        out.append("N 400 %d 400 %d {lab=GND}" % (cy + 90, cy + 120))
        out.append("C {devices/gnd.sym} 400 %d 0 0 {name=g%s lab=GND}"
                   % (cy + 120, sig))

    out.append(code("SETUP", 700, -400, SETUP))
    out.append(code("CONTROL", 700, 0, CONTROL))

    for name, body in (("SETUP", SETUP), ("CONTROL", CONTROL)):
        assert '"' not in body, "%s carries a double quote" % name
        assert "{" not in body.replace("\\{", "").replace("\\}", ""), \
            "%s carries an unescaped brace" % name

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("wrote", os.path.relpath(OUT, HERE))


if __name__ == "__main__":
    main()
