#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
inbox_watch.py -- 一号机收件箱看守（孤儿脚本，后台常驻）。

监视 D:\\SILVACO_LOCAL\\inbox\\ 里出现的 RESULTS_*.tar.gz（二号机人工拷回的离线
运行结果包），到货后自动：解包 → 校验 manifest → 逐 case 统计（状态/耗时/
关键曲线 CSV）→ 出对比图 PNG → 写 REPORT.md → 追加一行到运行日志留痕。

用法：
    python inbox_watch.py            # 前台轮询（60s 一次）
    python inbox_watch.py --once     # 只处理当前已在 inbox 的包然后退出
处理过的包会移动到 inbox\\processed\\，不会重复统计。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import shutil
import tarfile
import time
from pathlib import Path

ROOT = Path(r"D:\SILVACO_LOCAL")
INBOX = ROOT / "inbox"
DONE = INBOX / "processed"
OUT = ROOT / "outputs" / "offline_runs"
TRACE = ROOT / "docs" / "AGENT_运行日志_与复现手册.md"


def analyse(run_dir: Path) -> str:
    """逐 case 统计，返回 REPORT.md 文本。出图尽力而为（无 CSV 就只报状态）。"""
    rows = []
    curves = {}   # case -> (t, Id) / (t, Tmax)
    for case in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        st = (case / "STATUS").read_text().strip() if (case / "STATUS").exists() else "missing"
        try:
            t0 = int((case / "t_start").read_text())
            t1 = int((case / "t_end").read_text())
            dur = f"{(t1 - t0) / 60:.0f} min"
        except Exception:
            dur = "-"
        n_log = len(list(case.glob("*.log")))
        n_csv = len(list(case.glob("*.csv"))) + len(list(case.glob("*.result")))
        # 失败摘要
        note = ""
        tail = case / "typescript_tail.txt"
        if st != "done" and tail.exists():
            for ln in tail.read_text(errors="replace").splitlines():
                if "ERROR" in ln or "FATAL" in ln.upper():
                    note = ln.strip()[:90]
                    break
        rows.append((case.name, st, dur, n_log, n_csv, note))
        # victoryextract 的曲线 CSV（打包时已展平命名 <tag>_Id_t.csv / <tag>_Tmax_t.csv）
        for kind in ("Id_t", "Tmax_t"):
            for f in case.glob(f"*{kind}*.csv"):
                curves.setdefault(kind, {})[case.name] = f

    # 出图（可选依赖 pandas/matplotlib，一号机已装）
    pngs = []
    try:
        import pandas as pd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        for kind, m in curves.items():
            fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
            for name, f in sorted(m.items()):
                try:
                    df = pd.read_csv(f)
                    x, y = df.columns[0], df.columns[1]
                    ax.plot(df[x], df[y].abs() if kind == "Id_t" else df[y],
                            lw=1.6, label=name)
                except Exception:
                    continue
            ax.set_xscale("log")
            if kind == "Id_t":
                ax.set_yscale("log")
            ax.set_xlabel("Time (s)", fontsize=12)
            ax.set_ylabel("|Id| (A/um)" if kind == "Id_t" else "Peak lattice T (K)",
                          fontsize=12)
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)
            png = run_dir / f"compare_{kind}.png"
            fig.tight_layout()
            fig.savefig(png)
            plt.close(fig)
            pngs.append(png.name)
    except Exception as e:  # 出图失败不影响报告
        pngs.append(f"(绘图跳过: {e})")

    md = [f"# 离线运行结果统计 — {run_dir.name}",
          f"生成: {_dt.datetime.now():%Y-%m-%d %H:%M}",
          "",
          "| case | 状态 | 耗时 | log | csv | 失败摘要 |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        md.append("| " + " | ".join(str(x) for x in r) + " |")
    done = sum(1 for r in rows if r[1] == "done")
    md += ["", f"**{done}/{len(rows)} case 完成。** 对比图: {', '.join(pngs) or '无'}",
           "", "> A→E 阶梯判读：比较各 case 的 Tmax_t 峰值即可分离 LET/打击点/偏压",
           "> 各自的贡献；W_transfer 用 Id-Vg 提取 VTH 对照论文 1.2 V。"]
    return "\n".join(md) + "\n"


def process(pkg: Path) -> None:
    stamp = _dt.datetime.now().strftime("%H:%M")
    dest = OUT / pkg.stem.replace(".tar", "")
    dest.mkdir(parents=True, exist_ok=True)
    print(f"[{stamp}] 收到 {pkg.name} -> 解包到 {dest}")
    with tarfile.open(pkg) as tf:
        tf.extractall(dest.parent, filter="data")
    inner = dest if dest.exists() else dest.parent / pkg.stem
    report = analyse(inner)
    (inner / "REPORT.md").write_text(report, encoding="utf-8")
    print(report)
    # 留痕
    try:
        with TRACE.open("a", encoding="utf-8") as f:
            f.write(f"\n| { _dt.datetime.now():%m-%d %H:%M} | 二号机结果包 {pkg.name} "
                    f"已自动统计 | {inner / 'REPORT.md'} |\n")
    except Exception:
        pass
    DONE.mkdir(parents=True, exist_ok=True)
    shutil.move(str(pkg), DONE / pkg.name)
    print(f"[done] 报告: {inner / 'REPORT.md'}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=int, default=60)
    a = ap.parse_args()
    INBOX.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"[watch] 盯着 {INBOX}（把二号机的 RESULTS_*.tar.gz 丢进来即可）")
    while True:
        for pkg in sorted(INBOX.glob("RESULTS_*.tar.gz")):
            try:
                process(pkg)
            except Exception as e:
                print(f"[error] {pkg.name}: {e}")
                bad = INBOX / "bad"
                bad.mkdir(exist_ok=True)
                shutil.move(str(pkg), bad / pkg.name)
        if a.once:
            return 0
        time.sleep(a.interval)


if __name__ == "__main__":
    raise SystemExit(main())
