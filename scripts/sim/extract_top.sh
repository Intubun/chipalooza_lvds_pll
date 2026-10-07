#!/bin/bash
# Post-layout netlists of the whole slot for the pad and PEX benches
#
#   bash scripts/sim/extract_top.sh        # in the container; or: make extract-top
#
# One magic extraction of layout/slot_14.gds, hierarchical, with coupling
# capacitance (cthresh 0.01 fF, as extract_lvds.sh and CACE's pex column), and
# xschem's netlist of the top schematic.  scripts/sim/pex_top.py turns them into
#
#   netlist/pex/slot_14_pex.spice    everything as laid out       -> slot_14_tb_lvds_pex
#   netlist/pex/slot_14_wires.spice  the top-level wiring as laid
#                                    out, the blocks as schematics -> slot_14_tb_lvds_pads
#
# Capacitance only: no wire resistance.  The longest top-level runs are 1 um
# metal4 (ref_clk, ~430 um: ~40 ohm into ~0.1 pF) and 3.27 um metal3 (the
# outputs, <3 ohm) - small next to the pads.  Work files go to build/extract_top/.
#
# No `set -u`: sak-pdk-script.sh reads unset variables.
cd "$(dirname "$0")/../.." || exit 1
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
ROOT=$PWD
OUT=$ROOT/netlist/pex
W=$ROOT/build/extract_top
rm -rf "$W" && mkdir -p "$W" "$OUT"

xschem -s -r -x -q --rcfile schematic/xschem/xschemrc --command "
    set top_is_subckt 1;
    set netlist_dir [file normalize $W];
    xschem set netlist_name slot_14_sch.spice; xschem netlist
" schematic/xschem/slot_14.sch > "$W/xschem.log" 2>&1
if [ ! -s "$W/slot_14_sch.spice" ]; then
    echo "  Schaltplan-Netzliste fehlt -- $W/xschem.log"; exit 1
fi
{
    echo "gds flatglob via_stack*"
    echo "gds read $ROOT/layout/slot_14.gds"
    echo "load slot_14"; echo "readspice $W/slot_14_sch.spice"; echo "load slot_14"
    echo "select top cell"; echo "expand"
    echo "extract path $W"; echo "extract all"
    echo "ext2spice lvs"; echo "ext2spice cthresh 0.01"
    echo "ext2spice -p $W -o $W/slot_14_raw.spice"
    echo "quit -noprompt"
} > "$W/ext.tcl"
(cd "$W" && magic -dnull -noconsole -rcfile "$PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc" < ext.tcl > magic.log 2>&1)
if [ ! -s "$W/slot_14_raw.spice" ]; then
    echo "  Extraktion fehlgeschlagen -- $W/magic.log"; exit 1
fi
python3 scripts/sim/pex_top.py "$W/slot_14_raw.spice" "$W/slot_14_sch.spice" \
    schematic/xschem/slot_14.sym "$OUT"
