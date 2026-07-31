# -*- coding: utf-8 -*-
"""
T2 时间族叠加图脚本（kb43 模板 T2 配套，可直接改配置块复用）
输入：victoryextract extract.profile 产出的 2 列 csv（"depth", "<field>"），一个时刻一个文件
输出：outputs/paper_figs/<OUTPNG>
调色：dataviz 参考调色板 sequential blue（ordinal 带内 8 步，250->700，时间早=浅、晚=深）
"""
import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "T2_demo_data")

# ---------- 调色板（validated reference palette, sequential blue, ordinal band） ----------
RAMP8 = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
         "#2a78d6", "#1c5cab", "#104281", "#0d366b"]   # steps 250..700
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"

TAGS   = ["prestrike", "t70ps", "t200ps", "t1ns", "t10ns", "t100ns", "t1us", "final"]
LABELS = ["pre-strike", "70 ps", "200 ps", "1 ns", "10 ns", "100 ns", "1 μs", "final"]

def load(fname):
    xs, ys = [], []
    with open(os.path.join(DATA, fname), newline="") as f:
        rd = csv.reader(f, skipinitialspace=True)
        header = next(rd)
        for row in rd:
            if len(row) >= 2:
                xs.append(float(row[0])); ys.append(float(row[1]))
    return np.asarray(xs), np.asarray(ys), header

def style_ax(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=8.5, width=0.8)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)

def overlay(prefix, ylabel, title, outpng, logy=False, vlines=None, peak_fmt=None,
            peak_offset=(12, -6)):
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=200)
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    peak = (None, None, None)  # (x, y, label)
    for tag, lab, col in zip(TAGS, LABELS, RAMP8):
        x, y, _ = load(f"{prefix}_{tag}.csv")
        if logy:
            m = y > 0
            x, y = x[m], y[m]
        ax.plot(x, y, color=col, lw=2.0, label=lab, solid_capstyle="round")
        if len(y) and (peak[1] is None or y.max() > peak[1]):
            peak = (x[np.argmax(y)], y.max(), lab)
    if logy:
        ax.set_yscale("log")
    if vlines:
        for xv, txt in vlines:
            ax.axvline(xv, color=MUTED, lw=0.8, ls=(0, (4, 3)))
            ax.annotate(txt, (xv, 1.0), xycoords=("data", "axes fraction"),
                        xytext=(3, -2), textcoords="offset points",
                        ha="left", va="top", fontsize=7.5, color=MUTED)
    if peak_fmt and peak[1] is not None:
        ax.annotate(peak_fmt.format(v=peak[1], x=peak[0], t=peak[2]),
                    xy=(peak[0], peak[1]), xytext=peak_offset,
                    textcoords="offset points", fontsize=8.5, color=INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlabel(u"position (μm)", fontsize=9.5, color=INK2)
    ax.set_ylabel(ylabel, fontsize=9.5, color=INK2)
    ax.set_title(title, fontsize=10.5, color=INK, loc="left", pad=10)
    style_ax(ax)
    leg = ax.legend(fontsize=8, frameon=False, labelcolor=INK2,
                    loc="center left", bbox_to_anchor=(1.01, 0.5),
                    handlelength=1.4, title="time", title_fontsize=8.5)
    leg.get_title().set_color(INK2)
    fig.tight_layout()
    out = os.path.join(HERE, outpng)
    fig.savefig(out, facecolor="white", bbox_inches="tight")
    print("saved", out)

# 图 1：温度沿沟道（axis=x y.val=-0.20 横切），8 时刻
overlay("T2_lat_x", "lattice temperature (K)",
        "Lattice temperature along mid-channel (y = −0.20 μm), strike at x₀ = 12.5 μm",
        "demo_T2_lattemp_x_family.png",
        vlines=[(12.5, "x₀")],
        peak_fmt="{v:.0f} K @ {t}")

# 图 2：电子浓度竖切（axis=y x.val=12.5），8 时刻，对数轴
overlay("T2_nc_y", u"electron conc (cm⁻³)",
        "Electron concentration, vertical cut through strike (x = 12.5 μm)",
        "demo_T2_nconc_y_family.png",
        logy=True,
        vlines=[(-0.30, "surface"), (-0.10, "epi/sub")],
        peak_fmt="{v:.2e} @ {t}", peak_offset=(40, -36))
