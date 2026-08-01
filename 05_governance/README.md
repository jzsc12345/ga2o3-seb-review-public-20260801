<!-- Provenance: Codex-compiled / post-2026-07-27-09:20 / historical sources only -->
# Pre-cutoff workflow rulebook compiled from the Claude workspace

本目录由 Codex 在截止日后编译，**编译物本身不是 Claude 原件**。只有
`MESSAGE_EVIDENCE_INDEX.csv` 与 `RULE_PROVENANCE.csv` 指向的 JSONL 消息、网页导出或 Git 对象
才是历史来源；`REPOSITORY_DERIVED` 明确表示只证明截止日前仓库正文，不宣称原消息作者。
当前执行仍受 `../precedence.md` 约束。

截止时间：`2026-07-27T09:20:00+08:00`（UTC：`2026-07-27T01:20:00Z`）。

| 文件 | 用途 |
|---|---|
| `RULEBOOK.md` | 16 条通过逐子句语义门的历史规则 |
| `CANDIDATE_UNIVERSE.json` | 本次封印的有限编译产物全集定义与边界 |
| `CANDIDATE_LEDGER.csv` | 25 个编译产物的五类 disposition 闭包 |
| `SOURCE_INDEX.csv` | 原始来源与 SHA |
| `MESSAGE_EVIDENCE_INDEX.csv` | 消息级证据 |
| `RULE_PROVENANCE.csv` | 规则到消息/Git 行的映射 |
| `SUPERSEDED_RULES.md` | 已撤回或只适用于历史阶段的规则 |
| `CONFLICT_REGISTER.md` | 未静默裁决的冲突 |
| `UNRESOLVED_CANDIDATES.md` | 非规则的来源/准入待核事项 |
| `CANONICAL_PAYLOAD.json` | 不含授权与锁的语义载荷哈希 DAG 根 |
| `USER_SEAL_AUTHORIZATION.jsonl` | 用户条件授权、覆盖与最终有效事件链 |
| `SEAL_REVIEW.md` | 封印前对抗审计、修正与授权边界 |
| `RULES_LOCK.json` | 规则文件哈希锁；用户 seal 状态单列 |

本版 universe 只覆盖明确列举的 `CR-001..016` 与 `SR-001..009`，不声称已经穷举所有历史消息。
