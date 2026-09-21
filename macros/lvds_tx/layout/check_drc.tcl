# DRC the placement hierarchy, deepest cell first, and report per cell.
addpath cells
drc euclidean on
drc on
drc style drc(full)
set total 0
foreach cell {iref_x15 predriver_comp predriver_stage predriver Driver lvds_tx} {
    load $cell -silent
    select top cell
    drc check
    drc catchup
    set n [drc list count total]
    incr total $n
    puts "DRC $cell $n"
}
load lvds_tx -silent
select top cell
drc check
drc catchup
puts "TOTAL DRC ERRORS: $total"
foreach {msg rects} [drc listall why] {
    puts "RULE ([llength $rects]) $msg  e.g. [lindex $rects 0]"
}
quit -noprompt
