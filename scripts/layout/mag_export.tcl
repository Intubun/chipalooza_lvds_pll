# Export GDS and an LVS netlist from the editable .mag hierarchy.
#
# Environment:
#   CELL     top cell
#   GDS      output GDS path
#   LVS_OUT  output SPICE path for netgen
#   EXT_DIR  scratch directory for .ext files

crashbackups stop
drc off
addpath .
load $::env(CELL) -silent
select top cell
gds write $::env(GDS)

file mkdir $::env(EXT_DIR)
extract path $::env(EXT_DIR)
extract all
ext2spice lvs
ext2spice subcircuit top on
ext2spice -p $::env(EXT_DIR) -o $::env(LVS_OUT)
quit -noprompt
