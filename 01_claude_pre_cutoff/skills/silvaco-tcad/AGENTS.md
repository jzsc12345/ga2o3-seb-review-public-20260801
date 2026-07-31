# AGENTS.md — Silvaco TCAD 远程仿真工程 (Codex 入口)

本文件是 Codex 在本仓库的操作入口：只讲**怎么连、东西放哪、一次运行怎么闭环、什么绝对不做**；物理模型、ATLAS 语法、诊断方法一律去 `SKILL.md` 与 `references/`。

## 1. 你是谁 / 你在控制什么

- **主控端**：Windows 10，仓库根 `D:\SILVACO_LOCAL`。你在这里写 `.in` deck、`.py` 解析脚本、`.md` 报告，不在这里跑 ATLAS。
- **计算端**：远端 RHEL 7.9 虚拟机，hostname `tcad`，8 vCPU / 8 GB RAM，`/` 剩余约 123 GB。所有 `atlas / athena / devedit / deckbuild / tonyplot` 都只在这台机器上执行，经 SSH 驱动。
- **归档端**：Windows `E:\silvaco2425\bulk\{str,log}\`，只存大体积仿真产物。
- Silvaco 安装根 `/atctools/Synopsys/Silvaco2024`（可执行在 `bin/`，**默认不在 PATH**）。本项目冻结 `-V 5.40.0.R -P 4`（机器上另有 5.38.0.R，不要混用）。许可证是 **SFLM**，`SFLM_SERVERS=+localhost`，`sflm_monitord` 已在运行。
- 你面对的是一个**科研工程闭环**，不是"写个 deck 跑一下"：问题定义 → 资料核对 → 合并 deck → 远端提交 → 监控 → `.log`/`.str` 分层诊断 → 出图与报告 → 下一轮。

## 2. 连接与环境自检 checklist（每个新会话第一件事，整块复制执行）

> 本块是 bash 语法（for / awk / heredoc）。Windows 主控端必须在 **Git Bash** 里执行；整块贴进 PowerShell 会直接语法错误。

```bash
# --- (0) 先探测真实 IP 并核对 hostname==tcad。ens33 走 DHCP，IP 会漂移（实测租约 valid_lft 915sec）：
#     2026-07-26 实测 192.168.50.134 活（hostname=tcad，别名 silvaco 即指向它）、192.168.107.128 连不上。
#     两个 IP 都可能随时失效，禁止硬编码任何 IP，一切以本次探测结果为准。 ---
KEY="C:/Users/Administrator/.ssh/silvaco_ed25519"
CANDS="192.168.50.134 $(ssh -G silvaco 2>/dev/null | awk '/^hostname /{print $2}') 192.168.107.128"
TCAD_HOST=""
for H in $CANDS; do
  HN=$(ssh -i "$KEY" -o BatchMode=yes -o ConnectTimeout=4 root@"$H" hostname 2>/dev/null)
  [ "$HN" = "tcad" ] && { TCAD_HOST="$H"; break; }
done
echo "TCAD_HOST=${TCAD_HOST:-UNREACHABLE}"
# 为空 => 停止一切远端操作，向用户确认虚拟机状态（VMware NAT 网段会漂移），不要继续往下猜。
# VM 离线期间仍可做：用本地只读镜像 d:\knowledge\{pdf25,exp25,material_sil} 核对手册/官方例子/材料参数、
# 离线起草 deck——但依赖 atlas.key 的结论一律标 [待 atlas.key 复核]，其余存疑标 [未核实]。

# --- (1)~(5) 远端一次性体检：PATH / SFLM / DISPLAY / 版本 / 磁盘 ---
ssh -i "$KEY" root@"$TCAD_HOST" 'bash -s' <<'EOS'
export SILVACO=/atctools/Synopsys/Silvaco2024
export PATH=$SILVACO/bin:$PATH          # 唯一有效方式；etc/silvaco.profile 已实测证伪(315字节csh空壳,什么都不设,见 preflight §2.2)勿用
export SFLM_SERVERS=+localhost          # 许可证
export DISPLAY=:0                       # GUI (deckbuild/tonyplot) 必须；root 已登录 tty1
echo "== PATH ==";    which deckbuild atlas athena devedit tonyplot sflm
echo "== SFLM ==";    pgrep -a sflm_monitord | head -3
echo "== DISPLAY =="; echo "DISPLAY=$DISPLAY"; ls -d /tmp/.X11-unix/X0 2>/dev/null
echo "== DISK ==";    df -h / /root; df -h /mnt/hgfs/* 2>/dev/null | tail -3
echo "== VERSION ==";                   # 版本 + license checkout 的真实 smoke test
PRE=/root/DECKBUILD/RUN_preflight_$(date -u +%Y%m%dT%H%M%SZ)   # run 目录一律 RUN_ 前缀（见 batch-run §5）
mkdir -p "$PRE" && cd "$PRE"
printf 'go atlas simflags="-V 5.40.0.R -P 4"\nquit\n' > _ver.in
timeout 600 deckbuild -run -ascii _ver.in -outfile _ver.out; head -25 _ver.out   # 必须加 timeout：deckbuild 会挂住留孤儿进程（preflight §6.2 实测）
EOS
```

判定：任一项 fail 就**停在 preflight**，报告阻塞项，不要写 deck、不要提交、不要把环境错误当成物理/收敛问题去改模型。完整判定表见 `references/preflight-and-environment.md`。

## 3. 文件放置纪律（用户硬规则，不可协商）

| 位置 | 只放 | 绝不放 |
|---|---|---|
| `D:\SILVACO_LOCAL\`（主控端） | `.py` 脚本 · `.md` 技术文档 · 轻量 `.csv` · `.png` 图/截图 · `.in` deck | 大体积 `.str`/`.log` · 远端工程整体副本 |
| `E:\silvaco2425\bulk\str\` / `...\log\` | 所有回传归档的 `.str` / `.log` | 源码、文档 |
| 远端 `/root/DECKBUILD/<run>/` | **唯一正在迭代的运行区**：运行期全部中间产物 | 长期归档（跑完就回传） |
| `/mnt/hgfs/{share_wm,share24,16sil_share}` | 小文件临时交换 | 任何大文件（HGFS 已 98% 满） |

`.in` deck 必须**建模与特性仿真合并为同一个文件**：

```silvaco
go atlas simflags="-V 5.40.0.R -P 4"
# ... mesh / region / electrode / doping  (结构；复杂多边形改用 DevEdit 或 Athena，见 SKILL.md)
save outf=dev.str
go atlas simflags="-V 5.40.0.R -P 4"
mesh inf=dev.str
# ... models / mobility / contact / method / log outf=idvd.log / solve ...
quit
```

## 4. 一次运行的最小闭环

| 步 | 动作 | 命令 / 产物 |
|---|---|---|
| 0 | 写 `RUN_MANIFEST.md` | run 名 `RUN_<case>_<UTCstamp>`、目的、变量、成功判据、预计时长 |
| 1 | 本地写合并 deck | `D:\SILVACO_LOCAL\decks\<case>.in` |
| 2 | 建远端 run 目录 + 上传 | `ssh -i "$KEY" root@$TCAD_HOST "mkdir -p /root/DECKBUILD/$RUN"`；`scp -i "$KEY" decks/<case>.in root@$TCAD_HOST:/root/DECKBUILD/$RUN/` |
| 3 | 提交 | **[默认]** `deckbuild -run -ascii <case>.in -outfile <case>.out`（长任务加 `nohup ... &`）· 候选项：DeckBuild GUI 内 `simulate` · VWF job submit · 纯 `atlas -V 5.40.0.R -P 4 <case>.in` 单模块直跑 |
| 4 | 监控（后台单次等待，不轮询刷屏） | **[默认]** runner + `.exit` 退出码哨兵文件（权威写法，见 `references/batch-run-and-monitor.md` §6/§8）· 无 runner 时用表下"退化监控"代码块（必须在远端执行） |
| 5 | 回传 | `.log`/`.csv` 小件回 `D:\SILVACO_LOCAL\outputs\`；`.str`/大 `.log` 直接 `scp` 到 `E:\silvaco2425\bulk\{str,log}\` |
| 6 | 解析 | 按 `references/results-and-reporting.md` §3.2 的 Python 骨架解析 `.log` → `.csv`（首次使用先把骨架落盘成实体脚本；`scripts\` 目录现有 `silvaco_remote.py`、`let_calc.py` 等，**没有** `parse_log.py`）。ATLAS `.log` 是曲线文件，取代 Sentaurus `.plt` |
| 7 | 出图 | **[默认]** TonyPlot（远端 `DISPLAY=:0`，看 `.str` 空间分布 + `.log` 曲线）· TonyPlot3D · Victory Visual（出版级导出）· 无头场景用 Python/matplotlib 出 `.png`（DPI≥300），并**注明 `.str` 空间诊断尚未查看** |
| 8 | 写结论 | `docs\<case>.md`：判据、指标、图路径、根因、下一步 |

退化监控（仅当没用 batch-run §8 的 runner 时；整段经 ssh 在**远端**执行——`pgrep` 在 Windows 上不存在）：

```bash
ssh -i "$KEY" root@"$TCAD_HOST" '
  cd /root/DECKBUILD/RUN_<case>_<UTCstamp>
  until grep -qEi "ATLAS DIED|Convergence failure|solution did not converge|fail\.quit|license" <case>.out \
        || ! pgrep -x atlas >/dev/null; do sleep 60; done
  tail -30 <case>.out'
# 用 pgrep -x 而非 -f（-f 会匹配到自身命令行恒真误报）；进程退出只说明结束、不说明收敛，必须再看 .out 尾部与 .log。
```

远程提交/回传的现行封装是 `D:\SILVACO_LOCAL\scripts\silvaco_remote.py`（内含 xterm+script 供 TTY 的已验证提交模式），可替代第 2/3/5 步的手工 ssh/scp。

参数扫描：**[默认]** DeckBuild `set` 变量 + 外部 Python 生成多份 deck；候选项 **VictoryDoE**（本项目现行 DoE 通道：契约 `D:\SILVACO_LOCAL\docs\victorydoe_agent_control_API.md`，控制脚本 `scripts\victorydoe_ctl.py`）· VWF Automation Tools（DOE/split 表）· DeckBuild `loop / l.end`。扫描前 `RUN_MANIFEST.md` 必须先写好。

## 5. 禁止事项

1. **不要在 Windows 上迭代 deck 的物理正确性**——ATLAS 只在远端跑；本地只做文本编辑与解析。
2. **不要往 `/mnt/hgfs/*` 写大文件**（已 98% 满，会拖死共享层）。归档走 `scp` → `E:\silvaco2425\bulk\`。
3. **不要硬编码 IP**（`192.168.107.128` / `192.168.50.134` 都不许写进 runner 或脚本），每次按第 2 节探测 `$TCAD_HOST`。
4. **不要跳过版本锁**：所有 `go atlas` 带 `simflags="-V 5.40.0.R -P 4"`；混用 5.38.0.R 的结果不可比。
5. **不要 `grep "Error"`** 判断结束——正常收敛信息会误触发。用第 4 节的终止串候选集（`ATLAS DIED` / `Convergence failure` / `solution did not converge` / `fail.quit` / `License`）加进程退出判断；也不要靠 `pgrep atlas` 单独判定（并发 run 会混淆）。
6. **没有 `RUN_MANIFEST.md` 不许开跑扫描**；同类失败最多试两次，第二次仍失败就停手回到资料核对与根因分析。
7. 不要绕过 `deckbuild -run` 的产物约定去手工拼凑结果目录；不要在未知目录删除/覆盖文件；不要记录或索取 license/账号/口令。
8. **不要编造 ATLAS 参数名**。存在性的唯一权威是远端关键字表 `$SILVACO/lib/atlas/5.40.0.R/common/atlas.key`：`grep -n -i '<参数>' $SILVACO/lib/atlas/5.40.0.R/common/atlas.key`，行格式 = 名字 · 类型（NUM/LOG/CHAR）· 内部序号 · **默认值**。grep 不出来就是 ATLAS 5.40.0.R 里没有这个参数，写 **[未核实]**，不要靠印象补全、也不要删掉存疑条目。语义/单位去手册正文 `$SILVACO/lib/atlas/5.40.0.R/docs/atlas_users1.pdf`（远端有 `pdftotext`）——注意 `$SILVACO/doc/` 下只有安装与 SFLM 文档，**没有** ATLAS 手册，别拿它当核对源。远端不可达（VM 关机）时，语义与例子核对降级用本地只读镜像：手册 `d:\knowledge\pdf25\atlas_users1.pdf`、官方例子 `d:\knowledge\exp25\`（184 个 `.in`）、材料参数库 `d:\knowledge\material_sil\`；atlas.key 本地**无**副本，凡依赖它的结论（登记名/行号/默认值）一律标 [待 atlas.key 复核]。
9. **抄 examples 之前先验血统**：`grep -iE '^ *go ' <deck>.in`。`$SILVACO/examples/deckbuild/5.2.40.R/` 里大量 deck 是 `go victorydevice` / `victoryprocess`，Victory Device 的语句与 ATLAS **不通用**（本包历史上的 `lte.timestep` / `seu.max.rad` / `seu.max.inc` / `seu.n.inc` / `hysteresis` / `e.min` / `constant.timestep` 等假参数，全部来自误抄 Victory 例子）。只有 `go atlas` 的行可以直接进 ATLAS deck；非 atlas 血统的例子若要引用，必须逐个 token 回 atlas.key 复核并注明出处。
10. **改数之前先看 atlas.key 的默认值列**，不要凭字面猜"调小 = 更严"。典型反例：`climit` 不是残差/收敛容差，而是求解器 X-norm 里的**载流子浓度归一化因子**（最低可分辨浓度），`[已核实: atlas.key:688  climit  NUM  51  10000]` —— 默认 1e4，**无量纲**；cm⁻³ 形式是 `clim.dd`，`climit.dd` 是其别名 [已核实: atlas_users1.pdf p.1417 METHOD 参数表两者并列（均 Real / 4.5e13 / cm⁻³）；p.1426 "CLIMIT.DD — This is an alias for CLIM.DD"]，atlas.key 侧登记名与行号 [待 atlas.key 复核]。手册对击穿/小漏电仿真明确推荐调小：原文 "A value of CLIMIT=1e-4 is recommended for all simulations of breakdown"，且 p.1122 警告不调小 "a 'false' solution may be obtained"——所以 deck 里的 1e-4 是正规设定，不是"过严的容差"。

## 6. 路由表

| 需要 | 读取 |
|---|---|
| 全流程规则、物理模型选择、闭环方法论 | `SKILL.md` |
| 首次/新机环境体检、SFLM、DISPLAY、版本、判定表 | `references/preflight-and-environment.md` |
| DeckBuild 运行、VWF 扫描、监控与作业管理 | `references/batch-run-and-monitor.md` |
| 结构与网格（ATLAS 内建 mesh / DevEdit / Athena） | `references/structure-and-mesh.md` |
| ATLAS Physics / method / solve / save·log | `references/device-physics-and-solver.md` |
| GaN·Ga2O3 HEMT、BV、singleeventupset、SEB | `references/wbg-radiation-and-seb.md` |
| TonyPlot 可视化、`.log` 解析、报告与经验沉淀 | `references/results-and-reporting.md` |

上表六个 `references/` 文件名与 `SKILL.md` §5 一致 [已核实: `ls D:\SILVACO_LOCAL\skills\silvaco-tcad\references\` → batch-run-and-monitor.md · device-physics-and-solver.md · preflight-and-environment.md · results-and-reporting.md · structure-and-mesh.md · wbg-radiation-and-seb.md]。若某个文件名与上表不符，仍以 `ls` 的实际清单为准。

## 7. 最小交付标准

一次任务至少交付：远端 run 目录名与 deck 路径 · `.out` 终止状态原文 · `.log` 曲线结论 + `.str` 空间分布结论（无 DISPLAY 时明确标注未查看）· 至少一个持久化产物（`.png` 或 `.md` 表格）· 归档到 `E:\silvaco2425\bulk\` 的文件清单 · 下一轮建议或"已达判据"的明确结论。
