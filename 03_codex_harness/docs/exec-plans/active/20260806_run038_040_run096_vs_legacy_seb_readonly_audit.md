# RUN038–040、RUN096 与历史正确 SEB 案例的三端电流差异审计计划

> 状态：REVISION_4 / WEB_REVIEW_REQUIRED
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

## 2. 网页端三轮裁决及本版响应

网页端第一轮结论为 `REVISE`，本版按以下口径修订：

- `COMPARISON_SCOPE = RUN038,RUN039,RUN040,RUN096`；
- `CURRENT_DEFINITION = BOTH`；
- 10% 容差只在信号越过明确噪声门，并连续维持规定时间时有效；
- 完整审计需要历史正确案例的原始日志和 STR，因此未来需要单独批准只读远端读取；
- 当前仍为计划评审，**没有** SSH、远端读取、仿真或修改授权。

网页端第二轮仍为 `REVISE`，Revision 3 继续补齐：

- 先判 `PHASE2_*` 观察状态，再按固定优先级选择六类失败解释；
- 所有电流必须先完成 A/µm、宽度、符号和电极映射，再计算基线/KCL；
- 明确 `raw_KCL<=5%`、`err_KCL<=10%` 的 PASS 门；
- 三连续点之外，必须满足历史可比案例给出的绝对保持时间；
- 阶段二强制门收敛为“端电流漏—源配对 + 基线增强电流路径连通”；
- 电场、impact 和温度改为独立机制证据，不要求每一帧全部同时成立。

网页端第三轮仍为 `REVISE`，Revision 4 只收紧空间阶段二判据：

- 旧 `mask_J` 不再允许在 `|Je|` 与 `|Jtotal|` 之间任选；唯一主量改名并固定为 β-Ga₂O₃
  半导体中的电子传导电流密度矢量 `Jn`；
- 连通图只允许经过预先登记的 β-Ga₂O₃ 半导体 region，禁止穿过介质、金属、NiO 或其他
  无关 region；
- 三张空间帧必须来自同一个端电流 `T_hold,candidate` 区间的前、中、后三段；
- 二值连通之外，新增固定横截面上的带符号 `Jn·n` 通量闭合门，证明连通分量确实承载
  端电流阶段二增量，而不是一条低电流细丝。

## 3. 先判观察状态，再按固定顺序选择失败解释

本审计使用两层结果，禁止把“是否观察到阶段二”和“为什么没有观察到”写成同一标签。

### 3.0 第一层：阶段二观察状态

每个 RUN 必须先给出且只给出一个观察状态：

- `PHASE2_CONFIRMED`：第 6 节规定的端电流配对、`Jn` 源—漏拓扑与通量闭合、绝对持续
  时间三门同时通过；
- `PHASE2_NOT_CONFIRMED`：证据足以检查三门，但至少一门明确失败；
- `PHASE2_NOT_EVALUABLE`：单位、电极映射、accepted 输出、空间帧或参考持续时间不足，
  无法完成三门检查。

只有观察状态不是 `PHASE2_CONFIRMED` 时，才进入第二层六类失败解释。若阶段二已经确认，
第二层写 `PRIMARY_FAILURE_EXPLANATION=NONE`；配置或数值异常只能作为有效性警告，不得抹去
已经观察到的阶段二事实。

### 3.0.1 第二层固定决策顺序

按下面顺序检查，一旦某一项满足就把它作为**唯一主解释**；其他同时存在的事实放入
`SECONDARY_FLAGS`：

1. `CONFIGURATION_ERROR_CONFIRMED`；
2. `NUMERICAL_TERMINATION`；
3. `OUTPUT_SAMPLING_INSUFFICIENT`；
4. `TIME_WINDOW_INSUFFICIENT`；
5. `PHYSICS_CONFIGURATION_CANDIDATE`；
6. `NOT_EVALUABLE`。

这个顺序的含义是：先排除会让数据集本身失效的确定配置错误，再判断是否被数值中止，
然后区分“运行了但没保存够”“保存够但真实窗口太短”“窗口和输出都够但物理没有形成”，
最后才使用不可评估。比如一个 RUN 同时存在电极映射错误和 `Cannot trap`，主解释必须是
`CONFIGURATION_ERROR_CONFIRMED`，`NUMERICAL_TERMINATION` 只能写入次级标志。

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
中的请求时间当作已输出时间。该类只在运行时间本身可核实且没有更高优先级配置/数值失败时
使用；因此它不再与兜底的 `NOT_EVALUABLE` 重叠。

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
只有前五类均不满足时才把它作为主解释。它是允许且优先于猜测的结论。

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

## 5. 单位归一化、电流定义、基线、KCL 与持续性

### 5.1 单位与电极映射是所有计算的前置硬门

计算基线、MAD、信号门、配对误差或 KCL 之前，必须对 source、drain、gate 和 gate_fp
逐列登记：

| 字段 | 必须记录的内容 |
|---|---|
| 原始列名 | 日志/CSV 中的原始名称，不自行重命名后隐去 |
| 原始单位 | A、A/µm、A/mm、mA/mm 或其他运行时单位 |
| 电极映射 | 原始列对应的实际 electrode name/number，gate_fp 是否 common=gate |
| 符号约定 | 正电流流入还是流出器件，并用一个 accepted 静态点核对 |
| 宽度来源 | deck 的 `mesh width`、日志打印或原始案例说明；必须给出处 |
| 换算公式 | 原始数值如何得到 A/µm |

允许的常见换算写成显式公式：

```text
原始为 A，总器件宽度 W_um：I_Aum = I_A / W_um
原始为 A/mm：              I_Aum = I_Amm * 1e-3
原始为 mA/mm：             I_Aum = I_mAmm * 1e-6
原始已为 A/µm：            I_Aum = I_original
```

如果单位、宽度或电极映射任何一项无法核实，则
`PHASE2_OBSERVATION_STATUS=PHASE2_NOT_EVALUABLE`，主失败解释按第 3.0.1 节决策树选择；不得继续
计算看似精确的基线或误差。

若 gate 与 gate_fp 在输出中是两个独立电流列但电学上属于同一栅节点，则先分别完成单位和
符号核对，再定义 `Ig=Igate+Igate_fp`；若运行时已经合并为一个 common-gate 电流列，则禁止
重复相加。该选择必须在审计表中显式记录。

### 5.2 同时保留两种电流

完成 A/µm 归一化后，同时保留：

1. **原始电流** `Ik(t)`：检查符号、电极映射和原始 KCL；
2. **基线扣除电流** `ΔIk(t)=Ik(t)-Ik,base`：识别粒子引起的阶段一、阶段二。

任何图和 CSV 都必须同时保留原始列与基线扣除列，不允许只展示绝对值后判断方向。

### 5.3 打击前基线窗口

基线必须来自所有静态偏压已经到位、离子源尚未开启的 accepted 点：

- 优先取紧邻打击前的最后 5 个连续 accepted 点；
- 若只有 3–4 个，则全部使用并标记 `BASELINE_SPARSE`；
- 少于 3 个则基线与基线扣除指标写 `NOT_EVALUABLE`；
- `Ik,base` 取该窗口的中位数；
- 基线波动取 `MADk = median(|Ik-Ik,base|)`。

### 5.4 信号门与近零分母

每个端子的增量信号门定义为：

```text
floor_k = max(1e-12 A/µm, 5 * MADk)
```

一对电流的幅度门为 `floor_pair=max(floor_a,floor_b)`。若
`max(|ΔIa|,|ΔIb|) < floor_pair`，该点的“大小接近、方向相反”写
`NOT_EVALUABLE`，不计算相对误差。三端增量 KCL 的分母门取三个端子信号门的最大值。

原始 KCL 使用独立幅度门：

```text
raw_floor = max(1e-12 A/µm, 5 * max(MADs, MADd, MADg))
```

若三个原始电流最大幅度低于 `raw_floor`，原始 KCL 只写 `NOT_EVALUABLE`。

### 5.5 误差量与数值 PASS 门

```text
raw_KCL = |Id + Is + Ig| / max(|Id|, |Is|, |Ig|)
err_DG  = |ΔId + ΔIg| / max(|ΔId|, |ΔIg|)
err_DS  = |ΔId + ΔIs| / max(|ΔId|, |ΔIs|)
err_KCL = |ΔId + ΔIs + ΔIg| / max(|ΔId|, |ΔIs|, |ΔIg|)
```

上述公式适用于确认只有 source、drain、合并后的 gate 三个电学端子的 RUN。若运行时存在独立
substrate、body 或未合并的 field-plate 电学端子，KCL 求和必须纳入全部端子；漏掉端子时不得
用三端公式判 FAIL。

在越过相应信号门后：

- `raw_KCL <= 0.05` 才记 `RAW_KCL_PASS`；
- `err_KCL <= 0.10` 才记 `DELTA_KCL_PASS`；
- `err_DG <= 0.10` 或 `err_DS <= 0.10` 才能进入对应电流配对候选。

原始 KCL 采用更紧的 5% 门，是为了先排除列映射、符号或漏掉 gate_fp 端子的错误；增量 KCL
保留 10% 门以容纳基线扣除噪声。未过门必须报告实际比值，不得只写“基本守恒”。

### 5.6 持续性：三点门 + 绝对保持时间

“大小接近、方向相反”必须同时满足：

1. 至少 3 个连续 accepted 点；
2. 连续成立的绝对时间跨度 `T_hold,candidate` 不小于可比历史正确案例的
   `T_hold,reference`；
3. 这些点的原始与增量 KCL 均通过第 5.5 节门槛。

`τ_end/τ_start >= 2` 只保留为采样跨度的辅助信息，**不得**单独作为持续性门，因为 1–2 ps
也可能满足倍数条件却不构成持续路径。

`T_hold,reference` 必须在读取历史原始日志/STR、通过第 4 节可比性检查后预先登记，再查看
候选 RUN 的阶段二帧。若当前还没有可比参考保持时间，则写
`PERSISTENCE_DURATION_NOT_EVALUABLE`，不得确认 `PHASE2_CONFIRMED`。输出采样本身不足时，按
第 3.0.1 节优先裁决 `OUTPUT_SAMPLING_INSUFFICIENT`。

## 6. 两个阶段的端电流与空间联合判据

### 6.1 阶段一：初始载流子分离与电荷收集

端电流条件：

- `err_DG <= 0.10` 且满足第 5 节信号门；
- 源极增量响应显著小于漏—栅配对；
- `RAW_KCL_PASS` 与 `DELTA_KCL_PASS`；
- 电流配对至少连续 3 个 accepted 点。

空间证据至少要显示粒子产生载流子、电子/空穴分离和栅极响应。阶段一成立不代表 deck
错误，也不代表已经发生 SEB。

### 6.2 阶段二的两个强制门

`PHASE2_CONFIRMED` 必须同时通过以下两个强制门，并通过第 5.6 节绝对保持时间门：

#### 强制门 A：端电流配对

- `err_DS <= 0.10` 且越过信号门；
- 栅极增量相对打击后峰值持续回落；
- `RAW_KCL_PASS` 与 `DELTA_KCL_PASS`；
- 至少 3 个连续 accepted 点成立。

#### 强制门 B：源—漏电子传导路径的拓扑与通量

强制门 B 包含两个不可互换的子门：

1. `B1_TOPOLOGY`：在第 6.3 节规定的 3 张 accepted STR 中，基线增强后的 nominal
   `mask_Jn` 都存在从 source 半导体接触边界连到 drain 半导体接触边界的连通分量；
2. `B2_FLUX_CLOSURE`：同 3 张 STR 中，第 6.3 节规定的电子电流横截面通量与同一时刻的
   漏—源端电流增量通过预声明的 20% 闭合门。

`B1_TOPOLOGY` 与 `B2_FLUX_CLOSURE` 必须同时通过。**绝对电子浓度高**、`Jtotal` 连通、
三端 KCL 或某一条很细的低电流分量，都不能单独替代这两个子门。

### 6.3 唯一主电流密度、region 掩膜、三帧取样和横截面闭合

#### 6.3.1 唯一主空间量

主裁决只使用 **ATLAS 电子传导电流密度矢量**：

```text
Jn = (Jnx, Jny)
|Jn| = sqrt(Jnx^2 + Jny^2)
```

运行时字段清单必须把 ATLAS/STR 中的精确字段名一次性映射到 `Jnx`、`Jny`；历史文件若以
`Je,x/Je,y`、`Electron Current Density X/Y` 或其他标签显示，只能在证明它们就是电子传导
电流密度分量后登记。打击前与瞬态帧必须使用同一字段、同一插值方法和同一单位。

禁止用 `|Jtotal|`、空穴电流、位移电流或电子浓度替换 `|Jn|` 完成主连通裁决。若目标 STR
没有可核实的 `Jnx/Jny`，空间强制门写 `NOT_EVALUABLE`，不得选择另一个更容易连通的字段。

#### 6.3.2 允许连通的半导体 region

连通图只能在以下 β-Ga₂O₃ 半导体 region 内建立：

- RUN038、RUN039、RUN040：region `3,4,5,6`；
- RUN096：region `3,4,5,6,7`；
- 历史正确案例：只读取得原始 deck/STR 后，先登记其中所有且仅有的 β-Ga₂O₃
  source—drain 有效半导体 region，再打开候选瞬态帧。

介质、Aluminum、电极、NiO、空气以及其他无关 region 全部从图节点和图边中删除；任何跨越
被排除 region 的插值边也必须删除。source/drain 端点定义为允许半导体域与各自金属电极直接
接触的边界，不得把金属内部或介质表面当作连通终点。

#### 6.3.3 `mask_Jn` 阈值

在查看候选时刻帧之前，使用打击前 STR 定义每个允许网格位置的
`Jn_pre=|Jn(tpre)|`。电子电流路径掩膜必须同时满足绝对门和相对增强门：

```text
mask_Jn = allowed_beta_Ga2O3_region AND
          (|Jn(t)| >= Jn_abs) AND
          (|Jn(t)| / max(Jn_pre, Jn_noise) >= R_Jn)
```

本轮预声明三档，只允许报告三档敏感性，不得看完候选图再改阈值：

| 档位 | `Jn_abs` | `Jn_noise` | `R_Jn` |
|---|---:|---:|---:|
| loose | `1e-4 A/cm²` | `1e-12 A/cm²` | 3 |
| nominal（主裁决） | `1e-3 A/cm²` | `1e-12 A/cm²` | 10 |
| strict | `1e-2 A/cm²` | `1e-12 A/cm²` | 30 |

主裁决使用 nominal 档。只有 nominal 档连续连通才通过 `B1_TOPOLOGY`；loose/strict 只用于
说明阈值敏感性，不能救回 nominal 失败。若打击前 STR 的数值噪声高于
`1e-12 A/cm²`，则 `Jn_noise` 改为打击前允许半导体非接触体区 `|Jn|` 的第 99 百分位，
并在查看候选帧前冻结该数值。

#### 6.3.4 三张 STR 必须绑定同一个端电流保持区间

先由第 5.6 节端电流配对确定唯一闭区间 `[tH0,tH1]`，其长度为
`T_hold,candidate=tH1-tH0`。随后把该区间等分为前、中、后三段，并只从每段选择一张
accepted STR：

- early：前 1/3 内、最接近 `tH0 + T_hold,candidate/6` 的 accepted STR；
- middle：中 1/3 内、最接近 `tH0 + T_hold,candidate/2` 的 accepted STR；
- late：后 1/3 内、最接近 `tH0 + 5*T_hold,candidate/6` 的 accepted STR。

三张 STR 必须都落在同一个 `[tH0,tH1]` 内，并分别代表其前、中、后段；不得用区间外帧、
拒绝步或插值伪造帧补齐。任一分段没有 accepted STR，强制门 B 不可评估，并按固定顺序裁决
`OUTPUT_SAMPLING_INSUFFICIENT`。

#### 6.3.5 横截面电子电流通量闭合

在打开候选三帧之前，根据几何冻结 4 条竖直横截面：source implant 出口、gate/field-plate
右侧瓶颈、中部 drift、drain implant 入口。每条切线的精确 `xcut`、穿过的允许 region 和
积分 `y` 区间必须从 deck/打击前 STR 登记；积分不得跨介质、金属、NiO 或无关 region。

对每张 early/middle/late STR，在每个切面使用**带符号的横向分量** `Jnx`，而不是 `|Jn|`：

```text
C_SD(t) = nominal mask_Jn 中每个都同时接触 source 与 drain 的全部连通分量之并集
Icut_Aum(t) = 1e-4 * integral over [C_SD(t) intersect x=xcut]
              [Jnx(xcut,y,t) dy_cm]
Icut_pre_Aum(t) = 1e-4 * integral over the same geometric segments
                  [Jnx(xcut,y,tpre) dy_cm]
DeltaIcut(t) = Icut_Aum(t) - Icut_pre_Aum(t)
Iterm(t) = (|DeltaId(t)| + |DeltaIs(t)|) / 2
err_flux(t,xcut) = ||DeltaIcut(t)| - Iterm(t)| /
                   max(|DeltaIcut(t)|, Iterm(t))
```

`1e-4` 把二维积分所得的 A/cm 换算为 A/µm。`DeltaId/DeltaIs` 必须已经按第 5 节完成单位、
宽度和符号登记，并取同一 accepted 时刻；不得拿邻近日志点冒充 STR 时刻。
积分只取 `C_SD(t)` 与切线的交集，不能把连通分量之外的旁路电流加进来凑闭合；若 nominal
`mask_Jn` 没有任何同时接触 source 与 drain 的连通分量，则 `B1_TOPOLOGY` 已失败，不再计算
主闭合值。

每一张 early/middle/late 帧都必须满足：

1. source implant 出口与 drain implant 入口两条切线均有 `err_flux <= 0.20`；
2. 两条内部切线中至少一条有 `err_flux <= 0.20`；
3. 所有通过切线的 `DeltaIcut` 方向与已登记的 source→drain 电子传导方向一致；
4. 对应时刻的 `RAW_KCL_PASS`、`DELTA_KCL_PASS` 和端电流强制门 A 均成立。

三张帧全部满足才通过 `B2_FLUX_CLOSURE`。拓扑连通但横截面闭合失败时，只能报告
`LOW_CURRENT_COMPONENT_CONNECTED / PHASE2_NOT_CONFIRMED`；`Jtotal` 通量可以另作敏感性旁证，
但不得替代 `Jn` 主门。

载流子浓度仅作通路佐证，采用同样的“基线增强”而不是绝对浓度：

```text
mask_n = (n(t) - npre >= n_abs) AND
         (n(t) / max(npre, n_noise) >= R_n)
```

预声明敏感性为：

| 档位 | `n_abs` | `n_noise` | `R_n` |
|---|---:|---:|---:|
| loose | `1e10 cm^-3` | `1 cm^-3` | 3 |
| nominal | `1e11 cm^-3` | `1 cm^-3` | 10 |
| strict | `1e12 cm^-3` | `1 cm^-3` | 30 |

`mask_n` 可以证明载流子增强区，但不能替代 nominal `mask_Jn` 的源—漏连通门或电子通量
闭合门。

### 6.4 机制证据与阶段二观察状态分开

以下三项是解释 SEB 机理强弱的附加证据，不要求它们在每一帧同时成立，也不作为
`PHASE2_CONFIRMED` 的强制门：

- `E_FIELD_REDISTRIBUTION_SEEN`：电场峰值或高场区相对打击前发生可追踪重分布；
- `IMPACT_EVOLUTION_SEEN`：impact 峰值、面积或位置出现持续增长/迁移/衰减；
- `THERMAL_OVERLAP_SEEN`：晶格温度热点与已确认电流路径存在空间重合并可追踪。

每项应分别报告 `SEEN / NOT_SEEN / NOT_EVALUABLE`。由此可以出现“阶段二电流路径已确认，
但热正反馈未确认”的合法结果，而不强迫所有五种场量每帧同时通过。

若缺少同一保持区间前、中、后三段的 accepted STR，强制门 B 不可评估，并按第 3.0.1 节优先裁决
`OUTPUT_SAMPLING_INSUFFICIENT`。

## 7. 终点趋势判据

每组使用最后 5 个连续 accepted 点；若只有 3–4 个则全部使用并标记 `ENDPOINT_SPARSE`。
在 `log10(τ)` 轴上报告 Theil–Sen 斜率或相邻点稳健中位斜率，至少覆盖：

- `|ΔIs|`、`|ΔId|`、`|ΔIg|`；
- nominal `mask_Jn` 连通量与 `B2_FLUX_CLOSURE` 误差；
- electron/hole 最大值与关键路径上的低分位值；
- `ImpactMax`；
- `Tmax`。

裁决规则：

- 强制门 A、B 和绝对保持时间门全部通过：观察状态为 `PHASE2_CONFIRMED`，不再分配失败
  主解释；
- 源极电流、`mask_Jn` 连通量或横截面 `DeltaIcut` 仍连续朝阶段二发展，且计算正常到达
  窗口末端：有可比历史
  时间锚时按实际窗口裁决 `TIME_WINDOW_INSUFFICIENT`；无可比时间锚时观察状态为
  `PHASE2_NOT_EVALUABLE`、主解释为 `NOT_EVALUABLE`，仅把
  `TIME_WINDOW_INSUFFICIENT_CANDIDATE` 放入次级标志；
- 上述量均已连续回落并稳定接近基线，且已具备充分时间和输出，但 nominal `mask_Jn`
  没有源—漏连通或 `B2_FLUX_CLOSURE` 失败：观察状态为 `PHASE2_NOT_CONFIRMED`，主解释为
  `PHYSICS_CONFIGURATION_CANDIDATE`；
- 末端受 `Cannot trap`、时间步坍缩或人工停止控制：若没有更高优先级确定配置错误，观察
  状态按现有证据填 `PHASE2_NOT_CONFIRMED` 或 `PHASE2_NOT_EVALUABLE`，主解释为
  `NUMERICAL_TERMINATION`；
- 只有一个末点或趋势互相矛盾：按第 3.0.1 节检查更高优先级类别；均不适用时主解释为
  `NOT_EVALUABLE`。

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
2. 先完成每个端子的原始单位、宽度来源、符号和电极映射表，全部换算为 A/µm；
3. 从原始日志识别 accepted VGS/VDS、打击时刻、accepted 时间和终止状态；
4. 按第 5 节生成原始与基线扣除的 Is/Id/Ig、KCL、误差和信号门；
5. 本地审计完成后列出历史目录的最小只读清单；
6. 用户另行批准只读 SSH 后，才读取历史正确案例的原始 deck/log/STR；
7. 完成第 4 节可比性表；若可比，先从历史案例冻结 `T_hold,reference`，若不可比则明确
   `PERSISTENCE_DURATION_NOT_EVALUABLE`；
8. 在打开候选时刻 STR 前，按第 6.3 节登记 `Jnx/Jny` 精确字段映射、允许 region、
   loose/nominal/strict 阈值、实际 `Jn_noise`、4 条 `xcut` 和 20% 通量闭合门；
9. 对 RUN038–040、RUN096 的同一 `T_hold,candidate` 区间选择 early/middle/late 三帧，完成
   nominal `mask_Jn` 连通与 `DeltaIcut`—端电流闭合审计，并分开记录 carrier、电场、impact
   和晶格温度机制证据；
10. 按第 7 节计算末端多点趋势；
11. 先给 `PHASE2_*` 观察状态，再严格按第 3.0.1 节顺序分配唯一主失败解释；
12. 只把可直接证明的错误写 `CONFIGURATION_ERROR_CONFIRMED`，其余差异写候选；
13. 汇总最多三个可证伪候选，不修改 deck、不启动仿真。

## 10. 交付物

最终只读审计应包含：

1. 五组输入与结果文件清单；
2. 原始单位、宽度来源、电极/符号映射与 A/µm 换算表；
3. 真实偏压、打击前基线、真实终止时间和求解状态表；
4. 原始三端电流及 `raw_KCL` 曲线和 5% 门判读；
5. 基线扣除三端电流及 `err_DG/err_DS/err_KCL` 曲线和 10% 门判读；
6. 每组基线 MAD、信号门、连续点数、`T_hold,candidate` 与
   `T_hold,reference` 表；
7. 阶段一端电流证据及阶段二强制门 A 表；
8. 同一 `T_hold,candidate` 前、中、后三帧的 nominal `mask_Jn` 源—漏连通图，以及
   loose/strict 敏感性表；
9. 4 条冻结横截面的 `DeltaIcut`、`Iterm`、`err_flux`、方向和 20% 门判读表；
10. carrier、电场、impact、晶格温度机制证据的独立状态表；
11. 末端多点趋势表；
12. 每个 RUN 的 `PHASE2_*` 观察状态、唯一主失败解释和次级标志；
13. 六类主解释的直接证据；
14. 结构、源项、模型和数值差异候选表；
15. 最多三个可证伪根因与未来最小单变量验证建议。

## 11. 完成条件

只有同时满足以下条件，才允许结束完整审计：

- RUN038–040、RUN096 与历史正确案例都有原始日志/STR，或明确标为缺失；
- 没有把请求时间、文件名电压或拒绝步冒充 accepted 结果；
- 所有端子已经记录原始单位、宽度来源、符号/电极映射和换算公式；
- 原始电流和基线扣除电流均已检查；
- `raw_KCL` 与 `err_KCL` 已分别按 5%/10% 数值门判读；
- 基线、MAD、绝对噪声门、连续点数和参考绝对保持时长均已记录；
- 主空间量固定为电子传导电流密度 `Jn`，并在打击前/瞬态使用同一字段、单位与插值；
- 连通图仅使用预登记的 β-Ga₂O₃ 半导体 region，不跨介质、金属、NiO 或无关 region；
- 阶段二具有同一 `T_hold,candidate` 前、中、后三帧 nominal `mask_Jn` 源—漏连通证据；
- 三帧均按冻结横截面完成电子通量—端电流 20% 闭合，而不只依赖二值连通或 KCL；
- loose/nominal/strict 阈值在查看候选帧前冻结并报告敏感性；
- 电场、impact、温度作为独立机制证据，没有被错误设成每帧同时强制通过；
- 先给阶段二观察状态，再按固定顺序给唯一主失败解释；
- 数值中止与时间窗/输出采样不足已经分开；
- 配置错误只由直接证据确认，物理差异只列候选；
- 每个关键结论可回指具体日志、CSV 或 STR；
- 没有改 deck、没有启动仿真、没有新增 RUN。

## 12. 下一轮网页端裁决格式

网页端复审后请返回：

```text
REVIEW_VERDICT: ACCEPT / REVISE / REJECT
PHASE2_OBSERVATION_STATUS: PASS / REVISE
SIX_CLASS_DECISION_ORDER: PASS / REVISE
UNIT_CONVERSION_AND_KCL: PASS / REVISE
BASELINE_AND_FLOOR: PASS / REVISE
PERSISTENCE_RULE: PASS / REVISE
SPATIAL_PHASE2_RULE: PASS / REVISE
PRIMARY_J_FIELD_AND_REGION_MASK: PASS / REVISE
HOLD_INTERVAL_FRAME_BINDING: PASS / REVISE
CROSS_SECTION_FLUX_CLOSURE: PASS / REVISE
MECHANISM_EVIDENCE_SEPARATION: PASS / REVISE
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
