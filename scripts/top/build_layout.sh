#!/bin/bash
# The top-level layout, from the hand-drawn floor plan to layout/slot_14.gds (2026-10-07).
#
#   bash scripts/top/build_layout.sh             # the chain into build/top/, nothing else
#   bash scripts/top/build_layout.sh --install   # ... and copy the result to layout/slot_14(.klay).gds
#
# layout/slot_14_base.gds is the floor plan as drawn in KLayout: the blocks, the
# lines between them and their stubs, the control lines from dig_in, the
# frame.  Each step reads the one before:
#
#   1_shift.gds   floorplan_shift.py  the LVDS group up by 92.25 um, old pad and control lines out
#   2_route.gds   route_top.py        lvds_pattern from its macro, control lines, reset diode,
#                                     bias, supplies, decaps
#   3_pads.gds    route_pads.py       Out_n -> pad 0, Out_p -> pad 1, ref_clk <- pad 2
#   4_odt.gds     add_odt.py          the ref_clk termination on pad 2, wired
#   5_bt.gds      add_bt.py           the switchable back-termination of the LVDS pair, wired
#
# --install refuses when layout/slot_14.klay.gds differs from slot_14.gds - a
# KLayout save would be lost - and keeps the old one in layout/backups/.
set -e
cd "$(dirname "$0")/../.."
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1 || true
B=build/top
mkdir -p $B
python3 scripts/top/floorplan_shift.py --in layout/slot_14_base.gds --out $B/1_shift.gds
python3 scripts/top/route_top.py       --in $B/1_shift.gds          --out $B/2_route.gds
python3 scripts/top/route_pads.py      --in $B/2_route.gds          --out $B/3_pads.gds
python3 scripts/top/add_odt.py         --in $B/3_pads.gds           --out $B/4_odt.gds
python3 scripts/top/add_bt.py          --in $B/4_odt.gds            --out $B/5_bt.gds

if [ "$1" = --install ]; then
    if ! cmp -s layout/slot_14.gds layout/slot_14.klay.gds; then
        echo "layout/slot_14.klay.gds differs from slot_14.gds (a KLayout save?) - nothing installed"
        exit 1
    fi
    ts=$(date +%Y-%m-%d_%Hh%Mm%Ss)
    mkdir -p layout/backups
    cp layout/slot_14.gds layout/backups/slot_14_VOR_build_$ts.gds
    cp $B/5_bt.gds layout/slot_14.gds
    cp $B/5_bt.gds layout/slot_14.klay.gds
    echo "installiert: layout/slot_14.gds (+ .klay.gds), alt: layout/backups/slot_14_VOR_build_$ts.gds"
fi
