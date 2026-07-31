# RUN094_wang1000-nofp-lgd9-x11-reference — 按Wang20um无场板Lgd9参考几何复核1000V热失控，物理参数冻结RUN092

- 日期:2026-07-30 06:18（07:05 首发因 region 编号越界主动停机；07:08 纯编号修复） | git:16c8369 | deck:`decks\RUN094_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_long.in` (sha256:29fb39364296a784)
- 远端:`/root/DECKBUILD/runs/RUN094_wang1000-nofp-lgd9-x11-reference/` | tmux:`deck_RUN094_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_long`（已结束） | 看板:`outputs\RUN094_nofp_Lgd9_live\screenshots\`

## 1. 目标与判据(发射前填)

在 VGS=0 V、VDS=1000 V、xion=11 µm 下，检验 Wang 论文的
20 µm / 无场板 / Lgd=9 µm 几何是否能把 RUN092 的局域热 SET 推入持续
电热正反馈。物理参数全部冻结 RUN092。

判据：
1. 100 ps/400 ps/1 ns 的 impact、hole、Jtotal、Joule 与温度热点是否形成
   从 x≈11 打击柱到 x≈9 栅右缘的连续导电路径；
2. 100 ns 前 `Id` 是否保持或再上冲，而不是 RUN092 的 1.3 ns 后衰减；
3. 0.5/1/10/100 µs 仍按账本 C5/C6 联合判，温度不能单独定性；
4. PHOTOGEN 积分电荷须在 2.423015 pC 的 ±5% 内。

## 2. 与上一 RUN 的差异(发射前填)

单变量:lateral geometry only: Lgd20+FP11 -> Lgd9+noFP
deck diff 全部行:
```diff
-set x_dev=31.0
+set x_dev=20.0
-set x_drn_imp_l=28.0
+set x_drn_imp_l=17.0
-set x_drn_l=29.0
+set x_drn_l=18.0
-region id=10 name=gate_fp ... x=9..11 y=-0.42
-contact name=gate_fp ... common=gate
-probe name=Field_FP_End ...
+# no field-plate region/contact/probe
-probe Tdrain x=30; probe Tbottom x=15.5
+probe Tdrain x=19; probe Tbottom x=10
```

其余 diff 只有 RUN 编号和输出文件名隔离。`git diff --no-index` 已现场复核：
material/mobility/impact/trap/models/method/thermcontact/singleeventupset/
solve 时间表均没有参数变化。禁用旧 impact 三数与 `p型2e6` 均为 0 命中。

⚠ 物理模型改动：无。唯一物理变量是论文参考 lateral geometry。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图:`figs\RUN094_preflight_structure.png`
- 网格图:`figs\RUN094_preflight_track_mesh.png`
- 实机截图:`shots\RUN094_actual_structure_gui.png`
- exact preflight 来源：RUN093 同结构 DevEdit-only 实跑，11672 points /
  22992 triangles / 0 obtuse / 0 error / 0 warning，无 RUN093 ATLAS。
- RUN093 与 RUN094 的 `go devedit`→首个 `structure outfile` 有效语句
  归一化后 `60/60` 逐字相同；不是拿相似结构图冒充正式 deck 预检。
- full deck SHA256:
  `29FB39364296A7841F6B769B471EBE99A1372074181C484D7A5DD87A03B6DB2B`
- 发给用户时间:06:16（RUN093 实机图） | 计划 tmux:
  `deck_RUN094_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_long`
- 发射闸门：当前 RUN092 是唯一 ATLAS 任务；为避免两个 P4 热瞬态相互争抢，
  RUN092 到达可判长尾或退出后再发射 RUN094。

## 4. 结果索引(到站后填)

- `csv\RUN092_094_geometry_reference_full_curve.csv`：RUN092/094 全时域同轴对照。
- `csv\RUN092_094_geometry_reference_milestones.csv`：20 ps–100 µs 里程碑。
- `csv\RUN092_094_geometry_reference_spatial_peaks.csv`：六时刻三剖面的峰值与坐标。
- `csv\RUN094_final_metrics_and_screen.csv`：最终数值、反弹量与机械标签。
- `csv\spatial\`：VictoryExtract 36 个轻量 cutline CSV，100 ps/400 ps/
  1 ns/10 ns/1 µs/100 µs × RUN092/094 × surface/UID-sub/track。
- `figs\RUN092_094_geometry_reference_full_curve.png`：全曲线与累计端口能量。
- `figs\RUN092_094_100ps_surface_compare.png`：100 ps 近界面六物理量。
- `figs\RUN092_094_surface_temperature_evolution.png`：六时刻温度空间演化。
- `figs\RUN092_094_surface_current_evolution.png`：六时刻 Jtotal 空间演化。
- `figs\RUN092_094_trap_rebound_audit.png`：带电 Fe/电子/Jtotal 关联。
- 后处理脚本：
  `D:\SILVACO_LOCAL\scripts\analyze_run092_094_geometry_reference.py`
- 大文件：3 log + 19 STR 已归档到
  `E:\silvaco2425\bulk\{log,str}\RUN094_wang1000-nofp-lgd9-x11-reference__*`。
- 远端后处理：
  `/root/DECKBUILD/postproc/RUN092_094_geometry_reference/`（36 CSV，0 error）。

## 5. 判据结论(到站后填)

07:05 首发时 ATLAS 明确报告
`Specified region index out of range`：删除场板后总 region 数是 10，但衬底的
material/mobility/impact/trap 仍引用 11。该次运行在 `solve` 前主动停止，转录已保留为
`logs\typescript_attempt1_region11_invalid.txt`，也复制到
`E:\silvaco2425\bulk\log\RUN094_wang1000-nofp-lgd9-x11-reference\`。
当前仅把衬底/源/漏/栅连续重编号为 7/8/9/10，所有数值和物理语句均未改变；
修复后的 RUN093 DevEdit 复验仍为 11672 点、0 error、0 warning。

**正式运行：COMPLETE。**

- `Id_peak=6.71170e-4 A/µm @31 ps`；
- `Tmax_peak=405.902 K @0.67284 ns`；
- 100 ps/400 ps 的电流和 impact 显著高于 RUN092，但到 1 ns
  `Id=2.7772e-6 A/µm`，比 RUN092 低约 35 倍；
- 4 ns→16.25 ns 出现 269×延迟电流反弹，但绝对峰仅
  `1.1779e-5 A/µm`，没有热失控；
- `Id(0.5/1/10/100 µs)=6.5730e-7/5.5575e-7/3.8627e-7/
  2.1875e-7 A/µm`；
- `Tmax(0.5/1/10/100 µs)=319.143/315.045/322.397/378.877 K`；
- 机械标签：
  `RECOVERABLE_SET_ENVELOPE_WITH_DELAYED_TRAP_REBOUND_NOT_10X_DARK`。

数值门：0 偏置折半、69 次瞬态缩步、4 次被拒绝的温度越界试探、
0 `ERROR #`、0 `Command Error`；`ATLAS version 5.40.0.R finished at
Thu Jul 30 08:42:26 2026`。`AreaTimeInt=1.52057067e11 cm⁻¹`
（2.43622 pC/µm）。wrapper 仍没有 `simulator exits with code`，
因此只报告完整结束链，不伪造 exit-code PASS。
