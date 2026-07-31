# RUN119 DevEdit-only 网格门禁合同

> 用户授权：2026-07-31，执行推荐的 DevEdit-only 候选网格预检。  
> 禁止项：ATLAS、偏压、粒子源、物理模型、瞬态求解。  
> 发射门：本文件只授权网格生成；RUN119 的 500 ns ATLAS 臂仍保持关闭。

## 1. 输入与运行身份

| 项目 | 冻结值 |
|---|---|
| 本地 deck | `D:\SILVACO_LOCAL\decks\RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_preflight_mesh_only.in` |
| deck SHA-256 | `FA2A015C860D4E15D3E3C5BEDAA71D47278019FCA3C5EB4421D2C71A35B8C6E1` |
| 远端目录 | `/root/DECKBUILD/preflight/RUN119_uidNd1e16_mesh/` |
| tmux 会话 | `deck_RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_preflight_mesh_only` |
| 候选 STR | `RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_preflight_mesh.str` |
| 基线 STR | RUN093 与 RUN096 两件，SHA-256 均为 `F6DB93FE38EEC6669B91EB4E5C25262F029AE41F5E3C6FD9CC84D4B070C12530` |

## 2. 发射前机器合同

- RUN093 与候选有效 DevEdit 命令数：`57 / 57`；
- 候选反向替换 `nd_uid=1.0e16 → 5.0e15` 与输出名后：命令序列逐项完全一致；
- 有效命令中 `go atlas`、`solve`、`singleeventupset`、`models`、`impact`、`trap`、`thermcontact` 命中数均为 `0`；
- 发射前 VM：tmux 会话 `0`，ATLAS 进程 `0`，目标目录不存在。

## 3. PASS 判据

本项目的 `simulator exits with code 0` 仍是 **ATLAS** 生产运行唯一完成判据。本次实际发现纯 DevEdit deck 不打印该 ATLAS 专用短语，冻结先例 RUN093 也同样只打印 `Parse complete / Error(s)=0 / Warning(s)=0`，且 `EXIT.txt` 为空。因此纯 DevEdit 门采用同血统可证伪判据：tmux 自然消失、无 DevEdit/ATLAS 残留进程、`Parse complete`、`0 error / 0 warning`、目标 STR 存在，再比较候选 ASCII STR 的：

1. `c` 行数量及整行序列（节点编号、x/y 坐标、标志）；
2. `t` 行数量及整行序列（三角编号、region、三节点与邻接）；

必须与字节一致的 RUN093/RUN096 基线逐行完全相同。任一不一致均保持
`MESH_TOPOLOGY_UNVERIFIED / LAUNCH_GATE_CLOSED`，不得启动 ATLAS。

## 4. 运行与拓扑结果

| 检查项 | RUN096 基线 | RUN119 候选 | 裁决 |
|---|---:|---:|---|
| 点数 | 11672 | 11672 | PASS |
| 三角数 | 22992 | 22992 | PASS |
| 钝角 | 0 | 0 | PASS |
| DevEdit error / warning | 0 / 0 | 0 / 0 | PASS |
| `c` 坐标行 SHA-256 | `60CB95F5…F9E6` | `60CB95F5…F9E6` | **逐行完全相同** |
| `t` 三角行 SHA-256 | `513D1624…62E3` | `513D1624…62E3` | **逐行完全相同** |

候选完整 STR SHA-256 为 `DB19FC9FDE43909C03952ECB961555412C9A9971D0E54009CC872752081BD73D`。它与基线完整 SHA 不同，原因是区域 donor 数据改变；几何坐标与三角连接已被单独抽出并逐行证明一致。

实际候选图：

- `D:\SILVACO_LOCAL\outputs\runs\RUN119_wang1000-uidnd1e16-short500ns\figs\RUN119_A14_structure_CANDIDATE_actual_devedit.png`
- `D:\SILVACO_LOCAL\outputs\runs\RUN119_wang1000-uidnd1e16-short500ns\figs\RUN119_A14_mesh_CANDIDATE_actual_topology.png`

最终状态：`MESH_TOPOLOGY_PASS / A14_READY_FOR_REVIEW / ATLAS_LAUNCH_GATE_CLOSED`。本次没有运行 ATLAS、没有爬压、没有打粒子，也没有产生任何单粒子物理结果。
