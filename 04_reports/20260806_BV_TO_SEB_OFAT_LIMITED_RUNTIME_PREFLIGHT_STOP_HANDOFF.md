# BV→SEB OFAT 有限运行预检：G1 前停止交接

> Status: `STOPPED_BEFORE_G1 / STAGE_ISOLATION_BLOCKED`
>
> Input commit: `994d83bc444e7a17695f003b65f0d90da25c8023`
>
> Date: 2026-08-06
>
> `NO SEU TRANSIENT`
>
> `NO PAIRED TRANSIENT`
>
> `NO AUTOMATIC EXPANSION OF AUTHORIZATION`
>
> `NO AUTO-FIX AFTER FAILURE`

## 1. 本轮结果先说清楚

本轮没有启动 DeckBuild、DevEdit、ATLAS，也没有创建远端 preflight 目录。停止原因不是候选物理失败，也不是 parser 失败，而是冻结候选和授权门序之间存在不可同时满足的执行矛盾：

1. 用户要求严格按 `G1 parser-only → G2 structure/mesh → G3 source-off 300 V` 执行，禁止跳级；
2. 用户同时禁止修改候选 deck、失败后自动修复和权限自动扩张；
3. A/B 候选都没有阶段开关；
4. DeckBuild 5.2.40.R 官方手册说明 batch mode 会执行整个输入 deck，没有“仅解析”“执行到指定行”或“运行选区”的批处理参数；
5. A 在同一 deck 中先执行 DevEdit 建模，再进入 ATLAS 并爬到 300 V；B 在 `go atlas` 后建网格并继续爬到 300 V。

因此，直接运行冻结候选会把后续门一并执行；机械截断、插入 `quit` 或生成阶段 wrapper 又属于当前未获授权的新执行输入。为避免把整 deck 运行冒充 parser-only，本轮在 G1 前硬停。

## 2. 固定输入与来源核对

两份候选均来自固定提交中的以下路径：

- [Arm A 候选](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_A_bv_devedit_static300_sourceoff_preflight.in)
- [Arm B 候选](attachments/20260806_bv_to_seb_ofat/next_stage/OFAT_B_bv_direct_atlas_static300_sourceoff_preflight.in)

使用 `git diff --exit-code <fixed-commit> -- <A> <B>` 核对，工作树候选相对固定提交差异为 0。没有生成新的文件哈希。

静态 active-token 核对：

| Arm | active `singleeventupset` | active `tfinal` | active `tonyplot` |
|---|---:|---:|---:|
| A | 0 | 0 | 0 |
| B | 0 | 0 | 0 |

## 3. 唯一确定的环境

| 项 | 现场结果 |
|---|---|
| SSH 配置入口 | `silvaco` → `root@192.168.50.100:22` |
| VM hostname | `tcad` |
| VM 网卡地址 | `192.168.50.134` |
| OS | Red Hat Enterprise Linux Server 7.9 (Maipo) |
| SILVACO root | `/atctools/Synopsys/Silvaco2024` |
| DeckBuild 安装版本 | `5.2.29.R`, `5.2.40.R`；目标版本为 `5.2.40.R` |
| ATLAS 安装版本 | `5.38.0.R`, `5.40.0.R`；目标版本为 `5.40.0.R` |
| SFLM | TCP 3162 正常监听，`sflm.service=active` |
| 现场 ATLAS/DeckBuild/tmux | 0 / 0 / 0 |
| 计划远端目录 | `/root/DECKBUILD/preflight/OFAT_994d83b_20260806` |
| 目录状态 | 未创建 |

由于没有启动模拟器，版本字段是安装与目标版本证据，不冒充本轮 runtime banner。

## 4. 门禁状态

| 门 | A | B | 说明 |
|---|---|---|---|
| 输入来源 | PASS | PASS | 与固定提交字节一致 |
| 禁止瞬态 token | PASS | PASS | active 三项均为 0 |
| G1 parser-only | NOT_EXECUTED | NOT_EXECUTED | 冻结输入无法与 G2/G3 隔离 |
| G2 structure/mesh | NOT_REACHED | NOT_REACHED | 不允许越过 G1 |
| G3 source-off 300 V | NOT_REACHED | NOT_REACHED | 不允许越过 G1/G2 |
| Direct-mesh 等价性 | NOT_EVALUATED | NOT_EVALUATED | B 未运行 |

这些标签不得改写为 `ARM_A_PARSER_FAILED` 或 `ARM_B_PARSER_FAILED`，因为 parser 从未启动。

## 5. 为什么不能“先跑起来再看日志”

Arm A 第 12 行进入 DevEdit，第 226 行保存结构，第 230 行进入 ATLAS，第 340 行开始静态求解，第 354 行继续到 300 V。Arm B 第 11 行进入 ATLAS，第 15–81 行同时完成网格、region 和 electrode 构造，第 190 行开始静态求解，第 204 行继续到 300 V。

DeckBuild 5.2.40.R 手册 `deckbuild_users1.pdf` 第 24–25 页说明 batch mode 自动执行整个 input deck；列出的 batch 参数只有运行、输出、ascii、优化器、错误/标准输出、nice、preferences 和 help，没有 parse-only 或行范围参数。ATLAS 启动脚本也没有 syntax-only/check-only 分支。

所以：

```text
直接 start-deck
  → 不可保证停在 G1
  → 可能在人工检查 G1 之前已进入 G2/G3
  → 违反“禁止跳级”和“任一门失败立即停止”
```

## 6. 网页端需要裁决的唯一执行缺口

下一轮只能在下列三种边界中选一，不能默认为已授权：

### 方案 A（推荐）：授权阶段执行包，并修正不可实现的门序

允许机械生成、先审后跑的 stage packet；冻结原候选不改。由于 A 的 ATLAS region/material table 必须依赖 DevEdit 生成的 STR，而 B 的 region parser 与结构构造是同一组 ATLAS 命令，建议门序明确为：

```text
A: DevEdit structure/mesh → ATLAS parser/material/binding → 300 V static
B: ATLAS parser+structure/mesh combined gate → 300 V static
```

每个 packet 只能从候选逐行抽取；禁止改参数、改命令拼写或修复失败。必须在发射前把 packet diff 交回审查。

### 方案 B：授权 DeckBuild GUI 选区执行

候选字节不改，但必须接受 GUI 选区并非标准 `start-deck` 批处理，且 B 的 parser 与结构仍无法物理拆开。该方案的复现性较差，不推荐。

### 方案 C：允许整 deck 运行，但放弃逐门硬停

这会让 parser、结构和 300 V 在一个进程内连续执行，只能事后审计，不满足当前“失败即停”的方法合同，不推荐。

## 7. 附件索引

- [环境与输入证据](attachments/20260806_bv_to_seb_ofat/runtime_preflight_stop_20260806/ENVIRONMENT_AND_INPUT_EVIDENCE.md)
- [阶段隔离阻塞分析](attachments/20260806_bv_to_seb_ofat/runtime_preflight_stop_20260806/STAGE_ISOLATION_BLOCKER.md)
- [只读命令登记](attachments/20260806_bv_to_seb_ofat/runtime_preflight_stop_20260806/READ_ONLY_COMMAND_REGISTER.md)

## 8. 未执行事项

```text
SEU_TRANSIENT_EXECUTED: NO
PAIRED_TRANSIENT_EXECUTED: NO
NEW_RUN_CREATED: NO
PARAMETERS_ADJUSTED: NO
AUTO_FIX_PERFORMED: NO
REMOTE_DIRECTORY_CREATED: NO
DECKBUILD_EXECUTED: NO
DEVEDIT_EXECUTED: NO
ATLAS_EXECUTED: NO
PARSER_EXECUTED: NO
STRUCTURE_OR_MESH_GENERATED: NO
300V_STATIC_EXECUTED: NO
```

