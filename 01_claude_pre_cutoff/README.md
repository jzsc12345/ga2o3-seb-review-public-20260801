# README — D:\SILVACO_LOCAL 主控架构（新窗口第一入口）

> 用途：给任何新开的 agent 窗口（Codex / Claude）解释整个系统怎么运作。
> 初版 2026-07-26；**2026-07-27 按产线收束令（账本 B12）大修：VictoryDoE 已全弃，
> 相关文档/脚本/技能包已冻结压缩删除（详单 `docs\废案登记_20260727.md`）。
> 现行路线三条铁则见 `AGENTS.md` §0。**

---

## 1. 一句话使命

主控 Windows 端 `D:\SILVACO_LOCAL` 指挥远端 Silvaco 2024 VM（RHEL 7.9, hostname `tcad`）完成
β-Ga₂O₃ 横向 E-mode MOSFET 的 SEB（单粒子烧毁）仿真拟合——
**一切问题先查本地知识库 `D:\knowledge`，再动手改 deck，绝不凭印象猜参数。**

---

## 2. 目录架构图

```
D:\SILVACO_LOCAL\                      ← 主控端（只放 .py/.md/.in/轻量 csv/png）
├── README.md                          ← 本文件，第一入口
├── SEB.in / mySEU.c                   ← 用户原始基线（保持不动，改动一律落 decks\）
├── knowledge\                         ← 本项目知识库（.md）
│   ├── 00_PATH_MAP.md                 ← ★ 唯一路径权威 + 强制检索顺序 + 证据规则
│   └── 10..50 系列                    ← 10 材料参数表 / 11 models 激活与作用域 /
│                                        12 mobility / 13 impact 晶向电离 / 14 incomplete /
│                                        15 interface Qf 与体陷阱 / 16 热模型与自热 /
│                                        20 NiO p 型 / 30 FNT-PFE-TAT 栅漏 /
│                                        40 singleeventupset 源项 / 50 SEB deck 十大缺陷清单
├── docs\
│   ├── 冻结计划书_W1_静态基线冻结.md  ← ★ 现行计划入口（D-0..D-6 分支链 + w1_judge 机检）
│   ├── AGENT_运行日志_与复现手册.md   ← ★ 接续入口（§4 动作级留痕，末 20 行=最新状态）
│   ├── 废案登记_20260727.md           ← 废案清单与归档指针（误入旧路线先读它）
│   ├── CODEX_避坑清单_20260727.md     ← 13 新坑+9 高危老坑（从 15.8MB 会话转写挖掘）
│   └── CODEX_考卷/答卷 系列           ← 验收留痕（v1/v2）
├── decks\                             ← .in / .sdb（现役=sweep_bv_*.in 产线对 + W1_D*.in 冻结包；
│                                        SEB_Ga2O3_VDOE.sdb 仅为历史血统基准，载体形态已废）
├── scripts\                           ← 11 个 .py（见 §2.1；check_layout.py 做布局巡检）
├── outputs\                           ← .png / 轻量 .csv / .md 报告
│   ├── errors\                        ← ★ GUI 出错截图专用收集夹（错误→截图→查库→候选→验证回路）
│   ├── reports\                       ← 分析报告与统计
│   ├── paper_figs\                    ← 小论文/大论文组图待填区
│   └── <session>\screenshots\         ← 各仿真会话 3 分钟截图看板
├── inbox\                             ← 二号机离线结果包 RESULTS_*.tar.gz 落地点（inbox_watch 看守）
├── skills\                            ← 🔒 冻结区：silvaco-tcad（通用方法论）+ handoff-longmemory
│                                        （🌱活协议）+ report-writer（🌱活协议）。只许 .md/.py/.sh/.json，
│                                        发现缺陷写 docs\ 勘误不改包本体。
│                                        （victorydoe-gui-flow 已按 B12 于 07-27 归档删除）
├── archive\                           ← 归档收容（zip/旧副本，只进不出、不引用——
│                                        **唯一例外：Wang2026 目标论文 PDF 正本在此，准许只读引用**）
└── silvaco\                           ← 历史 handoff 与证据（只读为主，上一轮物理口径在此）

★ 每个子目录都有自己的 README.md 索引内容与规矩——进目录先读它。
★ 布局合规：python scripts\check_layout.py（烟测 S0；各目录允许的文件类型白名单在其中）。

D:\knowledge\                          ← ★ 四库合一知识库（检索顺序 ①→④，各库根有 README 导航）
├── material_sil\                      ① 128 个 smdb XML 材料文件 —— 参数数值最高权威
├── pdf25\                             ② 26 本 2025 手册 PDF（atlas_users1.pdf 14.7 MB 主力）
├── exp25\                             ③ 184 个官方例子 .in（6 大类）
├── paper\                             ④ 43 个文献文件（paper_seb / paper_PFE / paper_trap …）
└── README.md                          总导航

E:\silvaco2425\bulk\{str,log}\         ← 大体积 .str/.log 归档（E 盘余 ~67 GB，回传前看余量）
    ⚠ E:\silvaco2425 根目录是 VMware 虚拟机本体（120 GB vmdk），勿混放

远端（Silvaco VM）
├── /root/DECKBUILD/                   ← 生产运行区（每轮一个 run 目录）
├── /root/SilvacoVDoE/                 ← 已弃产线的历史工作区（仅寻址旧产物，勿新建/复跑工程，B12）
└── /atctools/Synopsys/Silvaco2024/    ← 安装根；atlas.key 在 lib/atlas/5.40.0.R/common/
```

### 2.1 scripts\ 九个脚本

| 脚本 | 一行说明 |
|---|---|
| `silvaco_remote.py` | SSH 控制层：双 IP 自动探测 / GUI 会话环境注入 / xterm 后台启动 / 轮询 / 归档 |
| `screenshot_watch.py` | 每 3 分钟抓 VM 桌面 :0 截图到 `outputs\`，做运行看板 |
| `lhd_pareto.py` | LHD 拉丁超立方采样 → aux.in SWEEP list 生成 + 帕累托前沿判定 + 收缩箱迭代（B12 寻优回路） |
| `let_calc.py` | LET 单位换算与反算（MeV·cm²/mg ↔ pC/µm，ρ=5.88, Ei=15.6 eV） |
| `make_offline_bundle.py` | 生成二号机（无 agent、有 Silvaco VM）离线自治工程包，split 全展开成字面量 case.in |
| `inbox_watch.py` | 后台看守 `inbox\`：解包二号机结果 → 校验 manifest → 统计出图写 REPORT |
| `impact_axis_compare.py` | Chynoweth 晶向电离系数 x/y/z 三轴对比（用户表 2.3） |
| `sub_leak_estimate.py` | n 1.5e15 衬底是否构成并联漏电通道的量级估算 |
| `ni_and_substrate_choice.py` | 论证 p=2e6 假半绝缘数值上危险、深受主补偿才是正路 |

---

## 3. ★ 全流程 agent 运作方式（标准回路，禁止跳步）

遇到任何仿真问题，按这个回路走一圈：

```
①  查 knowledge\00_PATH_MAP.md      → 定位该问题归哪个库、哪个文件
②  D:\knowledge\material_sil\       → 查材料参数数值（最高权威；缺值按平替令补 4H-SiC/GaN）
③  D:\knowledge\pdf25\              → 查语句语法语义（Read 工具 pages 参数每次 ≤20 页，先读目录页）
④  D:\knowledge\exp25\              → Grep 找可抄的官方例子 .in（命中统计见 00_PATH_MAP §5）
⑤  D:\knowledge\paper\              → 找物理依据与实验标定值
⑥  改 deck                          → 只改 decks\ 下的文件，原件 SEB.in / mySEU.c 不动
⑦  scripts\silvaco_remote.py        → 推送远端后台运行（必须 xterm+script pty 包裹，见 §4）
⑧  scripts\screenshot_watch.py      → 每 3 分钟截图留痕
⑨  scripts\lhd_pareto.py            → 批量扫参/寻优：LHD 生成 aux.in SWEEP list → tmux 跑批 → 收数复算前沿
⑩  结果回传                         → 大 .str/.log 归档 E:\silvaco2425\bulk\，轻量 csv/png 进 outputs\
⑪  结论沉淀                         → 写进 docs\HANDOFF_*.md（含证据），更新 knowledge\ 对应篇
```

**禁止跳过 ①–⑤ 直接猜参数。** 反面教材：历史上曾凭印象产出
`lte.timestep`、`seu.max.rad`、`seu.max.inc`、`seu.n.inc`、`impact hysteresis`、`impact e.min`
六个**根本不存在**的参数并标了「已核实」，复制进 deck 直接跑挂。裁决规则：

- 参数**是否存在** = 远端 `atlas.key`（345 KB）唯一裁决；远端不可达时标 `[待 atlas.key 复核]`。
- 参数**数值** = `material_sil` XML > 手册 > 文献；β-Ga₂O₃ 查不到的值**必须**按平替强制令填
  最相似材料值（首选 4H-SiC，次选 GaN/ZnO/diamond，逐物理量选择）并标 `[平替:xxx]`，绝不留空。
- `[已核实]` 只能配当场贴得出的证据：XML 行 / PDF 文件名+页码 / 例子 .in 实际行 / grep 输出。

---

## 4. 环境事实速查（都已踩坑验证，不要重新猜）

| 事实 | 内容 |
|---|---|
| SSH 双 IP | `ssh -i C:/Users/Administrator/.ssh/silvaco_ed25519 root@<IP>`；IP 在 `192.168.107.128` / `192.168.50.134` 之间漂移，`silvaco_remote.py` 自动双探测，**绝不硬编码** [已核实:docs/HANDOFF §2.1] |
| XAUTHORITY 坑 | 纯 SSH 有 `DISPLAY` 没 X cookie ⇒ GUI 进程能起但窗口永不弹。必须从 `/proc/$(pgrep -f mate-session)/environ` 提取 `XAUTHORITY=/var/run/lightdm/root/xauthority` + DBus 地址 + `XDG_RUNTIME_DIR=/run/user/0`；`silvaco_remote.py` 的 `SESSION_ENV_PRELUDE` 已封装 [已核实:docs/HANDOFF §2.3] |
| deckbuild pty 坑 | `ssh ... deckbuild -ascii -run` 无 pty 永久挂起（CPU 0%，typescript 空）。正确写法：`nohup xterm -e bash -lc 'script -q -f -c "deckbuild -ascii -run deck.in" typescript'` 后台跑；副作用是 VM 桌面可见，正好被截图看板拍到 [已核实:docs/HANDOFF §2.3] |
| CRLF/bytes 坑 | Windows 文件自带 CRLF，且 `subprocess.run(text=True)` 会把 `\n` 翻回 `\r\n` ⇒ bash 报 `$'\r': command not found`。`silvaco_remote.sh()` 先 `_posix()` 去 CR 再以 **bytes** 传 stdin [已核实:docs/HANDOFF §10.1] |
| 版本冻结 | `simflags="-V 5.40.0.R -P 4"`；8 vCPU / 8 GB ⇒ 最多同时 2 个 ATLAS；许可证 `export SFLM_SERVERS=+localhost` [已核实:docs/HANDOFF §2.2] |
| batch_vdoe.pl | 建工程前会先 `rm -r <project>`，同名工程历史结果被删 [已核实:docs/HANDOFF §10.4] |
| SOLVE/METHOD | 瞬态 SOLVE 无 `tstart` 参数（本项目曾因此报 Invalid parameter）；`METHOD min.temp` 默认 120 K 是晶格温度钳位不是解 [已核实:atlas.key:710] |

> 注：上表 `[已核实:docs/HANDOFF §x]` 的出处文件已按 B12 归档至
> `E:\silvaco2425\bulk\deprecated\废案_VDoE路线_20260727.zip`，证据仍可解包查验；
> 同类坑的现行汇编见 `docs\CODEX_避坑清单_20260727.md`。

文件放置纪律（用户明令）：

| 位置 | 只放 |
|---|---|
| `D:\SILVACO_LOCAL` | `.py` / `.md` / 轻量 `.csv` / `.png` / `.in` |
| `E:\silvaco2425\bulk\{str,log}\` | 一切大体积 `.str` / `.log` 归档 |
| 远端 `/root/DECKBUILD/<run>` | 正在迭代的 deck / 结构 / 运行产物 |
| `/mnt/hgfs/*`（VM 共享目录） | **什么都不放**（98% 满） |

`.in` deck 必须建模与电学求解合一：
`go atlas`(建结构) → `save outf=*.str` → `go atlas` → `mesh inf=*.str` → 求解。

---

## 5. 当前项目状态（2026-07-27，随运行日志 §4 滚动，此处只写大势）

**攻关目标（2026-07-27 靶心校准，账本 C6）：复现 Wang2026 Fig.4 红曲线（含衬底）的
电流-温度双轨迹与 SEB 四阶段形态**（尖峰 → ~10ns 骤降近零 → 数 µs 电流增益 → 5e-8s
不可逆），SEB 判定=电流增益不可逆的形态学（kb45）。历史表述"600K→1500K"作废：
1500K 出自 Wang2026 的 2720V **DC 电热击穿**佐证（Fig.2c，这条在 BV 两段法里仍正确），
不是 SEB 温度阈值；600K 病历（十大缺陷）仍是修复起点。
（唯一拟合目标 = Wang 2026 横向 E-mode β-Ga₂O₃，PDF 正本在 `archive\`，见 AGENTS.md §0）。
已定性：`mySEU.c` 公式无错、仅 LET 常数少 20.5%（0.36 → 应 0.4529 pC/µm）；deck 侧十大缺陷
清单在 `knowledge\50`；衬底旁路为静态漏电主因（四点标度实锤），W1 冻结计划书 D0/D1 已跑完、
D-2 分支裁决（b1=TRAP 路线）待审核；wang1600 四使能器全链条在 tmux 生产中。
**产线现状**：SWEEP 三层产线已实弹打通（`decks\sweep_bv_main/aux.in`，5 点 151 秒），
LHD+帕累托寻优器 `scripts\lhd_pareto.py` 已交付，首轮待发射包见
`outputs\reports\lhd_round1_wait_package.md`（受并发闸门 C1 节流）。
⚠ `skills\silvaco-tcad\` 经 285-token 审计+复审修复（可用性 8/10，报告在包内），引用其 deck
片段前仍须对 atlas.key 核参数；其 SKILL.md 的"VictoryDoE 现行 DoE 通道"与裸跑提交示例
两处**已废止**（勘误见 `docs\废案登记_20260727.md`）。
逐日细节以 `docs\AGENT_运行日志_与复现手册.md` §4 为准。

---

## 6. 给新窗口的接续提示词（复制即用）

```text
先读 D:\SILVACO_LOCAL\AGENTS.md（§0 现行路线三铁则）→ README.md → knowledge\CONSTRAINTS_用户约束账本.md（特别是 B12 与 §R）→ docs\AGENT_运行日志_与复现手册.md §4 末 20 行 → docs\冻结计划书_W1_静态基线冻结.md → docs\废案登记_20260727.md + docs\CODEX_避坑清单_20260727.md。
主产线=DeckBuild+aux.in+tmux（B12），VictoryDoE 已全弃；唯一拟合目标=Wang2026（PDF 在 archive\，准许只读引用）。
遇任何仿真问题按 D:\knowledge 的 material_sil → pdf25 → exp25 → paper 顺序查证，禁止猜参数；缺值按平替令补 4H-SiC/GaN 并标 [平替:xxx]，参数拼写以远端 atlas.key 为唯一裁决。
远端用 scripts\silvaco_remote.py 连接（IP 自动探测），长任务走 /root/bin/vdoe_tmux.sh（纯 tmux 封装，名字是历史遗留）；不要动 SEB.in / mySEU.c 原件，改动一律落 decks\。
```
