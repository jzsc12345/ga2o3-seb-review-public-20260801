from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "figures"


def setup() -> None:
    plt.rcParams.update(
        {
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "figure.dpi": 160,
            "savefig.dpi": 220,
        }
    )
    OUT.mkdir(parents=True, exist_ok=True)


def gap_dashboard() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6), gridspec_kw={"width_ratios": [0.9, 1.6]})
    colors = ["#ef6c35", "#2b6cb0"]
    vals = [1715.0, 394.152]
    axes[0].bar(["Wang Fig.3\n图读目标", "RUN096\n冻结基线"], vals, color=colors, width=0.62)
    axes[0].set_ylabel("Peak lattice temperature (K)")
    axes[0].set_ylim(0, 1900)
    axes[0].set_title("1000 V 温度峰值仍差 1320.85 K", loc="left", fontweight="bold")
    for idx, value in enumerate(vals):
        axes[0].text(idx, value + 45, f"{value:.1f} K", ha="center", fontweight="bold")
    axes[0].text(0.5, 110, "RUN096 仅达到目标约 23%", ha="center", color="#b33a1f")
    axes[0].spines[["top", "right"]].set_visible(False)

    labels = ["完整热源", "HfO2 热容", "Eg(T)", "低场 mu_n(T)", "F.VSATN(T)"]
    deltas = [0.0767, -11.826, -0.654, 0.579, -1.237]
    bar_colors = ["#2f855a" if val > 0 else "#64748b" for val in deltas]
    axes[1].barh(labels, deltas, color=bar_colors)
    axes[1].axvline(0, color="#111827", linewidth=0.9)
    axes[1].set_xlabel("ΔTpeak vs 对应基线 (K)")
    axes[1].set_title("已验证旋钮均无法解释千 K 级差距", loc="left", fontweight="bold")
    for idx, value in enumerate(deltas):
        axes[1].text(value + 0.25, idx, f"{value:+.3f} K", va="center", ha="left")
    axes[1].spines[["top", "right"]].set_visible(False)
    fig.suptitle("核心审计：缺的不是一个温度系数，而是持续 J·E 电流通道", x=0.04, ha="left", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    fig.savefig(OUT / "13_fit_gap_dashboard.png", bbox_inches="tight")
    plt.close(fig)


def stage_funnel() -> None:
    stages = [
        ("结构/网格", "PASS", "20 µm · Lgd 9 µm · xion 11 µm\n11,672 点 / 22,992 三角形", "#2f855a"),
        ("源项电荷", "PASS", "源极收集 2.436 pC/µm\n较目标 2.423 pC/µm 高 0.545%", "#2f855a"),
        ("1000 V 冻结基线", "PASS", "RUN096 完成长尾至 100 µs\n但电流持续衰减", "#2b6cb0"),
        ("持续电流丝", "OPEN", "50→100→500 ns 路径能力持续下降\n主缺项尚未找到", "#d97706"),
        ("1600 V 空间复现", "BLOCKED", "RUN104–107 仅到 1033.8–1098.5 V", "#c2413b"),
        ("Wang 图级拟合", "NOT YET", "Fig.2/3/4/6–7 尚未同口径闭环", "#7c3aed"),
    ]
    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.text(0.45, 6.72, "当前处于哪一阶段？", fontsize=18, fontweight="bold", color="#111827")
    ax.text(0.45, 6.36, "输入层已基本冻结 → 输出层卡在持续电流通道与高压母态", fontsize=10.5, color="#475569")
    for idx, (title, status, body, color) in enumerate(stages):
        y = 5.55 - idx * 0.88
        ax.add_patch(FancyBboxPatch((0.55, y), 11.7, 0.65, boxstyle="round,pad=0.012,rounding_size=0.08", facecolor="#f8fafc", edgecolor="#d7dee7", linewidth=1.0))
        ax.add_patch(FancyBboxPatch((0.72, y + 0.12), 1.15, 0.4, boxstyle="round,pad=0.01,rounding_size=0.05", facecolor=color, edgecolor=color))
        ax.text(1.295, y + 0.32, status, ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        ax.text(2.1, y + 0.41, title, va="center", fontsize=11.5, fontweight="bold", color="#111827")
        ax.text(4.45, y + 0.32, body, va="center", fontsize=9.2, color="#334155")
        if idx < len(stages) - 1:
            ax.annotate("", xy=(6.35, y - 0.18), xytext=(6.35, y - 0.04), arrowprops={"arrowstyle": "-|>", "color": "#94a3b8", "lw": 1.3})
    fig.savefig(OUT / "14_current_stage_funnel.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def context_matrix() -> None:
    columns = [
        ("Fig.2", "静态 · VGS=0", "BV≈2720 V\n局部 T>1500 K", "尚无同支路拟合", "#c2413b"),
        ("Fig.3", "瞬态 · VDS=1000 V", "图读≈1715 K@220 ns", "RUN096=394 K@0.686 ns", "#d97706"),
        ("Fig.4", "电流阶段 · VDS=1200 V", "短峰→回落→持续增益", "最终几何无有效配对", "#c2413b"),
        ("Fig.6/7", "空间图 · 1600 V, LET=75", "2–500 ns 载流子演化", "静态母态未建立", "#c2413b"),
    ]
    fig, ax = plt.subplots(figsize=(12.8, 5.4))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    ax.text(0.42, 4.92, "Wang2026 的四个上下文必须分开验收", fontsize=17, fontweight="bold", color="#111827")
    ax.text(0.42, 4.56, "不能把静态 2720 V、1000 V 温升、1200 V 电流阶段和 1600 V 空间图拼成一个“拟合成功”", fontsize=9.8, color="#475569")
    for idx, (fig_no, condition, target, current, color) in enumerate(columns):
        x = 0.45 + idx * 3.08
        ax.add_patch(FancyBboxPatch((x, 0.58), 2.82, 3.55, boxstyle="round,pad=0.02,rounding_size=0.08", facecolor="#f8fafc", edgecolor="#d7dee7"))
        ax.text(x + 0.2, 3.78, fig_no, fontsize=15, fontweight="bold", color=color)
        ax.text(x + 0.2, 3.35, condition, fontsize=9.2, fontweight="bold", color="#334155")
        ax.text(x + 0.2, 2.58, "论文目标", fontsize=8.4, color="#64748b")
        ax.text(x + 0.2, 2.12, target, fontsize=10, fontweight="bold", color="#111827")
        ax.text(x + 0.2, 1.46, "当前证据", fontsize=8.4, color="#64748b")
        ax.text(x + 0.2, 1.02, current, fontsize=9.6, color=color, fontweight="bold")
    fig.savefig(OUT / "15_wang_context_matrix.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    setup()
    gap_dashboard()
    stage_funnel()
    context_matrix()
    print(f"OUTPUT={OUT}")
