#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
PLL_DIR="$PROJECT_ROOT/macros/pll_analog/schematic/xschem"
WORK=$(mktemp -d /tmp/pll-cp-pvt.XXXXXX)
JOBS=${JOBS:-4}
KEEP_WORK=${KEEP_WORK:-0}
TEMPS=${TEMPS:-"-40 27 125"}
CORNERS=${CORNERS:-"tt ss ff sf fs"}
VDDS=${VDDS:-"1.08 1.20 1.32"}
VCTRLS=${VCTRLS:-"0.50 0.60 0.70 0.80 0.90"}
cleanup() {
  if [[ $KEEP_WORK == 1 ]]; then
    echo "Characterization work directory: $WORK" >&2
  else
    rm -rf "$WORK"
  fi
}
trap cleanup EXIT

export PATH=/foss/tools/xschem/bin:/foss/tools/ngspice/bin:/foss/tools/sak:$PATH
export HOME=${HOME:-/headless}
export TOOLS=${TOOLS:-/foss/tools}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks}
export DESIGNS=${DESIGNS:-/foss/designs}
export PDK=ihp-sg13cmos5l
export PDKPATH=$PDK_ROOT/$PDK
export SPICE_USERINIT_DIR=$PDKPATH/libs.tech/ngspice

(cd "$PLL_DIR" && env -u DISPLAY xschem -n -q -x -o "$WORK" -N charge_pump.spice charge_pump.sch || [[ $? -eq 10 ]]) \
  >"$WORK/xschem.log" 2>&1
test ! -s "$WORK/xschem.log" || { cat "$WORK/xschem.log" >&2; exit 1; }
test -s "$WORK/charge_pump.spice"

sed -e 's/^\*\*\.subckt charge_pump/.subckt charge_pump/' \
    -e '0,/^\*\*\.ends$/s//.ends/' \
    -e '/^\.end$/d' \
    "$WORK/charge_pump.spice" > "$WORK/charge_pump_base.spice"

run_point() {
  local corner=$1 vdd=$2 temp=$3 vctrl=$4 log
  log="$WORK/${corner}_${vdd}_${temp}_${vctrl}.log"
  {
    cat "$WORK/charge_pump_base.spice"
    cat <<EOF
.lib ${PDK_ROOT}/ihp-sg13cmos5l/libs.tech/ngspice/models/cornerMOSlv.lib mos_${corner}
XCP UP DOWN IREF VCTRL VDD 0 charge_pump
VDD_SRC VDD 0 ${vdd}
IREF_SRC IREF 0 -2u
VUP UP 0 ${vdd}
VDOWN DOWN 0 0
VCTRL_CLAMP VCTRL 0 ${vctrl}
.options temp=${temp}
.control
op
print i(VCTRL_CLAMP)
alter VUP=0
alter VDOWN=${vdd}
op
print i(VCTRL_CLAMP)
alter VUP=${vdd}
op
print i(VCTRL_CLAMP)
.endc
.end
EOF
  } | ngspice -b >"$log" 2>&1 || { cat "$log" >&2; return 1; }

  mapfile -t currents < <(awk '/i\(vctrl_clamp\) =/ { print $3 }' "$log")
  if [[ ${#currents[@]} -ne 3 ]]; then
    cat "$log" >&2
    return 1
  fi
  awk -v c="$corner" -v v="$vdd" -v t="$temp" -v ctrl="$vctrl" \
      -v up="${currents[0]}" -v down="${currents[1]}" -v both="${currents[2]}" \
    'BEGIN {
      avg = (up - down) / 2
      mismatch = 100 * (up + down) / avg
      if (mismatch < 0) mismatch = -mismatch
      printf "%s,%.2f,%d,%.2f,%.9g,%.9g,%.9g,%.4f\n", \
        c, v, t, ctrl, up, down, both, mismatch
    }'
}
export -f run_point
export WORK PDK_ROOT

{
  for corner in $CORNERS; do
    for vdd in $VDDS; do
      for temp in $TEMPS; do
        for vctrl in $VCTRLS; do
          printf '%s %s %s %s\n' "$corner" "$vdd" "$temp" "$vctrl"
        done
      done
    done
  done
} | xargs -P "$JOBS" -n 4 bash -c 'run_point "$@"' _ > "$WORK/results.unsorted.csv"

echo 'corner,vdd_v,temp_c,vctrl_v,up_a,down_a,both_a,mismatch_pct'
sort -t, -k1,1 -k2,2n -k3,3n -k4,4n "$WORK/results.unsorted.csv"
