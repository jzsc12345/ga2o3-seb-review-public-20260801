# RUN103_wang1000-nofp-lgd9-x11-mobt-ma18 — 从冻结RUN096单变量验证Ma2016约束的主动体区电子低场mobility(T)反馈

- 日期:2026-07-31 00:14 | git:16c8369 | deck:`decks\RUN103_Wang2026_nofp_Lgd9_x11_mobT_Ma18_SEB_1000V_Et0p8_long.in` (sha256:489ca703b05f1c77)
- 远端:`/root/DECKBUILD/runs/RUN103_wang1000-nofp-lgd9-x11-mobt-ma18/` | tmux:`deck_RUN103_Wang2026_nofp_Lgd9_x11_mobT_Ma18_SEB_1000V_Et0p8_long` | 看板:`outputs\RUN103_mobT_Ma18_live\screenshots\`

## 1. 目标与判据(发射前填)

从冻结 RUN096 单变量验证 Ma 2016 约束的主动体区电子**低场**
`mobility(T)` 反馈。

证据口径：

- ATLAS 2025 手册 Eq. 3-223 与官方 `Photon_LASER_ex09.in` 核实
  `ANALYTIC` Caughey–Thomas 公式和参数绑定。
- Ma et al., *Applied Physics Letters* 109, 212101 (2016),
  arXiv `1610.04198` Eq. (7) 是 300–500 K 的 β-Ga₂O₃
  温度/掺杂经验迁移率。按本 deck 三个主动体区掺杂计算，300–400 K
  有效幂指数分别为 channel `-1.76`、UID `-1.90`、substrate `-1.91`；
  本臂采用共同近似 `-1.8`。
- 只改主动体区 regions 3–5；重掺 source/drain regions 6–7 与所有
  hole mobility 冻结，避免把接触区的不同温度趋势混进主变量。
- `VSATN/VSATP=2e7 cm/s` 仍是显式常数，因此本 RUN 只验证
  **低场电子迁移率反馈**，绝不称“完整高场 mobility(T)”。

到站判据：静态 1000 V 母解同分支；`MODELS PRINT` 在 regions 3–5
逐区打印 Caughey `alpha=beta=-1.8`，regions 6–7 仍为0；自然到100 µs；
`ATLAS finished=1`、硬错误0、源电荷误差绝对值≤5%。比较
31/100/400 ps、1 ns、0.5/1/10/100 µs 的 `Id/Tmax/Joule/impact`，
并提取 `e.mobility/Jtotal/lattice temperature` 空间场。

## 2. 与上一 RUN 的差异(发射前填)

母线：冻结 RUN096，SHA-256
`786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5`。

单变量：regions 3–5 的
`ALPHAN.CAUG/BETAN.CAUG: 0/0 -> -1.8/-1.8`。
除注释和 RUN103 输出文件名外，完整物理 diff 为：

deck diff 全部行:
```diff
- mobility region=3 ... alphan.caug=0 betan.caug=0 gamman.caug=0
+ mobility region=3 ... alphan.caug=-1.8 betan.caug=-1.8 gamman.caug=0
- mobility region=4 ... alphan.caug=0 betan.caug=0 gamman.caug=0
+ mobility region=4 ... alphan.caug=-1.8 betan.caug=-1.8 gamman.caug=0
- mobility region=5 ... alphan.caug=0 betan.caug=0 gamman.caug=0
+ mobility region=5 ... alphan.caug=-1.8 betan.caug=-1.8 gamman.caug=0
```

物理模型改动：**有，仅上述主动体区电子低场温度指数**；用户已明确要求
“查证并单变量验证温度相关 band/mobility 反馈”。结构、11672 点网格、
HfO₂ `HC.STD`、Fe trap、impact、band、hole mobility、S/D mobility、
常数 VSAT、热源、热边界、SEU、LET、求解器和时间表冻结。禁值
`AN=2.5e6/BN=3.96e7/BETAN=1.37/p-type 2e6` 零命中。
deck SHA-256：
`489CA703B05F1C77806C65AB1979502A05603C0D5D1564C3B67A285D4779A828`。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图：`figs\RUN103_preflight_structure_same_as_RUN096.png`
  （SHA `9116F839…11B76`）
- 网格图：`figs\RUN103_preflight_mesh_same_as_RUN096.png`
  （SHA `B38FDA19…F42C0`；11672 points / 22992 triangles / 0 obtuse）
- 发给用户时间：2026-07-31 本轮发射前进展消息
- tmux：`deck_RUN103_Wang2026_nofp_Lgd9_x11_mobT_Ma18_SEB_1000V_Et0p8_long`

## 4. 结果索引

- `csv\RUN096_102_103_tempfeedback_milestones.csv`
- `csv\RUN096_102_103_tempfeedback_peaks.csv`
- `csv\RUN096_102_103_tempfeedback_spatial_summary.csv`
- `csv\spatial\`：三臂×五时刻×四切线，共60个原始VictoryExtract CSV
- `figs\RUN096_102_103_tempfeedback_curves_and_parameters.png`
- `figs\RUN096_102_103_tempfeedback_spatial.png`
- 完整报告：
  `D:\SILVACO_LOCAL\docs\
  RUN102_RUN103_温度相关Band_Mobility单变量验证_20260731.md`
- 大文件：`E:\silvaco2425\bulk\{log,str}\
  RUN103_mobT_Ma18_20260731__*`；3 log + 19 STR，`skipped=0`

## 5. 判据结论

**COMPLETE / POSTPROCESSED / OFAT PASS / HYPOTHESIS REJECTED。**

A14 四件预检包于 2026-07-31 00:16 发给用户；00:16:52 经标准
`vdoe_tmux.sh start-deck` 发射，01:55:38 自然到 100 µs。运行时解析门：
regions 3–5 电子 Caughey `alpha=beta=-1.8`，regions 6–7 与全部空穴
指数仍为0，band 参数仍为0/0。`ATLAS finished=1`，硬错误/Command
Error=0，静态折半0，瞬态自动缩步71次。源电荷2.436243124 pC，相对
2.423015 pC为+0.545937%。

全局 Id 峰 `6.711050924e-4 A/µm@31 ps`，与RUN096差-0.0016913%；
Tmax峰`394.7307799 K@0.693085906 ns`，只比RUN096 **高0.578511 K**。
100 µs 界面 `µn_min=8.412790 cm²/(V·s)`，证明模型真实生效；但此时
Id=1.766671972e-7 A/µm（比RUN096低19.330%），Tmax=369.0998449 K
（低9.580938 K），说明低场迁移率下降在慢尾抑制功率，而不是触发SEB。
裁决：主动体区低场电子mobility(T)不能解释Wang约1500 K；常数VSAT仍
意味着高场速度温变尚未覆盖。
