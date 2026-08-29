#!/usr/bin/env python3
"""Run one transistor-level integer-N closed-loop PLL characterization point.

Run this script inside the IIC-OSIC-TOOLS container. It netlists the PLL
testbench, substitutes the requested operating point, and reports
frequency, 1%-band lock time, deterministic period jitter, control voltage,
and core supply power without retaining a large raw file.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import subprocess
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corner", choices=("tt", "ss", "ff", "sf", "fs"), default="tt")
    parser.add_argument("--vdd", type=float, default=1.2)
    parser.add_argument("--temp", type=int, default=27)
    parser.add_argument("--fref", type=float, default=100e6, help="reference frequency in Hz")
    parser.add_argument("--divide", type=int, default=20, help="integer VCO feedback ratio")
    parser.add_argument("--sim-time", type=float, default=10e-6, help="transient duration in seconds")
    parser.add_argument("--max-step", type=float, default=5e-12, help="maximum transient step in seconds")
    return parser.parse_args()


def measurement_value(log: str, name: str) -> float | None:
    match = re.search(rf"^{re.escape(name)}\s+=\s+([\d.eE+-]+)", log, re.MULTILINE)
    return float(match.group(1)) if match else None


def main() -> None:
    args = parse_args()
    if not 4 <= args.divide <= 80:
        raise SystemExit("divide must be in the supported 4-80 range")

    project_root = Path(__file__).resolve().parents[2]
    pll_dir = project_root / "schematic" / "xschem" / "pll"
    output_frequency = args.fref * args.divide / 2.0
    if not 500e6 <= output_frequency <= 1e9:
        raise SystemExit("fref * divide / 2 must produce a 500 MHz-1 GHz PLL output")

    env = os.environ.copy()
    env.setdefault("PDK_ROOT", "/foss/pdks")
    env.setdefault("PDK", "ihp-sg13cmos5l")
    env.setdefault("PDKPATH", f"{env['PDK_ROOT']}/{env['PDK']}")
    env.setdefault("SPICE_USERINIT_DIR", f"{env['PDKPATH']}/libs.tech/ngspice")

    with tempfile.TemporaryDirectory(prefix="pll-closed-loop-") as temp_dir:
        netlist_result = subprocess.run(
            [
                "xschem",
                "-n",
                "-q",
                "-x",
                "-o",
                temp_dir,
                "-N",
                "pll.spice",
                "testbenches/xschem/pll.tb.sch",
            ],
            cwd=pll_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        if netlist_result.returncode not in (0, 10):
            raise SystemExit(netlist_result.stderr or netlist_result.stdout)

        netlist_path = Path(temp_dir) / "pll.spice"
        netlist = netlist_path.read_text()
        period = 1.0 / args.fref
        pulse_width = period / 2.0 - 20e-12
        netlist = re.sub(
            r"VREF REF_CLK 0 PULSE\([^\n]+\)",
            f"VREF REF_CLK 0 PULSE(0 {args.vdd} 1n 20p 20p {pulse_width:.12g} {period:.12g})",
            netlist,
        )
        netlist = re.sub(r"VDD_SRC VDD 0 [\d.]+", f"VDD_SRC VDD 0 {args.vdd}", netlist)
        netlist = re.sub(r"VENABLE ENABLE 0 [\d.]+", f"VENABLE ENABLE 0 {args.vdd}", netlist)
        netlist = re.sub(r"VRESET RESET_N 0 [\d.]+", f"VRESET RESET_N 0 {args.vdd}", netlist)
        netlist = netlist.replace("out_high=1.2", f"out_high={args.vdd}")
        netlist = netlist.replace("mos_tt", f"mos_{args.corner}")
        netlist = netlist.replace(".options temp=27", f".options temp={args.temp}")
        netlist = netlist.replace("div_factor=20 high_cycles=1", f"div_factor={args.divide} high_cycles=1")
        netlist = netlist.replace("v(x_pll.x_vco.net1)=1.2", f"v(x_pll.x_vco.net1)={args.vdd}")

        settled_start = args.sim_time - 2e-6
        edge_count = 501
        commands = [
            ".control",
            "save v(PLL_CLK) v(x_pll.VCO_CLK) v(x_pll.VCTRL) i(VDD_SRC)",
            f"tran {args.max_step:.12g} {args.sim_time:.12g} uic",
        ]
        for index in range(1, edge_count + 1):
            commands.append(
                f"meas tran settled_edge_{index} when v(PLL_CLK)={args.vdd / 2} "
                f"rise={index} TD={settled_start:.12g}"
            )

        window_starts = []
        start = 0.5e-6
        while start <= args.sim_time - 0.5e-6 + 1e-15:
            window_starts.append(start)
            index = len(window_starts) - 1
            commands.append(
                f"meas tran lock_{index}_a when v(PLL_CLK)={args.vdd / 2} rise=1 TD={start:.12g}"
            )
            commands.append(
                f"meas tran lock_{index}_b when v(PLL_CLK)={args.vdd / 2} rise=101 TD={start:.12g}"
            )
            start += 0.25e-6

        commands.extend(
            (
                f"meas tran vctrl_avg avg v(x_pll.VCTRL) from={settled_start:.12g} to={args.sim_time:.12g}",
                f"meas tran idd_avg avg i(VDD_SRC) from={settled_start:.12g} to={args.sim_time:.12g}",
                ".endc",
            )
        )
        netlist = re.sub(r"\.control\n.*?\.endc", "\n".join(commands), netlist, count=1, flags=re.DOTALL)
        netlist_path.write_text(netlist)

        simulation = subprocess.run(
            ["ngspice", "-b", str(netlist_path)],
            cwd=temp_dir,
            env=env,
            capture_output=True,
            text=True,
        )
        log = simulation.stdout + simulation.stderr
        if simulation.returncode != 0:
            raise SystemExit(log)

        edges = [measurement_value(log, f"settled_edge_{index}") for index in range(1, edge_count + 1)]
        if any(value is None for value in edges):
            raise SystemExit("PLL did not produce enough settled output edges")
        periods = [edges[index + 1] - edges[index] for index in range(edge_count - 1)]  # type: ignore[operator]
        mean_period = statistics.mean(periods)
        rms_jitter = math.sqrt(statistics.mean((value - mean_period) ** 2 for value in periods))

        lock_windows: list[tuple[float, float | None]] = []
        for index, start in enumerate(window_starts):
            first = measurement_value(log, f"lock_{index}_a")
            last = measurement_value(log, f"lock_{index}_b")
            frequency = None if first is None or last is None else 100.0 / (last - first)
            lock_windows.append((start, frequency))

        lock_time = None
        for index, (start, frequency) in enumerate(lock_windows):
            remaining = [item[1] for item in lock_windows[index:]]
            if frequency is not None and all(
                value is not None and abs(value / output_frequency - 1.0) <= 0.01 for value in remaining
            ):
                lock_time = start
                break

        vctrl = measurement_value(log, "vctrl_avg")
        idd = measurement_value(log, "idd_avg")
        result = {
            "corner": args.corner,
            "vdd_v": args.vdd,
            "temp_c": args.temp,
            "reference_hz": args.fref,
            "divide": args.divide,
            "target_output_hz": output_frequency,
            "measured_output_hz": 1.0 / mean_period,
            "lock_time_s_1pct": lock_time,
            "rms_period_jitter_s": rms_jitter,
            "peak_to_peak_period_jitter_s": max(periods) - min(periods),
            "vctrl_v": vctrl,
            "supply_power_w": None if idd is None else -idd * args.vdd,
        }
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
