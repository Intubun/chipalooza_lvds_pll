#!/usr/bin/env bash
# Per-block layout sign-off loop on an editable Magic hierarchy:
#
#   1. full Magic DRC on the .mag source
#   2. GDS export + layout netlist
#   3. Netgen LVS against a reference SPICE netlist
#   4. KLayout antenna check on the exported GDS
#   5. full-RC Magic PEX (unless NO_PEX=1)
#
#   signoff_cell.sh <mag_dir> <cell> <reference.spice> <out_dir>
#
# The GDS is written next to <mag_dir> (../<cell>.gds). Reports go to
# <out_dir>; the PEX netlist to <out_dir>/<cell>_magic_pex_3.spice.
# Exits non-zero on any DRC, LVS, or antenna failure. Run inside the
# IIC-OSIC container.
set -euo pipefail

if [ $# -ne 4 ]; then
  echo "usage: $0 <mag_dir> <cell> <reference.spice> <out_dir>" >&2
  exit 2
fi

HERE=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
MAG_DIR=$(realpath "$1")
CELL=$2
REFERENCE=$(realpath "$3")
OUT=$(realpath -m "$4")
GDS=$(realpath -m "$MAG_DIR/../$CELL.gds")
mkdir -p "$OUT"

export PDK_ROOT=${PDK_ROOT:-/foss/pdks}
export PDK=ihp-sg13cmos5l
export PDKPATH=$PDK_ROOT/$PDK
export SPICE_USERINIT_DIR=$PDKPATH/libs.tech/ngspice
export KLAYOUT_PATH=/headless/.klayout:$PDKPATH/libs.tech/klayout
export PATH=/foss/tools/bin:/foss/tools/klayout:$PATH

status=0

echo "== Magic DRC (editable .mag, drc(full))"
"$HERE/magic_batch.sh" "$MAG_DIR" "$HERE/mag_drc.tcl" CELL="$CELL" \
  >"$OUT/$CELL.mag_drc.log" 2>&1
drc_count=$(sed -n 's/^DRC_COUNT=//p' "$OUT/$CELL.mag_drc.log" | tail -1)
echo "   DRC_COUNT=${drc_count:-missing}"
[ "${drc_count:-1}" = 0 ] || status=1

echo "== GDS export + layout netlist"
"$HERE/magic_batch.sh" "$MAG_DIR" "$HERE/mag_export.tcl" CELL="$CELL" \
  GDS="$GDS" LVS_OUT="$OUT/${CELL}_layout.spice" EXT_DIR="$OUT/ext" \
  >"$OUT/$CELL.export.log" 2>&1
echo "   $GDS"

echo "== Netgen LVS"
# Magic extracts rhigh/cap_cmomf gencells as subcircuits of their own cell
# (dev_rhigh_*, dev_cap_cmomf_*) holding a plain R/C. Rewrite each schematic
# instance of those primitives to the matching layout cell so that Netgen
# compares like with like; the cell name encodes w/l, so a size mismatch
# still fails LVS.
python3 "$HERE/lvs_reference.py" "$REFERENCE" "$OUT/${CELL}_layout.spice" \
  "$OUT/${CELL}_reference.spice"
REFERENCE="$OUT/${CELL}_reference.spice"
netgen -batch lvs "$OUT/${CELL}_layout.spice $CELL" "$REFERENCE $CELL" \
  "$PDK_ROOT/$PDK/libs.tech/netgen/${PDK}_setup.tcl" \
  "$OUT/$CELL.lvs.out" >"$OUT/$CELL.lvs.log" 2>&1 || true
if grep -q "Circuits match uniquely" "$OUT/$CELL.lvs.out"; then
  echo "   Circuits match uniquely"
  if grep -q "property errors" "$OUT/$CELL.lvs.out"; then
    echo "   NOTE: property errors reported; inspect $OUT/$CELL.lvs.out"
  fi
else
  echo "   LVS MISMATCH; see $OUT/$CELL.lvs.out"
  status=1
fi

echo "== KLayout antenna"
rm -rf "$OUT/antenna"
python3 "$PDK_ROOT/$PDK/libs.tech/klayout/tech/drc/run_drc.py" \
  --path="$GDS" --topcell="$CELL" --run_dir="$OUT/antenna" --antenna_only \
  >"$OUT/$CELL.antenna.log" 2>&1 || true
if grep -q "No DRC violations detected" "$OUT/$CELL.antenna.log"; then
  echo "   antenna clean"
else
  echo "   ANTENNA VIOLATIONS; see $OUT/antenna"
  status=1
fi

if [ "${NO_PEX:-0}" != 1 ]; then
  echo "== Magic full-RC PEX"
  "$HERE/magic_batch.sh" "$MAG_DIR" "$HERE/mag_pex.tcl" CELL="$CELL" \
    PEX_OUT="$OUT/${CELL}_magic_pex_3.spice" EXT_DIR="$OUT/pex_ext" \
    >"$OUT/$CELL.pex.log" 2>&1
  echo "   $OUT/${CELL}_magic_pex_3.spice"
fi

rm -rf "$OUT/ext" "$OUT/pex_ext"
if [ "$status" = 0 ]; then
  echo "SIGNOFF PASS: $CELL"
else
  echo "SIGNOFF FAIL: $CELL"
fi
exit "$status"
