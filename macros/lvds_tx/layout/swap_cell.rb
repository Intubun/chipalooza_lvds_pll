# Replace the contents of ONE cell inside a GDS, leaving the file otherwise
# exactly as it was.
#
# The generator owns cells/ and lvds_tx_gen.gds; lvds_tx.gds is the working
# file someone edits in KLayout.  Regenerating the working file would throw
# that work away, so when a single device changes, only that cell is lifted
# across.  Everything else -- the placement, and anything drawn by hand --
# is left untouched.
#
#   klayout -b -r swap_cell.rb -rd target=lvds_tx.gds \
#       -rd source=lvds_tx_gen.gds -rd cell=dev_n_w8_l2_ng6

target_file = $target
source_file = $source
cellname    = $cell

target = RBA::Layout::new
target.read(target_file)
source = RBA::Layout::new
source.read(source_file)

tc = target.cell(cellname)
sc = source.cell(cellname)
if tc.nil? || sc.nil?
  puts "FEHLER: #{cellname} fehlt in einer der beiden Dateien"
  exit 1
end

before_bbox = tc.bbox.to_s
after_bbox  = sc.bbox.to_s
before_n = 0
target.layer_indexes.each { |li| before_n += tc.shapes(li).size }

# what the rest of the file looks like now, to prove it does not move
fingerprint = {}
target.each_cell do |c|
  next if c.name == cellname
  n = 0
  target.layer_indexes.each { |li| n += c.shapes(li).size }
  fingerprint[c.name] = [n, c.bbox.to_s, c.each_inst.count { true }]
end

tc.clear
after_n = 0
source.layer_indexes.each do |sli|
  info = source.get_info(sli)
  tli = target.layer(info)
  sc.shapes(sli).each do |sh|
    tc.shapes(tli).insert(sh)
    after_n += 1
  end
end

changed = []
target.each_cell do |c|
  next if c.name == cellname
  n = 0
  target.layer_indexes.each { |li| n += c.shapes(li).size }
  now = [n, c.bbox.to_s, c.each_inst.count { true }]
  changed << c.name if fingerprint[c.name] != now
end

puts "Zelle          : #{cellname}"
puts "  Shapes       : #{before_n} -> #{after_n}"
puts "  Bounding Box : #{before_bbox} -> #{after_bbox}"
puts "  BBox gleich  : #{before_bbox == after_bbox ? 'ja' : 'NEIN - Instanzen wuerden verrutschen!'}"
puts "Andere Zellen  : #{changed.empty? ? 'unveraendert (' + fingerprint.size.to_s + ' geprueft)' : changed.join(', ')}"

if before_bbox != after_bbox
  puts "ABBRUCH: nichts geschrieben."
  exit 1
end

target.write(target_file)
puts "geschrieben: #{target_file}"
