#!/bin/bash
# Regenerate the device cells (dev_*) of layout/lvds_tx.gds from the
# schematic -- and nothing else in the file.  Runs inside the IIC-OSIC-TOOLS
# container:
#
#   make layout-pcells           (in macros/lvds_tx)
#   make layout-pcells-check     the same as a dry run: reports, writes nothing
#
#   1. the netlist of the schematic               -> netlist/schematic/
#   2. one magic gencell per device geometry      -> build/pcells/cells/
#   3. the gencells' DRC errors patched out, every cell DRC'd
#   4. every cell written to a GDS of its own     -> build/pcells/gds/
#   5. swap_pcells.py takes them into layout/lvds_tx.gds; the old file goes
#      to layout/backups/ first
#
# Save in KLayout before, reload after: KLayout keeps its own copy of the
# file until it is told to read it again.
#
# No `set -u`: sak-pdk-script.sh reads unset variables.
cd "$(dirname "$0")/../.." || exit 1          # macros/lvds_tx
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
set -o pipefail
RC=/foss/pdks/ihp-sg13cmos5l/libs.tech/magic/ihp-sg13cmos5l.magicrc
P=$(pwd)/scripts/pcells
B=build/pcells
NET=netlist/schematic/lvds_tx.spice
mkdir -p $B netlist/schematic

echo "== Netzliste =="
# Build output (.gitignore), so it is written fresh every time: a stale
# netlist cannot outlive the schematic it came from.
rm -f $NET
xschem -s -r -x -q --rcfile schematic/xschem/xschemrc --command '
    set top_is_subckt 1;
    set lvs_ignore 1;
    set netlist_dir [file normalize netlist/schematic];
    xschem netlist
' schematic/xschem/lvds_tx.sch > $B/netlist.log 2>&1
if [ ! -s $NET ] || grep -q "IS MISSING" $NET; then
    echo "  Netzliste fehlt oder ist unvollstaendig -- $B/netlist.log"
    exit 1
fi
echo "  $NET"

echo "== Zellen =="
rm -rf $B/cells $B/gds && mkdir -p $B/cells $B/gds
python3 $P/gen_devices.py $B/cells/gen_devices.tcl | sed 's/^/  /' || exit 1
(cd $B/cells && magic -dnull -noconsole -rcfile "$RC" gen_devices.tcl \
    > gen_devices.log 2>&1)
if grep -q "^ERROR" $B/cells/gen_devices.log; then
    grep "^ERROR" $B/cells/gen_devices.log | sed 's/^/  /'
    exit 1
fi
MADE=$(grep -c "^MADE " $B/cells/gen_devices.log)
echo "  erzeugt: $MADE"
python3 $P/patch_cells.py $B/cells | sed 's/^/  /' || exit 1

(cd $B/cells && magic -dnull -noconsole -rcfile "$RC" \
    $P/check_drc_cells.tcl > ../drc.log 2>&1)
# "^DRC dev_", not "^DRC ": magic says "DRC style is now ..." first
CHECKED=$(grep -c "^DRC dev_" $B/drc.log)
DIRTY=$(awk '/^DRC dev_/ && $3 > 0 {print "  " $0}' $B/drc.log)
if [ -n "$DIRTY" ] || [ "$CHECKED" -ne "$MADE" ]; then
    echo "$DIRTY"
    echo "  DRC: $CHECKED von $MADE Zellen geprueft, nicht alle sauber" \
         "-- lvds_tx.gds bleibt, wie es ist ($B/drc.log)"
    exit 1
fi
echo "  DRC: alle $CHECKED sauber"
# cells without a guard ring have no tap; the cell above them provides it
LU=$(grep -c "^LU dev_" $B/drc.log)
[ "$LU" -gt 0 ] && echo "  ohne Ring (LU.a/b, Taps in der Zelle darueber): $LU Zellen"

(cd $B/cells && magic -dnull -noconsole -rcfile "$RC" \
    $P/export_pcells.tcl > ../gds.log 2>&1)
WRITTEN=$(ls $B/gds/dev_*.gds 2>/dev/null | wc -l)
if [ "$WRITTEN" -ne "$MADE" ]; then
    echo "  GDS: nur $WRITTEN von $MADE Zellen geschrieben -- $B/gds.log"
    exit 1
fi

echo "== layout/lvds_tx.gds =="
python3 $P/swap_pcells.py "$@"
