#!/usr/bin/env bash
# Netlist every top-level bench, so that xschem's Simulate arrow works on any of
# them.
#
# The arrow does not netlist - proc simulate in xschem.tcl only computes the
# netlist path and runs ngspice on whatever is already there. So a bench is
# ready for the arrow once its netlist exists. (Until 2026-10-07 this also
# injected the PLL's d_cosim auto-bridges; the PLL has left the project.)
#
# make sim-xschem netlists a single bench the same way before simulating.
#
# Usage: prepare_benches.sh <repo_root> [bench.sch ...]
set -euo pipefail

ROOT=${1:?usage: prepare_benches.sh <repo_root> [bench.sch ...]}
shift || true

TB_DIR="$ROOT/testbenches/xschem"
SIM_DIR="$TB_DIR/simulations"

mkdir -p "$SIM_DIR"

if [ "$#" -gt 0 ]; then
  BENCHES=("$@")
else
  BENCHES=("$TB_DIR"/*_tb_*.sch)
fi

ok=0
fail=0
for sch in "${BENCHES[@]}"; do
  name=$(basename "$sch" .sch)
  # xschem returns non-zero on schematics it still netlists correctly, so the
  # netlist itself is what gets checked, not the exit status.
  (cd "$TB_DIR" && xschem -r -x -q --rcfile xschemrc --command "
      xschem set netlist_type spice
      set netlist_dir $SIM_DIR
      xschem netlist
   " "$name.sch") >/dev/null 2>&1 || true

  spice="$SIM_DIR/$name.spice"
  if [ ! -s "$spice" ] || ! grep -qE '^[Xx]' "$spice"; then
    printf '  %-58s NETLIST FAILED\n' "$name"
    fail=$((fail + 1))
    continue
  fi
  printf '  %-58s ready\n' "$name"
  ok=$((ok + 1))
done

echo "  ---"
echo "  $ok bench(es) ready for the Simulate arrow, $fail failed"
[ "$fail" -eq 0 ]
