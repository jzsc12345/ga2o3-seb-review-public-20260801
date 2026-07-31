# AGENTS.md — Harness 入口，不是百科全书

你在 `D:\SILVACO_LOCAL\harness`。本目录只管理 2026-07-27 09:20 +08:00 之后的
Codex 工作证据；不得把这里的内容回写进 `D:\SILVACO_LOCAL\skills`。

## 启动顺序

1. 读本文件。
2. 读 `ARCHITECTURE.md`。
3. 读 `docs/exec-plans/active/` 中唯一活动计划。
4. 按任务只读对应的 `docs/research-results/` 或 `docs/imported/post_cutoff/` 子树。
5. 动手前运行 `python tools/check_harness.py`。

## 证据优先级

`pre-cutoff Git 对象` → `冻结 SHA 的 RUN deck/CSV/PNG` → `运行目录 typescript/结果文件`
→ `经核验研究报告` → `post-cutoff imported Markdown` → `聊天记忆/推断`。

任何后期 Markdown 与分界前 Git 对象冲突时，分界前对象优先；任何 Markdown 与原始 CSV、
PNG、deck SHA 冲突时，原始证据优先。`AUTHOR_UNVERIFIED` 不是贬义，而是禁止伪造归属。

## 依赖方向

`product-specs → design-docs → exec-plans → run-evidence → research-results → reports`

只允许向右引用。`imported/post_cutoff` 是隔离档案，不得反向改写 `product-specs` 或 Claude
skill；需要提升一条规则时，先在活动计划中记录证据与用户裁决，再写入对应层。

## 仿真闸门

- 无 A13 物理核签，不编制实弹 deck。
- 无 A14 四件包（结构图、网格图、完整 diff、tmux 会话名），不发射。
- 运行只认 `typescript` 内 `simulator exits with code`；文件名和 `EXIT.txt` 不能替代。
- 大 `.str/.log` 不进本仓；只收轻量 `.csv/.png/.in/.py/.md/.c/.sh`。
- `RUN095/RUN096` 是当前可复现基线；后期 OFAT 只能作为相对证据，不能改写其 SHA。

## 报错与批判性

先查冻结经验和原始手册/例子，再提出 2–4 个候选；不凭印象发明 ATLAS 参数。
用户建议若与冻结计划冲突，要展示证据和代价，不可静默掉头。物理解释用大白话和因果箭头；
结论必须标 `已实测 / 只读推断 / 未核实`。

## 机械检查

每次交付前运行：

```powershell
python tools\check_harness.py
```

若检查失败，先修结构或清单，禁止用“继续执行”绕过。

## 垃圾回收

活动计划完成后移入 `docs/exec-plans/completed/`；重复报告保留一个权威入口，其他只保留
SHA/来源索引。不要删除原始运行证据；只清理重复解释和失效链接。

