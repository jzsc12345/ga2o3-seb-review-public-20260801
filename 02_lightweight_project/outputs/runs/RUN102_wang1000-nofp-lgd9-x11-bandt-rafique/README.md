# RUN102_wang1000-nofp-lgd9-x11-bandt-rafique — 从冻结RUN096单变量验证Rafique一手Varshni Eg(T)反馈

- 日期:2026-07-31 00:14 | git:16c8369 | deck:`decks\RUN102_Wang2026_nofp_Lgd9_x11_bandT_Rafique_SEB_1000V_Et0p8_long.in` (sha256:f1b8b8286c53d681)
- 远端:`/root/DECKBUILD/runs/RUN102_wang1000-nofp-lgd9-x11-bandt-rafique/` | tmux:`deck_RUN102_Wang2026_nofp_Lgd9_x11_bandT_Rafique_SEB_1000V_Et0p8_long` | 看板:`outputs\RUN102_bandT_Rafique_live\screenshots\`

## 1. 目标与判据(发射前填)

从冻结 RUN096 单变量验证 Rafique 一手 Varshni `Eg(T)` 反馈。

证据口径：

- ATLAS 2025 手册 Eq. 3-38 核实 `EG300/EGALPHA/EGBETA` 公式；
  `EG300` 是 300 K 锚点，所以本臂在 300 K 与 RUN096 同带隙。
- Rafique et al., *Optical Materials Express* 7, 3561–3570 (2017),
  DOI `10.1364/OME.7.003561` 直接报告
  `EGALPHA=4.45e-3 eV/K, EGBETA=2000 K`。
- 原始测量拟合范围是 77–298 K；本项目温度超过 298 K 时只称
  **外推敏感性**，不称高温材料定标。
- Wang 2026 只声明使用 temperature-dependent band parameters，
  没有披露这两个系数；本 RUN 不冒充 Wang 参数复现。

到站判据：静态 1000 V 母解与 RUN096 同分支；`MODELS PRINT` 在 regions 3–7
逐区打印 `EGALPHA=0.00445/EGBETA=2000`；自然到 100 µs；
`ATLAS finished=1`、硬错误0、源电荷误差绝对值≤5%。比较
31/100/400 ps、1 ns、0.5/1/10/100 µs 的 `Id/Tmax/Joule/impact`，
并提取 `band.temp/Jtotal/lattice temperature` 空间场。

## 2. 与上一 RUN 的差异(发射前填)

母线：冻结 RUN096，SHA-256
`786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5`。

单变量：regions 3–7 的 `EGALPHA/EGBETA: 0/0 -> 4.45e-3/2000`。
除注释和 RUN102 输出文件名外，完整物理 diff 为：

deck diff 全部行:
```diff
- material region=3 ... eg300=$eg_g egalph=0 egbeta=0
+ material region=3 ... eg300=$eg_g egalpha=4.45e-3 egbeta=2000
- material region=4 ... eg300=$eg_g egalph=0 egbeta=0
+ material region=4 ... eg300=$eg_g egalpha=4.45e-3 egbeta=2000
- material region=5 ... eg300=$eg_g egalph=0 egbeta=0
+ material region=5 ... eg300=$eg_g egalpha=4.45e-3 egbeta=2000
- material region=6 ... eg300=$eg_g egalph=0 egbeta=0
+ material region=6 ... eg300=$eg_g egalpha=4.45e-3 egbeta=2000
- material region=7 ... eg300=$eg_g egalph=0 egbeta=0
+ material region=7 ... eg300=$eg_g egalpha=4.45e-3 egbeta=2000
```

物理模型改动：**有，仅上述 Varshni 二参数对**；用户已明确要求“查证并
单变量验证温度相关 band/mobility 反馈”。结构、11672 点网格、HfO₂
`HC.STD`、Fe trap、impact、全部 mobility、热源、热边界、SEU、LET、求解器
和时间表冻结。禁值 `AN=2.5e6/BN=3.96e7/BETAN=1.37/p-type 2e6` 零命中。
deck SHA-256：
`F1B8B8286C53D681A89CAF369BF0B06A575C442A53A19918C8732895135C4923`。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图：`figs\RUN102_preflight_structure_same_as_RUN096.png`
  （SHA `9116F839…11B76`）
- 网格图：`figs\RUN102_preflight_mesh_same_as_RUN096.png`
  （SHA `B38FDA19…F42C0`；11672 points / 22992 triangles / 0 obtuse）
- 发给用户时间：2026-07-31 本轮发射前进展消息
- tmux：`deck_RUN102_Wang2026_nofp_Lgd9_x11_bandT_Rafique_SEB_1000V_Et0p8_long`

## 4. 结果索引

- 配对里程碑：
  `..\RUN103_wang1000-nofp-lgd9-x11-mobt-ma18\csv\
  RUN096_102_103_tempfeedback_milestones.csv`
- 峰值：
  `..\RUN103_wang1000-nofp-lgd9-x11-mobt-ma18\csv\
  RUN096_102_103_tempfeedback_peaks.csv`
- 60 个空间剖面与汇总：
  `..\RUN103_wang1000-nofp-lgd9-x11-mobt-ma18\csv\spatial\`、
  `..\RUN103_wang1000-nofp-lgd9-x11-mobt-ma18\csv\
  RUN096_102_103_tempfeedback_spatial_summary.csv`
- 主图：
  `..\RUN103_wang1000-nofp-lgd9-x11-mobt-ma18\figs\
  RUN096_102_103_tempfeedback_curves_and_parameters.png`、
  `RUN096_102_103_tempfeedback_spatial.png`
- 完整报告：
  `D:\SILVACO_LOCAL\docs\
  RUN102_RUN103_温度相关Band_Mobility单变量验证_20260731.md`
- 大文件：`E:\silvaco2425\bulk\{log,str}\
  RUN102_bandT_Rafique_20260731__*`；3 log + 19 STR，`skipped=0`

## 5. 判据结论

**COMPLETE / POSTPROCESSED / OFAT PASS / HYPOTHESIS REJECTED。**

A14 四件预检包于 2026-07-31 00:16 发给用户；00:16:52 经标准
`vdoe_tmux.sh start-deck` 发射，01:57:22 自然到 100 µs。运行时解析门：
regions 3–7 均打印 `EGALPHA=0.00445/EGBETA=2000`，全部 mobility
温度指数仍为0。`ATLAS finished=1`，硬错误/Command Error=0，静态折半0，
瞬态自动缩步72次。源电荷2.436242837 pC，相对2.423015 pC为+0.545925%。

全局 Id 峰 `6.711172253e-4 A/µm@31 ps`，与 RUN096 差+0.0001166%；
Tmax 峰 `393.4977903 K@0.684614404 ns`，比 RUN096 **低0.654478 K**。
400 ps 界面 `Eg_min=4.764487 eV`，证明模型真实生效；但温度/电流/impact
空间峰形没有换路。100 µs 时 Id=2.200918023e-7 A/µm、Tmax=379.1230444 K，
仍是恢复后的低漏电慢热态。裁决：Rafique 参数的高温外推敏感性不能解释
Wang 约1500 K与当前约394 K的差距。
