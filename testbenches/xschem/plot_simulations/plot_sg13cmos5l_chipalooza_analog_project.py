# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Tim Edwards and Simon Dorrer
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: Simon Dorrer
# Description: Transient plots for the analog project macro based on ngspice exports.
#              Plots the LVDS output pair, its midpoint Vos and the differential Vod.
# Created: 06.05.2026
# Last Modified: 02.08.2026
# ============================================

# Imports
import os
import numpy as np
import matplotlib.pyplot as plt
import ngspice2python as ng
from pathlib import Path
# ============================================

# Plotting Configuration
# ============================================
# Interactive mode stays off: the plt.show() at the end of main() then blocks in the GUI
# event loop, which is what draws the windows in the first place. With plt.ion() the call
# returns immediately and nothing pumps that loop afterwards, so no window ever appears.
plt.close("all")

# Matplotlib Settings
# %matplotlib qt
# %matplotlib inline

# Pure Matplotlib text rendering (no external LaTeX dependency)
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.size": 14,
})
# =========================================================================

def main():
    # Resolve data and output paths relative to this script
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load ngspice transient simulation data
    # ------------------------------------------------------------------
    ngspice_file = data_dir / "sg13cmos5l_chipalooza_analog_project_tb_tran.txt"

    time = ng.loadngspicecol(str(ngspice_file), "time")
    analog_1 = ng.loadngspicecol(str(ngspice_file), "v(d_p)")
    analog_2 = ng.loadngspicecol(str(ngspice_file), "v(d_n)")
    vos = ng.loadngspicecol(str(ngspice_file), "v(vos)")
    vod = ng.loadngspicecol(str(ngspice_file), "vod")
    d_p = ng.loadngspicecol(str(ngspice_file), "v(x1.core_p)")
    d_n = ng.loadngspicecol(str(ngspice_file), "v(x1.core_n)")

    # Display-friendly axis scale
    time_ns = time * 1e9

    # ------------------------------------------------------------------
    # 2. Transient Plot (Voltages over Time)
    # ------------------------------------------------------------------
    out_p_color = '#2f855a'
    out_n_color = '#805ad5'
    vos_color = '#ff6b35'
    vod_color = '#0c5da5'

    fig1, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    fig1.suptitle('Chipalooza 2026 Analog Project - pattern generator into the LVDS driver')

    ax0.plot(time_ns, d_p, color='#0c5da5', linewidth=1.2, label=r'$core_\mathrm{p}$')
    ax0.plot(time_ns, d_n, color='#c1440e', linewidth=1.2, label=r'$core_\mathrm{n}$')
    ax0.set_ylabel(r'$V$ (V)')
    ax0.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax0.legend(loc='best')

    ax1.plot(time_ns, analog_1, color=out_p_color, linewidth=2.0, label=r'$d_\mathrm{p}$ (analog_pin[2])')
    ax1.plot(time_ns, analog_2, color=out_n_color, linewidth=2.0, label=r'$d_\mathrm{n}$ (analog_pin[3])')
    ax1.plot(time_ns, vos, color=vos_color, linewidth=2.0, linestyle='--', label=r'$V_\mathrm{os}$')
    ax1.set_ylabel(r'$V$ (V)')
    ax1.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax1.legend(loc='best')

    ax2.plot(time_ns, vod * 1e3, color=vod_color, linewidth=2.0, label=r'$V_\mathrm{od}$')
    ax2.set_xlabel(r'$t$ (ns)')
    ax2.set_ylabel(r'$V_\mathrm{od}$ (mV)')
    ax2.grid(visible=True, which='major', linestyle='--', alpha=0.45)
    ax2.legend(loc='best')

    plt.tight_layout()

    # ------------------------------------------------------------------
    # 3. Export transient figures and CSV
    # ------------------------------------------------------------------
    fig1.savefig(str(figures_dir / "sg13cmos5l_chipalooza_analog_project_tb_tran.svg"), bbox_inches='tight')
    fig1.savefig(str(figures_dir / "sg13cmos5l_chipalooza_analog_project_tb_tran.pdf"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "sg13cmos5l_chipalooza_analog_project_tb_tran.csv"),
               np.column_stack((time_ns, analog_1, analog_2, vos, vod, d_p, d_n)),
               comments="", header="time_ns,d_p,d_n,vos,vod,core_p,core_n",
               delimiter=",")

    # ------------------------------------------------------------------
    # 4. Open the plot window (blocks until it is closed)
    # ------------------------------------------------------------------
    # Only open the interactive window when requested (sim-view-xschem sets
    # SHOW_PLOTS=1); batch/headless runs just save the figures and exit.
    if os.environ.get("SHOW_PLOTS"):
        plt.show()
    # ============================================

# Main Execution
if __name__ == '__main__':
    main()
# =========================================================================