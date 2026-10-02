# Import the foundry antenna standard cell as an editable Magic cell for the
# custom prescaler hierarchy.  Run through scripts/layout/magic_batch.sh.
if {![info exists ::env(PDK_ROOT)]} { set ::env(PDK_ROOT) /foss/pdks }
if {![info exists ::env(PDK)]} { set ::env(PDK) ihp-sg13cmos5l }
set lib "$::env(PDK_ROOT)/$::env(PDK)/libs.ref/sg13cmos5l_stdcell/gds/sg13cmos5l_stdcell.gds"
gds readonly false
gds rescale false
gds read $lib
load sg13cmos5l_antennanp
save prescaler_antenna
quit -noprompt
