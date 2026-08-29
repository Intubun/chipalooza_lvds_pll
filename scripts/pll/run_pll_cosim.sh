#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
PLL_DIR="$PROJECT_ROOT/macros/pll_analog/schematic/xschem"
RTL_DIR="$PROJECT_ROOT/macros/pll_digital/rtl"
DIV_INTEGER=${DIV_INTEGER:-20}
DIV_FRACTIONAL=${DIV_FRACTIONAL:-0}
TEST_DIV=${TEST_DIV:-1}
FREF_HZ=${FREF_HZ:-100e6}
SIM_TIME_S=${SIM_TIME_S:-4e-6}
MAX_STEP_S=${MAX_STEP_S:-5e-12}
VDD=${VDD:-1.2}
CORNER=${CORNER:-tt}
TEMP_C=${TEMP_C:-27}
TOOLS_BIN=${TOOLS_BIN:-/foss/tools/bin}
REAL_VERILATOR=${REAL_VERILATOR:-$TOOLS_BIN/verilator}

python3 - "$DIV_INTEGER" "$DIV_FRACTIONAL" "$TEST_DIV" "$FREF_HZ" "$SIM_TIME_S" "$CORNER" "$TEMP_C" <<'PY'
import sys
integer, fractional, test_div = map(int, sys.argv[1:4])
fref, sim_time = map(float, sys.argv[4:6])
corner = sys.argv[6]
temp = float(sys.argv[7])
if not 4 <= integer <= 80:
    raise SystemExit("DIV_INTEGER must be 4-80")
if not 0 <= fractional <= 65535:
    raise SystemExit("DIV_FRACTIONAL must be 0-65535")
if not 0 <= test_div <= 3:
    raise SystemExit("TEST_DIV must be 0-3")
if not 25e6 <= fref <= 250e6:
    raise SystemExit("FREF_HZ must be 25e6-250e6")
if sim_time < 2e-6:
    raise SystemExit("SIM_TIME_S must be at least 2e-6")
if corner not in ("tt", "ss", "ff", "sf", "fs"):
    raise SystemExit("CORNER must be tt, ss, ff, sf, or fs")
if not -40 <= temp <= 125:
    raise SystemExit("TEMP_C must be -40 to 125")
PY

WORK=$(mktemp -d "${TMPDIR:-/tmp}/pll-cosim.XXXXXX")
cleanup() {
  if [[ ${KEEP_WORK:-0} == 1 ]]; then
    echo "co-simulation work directory: $WORK" >&2
  else
    rm -rf "$WORK"
  fi
}
trap cleanup EXIT
mkdir -p "$WORK/bin"

# ngspice-46's vlnggen helper lowercases case-sensitive Verilator options and
# does not parse Verilator-5 port declarations. This temporary wrapper fixes
# those compatibility issues and supplies the known pll_digital port table.
cat >"$WORK/bin/verilator" <<'EOF'
#!/usr/bin/env bash
args=()
previous=""
mdir=""
for argument in "$@"; do
  case "$argument" in
    --mdir) argument=-Mdir ;;
    --cflags) argument=-CFLAGS ;;
    -i/foss/*) argument="-I${argument:2}" ;;
  esac
  if [[ "$previous" == --prefix && "$argument" == vlng ]]; then
    argument=Vlng
  fi
  if [[ "$previous" == -Mdir ]]; then
    mdir=$argument
  fi
  args+=("$argument")
  previous=$argument
done

if [[ " ${args[*]} " == *" --build "* && -n "$mdir" ]]; then
  cat >"$mdir/inputs.h" <<'HEAD'
VL_DATA(8, ref_clk, 0, 0)
VL_DATA(8, vco_clk, 0, 0)
VL_DATA(8, reset_n, 0, 0)
VL_DATA(8, enable, 0, 0)
VL_DATA(8, div_integer, 6, 0)
VL_DATA(16, div_fractional, 15, 0)
VL_DATA(8, test_div_select, 1, 0)
HEAD
  cat >"$mdir/outputs.h" <<'HEAD'
VL_DATA(8, feedback_clk, 0, 0)
VL_DATA(8, pll_clk, 0, 0)
VL_DATA(8, test_clk, 0, 0)
VL_DATA(8, up, 0, 0)
VL_DATA(8, down, 0, 0)
HEAD
  : >"$mdir/inouts.h"
fi

"$REAL_VERILATOR" "${args[@]}"
status=$?
if [[ $status -eq 0 && -n "$mdir" && -f "$mdir/Vlng.h" ]]; then
  ln -sf Vlng.h "$mdir/vlng.h"
  if [[ -f "$mdir/Vlng__ALL.a" ]]; then
    ln -sf Vlng__ALL.a "$mdir/vlng__all.a"
  fi
fi
exit "$status"
EOF
chmod +x "$WORK/bin/verilator"

export REAL_VERILATOR
export PATH="$WORK/bin:$TOOLS_BIN:$PATH"
export PDK_ROOT=${PDK_ROOT:-/foss/pdks}
export PDK=${PLL_PDK:-ihp-sg13cmos5l}
export PDKPATH=${PLL_PDKPATH:-$PDK_ROOT/$PDK}
export SPICE_USERINIT_DIR=$PDKPATH/libs.tech/ngspice

(
  cd "$WORK"
  ngspice vlnggen \
    "$RTL_DIR/pll_digital.v" \
    "$RTL_DIR/pfd.v" \
    "$RTL_DIR/fractional_divider.v" \
    "$RTL_DIR/clock_output_divider.v" >build.log 2>&1
  mv pll_digital.so pll_digital_cosim.so
)

expected_inputs='ref_clk vco_clk reset_n enable div_integer test_div_select div_fractional'
expected_outputs='feedback_clk up down pll_clk test_clk'
actual_inputs=$(sed -n 's/^VL_DATA([^,]*,\([^,]*\),.*/\1/p' "$WORK/pll_digital_obj_dir/inputs.h" | paste -sd' ' -)
actual_outputs=$(sed -n 's/^VL_DATA([^,]*,\([^,]*\),.*/\1/p' "$WORK/pll_digital_obj_dir/outputs.h" | paste -sd' ' -)
if [[ $actual_inputs != "$expected_inputs" || $actual_outputs != "$expected_outputs" ]]; then
  printf 'd_cosim port order changed; update pll_digital_cosim.sym before simulation.\n' >&2
  printf 'inputs:  %s\noutputs: %s\n' "$actual_inputs" "$actual_outputs" >&2
  exit 1
fi

(
  cd "$PLL_DIR"
  env -u DISPLAY xschem -n -q -x -o "$WORK" -N pll_cosim.spice ../../testbenches/xschem/pll_cosim.tb.sch \
    >"$WORK/xschem.log" 2>&1 || [[ $? -eq 10 ]]
)

export DIV_INTEGER DIV_FRACTIONAL TEST_DIV FREF_HZ SIM_TIME_S MAX_STEP_S VDD CORNER TEMP_C
python3 - "$WORK/pll_cosim.spice" <<'PY'
import os
import re
import sys

path = sys.argv[1]
text = open(path).read()
integer = int(os.environ["DIV_INTEGER"])
fractional = int(os.environ["DIV_FRACTIONAL"])
test_div = int(os.environ["TEST_DIV"])
fref = float(os.environ["FREF_HZ"])
sim_time = float(os.environ["SIM_TIME_S"])
max_step = float(os.environ["MAX_STEP_S"])
vdd = float(os.environ["VDD"])
corner = os.environ["CORNER"]
temp = float(os.environ["TEMP_C"])
period = 1.0 / fref
settled_start = sim_time - 1.0e-6

text = re.sub(
    r"VREF REF_CLK 0 PULSE\([^\n]+\)",
    f"VREF REF_CLK 0 PULSE(0 {vdd} 1n 20p 20p {period / 2 - 20e-12:.12g} {period:.12g})",
    text,
)
text = re.sub(r"VDD_SRC VDD 0 \S+", f"VDD_SRC VDD 0 {vdd}", text)
text = re.sub(r"VENABLE ENABLE 0 \S+", f"VENABLE ENABLE 0 {vdd}", text)
text = text.replace("PULSE(0 1.2 2n", f"PULSE(0 {vdd} 2n")
text = text.replace("mos_tt", f"mos_{corner}")
text = text.replace(".options temp=27", f".options temp={temp}")
text = text.replace("v(x_pll.x_analog.x_vco.net1)=1.2", f"v(x_pll.x_analog.x_vco.net1)={vdd}")
for prefix, width, value in (
    ("DIV_INT", 7, integer),
    ("DIV_FRAC", 16, fractional),
    ("TEST_DIV", 2, test_div),
):
    source_prefix = "V" + prefix
    for bit in range(width):
        voltage = vdd if (value >> bit) & 1 else 0
        text = re.sub(
            rf"^{source_prefix}{bit} {prefix}{bit} 0 \S+",
            f"{source_prefix}{bit} {prefix}{bit} 0 {voltage}",
            text,
            flags=re.MULTILINE,
        )

commands = [
    ".control",
    "set numdgt=15",
    'pre_set auto_bridge_d_in = ( ".model auto_adc adc_bridge(in_low=0.3 in_high=0.9 rise_delay=5p fall_delay=5p)" "auto_bridge%d [ %s ] [ %s ] auto_adc" )',
    f'pre_set auto_bridge_d_out = ( ".model auto_dac dac_bridge(out_low=0 out_high={vdd} t_rise=20p t_fall=20p)" "auto_bridge%d [ %s ] [ %s ] auto_dac" )',
    "save v(PLL_CLK) v(x_pll.x_analog.VCTRL)",
    f"tran {max_step:.12g} {sim_time:.12g} uic",
]
for edge in range(1, 102):
    commands.append(
        f"meas tran cosim_edge_{edge} when v(PLL_CLK)={vdd / 2} rise={edge} TD={settled_start:.12g}"
    )
commands.append(
    f"meas tran vctrl_avg avg v(x_pll.x_analog.VCTRL) from={settled_start:.12g} to={sim_time:.12g}"
)
commands.append(".endc")
text = re.sub(r"\.control\n.*?\.endc", "\n".join(commands), text, count=1, flags=re.DOTALL)
open(path, "w").write(text)
PY

(
  cd "$WORK"
  ngspice -b pll_cosim.spice >simulation.log 2>&1
)

python3 - "$WORK/simulation.log" <<'PY'
import json
import math
import os
import re
import statistics
import sys

log = open(sys.argv[1]).read()
bad = ("mismatched XSPICE", "undefined symbol", "no entry function", "simulation interrupted")
if any(item.lower() in log.lower() for item in bad):
    raise SystemExit(log)

def value(name):
    match = re.search(rf"^{name}\s+=\s+([\d.eE+-]+)", log, re.MULTILINE)
    return None if match is None else float(match.group(1))

edges = [value(f"cosim_edge_{index}") for index in range(1, 102)]
if any(edge is None for edge in edges):
    raise SystemExit("co-simulation did not produce 101 settled PLL output edges")
periods = [edges[index + 1] - edges[index] for index in range(100)]
mean_period = statistics.mean(periods)
rms_jitter = math.sqrt(statistics.mean((period - mean_period) ** 2 for period in periods))
integer = int(os.environ["DIV_INTEGER"])
fractional = int(os.environ["DIV_FRACTIONAL"])
fref = float(os.environ["FREF_HZ"])
target = fref * (integer + fractional / 65536.0) / 2.0
measured = 1.0 / mean_period
if abs(measured / target - 1.0) > 0.01:
    raise SystemExit(f"co-simulation frequency error exceeds 1%: target={target} measured={measured}")
print(json.dumps({
    "corner": os.environ["CORNER"],
    "divide": integer + fractional / 65536.0,
    "reference_hz": fref,
    "target_output_hz": target,
    "temp_c": float(os.environ["TEMP_C"]),
    "vdd_v": float(os.environ["VDD"]),
    "measured_output_hz": measured,
    "rms_period_jitter_s": rms_jitter,
    "peak_to_peak_period_jitter_s": max(periods) - min(periods),
    "vctrl_v": value("vctrl_avg"),
}, indent=2, sort_keys=True))
PY
