# RUN119 A14 预检合同与机器核对

> 编制日期：2026-07-31  
> A13：**PASS（用户已核签 `Nd_UID=1.0e16 cm^-3` 首臂）**  
> A14：**INCOMPLETE / BLOCKED**  
> 网格：**MESH_TOPOLOGY_UNVERIFIED**  
> 发射门：**LAUNCH_GATE_CLOSED**  
> 本轮边界：只编制本地 deck 与 A14 文件；未上传，未运行 DevEdit、ATLAS、VictoryExtract 或 tmux。

## 1. 母线、候选与唯一变量

| 项目 | 值 |
|---|---|
| 母线 deck | `D:\SILVACO_LOCAL\decks\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in` |
| 母线 SHA-256 | `786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5` |
| 候选 deck | `D:\SILVACO_LOCAL\decks\RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns.in` |
| 候选 SHA-256 | `55FCFAEEA7D73C54535D303A34072BE73E25BBB5A7E5D810838AED18045B1DC9` |
| 唯一物理变量 | `set nd_uid = 5.0e15 → 1.0e16 cm^-3` |
| UID 厚度 | `0.20 µm`，冻结 |
| 机械改动 | 输出前缀改为 RUN119；在 `t500ns.str` 后删除 1–100 µs 执行尾巴；保留 `log off`、源积分 EXTRACT、`quit` |

物理命题不是“界面已经证实堵塞”，而是：UID 可电离 donor 库存是否限制了离子后浅层通路的持续供电子能力。中心点直接复用 RUN096，本臂只做 `2×` 敏感性。

## 2. A14 四件状态

| # | A14 件 | 本地文件或保留值 | 裁决 |
|---|---|---|---|
| 1 | 结构图 | `D:\SILVACO_LOCAL\outputs\runs\RUN119_wang1000-uidnd1e16-short500ns\figs\RUN119_A14_structure_REFERENCE_RUN096_geometry_unchanged.png` | **REFERENCE ONLY**：RUN096 几何血统图；几何命令未变，但不是 RUN119 候选实建证据 |
| 2 | 网格图 | `D:\SILVACO_LOCAL\outputs\runs\RUN119_wang1000-uidnd1e16-short500ns\figs\RUN119_A14_mesh_INTENT_REFERENCE_topology_unverified.png` | **UNVERIFIED**：仅表示 RUN096 径迹区网格意图；不得冒充 RUN119 候选网格图 |
| 3 | 完整 deck diff | `D:\SILVACO_LOCAL\outputs\runs\RUN119_wang1000-uidnd1e16-short500ns\logs\RUN096_RUN119_full_deck_diff.md` | **PASS**：原始文本完整 diff 已落盘；逻辑命令机器核对见 §3 |
| 4 | tmux 会话名 | `deck_RUN119_Wang2026_nofp_Lgd9_x11_uidNd1e16_SEB_1000V_short500ns` | **RESERVED ONLY**：名称已冻结，但会话未创建、未启动 |

两张参考图的 SHA-256：

- 结构参考：`9116F8398F8B63D2046704CC1B357AA333CD9DE08D006CCD7F225F02AB511B76`
- 网格意图参考：`B38FDA192E4CBBE99F1ABAD9379A3221C6EE8F31A764374F23F56FA85D0F42C0`

它们与 RUN094/RUN096 血统源图逐字节相同。复制是为了让 A14 包自足，不是为了制造候选运行证据。

## 3. 归一化 deck 合同机检

检查方法：去除空行与注释、拼接反斜杠续行、压缩空白；从 RUN096 删除 `t500ns.str` 与下一条 `log off` 之间的真实 10 条尾部命令；再把 RUN119 输出前缀、EXTRACT 名和 `nd_uid` 反向映射为 RUN096 值，做逐命令序列比较。

| 检查项 | 实测 | 期望 | 结果 |
|---|---:|---:|---|
| RUN096 逻辑命令 | 183 | 183 | PASS |
| 删除的 500 ns 后命令 | 10 | 10 | PASS |
| 截断后 RUN096 逻辑命令 | 173 | 173 | PASS |
| RUN119 逻辑命令 | 173 | 173 | PASS |
| 允许变换反向映射后序列 | 完全一致 | 完全一致 | PASS |
| 0–500 ns `solve tstop=` | 22 | 22 | PASS |
| RUN119 输出前缀出现次数 | 20 | 20 | PASS |
| mobility 卡 | 5 | 5 | PASS |
| 常数 `vsatn/vsatp=2e7, betan/betap=7.52` 卡 | 5 | 5 | PASS |
| impact 卡 | 5 | 5 | PASS |
| region 7 Fe acceptor trap | 1 | 1 | PASS |
| `log off` / EXTRACT init / 面积分 / `quit` | 2 / 1 / 1 / 1 | 2 / 1 / 1 / 1 | PASS |
| `t500ns.str` 后下一条有效命令 | `log off` | `log off` | PASS |

实际删除的 RUN096 尾部命令为：

```text
solve tstop=1e-6 dt=1e-8 previous
save outfile="..._t1us.str"
solve tstop=2e-6 dt=1e-7 previous
solve tstop=5e-6 dt=2e-7 previous
solve tstop=10e-6 dt=5e-7 previous
save outfile="..._t10us.str"
solve tstop=20e-6 dt=1e-6 previous
solve tstop=50e-6 dt=2e-6 previous
solve tstop=100e-6 dt=5e-6 previous
save outfile="..._t100us.str"
```

注意：早期审查摘要曾误写这组尾部步长；本合同以 RUN096 实物逐命令读取结果为准。

## 4. 禁用项与冻结项

在有效命令中机器检索以下禁用项，命中数均为 0：

```text
F.VSATN
.lib
ALPHAN.FLD / THETAN.FLD / TNOMN.FLD
以及任意 VSATN.FLD / VSATP.FLD / BETAN.FLD / BETAP.FLD
INTERFACE
INTTRAP
THERMIONIC
QF=
S.S CHARGE
p.type doping
旧 impact: an=2.5e6 / bn=3.96e7 / impact betan=1.37
p-type 2e6
```

冻结项仍保留：RUN096 常数 VSAT 五区、五区 SELB impact、region 7 Fe 深受主、三热接触、`VDS=1000 V`、`xion=11 µm`、`B.DENSITY=0.4529 pcunits`、T0/TC、求解器与全部 0–500 ns 时间步。

## 5. 为什么发射门仍关闭

RUN096 deck 只有 `imp.refine min.spacing=0.020`，没有显式 `imp.refine impurity=Donors sensitivity=...`。因此，不能仅凭 deck 文本断言 donor 值翻倍一定改变网格；反过来，手册与文本也不能证明候选节点坐标和三角连接必然逐点相同。候选结构尚未由 DevEdit 实建，节点数、坐标与连接表都不存在，所以 A13 规定的网格拓扑硬门尚无可核对对象。

这一步像“图纸尺寸没改，但还没把零件加工出来”：可以确认设计意图冻结，却不能拿旧零件照片证明新零件的孔位一模一样。因此本包必须保持：

```text
A14_INCOMPLETE
MESH_TOPOLOGY_UNVERIFIED
LAUNCH_GATE_CLOSED
```

下一次若用户另行授权，只允许先做 **DevEdit-only 候选网格预检**，生成候选结构图与网格图并比较 RUN096 的节点数、坐标和三角连接；在这项 PASS 且 A14 再次由用户点头前，仍不得运行 ATLAS。
