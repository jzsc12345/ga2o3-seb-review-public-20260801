# 网页端唯一入口：BV→SEB 候选规范化与 DevEdit/direct-mesh OFAT 核签

> Provenance: Codex-generated / post-2026-07-27-09:20 / lower-trust；需网页端独立复核
>
> Date: 2026-08-06
>
> Current stage: `PLAN_REVIEW_PACKAGE / REVISE_BEFORE_COMPARISON`
>
> Authorization: `DOCUMENTATION_AND_PUBLICATION_ONLY / NO_SIMULATION_AUTHORIZATION`

## 0. 一句话状态

原始 `bv.in` 是结构、区域、掺杂、迁移率和 impact 血统的唯一母版；ZIP 内
`bv_SEB_x10p25_300V.in` 仍只是 `CANDIDATE_PARENT / NOT_RUNTIME_VALIDATED`。本轮只请网页端核签
“如何把候选规范化并关闭 parser/mesh/300 V 静态门”，不授权任何 SEB 瞬态或 A/B 对照发射。

## 1. 任务目标与背景决策

目标是准备一个最小 OFAT：

- A 臂：由原始 `bv.in` 转换出的 DevEdit SEB 候选；
- B 臂：从 A 臂机械转写的 direct ATLAS mesh twin；
- 唯一计划变量：结构/网格生成路线；
- 只比较晚期三端电流响应、运行时间与 accepted-step 数；
- 当前不判断哪条网格路线“物理更准确”。

此前已撤回 `RUN238` 作为受控父本的判断。历史 direct-mesh `seb_2` 只可提供运行时间和晚时间输出
预算参考，不能提供材料、impact、热边界、粒子源或 solver 参数。

## 2. 三层术语必须严格分开

| 层级 | 本包允许的表述 | 本包禁止的越级结论 |
|---|---|---|
| 原始三端电流配对 | `RAW_TERMINAL_DS_PAIRING=OBSERVED/NOT_OBSERVED`，并报告 raw/baseline-subtracted KCL | 不能单独称为正式 Phase 2 |
| Revision 4 正式空间 Phase 2 | 需端电流门、同一保持区间三帧 `Jn` 源漏连通、横截面通量闭合和绝对保持时间 | 不能由 `|Id|≈|Is|`、单帧或电子浓度图替代 |
| 热失控 SEB | 需独立的后段 `Id↑ + impact↑ + Tmax↑` 正反馈证据 | 不能由端电流配对或一次温升推出 |

本 OFAT 当前只计划输出 `SET_LIKE_CURRENT_RESPONSE`、`CURRENT_DEFINED_SEB_CANDIDATE`、
`INSUFFICIENT_TIME_WINDOW`、`NUMERICAL_TERMINATION` 或前置等价失败 `OFAT_INVALID`。

## 3. 最新网页端独立裁决

完整原文见 [LATEST_WEB_REVIEW_VERDICT_20260806.md](attachments/20260806_bv_to_seb_ofat/LATEST_WEB_REVIEW_VERDICT_20260806.md)。

```text
REVIEW_VERDICT = REVISE
CONTROLLED_LINEAGE_MASTER = original bv.in
ZIP_DECK = CANDIDATE_PARENT / NOT_RUNTIME_VALIDATED
CONTROLLED_EXECUTION_PARENT = NONE
DIRECT_MESH_TWIN = mechanically derived from normalized candidate only
COMPARISON_READY = NO
FINAL_RECOMMENDATION = REVISE_BEFORE_COMPARISON
```

已经关闭的事实门：patch 可应用于本轮原始 `bv.in`，结果与 ZIP 候选一致；原器件是一个连续的厚
Nickel gate，没有独立 `gate_fp`；几何、12 个 region、厚 Nickel 电极、active impurity、mobility、
impact 与 active interface charge 在转换中保持。两份 deck 均未启用 active trap，只能说 trap 注释未变。

## 4. 仍未关闭的阻塞项

### 4.1 静态母态与物理正文发生额外变化

候选相对原始 `bv.in` 还新增/改变：

1. 新增 `auger`，但没有显式 Auger 参数；
2. 新增 `max.temp=50000`；
3. 200→300 V 从 `vstep=15` 改为 `vstep=10`；
4. 移除了原始 gate 状态的 `outf/load` 流。

修订计划建议：恢复原始静态序列；移除新增 `auger` 和 `max.temp=50000`；A/B 共享同一份规范物理正文。

### 4.2 source-off baseline 尚未成立

候选 C 源在 `t=0` 为 `exp(-4)≈0.0183`，且 source statement 位于静态爬压前。正式比较前至少需要：

- 粒子源尚未声明，或运行证据证明严格为零；
- `VGS=0 V、VDS=300 V` 真实 accepted；
- 同一静态母态下 5 个 accepted、source-off baseline 点；
- baseline 后才声明/开启同一粒子源。

这必须经过 parser/短静态门验证，不能只靠文本推测。

### 4.3 网格、热边界与 runtime 门尚未成立

1. 五个 `refine mode=x` 窗口没有证明 y 向分辨率；需实际 STR 的 Δx/Δy、中心 spacing 和全 y 连续性；
2. `vfinal=300` 只是输入目标，不是 accepted 300 V 证据；
3. `thermcontact` 与 `elec.num` 的实际绑定未验证；
4. `MATERIAL region=10 mun=50` 指向厚 Nickel source，需判定是报错、忽略或误施加；
5. NiO `tcon.const tc.const=2.27` 的 runtime 解释未验证；
6. 候选没有显式产生 20 µs、50 µs 判据点与对应 STR；
7. 末尾交互式 `tonyplot` 必须从 benchmark 计时路径移除；
8. A/B 必须显式统一 10/20/50/100 µs accepted 输出和保存字段。

### 4.4 legacy benchmark 例外尚未批准

原始 `bv.in` 含 `Acceptors=2e6` 与旧 impact `2.5e6/3.96e7/betan=1.37`。它们是母版血统而非转换新增，
但违反现役 production preflight。若保留，只能由用户单独书面批准：

```text
benchmark-only exception
LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB
```

该例外只服务于 DevEdit/direct-mesh 数值路线比较；不能提升为生产物理参数，也不能静默改值绕过门禁。

### 4.5 current-only 判据还需落入 deck

计划已经补入“回落到噪声底”的 SET 分支：如果曾存在可分辨峰值，且 ΔId/ΔIs 在至少两个连续晚期 accepted
点低于各自 floor、50→100 µs 无回升并通过 KCL，可判 `SET_LIKE_CURRENT_RESPONSE`，不强迫对噪声底下点
计算 log slope。该判据仍需与四段电荷积分、`OFAT_INVALID` 优先级一起落实到候选正文。

## 5. 完整附件索引

本节是公开提交的文件清单，也是网页端逐行复核的导航。二进制 ZIP 保留原包；同时拆出四个文本成员。

| 仓库路径 | 角色 | 来源/性质 | 证据等级 | 支持问题 |
|---|---|---|---|---|
| [本交接入口](20260806_BV_TO_SEB_OFAT_AUTHORIZATION_HANDOFF.md) | 唯一入口 | Codex 生成 | 导航/低信任 | 全部 |
| [完整修订计划](../03_codex_harness/docs/exec-plans/active/20260806_devedit_vs_direct_atlas_mesh_current_only_ofat_plan_review.md) | 完整修订计划 | Codex 生成、吸收网页裁决 | 待核签计划 | Q1–Q7；重点 §7–§13 |
| [原始 bv.in](attachments/20260806_bv_to_seb_ofat/bv.in) | 唯一结构/物理血统母版 | 用户上传原件的附件缓存副本 | 权威源证据 | Q1、Q3、Q5、Q6 |
| [原始转换 ZIP](attachments/20260806_bv_to_seb_ofat/BV_to_SEB_package.zip) | 原始转换包 | 用户原始二进制附件 | 权威封装证据 | Q1、Q8 |
| [候选 deck](attachments/20260806_bv_to_seb_ofat/bv_SEB_x10p25_300V.in) | DevEdit SEB 候选 | ZIP 原始成员/复制 | 候选、未运行 | Q1–Q4、Q7 |
| [转换 patch](attachments/20260806_bv_to_seb_ofat/bv_to_SEB.patch) | 转换差异 | ZIP 原始成员/复制 | 权威差异证据 | Q1、Q3 |
| [粒子源 C 文件](attachments/20260806_bv_to_seb_ofat/mySEU_bv.c) | 粒子源 | ZIP 原始成员/复制 | 候选源证据 | Q4、Q7 |
| [原转换说明](attachments/20260806_bv_to_seb_ofat/BV_to_SEB_conversion_notes.md) | 原转换说明 | ZIP 原始成员；与用户单独上传说明字节一致 | 支持材料 | Q1–Q4 |
| [最新网页裁决](attachments/20260806_bv_to_seb_ofat/LATEST_WEB_REVIEW_VERDICT_20260806.md) | 最新网页裁决 | 用户粘贴的网页端独立审查 | 审查权威 | Q1–Q8 |
| [lessons.md](../lessons.md) | 永久交接规则 | Codex 根据用户纠正追加 | 流程规则 | 后续交接 |

## 6. 逐行审查定位

| 复核主题 | 先看位置 |
|---|---|
| 父本身份与 ZIP 候选边界 | 本入口 §0、§3；计划 §0、§2 |
| 三层术语边界 | 本入口 §2；计划 §1 |
| 转换保真与额外物理/数值变化 | 本入口 §3–§4.1；计划 §2.2、§7 |
| source-off baseline | 本入口 §4.2；计划 §7.4、§8 |
| 网格和 runtime 门 | 本入口 §4.3；计划 §7.5–§7.7、§11 |
| current-only 分类和低于 floor 的 SET | 本入口 §4.5；计划 §5、§9 |
| direct-mesh 等价与 OFAT 失效条件 | 计划 §7、§11、§12 |
| benchmark-only 例外 | 本入口 §4.4；计划 §7.9、§13 |

## 7. 请网页端回答的精确问题

1. 候选规范化是否完整吸收最新网页审查的 12 条强制修订？
2. 下一授权是否只限“本地候选编制 + parser/mesh/300 V 静态 preflight”，且明确不含 SEB 瞬态？
3. 是否应恢复 `vstep=15` 与等价 `outf/load`，并删除新增 `auger`/`max.temp=50000`？
4. source-off 五点 baseline 合同是否充分；应使用哪一种可实测的 ATLAS source 启停语法？
5. direct ATLAS twin 能否保留厚 Nickel source/drain/阶梯 gate、单一 `elec.id=3` 和真实接触长度？
6. 是否批准 legacy `benchmark-only exception`？若拒绝，本 OFAT 是否直接判不可执行？
7. region 10 `mun=50` 或 NiO 热参数 runtime 语义异常时，是否必须停下另开父本修订？
8. 原 ZIP 与拆出文本成员是否足以独立复核；还需要补充哪些原始证据？

## 8. 建议网页端回复格式

```text
REVIEW_VERDICT: ACCEPT | REVISE
CANDIDATE_PREPARATION_SCOPE: ACCEPT | REVISE
STATIC_SEQUENCE: ACCEPT | REVISE
SOURCE_OFF_BASELINE: ACCEPT | REVISE
DIRECT_MESH_EQUIVALENCE: FEASIBLE | CONDITIONAL | NOT_FEASIBLE
BENCHMARK_ONLY_EXCEPTION: APPROVE | REJECT | USER_DECISION_REQUIRED
RUNTIME_GATE_ORDER: ACCEPT | REVISE
ATTACHMENT_COMPLETENESS: PASS | REVISE
MANDATORY_REVISIONS:
1. ...
NEXT_AUTHORIZATION:
...
```

## 9. 本次公开提交的精确范围

只提交以下 10 个文件：本入口、修订计划、原始 `bv.in`、原始 ZIP、ZIP 四个文本成员、最新网页裁决、
`lessons.md`。不提交、不暂存、不清理任何无关文件。

## 10. 授权和禁止边界

本 handoff 及其公开提交**不授权**：SSH、DevEdit、ATLAS、DeckBuild、任何仿真、修改 simulation deck、
创建新 RUN、调整物理参数、创建 branch/worktree、覆盖结果或处理无关仓库文件。网页端建议也不自动产生
执行权；后续动作仍需用户把明确核签发回执行端。

## 11. 期望的下一裁决

当前推荐保持：

```text
REVISE_BEFORE_COMPARISON
```

只有网页端确认候选规范化合同和 benchmark-only 边界后，才讨论一次独立、受限的本地候选准备授权；
该授权仍不得自动扩大为 paired SEB transient。
