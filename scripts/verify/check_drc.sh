#!/bin/bash
# Top-level DRC (KLayout, IHP deck) of layout/sg13cmos5l_chipalooza_analog_project.gds.
#
#   bash scripts/verify/check_drc.sh                # in the container, from anywhere
#   bash scripts/verify/check_drc.sh --with-pll     # count Rahul's PLL cells too
#   bash scripts/verify/check_drc.sh --no-antenna   # skip the antenna rules (faster)
#   bash scripts/verify/check_drc.sh --density      # include the density rules
#   bash scripts/verify/check_drc.sh <gds>          # another copy of the top layout
#
# Checks a snapshot of the file (KLayout may save while the deck runs).  Results in
# build/verify/drc/: the snapshot, *_full.lyrdb (open it in KLayout: Tools > Marker
# Browser), drc.log.  The summary sorts the errors by the top-level cell they sit
# in; errors only in cells of the PLL are listed but not counted until it is
# finished (--with-pll counts them).  Exit status 0 only when nothing counted is left.
#
# Density is off by default: the slot is checked for density at chip level, with
# the fill the harness adds.
#
# No `set -u`: sak-pdk-script.sh reads unset variables.
TOP=sg13cmos5l_chipalooza_analog_project
cd "$(dirname "$0")/../.." || exit 1
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
ANT=--antenna
DENS=--no_density
PLL=
GDS=layout/$TOP.gds
while [ $# -gt 0 ]; do
    case $1 in
        --with-pll) PLL=--with-pll ;;
        --no-antenna) ANT= ;;
        --density) DENS= ;;
        -h|--help) sed -n 2,20p "$0"; exit 0 ;;
        *) GDS=$1 ;;
    esac
    shift
done
RUN=build/verify/drc
rm -rf "$RUN" && mkdir -p "$RUN"
cp "$GDS" "$RUN/$TOP.gds"
echo "== DRC $TOP ($GDS$([ -n "$ANT" ] && echo ", mit Antenne")$([ -z "$DENS" ] && echo ", mit Dichte"))"
python3 "$PDK_ROOT/$PDK/libs.tech/klayout/tech/drc/run_drc.py" \
    --path="$RUN/$TOP.gds" --topcell=$TOP --run_dir="$RUN" --mp=4 $DENS $ANT \
    > "$RUN/drc.log" 2>&1
python3 scripts/verify/drc_summary.py "$RUN" "$RUN/$TOP.gds" $TOP $PLL
