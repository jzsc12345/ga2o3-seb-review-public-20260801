# RUN096_wang1000-nofp-lgd9-x11-hfo2hc — V4.1 only: add verified HfO2 HC.STD and quantify the temperature/solver change relative to RUN095

> **FROZEN_PRODUCTION_BASELINE — 2026-07-31 用户冻结。**
> 本 RUN 是当前权威生产停止点；原始 deck、结果、SHA 与归档只读保留。
> 既有 RUN097–RUN101 不得覆盖或反向改写本基线；新实验只能直接从本 RUN 派生。

- 日期:2026-07-30 10:46 | git:16c8369 | deck:`decks\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in` (sha256:786ea68542aa2356)
- 远端:`/root/DECKBUILD/runs/RUN096_wang1000-nofp-lgd9-x11-hfo2hc/` | tmux:`deck_RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long` | 看板:`outputs\RUN096_hfo2hc_live\screenshots\`

## 1. 目标与判据(发射前填)

V4.1 only: add verified HfO2 HC.STD and quantify the temperature/solver change relative to RUN095

判据：

1. `MODELS PRINT` 必须把 region 2/HfO2 从 `Cap.Model=NONE` 改为
   `HC.STD`，并打印 `HC.A/B/C/D=4.0/4.5e-4/0/-1.1e4`；
2. 100 ps/400 ps/1 ns 的 Id、impact、hole、Joule 仍应与 RUN095
   同量级；若电学轨迹改变，不能把温差只归于 HfO2 热容；
3. 报 `Tmax_peak`、x=11 径迹温度、0.5/1/10/100 us 长尾与求解器
   重试数；不预押温度必须升或降；
4. 该 SMDB 多项式的来源拟合范围是 200–400 K。若任何 HfO2 节点超过
   400 K，结果必须标为“外推敏感性”，不能写成高温参数已验证。

## 2. 与上一 RUN 的差异(发射前填)

单变量:HfO2 heat capacity only: Cap.Model NONE -> HC.STD(4.0,4.5e-4,0,-1.1e4)
deck diff 全部行:
```diff
 material region=2 permittivity=25.0 \
-         tcon.const tc.const=0.023
+         tcon.const tc.const=0.023 \
+         hc.std hc.a=4.0 hc.b=4.5e-4 hc.c=0.0 hc.d=-1.1e4
```

机器审计：

- RUN095/RUN096 有效语句 `298/299`；
- 输出标签归一化并移除上面唯一新增行后，两个 deck 逐字相同；
- 旧 impact 三数、`p型2e6`：0 命中；
- SHA256：
  `786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5`。

⚠ 物理模型改动：**有且只有 HfO2 热容**。用户本轮明确授权五小时按
推荐顺序自主推进；本 RUN 是审计 §10 V4.1 的既定单变量，不附带
`^BOUNDARY`、结构、热源、热导率、Fe、impact、mobility 或 LET 改动。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图（与 RUN095/RUN094 字节同源）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN094_wang1000-nofp-lgd9-x11-reference\figs\RUN094_preflight_structure.png`
- 网格图（同一 11672 points / 22992 triangles / 0 obtuse）：
  `D:\SILVACO_LOCAL\outputs\runs\RUN094_wang1000-nofp-lgd9-x11-reference\figs\RUN094_preflight_track_mesh.png`
- 实机结构截图：
  `D:\SILVACO_LOCAL\outputs\runs\RUN094_wang1000-nofp-lgd9-x11-reference\shots\RUN094_actual_structure_gui.png`
- 数值证据：
  - `D:\knowledge\material_sil\hfo2:21-32`：SMDB 原始 XML；
  - `D:\knowledge\pdf25\atlas_users1.pdf` pp.607–608：
    `C(T)=HC.A+HC.B*T+HC.C*T^2+HC.D/T^2`，单位 J/cm3/K；
  - RUN090/095 实际打印 HfO2 `Cap.Model=NONE`。
- 发给用户时间:10:46–10:49 | tmux 会话:
  `deck_RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long`

## 4. 结果索引

- 主图：
  `D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\figs\RUN095_096_hfo2hc_comparison.png`
- 同时间点电流/温度：
  `D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\csv\RUN095_096_hfo2hc_milestones.csv`
- HfO2中线/界面/径迹温度摘要：
  `D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\csv\RUN095_096_hfo2hc_spatial_summary.csv`
- 24份 VictoryExtract 原始 cutline：
  `D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\csv\spatial\`
- 本地轻量日志：
  `D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\logs\`
- 最终实机截图：
  `D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\shots\RUN096_final_structure_gui.png`
- 大文件归档：`E:\silvaco2425\bulk\log\RUN096_wang1000-nofp-lgd9-x11-hfo2hc__*`
  共3件；`E:\silvaco2425\bulk\str\RUN096_wang1000-nofp-lgd9-x11-hfo2hc__*`
  共19件；`skipped=0`。

## 5. 判据结论

**状态：COMPLETED_AND_POSTPROCESSED。** 10:47:55 发射，13:15:39
自然到100 us；ATLAS `finished`、硬错误0、静态偏置折半0、瞬态缩步77。
wrapper仍没有打印`simulator exits with code`，所以本报告只声明
“ATLAS finished + 0 hard error”，不补写不存在的封装退出码PASS。
源面积-时间积分为 `1.52057066196291e11 cm^-1`，对应
`2.436222785 pC/um`，相对目标2.423015 pC/um为 `+0.5451%`。

运行时 `Thermal Parameters` 表明确验收 region 2/HfO2：

```text
Cap. Model   : ... HC.STD ...
Spec. Heat a : ... 4 ...
Spec. Heat b : ... 0.00045 ...
Spec. Heat c : ... 0 ...
Spec. Heat d : ... -1.1e+04 ...
```

RUN095/RUN096的峰值对照：

| 指标 | RUN095 Cap.NONE | RUN096 HC.STD | 变化 |
|---|---:|---:|---:|
| Id峰值 | 6.711362588e-4 A/um @31 ps | 6.711164427e-4 A/um @31 ps | -0.00295% |
| Tmax峰值 | 405.978439 K @0.683161 ns | 394.152269 K @0.685934 ns | **-11.826171 K** |
| 100 ps Tmax | 331.690665 K | 325.989607 K | -5.701057 K |
| 400 ps Tmax | 385.693504 K | 374.469401 K | -11.224103 K |
| 1 ns Tmax | 373.256462 K | 366.831870 K | -6.424592 K |
| 100 us Tmax | 378.924582 K | 378.680783 K | -0.243799 K |

空间证据更直接：400 ps的HfO2中线最高温度由354.428 K降到334.005 K
（-20.423 K），Ga2O3界面下由382.095 K降到372.395 K（-9.700 K），
而x=11 um离子径迹最大温差只有-0.000791 K。电流曲线在所有里程碑的
差异不超过约0.15%，说明这个温差可以归于HfO2热容，而不是电学轨迹换支。

整个RUN096的全局Tmax也只有394.152 K，因此HfO2节点不可能超过400 K，
SMDB多项式没有越出其200–400 K拟合范围。HfO2热容的作用是给顶部热点
增加热惯性、压低早期峰值；它没有加热源，也没有把粒子柱接成持续源漏
电流丝。故 **“HfO2热容缺失导致论文约1715 K差距”根因分支关闭**，
器件分类仍是恢复型SET包络加陷阱延迟反弹，不是Wang式持续SEB。

转录里有19次120 K和2次5000 K试探，均伴随缩步拒绝；395个正式接受
SSF点的最低Tmin为298.748 K@0.726 ns，从未接受120 K解。因此A/B裁决
仍为 **A类Newton伴随下冲**，不是B类错误热边界收敛。

零ATLAS后处理：

- `D:\SILVACO_LOCAL\decks\RUN095_096_hfo2hc_spatial.in`：
  8次STR load、24条profile、24/24 CSV成功、Command Error=0；
- `D:\SILVACO_LOCAL\scripts\analyze_run095_096_hfo2hc.py`：
  已运行并生成上面的CSV/PNG。
