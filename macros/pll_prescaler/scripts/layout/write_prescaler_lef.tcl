# Write compact P&R abstracts for the signed-off TSPC macros. Magic's generic
# `lef write` exposes transistor-level routing as thousands of false access
# shapes, so only the actual TopMetal1 rails are exposed here.
set script_dir [file dirname [file normalize [info script]]]
set layout_dir [file normalize [file join $script_dir ../../layout]]

proc header {out name width height foreign_x foreign_y} {
    puts $out "VERSION 5.7 ;"
    puts $out {  NOWIREEXTENSIONATPIN ON ;
  DIVIDERCHAR "/" ;
  BUSBITCHARS "[]" ;}
    puts $out "MACRO $name"
    puts $out "  CLASS BLOCK ;"
    puts $out "  FOREIGN $name $foreign_x $foreign_y ;"
    puts $out {  ORIGIN 0.000 0.000 ;}
    puts $out "  SIZE $width BY $height ;"
    puts $out {  SYMMETRY X Y ;}
}

proc signal_pin {out name x0 y0 x1 y1 {gate_area ""}} {
    puts $out "  PIN $name"
    if {$name eq "Q" || $name eq "Q2"} {
        puts $out {    DIRECTION OUTPUT ;}
    } else {
        puts $out {    DIRECTION INPUT ;}
    }
    puts $out {    USE SIGNAL ;}
    if {$gate_area ne ""} {
        puts $out "    ANTENNAGATEAREA $gate_area ;"
        puts $out {    ANTENNADIFFAREA 2.015400 ;}
    }
    puts $out {    PORT
      LAYER Metal4 ;}
    puts $out "        RECT $x0 $y0 $x1 $y1 ;"
    puts $out {    END}
    puts $out "  END $name"
}

proc power_pin {out name use m4x0 m4y0 m4x1 m4y1} {
    puts $out "  PIN $name"
    puts $out {    DIRECTION INOUT ;}
    puts $out "    USE $use ;"
    puts $out {    PORT
      LAYER Metal4 ;}
    puts $out "        RECT $m4x0 $m4y0 $m4x1 $m4y1 ;"
    puts $out {    END}
    puts $out "  END $name"
}

proc lower_obstructions {out width height access_x} {
    puts $out {  OBS
    LAYER Metal1 ;}
    puts $out "      RECT 0.000 0.000 $width $height ;"
    puts $out {    LAYER Metal2 ;}
    puts $out "      RECT 0.000 0.000 $access_x $height ;"
    puts $out {    LAYER Metal3 ;}
    puts $out "      RECT 0.000 0.000 $access_x $height ;"
    puts $out {    LAYER Metal4 ;}
    puts $out "      RECT 0.000 0.000 $access_x $height ;"
}

# Programmable /2-/3 prescaler. The generated MAG/GDS hierarchy is normalized
# to the same zero-based boundary used by LEF/DEF.
set out [open [file join $layout_dir pll_tspc_div23.lef] w]
header $out pll_tspc_div23 109.320 135.500 0.000 0.000
signal_pin $out Q2 108.700 125.190 109.320 125.810 0.156000
power_pin $out VSS GROUND 4.010 2.690 4.630 3.310
power_pin $out VDD POWER 7.510 8.690 8.130 9.310
signal_pin $out RESET_B 108.700 128.190 109.320 128.810 0.468000
signal_pin $out CLK 108.700 131.190 109.320 131.810 1.560000
signal_pin $out MODULUS_REQUEST 108.700 134.190 109.320 134.810 0.312000
lower_obstructions $out 109.320 135.500 107.320
puts $out {    LAYER TopMetal1 ;
      RECT 0.000 0.000 1.640 135.500 ;
      RECT 3.500 0.000 5.140 135.500 ;
      RECT 7.000 0.000 8.640 135.500 ;
      RECT 10.500 0.000 12.140 135.500 ;
      RECT 14.000 0.000 15.640 135.500 ;
      RECT 17.500 0.000 19.140 135.500 ;
      RECT 21.000 0.000 22.640 135.500 ;
  END
END pll_tspc_div23
END LIBRARY}
close $out

# Dedicated fixed /2 output divider.
set out [open [file join $layout_dir pll_tspc_div2.lef] w]
header $out pll_tspc_div2 65.000 48.000 0.000 0.000
power_pin $out VSS GROUND 0.690 2.690 1.310 3.310
power_pin $out VDD POWER 4.190 8.690 4.810 9.310
signal_pin $out RESET_B 64.380 44.690 65.000 45.310 0.312000
signal_pin $out CLK 64.380 46.690 65.000 47.310 0.780000
signal_pin $out Q 64.380 42.690 65.000 43.310 0.156000
lower_obstructions $out 65.000 48.000 63.000
puts $out {    LAYER TopMetal1 ;
      RECT 0.180 0.000 1.820 48.000 ;
      RECT 3.680 0.000 5.320 48.000 ;
      RECT 7.180 0.000 8.820 48.000 ;
      RECT 10.680 0.000 12.320 48.000 ;
      RECT 14.180 0.000 15.820 48.000 ;
      RECT 17.680 0.000 19.320 48.000 ;
  END
END pll_tspc_div2
END LIBRARY}
close $out
