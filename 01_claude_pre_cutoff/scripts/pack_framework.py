#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pack_framework.py -- 把 SILVACO_LOCAL 框架打成可分享 zip（GitHub 发布风格）。

只带框架本体（脚本/文档/知识/技能/deck/git 历史），不带运行产物、归档、
收件箱与历史区。四库 D:\\knowledge 体量大（~400MB）不进包——安装教程里
说明单独拷贝。

用法： python pack_framework.py            # 产出 outputs\\SILVACO_LOCAL_framework_<日期>.zip
       python pack_framework.py --with-git # 连 .git 历史一起带上（默认带）
"""

from __future__ import annotations

import datetime as _dt
import sys
import zipfile
from pathlib import Path

ROOT = Path(r"D:\SILVACO_LOCAL")
OUT = ROOT / "outputs"

INCLUDE_DIRS = ["knowledge", "docs", "decks", "scripts", "skills"]
INCLUDE_FILES = ["README.md", "INSTALL.md", ".gitignore", "SEB.in", "mySEU.c"]
INCLUDE_GIT = "--no-git" not in sys.argv

SKIP_PARTS = {"__pycache__", "screenshots", "offline_runs", "_remote_logs"}
SKIP_SUFFIX = {".pyc", ".tar.gz", ".zip", ".str", ".tdr"}


def want(p: Path) -> bool:
    if SKIP_PARTS & set(p.parts):
        return False
    if p.suffix.lower() in SKIP_SUFFIX:
        return False
    return True


def main() -> int:
    stamp = _dt.datetime.now().strftime("%Y%m%d")
    out = OUT / f"SILVACO_LOCAL_framework_{stamp}.zip"
    OUT.mkdir(exist_ok=True)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in INCLUDE_FILES:
            p = ROOT / f
            if p.exists():
                z.write(p, f"SILVACO_LOCAL/{f}")
                n += 1
        for d in INCLUDE_DIRS + ([".git"] if INCLUDE_GIT else []):
            base = ROOT / d
            if not base.exists():
                continue
            for p in base.rglob("*"):
                if p.is_file() and want(p):
                    z.write(p, f"SILVACO_LOCAL/{p.relative_to(ROOT).as_posix()}")
                    n += 1
    print(f"[pack] {out}  ({out.stat().st_size/1e6:.1f} MB, {n} 文件)")
    print("[note] 四库 D:\\knowledge 不在包内——按 INSTALL.md §1① 单独拷贝")
    return 0


if __name__ == "__main__":
    sys.exit(main())
