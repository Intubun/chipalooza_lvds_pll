#!/usr/bin/env python3
"""Emit the magic Tcl that builds one leaf cell per distinct device geometry.

`magic::gencell` names the cell it creates itself, and the name is not
predictable, so every call is bracketed by a diff of `cellname list allcells`
and the new cell is renamed to the stable name `devices.py` derived from the
geometry.
"""
import sys

from devices import parse, unique_devices

# Every device carries its own guard ring and has the gates of a block
# strapped by the generator, so a device is a self-contained four-terminal
# block long before anything is routed.
#
# Via coverage 0 on source, drain and gate stops every MOSFET terminal on
# metal1: no via1, no metal2 strap anywhere in the cell.  The router owns
# metal2 and up completely, and a device no longer spends a layer on a strap
# the router would have to work around.
#
# It also retires the PDK's worst gencell quirk.  At the default coverage of
# 100 the source/drain metal2 strap stops 0.15 um short of the gate rail
# where M2.b wants 0.21, so every MOSFET came out with spacing errors; 80
# opened the gap, and on a 0.8 um finger the shortened strap then fell under
# the M2.d minimum area and had to be widened by `patch_cells.py`.  With no
# metal2 in the cell at all, neither rule has anything to catch.
#
# `full_metal` is not that switch, despite the name -- it is the metal on the
# guard ring, and stays on.
MOS_OPTS = ("guard 1 conn_gates 1 full_metal 1 doports 1 "
            "viasrc 0 viadrn 0 viagate 0")

# Gate access, per device, decided by gate length.
#
# `conn_gates 1` merges the per-finger gate contacts into one rail across the
# top and bottom of the device.  That is one clean gate terminal, but the
# rail is a wall: source and drain cannot reach the guard ring on metal1
# without crossing it.
#
# `conn_gates 0` leaves one contact per finger (G0, G1, ... instead of G),
# and `polycov` shortens each one so a corridor opens between them.  At
# polycov 50 the gap on a 2 um gate is 1.35 um, of which 0.99 um is usable
# for a metal1 wire after M1.b spacing -- room for source/drain to leave the
# device sideways.
#
# It only works on the long-channel devices.  The metal1 over a single poly
# contact is under the 0.09 um2 minimum area (M1.d) once the pads no longer
# merge: with conn_gates 0 across the board, 17 of 27 cells fail, every one
# of them at l = 0.4, 0.45 or 0.5 um.  Shortening the contact makes that
# worse, so 1 um fails too once polycov comes in (40 errors on
# dev_n_w2_l1_ng20).  2 um is where both hold.  Everything shorter keeps the
# rail, and the router crosses it on metal2.
GATE_ACCESS_MIN_L = 2.0         # um
INDIVIDUAL_GATES = "conn_gates 0 polycov 50"
RES_OPTS = "guard 1 full_metal 1 doports 1"
CAP_OPTS = "mmin metal1 mmax metal4 subblock 0"

PREAMBLE = [
    "drc off",
    "load devscratch -silent",
    "box 0 0 0 0",
    "proc mkdev {type name params} {",
    "    set before [cellname list allcells]",
    "    box 0 0 0 0",
    "    eval \"magic::gencell sg13cmos5l::$type inst_$name $params\"",
    "    set after [cellname list allcells]",
    "    set new {}",
    "    foreach c $after { if {[lsearch $before $c] < 0} { set new $c } }",
    "    if {$new eq {}} { puts \"ERROR: no cell created for $name\"; return }",
    "    cellname rename $new $name",
    "    puts \"MADE $name from $new\"",
    "}",
]


def main(outpath):
    lines = list(PREAMBLE)
    for cellname, dev in unique_devices(parse()).items():
        if dev.kind == "mos":
            params = "w %g l %g ng %d m 1 %s" % (dev.w, dev.l, dev.ng, MOS_OPTS)
            if dev.l >= GATE_ACCESS_MIN_L:
                params += " " + INDIVIDUAL_GATES
        elif dev.kind == "res":
            params = "w %g l %g nx 1 m 1 %s" % (dev.w, dev.l, RES_OPTS)
        else:
            params = "w %g l %g %s" % (dev.w, dev.l, CAP_OPTS)
        # per-device overrides come last, so they win over the defaults
        # above; "_" keys are for patch_cells.py, not for gencell
        for key, value in sorted(dev.opts.items()):
            if key.startswith("_"):
                continue
            params += " %s %s" % (key, value)
        lines.append("mkdev %s %s {%s}" % (dev.model, cellname, params))
    lines += ["writeall force", "quit -noprompt"]
    with open(outpath, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote %s (%d leaf cells)" % (outpath, len(lines) - len(PREAMBLE) - 2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "gen_devices.tcl")
