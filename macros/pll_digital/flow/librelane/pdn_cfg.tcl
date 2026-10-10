# Single-layer block PDN. The fixed TSPC macro exposes controlled M4 supply access
# at opposite edges; its LEF blocks vertical straps from crossing the internal
# horizontal VDD and VSS bars.
source $::env(SCRIPTS_DIR)/openroad/common/io.tcl
source $::env(SCRIPTS_DIR)/openroad/common/set_global_connections.tcl
set_global_connections

set secondary []
foreach vdd $::env(VDD_NETS) gnd $::env(GND_NETS) {
    if {$vdd != $::env(VDD_NET)} {
        lappend secondary $vdd
    }
    if {$gnd != $::env(GND_NET)} {
        lappend secondary $gnd
    }
}

set_voltage_domain -name CORE -power $::env(VDD_NET) -ground $::env(GND_NET) \
    -secondary_power $secondary

set pin_args [list]
if {$::env(PDN_ENABLE_PINS)} {
    lappend pin_args -pins $::env(PDN_VERTICAL_LAYER)
}

define_pdn_grid \
    -name stdcell_grid \
    -starts_with POWER \
    -voltage_domain CORE \
    {*}$pin_args

add_pdn_stripe \
    -grid stdcell_grid \
    -layer $::env(PDN_VERTICAL_LAYER) \
    -width $::env(PDN_VWIDTH) \
    -pitch $::env(PDN_VPITCH) \
    -offset $::env(PDN_VOFFSET) \
    -spacing $::env(PDN_VSPACING) \
    -starts_with POWER

if {$::env(PDN_ENABLE_RAILS)} {
    add_pdn_stripe \
        -grid stdcell_grid \
        -layer $::env(PDN_RAIL_LAYER) \
        -width $::env(PDN_RAIL_WIDTH) \
        -followpins

    add_pdn_connect \
        -grid stdcell_grid \
        -layers "$::env(PDN_RAIL_LAYER) $::env(PDN_VERTICAL_LAYER)"
}

# pdngen deliberately stops its M4 straps at hard-macro obstructions. Escape
# VDD on M3 and VSS on M2 so their long trunks cannot short where they cross,
# then join the uninterrupted right-side M4 straps. Coordinates are in DBU and
# follow the fixed /2 placement in config.yaml.
proc add_tspc_power_stitches {} {
    set block [ord::get_db_block]
    set tech [ord::get_db_tech]
    set m2 [$tech findLayer Metal2]
    set m3 [$tech findLayer Metal3]
    set m4 [$tech findLayer Metal4]
    set via2 [$tech findVia Via2_XY]
    set via3 [$tech findVia Via3_XY]
    foreach {net_name layer rectangles via2_points via3_points m3_patches m4_patches} {
        VDD Metal3 {
            {144200 9700 144800 34000} {144500 9700 215760 10300}
            {215460 9700 216060 15200}
        } {} {{144500 34000} {215760 15200}} {} {
            {144100 33600 144900 34400}
        }
        VSS Metal2 {
            {140700 11700 141300 28000} {141000 11700 218760 12300}
            {218460 11700 219060 15120}
        } {{141000 28000}} \
          {{141000 28000}} {
            {140600 27600 141400 28400}
        } {
            {140600 27600 141400 28400}
        }
    } {
        set net [$block findNet $net_name]
        set wire [odb::dbSWire_create $net FIXED]
        set routing_layer [expr {$layer eq "Metal2" ? $m2 : $m3}]
        foreach rect $rectangles {
            lassign $rect x0 y0 x1 y1
            odb::dbSBox_create $wire $routing_layer $x0 $y0 $x1 $y1 STRIPE
        }
        foreach point $via2_points {
            lassign $point x y
            odb::dbSBox_create $wire $via2 $x $y STRIPE
        }
        foreach point $via3_points {
            lassign $point x y
            odb::dbSBox_create $wire $via3 $x $y STRIPE
        }
        foreach rect $m3_patches {
            lassign $rect x0 y0 x1 y1
            odb::dbSBox_create $wire $m3 $x0 $y0 $x1 $y1 STRIPE
        }
        foreach rect $m4_patches {
            lassign $rect x0 y0 x1 y1
            odb::dbSBox_create $wire $m4 $x0 $y0 $x1 $y1 STRIPE
        }
    }
}

rename pdngen pdngen_without_tspc_stitches
proc pdngen {args} {
    pdngen_without_tspc_stitches {*}$args
    add_tspc_power_stitches
}
