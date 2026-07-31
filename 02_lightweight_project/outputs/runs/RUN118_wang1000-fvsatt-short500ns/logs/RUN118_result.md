# RUN118 结果裁决：高场电子 `F.VSATN(T)` 500 ns 严格单变量烟测

## 0. 一句话结论

RUN118 已按用户核签的四个 SHA **只发射一次并自然到达 500 ns**。解析绑定、
1000 V 静态母态、离子源电荷和到站门都通过；但是瞬态中出现 15 次被缩步拒绝的
120 K Newton 试探，因此按预注册 A13 §6.6，正式状态只能是：

```text
DIAGNOSTIC_COMPLETE / NUMERICAL_VALIDITY_GATE_FAIL_120K_TRIALS
NO_FORMAL_PHYSICS_CAUSATION / NO_LONG_RUN_UPGRADE
```

被接受的解从未收敛到 120 K，最低值是 `296.2101887 K @ 0.728063863 ns`，
所以这是 A 类“Newton 试探下冲”，不是 B 类“热边界把器件真的算冷到 120 K”。
诊断数值仍很清楚：端电流、焦耳热、温度和二维导电丝均与 RUN096 几乎重合，
高场电子 `VSAT(T)` **不像** Wang 温差约 1100 K 的主因；但由于数值有效门失败，
这里不把“很不像”升级成正式因果关闭。

## 1. 冻结合同与实际执行

用户核签四件：

| 文件 | SHA-256 |
|---|---|
| `decks\RUN118_ga2o3_vsatn.c` | `F122D78C98A1C5BBD9F95C28ED909FF90BFE2A6F41F7BE329001F9FEA28BA03C` |
| `decks\RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_short500ns.in` | `0B869D3AFF31789D6D0C29E813016C964282BF41AB24819EF503DB99AE4906CE` |
| `scripts\run118_vsatn_ctypes_check.py` | `B3D34898D2919AAF5E82DB7D40A92E078E8DA2CBB10078F139BA941490031397` |
| `scripts\run118_contract_check.py` | `AEBE769DFDE46D155EE71F955C6161F8C8E07C40BE920B588C36395872F404E0` |

远端运行箱：
`/root/DECKBUILD/runs/RUN118_wang1000-fvsatt-short500ns`。唯一发射会话：
`deck_RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_short500ns`。
结构、网格、LET、Fe、impact、热模块、solver 与 0–500 ns 的时间表均冻结；
唯一物理变量是 regions 3–7 的电子 `VSATN=2e7` 常数换成 RUN117 已验证的
`F.VSATN(T)` 回调。

## 2. 六道预注册门逐项裁决

| A13 门 | 实测证据 | 裁决 |
|---|---|---|
| 解析/绑定 | 两轮 summary 各 5/5 显示 `Using interpreter function for Vsat`；`.lib` 路径命中；SCI/CPP/glibc fatal=0；GaN `1.91e7`=0；静态日志最后一行真实 `VDS=1000 V` | PASS |
| 源项电荷 | `AreaTimeInt_cmInv_RUN118=1.52057107956609e11 cm^-1` → `Q=2.436223454017 pC/µm`，相对 2.423015 为 `+0.545125%`，落在 ±5% 窗 | PASS |
| 到站 | `t500ns.str` 存在；EXTRACT 完成；`ATLAS version 5.40.0.R finished` | PASS |
| 非主因 | 100/500 ns 的 `|ΔId|<0.075%/0.010%`、`|Δsigned path|<0.013%/0.016%`、`|ΔTmax|<0.038/0.019 K` | 诊断满足，但被数值门覆盖 |
| 升级 | 100/500 ns 没有任何两项增加 ≥10%，Tmax 也没有增加 ≥5 K | FAIL，不准长跑 |
| 数值有效性 | 15 次 `Updated temperatures exceeding limits` 均显示试探 `Lattice Minimum=120 K`，紧跟 `Will repeat with smaller time-step`；接受解 Tmin 最低 296.210 K | **FAIL（按 A13 字面）** |

方向否决门不严格成立：Id 与 JouleMax 略降，但 signed 路径容量略升
`+0.0125%/+0.0160%`，不能把数值噪声硬说成方向一致的负反馈。

## 3. 精确三时刻结果

所有值均来自日志中**恰好等于** 50/100/500 ns 的已接受行，不用邻点插值。

| t | RUN118 Id (A/µm) | 相对 RUN096 | RUN118 Tmax (K) | ΔT (K) | RUN118 JouleMax | 相对 RUN096 | signed 路径 (A/cm²) | 相对 RUN096 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 ns | `5.446813375e-6` | `−0.12745%` | `342.1265285` | `−0.05460` | `1.224255504e11` | `−0.22033%` | `190.256054` | `+0.31658%` |
| 100 ns | `2.249493174e-6` | `−0.07495%` | `332.2847280` | `−0.03776` | `5.105289369e10` | `−0.12928%` | `62.8096234` | `+0.01251%` |
| 500 ns | `6.572038402e-7` | `−0.00941%` | `319.1057016` | `−0.01846` | `1.490774977e10` | `−0.03760%` | `13.6085593` | `+0.01598%` |

全曲线峰值：

- RUN096：`Id_peak=6.711164427e-4 A/µm @31 ps`，
  `Tmax_peak=394.1522685 K @0.685934316 ns`；
- RUN118：`Id_peak=6.689374046e-4 A/µm @31 ps`，
  `Tmax_peak=392.9155126 K @0.696612964 ns`；
- RUN118 峰温反而低 `1.236756 K`，不是向 Wang 高温靠近。

## 4. 二维电流路径：形态没有重排

VictoryExtract 只读现成 STR，50/100/500 ns 共完成：

- HEATMAP：RUN096+RUN118 共 12 个 CSV；
- 原生顶点：共 6 个 CSV；
- 原生 Delaunay 有向最宽路径逐边符号核验：6/6 的
  `nonpositive_edge_count=0`；
- 正式 x=18→2 µm、y≤0.15 µm 路径的瓶颈六态都在
  `(14.6484 µm, 0.0187 µm)`；最大深度 0.2 µm，没有转进 Fe 衬底。

这像给同一条公路换了一个会随温度轻微限速的限速牌：车流图、最窄路口和堵点
都没换位置，只在千分之一级别抖动 → 缺失的持续热失控不能靠继续拧这张限速牌补出来。

## 5. 图、CSV 与大文件位置

- 端电流/Tmax/Joule 叠图：
  `D:\SILVACO_LOCAL\outputs\runs\RUN118_wang1000-fvsatt-short500ns\figs\RUN096_118_fvsatn_terminal_overlay.png`
- 二维导电丝空间图：
  `D:\SILVACO_LOCAL\outputs\reports\RUN096_118_fvsatn_topology_20260731\figs\RUN096_118_native_vertex_paths.png`
- 三时刻端量 CSV：
  `D:\SILVACO_LOCAL\outputs\runs\RUN118_wang1000-fvsatt-short500ns\csv\RUN096_118_fvsatn_milestones.csv`
- 路径逐边符号表：
  `D:\SILVACO_LOCAL\outputs\reports\RUN096_118_fvsatn_topology_20260731\csv\RUN096_118_directed_path_signcheck.csv`
- 归档日志：`E:\silvaco2425\bulk\log\RUN118_wang1000-fvsatt-short500ns__*`
- 归档结构：`E:\silvaco2425\bulk\str\RUN118_wang1000-fvsatt-short500ns__*`（16 件）
- 大型 VictoryExtract 原始 CSV：
  `E:\silvaco2425\bulk\csv\RUN096_118_topology_20260731\`

## 6. 基础设施留痕

`vdoe_tmux.sh` 是历史命名的纯 tmux wrapper。它本轮生成的 `EXIT.txt` 为 0 字节，
`typescript` 没有 `simulator exits with code`，所以 `silvaco_remote.py poll` 显示
`status=unknown`；RUN096 也没有这句。完成证据必须暂时采用“三件交叉验证”：
500 ns STR 存在 + EXTRACT 数值到站 + `ATLAS ... finished`。这属于 runner 判据兼容债，
不是 RUN118 仿真失败。

`extract_errors.py scan-remote` 还会扫描旧 `_remote_logs` 缓存，把历史 VDoE 错误
重复写回知识库。本轮已逆转该污染；RUN118 的隔离计数以归档 typescript 为准：
SCI/Command Error/fatal/step-too-small/Cannot-trap/full NO-CONVERGENCE 均为 0，
温度越限试探 15 次、全部被缩步拒绝。

## 7. 下一步边界

本结果**不授权**延长到 100 µs，也不授权继续调整 `F.VSATN(T)` 参数或叠加第二变量。
若继续主线，应该回到已经排在第二优先级的 UID 面电荷/沟道—UID 交界路线，先另写
A13 对抗核签；若先修工具，则只修 runner 完成判据与错误扫描缓存隔离，不消耗 ATLAS 机时。
