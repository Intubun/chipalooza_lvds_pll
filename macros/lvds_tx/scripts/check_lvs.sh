#!/bin/bash
# KLayout LVS of one routed cell against its schematic.
#
#   bash scripts/check_lvs.sh predriver     # or predriver_comp, predriver_stage
#   bash scripts/check_lvs.sh predriver layout/backups/<some copy>.gds
#
# The schematic side is exported from xschem as CDL, the layout side is
# layout/lvds_tx.gds (or the GDS given second) with that cell as top.
# Results go to build/lvs_<cell>/, the summary line to stdout.  Exit status
# 0 only when the netlists match.
#
# Taps are not extracted as devices (--disable_tap_extraction, as the
# container's sak-lvs.sh does): the schematic has none.  "Va" is joined by
# name (--implicit_nets): `predriver` has two Va rails, over the comparator
# loads and under the stage, which only the supply comb in `lvds_tx` joins.
#
# No `set -u`: sak-pdk-script.sh reads unset variables.
CELL=${1:-predriver}
GDS=$(realpath "${2:-$(dirname "$0")/../layout/lvds_tx.gds}")
cd "$(dirname "$0")/.." || exit 1          # macros/lvds_tx
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
RUN=build/lvs_$CELL
rm -rf "$RUN" && mkdir -p "$RUN"

xschem -s -r -x -q --rcfile schematic/xschem/xschemrc --command "
    set spiceprefix 1; set lvs_netlist 1; set top_is_subckt 1;
    set lvs_ignore 1; set ev_precision 5;
    set netlist_dir [file normalize $RUN];
    xschem set netlist_name ${CELL}.cdl; xschem netlist
" schematic/xschem/$CELL.sch > "$RUN/xschem.log" 2>&1

python3 /foss/pdks/ihp-sg13cmos5l/libs.tech/klayout/tech/lvs/run_lvs.py \
    --layout="$GDS" --netlist="$RUN/$CELL.cdl" --topcell="$CELL" \
    --run_dir="$RUN" --run_mode=deep --disable_tap_extraction \
    --implicit_nets=Va > "$RUN/lvs.log" 2>&1

if grep -q "Congratulations! Netlists match." "$RUN/lvs.log"; then
    echo "  LVS $CELL: Netzlisten stimmen ueberein"
    exit 0
fi
echo "  LVS $CELL: Netzlisten stimmen NICHT ueberein -- $RUN/lvs.log"
exit 1
