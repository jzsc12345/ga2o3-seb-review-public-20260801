#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_layout.py -- 主控端布局合规检查（烟测 S0 / 日常巡检）。

规则来源：用户 2026-07-26 指令 ——
  * skills\\ 为冻结区，只允许 .md/.py/.sh/.json；
  * 各目录只放约定类型，杂物进 archive\\；
  * 大体积 .str/.log 不得出现在主控端任何位置。

退出码：0 = 合规；1 = 有违规（逐条列出）。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\SILVACO_LOCAL")

# 目录 -> 允许的扩展名（小写，含点）。None = 不检查（自由区）。
POLICY: dict[str, set[str] | None] = {
    "scripts":   {".py", ".md", ".sh"},        # .sh = 部署到 VM 的远端脚本（scripts\remote\）
    "decks":     {".in", ".sdb", ".csv", ".md", ".c"},
    "knowledge": {".md", ".json"},             # .json = errors_db 等机器可读伴生库
    "docs":      {".md"},
    "skills":    {".md", ".py", ".sh", ".json"},
    "outputs":   {".png", ".csv", ".md", ".log", ".err", ".json", ".gz", ".txt",
                  ".pptx", ".html"},   # 汇报产物（report-writer 体裁 A/B）落 outputs\reports\
    "inbox":     None,      # 投递区不限
    "archive":   None,      # 收容区不限
    "silvaco":   None,      # 历史区不检查
    "claude-sentaurus-skill-main": None,  # 源包原样保留
    ".claude":   None,
    ".codex":    None,
}

# 根层允许的散文件
ROOT_ALLOWED = {"README.md", "AGENTS.md", "INSTALL.md", "PREFLIGHT.md",
                ".gitignore", "SEB.in", "mySEU.c"}

# 主控端全域禁止的大文件类型（应归档 E:\silvaco2425\bulk\）
FORBIDDEN_EVERYWHERE = {".str", ".tdr", ".vmdk", ".vmem"}
SIZE_LIMIT_MB = 50  # 单文件超过即警告（截图/CSV 不应这么大）


def main() -> int:
    violations: list[str] = []
    warnings: list[str] = []

    # 1. 根层散文件
    for p in ROOT.iterdir():
        if p.is_file() and p.name not in ROOT_ALLOWED:
            violations.append(f"根目录散文件: {p.name}  → 归位或移 archive\\")

    # 豁免子树：离线包打包工位（.in/.sh/manifest 是其设计产物）与 Python 缓存
    EXEMPT_PARTS = {"__pycache__", "offline", "offline_runs", "_remote_logs",
                    "ref_GaN_Power_ex01",   # 官方三层产线参考包（.set/.dat/.png 原样保存）
                    "ref_examples_aux_set"} # 例子库 aux/set/SWEEP 语料（642 文件收割包）

    # 2. 各目录扩展名策略
    for sub, allowed in POLICY.items():
        d = ROOT / sub
        if not d.exists() or allowed is None:
            continue
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            if EXEMPT_PARTS & set(p.parts):
                continue
            ext = p.suffix.lower()
            if ext in FORBIDDEN_EVERYWHERE:
                violations.append(f"禁类文件: {p.relative_to(ROOT)}  → E:\\silvaco2425\\bulk\\")
            elif ext not in allowed:
                violations.append(f"越界类型: {p.relative_to(ROOT)} ({ext or '无扩展名'}) "
                                  f"→ {sub}\\ 只允许 {sorted(allowed)}")
            if p.stat().st_size > SIZE_LIMIT_MB * 1024 * 1024:
                warnings.append(f"超大文件({p.stat().st_size/1e6:.0f}MB): {p.relative_to(ROOT)}")

    # 3. skills 冻结区必备件
    for pkg in ("silvaco-tcad",):  # victorydoe-gui-flow 已按账本 B12 归档删除(2026-07-27)
        if not (ROOT / "skills" / pkg / "SKILL.md").exists():
            violations.append(f"skills\\{pkg}\\SKILL.md 缺失 —— 冻结包不完整")

    # 4. README 覆盖率
    for sub in ("scripts", "decks", "knowledge", "docs", "skills",
                "outputs", "inbox", "archive", "silvaco"):
        if (ROOT / sub).exists() and not (ROOT / sub / "README.md").exists():
            violations.append(f"{sub}\\README.md 缺失")

    print(f"检查根: {ROOT}")
    if violations:
        print(f"\n✗ 违规 {len(violations)} 条:")
        for v in violations:
            print(f"  - {v}")
    if warnings:
        print(f"\n⚠ 警告 {len(warnings)} 条:")
        for w in warnings:
            print(f"  - {w}")
    if not violations and not warnings:
        print("✓ 布局完全合规")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
