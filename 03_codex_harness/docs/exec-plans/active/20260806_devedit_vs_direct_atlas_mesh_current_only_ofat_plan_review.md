# DevEdit vs Direct ATLAS Mesh：电流定义 SET/SEB 最小 OFAT 计划审查包

> Status: PLAN_REVIEW_ONLY / NOT_AUTHORIZED_FOR_EXECUTION
>
> Date: 2026-08-06
>
> Scope: current-only late-response comparison
>
> Execution remains prohibited: SSH, simulation, deck modification, new RUN, branch/worktree and parameter changes.
> Publication of this review package is separately authorized by the current user instruction.
> This document does not authorize any remote or simulation action.

## 0. 审查结论摘要

本对照在技术上**原则可行，但当前尚不具备直接发射条件**。

- 撤回“RUN238 是本 OFAT 父本”的旧裁决。RUN238 不再进入本计划。
- 结构、区域、掺杂、迁移率和 impact 血统的**唯一母版**是用户本轮提供的原始
  [`bv.in`](../../../../04_reports/attachments/20260806_bv_to_seb_ofat/bv.in)；A 臂实验父本候选为
  [`bv_SEB_x10p25_300V.in`](../../../../04_reports/attachments/20260806_bv_to_seb_ofat/bv_SEB_x10p25_300V.in)。
- 当前身份固定为：`CONTROLLED_LINEAGE_MASTER=bv.in`、`CONTROLLED_EXECUTION_PARENT=NONE`、`ZIP_DECK=CANDIDATE_PARENT / NOT_RUNTIME_VALIDATED`。
- `bv_to_SEB.patch` 已由网页端独立核验：可干净应用到本轮原始 `bv.in`，应用结果与 ZIP 内候选 deck 逐字节一致。因此 patch provenance 门已关闭；这不等于 runtime 验证通过。
- B 臂应由该 BV-derived SEB 候选机械转写为 direct ATLAS mesh，而不是继承 RUN238 或历史 `seb_2` 的物理参数。
- 只允许替换“结构/网格生成块”。从材料定义开始，到接触、偏置、SEU、求解器、时间表和输出字段，A/B 必须共享同一份规范正文。
- 历史 direct-mesh `seb_2` 仅用作“direct mesh 可运行”和“晚时间输出预算”的旁证；不得把它的物理卡替换进 BV-derived 父本。
- 在 direct-mesh 双生 deck 尚未编制、几何/区域/掺杂/电极/静态母态等价门尚未关闭前，不得发射对照。

本计划只裁决**晚期端电流是 SET-like 还是 current-defined-SEB candidate**。它不裁决正式空间 Phase 2，也不裁决 thermal-runaway SEB。

## 1. 三层结论必须严格分离

### 1.1 本计划允许输出的端电流事实

本计划可以回答：

- 打击后的漏/源电流是否先峰值后持续衰减；
- 漏/源电流是否保持异号、满足 KCL，并在晚时间持续高于基线；
- 两种网格生成路线是否给出相同的 current-only 分类；
- 两条路线的电流误差、运行时间和 accepted-step 数是否有显著差异。

### 1.2 本计划禁止越级输出的结论

以下结论不属于本计划：

- `FORMAL_SPATIAL_PHASE2_CONFIRMED`；
- `THERMAL_RUNAWAY_SEB`；
- “direct mesh 比 DevEdit 物理上更准确”；
- “DevEdit 导致或抑制 SEB”；
- “端电流配对已经证明源—漏内部导电丝形成”。

原始三端电流配对只是一道端子门。正式空间 Phase 2 仍需 Revision 4 的 `Jn` 连通、同一保持区间三帧和横截面通量闭合；热失控还需要独立的后段电流—impact—温度正反馈证据。

## 2. 受控父本与历史证据的角色

### 2.1 两层父本定义

**结构/物理血统母版**：用户用于约 980 V BV 拟合的原始 `bv.in`。
**SEB 实验父本候选**：

[`bv_SEB_x10p25_300V.in`](../../../../04_reports/attachments/20260806_bv_to_seb_ofat/bv_SEB_x10p25_300V.in)

配套源与审计件：

- [`mySEU_bv.c`](../../../../04_reports/attachments/20260806_bv_to_seb_ofat/mySEU_bv.c)
- [`bv_to_SEB.patch`](../../../../04_reports/attachments/20260806_bv_to_seb_ofat/bv_to_SEB.patch)
- [`BV_to_SEB_conversion_notes.md`](../../../../04_reports/attachments/20260806_bv_to_seb_ofat/BV_to_SEB_conversion_notes.md)

选择理由：

1. 它从用户指定的 `bv.in` 结构、区域、掺杂、迁移率和 impact 血统转换，而不是从 RUN238 转换；
2. 已核验 patch 显示，SEB 转换新增局部径迹网格、自热、热接触、C 源、300 V 静态终点及 100 µs 分段瞬态，同时也引入了下文必须撤回或重新闭合的数值/模型变化；
3. 它的 `xion=10.25 µm`、C 源 `x0=10.25 µm`、`y=0–0.6 µm`、`r=0.05 µm`、LET/T0/Tc 内部一致；
4. 它保留用户 BV 母版的复杂 DevEdit 区域与厚金属几何，避免把另一个器件血统误当父本；
5. 100 µs 终点比原计划 10 µs 更适合区分晚期衰减与持续端电流。

当前标签仍为 `CANDIDATE_PARENT / NOT_RUNTIME_VALIDATED`，不是“已验证父本”。

### 2.2 转换包只读审查结果

已确认的转换保真项：

- ZIP 内四个声明文件均存在；
- `bv_to_SEB.patch` 可干净应用到本轮原始 `bv.in`，应用结果与候选 deck 逐字节一致，`PROVENANCE_GATE=PASS`；
- deck 与 C 源的 xion/x0、径迹 y 范围、半径和时间参数一致；
- 五个 x refinement 窗口按名义坐标嵌套且未越出 `x=0–15 µm`；
- 瞬态目标从 4 ps 递增到 100 µs；
- BV 高压扫描被替换为 300 V 静态母态与 SEU 瞬态；
- 12 个 region 边界、厚 Nickel source/drain/阶梯 gate、`elec.id=1/2/3`、active impurity、mobility、impact 和 active interface charge 保持不变；
- 原始 gate 是一个连续的厚 Nickel `gate` 电极，没有独立 `gate_fp`；候选仍保持这个单电极拓扑；
- 两个文件都没有启用 active trap，相关 trap 仅为注释；只能说“trap 注释保持不变”；
- `auger`、`lat.temp`、两个 `thermcontact` 和 `singleeventupset F.SEU` 是候选中的显式新增项。

转换保真仍是 `PARTIAL_PASS`，因为静态母态和物理正文没有完全保持：

1. 原始 `models` 不含 `auger` 或 `lat.temp`；候选同时新增了两者；
2. 原始 `METHOD` 不含 `max.temp=50000`；候选新增了该项；
3. 原始 200→300 V 为 `vstep=15`；候选改为 `vstep=10`；
4. 原始 gate 状态含 `outf/load` 流；候选移除了该流程。

尚未关闭的 runtime/执行门：

1. 五层窗口全是 `refine mode=x` 且没有显式目标 spacing；必须从实际 STR 报告径迹中心与 `xion±3r` 的 Δx/Δy、全 y 连续性，不能用窗口存在或总节点数代替；
2. 300 V 必须以真实 accepted VDS、暗态端电流和保存 STR 反查，目标值/文件名不能代替到站；
3. `thermcontact ... elec.num=...` 的实际电极/面积绑定尚未由 parser/runtime 表证明；
4. `MATERIAL region=10 mun=50` 实际指向厚 Nickel source region 10；必须判明 runtime 是报错、忽略还是误施加，不能假设无害；
5. NiO `tcon.const tc.const=2.27` 的 parser/runtime 解释尚未核实；
6. C 源在 `t=0` 为 `exp(-4)≈0.0183`，且 source statement 位于静态爬压之前；当前文件不能证明存在严格 source-off 的静态母态与 baseline；
7. 当前 deck 没有 5 个真正 source-off、目标 VGS/VDS 下的 accepted baseline 点；
8. 当前 deck 继承 `substrate Acceptors=2e6` 与 `impact 2.5e6/3.96e7/betan=1.37`。这不是转换新增，但与现行 production preflight ban 冲突；仅在用户书面批准 `benchmark-only exception` 后才可原样用于本数值路线对照；
9. 新增 `auger` 没有显式参数，会引入无法追溯的父材料默认值；
10. `max.temp=50000`、静态步长变化和移除 `outf/load` 都是数值/母态变化，不能伪装成纯 SEB 必需增量；
11. 候选未显式生成计划要求的 20 µs、50 µs accepted 判据点及对应统一 STR；
12. 末尾 `tonyplot` 不属于非交互 benchmark 执行链，可能阻塞 runner 或污染 wall-time。

### 2.3 候选规范化裁决（未来编制要求，本轮不改 deck）

未来若获“本地候选编制”授权，A/B 共享 physics body 必须先规范化：

1. 几何、12 个 region、active impurity、mobility、impact、interface charge 和单一厚 Nickel gate 全部以原始 `bv.in` 为准；
2. 恢复原始静态母态语义：200→300 V 恢复 `vstep=15`，恢复等价的 gate 状态 `outf/load` 流；文件名可机械确定化，但 A/B 的求解序列必须相同；
3. `lat.temp` 与 thermcontact 作为 SEB 电热增量保留，但必须先关闭 runtime 绑定门；
4. 删除候选新增的 `auger`；除非未来另有独立物理依据、显式参数和单独授权；
5. 删除候选新增的 `max.temp=50000`；不得把它当作转换所必需的默认项；
6. 在 active `singleeventupset` 声明之前建立严格 source-off 的 300 V 母态，并在相同 VGS/VDS 下生成 5 个 accepted baseline 记录；若所用语法无法保证源严格为零，则 baseline 门失败，不得发瞬态；
7. 明确生成 10、20、50、100 µs accepted 判据点，并在两臂相同的预声明时刻保存相同字段 STR；
8. 删除 benchmark 执行路径末尾的 `tonyplot`，绘图留给计时区间外的统一后处理；
9. trap 继续保持未启用；不得把注释描述成 active trap 模型；
10. `MATERIAL region=10 mun=50` 与 NiO 热参数若 runtime 不能给出唯一、可接受的解释，候选不得晋升；修正它们需要新的父本修订授权，不能在 mesh OFAT 内静默处理。

若未来获准使用第 8 项 legacy 参数，A/B 产物必须统一标记 `LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB`。该例外只允许原样比较两种网格生成路线，不授权把这些参数复制到生产 SEB 母线，也不允许静默改值来绕过 preflight。

### 2.4 历史 direct-mesh 案例只作旁证

下列历史案例不可作为物理父本：

历史 direct-mesh `seb_2` 的只读远端证据（路径保留在先前私有 handoff，不在本公开包展开）。

它只用于说明：

- direct ATLAS mesh 路线可以完成长瞬态；
- 晚期电流可能在微秒之后继续变化；
- 运行时间和 accepted 输出调度需要分段统计。

不得用它的材料、掺杂、impact 或热卡覆盖 BV-derived 父本。第一个历史 `x=10um--T30min_meshcu` 缺少生成 deck，更不能作为可重建 OFAT 父本。

## 3. OFAT 的唯一自变量

### 3.1 A 臂：DevEdit route

- 使用包内 `bv_SEB_x10p25_300V.in` 的 DevEdit 几何和局部径迹网格生成方法；
- 生成结构后进入与 B 臂相同的 ATLAS 物理正文；
- 保留 DevEdit 实际产生的非结构化三角网格。

### 3.2 B 臂：direct ATLAS mesh route

- 用 ATLAS 内建 `mesh width=...`、`x.mesh`、`y.mesh`、`region`、`electrode`、`doping` 重新表达同一名义器件；
- 不允许借 direct-mesh 重写之机修改结构尺寸、物理参数、掺杂或求解策略；
- 使用与 A 臂相同的局部网格目标尺寸，但允许三角剖分拓扑、节点数和三角形数自然不同。

### 3.3 允许不同的内容

只有以下差异属于自变量：

1. 结构/网格生成语法；
2. 由两种 mesher 自然产生的节点位置、三角拓扑、节点数和三角形数；
3. 若不可避免，region 数字编号可以不同，但必须有唯一语义映射；
4. A/B 输出文件名和臂标签。

其余差异均不是 OFAT，必须在发射前消除。

## 4. 等价合同

### 4.1 几何与区域边界

A/B 必须使用同一坐标表，至少逐项核对：

- 器件横向范围、总深度；
- source、单一连续厚 Nickel 阶梯 gate（含其场板延伸部分）、drain 的边界位置；
- SiO₂、Al₂O₃、NiO、channel、UID、substrate 的上下边界；
- source/drain n+ 区域的横向范围与深度；
- 所有材料交界面；
- ion track 与这些边界的相交顺序。

验收方式不是“图看起来相似”，而是：名义坐标表逐项相同，并由两份结构文件反查边界位置。任一关键边界错位即 `OFAT_INVALID`。

### 4.2 电极与宽度

必须相同：

- electrode 名称、数量、位置和接触的半导体边界；
- 单一 `gate` 的完整厚金属边界、`elec.id=3` 和连续等势关系；
- gate work function；
- source/drain 接触类型；
- `width` 及电流从原始单位转换到 A/µm 的公式。

任何一臂出现额外 `gate_fp`、丢失电极、重命名、厚金属被零厚度线接触替代、接触边界长度变化或单一 gate 被拆成多个独立电极，均使 OFAT 无效。

### 4.3 材料、掺杂、陷阱与模型

从 ATLAS 物理正文起，A/B 必须逐行等价：

- 材料名称、父材料和所有显式材料参数；
- mobility、SRH、incomplete、Fermi/BGN 等启用状态；规范化候选中 Auger 必须保持关闭；
- Ga₂O₃ 与 NiO 的区域材料绑定；
- 所有均匀/非均匀掺杂的种类、浓度和空间范围；
- trap 的类型、能级、密度、截面和区域；
- impact 模型、方向和全部系数；
- self-heating 模型、热材料参数和 thermal contact；
- MODELS、METHOD、数值容差与 compliance。

不允许 direct mesh 版本静默回退到另一个材料父槽位。两臂的 `MODELS PRINT` 与材料/区域表必须按语义一致。

### 4.4 偏置、静态母态与粒子源

必须相同：

- VGS、VDS 目标值及到站顺序；
- 静态 homotopy/爬压过程；
- 打击前保存时刻与状态；
- xion、y 起止、轨迹方向；
- LET、radius、时间函数、T0/TC；
- SEU 启用模型与源项语法；
- 瞬态初始条件和 `solve previous` 关系。

不得共享同一个 MASTER STR：不同网格的解文件不能跨臂加载。A/B 必须各自从相同初始条件、用相同求解序列独立建立静态母态。

### 4.5 网格目标

两臂使用相同的**网格分辨率合同**，而不是强求相同节点：

- channel/oxide 界面最大 Δx、Δy 相同；
- 厚 gate 的场板延伸端点 ROI 最大 Δx、Δy 相同；
- ion track 核心和 `xion ± 3r` 范围最大 Δx 相同；
- track 的全 y 路径必须穿过目标半导体并有连续节点覆盖；
- source/drain 结、NiO/Ga₂O₃ 界面和 thermal contact 附近采用相同名义分辨率；
- 两臂都不得有 obtuse triangle 或未解析薄层。

节点数差异本身不是失败；如果其中一臂为通过质量门而需要额外改变 ROI、结构边界或物理定义，则 OFAT 失效。

## 5. 发射前等价门

以下门全部通过，才可在未来另行授权发射；本计划不执行这些门。

### G0：文本差异门

- 把两个候选拆成“route-specific structure block”和“shared physics body”；
- shared physics body 必须逐行一致；
- 完整 diff 中只能出现第 3.3 节允许的差异。

### G1：结构与材料门

- 区域边界坐标相同；
- 材料—语义 region 映射相同；
- 电极数量、名称、接触边界和单一厚 gate 的连续等势关系相同；
- 掺杂/陷阱空间范围相同；
- ion path 经过的材料序列相同。

### G2：网格质量门

- 两臂各自报告 nodes、triangles、obtuse；
- 第 4.5 节各 ROI 的实测最大 Δx/Δy 均满足同一合同；
- 不允许用总节点数替代 ROI 网格验收。

### G3：静态母态等价门

两臂必须真实接受同一 VGS/VDS，且：

- 不存在 `Cannot trap`、被拒解冒充到站或 compliance 提前终止；
- 温度初值与热边界状态相同；
- 打击前 raw `Id/Is/Ig` 在信号高于 floor 时相对差不超过 5%；
- 低于 floor 时只比较绝对差，差值不得超过两臂较大的 floor；
- gate 下缘、同一厚 gate 的场板延伸端点、xion 处的电势和 |E| 探针差异不超过 5%。

G3 未通过时，不得把后续差异解释成 mesh-route 效应。

## 6. 统一输出时间表

### 6.1 打击前基线

每臂必须在 active 粒子源尚未声明或已被证明严格为零、目标 VGS/VDS 已真实接受后，生成并保存 5 个 accepted 基线记录。五点必须来自同一个 source-off 目标母态保持段，记录 raw `Id/Is/Ig`、偏压和接受状态；不得用 `F.SEU(t=0)=exp(-4)` 冒充 source-off，也不得用不同偏压的爬压点拼成 baseline。

少于 5 个 accepted source-off 点，或无法证明源严格为零，记 `BASELINE_GATE_FAIL / NOT_EVALUABLE`，不进入 current-only 裁决。候选编制时必须先用 parser/短静态烟测证明该顺序可执行；本计划不预设未验证的语法。

### 6.2 瞬态 accepted 输出点

两臂必须请求并记录相同的 accepted 时刻：

```text
2 ps, 10 ps, 100 ps,
1 ns, 2 ns, 5 ns, 10 ns,
50 ns, 100 ns, 500 ns,
1 µs, 2 µs, 5 µs, 10 µs,
20 µs, 50 µs, 100 µs
```

至少在以下时刻保存相同字段的 STR：

```text
100 ps, 1 ns, 10 ns, 100 ns, 1 µs, 5 µs, 10 µs, 20 µs, 50 µs, 100 µs
```

STR 字段保持一致，至少包含 electron/hole concentration、potential、electric field、Jn/Je、Jtotal、impact generation 和 lattice temperature。它们用于完整留证；本计划的一级分类仍只使用端电流。

### 6.3 最小晚时间窗口

**最低观察终点固定为 100 µs，晚时间判定区间固定为 10–100 µs。**

理由：10 ns 只能用于早期筛查，不能区分“正在衰减”与“形成晚期平台”；转换包本身已把终点设为 100 µs，且现有历史案例表明微秒尺度仍可能转折。100 µs 是本次**成对比较的最低终点**，不是从历史案例移植的物理阶段时间。

若到 100 µs 仍不能区分衰减与持续，则结果必须为 `INSUFFICIENT_TIME_WINDOW`。不得在本 OFAT 内擅自延长；后续 1 ms 或更长成对延长需另行计划与授权。

## 7. 电流统一、基线、floor 与 KCL

### 7.1 单位与符号

每个 terminal 必须记录：

- 日志原始列名和单位；
- device width 的来源；
- ATLAS 电流正负号映射；
- 转换到 A/µm 的公式。

不得在单位或电极映射未关闭前比较 A/B。

### 7.2 基线与噪声 floor

对每个 terminal `k`，以打击前最后 5 个 accepted 点计算：

```text
I0_k    = median(I_k,pre)
MAD_k   = median(|I_k,pre - I0_k|)
floor_k = max(1e-12 A/µm, 5 × MAD_k)
ΔI_k(t) = I_k(t) - I0_k
```

current-defined-SEB candidate 的绝对电流门为：

```text
I_SEB_GATE = max(floor_d, floor_s, 1e-6 A/µm)
```

其中 `1e-6 A/µm = 1 mA/mm`。它只用于 current-defined candidate，不是静态 BV 判据，也不是 thermal-runaway 判据。

### 7.3 KCL 与漏—源配对

逐 accepted 点计算：

```text
raw_KCL = |Id + Is + Ig| / max(|Id|, |Is|, |Ig|)
err_DS  = |ΔId + ΔIs| / max(|ΔId|, |ΔIs|)
err_KCL = |ΔId + ΔIs + ΔIg| / max(|ΔId|, |ΔIs|, |ΔIg|)
```

当分母未超过对应 floor 时，该点写 `NOT_EVALUABLE`，不得制造漂亮比例。

通过门：

- `raw_KCL ≤ 5%`；
- `err_DS ≤ 10%`；
- `err_KCL ≤ 10%`；
- `ΔId` 与 `ΔIs` 异号；
- 至少 3 个连续 accepted 点满足；
- current-defined candidate 还必须在 10–100 µs 晚窗口持续满足。

## 8. 四种 current-only 一级结果

每一臂只能给出以下四类之一。若等价门失败，则实验标为 `OFAT_INVALID`，不进入这四类。

为避免“仍在下降”和“已经形成平台”靠主观看图裁决，先定义晚窗口幅度：

```text
A(t) = max(|ΔId(t)|, |ΔIs(t)|)
Rlate = A(100 µs) / A(10 µs)
Slate = 对 10、20、50、100 µs 四点拟合得到的 d(log10 A)/d(log10 t)
```

只有四个晚时间点均为 accepted、且相应 `ΔId/ΔIs` 均高于各自 noise floor 时才计算 `Rlate/Slate`。低于 floor 时先走下面的独立恢复分支，不能直接判 `INSUFFICIENT_TIME_WINDOW`。

```text
RECOVERED_TO_FLOOR =
  打击后曾出现可分辨的 drain/source 响应峰
  AND |ΔId|、|ΔIs| 在至少两个连续 late accepted 点均低于各自 floor
  AND 进入 floor 之前的 accepted 点显示持续衰减且 KCL 通过
  AND 50→100 µs 不存在重新越过 floor 的回升
```

`RECOVERED_TO_FLOOR=TRUE` 时允许直接判 `SET_LIKE_CURRENT_RESPONSE`，不强迫对低于 floor 的点取对数或拟合 `Rlate/Slate`。若晚点低于 floor 但不满足上述完整恢复链，才进入未决/不足类。对仍高于 floor 的四点，趋势边界固定如下：

- 明确衰减：`Rlate ≤ 0.50` 且 `Slate ≤ -0.20`；
- 明确持续/增长：`Rlate ≥ 0.80` 且 `Slate ≥ -0.10`；
- 落在两者之间、两个指标互相矛盾或拟合受数值振荡支配：晚趋势未决。

### 8.1 SET_LIKE_CURRENT_RESPONSE

满足下列 A 或 B 分支，并通过 KCL 门：

**A. 高于 floor 的可拟合衰减分支**

1. 打击后出现可分辨的 drain/source 响应峰；
2. 在 10、20、50、100 µs 的 accepted 点上通过“明确衰减”门；
3. 50→100 µs 没有二次回升；
4. 100 µs 时已低于 `I_SEB_GATE`，或虽尚高于该门但 `Rlate/Slate` 均证明它在整个 10–100 µs 区间持续向基线收敛；
5. KCL 可评估且通过。

**B. 已恢复到 floor 分支**

1. `RECOVERED_TO_FLOOR=TRUE`；
2. 可评估区间内 raw KCL 与 baseline-subtracted KCL 通过；
3. 不要求对低于 floor 的点计算相对误差或 log-slope。

“向基线衰减”不要求在 100 µs 已完全回到零，但必须有连续晚期证据，而不是只看一个末点。

### 8.2 CURRENT_DEFINED_SEB_CANDIDATE

同时满足：

1. 10–100 µs 晚窗口内，漏/源基线差分电流持续异号配对；
2. `raw_KCL`、`err_DS`、`err_KCL` 均通过；
3. 10、20、50、100 µs 的 `|ΔId|` 与 `|ΔIs|` 均清楚高于 `I_SEB_GATE`；
4. 晚窗口通过“明确持续/增长”门；
5. 条件至少跨越完整的 10–100 µs 绝对保持区间，而非仅靠三个相邻 ps 点。

该标签只表示“端电流定义的 SEB 候选”。不得改写为正式空间 Phase 2 或 thermal-runaway SEB。

### 8.3 INSUFFICIENT_TIME_WINDOW

满足以下任一情况：

- 正常到达 100 µs，但晚期电流仍在变化，衰减与平台/回升无法区分；
- 终点前因预先声明的非数值硬停而结束，晚窗口不完整；
- 只有早期配对或早期峰值，没有足够的 10–100 µs accepted 点；
- `Rlate/Slate` 落入未决带、彼此矛盾或受明显数值振荡支配。
- 晚点落到 floor 附近，但既不满足 `RECOVERED_TO_FLOOR` 的连续恢复条件，也没有足够的高于-floor 点计算趋势。

### 8.4 NUMERICAL_TERMINATION

只有在配置/等价门已经通过的合法候选上，出现以下任一情况且发生在获得完整晚时间证据之前，才使用本标签：

- `Cannot trap` 或同类求解失败；
- 时间步持续折半后退出；
- 非物理 accepted 解、NaN/溢出或 ATLAS 异常终止；
- compliance/runner 行为意外截断，且不是预先声明的物理硬停；
- 求解器无法建立或保持目标静态母态，而几何、材料、电极、偏置和输入合同本身已通过配置门。

不得把数值终止重命名为 `INSUFFICIENT_TIME_WINDOW`。

若失败来自几何/电极/材料/热接触/输出合同不等价、候选语义错误或 benchmark exception 缺失，则优先记 `OFAT_INVALID`，不得用 `NUMERICAL_TERMINATION` 掩盖配置问题。

## 9. A/B 电流准确度比较

### 9.1 一级比较：分类是否一致

首先报告：A/B 是否得到相同的四类 current-only 结果。

- 分类一致：继续比较数值误差；
- 分类不同且两臂均通过等价门：结论是“结果对 mesh-generation route 敏感”，不能选更像预期的一臂为真；
- 任一臂 `OFAT_INVALID` 或数值终止：不得作准确度优劣排序。

### 9.2 二级比较：电流波形误差

在相同 accepted 时刻比较：

1. raw `Id/Is/Ig`；
2. baseline-subtracted `ΔId/ΔIs/ΔIg`；
3. 峰值幅度和峰值时间；
4. 0–10 ns、10 ns–1 µs、1–10 µs、10–100 µs 四段的带符号电荷积分；
5. 晚窗口稳健斜率；
6. KCL 指标。

当两臂信号均高于 floor 时，用对称相对差：

```text
δsym(a,b) = 2|a-b| / (|a|+|b|)
```

当任一信号低于 floor 时，只报告绝对差与 floor 的比值，不计算不稳定的相对误差。

预声明的“电流数值一致”门：

- 关键时刻 `δsym ≤ 10%`；
- 四段电荷积分 `δsym ≤ 10%`；
- 峰值时间差不超过相邻两个预声明输出点之间隔；
- 两臂各自 KCL 均通过。

这些门衡量两条数值路线的一致性，不等于实验真实性。

## 10. 运行时间与 accepted-step 比较

### 10.1 运行环境控制

未来若获授权，两臂必须：

- 使用相同 VM、ATLAS 版本、license 环境和 `-P4`；
- 不与其他 ATLAS 作业并发；
- 采用相同 runner、tmux/PTY 记录方式；
- 顺序执行，记录执行先后和机器负载；
- 不把 DevEdit 建模时间混入 ATLAS 瞬态时间后再作单一比较。
- benchmark deck 不含交互式 `tonyplot`；结构生成、ATLAS 求解与统一后处理分别计时，绘图时间不计入求解性能。

### 10.2 分段记录

分别记录：

- structure/mesh build wall time；
- ATLAS import/init wall time；
- static-bias wall time；
- transient 0–10 ns、10 ns–1 µs、1–10 µs、10–100 µs wall time；
- accepted transient steps；
- rejected/cutback steps；
- 可获得时记录 Newton iteration 总数；
- nodes、triangles、峰值内存；
- 每个 accepted step 的平均/中位 wall time。

### 10.3 性能裁决

- 首轮只报告原始差异，不从一次顺序跑断言稳定加速；
- 总瞬态时间差小于或等于 15%：记为“无明确性能优劣”；
- 差异大于 15%：只记为“性能差异候选”；若要形成性能结论，需未来另授权反序重复 B→A；
- accepted-step 数必须与 cutback 数共同解释，不能只用 wall time 排名。

## 11. 早停规则

早停不得破坏 SET 与 current-defined-SEB 的区分。

1. **配置/等价门失败即停**：标 `OFAT_INVALID`，不发粒子，不允许边跑边修另一臂；
2. **合法配置的静态求解失败即停**：仅当配置门已通过而求解器不能接受目标母态时，标 `NUMERICAL_TERMINATION`，不发粒子；
3. **数值失败即停**：保留最后 accepted 点，标 `NUMERICAL_TERMINATION`；
4. **100 µs 前不得仅凭峰值或漏—源配对宣布 candidate SEB**；
5. **100 µs 前不得仅凭电流下降几个点宣布 SET-like**；
6. 正常到达 100 µs 后，若四类判据仍不闭合，标 `INSUFFICIENT_TIME_WINDOW` 并停止；
7. 不在本轮自动延长到 1 ms 或更长，不自动改时间步、solver、物理参数或网格；
8. 一臂早停后，另一臂可以按原合同跑到同一预声明终点用于保存证据，但不得把不对称窗口作准确度排名。

## 12. 会使 OFAT 失效的不可避免非等价

以下任一项无法消除时，应选择 `CONTROLLED_COMPARISON_NOT_FEASIBLE`，而不是继续发射：

1. direct ATLAS 无法复现相同的 region 边界、厚 Nickel source/drain、单一厚 Nickel 阶梯 gate 及其 `elec.id=3` 接触语义；
2. mesher route 改变了金属/介质/半导体的实际接触长度或界面拓扑；
3. DevEdit 导入与 direct mesh 的材料/region 绑定无法得到同一 runtime material table；
4. 掺杂或陷阱不能在两条路线中形成相同的空间分布；
5. 同一 xion/半径/轨迹在两网格中穿过不同材料或不能满足相同分辨率合同；
6. thermal contact 的位置或面积不同；
7. 两臂无法使用同一求解序列、时间表和输出字段；
8. 任一臂不能到达相同 VGS/VDS 静态母态；
9. 打击前电流、关键电势或 |E| 超出 G3 等价门；
10. 为使其中一臂收敛，必须改 CLIMIT、METHOD、物理模型、材料、偏置或粒子源。

节点数、三角拓扑和 mesher 自然产生的局部插值差异是实验自变量，不属于上述失效项；但局部网格目标不达标属于失效项。

## 13. 技术可行性与未关闭缺口

### 13.1 技术上是否能只改变 mesh-generation route

**条件可行。** BV-derived DevEdit 几何的边界均为水平/垂直线段，因此 direct ATLAS 有机会用矩形 region 的组合表达；但其中存在凹多边形、一个 region 的多段 polygon、厚 Nickel 金属和电极—热接触耦合。B 臂可能需要把一个语义 region 拆成多个矩形。只有在拆分后仍能证明材料、接触长度、电极等势、热边界和掺杂分布完全等价，才能认定“只改变 mesh-generation route”。

如果 direct ATLAS 只能把厚金属改成零厚度 line electrode，或只能改变 oxide/Al₂O₃/NiO 的边界拓扑，则本 OFAT 不可行，不能用“尽量接近”代替。

### 13.2 当前为什么还不能发射

当前至少缺少：

1. 按第 2.3 节规范化 A 臂候选：恢复原始静态母态序列，移除未授权 Auger/`max.temp`，增加严格 source-off 五点 baseline、20/50 µs 输出，并移除交互式绘图；
2. 对规范化候选做 parser-only、DevEdit-only 和 runtime region/material/electrode/thermal-contact 验收；
3. 从实际 STR 关闭径迹中心和 `xion±3r` 的 Δx/Δy、中心 spacing、全 y 连续性门；
4. 用真实 accepted 状态关闭 300 V、暗态电流和母态 STR 门；
5. 判明 `MATERIAL region=10 mun=50` 与 NiO 热参数的 runtime 语义；
6. 明确处理现行 preflight ban 与“原样继承 p-type 2e6/旧 impact”的冲突，禁止静默绕过；
7. 从规范化 BV-derived SEB 候选机械派生 direct ATLAS twin deck；
8. 建立唯一坐标/区域/电极/掺杂语义映射表，明确单一厚 Nickel gate，禁止新增 `gate_fp`；
9. 两臂相同的 ROI 网格分辨率合同实测结果；
10. direct mesh 的结构图、网格图和 runtime material table；
11. A/B 静态 300 V 母态等价证据；
12. 两臂统一到 100 µs 的 accepted 输出、source-off baseline 和 STR 字段清单；
13. 发射前完整 diff，证明 shared physics body 没有漂移。

patch 来源完整性已经关闭，不再列为缺口。以上缺口需要未来单独授权“本地候选编制 + parser/mesh/300 V 静态 preflight”后分阶段关闭；该授权仍不包含成对 SEB 瞬态。本计划本身不创建候选 deck 或 RUN。

## 14. 未来计划审查包的最小交付（本轮不执行）

未来若用户另行授权编制，应先交付而不直接发射：

1. A/B 两份候选 deck 的绝对路径；
2. 公共 physics body 与两个 route block 的说明；
3. 完整 deck diff；
4. 坐标、region、材料、掺杂、陷阱和 electrode 映射表；
5. 两张结构图、两张网格图及 ROI Δx/Δy 表；
6. 各自预留的 tmux 会话名；
7. 统一输出时间/字段表；
8. 静态等价门计划；
9. 明确声明 `NO_CURRENT_DEFINED_SEB_CONCLUSION_BEFORE_100US`；
10. 用户书面批准、且只适用于本数值路线对照的 `benchmark-only exception`；
11. 用户对一次成对发射的独立核签。

## 15. 本轮授权边界

本文件仅是计划审查包。它没有授权：

- SSH 或读取远端新证据；
- DevEdit、ATLAS、DeckBuild、VictoryExtract/VictoryVisual；
- deck 修改或 direct-mesh twin 编制；
- 创建 RUN 编号或输出目录；
- 发射、监控、续跑、改参；
- branch/worktree；
- hashing；
- push 或其他外部发布。

## Final recommendation

**REVISE_BEFORE_COMPARISON**

理由：唯一血统母版已经纠正为本轮原始 `bv.in`，patch provenance 已独立通过，RUN238 已退出本计划；但 ZIP deck 仍只是 `CANDIDATE_PARENT / NOT_RUNTIME_VALIDATED`。它尚需恢复静态母态序列、去掉未授权 Auger/`max.temp`、建立严格 source-off baseline，并关闭 parser/mesh/300 V/热绑定门；现行 preflight ban 的 benchmark-only exception、direct ATLAS 双生 deck 和全部等价门也尚未建立。下一步只适合另行授权“本地候选编制 + parser/mesh/300 V 静态 preflight”，不适合直接授权成对 SEB 瞬态。
