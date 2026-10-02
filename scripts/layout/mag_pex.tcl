# Full-RC Magic extraction (EXT_MODE=3 equivalent) of a flattened copy of
# the editable .mag hierarchy. The source cells are not modified.
#
# Environment:
#   CELL     top cell
#   PEX_OUT  output SPICE path; the subcircuit is named <CELL>_pex
#   EXT_DIR  scratch directory for .ext files

crashbackups stop
drc off
addpath .
load $::env(CELL) -silent
select top cell
flatten $::env(CELL)_pex
load $::env(CELL)_pex
select top cell

file mkdir $::env(EXT_DIR)
extract path $::env(EXT_DIR)
ext2spice lvs
extresist threshold 10000
extresist mindelay 1
extresist minres 1000
extract do resistance
extract do unique
extract all
ext2spice extresist on
ext2spice cthresh 0.01
ext2spice -p $::env(EXT_DIR) -o $::env(PEX_OUT)
quit -noprompt
