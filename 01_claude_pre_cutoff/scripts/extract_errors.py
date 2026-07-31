#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
extract_errors.py -- 成长型错误日志提取器。

目标：用户不必再整段回传日志。本脚本扫描本地或远端的 ATLAS 运行产物
（typescript / *.out / run_all.out），按指纹归类错误，并把「哪个错、在哪个 deck、
何时、出现几次、已知解法是什么」累积进一个**长期成长的错误数据库**：

    knowledge/errors_db.json        机器可读（计数/首末见/案例路径）
    knowledge/ERRORS_错误知识库.md   人类可读（按频次排序 + 已知解法 + 待研究）

新错误第一次出现 → 记为 UNKNOWN，提示按 D:\\knowledge 四库检索并把解法回填
（回填= 编辑本文件 KNOWN_FIXES 或直接改 md 的解法栏，两处都认）。

用法
  python extract_errors.py scan <文件或目录>...        # 本地扫描
  python extract_errors.py scan-remote <远端目录>      # SSH 拉取 typescript/*.out 后扫描
  python extract_errors.py top                        # 看累计榜
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\SILVACO_LOCAL")
DB = ROOT / "knowledge" / "errors_db.json"
MD = ROOT / "knowledge" / "ERRORS_错误知识库.md"

# ---------------------------------------------------------------------------
# 错误指纹：正则 -> (类别, 简称)。顺序即优先级，先匹配先归类。
# 新遇到的错误若都不匹配，落入 UNKNOWN- 桶（截取首行做临时指纹）。
# ---------------------------------------------------------------------------
FINGERPRINTS: list[tuple[str, str, str]] = [
    # -- 牛顿/收敛族（用户点名的大头）--
    (r"Convergence problem.*Taking smaller bias", "newton", "偏压折半（DC 爬压不收敛）"),
    (r"Updated temperatures exceeding limits", "newton", "晶格温度越限（撞 min.temp/max.temp 钳位）"),
    (r"Step-size is too small", "newton", "步长缩到下限（瞬态/爬压死亡螺旋）"),
    (r"solution did not converge|NO CONVERGENCE", "newton", "整步不收敛"),
    (r"time step too small|dt.*below.*minimum", "newton", "时间步小于 dt.min"),
    # -- 语法/参数族 --
    (r"Invalid parameter specification.*==>\s*(\w+)", "syntax", "无效参数（捕获组=参数名）"),
    (r"ERROR #\s*\d+", "syntax", "ATLAS 编号错误（看上下文行）"),
    (r"Unknown (statement|parameter|keyword)", "syntax", "未知语句/关键字"),
    (r"Command Error: invalid expr", "syntax", "VictoryExtract 变量名不匹配 log 注册表"),
    (r"Unknown command", "syntax", "VE 不存在的命令（cutline/profile/slice 系——正解 extract.profile）"),
    (r"no impurity specified", "syntax", "经典 extract 解析器语法错（extract name= 混用 VE 写法）"),
    # -- 网格/结构族 --
    (r"No region defined for element", "mesh", "网格元素无归属 region（电极≠region 坑）"),
    (r"Electrode shortened", "mesh", "电极被裁剪（坐标与网格线不齐）"),
    (r"mesh.*too (coarse|fine)|node limit", "mesh", "网格规模问题"),
    # -- 材料族 --
    (r"No default material specified for user material", "material", "user material 静默退化（G 记录丢失指纹）"),
    # -- 许可证/环境族 --
    (r"license|LICENSE|SFLM", "env", "许可证问题（先查 SFLM_SERVERS 与 sflm 进程）"),
    (r"cannot open display|Could not connect to display", "env", "X display 不可达（XAUTHORITY 坑）"),
    (r"simulator exits with code [1-9]", "env", "非零退出（综合症状，看前文定因）"),
]

# 已知解法：类别/简称 -> 解法与出处。随经验增长手工/agent 回填。
KNOWN_FIXES: dict[str, str] = {
    "偏压折半（DC 爬压不收敛）":
        "若伴随温度越限：DC 段去掉 lat.temp、瞬态前重开（E1 实验：672 折半→0）。"
        "否则减 vstep、检查是否 VGS 未加（导通态推高压）。出处 docs/仿真痛点 C1/C2。",
    "晶格温度越限（撞 min.temp/max.temp 钳位）":
        "120K=min.temp 默认钳位不是解；同上 E1 方案；热边界欠定也会触发（knowledge/16）。",
    "无效参数（捕获组=参数名）":
        "参数不存在。先查远端 atlas.key（grep -n '<参数>'）；已知冤案：tstart。"
        "禁止凭印象写参数（docs/仿真痛点 A7）。",
    "网格元素无归属 region（电极≠region 坑）":
        "ATLAS 原生 electrode 是边界条件不是 region，金属头网格带必须被介质 region 覆盖"
        "（decks/README 铁则 2）。",
    "user material 静默退化（G 记录丢失指纹）":
        "grep -a '^G [0-9]' 结构文件自检；兜底按 region 号绑定材料（knowledge/00 §更正框）。",
    "X display 不可达（XAUTHORITY 坑）":
        "注入 mate-session 会话环境（silvaco_remote.SESSION_ENV_PRELUDE）。",
    "许可证问题（先查 SFLM_SERVERS 与 sflm 进程）":
        "export SFLM_SERVERS=+localhost；pgrep -f sflm 确认守护在。",
    "VictoryExtract 变量名不匹配 log 注册表":
        "瞬态时间轴合法名是 \"transient time\" 不是 \"time\"；探针按 log 头 o 记录的注册名"
        "（如 Tmax）。判据=head -60 <log> 看 o/f 记录。SMOKE n7/n8 实测修复 2026-07-27。",
    "经典 extract 解析器语法错（extract name= 混用 VE 写法）":
        "extract name= 走另一套经典解析器，不接受 VE 的 curve(\"x\",\"y\") 引号写法；"
        "峰值标量改由 Python 从 extract.csv 产物计算。正确经典写法待研究。",
}

CONTEXT_LINES = 3


def load_db() -> dict:
    if DB.exists():
        return json.loads(DB.read_text(encoding="utf-8"))
    return {"entries": {}}


def save_db(db: dict) -> None:
    DB.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")
    render_md(db)


def classify(line: str) -> tuple[str, str] | None:
    for pat, cat, name in FINGERPRINTS:
        if re.search(pat, line):
            return cat, name
    return None


def scan_file(db: dict, path: Path, label: str = "") -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0
    lines = text.replace("\r", "").splitlines()
    hits = 0
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    seen_unknown_err = False
    for i, ln in enumerate(lines):
        res = classify(ln)
        if res is None:
            # UNKNOWN 桶：只抓带 ERROR/FATAL 字样但没被指纹覆盖的
            if re.search(r"\bFATAL\b|\*\* ERROR", ln) and not seen_unknown_err:
                res = ("unknown", "UNKNOWN-" + ln.strip()[:60])
                seen_unknown_err = True
            else:
                continue
        cat, name = res
        key = f"{cat}::{name}"
        e = db["entries"].setdefault(key, {
            "category": cat, "name": name, "count": 0,
            "first_seen": now, "last_seen": now, "cases": []})
        e["count"] += 1
        e["last_seen"] = now
        ctx = "\n".join(lines[max(0, i - CONTEXT_LINES): i + CONTEXT_LINES + 1])[-500:]
        case = {"file": str(path), "label": label, "when": now, "context": ctx}
        e["cases"] = (e["cases"] + [case])[-5:]        # 每类只留最近 5 例
        hits += 1
    return hits


def render_md(db: dict) -> None:
    rows = sorted(db["entries"].values(), key=lambda e: -e["count"])
    out = ["# 错误知识库（extract_errors.py 自动生成+人工回填解法）",
           f"更新: {_dt.datetime.now():%Y-%m-%d %H:%M}　累计错误类型: {len(rows)}",
           "",
           "| 次数 | 类别 | 错误 | 已知解法 | 首见 | 末见 |",
           "|---|---|---|---|---|---|"]
    for e in rows:
        fix = KNOWN_FIXES.get(e["name"], "**⚠ 待研究**（按 knowledge/00 检索顺序查四库后回填）")
        out.append(f"| {e['count']} | {e['category']} | {e['name']} | {fix} "
                   f"| {e['first_seen']} | {e['last_seen']} |")
    out += ["", "## 最近案例（每类保留 5 条，含上下文）", ""]
    for e in rows:
        if not e["cases"]:
            continue
        out.append(f"### {e['name']}")
        for c in e["cases"][-2:]:
            out.append(f"- `{c['file']}` @{c['when']}")
            out.append("```\n" + c["context"] + "\n```")
    MD.write_text("\n".join(out) + "\n", encoding="utf-8")


def cmd_scan(paths: list[str]) -> int:
    db = load_db()
    total = 0
    for raw in paths:
        p = Path(raw)
        files = [p] if p.is_file() else list(p.rglob("typescript")) + \
            list(p.rglob("*.out")) + list(p.rglob("run_all.out"))
        for f in files:
            n = scan_file(db, f)
            if n:
                print(f"[scan] {f}  +{n}")
                total += n
    save_db(db)
    print(f"\n共 {total} 条命中 → {MD}")
    return 0


def cmd_scan_remote(remote_dir: str) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from silvaco_remote import Remote
    rem = Remote(); rem.resolve()
    tmp = ROOT / "outputs" / "reports" / "_remote_logs"
    tmp.mkdir(parents=True, exist_ok=True)
    listing = rem.sh(f"find {remote_dir} -maxdepth 3 \\( -name typescript -o -name '*.out' \\) "
                     f"-size -30M 2>/dev/null | head -40", timeout=60).stdout.split()
    for rp in listing:
        local = tmp / rp.strip("/").replace("/", "__")
        if rem.pull(rp, local):
            print(f"[pull] {rp}")
    return cmd_scan([str(tmp)])


def cmd_top() -> int:
    db = load_db()
    for e in sorted(db["entries"].values(), key=lambda x: -x["count"])[:15]:
        fix = "✓有解法" if e["name"] in KNOWN_FIXES else "⚠待研究"
        print(f"{e['count']:>5}  [{e['category']:<8}] {fix}  {e['name']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan"); s.add_argument("paths", nargs="+")
    r = sub.add_parser("scan-remote"); r.add_argument("remote_dir")
    sub.add_parser("top")
    a = ap.parse_args()
    if a.cmd == "scan":
        return cmd_scan(a.paths)
    if a.cmd == "scan-remote":
        return cmd_scan_remote(a.remote_dir)
    return cmd_top()


if __name__ == "__main__":
    sys.exit(main())
