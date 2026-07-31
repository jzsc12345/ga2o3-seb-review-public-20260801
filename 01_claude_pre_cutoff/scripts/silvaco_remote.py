#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
silvaco_remote.py -- SSH control layer between the Windows control node
(D:\\SILVACO_LOCAL) and the remote Silvaco 2024 VM.

Why an xterm?  `deckbuild -ascii -run` needs a controlling TTY.  Launched
straight over SSH it blocks forever before ATLAS ever starts (reproduced
2026-07-26).  The proven pattern -- and the one already used by this
project's guarded runner -- is:

    DISPLAY=:0 nohup xterm -e bash -lc 'script -q -f -c "deckbuild ..." typescript'

`script` supplies the pty, `xterm` gives it a real terminal on the VM's
physical X display, and `nohup` detaches it so the SSH session can drop.
It also makes the run VISIBLE on the VM desktop, which is what the
3-minute screenshot watchdog captures.

File-placement discipline enforced here:
  - control node D:\\SILVACO_LOCAL  ->  .py .md .csv .png .in only
  - bulk .str / .log archives       ->  E:\\silvaco2425\\bulk\\{str,log}
  - live run directories            ->  remote /root/DECKBUILD/<project>/<run>
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# Fixed local layout
# --------------------------------------------------------------------------
CONTROL_ROOT = Path(r"D:\SILVACO_LOCAL")
DECKS_DIR = CONTROL_ROOT / "decks"
OUTPUTS_DIR = CONTROL_ROOT / "outputs"
BULK_ROOT = Path(r"E:\silvaco2425\bulk")
BULK_STR = BULK_ROOT / "str"
BULK_LOG = BULK_ROOT / "log"

SSH_KEY = r"C:/Users/Administrator/.ssh/silvaco_ed25519"
# The ~/.ssh/config alias `silvaco` still points at 192.168.50.134, which the
# VM lost on its last cold boot.  Candidates are probed in order; never
# hardcode a single address into a runner.
HOST_CANDIDATES = ["192.168.107.128", "192.168.50.134"]
SSH_USER = "root"

SILVACO_BIN = "/atctools/Synopsys/Silvaco2024/bin"
ATLAS_VERSION = "5.40.0.R"
ATLAS_PARALLEL = 4
REMOTE_PROJECT = "/root/DECKBUILD/Wang2026_SEB_fit_20260726"

_SSH_BASE = [
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=8",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "LogLevel=ERROR",
    "-i", SSH_KEY,
]

# --------------------------------------------------------------------------
# Desktop-session environment
#
# A bare SSH shell has DISPLAY but no XAUTHORITY, so any Silvaco GUI
# (VictoryDoE, TonyPlot, DeckBuild, Victory Visual) starts, fails the X
# handshake, and dies without ever mapping a window -- it looks like "the
# app won't open".  The VM runs MATE under lightdm, whose cookie lives at
# /var/run/lightdm/root/xauthority, and MATE also owns the session DBus.
#
# This prelude lifts the real session environment out of /proc/<mate-session>
# so a remotely launched GUI is byte-for-byte what you get by typing the
# command into a terminal on the VM desktop.
# --------------------------------------------------------------------------
SESSION_ENV_PRELUDE = r"""
__SESSPID=$(pgrep -f mate-session 2>/dev/null | head -1)
if [ -n "$__SESSPID" ] && [ -r "/proc/$__SESSPID/environ" ]; then
  set -a
  eval "$(tr '\0' '\n' < /proc/$__SESSPID/environ \
        | grep -E '^(DISPLAY|XAUTHORITY|DBUS_SESSION_BUS_ADDRESS|XDG_RUNTIME_DIR|XDG_DATA_DIRS|XDG_CONFIG_DIRS|LANG)=' \
        | sed 's/^\([A-Za-z_][A-Za-z0-9_]*\)=\(.*\)$/\1="\2"/')"
  set +a
fi
export DISPLAY="${DISPLAY:-:0}"
if [ -z "$XAUTHORITY" ] && [ -r /var/run/lightdm/root/xauthority ]; then
  export XAUTHORITY=/var/run/lightdm/root/xauthority
fi
export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
export SFLM_SERVERS="${SFLM_SERVERS:-+localhost}"
"""


def _posix(text: str) -> str:
    """Strip CR from anything shipped to the remote bash.

    This file lives on Windows, so every literal here carries CRLF.  bash
    reads a trailing '\\r' as part of the token, which turns a backslash
    line-continuation into 'backslash + CR' (no longer a continuation) and
    makes plain commands fail with "$'\\r': command not found".  Normalise
    once, at the single point where text crosses to the remote shell.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


class RemoteError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Connection
# --------------------------------------------------------------------------
@dataclass
class Remote:
    host: str = ""
    user: str = SSH_USER
    _resolved: bool = field(default=False, repr=False)

    def resolve(self, verbose: bool = True) -> str:
        """Probe the candidate addresses and latch the first that answers."""
        if self._resolved and self.host:
            return self.host
        if self.host:
            candidates = [self.host]
        else:
            candidates = HOST_CANDIDATES
        for cand in candidates:
            cmd = ["ssh", *_SSH_BASE, f"{self.user}@{cand}", "echo __OK__; hostname"]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            except subprocess.TimeoutExpired:
                continue
            if r.returncode == 0 and "__OK__" in r.stdout:
                self.host = cand
                self._resolved = True
                if verbose:
                    name = r.stdout.replace("__OK__", "").strip()
                    print(f"[remote] {self.user}@{cand} reachable (hostname={name})")
                return cand
        raise RemoteError(
            "no reachable Silvaco host among " + ", ".join(candidates) +
            " -- check the VM is powered on and the VMware vmnet subnet matches"
        )

    @property
    def target(self) -> str:
        return f"{self.user}@{self.resolve(verbose=False)}"

    # ---- primitives ------------------------------------------------------
    def sh(self, script: str, timeout: int = 120, check: bool = False,
           login: bool = True, session_env: bool = True) -> subprocess.CompletedProcess:
        """Run a bash snippet remotely, passed on stdin (avoids quoting hell).

        session_env=True prepends the MATE desktop environment so GUI tools
        and X screen-grabs behave exactly as they do on the VM console.
        """
        flag = "-l -s" if login else "-s"
        cmd = ["ssh", *_SSH_BASE, self.target, f"bash {flag}"]
        payload = (SESSION_ENV_PRELUDE + "\n" + script) if session_env else script
        # NOTE: bytes, not text=True.  With text=True Python wraps stdin in a
        # TextIOWrapper whose default newline translation rewrites every '\n'
        # back into '\r\n' on Windows -- which re-introduces exactly the CRs
        # _posix() just stripped, and bash then chokes with
        # "$'\r': command not found".  Encoding here keeps the payload LF-only.
        raw = subprocess.run(cmd, input=_posix(payload).encode("utf-8"),
                             capture_output=True, timeout=timeout)
        r = subprocess.CompletedProcess(
            raw.args, raw.returncode,
            raw.stdout.decode("utf-8", "replace"),
            raw.stderr.decode("utf-8", "replace"),
        )
        if check and r.returncode != 0:
            raise RemoteError(f"remote command failed (rc={r.returncode}):\n{r.stderr}")
        return r

    def push(self, local: Path, remote_path: str, timeout: int = 300) -> None:
        cmd = ["scp", *_SSH_BASE, str(local), f"{self.target}:{remote_path}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RemoteError(f"scp push {local} failed: {r.stderr}")

    def pull(self, remote_path: str, local: Path, timeout: int = 900) -> bool:
        local.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["scp", *_SSH_BASE, f"{self.target}:{remote_path}", str(local)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0

    def exists(self, remote_path: str) -> bool:
        return self.sh(f"test -e {shlex.quote(remote_path)}", timeout=30).returncode == 0

    def read(self, remote_path: str, timeout: int = 60) -> str:
        r = self.sh(f"cat {shlex.quote(remote_path)} 2>/dev/null", timeout=timeout)
        return r.stdout


# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------
PREFLIGHT_SCRIPT = f"""
export PATH={SILVACO_BIN}:$PATH
export SFLM_SERVERS=${{SFLM_SERVERS:-+localhost}}
echo "HOSTNAME=$(hostname)"
echo "IPS=$(hostname -I)"
echo "NPROC=$(nproc)"
echo "DISPLAY_SOCKETS=$(ls /tmp/.X11-unix/ 2>/dev/null | tr '\\n' ' ')"
echo "SFLM_SERVERS=$SFLM_SERVERS"
for t in deckbuild atlas devedit tonyplot victorydoe victoryvisual victoryextract vwf; do
  printf 'TOOL %-16s %s\\n' "$t" "$(command -v $t 2>/dev/null || echo MISSING)"
done
echo "ATLAS_VERSIONS=$(ls {SILVACO_BIN}/../lib/atlas 2>/dev/null | tr '\\n' ' ')"
echo "SFLM_PROC=$(ps -ef | grep -c '[s]flm_monitord')"
echo "XDPYINFO=$(DISPLAY=:0 xdpyinfo >/dev/null 2>&1 && echo OK || echo FAIL)"
echo "ROOT_FREE=$(df -h / | awk 'NR==2{{print $4}}')"
echo "RUNNING_ATLAS=$(ps -ef | grep -c '[a]tlas.exe')"
"""


def preflight(rem: Remote) -> dict:
    r = rem.sh(PREFLIGHT_SCRIPT, timeout=120)
    info: dict = {"tools": {}}
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("TOOL "):
            parts = line.split(None, 2)
            if len(parts) == 3:
                info["tools"][parts[1]] = parts[2]
        elif "=" in line:
            k, _, v = line.partition("=")
            info[k.strip()] = v.strip()
    return info


# --------------------------------------------------------------------------
# Detached deck launch
# --------------------------------------------------------------------------
# The session prelude (DISPLAY + XAUTHORITY + DBus + PATH + SFLM) is already
# applied by Remote.sh(), so the xterm inherits a real desktop environment.
_LAUNCH = """
set -e
WD={wd}
mkdir -p "$WD"
cd "$WD"
rm -f exit_code.txt typescript xterm.log STATUS.txt
echo "running" > STATUS.txt
nohup xterm -geometry {geom} -T {title} \\
  -e bash -lc 'cd "'"$WD"'"; \\
      export DISPLAY="'"$DISPLAY"'" XAUTHORITY="'"$XAUTHORITY"'"; \\
      export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH SFLM_SERVERS=+localhost; \\
      script -q -f -c "deckbuild -ascii -run {deck}" typescript; \\
      rc=$?; printf "%s\\n" "$rc" > exit_code.txt; \\
      if [ "$rc" = "0" ]; then echo done > STATUS.txt; else echo failed > STATUS.txt; fi' \\
  > xterm.log 2>&1 &
echo "XTERM_PID=$!"
sleep 2
echo "LAUNCHED"
"""


def launch_deck(rem: Remote, workdir: str, deck_name: str,
                title: str = "ATLAS", display: str = ":0",
                geom: str = "150x46") -> str:
    """Start a deck detached on the VM's physical display. Returns xterm pid."""
    script = _LAUNCH.format(
        bin=SILVACO_BIN, wd=shlex.quote(workdir), display=display,
        geom=geom, title=shlex.quote(title), deck=shlex.quote(deck_name),
    )
    r = rem.sh(script, timeout=90)
    if "LAUNCHED" not in r.stdout:
        raise RemoteError(f"launch failed:\n{r.stdout}\n{r.stderr}")
    pid = ""
    for line in r.stdout.splitlines():
        if line.startswith("XTERM_PID="):
            pid = line.split("=", 1)[1].strip()
    print(f"[launch] {deck_name} in {workdir} (xterm pid {pid}, DISPLAY={display})")
    return pid


# ATLAS terminators.  Deliberately NOT `grep Error` -- normal convergence
# chatter contains the word "error" and would give false positives.
FAIL_PATTERNS = ("ATLAS DIED", "Fatal error", "license", "LICENSE",
                 "syntax error", "Unknown parameter")


@dataclass
class RunState:
    status: str = "running"
    exit_code: int | None = None
    tail: str = ""
    seconds: float = 0.0


def poll_run(rem: Remote, workdir: str, tail_lines: int = 25) -> RunState:
    script = f"""
cd {shlex.quote(workdir)} 2>/dev/null || {{ echo "STATUS=missing"; exit 0; }}
echo "STATUS=$(cat STATUS.txt 2>/dev/null || echo unknown)"
echo "EXITCODE=$(cat exit_code.txt 2>/dev/null || echo none)"
echo "---TAIL---"
tail -{tail_lines} typescript 2>/dev/null | tr -d '\\r'
"""
    r = rem.sh(script, timeout=60)
    st = RunState()
    body, _, tail = r.stdout.partition("---TAIL---")
    st.tail = tail.strip()
    for line in body.splitlines():
        if line.startswith("STATUS="):
            st.status = line.split("=", 1)[1].strip()
        elif line.startswith("EXITCODE="):
            v = line.split("=", 1)[1].strip()
            st.exit_code = int(v) if v.isdigit() else None
    return st


def wait_for_run(rem: Remote, workdir: str, poll_s: int = 30,
                 timeout_s: int = 7200, on_poll=None) -> RunState:
    """Block until the deck terminates. `on_poll(elapsed, state)` fires each tick."""
    t0 = time.time()
    while True:
        st = poll_run(rem, workdir)
        st.seconds = time.time() - t0
        if on_poll:
            on_poll(st.seconds, st)
        if st.status in ("done", "failed"):
            return st
        if st.seconds > timeout_s:
            st.status = "timeout"
            return st
        time.sleep(poll_s)


# --------------------------------------------------------------------------
# Archiving: bulk .str/.log off the control node
# --------------------------------------------------------------------------
def archive_bulk(rem: Remote, workdir: str, run_tag: str,
                 max_str_mb: int = 400) -> dict:
    """Pull .log files (small, needed for curves) and .str files to E:\\ bulk."""
    BULK_STR.mkdir(parents=True, exist_ok=True)
    BULK_LOG.mkdir(parents=True, exist_ok=True)
    listing = rem.sh(
        f"cd {shlex.quote(workdir)} && ls -1 *.log *.str *.out typescript 2>/dev/null",
        timeout=60).stdout.split()
    pulled = {"log": [], "str": [], "skipped": []}
    for name in listing:
        if name.endswith(".str"):
            dest = BULK_STR / f"{run_tag}__{name}"
            key = "str"
        else:
            dest = BULK_LOG / f"{run_tag}__{name}"
            key = "log"
        if rem.pull(f"{workdir}/{name}", dest):
            pulled[key].append(str(dest))
        else:
            pulled["skipped"].append(name)
    return pulled


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Silvaco remote control")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("preflight", help="probe host, tools, license, display")

    p_run = sub.add_parser("run", help="upload a deck and launch it detached")
    p_run.add_argument("deck", help="local .in file under decks/")
    p_run.add_argument("--workdir", default=None)
    p_run.add_argument("--title", default=None)
    p_run.add_argument("--wait", action="store_true")
    p_run.add_argument("--timeout", type=int, default=7200)
    p_run.add_argument("--extra", nargs="*", default=[],
                       help="extra local files to upload alongside (e.g. mySEU.c)")

    p_poll = sub.add_parser("poll", help="show status of a remote run dir")
    p_poll.add_argument("workdir")

    p_arch = sub.add_parser("archive", help="pull .log/.str to E:\\silvaco2425\\bulk")
    p_arch.add_argument("workdir")
    p_arch.add_argument("tag")

    a = ap.parse_args(argv)
    rem = Remote()

    if a.cmd == "preflight":
        info = preflight(rem)
        for k, v in info.items():
            if k == "tools":
                for t, path in v.items():
                    mark = "OK " if path != "MISSING" else "!! "
                    print(f"  {mark}{t:<16} {path}")
            else:
                print(f"{k:<18} {v}")
        missing = [t for t, p in info["tools"].items() if p == "MISSING"]
        if missing:
            print(f"\nMISSING TOOLS: {', '.join(missing)}")
        return 0

    if a.cmd == "run":
        deck = Path(a.deck)
        if not deck.is_absolute():
            deck = DECKS_DIR / deck
        if not deck.exists():
            print(f"deck not found: {deck}", file=sys.stderr)
            return 2
        wd = a.workdir or f"{REMOTE_PROJECT}/{deck.stem}"
        rem.sh(f"mkdir -p {shlex.quote(wd)}", check=True, timeout=60)
        rem.push(deck, f"{wd}/{deck.name}")
        for extra in a.extra:
            ep = Path(extra)
            if not ep.is_absolute():
                ep = CONTROL_ROOT / extra
            rem.push(ep, f"{wd}/{ep.name}")
            print(f"[push] {ep.name}")
        launch_deck(rem, wd, deck.name, title=a.title or deck.stem)
        print(f"[workdir] {wd}")
        if a.wait:
            def show(el, st):
                print(f"  t={el:7.0f}s status={st.status}")
            st = wait_for_run(rem, wd, timeout_s=a.timeout, on_poll=show)
            print(f"[final] status={st.status} exit={st.exit_code}")
            print(st.tail)
            return 0 if st.status == "done" else 1
        return 0

    if a.cmd == "poll":
        st = poll_run(rem, a.workdir)
        print(f"status={st.status} exit={st.exit_code}")
        print(st.tail)
        return 0

    if a.cmd == "archive":
        res = archive_bulk(rem, a.workdir, a.tag)
        for k, v in res.items():
            print(f"{k}: {len(v)}")
            for item in v[:20]:
                print(f"   {item}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
