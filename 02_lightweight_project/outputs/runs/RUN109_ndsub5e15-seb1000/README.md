# RUN109_ndsub5e15-seb1000 — 冻结RUN096，仅取Nd_sub=5e15 cm^-3中点，寻找浅UID与深Fe路径的折中并自然推进到100us

- 日期:2026-07-31 06:10 | git:16c8369 | deck:`decks\RUN109_Wang2026_nofp_Lgd9_x11_subNd5e15_SEB_1000V_Et0p8_long.in` (sha256:360fd385bcce609f)
- 远端:`/root/DECKBUILD/runs/RUN109_ndsub5e15-seb1000/` | tmux:`deck_RUN109_Wang2026_nofp_Lgd9_x11_subNd5e15_SEB_1000V_Et0p8_long` | 看板:`outputs\RUN109_ndsub5e15_seb1000_live\screenshots\`

## 1. 目标与判据(发射前填)

冻结RUN096，仅取 `Nd_sub=5e15 cm^-3` 中点，寻找浅UID与深Fe路径的折中，
并自然推进到 `100 µs`。

1. 静态母态必须真实到达 `VDS=1000 V`，且
   `|Id|≤1e-9 A/µm`；未到站则瞬态无效；
2. 源项积分电荷必须落在冻结目标 `2.423015 pC/µm` 的 ±5%；
3. 自然推进至 `100 µs`，不得中途改 solver、时间步或任何物理参数；
4. 用与 RUN096/RUN108 完全相同的 10 时刻×8 切线做 VictoryExtract。
   若 50–500 ns 的同一时刻，浅路与深路瓶颈和端电流都达到 RUN096
   的至少 10 倍，记“背景补偿主因获得强支持”；两路都提高至少 2 倍
   但端电流不足 10 倍，记“联合路径改善但不足”；一条改善而另一条降至
   0.5 倍以下，记“路径重分配、仍不充分”；端电流与两路联合改善均低于
   2 倍，记“背景施主不是主因”；
5. 峰温是结果，不预押 1500 K；本臂不改变高场 VSAT(T)。

## 2. 与上一 RUN 的差异(发射前填)

单变量:Nd_sub: 1.5e15 -> 5.0e15 cm^-3 only
deck diff 全部行:

`D:\SILVACO_LOCAL\outputs\runs\RUN109_ndsub5e15-seb1000\logs\RUN096_RUN109_full_deck_diff.txt`

物理差异只有：

```diff
-set nd_sub      = 1.5e15
+set nd_sub      = 5.0e15
```

其余 diff 是 RUN096→RUN109 注释和输出前缀机械隔离。去注释、归一
`RUN109→RUN096` 和 `5.0e15→1.5e15` 后，有效语句 `299/299`，
`UNEXPECTED_DIFFS=0`。

⚠ 物理模型改动：没有增删 `lat.temp/impact/trap/incomplete` 或材料模型；
只有用户授权“按三个优先级由代理选择效果最佳路线继续下一波”下的 n 型衬底
背景施主单变量。Fe `Nt/Elevel/σn/σp`、channel/UID、结构、网格、mobility、
常数 VSAT、热参数、离子源和时间表全部冻结。旧禁值
`an=2.5e6 / bn=3.96e7 / betan=1.37 / p型2e6` 零命中。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图（与 RUN096/RUN108 同源）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN109_ndsub5e15-seb1000\figs\RUN109_preflight_structure_from_RUN094.png`
- 网格图（与 RUN096/RUN108 同源，11672 points / 22992 triangles /
  0 obtuse）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN109_ndsub5e15-seb1000\figs\RUN109_preflight_mesh_from_RUN094.png`
- deck SHA-256：
  `360FD385BCCE609FC48AD341A5F2DAFC6340C7C178CB9BCA4D5540D8354E5090`
- 发给用户时间：2026-07-31 06:12；tmux：
  `deck_RUN109_Wang2026_nofp_Lgd9_x11_subNd5e15_SEB_1000V_Et0p8_long`

### 3.1 发射留痕

- 06:12 发射前现场门：远端无 tmux、`RUNNING_ATLAS=0`，许可证
  `server=2 / TCP3162=OPEN / verify=OK`；
- 本地/远端 deck SHA 均为
  `360FD385BCCE609FC48AD341A5F2DAFC6340C7C178CB9BCA4D5540D8354E5090`；
- 经 `/root/bin/vdoe_tmux.sh start-deck` 正规发射；
- 看板首烟测因 label 含空格造成远端临时文件名未引用而失败；未改仿真。
  改用无空格 label 后单帧抓取 PASS，正式 watcher PID=`23452`，
  每 180 s 一张。

## 4. 结果索引(到站后填)

- 本地轻日志：
  `logs\RUN109_static_final.log`、
  `logs\RUN109_transient_final.log`、
  `logs\RUN109_typescript_final.txt`；
- RUN109 单臂 80 条 VictoryExtract 切线、3 张摘要 CSV 和 4 张图：
  `D:\SILVACO_LOCAL\outputs\reports\RUN109_persistent_path_audit_20260731\`；
- RUN096/108/109 三臂合并曲线和精确 CSV：
  `D:\SILVACO_LOCAL\outputs\reports\RUN096_108_109_ndsub_path_overlay_20260731\`；
- 正式裁决：
  `D:\SILVACO_LOCAL\docs\RUN109_Ndsub中点_三曲线合拢裁决_20260731.md`；
- 大文件归档：
  `E:\silvaco2425\bulk\{log,str}\RUN109_ndsub5e15_seb1000_COMPLETE__*`
  （3 log + 19 STR，`skipped=0`）。

## 5. 判据结论(到站后填)

**COMPLETE / POSTPROCESSED：路径重分配、仍不充分。**

- 静态真实到 `1000.000000 V`，源/漏
  `Jt=-4.893687862e-16/-1.857216357e-15 A/µm`；
- 自然到 `100 µs`，`ATLAS 5.40.0.R finished`；
  `Taking smaller bias=0`、`Cannot trap=0`、硬错误 0；
- 源积分 `2.430824596 pC/µm`，相对目标 `+0.322309%`，PASS；
- `Id_peak=6.5323271e-4 A/µm @31 ps`，
  `Tmax_peak=391.9161127 K @695.507 ps`；
  100 µs 为 `Id=2.040481659e-7 A/µm / Tmax=374.1166569 K`；
- VictoryExtract `80/80 CSV`、`Command Error=0`；
- 相对 RUN096，RUN109 在 50 ns 的浅/深路径为
  `3.2806×/2.6950×`，但端电流仅 `1.0070×`；到 100/500 ns，
  深路仍为 `3.2193×/3.0103×`，浅路降为
  `0.1559×/0.1624×`，端电流为 `0.9942×/0.9713×`。

因此 `Nd_sub` 只保留为路径分配敏感轴，不再作为 Wang 持续电流缺失的
主因；高场 `VSAT(T)` 和空穴迁移率温变因“持续首尾接通路径”门未满足，
本轮不开放生产 OFAT。
