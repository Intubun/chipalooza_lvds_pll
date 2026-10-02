#!/bin/bash
# Top-level DRC and LVS in one go (see check_drc.sh and check_lvs.sh for the options;
# the ones given here are passed to both where they apply).
#
#   bash scripts/verify/check_all.sh
#
# Exit status 0 only when both are clean.
cd "$(dirname "$0")" || exit 1
DRC_ARGS=(); LVS_ARGS=()
for a in "$@"; do
    case $a in
        --with-pll|--no-antenna|--density) DRC_ARGS+=("$a") ;;
        --strict-ports) LVS_ARGS+=("$a") ;;
        *) DRC_ARGS+=("$a"); LVS_ARGS+=("$a") ;;
    esac
done
bash check_drc.sh "${DRC_ARGS[@]}"; d=$?
bash check_lvs.sh "${LVS_ARGS[@]}"; l=$?
echo "== DRC $([ $d = 0 ] && echo sauber || echo FEHLER), LVS $([ $l = 0 ] && echo sauber || echo FEHLER)"
[ $d = 0 ] && [ $l = 0 ]
