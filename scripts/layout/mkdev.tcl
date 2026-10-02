# Build IHP PDK device cells with stable names.
#
# magic::gencell picks its own cell name, so each call is bracketed by a diff
# of `cellname list allcells` and the new cell is renamed. Source this file,
# call mkdev once per device, then `writeall force`.
#
#   mkdev sg13_lv_nmos dev_n_w0p9_l0p13_ng1_noguard_m1 \
#       {w 0.9 l 0.13 ng 1 m 1 guard 0 conn_gates 1 full_metal 1 doports 1 \
#        viasrc 0 viadrn 0 viagate 0}
#
# `w` is the width per finger (the schematic's total width divided by ng).

drc off
load mkdev_scratch -silent

proc mkdev {type name params} {
    if {[cellname list exists $name]} {
        puts "KEEP $name (already exists)"
        return
    }
    set before [cellname list allcells]
    box 0 0 0 0
    eval "magic::gencell sg13cmos5l::$type inst_$name $params"
    set new {}
    foreach cell [cellname list allcells] {
        if {[lsearch $before $cell] < 0} {
            set new $cell
        }
    }
    if {$new eq {}} {
        error "mkdev: no cell created for $name"
    }
    cellname rename $new $name
    puts "MADE $name"
}
