# Full Magic DRC on the editable .mag hierarchy (not on an exported GDS:
# GDS export generates contact/enclosure geometry that can hide real errors
# in the source cells).
#
# Environment: CELL (top cell to check)

crashbackups stop
drc off
addpath .
load $::env(CELL) -silent
select top cell
expand
drc style drc(full)
drc on
drc check
drc catchup
puts "DRC_COUNT=[drc list count total]"
puts "DRC_WHY_BEGIN"
puts [drc listall why]
puts "DRC_WHY_END"
puts "BBOX=[box values]"
quit -noprompt
