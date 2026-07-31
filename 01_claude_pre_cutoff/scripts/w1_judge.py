#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
w1_judge.py -- W1 冻结计划书的机检判据仲裁器（供框架外执行者 Grok 无脑照抄）。

设计原则（R1 评审乙 异议2 的收口件）：
  * 每个子命令最后一行恰好打印一行裁决，以 PASS / FAIL / STOP / INFO 开头。
  * 执行者只看最后一行；出现 STOP 一律按计划书 §6 停手报告。
  * 真判据来源：typescript 的 "simulator exits with code"，或 runner 未写该行时
    ATLAS "finished" + 零 "ERROR #" 的兼容双门（废案登记 §四.1）、
    折半指纹 "Taking smaller bias"（extract_errors.py 同款指纹）、
    deck 内 extract name= 标量、EXTRACT.PROFILE csv。

用法（均在 D:\SILVACO_LOCAL 下执行）：
  python scripts\w1_judge.py exitcode  <typescript路径>
  python scripts\w1_judge.py halvings  <typescript路径> [--max 5]
  python scripts\w1_judge.py extract   <typescript路径> <标量名> [--max 1e-9]
                                       [--ref 3.1e-6 --reltol 0.01]
  python scripts\w1_judge.py profile   <csv路径> [--tail-um 0.5]
  python scripts\w1_judge.py vth       <typescript路径> --wf 5.23
                                       [--target 1.2 --tol 0.1]
                                       [--id-ref 1.3e-5 --id-tol 0.30]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WF_MIN, WF_MAX = 5.0, 5.65  # 高功函数金属物理窗（越界 = STOP，计划书 §6-5）


def read_text(p: str) -> str:
    f = Path(p)
    if not f.exists():
        print(f"STOP FILE_NOT_FOUND {p}")
        sys.exit(2)
    return f.read_text(encoding="utf-8", errors="ignore")


def find_scalar(text: str, name: str):
    """extract name=... 的结果行形如  NAME=value ；取最后一次出现。"""
    hits = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not hits:
        return None
    try:
        return float(hits[-1])
    except ValueError:
        return None


def cmd_exitcode(a):
    t = read_text(a.file)
    codes = re.findall(r"simulator exits with code\s+(\d+)", t)
    errors = re.findall(r"^.*ERROR\s+#.*$", t, flags=re.MULTILINE)
    atlas_finished = bool(re.search(r"ATLAS[^\r\n]*\bfinished\b", t))
    print(f"exit codes found: {codes}")
    print(f"ATLAS finished: {atlas_finished}; ERROR # count: {len(errors)}")
    for line in errors[:5]:
        print(f"  ERR: {line.strip()[:160]}")
    if errors or any(c != "0" for c in codes):
        print(f"FAIL exit codes={codes} errors={len(errors)}")
        return 1
    if codes:
        print(f"PASS all {len(codes)} simulator exit(s) == 0, no 'ERROR #'")
        return 0
    if atlas_finished:
        print("PASS ATLAS finished, no 'ERROR #' (runner supplied no simulator exit line)")
        return 0
    print("STOP NO_EXIT_LINE (no simulator exit line and no ATLAS finished marker)")
    return 1


def cmd_halvings(a):
    t = read_text(a.file)
    n = len(re.findall(r"Taking smaller bias", t))
    if n <= a.max:
        print(f"PASS halvings={n} (<= {a.max})")
        return 0
    print(f"FAIL halvings={n} (> {a.max}) -- E1 not effective on this deck, stop and report")
    return 1


def cmd_extract(a):
    t = read_text(a.file)
    v = find_scalar(t, a.name)
    if v is None:
        print(f"STOP NOT_FOUND {a.name} (also check results.final in the remote workdir)")
        return 2
    print(f"{a.name}={v:.6e}")
    if a.max is not None:
        if abs(v) <= a.max:
            print(f"PASS |{a.name}|={abs(v):.3e} <= {a.max:.3e}")
            return 0
        print(f"FAIL |{a.name}|={abs(v):.3e} > {a.max:.3e}")
        return 1
    if a.ref is not None:
        rel = abs(v - a.ref) / max(abs(a.ref), 1e-300)
        if rel <= a.reltol:
            print(f"PASS rel.diff={rel:.3%} <= {a.reltol:.1%} (ref {a.ref:.3e})")
            return 0
        print(f"FAIL rel.diff={rel:.3%} > {a.reltol:.1%} (ref {a.ref:.3e})")
        return 1
    print(f"INFO recorded {a.name}={v:.6e}")
    return 0


def cmd_profile(a):
    """EXTRACT.PROFILE csv：第一列=深度，含 'lectron' 的列=电子浓度。
    评判窗口 = 剖面最深 tail_um（衬底段）。
    OPEN    = 窗内最大 n >= 1e14（衬底未耗尽，旁路敞开）
    PINCHED = 窗内最大 n <= 1e8 （knowledge\\50 (5) 判据带）
    AMBIG   = 介于其间 -> 停手交审核方。"""
    rows = []
    header = None
    for line in read_text(a.file).splitlines():
        parts = [p.strip() for p in re.split(r"[,\t]", line) if p.strip()]
        if not parts:
            continue
        try:
            rows.append([float(x) for x in parts])
        except ValueError:
            if header is None:
                header = parts
    if not rows or len(rows[0]) < 2:
        print("STOP CSV_UNREADABLE (no numeric rows with >=2 columns)")
        return 2
    ci = 1
    if header:
        for i, h in enumerate(header):
            if "lectron" in h:
                ci = i
                break
    depth = [r[0] for r in rows]
    dmax = max(depth)
    tail = [r[ci] for r in rows if r[0] >= dmax - a.tail_um and len(r) > ci]
    if not tail:
        print("STOP EMPTY_TAIL_WINDOW")
        return 2
    nmax = max(tail)
    verdict = "OPEN" if nmax >= 1e14 else ("PINCHED" if nmax <= 1e8 else "AMBIG")
    print(f"depth range: {min(depth):.3f}..{dmax:.3f} um; tail window {a.tail_um} um; "
          f"nmax_tail={nmax:.3e} cm-3")
    print(f"INFO verdict={verdict}")
    return 0


def cmd_vth(a):
    t = read_text(a.file)
    vth = find_scalar(t, "VTH_V")
    id10 = find_scalar(t, "Id_vg10_Aum")
    if vth is None:
        print("STOP NOT_FOUND VTH_V (first run of the wang deck may have failed on "
              "syntax -- per plan, do NOT edit syntax; archive the error and report)")
        return 2
    print(f"VTH_V={vth:.4f}  Id_vg10_Aum={'%.4e' % id10 if id10 is not None else 'NOT_FOUND'}")
    if abs(vth - a.target) <= a.tol:
        if id10 is None:
            print("STOP VTH_OK_BUT_ID_MISSING")
            return 2
        rel = abs(abs(id10) - a.id_ref) / a.id_ref
        if rel <= a.id_tol:
            print(f"PASS VTH={vth:.3f} in {a.target}+/-{a.tol}; Id consistency {rel:.1%} <= {a.id_tol:.0%}")
            return 0
        print(f"STOP CONSISTENCY_FAIL VTH ok but Id off by {rel:.1%} (> {a.id_tol:.0%}) -- report")
        return 2
    nxt = round(a.wf + (a.target - vth), 3)
    if nxt < WF_MIN or nxt > WF_MAX:
        print(f"STOP WF_WINDOW next wf {nxt} outside [{WF_MIN},{WF_MAX}] eV -- report")
        return 2
    print(f"FAIL VTH={vth:.3f} not in {a.target}+/-{a.tol}; NEXT_WF={nxt} "
          f"(edit 'set gate_wf' line to this value, log it, rerun; max 5 rounds)")
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="W1 mechanical judge")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("exitcode"); p.add_argument("file"); p.set_defaults(fn=cmd_exitcode)

    p = sub.add_parser("halvings"); p.add_argument("file")
    p.add_argument("--max", type=int, default=5); p.set_defaults(fn=cmd_halvings)

    p = sub.add_parser("extract"); p.add_argument("file"); p.add_argument("name")
    p.add_argument("--max", type=float, default=None)
    p.add_argument("--ref", type=float, default=None)
    p.add_argument("--reltol", type=float, default=0.01)
    p.set_defaults(fn=cmd_extract)

    p = sub.add_parser("profile"); p.add_argument("file")
    p.add_argument("--tail-um", dest="tail_um", type=float, default=0.5)
    p.set_defaults(fn=cmd_profile)

    p = sub.add_parser("vth"); p.add_argument("file")
    p.add_argument("--wf", type=float, required=True)
    p.add_argument("--target", type=float, default=1.2)
    p.add_argument("--tol", type=float, default=0.1)
    p.add_argument("--id-ref", dest="id_ref", type=float, default=1.3e-5)
    p.add_argument("--id-tol", dest="id_tol", type=float, default=0.30)
    p.set_defaults(fn=cmd_vth)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
