#!/usr/bin/env bash
# Guard the d_cosim port order.
#
# pll_digital_cosim.sym pins the order of the RTL ports into its format string:
#
#   format="@name [ @@ref_clk @@vco_clk @@reset_n @@enable
#                   @@test_div_select[1..0] @@div_ratio[9..0] ]
#                 [ @@feedback_clk @@up @@down @@pll_clk @@test_clk ] @model"
#
# d_cosim passes the two bundles positionally, so a reordered port list in
# macros/pll_digital/rtl would silently connect the block wrong rather than
# fail. Verilator writes the order it actually used into inputs.h / outputs.h,
# so compare the two and stop the build on a mismatch.
#
# Usage: check_cosim_ports.sh <pll_digital_obj_dir>
set -euo pipefail

OBJ_DIR=${1:?usage: check_cosim_ports.sh <pll_digital_obj_dir>}

EXPECT_IN="ref_clk vco_clk reset_n enable test_div_select div_ratio"
EXPECT_OUT="feedback_clk up down pll_clk test_clk"

# VL_DATA(8,ref_clk,0,0) -> ref_clk, without needing a backreference
names() {
  grep -o "VL_DATA([0-9]*,[a-z_]*" "$1" | cut -d, -f2 | paste -sd' ' -
}

ACTUAL_IN=$(names "$OBJ_DIR/inputs.h")
ACTUAL_OUT=$(names "$OBJ_DIR/outputs.h")

if [ "$ACTUAL_IN" != "$EXPECT_IN" ] || [ "$ACTUAL_OUT" != "$EXPECT_OUT" ]; then
  echo "ERROR: d_cosim port order changed - update pll_digital_cosim.sym" >&2
  echo "  inputs   expected: $EXPECT_IN" >&2
  echo "           actual:   $ACTUAL_IN" >&2
  echo "  outputs  expected: $EXPECT_OUT" >&2
  echo "           actual:   $ACTUAL_OUT" >&2
  exit 1
fi

echo "d_cosim port order matches pll_digital_cosim.sym"
