# RUN119 — UID donor 2× 敏感性臂（网格门 PASS，ATLAS 未发射）

> 状态：**STATIC_GATE_FAIL / STOPPED_BY_A13 / NO_VALID_TRANSIENT / UID_DONOR_ROUTE_CLOSED**  
> 日期：2026-07-31  
> DevEdit 预检目录：`/root/DECKBUILD/preflight/RUN119_uidNd1e16_mesh/`，**已完成**  
> ATLAS 生产目录：`/root/DECKBUILD/runs/RUN119_wang1000-uidnd1e16-short500ns/`，**已创建**  
> ATLAS tmux：`deck_RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns`，**2026-07-31 23:51 启动；2026-08-01 00:09 按静态门止损**

## 1. 目标与 A13 核签

本轮只检验一个问题：把 UID 的 n 型背景施主从 `5.0e15` 提高到 `1.0e16 cm^-3`，是否会增强单粒子后浅层电子通路的持续供电子能力。UID 厚度保持 `0.20 µm`；RUN096 作为 `1×` 中心对照，本候选是 `2×` 首臂。用户已授权编制 deck 与 A14 包，但明确禁止本轮发射。

- A13 核签书：`D:\SILVACO_LOCAL\docs\plans\RUN119_A13_UID_sheetdose_对抗核签_20260731.md`
- 母线：`D:\SILVACO_LOCAL\decks\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in`
- 母线 SHA-256：`786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5`
- 候选：`D:\SILVACO_LOCAL\decks\RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns.in`
- 候选 SHA-256：`55FCFAEEA7D73C54535D303A34072BE73E25BBB5A7E5D810838AED18045B1DC9`

## 2. 与 RUN096 的差异

唯一物理改动：

```diff
-set nd_uid      = 5.0e15
+set nd_uid      = 1.0e16
```

允许的机械改动只有 RUN119 输出前缀，以及在 `t500ns.str` 后删除 1–100 µs 执行尾巴，同时保留 `log off`、源积分 EXTRACT 与 `quit`。完整原始 diff 和归一化逐命令核对分别见：

- `logs\RUN096_RUN119_full_deck_diff.md`
- `logs\RUN119_preflight_contract.md`

物理模型没有新增或删减：常数 VSAT、impact、Fe trap、`lat.temp heat.full joule.heat gr.heat pt.heat`、材料参数、热边界、单粒子源和 solver 均冻结。

## 3. A14 四件

| A14 件 | 本地内容 | 状态 |
|---|---|---|
| 结构图 | `figs\RUN119_A14_structure_CANDIDATE_actual_devedit.png` | PASS：RUN119 候选 STR 实建图 |
| 网格图 | `figs\RUN119_A14_mesh_CANDIDATE_actual_topology.png` | PASS：候选全网格与 x=11 µm 径迹区实图 |
| 完整 deck diff | `logs\RUN096_RUN119_full_deck_diff.md` | PASS |
| tmux 会话名 | `deck_RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns` | PASS：生产名已冻结；未创建、未发射 |

四个槽位现已齐备，状态为 **A14_READY_FOR_REVIEW**，等待用户核签后才能发射 ATLAS。原来的两张 `REFERENCE` 图保留作血统审计，不再作为 A14 当前证据。详细网格门结果见 `logs\RUN119_devedit_only_mesh_gate_contract.md`。

## 4. 运行与结果

用户另行授权后，仅运行了 DevEdit-only 网格预检：

- deck SHA：`FA2A015C860D4E15D3E3C5BEDAA71D47278019FCA3C5EB4421D2C71A35B8C6E1`，本地/远端一致；
- DevEdit：`11672` 点、`22992` 三角、`0` 钝角、`0` error、`0` warning；
- 候选与 RUN096 的全部 `11672` 条 `c` 坐标行逐行相同，拓扑 SHA 均为 `60CB95F51D4F21F549A08D503A10A53E870DBFBF23BE58BAF26FCDE85BECF9E6`；
- 全部 `22992` 条 `t` 三角连接行逐行相同，拓扑 SHA 均为 `513D1624E1752873894833194316D1EE25860C9C721522ABECF3B6E1F38162E3`；
- 候选完整 STR SHA=`DB19FC9FDE43909C03952ECB961555412C9A9971D0E54009CC872752081BD73D`；完整文件与 RUN096 不同是 donor 场变化，不是网格漂移；
- 运行前、运行中、结束后 ATLAS 进程均为 `0`；DevEdit tmux 已自然消失；
- 大 STR 已归 `E:\silvaco2425\bulk\str\RUN119_wang1000-uidnd1e16-short500ns__RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_preflight_mesh.str`，未放入主控 D 盘。

## 5. 下一道门

DevEdit-only 网格门已经 PASS，A14 四件现可供核签。下一步若用户明确授权，才允许按冻结 SHA 发射一次 **1000 V、截至 500 ns 的 RUN119 ATLAS 严格单变量臂**；未经该授权，生产目录、tmux、偏压与单粒子源继续保持未启动。

## 6. 用户核签与发射前实时闸门

2026-07-31 23:50（UTC+08:00），用户明确核签当前 A14，并授权只发射一次冻结的 RUN119 1000 V、500 ns 严格单变量 ATLAS 臂。授权同时冻结以下止损规则：若 100 ns 与 500 ns 的持续电子通路、漏极电流/Joule 热没有形成同方向改善，立即关闭 UID donor 主因路线，不继续扫掺杂。

发射前现场复核：候选 deck SHA-256 仍为 `55FCFAEEA7D73C54535D303A34072BE73E25BBB5A7E5D810838AED18045B1DC9`；`check_layout.py` PASS；VM `SFLM_VERIFY=OK`、`RUNNING_ATLAS=0`、tmux 会话数 `0`；生产目录 `/root/DECKBUILD/runs/RUN119_wang1000-uidnd1e16-short500ns/` 不存在。故 A14 用户核签与机器闸门均已闭合，可以执行一次标准 tmux 发射；本段写入时尚未发射。

## 7. 唯一一次 ATLAS 发射

2026-07-31 23:51:31（UTC+08:00）通过 `/root/bin/vdoe_tmux.sh start-deck` 发射一次，远端上传 SHA 与核签 SHA 完全一致。启动后实测只有一个同名 tmux 会话、一个 `atlas` 主进程；网格仍为 `11672` 点、`22992` 三角、`0` 钝角。未创建任何第二臂，未改结构、LET、Fe、impact、热模块、solver 或时间步。三分钟截图看板已启动，首图为 `D:\SILVACO_LOCAL\outputs\RUN119_uidnd1e16_short500ns_live\screenshots\shot_20260731T235159_RUN119_1000V_UID2x.png`。

## 8. 静态门止损与最终裁决

静态漏压最后只收敛到 `878.9508057 V`，末态 `|Id|=6.807961192e-14 A/µm`；随后 Newton 50 次未收敛、bias cutback 共 16 次并打印 `Cannot trap`。DeckBuild 仍机械进入自热和 SINGLEEVENTUPSET，但真实母态不是 1000 V。按 A13 §9.1，agent 在不足 2 ps、首个 `t2ps.str` 尚未保存时精确停止；`t50ns/t100ns/t500ns` 全部不存在，故没有资格执行瞬态改善比值。

最终关闭 UID donor 主因路线，不跑 `0.5×`，不继续盲扫掺杂。该关闭理由是 `STATIC_INADMISSIBLE`，不是伪造的 100/500 ns 阴性。完整报告：`logs\RUN119_result.md`；静态轨迹：`figs\RUN119_static_gate_fail_878p950806V.png` 与 `csv\RUN119_static_gate_trace.csv`。3 log + 3 STR 已用标签 `RUN119_staticgate_fail_878p950806V` 归档到 `E:\silvaco2425\bulk\`，`skipped=0`；远端原件保留，tmux/ATLAS/watcher 均为 0。
