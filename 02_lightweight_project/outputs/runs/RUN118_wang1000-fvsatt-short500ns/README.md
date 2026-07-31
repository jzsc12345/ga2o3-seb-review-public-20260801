# RUN118_wang1000-fvsatt-short500ns — 冻结RUN096，仅验证已通过parser的电子F.VSATN(T)对1000V SEB至500ns的影响

- 日期:2026-07-31 18:57 | git:16c8369 | deck:`decks\RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_short500ns.in` (sha256:0b869d3aff31789d)
- 远端:`/root/DECKBUILD/runs/RUN118_wang1000-fvsatt-short500ns/` | tmux:`deck_RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_short500ns`（已自然结束） | 归档:log3/str16/skipped0

## 1. 目标与判据(发射前填)

冻结RUN096，仅验证RUN117已通过parser/binding的电子F.VSATN(T)对1000V SEB
至500ns的影响。启动门、源电荷门、非主因/方向否决/升级/数值有效性六道判据
全部预注册在A13 §6；运行后不得换门槛挑结果。

## 2. 与上一 RUN 的差异(发射前填)

单变量：regions3–7电子`VSATN=2e7`常数→RUN117验证的`F.VSATN(T)`；
500ns后执行截断是非物理差异。完整、不省略diff：
`logs\RUN096_RUN118_full_deck_diff.md`，SHA=
`F5A6EE135B72E0D0859274E4A724A906F9E69A36F4D4E6AE267ECC7E41F319CD`。

⚠ 物理模型改动：有，仅五区电子高场VSAT模型族；结构、LET、Fe、impact、
热模块、solver与0–500ns时间表冻结。用户已按四SHA核签，且只发射一次。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图：`figs\RUN118_preflight_structure_RUN096_identical.png`，SHA=`9116F839…B511B76`
- 网格图：`figs\RUN118_preflight_track_mesh_RUN096_identical.png`，SHA=`B38FDA19…0F42C0`
- 全量diff：`logs\RUN096_RUN118_full_deck_diff.md`
- tmux：`deck_RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_short500ns`
- A13：`docs\plans\RUN118_A13_FVSATN_500NS_物理核签_20260731.md`
- 状态：2026-07-31 18:59编制完成；19:13正规发射，20:36自然到500ns并完成EXTRACT。

## 4. 结果索引(到站后填)

- `logs\RUN118_preflight_contract.md`：十道合同门、四SHA、远端零写入证据。
- `logs\RUN096_RUN118_full_deck_diff.md`：248行全量diff。
- `logs\RUN118_result.md`：六道裁决门、精确三时刻表、数值有效性与基础设施留痕。
- `figs\RUN096_118_fvsatn_terminal_overlay.png`：Id/Tmax/Joule全时域叠图。
- `csv\RUN096_118_fvsatn_{milestones,peaks}.csv`：轻量数值表。
- 二维路径图/CSV：`outputs\reports\RUN096_118_fvsatn_topology_20260731\`。
- 大文件已归档：`E:\silvaco2425\bulk\{str,log}\RUN118_wang1000-fvsatt-short500ns__*`。

## 5. 判据结论(到站后填)

`DIAGNOSTIC_COMPLETE / NUMERICAL_VALIDITY_GATE_FAIL_120K_TRIALS /
NO_FORMAL_PHYSICS_CAUSATION / NO_LONG_RUN_UPGRADE`。

解析绑定、1000V、源电荷和500ns到站均PASS；但15次120K Newton试探触发
A13 §6.6字面失败。所有120K点都被缩步拒绝，接受解最低296.210K，因此是
A类收敛伴随现象，不是错误热边界的B类收敛解。诊断上100/500ns的Id、Tmax、
Joule与signed路径均只变化千分之一级，F.VSATN(T)不像约1100K温差的主因，
但本轮不据此申请长跑或第二变量。详见`logs\RUN118_result.md`。
