# OFAT A/B 本地预检结果

> Date: 2026-08-06
>
> Scope: candidate preparation and read-only/textual verification
>
> No SSH / no VM / no SEU transient / no paired transient / no new RUN

## 1. 结论先行

候选文本已编制，但本阶段不能完成用户授权中的 SILVACO parser、结构/网格生成和 300 V 静态预检，
因为当前 Windows 主控环境找不到本地 SILVACO 命令，而授权明确禁止 SSH 和 VM/远端执行。

```text
STATUS = PREPARED_NOT_RUNTIME_VALIDATED
LOCAL_SILVACO_RUNTIME = NOT_FOUND
PARSER_A/B = NOT_EXECUTED
MESH_A/B = NOT_EXECUTED
STATIC_300V_A/B = NOT_EXECUTED
SEU_TRANSIENT = NOT_EXECUTED
```

没有用文本检查冒充 parser/runtime PASS，也没有生成伪结构图、伪网格图或伪 300 V 证据。

## 2. 本机工具探测

`Get-Command` 结果：

| 命令 | 状态 |
|---|---|
| deckbuild | NOT_FOUND |
| atlas | NOT_FOUND |
| devedit | NOT_FOUND |
| tonyplot | NOT_FOUND |
| victorydevice | NOT_FOUND |
| victoryextract | NOT_FOUND |

本机相关 SILVACO 进程为 0。`E:\silvaco2425` 是 VM 文件/大结果归档位置，不是可直接调用的 Windows
SILVACO 安装。本轮没有启动 VMware，也没有通过 SSH 使用 Linux 端软件。

## 3. 已完成的候选规范化文本门

| 检查 | A | B |
|---|---:|---:|
| active `singleeventupset` | 0 | 0 |
| active `tfinal` | 0 | 0 |
| active Auger | 0 | 0 |
| active `max.temp` | 0 | 0 |
| active `tonyplot` | 0 | 0 |
| `vstep=15` 到 300 V | 1 | 1 |
| source-off `solve previous` baseline 语句 | 5 | 5 |
| active thermcontact | 2 | 2 |
| gate-state outf/load | present | present |
| shared block 行数 | 143 | 143 |
| shared block 文本 | identical | identical |

这里的“present/identical”只证明候选文件内容，不证明语法被 SILVACO 接受或解被接受。

## 4. benchmark-only ban scan

现行 production ban checker 按预期拒绝候选：

- A：legacy impact `2.5e6 / 3.96e7 / betan=1.37` 三项命中；
- B：`Acceptors=2e6` 加 legacy impact 三项命中。

A 的 `Acceptors=2e6` 使用 DevEdit `impurity` 语法，现有 checker 没匹配到；这不表示该项不存在。

用户已书面批准本对照的窄范围标签：

```text
LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB
```

因此这些命中是**已公开例外证据**，不是 production preflight PASS，也不得在候选中静默改值。

## 5. parser/runtime/结构/网格门

| 门 | A | B | 说明 |
|---|---|---|---|
| parser | NOT_EXECUTED | NOT_EXECUTED | 本地命令缺失 |
| region/material mapping | NOT_EVALUABLE | NOT_EVALUABLE | 需 runtime table |
| terminal count/name/boundary | NOT_EVALUABLE | NOT_EVALUABLE | 需 parser + structure |
| thermcontact/elec.num | NOT_EVALUABLE | NOT_EVALUABLE | 需 runtime table |
| `MATERIAL region=10 mun=50` | NOT_EVALUABLE | NOT_EVALUABLE | 两臂文本均指向 source Nickel region 10 |
| NiO `tcon.const tc.const=2.27` | NOT_EVALUABLE | NOT_EVALUABLE | 需 parser/runtime |
| nodes/triangles/obtuse | NOT_AVAILABLE | NOT_AVAILABLE | 未生成 STR |
| actual structure image | NOT_AVAILABLE | NOT_AVAILABLE | 未生成 STR，禁止伪造 |
| actual mesh image | NOT_AVAILABLE | NOT_AVAILABLE | 未生成 STR，禁止伪造 |
| track dx/dy/full-y continuity | NOT_EVALUABLE | NOT_EVALUABLE | 只有输入合同，无 STR |

B 臂另有两个必须由 parser/structure 关闭的语义门：

1. 显式 Air region 13 是否与 DevEdit 的未填充 work-area 背景等价；
2. 两个 `name=gate, num=3` 矩形是否在本版本中形成单一 stepped-gate terminal。

未关闭前继续标记 `DIRECT_MESH_EQUIVALENCE=CONDITIONAL_NOT_DEMONSTRATED`。

## 6. 300 V source-off 静态门

| 证据 | A | B |
|---|---|---|
| VGS=0 accepted | NOT_EXECUTED | NOT_EXECUTED |
| VDS=300 accepted | NOT_EXECUTED | NOT_EXECUTED |
| Cannot trap / rejected / compliance audit | NOT_EXECUTED | NOT_EXECUTED |
| accepted 300 V STR | NOT_AVAILABLE | NOT_AVAILABLE |
| five accepted source-off points | TEXTUALLY_REQUESTED / NOT_RUNTIME_PROVEN | 同左 |
| raw Id/Is/Ig | NOT_AVAILABLE | NOT_AVAILABLE |
| initial temperature/thermal boundary | NOT_EVALUABLE | NOT_EVALUABLE |
| potential and |E| at three points | NOT_AVAILABLE | NOT_AVAILABLE |
| static equivalence | NOT_EVALUABLE | NOT_EVALUABLE |

source-off 顺序在候选中是：没有 active SEU → 建立 300 V → 保存 STR → 开 baseline log → 五次
`solve previous`。这比原候选在静态爬压前声明非零 C 源更严格，但仍需 SILVACO 实跑证明五点均 accepted。

## 7. 仓库基线检查

- 公共提交仓库在本轮开始时为 clean `main...origin/main`。
- 主工作区 `check_layout.py` 报 182 条既存违规；未清理、未修改、未纳入本提交。
- Harness 检查存在 6 条既存 package/protected 差异；未修改受保护文件。
- 本阶段没有 branch/worktree，没有新 RUN，没有仿真进程。

## 8. 下一步建议

在不扩大当前授权的前提下已经没有更多真实 runtime 证据可获得。要关闭本阶段剩余门，用户需要在固定
GitHub handoff 审核后单独提供以下二者之一：

1. 一个可直接调用的本地 Windows SILVACO 可执行路径；或
2. 一次仅限这两份候选的 VM/SSH parser + mesh + source-off 300 V 静态预检授权。

即使授权，也必须继续禁止 SEU/paired transient；A/B 任一结构或语义不等价就停止为 `OFAT_INVALID`。
