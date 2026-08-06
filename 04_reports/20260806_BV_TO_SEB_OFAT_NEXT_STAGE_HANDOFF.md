# BV→SEB OFAT 下一阶段唯一交接入口

> Date: 2026-08-06
>
> Task status: `PARTIAL / PREPARED_NOT_RUNTIME_VALIDATED`
>
> Authorization boundary: local candidate preparation + parser/mesh/static-300-V preflight only
>
> Runtime outcome: `BLOCKED_BY_LOCAL_SILVACO_RUNTIME_UNAVAILABLE`

## 1. 结论先行

本轮已完成两臂候选 deck、坐标/区域映射、完整 A/B diff、统一后处理合同和本地预检报告。
但当前 Windows 主控环境找不到 `deckbuild/atlas/devedit`，而本轮又明确禁止 SSH/VM，因而：

```text
PARSER_A/B = NOT_EXECUTED
MESH_A/B = NOT_EXECUTED
STATIC_300V_A/B = NOT_EXECUTED
SEU_TRANSIENT = NOT_EXECUTED
```

没有用文本门冒充 SILVACO parser/runtime PASS，也没有伪造结构图、网格图、节点数、300 V STR
或端电流数据。当前不能提升任何候选为受控执行父本。

## 2. 本轮授权与边界

本轮允许：

1. 本地候选 deck 编制；
2. parser-only 检查；
3. DevEdit/direct-mesh 结构与网格生成检查；
4. 300 V source-off 静态等价预检；
5. 形成本交接并 scoped push。

本轮固定禁止：

```text
NO SEU TRANSIENT
NO PAIRED TRANSIENT
NO AUTOMATIC EXPANSION OF AUTHORIZATION
NO SSH / NO VM / NO NEW RUN / NO PARAMETER TUNING
```

用户已批准的窄范围例外为：

```text
LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB
```

它只允许 A/B 为保持原始 `bv.in` 血统而共同保留 substrate `Acceptors=2e6` 和旧 SELB
`2.5e6 / 3.96e7 / betan=1.37`；不等于 production preflight PASS，也不允许把结果命名为
production-qualified SEB。

## 3. 父本与候选身份

| 对象 | 身份 | 当前状态 |
|---|---|---|
| 原始 [`bv.in`](attachments/20260806_bv_to_seb_ofat/bv.in) | 唯一 lineage master | 原件未修改 |
| 原 ZIP deck [`bv_SEB_x10p25_300V.in`](attachments/20260806_bv_to_seb_ofat/bv_SEB_x10p25_300V.in) | `CANDIDATE_PARENT` | `NOT_RUNTIME_VALIDATED`，原件未修改 |
| [A 臂：DevEdit source-off 300 V 候选](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_A_bv_devedit_static300_sourceoff_preflight.in) | DevEdit 路线候选 | `PREPARED_NOT_RUNTIME_VALIDATED` |
| [B 臂：direct ATLAS mesh source-off 300 V 候选](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_B_bv_direct_atlas_static300_sourceoff_preflight.in) | direct-mesh 路线候选 | `CONDITIONAL_NOT_DEMONSTRATED` |

```text
CONTROLLED_EXECUTION_PARENT = NONE
```

历史 direct-mesh `seb_2` 没有向候选注入任何材料、掺杂、impact、热模型或 solver 参数。

## 4. 候选规范化做了什么

A/B 共同静态正文现在逐行相同，且共同：

- 保留原始几何/区域语义、掺杂、interface charge、mobility、legacy impact 与热模型血统；
- 删除 active Auger；
- 删除 `max.temp=50000`；
- 恢复 200→300 V 的 `vstep=15`；
- 恢复 gate-state `outf/load` 流；
- 完全移除 active `singleeventupset`、`tfinal` 与 `tonyplot`；
- 在 source 严格关闭的 300 V 静态状态请求 5 次 `solve previous` baseline 记录；
- 只把 10/20/50/100 µs 写成未来输出合同注释，本轮没有粒子瞬态。

A 臂保留原始 DevEdit 12 个 polygon/region，只增加 `x=10.10..10.40, y=0..0.60 µm`
的双向 `max.width/max.height=0.016 µm` 输入合同。B 臂把同一轴对齐边界机械表达为 direct
ATLAS mesh、矩形区域和厚 Nickel 电极候选。

完整变化见 [A/B 全量 diff](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_A_vs_B_complete.diff)，
坐标逐项映射见 [区域映射合同](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_AB_COORDINATE_REGION_MAP.md)。

## 5. 当前文本门与真实运行门

### 5.1 已完成的文本门

| 检查 | A | B |
|---|---:|---:|
| active `singleeventupset` | 0 | 0 |
| active `tfinal` | 0 | 0 |
| active Auger | 0 | 0 |
| active `max.temp` | 0 | 0 |
| active `tonyplot` | 0 | 0 |
| 300 V 段 `vstep=15` | 1 | 1 |
| source-off `solve previous` | 5 | 5 |
| active thermcontact | 2 | 2 |
| shared static block | 143 lines | 143 lines, byte-for-byte equal |

这些结果只证明候选文本满足合同，不证明语法可运行、偏压可到站或两臂物理等价。

### 5.2 未执行的真实门

| 必须回传的运行证据 | A | B |
|---|---|---|
| parser / fatal / warning | `NOT_EXECUTED` | `NOT_EXECUTED` |
| actual structure image | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| actual mesh image | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| nodes / triangles / obtuse | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| 径迹 ROI 实际 Δx/Δy 与全 y 连续性 | `NOT_EVALUABLE` | `NOT_EVALUABLE` |
| region/material runtime table | `NOT_EVALUABLE` | `NOT_EVALUABLE` |
| source/drain/gate terminal table | `NOT_EVALUABLE` | `NOT_EVALUABLE` |
| thermcontact ↔ elec.num 绑定 | `NOT_EVALUABLE` | `NOT_EVALUABLE` |
| VGS=0、VDS=300 V accepted | `NOT_EXECUTED` | `NOT_EXECUTED` |
| accepted 300 V STR + 五点 baseline | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| 300 V Id/Is/Ig、Tmax、势、电场 | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| 静态等价结论 | `NOT_EVALUABLE` | `NOT_EVALUABLE` |

详细证据见 [本地预检结果](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_AB_LOCAL_PREFLIGHT_RESULT.md)。

## 6. 尚未关闭的结构/语义硬门

除共同血统中的 `MATERIAL region=10 mun=50` 和 NiO `tcon.const tc.const=2.27` 需要运行时解释外，
B 臂还有两个路线特有硬门：

1. 为满足 direct ATLAS 每个 mesh point 必须有材料的要求而加入的 Air region 13，是否与 DevEdit
   未填充 work-area 背景电/热等价；
2. 两个同为 `name=gate, num=3` 的厚 Nickel 矩形，是否在目标版本中形成一个连续 stepped-gate
   terminal，而不是额外端子或错误覆盖。

任一门失败，直接：

```text
OFAT_INVALID
CONTROLLED_COMPARISON_NOT_FEASIBLE
```

不得为跑通而改成零厚度电极、独立 `gate_fp`、不同接触长度或不同热边界。

## 7. 后处理责任边界

[统一后处理合同](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_AB_POSTPROCESS_CONTRACT.md)
只是一份未执行规范：deck 负责输出 source-off baseline、accepted 时间点和 raw terminal currents；
floor、KCL、趋势拟合、四段带符号电荷积分和最终标签只属于统一 postprocess/analysis。

三层术语继续分离：

1. raw three-terminal current pairing；
2. Revision 4 formal spatial Phase 2；
3. thermal-runaway SEB。

本轮没有 transient 数据，因此三者均未作新裁决。

## 8. 给网页端的逐项审查问题

请网页端只基于本固定提交审查以下八项：

1. A 臂是否真正只改了径迹网格输入合同和 source-off 静态预检序列，而没有改变原始 12-region
   几何与 `bv.in` 物理血统？
2. B 臂以 Air region 13 作为背景的表达是否有明确 ATLAS 语义依据；若没有，是否应在运行前即裁决
   direct-mesh `OFAT_INVALID`？
3. 重复 region 3/4/12 和同号同名 gate electrode 的写法是否足以进入一次 parser/structure 预检，
   还是存在可在不改变拓扑前提下更可靠的 direct-ATLAS 表达？
4. A/B 的 source-off 300 V sequence 是否已经做到可比较；五次 `solve previous` 是否足以请求五个
   baseline accepted 记录，还是需要不改变物理状态的更明确日志写法？
5. `MATERIAL region=10 mun=50` 与 NiO 热参数是否应在一次 parser/runtime preflight 中原样保留并
   只观察解释，还是已构成运行前可确认的配置错误？
6. 当前双向 0.016 µm 径迹 ROI 合同是否适合作为 r=0.05 µm 的两臂共同预检目标？
7. 在没有本地 SILVACO 的情况下，本轮应保持 `PREPARED_NOT_RUNTIME_VALIDATED`，还是允许下一次
   单独授权仅限 VM/SSH parser + mesh + source-off 300 V 静态预检？
8. 下一授权是否应继续明确排除 SEU/paired transient，直到 A/B 均通过结构、网格、terminal、热边界
   和 300 V 静态等价门？

## 9. 建议裁决字段

请网页端按以下字段回复，避免把文本审计误当成运行验证：

```text
REVIEW_VERDICT: ACCEPT / REVISE
ARM_A_CANDIDATE_PREPARATION: PASS / REVISE
ARM_B_DIRECT_MESH_SYNTAX: CONDITIONAL / REVISE / NOT_FEASIBLE
AIR_BACKGROUND_EQUIVALENCE: NOT_DEMONSTRATED / PRECHECK_REJECT
STEPPED_GATE_TERMINAL_SEMANTICS: NOT_DEMONSTRATED / PRECHECK_REJECT
SOURCE_OFF_STATIC_SEQUENCE: PASS / REVISE
TRACK_MESH_INPUT_CONTRACT: PASS / REVISE
POSTPROCESS_RESPONSIBILITY_SPLIT: PASS / REVISE
RUNTIME_PREFLIGHT_REQUIRED: YES
NEXT_AUTHORIZATION: NO_EXECUTION / LIMITED_RUNTIME_PREFLIGHT_ONLY
```

## 10. 唯一下一步建议

```text
REVIEW_CANDIDATES_THEN_AUTHORIZE_LIMITED_RUNTIME_PREFLIGHT_ONLY
```

若网页端接受候选文本，下一次授权最多只允许两臂的 parser、结构/网格生成和 source-off 300 V
静态等价预检。即便该预检通过，也不得自动扩展到 SEU transient 或 paired transient。
