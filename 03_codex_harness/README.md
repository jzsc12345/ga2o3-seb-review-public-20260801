# Ga₂O₃ SEB Codex Harness

本目录是 **2026-07-27 09:20:00 +08:00 之后资料的隔离层**。它不替代、也不修改
`skills/` 中的 Claude 方法包；它只负责让后续 Codex 能看懂、验证、追责和清理后续工作。

## 两条证据线

- **Claude / pre-cutoff 线**：以 Git commit `540379dab74fdda861f688204b4d45ec5f59a9d2`
  为可审计锚点，导出时从 Git 对象读取，绝不复制当前工作树的同名文件。
- **Codex / post-cutoff 线**：凡当前字节相对上述 commit 有差异的 Markdown，或 Git 未跟踪
  Markdown，统一镜像到 `docs/imported/post_cutoff/`，并在 CSV 清单中记录原路径、状态、SHA、
  时间和 `AUTHOR_UNVERIFIED`。这是一条保守隔离规则，不冒充精确作者鉴定。

## 入口

1. `AGENTS.md`：短导航和强制闸门。
2. `ARCHITECTURE.md`：层级、依赖方向和禁止事项。
3. `docs/exec-plans/active/`：正在执行的计划和决策记录。
4. `docs/research-results/`：经证据核验的研究结论和汇报底稿。
5. `docs/imported/post_cutoff/`：后期资料镜像，不自动加载。
6. `tools/check_harness.py`：结构、链接、SHA 清单和污染边界检查。

## 原则

`skills/` 是方法论正本；`harness/` 是后期工作台。前者不再追加资料，后者可以迭代，
但每次迭代必须经过清单、验证和垃圾回收。

