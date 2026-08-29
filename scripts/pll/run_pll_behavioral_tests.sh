#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
PLL_DIR="$PROJECT_ROOT/schematic/xschem/pll"
RTL_DIR="$PLL_DIR/rtl"
TB_DIR="$PLL_DIR/testbenches/rtl"
TOOLS_BIN=${TOOLS_BIN:-/foss/tools/bin}
IVERILOG=${IVERILOG:-$TOOLS_BIN/iverilog}
VVP=${VVP:-$TOOLS_BIN/vvp}
WORK=$(mktemp -d "${TMPDIR:-/tmp}/pll-behavioral.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

sources=(
  "$RTL_DIR/pfd.v"
  "$RTL_DIR/fractional_divider.v"
  "$RTL_DIR/clock_output_divider.v"
  "$RTL_DIR/pll_digital.v"
  "$RTL_DIR/pll_behavioral.v"
  "$TB_DIR/tb_pll_behavioral.v"
)

run_case() {
  local name=$1 integer=$2 fractional=$3 ref_period_ns=$4
  local output="$WORK/$name"
  "$IVERILOG" -g2012 -s tb_pll_behavioral \
    -Ptb_pll_behavioral.DIV_INTEGER="$integer" \
    -Ptb_pll_behavioral.DIV_FRACTIONAL="$fractional" \
    -Ptb_pll_behavioral.REF_PERIOD_NS="$ref_period_ns" \
    -o "$output" "${sources[@]}"
  "$VVP" "$output"
}

run_case ref25_out500_int 40 0 40.0
run_case ref25_out1g_int 80 0 40.0
run_case ref250_out500_int 4 0 4.0
run_case ref250_out1g_int 8 0 4.0
run_case ref25_frac 40 32768 40.0
run_case ref25_high_frac 79 32768 40.0
run_case ref100_frac 19 32768 10.0
run_case ref250_frac 4 32768 4.0
run_case ref250_high_frac 7 32768 4.0

echo "ALL BEHAVIORAL PLL TESTS PASSED"
