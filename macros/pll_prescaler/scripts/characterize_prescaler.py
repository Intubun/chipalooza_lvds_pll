#!/usr/bin/env python3
"""Characterize the TSPC /2-/3 prescaler at the analog VCO PVT maxima."""

import csv
import re
import subprocess
import tempfile
from pathlib import Path


MACRO_ROOT = Path(__file__).resolve().parents[1]
NETLIST = MACRO_ROOT / "netlist/schematic/pll_tspc_div23.spice"
RESULTS = MACRO_ROOT / "info/pll_tspc_div23_pvt.csv"
MODEL = Path("/foss/pdks/ihp-sg13cmos5l/libs.tech/ngspice/models/cornerMOSlv.lib")

# Maximum measured buffered-VCO frequencies at VCTRL=0.95 V. These are the
# most demanding characterized point for each process family.
CASES = (
    ("ss", "mos_ss", 1.08, 125, 2.31502917e9),
    ("tt", "mos_tt", 1.20, 27, 4.04727214e9),
    ("ff", "mos_ff", 1.32, -40, 6.29802242e9),
    ("sf", "mos_sf", 1.32, -40, 4.45335100e9),
    ("fs", "mos_fs", 1.32, -40, 4.94388700e9),
)


def deck(corner, vdd, temp_c, frequency_hz, modulus):
    period_ns = 1e9 / frequency_hz
    edge_ns = max(0.005, period_ns * 0.04)
    high_ns = period_ns / 2 - edge_ns
    start_ns = 3 * period_ns
    stop_ns = 45 * period_ns
    request = vdd if modulus == 2 else 0
    return f"""\
.lib {MODEL} {corner}
.temp {temp_c}
.include {NETLIST}
VDD VDD 0 {vdd}
VRESET RESET_B 0 pulse(0 {vdd} {start_ns - period_ns}n {edge_ns}n {edge_ns}n 100n 200n)
VCLK CLK 0 pulse(0 {vdd} {start_ns}n {edge_ns}n {edge_ns}n {high_ns}n {period_ns}n)
VREQUEST MODULUS_REQUEST 0 {request}
XPRE CLK RESET_B MODULUS_REQUEST Q2 VDD 0 pll_tspc_div23
CQ2 Q2 0 3f
.control
set noaskquit
tran {period_ns / 300}n {stop_ns}n
meas tran q2_min min v(Q2) from={start_ns + 10 * period_ns}n to={stop_ns}n
meas tran q2_max max v(Q2) from={start_ns + 10 * period_ns}n to={stop_ns}n
meas tran edge_8 when v(Q2)={vdd / 2} rise=8
meas tran edge_9 when v(Q2)={vdd / 2} rise=9
let output_period=edge_9-edge_8
print q2_min q2_max output_period
quit
.endc
.end
"""


def simulate(case, modulus, directory):
    name, corner, vdd, temp_c, frequency_hz = case
    source = directory / f"{name}_div{modulus}.spice"
    log = source.with_suffix(".log")
    source.write_text(deck(corner, vdd, temp_c, frequency_hz, modulus))
    subprocess.run(
        ["ngspice", "-b", "-o", str(log), str(source)],
        check=True,
    )
    text = log.read_text()
    values = {
        key: float(value)
        for key, value in re.findall(
            r"^(q2_min|q2_max|output_period)\s+=\s+([-+0-9.eE]+)",
            text,
            re.MULTILINE,
        )
    }
    if len(values) != 3:
        raise RuntimeError(f"Missing measurements in {log}")

    expected_s = modulus / frequency_hz
    period_error = values["output_period"] / expected_s - 1
    passed = (
        values["q2_min"] < 0.2 * vdd
        and values["q2_max"] > 0.8 * vdd
        and abs(period_error) < 0.02
    )
    return {
        "corner": name,
        "vdd_v": vdd,
        "temp_c": temp_c,
        "input_frequency_hz": frequency_hz,
        "modulus": modulus,
        "q2_min_v": values["q2_min"],
        "q2_max_v": values["q2_max"],
        "output_period_s": values["output_period"],
        "period_error": period_error,
        "result": "PASS" if passed else "FAIL",
    }


def main():
    rows = []
    with tempfile.TemporaryDirectory(prefix="pll-prescaler-") as temporary:
        directory = Path(temporary)
        for case in CASES:
            for modulus in (2, 3):
                row = simulate(case, modulus, directory)
                rows.append(row)
                print(
                    f"{row['result']} {row['corner']} "
                    f"{row['input_frequency_hz'] / 1e9:.3f} GHz /{row['modulus']}"
                )

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    if any(row["result"] != "PASS" for row in rows):
        raise SystemExit("Prescaler characterization failed")
    print(f"Wrote {RESULTS}")


if __name__ == "__main__":
    main()
