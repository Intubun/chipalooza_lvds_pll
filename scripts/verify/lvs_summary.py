#!/usr/bin/env python3
"""Summary of a KLayout LVS run: verdict, then every circuit that did not match
with what is unmatched in it.   lvs_summary.py <run_dir> <top>"""
import glob, sys
import klayout.db as kdb
run, top = sys.argv[1:3]
log = open(run + "/lvs.log", errors="ignore").read()
dbs = glob.glob(run + "/*.lvsdb")
if not dbs:
    print("  keine .lvsdb -- Abbruch im Lauf, siehe %s/lvs.log:" % run)
    print("\n".join("    " + l for l in log.strip().split("\n")[-8:]))
    sys.exit(2)
lvs = kdb.LayoutVsSchematic(); lvs.read(dbs[0])
x = lvs.xref()
S = kdb.NetlistCrossReference
ok = (S.Match, S.MatchWithWarning)
bad = 0
name = lambda o: o.expanded_name() if hasattr(o, "expanded_name") and o is not None else (o.name if o is not None else "-")
for cp in x.each_circuit_pair():
    a, b = cp.first(), cp.second()
    st = cp.status()
    cname = (a or b).name
    if st in ok:
        continue
    bad += 1
    print("  %-28s %s" % (cname, {S.Mismatch: "MISMATCH", S.NoMatch: "keine Entsprechung", S.Skipped: "uebersprungen"}.get(st, str(st))))
    if a is None or b is None:
        print("     nur im %s" % ("Schaltplan" if a is None else "Layout"))
        continue
    for kind, it in (("Pin", x.each_pin_pair), ("Netz", x.each_net_pair), ("Device", x.each_device_pair), ("Subcircuit", x.each_subcircuit_pair)):
        items = [p for p in it(cp) if p.status() not in ok]
        for p in items[:12]:
            print("     %-10s Layout %-28s Schaltplan %s" % (kind, name(p.first()), name(p.second())))
        if len(items) > 12:
            print("     ... %d weitere %s" % (len(items) - 12, kind))
if "Congratulations! Netlists match." in log:
    print("  LVS: Netzlisten stimmen ueberein")
    sys.exit(0)
if bad == 0:
    # the deck has checks outside the cross reference (flag_missing_ports: unlabelled or
    # misnamed top-level ports) - show what it said
    print("  Abgleich der Circuits ok, aber der Lauf meldet einen Fehler:")
    said = [l.split(" : ", 1)[-1].strip() for l in log.split("\n") if "ERROR" in l or "port" in l.lower()]
    print("\n".join("    " + l for l in said[-12:]))
print("  LVS: Netzlisten stimmen NICHT ueberein (%d Circuits) -- %s, im Netlist Browser: %s" % (bad, run + "/lvs.log", dbs[0]))
sys.exit(1)
