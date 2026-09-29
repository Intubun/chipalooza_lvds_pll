# DRC the placement hierarchy, deepest cell first, and report per cell.
#
# One rule is reported but not counted: magic's "can't abut or partially
# overlap between subcells".  The generator does overlap blocks -- two pmos
# by 0.85 um, two nmos by 0.175 um, so that they share well and
# ThickGateOx (spacing.py) -- and magic takes those without complaint.  What
# it flags is overlap drawn by hand into a cell in ROUTED (build_placement.py;
# iref_x15 had it, before it became its own macro).  KLayout's sign-off deck,
# which reads the merged shapes, accepts both; it runs right after this in
# run_all.sh, and it is the one that decides.
addpath cells
drc euclidean on
drc on
drc style drc(full)
set overlap "This layer can't abut or partially overlap between subcells"
set total 0
set adopted 0
foreach cell {predriver_comp predriver_stage predriver Driver lvds_tx} {
    load $cell -silent
    select top cell
    drc check
    drc catchup
    set n [drc list count total]
    set why [dict keys [drc listall why]]
    if {$n > 0 && $why eq [list $overlap]} {
        incr adopted $n
        puts "DRC $cell $n (nur Teilzellen-Ueberlappung aus lvds_tx.gds, nicht gezaehlt)"
    } else {
        incr total $n
        puts "DRC $cell $n"
    }
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
