# OpenAI Harness Engineering → 本项目映射

来源：OpenAI, *Harness engineering: leveraging Codex in an agent-first world*, 2026-02-11。
https://openai.com/index/harness-engineering/

本文采用的映射：

- 大而全 AGENTS 会挤占上下文并快速腐烂 → 本 harness 的 AGENTS 只做目录和硬闸门。
- repository knowledge 是 system of record → 设计、计划、证据、结果分层并版本化。
- progressive disclosure → imported 后期文档默认不加载，先读索引再定向读取。
- architecture/taste 必须机械执行 → `tools/check_harness.py` 检查目录、来源清单和越界文件。
- agent 自治需要可读日志、指标、截图 → RUN 证据必须包含 CSV、空间图和进程/退出证据。
- entropy 需要周期性 garbage collection → 完成计划归档、重复解释降级为索引，保留原始证据。

本文是软件工程经验，不是 TCAD 物理依据；它只决定信息如何组织和验证。

