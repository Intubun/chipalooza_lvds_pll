#!/usr/bin/env python3
"""Generate the CACE testbench template for lvds_tx.

CACE substitutes CACE{name} placeholders in a template schematic and runs it
once per condition set, so the corner, temperature, supply, reference and data
rate all become sweepable without touching this bench. Two details of that
format are easy to get wrong and are the reason this file exists rather than a
hand-drawn schematic:

  - inside a .sch the braces must be escaped, CACE\\{corner\\}, because xschem
    uses bare braces to delimit properties;
  - the results file is one whitespace-separated line per run, written to
    CACE\\{simpath\\}/CACE\\{filename\\}_CACE\\{N\\}.data, and its columns must
    line up with the `variables` list in the datasheet, in order.

The DUT is instantiated as its own symbol and its netlist comes in through
.include CACE\\{DUT_path\\}, which is what lets CACE point the same template at
the schematic, the extracted layout or the R-C extracted netlist.

The input pair is driven by two ideal PULSE sources rather than through
lvds_pattern: what is characterised here is the transmitter. Driving D_n from
its own source instead of an inverter keeps the two edges matched, so the
measurement is not contaminated by a pattern generator's rise/fall asymmetry -
which is exactly the effect that dominates Vos p-p at the top level.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "templates", "lvds_compliance.sch")

HEADER = """v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}"""


def lab(name, x, y, rot=0, flip=0):
    return ("C {devices/lab_pin.sym} %d %d %d %d "
            "{name=l_%s sig_type=std_logic lab=%s}"
            % (x, y, rot, flip, name.replace("[", "_").replace("]", ""), name))


def vsource(name, node, value, x, y, savecurrent=False):
    return [lab(node, x, y - 40),
            "N %d %d %d %d {lab=%s}" % (x, y - 40, x, y - 20, node),
            'C {devices/vsource.sym} %d %d 0 0 {name=%s value="%s" '
            "savecurrent=%s}" % (x, y, name, value,
                                 "true" if savecurrent else "false"),
            "N %d %d %d %d {lab=GND}" % (x, y + 20, x, y + 40),
            "C {devices/gnd.sym} %d %d 0 0 {name=g_%s lab=GND}" % (x, y + 40, name)]


def isource(name, node, value, x, y):
    return [lab(node, x, y - 40),
            "N %d %d %d %d {lab=%s}" % (x, y - 40, x, y - 20, node),
            "C {devices/isource.sym} %d %d 0 0 {name=%s value=%s}"
            % (x, y, name, value),
            "N %d %d %d %d {lab=GND}" % (x, y + 20, x, y + 40),
            "C {devices/gnd.sym} %d %d 0 0 {name=g_%s lab=GND}" % (x, y + 40, name)]


def code(name, x, y, body):
    """A code_shown block. CACE placeholders arrive already escaped."""
    return ('C {devices/code_shown.sym} %d %d 0 0 {name=%s\n'
            "simulator=ngspice\n"
            "only_toplevel=false\n"
            'value="\n%s\n"}' % (x, y, name, body))


# ---------------------------------------------------------------- the two blocks
SETUP = r"""* Corner and temperature are conditions, so one template covers the whole grid.
.lib cornerMOSlv.lib mos_CACE\{corner\}
.lib cornerMOShv.lib mos_CACE\{corner\}
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
.include cap_cmomf.lib

* The DUT netlist: schematic, extracted layout or R-C extracted, whichever
* CACE was asked for. This one line is what makes the three columns possible.
.include CACE\{DUT_path\}

.temp CACE\{temperature\}
.option warn=1

* The common-mode loop starts far from its operating point, so the bench gives
* it a hint and then measures only well after it has settled. Measuring across
* the cold start is how a driver that is not compliant comes out looking
* compliant.
.ic v(x1.xdrv.cmfb)=CACE\{cmfb_ic\}"""

CONTROL = r""".control

    * The analysis window and the measurement window are conditions in their
    * own right rather than expressions over the bit period. ngspice's control
    * language takes plain numbers here - a quoted expression is accepted in a
    * netlist line but silently skips the analysis in a .control block, which
    * leaves every meas reporting it is limited to tran, dc, sp or ac.
    * savecurrent on the supply emits a .save line into the netlist, and a
    * single .save makes ngspice keep only what is listed - every node
    * voltage is dropped. So name everything this bench measures.
    save v(Out_p) v(Out_n) v(Vos) i(VA)

    tran CACE\{tstep\} CACE\{tstop\}

    let vod = v(Out_p)-v(Out_n)

    meas tran vod_max MAX vod    from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vod_min MIN vod    from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vos_max MAX v(Vos) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vos_min MIN v(Vos) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran vos_avg AVG v(Vos) from=CACE\{tmeas\} to=CACE\{tstop\}
    meas tran i_va    AVG i(VA)  from=CACE\{tmeas\} to=CACE\{tstop\}

    * Clause 4.1.1 is written on the magnitude, and an unbalanced driver has
    * two different magnitudes. Report the worse one, not the average.
    let vod_mag  = min(vod_max, -vod_min)
    let vos_pp   = vos_max - vos_min
    let i_supply = -i_va

    echo $&vod_mag $&vos_avg $&vos_pp $&i_supply > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc"""


def main():
    out = [HEADER]

    # supplies and references
    out += vsource("VA", "Va", r"CACE\{vdd\}", -700, -400, savecurrent=True)
    out += vsource("Vrf", "Vref", r"CACE\{vref\}", -700, -240)
    out += isource("Ipd", "Iref_pd", r"-CACE\{iref\}", -700, -80)
    out += isource("Idrv", "Iref_drv", r"-CACE\{iref\}", -700, 80)

    # the complementary input pair
    out += vsource("VDp", "D_p",
                   r"PULSE(0 CACE\{vddc\} 0 CACE\{tedge\} CACE\{tedge\} "
                   r"'CACE\{period\}/2-CACE\{tedge\}' CACE\{period\})",
                   -700, 240)
    out += vsource("VDn", "D_n",
                   r"PULSE(0 CACE\{vddc\} 'CACE\{period\}/2' CACE\{tedge\} "
                   r"CACE\{tedge\} 'CACE\{period\}/2-CACE\{tedge\}' CACE\{period\})",
                   -700, 400)

    # the device under test, wired by label at every pin
    out.append("C {lvds_tx.sym} 0 0 0 0 {name=x1}")
    for pin, (px, py) in (("D_p", (-150, -50)), ("D_n", (-150, -30)),
                          ("Iref_pd", (-150, -10)), ("Iref_drv", (-150, 10)),
                          ("Vref", (-150, 30))):
        out.append("N %d %d %d %d {lab=%s}" % (px - 60, py, px, py, pin))
        out.append(lab(pin, px - 60, py, 0, 0))
    out.append("N 150 60 210 60 {lab=Va}")
    out.append(lab("Va", 210, 60, 0, 1))
    out.append("N 150 80 210 80 {lab=GND}")
    out.append("C {devices/gnd.sym} 210 80 1 0 {name=g_dut lab=GND}")

    # the standard 100 ohm termination with the Vos tap
    out += ["N 150 -30 300 -30 {lab=Out_p}", lab("Out_p", 300, -30, 0, 1),
            "N 150 -10 300 -10 {lab=Out_n}", lab("Out_n", 300, -10, 0, 1),
            "N 420 -120 420 -90 {lab=Out_p}", lab("Out_p", 420, -120),
            "C {devices/res.sym} 420 -60 0 0 {name=Rp value=49.9}",
            "N 420 -30 420 0 {lab=Vos}",
            "N 420 0 420 30 {lab=Vos}",
            "C {devices/res.sym} 420 60 0 0 {name=Rn value=49.9}",
            "N 420 90 420 120 {lab=Out_n}", lab("Out_n", 420, 120),
            "N 420 0 500 0 {lab=Vos}", lab("Vos", 500, 0, 0, 1)]

    out.append(code("SETUP", 700, -400, SETUP))
    out.append(code("CONTROL", 700, 0, CONTROL))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("wrote", os.path.relpath(OUT, HERE))


if __name__ == "__main__":
    main()
