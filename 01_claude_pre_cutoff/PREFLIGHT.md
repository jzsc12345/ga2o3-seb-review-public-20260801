# PREFLIGHT.md — 全框架烟测总检单

> **铁律（账本 B11）：任何 agent 在修改本架构（scripts/skills/knowledge 结构、运行链路、
> 判据体系）之前，必须先跑通对应级别的 preflight。烟测不过 → 只许修复烟测项，禁止动架构。**
> 2026-07-27 按产线收束令（账本 B12）修订：L2/L3 的 VictoryDoE 检查项已摘除，
> 摘除记录见 `docs\废案登记_20260727.md`。
> 自动化半边：`python scripts\preflight_all.py`（默认 L2；`--full` 到 L3）。
> 本文是它的人读对照表：每项=命令 → 预期 → 失败去哪修。

## 分级总览

| 级 | 覆盖 | 何时必须过 |
|---|---|---|
| **L0 本地静态** | 布局/git/依赖/各脚本自检/文档在位/四库可达 | 改任何本地脚本或文档结构前 |
| **L1 远端连通** | VM 探测/工具链/license/tmux/远端目录架构 | 提交任何仿真前 |
| **L2 可视** | X 会话/截图回传 | 出空间图或开截图看板前 |
| **L3 全链路** | VE 微提取实跑 + SWEEP 产线三件套证据 | 改运行链路（runner/judge/提取模板）前 |

完整端到端 = B12 主产线一圈：LHD 采样（`scripts\lhd_pareto.py`）→ aux.in SWEEP list →
tmux 跑批 → victoryextract/经典 EXTRACT 收数 → 帕累托复算。实弹样例见
`decks\sweep_bv_main/aux.in`（5 点 151 秒）与 `outputs\reports\lhd_round1_wait_package.md`。

## L0 本地静态

| 项 | 命令 | 预期 | 失败修复 |
|---|---|---|---|
| 布局合规 | `python scripts\check_layout.py` | `✓ 布局完全合规` | 按输出逐条归位；白名单在脚本 POLICY |
| git 健康 | `git log -1 --format="%an %h %s"` | 提交人 `silvaco-agent` | 陌生提交=异常信号→查 `git diff`，见 handoff-longmemory §5 |
| python 依赖 | `python -c "import numpy,pandas,matplotlib,pptx"` | 无输出 | `pip install <缺的>` |
| judge 自检 | `python scripts\w1_judge.py --help` | 5 子命令列出 | 回滚 `git checkout -- scripts/w1_judge.py` |
| 错误库 | `python scripts\extract_errors.py top` | 榜单打印 | errors_db.json 损坏→删除重扫 |
| PPT 生成器 | 用 `_gen_selftest_outline.md` 生成 | `[pptx] ... (3 页)` | 见 report-writer SKILL §5 语法 |
| 关键文档 | AGENTS/README/账本/PATH_MAP/运行日志 在位 | 全在 | 从 git 恢复 |
| 四库 | `D:\knowledge\{material_sil,pdf25,exp25,paper}` | 四库全在 | 用户挂盘/恢复；缺库时禁止查证类工作 |

## L1 远端连通

| 项 | 命令 | 预期 | 失败修复 |
|---|---|---|---|
| VM 探测 | `python scripts\silvaco_remote.py preflight` | 8 行 OK + XDPYINFO OK | 双 IP 均拒连=VM 关机→请用户开机；IP 漂移已自动双探测 |
| 工具链+license | 同上输出 | 无 MISSING；SFLM_PROC≥1 | `export SFLM_SERVERS=+localhost`；查 sflm 进程 |
| tmux 驱动 | `ssh ... "/root/bin/vdoe_tmux.sh status"` | `== tmux 会话 ==` 段 | 重部署：`scp scripts\remote\vdoe_tmux.sh` + `sed -i 's/\r$//'` + chmod |
| 远端架构 | `ls /root/DECKBUILD/{README.txt,postproc,_lab}` | 全在 | 重跑本文档尾注的建目录段（只增不移） |
| 僵尸嫌疑扫描 | `python scripts\preflight_all.py --level 1` | 零 `dbascii.exe/atlas.exe*` 嫌疑（etime>2h、累计 `%CPU<1`；有活跃 ATLAS 后代的 runner 包裹层除外） | 打印 PID/etime/%CPU/cwd 后报告用户裁决，禁自行 kill（豁免令） |

## L2 可视（原"GUI"级；VDoE 窗口/xctl 两项已按 B12 摘除）

| 项 | 命令 | 预期 | 失败修复 |
|---|---|---|---|
| X 会话 | 注入 mate-session 环境后 `xdpyinfo` | name of display: :0 | **XAUTHORITY 坑**：必须 `/var/run/lightdm/root/xauthority`；VM 桌面必须已登录 |
| 截图回传 | `python scripts\screenshot_watch.py --session _preflight --once` | `[shot] ...png` | CRLF/bytes 坑已封装；若 capture failed 查 X 会话项 |

## L3 全链路

| 项 | 命令 | 预期 | 失败修复 |
|---|---|---|---|
| VE 微提取 | preflight_all --full 内置（对 n5_prestrike.str 切一刀出 csv） | `VEOK <行数>` | 语法答案在 `knowledge\41`；死路清单防猜 |
| SWEEP 产线三件套 | preflight_all --full 内置（本地文件检查） | `decks\sweep_bv_main.in` + `sweep_bv_aux.in` + `outputs\reports\sweep_bv_summary.csv` 在位 | 从 git 恢复；csv 缺失→按 kb42 重跑 5 点 SWEEP 再转存 |

## 已知在跑任务的豁免

preflight 期间**不得**为了"干净"而 kill 正在跑的 atlas/tmux 会话（W1 执行、验证线可能在场）——
并发闸门规则见冻结计划书 §3.G；`pkill atlas` 全局禁止（账本/交接单 §0）。

## 附：远端目录架构重建段（幂等，只增不移）

```bash
mkdir -p /root/DECKBUILD/postproc/{csv,cutlines,shots,figs} /root/DECKBUILD/_lab /root/DECKBUILD/runs
# README.txt 若丢失，从本仓库 docs\AGENT_运行日志 §4 2026-07-27 留痕行所引版本恢复
```
