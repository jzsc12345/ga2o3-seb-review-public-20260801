#!/bin/bash
set -u

workdir=/root/DECKBUILD/preflight/VICTORYMESH_SEB_ATLAS_TRANSPORT_RESAVE_D75BFD9_20260807
sentinel="$workdir/VICTORY_EXECUTION_STARTED.flag"

cd "$workdir" || exit 31
if [ -e "$sentinel" ]; then
  echo "VICTORY_EXECUTION_ALREADY_CONSUMED"
  exit 90
fi

# The sentinel is created immediately before the sole allowed controller.
# Re-invoking this launcher cannot start a second Victory Mesh process.
: > "$sentinel" || exit 32
export SFLM_SERVERS=+localhost
export PATH=/atctools/Synopsys/Silvaco2024/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

/usr/bin/script -q -f -c \
  '/root/.local/bin/python3 run_victory_resave_gate.py --deck VICTORYMESH_ATLAS_TRANSPORT_RESAVE_EXECUTED.in --transcript victorymesh_transcript.log --status RESAVE_STATUS.txt --timeout 120' \
  controller.typescript
controller_exit=$?
echo "CONTROLLER_EXIT=$controller_exit" > CONTROLLER_EXIT.txt
exit "$controller_exit"
