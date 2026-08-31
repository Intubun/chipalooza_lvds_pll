#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
PLL_DIR="$PROJECT_ROOT/macros/pll_digital"
RTL_DIR="$PLL_DIR/rtl"
TB_DIR="$PLL_DIR/testbenches/verilog"
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
  local name=$1 ratio=$2 ref_period_ns=$3
  local output="$WORK/$name"
  "$IVERILOG" -g2012 -s tb_pll_behavioral \
    -Ptb_pll_behavioral.DIV_RATIO="$ratio" \
    -Ptb_pll_behavioral.REF_PERIOD_NS="$ref_period_ns" \
    -o "$output" "${sources[@]}"
  "$VVP" "$output"
}

run_case ref25_out500_int 320 40.0
run_case ref25_out1g_int 640 40.0
run_case ref250_out500_int 32 4.0
run_case ref250_out1g_int 64 4.0
run_case ref25_frac 324 40.0
run_case ref25_high_frac 636 40.0
run_case ref100_frac 156 10.0
run_case ref250_frac 36 4.0
run_case ref250_high_frac 60 4.0

echo "ALL BEHAVIORAL PLL TESTS PASSED"
