# DRC every generated leaf cell and print one line per cell.
# addpath is not optional: without it `load <cell>` does not find the
# file, magic silently creates an empty cell of that name, and every
# cell reports 0 errors no matter what is in it.
addpath cells
drc euclidean on
drc style drc(full)
foreach f [lsort [glob -nocomplain cells/*.mag]] {
    set cell [file rootname [file tail $f]]
    if {$cell eq "devscratch"} { continue }
    load $cell -silent
    select top cell
    drc check
    drc catchup
    puts "DRC $cell [drc list count total]"
}
quit -noprompt
