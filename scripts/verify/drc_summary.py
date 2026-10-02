#!/usr/bin/env python3
"""Summary of a KLayout DRC run on the top layout, sorted by where the errors are.

    drc_summary.py <run_dir> <layout.gds> <top> [--with-pll]

Each error belongs to the cell the deck reports it in.  Errors in a cell that
only the PLL uses (Rahul's part) are listed but not counted unless --with-pll.
Errors in the top cell itself are counted, and those that lie on the PLL are
marked: they are the top level's own wiring to it (antenna on its inputs, for
one).  Exit status 0 only when no counted error is left.
"""
import glob, sys
from collections import Counter, defaultdict
import klayout.db as kdb
import klayout.rdb as rdb

run, gds, top = sys.argv[1:4]
with_pll = "--with-pll" in sys.argv
ly = kdb.Layout(); ly.read(gds); t = ly.cell(top)
owner = defaultdict(set)              # cell name -> names of the top-level cells that use it
pll_box = kdb.DBox()
for inst in t.each_inst():
    c = ly.cell(inst.cell_index)
    for ci in [c.cell_index()] + list(c.called_cells()):
        owner[ly.cell(ci).name].add(c.name)
    if c.name == "pll":
        pll_box += inst.dbbox()
lyrdb = glob.glob(run + "/*_full.lyrdb")
if not lyrdb:
    sys.exit("  kein Ergebnis (*_full.lyrdb) in %s -- siehe %s/drc.log" % (run, run))
r = rdb.ReportDatabase(""); r.load(lyrdb[0])


def where(it):
    for v in it.each_value():
        s = v.to_s().split(": ", 1)[-1]
        for T in (kdb.DPolygon, kdb.DEdgePair, kdb.DEdge, kdb.DBox):
            try:
                return T.from_s(s).bbox()
            except Exception:
                pass
    return None


counted, ignored = Counter(), Counter()
at_pll = Counter()
for it in r.each_item():
    cell = r.cell_by_id(it.cell_id()).name()
    cat = r.category_by_id(it.category_id()).name()
    if cell == top:
        group = "Top-Zelle"
        b = where(it)
        if b is not None and not pll_box.empty() and pll_box.contains(b.center()):
            at_pll[cat] += 1
    else:
        users = owner.get(cell, {cell})
        group = "/".join(sorted(users))
    if users_pll_only := (cell != top and owner.get(cell) == {"pll"}):
        (counted if with_pll else ignored)[(group, cat)] += 1
    else:
        counted[(group, cat)] += 1

print("  %-40s %5s" % ("Zelle (Top-Instanz) / Regel", "Anz."))
for (g, cat), n in sorted(counted.items()):
    note = "  (davon %d an der PLL: Top-Verdrahtung zu ihr)" % at_pll[cat] if g == "Top-Zelle" and at_pll[cat] else ""
    print("  %-40s %5d%s" % ("%s / %s" % (g, cat), n, note))
if ignored:
    print("  -- nicht gezaehlt, nur in der PLL (Rahul): %d Fehler, %s" % (
        sum(ignored.values()), ", ".join("%s %d" % (c, n) for c, n in Counter({c: n for (g, c), n in ignored.items()}).most_common(6))))
n = sum(counted.values())
print("  DRC: %s" % ("sauber" if n == 0 else "%d Fehler -- %s (in KLayout: Tools > Marker Browser)" % (n, lyrdb[0])))
sys.exit(0 if n == 0 else 1)
