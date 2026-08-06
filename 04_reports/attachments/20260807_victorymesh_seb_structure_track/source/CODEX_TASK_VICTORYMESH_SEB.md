# Codex Desktop 目标任务：将 `str.txt` 改为 Victory Mesh 网格，并建立 SEB xion 贯穿径迹网格

## 任务性质

本任务允许目标模式下的本地/既有 TCAD VM 调研与结构网格执行，但只限 DevEdit + Victory Mesh。不得进入 ATLAS 求解、300 V 静态、SEU/SET/SEB 瞬态或任何参数拟合。

直接复用项目中已建立的 SSH alias、TCAD VM、tmux、标准 runner、STR 回传、结构图和网格分析流程。不要重新搭建或全面排查连接环境；只有具体命令失败时才检查该失败点。

## 固定输入

1. `str.txt`：唯一结构、区域、掺杂、厚 Nickel 电极和原始 DevEdit 网格血统。
2. `changban3(1).in`：仅作为 `DevEdit → Victory Mesh → load → line/refine → remesh → save mode=atlas` 的流程与语法参考。

禁止从 `changban3(1).in` 复制它的器件尺寸、材料参数、掺杂、介质层、接触、网格数值或物理模型。

## 原始目标

完成两个严格分开的结构网格阶段：

### 阶段 1：Victory Mesh 基线网格

把 `str.txt` 的 DevEdit 结构原样生成后交给 Victory Mesh 重网格，得到结构、区域、电极和掺杂均不变的 ATLAS-compatible 基线 STR。

### 阶段 2：SEB xion 贯穿径迹网格

在阶段 1 已通过的 Victory Mesh 基线流程上，只增加围绕粒子入射位置的二维局部网格控制，得到用于后续 SEB 的 track-refined STR。

固定粒子坐标合同：

```text
xion = 10.25 µm
r = 0.05 µm
track ROI x = 10.10–10.40 µm  (xion ± 3r)
track ROI y = 0.00–0.60 µm
actual max Δx ≤ 0.016 µm
actual max Δy ≤ 0.016 µm
full-y continuity = PASS
```

不得把单一中心节点列、输入 spacing、总节点数或图片外观当作二维网格合同通过。

## 第一步：定点生成 Victory Mesh 基线 deck

不要修改 `str.txt` 原件。创建派生文件：

```text
BV_VM_BASELINE_FROM_STR.in
```

保留 `str.txt` 中从开头到最终 DevEdit `structure` 语句的几何、12 个 region、impurity、厚 Nickel source/drain/gate 和既有 DevEdit 语句。唯一允许的 DevEdit 输出改动是把：

```silvaco
structure outf=mesh_A4.str
```

在派生文件中改为不会覆盖原文件的明确名称，例如：

```silvaco
structure outf=BV_DEVEDIT_RAW_FOR_VM.str
```

紧接该 `structure` 语句后追加 Victory Mesh 块，不要插入 ATLAS：

```text
go victorymesh
load DevEdit raw STR
建立适合当前横向、轴对齐、薄层结构的 Victory Mesh 网格控制
执行一次 remesh
保存为 ATLAS-compatible STR
quit
```

先查当前安装版本的 Victory Mesh 用户手册和例子库，确认正式命令。重点确认用户所说的 R 开头网格的准确名称，以及它与 Delaunay、Conformal、rectilinear/rectangular/custom volume mesh 的关系。

`changban3(1).in` 中的 `line x`、`line y`、`remesh delaunay`、region/interface `refine` 和 `save ... mode=atlas` 只作为已提供的成品流程参考。不得盲目认定 Delaunay 是当前横向器件的最佳路线；必须根据当前安装手册和横向器件例子，在运行前冻结唯一 mesher 路线。不得运行时自动 fallback 或同时试多种算法。

基线 Victory Mesh 必须至少在下列实际边界设置合适的 x/y 线或等价的当前版本语法：

```text
x = 0, 0.5, 1, 1.5, 2, 4, 6, 14, 14.5, 15 µm
y = -0.20, -0.18, -0.17, -0.12, -0.07, -0.02,
     0, 0.15, 0.20, 0.40, 0.60 µm
```

这些是结构边界，不是允许修改的几何参数。局部 spacing 必须由手册、模板和现有项目成功案例确定，不能直接复制 `changban3(1).in` 的数值。

阶段 1 输出建议：

```text
BV_VM_BASELINE_FROM_STR.str
```

阶段 1 必须真实验证：

- Victory Mesh 能读取 DevEdit raw STR；
- 输出可保存为 ATLAS-compatible 2D STR；
- 12 个语义 region 全部保留；
- source、drain、gate 仍只有 3 个电极；
- stepped gate 仍是单一连续厚 Nickel 电极；
- 无独立 `gate_fp`；
- region 几何、实际接触长度、材料界面和 impurity 不变；
- user material 50/51 或其实际映射没有丢失；
- 报告 nodes、triangles、网格质量、region/electrode 表；
- 输出真实结构图和网格图。

任一拓扑、材料、掺杂或电极内容丢失，阶段 1 立即失败，不得进入阶段 2，不得近似重建。

## 第二步：只增加 SEB xion 贯穿路径网格

只有阶段 1 完整通过后，复制阶段 1 deck 为：

```text
BV_VM_SEB_TRACK_X10P25.in
```

阶段 2 与阶段 1 的唯一允许差异是 Victory Mesh 中的 track-specific 网格语句和输出文件名。不得改变 DevEdit 结构块、mesher 类型、全局网格策略、region/interface 语义或物理血统。

在 Victory Mesh 块中，使用当前版本手册和例子支持的精确语法，建立真正二维的局部网格柱：

```text
x = 10.10–10.40 µm
y = 0.00–0.60 µm
```

要求：

- x 方向必须有多列节点覆盖 `xion±3r`，不能只在 `x=10.25` 放一列；
- y 方向必须从 `0` 贯穿到 `0.60 µm`；
- 在 `y=0, 0.15, 0.20, 0.40, 0.60 µm` 材料/区域边界处保持连续和足够细化；
- 目标区域实际 `max Δx`、`max Δy` 均不超过 `0.016 µm`；
- 不允许全器件无差别加密；
- 不允许改变边界坐标、厚金属、接触、材料或掺杂。

优先使用 Victory Mesh 的正式 line/custom-volume/box/shape/region refine 语法实现。若采用 Delaunay，必须证明 line + refine 能在最终 STR 中同时满足独立的 x/y 合同；若采用手册中的 R-tree/rectilinear/conformal 路线，必须给出其正式名称、手册位置和当前器件适用理由。

阶段 2 输出建议：

```text
BV_VM_SEB_TRACK_X10P25.str
```

阶段 2 必须使用生成 STR 实测：

- ROI 内所有相交三角形或网格单元的最大 x span；
- ROI 内所有相交三角形或网格单元的最大 y span；
- xion 中心及 `xion±3r` 的横向节点覆盖；
- y=0–0.60 µm 全路径连续性；
- 结构、12 region、3 electrode、厚 stepped gate 与阶段 1 一致；
- 阶段 1 与阶段 2 的语义差异只有网格。

阶段 2 合同失败时立即停止，不得自动换算法、放宽 `0.016 µm`、修改结构或反复试参。

## 运行范围

允许：

- 只读检索当前安装版本的 Victory Mesh 手册和例子库；
- 复用既有 SSH/tmux/runner；
- 运行阶段 1 的 DevEdit + Victory Mesh 一次；
- 阶段 1 通过后运行阶段 2 的 DevEdit + Victory Mesh 一次；
- 回传并分析真实 STR、日志、结构图和网格图；
- 编制唯一 GitHub handoff 并 scoped push。

禁止：

- `go atlas`；
- ATLAS parser、solve 或偏压；
- 300 V 静态；
- `singleeventupset`、`tfinal`；
- SEU、SET、SEB 或 paired transient；
- 修改 `str.txt` 原件；
- 修改 `changban3(1).in` 原件；
- 修改任何器件几何、region、电极、掺杂、材料和物理参数；
- branch/worktree；
- 自动 fallback；
- 失败后未经复审自动重跑。

固定声明：

```text
VICTORYMESH_STRUCTURE_MESH_ONLY
NO ATLAS
NO STATIC_BIAS
NO SEU_TRANSIENT
NO PAIRED_TRANSIENT
NO AUTOMATIC_EXPANSION_OF_AUTHORIZATION
```

## 执行顺序

1. 完整阅读两个输入文件。
2. 查本机 Victory Mesh 手册和横向器件例子，确定正式 mesher 名称和唯一路线。
3. 编制阶段 1 deck、完整 diff 和静态扫描。
4. Review for bugs，再做第一性原理简化检查。
5. 执行阶段 1 一次。
6. 阶段 1 失败则停止并交接证据。
7. 阶段 1 通过后编制阶段 2 deck、完整 mesh-only diff 和静态扫描。
8. Review for bugs，再做第一性原理简化检查。
9. 执行阶段 2 一次。
10. 测量真实 STR，形成最终 handoff，push 后停止。

## 必须交付

- `BV_VM_BASELINE_FROM_STR.in`
- `BV_VM_BASELINE_FROM_STR.str`（若阶段 1 成功）
- `BV_VM_SEB_TRACK_X10P25.in`（仅阶段 1 通过后）
- `BV_VM_SEB_TRACK_X10P25.str`（若阶段 2 成功）
- 两阶段完整 diff；
- Victory Mesh 手册/例子依据；
- mesher 选择裁决；
- 完整 typescript/stdout/stderr；
- 两阶段结构图与网格图；
- region/electrode/material/impurity 保留表；
- 阶段 1 与阶段 2 nodes/triangles/网格质量；
- track ROI 实测 CSV；
- 阶段 1 与阶段 2的语义等价审计；
- 单一 GitHub line-by-line handoff。

最终回复必须给出固定 `blob/<commit>/...` handoff 链接，并明确：

```text
STAGE1_RESULT:
STAGE2_RESULT:
MESHER_FAMILY_AND_EXACT_COMMAND:
DEVEDIT_STR_LOAD:
ATLAS_MODE_SAVE:
REGION_COUNT:
ELECTRODE_COUNT:
THICK_GATE_PRESERVED:
BASELINE_STR:
TRACK_STR:
TRACK_MAX_DX:
TRACK_MAX_DY:
FULL_Y_CONTINUITY:
ATLAS_EXECUTED: NO
STATIC_BIAS_EXECUTED: NO
SEU_TRANSIENT_EXECUTED: NO
COMMIT:
FIXED_HANDOFF_URL:
```
