# Harness Architecture

## 1. 目标

这套架构把“历史正本”和“后期探索”分开，防止 agent 因为看到更多 Markdown 就误以为
每一条都是同等级真相。它采用短入口、渐进展开、固定依赖方向和机械检查。

## 2. 目录

```text
harness/
├── AGENTS.md                         # 约束与导航
├── ARCHITECTURE.md                   # 本文件
├── README.md                         # 给人的总览
├── assets/figures/                   # 汇报用轻量 PNG
├── docs/
│   ├── design-docs/                  # 证据边界、核心信念
│   ├── exec-plans/
│   │   ├── active/                   # 唯一活动计划
│   │   ├── completed/                # 已闭环计划
│   │   └── tech-debt-tracker.md
│   ├── generated/                    # 机器生成 CSV/清单，不手改
│   ├── imported/post_cutoff/         # 后期 Markdown 镜像、默认不加载
│   ├── product-specs/                # Wang2026 拟合验收合同
│   ├── references/                   # 官方方法论和来源说明
│   ├── reviews/                      # 外部审计原结论的证据化裁决
│   ├── research-results/             # 已核验结论与论文图表接口
│   └── run-evidence/                 # RUN 索引，不复制大文件
└── tools/                            # 构建、检查、报告脚本
```

## 3. 固定边界

1. `D:\SILVACO_LOCAL\skills` 只读；harness 不向它写入任何文件。
2. Claude 冻结包从 Git commit `540379d` 的对象读取，不从当前工作树复制。
3. 当前工作树中的同名文档仅能进入 post-cutoff 隔离层。
4. 论文、手册、STR、LOG、许可证信息、密钥不进 GitHub 轻量包。
5. 报告中的结论必须能回到 deck、CSV、PNG 或运行证据；没有图就写绝对路径待填项和图注。

## 4. 为什么不移动原文件

当前工作区有大量历史交叉引用，直接移动会制造新断链。迁入采用“只读镜像 + 来源清单”，
原文件保留原位；面向新 agent 和 GitHub 的入口只暴露 harness 结构。等引用检查稳定后，才可
在单独计划中讨论物理迁移。
