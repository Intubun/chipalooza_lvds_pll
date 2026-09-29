#!/bin/bash
# Placement flow for lvds_tx: netlist -> leaf cells -> hierarchy -> DRC -> GDS.
#
#   docker exec iic-osic-tools_xserver bash -lc \
#     'bash /foss/designs/chipalooza_lvds_pll/macros/lvds_tx/layout/run_all.sh'
#
# This builds the placement only.  Nothing is routed, so there is no LVS step
# here: the cells are a frame for the routing that comes next.
#
# With --floorplan, make_floorplan.py rewrites floorplan.json from its plan
# before the placement is built; without it the stored floorplan is kept.
#
# Logs and the DRC run directories go to build/, which is rebuilt output.
#
# No `set -u`: sak-pdk-script.sh reads unset variables and would take the
# whole shell down with it.
cd "$(dirname "$0")" || exit 1
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
RC=/foss/pdks/ihp-sg13cmos5l/libs.tech/magic/ihp-sg13cmos5l.magicrc
B=build
mkdir -p $B
RES=0
bash check_untouched.sh > /dev/null

echo "== netlist =="
# The netlist is build output (it is in .gitignore), so it is regenerated
# from the schematic rather than trusted to be present and current.
mkdir -p ../netlist/schematic
xschem -s -r -x -q --rcfile ../schematic/xschem/xschemrc --command '
    set top_is_subckt 1;
    set lvs_ignore 1;
    set netlist_dir [file normalize ../netlist/schematic];
    xschem netlist
' ../schematic/xschem/lvds_tx.sch > $B/netlist.log 2>&1
if grep -q "IS MISSING" ../netlist/schematic/lvds_tx.spice 2>/dev/null; then
    echo "  unresolved symbols in the netlist -- is the PDK selected?"; RES=1
fi
python3 devices.py

echo "== leaf cells =="
bash build_cells.sh > $B/cells.log 2>&1
grep -E "^DRC |patched|generated:" $B/cells.log
grep -qE "^DRC .* [1-9][0-9]*$" $B/cells.log && { echo "  leaf cell DRC errors"; RES=1; }

if [ "$1" = "--floorplan" ]; then
    echo "== floorplan =="
    python3 make_floorplan.py || RES=1
fi

echo "== placement =="
python3 build_placement.py || RES=1

echo "== DRC =="
magic -dnull -noconsole -rcfile "$RC" check_drc.tcl > $B/drc.log 2>&1
grep -E "^DRC |TOTAL DRC|^RULE" $B/drc.log
grep -q "TOTAL DRC ERRORS: 0" $B/drc.log || RES=1

echo "== GDS =="
magic -dnull -noconsole -rcfile "$RC" save_gds.tcl > $B/gds.log 2>&1
ls -l lvds_tx_gen.gds | awk '{print "  lvds_tx_gen.gds", $5, "bytes"}'

# The pre-driver's scripted routing (route_predriver.py, check_lvs.sh) is
# switched off for now, while the metal stack is being reconsidered: the
# chip's power straps run vertically in Metal4 over the whole slot.

# The PDK asks for the klayout deck on sign-off; magic's checker is for
# interactive work.  Density is excluded: it is only meaningful on a whole
# chip, after fill generation.
echo "== klayout sign-off DRC =="
rm -rf $B/klayout_drc
python3 /foss/pdks/ihp-sg13cmos5l/libs.tech/klayout/tech/drc/run_drc.py \
    --path=lvds_tx_gen.gds --topcell=lvds_tx --run_dir=$B/klayout_drc --mp=4 \
    --no_density > $B/klayout_drc.log 2>&1
grep -E "DRC Check (Passed|Failed)|violations detected" $B/klayout_drc.log | tail -2
grep -q "DRC Check Passed" $B/klayout_drc.log || RES=1

# The placement with the hand-routed cells of lvds_tx.gds put back in.
# lvds_tx.gds is only read; what comes out is a file of its own.
if [ -f lvds_tx.gds ]; then
    echo "== routed cells =="
    python3 merge_routed.py || RES=1
    rm -rf $B/klayout_drc_merged
    python3 /foss/pdks/ihp-sg13cmos5l/libs.tech/klayout/tech/drc/run_drc.py \
        --path=lvds_tx_merged.gds --topcell=lvds_tx \
        --run_dir=$B/klayout_drc_merged --mp=4 --no_density \
        > $B/klayout_drc_merged.log 2>&1
    grep -E "DRC Check (Passed|Failed)|violations detected" \
        $B/klayout_drc_merged.log | tail -2
    grep -q "DRC Check Passed" $B/klayout_drc_merged.log || RES=1
fi

echo "== lvds_tx.gds =="
bash check_untouched.sh verify || RES=1

echo
[ $RES -eq 0 ] && echo "PLACEMENT CLEAN" || echo "FAILURES -- see $B/cells.log / $B/drc.log / $B/klayout_drc.log"
exit $RES
