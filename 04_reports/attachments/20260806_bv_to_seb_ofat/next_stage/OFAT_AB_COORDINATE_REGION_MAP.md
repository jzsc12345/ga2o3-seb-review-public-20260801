# OFAT A/B 坐标、区域、材料、掺杂与电极映射

> Provenance: Codex-generated / post-2026-07-27-09:20 / lower-trust
>
> Status: TEXT CONTRACT / NOT RUNTIME VALIDATED
>
> Label: `LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB`

## 1. 固定血统

- 唯一血统母版：`../bv.in`。
- A 臂：DevEdit polygon 与原始 12 个 region 保持不变，仅把径迹预留网格改成显式双向上限。
- B 臂：把同一组轴对齐 polygon 机械拆成 direct ATLAS 矩形并集。
- A/B 从 `SHARED STATIC PHYSICS AND BIAS BLOCK START` 起逐行相同。
- 本文件不证明 parser、结构、网格或 300 V 到站。

## 2. 器件边界与语义区域

| 语义 | 原始编号 | 材料 | 几何（µm） | 掺杂 | B 臂表达 |
|---|---:|---|---|---|---|
| substrate | 1 | Ga2O3 | x=0..15, y=0.40..0.60 | Acceptors=2e6 | 单矩形 region 1 |
| uid | 2 | Ga2O3 | x=0..15, y=0.20..0.40 | Donors=1.5e15 | 单矩形 region 2 |
| channel | 3 | Ga2O3 | x=0..15, y=0.15..0.20；x=1..14, y=0..0.15 | Donors=1e17 | 两个同编号矩形并集 |
| oxide-left | 4 | SiO2 | x=0.5..2, y=-0.17..-0.02 | 无 | region 4 第一个矩形 |
| oxide-right | 4 | SiO2 | x=4..14.5, y=-0.17..-0.02 | 无 | region 4 第二个矩形 |
| source n+ | 5 | Ga2O3 | x=0..1, y=0..0.15 | Donors=5e19 | 单矩形 region 5 |
| drain n+ | 6 | Ga2O3 | x=14..15, y=0..0.15 | Donors=5e19 | 单矩形 region 6 |
| barrier | 7 | Al2O3 | x=0.5..14.5, y=-0.02..0 | 无 | 单矩形 region 7 |
| P- | 8 | NiO | x=2..4, y=-0.07..-0.02 | Acceptors=1.3e18 | 单矩形 region 8 |
| P+ | 9 | NiO | x=2..4, y=-0.12..-0.07 | Acceptors=3e19 | 单矩形 region 9 |
| source metal | 10 | Nickel | x=0..0.5, y=-0.18..0 | 无 | region 10 + electrode 1 |
| drain metal | 11 | Nickel | x=14.5..15, y=-0.18..0 | 无 | region 11 + electrode 2 |
| stepped gate | 12 | Nickel | x=1.5..6, y=-0.20..-0.17；x=2..4, y=-0.17..-0.12 | 无 | 两个 region 12 矩形 + 两个同名同号 gate electrode |

active interface charge 在两臂共同正文中保持：

```text
qf=-9e12, x=2..4, y=-0.02..0.02
```

trap 仅是注释，A/B 都没有 active trap。

## 3. B 臂显式 Air 背景

ATLAS 手册要求命令式矩形网格的每一个 mesh point 都有材料。DevEdit 母版在
`work.area x=0..15, y=-0.2..0.6` 内保留了未被 12 个物理 region 填充的上部背景；B 臂用
region 13 `Air` 先覆盖 work area，再由 1..12 覆盖相应物理区域。

这只是**候选映射**，当前不能写成已经等价。实际 parser/structure 图必须回答：

1. DevEdit 未填充背景在 STR 中是否确实等价于 Air；
2. region 13 是否会改变热/电边界或 region runtime table；
3. region 13 先定义、随后使用 1..12 的顺序是否被本地版本接受。

任一答案是否定或不唯一，B 臂标记 `OFAT_INVALID`，不得改成近似结构。

## 4. 电极合同

| terminal | 编号 | 厚金属边界 | 与半导体接触边界 | B 臂候选语义 |
|---|---:|---|---|---|
| source | 1 | x=0..0.5, y=-0.18..0 | y=0, x=0..0.5 | 一个厚 Nickel region/electrode |
| drain | 2 | x=14.5..15, y=-0.18..0 | y=0, x=14.5..15 | 一个厚 Nickel region/electrode |
| gate | 3 | 两段连续 stepped Nickel | 经 NiO/oxide 的 gate 边界保持原坐标 | 两个矩形声明同为 `name=gate, num=3` |

ATLAS 用户手册说明：多个 `ELECTRODE` 语句可以使用同一 NAME，同名节点按电气连接处理，电流合并；
本地项目也存在重复 `num=12 name=gate` 的 direct-ATLAS 写法。以上只是语法依据，仍必须由本版本
parser/runtime 表确认：最终只能出现 source/drain/gate 三个 terminal，gate 全部节点等势，不能生成独立
`gate_fp`。

## 5. 网格合同

未来粒子源只作为坐标合同存在，本轮没有 active source：

```text
xion = 10.25 µm
r = 0.05 µm
xion ± 3r = 10.10..10.40 µm
y = 0..0.60 µm
```

| ROI | 预声明最大 Δx | 预声明最大 Δy | 当前证据 |
|---|---:|---:|---|
| 径迹核心与 ±3r | 0.016 µm | 0.016 µm | 仅输入合同，STR 未生成 |
| 全 y 径迹 | 0.016 µm | 0.016 µm | 连续性未实测 |
| channel/oxide | 继承 A 的既有细化；B 在 y=-0.02/0 设置 0.002 µm | 同左 | 未实测 |
| stepped-gate/FP 端点 | B 在 x=6 设置 0.010 µm，y=-0.17 设置 0.002 µm | 同左 | 未实测 |
| source/drain 结 | B 在 x=1/14 设置 0.020 µm，y=0/0.15 设置 0.002/0.008 µm | 同左 | 未实测 |
| NiO/Ga2O3 与 thermcontact | 关键 y 边界均显式 mesh line | 见候选 deck | 未实测 |

总节点数不能替代这些 ROI 的实际 Δx/Δy。A 臂的 `constr.mesh max.width/max.height=0.016` 和 B 臂
`x.mesh/y.mesh` 都只是输入意图；只有生成后的 STR 才能关门。

## 6. 必须保持的共同正文

共同正文保留母版的：

- Ga2O3、Al2O3、NiO 显式卡；
- `MATERIAL region=10 mun=50`（虽指向 source Nickel，runtime 意义仍是阻塞项）；
- Ga2O3 mobility；
- interface qf；
- legacy SELB `2.5e6/3.96e7/betan=1.37`；
- `lat.temp` 与两个 source/drain thermcontact；
- METHOD、bias ramp、gate state outf/load、五点 source-off baseline；
- 相同 OUTPUT 与静态比较点。

候选规范化已经从 active 路径删除：Auger、`max.temp=50000`、`singleeventupset`、所有 `tfinal`、
`tonyplot`。这些删除尚未经过 SILVACO parser/runtime 验证。

## 7. 当前结论

```text
COORDINATE_MAP = TEXTUALLY_COMPLETE
SHARED_PHYSICS_BODY = TEXTUALLY_IDENTICAL
PARSER_RESULT_A = NOT_EXECUTED
PARSER_RESULT_B = NOT_EXECUTED
STRUCTURE_EQUIVALENCE = NOT_DEMONSTRATED
DIRECT_MESH_FEASIBILITY = CONDITIONAL_NOT_DEMONSTRATED
```

