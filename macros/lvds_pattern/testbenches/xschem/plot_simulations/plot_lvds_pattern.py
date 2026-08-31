# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Transient plots for the lvds_pattern standard-cell block.
#              Top panel walks the whole sequence, bottom panel zooms into the
#              PRBS so the pair and its crossing are actually visible.
# ============================================

import os
from pathlib import Path

import matplotlib.pyplot as plt
import ngspice2python as ng
import numpy as np

plt.close("all")
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.size": 13,
})


def main():
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    f = str(data_dir / "lvds_pattern_tb_tran.txt")
    time = ng.loadngspicecol(f, "time") * 1e9
    d_p = ng.loadngspicecol(f, "v(d_p)")
    d_n = ng.loadngspicecol(f, "v(d_n)")
    mode = ng.loadngspicecol(f, "v(mode)")
    en = ng.loadngspicecol(f, "v(en)")

    p_color, n_color = "#0c5da5", "#c1440e"
    ctl_color = "#6b7280"

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7))
    fig.suptitle("lvds_pattern - clock passthrough, PRBS-7 and the clock gate")

    ax1.plot(time, d_p, color=p_color, linewidth=0.9, label=r"$D_\mathrm{p}$")
    ax1.plot(time, mode, color=ctl_color, linewidth=1.6, linestyle="--", label="mode")
    ax1.plot(time, en, color="#2f855a", linewidth=1.6, linestyle=":", label="en")
    ax1.set_ylabel(r"$V$ (V)")
    ax1.set_xlabel(r"$t$ (ns)")
    ax1.grid(visible=True, which="major", linestyle="--", alpha=0.4)
    ax1.legend(loc="upper right", ncol=3, fontsize=10)

    # zoom on a few PRBS bits, well after mode goes high
    lo, hi = 60.0, 68.0
    sel = (time >= lo) & (time <= hi)
    ax2.plot(time[sel], d_p[sel], color=p_color, linewidth=1.8, label=r"$D_\mathrm{p}$")
    ax2.plot(time[sel], d_n[sel], color=n_color, linewidth=1.8, label=r"$D_\mathrm{n}$")
    ax2.set_ylabel(r"$V$ (V)")
    ax2.set_xlabel(r"$t$ (ns)")
    ax2.set_title("PRBS-7 at 1 Gb/s, into the 170 fF pre-driver load", fontsize=11)
    ax2.grid(visible=True, which="major", linestyle="--", alpha=0.4)
    ax2.legend(loc="upper right", fontsize=10)

    plt.tight_layout()
    fig.savefig(str(figures_dir / "lvds_pattern_tb_tran.svg"), bbox_inches="tight")
    fig.savefig(str(figures_dir / "lvds_pattern_tb_tran.pdf"), bbox_inches="tight")
    np.savetxt(str(figures_dir / "lvds_pattern_tb_tran.csv"),
               np.column_stack((time, d_p, d_n, mode, en)), comments="",
               header="time_ns,D_p,D_n,mode,en", delimiter=",")

    if os.environ.get("SHOW_PLOTS"):
        plt.show()


if __name__ == "__main__":
    main()
