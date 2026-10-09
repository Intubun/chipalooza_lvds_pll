#!/bin/bash
# DRC (antenna rules included) and LVS of layout/lvds_bt.gds against schematic/xschem/lvds_bt.sch
#
#   bash macros/lvds_bt/scripts/check.sh          # in the container
#
# Results in build/lvds_bt/{drc,lvs}/.  Exit status 0 only when both are clean.
# No `set -u`: sak-pdk-script.sh reads unset variables.
TOP=lvds_bt
cd "$(dirname "$0")/.." || exit 1
M=$PWD
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
B=$M/../../build/$TOP
rm -rf "$B" && mkdir -p "$B/drc" "$B/lvs"

python3 "$PDK_ROOT/$PDK/libs.tech/klayout/tech/drc/run_drc.py" --path="$M/layout/$TOP.gds" \
    --topcell=$TOP --run_dir="$B/drc" --mp=4 --no_density --antenna > "$B/drc/drc.log" 2>&1
N=$(python3 - "$B/drc" <<'EOF'
import glob, sys, klayout.rdb as rdb
n = 0
for f in glob.glob(sys.argv[1] + "/*.lyrdb"):
    db = rdb.ReportDatabase(""); db.load(f)
    for cat in db.each_category():
        k = cat.num_items()
        if k:
            print("   %-28s %d" % (cat.name(), k), file=sys.stderr); n += k
print(n)
EOF
)
echo "== DRC $TOP: $N Fehler"

xschem -s -r -x -q --rcfile schematic/xschem/xschemrc --command "
    set spiceprefix 1; set lvs_netlist 1; set top_is_subckt 1; set lvs_ignore 1;
    set netlist_dir [file normalize $B/lvs];
    xschem set netlist_name $TOP.cdl; xschem netlist
" schematic/xschem/$TOP.sch > "$B/lvs/xschem.log" 2>&1
python3 "$PDK_ROOT/$PDK/libs.tech/klayout/tech/lvs/run_lvs.py" --layout="$M/layout/$TOP.gds" \
    --netlist="$B/lvs/$TOP.cdl" --topcell=$TOP --run_dir="$B/lvs" --run_mode=deep \
    --disable_tap_extraction > "$B/lvs/lvs.log" 2>&1
if grep -q "Congratulations! Netlists match" "$B/lvs/lvs.log"; then
    echo "== LVS $TOP: Netzlisten stimmen ueberein"; L=0
else
    echo "== LVS $TOP: Unterschiede -- $B/lvs/lvs.log"; L=1
fi
[ "$N" = 0 ] && [ "$L" = 0 ]
