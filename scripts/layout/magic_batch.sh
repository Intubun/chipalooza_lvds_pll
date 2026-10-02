#!/usr/bin/env bash
# Run a Magic Tcl script headlessly with the IHP SG13CMOS5L tech, from a
# directory of editable .mag cells.
#
#   magic_batch.sh <mag_dir> <script.tcl> [NAME=value ...]
#
# NAME=value pairs are exported to the environment and are readable in the
# script as $::env(NAME). Run inside the IIC-OSIC container.
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: $0 <mag_dir> <script.tcl> [NAME=value ...]" >&2
  exit 2
fi

MAG_DIR=$(realpath "$1")
SCRIPT=$(realpath "$2")
shift 2
for assignment in "$@"; do
  export "${assignment?}"
done

export PDK_ROOT=${PDK_ROOT:-/foss/pdks}
export PDK=ihp-sg13cmos5l
export PDKPATH=$PDK_ROOT/$PDK
export SPICE_USERINIT_DIR=$PDKPATH/libs.tech/ngspice
export KLAYOUT_PATH=/headless/.klayout:$PDKPATH/libs.tech/klayout
export PATH=/foss/tools/bin:/foss/tools/klayout:$PATH

export LAYOUT_SCRIPTS
LAYOUT_SCRIPTS=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
cd "$MAG_DIR"
magic -dnull -noconsole \
  -rcfile "$PDK_ROOT/$PDK/libs.tech/magic/ihp-sg13cmos5l.magicrc" \
  "$SCRIPT" </dev/null
