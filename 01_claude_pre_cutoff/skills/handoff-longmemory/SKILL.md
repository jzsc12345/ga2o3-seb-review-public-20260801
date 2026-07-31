---
name: handoff-longmemory
description: Self-managed long-term memory and handoff protocol for agents working in D:\SILVACO_LOCAL. Use at session start (recall), before context gets long (checkpoint), on any user correction (constraints ledger update), and at session end or model switch (handoff generation). Solves cross-window amnesia, context-compression drift, and stale-memory execution of retracted user requirements.
---

# handoff-longmemory — 自制上下文长记忆协议

> 解决三件事：①跨窗口零记忆（新窗口/换模型/258K 上下文用尽）；②长对话压缩后跑偏；
> ③用户撤回过的要求被旧记忆复活执行。
> 本包是**协议**不是程序：靠固定文件位置 + 固定动作时机，任何 agent（Codex/Claude）照做即可。

## 1. 记忆文件体系（固定位置，缺一不可）

| 文件 | 角色 | 更新时机 |
|---|---|---|
| `knowledge\CONSTRAINTS_用户约束账本.md` | 用户约束/偏好/冻结值/**撤回区** | 用户每次强调、纠正、撤回 → **当场**更新 |
| `docs\AGENT_运行日志_与复现手册.md` §4 | 动作留痕流水 | 每个动作实时追加 |
| `docs\HANDOFF_*.md` | 阶段快照（技术路线/交接件） | 重要阶段收口时 |
| `knowledge\ERRORS_错误知识库.md` | 成长型错误库（extract_errors.py 生成+回填） | 每次扫日志 |
| git 历史 | 全仓状态可回滚锚点 | 每个 checkpoint |

## 2. 会话生命周期四动作

### 启动（新窗口第一件事）
```
读 README.md → knowledge\CONSTRAINTS_用户约束账本.md（全文，特别是 §R 撤回区）
→ docs\AGENT_运行日志 §4 最后 20 行 → 最新 HANDOFF_*.md
```
**先读撤回区再干活**——防止执行已作废的旧要求。

### 运行中（每完成一个动作）
- 留痕一行进运行日志 §4（时间/动作/产物/证据）
- 用户给出新约束或纠正 → 账本加行；用户说"不要之前的要求" → 旧行**移入 §R 划线**，不删除

### 上下文将满 / 重要阶段（checkpoint）
```
1. 账本与日志同步检查
2. git add -A && git commit -m "checkpoint-NN: <一句话>"
3. 若阶段收口：写/更新 HANDOFF_<主题>_<日期>.md（用 §3 模板）
```

### 收尾 / 换模型 / 换窗口（handoff）
写 `docs\HANDOFF_TO_<目标>_<日期>.md`，模板见 §3；末尾附「三行接续提示词」。

## 3. HANDOFF 模板（各节都要，宁短勿缺）

```markdown
# 交接 → <目标窗口>
## 0 一句话状态
## 1 立即待办（按序，含恢复命令/文件路径）
## 2 产物地图（本阶段产出，逐条已核实落盘）
## 3 已验证事实（不要重推导；含被推翻的旧判断及其证据）
## 4 约束速引（指向账本，列本阶段新增行号）
## 5 风险与未决（诚实列出未验证项）
## 6 三行接续提示词（复制即用）
```

## 4. 防跑偏自检（每 10 轮对话或感觉偏航时）

问自己三个问题，任何一个答不出就回读账本：
1. 当前动作对应 8 周计划的哪一格？（`docs\计划_8周小论文冲刺.md`）
2. 本轮只改了一个变量吗？（账本 A8）
3. 我引用的要求在撤回区吗？（账本 §R）

## 5. 防恶意/误改

- 任何窗口不得改 skills\ 冻结包与原始基线（账本 A4/A10）；
- 发现工作树与预期不符：`git status` + `git diff` 看改动，`git checkout -- <file>` 回滚，
  并把事件记入运行日志；
- checkpoint 提交人固定 `silvaco-agent`，出现陌生提交即为异常信号。
