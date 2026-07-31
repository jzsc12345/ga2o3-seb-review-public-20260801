#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
screenshot_watch.py -- capture the remote Silvaco VM's X display every N
minutes (default 3) into a dedicated local output folder.

The simulation runs inside an xterm on the VM's physical display :0 (see
silvaco_remote.py for why a real terminal is required), so a screenshot of
:0 shows the live ATLAS progress, any TonyPlot / VictoryDoE window, and the
desktop state -- all in one frame.

Capture chain on the VM:  ImageMagick `import -window root` -> PNG
Then scp back to the control node.  PNGs are the one bulky artefact the
control node is allowed to hold, so they land in
D:\\SILVACO_LOCAL\\outputs\\<session>\\screenshots\\.

Usage
  python screenshot_watch.py --session wang2026_seb --interval 180
  python screenshot_watch.py --session wang2026_seb --once
  python screenshot_watch.py --session wang2026_seb --until-status /root/.../run
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from silvaco_remote import Remote, OUTPUTS_DIR, poll_run  # noqa: E402

REMOTE_TMP = "/tmp/silvaco_shots"


def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%dT%H%M%S")


def capture_once(rem: Remote, dest_dir: Path, display: str = ":0",
                 label: str = "") -> Path | None:
    """Grab the VM root window and pull it back. Returns the local PNG path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = _stamp()
    suffix = f"_{label}" if label else ""
    remote_png = f"{REMOTE_TMP}/shot_{ts}{suffix}.png"

    script = f"""
export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
mkdir -p {REMOTE_TMP}
export DISPLAY={display}
if ! xdpyinfo >/dev/null 2>&1; then echo "XFAIL"; exit 1; fi
# -window root grabs the whole desktop; ImageMagick is present as /usr/bin/import
import -window root -quality 92 {remote_png} 2>/dev/null \\
  || xwd -root -silent | convert xwd:- {remote_png} 2>/dev/null
if [ -s {remote_png} ]; then
  echo "OK $(stat -c%s {remote_png})"
else
  echo "CAPFAIL"
fi
"""
    r = rem.sh(script, timeout=120)
    if "OK" not in r.stdout:
        reason = "X display unreachable" if "XFAIL" in r.stdout else "capture failed"
        print(f"[shot] {ts} -- {reason}", file=sys.stderr)
        return None

    local = dest_dir / f"shot_{ts}{suffix}.png"
    if not rem.pull(remote_png, local):
        print(f"[shot] {ts} -- pull failed", file=sys.stderr)
        return None
    rem.sh(f"rm -f {remote_png}", timeout=30)
    size_kb = local.stat().st_size / 1024
    print(f"[shot] {local.name}  ({size_kb:.0f} KB)")
    return local


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="periodic VM screenshot watchdog")
    ap.add_argument("--session", required=True,
                    help="output session name -> outputs/<session>/screenshots/")
    ap.add_argument("--interval", type=float, default=180.0,
                    help="seconds between captures (default 180 = 3 min)")
    ap.add_argument("--once", action="store_true", help="single capture then exit")
    ap.add_argument("--max-shots", type=int, default=0, help="0 = unlimited")
    ap.add_argument("--until-status", default=None,
                    help="remote run dir; stop when its STATUS.txt is done/failed")
    ap.add_argument("--display", default=":0")
    ap.add_argument("--label", default="")
    a = ap.parse_args(argv)

    dest = OUTPUTS_DIR / a.session / "screenshots"
    rem = Remote()
    rem.resolve()
    print(f"[watch] session={a.session}")
    print(f"[watch] dest={dest}")

    if a.once:
        return 0 if capture_once(rem, dest, a.display, a.label) else 1

    print(f"[watch] interval={a.interval:.0f}s  "
          f"stop_on={a.until_status or 'ctrl-c / max-shots'}")
    n = 0
    try:
        while True:
            capture_once(rem, dest, a.display, a.label)
            n += 1
            if a.max_shots and n >= a.max_shots:
                print(f"[watch] reached max-shots={a.max_shots}")
                break
            if a.until_status:
                st = poll_run(rem, a.until_status, tail_lines=3)
                if st.status in ("done", "failed", "missing"):
                    print(f"[watch] run status={st.status} -- final capture")
                    capture_once(rem, dest, a.display, f"{a.label}final")
                    break
            time.sleep(a.interval)
    except KeyboardInterrupt:
        print("\n[watch] interrupted")
    print(f"[watch] {n} screenshots in {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
