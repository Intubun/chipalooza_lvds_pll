# Write every generated device cell to a GDS of its own, ../gds/<cell>.gds,
# for swap_pcells.py.  Runs in build/pcells/cells (update_pcells.sh).
#
# One file per cell rather than one library: `gds write` writes the cell in
# the window and what is below it, and a device cell has nothing below it.
addpath .
drc off
foreach f [lsort [glob -nocomplain *.mag]] {
    set cell [file rootname $f]
    if {$cell eq "devscratch"} { continue }
    load $cell -silent
    gds write ../gds/$cell.gds
    puts "GDS $cell"
}
quit -noprompt
