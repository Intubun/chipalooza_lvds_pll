#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
PLL_DIR="$PROJECT_ROOT/macros/pll_analog/schematic/xschem"
WORK=$(mktemp -d /tmp/pll-ring-pvt.XXXXXX)
JOBS=${JOBS:-4}
KEEP_WORK=${KEEP_WORK:-0}
TEMPS=${TEMPS:-"-40 27 125"}
CORNERS=${CORNERS:-"tt ss ff sf fs"}
VDDS=${VDDS:-"1.08 1.20 1.32"}
VCTRLS=${VCTRLS:-"0.80"}
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
export SPICE_USERINIT_DIR=$PDK_ROOT/ihp-sg13cmos5l/libs.tech/ngspice

(cd "$PLL_DIR" && env -u DISPLAY xschem --no_x -n -q -o "$WORK" ring_oscillator.sch) \
  >"$WORK/xschem.log" 2>&1
test ! -s "$WORK/xschem.log" || { cat "$WORK/xschem.log" >&2; exit 1; }

sed -e 's/^\*\*\.subckt ring_oscillator/.subckt ring_oscillator/' \
    -e '0,/^\*\*\.ends$/s//.ends/' \
    -e '/^\.end$/d' \
    "$WORK/ring_oscillator.spice" > "$WORK/ring_base.spice"

run_point() {
  local corner=$1 vdd=$2 temp=$3 vctrl=$4 log t1 t2 idd vbp vmin vmax
  log="$WORK/${corner}_${vdd}_${temp}_${vctrl}.log"

  {
    cat "$WORK/ring_base.spice"
    cat <<EOF
.lib ${PDK_ROOT}/ihp-sg13cmos5l/libs.tech/ngspice/models/cornerMOSlv.lib mos_${corner}
XRO VCTRL FREQ VDD 0 ring_oscillator
VDD_SRC VDD 0 ${vdd}
VCTRL_SRC VCTRL 0 ${vctrl}
CLOAD FREQ 0 5f
.ic v(XRO.VCO_CORE)=0 v(XRO.net1)=${vdd} v(XRO.net2)=0
.options temp=${temp}
.control
save v(FREQ) v(XRO.VCO_CORE) v(XRO.VBP) i(VDD_SRC)
tran 2p 8n uic
meas tran t1 when v(FREQ)=${vdd}/2 rise=1 TD=3n
meas tran t2 when v(FREQ)=${vdd}/2 rise=2 TD=3n
meas tran idd avg i(VDD_SRC) from=3n to=8n
meas tran vbp avg v(XRO.VBP) from=3n to=8n
meas tran vmin min v(FREQ) from=3n to=8n
meas tran vmax max v(FREQ) from=3n to=8n
.endc
.end
EOF
  } | ngspice -b >"$log" 2>&1 || { cat "$log" >&2; return 1; }

  get_value() { awk -v name="$1" '$1 == name && $2 == "=" { print $3; exit }' "$log"; }
  t1=$(get_value t1)
  t2=$(get_value t2)
  idd=$(get_value idd)
  vbp=$(get_value vbp)
  vmin=$(get_value vmin)
  vmax=$(get_value vmax)

  if [[ -n $t1 && -n $t2 && -n $idd ]]; then
    awk -v c="$corner" -v v="$vdd" -v t="$temp" -v ctrl="$vctrl" -v pctrl="$vbp" \
        -v a="$t1" -v b="$t2" -v i="$idd" -v lo="$vmin" -v hi="$vmax" \
      'BEGIN {
        frequency = 1 / (b - a)
        current = -i
        power = v * current
        energy = power / frequency
        printf "%s,%.2f,%d,%.4g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g\n", \
          c, v, t, ctrl, pctrl, frequency, current, power, energy, lo, hi
      }'
  else
    printf '%s,%.2f,%d,%.4g,%s,FAIL,FAIL,FAIL,FAIL,%s,%s\n' \
      "$corner" "$vdd" "$temp" "$vctrl" "$vbp" "$vmin" "$vmax"
  fi
}
export -f run_point
export WORK
export TEMPS
export CORNERS
export VDDS
export VCTRLS

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

echo 'corner,vdd_v,temp_c,vctrl_v,vbp_v,freq_hz,current_a,power_w,energy_j,vmin_v,vmax_v'
sort -t, -k1,1 -k2,2n -k3,3n -k4,4n "$WORK/results.unsorted.csv"
