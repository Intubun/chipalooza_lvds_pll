#!/bin/bash
# Top-level LVS (KLayout, IHP deck) of layout/sg13cmos5l_chipalooza_analog_project.gds
# against the top schematic - without Rahul's PLL for now (prepare_lvs.py).
#
#   bash scripts/verify/check_lvs.sh                  # in the container, from anywhere
#   bash scripts/verify/check_lvs.sh --strict-ports   # also compare the top-level pin names
#   bash scripts/verify/check_lvs.sh <gds>            # another copy of the top layout
#
# Results in build/verify/lvs/: reference.cdl, layout.gds (the copies that were
# compared), <top>.lvsdb (open it in KLayout: Tools > Netlist Browser), lvs.log.
# The summary goes to stdout; exit status 0 only when the netlists match.
#
# By default the top-level pin NAMES are not compared (--ignore_top_ports_mismatch):
# the slot-14 frame calls them s14_an[0..2], ibias0, analog_bus1, ..., the schematic
# still has the template's analog_pin[0..3], ibias[0], analog_bus[1], ...  The
# circuit behind the pins is compared either way.  --strict-ports compares the names
# too, once the schematic follows the frame.
#
# Taps are not extracted as devices (--disable_tap_extraction): no schematic here
# draws them.  Floating metal (the flags doodle) is purged (--purge_nets).
#
# No `set -u`: sak-pdk-script.sh reads unset variables.
TOP=sg13cmos5l_chipalooza_analog_project
cd "$(dirname "$0")/../.." || exit 1
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
PORTS=--ignore_top_ports_mismatch
GDS=layout/$TOP.gds
while [ $# -gt 0 ]; do
    case $1 in
        --strict-ports) PORTS= ;;
        -h|--help) sed -n 2,22p "$0"; exit 0 ;;
        *) GDS=$1 ;;
    esac
    shift
done
RUN=build/verify/lvs
rm -rf "$RUN" && mkdir -p "$RUN"
echo "== LVS $TOP ($GDS)"

xschem -s -r -x -q --rcfile schematic/xschem/xschemrc --command "
    set spiceprefix 1; set lvs_netlist 1; set top_is_subckt 1;
    set lvs_ignore 1; set ev_precision 5;
    set netlist_dir [file normalize $RUN];
    xschem set netlist_name schematic.cdl; xschem netlist
" schematic/xschem/$TOP.sch > "$RUN/xschem.log" 2>&1
if [ ! -s "$RUN/schematic.cdl" ]; then
    echo "  Schaltplan-Netzliste fehlt -- $RUN/xschem.log"; exit 2
fi
python3 scripts/verify/prepare_lvs.py "$RUN" "$RUN/schematic.cdl" "$GDS" \
    "$PDK_ROOT/$PDK/libs.ref/sg13cmos5l_stdcell/cdl/sg13cmos5l_stdcell.cdl" || exit 2

python3 "$PDK_ROOT/$PDK/libs.tech/klayout/tech/lvs/run_lvs.py" \
    --layout="$RUN/layout.gds" --netlist="$RUN/reference.cdl" --topcell=$TOP \
    --run_dir="$RUN" --run_mode=deep --disable_tap_extraction --purge_nets \
    $PORTS > "$RUN/lvs.log" 2>&1

python3 scripts/verify/lvs_summary.py "$RUN" $TOP
