#!/usr/bin/env python3
"""Insert the d_cosim auto-bridge setup into a netlist, after xschem has written it.

The top cell instantiates pll_cosim, so the PFD and both dividers are the RTL of
macros/pll_digital running through ngspice's d_cosim. Where that block meets the
analog loop - UP / DOWN into the charge pump, VCO_CLK back out of the ring - the
digital and analog worlds have to be bridged. ngspice will place those bridges
itself if auto_bridge_d_in and auto_bridge_d_out are set before the circuit is
parsed, which is what the two `pre_set` lines below do.

They cannot live in the schematic. xschem carries an ngspice block as a
`value="..."` property, and the pre_set syntax needs double quotes of its own -
the first one ends the property and the rest of the control block, `.endc`
included, is silently dropped. scripts/pll/run_pll_cosim.sh works around this
the same way, by writing the lines into the netlist from outside.

Idempotent: running it twice leaves one copy.

Usage: inject_cosim_bridges.py <netlist.spice> [vdd]
"""
import sys

MARK = "auto_bridge_d_in"


def lines(vdd):
    adc = '".model auto_adc adc_bridge(in_low=0.3 in_high=0.9 rise_delay=5p fall_delay=5p)"'
    dac = '".model auto_dac dac_bridge(out_low=0 out_high=%s t_rise=20p t_fall=20p)"' % vdd
    tin = '"auto_bridge%d [ %s ] [ %s ] auto_adc"'
    tout = '"auto_bridge%d [ %s ] [ %s ] auto_dac"'
    return ["* d_cosim needs the analog/digital boundary bridged; see",
            "* scripts/pll/inject_cosim_bridges.py for why these are not in the schematic.",
            "pre_set auto_bridge_d_in = ( %s %s )" % (adc, tin),
            "pre_set auto_bridge_d_out = ( %s %s )" % (dac, tout)]


def main(path, vdd="1.2"):
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    if MARK in text:
        print("%s: auto-bridge setup already present" % path)
        return

    out, done = [], False
    for line in text.split("\n"):
        out.append(line)
        if not done and line.strip().lower() == ".control":
            out.extend(lines(vdd))
            done = True

    if not done:
        raise SystemExit("%s: no .control block to insert into" % path)

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print("%s: auto-bridge setup inserted" % path)


if __name__ == "__main__":
    main(*sys.argv[1:])
