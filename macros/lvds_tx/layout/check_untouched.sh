#!/bin/bash
# What the generator owns, and what it must never write.
#
# Everything under cells/, the .mag hierarchy, floorplan.json, the logs and
# lvds_tx_gen.gds are generated and may be rebuilt at will.  lvds_tx.gds is
# the file someone edits in KLayout: no script here writes it, and this
# check is what makes that claim testable rather than a promise.
#
#   bash check_untouched.sh          record the current state
#   bash check_untouched.sh verify   compare against the recorded state
cd "$(dirname "$0")" || exit 1
OWNED="lvds_tx.gds"
STATE=".untouched.state"

snapshot() {
    for f in $OWNED; do
        [ -f "$f" ] && echo "$f $(md5sum < "$f" | cut -d" " -f1) $(stat -c%Y "$f")"
    done
}

if [ "$1" = "verify" ]; then
    [ -f "$STATE" ] || { echo "kein Vergleichsstand - erst ohne Argument aufrufen"; exit 0; }
    if diff -q <(snapshot) "$STATE" > /dev/null; then
        echo "unveraendert: $OWNED"
    else
        echo "ACHTUNG - eine Nutzerdatei hat sich geaendert:"
        diff "$STATE" <(snapshot)
        exit 1
    fi
else
    snapshot > "$STATE"
    echo "Stand festgehalten: $OWNED"
fi
