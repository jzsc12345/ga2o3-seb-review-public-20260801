# RUN095_wang1000-nofp-lgd9-x11-heatfull — 只切换热源方程，量化 HEAT.FULL+GR/PT 相对 RUN094 默认 J·E 的温升贡献

> **FROZEN_READ_ONLY_REFERENCE — 2026-07-31 用户冻结。**
> 本 RUN 是可信、已完成的 V3 热源方程对照；原始结果与证据只读保留。
> 未经新的明确批准，不得修改、重跑或作为新变量分支继续派生。

- 日期:2026-07-30 08:48 | git:16c8369 | deck:`decks\RUN095_Wang2026_nofp_Lgd9_x11_heatfull_SEB_1000V_Et0p8_long.in` (sha256:a87f4eddc49d4f10)
- 远端:`/root/DECKBUILD/runs/RUN095_wang1000-nofp-lgd9-x11-heatfull/` | tmux:`deck_RUN095_Wang2026_nofp_Lgd9_x11_heatfull_SEB_1000V_Et0p8_long` | 看板:`outputs\RUN095_heatfull_live\screenshots\`

## 1. 目标与判据(发射前填)

只切换热源方程，量化 `HEAT.FULL + JOULE.HEAT + GR.HEAT + PT.HEAT`
相对 RUN094 默认 `J·E` 的温升贡献。RUN094 已实测：到 1 ns 的端口能量是
RUN092 的 2.03 倍、收敛 `Tmax` 峰为 405.90 K，因此按审计 V3 选择它作为
热响应更强的母臂。

判据：
1. 100 ps/400 ps/1 ns 的 `Id/Impact/Hole/Joule` 电学轨迹应与 RUN094
   同量级；若电学轨迹本身漂移，不能把温差都归因于新热源；
2. 对同一 STR 全区积分 Joule / generation-recombination /
   Peltier-Thomson 三项，给出各项占总热功率和累计热能的比例；
3. 若 GR/PT 只贡献几个百分点且 `Tmax` 峰变化很小，关闭该根因分支；
   若贡献显著，则纳入正式模型，但仍不得把被拒绝的 Newton 温度试探
   当作收敛温度；
4. 仍跑到 100 µs，并保留 RUN094 的恢复/反弹联合判据。

## 2. 与上一 RUN 的差异(发射前填)

单变量:heat_source_equation_only: J·E -> HEAT.FULL+JOULE.HEAT+GR.HEAT+PT.HEAT
deck diff 全部行:
```diff
-models analytic fldmob srh auger fermi incomplete print lat.temp joule.heat
+models analytic fldmob srh auger fermi incomplete print lat.temp heat.full joule.heat gr.heat pt.heat
```

将全部输出标签 `RUN094→RUN095` 后不算物理差异。机器审计：

- 有效语句 `298/298`；把新热源行归一化回旧行后逐字相同；
- DevEdit 几何块 `60/60` 逐字相同；
- 旧 impact 三数与 `p型2e6`：0 命中；
- `material/mobility/impact/trap/thermcontact/singleeventupset/solve`
  所有数值均未改变。

⚠ 物理模型改动：**有且只有热源方程开关**。这正是差距审计 §10 V3，
用户已在本轮给出五小时自主推进授权；不附带任何结构、迁移率、impact、
Fe、LET、热导率、热容或热边界调整。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图（与 RUN094 字节同源）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN094_wang1000-nofp-lgd9-x11-reference\figs\RUN094_preflight_structure.png`
- 网格图（同一 11672 点 / 22992 三角形 / 0 obtuse）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN094_wang1000-nofp-lgd9-x11-reference\figs\RUN094_preflight_track_mesh.png`
- 实机结构截图：
  `D:\SILVACO_LOCAL\outputs\runs\RUN094_wang1000-nofp-lgd9-x11-reference\shots\RUN094_actual_structure_gui.png`
- deck diff：见 §2；full SHA256：
  `A87F4EDDC49D4F10C149AF28A268A7CE0563AE5A7A752DD096CBF58CBB040DA6`
- 语法证据：
  - 远端 `atlas.key`：`heat.full`、`pt.heat`、`joule.heat`、`gr.heat`
    全部现场可查；
  - 官方例 `D:\knowledge\exp25\CMOS_ands_BiCMOS\Bulk_ex03.in:56`
    使用 `lat.temp heat.full`；
  - ATLAS 2025 手册 pp.613–615：`HEAT.FULL` 选择完整热源式，
    三个 flags 控制 Joule、GR 与 Peltier/Joule-Thomson 项。
- 发给用户时间:08:48–08:50 | tmux 会话:
  `deck_RUN095_Wang2026_nofp_Lgd9_x11_heatfull_SEB_1000V_Et0p8_long`

## 4. 结果索引(到站后填)

- 完整曲线：
  `csv\RUN094_095_heat_source_curve.csv`
- 六时刻电学/温度里程碑：
  `csv\RUN094_095_heat_source_milestones.csv`
- 六时刻全区热源积分：
  `csv\RUN094_095_heat_integrals.csv`
- 48 个 VictoryExtract 原始积分：
  `csv\heat_sources\`
- 16 条空间 cutline：
  `csv\spatial\`
- 曲线与热源分量总图：
  `figs\RUN094_095_heat_source_comparison.png`
- 空间证据图（|E|、T、Jtotal、径迹 depth cut）：
  `figs\RUN094_095_heat_source_spatial_cutlines.png`
- 结构/网格仍引用完全相同的 RUN094 预检图，见 §3；RUN095 不重复造图冒充
  新结构。
- 最终 GUI 截图：
  `D:\SILVACO_LOCAL\outputs\RUN095_heatfull_live\screenshots\shot_20260730T102955_final.png`
- 本地轻日志：
  `logs\RUN095_static_final.log`、`logs\RUN095_transient_final.log`
- 大文件已归档：
  `E:\silvaco2425\bulk\log\RUN095_wang1000-nofp-lgd9-x11-heatfull__*`
  （3 件）；
  `E:\silvaco2425\bulk\str\RUN095_wang1000-nofp-lgd9-x11-heatfull__*`
  （19 件）；`skipped=0`。
- 远端只读后处理：
  `/root/DECKBUILD/postproc/RUN094_095_heat_sources/`

## 5. 判据结论(到站后填)

**状态：COMPLETE — V3「热源方程不完整」已关闭。**

运行验收：

- ATLAS 5.40.0.R 于 `2026-07-30 10:22:25 +08:00` 正常打印
  `finished`；`Error #/Command Error/region out of range=0`；
- 静态爬压折半 `0`；瞬态小步重试 `75`；温度越界试探 `23`。
  后两者均被折半拒绝，接受解 Tmin 始终约 300 K，不能把试探的 120 K
  当物理解；
- wrapper 未写 `simulator exits with code`，所以不虚构 exit-code PASS；
- 源项积分 `1.52057066174147e11 cm^-1`，对应
  `2.4362228 pC/um`，比名义 `2.423015 pC/um` 高 `0.545%`，通过 5% 门。

核心结果：

| 指标 | RUN094 默认 J·E | RUN095 HEAT.FULL | 差值/比例 |
|---|---:|---:|---:|
| `Tmax_peak` | 405.901744 K @ 0.672839 ns | 405.978439 K @ 0.683161 ns | **+0.076695 K** |
| 100 ps total heat | 0.437563 W/um | 0.454823 W/um | +3.945% |
| 400 ps total heat | 0.300877 W/um | 0.301768 W/um | +0.296% |
| 1 ns total heat | 0.00598256 W/um | 0.00609110 W/um | +1.814% |
| 1 us total heat | 0.000668368 W/um | 0.000668751 W/um | +0.057% |
| 100 us total heat | 0.000261244 W/um | 0.000261237 W/um | -0.0024% |

100 ps 时 GR 占 RUN095 total 的 3.525%，PT 为 -0.010%；400 ps 时
GR 只占 0.194%、PT 0.008%；1 ns 时 GR/PT 分别 1.653%/0.191%。
它们确实存在，但远小于把约 406 K 推到 Wang 图3约 1715 K 所需的量级。

空间 cutline 还揭示：HEAT.FULL 在 x=11 um 离子径迹深处增加了一层分布热，
100 ps 最大局部 `ΔT≈4.72 K`、400 ps `≈3.01 K`；然而全器件温度峰在
漏侧电流通路，两臂峰值只差 0.077 K。因此它没有把径迹、impact 与漏源
导电路径接成持续高功率电流丝。

恢复判据也不变：RUN095
`Id_peak=6.71136e-4 A/um @31 ps`；
0.5/1/10/100 us 的 Id 分别为
`6.57295e-7 / 5.55725e-7 / 3.86248e-7 / 2.18687e-7 A/um`；
3.97 ns→16.25 ns 有 `271×` 延迟反弹，但随后下降。
故标签仍是
`RECOVERABLE_SET_ENVELOPE_WITH_DELAYED_TRAP_REBOUND_NOT_10X_DARK`，
不是 Wang 式持续 SEB。

结论：完整热源只增加几个百分点的瞬时总热功率和最多几 K 的径迹局部温升，
不能解释论文与本轮约 1300 K 的温度差。下一轮不再调 GR/PT；应把优先级放回
“持续局域电流丝为何没有建立”，先做模型完整性/热边界拓扑的最小判别，
再考虑 Fe、迁移率、impact 或 LET。
