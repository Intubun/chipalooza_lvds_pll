# Compare two GDS files cell by cell and name what differs.
a = RBA::Layout::new; a.read($a)
b = RBA::Layout::new; b.read($b)
def stats(ly)
  h = {}
  ly.each_cell do |c|
    n = 0
    ly.layer_indexes.each { |li| n += c.shapes(li).size }
    h[c.name] = [n, c.bbox.to_s, c.each_inst.count { true }]
  end
  h
end
sa, sb = stats(a), stats(b)
puts "Zellen: #{sa.size} vorher, #{sb.size} nachher"
(sa.keys | sb.keys).sort.each do |k|
  next if sa[k] == sb[k]
  puts "  #{k}"
  puts "     vorher : Shapes=#{sa[k] ? sa[k][0] : '-'} Instanzen=#{sa[k] ? sa[k][2] : '-'} BBox=#{sa[k] ? sa[k][1] : '-'}"
  puts "     nachher: Shapes=#{sb[k] ? sb[k][0] : '-'} Instanzen=#{sb[k] ? sb[k][2] : '-'} BBox=#{sb[k] ? sb[k][1] : '-'}"
end
ta = 0; sa.each_value { |v| ta += v[0] }
tb = 0; sb.each_value { |v| tb += v[0] }
puts "Shapes gesamt: #{ta} -> #{tb}"
