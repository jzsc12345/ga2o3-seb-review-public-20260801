#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pareto_bv_ron.py  --  BV / Ron 折中分析（配 DeckBuild loop + 经典 extract 管线）

输入两种任选其一:
  A) results.final   DeckBuild 经典 extract 的追加式结果文件（实测: 跨 run 追加、
     同名重复也追加、永不截断 -- 所以 loop 起跑前必须 rm results.final）。
     约定 loop 每轮按固定顺序写三条:
         extract name="nd"  $ndrift          <- 把本轮扫参值本身记进 results.final
         extract name="bv"  x.val from curve(...) where ...
         extract name="ron" y.val from curve(...) where ...
     本脚本按 (nd, bv, ron) 名字分组、按文件顺序配对成行。
  B) CSV             三列: doping,bv,ron（有表头）

用法:
  python pareto_bv_ron.py results.final
  python pareto_bv_ron.py sweep.csv
  python pareto_bv_ron.py results.final --names nd,bv,ron --out pareto.png
"""
import argparse
import csv
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# 1. 读入
# ----------------------------------------------------------------------------
_ENTRY = re.compile(r'^\s*(?P<name>[^=]+?)\s*=\s*(?P<val>[-+0-9.eE]+)\s*$')


def read_results_final(path, names=("nd", "bv", "ron")):
    """按名字分组解析 results.final。每遇到一次第一名字(nd)就开新行。"""
    xkey, bvkey, ronkey = names
    rows, cur = [], {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = _ENTRY.match(line)
            if not m:
                continue
            name, val = m.group("name").strip(), float(m.group("val"))
            if name == xkey:                       # 新一轮开始
                if cur:
                    rows.append(cur)
                cur = {xkey: val}
            elif name in (bvkey, ronkey):
                cur[name] = val
    if cur:
        rows.append(cur)
    rows = [r for r in rows if len(r) == 3]        # 丢弃残缺轮（如中途报错）
    if not rows:
        sys.exit(f"results.final 中没有完整的 ({xkey},{bvkey},{ronkey}) 组")
    a = np.array([[r[xkey], r[bvkey], r[ronkey]] for r in rows])
    return a[:, 0], a[:, 1], a[:, 2]


def read_csv3(path):
    with open(path, encoding="utf-8-sig") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        data = np.array([[float(v) for v in row[:3]] for row in rdr if row])
    return data[:, 0], data[:, 1], data[:, 2]


# ----------------------------------------------------------------------------
# 2. 帕累托前沿（目标: BV 最大化, Ron 最小化）
# ----------------------------------------------------------------------------
def pareto_mask(bv, ron):
    """True = 非被支配点。点 j 支配 i 当 bv_j>=bv_i 且 ron_j<=ron_i 且至少一严格。"""
    n = len(bv)
    mask = np.ones(n, bool)
    for i in range(n):
        dom = (bv >= bv[i]) & (ron <= ron[i]) & ((bv > bv[i]) | (ron < ron[i]))
        if dom.any():
            mask[i] = False
    return mask


def knee_index(bv, ron):
    """归一化后到乌托邦点 (BV=1, Ron=0) 欧氏距离最小的点 = 折中膝点。"""
    nb = (bv - bv.min()) / (np.ptp(bv) or 1.0)
    nr = (ron - ron.min()) / (np.ptp(ron) or 1.0)
    return int(np.argmin(np.hypot(1.0 - nb, nr)))


# ----------------------------------------------------------------------------
# 3. 画图
# ----------------------------------------------------------------------------
RED, BLUE, GRAY = "#c0392b", "#1f77b4", "#9aa0a6"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile")
    ap.add_argument("--names", default="nd,bv,ron",
                    help="results.final 里三个 extract 名, 顺序=x,BV,Ron")
    ap.add_argument("--out", default="pareto_bv_ron.png")
    ap.add_argument("--xlabel", default="drift doping $N_d$ (cm$^{-3}$)")
    args = ap.parse_args()

    names = tuple(s.strip() for s in args.names.split(","))
    if args.infile.endswith(".csv"):
        x, bv, ron = read_csv3(args.infile)
    else:
        x, bv, ron = read_results_final(args.infile, names)

    order = np.argsort(x)
    x, bv, ron = x[order], bv[order], ron[order]

    # 归一化（min-max）。BV 与 Ron 通常同随掺杂下降, 折中交叉点取
    # 「归一化 BV」与「归一化 Ron 收益 (1-nr)」相等处。
    nb = (bv - bv.min()) / (np.ptp(bv) or 1.0)
    nr = (ron - ron.min()) / (np.ptp(ron) or 1.0)
    diff = nb - (1.0 - nr)
    xc = None
    sc = np.where(np.diff(np.sign(diff)) != 0)[0]   # 交叉区间
    if sc.size:
        i = sc[0]                                    # 线性插值求交点
        t = diff[i] / (diff[i] - diff[i + 1])
        xc = x[i] + t * (x[i + 1] - x[i])

    pm = pareto_mask(bv, ron)
    ki = knee_index(bv, ron)

    fig, (ax1, ax3) = plt.subplots(
        1, 2, figsize=(12.5, 5.0), constrained_layout=True)

    # -- 面板 1: BV/Ron vs 掺杂, 双 y 轴（左 BV 红 / 右 Ron 蓝）--------------
    ax1.plot(x, bv, "o-", color=RED, lw=2, ms=5, label="BV (maximize)")
    ax1.set_xlabel(args.xlabel)
    ax1.set_ylabel("BV (V)", color=RED)
    ax1.tick_params(axis="y", labelcolor=RED)
    ax1.set_xscale("log")
    ax2 = ax1.twinx()
    ax2.plot(x, ron, "s-", color=BLUE, lw=2, ms=5, label="Ron (minimize)")
    ax2.set_ylabel(r"$R_{on,sp}$ (a.u.)", color=BLUE)
    ax2.tick_params(axis="y", labelcolor=BLUE)
    ax2.set_yscale("log")
    if xc is not None:
        ax1.axvline(xc, color=GRAY, ls="--", lw=1.5)
        ax1.annotate(f"normalized crossover\nx = {xc:.3g}",
                     xy=(xc, 0.5), xycoords=("data", "axes fraction"),
                     xytext=(8, 0), textcoords="offset points",
                     fontsize=9, color="#444444")
    ax1.axvline(x[ki], color="#444444", ls=":", lw=1.5)
    ax1.annotate(f"knee x = {x[ki]:.3g}",
                 xy=(x[ki], 0.92), xycoords=("data", "axes fraction"),
                 xytext=(8, 0), textcoords="offset points",
                 fontsize=9, color="#444444")
    ax1.grid(alpha=0.25, lw=0.5)
    ax1.set_title("BV / Ron vs doping (twin axes, each in own units)")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="center left", fontsize=9, framealpha=0.9)

    # -- 面板 2: 帕累托平面 Ron(x) vs BV(y) ----------------------------------
    ax3.scatter(ron[~pm], bv[~pm], s=40, color=GRAY, label="dominated", zorder=2)
    fr = np.argsort(ron[pm])
    ax3.plot(ron[pm][fr], bv[pm][fr], "o-", color=RED, lw=2, ms=7,
             label="Pareto frontier", zorder=3)
    ax3.scatter([ron[ki]], [bv[ki]], s=160, facecolor="none",
                edgecolor="#111111", lw=2, label="knee (closest to utopia)",
                zorder=4)
    for xi, bvi, roni in zip(x[pm], bv[pm], ron[pm]):
        ax3.annotate(f"{xi:.2g}", xy=(roni, bvi),
                     xytext=(5, 4), textcoords="offset points", fontsize=8,
                     color="#444444")
    ax3.set_xlabel(r"$R_{on,sp}$ (a.u.)  $\rightarrow$ minimize")
    ax3.set_ylabel(r"BV (V)  $\rightarrow$ maximize")
    ax3.set_xscale("log")
    ax3.grid(alpha=0.25, lw=0.5)
    ax3.set_title("Trade-off plane (labels = doping)")
    ax3.legend(loc="lower left", fontsize=9, framealpha=0.9)

    fig.savefig(args.out, dpi=160)
    print(f"saved {args.out}")
    print(f"knee point : x={x[ki]:.4g}  BV={bv[ki]:.4g}  Ron={ron[ki]:.4g}")
    if xc is not None:
        print(f"normalized-curve crossover at x = {xc:.4g}")
    print("pareto frontier rows (x, BV, Ron):")
    for xi, bvi, roni in zip(x[pm], bv[pm], ron[pm]):
        print(f"  {xi:.4g}  {bvi:.4g}  {roni:.4g}")


if __name__ == "__main__":
    main()
