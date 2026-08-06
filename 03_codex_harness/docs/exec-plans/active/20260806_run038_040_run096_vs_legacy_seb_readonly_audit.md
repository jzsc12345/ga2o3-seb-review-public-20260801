# RUN038–040、RUN096 与历史正确 SEB 案例的三端电流差异审计计划

> 状态：REVISION_2 / WEB_REVIEW_REQUIRED
> 性质：REPORT_ONLY / READ_ONLY
> 授权边界：NO_SSH / NO_REMOTE / NO_SIMULATION / NO_DECK_CHANGE
> 本文件只供网页端评审下一步，不授权执行任何仿真、远端读取或 deck 修改。

## 1. 待解决的问题

比较以下五组结果：

1. RUN038；
2. RUN039；
3. RUN040；
4. RUN096；
5. 用户指定的历史正确案例：
   `/root/Desktop/sharer24/SEB/def/x=10um--T30min_meshcu/`。

目标是解释：为什么历史案例后期能够形成漏极电流与源极电流大小接近、方向相反，
而 RUN038–040 和 RUN096 主要表现为漏极电流与栅极电流大小接近、方向相反，或只出现
早期电荷收集阶段，没有形成可验证的后续源—漏持续导电阶段。

这里的“相等”均指**电流**大小接近、符号相反，不是漏极电压等于栅极电压。

## 2. 网页端第一轮裁决及本版响应

网页端第一轮结论为 `REVISE`，本版按以下口径修订：

- `COMPARISON_SCOPE = RUN038,RUN039,RUN040,RUN096`；
- `CURRENT_DEFINITION = BOTH`；
- 10% 容差只在信号越过明确噪声门，并连续维持规定时间时有效；
- 完整审计需要历史正确案例的原始日志和 STR，因此未来需要单独批准只读远端读取；
- 当前仍为计划评审，**没有** SSH、远端读取、仿真或修改授权。

## 3. 六类裁决必须分开

每个 RUN、每个待解释现象均给出一个主裁决；可附次级事实标签，但不得把不同原因合并成
“时间或输出不够”。

### 3.1 `TIME_WINDOW_INSUFFICIENT`

只有同时满足以下条件才允许使用：

1. 静态母态与离子源已经验真；
2. 求解没有以 `Cannot trap`、时间步坍缩、人工停止或错误退出结束；
3. 终点前至少有连续 3 个 accepted 点，且源极电流、载流子通路、impact 或温度仍朝阶段二
   方向发展；
4. 存在可比较的历史正确案例，能够证明其阶段二开始时间晚于本 RUN 的真实终止时间。

若第 4 条不成立，只能写 `TIME_WINDOW_INSUFFICIENT_CANDIDATE`，主裁决写
`NOT_EVALUABLE`，不能因为“没看见阶段二”就断言时间不够。

### 3.2 `OUTPUT_SAMPLING_INSUFFICIENT`

仿真实际时间可能已经覆盖目标阶段，但 accepted 日志点、端电流输出或 STR 保存过稀，无法
检验持续性或空间通路。必须指出缺的是哪一个时间区间、哪一种量和哪几帧 STR；不得把文件名
中的请求时间当作已输出时间。

### 3.3 `NUMERICAL_TERMINATION`

出现以下任一项时优先使用：

- `Cannot trap` 或不可恢复的 bias/time cutback；
- accepted 时间不再前进，时间步持续坍缩；
- ATLAS 未正常结束且目标时间未到；
- 人工停止、许可证或封装异常导致未到站。

此类只能说明计算未完成；除非已有独立物理证据，否则不得把失败后的最后一点解释成
SET、SEB 或时间窗不足。

### 3.4 `CONFIGURATION_ERROR_CONFIRMED`

必须有 deck、运行时打印、日志或 STR 的直接证据，适用范围限定为：

- source/drain/gate/gate_fp 电极名称或电流列映射错误；
- 实际 accepted VGS/VDS 没有达到声称工作点；
- 粒子径迹未进入或未贯穿预定 Ga₂O₃ 目标区域；
- 声称启用的模型实际未启用，或运行时明确打印了错误材料继承；
- 电流单位、器件宽度或 A/µm 与 A/mm 换算错误；
- 读错 STR、log 或把拒绝步当 accepted 解。

仅仅发现两个 deck 的结构、材料或模型不同，不足以确认配置错误。

### 3.5 `PHYSICS_CONFIGURATION_CANDIDATE`

当数值已正常到站、输出足够、阶段二仍缺失，并且端电流及空间场量已经持续回落到基线附近，
可把材料、陷阱、impact、热模型、结构或应力差异列为候选。必须保留“候选”字样；没有单变量
对照时不得宣称因果。

### 3.6 `NOT_EVALUABLE`

原始日志/STR 缺失、参考案例不可比、信号低于噪声门、时间点不足或多项证据互相冲突时使用。
它是允许且优先于猜测的结论。

## 4. 历史正确案例的可比性与充分时间窗

历史案例的阶段二开始时间和持续时长，只有在以下项目均核对后才能作为参考：

| 项目 | 必须核对的事实 |
|---|---|
| 工作点 | 真实 accepted VGS、VDS，不用目录名或文件名代替 |
| 静态母态 | 打击前 Is/Id/Ig、温度、是否从可信静态解启动 |
| 离子源 | xion、入口/出口、LET 或 pcunits、半径、T0/TC、时间积分 |
| 关键结构 | 沟道、UID、衬底、介质、NiO/场板和电极拓扑 |
| 热模型 | LAT.TEMP、热导率/热容、热接触位置和边界条件 |
| 输出 | accepted 时间点、三端电流、关键 STR 保存时刻 |

只要其中一项对阶段时序有实质影响且无法核对，就不能用历史案例的时间直接裁决 RUN038–040
或 RUN096；时间窗结论写 `NOT_EVALUABLE`。

若全部可比，则：

- `t_phase2,start` 取历史案例首次满足阶段二全部端电流与空间条件的 accepted 时刻；
- `t_phase2,hold` 取该状态连续成立的 accepted 时间跨度；
- 待审 RUN 的充分窗口至少应覆盖
  `t_phase2,start + t_phase2,hold`；
- 仍须检查待审 RUN 自身终点趋势，不能只按钟表时间机械裁决。

## 5. 电流定义、基线、噪声门与持续性

### 5.1 同时保留两种电流

1. **原始电流** `Ik(t)`：检查符号、单位、电极列映射和原始 KCL；
2. **基线扣除电流** `ΔIk(t)=Ik(t)-Ik,base`：识别粒子引起的阶段一、阶段二。

任何图和 CSV 都必须同时保留原始列与基线扣除列，不允许只展示绝对值后判断方向。

### 5.2 打击前基线窗口

基线必须来自所有静态偏压已经到位、离子源尚未开启的 accepted 点：

- 优先取紧邻打击前的最后 5 个连续 accepted 点；
- 若只有 3–4 个，则全部使用并标记 `BASELINE_SPARSE`；
- 少于 3 个则该 RUN 的基线扣除电流主裁决为 `NOT_EVALUABLE`；
- `Ik,base` 取该窗口的中位数；
- 基线波动取 `MADk = median(|Ik-Ik,base|)`。

### 5.3 信号门与近零分母

每个端子的信号门定义为：

```text
floor_k = max(1e-12 A/µm, 5 * MADk)
```

一对电流的幅度门为 `floor_pair=max(floor_a,floor_b)`。若
`max(|ΔIa|,|ΔIb|) < floor_pair`，该点的“大小接近、方向相反”写
`NOT_EVALUABLE`，不计算相对误差。三端 KCL 的分母门同理取三个端子信号门的最大值。

### 5.4 误差量

```text
raw_KCL = |Id + Is + Ig| / max(|Id|, |Is|, |Ig|)
err_DG  = |ΔId + ΔIg| / max(|ΔId|, |ΔIg|)
err_DS  = |ΔId + ΔIs| / max(|ΔId|, |ΔIs|)
err_KCL = |ΔId + ΔIs + ΔIg| / max(|ΔId|, |ΔIs|, |ΔIg|)
```

只有越过相应信号门后，10% 容差才生效。

### 5.5 持续性

“大小接近、方向相反”必须：

- 在至少 3 个连续 accepted 点成立；并且
- 以 `τ=t-tstrike` 计，首末点满足 `τ_end/τ_start >= 2`。

若输出过稀而无法满足这两个条件，应裁决为 `OUTPUT_SAMPLING_INSUFFICIENT`，不得用单个峰值
或单个终点代替持续阶段。

## 6. 两个阶段的端电流与空间联合判据

### 6.1 阶段一：初始载流子分离与电荷收集

端电流条件：

- `err_DG <= 0.10` 且满足信号门和持续性；
- 源极增量响应显著小于漏—栅配对；
- 原始 KCL 与电极映射检查通过。

空间证据至少要显示粒子产生载流子、电子/空穴分离和栅极响应。阶段一成立不代表 deck
错误，也不代表已经发生 SEB。

### 6.2 阶段二：源—漏持续导电路径

端电流必要条件：

- `err_DS <= 0.10` 且满足信号门和持续性；
- 栅极增量相对其打击后峰值持续回落；
- 原始与基线扣除 KCL 均通过。

这些条件只证明端子电流配对，**不能单独证明**源—漏导电丝。阶段二还必须在至少 3 个连续
accepted STR 中同时具备：

1. 电子浓度或总/电子电流密度的连通分量从源接触边界延伸到漏接触边界；
2. 栅区响应回落，不再由 gate 电流承担主要电荷收集；
3. 电场分布显示源—漏路径及栅/场板附近场重分布；
4. impact 区域的位置、面积和峰值随时间可追踪；
5. 晶格温度热点与电流路径空间重合，其增长、平台或衰减趋势可追踪。

空间连通阈值不得事后挑选。审计时应从打击前同场量的基线与数值底噪声明阈值，并同时输出
阈值敏感性。若缺少连续 STR，主裁决为 `OUTPUT_SAMPLING_INSUFFICIENT`。

## 7. 终点趋势判据

每组使用最后 5 个连续 accepted 点；若只有 3–4 个则全部使用并标记 `ENDPOINT_SPARSE`。
在 `log10(τ)` 轴上报告 Theil–Sen 斜率或相邻点稳健中位斜率，至少覆盖：

- `|ΔIs|`、`|ΔId|`、`|ΔIg|`；
- 电子/总电流路径连通量；
- electron/hole 最大值与关键路径上的低分位值；
- `ImpactMax`；
- `Tmax`。

裁决规则：

- 源极电流、载流子通路、impact 或温度仍连续朝阶段二发展，且计算正常到达窗口末端：只可列
  `TIME_WINDOW_INSUFFICIENT_CANDIDATE`；有可比历史时间锚后才升级为
  `TIME_WINDOW_INSUFFICIENT`；
- 上述量均已连续回落并稳定接近基线，空间上也没有源—漏连通路径：列
  `PHYSICS_CONFIGURATION_CANDIDATE`；
- 末端受 `Cannot trap`、时间步坍缩或人工停止控制：主裁决
  `NUMERICAL_TERMINATION`；
- 只有一个末点或趋势互相矛盾：`NOT_EVALUABLE`。

## 8. 已定位的本地证据路径

以下路径已经在主控端存在；它们只是审计输入，不代表其中旧结论自动有效。

### 8.1 RUN038

- deck：`D:\SILVACO_LOCAL\decks\RUN038_Wang2026_x13_SEB_long_VDS1200.in`
- RUN 入口：`D:\SILVACO_LOCAL\outputs\runs\RUN038_x13-seb-long-vds1200\README.md`
- 全时序 CSV：`D:\SILVACO_LOCAL\outputs\runs\RUN038_x13-seb-long-vds1200\csv\RUN038_Id_Tmax_Hole_Impact.csv`
- 里程碑：`D:\SILVACO_LOCAL\outputs\runs\RUN038_x13-seb-long-vds1200\csv\RUN038_milestones.csv`
- 联合空间证据：`D:\SILVACO_LOCAL\outputs\runs\RUN038_x13-seb-long-vds1200\figs\RUN038_040_longtail_spatial.png`
- 大文件归档前缀：`E:\silvaco2425\bulk\log\RUN038_x13-seb-long-vds1200__*` 与
  `E:\silvaco2425\bulk\str\RUN038_x13-seb-long-vds1200__*`
- 远端只读指针：`/root/DECKBUILD/runs/RUN038_x13-seb-long-vds1200/`

### 8.2 RUN039

- deck：`D:\SILVACO_LOCAL\decks\RUN039_Wang2026_x13_SEB_long_VDS1400.in`
- RUN 入口：`D:\SILVACO_LOCAL\outputs\runs\RUN039_x13-seb-long-vds1400\README.md`
- 全时序 CSV：`D:\SILVACO_LOCAL\outputs\runs\RUN039_x13-seb-long-vds1400\csv\RUN039_Id_Tmax_Hole_Impact.csv`
- 里程碑：`D:\SILVACO_LOCAL\outputs\runs\RUN039_x13-seb-long-vds1400\csv\RUN039_milestones.csv`
- 场板电场审计：`D:\SILVACO_LOCAL\outputs\runs\RUN039_x13-seb-long-vds1400\RUN039_FP_FIELD_AUDIT.md`
- 大文件归档前缀：`E:\silvaco2425\bulk\log\RUN039_x13-seb-long-vds1400__*` 与
  `E:\silvaco2425\bulk\str\RUN039_x13-seb-long-vds1400__*`
- 远端只读指针：`/root/DECKBUILD/runs/RUN039_x13-seb-long-vds1400/`

### 8.3 RUN040

- deck：`D:\SILVACO_LOCAL\decks\RUN040_Wang2026_x13_SEB_long_VDS1500.in`
- RUN 入口：`D:\SILVACO_LOCAL\outputs\runs\RUN040_x13-seb-long-vds1500\README.md`
- 全时序 CSV：`D:\SILVACO_LOCAL\outputs\runs\RUN040_x13-seb-long-vds1500\csv\RUN040_Id_Tmax_Hole_Impact.csv`
- 里程碑：`D:\SILVACO_LOCAL\outputs\runs\RUN040_x13-seb-long-vds1500\csv\RUN040_milestones.csv`
- 温度完整性图：`D:\SILVACO_LOCAL\outputs\runs\RUN040_x13-seb-long-vds1500\figs\RUN040_Tmax_integrity_audit.png`
- 大文件归档前缀：`E:\silvaco2425\bulk\log\RUN040_x13-seb-long-vds1500__*` 与
  `E:\silvaco2425\bulk\str\RUN040_x13-seb-long-vds1500__*`
- 远端只读指针：`/root/DECKBUILD/runs/RUN040_x13-seb-long-vds1500/`

### 8.4 RUN096

- deck：`D:\SILVACO_LOCAL\decks\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in`
- RUN 入口：`D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\README.md`
- 静态日志：`D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\logs\RUN096_static_final.log`
- 瞬态日志：`D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\logs\RUN096_transient_final.log`
- 端电流里程碑：`D:\SILVACO_LOCAL\outputs\runs\RUN096_wang1000-nofp-lgd9-x11-hfo2hc\csv\RUN095_096_hfo2hc_milestones.csv`
- 80 条空间剖面和汇总：
  `D:\SILVACO_LOCAL\outputs\reports\RUN096_persistent_path_audit_20260731\csv\`
- 空间提取日志：
  `D:\SILVACO_LOCAL\outputs\reports\RUN096_persistent_path_audit_20260731\logs\victoryextract.log`
- 路径时间图：
  `D:\SILVACO_LOCAL\outputs\reports\RUN096_persistent_path_audit_20260731\figs\RUN096_persistent_path_timeline.png`
- 大文件归档前缀：`E:\silvaco2425\bulk\log\RUN096_wang1000-nofp-lgd9-x11-hfo2hc__*` 与
  `E:\silvaco2425\bulk\str\RUN096_wang1000-nofp-lgd9-x11-hfo2hc__*`
- 远端只读指针：`/root/DECKBUILD/runs/RUN096_wang1000-nofp-lgd9-x11-hfo2hc/`

### 8.5 历史正确案例（当前未读取）

- 远端目录：`/root/Desktop/sharer24/SEB/def/x=10um--T30min_meshcu/`
- 用户截图显示但尚未现场核实的候选文件：`Vds300_X10.log`、`Vds300_X10.str`、
  `1e-13_Vds300_X10.str`、`4e-12_Vds300_X10.str`、`1e-11_Vds300_X10.str`、
  `5e-8_Vds300_X10.str`、`7e-10_Vds300_X10.str`、`1e-9_Vds300_X10.str`、
  `1e-7_Vds300_X10.str`、`1e-6_Vds300_X10.str`、`total_1e-6_Vds300_X10.str`。
- 当前状态：`REMOTE_READ_PENDING / NOT_AUTHORIZED / NOT_VERIFIED`。

## 9. 只读审计执行顺序（获批后才执行）

1. 先盘点第 8 节本地文件，登记存在性、真实大小、来源和生成方式；
2. 从原始日志识别 accepted VGS/VDS、打击时刻、accepted 时间、终止状态和电流列映射；
3. 按第 5 节生成原始与基线扣除的 Is/Id/Ig、KCL、误差和信号门；
4. 按第 7 节计算末端多点趋势；
5. 对 RUN038–040、RUN096 的现有 STR 做三帧以上的电子、空穴、Jtotal/Je、电场、impact、
   晶格温度空间连续性审计；
6. 只把可直接证明的错误写 `CONFIGURATION_ERROR_CONFIRMED`，其余差异写候选；
7. 本地审计完成后列出历史目录的最小只读清单；
8. 用户另行批准只读 SSH 后，才读取历史正确案例的原始 deck/log/STR；
9. 先做可比性表，再决定能否使用历史阶段二时间锚；
10. 汇总六类主裁决与最多三个可证伪候选，不修改 deck、不启动仿真。

## 10. 交付物

最终只读审计应包含：

1. 五组输入与结果文件清单；
2. 真实偏压、打击前基线、真实终止时间和求解状态表；
3. 原始三端电流及原始 KCL 曲线；
4. 基线扣除三端电流及 `err_DG/err_DS/err_KCL` 曲线；
5. 每组基线 MAD、信号门、连续点数和持续时间表；
6. 阶段一/阶段二端电流证据表；
7. 至少三帧空间证据拼图和源—漏连通性表；
8. 末端多点趋势表；
9. 六类主裁决及其直接证据；
10. 结构、源项、模型和数值差异候选表；
11. 最多三个可证伪根因与未来最小单变量验证建议。

## 11. 完成条件

只有同时满足以下条件，才允许结束完整审计：

- RUN038–040、RUN096 与历史正确案例都有原始日志/STR，或明确标为缺失；
- 没有把请求时间、文件名电压或拒绝步冒充 accepted 结果；
- 原始电流和基线扣除电流均已检查；
- 基线、MAD、绝对噪声门、连续点数和持续时长均已记录；
- 阶段二具有多帧源—漏空间连通证据，而不只依赖 KCL；
- 数值中止与时间窗/输出采样不足已经分开；
- 配置错误只由直接证据确认，物理差异只列候选；
- 每个关键结论可回指具体日志、CSV 或 STR；
- 没有改 deck、没有启动仿真、没有新增 RUN。

## 12. 下一轮网页端裁决格式

网页端复审后请返回：

```text
REVIEW_VERDICT: ACCEPT / REVISE / REJECT
SIX_CLASS_TAXONOMY: PASS / REVISE
BASELINE_AND_FLOOR: PASS / REVISE
PERSISTENCE_RULE: PASS / REVISE
SPATIAL_PHASE2_RULE: PASS / REVISE
LOCAL_PATHS_SUFFICIENT: YES / NO
REMOTE_READONLY_REQUIRED: YES / NO
MANDATORY_REVISIONS:
1. ...
2. ...
NEXT_AUTHORIZATION:
- 只读本地审计；或
- 只读本地审计 + 只读 SSH 指定历史目录；或
- 暂不执行，继续修订计划。
```

任何 `ACCEPT` 只代表认可审计方法。只有用户另行明确授权，才能进行只读 SSH；本计划永远
不自动授权仿真、deck 修改或创建新 RUN。
