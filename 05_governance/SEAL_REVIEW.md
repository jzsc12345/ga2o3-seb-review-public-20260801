<!-- Provenance: Codex-generated / post-2026-07-27-09:20 / conditional user authorization -->
# Rulebook seal review — sealed release, 2026-08-01

## 当前阶段

```text
TECHNICAL_REVIEW=PASS
AGENT_SEAL=SEALED
USER_SEAL=SEALED
BLOCKER_COUNT=0
```

用户当前授权 `USR-SEAL-003` 的全部条件已经满足：规则语义 16/16、候选闭包无遗漏、根入口可发现、
源目录布局通过，并且 PENDING 状态下的锁、包清单与八项统一只读验证均通过。封印时间为
`2026-08-01T03:21:32.5101211Z`；最终锁与包清单随后按本文件内容重算并复验。

## 封印对象与边界

封印对象不是“全部历史聊天”，而是 `COMPILED_RULE_ARTIFACT_SET_V1`：16 条 accepted 规则与
9 条 superseded 规则，共 25 个明确列举的编译产物。`CANDIDATE_UNIVERSE.json` 明示该集合并非
对 SRC-001 或 SRC-004 的穷举；`CANDIDATE_LEDGER.csv` 的闭包为：

```text
TOTAL=25
ACCEPTED=16
REJECTED=0
SUPERSEDED=9
UNRESOLVED=0
MERGED=0
UNACCOUNTED=0
```

`UNRESOLVED_CANDIDATES.md` 的四项是来源准入/归属事项，不是规则候选，未被用于拼凑计数。

## 语义审计与修正

最初上传包被网页端 Pro 拒绝后，本轮重新从原始 JSONL 和 cutoff commit 逐子句核验，不把旧
`SEAL_REVIEW.md`、旧 lock 或 agent 总结当事实。主要修正如下：

1. CR-005 把没有直接来源的精确 `2–4` 错配改回用户原意“若干”。
2. CR-006/007/008/011/012/016 补录 assistant 原始记录并标 `MIXED`。
3. CR-010/013/014/015 对无法证明原消息作者的规则标 `REPOSITORY_DERIVED`，不冒充 Claude 或用户原创。
4. CR-013 删除无截止前通用依据的“源项”。
5. CR-016 删除无通用来源的“可证伪”，保留有来源的 `2–4` 与代价。
6. CR-009 删除“从第一个尚未验证步骤继续”的推演性扩写。
7. CR-014 收窄为“桌面应用版本更新后的首个会话”，不再泛化到恢复或新环境。
8. CR-015 改用实际存在的 cutoff 报告路径，并取消不完整的纯 USER 归属。

独立只读复核结果：

```text
CR-001..CR-008: 8/8 PASS, blockers 0
CR-009..CR-016 first corrected pass: 5/8 PASS, four defects found
CR-009/CR-014/CR-015 fresh re-review after narrow fixes: 3/3 PASS, blockers 0
FINAL_RULE_SEMANTIC_PASS=16/16
POST_CUTOFF_CONTAMINATION_COUNT=0
PARTIAL_ENTAILMENT_COUNT=0
UNKNOWN_SOURCE_CLAIM_COUNT=0
```

## 入口、候选与权限审计

- 根与 Harness 两个失效的旧 Rulebook 指针已经替换为现存 README/Rulebook/provenance/lock。
- 根与 Harness 入口均可直接发现 Rulebook、precedence、active plans 和统一只读验证器。
- 用户授权链保留三个事件：早期条件授权 → 后出的 PENDING 覆盖 → 当前“零 blocker 后封印同步”
  条件授权。有效事件是 `USR-SEAL-003`，绑定 canonical payload digest
  `0006C0C09EEEEEDB1D18292D76F8789E2EAAF86F3035523657F6FDEE6E71AC25`。
- 授权事件由 Codex 记录但不由 Codex签署；用户原消息 ID、turn ID、UTC、原始记录 SHA 和短原文
  保存在 `USER_SEAL_AUTHORIZATION.jsonl`。

## 封印前机械验证

在把 PENDING 状态提升为 SEALED 之前，本轮原始命令结果为：

```text
SOURCE_LAYOUT_RESULT=PASS
CHECK_LAYOUT=PASS
CHECK_LINKS=PASS
CHECK_CUTOFF=PASS
CHECK_CANDIDATES=PASS
CHECK_PROVENANCE=PASS
CHECK_SEAL=PASS
CHECK_PACKAGE=PASS
CHECK_PROTECTED=PASS
HARNESS_CHECK=PASS
CHECK_COUNT=8
ERROR_COUNT=0
```

SEALED 状态的锁、review 与 manifest 仍须通过同一套最终复验；若任一文件随后改变，锁即不再代表
该新内容，必须重新走审计、授权与封印流程。

## 明确不授权

本封印不证明材料参数正确、不表示 Wang 2026 已拟合，也不授权 SSH、VM、ATLAS、DeckBuild、
Victory*、许可证操作、RUN121、任何新仿真、deck 物理改动、删除、历史重写、force push、受限全文
上传或秘密/原始个人数据发布。GitHub 同步只使用独立的白名单净化历史。
