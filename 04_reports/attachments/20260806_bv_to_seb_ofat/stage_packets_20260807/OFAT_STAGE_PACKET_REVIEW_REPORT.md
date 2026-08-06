# BV→SEB OFAT stage packet 静态审查报告

> Status: `STAGE_PACKETS_PREPARED / NOT_RUNTIME_VALIDATED`
>
> Source fixed commit: `994d83bc444e7a17695f003b65f0d90da25c8023`
>
> Web verdict: `ACCEPT_OPTION_A_WITH_STAGED_AUTHORIZATION`
>
> `LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB`
>
> `NO SSH EXECUTION / NO VM UPLOAD / NO DECKBUILD EXECUTION / NO DEVEDIT EXECUTION / NO ATLAS EXECUTION / NO 300V STATIC EXECUTION`
>
> `NO SEU TRANSIENT / NO PAIRED TRANSIENT / NO AUTO_FIX AFTER FAILURE / NO AUTOMATIC EXPANSION OF AUTHORIZATION`

## 1. 结论

两份冻结候选可以在不改动其正本、不改物理/数值语句的条件下机械拆为五个 stage packet：A1、A2、A3、B1、B2。每个 packet 的所有非注释语句（除 A1/A2/B1 为阶段止损新增的单个 `quit`）都是对应冻结候选原始语句的精确、顺序不变子序列。

本轮没有运行任何 packet。以下 `PASS` 仅指文本抽取与禁止命令静态扫描通过，不是 parser、结构、网格、材料、terminal、thermcontact 或 300 V 运行门通过。

`B1B_ZERO_BIAS_INIT_REQUIRED = NOT_ESTABLISHED`。没有在本轮得到“必须 `solve init` 才能输出可检查 STR”的可执行证据，因此没有创建 B1B packet。

## 2. 冻结来源与机械抽取

| Packet | 冻结来源 | 保留原行 | 删除原行 | 新增 active 行 |
|---|---|---:|---:|---|
| A1 | `OFAT_A_bv_devedit_static300_sourceoff_preflight.in` | 1–228 | 229–378 | `quit` |
| A2 | 同上 | 1–8；230–336 | 9–229；337–378 | `quit` |
| A3 | 同上 | 1–8；230–378 | 9–229 | 无 |
| B1 | `OFAT_B_bv_direct_atlas_static300_sourceoff_preflight.in` | 1–189 | 190–228 | `quit` |
| B2 | 同上 | 1–228 | 无 | 无 |

统一新增内容仅为注释型来源/阶段标签；A1、A2、B1 另加阶段结束所需 `quit`。没有新增或改写输出文件名。冻结 A/B 候选未覆盖、未格式化、未暂存。

## 3. 修订后的门序

### Arm A

1. **A1 — DEVEDIT_STRUCTURE_MESH_PACKET**：`go devedit` 至原 `structure outf=OFAT_A_bv_devedit_mesh_x10p25.str`，随后停止；无 `go atlas`，无 `solve`。
2. **A2 — ATLAS_INPUT_AND_BINDING_PACKET**：加载 A1 预期 STR，保留共享 material/models/impact/thermcontact/probe/METHOD/OUTPUT；在首个 `solve` 前停止。
3. **A3 — SOURCE_OFF_300V_STATIC_PACKET**：从同一 A1 STR 独立加载，保留原 gate outf/load、`vstep=15` 至 300 V、两次 save 与五次 `solve previous`；无粒子源、无瞬态。

### Arm B

1. **B1 — ATLAS_INPUT_STRUCTURE_MESH_PACKET**：保留 direct-ATLAS mesh/region/doping/electrode 和共享声明，在原首个 `solve init` 前停止。
2. **B1B — 未创建**：是否需要零偏 `solve init` 才能得到可检查 STR 尚未证明，不能自行扩权。
3. **B2 — SOURCE_OFF_300V_STATIC_PACKET**：保留完整 direct-ATLAS 输入和冻结 source-off 300 V 静态序列；无粒子源、无瞬态。

## 4. 禁止行为静态扫描

| Packet | SEU | tfinal | solve | 瞬态 solve | go devedit | go atlas | structure | save | quit | system/ssh/shell |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
| A2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| A3 | 0 | 0 | 15 | 0 | 0 | 1 | 0 | 2 | 1 | 0 |
| B1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| B2 | 0 | 0 | 15 | 0 | 0 | 1 | 0 | 2 | 1 | 0 |

对五个 packet 的 active 语句逐行比较结果：

```text
PARAMETER_VALUE_CHANGES = NO
PHYSICS_MODEL_CHANGES = NO
CONTACT_REGION_DOPING_MESH_COORDINATE_CHANGES = NO
ACTIVE_STATEMENT_PRESERVATION = PASS_EXACT_SUBSEQUENCE
```

A3/B2 的 15 条 `solve` 与冻结候选一致：`solve init`、`solve prev`、gate 0 V outf/load、0.01/0.1/0.5 V、1 V 步进至 10 V、5 V 至 50 V、10 V 至 200 V、15 V 至 300 V、五次 `solve previous`。没有 `singleeventupset`、`tfinal` 或 time-domain solve。

## 5. 仍开放、不得写成 PASS 的门

1. DeckBuild batch 没有已确认的 parse-only stage selector。
2. A2 在第一个 solve 前能得到哪些真实 runtime table 未验证。
3. B1 在不执行 `solve init` 时能否生成可检查 STR 未验证。
4. B 的 Air region 13 电学、热学与拓扑语义未验证。
5. B 中重复 region 3/4/12 的 union/覆盖语义未验证。
6. B 中两个同名同号 gate electrode 是否形成唯一连续 terminal 未验证。
7. `MATERIAL region=10 mun=50` 的 parser/runtime 解释未验证。
8. NiO `tcon.const tc.const=2.27` 的 parser/runtime 解释未验证。
9. 五次 `solve previous` 是否产生五个可辨识 accepted baseline 点未验证。

## 6. 下一轮建议授权（本轮没有授予）

| 顺序 | Packet | 建议范围 | 到站后必须停止 |
|---:|---|---|---|
| 1 | A1 | 单次 DevEdit structure/mesh | 是 |
| 2 | A2 | 单次 ATLAS input/binding gate，无 solve | 是 |
| 3 | B1 | 单次 direct-ATLAS input gate，无 solve | 是 |
| 4 | 条件 B1B | 仅当网页端另行核签零偏 init packet | 是 |
| 5 | A3 | 仅在 A1/A2 通过后，source-off 300 V | 是 |
| 6 | B2 | 仅在 B1 或获批 B1B 通过后，source-off 300 V | 是 |

各步必须独立核签；任一失败不得自动修 deck、改参数或进入下一步。即使 A3/B2 成功，也不进入 SEU 或 paired transient。

