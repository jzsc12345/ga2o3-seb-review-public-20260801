#!/usr/bin/env python3
"""Run one interactive Victory Mesh process with hard INFO gates.

This controller exists solely to ensure that MATERIAL and SAVE are not sent
unless their immediately preceding INFO evidence matches the frozen STR.
It performs no retry, fallback, remesh, ATLAS invocation, or solve.
"""

from __future__ import annotations

import argparse
import os
import pty
import re
import select
import signal
import subprocess
import sys
import time
from pathlib import Path


PROMPT = b"VICTORYMESH>"
EXPECTED_ELEMENTS = {
    "MATERIAL:GA2O3": 62100,
    "MATERIAL:NIO": 4000,
    "MATERIAL:GAN": 62100,
    "MATERIAL:ZNO": 4000,
    "MATERIAL:SIO2": 34200,
    "MATERIAL:AL2O3": 5360,
    "MATERIAL:NICKEL": 5690,
}


def read_deck(path: Path) -> dict[str, list[str]]:
    stages: dict[str, list[str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        marker = re.fullmatch(r"# STAGE: ([A-Z]+)_(BEGIN|END)", line)
        if marker:
            name, edge = marker.groups()
            if edge == "BEGIN":
                if current is not None:
                    raise RuntimeError("nested stage markers")
                current = name
                stages[current] = []
            else:
                if current != name:
                    raise RuntimeError("unbalanced stage markers")
                current = None
            continue
        if current is not None and line and not line.startswith("#"):
            stages[current].append(line)

    quit_lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().lower() == "quit"
    ]
    if set(stages) != {"PREMAP", "MAPPING", "POSTMAP", "SAVE"}:
        raise RuntimeError(f"unexpected stages: {sorted(stages)}")
    if quit_lines != ["quit"]:
        raise RuntimeError("deck must contain exactly one quit")
    return stages


class VictorySession:
    def __init__(self, transcript: Path, timeout: float) -> None:
        self.transcript_path = transcript
        self.timeout = timeout
        self.master, slave = pty.openpty()
        self.log = transcript.open("wb")
        self.proc = subprocess.Popen(
            ["/atctools/Synopsys/Silvaco2024/bin/victorymesh", "-P", "4"],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True,
            start_new_session=True,
        )
        os.close(slave)

    def _read_until(self, token: bytes, timeout: float | None = None) -> bytes:
        deadline = time.monotonic() + (self.timeout if timeout is None else timeout)
        out = bytearray()
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                # Drain whatever remains after exit.
                ready, _, _ = select.select([self.master], [], [], 0)
                if ready:
                    try:
                        chunk = os.read(self.master, 65536)
                    except OSError:
                        chunk = b""
                    if chunk:
                        out.extend(chunk)
                        self.log.write(chunk)
                        self.log.flush()
                raise RuntimeError(
                    f"Victory Mesh exited early with code {self.proc.returncode}"
                )
            ready, _, _ = select.select([self.master], [], [], 0.25)
            if not ready:
                continue
            try:
                chunk = os.read(self.master, 65536)
            except OSError:
                chunk = b""
            if not chunk:
                continue
            out.extend(chunk)
            self.log.write(chunk)
            self.log.flush()
            if token in out:
                return bytes(out)
        raise TimeoutError(f"timed out waiting for {token!r}")

    def start(self) -> bytes:
        return self._read_until(PROMPT, 120.0)

    def command(self, command: str) -> bytes:
        banner = f"\nCONTROLLER_SEND: {command}\n".encode()
        self.log.write(banner)
        self.log.flush()
        os.write(self.master, command.encode("utf-8") + b"\n")
        return self._read_until(PROMPT)

    def quit(self) -> int:
        self.log.write(b"\nCONTROLLER_SEND: quit\n")
        self.log.flush()
        os.write(self.master, b"quit\n")
        deadline = time.monotonic() + 60.0
        while self.proc.poll() is None and time.monotonic() < deadline:
            ready, _, _ = select.select([self.master], [], [], 0.25)
            if ready:
                try:
                    chunk = os.read(self.master, 65536)
                except OSError:
                    chunk = b""
                if chunk:
                    self.log.write(chunk)
                    self.log.flush()
        if self.proc.poll() is None:
            raise TimeoutError("Victory Mesh did not exit after quit")
        return int(self.proc.returncode or 0)

    def stop_without_retry(self) -> None:
        if self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGTERM)
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait(timeout=10)

    def close(self) -> None:
        self.log.close()
        try:
            os.close(self.master)
        except OSError:
            pass


def output_text(blob: bytes) -> str:
    return blob.decode("utf-8", errors="replace").replace("\r", "")


def reject_errors(text: str, context: str) -> None:
    patterns = [r"\bfatal\b", r"parse error", r"unknown command", r"error:"]
    hits = [p for p in patterns if re.search(p, text, flags=re.IGNORECASE)]
    if hits:
        raise RuntimeError(f"{context}: error pattern(s) {hits}")


def validate_material_info(selector: str, text: str) -> None:
    reject_errors(text, selector)
    material = selector.split(":", 1)[1]
    if not re.search(rf"\bMATERIAL\s*:\s*{re.escape(material)}\b", text, re.I):
        raise RuntimeError(f"{selector}: material label not reported")
    elements = [int(v) for v in re.findall(r"\bELEMENTS\s*:\s*(\d+)", text, re.I)]
    expected = EXPECTED_ELEMENTS[selector]
    if expected not in elements:
        raise RuntimeError(
            f"{selector}: expected ELEMENTS={expected}, observed {elements}"
        )


def validate_electrodes(text: str) -> None:
    reject_errors(text, "TYPE:ELECTRODE")
    if not re.search(r"\bNAME\s*:\s*[^\n]*\bSOURCE\b", text, re.I):
        raise RuntimeError("source electrode not reported")
    if not re.search(r"\bNAME\s*:\s*[^\n]*\bDRAIN\b", text, re.I):
        raise RuntimeError("drain electrode not reported")
    if not re.search(r"\bNAME\s*:\s*[^\n]*\bGATE\b", text, re.I):
        raise RuntimeError("gate electrode not reported")
    if re.search(r"gate_fp", text, re.I):
        raise RuntimeError("unexpected gate_fp electrode")


def run(args: argparse.Namespace) -> int:
    deck = Path(args.deck).resolve()
    transcript = Path(args.transcript).resolve()
    status = Path(args.status).resolve()
    stages = read_deck(deck)
    transcript.parent.mkdir(parents=True, exist_ok=True)

    # Freeze the exact command contract before launching the single process.
    if stages["MAPPING"] != [
        'material regions="MATERIAL:GA2O3" value="GaN"',
        'material regions="MATERIAL:NIO" value="ZnO"',
    ]:
        raise RuntimeError("mapping stage is not the approved two-command mapping")
    if stages["SAVE"] != [
        'save out="VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str" mode=atlas'
    ]:
        raise RuntimeError("save stage is not the approved one-time ATLAS-mode save")

    session: VictorySession | None = None
    try:
        session = VictorySession(transcript, args.timeout)
        session.start()

        pre_outputs: dict[str, str] = {}
        for command in stages["PREMAP"]:
            text = output_text(session.command(command))
            pre_outputs[command] = text
        validate_material_info(
            "MATERIAL:GA2O3", pre_outputs['info regions="MATERIAL:GA2O3"']
        )
        validate_material_info(
            "MATERIAL:NIO", pre_outputs['info regions="MATERIAL:NIO"']
        )
        validate_electrodes(pre_outputs['info regions="TYPE:ELECTRODE"'])

        for command in stages["MAPPING"]:
            reject_errors(output_text(session.command(command)), command)

        post_outputs: dict[str, str] = {}
        for command in stages["POSTMAP"]:
            text = output_text(session.command(command))
            post_outputs[command] = text
        for selector in (
            "MATERIAL:GAN",
            "MATERIAL:ZNO",
            "MATERIAL:SIO2",
            "MATERIAL:AL2O3",
            "MATERIAL:NICKEL",
        ):
            validate_material_info(
                selector, post_outputs[f'info regions="{selector}"']
            )
        validate_electrodes(post_outputs['info regions="TYPE:ELECTRODE"'])

        for command in stages["SAVE"]:
            reject_errors(output_text(session.command(command)), command)
        output_path = Path(
            "VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str"
        )
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise RuntimeError("approved output STR was not created")

        return_code = session.quit()
        if return_code != 0:
            raise RuntimeError(f"Victory Mesh quit with code {return_code}")
        status.write_text(
            "STATUS=RESAVE_COMPLETE\n"
            "EXECUTION_COUNT=1\n"
            "PREMAP_GA2O3_SELECTOR_COUNT=5\n"
            "PREMAP_NIO_SELECTOR_COUNT=2\n"
            "SAVE_COUNT=1\n"
            "ATLAS_EXECUTED=NO\n"
            "SOLVE_EXECUTED=NO\n",
            encoding="utf-8",
        )
        return 0
    except Exception as exc:
        if session is not None:
            session.log.write(f"\nCONTROLLER_HARD_STOP: {exc}\n".encode())
            session.log.flush()
            session.stop_without_retry()
        status.write_text(
            "STATUS=HARD_STOP\n"
            "EXECUTION_COUNT=1\n"
            f"REASON={exc}\n"
            "SECOND_LAUNCH=NO\n"
            "AUTO_FALLBACK=NO\n",
            encoding="utf-8",
        )
        return 2
    finally:
        if session is not None:
            session.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deck", required=True)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--timeout", type=float, default=90.0)
    return run(parser.parse_args())


if __name__ == "__main__":
    sys.exit(main())
