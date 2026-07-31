#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
preflight_all.py -- 全框架烟测执行器（PREFLIGHT.md 的自动化半边）。

分级：
  L0 本地静态（无网可跑）：布局/ git / python 依赖 / 各脚本自检
  L1 远端连通：VM 探测 + 工具链 + license + tmux 驱动
  L2 GUI：X 会话 + 截图回传（VDoE 窗口/xctl 检查已随账本 B12 摘除）
  L3 全链路（--full）：微型 VE 提取实跑（秒级）；完整 S1-S11 见 GUI 技能包烟测

用法：python scripts\\preflight_all.py [--level 2] [--full]
退出码 0=所选级别全绿；1=有 FAIL。任何 agent 改架构前必须全绿（账本 A13）。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\SILVACO_LOCAL")
SSHK = "C:/Users/Administrator/.ssh/silvaco_ed25519"
IPS = ["192.168.107.128", "192.168.50.134"]

RESULTS: list[tuple[str, str, str]] = []   # (级, 名, PASS/FAIL/SKIP + 摘要)


def run(cmd, timeout=90, cwd=None, input_=None):
    return subprocess.run(cmd, capture_output=True, timeout=timeout,
                          cwd=cwd or ROOT, input=input_)


def check(level: str, name: str):
    def deco(fn):
        def wrapper(do: bool):
            if not do:
                RESULTS.append((level, name, "SKIP"))
                return
            try:
                ok, detail = fn()
            except Exception as e:
                ok, detail = False, f"异常: {e}"
            RESULTS.append((level, name, ("PASS " if ok else "FAIL ") + detail[:80]))
        return wrapper
    return deco


# ---------------- L0 本地静态 ----------------
@check("L0", "布局合规 check_layout")
def c_layout():
    r = run([sys.executable, "scripts/check_layout.py"])
    out = r.stdout.decode("utf-8", "replace")
    return "完全合规" in out, out.strip().splitlines()[-1]


@check("L0", "git 仓库与提交人")
def c_git():
    r = run(["git", "log", "-1", "--format=%an %h %s"])
    line = r.stdout.decode("utf-8", "replace").strip()
    return r.returncode == 0 and "silvaco-agent" in line, line[:70]


@check("L0", "python 依赖 numpy/pandas/mpl/pptx")
def c_deps():
    r = run([sys.executable, "-c",
             "import numpy,pandas,matplotlib,pptx;print('ok')"])
    return b"ok" in r.stdout, r.stderr.decode()[:60] or "全部可导入"


@check("L0", "w1_judge 五子命令自检")
def c_judge():
    r = run([sys.executable, "scripts/w1_judge.py", "--help"])
    ok = all(k in r.stdout.decode() for k in
             ("exitcode", "halvings", "extract", "profile", "vth"))
    return ok, "5 子命令在位" if ok else "子命令缺失"


@check("L0", "extract_errors 指纹库")
def c_errdb():
    r = run([sys.executable, "scripts/extract_errors.py", "top"])
    return r.returncode == 0, f"{len(r.stdout.decode().splitlines())} 行榜单"


@check("L0", "make_report_pptx 生成器")
def c_pptx():
    fixture = ROOT / "outputs" / "reports" / "_gen_selftest_outline.md"
    if not fixture.exists():
        return False, "自测 outline 缺失"
    r = run([sys.executable, "scripts/make_report_pptx.py", str(fixture),
             "-o", str(ROOT / "outputs" / "reports" / "_preflight_gen.pptx")])
    return b"[pptx]" in r.stdout, "3 页生成"


@check("L0", "关键文档在位（账本/计划书/AGENTS/README）")
def c_docs():
    need = ["AGENTS.md", "README.md", "PREFLIGHT.md",
            "knowledge/CONSTRAINTS_用户约束账本.md",
            "knowledge/00_PATH_MAP.md",
            "docs/AGENT_运行日志_与复现手册.md"]
    miss = [n for n in need if not (ROOT / n).exists()]
    return not miss, "全在" if not miss else f"缺 {miss}"


@check("L0", "四库知识库可达")
def c_kb():
    kb = Path(r"D:\knowledge")
    need = ["material_sil", "pdf25", "exp25", "paper"]
    miss = [n for n in need if not (kb / n).exists()]
    return not miss, "四库全在" if not miss else f"缺 {miss}"


# ---------------- L1 远端连通 ----------------
_HOST: list[str] = []


@check("L1", "VM 双 IP 探测")
def c_vm():
    for ip in IPS:
        r = run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
                 "-o", "StrictHostKeyChecking=accept-new", "-o", "LogLevel=ERROR",
                 "-i", SSHK, f"root@{ip}", "echo UP"], timeout=20)
        if b"UP" in r.stdout:
            _HOST.append(ip)
            return True, f"在线 {ip}"
    return False, "双 IP 均拒连（VM 关机？）"


def _ssh(script: str, timeout=60):
    if not _HOST:
        raise RuntimeError("无在线主机")
    return run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                "-o", "LogLevel=ERROR", "-i", SSHK, f"root@{_HOST[0]}",
                "bash -l -s"], timeout=timeout,
               input_=script.replace("\r\n", "\n").encode())


@check("L1", "silvaco 工具链+license+磁盘")
def c_tools():
    r = _ssh("export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH\n"
             "for t in deckbuild atlas victoryvisual victoryextract tonyplot; do "
             "command -v $t >/dev/null || echo MISS:$t; done\n"
             "pgrep -f sflm_monitord >/dev/null || echo MISS:sflm\n"
             "df -h / | awk 'NR==2{print $4}'")
    out = r.stdout.decode("utf-8", "replace")
    return "MISS" not in out, ("剩余 " + out.strip().splitlines()[-1]) if out.strip() else "?"


@check("L1", "tmux 驱动 vdoe_tmux.sh")
def c_tmux():
    r = _ssh("/root/bin/vdoe_tmux.sh status 2>&1 | head -2")
    return b"tmux" in r.stdout, r.stdout.decode("utf-8", "replace").strip()[:50]


@check("L1", "远端目录架构（postproc/README）")
def c_remote_layout():
    r = _ssh("ls /root/DECKBUILD/README.txt /root/DECKBUILD/postproc "
             "/root/DECKBUILD/_lab >/dev/null 2>&1 && echo OK")
    return b"OK" in r.stdout, "runs/postproc/_lab 在位"


@check("L1", "僵尸嫌疑扫描")
def c_zombie_scan():
    r = _ssh(
        "set -o pipefail\n"
        "ps -eo pid= -o ppid= -o etimes= -o pcpu= -o comm= | "
        "while read pid ppid etimes pcpu comm; do "
        "cwd=$(readlink -f /proc/$pid/cwd 2>/dev/null || true); "
        "printf 'PROC\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "
        "\"$pid\" \"$ppid\" \"$etimes\" \"$pcpu\" \"$comm\" \"$cwd\"; "
        "done"
    )
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip()
        return False, f"远端进程扫描失败 rc={r.returncode}: {err[:100]}"
    rows = {}
    children = {}
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split("\t", 6)
        if len(parts) != 7 or parts[0] != "PROC":
            continue
        _, pid, ppid, etimes, pcpu, comm, cwd = parts
        try:
            row = {
                "pid": int(pid), "ppid": int(ppid), "etimes": int(etimes),
                "pcpu": float(pcpu), "comm": comm, "cwd": cwd or "?",
            }
        except ValueError:
            continue
        rows[row["pid"]] = row
        children.setdefault(row["ppid"], []).append(row["pid"])
    if not rows:
        return False, "远端进程扫描返回零条 PROC，拒绝假绿"

    def has_active_atlas_descendant(pid: int) -> bool:
        stack = list(children.get(pid, []))
        while stack:
            child_pid = stack.pop()
            child = rows.get(child_pid)
            if child is None:
                continue
            if child["comm"].startswith("atlas.exe") and child["pcpu"] >= 1.0:
                return True
            stack.extend(children.get(child_pid, []))
        return False

    suspects = []
    for row in rows.values():
        is_solver = (row["comm"].startswith("dbascii.exe") or
                     row["comm"].startswith("atlas.exe"))
        if not is_solver or row["etimes"] <= 7200 or row["pcpu"] >= 1.0:
            continue
        # dbascii 是 runner 包裹层；只要其后代 ATLAS 仍有累计 CPU，就不是孤立僵尸。
        if row["comm"].startswith("dbascii.exe") and \
                has_active_atlas_descendant(row["pid"]):
            continue
        suspects.append(row)

    if suspects:
        for row in suspects:
            hours, rem = divmod(row["etimes"], 3600)
            minutes, seconds = divmod(rem, 60)
            print(
                f"  SUSPECT pid={row['pid']} etime={hours:02d}:{minutes:02d}:{seconds:02d} "
                f"pcpu={row['pcpu']:.1f}% cwd={row['cwd']}"
            )
        return False, (
            f"{len(suspects)} 个嫌疑；报告用户裁决，禁自行 kill（豁免令）"
        )
    return True, "零嫌疑（>2h、累计 CPU<1%、且无活跃 ATLAS 后代）"


# ---------------- L2 GUI ----------------
@check("L2", "X 会话环境注入")
def c_xenv():
    r = _ssh('SESSPID=$(pgrep -f mate-session | head -1)\n'
             '[ -n "$SESSPID" ] || { echo NOSESS; exit 0; }\n'
             'export DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/xauthority\n'
             'xdpyinfo >/dev/null 2>&1 && echo XOK')
    return b"XOK" in r.stdout, "DISPLAY=:0 可认证"


# （原 c_vdoe_win / c_xctl 两项已随账本 B12 产线收束令于 2026-07-27 摘除：
#   VDoE 窗口检查会主动把已弃用的 victorydoe 拉起来等 18 秒，xctl 是 GUI 自动化专用；
#   可见性职能改由 c_xenv + c_shot 承担。详见 docs\废案登记_20260727.md）


@check("L2", "截图回传")
def c_shot():
    r = run([sys.executable, "scripts/screenshot_watch.py",
             "--session", "_preflight", "--once", "--label", "pf"], timeout=150)
    return b"[shot]" in r.stdout, "outputs\\_preflight\\screenshots\\"


# ---------------- L3 全链路（--full）----------------
@check("L3", "VE 微提取实跑（str→csv，走正规 runner）")
def c_ve():
    # 教训链（2026-07-27 三连实测）：手搓 pty 的三种姿势全是坑——
    #  ① script 放 stdin 中段 → 吞后续行；② 挂 </dev/null → deckbuild 空转；
    #  ③ script 放 stdin 末行 → stdin 已 EOF，deckbuild 同样立退。
    # 正解 = 吃狗粮：走项目正规 runner（silvaco_remote 的 xterm 通道，久经实战）。
    _ssh("rm -f /root/DECKBUILD/_lab/preflight/pf.csv", timeout=30)
    # 注意：runner 对相对路径会自动加 decks\ 前缀——只传文件名（曾因传 decks/xx 双拼致 rc=2）
    r = run([sys.executable, "scripts/silvaco_remote.py", "run",
             "_preflight_ve.in",
             "--workdir", "/root/DECKBUILD/_lab/preflight",
             "--wait", "--timeout", "240"], timeout=300)
    r2 = _ssh("cd /root/DECKBUILD/_lab/preflight && "
              "test -s pf.csv && echo VEOK $(wc -l < pf.csv)", timeout=40)
    out = r2.stdout.decode("utf-8", "replace")
    if "VEOK" in out:
        return True, out.strip().splitlines()[-1]
    tail = (r.stdout or r.stderr).decode("utf-8", "replace").strip().splitlines()
    return False, "无产物; runner: " + (tail[-1] if tail else "无输出")


@check("L3", "SWEEP 产线三件套（B12 主产线证据）")
def c_sweep():
    import os
    need = ["decks/sweep_bv_main.in", "decks/sweep_bv_aux.in",
            "outputs/reports/sweep_bv_summary.csv"]
    missing = [p for p in need if not os.path.exists(p)]
    return (not missing), ("在位" if not missing else "缺: " + ", ".join(missing))


CHECKS = {
    0: [c_layout, c_git, c_deps, c_judge, c_errdb, c_pptx, c_docs, c_kb],
    1: [c_vm, c_tools, c_tmux, c_remote_layout, c_zombie_scan],
    2: [c_xenv, c_shot],
    3: [c_ve, c_sweep],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, default=2, choices=[0, 1, 2, 3])
    ap.add_argument("--full", action="store_true", help="等价 --level 3")
    a = ap.parse_args()
    top = 3 if a.full else a.level
    for lv in range(0, 4):
        do = lv <= top
        for fn in CHECKS[lv]:
            fn(do)
            if do and RESULTS and RESULTS[-1][2].startswith("FAIL") and lv >= 1 and fn is c_vm:
                top = 0    # VM 不通则跳过后续远端项
    print(f"\n{'级':<4}{'检查项':<34}结果")
    print("-" * 72)
    fails = 0
    for lv, name, res in RESULTS:
        print(f"{lv:<4}{name:<34}{res}")
        if res.startswith("FAIL"):
            fails += 1
    print("-" * 72)
    verdict = "✓ 全绿——架构可信，允许在其上工作/修改" if fails == 0 else \
              f"✗ {fails} 项 FAIL——按 PREFLIGHT.md 对应条目修复，修复前禁止改架构"
    print(verdict)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
