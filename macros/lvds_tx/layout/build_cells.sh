#!/bin/bash
# Regenerate every leaf device cell from scratch, patch the PDK's DRC errors
# out of them, check the result, and say whether the cells above still fit.
#
# This is the cheap half of the flow: it leaves the placement alone, and with
# it anything drawn into the GDS by hand.  Safe only while the leaf cells
# keep their names and their sizes, which is what the last step checks.
# Runs inside the IIC-OSIC-TOOLS container.
set -e
cd "$(dirname "$0")"
# the PDK helper returns non-zero even when it works, so keep set -e off it
source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l >/dev/null || true
RC=/foss/pdks/ihp-sg13cmos5l/libs.tech/magic/ihp-sg13cmos5l.magicrc

rm -rf cells && mkdir cells
python3 gen_devices.py cells/gen_devices.tcl
(cd cells && magic -dnull -noconsole -rcfile "$RC" gen_devices.tcl > gen_devices.log 2>&1)
grep -c "^MADE " cells/gen_devices.log | xargs echo "leaf cells generated:"
python3 patch_cells.py cells
magic -dnull -noconsole -rcfile "$RC" check_drc_cells.tcl 2>&1 | grep -E "^DRC "
python3 build_placement.py --check
# Export so the result can be looked at.  Only ever lvds_tx_gen.gds -- the
# placement is not rewritten and lvds_tx.gds is not touched.
magic -dnull -noconsole -rcfile "$RC" save_gds.tcl > gds.log 2>&1
ls -l lvds_tx_gen.gds | awk '{print "  lvds_tx_gen.gds neu geschrieben:", $5, "bytes"}'
