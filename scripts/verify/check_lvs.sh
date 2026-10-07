#!/bin/bash
# Top-level LVS (KLayout, IHP deck) of layout/slot_14.gds against the top schematic.
#
#   bash scripts/verify/check_lvs.sh                  # in the container, from anywhere
#   bash scripts/verify/check_lvs.sh --ignore-ports   # leave the top-level pin names out
#   bash scripts/verify/check_lvs.sh <gds>            # another copy of the top layout
#
# Results in build/verify/lvs/: reference.cdl, layout.gds (the copies that were
# compared), <top>.lvsdb (open it in KLayout: Tools > Netlist Browser), lvs.log.
# The summary goes to stdout; exit status 0 only when the netlists match.
#
# The schematic carries the slot-14 frame pin for pin (scripts/gen_top.py), so the
# top-level pin names are compared too.  --ignore-ports leaves them out
# (--ignore_top_ports_mismatch) - the circuit behind the pins is compared either way.
#
# Taps are not extracted as devices (--disable_tap_extraction): no schematic here
# draws them.  Floating metal is purged (--purge_nets).
#
# No `set -u`: sak-pdk-script.sh reads unset variables.
TOP=slot_14
cd "$(dirname "$0")/../.." || exit 1
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
PORTS=
GDS=layout/$TOP.gds
while [ $# -gt 0 ]; do
    case $1 in
        --ignore-ports) PORTS=--ignore_top_ports_mismatch ;;
        --strict-ports) PORTS= ;;      # the default since 2026-10-07
        -h|--help) sed -n 2,18p "$0"; exit 0 ;;
        *) GDS=$1 ;;
    esac
    shift
done
RUN=build/verify/lvs
rm -rf "$RUN" && mkdir -p "$RUN"
echo "== LVS $TOP ($GDS)"

xschem -s -r -x -q --rcfile schematic/xschem/xschemrc --command "
    set spiceprefix 1; set lvs_netlist 1; set top_is_subckt 1;
    set lvs_ignore 1; set ev_precision 5;
    set netlist_dir [file normalize $RUN];
    xschem set netlist_name schematic.cdl; xschem netlist
" schematic/xschem/$TOP.sch > "$RUN/xschem.log" 2>&1
if [ ! -s "$RUN/schematic.cdl" ]; then
    echo "  Schaltplan-Netzliste fehlt -- $RUN/xschem.log"; exit 2
fi
python3 scripts/verify/prepare_lvs.py "$RUN" "$RUN/schematic.cdl" "$GDS" \
    "$PDK_ROOT/$PDK/libs.ref/sg13cmos5l_stdcell/cdl/sg13cmos5l_stdcell.cdl" || exit 2

# vss_1v2 and vss_3v3 are one net: every tap of either ground sits in the same
# p-substrate, so the extraction merges them, and the harness ties them on purpose
# (chipalooza_frame.v: assign vss3v3 = vss1v2, a 0-ohm resistor in its schematic).
# The schematic keeps both frame pins, so the deck has to be told: a copy of it
# joins the listed nets of the reference right after reading it.  Both pins stay
# pins, so the strict port check still sees both names.
DECK=build/verify/lvs_deck
rm -rf "$DECK" && cp -rL "$PDK_ROOT/$PDK/libs.tech/klayout/tech/lvs" "$DECK"    # -L: it links into ihp-sg13g2
python3 - "$DECK/sg13cmos5l.lvs" <<'EOF'
import sys
p = sys.argv[1]
s = open(p).read()
anchor = '    schematic($schematic, reader)\n'
assert s.count(anchor) == 1, "deck changed - no unique schematic() call to hook into"
hook = anchor + '''    (ENV["LVS_JOIN_NETS"] || "").split(";").each do |spec|
      cname, a, b = spec.split(",")
      c = schematic.circuit_by_name(cname) || schematic.circuit_by_name(cname.upcase)
      na = c && (c.net_by_name(a) || c.net_by_name(a.upcase))
      nb = c && (c.net_by_name(b) || c.net_by_name(b.upcase))
      if na && nb
        c.join_nets(na, nb)
        logger.info("Joined #{a} and #{b} in the reference #{cname} (LVS_JOIN_NETS)")
      else
        error("LVS_JOIN_NETS: #{spec} not found in the reference")
      end
    end
'''
open(p, "w").write(s.replace(anchor, hook))
EOF
LVS_JOIN_NETS="$TOP,vss_1v2,vss_3v3" python3 "$DECK/run_lvs.py" \
    --layout="$RUN/layout.gds" --netlist="$RUN/reference.cdl" --topcell=$TOP \
    --run_dir="$RUN" --run_mode=deep --disable_tap_extraction --purge_nets \
    $PORTS > "$RUN/lvs.log" 2>&1

python3 scripts/verify/lvs_summary.py "$RUN" $TOP
