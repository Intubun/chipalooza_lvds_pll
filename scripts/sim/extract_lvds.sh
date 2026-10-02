#!/bin/bash
# Post-layout netlists of lvds_tx and lvds_pattern for
# testbenches/xschem/sg13cmos5l_chipalooza_analog_project_tb_lvds_postlayout.sch
#
#   bash scripts/sim/extract_lvds.sh        # in the container; or: make extract-lvds
#
# Magic extraction with coupling capacitance (cthresh 0.01 fF) - the same
# script CACE runs for its pex column - of macros/<cell>/layout/<cell>.gds,
# with the port order read from the schematic.  Writes netlist/pex/lvds_tx_pex.spice
# and netlist/pex/lvds_pattern_pex.spice; the work files go to build/extract_lvds/.
#
# lvds_tx gets the node names the bench uses: the CMFB node as xdrv.cmfb (its
# .ic) and the pre-driver pair as In_p / In_n, plus a 1 TOhm shunt on every node,
# because metal islands that only coupling caps reach make the operating point
# singular otherwise.
#
# No `set -u`: sak-pdk-script.sh reads unset variables.
cd "$(dirname "$0")/../.." || exit 1
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null 2>&1
ROOT=$PWD
OUT=$ROOT/netlist/pex
W=$ROOT/build/extract_lvds
rm -rf "$W" && mkdir -p "$W" "$OUT"
for m in lvds_tx lvds_pattern; do
    mkdir -p "$W/$m"
    xschem -s -r -x -q --rcfile macros/$m/schematic/xschem/xschemrc --command "
        set top_is_subckt 1; set lvs_ignore 1;
        set netlist_dir [file normalize $W/$m];
        xschem set netlist_name ${m}_sch.spice; xschem netlist
    " macros/$m/schematic/xschem/$m.sch > "$W/$m/xschem.log" 2>&1
    if [ ! -s "$W/$m/${m}_sch.spice" ]; then
        echo "  Schaltplan-Netzliste von $m fehlt -- $W/$m/xschem.log"; exit 1
    fi
    {
        echo "gds flatglob via_stack*"
        echo "gds read $ROOT/macros/$m/layout/$m.gds"
        echo "load $m"; echo "readspice $W/$m/${m}_sch.spice"; echo "load $m"
        echo "select top cell"; echo "expand"
        echo "extract path $W/$m"; echo "extract all"
        echo "ext2spice lvs"; echo "ext2spice cthresh 0.01"
        echo "ext2spice -p $W/$m -o $W/$m/${m}_raw.spice"
        echo "quit -noprompt"
    } > "$W/$m/ext.tcl"
    (cd "$W/$m" && magic -dnull -noconsole -rcfile "$PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc" < ext.tcl > magic.log 2>&1)
    if [ ! -s "$W/$m/${m}_raw.spice" ]; then
        echo "  Extraktion von $m fehlgeschlagen -- $W/$m/magic.log"; exit 1
    fi
done
python3 - "$W" "$OUT" <<'EOF'
import re, sys
W, OUT = sys.argv[1:3]
tok = lambda l, a, b: re.sub(r"(?<=\s)%s(?=\s|$)" % re.escape(a), b, l)
# lvds_tx: CMFB node and the pre-driver pair under the names the bench uses
out, sub = [], None
for l in open(W + "/lvds_tx/lvds_tx_raw.spice").read().split("\n"):
    if l.startswith(".subckt "): sub = l.split()[1]
    if not l.startswith("*"):
        if sub == "Driver": l = tok(l, "x_cmfb/cmfb", "cmfb")
        if sub == "lvds_tx":
            l = tok(l, "pd/In_p", "In_p"); l = tok(l, "pd/In_n", "In_n")
            l = tok(l, "drv/x_cmfb/cmfb", "xdrv.cmfb")
    if l.startswith(".ends"): sub = None
    out.append(l)
open(OUT + "/lvds_tx_pex.spice", "w").write(
    "* lvds_tx, magic extraction with coupling C (scripts/sim/extract_lvds.sh)\n"
    "* CMFB node -> xdrv.cmfb, pre-driver pair -> In_p / In_n\n"
    ".option rshunt=1e12\n" + "\n".join(out))
open(OUT + "/lvds_pattern_pex.spice", "w").write(
    "* lvds_pattern, magic extraction with coupling C (scripts/sim/extract_lvds.sh)\n"
    + open(W + "/lvds_pattern/lvds_pattern_raw.spice").read())
for m in ("lvds_tx", "lvds_pattern"):
    t = open("%s/%s_pex.spice" % (OUT, m)).read()
    print("  %-13s %4d C, %3d Instanzen -> %s/%s_pex.spice" % (m, len(re.findall(r"^C", t, re.M)), len(re.findall(r"^X", t, re.M)), OUT, m))
EOF
