#!/bin/bash
# Placement flow for lvds_tx: netlist -> leaf cells -> hierarchy -> DRC -> GDS.
#
#   docker exec iic-osic-tools_xserver bash -lc \
#     'bash /foss/designs/chipalooza_lvds_pll/macros/lvds_tx/layout/run_all.sh'
#
# This builds the placement only.  Nothing is routed, so there is no LVS step
# here: the cells are a frame for the routing that comes next.
#
# No `set -u`: sak-pdk-script.sh reads unset variables and would take the
# whole shell down with it.
cd "$(dirname "$0")" || exit 1
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
RC=/foss/pdks/ihp-sg13cmos5l/libs.tech/magic/ihp-sg13cmos5l.magicrc
RES=0

echo "== netlist =="
# The netlist is build output (it is in .gitignore), so it is regenerated
# from the schematic rather than trusted to be present and current.
mkdir -p ../netlist/schematic
xschem -s -r -x -q --rcfile ../schematic/xschem/xschemrc --command '
    set top_is_subckt 1;
    set lvs_ignore 1;
    set netlist_dir [file normalize ../netlist/schematic];
    xschem netlist
' ../schematic/xschem/lvds_tx.sch > netlist.log 2>&1
if grep -q "IS MISSING" ../netlist/schematic/lvds_tx.spice 2>/dev/null; then
    echo "  unresolved symbols in the netlist -- is the PDK selected?"; RES=1
fi
python3 devices.py

echo "== leaf cells =="
bash build_cells.sh > cells.log 2>&1
grep -E "^DRC |patched|generated:" cells.log
grep -qE "^DRC .* [1-9][0-9]*$" cells.log && { echo "  leaf cell DRC errors"; RES=1; }

echo "== placement =="
python3 build_placement.py || RES=1

echo "== DRC =="
magic -dnull -noconsole -rcfile "$RC" check_drc.tcl > drc.log 2>&1
grep -E "^DRC |TOTAL DRC|^RULE" drc.log
grep -q "TOTAL DRC ERRORS: 0" drc.log || RES=1

echo "== GDS =="
magic -dnull -noconsole -rcfile "$RC" save_gds.tcl > gds.log 2>&1
ls -l lvds_tx_gen.gds | awk '{print "  lvds_tx_gen.gds", $5, "bytes"}'

# The PDK asks for the klayout deck on sign-off; magic's checker is for
# interactive work.  Density is excluded: it is only meaningful on a whole
# chip, after fill generation.
echo "== klayout sign-off DRC =="
rm -rf klayout_drc
python3 /foss/pdks/ihp-sg13cmos5l/libs.tech/klayout/tech/drc/run_drc.py \
    --path=lvds_tx_gen.gds --topcell=lvds_tx --run_dir=klayout_drc --mp=4 \
    --no_density > klayout_drc.log 2>&1
grep -E "DRC Check (Passed|Failed)|violations detected" klayout_drc.log | tail -2
grep -q "DRC Check Passed" klayout_drc.log || RES=1

echo
[ $RES -eq 0 ] && echo "PLACEMENT CLEAN" || echo "FAILURES -- see cells.log / drc.log / klayout_drc.log"
exit $RES
