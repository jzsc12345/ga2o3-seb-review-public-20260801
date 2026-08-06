# BV→SEB OFAT stage packet 唯一交接入口

> Status: `STAGE_PACKETS_PREPARED / WAITING_FOR_WEB_REVIEW / NOT_RUNTIME_VALIDATED`
>
> Source fixed commit: `994d83bc444e7a17695f003b65f0d90da25c8023`
>
> Upstream stop handoff: [G1 前停止交接](20260806_BV_TO_SEB_OFAT_LIMITED_RUNTIME_PREFLIGHT_STOP_HANDOFF.md)
>
> Web verdict received: `ACCEPT_OPTION_A_WITH_STAGED_AUTHORIZATION`
>
> `LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB`

## 1. 本轮结果

已按网页裁决把冻结 A/B 完整候选机械抽取为五个 stage packet，并生成来源 manifest、逐 packet 完整 unified diff、禁止行为扫描和审查报告。

本轮没有上传、SSH 或运行任何 packet。没有生成日志、STR、结构图或网格图；也没有创建 RUN 编号。

```text
NO SSH EXECUTION
NO VM UPLOAD
NO DECKBUILD EXECUTION
NO DEVEDIT EXECUTION
NO ATLAS EXECUTION
NO 300V STATIC EXECUTION
NO SEU TRANSIENT
NO PAIRED TRANSIENT
NO AUTO_FIX AFTER FAILURE
NO AUTOMATIC EXPANSION OF AUTHORIZATION
```

## 2. 阶段隔离问题与裁决

冻结候选 A/B 都把结构/输入声明与 300 V 静态序列放在同一 deck 中，而标准 batch 不提供已确认的 parse-only/行范围阶段选择器。上一轮因此正确停止在 G1 前；这不是 parser 或候选物理失败。

网页端采用方案 A：冻结候选正本不变，允许新建“只删除后续阶段语句”的派生 packets，先公开审查，之后再逐个核签运行。本轮只完成 packets 与文档发布。

## 3. 冻结候选

- [Arm A 完整候选](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_A_bv_devedit_static300_sourceoff_preflight.in)
- [Arm B 完整候选](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_B_bv_direct_atlas_static300_sourceoff_preflight.in)

```text
CANDIDATE_A_UNCHANGED = YES
CANDIDATE_B_UNCHANGED = YES
CANDIDATE_BYTES_MUST_REMAIN_UNCHANGED = YES
```

## 4. 门序与 packets

### Arm A

```text
A1 DEVEDIT_STRUCTURE_MESH_PACKET
  → 未来仅生成 DevEdit STR/结构/网格证据；无 ATLAS/solve
A2 ATLAS_INPUT_AND_BINDING_PACKET
  → 未来加载 A1 STR；在第一个 solve 前停止
A3 SOURCE_OFF_300V_STATIC_PACKET
  → 仅在 A1/A2 通过后；冻结 source-off 静态序列；到站即停
```

### Arm B

```text
B1 ATLAS_INPUT_STRUCTURE_MESH_PACKET
  → direct-ATLAS 输入组合门；在第一个 solve 前停止
B1B_ZERO_BIAS_INIT_REQUIRED = NOT_ESTABLISHED
B1B_PACKET_CREATED = NO
B2 SOURCE_OFF_300V_STATIC_PACKET
  → 仅在 B1 或另行获批 B1B 通过后；到站即停
```

Packet 文件：

1. [A1 DevEdit structure/mesh](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/OFAT_A1_devedit_structure_mesh_packet.in)
2. [A2 ATLAS input/binding](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/OFAT_A2_atlas_input_binding_packet.in)
3. [A3 source-off 300 V static](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/OFAT_A3_sourceoff_300V_static_packet.in)
4. [B1 direct-ATLAS input/structure/mesh](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/OFAT_B1_atlas_input_structure_mesh_packet.in)
5. [B2 source-off 300 V static](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/OFAT_B2_sourceoff_300V_static_packet.in)

## 5. 来源证明与完整 diff

- [机器可读来源 manifest（CSV）](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/manifests/OFAT_STAGE_PACKET_MANIFEST.csv)
- [机器可读禁止行为扫描（CSV）](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/manifests/OFAT_STAGE_PACKET_SCAN.csv)

完整 unified diff：

1. [A1 vs frozen A](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/diffs/OFAT_A1_vs_frozen_A.diff)
2. [A2 vs frozen A](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/diffs/OFAT_A2_vs_frozen_A.diff)
3. [A3 vs frozen A](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/diffs/OFAT_A3_vs_frozen_A.diff)
4. [B1 vs frozen B](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/diffs/OFAT_B1_vs_frozen_B.diff)
5. [B2 vs frozen B](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/diffs/OFAT_B2_vs_frozen_B.diff)

所有非注释源语句的静态比较结论：

```text
ACTIVE_STATEMENT_PRESERVATION = PASS_EXACT_SUBSEQUENCE
PARAMETER_VALUE_CHANGES = NO
PHYSICS_MODEL_CHANGES = NO
CONTACT_REGION_DOPING_MESH_COORDINATE_CHANGES = NO
```

## 6. 禁止行为扫描摘要

| Packet | SEU | tfinal | solve | transient solve | go DevEdit | go ATLAS | structure | save | quit | system/ssh/shell |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
| A2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| A3 | 0 | 0 | 15 | 0 | 0 | 1 | 0 | 2 | 1 | 0 |
| B1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| B2 | 0 | 0 | 15 | 0 | 0 | 1 | 0 | 2 | 1 | 0 |

A3/B2 的 15 条 solve 是冻结候选已有的 source-off 静态序列；没有瞬态 solve。详细行号和完整语句见扫描 CSV。

## 7. 未决风险（全部 OPEN）

1. DeckBuild batch 没有已确认的 parse-only stage selector。
2. A2 在第一个 solve 前可得到哪些 runtime table 未验证。
3. B1 不执行 `solve init` 时是否能生成可检查 STR 未验证。
4. Air region 13 语义未验证。
5. 重复 region 3/4/12 语义未验证。
6. 两个同名同号 gate electrode 的唯一 terminal 语义未验证。
7. `MATERIAL region=10 mun=50` 未验证。
8. NiO 热参数未验证。
9. 五次 `solve previous` 是否形成五个 accepted baseline 点未验证。

不得把上述任何一项从 packet 文本静态扫描推断为 PASS。

## 8. 下一轮建议授权表

| 建议次序 | 单独核签对象 | 最大范围 | 禁止自动进入 |
|---:|---|---|---|
| 1 | A1 | 单次 DevEdit structure/mesh | A2/A3 |
| 2 | A2 | 单次 ATLAS input/binding，无 solve | A3 |
| 3 | B1 | 单次 direct-ATLAS input gate，无 solve | B1B/B2 |
| 4 | 条件 B1B | 仅网页端先核签新增的零偏 init packet | B2 |
| 5 | A3 | source-off 300 V，成功也停止 | SEU/paired transient |
| 6 | B2 | source-off 300 V，成功也停止 | SEU/paired transient |

推荐网页端先审查本提交中的 packet、manifest、diff 和静态扫描；未单独核签前不上传、不运行。

## 9. 附件索引

- [完整 packet 审查报告](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/OFAT_STAGE_PACKET_REVIEW_REPORT.md)
- [来源 manifest](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/manifests/OFAT_STAGE_PACKET_MANIFEST.csv)
- [禁止行为扫描](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/manifests/OFAT_STAGE_PACKET_SCAN.csv)
- [packets 目录](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/)
- [diffs 目录](attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/diffs/)

## 10. 本轮未执行确认

```text
REMOTE_UPLOAD_EXECUTED: NO
SSH_EXECUTED: NO
DEVEDIT_EXECUTED: NO
ATLAS_EXECUTED: NO
STATIC_300V_EXECUTED: NO
SEU_TRANSIENT_EXECUTED: NO
PAIRED_TRANSIENT_EXECUTED: NO
DECKBUILD_EXECUTED: NO
STRUCTURE_OR_MESH_GENERATED: NO
NEW_RUN_CREATED: NO
PARAMETERS_ADJUSTED: NO
AUTO_FIX_PERFORMED: NO
```
