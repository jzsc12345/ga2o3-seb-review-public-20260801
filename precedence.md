<!-- Provenance: Codex-generated / post-2026-07-27-09:20 / lower-trust governance synthesis -->
# 权限、证据与时间：三轴裁决规则

本文件解决一个常见误区：**“旧”不等于“更权威”，“Claude 写的”也不等于“当前仍授权”。**
判断任何一句话时，必须分别回答三个问题。

## 1. 执行授权轴

从高到低：当前用户明确指令 → 现行用户约束账本 → 用户核签的活动计划 → 兼容入口文件 →
历史 Claude 规则 → Codex 候选。新授权可以改变未来动作，但不能篡改过去证据。

Harness 治理授权不自动包含 SSH、仿真、许可证维护、删除、覆盖、提交、推送或发布。涉及这些
动作时必须从当前对话和活动计划重新取得授权。

## 2. 技术事实轴

从高到低：原始运行证据（deck、typescript、STR、CSV、PNG）→ `atlas.key` / SMDB / 官方手册 /
官方例子 → 论文原文 → 项目报告 → handoff 与聊天摘要。低层文字若与高层证据冲突，保留原文但
标记冲突，禁止静默改写原始证据。

## 3. 来源完整性轴

`USER_DIRECTIVE`、`CLAUDE_PRE_CUTOFF`、`CODEX_POST_CUTOFF`、`MIXED`、`UNKNOWN` 只说明来源，
不直接决定技术真伪。截止日前规则也必须有可追溯的消息 ID/JSONL 行/Git 对象；截止日后的材料
不能冒充 Claude-frozen。

## 4. 冲突裁决顺序

1. 先冻结冲突双方原文与 SHA，不覆盖。
2. 判断它们冲突的是授权、事实还是来源；不得混为一谈。
3. 当前用户已明确撤回的路线进入 `SUPERSEDED_RULES.md`，不得因旧快照再次激活。
4. 尚无证据时写 `[未核实]`，提出 2–4 个可证伪方案；不得填入猜测参数。
5. 只有用户明确批准的 Codex candidate 才能从 `pending` 进入 `accepted`。

## 5. 本轮治理边界

本轮只建设 Harness 控制面与来源索引，不授权 VM、ATLAS、DeckBuild、VictoryExtract、物理参数
修改或现役 deck 变更。科研活动计划保持独立，不能把治理计划的“完成”当成仿真核签。
