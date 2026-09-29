# Write the generator's own GDS.  NOT lvds_tx.gds: that file belongs to
# whoever is working in KLayout, and nothing here may write it.
addpath cells
drc off
load lvds_tx -silent
select top cell
puts "BBOX: [box values]"
gds write lvds_tx_gen.gds
quit -noprompt
