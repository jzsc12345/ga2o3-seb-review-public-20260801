# VE 剖面 CSV -> matplotlib 曲线（Task B 目标③ 可视化验证）
# CSV 格式: 两列, 带引号表头 "depth", "<field>"; depth = 沿切线距离(µm)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def load_ve_csv(path):
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [c.strip().strip('"') for c in df.columns]
    return df

fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))

# (a) 电子浓度: 纵切 x=12.5 (打击径迹), 对数轴
for f, lab in [("ve_csv/pre_econc.csv", "pre-strike"), ("ve_csv/t200_econc.csv", "t=200 ps")]:
    d = load_ve_csv(f)
    axes[0, 0].semilogy(d.iloc[:, 0], d.iloc[:, 1].clip(lower=1), label=lab)
axes[0, 0].set(title="Electron conc @ x=12.5 um", xlabel="depth along cut (um)", ylabel="n (cm$^{-3}$)")
axes[0, 0].legend()

# (b) 碰撞电离率: 横切 y=-0.3 (峰值面), 对数轴
for f, lab in [("ve_csv/pre_impact_y.csv", "pre-strike"), ("ve_csv/t200_impact_y.csv", "t=200 ps")]:
    d = load_ve_csv(f)
    axes[0, 1].semilogy(d.iloc[:, 0], d.iloc[:, 1].clip(lower=1), label=lab)
axes[0, 1].set(title="Impact gen rate @ y=-0.3 um", xlabel="x (um)", ylabel="G$_{II}$ (cm$^{-3}$s$^{-1}$)")
axes[0, 1].legend()

# (c) 晶格温度: 纵切 x=12.5
for f, lab in [("ve_csv/pre_ltemp.csv", "pre-strike"), ("ve_csv/t200_ltemp.csv", "t=200 ps")]:
    d = load_ve_csv(f)
    axes[1, 0].plot(d.iloc[:, 0], d.iloc[:, 1], label=lab)
axes[1, 0].set(title="Lattice temperature @ x=12.5 um", xlabel="depth along cut (um)", ylabel="T$_L$ (K)")
axes[1, 0].legend()

# (d) 热功率密度(总) 横切 + 热导率 纵切 (双轴)
d = load_ve_csv("ve_csv/t200_heatpow_y.csv")
axes[1, 1].semilogy(d.iloc[:, 0], d.iloc[:, 1].clip(lower=1), color="tab:red", label="total heat power (y=-0.3)")
axes[1, 1].set(title="Total heat power / heat conductivity", xlabel="x or depth (um)", ylabel="W cm$^{-3}$")
ax2 = axes[1, 1].twinx()
k = load_ve_csv("ve_csv/t200_kappa.csv")
ax2.plot(k.iloc[:, 0], k.iloc[:, 1], color="tab:blue", label="heat conductivity (x=12.5)")
ax2.set_ylabel("kappa (W cm$^{-1}$K$^{-1}$)")
axes[1, 1].legend(loc="upper right")
ax2.legend(loc="lower right")

fig.tight_layout()
fig.savefig("ve_profiles.png", dpi=130)
print("saved ve_profiles.png")
