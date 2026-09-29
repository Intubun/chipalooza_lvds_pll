# DRC every generated device cell and print one line per cell.  Runs in
# build/pcells/cells (update_pcells.sh).
#
# addpath is not optional: without it `load <cell>` does not find the
# file, magic silently creates an empty cell of that name, and every
# cell reports 0 errors no matter what is in it.
#
# The latch-up rules LU.a/LU.b (diffusion no further than 20 um from a
# well or substrate tap) are counted apart, on an "LU" line of their own: a
# cell built without a guard ring (devices.py: SUBCKT_OVERRIDES) has no tap
# at all, and gets its taps from the cell it is placed in.  The sign-off
# deck checks them there.  Everything else is an error in the cell itself.
addpath .
drc euclidean on
drc style drc(full)
foreach f [lsort [glob -nocomplain *.mag]] {
    set cell [file rootname [file tail $f]]
    if {$cell eq "devscratch"} { continue }
    load $cell -silent
    select top cell
    drc check
    drc catchup
    set n 0
    set lu 0
    foreach {msg rects} [drc listall why] {
        if {[string match "*(LU.a)*" $msg] || [string match "*(LU.b)*" $msg]} {
            incr lu [llength $rects]
        } else {
            incr n [llength $rects]
        }
    }
    puts "DRC $cell $n"
    if {$lu > 0} { puts "LU $cell $lu" }
}
quit -noprompt
