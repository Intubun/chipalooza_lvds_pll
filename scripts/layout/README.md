# Magic layout scripts

These scripts generate PDK devices and sign off hand-edited Magic `.mag`
blocks. Run them inside the IIC-OSIC container.

| File | Purpose |
| --- | --- |
| `magic_batch.sh <mag_dir> <script.tcl> [NAME=value ...]` | Runs a Magic Tcl script headlessly with the IHP tech. Each `NAME=value` becomes `$::env(NAME)`. |
| `mkdev.tcl` | Defines `mkdev <model> <cellname> {gencell params}`, which builds a PDK gencell under a fixed name (`w` is per finger). |
| `mag_drc.tcl` | Runs full Magic DRC (`drc(full)` followed by `drc catchup`) on the editable `.mag` source. |
| `mag_export.tcl` | Writes the GDS and an LVS netlist from the `.mag` hierarchy. |
| `mag_pex.tcl` | Full-RC extraction (threshold 10 Ω, minres 1 Ω, mindelay 1 ps) of a flattened copy. |
| `signoff_cell.sh <mag_dir> <cell> <ref.spice> <out_dir>` | Runs DRC, then GDS export, Netgen LVS, KLayout antenna (`--antenna_only`) and PEX. It exits non-zero on any DRC, LVS or antenna failure. |

To generate devices, write a Tcl file that sources `mkdev.tcl`, calls `mkdev`
for each device, and ends with `writeall force` and `quit -noprompt`. Then
run it from the target `mag` directory:

```sh
scripts/layout/magic_batch.sh macros/<macro>/layout/mag my_devices.tcl
```

In `pll_analog`, `make layout-signoff CELL=<cell>` writes the reference
netlist from Xschem, runs `signoff_cell.sh`, and puts its reports in
`verification/signoff/<cell>/`.

`drc check` without `drc catchup` returns before the check has finished, so
it reports 0 errors. Always use `mag_drc.tcl`.
