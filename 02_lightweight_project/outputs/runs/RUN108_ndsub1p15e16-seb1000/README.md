# RUN108_ndsub1p15e16-seb1000 — 冻结RUN096，仅提高n型衬底背景施主，裁决Fe过补偿是否导致深电子路径饿死

- 日期:2026-07-31 04:32 | git:16c8369 | deck:`decks\RUN108_Wang2026_nofp_Lgd9_x11_subNd1p15e16_SEB_1000V_Et0p8_long.in` (sha256:b044e3b71f2abd34)
- 远端:`/root/DECKBUILD/runs/RUN108_ndsub1p15e16-seb1000/` | tmux:`deck_RUN108_Wang2026_nofp_Lgd9_x11_subNd1p15e16_SEB_1000V_Et0p8_long` | 看板:`outputs\RUN108_ndsub1p15e16_seb1000_live\screenshots\`

## 1. 目标与判据(发射前填)

冻结RUN096，仅提高n型衬底背景施主，裁决Fe过补偿是否导致深电子路径饿死。

1. 静态母态必须真实到达 `VDS=1000 V`，且
   `|Id|≤1e-9 A/µm`；未到站则瞬态无效；
2. 源项积分电荷必须落在冻结目标 `2.423015 pC/µm` 的 ±5%；
3. 自然推进至 `100 µs`，不得中途改 solver、时间步或物理参数；
4. 与 RUN096 同时刻同切线比较栅右 `x≈9 µm`、Fe 中部
   `y=2.85 µm`、端电流和 `Tmax`。若 50–500 ns 深路瓶颈、浅路瓶颈
   或晚期端电流提高至少一个数量级，记“Fe 过补偿候选获得支持”；
   若变化小于 2 倍，记“背景施主不是主因”；中间值记“敏感但不充分”；
5. 峰温是结果，不预押必须达到 1500 K；本臂不改变高场 VSAT(T)。

## 2. 与上一 RUN 的差异(发射前填)

单变量:Nd_sub: 1.5e15 -> 1.15e16 cm^-3 only
deck diff 全部行:

`D:\SILVACO_LOCAL\outputs\runs\RUN108_ndsub1p15e16-seb1000\logs\RUN096_RUN108_full_deck_diff.txt`

物理差异只有：

```diff
-set nd_sub      = 1.5e15
+set nd_sub      = 1.15e16
```

其余 diff 是 RUN096→RUN108 注释和输出前缀机械隔离。去注释、归一
`RUN108→RUN096` 和 `1.15e16→1.5e15` 后，有效语句 `299/299`，
`UNEXPECTED_DIFFS=0`。

⚠ 物理模型改动：没有增删 `lat.temp/impact/trap/incomplete` 或材料模型；
只有用户已授权 B 阶段的 n 型衬底背景施主单变量。Fe `Nt/Elevel/σn/σp`、
channel/UID、结构、网格、mobility、常数 VSAT、热参数、离子源和时间表冻结。
旧禁值 `an=2.5e6 / bn=3.96e7 / betan=1.37 / p型2e6` 零命中。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图（与 RUN096 同源）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN108_ndsub1p15e16-seb1000\figs\RUN108_preflight_structure_from_RUN094.png`
- 网格图（与 RUN096 同源，11672 points / 22992 triangles / 0 obtuse）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN108_ndsub1p15e16-seb1000\figs\RUN108_preflight_mesh_from_RUN094.png`
- deck SHA-256：
  `B044E3B71F2ABD34C4889855828DC4F6D44F0271E129A75A3CF8C16ECB032528`
- 发给用户时间：2026-07-31 本轮；tmux：
  `deck_RUN108_Wang2026_nofp_Lgd9_x11_subNd1p15e16_SEB_1000V_Et0p8_long`

## 4. 结果索引

- 运行摘要：`csv\RUN108_run_summary.csv`
- 单臂 80 条 VE 切线、3 CSV、4 PNG：
  `D:\SILVACO_LOCAL\outputs\reports\RUN108_persistent_path_audit_20260731\`
- RUN096/RUN108 合并曲线：
  `D:\SILVACO_LOCAL\outputs\reports\RUN096_108_ndsub_path_overlay_20260731\`
- 正式裁决：
  `D:\SILVACO_LOCAL\docs\RUN108_Ndsub深路改善但浅路受损裁决_20260731.md`
- 大文件：
  `E:\silvaco2425\bulk\{log,str}\RUN108_ndsub1p15e16_seb1000_COMPLETE__*`
  （3 log + 19 str，skipped=0）。

## 5. 判据结论

**COMPLETE / POSTPROCESSED / SENSITIVE BUT INSUFFICIENT。** 静态 1000 V、
源电荷、100 µs 和 80/80 VE 全部通过。50 ns 深路提高 22.38 倍，但
100/500 ns 浅路分别降至 RUN096 的 2.59%/0.152%；`Id(100µs)`低14.17%，
`Tmax(100µs)`低9.81 K。背景施主控制路径分配，但不是持续SEB主因。
